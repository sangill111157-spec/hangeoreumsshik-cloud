import os
import re
import sys
import glob
import json
import time
import subprocess

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
EXT_DIR = os.path.join(ROOT, "chrome_omni_commander")
WATCHER_PY = os.path.join(ROOT, "rgon_auto_watcher.py")
MORNING_PY = os.path.join(ROOT, "rgon_morning_routine.py")
BRIDGE_PY = os.path.join(ROOT, "rgon_telegram_bridge.py")


def find_queue_ports_and_paths():
    ports = {8765, 8099, 5000, 5050, 9999}
    if os.path.exists(EXT_DIR):
        for fn in os.listdir(EXT_DIR):
            if fn.endswith((".js", ".json", ".html")):
                p = os.path.join(EXT_DIR, fn)
                try:
                    with open(p, "r", encoding="utf-8", errors="replace") as f:
                        txt = f.read()
                    for m in re.findall(r"(?:127\.0\.0\.1|localhost):(\d{2,5})", txt):
                        ports.add(int(m))
                except Exception:
                    pass
    return sorted(ports)


MORNING_CODE = r'''# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from datetime import datetime

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
SHEETS_PY = r"C:\Users\sangi\Desktop\run_all_sheets.py"
HEARTBEAT_PY = os.path.join(ROOT, "rgon_agency_heartbeat.py")
BRIDGE_PY = os.path.join(ROOT, "rgon_telegram_bridge.py")


def run_step(title, cmd, cwd=ROOT, timeout=180):
    print(f"▶ {title} 실행 중...")
    try:
        p = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout
        )
        return p.returncode, ((p.stdout or "") + "\n" + (p.stderr or "")).strip()
    except Exception as e:
        return 1, str(e)


def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    # 1. 4대 구글 시트 최신 동기화
    s_code, s_out = 1, "시트 스크립트 없음"
    if os.path.exists(SHEETS_PY):
        s_code, s_out = run_step("4대 구글 시트 통합 동기화", [sys.executable, SHEETS_PY], cwd=os.path.dirname(SHEETS_PY), timeout=180)

    # 2. 6대 청사 무인 박동 갱신
    h_code, h_out = run_step("6대 청사 무인 박동", [sys.executable, HEARTBEAT_PY], cwd=ROOT, timeout=60)

    # 3. 텔레그램 모닝 종합 브리핑 발송
    run_step("텔레그램 브리핑 발송", [sys.executable, BRIDGE_PY, "--send-brief"], cwd=ROOT, timeout=30)

    sheet_status = "✅ 4대 시트 동기화 성공" if s_code == 0 else f"⚠️ 시트 점검({s_code})"
    hb_status = "✅ 6대 청사 ALL OK" if h_code == 0 else f"⚠️ 청사 점검({h_code})"
    summary = (
        f"🌅 [RGON 사령부 07:00 모닝 종합 브리핑 완료 ({ts})]\n"
        f"• 구글 시트: {sheet_status}\n"
        f"• 6대 청사: {hb_status}\n"
        f"• 오늘 하루도 무토큰 자동화 사령부가 24시간 보좌합니다! 🫡👑"
    )
    run_step("모닝 인사 발송", [sys.executable, BRIDGE_PY, "--send-text", summary], cwd=ROOT, timeout=30)
    print("🎉 모닝 루틴 완료!")


if __name__ == "__main__":
    main()
'''


