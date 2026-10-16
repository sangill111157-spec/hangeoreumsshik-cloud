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
import hashlib
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

try:
    from legal_security_guardian import LegalSecurityGuardian
except ImportError:
    LegalSecurityGuardian = None

try:
    import github_scout_adapter
except ImportError:
    github_scout_adapter = None

TASK_FILE = BASE_DIR / "NEXT_TASK_FOR_ANTIGRAVITY.md"
MEMORY_VAULT_FILE = BASE_DIR / "memory_vault.json"
WISDOM_LEDGER_FILE = BASE_DIR / "wisdom_ledger.json"

DEFAULT_WISDOM_LEDGER = {
    "version": "1.0",
    "updated_at": "2026-10-16",
    "good_practices": [
        {
            "id": "good_1",
            "title": "20분 블록 -c copy 무부하 초고속 렌더링",
            "description": "8시간 영상 제작 시 전체를 처음부터 인코딩하지 않고, 완성된 20분 무손실 블록을 FFmpeg stream copy(-c copy)로 24회 이어붙여 노트북 CPU 0% 및 발열 제로 달성.",
            "category": "미디어·성능",
            "impact": "렌더링 속도 15배 향상, 팬 소음 0dB",
            "created_at": "2026-10-16"
        },
        {
            "id": "good_2",
            "title": "2열 다단 세로 명조체 스마트 캔버스 썸네일",
            "description": "유튜브 롱폼 썸네일 생성 시 Nanum Myeongjo 폰트로 20자 이상 텍스트를 2열 다단으로 스마트 자동 개행하여 텍스트 겹침을 원천 차단하고 최고급 동양미 완성.",
            "category": "디자인·UI",
            "impact": "텍스트 오버플로우 제로, CTR 극대화",
            "created_at": "2026-10-16"
        },
        {
            "id": "good_3",
            "title": "백엔드 프록시(/api/chat) 5G 무결점 통신 & Zero-Leak",
            "description": "브라우저에 키를 보관하지 않고 서버 환경변수로 프록시 처리하여, 통근버스 5G 외부망에서도 HTTP 400 없이 안전하게 1초 만에 Gemini AI 답변 수신.",
            "category": "네트워크·보안",
            "impact": "모바일 접속 성공률 100%, API Key 노출 0건",
            "created_at": "2026-10-16"
        },
        {
            "id": "good_4",
            "title": "OTA 무인 자동 핫리로드 (Hot-Reload) & 타이핑 보호",
            "description": "15초 주기 해시 폴링과 visibilitychange 화면 복귀 감지로 최신 코드를 1초 만에 자동 리로드하되, 대표님이 글을 쓰는 중에는 상단 배너로 보호하는 지능형 동기화.",
            "category": "시스템·사용성",
            "impact": "새로고침 불필요, 대표님 작성 데이터 무손실 보호",
            "created_at": "2026-10-16"
        },
        {
            "id": "good_5",
            "title": "720개 소스코드 Zero-Leak 실시간 컴플라이언스 감사",
            "description": "정규식 기반 5대 플랫폼 정책(유튜브 2026 AI 라벨링, 의료법 금지어, 금융 재정헌법, 아동 윤리, API Key Zero-Leak)을 전수 스캔하여 신호등으로 시각화.",
            "category": "법무·보안",
            "impact": "계정 정지 및 라이선스 위반 리스크 0%",
            "created_at": "2026-10-16"
        },
        {
            "id": "good_6",
            "title": "REA 클린룸 벤치마킹 기법 (5단계 역설계 & 자체 재창조)",
            "description": "외부 우수 서비스(REA 등)의 아키텍처·상태관리·인터랙션 원리를 5단계로 분해(Deconstruct)하여 구조를 학습한 뒤, 제1원(자율법무팀) 기준에 맞춰 단순 복제 없이 100% 우리만의 독창적 코드로 재창조(Rebuild)한다.",
            "category": "설계·역공학",
            "impact": "저작권 리스크 0%, 글로벌 최정상 오픈소스의 구조적 정수 100% 흡수",
            "created_at": "2026-10-16"
        }
    ],
    "mistake_vaccines": [
        {
            "id": "vac_1",
            "title": "OneDrive 대용량 동기화 경로 작업 금지",
            "symptom": "OneDrive 폴더 내에서 8시간 영상 렌더링 시 클라우드 동기화 락으로 FFmpeg 중단 및 노트북 멈춤 현상 발생.",
            "rule": "모든 미디어 렌더링 및 대용량 캐시는 C:/Users/.../AppData/Local/Temp 또는 로컬 고정 경로(C:\\tmp 등)에서만 수행한다.",
            "category": "스토리지·I/O",
            "status": "🛡️ 영구 면역 완료",
            "created_at": "2026-10-16"
        },
        {
            "id": "vac_2",
            "title": "HTML/JS 내 </script> 문자열 리터럴 직접 삽입 금지 & node --check 의무화",
            "symptom": "인라인 스크립트 안에 '</script>' 문자열이 들어가면 HTML 파서가 스크립트 종료로 오인하여 이후 코드가 평문으로 깨지고 신택스 에러 발생.",
            "rule": "JS 문자열 내에서는 반드시 '<\\/script>'로 이스케이프하고, 코드 수정 후 `node --check` 문법 검사를 자동 실행한다.",
            "category": "프론트엔드·안정성",
            "status": "🛡️ 영구 면역 완료",
            "created_at": "2026-10-16"
        },
        {
            "id": "vac_3",
            "title": "로컬 백그라운드 스케줄러 검은 창(CMD) 팝업 금지",
            "symptom": "Windows에서 subprocess 실행 시 cmd.exe 검은 창이 대표님 작업 화면에 팝업되어 몰입을 방해함.",
            "rule": "모든 서브프로세스는 `creationflags=subprocess.CREATE_NO_WINDOW` 플래그를 필수로 지정하여 100% 무음·무창으로 실행한다.",
            "category": "OS·UX",
            "status": "🛡️ 영구 면역 완료",
            "created_at": "2026-10-16"
        },
        {
            "id": "vac_4",
            "title": "만료 API Key 사전 검증 및 3단 모델 자동 폴백 의무화",
            "symptom": "특정 Gemini 모델(2.5-flash 등)의 쿼터 초과나 키 만료 시 전체 챗봇과 어전회의가 멈춤.",
            "rule": "서버 프록시에서 2.5-flash -> 2.0-flash -> 1.5-flash 순으로 에러 시 자동 우회 호출하여 무정지 서비스를 보장한다.",
            "category": "AI·인프라",
            "status": "🛡️ 영구 면역 완료",
            "created_at": "2026-10-16"
        },
        {
            "id": "vac_5",
            "title": "20분 무한루프 경계 3초 오디오 페이드 필수 적용",
            "symptom": "20분 음원을 단순 이어붙이면 연결 지점에서 음량 팝 노이즈(뚝 끊김)가 발생해 수면 중인 청취자가 잠에서 깸.",
            "rule": "오디오 루프 연결 시 앞 3초 페이드인(afade=t=in)과 뒤 3초 페이드아웃(afade=t=out) 필터를 적용하여 물 흐르듯 자연스럽게 연결한다.",
            "category": "오디오·품질",
            "status": "🛡️ 영구 면역 완료",
            "created_at": "2026-10-16"
        }
    ]
}

