# -*- coding: utf-8 -*-
r"""
静默启动器 —— 让 start.bat 能在「完全看不到窗口」的情况下把服务挂到后台。

为什么需要它
------------
pythonw.exe 没有控制台，启动后 sys.stdout / sys.stderr 直接是 None。
目标脚本里任何一句 print() 都会抛
    AttributeError: 'NoneType' object has no attribute 'write'
把自己当场干掉 —— run.py 和 feishu_bot.py 里 print 都不少，所以不能直接
拿 pythonw 去跑它们。

这里在跑目标之前，先做两件事：
    1. 把 stdout / stderr 接到 logs\<脚本名>.log（行缓冲，崩了也能看到最后几行）
    2. 把自己的 pid 写进 logs\<脚本名>.pid，供 `start.bat stop` 精确点杀

用法（start.bat 内部调用，人不用手敲）
------------------------------------
    pythonw.exe scripts\_silent.pyw run.py --port auto --open
    pythonw.exe scripts\_silent.pyw feishu_bot.py

退出码
------
    2  没给目标脚本
    3  目标脚本不存在
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 2:
        return 2

    script = BASE / sys.argv[1]
    if not script.is_file():
        return 3

    logs = BASE / "logs"
    logs.mkdir(exist_ok=True)
    stem = script.stem                      # run / feishu_bot

    # 先接管输出，之后目标脚本里的任何 print 都落到文件里。
    # errors="replace" 防止 Windows 控制台编码残留导致写日志时二次报错。
    handle = open(logs / f"{stem}.log", "w",
                  encoding="utf-8", errors="replace", buffering=1)
    sys.stdout = handle
    sys.stderr = handle

    (logs / f"{stem}.pid").write_text(str(os.getpid()), encoding="utf-8")

    # 目标脚本按自己的位置找 config.json / skills，所以工作目录要回到项目根
    os.chdir(BASE)
    sys.argv = [str(script)] + sys.argv[2:]

    try:
        runpy.run_path(str(script), run_name="__main__")
    finally:
        handle.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
