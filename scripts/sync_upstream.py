# -*- coding: utf-8 -*-
"""
从上游 awesome-seedance 拉取最新数据，同步到本项目。

用法：
    python scripts/sync_upstream.py            # 检查并同步（默认）
    python scripts/sync_upstream.py --check    # 只检查，一个字节都不写
    python scripts/sync_upstream.py --json     # 结果以单行 JSON 打到 stdout（给后端调用）
    python scripts/sync_upstream.py --force-regen   # 即使数据没变也重生成技能

做四件事：
    1. 拉上游 data/ 下的数据文件，和本地逐字节比对（忽略行尾差异），**只有真变了才落盘**
    2. 数据有变化时重生成 14 个自建技能（build_extra_skills.py，已验证幂等）
    3. 拉 13 个上游技能（我们自己不生成的）的 SKILL.md / references/cases.md
    4. 拉 EXTRA_FILES 里的「孤儿文件」——不从 data/ 渲染、项目里也没人生成的文件

然后把结果写进 data/update-status.json，供前端显示「上次检查时间 / 数据版本」。

不碰这些：seedance-prompt-lint（我们改造过的）、prompt-library、storyboard-writer、production-workflow
的 SKILL.md 与 cases.md。（注意 EXTRA_FILES 是例外，见下方注释。）
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SKILLS_DIR = ROOT / "skills"
STATUS_FILE = DATA / "update-status.json"
EXTRA_CFG = DATA / "skills-extra.json"
BUILDER = ROOT / "scripts" / "build_extra_skills.py"

REPO = "LearnPrompt/awesome-seedance"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
MIRROR_PREFIX = "https://gh-proxy.com/"   # 直连偶发断流，走这个兜底
TIMEOUT = 10
HISTORY_KEEP = 20

# 拉取源，按顺序试，第一个成功的就用。
# 实测（2026-10-16）：raw.githubusercontent.com 直连**首次要 60 秒**、之后 2 秒；
# gh-proxy 稳定 ~1.9 秒 —— 所以默认镜像优先，直连留作兜底。
# 内容可信度：拿到的一定是合法 JSON 才落盘；且实测与直连内容逐字段一致。
_BASES = [MIRROR_PREFIX + RAW_BASE, RAW_BASE]

CN_TZ = timezone(timedelta(hours=8))

# 喂给生成器的数据文件（顺序即报告顺序）
DATA_FILES = [
    "data/cases.json",
    "data/case-taxonomy.json",
    "data/style-library.json",
    "data/skills.json",
]

# 永远不同步的技能目录：含我们改造过的 lint，以及非模板类技能
NEVER_TOUCH = {
    "seedance-prompt-lint",
    "seedance-prompt-library",
    "seedance-storyboard-writer",
    "seedance-production-workflow",
}

# ---- 孤儿文件：只从上游拉，本地不生成 ----
# 背景（2026-10-16 发现）：skills/seedance-prompt-library/references/style-library.md
#   · 有 141 KB，内容是从上游 data/style-library.json 渲染出来的；
#   · 但本项目**没有任何脚本生成它**（grep scripts/ 零命中）；
#   · 而 seedance-prompt-library 又在 NEVER_TOUCH 里，上面的第 3 步也不会拉它。
#   → 结果：data/style-library.json 更新了，这个 md 却永远停在搬进来那天。
# 这里把它单列出来跟随上游，填补这个缺口。
# 校验偏保守：内容太短或为空一律不写，避免上游返回错误页把本地文件搞坏。
EXTRA_FILES = [
    "agents/skills/seedance-prompt-library/references/style-library.md",
]
EXTRA_MIN_BYTES = 4096          # 孤儿文件的最小可信体积（实际 141 KB，留足余量）


# ---------------------------------------------------------------- 小工具

def now_iso() -> str:
    return datetime.now(CN_TZ).isoformat(timespec="seconds")


def normalize(b: bytes) -> bytes:
    """抹平行尾差异，只比内容。"""
    return b.replace(b"\r\n", b"\n")


def same(a: bytes, b: bytes) -> bool:
    return normalize(a) == normalize(b)


def looks_like_markdown(b: bytes) -> bool:
    """粗校验：Markdown 应以 `#` 标题开头。
    用来挡住上游返回 HTML 错误页 / 登录页 / 空响应之类的东西。"""
    return b.lstrip()[:64].startswith(b"#")


def local_eol(p: Path) -> bytes:
    """读本地文件用的行尾，保持项目原有风格不变。"""
    try:
        raw = p.read_bytes()
    except OSError:
        return b"\r\n"
    return b"\r\n" if b"\r\n" in raw else b"\n"


def write_keeping_eol(p: Path, content: bytes) -> None:
    eol = local_eol(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(normalize(content).replace(b"\n", eol))


def fetch(rel_path: str) -> tuple[bytes | None, str]:
    """按 _BASES 顺序试，返回第一个成功的。只读全局，可安全并发调用。"""
    last = ""
    for base in _BASES:
        try:
            req = urllib.request.Request(
                base + rel_path, headers={"User-Agent": "prompt_v-sync/1.0"}
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                if r.status == 200:
                    return r.read(), ""
                last = f"HTTP {r.status}"
        except Exception as e:                      # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
    return None, last


def meta_of_cases(raw: bytes) -> dict:
    """从 cases.json 里取版本信息用于展示。"""
    try:
        d = json.loads(raw.decode("utf-8"))
        return {
            "exportedAt": (d.get("meta") or {}).get("exportedAt", ""),
            "caseCount": len(d.get("cases") or []),
        }
    except Exception:                               # noqa: BLE001
        return {}


def meta_of_taxonomy(raw: bytes) -> dict:
    try:
        d = json.loads(raw.decode("utf-8"))
        return {"taxonomyKeys": len(d.get("assignments") or {})}
    except Exception:                               # noqa: BLE001
        return {}


def self_built_ids() -> set[str]:
    """14 个由 build_extra_skills.py 生成的技能 id。"""
    try:
        d = json.loads(EXTRA_CFG.read_text(encoding="utf-8"))
        return {s["id"] for s in d.get("skills") or []}
    except Exception:                               # noqa: BLE001
        return set()


def upstream_skill_names() -> list[str]:
    """本地有 cases.md、但不是我们生成的技能 —— 这些要从上游拉。"""
    mine = self_built_ids()
    names = sorted(p.parent.parent.name for p in SKILLS_DIR.glob("*/references/cases.md"))
    return [n for n in names if n not in mine and n not in NEVER_TOUCH]


# ---------------------------------------------------------------- 主流程

def run(check_only: bool, force_regen: bool) -> dict:
    started = now_iso()
    report: dict = {
        "checkedAt": started,
        "ok": True,
        "changed": False,
        "message": "",
        "dataFiles": [],
        "errors": [],
        "skills": {"regenerated": 0, "pulledFromUpstream": 0,
                   "pulledNames": [], "extraFiles": []},
    }

    data_changed_something = False

    # ---- 1. 数据文件（并发拉取，按顺序串行判断与落盘）
    with ThreadPoolExecutor(max_workers=len(DATA_FILES)) as ex:
        fetched = list(ex.map(fetch, DATA_FILES))

    for rel, (remote, err) in zip(DATA_FILES, fetched):
        local_p = ROOT / rel
        item = {"path": rel, "changed": False, "written": False}

        if remote is None:
            item["status"] = "拉取失败"
            item["error"] = err
            report["errors"].append(f"{rel}: {err}")
            report["dataFiles"].append(item)
            continue

        # 下载下来的必须是合法 JSON，否则拒绝覆盖
        if rel.endswith(".json"):
            try:
                json.loads(remote.decode("utf-8"))
            except Exception as e:                  # noqa: BLE001
                item["status"] = "内容不是合法 JSON，已忽略"
                item["error"] = str(e)
                report["errors"].append(f"{rel}: 收到的不是合法 JSON")
                report["dataFiles"].append(item)
                continue

        local_raw = local_p.read_bytes() if local_p.is_file() else b""
        if same(local_raw, remote):
            item["status"] = "无变化"
        else:
            item["changed"] = True
            changed_data = True
            data_changed_something = True
            if check_only:
                item["status"] = "有新版本（未写入）"
            else:
                write_keeping_eol(local_p, remote)
                item["written"] = True
                item["status"] = "已更新"

        if rel == "data/cases.json":
            item.update(meta_of_cases(remote))
        elif rel == "data/case-taxonomy.json":
            item.update(meta_of_taxonomy(remote))

        report["dataFiles"].append(item)

    report["changed"] = data_changed_something

    # 数据版本（前端展示用）：直接读落盘后的本地文件，保证显示的就是真实状态
    _cases = DATA / "cases.json"
    _tax = DATA / "case-taxonomy.json"
    dv: dict = {}
    if _cases.is_file():
        dv.update(meta_of_cases(_cases.read_bytes()))
    if _tax.is_file():
        dv.update(meta_of_taxonomy(_tax.read_bytes()))
    report["dataVersion"] = dv

    # ---- 2. 重生成 14 个自建技能
    should_regen = (data_changed_something or force_regen) and not check_only
    if should_regen:
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        try:
            p = subprocess.run(
                [sys.executable, str(BUILDER)],
                cwd=str(ROOT), capture_output=True, text=True,
                encoding="utf-8", errors="replace", env=env, timeout=180,
            )
            if p.returncode == 0:
                report["skills"]["regenerated"] = len(self_built_ids())
            else:
                report["errors"].append(f"重生成技能失败：{(p.stderr or p.stdout or '')[-300:]}")
        except Exception as e:                      # noqa: BLE001
            report["errors"].append(f"重生成技能异常：{e}")

    # ---- 3. 拉上游技能的 SKILL.md / references/cases.md，外加 EXTRA_FILES 孤儿文件
    # 上游的技能文件也是从同一份数据生成的：数据没变就不必拉（省掉 26 次请求）
    pulled: list[str] = []
    extra_touched: list[str] = []
    if should_regen:
        # (上游相对路径, 本地相对 skills/ 的落地路径, 最小可信体积)
        jobs: list[tuple[str, str, int]] = []
        for name in upstream_skill_names():
            jobs.append((f"agents/skills/{name}/SKILL.md", f"{name}/SKILL.md", 0))
            jobs.append(
                (f"agents/skills/{name}/references/cases.md",
                 f"{name}/references/cases.md", 0)
            )
        for rel in EXTRA_FILES:
            jobs.append((rel, rel.split("agents/skills/", 1)[-1], EXTRA_MIN_BYTES))

        with ThreadPoolExecutor(max_workers=8) as ex:
            got = list(ex.map(lambda j: (*j, *fetch(j[0])), jobs))

        extra_dests = {rel.split("agents/skills/", 1)[-1] for rel in EXTRA_FILES}
        touched_names: set[str] = set()
        for _rel, dest, minbytes, remote, _err in got:
            if remote is None:
                continue
            if minbytes and len(remote) < minbytes:
                report["errors"].append(
                    f"{dest}：拉到的内容只有 {len(remote)} 字节（预期 ≥{minbytes}），疑似异常，已跳过"
                )
                continue
            if dest in extra_dests and not looks_like_markdown(remote):
                report["errors"].append(
                    f"{dest}：拉到的内容不像 Markdown（未以 # 开头），疑似上游返回了错误页，已跳过"
                )
                continue
            local_p = SKILLS_DIR / dest
            if local_p.is_file() and same(local_p.read_bytes(), remote):
                continue
            write_keeping_eol(local_p, remote)
            if dest in extra_dests:
                extra_touched.append(dest)
            else:
                touched_names.add(dest.split("/", 1)[0])

        pulled = sorted(touched_names)
        report["skills"]["pulledFromUpstream"] = len(pulled)
        report["skills"]["pulledNames"] = pulled
        report["skills"]["extraFiles"] = sorted(extra_touched)

    # ---- 4. 结论
    if report["errors"] and not report["dataFiles"]:
        report["ok"] = False
        report["message"] = "无法连接上游，本次没有改动"
    elif report["errors"]:
        report["ok"] = False
        report["message"] = "部分内容拉取失败：" + "；".join(report["errors"][:2])
    elif report["changed"]:
        n = report["dataVersion"].get("caseCount")
        report["message"] = f"已同步上游新数据（{n} 条案例）"
    elif check_only:
        report["message"] = "上游无新数据"
    else:
        n = report["dataVersion"].get("caseCount")
        report["message"] = f"已是最新（{n} 条案例），技能无变化"

    # ---- 5. 写状态文件
    status = {
        "$comment": "由 scripts/sync_upstream.py 自动写入。checkedAt=每次检查都会更新；dataVersion=上游数据的版本，只有真有新数据才变。",
        "checkedAt": report["checkedAt"],
        "ok": report["ok"],
        "changed": report["changed"],
        "message": report["message"],
        "dataVersion": report["dataVersion"],
        "skills": report["skills"],
        "dataFiles": report["dataFiles"],
        "errors": report["errors"],
        "history": [],
    }
    if not check_only:
        old = {}
        if STATUS_FILE.is_file():
            try:
                old = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
            except Exception:                       # noqa: BLE001
                old = {}
        hist = list(old.get("history") or [])
        hist.append({
            "checkedAt": report["checkedAt"],
            "ok": report["ok"],
            "changed": report["changed"],
            "message": report["message"],
        })
        status["history"] = hist[-HISTORY_KEEP:]
        STATUS_FILE.write_text(
            json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="同步上游 awesome-seedance 数据")
    ap.add_argument("--check", action="store_true", help="只检查，不写任何文件")
    ap.add_argument("--json", action="store_true", help="以单行 JSON 输出结果")
    ap.add_argument("--force-regen", action="store_true", help="即使数据没变也重生成技能")
    args = ap.parse_args()

    rep = run(check_only=args.check, force_regen=args.force_regen)

    if args.json:
        print(json.dumps(rep, ensure_ascii=False))
    else:
        print(f"检查时间：{rep['checkedAt']}")
        print(f"结论    ：{rep['message']}")
        print()
        print("数据文件：")
        for it in rep["dataFiles"]:
            extra = ""
            if "caseCount" in it:
                extra = f"  {it['caseCount']} 条 · {it.get('exportedAt', '')}"
            elif "taxonomyKeys" in it:
                extra = f"  {it['taxonomyKeys']} 个键"
            print(f"  [{it['status']:<12}] {it['path']}{extra}")
        print()
        sk = rep["skills"]
        print(f"技能：重生成 {sk['regenerated']} 个 · 从上游拉取 {sk['pulledFromUpstream']} 个")
        if sk.get("extraFiles"):
            for f in sk["extraFiles"]:
                print(f"  孤儿文件已更新：{f}")
        if rep["errors"]:
            print()
            print("错误：")
            for e in rep["errors"]:
                print("  - " + e)

    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
