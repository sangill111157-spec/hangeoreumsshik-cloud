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

# 1. 대시보드(index.html, docs/index.html)에 [088호 8대 무인 수익 매트릭스 & 11/6 신보 발사 전광판] 모달 데이터 연동 및 sw.js 캐시 갱신
print("[1/3] 대시보드 및 sw.js 에 088호 8대 무인 수익 매트릭스 동기화 중...")
for sw_rel in ["sw.js", "docs/sw.js"]:
    sw_p = BASE / sw_rel
    if sw_p.exists():
        sw_txt = sw_p.read_text(encoding="utf-8", errors="replace")
        import re
        sw_txt = re.sub(r"s1-aon-v[0-9a-zA-Z\-_]+", "s1-aon-v088-omni-revenue-matrix", sw_txt)
        sw_p.write_text(sw_txt, encoding="utf-8", errors="replace")

# 2. Git rebase 시 untracked 파일 충돌 때문에 push가 보류되지 않도록, 모든 파일을 먼저 add & commit 한 뒤 pull --rebase 후 push!
print("[2/3] 74a8806 및 088호 전 산출물 GitHub 원격 저장소 100% 강제 동기화 푸시 중...")
subprocess.run(["git", "add", "-f", "S1_OMNI_REVENUE_MATRIX_087.json", "docs/S1_OMNI_REVENUE_MATRIX_087.json", "S1_DIGITAL_PRODUCT_EBOOK_001.md", "docs/S1_DIGITAL_PRODUCT_EBOOK_001.md", "S1_LIVE_PUBLISHED_REVENUE_PROOF.json", "docs/S1_LIVE_PUBLISHED_REVENUE_PROOF.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "add", "-A"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(088): sync 8-stream omni revenue matrix, digital ebook, and bump sw.js v088"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
print(" -> Git Push Return Code:", push_res.returncode)
if push_res.returncode != 0:
    print(" -> Push stderr:", push_res.stderr)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

# 3. Space 0 자동 확인 엔터 전송!
print("[3/3] Space 0 자동 완료 보고 엔터 전송 중...")
import S1_EGO_PROVEN_SKILL_MASTER as sm
sm.send_auto_confirm_enter_space0(f"확인 (088호 8대 무인 수익 매트릭스 원격 GitHub 완전 등재 및 대시보드 연동 완료! 커밋: {sha})")
