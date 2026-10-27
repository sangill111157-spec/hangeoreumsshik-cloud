# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, json, time
from pathlib import Path

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [P0-1] SENTINEL INJECTION & PYTEST RUN (mtime, SHA256, Content)")
print("================================================================================")
sl_path = os.path.join(backend_dir, 'data', 'stop_loss_state.json')

sentinel_data = {
    "stop_loss_fired": {"__SENTINEL__": "2026-08-30T00:00:00"},
    "price_fail_count": {},
    "gate_blocked_alert_fired": {},
    "reject_count": {},
    "next_retry": {},
    "locked_tickers": {},
    "last_re_alert": {},
    "updated_at": "2026-08-30T00:00:00Z"
}

with open(sl_path, 'w', encoding='utf-8') as f:
    json.dump(sentinel_data, f, indent=2)

stat_before = os.stat(sl_path)
mtime_before = stat_before.st_mtime
with open(sl_path, 'rb') as f:
    bytes_before = f.read()
sha_before = hashlib.sha256(bytes_before).hexdigest()

print(f"BEFORE pytest run:")
print(f"  mtime  : {mtime_before} ({time.ctime(mtime_before)})")
print(f"  Size   : {len(bytes_before)} bytes")
print(f"  SHA256 : {sha_before}")
print("  Content:")
print(bytes_before.decode('utf-8'))

# Run full pytest
print("\n--- Executing pytest tests/ -v ---")
res_py = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"Pytest returncode: {res_py.returncode}")

stat_after = os.stat(sl_path)
mtime_after = stat_after.st_mtime
with open(sl_path, 'rb') as f:
    bytes_after = f.read()
sha_after = hashlib.sha256(bytes_after).hexdigest()

print(f"\nAFTER pytest run:")
print(f"  mtime  : {mtime_after} ({time.ctime(mtime_after)})")
print(f"  Size   : {len(bytes_after)} bytes")
print(f"  SHA256 : {sha_after}")
print("  Content:")
print(bytes_after.decode('utf-8'))

mtime_match = (mtime_before == mtime_after)
sha_match = (sha_before == sha_after)
sentinel_preserved = ("__SENTINEL__" in bytes_after.decode('utf-8'))

print(f"\n[ISOLATION VERIFICATION RESULTS]")
print(f"  mtime unchanged        : {mtime_match}")
print(f"  SHA256 unchanged       : {sha_match}")
print(f"  SENTINEL preserved     : {sentinel_preserved}")

print("\n================================================================================")
print("2. [P0-1] updated_at grep & test_stop_loss_corrupt_state_file_fails_closed source")
print("================================================================================")
print("--- git grep -n 'updated_at' app/ ---")
res_up = subprocess.run('git grep -n "updated_at" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_up.stdout)

print("--- test_stop_loss_corrupt_state_file_fails_closed source in test_scheduler_sizing.py ---")
sizing_file = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
with open(sizing_file, 'r', encoding='utf-8', errors='replace') as f:
    s_lines = f.readlines()

for i, l in enumerate(s_lines, 1):
    if "def test_stop_loss_corrupt_state_file_fails_closed" in l:
        for j in range(i-1, min(i+35, len(s_lines))):
            print(f"{j+1:4d}: {s_lines[j]}", end="")
        break
