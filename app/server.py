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
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
    CONFIG_FILE.write_text(
        json.dumps(
            {
                "base_url": cfg.base_url,
                "api_key": cfg.api_key,
                "model": cfg.model,
                "temperature": cfg.temperature,
            },
            ensure_ascii=False,
            indent=2,
        ),
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


# ---------------------------------------------------------------- 静态页面

if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