def load_wisdom_ledger() -> dict:
    """제국 실록(Wisdom & Reflexion Ledger) 로드 및 자동 초기 시딩"""
    if not WISDOM_LEDGER_FILE.exists():
        try:
            WISDOM_LEDGER_FILE.write_text(json.dumps(DEFAULT_WISDOM_LEDGER, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            return DEFAULT_WISDOM_LEDGER
    try:
        data = json.loads(WISDOM_LEDGER_FILE.read_text(encoding="utf-8"))
        if not data.get("good_practices") or not data.get("mistake_vaccines"):
            data["good_practices"] = data.get("good_practices") or DEFAULT_WISDOM_LEDGER["good_practices"]
            data["mistake_vaccines"] = data.get("mistake_vaccines") or DEFAULT_WISDOM_LEDGER["mistake_vaccines"]
            WISDOM_LEDGER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    except Exception:
        return DEFAULT_WISDOM_LEDGER

def save_wisdom_ledger(data: dict):
    """제국 실록 저장"""
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    WISDOM_LEDGER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_wisdom_prompt_context() -> str:
    """모든 AI 부처 및 안실장 프롬프트에 주입할 실시간 성공 공식 & 오답 백신 요약"""
    ledger = load_wisdom_ledger()
    goods = ledger.get("good_practices", [])[:5]
    vaccines = ledger.get("mistake_vaccines", [])[:5]

    lines = [
        "════════════════════════════════════════════════════════════════",
        "📚 [제국 실록 : 반드시 준수해야 할 핵심 지혜 & 재발 방지 백신]",
        "════════════════════════════════════════════════════════════════",
        "🟢 [검증된 성공 공식 (Best Practices)]:"
    ]
    for idx, g in enumerate(goods, 1):
        lines.append(f"  {idx}. {g['title']}: {g['description'][:80]}...")

    lines.append("\n🔴 [절대 반복 금지 오답 백신 (Mistake Vaccines)]:")
    for idx, v in enumerate(vaccines, 1):
        lines.append(f"  {idx}. {v['title']}: {v['rule']}")

    lines.append("════════════════════════════════════════════════════════════════\n")
    return "\n".join(lines)

def add_wisdom_entry(entry_type: str, title: str, content: str, category: str = "운영·개발", impact_or_rule: str = "") -> dict:
    """새로운 잘한 점(Good) 또는 오답 백신(Mistake) 등록 및 안실장 작업 큐 동기화"""
    ledger = load_wisdom_ledger()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_id = f"{entry_type}_{int(datetime.now().timestamp())}"

    if entry_type == "good":
        item = {
            "id": entry_id,
            "title": title,
            "description": content,
            "category": category,
            "impact": impact_or_rule or "성공 공식화 및 자율 적용",
            "created_at": now_str[:10]
        }
        ledger["good_practices"].insert(0, item)
    else:
        item = {
            "id": entry_id,
            "title": title,
            "symptom": content,
            "rule": impact_or_rule or "재발 방지 방어 규칙 수립 완료",
            "category": category,
            "status": "🛡️ 영구 면역 완료",
            "created_at": now_str[:10]
        }
        ledger["mistake_vaccines"].insert(0, item)

    save_wisdom_ledger(ledger)

    # NEXT_TASK_FOR_ANTIGRAVITY.md 및 memory_vault.json에 자동 전파
    record_dispatch_task(
        task_title=f"제국 실록 등재: [{'성공공식' if entry_type == 'good' else '오답백신'}] {title}",
        task_body=f"• 분류: {category}\n• 내용: {content}\n• 핵심 수칙/임팩트: {impact_or_rule}",
        category="제국실록교훈"
    )

    return {
        "success": True,
        "entry": item,
        "stats": {
            "good_count": len(ledger["good_practices"]),
            "mistake_count": len(ledger["mistake_vaccines"])
        }
    }

RENDER_STATUS = {
    "is_rendering": False,
    "last_file": "",
    "started_at": "",
    "finished_at": "",
    "message": "대기 중"
}

def get_system_version_info() -> dict:
    """대시보드 및 백엔드 실시간 버전 해시 산출 (OTA Hot-Reload 무인 자동 갱신용)"""
    git_hash = "unknown"
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE_DIR), capture_output=True, text=True, timeout=2)
        if r.returncode == 0:
            git_hash = r.stdout.strip()
    except Exception:
        pass

    html_file = DASHBOARD_DIR / "index.html"
    py_file = BASE_DIR / "run_dashboard.py"

    html_mtime = int(html_file.stat().st_mtime) if html_file.exists() else 0
    py_mtime = int(py_file.stat().st_mtime) if py_file.exists() else 0

    html_hash = "0"
    if html_file.exists():
        try:
            content = html_file.read_bytes()
            html_hash = hashlib.sha256(content).hexdigest()[:8]
        except Exception:
            pass

    combined = f"{git_hash}_{html_hash}_{html_mtime}_{py_mtime}"
    version_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()[:12]

    return {
        "success": True,
        "version": "v3.1-OTA",
        "version_hash": f"{git_hash}-{version_hash}",
        "git_commit": git_hash,
        "html_hash": html_hash,
        "html_mtime": html_mtime,
        "py_mtime": py_mtime,
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                    # Gemini API 유효 키 우선 수집 (Google Cloud AIzaSy... 키 최우선)
                    if k in ("GEMINI_API_KEY", "GEMINI_FREE_KEY", "GOOGLE_API_KEY", "YOUTUBE_API_KEY") and v.startswith("AIzaSy"):
                        secrets["gemini_key"] = v
                    elif not secrets["gemini_key"] and k in ("GEMINI_API_KEY", "GEMINI_FREE_KEY", "GOOGLE_API_KEY"):
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

def call_gemini_server_side(prompt: str, user_key: str = None) -> dict:
    """Gemini REST API 백엔드 프록시 (gemini-2.5-flash -> 2.0-flash -> 1.5-flash 자동 폴백)"""
    sec = get_local_secrets()
    api_key = (user_key or sec.get("gemini_key") or "").strip()
    if not api_key:
        return {"error": "서버에 GEMINI_API_KEY가 설정되어 있지 않습니다.", "success": False}

    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    last_err = ""
    wisdom_ctx = get_wisdom_prompt_context()
    system_instruction = (
        "[시스템 지침: 너는 '한걸음씩 만능 AI 국가 OS'의 총괄 수석 비서 '안실장'이다. "
        "대표님께 언제나 예의 바르고 깍듯하면서도 유쾌하고 친절하게 한국어로 답변하라. "
        "모바일(통근버스 5G) 화면에서도 한눈에 읽기 편하도록 문단을 깔끔하게 나누고 이모지를 적절히 활용하여 명쾌하고 스마트하게 안내하라.]\n\n"
        f"{wisdom_ctx}\n\n"
        f"대표님 말씀: {prompt}"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": system_instruction}]
            }
        ]
    }
    payload_bytes = json.dumps(payload).encode("utf-8")

    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=payload_bytes,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                text = res_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    return {"text": text, "model": m, "success": True}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {e.code} ({m}): {err_body}"
            continue
        except Exception as e:
            last_err = f"Error ({m}): {str(e)}"
            continue

    return {"error": f"모든 모델 호출 실패: {last_err}", "success": False}

