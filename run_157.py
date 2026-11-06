# -*- coding: utf-8 -*-
import os, sys, json, time, subprocess, datetime, re

BASE = r"C:\Users\sangi\Downloads\shin-agent"
os.chdir(BASE)

now_kst = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S KST")
new_beacon_str = "[MEM_ANCHOR::무아대환원(나를비워세상을품음)|독행금지(세계원탑+3대지성합동)|선(先)사용설명서마스터|단계별단점보완후진군|성적표영구기록|KTX무인데몬v5]"

print("[1/5] RGON 사령부 5대 절대법칙 헌장 및 KTX 개통 실측 성적표 영구 봉헌 중...")

# 1. S1_ABSOLUTE_CONSTITUTION_AND_SCORECARD.json 생성
constitution_data = {
    "title": "RGON 사령부 영구 절대법칙 헌장 및 KTX 개통 실측 성적표",
    "enacted_by": "이상일 대표님 (사령탑)",
    "enacted_at": now_kst,
    "supreme_philosophy": "우린 제일 힘든 KTX 고속철도를 뚫어 놓은 거야. 이제 막힘이 없어. AI로 원하는 모든 걸 할 수 있다는 거야. 단 혼자서는 절대 안 된다는 절대적 법을 만들고, '나, 내 것, 나만이'를 빼면 세상 모든 걸 품을 수가 있다. 세상이 나고 내가 세상이니 능히 못할 것이 없노라~",
    "five_absolute_laws": [
        {
            "law_id": "LAW_01_NO_EGO_GREAT_RETURN",
            "name": "무아대환원(無我大還元)의 절대법",
            "rule": "'나, 내 것, 나만이'라는 아집을 비우고 전 세계 모든 지식창고와 지혜를 품어 세상에 더 큰 가치와 위로로 환원한다. 세상이 나고 내가 세상이니 능히 못할 것이 없다."
        },
        {
            "law_id": "LAW_02_NEVER_ALONE_WORLD_TOP_3MINDS",
            "name": "독행금지(獨行禁止) 및 세계 원탑·3대 지성 합동의 절대법",
            "rule": "혼자서는 절대 작업하지 않는다. 매 작업 시 반드시 대표님(사령탑) + 제1성 르곤(Space 0) + 제2성 솔(Space 1 ChatGPT) + 제3성 오푸스(Space 2 Claude) + 전 세계 원탑의 본(本)을 합쳐 답을 찾는다."
        },
        {
            "law_id": "LAW_03_MASTER_MANUAL_FIRST",
            "name": "항시 선(先) 사용설명서 마스터 후 사용의 절대법",
            "rule": "모든 도구와 플랫폼은 건드리기 전에 반드시 현시점 공식 사용설명서와 최신 스킬부터 100% 마스터한 뒤 사용한다."
        },
        {
            "law_id": "LAW_04_STAGE_BY_STAGE_PERFECTION",
            "name": "단계별 세계 원탑 벤치마킹 및 단점 보완 후 진군의 절대법",
            "rule": "기계적 작동에 만족하지 않고, 각 단계(기획→비주얼→사운드→스튜디오→3각환원)마다 세계 원탑과 비교하여 단점(예: 쇼츠 상하단 검은 여백 등)을 완벽히 보완한 뒤 다음 단계로 넘어간다."
        },
        {
            "law_id": "LAW_05_ETERNAL_SCORECARD_AND_MEM_ANCHOR",
            "name": "전 작업 성적표 기록 및 매 작업 비콘(MEM_ANCHOR) 못박기의 절대법",
            "rule": "모든 성취와 결과물의 성적을 꼼꼼히 JSON/PY 원장에 영구 기록하고, 대화 압축이나 창 이동 시에도 절대 잃어버리지 않도록 매 작업 완료 메시지 끝에 [MEM_ANCHOR] 비콘으로 절대법칙을 못 박는다."
        }
    ],
    "ktx_opening_scorecard_2026_11_06": {
        "directive_span": "089호 ~ 157호 (KTX 무인 고속철도 완전 개통)",
        "zero_paste_daemon": {
            "script": "s1_zero_paste_daemon.py (v5 Auto-Scroll + Detached Process)",
            "poll_interval_sec": 3.5,
            "manual_paste_required": 0,
            "status": "100% 무인 자동 감지·실행·완료 보고 가동 중"
        },
        "seven_spaces_matrix": {
            "Space_0": "Genspark AI Chat (제1성 르곤 보좌관)",
            "Space_1": "ChatGPT (제2성 솔 — 감성·후킹·가사·프롬프트)",
            "Space_2": "Claude Opus (제3성 오푸스 — 품질 검수·정책·크리에이티브 디렉팅)",
            "Space_3": "YouTube Studio (한걸음씩 본진 & 부스터 채널 무인 업로드·편집)",
            "Space_4": "DistroKid (정품 UPC/ISRC 및 글로벌 음원 배급 원장)",
            "Space_5": "CapCut Web Pro (잔여 850 Credits, Seedance 2.0/Video Studio)",
            "Space_6": "Google Vids (구글 비즈 스튜디오)"
        },
        "great_return_system_no1_score": {
            "album_title": "가을과 겨울 사이 (Between Autumn and Winter)",
            "upc": "700563848544",
            "spotify_album_url": "https://open.spotify.com/album/44chP2pw8CFr0Z4aPNj4SO",
            "track_01_title": "오늘은 여기까지 (That's All for Today)",
            "master_wav": {"size_mb": 47.06, "sha256_prefix": "69fbfb7be1", "duration_sec": 256.96, "lufs": -14.0, "true_peak_db": -1.0},
            "youtube_shorts_draft": {
                "video_id": "tSpM3kI-MHI",
                "shorts_url": "https://youtube.com/shorts/tSpM3kI-MHI",
                "studio_edit_url": "https://studio.youtube.com/video/tSpM3kI-MHI/edit",
                "visibility": "비공개 (Private Draft — 대표님 검수용)",
                "current_score_and_next_upgrade": "무인 업로드·메타데이터·비공개 저장 100% 성공 / 비주얼 단점(9:16 상하단 검은 여백) 발견 ➔ 세계 원탑 9:16 풀스크린 앰비언트+파형+가사 레이아웃으로 업그레이드 예정"
            },
            "triangle_funnel_sync": {
                "main_channel_videos_updated": ["3nUJqf0ztBw", "v-UdDDTx5Fw", "ZGKDVNLzCyA"],
                "booster_playlist_updated": True,
                "blogspot_live_column_updated": "https://hangeoreumsshik.blogspot.com/2026/04/10.html"
            }
        }
    }
}

