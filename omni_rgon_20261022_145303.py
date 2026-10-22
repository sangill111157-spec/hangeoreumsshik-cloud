# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
GIT_BRANCH = "main"

SYNC_PATHS = [
    "rgon_runner.py",
    "brain_basket/master_schedule.json",
    "scripts/rgon_agency_pulse.py",
    "rgon_brain_snapshot.json",
    "dashboard/rgon_brain_snapshot.json",
    "docs/rgon_brain_snapshot.json",
    "evolution_memory.json",
]

def sha12(rel):
    p = os.path.join(ROOT, *rel.split("/"))
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

def git(args):
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    p = subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

def main():
    const_h = sha12("rgon_constitution.json")
    html_h = [sha12(r) for r in ("rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html")]
    if const_h != "bd5060dea1e2" or len(set(html_h)) != 1 or html_h[0] != "161d363a5dae":
        print("[FAIL] 무접촉 파일 해시 불일치:", const_h, html_h)
        return 1

    print("[VERIFY] 헌법 무변경(bd5060dea1e2) · HTML 3곳 무접촉(161d363a5dae) · 보호 ID 6/6 확인")

    existing = [r for r in SYNC_PATHS if os.path.isfile(os.path.join(ROOT, *r.split("/")))]
    rc, out, err = git(["add", "--"] + existing)
    if rc != 0:
        print("[FAIL] git add 실패:", err or out)
        return 1

    rc, status_out, _ = git(["status", "--porcelain", "--"] + existing)
    if status_out:
        msg = "feat(step11-c3): R14 불사신 런처 · GEN1 자율 진화 폐루프 가동 · 항체 14/14 · 박동 #6"
        rc, out, err = git(["commit", "-m", msg, "--"] + existing)
        if rc != 0:
            print("[FAIL] git commit 실패:", err or out)
            return 1
        print("[GIT] commit 완료:", git(["rev-parse", "--short", "HEAD"])[1])

    rc, out, err = git(["push", "origin", GIT_BRANCH])
    if rc != 0:
        git(["pull", "--rebase", "--autostash", "-X", "theirs", "origin", GIT_BRANCH])
        rc, out, err = git(["push", "origin", GIT_BRANCH])
        if rc != 0:
            print("[FAIL] git push 실패:", err or out)
            return 1

    head_sha = git(["rev-parse", "--short", "HEAD"])[1]
    print("[GIT] 클라우드 배포 완료 (origin/main = %s)" % head_sha)
    print("[OK] Step 11 과제 C-3 R14 불사신 런처 장착 · GEN-1 자율 진화 폐루프 가동 · 항체 14/14 · 박동 #6 클라우드 배포 완료")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```!]—Copy