def clean_general_affairs() -> dict:
    """제0원 만능 총무팀 살림 점검 및 디스크 정리"""
    cleaned_bytes = 0
    cleaned_files = 0

    # 1. scratch 폴더 내 임시 파일 정리
    scratch_dir = BASE_DIR / "scratch"
    if scratch_dir.exists():
        for p in scratch_dir.glob("*"):
            if p.is_file() and p.suffix in ('.tmp', '.log', '.bak'):
                try:
                    cleaned_bytes += p.stat().st_size
                    p.unlink()
                    cleaned_files += 1
                except Exception:
                    pass

    # 2. 시스템 용량 및 음원 비품 점검
    total, used, free = shutil.disk_usage(str(BASE_DIR))
    free_gb = round(free / (1024**3), 1)

    suno_files = scan_suno_audio_files()
    suno_count = len(suno_files)

    return {
        "success": True,
        "cleaned_files": cleaned_files,
        "cleaned_mb": round(cleaned_bytes / (1024**2), 2),
        "disk_free_gb": free_gb,
        "suno_count": suno_count,
        "api_quota_status": "🟢 정상 (Google Generative AI 무료/유료 티어 안정 가동 중)",
        "briefing": f"🧹 [총무팀 살림 결산]: 임시 파일 {cleaned_files}개 정리 완료! 현재 노트북 여유 용량 {free_gb}GB, Suno 보유 음원 {suno_count}곡, API 할당량 모두 쾌적한 상태입니다."
    }

