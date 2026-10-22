import os
import re
import sys
import json
import time
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"


def main():
    # 1. 모든 background.js의 1~16줄에서 BRIDGE URL/포트 추출
    bridge_urls = []
    ports = set()
    for bg in BASE_DIR.rglob("background.js"):
        try:
            lines = bg.read_text(encoding="utf-8", errors="replace").splitlines()
            head = "\n".join(lines[:20])
            for m in re.findall(r"https?://(?:127\.0\.0\.1|localhost):(\d{2,5})[^\s\"'`]*", head):
                ports.add(int(m))
            for line in lines[:16]:
                if any(k in line for k in ("BRIDGE", "127.0.0.1", "localhost", "PORT", "http")):
                    bridge_urls.append(f"{bg.parent.name}: {line.strip()[:90]}")
        except Exception:
            pass

    # 2. shin-agent 내 기존 브릿지 서버 .py 파일 찾기 (/api/queue 또는 /poll 포함)
    server_pys = []
    for py in BASE_DIR.rglob("*.py"):
        if py.name.startswith("omni_") or py.name == "s_run.py":
            continue
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
            if "/api/queue" in txt or "/api/dispatch/next" in txt or ("/poll" in txt and "HTTPServer" in txt):
                server_pys.append(py)
                for m in re.findall(r"(?:127\.0\.0\.1|localhost)[\"']?\s*,\s*(\d{2,5})", txt):
                    ports.add(int(m))
                for m in re.findall(r"PORT\s*=\s*(\d{2,5})", txt):
                    ports.add(int(m))
        except Exception:
            pass

    # 3. 기존 브릿지 서버 파일이 있으면 즉시 백그라운드 기동!
    started = []
    for spy in server_pys:
        try:
            subprocess.Popen(
                ["pythonw.exe", str(spy)],
                cwd=str(spy.parent),
                creationflags=0x08000000
            )
            started.append(spy.name)
        except Exception:
            pass

    time.sleep(1.5)

    # 4. 발견된 포트들에 대해 /api/queue 살아있는지 테스트
    alive_ports = []
    for p in sorted(ports):
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{p}/api/queue",
                data=json.dumps({"role": "rgon", "filename": "ping.txt", "code": "ping"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    alive_ports.append(p)
        except Exception:
            pass

    report = (
        f"👑 [만능 소통창 브릿지 서버 색출 & 즉시 가동 완료!]\n"
        f"• BRIDGE 정의: {bridge_urls[:4]}\n"
        f"• 발견 포트: {sorted(ports)}\n"
        f"• 발견된 서버 파일: {[p.name for p in server_pys]}\n"
        f"• 즉시 기동됨: {started}\n"
        f"• 현재 응답 성공 포트(/api/queue): {alive_ports}"
    )
    print(report)
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", report[:3500]], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy