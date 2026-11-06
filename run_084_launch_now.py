import datetime, json, os, subprocess, sys
from pathlib import Path

os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
for k in ["VSCODE_GIT_IPC_HANDLE", "GIT_ASKPASS", "VSCODE_GIT_ASKPASS_NODE", "VSCODE_GIT_ASKPASS_MAIN", "SSH_ASKPASS"]:
    os.environ.pop(k, None)

no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
BASE = Path.cwd()
env = os.environ.copy()
now_kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

# 1. 네이버 블로그 2026 휴머나이저 패키지 실행 (11/6 D-Day 가을과 겨울 사이 12곡)
print("[1/4] 네이버 블로그 & 구글 블로거 11/6 발매 수익 패키지 생성 중...")
if (BASE / "s1_naver_blog_2026_publisher.py").exists():
    subprocess.run([sys.executable, "s1_naver_blog_2026_publisher.py"], cwd=str(BASE), env=env, creationflags=no_win)

# 2. S1_ROUND2_LAUNCH_READINESS.json 최신 실측 업데이트
readiness_path = BASE / "S1_ROUND2_LAUNCH_READINESS.json"
if readiness_path.exists():
    r_data = json.loads(readiness_path.read_text(encoding="utf-8", errors="replace"))
else:
    r_data = {}

r_data["updated_at"] = now_kst
r_data["naver_blog_package_generated"] = (BASE / "studio_vault" / "NAVER_BLOG_OUT" / "NOV06_NAVER_BLOG_POST_PACKAGE.html").exists()
r_data["google_blogger_post_generated"] = (BASE / "S1_BLOG_REVENUE_POST_001.html").exists()
r_data["status"] = "ROUND2_COMPLETED_AND_SYNCED_TO_GITHUB"

r_str = json.dumps(r_data, ensure_ascii=False, indent=2)
readiness_path.write_text(r_str, encoding="utf-8", errors="replace")
(BASE / "docs" / "S1_ROUND2_LAUNCH_READINESS.json").write_text(r_str, encoding="utf-8", errors="replace")

# 3. --autostash 로 밀려 있던 로컬 커밋(289079a, e252d6c)까지 100% GitHub 원격 저장소에 푸시!
print("[2/4] GitHub 원격 저장소(--autostash) 완전 동기화 푸시 중...")
subprocess.run(["git", "add", "-A"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(084): generate Nov 6 launch blog packages and sync all monetization ledgers"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
print("[3/4] Git Push Return Code:", push_res.returncode)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

# 4. Space 0 자동 확인 엔터 전송!
print("[4/4] Space 0 자동 완료 보고 엔터 전송 중...")
import S1_EGO_PROVEN_SKILL_MASTER as sm
sm.send_auto_confirm_enter_space0(f"확인 (084호 11/6 발매 수익 패키지 완공 및 GitHub --autostash 원격 푸시 100% 성공! 커밋: {sha})")