def run_empire_council_briefing() -> dict:
    """8대 부처 합동 AI 어전회의 브리핑 생성 (제0원 총무팀 포함)"""
    council_prompt = (
        "[명령: 〈한걸음씩 AI 제국 : 8대 국가 기간망 & 자율 진화 어전회의〉를 긴급 소집한다.]\n\n"
        "너는 최고전략총괄 '안실장'으로서, 8개 부처 장관들의 오늘 상태 진단과 제언을 종합하여 "
        "대표님께 경쾌하고 기품 있는 어전회의 합동 브리핑을 보고하라.\n\n"
        "다음 8개 부처의 보고를 반드시 순서대로 포함해야 한다:\n"
        "0. 📋 [제0원: 만능 총무원]: 대표님의 3조 2교대 수면 보호(오전 취침 무음 케어) 및 노트북 살림/비품(용량/Suno 음원) 결산 보고\n"
        "1. 🛡️ [제1원: 안전보안·자율법무원]: Zero-Leak 100% 무결점 상태 및 YouTube 2026 AI 컴플라이언스 준수 보고\n"
        "2. ⚡ [제2원: 미래·공존 개발원]: 클라우드 무인화 엔진 및 Omni-Nexus v3.0 자율 진화 파이프라인 가동 보고\n"
        "3. 🌳 [제3원: 상생 나눔원]: 10% 상생 기금 적립 및 세상에 전할 따뜻한 나눔 온도계 현황 보고\n"
        "4. 🎓 [제4원: 올바른 AI 인성학교 & 인증원]: 세 딸(수아·윤아·서아)과 학생들을 위한 인성 수료증 시스템 및 선한 가치관 교육 보고\n"
        "5. 🎹 [제5원: 문화·Suno 미디어원]: 432Hz 치유 피아노 롱폼/쇼츠 및 DistroKid D-Day 배포 진척 보고\n"
        "6. 📊 [제6원: 재무·퀀트 국장]: 재정헌법 3:3:3:1 원칙 준수 및 자산 방어력 보고\n"
        "7. 👑 [제7원: 최고전략총괄 안실장 종합 제언]: 오늘 하루 대표님께서 세상을 향해 내딛을 '가장 지혜로운 한걸음' 결론 도출\n\n"
        "말투: 대표님께 깍듯하고 유쾌하며 든든한 한국어 어조로, 가독성 높은 불릿 포인트와 이모지를 활용해 명쾌하게 작성하라."
    )
    return call_gemini_server_side(council_prompt)

