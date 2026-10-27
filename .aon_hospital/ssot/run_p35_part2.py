# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [P0-5] test_scheduler_sizing.py Single-File Comprehensive Inspection")
print("================================================================================")
sizing_path = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
real_path = os.path.realpath(sizing_path)
print(f"os.path.realpath: {real_path}")

with open(real_path, 'rb') as f:
    raw_b = f.read()

sha = hashlib.sha256(raw_b).hexdigest()
raw_lines = raw_b.splitlines()
print(f"Byte Size: {len(raw_b)}")
print(f"SHA256: {sha}")
print(f"len(splitlines): {len(raw_lines)}")

# Def test regex count & list
def_matches = []
with open(real_path, 'r', encoding='utf-8', errors='replace') as f:
    text_lines = f.readlines()

for idx, l in enumerate(text_lines, 1):
    if re.match(r'^\s*def test_', l):
        def_matches.append((idx, l.strip()))

print(f"Regex match count (^\s*def test_): {len(def_matches)}")

# Collect only on test_scheduler_sizing.py
cmd_sizing_col = [os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/test_scheduler_sizing.py', '--collect-only', '-q']
res_sc = subprocess.run(cmd_sizing_col, cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
sizing_col_items = [l.strip() for l in res_sc.stdout.splitlines() if "::" in l]
print(f"pytest --collect-only items with '::': {len(sizing_col_items)}")
print("First 3 items:")
for l in sizing_col_items[:3]:
    print(" ", l)
print("Last 3 items:")
for l in sizing_col_items[-3:]:
    print(" ", l)

print("\n================================================================================")
print("2. [P0-6] Full Collect vs Full Run & 9 Skipped Items Names")
print("================================================================================")
# 1) Full collect
res_all_col = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '--collect-only', '-q'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
all_col_items = [l.strip() for l in res_all_col.stdout.splitlines() if "::" in l]
print(f"Full collect items count: {len(all_col_items)}")

# 2) Full run
res_all_run = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
run_lines = res_all_run.stdout.splitlines()

# Extract SKIPPED tests from run output
skipped_tests = [l for l in run_lines if "SKIPPED" in l]
print(f"\nTotal SKIPPED tests ({len(skipped_tests)}):")
for st in skipped_tests:
    print(" ", st.strip())

last_run_line = [l.strip() for l in run_lines if l.strip()][-1]
print("\nExact pytest -v last summary line:")
print(repr(last_run_line))

print("\n================================================================================")
print("3. [P1] conftest.py full source & kis_broker.py L130-160")
print("================================================================================")
cp_path = os.path.join(backend_dir, 'tests', 'conftest.py')
print("--- tests/conftest.py FULL ---")
with open(cp_path, 'r', encoding='utf-8', errors='replace') as f:
    print(f.read())

kb_path = os.path.join(backend_dir, 'app', 'services', 'kis_broker.py')
print("--- app/services/kis_broker.py L130-160 ---")
with open(kb_path, 'r', encoding='utf-8', errors='replace') as f:
    kb_lines = f.readlines()
for i in range(129, min(160, len(kb_lines))):
    print(f"{i+1:4d}: {kb_lines[i]}", end="")
