# -*- coding: utf-8 -*-
r"""
飞书通道 —— 让提示词智能体在飞书里被 @ / 私聊调用。

流程：
    飞书会话（私聊 / 群 @）
       ↓  WebSocket 长连接（官方推荐，无需公网 IP）
    im.message.receive_v1 事件
       ↓  白名单过滤 + message_id 去重 + 剥 @占位
    Agent.run_full()  ←—— 复用网页端整条流水线（选技能→生成→质检）
       ↓
    飞书交互卡片回帖（超 30KB 自动降级纯文本分段）

跑法：  C:\Python314\python.exe feishu_bot.py
配置：  config.json 的 "feishu": {"app_id": "...", "app_secret": "..."}
白名单：data/feishu-whitelist.json  {"open_ids": [], "chat_ids": []}
        —— 陌生会话第一次发消息时，它的 open_id / chat_id 会打进日志，
           把那一行贴进白名单文件即可放行。
"""
from __future__ import annotations

import json
import re
import sys
import threading
import time
from collections import deque
from pathlib import Path

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    P2ImMessageReceiveV1,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
)

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from app.agent import Agent            # noqa: E402
from app.skill_loader import SkillLoader  # noqa: E402

CONFIG_FILE = BASE / "config.json"
WHITELIST_FILE = BASE / "data" / "feishu-whitelist.json"

# 生成耗时约 20~30 秒；同一会话的消息串行排队，避免回答乱序
MAX_HISTORY = 8          # 每个会话保留的上下文条数
CARD_LIMIT = 28_000      # 飞书卡片 JSON 的安全上限（官方约 30KB）
CHUNK = 3_500            # 纯文本降级时每段长度


# ---------------------------------------------------------------- 配置

def load_config() -> dict:
    data = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.is_file() else {}
    fs = data.get("feishu") or {}
    if not fs.get("app_id") or not fs.get("app_secret"):
        print("[飞书] config.json 里还没有 feishu.app_id / feishu.app_secret，退出。")
        sys.exit(2)
    return fs


def load_whitelist() -> dict:
    """{"open_ids": [...], "chat_ids": [...]}，文件不存在=空白名单（只记日志不放行）。"""
    if WHITELIST_FILE.is_file():
        try:
            return json.loads(WHITELIST_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"open_ids": [], "chat_ids": []}


# ---------------------------------------------------------------- 卡片

def md_to_lark(text: str) -> str:
    """轻量转换：飞书 lark_md 是 markdown 子集，把最常见的表格降级成易读行。"""
    out = []
    for line in text.split("\n"):
        s = line.rstrip()
        if s.strip().startswith("|") and set(s.replace("|", "").strip()) <= {"-", ":", " "}:
            continue                      # 表格分隔行直接去掉
        if s.strip().startswith("|"):
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            s = "　·　" + "　｜　".join(cells)
        out.append(s)
    return "\n".join(out)


def build_card(res: dict, elapsed: float, issues: str | None = None, revised: str | None = None) -> dict:
    """三段式卡片：① 提示词 ② 质检问题 ③ 纠正后的提示词（都是复制即用）。"""
    used = res.get("skills_used") or []
    skill_line = "、".join(used) if used else "（未用技能）"
    g = res.get("generate") or {}

    elements = [
        {"tag": "markdown",
         "content": "**① 提示词（复制即用）**\n" + md_to_lark(g.get("content") or "（没有产出）")},
    ]
    if issues:
        elements.append({"tag": "hr"})
        elements.append({"tag": "markdown",
                         "content": "**② 质检发现的问题**\n" + md_to_lark(issues)})
    if revised:
        elements.append({"tag": "hr"})
        elements.append({"tag": "markdown",
                         "content": "**③ 纠正后的提示词（复制即用）**\n" + md_to_lark(revised)})

    elements.append({"tag": "hr"})
    elements.append({"tag": "note", "elements": [
        {"tag": "plain_text",
         "content": f"技能：{skill_line}　·　耗时 {elapsed:.0f}s　·　发「新话题」清空本会话记忆"}
    ]})

    title = "🎬 提示词已生成（已按质检修正）" if revised else "🎬 分镜提示词已生成"
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "blue",
            "title": {"tag": "plain_text", "content": title},
        },
        "elements": elements,
    }


def card_size(card: dict) -> int:
    return len(json.dumps(card, ensure_ascii=False).encode("utf-8"))


# ---------------------------------------------------------------- 质检修正

# 2026-10-17：提示词与解析规则已收进 app/agent.py 的 Agent.revise()，
# 网页端和飞书共用同一份实现（此前只有飞书有，网页端跑完质检就结束，
# 用户看不到「纠正后的提示词」）。这里保留薄封装，调用方不用改。


