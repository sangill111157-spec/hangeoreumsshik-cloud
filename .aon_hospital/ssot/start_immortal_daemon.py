# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent

def launch_detached_daemon():
    flags = 0
    if os.name == 'nt':
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

    cmd = [sys.executable, str(BASE_DIR / "immortal_tunnel_daemon.py")]
    proc = subprocess.Popen(
        cmd,
        cwd=str(BASE_DIR),
        creationflags=flags,
        close_fds=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"🚀 [불사조 데몬 독립 기동 완료] PID={proc.pid} (Windows DETACHED_PROCESS 모드)")
    return proc.pid

if __name__ == "__main__":
    pid = launch_detached_daemon()
    sys.exit(0)