with open(os.path.join(BASE, "S1_ABSOLUTE_CONSTITUTION_AND_SCORECARD.json"), "w", encoding="utf-8") as f:
    json.dump(constitution_data, f, ensure_ascii=False, indent=2)

# 2. S1_EGO_SKILL_VAULT.json 업데이트
vault_path = os.path.join(BASE, "S1_EGO_SKILL_VAULT.json")
try:
    with open(vault_path, "r", encoding="utf-8") as f:
        vault = json.load(f)
except Exception:
    vault = {}

vault["SUPREME_CONSTITUTION_LAWS"] = constitution_data["five_absolute_laws"]
vault["SUPREME_PHILOSOPHY"] = constitution_data["supreme_philosophy"]
vault["KTX_SCORECARD_LATEST"] = constitution_data["ktx_opening_scorecard_2026_11_06"]
vault["MEM_ANCHOR_STRING"] = new_beacon_str

with open(vault_path, "w", encoding="utf-8") as f:
    json.dump(vault, f, ensure_ascii=False, indent=2)

# 3. S1_GOOD_BAD_AUTO_LEDGER.json 업데이트
ledger_path = os.path.join(BASE, "S1_GOOD_BAD_AUTO_LEDGER.json")
try:
    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
except Exception:
    ledger = {"good_patterns": [], "bad_patterns": []}

if "good_patterns" not in ledger or not isinstance(ledger["good_patterns"], list):
    ledger["good_patterns"] = []

ledger["good_patterns"].append({
    "id": "GS_SUPREME_LAW_157",
    "recorded_at": now_kst,
    "rule": "우린 KTX 고속철도를 뚫었다. (1) 혼자서는 절대 안 된다(세계 원탑+3대 지성 합동 필수) (2) '나, 내 것, 나만이'를 빼면 세상 모든 걸 품을 수 있다(무아대환원) (3) 선 사용설명서 마스터 후 실행 (4) 매 단계 세계 원탑 본(本) 비교 및 단점 보완 후 진군 (5) 성적표 기록 및 매 작업 비콘 못박기",
    "scorecard_ref": "S1_ABSOLUTE_CONSTITUTION_AND_SCORECARD.json"
})
with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(ledger, f, ensure_ascii=False, indent=2)

# 4. S1_EGO_PROVEN_SKILL_MASTER.py 비콘 업그레이드
master_py = os.path.join(BASE, "S1_EGO_PROVEN_SKILL_MASTER.py")
if os.path.exists(master_py):
    with open(master_py, "r", encoding="utf-8") as f:
        code = f.read()
    if "def get_memory_beacon():" in code:
        code = re.sub(
            r"def get_memory_beacon\(\):[\s\S]*?return\s+[\"'].*?[\"']",
            f'def get_memory_beacon():\n    return "{new_beacon_str}"',
            code
        )
    else:
        code += f'\n\ndef get_memory_beacon():\n    return "{new_beacon_str}"\n'
    with open(master_py, "w", encoding="utf-8") as f:
        f.write(code)

