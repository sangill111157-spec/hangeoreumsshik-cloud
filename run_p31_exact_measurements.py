# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. Collect and Full Pytest Execution to scratch/")
print("==================================================")
# 1) collect-only to file
collect_file = os.path.join(scratch_dir, 'collect_now.txt')
cmd_collect = f'pytest tests/ --collect-only -q'
res_coll = subprocess.run(cmd_collect, cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
with open(collect_file, 'w', encoding='utf-8') as f:
    f.write(res_coll.stdout)
    if res_coll.stderr:
        f.write("\n--- STDERR ---\n" + res_coll.stderr)
print(f"Saved {collect_file}")

# Count lines in collect_now.txt
with open(collect_file, 'r', encoding='utf-8') as f:
    coll_lines = [l.strip() for l in f if l.strip() and not l.startswith('no tests ran') and not l.startswith('---')]
print(f"Total collected test items count: {len(coll_lines)}")

# 2) full pytest execution to file
pytest_file = os.path.join(scratch_dir, 'pytest_full.txt')
cmd_pytest = f'pytest tests/ -v'
res_pyt = subprocess.run(cmd_pytest, cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
with open(pytest_file, 'w', encoding='utf-8') as f:
    f.write(res_pyt.stdout)
    if res_pyt.stderr:
        f.write("\n--- STDERR ---\n" + res_pyt.stderr)
print(f"Saved {pytest_file}")

# Print last 15 lines of pytest output
print("\n--- Last 15 lines of pytest_full.txt ---")
for l in res_pyt.stdout.splitlines()[-15:]:
    print(l)

print("\n==================================================")
print("2. git status -s -uall")
print("==================================================")
res_st = subprocess.run('git status -s -uall', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_st.stdout)

print("\n==================================================")
print("3. order_gate.py FULL SOURCE")
print("==================================================")
og_path = os.path.join(backend_dir, 'app', 'core', 'order_gate.py')
with open(og_path, 'r', encoding='utf-8') as f:
    print(f.read())

print("\n==================================================")
print("4. git show --stat for last 7 commits")
print("==================================================")
res_stat = subprocess.run('git log -n 7 --stat', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_stat.stdout)

print("\n==================================================")
print("5. git show 9a3518e FULL DIFF")
print("==================================================")
res_show_9a = subprocess.run('git show 9a3518e', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_show_9a.stdout)
