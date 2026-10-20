# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, json

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [P0-3] INVESTIGATE data/stop_loss_state.json BEFORE & AFTER PYTEST")
print("================================================================================")
sl_path = os.path.join(backend_dir, 'data', 'stop_loss_state.json')

# Check current content & hash before pytest
if os.path.exists(sl_path):
    with open(sl_path, 'rb') as f:
        before_bytes = f.read()
    before_sha = hashlib.sha256(before_bytes).hexdigest()
    print(f"BEFORE pytest - File exists: True, Size: {len(before_bytes)} bytes, SHA256: {before_sha}")
    print("BEFORE Content:")
    print(before_bytes.decode('utf-8', errors='replace'))
else:
    print("BEFORE pytest - File does NOT exist.")

print("\n--- git grep -n 'STOP_LOSS_STATE_FILE' tests/ app/ ---")
res_grep_sl = subprocess.run('git grep -n "STOP_LOSS_STATE_FILE" tests/ app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_grep_sl.stdout)

# Run pytest on tests/
print("\n--- Running pytest tests/ -v ---")
res_py = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"Pytest return code: {res_py.returncode}")

# Check content & hash after pytest
if os.path.exists(sl_path):
    with open(sl_path, 'rb') as f:
        after_bytes = f.read()
    after_sha = hashlib.sha256(after_bytes).hexdigest()
    print(f"\nAFTER pytest - File exists: True, Size: {len(after_bytes)} bytes, SHA256: {after_sha}")
    print("AFTER Content:")
    print(after_bytes.decode('utf-8', errors='replace'))
    if before_sha != after_sha:
        print(f"🚨 CRITICAL: File SHA256 CHANGED during pytest execution! (Diff: {len(before_bytes)} -> {len(after_bytes)} bytes)")
    else:
        print("✅ File SHA256 unchanged during pytest execution.")

print("\n--- Running python processes check ---")
res_ps = subprocess.run('powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Path, StartTime"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_ps.stdout)
