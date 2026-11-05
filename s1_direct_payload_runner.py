import json
import subprocess
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
now_kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

# 1. S1_EGO_SKILL_VAULT.json 에 5번째 영구 스킬(검은 창 소멸 _StealthPopen + pythonw.exe) 정식 추가 등재
vault_path = BASE / "S1_EGO_SKILL_VAULT.json"
docs_vault_path = BASE / "docs" / "S1_EGO_SKILL_VAULT.json"

vault_data = {
    "version": "2.0.0-STEALTH-LOCKED",
    "locked_at": now_kst,
    "policy": "절대 수정·훼손 금지 (검은 창 0회 깜빡임 + 안실장 0회 호출 + 무복사 수거 + 자동 엔터)",
    "proven_skills": {
        "skill_1_auto_copy": "S1_EGO_PROVEN_SKILL_MASTER.scan_and_auto_copy_space0()",
        "skill_2_auto_confirm_enter": "S1_EGO_PROVEN_SKILL_MASTER.send_auto_confirm_enter_space0(msg)",
        "skill_3_side_room_harvest": "S1_EGO_PROVEN_SKILL_MASTER.ask_and_harvest_side_room(space_idx, prompt, wait_ms)",
        "skill_4_clear_locks": "S1_EGO_PROVEN_SKILL_MASTER.clear_all_spaces_lock()",
        "skill_5_stealth_zero_window": "_StealthPopen (CREATE_NO_WINDOW 0x08000000 global hook + pythonw.exe daemon)"
    }
}
vault_str = json.dumps(vault_data, ensure_ascii=False, indent=2)
vault_path.write_text(vault_str, encoding="utf-8", errors="replace")
docs_vault_path.parent.mkdir(parents=True, exist_ok=True)
docs_vault_path.write_text(vault_str, encoding="utf-8", errors="replace")

# 2. Git 커밋 & 푸시 (깜빡임 0회)
subprocess.run(["git", "add", "s1_rgon_to_anchongri_bridge.py", "s1_ego.py", "S1_EGO_PROVEN_SKILL_MASTER.py", "S1_EGO_SKILL_VAULT.json", "docs/S1_EGO_SKILL_VAULT.json"], cwd=str(BASE), creationflags=no_win)
subprocess.run(["git", "commit", "-m", "feat(078): lock _StealthPopen zero-window hook into S1_EGO_SKILL_VAULT"], cwd=str(BASE), creationflags=no_win)
subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=str(BASE), creationflags=no_win)
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), creationflags=no_win)

sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True, creationflags=no_win).strip()

# 3. Space 0 채팅창에 자동 확인 + 물리 엔터 전송!
try:
    import S1_EGO_PROVEN_SKILL_MASTER as sm
    sm.send_auto_confirm_enter_space0("확인 (078호 검은 창 소멸 + 무복사 자동수거 + 자동 엔터 100% 완공! 커밋: " + sha + ")")
except Exception as e:
    print("err:", e)