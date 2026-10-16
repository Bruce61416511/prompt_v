# -*- coding: utf-8 -*-
"""
生成本项目追加的独立技能（一个片型一个 Skill）。

照抄 upstream 的 scripts/lib/standalone-skill.mjs + scripts/lib/library.mjs 的渲染逻辑，
保证产出与 upstream 已有 13 个技能**格式完全一致**（可逐字节比对）。

输出：skills/<id>/SKILL.md  +  skills/<id>/references/cases.md

用法：
    python scripts/build_extra_skills.py            # 全部生成
    python scripts/build_extra_skills.py --dry-run  # 只打印，不写盘
    python scripts/build_extra_skills.py --only handheld-ugc-vlog
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SKILLS_DIR = ROOT / "skills"

# ---------------------------------------------------------------- upstream 常量
# 来源：scripts/lib/standalone-skill.mjs
CASE_LIMIT = 8                  # STANDALONE_CASE_LIMIT
PROMPT_MAX_CHARS = 3500         # STANDALONE_PROMPT_MAX_CHARS
SKILL_MARKER = "`references/cases.md` is generated from `data/`"
SUMMARY_MAX_CHARS = 400         # cases.md 里 summary.slice(0, 400)

# 来源：scripts/lib/library.mjs —— 这些字段按语言深合并
LANG_KEYED = ["title", "description", "useWhen", "structure", "guidance", "pitfalls", "copyPrompt"]


# ---------------------------------------------------------------- 通用小工具

def load_json(p: Path, default=None):
    if not p.is_file():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- JS 字符串语义
# ⚠️ 必须模拟 JS 的 UTF-16 语义，不能用 Python 的 len()/切片。
#
# 2026-10-16 踩坑：upstream 是 Node，`String.prototype.length` 和 `.slice()` 按
# **UTF-16 code unit** 计数；Python 的 len() 按 **code point**。一个 emoji 在 JS 里
# 占 2，在 Python 里占 1 —— 于是 `summary.slice(0, 400)` 会切在不同位置。
# 现象：13 个已有技能里 2 个的 cases.md 差 3~5 个字符（都出现在含 emoji 的案例上），
# 肉眼极难发现。改这里之后 13/13 逐字节一致。

def js_len(s: str) -> int:
    """等价于 JS 的 String.prototype.length。"""
    return len(s.encode("utf-16-le")) // 2


def js_slice(s: str, n: int) -> str:
    """等价于 JS 的 s.slice(0, n)。

    正好切在代理对中间时会丢掉那半个字符（JS 会留下孤立代理，两者渲染都是乱码，
    实际影响可忽略）。
    """
    b = s.encode("utf-16-le")
    if len(b) <= 2 * n:
        return s
    return b[: 2 * n].decode("utf-16-le", errors="ignore")


def collapse_ws(s) -> str:
    return re.sub(r"\s+", " ", str(s if s is not None else "")).strip()


def pick_lang(obj, lang: str) -> str:
    """对应 render.mjs 的 pickLang。"""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    return obj.get(lang) or obj.get("en") or obj.get("zh") or ""


def pick_text(primary, fallback) -> str:
    if isinstance(primary, str) and primary.strip():
        return primary.strip()
    if isinstance(fallback, str) and fallback.strip():
        return fallback.strip()
    return ""


def list_of(value, lang: str) -> list[str]:
    v = None
    if isinstance(value, dict):
        v = value.get(lang)
        if v is None:
            v = value.get("en")
    elif value is not None:
        v = value
    if isinstance(v, list):
        return v
    return [v] if v else []


def is_plain_obj(v) -> bool:
    return isinstance(v, dict)


# ---------------------------------------------------------------- 标题清理（render.mjs）
HEADING_CLEAN_THRESHOLD = 80
HEADING_MAX_LEN = 70

MODEL_PREFIX_RE = re.compile(r"^seedance(?:\s*\d+(?:\.\d+)?)?\s*[：:]\s*", re.I)
PROMPT_PREFIX_RE = re.compile(r"^prompt\s*[：:]\s*", re.I)
TRAILING_ELLIPSIS_RE = re.compile(r"(?:…|\.{3})\s*$")
TRAILING_ASCII_PUNCT_RE = re.compile(r"[.,;:!?]+$")


def _last_index_of_any(s: str, chars: str, min_index: int) -> int:
    best = -1
    for i, ch in enumerate(s):
        if ch in chars and i >= min_index:
            best = i
    return best


def truncate_at_boundary(s: str, max_len: int = HEADING_MAX_LEN):
    s = collapse_ws(s)
    if js_len(s) <= max_len:
        return s, False
    window = js_slice(s, max_len)
    idx = _last_index_of_any(window, ".!?。！？", 20)
    if idx < 0:
        idx = _last_index_of_any(window, ",，;；:：", 40)
    if idx < 0:
        idx = _last_index_of_any(window, " ", 20)
    text = (window[:idx] if idx >= 0 else window).strip()
    return TRAILING_ASCII_PUNCT_RE.sub("", text).strip(), True


def clean_heading_title(raw: str) -> str:
    t = collapse_ws(raw)
    has_prefix = bool(MODEL_PREFIX_RE.match(t) or PROMPT_PREFIX_RE.match(t))
    if not has_prefix:
        return TRAILING_ASCII_PUNCT_RE.sub("", t).strip() or t
    s = collapse_ws(PROMPT_PREFIX_RE.sub("", MODEL_PREFIX_RE.sub("", t)))
    if not s:
        return t
    if js_len(t) <= HEADING_CLEAN_THRESHOLD:
        return TRAILING_ASCII_PUNCT_RE.sub("", s).strip() or s
    s = re.sub(r"@\[[^\]]*\]\([^)]*\)", " ", s)
    s = re.sub(r"<<<[^>]*>>>", " ", s)
    s = re.sub(r"\{\{[^}]*\}\}", " ", s)
    s = collapse_ws(s)
    was_truncated = bool(TRAILING_ELLIPSIS_RE.search(s))
    s = TRAILING_ELLIPSIS_RE.sub("", s).strip()
    text, cut_truncated = truncate_at_boundary(s, HEADING_MAX_LEN)
    if not text:
        text = js_slice(t, HEADING_MAX_LEN)
    return f"{text}…" if (cut_truncated or was_truncated) else text


def display_title(case: dict, lang: str = "en") -> str:
    if lang == "zh":
        raw = pick_text(case.get("title"), case.get("titleEn"))
    else:
        raw = pick_text(case.get("titleEn"), case.get("title"))
    return clean_heading_title(raw or case.get("slug") or "")


# ---------------------------------------------------------------- Seedance 版本判定（render.mjs）
SEEDANCE_MODEL_RE = re.compile(r"^\s*seedance(?:[\s_-]*(\d+(?:\.\d+)?))?\s*(.*)$", re.I)
SEEDANCE_TEXT_VERSION_RE = re.compile(r"seedance[\s_-]*(\d+(?:\.\d+)?)", re.I)
BUCKET_RANK = {"2.5": 2, "2.0": 1, "unspecified": 0}


def seedance_version_of(model):
    if not isinstance(model, str):
        return None
    m = SEEDANCE_MODEL_RE.match(model)
    if not m:
        return None
    version = m.group(1)
    if not version:
        return "unspecified"
    return "2.5" if float(version) >= 2.5 else "2.0"


def seedance_version_in_text(text):
    if not isinstance(text, str) or not text:
        return None
    best = None
    for m in SEEDANCE_TEXT_VERSION_RE.finditer(text):
        v = "2.5" if float(m.group(1)) >= 2.5 else "2.0"
        if best is None or BUCKET_RANK[v] > BUCKET_RANK[best]:
            best = v
    return best


def classify_seedance(case: dict) -> str:
    best = None
    for model in (case.get("models") or []):
        v = seedance_version_of(model)
        if v is None or v == "unspecified":
            continue
        if best is None or BUCKET_RANK[v] > BUCKET_RANK[best]:
            best = v
    if best:
        return best
    return seedance_version_in_text(f"{case.get('title') or ''}\n{case.get('summary') or ''}") or "2.0"


# ---------------------------------------------------------------- 代码围栏（render.mjs）
def fence_for_prompt(prompt: str) -> str:
    longest = cur = 0
    for ch in prompt:
        if ch == "`":
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0
    return "`" * max(3, longest + 1)


def clip_prompt(text: str) -> str:
    t = (text or "").strip()
    if js_len(t) <= PROMPT_MAX_CHARS:
        return t
    return js_slice(t, PROMPT_MAX_CHARS).rstrip() + "\n\n[… truncated, full prompt on the goodcase.ai page]"


# ---------------------------------------------------------------- 模板库合并（library.mjs）

def apply_template_override(template: dict, override) -> dict:
    out = dict(template)
    for key, value in (override or {}).items():
        if key in LANG_KEYED and is_plain_obj(value) and is_plain_obj(out.get(key)):
            out[key] = {**out[key], **value}
        else:
            out[key] = value
    return out


def load_library() -> dict:
    style = load_json(DATA / "style-library.json", {}) or {}
    local = load_json(DATA / "templates-local.json", {}) or {}

    templates = []
    overrides = local.get("overrides", {}) or {}
    for tp in style.get("templates", []) or []:
        templates.append(apply_template_override(tp, overrides.get(tp.get("id"))))

    upstream_ids = {tp.get("id") for tp in (style.get("templates") or [])}
    seen_ids = {tp.get("id") for tp in templates}
    for tp in local.get("templates", []) or []:
        if tp.get("id") in upstream_ids or tp.get("id") in seen_ids:
            raise SystemExit(f"templates-local.json: 模板 id 重复：{tp.get('id')}")
        item = dict(tp)
        example_cases = tp.get("exampleCases") or []
        item["exampleCases"] = example_cases
        item["exampleCaseUrls"] = tp.get("exampleCaseUrls") or [
            f"https://goodcase.ai/cases/{s}" for s in example_cases
        ]
        item["local"] = True
        templates.append(item)
        seen_ids.add(tp.get("id"))

    return {"categories": style.get("categories", []) or [], "templates": templates}


# ---------------------------------------------------------------- 案例归组（library.mjs）

def build_template_index(templates: list[dict], taxonomy: dict, cases: list[dict]) -> dict:
    """按模板归组案例。

    ⚠️ 这里用 dict 当「有序 set」而不是 set：upstream 用的是 JS Set，JS Set 按**插入顺序**
    迭代；Python 的 set 顺序受 PYTHONHASHSEED 影响，**跨进程会变**。后果是 heatScore 并列
    的案例每次选出的「前 8 条」不一样，产物不可复现（实测 dry-run 与实际跑差 900 多字符）。
    改用 dict 后，迭代顺序 = assignments 的文件顺序，与 JS 一致。
    """
    template_ids = {tp["id"] for tp in templates}
    assignments = (taxonomy or {}).get("assignments", {}) or {}
    cases_by_slug = {c["slug"]: c for c in cases}
    slugs_by_template: dict[str, dict] = {tp["id"]: {} for tp in templates}

    for slug, template_id in assignments.items():
        if template_id is None:
            continue
        if template_id not in template_ids:
            raise SystemExit(f'case-taxonomy.json: "{slug}" 指向未知模板 "{template_id}"')
        if slug in cases_by_slug:
            slugs_by_template[template_id][slug] = True

    for tp in templates:
        for slug in (tp.get("exampleCases") or []):
            assigned = assignments.get(slug)
            if assigned and assigned != tp["id"]:
                continue
            if slug in cases_by_slug:
                slugs_by_template[tp["id"]][slug] = True

    out = {}
    for tp in templates:
        lst = [cases_by_slug[s] for s in slugs_by_template[tp["id"]]]
        # upstream 用简单 byHeat；list.sort 是稳定排序，并列时保持插入顺序
        lst.sort(key=lambda c: -(c.get("heatScore") or 0))
        out[tp["id"]] = lst
    return out


# ---------------------------------------------------------------- 渲染 SKILL.md

def skill_description(template: dict, skill: dict) -> str:
    zh = pick_lang(template.get("title"), "zh")
    en = pick_lang(template.get("title"), "en")
    extra = ", ".join(skill.get("triggers") or [])
    return collapse_ws(
        f'{pick_lang(template.get("description"), "en")} '
        f"Use when the user wants a Seedance 2.5 / 2.0 video prompt for this kind of clip"
        f" ({en}; 中文触发词: {zh}{', ' + extra if extra else ''}),"
        f" or asks how published cases of this type were prompted."
        f" Read references/cases.md before drafting."
    )


def render_skill_md(template: dict, skill: dict, cases: list[dict]) -> str:
    en = pick_lang(template.get("title"), "en")
    zh = pick_lang(template.get("title"), "zh")
    L: list[str] = []

    L.append("---")
    L.append(f"name: {skill['id']}")
    # 与 JS 的 JSON.stringify 一致：双引号包裹、非 ASCII 不转义
    L.append(f"description: {json.dumps(skill_description(template, skill), ensure_ascii=False)}")
    L.append("---")
    L.append("")
    L.append(f"# {en} · {zh}")
    L.append("")
    L.append(pick_lang(template.get("description"), "en"))
    L.append("")
    L.append(
        f"This Skill carries one prompt structure distilled from {len(cases)} human-verified "
        "Seedance cases on [goodcase.ai](https://goodcase.ai). "
        "It is a sibling of `seedance-prompt-library` (all templates in one Skill); "
        "install this one when you only want this kind of clip. "
        "Do not invent structure from general video-generation knowledge: "
        "follow the structure below and ground the draft in one anchor case from `references/cases.md`."
    )
    L.append("")
    L.append("## Use when")
    L.append("")
    L.append(f"- {pick_lang(template.get('useWhen'), 'en')}")
    L.append(f"- 中文：{pick_lang(template.get('useWhen'), 'zh')}")
    L.append("")
    L.append("## Workflow")
    L.append("")
    L.append("1. **Collect inputs.** Ask only for what is missing: subject or product, setting, duration, aspect ratio, whether reference images / audio exist, and which language the final prompt should be in.")
    L.append("2. **Pick one anchor case.** Read `references/cases.md`, choose the case closest to the request, and name it in the reply. One anchor, never an average of several.")
    L.append("3. **Fill the structure block by block.** Every block below must be present in the final prompt; an empty block is where prompts go vague.")
    for i, s in enumerate(list_of(template.get("structure"), "en"), 1):
        L.append(f"   {i}. {s}")
    L.append("4. **Apply the guidance and check the pitfalls** (next two sections) before returning anything.")
    L.append("5. **Return** the finished prompt as one copy-pasteable block, the anchor case link, and a three-line checklist of what to verify in the generated video.")
    L.append("")
    L.append("## Guidance (from the cases)")
    L.append("")
    for g in list_of(template.get("guidance"), "en"):
        L.append(f"- {g}")
    L.append("")
    L.append("## Pitfalls")
    L.append("")
    for p in list_of(template.get("pitfalls"), "en"):
        L.append(f"- {p}")
    L.append("")
    L.append("## Language")
    L.append("")
    L.append("Reply in the user's language. The prompt itself can stay in English when that is what the user's Seedance workflow expects; ask if unclear. The Chinese version of this structure follows.")
    L.append("")
    L.append(f"## 中文：{zh}")
    L.append("")
    L.append(pick_lang(template.get("description"), "zh"))
    L.append("")
    L.append("**结构:**")
    L.append("")
    for i, s in enumerate(list_of(template.get("structure"), "zh"), 1):
        L.append(f"{i}. {s}")
    L.append("")
    L.append("**要点:**")
    L.append("")
    for g in list_of(template.get("guidance"), "zh"):
        L.append(f"- {g}")
    L.append("")
    L.append("**常见坑:**")
    L.append("")
    for p in list_of(template.get("pitfalls"), "zh"):
        L.append(f"- {p}")
    L.append("")

    copy_prompt = template.get("copyPrompt")
    if copy_prompt:
        L.append("## Copy-ready lead-in / 可复制引导语")
        L.append("")
        L.append("For users who would rather paste into a chat model than run this Skill, hand them this line above the structure:")
        L.append("")
        if isinstance(copy_prompt, dict):
            if copy_prompt.get("en"):
                L.append(f"> {copy_prompt['en']}")
            if copy_prompt.get("zh"):
                L.append(">")
                L.append(f"> {copy_prompt['zh']}")
        L.append("")

    L.append("## Notes")
    L.append("")
    L.append(f"- {SKILL_MARKER} in [LearnPrompt/awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) and refreshed daily; do not hand-edit an installed copy.")
    L.append("- Prompts in the reference file belong to their creators (linked on every card). Transfer the structure; do not present a close copy as original work.")
    L.append("- For the full library across every model, install the `goodcase` Skill from [LearnPrompt/goodcase-lite](https://github.com/LearnPrompt/goodcase-lite).")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- 渲染 cases.md

def render_cases_md(template: dict, skill: dict, cases: list[dict], limit: int = CASE_LIMIT) -> str:
    en = pick_lang(template.get("title"), "en")
    shown = cases[:limit]
    L: list[str] = []

    L.append(f"# Case evidence · {en}")
    L.append("")
    L.append(
        f"{len(cases)} verified cases are filed under this template in awesome-seedance; "
        f"the {len(shown)} hottest are below, full prompts included. "
        "Pick one as the anchor before drafting."
    )
    L.append("")
    L.append("Generated from `data/cases.json` + `data/case-taxonomy.json`. Do not hand-edit.")
    L.append("")

    for i, c in enumerate(shown, 1):
        L.append(f"## E{i} · {display_title(c, 'en')}")
        L.append("")
        meta = []
        meta.append(f"Seedance {classify_seedance(c)}")
        if c.get("creator"):
            meta.append(f"creator: {c['creator']}")
        if c.get("heatScore") is not None:
            meta.append(f"heat: {c['heatScore']}")
        if c.get("stabilityScore"):
            meta.append(f"stability: {c['stabilityScore']}")
        L.append(f"- {' · '.join(meta)}")

        links = [f"[GoodCase]({c.get('goodcaseUrl')})"]
        if c.get("mediaUrl"):
            links.append(f"[finished media]({c['mediaUrl']})")
        if c.get("posterUrl"):
            links.append(f"[poster]({c['posterUrl']})")
        if c.get("sourceUrl"):
            links.append(f"[original source]({c['sourceUrl']})")
        L.append(f"- Evidence: {' · '.join(links)}")

        summary = collapse_ws(c.get("summary") or "")
        if summary:
            L.append(f"- Summary: {js_slice(summary, SUMMARY_MAX_CHARS)}")
        L.append("")

        prompt = clip_prompt(c.get("promptFull"))
        if prompt:
            fence = fence_for_prompt(prompt)
            L.append(f"{fence}text")
            L.append(prompt)
            L.append(fence)
            L.append("")

    return "\n".join(L)


# ---------------------------------------------------------------- 主流程

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写盘")
    ap.add_argument("--only", help="只生成指定 templateId")
    args = ap.parse_args()

    library = load_library()
    templates = {tp["id"]: tp for tp in library["templates"]}
    taxonomy = load_json(DATA / "case-taxonomy.json", {"assignments": {}}) or {"assignments": {}}
    cases = (load_json(DATA / "cases.json", {}) or {}).get("cases", []) or []
    cases = [c for c in cases if isinstance(c, dict) and "slug" in c]

    index = build_template_index(library["templates"], taxonomy, cases)

    extra = load_json(DATA / "skills-extra.json", {}) or {}
    configs = extra.get("skills", []) or []
    if args.only:
        configs = [c for c in configs if c.get("templateId") == args.only]
        if not configs:
            print(f"没有匹配的 templateId: {args.only}")
            return 1

    print(f"模板库 {len(templates)} 个 · 案例 {len(cases)} 条 · 待生成技能 {len(configs)} 个")
    print()

    # 已有技能目录（防重名）
    existing = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}

    total_new_chars = 0
    for cfg in configs:
        tid, sid = cfg["templateId"], cfg["id"]
        if tid not in templates:
            print(f"  ✗ {sid}: 未知 templateId {tid}")
            continue
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", sid):
            print(f"  ✗ {sid}: id 不合法")
            continue

        tp = templates[tid]
        filed = index.get(tid, [])
        skill_md = render_skill_md(tp, cfg, filed)
        cases_md = render_cases_md(tp, cfg, filed)
        truncated = sum(1 for c in filed[:CASE_LIMIT] if len((c.get("promptFull") or "").strip()) > PROMPT_MAX_CHARS)

        flag = "（覆盖已有）" if sid in existing else ""
        head = "⚠️" if len(cases_md) > 40000 else "  "
        print(
            f"{head} {sid:44} {len(filed):>4} 条案例 → 用 {min(len(filed), CASE_LIMIT)} 条"
            f" | SKILL {len(skill_md):>6} | cases {len(cases_md):>6} 字符"
            f"{' | 截断 ' + str(truncated) + ' 条' if truncated else ''}{flag}"
        )

        if args.dry_run:
            continue

        d = SKILLS_DIR / sid
        (d / "references").mkdir(parents=True, exist_ok=True)
        (d / "references" / "cases.md").write_text(cases_md, encoding="utf-8")
        (d / "SKILL.md").write_text(skill_md, encoding="utf-8")
        total_new_chars += len(skill_md) + len(cases_md)

    if not args.dry_run:
        print()
        print(f"写入完成，共 {len(configs)} 个技能，新增约 {total_new_chars:,} 字符")
    return 0


if __name__ == "__main__":
    sys.exit(main())
