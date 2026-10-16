"""
══════════════════════════════════════════════════════════════════
 한걸음씩 만능 AI 국가 OS (Omni-Nexus v2.0) 백엔드 런처
 run_dashboard.py
 
 [핵심 백엔드 API]
 1. GET  /api/config            : 로컬 토큰 자동 감지 및 브라우저 주입
 2. GET  /api/suno-files         : PC 다운로드 및 작업 폴더 오디오 목록
 3. GET  /api/audio?path=...     : 브라우저 내 오디오 미리듣기 스트리밍
 4. POST /api/render-suno        : 432Hz 8시간 롱폼 + 세로 쇼츠 백그라운드 렌더링
 5. POST /api/dispatch-to-agent  : 안실장 직통 태스크 하달 (NEXT_TASK_FOR_ANTIGRAVITY.md & memory_vault.json)
 6. GET  /api/system-status      : NVDA(8000) 헬스체크, 디스크 용량, 렌더러 상태
══════════════════════════════════════════════════════════════════
"""

import os
import sys
import io
import json
import socket
import shutil
import threading
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
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

TASK_FILE = BASE_DIR / "NEXT_TASK_FOR_ANTIGRAVITY.md"
MEMORY_VAULT_FILE = BASE_DIR / "memory_vault.json"

RENDER_STATUS = {
    "is_rendering": False,
    "last_file": "",
    "started_at": "",
    "finished_at": "",
    "message": "대기 중"
}

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
    """로컬 설정 파일들을 스캔하여 Gemini, Telegram 키 수집"""
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

def scan_suno_audio_files() -> list:
    """PC 다운로드 폴더 및 작업 폴더에서 최근 오디오 파일 검색"""
    search_dirs = [
        Path.home() / "Downloads",
        BASE_DIR / "assets",
        BASE_DIR / "output_healing",
        BASE_DIR
    ]
    extensions = {".mp3", ".wav", ".m4a"}
    found_files = []
    seen_paths = set()

    for s_dir in search_dirs:
        if not s_dir.exists():
            continue
        try:
            for item in s_dir.iterdir():
                if item.is_file() and item.suffix.lower() in extensions:
                    resolved = str(item.resolve())
                    if resolved in seen_paths:
                        continue
                    seen_paths.add(resolved)
                    stat = item.stat()
                    mtime_dt = datetime.fromtimestamp(stat.st_mtime)
                    found_files.append({
                        "name": item.name,
                        "path": resolved,
                        "folder": s_dir.name,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "mtime": stat.st_mtime,
                        "mtime_str": mtime_dt.strftime("%m-%d %H:%M")
                    })
        except Exception:
            pass

    found_files.sort(key=lambda x: x["mtime"], reverse=True)
    return found_files[:30]

def notify_telegram(title: str, message: str):
    """텔레그램 관제탑 발송 연동"""
    try:
        from control_tower_bot import send_briefing
        send_briefing(title, message)
    except Exception as e:
        print(f"[텔레그램 알림 예외] {e}")

def run_suno_render_worker(audio_path: str, hours: int = 8, ambient_vol: float = 0.25, shorts_text: str = ""):
    """백그라운드 롱폼 & 쇼츠 렌더러"""
    global RENDER_STATUS
    RENDER_STATUS["is_rendering"] = True
    RENDER_STATUS["last_file"] = Path(audio_path).name
    RENDER_STATUS["started_at"] = datetime.now().strftime("%H:%M:%S")
    RENDER_STATUS["message"] = f"'{RENDER_STATUS['last_file']}' 432Hz 렌더링 진행 중..."

    cmd = [
        sys.executable,
        str(BASE_DIR / "healing_music_producer.py"),
        "--piano", str(audio_path),
        "--hours", str(hours),
        "--ambient-vol", str(ambient_vol)
    ]
    if shorts_text:
        cmd.extend(["--shorts-text", shorts_text])

    try:
        res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode == 0:
            msg = (
                f"✅ **Suno 432Hz 힐링 비디오 렌더링 완성!**\n\n"
                f"• 음원: `{Path(audio_path).name}`\n"
                f"• 생성 결과: 20분 마스터, {hours}시간 롱폼 비디오, 25초 세로 쇼츠\n"
                f"• 저장 경로: `output_healing/`"
            )
            RENDER_STATUS["is_rendering"] = False
            RENDER_STATUS["finished_at"] = datetime.now().strftime("%H:%M:%S")
            RENDER_STATUS["message"] = "렌더링 완료! 결과물이 output_healing에 준비되었습니다."
            notify_telegram("🎬 [한걸음씩 Suno 렌더러]", msg)
        else:
            RENDER_STATUS["is_rendering"] = False
            RENDER_STATUS["message"] = "렌더링 실패"
            notify_telegram("⚠️ [Suno 렌더러 에러]", f"렌더링 실패:\n{res.stderr[-500:]}")
    except Exception as e:
        RENDER_STATUS["is_rendering"] = False
        RENDER_STATUS["message"] = f"예외 발생: {e}"
        notify_telegram("❌ [Suno 렌더러 예외]", str(e))

