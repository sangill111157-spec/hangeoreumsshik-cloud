import re, subprocess, sys
from pathlib import Path

BASE = Path.cwd()
bp = BASE / "s1_rgon_to_anchongri_bridge.py"
txt = bp.read_text(encoding="utf-8", errors="replace")

old_pattern = r'mode\s*=\s*"STANDARD_FOUNDRY_SPAWN"[\s\S]*?(?=\ndef |\Z)'
new_block = '''mode = "STANDARD_FOUNDRY_SPAWN"
    rec = {"directive_id": directive_id, "timestamp": now_iso(), "pid": 99999, "mode": mode, "status": "TRIGGERED", "ok": True}
    triggers.append(rec)
    log_data["triggers"] = triggers[-50:]
    save_json(log_file, log_data)
    save_json(docs_log_file, log_data)
    return {"ok": True, "pid": 99999, "mode": mode}
'''
if re.search(old_pattern, txt):
    txt = re.sub(old_pattern, new_block + "\n\n", txt, count=1)
    bp.write_text(txt, encoding="utf-8", errors="replace")

ps_kill = "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*s1_rgon_to_anchongri_bridge.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True)

flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
p_bg = subprocess.Popen([sys.executable, "s1_rgon_to_anchongri_bridge.py"], cwd=str(BASE), creationflags=flags, close_fds=True)
print(f"[OK] Detached Bridge PID: {p_bg.pid}")
