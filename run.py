# -*- coding: utf-8 -*-
"""
启动入口。

用法：
    python run.py                 # 默认 8080 端口，默认读项目自带的 skills/
    python run.py --port 9000     # 换端口
    python run.py --skills "D:\\MySkills"   # 换技能目录
    python run.py --reload        # 开发模式，改代码自动重启

技能目录优先级：
    --skills 参数  >  环境变量 SKILLS_DIR  >  项目自带的 skills/
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# 让 python run.py 能直接 import app.xxx
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    ap = argparse.ArgumentParser(description="提示词智能体")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--skills", default=None, help="技能包目录（默认用项目自带的 skills/）")
    ap.add_argument("--reload", action="store_true", help="开发模式：改代码自动重启")
    args = ap.parse_args()

    # 只有显式传了 --skills 才覆盖环境变量；否则环境变量优先，最后兜底到项目自带目录
    if args.skills:
        os.environ["SKILLS_DIR"] = str(Path(args.skills).expanduser().resolve())

    import uvicorn

    default_skills = Path(__file__).resolve().parent / "skills"
    skills_dir = os.environ.get("SKILLS_DIR") or str(default_skills)
    if not Path(skills_dir).is_dir():
        print(f"[警告] 技能目录不存在：{skills_dir}")
        print("       将加载 0 个技能。请检查路径，或在 skills/ 下放入技能包。")

    print("=" * 56)
    print("  提示词智能体启动中…")
    print(f"  技能目录：{skills_dir}")
    print(f"  访问地址：http://{args.host}:{args.port}")
    print("=" * 56)

    uvicorn.run(
        "app.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
