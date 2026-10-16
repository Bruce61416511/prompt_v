# -*- coding: utf-8 -*-
"""单技能演示：强制指定一个 skill 跑完整流水线，把产出写到 output/。

用法:
    python scripts/demo_one_skill.py --skill seedance-timeline-shot-script \
        --input "..." --out "output/xxx.md"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agent import Agent, LLMConfig  # noqa: E402
from app.skill_loader import SkillLoader  # noqa: E402


def load_cfg() -> dict:
    cfg_path = ROOT / "config.json"
    raw = json.loads(cfg_path.read_text(encoding="utf-8"))
    return raw


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True, help="强制使用的技能目录名")
    ap.add_argument("--input", required=True, help="用户需求原文")
    ap.add_argument("--out", default="", help="产出写到哪里（默认只打印）")
    args = ap.parse_args()

    cfg = load_cfg()
    loader = SkillLoader(str(ROOT / "skills"))
    llm_cfg = LLMConfig(
        api_key=cfg.get("api_key") or cfg.get("apiKey"),
        base_url=cfg.get("base_url") or cfg.get("baseUrl"),
        model=cfg.get("model"),
    )
    agent = Agent(loader, llm_cfg)

    steps: list[tuple[str, dict]] = []

    def on_step(stage: str, payload: dict) -> None:
        steps.append((stage, payload))
        print(f"  [{stage}] {payload}", flush=True)

    t0 = time.time()
    r = agent.run_full(args.input, forced=[args.skill], on_step=on_step)
    dt = time.time() - t0

    gen = r.get("generate") or {}
    content = gen.get("content") or ""
    picked = r.get("skills_used") or []
    lint = r.get("lint") or {}

    print("\n" + "=" * 60)
    print(f"耗时            : {dt:.1f}s")
    print(f"选中技能        : {picked}")
    print(f"产出字符数      : {len(content)}")
    print(f"质检字符数      : {len(lint.get('content') or '')}")
    print("=" * 60)
    print(content)
    if lint.get("content"):
        print("\n" + "-" * 60)
        print("【质检】")
        print(lint["content"])

    if args.out:
        out = ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(f"\n已写入 -> {out}")


if __name__ == "__main__":
    main()
