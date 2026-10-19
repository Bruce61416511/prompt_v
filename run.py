# -*- coding: utf-8 -*-
"""
启动入口。

用法：
    python run.py                       # 默认 8080 端口，默认读项目自带的 skills/
    python run.py --port 9000           # 换端口
    python run.py --port auto           # 从 8099 起自动找一个空闲端口（日常推荐）
    python run.py --open                # 启动后自动打开浏览器
    python run.py --skills "D:\\MySkills"   # 换技能目录
    python run.py --reload              # 开发模式，改代码自动重启

技能目录优先级：
    --skills 参数  >  环境变量 SKILLS_DIR  >  项目自带的 skills/

⚠️ 部署到服务器时注意：
    默认只监听 127.0.0.1（只有本机自己能访问）。要让局域网/公网访问，必须显式加：
        python run.py --host 0.0.0.0 --port 8099
    否则外部打不开，而服务器上 curl 127.0.0.1 却是通的 —— 极易误判成防火墙问题。
"""
from __future__ import annotations

import argparse
import atexit
import os
import socket
import sys
from pathlib import Path

# 让 python run.py 能直接 import app.xxx
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

AUTO_PORT_START = 8099        # --port auto 的起点（避开 8080 这类常被别的程序占用的端口）
AUTO_PORT_TRIES = 20          # 往后最多试多少个端口
RUNTIME_FILE = BASE_DIR / ".runtime-port"      # 记录当前端口，方便外部脚本判断"服务是否已在跑"


def _port_free(port: int, host: str) -> bool:
    """端口是否真的空着。

    故意不设 SO_REUSEADDR —— 在 Windows 上设了它会把"已被占用"也判成可用，
    导致 uvicorn 真正启动时才报错。
    """
    bind_host = "0.0.0.0" if host in ("0.0.0.0", "::") else host
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((bind_host, port))
        except OSError:
            return False
    return True


def _port_owner_hint(port: int) -> str:
    """尽量查出是谁占着端口（仅 Windows 有效，失败就返回空串，不影响启动）。"""
    if not sys.platform.startswith("win"):
        return ""
    import subprocess
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                             timeout=6, encoding="utf-8", errors="ignore").stdout
    except Exception:
        return ""
    for line in out.splitlines():
        if f":{port} " in line and "LISTENING" in line.upper():
            pid = line.split()[-1]
            name = ""
            try:
                q = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                                   capture_output=True, text=True, timeout=6,
                                   encoding="utf-8", errors="ignore").stdout
                if q.strip():
                    name = q.split()[0]
            except Exception:
                pass
            return f"占用它的进程：PID {pid} {name}".strip()
    return ""


def _pick_port(host: str) -> int:
    for p in range(AUTO_PORT_START, AUTO_PORT_START + AUTO_PORT_TRIES):
        if _port_free(p, host):
            return p
    print(f"[错误] {AUTO_PORT_START}~{AUTO_PORT_START + AUTO_PORT_TRIES - 1} 之间没有空闲端口。")
    print("       先关掉占端口的程序，或手动指定：python run.py --port 9010")
    raise SystemExit(2)


def main():
    ap = argparse.ArgumentParser(description="提示词智能体")
    ap.add_argument("--host", default="127.0.0.1",
                    help="监听地址。本机用默认值即可；部署到服务器要让外部访问，必须写 0.0.0.0")
    ap.add_argument("--port", default="8080",
                    help="端口号，或 auto（从 8099 起自动找空闲端口）")
    ap.add_argument("--skills", default=None, help="技能包目录（默认用项目自带的 skills/）")
    ap.add_argument("--open", action="store_true", help="启动后自动打开浏览器")
    ap.add_argument("--reload", action="store_true", help="开发模式：改代码自动重启")
    ap.add_argument("--allow-guest-write", action="store_true",
                    help="放开局域网访客的写权限（默认访客只读：能看案例，不能生成、不能改配置）")
    args = ap.parse_args()

    # 只有显式传了 --skills 才覆盖环境变量；否则环境变量优先，最后兜底到项目自带目录
    if args.skills:
        os.environ["SKILLS_DIR"] = str(Path(args.skills).expanduser().resolve())

    # 访客只读开关。必须在 app.server 被导入之前设好——它是 import 时读这个变量的，
    # 而 uvicorn.run("app.server:app") 是延迟导入，所以这里来得及。
    if args.allow_guest_write:
        os.environ["GUEST_READONLY"] = "0"

    # ---------------------------------------------------------------- 定端口
    raw = str(args.port).strip().lower()
    if raw == "auto":
        port = _pick_port(args.host)
        if port != AUTO_PORT_START:
            print(f"[提示] {AUTO_PORT_START} 已被占用，自动改用 {port}")
    else:
        try:
            port = int(raw)
        except ValueError:
            print(f"[错误] --port 只能是数字或 auto，收到的是：{args.port}")
            raise SystemExit(2)
        if not _port_free(port, args.host):
            print(f"[错误] 端口 {port} 已经被占用，服务起不来。")
            hint = _port_owner_hint(port)
            if hint:
                print(f"       {hint}")
            print("       换个端口：  python run.py --port 9000")
            print("       或自动挑：  python run.py --port auto")
            raise SystemExit(2)

    import uvicorn

    # ---------------------------------------------------------------- 自检 + 打印
    default_skills = BASE_DIR / "skills"
    skills_dir = os.environ.get("SKILLS_DIR") or str(default_skills)
    static_dir = BASE_DIR / "static"

    print("=" * 56)
    print("  提示词智能体启动中…")
    print(f"  Python   ：{sys.version.split()[0]}  ({sys.executable})")
    print(f"  技能目录 ：{skills_dir}")
    print(f"  访问地址 ：http://127.0.0.1:{port}")
    if args.host == "0.0.0.0":
        print("  监听地址 ：0.0.0.0 —— 局域网/公网可访问")
    print("=" * 56)

    if not Path(skills_dir).is_dir():
        print(f"[警告] 技能目录不存在：{skills_dir}")
        print("       将加载 0 个技能。请检查路径，或在 skills/ 下放入技能包。")
    if not static_dir.is_dir():
        print(f"[警告] 静态页面目录不存在：{static_dir}")
        print("       服务能起来，但打开页面会 404（缺 static/index.html）。")

    # 记下端口，外部启动脚本靠它判断服务是否已经在跑
    try:
        RUNTIME_FILE.write_text(str(port), encoding="utf-8")
        atexit.register(lambda: RUNTIME_FILE.unlink(missing_ok=True))
    except Exception:
        pass   # 写不了也不影响使用

    if args.open:
        import threading
        import webbrowser
        threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()

    uvicorn.run(
        "app.server:app",
        host=args.host,
        port=port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
