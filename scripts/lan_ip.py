# -*- coding: utf-8 -*-
"""打印本机在局域网里的 IPv4 地址。给 `start.bat lan` 用，不是测试文件。

为什么要单独一个文件：在批处理里塞 `python -c "..."` 要处理一堆引号和括号转义，
而且 `ipconfig` 的输出还随系统语言变（中文是「IPv4 地址」、英文是「IPv4 Address」），
解析起来很脆。

原理：对一个外部地址做 UDP connect。UDP 是无连接的，这一步不会真的发包，
只是让系统选一块网卡并把它的地址告诉我们——选中的就是默认路由那块网卡，
也就是同事能连到的那块。虚拟机 / 虚拟网卡一般不会抢到它。

退出码：0 = 拿到了地址，1 = 没找到（比如完全没联网）。
"""
from __future__ import annotations

import socket
import sys

# 两个都是纯用来「选路由」的，不会真的连上，也不依赖它们可达
PROBES = ("8.8.8.8", "114.114.114.114", "1.1.1.1")


def _via_route() -> str | None:
    for host in PROBES:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.connect((host, 80))
                ip = sock.getsockname()[0]
            finally:
                sock.close()
            if ip and not ip.startswith("127."):
                return ip
        except OSError:
            continue
    return None


def _via_hostname() -> str | None:
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except OSError:
        return None
    return ip if ip and not ip.startswith("127.") else None


def main() -> int:
    ip = _via_route() or _via_hostname()
    if not ip:
        return 1
    print(ip)
    return 0


if __name__ == "__main__":
    sys.exit(main())