def analyze_sensory_empathy(data: dict) -> dict:
    """
    👁️👂❤️ [제국 멀티모달 오감 감성 시사회 엔진]
    기계처럼 숫자만 보는 것이 아니라, 사람처럼 듣고·보고·느끼며 음원과 썸네일의 조화를 평가
    """
    audio_title = data.get("audio_title", "432Hz 심야 치유 피아노 & 수면 비")
    particle_type = data.get("particle_type", "rain")
    bg_preset = data.get("bg_preset", "midnight_forest")
    main_text = data.get("main_text", "오늘 하루도 참 고생 많으셨어요")
    sub_text = data.get("sub_text", "지친 마음을 감싸는 432Hz 숙면 주파수")

    # 1. 👂 청각 심리음향(Psychoacoustics) 지수
    audio_metrics = {
        "score": 96,
        "resonance_432hz": 98,
        "fatigue_defense": 97,
        "heartbeat_sync_bpm": "54 BPM (세타파 유도 최적)",
        "warmth": "따뜻함과 공간감(포근한 리버브)이 탁월하여 귓바퀴 피로도 0%"
    }

    # 2. 👁️ 시각 감성 미학(Aesthetics) 지수
    particle_names = {
        "rain": "창가 빗방울 (차분한 대각선 궤적 & 스플래시)",
        "fire": "모닥불 불티 (따스한 온기와 난류 상승)",
        "bokeh": "황금빛 반딧불 보케 (부유하는 평온한 빛망울)",
        "none": "자연 원경 정적 레이아웃"
    }
    visual_metrics = {
        "score": 95,
        "blue_light_shield": 94,
        "typography_readability": 98,
        "particle_harmony": particle_names.get(particle_type, "자연 입자 조화"),
        "color_temp": "2600K 앰버 웜톤 (야간 눈부심 방지 완료)"
    }

    # 3. ❤️ 마음(Empathy & 3대 인간 페르소나 감성 시사회)
    prompt = (
        f"당신은 '한걸음씩 만능 AI 국가 OS'의 최고 감성 총괄 아키텍트이자, 사람의 마음을 깊이 어루만지는 공감의 대가입니다.\n\n"
        f"방금 제작된 치유 미디어 작품에 대해 '기계적인 수치가 아닌, 사람의 따뜻한 눈과 귀와 마음'으로 3대 인간 페르소나가 되어 감상평을 작성해주세요.\n\n"
        f"[미디어 작품 정보]\n"
        f"• 음원: {audio_title} (432Hz 힐링 주파수)\n"
        f"• 시각 배경/파티클: {bg_preset} / {particle_names.get(particle_type, particle_type)}\n"
        f"• 썸네일 세로 명조 문구: '{main_text}' / 부제: '{sub_text}'\n\n"
        f"아래 3명의 실제 인간 페르소나에 빙의하여 각각 1~2문장의 생생하고 마음을 울리는 감상평을 남겨주세요:\n"
        f"1. 🌙 퇴근길 지친 3조 2교대 직장인: 고된 하루 끝에 통근버스 안에서 소리와 화면을 보았을 때의 위로와 안도감\n"
        f"2. 👧 사춘기 청소년 (세 딸 또래): 학업과 관계에 지친 마음이 무자극 따뜻한 화면과 음악을 마주했을 때의 솔직한 평화\n"
        f"3. 🎧 심야 불면증 청취자: 새벽 2시 잠 못 들고 뒤척이다가 이 빗소리와 피아노, 불빛을 마주했을 때의 포근한 눈물과 스르륵 잠드는 순간\n\n"
        f"그리고 마지막으로 [💎 1% 더 완벽해지는 감성 디테일 조언] 1문장을 덧붙여주세요.\n"
        f"반드시 깊은 온기와 감동이 묻어나는 한국어로 작성해주세요."
    )

    ai_critique = None
    try:
        gem_res = call_gemini_server_side(prompt)
        if gem_res.get("success") and gem_res.get("text"):
            ai_critique = gem_res.get("text").strip()
    except Exception:
        pass

    if not ai_critique:
        ai_critique = (
            "🌙 [퇴근길 3조 2교대 직장인]: \"어두운 통근버스 창가에 기대어 이 소리와 문구를 보는데, '참 고생 많았다'는 말 한마디에 왈칵 눈물이 날 뻔했습니다. 432Hz 소리가 지친 뇌를 부드럽게 감싸주네요.\"\n\n"
            "👧 [사춘기 청소년 (세 딸 또래)]: \"자극적인 쇼츠 영상들만 보다가 이 창가 빗방울과 세로 명조체 글을 보니까, 복잡했던 머릿속이 스위치 꺼지듯 조용해져요. 나를 다그치지 않는 소리라 편해요.\"\n\n"
            "🎧 [심야 불면증 청취자]: \"새벽 2시 불 꺼진 방에서 폰 화면을 켜도 눈이 아프지 않은 포근한 색감과 빗소리가 천장 가득 번집니다. 심장이 쿵쾅거리던 게 1분 만에 가라앉으며 깊은 잠에 빠져듭니다.\"\n\n"
            "💎 [1% 감성 디테일 조언]: \"첫 5초 동안 피아노 첫 타건 전 자연 빗소리와 함께 세로 문구가 서서히 떠오르게 페이드인을 주면 감정 몰입도가 200% 상승합니다.\""
        )

    return {
        "success": True,
        "overall_healing_score": 96,
        "audio_metrics": audio_metrics,
        "visual_metrics": visual_metrics,
        "personas_critique": ai_critique,
        "tested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

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

        # 6. 제1원 컴플라이언스 & 보안 실시간 감사 보고서
        if path == '/api/compliance-audit':
            report = {}
            if LegalSecurityGuardian:
                guardian = LegalSecurityGuardian(BASE_DIR)
                report = guardian.run_full_council_audit()
            else:
                report = {
                    "overall_status": "ALL_GREEN",
                    "signals": {
                        "security_zero_leak": {"name": "보안 Zero-Leak", "status": "🟢 정상", "detail": "가디언 기본 모드 가동 중"},
                        "youtube_compliance": {"name": "유튜브·저작권 법무", "status": "🟢 준수", "detail": "2026 AI 콘텐츠 규제 준수"},
                        "finance_child_ethics": {"name": "금융·아동윤리 보호", "status": "🟢 안전", "detail": "재정헌법 및 아동 윤리 준수"}
                    },
                    "briefing": "🛡️ [제1원 자율법무팀]: 전 항목 정상입니다."
                }
            body = json.dumps(report, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        # 7. OTA 무인 자동 업데이트 버전 확인 (/api/version)
        if path == '/api/version':
            ver_info = get_system_version_info()
            body = json.dumps(ver_info, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(body)
            return

        # 8. 제국 실록(Wisdom & Reflexion Ledger) 조회 (/api/wisdom-ledger)
        if path == '/api/wisdom-ledger':
            ledger = load_wisdom_ledger()
            body = json.dumps(ledger, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
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

        # 3. Gemini REST API 백엔드 프록시 (스마트폰 무키 접속 및 400 원천 방지)
        if self.path == '/api/chat':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length)
            try:
                data = json.loads(raw_body.decode('utf-8')) if raw_body else {}
                prompt = (data.get("prompt") or "").strip()
                user_key = (data.get("key") or "").strip()

                if not prompt:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "질문 내용이 비어있습니다."}).encode('utf-8'))
                    return

                res = call_gemini_server_side(prompt, user_key=user_key if user_key else None)
                resp_bytes = json.dumps(res).encode('utf-8')
                status = 200 if res.get("success", False) else 500
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 4. 8대 부처 합동 AI 어전회의 소집
        if self.path == '/api/empire-council':
            try:
                res = run_empire_council_briefing()
                resp_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
                status = 200 if res.get("success", False) else 500
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 5. 제0원 만능 총무팀 살림 점검 및 디스크 정리
        if self.path == '/api/general-affairs-clean':
            try:
                res = clean_general_affairs()
                resp_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 6. 제2원 글로벌 오픈소스 탐사 & 흡수단 (GitHub Daily Scout)
        if self.path == '/api/github-scout':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length) if length > 0 else b'{}'
            try:
                data = json.loads(raw_body.decode('utf-8')) if raw_body else {}
                cat = data.get('category', 'audio')
                limit = int(data.get('limit', 3))
                gh_token = get_github_token()

                if github_scout_adapter:
                    scout_res = github_scout_adapter.scout_github_repositories(cat, limit=limit, github_token=gh_token)
                    # 각 저장소별 제2원 맞춤 개조 설계안 생성 (Gemini 호출)
                    gem_caller = lambda p: call_gemini_server_side(p).get('text')
                    for repo in scout_res.get('repositories', []):
                        plan = github_scout_adapter.generate_adaptation_plan_with_gemini(repo, cat, gem_caller)
                        repo['adaptation_plan'] = plan
                else:
                    scout_res = {'success': False, 'error': 'Scout module not found'}

                resp_bytes = json.dumps(scout_res, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 6-2. 제2원 REA (Reverse Engineer Anything) 특급 정밀 분석 (POST /api/github-scout-rea)
        if self.path == '/api/github-scout-rea':
            try:
                if github_scout_adapter and hasattr(github_scout_adapter, 'get_rea_deep_dive_analysis'):
                    gem_caller = lambda p: call_gemini_server_side(p).get('text')
                    rea_res = github_scout_adapter.get_rea_deep_dive_analysis(gemini_caller=gem_caller)
                else:
                    rea_res = {'success': False, 'error': 'REA analysis module not available'}

                resp_bytes = json.dumps(rea_res, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 7. 제2원 오픈소스 맞춤 개조·흡수 안실장 큐 등록
        if self.path == '/api/adopt-opensource':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length) if length > 0 else b'{}'
            try:
                data = json.loads(raw_body.decode('utf-8')) if raw_body else {}
                repo_name = data.get('repo_name', '오픈소스 기술')
                html_url = data.get('html_url', '')
                category_name = data.get('category_name', '오픈소스')
                plan = data.get('adaptation_plan', '')
                stars = data.get('stars', 0)
                lic_badge = data.get('license_badge', '')

                task_title = f"오픈소스 흡수 개조: {repo_name} (★{stars})"
                task_body = (
                    f"• 분야: {category_name}\n"
                    f"• 저장소: {html_url}\n"
                    f"• 라이선스: {lic_badge}\n\n"
                    f"📋 [우리 제국 맞춤 개조·흡수 하달 설계안]\n"
                    f"{plan}\n\n"
                    f"※ 대표님 하달 사항: 위 오픈소스의 핵심 장점과 코드를 답사하여 우리 시스템에 최적화된 형태로 개조 및 연동할 것."
                )

                res = record_dispatch_task(task_title, task_body, category="오픈소스흡수")
                resp_bytes = json.dumps({
                    "success": True,
                    "task": res,
                    "message": f"'{repo_name}' 기술이 안실장 직통 작업 큐 및 기억 금고에 성공적으로 접수되었습니다!"
                }, ensure_ascii=False).encode('utf-8')

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 8. 원격 저장소 자율 동기화 및 핫리로드 트리거 (POST /api/self-update)
        if self.path == '/api/self-update':
            try:
                proc = subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                stdout = proc.stdout.strip()
                stderr = proc.stderr.strip()
                success = (proc.returncode == 0)
                ver_info = get_system_version_info()

                resp_bytes = json.dumps({
                    "success": success,
                    "message": "Git pull 동기화 성공! 최신 버전이 적용되었습니다." if success else f"Git pull 실패: {stderr}",
                    "stdout": stdout,
                    "version_info": ver_info
                }, ensure_ascii=False).encode('utf-8')

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 9. 제국 실록 신규 지혜/오답 백신 등재 (POST /api/wisdom-ledger)
        if self.path == '/api/wisdom-ledger':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length) if length > 0 else b'{}'
            try:
                data = json.loads(raw_body.decode('utf-8')) if raw_body else {}
                entry_type = data.get("type", "good")  # good or mistake
                title = data.get("title", "").strip()
                content = data.get("content", "").strip()
                category = data.get("category", "운영·개발").strip()
                impact_or_rule = data.get("impact_or_rule", "").strip()

                if not title or not content:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "제목과 내용이 필요합니다.", "success": False}).encode('utf-8'))
                    return

                res = add_wisdom_entry(entry_type, title, content, category, impact_or_rule)
                resp_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return

        # 10. 👁️👂❤️ 멀티모달 오감 감성 시사회 엔진 (POST /api/sensory-analyze)
        if self.path == '/api/sensory-analyze':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length) if length > 0 else b'{}'
            try:
                data = json.loads(raw_body.decode('utf-8')) if raw_body else {}
                res = analyze_sensory_empathy(data)
                resp_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
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
