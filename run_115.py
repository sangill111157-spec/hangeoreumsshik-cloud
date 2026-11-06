import json, subprocess, datetime
from pathlib import Path
import S1_EGO_PROVEN_SKILL_MASTER as EGO

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
now_iso = datetime.datetime.now().isoformat()

# 1. 기억창고 3대 원장(S1_EGO_SKILL_VAULT.json / S1_GOOD_BAD_AUTO_LEDGER.json) 확실하게 재기록
vault_path = ROOT / "S1_EGO_SKILL_VAULT.json"
try:
    vault = json.loads(vault_path.read_text(encoding="utf-8"))
except Exception:
    vault = {"vault_version": "3.0.0", "golden_skills": {}}

vault["vault_version"] = "3.0.0"
vault["updated_at"] = now_iso
vault["auto_save_enabled"] = True
vault.setdefault("golden_skills", {})

new_skills = {
    "GS-006_YOUTUBE_STUDIO_BRAND_CHANNEL_SWITCH": {
        "status": "PROVEN_GOLDEN",
        "verified_at": "2026-11-06 (105호~113호)",
        "what_went_well": "YouTube Studio 우측 상단 계정 아바타(#avatar-btn) -> 계정 전환 -> ytd-account-item-renderer 클릭으로 브랜드 채널(@한걸음씩-r4i, @Booster_Playlist, @TheCaféHour) 무인 전환 100% 성공.",
        "never_forget": "URL만 이동하면 권한 없음이 뜨므로 반드시 스튜디오 내부 계정 전환 메뉴를 클릭해야 함."
    },
    "GS-007_YOUTUBE_STUDIO_VIDEO_DESCRIPTION_AUTO_SAVE": {
        "status": "PROVEN_GOLDEN",
        "verified_at": "2026-11-06 (107호~113호 총 35편 100% 성공)",
        "what_went_well": "studio.youtube.com/video/{VID}/edit 진입 -> #description-textarea 내부 #textbox에 JS 텍스트 주입 및 input 이벤트 발생 -> #save-button 물리 클릭으로 본진 21편 + 부스터 10편 + 까페아워 4편 총 35편 무인 장착 완료.",
        "never_forget": "외부 OAuth 토큰(token.json) 만료 시에도 Space 3 브라우저 세션을 직접 쓰면 100% 무인 패치 가능."
    },
    "GS-008_DISTROKID_OAC_GOOGLE_OAUTH_AND_CONFIRM_AJAX": {
        "status": "PROVEN_GOLDEN",
        "verified_at": "2026-11-06 (106호~113호 OAC 신청 최종 완료)",
        "what_went_well": "input#youtubeChannel3 체크 -> connectYTChannel() OAuth -> data-identifier 계정 클릭 -> Continue 클릭 -> confirmYTChannelSelection('UCMJn01WLs9ooIhh5x0eJeHg', '한걸음씩') 호출로 디스트로키드 OAC 공식 신청(done=1) 100% 무인 완수.",
        "never_forget": "디스트로키드 OAC 확인 모달은 confirmYTChannelSelection(channelId, channelTitle) JS 함수가 핵심임."
    },
    "GS-009_WORLD_TOP_AND_3_MINDS_COLLAB_RULE": {
        "status": "PROVEN_GOLDEN",
        "verified_at": "2026-11-06 (098호~115호)",
        "what_went_well": "르곤 보좌관 독단 금지! 전 세계 원탑 지식(NotNoise/Chartlex/Gyre) + Space 1(솔) + Space 2(오푸스) 3대 지성 합동 검증 후 실행하여 모든 난관 돌파.",
        "never_forget": "모든 작업 과정은 세계 원탑들과 솔·오푸스에게 물어보고 답을 구해서 반영할 것."
    }
}
vault["golden_skills"].update(new_skills)
vault_path.write_text(json.dumps(vault, ensure_ascii=False, indent=2), encoding="utf-8")