def check_nvda_health() -> dict:
    """로컬 NVDA 트레이딩 FastAPI(8000) 생존 여부 확인"""
    url = "http://127.0.0.1:8000/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OmniNexus/2.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                return {"alive": True, "status": "정상 가동 (Online)"}
    except Exception:
        pass
    return {"alive": False, "status": "대기 / 오프라인 (Offline)"}

def get_system_metrics() -> dict:
    """시스템 상태 (디스크, NVDA, 렌더링 파일 목록)"""
    # 디스크 공간
    total, used, free = shutil.disk_usage(str(BASE_DIR))
    disk_info = {
        "total_gb": round(total / (1024**3), 1),
        "free_gb": round(free / (1024**3), 1),
        "free_pct": round((free / total) * 100, 1)
    }

    # 최근 렌더링 파일
    output_dir = BASE_DIR / "output_healing"
    recent_outputs = []
    if output_dir.exists():
        for p in output_dir.glob("*.mp4"):
            st = p.stat()
            recent_outputs.append({
                "name": p.name,
                "size_mb": round(st.st_size / (1024**2), 1),
                "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%m-%d %H:%M")
            })
        recent_outputs.sort(key=lambda x: x["mtime"], reverse=True)

    nvda = check_nvda_health()

    return {
        "nvda": nvda,
        "disk": disk_info,
        "render_status": RENDER_STATUS,
        "recent_outputs": recent_outputs[:5]
    }

def record_dispatch_task(task_title: str, task_body: str, category: str = "기획/지시") -> dict:
    """안실장 직통 태스크 하달 큐에 기록"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. NEXT_TASK_FOR_ANTIGRAVITY.md 업데이트
    header = f"\n\n## 📌 [{category}] {task_title} (접수시각: {now_str})\n\n"
    content = header + task_body.strip() + "\n\n---\n"

    if not TASK_FILE.exists():
        TASK_FILE.write_text("# 📋 안실장 직통 하달 작업 큐 (NEXT_TASK_FOR_ANTIGRAVITY.md)\n", encoding="utf-8")

    with open(TASK_FILE, "a", encoding="utf-8") as f:
        f.write(content)

    # 2. memory_vault.json 업데이트
    vault = []
    if MEMORY_VAULT_FILE.exists():
        try:
            vault = json.loads(MEMORY_VAULT_FILE.read_text(encoding="utf-8"))
        except Exception:
            vault = []

    vault_entry = {
        "id": f"mem_{int(datetime.now().timestamp())}",
        "timestamp": now_str,
        "category": category,
        "title": task_title,
        "content": task_body
    }
    vault.insert(0, vault_entry)
    MEMORY_VAULT_FILE.write_text(json.dumps(vault[:100], ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. 텔레그램 알림
    tg_msg = f"🔔 *[안실장 직통 작업 큐 등록]*\n\n• 분류: {category}\n• 제목: *{task_title}*\n\n{task_body[:200]}..."
    notify_telegram("🤖 [사령부 작업 하달]", tg_msg)

    return {"status": "ok", "task_file": str(TASK_FILE), "vault_id": vault_entry["id"]}

def find_available_port(start_port: int = 8501) -> int:
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return start_port

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. 설정 자동 주입
        if path == '/api/config':
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

        # 2. Suno MP3 목록
        if path == '/api/suno-files':
            files = scan_suno_audio_files()
            body = json.dumps({"files": files, "render_status": RENDER_STATUS}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        # 3. 오디오 미리듣기 스트리밍
        if path == '/api/audio':
            audio_p = query.get("path", [""])[0]
            if audio_p and Path(audio_p).exists() and Path(audio_p).is_file():
                try:
                    f_path = Path(audio_p)
                    content_type = "audio/mpeg" if f_path.suffix.lower() == ".mp3" else "audio/wav"
                    data = f_path.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    return
            self.send_response(404)
            self.end_headers()
            return

        # 4. 시스템 상태 (NVDA, 디스크, 렌더링 파일)
        if path == '/api/system-status':
            metrics = get_system_metrics()
            body = json.dumps(metrics).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        # 5. 기억 금고 목록
        if path == '/api/memory-vault':
            vault = []
            if MEMORY_VAULT_FILE.exists():
                try:
                    vault = json.loads(MEMORY_VAULT_FILE.read_text(encoding="utf-8"))
                except Exception:
                    pass
            body = json.dumps({"memories": vault}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 루트 및 index.html 요청 시 항상 최신 파일 서빙 (캐시 방지 헤더 강제 주입)
        if path in ('/', '/index.html', ''):
            html_file = DASHBOARD_DIR / "index.html"
            if html_file.exists():
                data = html_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.end_headers()
                self.wfile.write(data)
                return

        return super().do_GET()

    def do_POST(self):
        # 1. Suno 렌더링
        if self.path == '/api/render-suno':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length)
            try:
                data = json.loads(raw_body.decode('utf-8'))
                file_path = data.get("file_path", "").strip()
                hours = int(data.get("hours", 8))
                ambient_vol = float(data.get("ambient_vol", 0.25))
                shorts_text = data.get("shorts_text", "오늘 하루도 참 고생 많으셨어요.")

                if not file_path or not Path(file_path).exists():
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "오디오 파일 경로를 찾을 수 없습니다."}).encode('utf-8'))
                    return

                if RENDER_STATUS["is_rendering"]:
                    self.send_response(409)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "이미 다른 렌더링 작업이 진행 중입니다."}).encode('utf-8'))
                    return

                th = threading.Thread(
                    target=run_suno_render_worker,
                    args=(file_path, hours, ambient_vol, shorts_text),
                    daemon=True
                )
                th.start()

                resp_data = {
                    "status": "started",
                    "file_name": Path(file_path).name,
                    "hours": hours,
                    "message": "백그라운드 렌더링이 가동되었습니다. 완료 시 텔레그램으로 알림이 전송됩니다!"
                }
                body = json.dumps(resp_data).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        # 2. 안실장 직통 작업 하달 큐
        if self.path == '/api/dispatch-to-agent':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length)
            try:
                data = json.loads(raw_body.decode('utf-8'))
                title = data.get("title", "사령부 작업 지시").strip()
                body_content = data.get("content", "").strip()
                category = data.get("category", "개발/기획")

                if not body_content:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "작업 내용이 비어있습니다."}).encode('utf-8'))
                    return

                res = record_dispatch_task(title, body_content, category)
                resp_bytes = json.dumps(res).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass

def get_local_wifi_ip() -> str:
    """동일 Wi-Fi 공유기 내 스마트폰 접속용 로컬 IP 확인"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()

