import json, re, datetime, os, subprocess
from pathlib import Path
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] GitHub GH013(Secret Scanning) 차단을 유발한 110~115호 임시 OAuth 커밋 히스토리 소프트 리셋 중...")
subprocess.run(["git", "fetch", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "reset", "--mixed", "origin/main"], cwd=str(BASE), env=env, creationflags=no_win)

# 기억창고 파일 4종에서 혹시 모를 OAuth code/token 패턴 마스킹
MEMORY_FILES = [
    "S1_EGO_SKILL_VAULT.json",
    "S1_GOOD_BAD_AUTO_LEDGER.json",
    "S1_FAILURE_MEMORY_DB.json",
    "S1_EGO_PROVEN_SKILL_MASTER.py"
]

for mf in MEMORY_FILES:
    fp = BASE / mf
    if fp.exists():
        txt = fp.read_text(encoding="utf-8")
        txt = re.sub(r"4/0A[a-zA-Z0-9_\-]+", "REDACTED_OAUTH_CODE", txt)
        txt = re.sub(r"ya29\.[a-zA-Z0-9_\-]+", "REDACTED_ACCESS_TOKEN", txt)
        txt = re.sub(r"1//[a-zA-Z0-9_\-]+", "REDACTED_REFRESH_TOKEN", txt)
        fp.write_text(txt, encoding="utf-8")

print("[2/3] 순수 기억창고 4종(잘한점·못한점 자동원장 v3.0 + 자동저장 훅) 원격 GitHub 클린 푸시 중...")
subprocess.run(["git", "add", "-f"] + MEMORY_FILES, cwd=str(BASE), env=env, creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(116): permanently seal S1 Memory Vault v3.0 and auto-save hook (GH013 clean)"], cwd=str(BASE), env=env, creationflags=no_win)

res_origin = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
res_cloud = subprocess.run(["git", "push", "cloud", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)

o_stat = "OK" if res_origin.returncode == 0 else f"ERR({res_origin.stderr.strip()[:80]})"
c_stat = "OK" if res_cloud.returncode == 0 else f"ERR({res_cloud.stderr.strip()[:80]})"
sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

print("[3/3] Space 0 (르곤 창) 자동 완료 보고 엔터 전송 중...")
ego.send_auto_confirm_enter_space0(f"확인 (116호 GH013 클린업 완료! 원격푸시 origin:{o_stat} / cloud:{c_stat} | 기억창고 v3.0 영구등재 완료! 커밋:{sha})")
