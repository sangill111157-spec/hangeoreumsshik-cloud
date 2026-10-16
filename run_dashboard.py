"""
══════════════════════════════════════════════════════════════════
 한걸음씩 만능 AI 사령부 대시보드 원클릭 스마트 런처
 run_dashboard.py
 
 [핵심 기능]
 1. 로컬 환경 자동 스캔:
    - GitHub CLI (gh auth token) 토큰 자동 추출
    - 로컬 config/.env 에서 Gemini API 키 추출
    - 로컬 telegram_setup.json / config/.env 에서 텔레그램 토큰 및 Chat ID 추출
 2. Zero-Leak 로컬 주입 서버 (포트 8501):
    - 대시보드 정적 웹앱(dashboard/index.html) 서빙
    - /api/config 엔드포인트를 통해 브라우저 localStorage로 무부하·무입력 자동 주입
 3. 기본 웹브라우저 자동 오픈
══════════════════════════════════════════════════════════════════
"""

import os
import sys
import io
import json
import socket
import subprocess
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# 콘솔 UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = BASE_DIR / "dashboard"
DEFAULT_PORT = 8501
REPO_NAME = "sangill111157-spec/hangeoreumsshik-cloud"

def get_github_token() -> str:
    """GitHub CLI 또는 환경변수에서 PAT 토큰 자동 추출"""
    tok = os.getenv("GITHUB_TOKEN", "").strip()
    if tok:
        return tok

    gh_paths = [
        "gh",
        r"C:\Program Files\GitHub CLI\gh.exe",
        r"C:\Program Files (x86)\GitHub CLI\gh.exe"
    ]
    for gh in gh_paths:
        try:
            res = subprocess.run([gh, "auth", "token"], capture_output=True, text=True, check=True)
            t = res.stdout.strip()
            if t:
                return t
        except Exception:
            pass
    return ""

def get_local_secrets() -> dict:
    """로컬 설정 파일들을 뒤져서 Gemini, Telegram 키를 수집"""
    secrets = {
        "gemini_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", "").strip()
    }

    env_paths = [
        BASE_DIR / ".env",
        BASE_DIR / "config" / ".env",
        Path(r"C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation\config\.env")
    ]
    for ep in env_paths:
        if ep.exists():
            try:
                for line in ep.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if not secrets["gemini_key"] and k in ("GEMINI_API_KEY", "GEMINI_FREE_KEY", "GOOGLE_API_KEY"):
                        secrets["gemini_key"] = v
                    if not secrets["telegram_token"] and k in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN"):
                        secrets["telegram_token"] = v
                    if not secrets["telegram_chat_id"] and k in ("TELEGRAM_CHAT_ID", "CHAT_ID"):
                        secrets["telegram_chat_id"] = v
            except Exception:
                pass

    # 텔레그램 Connect-AI 설정 폴더 탐색
    tg_json_paths = [
        Path(r"C:\Users\sangi\.connect-ai-brain\_company\_agents\secretary\tools\telegram_setup.json"),
        BASE_DIR / "telegram_setup.json"
    ]
    for jp in tg_json_paths:
        if jp.exists():
            try:
                data = json.loads(jp.read_text(encoding="utf-8"))
                for k, v in data.items():
                    k_upper = k.upper()
                    if not secrets["telegram_token"] and k_upper in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN", "BOT_TOKEN"):
                        secrets["telegram_token"] = str(v)
                    if not secrets["telegram_chat_id"] and k_upper in ("TELEGRAM_CHAT_ID", "CHAT_ID"):
                        secrets["telegram_chat_id"] = str(v)
            except Exception:
                pass

    return secrets

def find_available_port(start_port: int = 8501) -> int:
    """사용 가능한 로컬 포트 탐색"""
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return start_port

class DashboardHandler(SimpleHTTPRequestHandler):
    """대시보드 전용 HTTP 핸들러"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        # 1. 설정 자동 주입 API
        if self.path == '/api/config':
            gh_token = get_github_token()
            sec = get_local_secrets()
            payload = {
                "github_token": gh_token,
                "gemini_key": sec["gemini_key"],
                "telegram_token": sec["telegram_token"],
                "telegram_chat_id": sec["telegram_chat_id"],
                "repo": REPO_NAME
            }
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        # 2. 루트 요청 시 index.html 서빙
        if self.path == '/' or self.path == '':
            self.path = '/index.html'

        return super().do_GET()

    def log_message(self, format, *args):
        # 콘솔을 깨끗하게 유지하기 위해 단순 정적 요청 로그는 최소화
        pass

def main():
    if not DASHBOARD_DIR.exists():
        print(f"❌ 오류: 대시보드 폴더를 찾을 수 없습니다: {DASHBOARD_DIR}")
        sys.exit(1)

    port = find_available_port(DEFAULT_PORT)
    server_address = ('127.0.0.1', port)
    httpd = ThreadingHTTPServer(server_address, DashboardHandler)

    gh_token = get_github_token()
    sec = get_local_secrets()

    masked_gh = f"{gh_token[:4]}***{gh_token[-3:]}" if len(gh_token) > 8 else "미감지"
    masked_gemini = f"{sec['gemini_key'][:4]}***{sec['gemini_key'][-3:]}" if len(sec['gemini_key']) > 8 else "미감지"
    masked_tg = f"{sec['telegram_token'][:4]}***{sec['telegram_token'][-3:]}" if len(sec['telegram_token']) > 8 else "미감지"

    print("═" * 68)
    print(" 🌿 한걸음씩 만능 AI 사령부 대시보드 런처 가동 중 (v2.0 Cloud Active)")
    print("═" * 68)
    print(f" 🌐 로컬 접속 주소: http://localhost:{port}")
    print(f" 📦 관제 대상 저장소: {REPO_NAME}")
    print(" ── 보안 키 자동 주입 상태 ──")
    print(f"  • GitHub CLI Token : {masked_gh} (자동 주입 준비 완료)")
    print(f"  • Gemini API Key    : {masked_gemini} (자동 주입 준비 완료)")
    print(f"  • Telegram Bot      : {masked_tg} (Chat ID: {sec['telegram_chat_id']})")
    print("═" * 68)
    print(" 🚀 기본 웹브라우저로 대시보드를 띄웁니다! (수동 입력 필요 없음)")
    print(" 🛑 대시보드를 종료하시려면 콘솔에서 Ctrl + C 를 누르세요.")
    print("═" * 68)

    # 브라우저 자동 오픈
    webbrowser.open(f"http://localhost:{port}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 한걸음씩 만능 AI 사령부 대시보드 서버를 안전하게 종료했습니다.")
        httpd.server_close()

if __name__ == "__main__":
    main()
