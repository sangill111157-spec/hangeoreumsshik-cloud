import os
import re
import sys
import json
import time
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(r"C:\Users\sangi\Downloads\shin-agent")
BG_JS = BASE_DIR / "rgon_aside_extension" / "background.js"
WATCHER_PY = BASE_DIR / "rgon_auto_watcher.py"
BRIDGE_PY = BASE_DIR / "rgon_telegram_bridge.py"


def find_bridge_port():
    if not BG_JS.exists():
        cands = list(BASE_DIR.rglob("background.js"))
        bg = cands[0] if cands else None
    else:
        bg = BG_JS

    ports = set()
    snippet = ""
    if bg and bg.exists():
        txt = bg.read_text(encoding="utf-8", errors="replace")
        lines = txt.splitlines()
        # 상단 80줄 및 bridgeFetch 정의부 추출
        top_lines = []
        for i, line in enumerate(lines):
            if i < 60 or "bridgeFetch" in line or "127.0.0.1" in line or "localhost" in line or "PORT" in line.upper():
                top_lines.append(f"L{i+1}: {line[:100]}")
                for m in re.findall(r"(?:127\.0\.0\.1|localhost):(\d{2,5})", line):
                    ports.add(int(m))
                for m in re.findall(r"(?:port|PORT)\s*[:=]\s*(\d{2,5})", line):
                    ports.add(int(m))
        snippet = "\n".join(top_lines[:35])

    # 혹시 shin-agent 안에 기존 bridge 서버 파이썬 파일이 있는지도 확인
    bridge_files = []
    for p in BASE_DIR.glob("*.py"):
        try:
            ptxt = p.read_text(encoding="utf-8", errors="replace")
            if "/api/queue" in ptxt or "/api/dispatch/next" in ptxt:
                bridge_files.append(p.name)
                for m in re.findall(r"(\d{4,5})", ptxt):
                    val = int(m)
                    if 1024 <= val <= 65535:
                        ports.add(val)
        except Exception:
            pass

    return sorted(ports), bridge_files, snippet


def main():
    ports, bridge_files, snippet = find_bridge_port()
    print(f"🎯 발견된 브릿지 포트: {ports}")
    print(f"🎯 기존 브릿지 서버 파일: {bridge_files}")

    # 만약 기존 브릿지 서버 스크립트(예: rgon_bridge_server.py 등)가 있거나 포트가 발견되면
    # rgon_auto_watcher.py의 QUEUE_PORTS에 해당 포트를 모두 추가하고 재기동!
    target_ports = sorted(set(ports) | {5000, 5050, 7777, 8000, 8080, 8099, 8765, 8766, 8787, 9000, 9999})
    if WATCHER_PY.exists():
        wtxt = WATCHER_PY.read_text(encoding="utf-8", errors="replace")
        wtxt_new = re.sub(
            r"QUEUE_PORTS\s*=\s*\[[^\]]*\]",
            f"QUEUE_PORTS = {repr(target_ports)}",
            wtxt
        )
        # /api/dispatch/next GET 요청에도 {"ok": true, "job": null} 응답하도록 보강
        wtxt_new = wtxt_new.replace(
            'self.wfile.write(b\'{"ok": true, "status": "online"}\')',
            'self.wfile.write(b\'{"ok": true, "status": "online", "job": null}\')'
        )
        WATCHER_PY.write_text(wtxt_new, encoding="utf-8")

        # 문지기 재기동
        ps_kill = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.CommandLine -like '*rgon_auto_watcher.py*' } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True)
        vbs = BASE_DIR / "rgon_watcher_silent.vbs"
        if vbs.exists():
            subprocess.Popen(["wscript.exe", str(vbs)], cwd=str(BASE_DIR))
        else:
            subprocess.Popen(["pythonw.exe", str(WATCHER_PY)], cwd=str(BASE_DIR))
        time.sleep(1.5)

    # 첫 번째 발견 포트로 실제 /api/queue 셀프 테스트!
    test_port = ports[0] if ports else 8765
    test_res = "테스트 전"
    try:
        req_data = json.dumps({"role": "rgon", "filename": "test_queue.txt", "code": "큐 개통 셀프 테스트 성공!"}).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{test_port}/api/queue",
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            test_res = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        test_res = f"오류: {e}"

    summary = (
        f"👑 [안총리 실행 큐 (/api/queue) 직통 개통 보고]\n"
        f"• 진짜 포트: {ports}\n"
        f"• 브릿지 파일: {bridge_files}\n"
        f"• 셀프 테스트(포트 {test_port}): {test_res}\n\n"
        f"[background.js 상단]\n{snippet[:600]}"
    )
    print(summary)
    if BRIDGE_PY.exists():
        subprocess.run([sys.executable, str(BRIDGE_PY), "--send-text", summary[:3500]], cwd=str(BASE_DIR))


if __name__ == "__main__":
    main()
Copy