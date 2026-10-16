# -*- coding: utf-8 -*-
"""用 seedance-prompt-lint 质检已有的 output 产物。

加载器只挂载 skills/seedance-prompt-lint 这一个技能（avoid 把 31 个技能全读进来）。
改造前的原始版本备份在 _参考_技能/_orig-lint/。

用法:
    python scripts/test_lint.py                     # 质检下方默认列表
    python scripts/test_lint.py <output文件> ...    # 指定文件
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agent import Agent, LLMConfig  # noqa: E402
from app.skill_loader import SkillLoader  # noqa: E402

DEFAULT_TARGETS = [
    "output/时间轴分镜-雨夜骑手-15秒.md",
    "output/随机抽测-定格动画.md",
]


def extract_prompt(text: str) -> str:
    """优先取 ```text 围栏里的正式提示词，取不到就用原文。"""
    m = re.search(r"```(?:text)?\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def main() -> None:
    targets = sys.argv[1:] or DEFAULT_TARGETS

    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    # 用 skills/ 里已改造过的 v2.0.0 版本，只加载质检技能本身
    loader = SkillLoader(str(ROOT / "skills"), include=["seedance-prompt-lint"])

    print("加载到的技能:", loader.names())
    if "seedance-prompt-lint" not in loader.skills:
        print("✗ 没找到质检技能，退出")
        return

    agent = Agent(loader, LLMConfig(
        api_key=cfg["api_key"], base_url=cfg["base_url"],
        model=cfg["model"], temperature=cfg.get("temperature", 0.7),
    ))

    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    report_lines = ["# seedance-prompt-lint 质检实测报告", ""]

    for t in targets:
        p = ROOT / t
        if not p.is_file():
            print(f"跳过（不存在）: {t}")
            continue

        prompt = extract_prompt(p.read_text(encoding="utf-8"))
        print(f"\n{'=' * 66}\n质检目标: {t}  ({len(prompt)} 字符)\n{'=' * 66}")

        t0 = time.time()
        r = agent.lint(prompt, skill_name="seedance-prompt-lint", temperature=0.2)
        dt = time.time() - t0
        content = r.get("content") or ""
        print(f"耗时 {dt:.1f}s / 产出 {len(content)} 字符\n")
        print(content)

        report_lines += [
            f"## {Path(t).name}",
            "",
            f"- 源文件：`{t}`",
            f"- 送检提示词长度：{len(prompt)} 字符",
            f"- 质检耗时：{dt:.1f}s ｜ 报告长度：{len(content)} 字符",
            "",
            content,
            "",
            "---",
            "",
        ]

    (out_dir / "质检实测报告.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\n已写入 -> {out_dir / '质检实测报告.md'}")


if __name__ == "__main__":
    main()
