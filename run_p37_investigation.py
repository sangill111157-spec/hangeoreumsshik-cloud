# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [Task 1] run_p36_part2_diff.py FULL SOURCE")
print("================================================================================")
diff_script_path = r'c:\Users\sangi\Downloads\shin-agent\run_p36_part2_diff.py'
with open(diff_script_path, 'r', encoding='utf-8', errors='replace') as f:
    print(f.read())

print("\n================================================================================")
print("2. [Task 1] pytest tests/ --collect-only -q to scratch/collect_p37.txt & line count")
print("================================================================================")
collect_file = os.path.join(scratch_dir, 'collect_p37.txt')
cmd_col = [os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '--collect-only', '-q']
res_col = subprocess.run(cmd_col, cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')

with open(collect_file, 'w', encoding='utf-8') as f:
    f.write(res_col.stdout)

with open(collect_file, 'r', encoding='utf-8', errors='replace') as f:
    c_lines = f.readlines()

colon_lines = [l for l in c_lines if "::" in l]
print(f"Total lines in collect_p37.txt: {len(c_lines)}")
print(f"Lines containing '::' in collect_p37.txt: {len(colon_lines)}")
print("Last 3 lines of collect_p37.txt:")
for l in c_lines[-3:]:
    print(" ", repr(l))

print("\n================================================================================")
print("3. [Task 2] git cat-file, hash-object, rev-parse on test_scheduler_sizing.py")
print("================================================================================")
res_cats = subprocess.run('git cat-file -s HEAD:tests/test_scheduler_sizing.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"git cat-file -s HEAD:tests/test_scheduler_sizing.py: {res_cats.stdout.strip()}")

res_hash = subprocess.run('git hash-object tests/test_scheduler_sizing.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"git hash-object tests/test_scheduler_sizing.py     : {res_hash.stdout.strip()}")

res_rev = subprocess.run('git rev-parse HEAD:tests/test_scheduler_sizing.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"git rev-parse HEAD:tests/test_scheduler_sizing.py  : {res_rev.stdout.strip()}")

sizing_path = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
with open(sizing_path, 'rb') as f:
    s_bytes = f.read()

sha256_val = hashlib.sha256(s_bytes).hexdigest()
split_lines = s_bytes.splitlines()

def_count = 0
for l in s_bytes.decode('utf-8', errors='replace').splitlines():
    if re.match(r'^\s*def test_', l):
        def_count += 1

print(f"Disk file byte size    : {len(s_bytes)}")
print(f"Disk file splitlines   : {len(split_lines)}")
print(f"Disk file SHA256       : {sha256_val}")
print(f"Disk file def test_ cnt: {def_count}")

print("\n================================================================================")
print("4. [Task 3] kis_broker.py L134-175 & scheduler.py L160-185 Source")
print("================================================================================")
kb_path = os.path.join(backend_dir, 'app', 'services', 'kis_broker.py')
with open(kb_path, 'r', encoding='utf-8', errors='replace') as f:
    kb_all = f.readlines()
print("--- app/services/kis_broker.py L134-175 ---")
for i in range(133, min(175, len(kb_all))):
    print(f"{i+1:4d}: {kb_all[i]}", end="")

sc_path = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')
with open(sc_path, 'r', encoding='utf-8', errors='replace') as f:
    sc_all = f.readlines()
print("\n--- app/services/scheduler.py L160-185 ---")
for i in range(159, min(185, len(sc_all))):
    print(f"{i+1:4d}: {sc_all[i]}", end="")