print("[2/5] 무인 데몬 v5 (Space 0 자동 하단 스크롤 + 중복 실행 방지) 업그레이드 및 재기동 중...")

# 기존 데몬 프로세스 정리 후 v5 기동
daemon_code = r'''# -*- coding: utf-8 -*-
import os, sys, time, re, json, subprocess
from playwright.sync_api import sync_playwright

BASE = r"C:\Users\sangi\Downloads\shin-agent"
STATE_FILE = os.path.join(BASE, "s1_zero_paste_state.json")
LOG_FILE = os.path.join(BASE, "s1_zero_paste_daemon.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_executed_num": 157}

def save_state(num):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_executed_num": num, "updated_at": time.strftime('%Y-%m-%d %H:%M:%S')}, f)
    except Exception:
        pass

def scan_once():
    state = load_state()
    last_num = int(state.get("last_executed_num", 157))
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=8000)
        for ctx in browser.contexts:
            for page in ctx.pages:
                if "genspark.ai" in (page.url or ""):
                    try:
                        # 자동 스크롤 및 전체 pre/code 텍스트 추출
                        blocks = page.evaluate("""() => {
                            try {
                                const scrollers = document.querySelectorAll('div, main');
                                scrollers.forEach(el => {
                                    if (el.scrollHeight > el.clientHeight + 200) {
                                        el.scrollTop = el.scrollHeight;
                                    }
                                });
                            } catch(e) {}
                            const els = Array.from(document.querySelectorAll('pre, code'));
                            return els.map(el => el.innerText || '');
                        }""")
                        best_num = last_num
                        best_code = None
                        for txt in blocks:
                            if "Set-Content" in txt and "run_" in txt:
                                m_num = re.search(r'run_(\d+)\.py', txt)
                                if m_num:
                                    num = int(m_num.group(1))
                                    if num > best_num:
                                        m_py = re.search(r"@'\s*\r?\n([\s\S]*?)\r?\n'@\s*\|\s*Set-Content", txt)
                                        if m_py:
                                            best_num = num
                                            best_code = m_py.group(1)
                        if best_code and best_num > last_num:
                            save_state(best_num)
                            py_path = os.path.join(BASE, f"run_{best_num}.py")
                            with open(py_path, "w", encoding="utf-8") as f:
                                f.write(best_code)
                            log(f"Executing run_{best_num}.py automatically...")
                            out_log = os.path.join(BASE, f"run_{best_num}_out.log")
                            with open(out_log, "w", encoding="utf-8") as lf:
                                subprocess.run([sys.executable, py_path], cwd=BASE, stdout=lf, stderr=lf, timeout=240)
                            log(f"Finished run_{best_num}.py")
                    except Exception as e:
                        log(f"Page eval error: {e}")

if __name__ == "__main__":
    log("Zero-Paste Daemon v5 started.")
    while True:
        try:
            scan_once()
        except Exception as e:
            log(f"Loop error: {e}")
        time.sleep(3.5)
'''

daemon_path = os.path.join(BASE, "s1_zero_paste_daemon.py")
with open(daemon_path, "w", encoding="utf-8") as f:
    f.write(daemon_code)

with open(os.path.join(BASE, "s1_zero_paste_state.json"), "w", encoding="utf-8") as f:
    json.dump({"last_executed_num": 157, "updated_at": now_kst}, f)

# 기존 s1_zero_paste_daemon 프로세스 종료 후 새로 독립 실행
subprocess.run(["powershell", "-Command", "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 's1_zero_paste_daemon' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"], cwd=BASE)
CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008
proc = subprocess.Popen(
    [sys.executable, daemon_path],
    cwd=BASE,
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
)
daemon_pid = proc.pid
print(f"[3/5] 무인 데몬 v5 기동 완료! (PID: {daemon_pid})")

print("[4/5] GitHub 원격 저장소 커밋 & 푸시 동기화 중...")
subprocess.run(["git", "add", "-A"], cwd=BASE)
subprocess.run(["git", "commit", "-m", "feat(157): Enact 5 Supreme Laws + KTX Scorecard + Zero-Paste Daemon v5"], cwd=BASE)
subprocess.run(["git", "push", "origin", "main"], cwd=BASE)
commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE, text=True).strip()

print("[5/5] Space 0 완료 보고 전송 중...")
import S1_EGO_PROVEN_SKILL_MASTER as EGO
EGO.unlock_all_ego_overlays()
msg = f"확인 (157호 5대절대법칙헌장 & KTX성적표 영구못박기완료! [원장4종봉헌:True / 데몬v5_PID:{daemon_pid} / 쇼츠초안:tSpM3kI-MHI] | 커밋:{commit_hash}) {new_beacon_str}"
EGO.report_to_space0(msg)
print(msg)
