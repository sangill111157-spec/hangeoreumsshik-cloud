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
HTML_REL = [
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
]
TARGET_FILES = HTML_REL + [
    "rgon_brain_snapshot.json",
    "evolution_memory.json",
]

def run_git(args):
    res = subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    if not os.path.isdir(ROOT):
        print("[FAIL] ROOT 경로 없음:", ROOT)
        return 1

    hashes = []
    for rel in HTML_REL:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            print("[FAIL] R13 위반 또는 파일 누락:", rel)
            return 1
        hashes.append(sha256_file(p))

    if len(set(hashes)) != 1:
        print("[FAIL] HTML 3곳 해시 불일치 감지! 배포 중단:", hashes)
        return 1

    print("[VERIFY] HTML 3곳 SHA-256 해시 100% 일치 확인:", hashes[0][:12])

    existing_targets = [rel for rel in TARGET_FILES if os.path.isfile(os.path.join(ROOT, rel))]
    code, out, err = run_git(["add", "--"] + existing_targets)
    if code != 0:
        print("[FAIL] git add 실패:", err)
        return 1

    code, status_out, _ = run_git(["status", "--porcelain", "--"] + existing_targets)
    if not status_out:
        print("[INFO] 이미 최신 상태입니다 (추가 커밋할 변경 없음).")
    else:
        msg = "feat(step11): sync R1-R13 realnames, purify agency cards & unify 3 HTML hashes"
        code, out, err = run_git(["commit", "-m", msg, "--"] + existing_targets)
        if code != 0:
            print("[FAIL] git commit 실패:", err or out)
            return 1
        print("[COMMIT] 커밋 완료:", out.splitlines()[0] if out else msg)

    print("[PUSH] GitHub 원격 저장소(origin main)로 푸시 중...")
    code, out, err = run_git(["push", "origin", "main"])
    if code != 0:
        print("[FAIL] git push 실패:", err or out)
        return 1

    code, rev_out, _ = run_git(["rev-parse", "--short", "HEAD"])
    print("[SYNC] 최신 커밋 해시:", rev_out)
    print("[OK] Step 11 과제 A-3 GitHub 클라우드 배포 완료 (로컬·클라우드 100% 동기화)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
Copy