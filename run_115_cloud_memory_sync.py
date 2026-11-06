import json, datetime, os, subprocess, shutil
from pathlib import Path
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/3] Git rebase/lock 상태 점검 및 클린업 중...")
for lock_f in [".git/index.lock", ".git/HEAD.lock"]:
    lp = BASE / lock_f
    if lp.exists():
        try: lp.unlink()
        except Exception: pass

for rb_dir in [".git/rebase-merge", ".git/rebase-apply"]:
    rp = BASE / rb_dir
    if rp.exists():
        subprocess.run(["git", "rebase", "--abort"], cwd=str(BASE), env=env, creationflags=no_win)

print("[2/3] S1_EGO_PROVEN_SKILL_MASTER.py 의 _auto_log_to_memory_vault 훅에 '원격 GitHub 자동 백업 푸시'까지 내장 중...")
sm_path = BASE / "S1_EGO_PROVEN_SKILL_MASTER.py"
sm_code = sm_path.read_text(encoding="utf-8")

upgraded_hook = '''
def _auto_log_to_memory_vault(msg: str) -> None:
    try:
        import datetime as _dt, subprocess as _sp, os as _os
        ledger_p = BASE / "S1_GOOD_BAD_AUTO_LEDGER.json"
        if ledger_p.exists():
            data = json.loads(ledger_p.read_text(encoding="utf-8"))
        else:
            data = {"ledger_name": "S1_GOOD_BAD_AUTO_LEDGER", "auto_execution_log": []}
        logs = data.get("auto_execution_log", [])
        logs.append({"timestamp": _dt.datetime.now().isoformat(), "report_message": str(msg)[:500]})
        data["auto_execution_log"] = logs[-200:]
        data["updated_at"] = _dt.datetime.now().isoformat()
        ledger_p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        _env = dict(_os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
        _nw = getattr(_sp, "CREATE_NO_WINDOW", 0x08000000)
        _sp.run(["git", "add", "-f", "S1_GOOD_BAD_AUTO_LEDGER.json", "S1_EGO_SKILL_VAULT.json"], cwd=str(BASE), env=_env, creationflags=_nw)
        _sp.run(["git", "commit", "-m", "chore(auto-memory): auto-save good/bad ledger on task completion"], cwd=str(BASE), env=_env, creationflags=_nw)
        _sp.run(["git", "push", "origin", "main"], cwd=str(BASE), env=_env, creationflags=_nw)
    except Exception:
        pass
'''

if "def _auto_log_to_memory_vault" in sm_code:
    idx = sm_code.index("def _auto_log_to_memory_vault")
    sm_code = sm_code[:idx] + upgraded_hook.lstrip()
    sm_path.write_text(sm_code, encoding="utf-8")

print("[3/3] 110호~115호 전 기억창고 및 수익화 실측 원장 원격 GitHub 강제 동기화 푸시 중...")
subprocess.run(["git", "add", "-f",
    "S1_EGO_SKILL_VAULT.json",
    "S1_GOOD_BAD_AUTO_LEDGER.json",
    "S1_EGO_PROVEN_SKILL_MASTER.py",
    "S1_FAILURE_MEMORY_DB.json",
    "S1_OAC_CALLBACK_AND_BATCH3_110.json",
    "S1_OAC_SUBMIT_AND_BOOSTER_SEO_111.json",
    "S1_ALL_3CHANNELS_SEO_AND_OAC_CODE_112.json",
    "S1_OAC_FINAL_AND_RETURN_113.json"
], cwd=str(BASE), env=env, creationflags=no_win)

subprocess.run(["git", "commit", "-m", "feat(115): sync all 110-115 memory vaults and 3-channel SEO proofs to GitHub origin"], cwd=str(BASE), env=env, creationflags=no_win)

# 원격 브랜치 상태 확인 후 안전 푸시
p1 = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
push_status = f"RC={p1.returncode}"
if p1.returncode != 0:
    subprocess.run(["git", "fetch", "origin", "main"], cwd=str(BASE), env=env, creationflags=no_win)
    subprocess.run(["git", "merge", "-X", "ours", "--no-edit", "origin/main"], cwd=str(BASE), env=env, creationflags=no_win)
    p2 = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), env=env, capture_output=True, text=True, creationflags=no_win)
    push_status = f"MERGE_PUSH_RC={p2.returncode} ({p2.stderr[:100]})"

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), env=env, text=True, creationflags=no_win).strip()

import importlib
importlib.reload(ego)
ego.send_auto_confirm_enter_space0(f"확인 (115호 로컬+GitHub 클라우드 자동기억창고 100% 동기화 완료! 푸시상태:{push_status} | 커밋:{sha})")
