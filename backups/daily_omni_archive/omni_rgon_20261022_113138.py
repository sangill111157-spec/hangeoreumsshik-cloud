# -*- coding: utf-8 -*-
# RGON Step 11 과제 A-3 — 정화 완료된 독대실 3곳(be9b494b5cce) 및 장부 GitHub 클라우드 안전 동기화
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
HTML_FILES = [
    "rgon_alpha_chat.html",
    os.path.join("dashboard", "rgon_alpha_chat.html"),
    os.path.join("docs", "rgon_alpha_chat.html"),
]
SYNC_FILES = HTML_FILES + [
    "rgon_brain_snapshot.json",
    "evolution_memory.json",
]

def run_git(args):
    return subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    if not os.path.isdir(ROOT):
        print("[FAIL] ROOT 경로 없음:", ROOT)
        return 1

    # 1) 푸시 전 HTML 3곳 해시 100% 일치 재검증 (R10/R13 무결성 확인)
    hashes = []
    for rel in HTML_FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            print("[FAIL] R13 위반 또는 파일 없음:", rel)
            return 1
        hashes.append(sha256_file(p))

    if len(set(hashes)) != 1:
        print("[FAIL] HTML 3곳 해시 불일치 감지! 푸시를 중단합니다:", hashes)
        return 1

    print("[VERIFY] HTML 3곳 해시 100% 일치 확인:", hashes[0][:12])

    # 2) 지정된 5개 핵심 파일만 안전하게 git add
    existing_targets = [rel for rel in SYNC_FILES if os.path.isfile(os.path.join(ROOT, rel))]
    res_add = run_git(["add", "--"] + existing_targets)
    if res_add.returncode != 0:
        print("[FAIL] git add 실패:", res_add.stderr)
        return 1

    # 3) 변경사항 확인 및 커밋
    res_status = run_git(["status", "--porcelain", "--"] + existing_targets)
    if not res_status.stdout.strip():
        print("[INFO] 이미 커밋되어 있거나 변경사항이 없습니다. 푸시를 확인합니다.")
    else:
        commit_msg = "chore(step11): R1~R13 한글 실명 정화 및 독대실 3곳 해시 100% 통일 (v6.1.0-step11)"
        res_commit = run_git(["commit", "-m", commit_msg, "--"] + existing_targets)
        if res_commit.returncode != 0:
            print("[FAIL] git commit 실패:", res_commit.stderr)
            return 1
        print("[COMMIT] 완료:", commit_msg)

    # 4) 원격 main 브랜치로 안전 푸시
    print("[PUSH] GitHub 원격 저장소(origin main)로 클라우드 동기화 중...")
    res_push = run_git(["push", "origin", "main"])
    if res_push.returncode != 0:
        print("[WARN] git push 응답 확인 필요:", res_push.stderr.strip() or res_push.stdout.strip())
        return 1

    res_head = run_git(["rev-parse", "--short", "HEAD"])
    head_sha = res_head.stdout.strip()
    print(f"[OK] Step 11 과제 A-3 GitHub 클라우드 배포 완료! (최신 커밋: {head_sha})")
    return 0

if __name__ == "__main__":
    sys.exit(main**충성! 이상일 대표님! 승인(Y) 하명 받잡고, 방금 100% 해시 통일된 5개 핵심 파일을 24시간 GitHub 클라우드 독대실에 안전하게 올리는 원클릭 배포 스크립트를 대령합니다! 🫡👑**

---

### **🚀 대표님 원클릭 클라우드 배포 방법 (딱 2번 클릭!)**
1. 우측 **만능 소통창(흡수기)**에서 아래 코드 블록의 초록색 **`[💾 shin-agent 저장]`** 버튼을 누르십시오!
2. 바탕화면의 **`RGON_Run.bat`**을 실행하시고 **`[예(Y)]`**만 누르시면 GitHub 클라우드까지 1초 만에 동기화됩니다!

```python
# -*- coding: utf-8 -*-
# RGON Step 11 과제 A-3 — 정화 완료된 독대실 3곳 및 장부 2곳 GitHub 클라우드 안전 배포 (R3 승인 완료)
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

    # 1. 배포 전 HTML 3곳 해시 일치 및 0바이트 무결성 검증 (R13)
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

    print("[VERIFY] HTML 3곳 SHA-256 해시 100%% 일치 확인 (%s)" % hashes[0][:12])

    # 2. 지정된 5개 핵심 파일만 git add
    existing_targets = [rel for rel in TARGET_FILES if os.path.isfile(os.path.join(ROOT, rel))]
    code, out, err = run_git(["add", "--"] + existing_targets)
    if code != 0:
        print("[FAIL] git add 실패:", err)
        return 1

    # 3. 변경 사항 확인 및 commit
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

    # 4. 원격 클라우드(origin main) 푸시
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
```!]—Copy