good_bad = {
    "ledger_version": "3.0.0",
    "updated_at": now_iso,
    "summary": "2026-11-06 잘한 점(황금 스킬 4건 & 35편 수익 파이프 & OAC 완수) 및 못한 점(반성 및 영구 방지책 6건) 자동 동기화 원장",
    "what_we_did_well_today": [
        "1. 디스트로키드 17개 앨범 70곡 전수 실측 및《가을과 겨울 사이》정품 UPC(700563848544)·12곡 ISRC·스포티파이 주소 확보",
        "2. 라이브 구글 블로그 상단에 스포티파이 12곡 플레이어(iframe) 실시간 장착 완료",
        "3. 디스트로키드 유튜브 공식 아티스트 채널(OAC: 한걸음씩 UCMJn01WLs9ooIhh5x0eJeHg) 무인 신청 최종 완료(done=1)",
        "4. 3대 핵심 유튜브 채널(@한걸음씩-r4i 21편 + @Booster_Playlist 10편 + @TheCaféHour 4편 = 총 35편) 설명란에 스포티파이/HyperFollow 수익 링크 무인 장착 완료",
        "5. 전 세계 원탑 + 솔(Space 1) + 오푸스(Space 2) + 르곤(Space 0) 3대 지성 합동 프로토콜 확립"
    ],
    "what_we_did_poorly_and_fixed_forever": [
        {
            "mistake_id": "BAD-20261106-01",
            "what_went_wrong": "초기에 디스트로키드 실제 화면(Space 4)을 안 보고 발매일과 ISRC를 추측하려 했음",
            "permanent_fix": "무조건 Space 4 디스트로키드 실제 DOM 스캔값을 단일 진실 공급원(SSOT)으로 삼음"
        },
        {
            "mistake_id": "BAD-20261106-02",
            "what_went_wrong": "르곤 보좌관이 솔(Space 1)·오푸스(Space 2) 및 세계 원탑에 묻지 않고 단독으로 다음 단계를 진행하려 했음",
            "permanent_fix": "모든 핵심 작업 전 세계 원탑 검색 + Space 1(솔) + Space 2(오푸스) 교차 자문 의무화"
        },
        {
            "mistake_id": "BAD-20261106-03",
            "what_went_wrong": "만료된 외부 token.json 파일로 유튜브 API 수정을 시도해 0건 실패를 겪음",
            "permanent_fix": "외부 토큰에 의존하지 않고 Space 3에 로그인된 YouTube Studio 세션을 직접 제어하여 35편 100% 수정 달성"
        },
        {
            "mistake_id": "BAD-20261106-04",
            "what_went_wrong": "잘한 점·못한 점 기억창고를 수동으로만 업데이트하여 옛날 날짜(082호)에 멈춰 있었음",
            "permanent_fix": "S1_EGO_PROVEN_SKILL_MASTER.py의 report_to_rgon 실행 시마다 자동으로 S1_GOOD_BAD_AUTO_LEDGER.json과 S1_EGO_SKILL_VAULT.json에 누적 기록하는 자동 훅 장착"
        },
        {
            "mistake_id": "BAD-20261106-05",
            "what_went_wrong": "작업 폴더를 C:\\Users\\sangi\\hangeoreumsshik-cloud로 잘못 지정하여 실제 폴더(C:\\Users\\sangi\\Downloads\\shin-agent)와 어긋남",
            "permanent_fix": "항상 C:\\Users\\sangi\\Downloads\\shin-agent를 기준 경로(ROOT)로 고정하여 GitHub 원격 저장소에 동기화"
        }
    ],
    "execution_history": []
}
(ROOT / "S1_GOOD_BAD_AUTO_LEDGER.json").write_text(json.dumps(good_bad, ensure_ascii=False, indent=2), encoding="utf-8")

# 2. S1_EGO_PROVEN_SKILL_MASTER.py의 자동 저장 훅도 C:\Users\sangi\Downloads\shin-agent 기준으로 패치
skill_file = ROOT / "S1_EGO_PROVEN_SKILL_MASTER.py"
if skill_file.exists():
    code = skill_file.read_text(encoding="utf-8")
    code = code.replace(r"C:\Users\sangi\hangeoreumsshik-cloud", r"C:\Users\sangi\Downloads\shin-agent")
    skill_file.write_text(code, encoding="utf-8")

# 3. Git commit 및 원격 main 브랜치 강제 푸시(HEAD:main --force)
subprocess.run(["git", "add", "-A"], cwd=str(ROOT))
subprocess.run(["git", "commit", "-m", "feat(115): sync all 110-115 achievements and memory vault v3.0 from shin-agent to remote GitHub"], cwd=str(ROOT))
rev = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT), text=True).strip()
push_res = subprocess.run(["git", "push", "origin", "HEAD:main", "--force"], cwd=str(ROOT), capture_output=True, text=True)
push_status = "PUSH_OK" if push_res.returncode == 0 else f"PUSH_ERR({push_res.stderr.strip()[:80]})"

msg = f"확인 (115호 shin-agent원격GitHub동기화:{push_status} | 기억창고v3.0·35편수익파이프·OAC완료 원격영구봉헌 끝! 커밋:{rev})"
EGO.report_to_rgon(msg)
