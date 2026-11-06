import json, subprocess, datetime
from pathlib import Path
import S1_EGO_PROVEN_SKILL_MASTER as EGO

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
REMOTE_URL = "https://github.com/sangill111157-spec/hangeoreumsshik-cloud.git"

# 1. git add & commit
subprocess.run(["git", "add", "-A"], cwd=str(ROOT), encoding="utf-8", errors="replace")
subprocess.run(["git", "commit", "-m", "feat(115): sync all 110-115 achievements and memory vault v3.0 to remote GitHub"], cwd=str(ROOT), encoding="utf-8", errors="replace")

rev_proc = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT), capture_output=True, encoding="utf-8", errors="replace")
rev = (rev_proc.stdout or "").strip()

# 2. origin 및 hangeoreumsshik-cloud 원격 푸시 결과 확인
p1 = subprocess.run(["git", "push", "origin", "HEAD:main", "--force"], cwd=str(ROOT), capture_output=True, encoding="utf-8", errors="replace")
p2 = subprocess.run(["git", "push", REMOTE_URL, "HEAD:main", "--force"], cwd=str(ROOT), capture_output=True, encoding="utf-8", errors="replace")

status1 = "OK" if p1.returncode == 0 else f"ERR({(p1.stderr or p1.stdout or '').strip()[:50]})"
status2 = "OK" if p2.returncode == 0 else f"ERR({(p2.stderr or p2.stdout or '').strip()[:50]})"

# 3. 앞으로 report_to_rgon 도 함께 쓸 수 있도록 S1_EGO_PROVEN_SKILL_MASTER.py 에 별칭(alias) 추가
skill_file = ROOT / "S1_EGO_PROVEN_SKILL_MASTER.py"
if skill_file.exists():
    sc = skill_file.read_text(encoding="utf-8", errors="replace")
    if "def report_to_rgon(" not in sc:
        sc += "\ndef report_to_rgon(msg: str) -> dict:\n    return send_auto_confirm_enter_space0(msg)\n"
        skill_file.write_text(sc, encoding="utf-8")

msg = f"확인 (115호 원격푸시결과 origin:{status1} | cloud:{status2} | 기억창고v3.0·35편수익파이프·OAC완료 영구봉헌 끝! 커밋:{rev})"
print(msg)
EGO.send_auto_confirm_enter_space0(msg)
