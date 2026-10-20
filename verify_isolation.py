# -*- coding: utf-8 -*-
import sys, os, subprocess, shutil, hashlib

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sl_path = os.path.join(backend_dir, 'data', 'stop_loss_state.json')
with open(sl_path, 'rb') as f:
    b_before = f.read()
sha_before = hashlib.sha256(b_before).hexdigest()
print(f"BEFORE test run - Size: {len(b_before)}, SHA256: {sha_before}")

res_test = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')

with open(sl_path, 'rb') as f:
    b_after = f.read()
sha_after = hashlib.sha256(b_after).hexdigest()
print(f"AFTER test run - Size: {len(b_after)}, SHA256: {sha_after}")

if sha_before == sha_after:
    print("✅ PERFECT: data/stop_loss_state.json is 100% ISOLATED and UNCHANGED during pytest!")
else:
    print("🚨 ERROR: SHA256 still changed!")

lines = [l.strip() for l in res_test.stdout.splitlines() if l.strip()]
print("\npytest returncode:", res_test.returncode)
print("pytest exact last line:", repr(lines[-1]))
