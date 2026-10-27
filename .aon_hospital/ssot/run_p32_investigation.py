# -*- coding: utf-8 -*-
import sys, os, subprocess, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. grep _telegram_fail_count & _stop_loss_disabled_last_alert")
print("==================================================")
res_grep_vars = subprocess.run('git grep -n "_telegram_fail_count\\|_stop_loss_disabled_last_alert" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_grep_vars.stdout)

print("\n==================================================")
print("2. TradingScheduler __new__ & __init__ full source")
print("==================================================")
sched_path = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')
with open(sched_path, 'r', encoding='utf-8') as f:
    sched_lines = f.readlines()

for i in range(80, min(195, len(sched_lines))):
    print(f"{i+1:4d}: {sched_lines[i]}", end="")

print("\n==================================================")
print("3. test_scheduler_sizing.py test def count & collect-only")
print("==================================================")
sizing_path = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
with open(sizing_path, 'r', encoding='utf-8') as f:
    sizing_lines = f.readlines()

def_tests = [l for l in sizing_lines if re.match(r'^\s*def test_', l)]
print(f"Number of 'def test_' in test_scheduler_sizing.py: {len(def_tests)}")

res_coll_sizing = subprocess.run('pytest tests/test_scheduler_sizing.py --collect-only -q', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("pytest tests/test_scheduler_sizing.py --collect-only -q output:")
print(res_coll_sizing.stdout)

print("\n==================================================")
print("4. collect_now.txt verification")
print("==================================================")
collect_file = os.path.join(backend_dir, 'scratch', 'collect_now.txt')
if os.path.exists(collect_file):
    with open(collect_file, 'r', encoding='utf-8') as f:
        c_lines = f.readlines()
    print(f"Total lines in collect_now.txt: {len(c_lines)}")
    print("Last 3 lines:")
    for l in c_lines[-3:]:
        print(" ", repr(l))
    
    col_items = [l for l in c_lines if "::" in l]
    print(f"Lines containing '::' in collect_now.txt: {len(col_items)}")
    
    # File-by-file breakdown
    file_counts = {}
    for l in col_items:
        fname = l.split("::")[0].strip()
        file_counts[fname] = file_counts.get(fname, 0) + 1
    print("\nFile-by-file test count breakdown:")
    for fn, cnt in sorted(file_counts.items()):
        print(f"  {fn:45s}: {cnt:3d} items")