def patch_watcher_with_http_and_txt(ports):
    # rgon_auto_watcher.py 안에 로컬 HTTP 큐 수신 서버(모든 후보 포트) + omni_*.txt 감지기 장착
    with open(WATCHER_PY, "r", encoding="utf-8", errors="replace") as f:
        code = f.read()

    addon_marker = "# === RGON_HTTP_QUEUE_SERVER_V2 ==="
    if addon_marker in code:
        print("✅ 이미 HTTP 큐 수신 서버가 장착되어 있습니다.")
        return

    http_addon = f'''
{addon_marker}
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

QUEUE_PORTS = {repr(ports)}

class RGONQueueHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_cors(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self._send_cors(200)

    def do_GET(self):
        self._send_cors(200)
        self.wfile.write(b'{{"ok": true, "status": "online"}}')

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else ""
        text_payload = raw
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                text_payload = (
                    data.get("code") or data.get("text") or data.get("content")
                    or data.get("prompt") or data.get("payload") or raw
                )
        except Exception:
            pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        is_py = any(k in text_payload for k in ("import ", "def ", "if __name__", "# -*-"))
        if is_py:
            out_path = os.path.join(ROOT, f"omni_queue_{{ts}}.py")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text_payload)
        else:
            out_path = os.path.join(ROOT, f"ahn_queue_{{ts}}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text_payload)
            inbox = os.path.join(ROOT, "ahn_inbox_latest.txt")
            with open(inbox, "w", encoding="utf-8") as f:
                f.write(text_payload)
            try:
                subprocess.run(["clip.exe"], input=text_payload.encode("utf-16le"), timeout=5)
            except Exception:
                pass
            try:
                send_tg(f"📮 [안총리 실행 큐 접수 성공!]\\n클립보드 및 ahn_inbox_latest.txt 적재 완료!\\n\\n{{text_payload[:300]}}")
            except Exception:
                pass

        self._send_cors(200)
        resp = json.dumps({{"ok": True, "status": "queued", "file": os.path.basename(out_path)}})
        self.wfile.write(resp.encode("utf-8"))


def _start_queue_servers():
    for port in QUEUE_PORTS:
        def _serve(p=port):
            try:
                srv = HTTPServer(("127.0.0.1", p), RGONQueueHandler)
                srv.serve_forever()
            except Exception:
                pass
        t = threading.Thread(target=_serve, daemon=True)
        t.start()

_start_queue_servers()
'''
    # main() 호출 직전에 삽입
    if 'if __name__ == "__main__":' in code:
        code = code.replace('if __name__ == "__main__":', http_addon + '\n\nif __name__ == "__main__":')
    else:
        code += "\n" + http_addon

    with open(WATCHER_PY, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ rgon_auto_watcher.py 에 로컬 큐 수신 서버(포트 {ports}) 장착 완료!")


def register_morning_schedule():
    # 아침 7시 01분 윈도우 스케줄러 등록 + 기존 auto_ morning_briefing.bat 백업 연결
    bat_path = r"C:\trading\auto_ morning_briefing.bat"
    if os.path.exists(bat_path):
        bak_path = bat_path + ".bak"
        if not os.path.exists(bak_path):
            with open(bat_path, "rb") as src, open(bak_path, "wb") as dst:
                dst.write(src.read())
        with open(bat_path, "r", encoding="utf-8", errors="replace") as f:
            btxt = f.read()
        call_line = f'python "{MORNING_PY}"'
        if "rgon_morning_routine.py" not in btxt:
            if "pause" in btxt.lower():
                btxt = re.sub(r"(?i)^(\s*pause\b)", call_line + r"\n\1", btxt, count=1, flags=re.M)
            else:
                btxt = btxt.rstrip() + "\n" + call_line + "\n"
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(btxt)
            print("✅ 기존 아침 7시 배치 파일(auto_ morning_briefing.bat)에 모닝 루틴 비파괴 연결 완료!")

    # 이중 보장용 윈도우 스케줄러 \RGON_Morning_Briefing_0700 등록
    cmd = [
        "schtasks", "/Create", "/F",
        "/SC", "DAILY", "/ST", "07:01",
        "/TN", "RGON_Morning_Briefing_0700",
        "/TR", f'python.exe "{MORNING_PY}"'
    ]
    subprocess.run(cmd, capture_output=True)
    print("✅ 윈도우 스케줄러 매일 아침 07:01 [RGON_Morning_Briefing_0700] 등록 완료!")


def restart_watcher():
    ps_kill = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -like '*rgon_auto_watcher.py*' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True)
    vbs = os.path.join(ROOT, "rgon_watcher_silent.vbs")
    if os.path.exists(vbs):
        subprocess.Popen(["wscript.exe", vbs], cwd=ROOT)
    else:
        subprocess.Popen(["pythonw.exe", WATCHER_PY], cwd=ROOT)
    time.sleep(1.5)
    print("✅ 24시간 무토큰 문지기 로봇 재기동 완료!")


def main():
    print("🚀 [안총리 없이 무토큰 직통 수리] 1. 모닝 종합 브리핑 스크립트 생성...")
    with open(MORNING_PY, "w", encoding="utf-8") as f:
        f.write(MORNING_CODE.strip() + "\n")

    ports = find_queue_ports_and_paths()
    print(f"🚀 [2] 크롬 확장프로그램 큐 포트 탐색 완료: {ports}")
    patch_watcher_with_http_and_txt(ports)

    print("🚀 [3] 매일 아침 7시 스케줄러 비파괴 연결...")
    register_morning_schedule()

    print("🚀 [4] 문지기 로봇 재기동 및 모닝 브리핑 즉시 테스트 발송...")
    restart_watcher()
    subprocess.run([sys.executable, MORNING_PY], cwd=ROOT)


if __name__ == "__main__":
    main()
Copy