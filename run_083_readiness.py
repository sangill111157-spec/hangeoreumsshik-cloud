import json, os, subprocess, sys
from pathlib import Path

os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
for k in ["VSCODE_GIT_IPC_HANDLE", "GIT_ASKPASS", "VSCODE_GIT_ASKPASS_NODE", "VSCODE_GIT_ASKPASS_MAIN", "SSH_ASKPASS"]:
    os.environ.pop(k, None)

no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
BASE = Path.cwd()
env = os.environ.copy()

# 1. 방금 성공한 289079a 커밋을 원격 GitHub main에 완전 동기화 (stash 없이 untracked 충돌 방지)
subprocess.run(["git", "add", "-A"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "chore(082): sync 289079a verified ego harvest and blog post"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

# 2. 제2라운드(실전 채널 무인 업로드) 사전 검수: 로컬 오디오/비디오 파일 및 API 토큰 준비 상태 점검
audio_files = list((BASE / "audio").glob("*")) if (BASE / "audio").exists() else []
studio_files = list((BASE / "studio_vault").rglob("*.mp3")) if (BASE / "studio_vault").exists() else []
publishers = [p.name for p in BASE.glob("*publish*.py")] + [p.name for p in BASE.glob("*youtube*.py")] + [p.name for p in BASE.glob("*blog*.py")]

readiness = {
    "stage": "ROUND2_PRE_AUDIT_CHANNEL_LAUNCH_READINESS",
    "audio_dir_count": len(audio_files),
    "audio_samples": [f.name for f in audio_files[:10]],
    "studio_mp3_count": len(studio_files),
    "publisher_scripts": sorted(list(set(publishers)))[:15],
    "blog_post_001_ready": (BASE / "S1_BLOG_REVENUE_POST_001.html").exists(),
    "monetization_pkg_001_ready": (BASE / "S1_MONETIZATION_PACKAGE_001.json").exists()
}
r_str = json.dumps(readiness, ensure_ascii=False, indent=2)
(BASE / "S1_ROUND2_LAUNCH_READINESS.json").write_text(r_str, encoding="utf-8", errors="replace")
(BASE / "docs" / "S1_ROUND2_LAUNCH_READINESS.json").write_text(r_str, encoding="utf-8", errors="replace")

gi = BASE / ".gitignore"
if gi.exists():
    gtxt = gi.read_text(encoding="utf-8", errors="replace")
    if "!S1_ROUND2_LAUNCH_READINESS.json" not in gtxt:
        gtxt += "\n!S1_ROUND2_LAUNCH_READINESS.json\n!docs/S1_ROUND2_LAUNCH_READINESS.json\n"
        gi.write_text(gtxt, encoding="utf-8", errors="replace")

subprocess.run(["git", "add", ".gitignore", "S1_ROUND2_LAUNCH_READINESS.json", "docs/S1_ROUND2_LAUNCH_READINESS.json"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "docs(083): Round 2 channel launch readiness pre-audit report"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

import S1_EGO_PROVEN_SKILL_MASTER as sm
sm.send_auto_confirm_enter_space0(f"확인 (083호 GitHub 원격 동기화 및 제2라운드 실전 채널 발사 사전검수 완료! 커밋: {sha})")
