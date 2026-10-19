# -*- coding: utf-8 -*-
"""
后端服务 —— 提供前端调用的 HTTP 接口。

启动：python run.py
接口：
    GET  /api/skills          查看加载到哪些 skill
    GET  /api/config          查看当前大模型配置（key 打码）
    POST /api/config          改大模型配置
    POST /api/chat            一次性返回：选skill → 生成 → 质检
    POST /api/stream          流式返回，前端能实时看到每一步
    GET  /api/update/status   上次检查上游的时间 + 当前数据版本
    POST /api/update/run      手动检查上游并同步（归类表 + 案例 + 重生成技能）
    GET  /api/cases           案例库列表（分页 + 搜索 + 筛选，只返回轻量字段）
    GET  /api/cases/{slug}    单条案例详情（含完整 prompt）
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .agent import Agent, LLMConfig
from .skill_loader import SkillLoader

# ---------------------------------------------------------------- 路径与配置

BASE_DIR = Path(__file__).resolve().parent.parent
# 默认读【项目自带的 skills 目录】，这样整个文件夹拷走就能跑。
# 想改读别处：环境变量 SKILLS_DIR，或 run.py --skills
SKILLS_DIR = Path(os.environ.get("SKILLS_DIR") or (BASE_DIR / "skills"))
STATIC_DIR = BASE_DIR / "static"
CONFIG_FILE = BASE_DIR / "config.json"

# 上游同步
SYNC_SCRIPT = BASE_DIR / "scripts" / "sync_upstream.py"
SYNC_STATUS_FILE = BASE_DIR / "data" / "update-status.json"
SYNC_TIMEOUT = 300          # 秒。正常几秒就完；给足余量防止网络抖动误判超时
_sync_lock = threading.Lock()


def _load_cfg() -> LLMConfig:
    """配置优先级：config.json > 环境变量 > 默认值。"""
    data: dict = {}
    if CONFIG_FILE.is_file():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    return LLMConfig(
        base_url=data.get("base_url")
        or os.environ.get("LLM_BASE_URL")
        or "https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=data.get("api_key") or os.environ.get("DASHSCOPE_API_KEY") or "",
        model=data.get("model") or os.environ.get("LLM_MODEL") or "qwen-plus",
        temperature=float(data.get("temperature", 0.7)),
    )


# 白名单：默认不过滤（项目自带的 skills 目录里放什么就加载什么）。
# 如果想过滤，在 config.json 里配 "skills_whitelist": ["名字1","名字2"]
def _load_skill_whitelist() -> list[str] | None:
    if CONFIG_FILE.is_file():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            wl = data.get("skills_whitelist")
            if isinstance(wl, list) and wl:
                return [str(x) for x in wl]
        except Exception:
            pass
    return None   # None = 不过滤，全加载


def _save_cfg(cfg: LLMConfig) -> None:
    """只覆盖大模型那四个键，其余内容原样保留。

    以前这里是把整个文件重写成四个键，结果网页端点一次「保存设置」，
    config.json 里的 feishu.app_id / app_secret 就被抹掉了 —— 飞书通道
    下次启动直接报「还没有 feishu.app_id」，而且要重新去后台抄一遍密钥。
    """
    data: dict = {}
    if CONFIG_FILE.is_file():
        try:
            loaded = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}          # 文件坏了就重新写一份，别让保存失败

    data.update({
        "base_url": cfg.base_url,
        "api_key": cfg.api_key,
        "model": cfg.model,
        "temperature": cfg.temperature,
    })
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------- 初始化

app = FastAPI(title="提示词智能体", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------- 局域网访客只读
# 这个服务本来只监听 127.0.0.1，没有任何鉴权，所以以前不用管权限。
# 一旦用 --host 0.0.0.0 开到局域网，同一网段的人就什么都能干：
# 改模型配置、拿你的 key 生成提示词（花你的钱）。但「看案例」是只读需求，
# 所以这里按来源 IP 区分：本机全权限，其他机器只允许 GET。
# 想让访客也能生成，启动时加 --allow-guest-write（或 GUEST_READONLY=0）。
_GUEST_READONLY = os.environ.get("GUEST_READONLY", "1") != "0"
_LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}


@app.middleware("http")
async def _block_guest_writes(request, call_next):
    if _GUEST_READONLY and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        peer = request.client.host if request.client else ""
        if peer not in _LOCAL_HOSTS:
            return JSONResponse(
                status_code=403,
                content={"detail": "局域网访客为只读模式：可以浏览案例，但不能生成或改配置。"
                                   "（要放开，启动时加 --allow-guest-write）"},
            )
    return await call_next(request)

loader = SkillLoader(SKILLS_DIR, include=_load_skill_whitelist())
cfg = _load_cfg()
agent = Agent(loader, cfg)


# ---------------------------------------------------------------- 请求模型

class ChatRequest(BaseModel):
    message: str
    skills: list[str] | None = None      # 手动指定 skill，不传就让模型自己选
    do_lint: bool = True                 # 是否跑质检
    history: list[dict] | None = None    # 多轮对话：之前的往来（role/content）
    last_skills: list[str] | None = None # 上一轮用过的技能，追问时兜底


class ConfigRequest(BaseModel):
    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None
    temperature: float | None = None


# ---------------------------------------------------------------- 接口

@app.get("/api/skills")
def get_skills():
    return {
        "skills_dir": str(SKILLS_DIR),
        "count": len(loader.skills),
        "skills": loader.catalog(),
    }


@app.post("/api/skills/reload")
def reload_skills():
    """重新扫描技能目录。顺便重读白名单，这样改完 config.json 不用重启。"""
    loader.include = [s.lower() for s in _load_skill_whitelist()] if _load_skill_whitelist() else None
    names = loader.reload()
    return {"ok": True, "count": len(names), "skills": names}


# ---------------------------------------------------------------- 上游同步

def _read_sync_status() -> dict:
    """读状态文件。没跑过就返回一个空壳，前端好渲染。"""
    if not SYNC_STATUS_FILE.is_file():
        return {
            "ok": None,
            "neverRun": True,
            "checkedAt": None,
            "changed": False,
            "message": "还没检查过",
            "dataVersion": {},
        }
    try:
        data = json.loads(SYNC_STATUS_FILE.read_text(encoding="utf-8"))
        data["neverRun"] = False
        return data
    except Exception as e:                          # noqa: BLE001
        return {
            "ok": False,
            "neverRun": False,
            "checkedAt": None,
            "changed": False,
            "message": f"状态文件读不出来：{e}",
            "dataVersion": {},
        }


@app.get("/api/update/status")
def update_status():
    """给前端显示「上次检查时间 / 数据版本」。"""
    return _read_sync_status()


@app.post("/api/update/run")
def update_run():
    """手动跑一次上游同步。秒级返回；同一时间只允许一个。"""
    if not _sync_lock.acquire(blocking=False):
        raise HTTPException(409, "已经有一个检查在跑了，等它结束再点。")
    try:
        if not SYNC_SCRIPT.is_file():
            raise HTTPException(500, f"找不到同步脚本：{SYNC_SCRIPT}")

        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        try:
            proc = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT)],
                cwd=str(BASE_DIR),
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", env=env, timeout=SYNC_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "检查超时了，多半是网络连不上上游。")
        except Exception as e:                      # noqa: BLE001
            raise HTTPException(500, f"跑同步脚本失败：{e}")

        status = _read_sync_status()
        status["stdout"] = (proc.stdout or "")[-4000:]
        if proc.stderr:
            status["stderr"] = proc.stderr[-2000:]

        # 技能文件可能被重写过，让内存里的缓存跟上
        try:
            names = loader.reload()
            status["skillCount"] = len(names)
        except Exception:                           # noqa: BLE001
            pass

        return status
    finally:
        _sync_lock.release()


# ---------------------------------------------------------------- 大模型配置

@app.get("/api/config")
def get_config():
    def mask(k: str) -> str:
        if not k:
            return ""
        return k[:6] + "****" + k[-4:] if len(k) > 12 else "****"

    return {
        "base_url": cfg.base_url,
        "model": cfg.model,
        "temperature": cfg.temperature,
        "api_key_masked": mask(cfg.api_key),
        "api_key_ready": bool(cfg.api_key),
    }


@app.post("/api/config")
def set_config(req: ConfigRequest):
    global cfg, agent
    if req.base_url is not None:
        cfg.base_url = req.base_url
    if req.api_key:
        cfg.api_key = req.api_key
    if req.model is not None:
        cfg.model = req.model
    if req.temperature is not None:
        cfg.temperature = req.temperature

    _save_cfg(cfg)
    agent = Agent(loader, cfg)   # 配置变了，重建一次
    return {"ok": True}


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not cfg.api_key:
        raise HTTPException(400, "还没配置 API Key，请先到设置里填。")

    steps: list[dict] = []
    result = agent.run_full(
        user_input=req.message,
        forced=req.skills,
        do_lint=req.do_lint,
        history=req.history,
        last_skills=req.last_skills,
        on_step=lambda s, p: steps.append({"stage": s, **p}),
    )
    result["steps"] = steps
    return result


@app.post("/api/stream")
def stream(req: ChatRequest):
    """SSE 流式：每完成一步就推一次，前端能实时看到进度。"""
    if not cfg.api_key:
        raise HTTPException(400, "还没配置 API Key。")

    def gen():
        queue: list[dict] = []

        def on_step(stage: str, payload: dict):
            queue.append({"stage": stage, **payload})

        # 因为 run_full 是同步的，这里用「执行完一次性推」的简化实现，
        # 保证前端至少能拿到完整的分步记录；真流式可后续换 async 版本。
        try:
            result = agent.run_full(
                user_input=req.message,
                forced=req.skills,
                do_lint=req.do_lint,
                history=req.history,
                last_skills=req.last_skills,
                on_step=on_step,
            )
            for item in queue:
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'stage': 'done', 'result': result}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------- 案例库
# 数据源就是 data/cases.json（上游同步脚本维护它）。这里只读、不写。
# 列表接口只吐轻量字段，完整 prompt 走详情接口 —— 834 条的 prompt 加起来 3.9 MB，
# 一次全塞给前端首屏会明显变慢。

CASES_FILE = BASE_DIR / "data" / "cases.json"
TAXONOMY_FILE = BASE_DIR / "data" / "case-taxonomy.json"
STYLE_LIB_FILE = BASE_DIR / "data" / "style-library.json"
TEMPLATES_LOCAL_FILE = BASE_DIR / "data" / "templates-local.json"

CASE_PAGE_DEFAULT = 60
CASE_PAGE_MAX = 120
CREATOR_FACET_TOP = 40

# 版本分档口径与上游 scripts/lib/render.mjs 完全一致：
# models 里的明确版本（多个取最高）> 标题/摘要里写的版本 > 兜底 2.0。裸标 "Seedance" 不参与。
SEEDANCE_MODEL_RE = re.compile(r"^\s*seedance(?:[\s_-]*(\d+(?:\.\d+)?))?\s*(.*)$", re.I)
SEEDANCE_TEXT_RE = re.compile(r"seedance[\s_-]*(\d+(?:\.\d+)?)", re.I)

_cases_lock = threading.Lock()
_cases_cache: dict = {"key": None, "list": [], "by_slug": {}, "hay": {},
                      "facets": {}, "version": {}}


def _seedance_version_of(model) -> str | None:
    """单个模型标签的档位："2.5" / "2.0" / "unspecified"，非 Seedance 返回 None。"""
    if not isinstance(model, str):
        return None
    m = SEEDANCE_MODEL_RE.match(model)
    if not m:
        return None
    if not m.group(1):
        return "unspecified"
    return "2.5" if float(m.group(1)) >= 2.5 else "2.0"


def _classify_seedance(case: dict) -> str:
    """整条案例的版本档，只有 2.5 / 2.0 两档，每条只算一次。"""
    for model in case.get("models") or []:
        if _seedance_version_of(model) == "2.5":
            return "2.5"
    for model in case.get("models") or []:
        if _seedance_version_of(model) == "2.0":
            return "2.0"
    text = f"{case.get('title') or ''}\n{case.get('summary') or ''}"
    found = ["2.5" if float(v) >= 2.5 else "2.0" for v in SEEDANCE_TEXT_RE.findall(text)]
    if "2.5" in found:
        return "2.5"
    return "2.0"          # 含 found 为空的情况：兜底 2.0


def _load_categories() -> dict[str, str]:
    """模板大类 id → 中文名。"""
    try:
        lib = json.loads(STYLE_LIB_FILE.read_text(encoding="utf-8"))
        out = {}
        for c in lib.get("categories") or []:
            title = c.get("title") or {}
            out[c.get("id", "")] = title.get("zh") or title.get("en") or c.get("id", "")
        return out
    except Exception:                               # noqa: BLE001
        return {}


def _load_templates() -> dict[str, dict]:
    """模板 id → {name, category}。
    合并 data/style-library.json 与 data/templates-local.json，
    口径与上游 scripts/lib/library.mjs 一致（overrides 按语言逐字段合并，templates 补全新增项）。"""
    tpl: dict[str, dict] = {}
    try:
        lib = json.loads(STYLE_LIB_FILE.read_text(encoding="utf-8"))
        for t in lib.get("templates") or []:
            if t.get("id"):
                tpl[t["id"]] = dict(t)
    except Exception:                               # noqa: BLE001
        pass

    try:
        loc = json.loads(TEMPLATES_LOCAL_FILE.read_text(encoding="utf-8"))
        for tid, patch in (loc.get("overrides") or {}).items():
            if tid not in tpl or not isinstance(patch, dict):
                continue
            for k, v in patch.items():
                if isinstance(v, dict) and isinstance(tpl[tid].get(k), dict):
                    tpl[tid][k] = {**tpl[tid][k], **v}
                else:
                    tpl[tid][k] = v
        for t in loc.get("templates") or []:
            if t.get("id"):
                tpl.setdefault(t["id"], t)
    except Exception:                               # noqa: BLE001
        pass

    out: dict[str, dict] = {}
    for tid, t in tpl.items():
        title = t.get("title") or {}
        name = (title.get("zh") or title.get("en") or tid) if isinstance(title, dict) else tid
        out[tid] = {"id": tid, "name": name, "category": t.get("category") or ""}
    return out


def _cases_key() -> tuple:
    """缓存指纹：任一数据文件的 mtime 变了就重建。"""
    key = []
    for p in (CASES_FILE, TAXONOMY_FILE, STYLE_LIB_FILE, TEMPLATES_LOCAL_FILE):
        try:
            key.append(p.stat().st_mtime_ns)
        except OSError:
            key.append(0)
    return tuple(key)


def _build_cases() -> dict:
    """把 cases.json 整理成列表用/详情用两份结构，顺便算好筛选面板的计数。"""
    raw = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    cases = raw.get("cases") or []
    meta = raw.get("meta") or {}

    taxonomy: dict[str, str] = {}
    try:
        t = json.loads(TAXONOMY_FILE.read_text(encoding="utf-8"))
        taxonomy = {k: v for k, v in (t.get("assignments") or {}).items() if isinstance(v, str)}
    except Exception:                               # noqa: BLE001
        taxonomy = {}

    templates = _load_templates()
    categories = _load_categories()

    light: list[dict] = []
    by_slug: dict[str, dict] = {}
    hay: dict[str, str] = {}
    n_model: Counter = Counter()
    n_level: Counter = Counter()
    n_tpl: Counter = Counter()
    n_creator: Counter = Counter()

    for c in cases:
        slug = c.get("slug") or ""
        if not slug:
            continue
        tpl_id = taxonomy.get(slug) or ""
        model = _classify_seedance(c)
        tpl_name = (templates.get(tpl_id) or {}).get("name", "")

        light.append({
            "slug": slug,
            "title": c.get("title") or c.get("titleEn") or slug,
            "summary": (c.get("summary") or "").strip(),
            "poster": c.get("posterUrl") or "",
            "creator": c.get("creator") or "",
            "model": model,
            "template": tpl_id,
            "templateName": tpl_name,
            "heat": c.get("heatScore"),
            "stability": c.get("stabilityScore"),
            "level": c.get("evidenceLevel") or "",
            "publishedAt": c.get("sourcePublishedAt") or "",
            "retestCount": len(c.get("retests") or []),
            "tags": c.get("tags") or [],
        })
        by_slug[slug] = {**c, "model": model, "template": tpl_id, "templateName": tpl_name}

        # 搜索用的低配串：只留必要字段，避免每次请求都去 lower() 全文
        hay[slug] = "\n".join([
            str(c.get("title") or ""), str(c.get("titleEn") or ""),
            str(c.get("summary") or ""), str(c.get("creator") or ""),
            str(c.get("promptFull") or ""),
        ]).lower()

        n_model[model] += 1
        n_level[light[-1]["level"]] += 1
        n_creator[light[-1]["creator"]] += 1
        if tpl_id:
            n_tpl[tpl_id] += 1

    cat_of = {tid: t["category"] for tid, t in templates.items()}
    n_cat: Counter = Counter()
    for tid, cnt in n_tpl.items():
        n_cat[cat_of.get(tid, "")] += cnt

    facets = {
        "models": [{"v": v, "n": n_model.get(v, 0)} for v in ("2.5", "2.0")],
        "levels": [{"v": v, "n": n_level.get(v, 0)} for v in ("L2", "L1", "L0") if n_level.get(v)],
        "templates": sorted(
            [{"id": tid, "name": t["name"], "category": t["category"], "n": cnt}
             for tid, t in templates.items()
             if (cnt := n_tpl.get(tid, 0))],
            key=lambda x: (-x["n"], x["name"]),
        ),
        "categories": [
            {"id": cid, "name": categories.get(cid, cid), "n": cnt}
            for cid, cnt in n_cat.most_common()
        ],
        "creators": [{"v": v, "n": n} for v, n in n_creator.most_common(CREATOR_FACET_TOP)],
    }

    return {
        "key": _cases_key(),
        "list": light,
        "by_slug": by_slug,
        "hay": hay,
        "facets": facets,
        "version": {
            "exportedAt": meta.get("exportedAt", ""),
            "caseCount": meta.get("caseCount") or len(light),
        },
    }


def _get_cases() -> dict:
    """带缓存的读取。数据文件没变就直接用内存里的。"""
    key = _cases_key()
    if _cases_cache["key"] == key and _cases_cache["list"]:
        return _cases_cache
    with _cases_lock:
        if _cases_cache["key"] == key and _cases_cache["list"]:
            return _cases_cache
        if not CASES_FILE.is_file():
            return {"key": key, "list": [], "by_slug": {}, "hay": {},
                    "facets": {}, "version": {}}
        built = _build_cases()
        _cases_cache.update(built)
        return _cases_cache


def _sort_cases(items: list[dict], sort: str, by_slug: dict) -> list[dict]:
    def num(v):
        return v if isinstance(v, (int, float)) else -1

    if sort == "stable":
        return sorted(items, key=lambda x: (-num(x["stability"]), -num(x["heat"])))
    if sort == "new":
        return sorted(items, key=lambda x: (x["publishedAt"] or ""), reverse=True)
    if sort == "title":
        return sorted(items, key=lambda x: x["title"])
    return sorted(items, key=lambda x: -num(x["heat"]))          # 默认按热度


@app.get("/api/cases")
def list_cases(
    q: str = "", model: str = "", template: str = "", level: str = "",
    creator: str = "", sort: str = "hot",
    offset: int = 0, limit: int = CASE_PAGE_DEFAULT,
):
    """案例库列表。只返回轻量字段，完整 prompt 用 /api/cases/{slug} 取。"""
    cache = _get_cases()
    items = cache["list"]

    if model:
        items = [it for it in items if it["model"] == model]
    if template:
        items = [it for it in items if it["template"] == template]
    if level:
        items = [it for it in items if it["level"] == level]
    if creator:
        items = [it for it in items if it["creator"] == creator]

    word = q.strip().lower()
    if word:
        hay = cache["hay"]
        items = [it for it in items if word in hay.get(it["slug"], "")]

    items = _sort_cases(items, sort, cache["by_slug"])

    offset = max(0, offset)
    limit = max(1, min(limit, CASE_PAGE_MAX))
    page = items[offset:offset + limit]

    return {
        "total": len(items),
        "offset": offset,
        "limit": limit,
        "hasMore": offset + len(page) < len(items),
        "items": page,
        "facets": cache["facets"],
        "dataVersion": cache["version"],
    }


@app.get("/api/cases/{slug}")
def get_case(slug: str):
    """单条案例的完整内容。"""
    cache = _get_cases()
    case = cache["by_slug"].get(slug)
    if not case:
        raise HTTPException(404, f"没有这条案例：{slug}")

    prompt = case.get("promptFull") or ""
    retests = []
    for r in case.get("retests") or []:
        retests.append({
            "model": r.get("model") or "",
            "verdict": r.get("verdict") or "",
            "testedAt": r.get("testedAt") or "",
            "score": r.get("finalScore"),
            "artifactUrl": r.get("artifactUrl") or "",
        })

    return {
        "slug": case.get("slug"),
        "title": case.get("title") or case.get("titleEn") or slug,
        "titleEn": case.get("titleEn") or "",
        "summary": case.get("summary") or "",
        "summaryEn": case.get("summaryEn") or "",
        "promptFull": prompt,
        "promptChars": len(prompt),
        "promptLines": prompt.count("\n") + 1 if prompt else 0,
        "posterUrl": case.get("posterUrl") or "",
        "mediaUrl": case.get("mediaUrl") or "",
        "goodcaseUrl": case.get("goodcaseUrl") or "",
        "sourceUrl": case.get("sourceUrl") or "",
        "creator": case.get("creator") or "",
        "models": case.get("models") or [],
        "model": case.get("model") or "",
        "template": case.get("template") or "",
        "templateName": case.get("templateName") or "",
        "tags": case.get("tags") or [],
        "heatScore": case.get("heatScore"),
        "stabilityScore": case.get("stabilityScore"),
        "evidenceLevel": case.get("evidenceLevel") or "",
        "publishedAt": case.get("sourcePublishedAt") or "",
        "retests": retests,
        "retestSummary": case.get("retestSummary") or {},
        "dataVersion": cache["version"],
    }


# ---------------------------------------------------------------- 静态页面

if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