def main():
    if not DASHBOARD_DIR.exists():
        print(f"❌ 오류: 대시보드 폴더를 찾을 수 없습니다: {DASHBOARD_DIR}")
        sys.exit(1)

    port = find_available_port(DEFAULT_PORT)
    # 0.0.0.0 바인딩: PC 로컬 및 동일 Wi-Fi 스마트폰 접속 허용
    server_address = ('0.0.0.0', port)
    httpd = ThreadingHTTPServer(server_address, DashboardHandler)

    gh_token = get_github_token()
    sec = get_local_secrets()
    wifi_ip = get_local_wifi_ip()

    masked_gh = f"{gh_token[:4]}***{gh_token[-3:]}" if len(gh_token) > 8 else "미감지"
    masked_gemini = f"{sec['gemini_key'][:4]}***{sec['gemini_key'][-3:]}" if len(sec['gemini_key']) > 8 else "미감지"
    masked_tg = f"{sec['telegram_token'][:4]}***{sec['telegram_token'][-3:]}" if len(sec['telegram_token']) > 8 else "미감지"

    print("═" * 74)
    print(" 🏛️  한걸음씩 만능 AI 국가 OS (Omni-Nexus v2.0) 서버 가동 중")
    print("═" * 74)
    print(f" 💻 PC 로컬 접속     : http://127.0.0.1:{port}")
    print(f" 📱 스마트폰(Wi-Fi)   : http://{wifi_ip}:{port}")
    print(f" 📦 관제 대상 저장소  : {REPO_NAME}")
    print(" ── 보안 키 자동 주입 상태 ──")
    print(f"  • GitHub CLI Token : {masked_gh} (자동 주입 준비 완료)")
    print(f"  • Gemini API Key    : {masked_gemini} (자동 주입 준비 완료)")
    print(f"  • Telegram Bot      : {masked_tg} (Chat ID: {sec['telegram_chat_id']})")
    print(" ── 5대 전문 워크스페이스 활성화 ──")
    print("  • Tab 1. 🎛️ 통합 관제 사령부 (GitHub Cloud & 재정 헌법 계산기)")
    print("  • Tab 2. 🎹 Suno AI & 썸네일 프로듀싱 스튜디오 (음원 스트리밍 & 캔버스)")
    print("  • Tab 3. 💬 AI 소통 & OSMU 멀티 개발실 (음성인식 마이크 & 안실장 큐)")
    print("  • Tab 4. 👨‍👧‍👧 세 딸 인성 교육 게임 연구소 (인성 밸런스 라이브 & 웹게임 내보내기)")
    print("  • Tab 5. 🧠 기억 금고 & 보안 설정 (Memory Vault & Zero-Leak)")
    print("═" * 74)
    print(" 🛑 서버를 종료하시려면 콘솔에서 Ctrl + C 를 누르세요.")
    print("═" * 74)

    # 기본 브라우저 자동 오픈
    try:
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Omni-Nexus v2.0 서버를 안전하게 종료했습니다.")
        httpd.server_close()

if __name__ == "__main__":
    main()
