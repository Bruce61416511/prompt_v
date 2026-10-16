# -*- coding: utf-8 -*-
"""
智能体调度器 —— 让「大模型自己决定用哪个 skill」。

流程（这就是你要的 "load skill"）：

    用户输入
       ↓
    ① 选 skill：把 skill 清单（只有 name + description）给模型，让它挑
       ↓
    ② 注入：把挑中的 SKILL.md 全文拼进 system prompt
       ↓
    ③ 生成：模型按 skill 规则写出分镜提示词
       ↓
    ④ 质检（可选）：再跑一遍 seedance-prompt-lint
       ↓
    输出
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Callable, Iterable

from openai import OpenAI

from .skill_loader import SkillLoader


# ---------------------------------------------------------------- 配置

@dataclass
class LLMConfig:
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key: str = ""
    model: str = "qwen-plus"
    temperature: float = 0.7


# ---------------------------------------------------------------- 调度器

class Agent:
    def __init__(self, loader: SkillLoader, cfg: LLMConfig):
        self.loader = loader
        self.cfg = cfg
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None or self._client.api_key != self.cfg.api_key:
            self._client = OpenAI(
                api_key=self.cfg.api_key,
                base_url=self.cfg.base_url,
                timeout=300,
            )
        return self._client

    # ------------------------------------------------------------ ① 选 skill

    def pick_skills(
        self,
        user_input: str,
        forced: list[str] | None = None,
        history: list[dict] | None = None,
        last_skills: list[str] | None = None,
    ) -> tuple[list[str], str]:
        """让大模型从技能清单里挑出该用的 skill。

        forced 非空时直接用它，跳过模型判断。
        模型选不出来就返回空列表 —— 不猜，把判断权交回用户。

        history / last_skills 是给【多轮对话】用的（2026-10-16 加）：
            用户第二轮往往只说「再改短点」「换成口播版」——光看这 5 个字，
            模型根本判断不出该用哪个技能，会被误判成「没找到合适技能」。
            所以要把上文（最近几条）+ 上一轮用过的技能一起给它看。

        返回 (技能列表, 来源)。来源取值：
            "user"   用户手动指定
            "model"  模型自己选的
            "reuse"  模型没选出来，沿用上一轮的技能（追问兜底）
        """
        if forced:
            return [n for n in forced if n in self.loader.skills], "user"
        if not self.loader.skills:
            return [], "model"

        # 组装上文摘要：只带最近 4 条，每条截断，够模型判断「这是不是同一件事」就行
        ctx = ""
        if history:
            recent: list[str] = []
            for m in history[-4:]:
                role = "用户" if m.get("role") == "user" else "助手"
                content = str(m.get("content") or "").replace("\n", " ")
                recent.append(f"  {role}：{content[:400]}")
            if recent:
                ctx = "以下是这段对话之前的内容（节选，用于理解上下文）：\n" + "\n".join(recent) + "\n\n"

        # 把「上一轮用了哪些技能」明写出来。
        # 2026-10-16 实测：只在上文里塞对话内容不够 —— 模型会把「再短一点，
        # 第二个镜头换成特写」判给另一个沾边的技能（workflow 而非 library），
        # 导致同一个需求两轮产出两套风格。直接点名就稳了。
        prev_line = ""
        if last_skills:
            valid_prev = [n for n in last_skills if n in self.loader.skills]
            if valid_prev:
                prev_line = f"上一轮用过的技能是：{'、'.join(valid_prev)}。\n\n"

        catalog = self.loader.catalog_for_llm()
        judge_prompt = (
            "你是一个调度器。下面是一个「技能包清单」，每条是 `名称：描述`。\n\n"
            f"{catalog}\n\n"
            f"{ctx}"
            f"{prev_line}"
            "现在用户提出了一个需求，请判断需要加载哪些技能包来完成它。\n"
            "规则：\n"
            "1. 只从上面的清单里选，不要编造名称。\n"
            "2. 只选「真正能完成这个需求」的技能。不相关的、只是沾边的，一律不要选。\n"
            "3. 大部分情况只选 1 个技能。只有当用户的需求确实需要多个技能配合时才多选，\n"
            "   例如用户明确要求「写完顺便检查一下」，可以同时选生成类和质检类。\n"
            "4. 用户只是要「检查/质检提示词」，就只选质检类技能 —— 不要连带选生成类。\n"
            "5. 【重要】如果这句话是对上文的追问或修改（例如「再短一点」「换个口播版」\n"
            "   「把第 2 个镜头改一下」「再来一版」），它和上文是同一个需求，\n"
            "   必须沿用「上一轮用过的技能」，不要换成别的技能。\n"
            "6. 如果从清单里找不到能完成这个需求的技能，返回空数组 []。\n"
            "   宁可返回空，也不要勉强选一个沾边的技能。\n"
            "7. 输出严格的 JSON 数组，例如 [\"技能名\"]，不要任何解释。\n\n"
            f"用户需求：{user_input}"
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.cfg.model,
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0,
            )
            raw = (resp.choices[0].message.content or "").strip()
            picked = self._extract_json_array(raw)
        except Exception:
            picked = []

        picked = [n for n in picked if n in self.loader.skills]
        if picked:
            return picked, "model"

        # 兜底：模型没选出来，但这是在多轮对话里、上一轮刚用过技能 → 沿用。
        # 不然「再改短点」这种追问会被直接拒掉。
        if history and last_skills:
            reuse = [n for n in last_skills if n in self.loader.skills]
            if reuse:
                return reuse, "reuse"

        return [], "model"

    @staticmethod
    def _extract_json_array(text: str) -> list[str]:
        m = re.search(r"\[.*?\]", text, re.DOTALL)
        if not m:
            return []
        try:
            data = json.loads(m.group(0))
            return [str(x) for x in data if isinstance(x, (str, int))]
        except Exception:
            return []

    # 说明：这里原本有个 _main_skill() 兜底 —— 模型选不出来时硬塞一个
    # 名字含 "official"/"seedance25" 的技能。2026-10-16 按用户要求删除。
    # 理由：兜底会掩盖「用户意图不明确」这个信号，把不相关的技能塞进
    # system prompt，产出驴唇不对马嘴的结果。正确做法是如实告诉用户
    # 「没找到合适的技能」，让用户补充或换个说法。


    # ------------------------------------------------------------ ②③ 生成

    # read_reference 工具声明（OpenAI function-calling 格式）。
    # 作用：大附件（如 39 万字节的官方手册）不内联，模型需要时自己取。
    _READ_REF_TOOL = {
        "type": "function",
        "function": {
            "name": "read_reference",
            "description": (
                "读取当前已挂载技能包的参考资料全文。"
                "凡是 system prompt 里标注「需按需读取」的资料，"
                "都必须先调用本工具读出来，再动笔写。"
                "不要凭空推测资料内容，也不要凭通用知识替代它。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": "技能名，例如 seedance-prompt-library",
                    },
                    "filename": {
                        "type": "string",
                        "description": "资料文件名，例如 style-library.md",
                    },
                },
                "required": ["skill", "filename"],
            },
        },
    }

    # 一次对话里最多允许模型取几次资料（防止反复拉大文件烧 token）
    MAX_REF_READS = 3

    # 单份资料回填给模型的字符上限。
    #
    # 历史：这里原来是 80_000，是拍脑袋定的「防上下文撑爆」。
    # 结果把 seedance-prompt-library 的模板库（106,284 字符）砍掉后 26%，
    # 最后 5 个模板（3d-cartoon / epic-fantasy-scifi / sports-extreme /
    # game-ui-livestream / food-asmr）模型永远看不到，正文里还会冒一句
    # 「资料较长，已截断」。
    #
    # 2026-10-16 实测校准后改成 150_000：
    #   整份模板库 106,284 字符灌进去，输入只有 35,339 tokens（≈0.33 token/字符，
    #   因为它是中英双语，英文约 4 字符/token）。离 64k 上下文上限还很远。
    # 按纯中文估算要保守些（约 0.7 token/字符）→ 150k 字符 ≈ 105k tokens 会超，
    # 所以这个值不要盲目再往上调；真要支持更大的附件，应该改成「按章节取」而不是继续放宽。
    REF_READ_MAX_CHARS = 150_000

    def generate(
        self,
        user_input: str,
        skill_names: list[str],
        history: list[dict] | None = None,
        temperature: float | None = None,
    ) -> dict:
        """加载 skill → 生成提示词。"""
        system, truncated = self.loader.build_system_prompt(skill_names)

        if not system:
            system = "你是一个专业的 AI 视频提示词工程师。请根据用户需求写出分镜提示词。"

        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(history[-8:])  # 只带最近几轮，防超长
        messages.append({"role": "user", "content": user_input})

        # 有「按需取」的附件时才给模型工具，否则不给（省 token、也免得它乱调）
        # ⚠️ 判断用 info["inline"] 这个「一次定死」的分类标记，
        #    不要用 info["content"] —— 它会被 read_reference 缓存污染。
        lazy_names = [
            f"{n}/{k}"
            for n in skill_names if n in self.loader.skills
            for k, v in self.loader.skills[n].references.items()
            if not v.get("inline")
        ]
        tools = [self._READ_REF_TOOL] if lazy_names else None

        t0 = time.time()
        ref_reads: list[str] = []
        usage = None
        nudged = False
        fallback_reads = 0

        for _ in range(self.MAX_REF_READS * 2 + 3):
            kwargs = {
                "model": self.cfg.model,
                "messages": messages,
                "temperature": self.cfg.temperature if temperature is None else temperature,
            }
            if tools:
                kwargs["tools"] = tools

            resp = self.client.chat.completions.create(**kwargs)
            usage = getattr(resp, "usage", None) or usage
            msg = resp.choices[0].message

            calls = getattr(msg, "tool_calls", None)
            text = msg.content or ""

            if not calls:
                # ---- 兜底 1：模型把工具调用「说」成了文本 ----
                # 2026-10-16 实测：deepseek-chat 约有一半概率不走结构化 tool_calls，
                # 而是吐 DeepSeek 的专有标记：
                #     <｜｜DSML｜｜ invoke name="read_reference">
                #     <｜｜DSML｜｜ parameter name="path">references/style-library.md</...
                # 或干脆写成 `read_reference("style-library.md")` 这种大白话。
                # 结果是 ref_reads 为空、正文只有一百多字，用户看到「我取不到，你贴给我吧」。
                #
                # 对策不解析 DSML 语法（各家格式不同、版本会变），只认一件事：
                #   「已知附件文件名有没有出现在模型的回复里」—— 最稳。
                wanted = [
                    n for n in lazy_names
                    if n.split("/", 1)[-1] in text and n not in ref_reads
                ]
                if wanted and fallback_reads < self.MAX_REF_READS and len(text) < 4000:
                    fallback_reads += 1
                    messages.append({"role": "assistant", "content": text})
                    blocks: list[str] = []
                    for ln in wanted:
                        skill, _, fname = ln.partition("/")
                        try:
                            body = self.loader.read_reference(skill, fname)
                        except Exception as e:
                            body = f"读取失败：{e}"
                        ref_reads.append(ln)
                        if len(body) > self.REF_READ_MAX_CHARS:
                            body = body[: self.REF_READ_MAX_CHARS] + "\n\n…（资料过长，已截断）"
                        blocks.append(f"【{ln}】\n\n{body}")
                    messages.append({
                        "role": "user",
                        "content": (
                            "（系统）已按你的要求读取参考资料，内容如下：\n\n"
                            + "\n\n".join(blocks)
                            + "\n\n请据此产出最终结果，不要再重复请求读取。"
                        ),
                    })
                    continue

                # ---- 兜底 2：连资料都没提，回得又特别短 ----
                # 典型表现：「我没取到这份资料，你贴给我吧」然后反问用户。
                # 补一条提醒逼它去读；只补一次，避免死循环。
                if tools and not ref_reads and not nudged and len(text) < 1500:
                    nudged = True
                    messages.append({"role": "assistant", "content": text})
                    messages.append({
                        "role": "user",
                        "content": (
                            "（系统提醒）你还没有读取本技能包的参考资料："
                            f"{'、'.join(lazy_names)}。"
                            "请现在调用 read_reference 工具把它读出来，"
                            "再据此产出最终结果。不要凭空推测，也不要让用户替你贴内容。"
                        ),
                    })
                    continue
                break   # 模型没要资料，正常结束

            # 把模型的调用意图登记进对话，再逐个执行、回填结果
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {
                            "name": c.function.name,
                            "arguments": c.function.arguments,
                        },
                    }
                    for c in calls
                ],
            })

            for c in calls:
                try:
                    args = json.loads(c.function.arguments or "{}")
                    tag = f"{args.get('skill')}/{args.get('filename')}"
                    if tag in ref_reads:
                        # 同一份资料重复请求：不再回灌全文，避免把上下文撑爆
                        result = f"（{tag} 已经给过你了，内容同上，不要重复请求。）"
                    else:
                        text = self.loader.read_reference(
                            args.get("skill", ""), args.get("filename", "")
                        )
                        ref_reads.append(tag)
                        result = text[: self.REF_READ_MAX_CHARS]   # 见 REF_READ_MAX_CHARS 注释
                        if len(text) > self.REF_READ_MAX_CHARS:
                            result += "\n\n…（资料过长，已截断）"
                except Exception as e:
                    result = f"读取失败：{e}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": c.id,
                    "content": result,
                })

        content = msg.content or ""

        return {
            "content": content,
            "skills_used": skill_names,
            "truncated": truncated,
            "system_chars": len(system),
            "references_read": ref_reads,       # 本次实际取过哪些资料
            "elapsed": round(time.time() - t0, 2),
            "tokens": {
                "prompt": getattr(usage, "prompt_tokens", None),
                "completion": getattr(usage, "completion_tokens", None),
            } if usage else None,
        }

    # ------------------------------------------------------------ ④ 质检

    def lint(self, prompt_text: str, skill_name: str | None = None, temperature: float = 0.2) -> dict:
        """用质检 skill 检查一段提示词。

        skill_name 指定用哪个质检技能；不传则自动找名字含 lint 的那个。
        """
        if not skill_name:
            skill_name = next(
                (n for n in self.loader.names() if "lint" in n.lower()), None
            )
        if not skill_name or skill_name not in self.loader.skills:
            return {"content": "（未找到质检类 skill，跳过质检）", "skills_used": []}

        return self.generate(
            user_input=f"请质检下面这段视频提示词：\n\n{prompt_text}",
            skill_names=[skill_name],
            temperature=temperature,
        )

    # ------------------------------------------------------------ 技能顺序整理

    # 技能之间「不绑定」。2026-10-16 按用户要求清空。
    #
    # 历史：这里曾经是 [["seedance25-official", "seedance-prompt-lint"]]，
    # 表示选中任一成员就自动补齐整条线。问题有两个：
    #   1. 双向补齐语义不对 —— 用户只想「检查一段现成提示词」，
    #      却被塞进整个「编写提示词」的官方技能（2万多字符）。
    #   2. 把「要不要质检」的决定权从用户手里拿走了。
    #
    # 现在：选什么就是什么。要质检就在需求里说出来，由模型判断是否选 lint。
    # 想恢复绑定，往这个列表里加 ["主技能", "后置技能"] 即可，代码不用动。
    PIPELINES: list[list[str]] = []

    def resolve_pipeline(self, picked: list[str]) -> list[str]:
        """整理技能列表：去重、校验存在性、按 PIPELINES 顺序排列。

        当前 PIPELINES 为空，本函数退化为「清洗 + 去重」，不再补齐任何技能。
        """
        out: list[str] = []
        used: set[str] = set()

        # 如果以后恢复了绑定，这里负责把整条线补上并保持定义顺序
        for line in self.PIPELINES:
            if any(n in picked for n in line):
                for n in line:
                    if n in self.loader.skills and n not in used:
                        out.append(n)
                        used.add(n)

        # 其余技能按模型给出的顺序原样保留
        for n in picked:
            if n not in used and n in self.loader.skills:
                out.append(n)
                used.add(n)

        return out

    # ------------------------------------------------------------ 完整链路

    def run_full(
        self,
        user_input: str,
        forced: list[str] | None = None,
        do_lint: bool = True,
        history: list[dict] | None = None,
        last_skills: list[str] | None = None,
        on_step: Callable[[str, dict], None] | None = None,
    ) -> dict:
        """一步到位：选 skill → 补齐流水线 → 生成 → 质检。

        on_step 是个回调，可以让前端看到每一步的进展。
        last_skills：上一轮用过的技能，多轮追问时用来兜底（详见 pick_skills）。
        """
        def emit(stage: str, payload: dict):
            if on_step:
                try:
                    on_step(stage, payload)
                except Exception:
                    pass

        # ① 选
        emit("picking", {})
        picked, source = self.pick_skills(
            user_input, forced=forced, history=history, last_skills=last_skills
        )

        # 用户手动指定了技能 → 直接用，不再让模型判断
        if forced:
            picked = self.resolve_pipeline(picked)
            emit("picked", {"skills": picked, "source": "user"})
            return self._run_after_pick(user_input, picked, do_lint, history, emit)

        # 追问兜底命中：沿用上一轮技能，前端提示一下，用户看得见
        if source == "reuse" and picked:
            picked = self.resolve_pipeline(picked)
            emit("picked", {"skills": picked, "source": "reuse"})
            return self._run_after_pick(user_input, picked, do_lint, history, emit)

        # 模型没选出来 → 不兜底，直接把判断权交回用户
        #
        # 2026-10-16 按用户要求：不再硬塞「主技能」。
        # 硬塞的后果是把不相关的技能拼进 system prompt，产出不可控。
        # 这里如实返回，让前端提示用户换个说法或手动选技能。
        if not picked:
            emit("no_skill", {
                "reason": "没有找到能完成这个需求的技能",
                "hint": "换个说法描述你的需求，或在左侧手动勾选要用的技能",
            })
            return {
                "skills_used": [],
                "generate": None,
                "lint": None,
                "need_user_action": True,
                "message": (
                    "没找到合适的技能来完成这个需求。\n"
                    "你可以：\n"
                    "  1. 换个说法再描述一次（说清要做什么、针对哪个平台/模型）\n"
                    "  2. 在左侧技能列表里手动勾选后再发送"
                ),
            }

        # ①.⑤ 整理技能列表（当前不补齐，只去重校验）
        final = self.resolve_pipeline(picked)
        if final != picked:
            emit("expanded", {"from": picked, "to": final})
        picked = final
        emit("picked", {"skills": picked, "source": "model"})

        return self._run_after_pick(user_input, picked, do_lint, history, emit)

    def _run_after_pick(
        self,
        user_input: str,
        picked: list[str],
        do_lint: bool,
        history: list[dict] | None,
        emit: Callable[[str, dict], None],
    ) -> dict:
        """技能已确定，跑生成 + 质检。抽出来给「手动指定」和「模型自选」共用。"""
        # ②③ 生成
        emit("generating", {"skills": picked})
        gen = self.generate(user_input, picked, history=history)
        emit("generated", {"chars": len(gen["content"])})

        result = {
            "skills_used": picked,
            "generate": gen,
            "lint": None,
        }

        # ④ 质检：只有本次真的选中了质检技能才跑
        #
        # 判据只看「picked 里有没有名字含 lint 的技能」。
        # 用户想要质检，就在需求里说出来，由模型决定是否选 lint ——
        # 技能之间不再强制绑定（PIPELINES 已清空）。
        lint_skill = next((n for n in picked if "lint" in n.lower()), None)

        if do_lint and lint_skill and gen["content"]:
            emit("linting", {})
            try:
                result["lint"] = self.lint(gen["content"], skill_name=lint_skill)
                emit("linted", {"chars": len(result["lint"]["content"])})
            except Exception as e:
                result["lint"] = {"content": f"（质检失败：{e}）", "skills_used": []}
                emit("linted", {"error": str(e)})
        elif do_lint and not lint_skill:
            emit("lint_skipped", {"reason": "本次没有选中质检技能，跳过质检"})

        return result

