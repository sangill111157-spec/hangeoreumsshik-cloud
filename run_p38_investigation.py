# -*- coding: utf-8 -*-
import sys, os, subprocess, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [Task 1] kis_broker.py POST Methods & _assert_order_allowed Inspection")
print("================================================================================")
kb_path = os.path.join(backend_dir, 'app', 'services', 'kis_broker.py')
with open(kb_path, 'r', encoding='utf-8', errors='replace') as f:
    kb_lines = f.readlines()

print("--- All method definitions in kis_broker.py ---")
for idx, l in enumerate(kb_lines, 1):
    if re.match(r'^\s*async def |^\s*def ', l):
        print(f"Line {idx:4d}: {l.strip()}")

print("\n--- All .post( or post calls in kis_broker.py ---")
for idx, l in enumerate(kb_lines, 1):
    if ".post(" in l or "client.post" in l or "httpx.post" in l:
        print(f"Line {idx:4d}: {l.strip()}")

print("\n--- All _assert_order_allowed occurrences in kis_broker.py ---")
for idx, l in enumerate(kb_lines, 1):
    if "_assert_order_allowed" in l:
        print(f"Line {idx:4d}: {l.strip()}")

print("\n================================================================================")
print("2. [Task 2] DRY_RUN Trade Path Inspection in auto_trader.py & scheduler.py")
print("================================================================================")
at_path = os.path.join(backend_dir, 'app', 'services', 'auto_trader.py')
with open(at_path, 'r', encoding='utf-8', errors='replace') as f:
    at_lines = f.readlines()

print("--- auto_trader.py execute_trade DRY_RUN branching (L140-200) ---")
for idx, l in enumerate(at_lines, 1):
    if "def execute_trade(" in l:
        for j in range(idx-1, min(idx+60, len(at_lines))):
            print(f"{j+1:4d}: {at_lines[j]}", end="")
        break

print("\n================================================================================")
print("3. [Task 3] emergency_stop / kill_switch Grep")
print("================================================================================")
res_em = subprocess.run('git grep -n "emergency_stop\\|EMERGENCY_STOP\\|kill_switch" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Grep results for emergency_stop / EMERGENCY_STOP / kill_switch in app/:")
print(res_em.stdout if res_em.stdout else "(None found)")

print("\n================================================================================")
print("4. [Task 3] collect_p37.txt File-by-File Breakdown (172 Closure)")
print("================================================================================")
col_file = os.path.join(scratch_dir, 'collect_p37.txt')
with open(col_file, 'r', encoding='utf-8', errors='replace') as f:
    col_lines = f.readlines()

file_counts = {}
for l in col_lines:
    if "::" in l:
        fn = l.split("::")[0].strip()
        file_counts[fn] = file_counts.get(fn, 0) + 1

total_col = sum(file_counts.values())
print(f"Total files: {len(file_counts)}")
for fn, cnt in sorted(file_counts.items()):
    print(f"  {fn:45s}: {cnt:3d} items")
print(f"-------------------------------------------------------------")
print(f"  {'SUM TOTAL':45s}: {total_col:3d} items")
