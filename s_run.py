#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""step1_git_sync_push.py (R10 항체: git pull --rebase 후 즉시 git push)"""

import subprocess
from pathlib import Path

ROOT = Path("C:/Users/sangi/Downloads/shin-agent")

def run(cmd):
    print("▶ 실행:", " ".join(cmd))
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip())
    return r.returncode

def main():
    print("=" * 64)
    print("🚀 [R10 클라우드 동기화] 최신 클라우드 변경분 병합 후 재푸시 시작")
    print("=" * 64)
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", "feat(mobile): Step 1 mobile quickbar UI upgrade"])
    rc = run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"])
    if rc != 0:
        run(["git", "rebase", "--abort"])
        run(["git", "pull", "--no-rebase", "-X", "ours", "origin", "main"])
    rc_push = run(["git", "push", "origin", "main"])
    if rc_push == 0:
        print("\n✅ [100% 대성공!] GitHub 클라우드 배포가 완벽히 끝났습니다!")
        print("📱 이제 스마트폰에서 독대실을 새로고침해 보십시오!")
    else:
        print("\n⚠️ 푸시 상태 코드:", rc_push)
    print("=" * 64)

if __name__ == "__main__":
    main()
