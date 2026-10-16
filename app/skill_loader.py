# -*- coding: utf-8 -*-
"""
Skill 加载器 —— 整个智能体的核心。

它做三件事：
  1. 扫描 skills 目录，把每个 skill 的 name / description / 正文读出来
  2. 用 description 让大模型挑出「这条需求该用哪些 skill」
  3. 把挑中的 skill 全文拼成 system prompt

这就是「load skill」的全部秘密：不是调用函数，是读文件 + 拼进系统提示词。
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------- 数据结构

@dataclass
class Skill:
    """一个 skill 的完整信息。"""

    name: str                 # frontmatter 里的 name（真正生效的身份）
    description: str          # 触发词都写在这里，用来匹配
    body: str                 # SKILL.md 去掉 frontmatter 后的正文
    dir_name: str             # 目录名（可能和 name 不一样）
    path: Path                # SKILL.md 绝对路径
    references: dict = field(default_factory=dict)  # 附件名 -> 内容
    meta: dict = field(default_factory=dict)        # 完整 frontmatter（含 tags/author/metadata）

    # 描述上限。对齐 Anthropic Agent Skills 规范：description ≤ 1024 字符。
    # 早期这里是 200，中文场景下太紧，会把触发词砍掉导致选错技能。
    DESC_LIMIT = 1024

    @property
    def short_desc(self) -> str:
        """给模型「选 skill」用的描述。

        1. 换行压成空格（清单里一行一个技能）
        2. 超长按「句末标点」截断，不硬切半句
        """
        d = self.description.strip().replace("\n", " ")
        if len(d) <= self.DESC_LIMIT:
            return d

        cut = d[: self.DESC_LIMIT]
        # 从强标点往弱标点找，至少要保留一半长度，避免砍得太狠
        for marks in ("。！？；", "，、,;"):
            i = max((cut.rfind(m) for m in marks), default=-1)
            if i > self.DESC_LIMIT * 0.5:
                return cut[: i + 1] + "…"
        return cut + "…"


# ---------------------------------------------------------------- 解析 frontmatter

# 容忍开头的 BOM、空行、缩进（`^[^\S\n]*` = 行首任意空白）。
# 只认第一行就是 `---` 的情况，这是 SKILL.md 规范。
_FM_RE = re.compile(r"^[^\S\n]*---[^\S\n]*\n(.*?)\n[^\S\n]*---[^\S\n]*\n?", re.DOTALL)


def _fallback_parse(raw: str) -> dict:
    """yaml 不可用或解析失败时的兜底：按「key: value」逐行抠。

    只处理单层字段；嵌套结构会丢。能跑就行，正式环境应该装 yaml。
    """
    meta: dict[str, str] = {}
    key = None
    for line in raw.splitlines():
        if re.match(r"^[A-Za-z_][\w-]*\s*:", line):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip().strip("\"'")
            meta[key] = val
        elif key and line.startswith((" ", "\t")):
            meta[key] = (meta.get(key, "") + "\n" + line.strip()).strip()
    return meta


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """把 SKILL.md 拆成 (元信息字典, 正文)。

    容错点：
      - 去掉 UTF-8 BOM（否则正则的 ^ 匹配不上，整个 frontmatter 丢失）
      - yaml 解析失败不再静默，打印警告后走逐行兜底
      - 字段名统一小写（Description / DESCRIPTION 都能认）
    """
    text = text.lstrip("\ufeff")

    m = _FM_RE.match(text)
    if not m:
        return {}, text

    raw, body = m.group(1), text[m.end():]

    meta: dict = {}
    try:  # 优先用 yaml（description 里可能有冒号、引号、嵌套）
        import yaml

        parsed = yaml.safe_load(raw)
        if isinstance(parsed, dict):
            meta = parsed
    except Exception as e:
        print(f"[警告] frontmatter yaml 解析失败，改用逐行兜底：{e}")

    if not meta:
        meta = _fallback_parse(raw)

    # 归一化：键统一小写去空白，值统一转字符串
    norm: dict[str, str] = {}
    for k, v in meta.items():
        if isinstance(v, (list, dict)):
            norm[str(k).strip().lower()] = str(v)
        else:
            norm[str(k).strip().lower()] = "" if v is None else str(v).strip()

    return norm, body


def _resolve_description(meta: dict, body: str) -> str:
    """按优先级取出「给模型选技能用的描述」。

    级联顺序（对齐 Anthropic 规范 + Claude Code 实现）：
      1. description         —— 标准字段
      2. when_to_use         —— 官方的独立触发说明字段，追加在后
      3. 正文第一段非标题文字 —— 兜底，总比空着好

    都没有就返回空串（这种技能基本选不上，reload 里会打警告）。
    """
    parts: list[str] = []

    d = meta.get("description", "").strip()
    if d:
        parts.append(d)

    w = meta.get("when_to_use", "").strip()
    if w:
        parts.append(f"何时使用：{w}")

    if not parts:  # 两个字段都没有，退而取正文首段
        for block in re.split(r"\n\s*\n", body.strip()):
            block = block.strip()
            if block and not block.startswith("#"):
                parts.append(re.sub(r"^[#>\-*\s]+", "", block).strip())
                break

    return "\n".join(parts).strip()


# ---------------------------------------------------------------- 加载器本体

class SkillLoader:
    """从目录里加载所有 skill，并支持按需取用。"""

    # 允许被浏览器直接发过来选定的 skill（防止乱传名字）
    MAX_SKILL_CHARS = 60_000   # 单个 skill 正文的硬上限，超了截断
    MAX_TOTAL_CHARS = 120_000  # 一次注入多个 skill 时的总量上限

    # 附件自动注入阈值：单个附件 ≤ 这个字符数就全文塞进 system prompt。
    # 超过的走「注入目录 + 提供 read_reference 工具」，由模型自己按需取。
    # 40_000 是实测定的：LP 模板库 33,264 字符能全塞，官方手册 198,729 字符必须按需。
    REF_INLINE_LIMIT = 40_000

    # 单次注入所有附件内容的总量上限（防止多个中等附件叠加超标）
    REF_INLINE_TOTAL = 60_000

    def __init__(self, skills_dir: str | os.PathLike, include: list[str] | None = None):
        """
        skills_dir : 技能库根目录
        include    : 只加载这些 skill（按目录名或 name 匹配）；None = 全加载
        """
        self.skills_dir = Path(skills_dir)
        self.include = [s.lower() for s in include] if include else None
        self.skills: dict[str, Skill] = {}
        self.reload()

    # ------------------------------------------------------------ 扫描

    def reload(self) -> list[str]:
        """重新扫描目录，返回加载到的 skill 名列表。"""
        self.skills.clear()
        if not self.skills_dir.is_dir():
            return []

        for entry in sorted(self.skills_dir.iterdir()):
            if not entry.is_dir():
                continue

            # 白名单过滤：目录名不在名单里就跳过（避免扫到几十个无关 skill）
            if self.include is not None:
                if entry.name.lower() not in self.include:
                    continue

            skill_md = entry / "SKILL.md"
            if not skill_md.is_file():
                # 也接受 skill.md 这种小写写法
                alt = entry / "skill.md"
                if not alt.is_file():
                    continue
                skill_md = alt

            try:
                text = skill_md.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = skill_md.read_text(encoding="utf-8", errors="ignore")

            meta, body = _parse_frontmatter(text)

            # name 缺失时兜底用目录名（官方规范里 name 可省略，默认目录名）
            name = (meta.get("name") or entry.name).strip()

            # 描述走三级级联：description → when_to_use → 正文首段
            desc = _resolve_description(meta, body)
            if not desc:
                print(f"[警告] {entry.name} 没有可用的 description，该技能基本选不上")

            # 同名冲突时保留先到的，并加后缀区分
            if name in self.skills:
                name = f"{name}@{entry.name}"

            refs = self._load_references(entry)

            self.skills[name] = Skill(
                name=name,
                description=desc,
                body=body,
                dir_name=entry.name,
                path=skill_md,
                references=refs,
                meta=meta,
            )

        return self.names()

    def _load_references(self, skill_dir: Path) -> dict:
        """扫描 references/ 下的附件。

        2026-10-16 改动：以前只登记「有哪些附件、多大」，不读内容 —— 结果是
        技能包成了空壳（模型看到有文件却读不到，只能凭通用知识硬编）。
        现在改成：
          - 小附件（≤ REF_INLINE_LIMIT）**当场读进内存**，稍后全文注入
          - 大附件只登记，走 read_reference() 按需取

        按需取是给 seedance25-official 准备的：它的手册有 198,729 字符，
        整个塞进去会吃掉大半上下文窗口。
        """
        refs: dict[str, dict] = {}
        ref_dir = skill_dir / "references"
        if not ref_dir.is_dir():
            return refs

        for f in sorted(ref_dir.iterdir()):
            if not f.is_file():
                continue
            size = f.stat().st_size     # 字节数，给前端展示用
            info = {
                "path": str(f),
                "size": size,
                "loaded": False,
                "content": None,
                # ⚠️ inline 是「分类标记」，加载时定死，之后谁都不许改。
                #
                # 2026-10-16 踩坑：以前全项目用 bool(info["content"]) 来判断
                # 「这份附件要不要内联」，而 read_reference() 又会把按需读到的
                # 内容回填进 info["content"]。于是第一次读完之后，这份大附件
                # 就被重新归类成「已内联」→ 不再下发 read_reference 工具 →
                # 模型想读却无工具可用，只能回一句「我取不到，你贴给我吧」。
                # 现象是「第一次问能用，之后每次都不行」，非常难查。
                # 现在分类只看 inline，content 降级为纯缓存。
                "inline": False,
            }

            # ⚠️ 判断阈值用「字符数」不是字节数 —— CJK 在 UTF-8 占 3 字节，
            # 拿字节数比会把中文附件误判成超大（用户 2026-10-16 实测踩过）。
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                print(f"[警告] 附件 {f.name} 读取失败，改为按需加载：{e}")
                refs[f.name] = info
                continue

            if len(content) <= self.REF_INLINE_LIMIT:
                info["content"] = content
                info["loaded"] = True
                info["inline"] = True       # ← 分类在此定死

            refs[f.name] = info
        return refs

    def read_reference(self, skill_name: str, filename: str) -> str:
        """按需读取某个 skill 的附件全文。

        ⚠️ 这里会把读到的内容缓存在 info["content"] 里，但**绝不能**因此改变
        这份附件的 inline 分类 —— 分类只认 info["inline"]（见 _load_references）。
        """
        skill = self.skills.get(skill_name)
        if not skill:
            raise KeyError(f"没有这个 skill: {skill_name}")
        info = skill.references.get(filename)
        if not info:
            raise KeyError(f"skill {skill_name} 下没有附件 {filename}")
        if info.get("content") is None:      # 首次读盘，之后走缓存
            info["content"] = Path(info["path"]).read_text(
                encoding="utf-8", errors="ignore"
            )
        info["loaded"] = True
        return info["content"]

    def list_references(self, skill_names: list[str]) -> list[dict]:
        """列出选中技能的所有附件（供前端/工具展示）。"""
        out = []
        for n in skill_names:
            s = self.skills.get(n)
            if not s:
                continue
            for fname, info in s.references.items():
                out.append({
                    "skill": n,
                    "name": fname,
                    "size": info["size"],
                    "inlined": bool(info.get("inline")),
                })
        return out

    # ------------------------------------------------------------ 查询

    def names(self) -> list[str]:
        return list(self.skills.keys())

    def catalog(self) -> list[dict]:
        """给前端用的 skill 清单。"""
        out = []
        for s in self.skills.values():
            # 正文预览：剥掉 markdown 标题符号，取前 1200 字
            preview = re.sub(r"^#{1,6}\s*", "", s.body, flags=re.MULTILINE).strip()
            out.append({
                "name": s.name,
                "dir_name": s.dir_name,
                "description": s.description,
                "body_chars": len(s.body),
                "body_preview": preview[:1200],
                "meta": s.meta,          # 完整 frontmatter（tags / author / metadata）
                "references": [
                    {
                        "name": k,
                        "size": v["size"],
                        "inlined": bool(v.get("inline")),    # 是否已随技能自动加载
                    }
                    for k, v in s.references.items()
                ],
            })
        return out

    def catalog_for_llm(self) -> str:
        """给大模型做「选 skill」用的清单，尽量省 token。"""
        lines = []
        for s in self.skills.values():
            lines.append(f"- {s.name}：{s.short_desc}")
        return "\n".join(lines)

    # ------------------------------------------------------------ 取正文

    def build_system_prompt(self, skill_names: list[str]) -> tuple[str, list[str]]:
        """把选中的 skill 拼成 system prompt。

        返回 (拼好的提示词, 实际用上但被截断的 skill 名列表)。

        2026-10-16 改动：**附件内容现在真的会进 prompt**。
        以前只列个文件名告诉模型「有这份资料」，模型没法读，技能包等于空壳。
        现在的策略分两档：
          - 小附件（已读进 content）→ 全文嵌入，标 `【参考资料：xxx】`
          - 大附件（只有登记信息）  → 只列目录 + 提示可用 read_reference 工具取
        """
        picked = [self.skills[n] for n in skill_names if n in self.skills]
        if not picked:
            return "", []

        parts: list[str] = []
        truncated: list[str] = []
        used = 0
        ref_budget = self.REF_INLINE_TOTAL   # 附件内容单独的预算

        for s in picked:
            body = s.body
            if len(body) > self.MAX_SKILL_CHARS:
                body = body[: self.MAX_SKILL_CHARS] + "\n\n…（正文过长，已截断）"
                truncated.append(s.name)
            if used + len(body) > self.MAX_TOTAL_CHARS:
                truncated.append(s.name)
                continue
            used += len(body)

            header = f"# === SKILL: {s.name} ===\n"

            # ---- 附件分成「可内联」和「需按需取」两类
            # 分类只看 inline 标记（加载时定死），不看 content 有没有被缓存过。
            inline_refs, lazy_refs = [], []
            for k, v in s.references.items():
                if v.get("inline"):
                    inline_refs.append((k, v))
                else:
                    lazy_refs.append((k, v))

            if lazy_refs:
                lst = "、".join(f"{k}（{v['size']} 字节）" for k, v in lazy_refs)
                header += (
                    f"（⚠️ 该 skill 的核心资料放在附件文件里，本次没有内联：{lst}。"
                    f"**动笔之前，必须先调用 read_reference 工具把用得到的那份读完**，"
                    f"再按里面的规范来写。不要凭记忆或通用知识替代，也不要假装读过。）\n"
                )

            chunk = header + body

            # ---- 内联附件：全文嵌入
            for k, v in inline_refs:
                content = v["content"]
                # 预算是硬的：这一篇放不下就退化成「按需取」，不截断半篇
                if ref_budget - len(content) < 0:
                    truncated.append(f"{s.name}::{k}")
                    chunk += (
                        f"\n\n（⚠️ 参考资料 {k} 体积较大，本次未内联。"
                        f"**写之前必须用 read_reference 工具把它读出来**，不要凭空推测。）"
                    )
                    continue
                ref_budget -= len(content)
                chunk += (
                    f"\n\n---\n\n## 【参考资料：{k}】\n\n"
                    f"以下是该技能包附带的资料全文，请以此为准，"
                    f"不要用你自己的通用知识替代其中的规范。\n\n"
                    f"{content}\n\n---"
                )

            parts.append(chunk)

        system = (
            "你是一个专业的 AI 视频提示词工程师。\n"
            "下面挂载了若干「技能包（Skill）」，它们是权威的写作规范。\n"
            "你必须严格按照这些技能包里的规则来工作，而不是凭自己的习惯发挥。\n"
            "如果技能包里规定了输出格式，就照那个格式输出，不要自创格式。\n"
            "技能包后附的【参考资料】是权威依据，必须遵循。\n"
            "如果某份资料标注为「需按需读取」：**先调用 read_reference 工具把它读出来再用**，\n"
            "不要跳过、不要凭通用知识替代、也不要让用户替你贴内容。\n"
            "只有当工具调用确实失败、拿不到内容时，才如实说明缺哪份资料 —— "
            "但仍要继续把能写的部分写完，不要因此停下来反问用户。\n\n"
            + "\n\n".join(parts)
        )
        return system, truncated