def revise(agent, gen_skill: str, prompt_text: str, lint_text: str) -> tuple[str | None, str | None]:
    """质检后自动修正。返回 (问题清单, 修正后提示词)；失败返回 (None, None)。"""
    try:
        out = agent.revise(prompt_text, lint_text, skill_name=gen_skill)
    except Exception as e:
        print(f"[飞书] 质检修正失败：{e!r}", flush=True)
        return None, None
    if out.get("error"):
        print(f"[飞书] 质检修正失败：{out['error']}", flush=True)
    return out.get("issues"), out.get("revised")


# ---------------------------------------------------------------- 主逻辑

class FeishuChannel:
    def __init__(self):
        fs = load_config()
        self.app_id = fs["app_id"]
        self.app_secret = fs["app_secret"]

        self.loader = SkillLoader(str(BASE / "skills"))
        self.agent = Agent(self.loader, self._llm_cfg())

        self.whitelist = load_whitelist()
        self._seen: set[str] = set()                 # message_id 去重
        self._seen_lock = threading.Lock()
        self._sessions: dict[str, dict] = {}         # chat_id -> {"history": deque, "last_skills": []}
        self._sess_lock = threading.Lock()

        self.api = (lark.Client.builder()
                    .app_id(self.app_id).app_secret(self.app_secret).build())

    @staticmethod
    def _llm_cfg():
        """和 server.py 的 _load_cfg 同一套优先级，但不 import fastapi。"""
        from app.agent import LLMConfig
        import os
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.is_file() else {}
        return LLMConfig(
            base_url=data.get("base_url") or os.environ.get("LLM_BASE_URL") or "",
            api_key=data.get("api_key") or os.environ.get("DASHSCOPE_API_KEY") or "",
            model=data.get("model") or os.environ.get("LLM_MODEL") or "qwen-plus",
            temperature=float(data.get("temperature", 0.7)),
        )

    # ---------- 会话状态 ----------

    def _session(self, chat_id: str) -> dict:
        with self._sess_lock:
            if chat_id not in self._sessions:
                self._sessions[chat_id] = {
                    "history": deque(maxlen=MAX_HISTORY),
                    "last_skills": [],
                }
            return self._sessions[chat_id]

    # ---------- 发送 ----------

    def _reply_card(self, message_id: str, card: dict) -> None:
        req = (ReplyMessageRequest.builder()
               .message_id(message_id)
               .request_body(ReplyMessageRequestBody.builder()
                             .content(json.dumps(card, ensure_ascii=False))
                             .msg_type("interactive")
                             .build())
               .build())
        resp = self.api.im.v1.message.reply(req)
        if not resp.success():
            print(f"[飞书] 卡片回复失败 code={resp.code} msg={resp.msg}", flush=True)

    def _send_text(self, chat_id: str, text: str) -> None:
        req = (CreateMessageRequest.builder()
               .receive_id_type("chat_id")
               .request_body(CreateMessageRequestBody.builder()
                             .receive_id(chat_id)
                             .msg_type("text")
                             .content(json.dumps({"text": text}, ensure_ascii=False))
                             .build())
               .build())
        resp = self.api.im.v1.message.create(req)
        if not resp.success():
            print(f"[飞书] 文本发送失败 code={resp.code} msg={resp.msg}", flush=True)

    def _deliver(self, message_id: str, chat_id: str, res: dict, elapsed: float,
                 issues: str | None = None, revised: str | None = None) -> None:
        card = build_card(res, elapsed, issues, revised)
        if card_size(card) <= CARD_LIMIT:
            self._reply_card(message_id, card)
            return
        # 超限降级：纯文本分段（同样只给三段式内容）
        self._send_text(chat_id, "⚠️ 本轮内容较长，卡片放不下，改为分段发送：")
        g = res.get("generate") or {}
        parts = [g.get("content") or ""]
        if issues:
            parts.append("② 质检发现的问题\n" + issues)
        if revised:
            parts.append("③ 纠正后的提示词\n" + revised)
        for part in parts:
            for i in range(0, len(part), CHUNK):
                self._send_text(chat_id, part[i:i + CHUNK])

    # ---------- 事件处理 ----------

    def _allowed(self, open_id: str, chat_id: str) -> bool:
        # 每条消息现读白名单 —— 加人不用重启通道
        self.whitelist = load_whitelist()
        return (open_id in self.whitelist.get("open_ids", [])
                or chat_id in self.whitelist.get("chat_ids", []))

    @staticmethod
    def _extract_text(msg) -> tuple[str, bool]:
        """返回 (纯文本, 是否群聊)。剥掉 @占位；非文字消息返回空串。"""
        chat_type = getattr(msg, "chat_type", "") or ""
        if msg.message_type != "text":
            return "", chat_type == "group"
        try:
            payload = json.loads(msg.content or "{}")
        except Exception:
            return "", chat_type == "group"
        text = payload.get("text", "")
        text = re.sub(r"@_user_\d+", "", text)           # 群里 @机器人 的占位
        return text.strip(), chat_type == "group"

    def on_message(self, data: P2ImMessageReceiveV1) -> None:
        try:
            self._handle(data)
        except Exception as e:
            print(f"[飞书] 处理异常：{e!r}", flush=True)

    def _handle(self, data: P2ImMessageReceiveV1) -> None:
        event = data.event
        msg = event.message
        sender = (event.sender.sender_id.open_id or "") if event.sender else ""
        chat_id = msg.chat_id or ""
        message_id = msg.message_id or ""

        # ① 去重（飞书会重推事件）
        with self._seen_lock:
            if message_id in self._seen:
                return
            self._seen.add(message_id)
            if len(self._seen) > 5000:
                self._seen.clear()

        # ② 白名单（陌生人：只记日志，提示怎么放行）
        if not self._allowed(sender, chat_id):
            print(f"[飞书] 陌生会话，已忽略 → 把下面的行加进 {WHITELIST_FILE.name} 可放行：\n"
                  f"   open_id={sender}\n   chat_id={chat_id}", flush=True)
            return

        # ③ 群聊必须 @机器人
        text, is_group = self._extract_text(msg)
        if is_group and not (getattr(msg, "mentions", None) and len(msg.mentions) > 0):
            return
        if not text:
            self._send_text(chat_id, "目前只看得懂文字消息，发一段文字描述吧。")
            return

        sess = self._session(chat_id)

        # ④ 会话命令
        if text.strip() in ("新话题", "清空", "重置"):
            sess["history"].clear()
            sess["last_skills"] = []
            self._send_text(chat_id, "🧹 已清空本会话记忆，下一句当作新话题。")
            return

        # ⑤ 占位 + 干活（同一会话天然按消息到达顺序串行：WS 回调是顺序分发的）
        print(f"[飞书] 收到 chat={chat_id[:12]}… 文本={text[:60]!r}", flush=True)
        self._send_text(chat_id, "⏳ 收到，正在生成 → 质检 → 自动修正（约 40~60 秒）…")

        t0 = time.time()
        history = list(sess["history"]) or None
        last_skills = sess["last_skills"] or None
        try:
            res = self.agent.run_full(
                user_input=text,
                do_lint=True,
                history=history,
                last_skills=last_skills,
            )
        except Exception as e:
            self._send_text(chat_id, f"❌ 生成出错了：{e}")
            return

        if res.get("need_user_action"):
            self._send_text(chat_id, res.get("message") or "没找到合适的技能，换个说法试试。")
            return

        # ⑥ 记忆
        sess["history"].append({"role": "user", "content": text})
        sess["history"].append({"role": "assistant",
                                "content": (res.get("generate") or {}).get("content", "")})
        sess["last_skills"] = res.get("skills_used") or []

        elapsed = time.time() - t0

        # ⑥.5 质检修正：现在由 run_full 内部完成（见 Agent._run_after_pick ⑤），
        # 直接取结果即可 —— 再调一遍 revise 会让同一次需求多跑 20 秒和一份 token。
        # 只有老版本 run_full（没有该字段）才回退到本地补跑。
        rev = res.get("revision") or {}
        issues, revised = rev.get("issues"), rev.get("revised")
        if not (issues or revised):
            lint_text = (res.get("lint") or {}).get("content") or ""
            gen_text = (res.get("generate") or {}).get("content") or ""
            gen_skill = next((n for n in (res.get("skills_used") or []) if "lint" not in n.lower()),
                             "seedance-prompt-library")
            if lint_text and gen_text and not res.get("lint_only"):
                issues, revised = revise(self.agent, gen_skill, gen_text, lint_text)

        self._deliver(message_id, chat_id, res, elapsed, issues, revised)
        print(f"[飞书] 已回复 chat={chat_id[:12]}… 耗时 {elapsed:.0f}s "
              f"({'含修正' if revised else '未修正'})", flush=True)

    # ---------- 启动 ----------

    def run(self) -> None:
        event_handler = (lark.EventDispatcherHandler.builder("", "")
                         .register_p2_im_message_receive_v1(self.on_message)
                         .build())
        ws = lark.ws.Client(self.app_id, self.app_secret,
                            event_handler=event_handler,
                            log_level=lark.LogLevel.WARNING)
        print(f"[飞书] 长连接启动中（app_id={self.app_id}）…  Ctrl+C 退出", flush=True)
        ws.start()


if __name__ == "__main__":
    FeishuChannel().run()
