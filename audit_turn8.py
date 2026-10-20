# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [A-1 & B-1] BASE_WEIGHTS definition in master_signal.py")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()
for i, l in enumerate(ms_lines):
    if 'BASE_WEIGHTS = {' in l:
        print(f"--- master_signal.py: BASE_WEIGHTS at line {i+1} ---")
        for j in range(i, min(len(ms_lines), i + 15)):
            print(f"{j+1:4d}: {ms_lines[j].rstrip()}")
        break

print("\n==================================================")
print("2. [B-1] stock.py master_signal call site (lines 720-775)")
print("==================================================")
with open(os.path.join(backend_dir, r'app\api\routes\stock.py'), 'r', encoding='utf-8', errors='replace') as f:
    st_lines = f.readlines()
for i, l in enumerate(st_lines):
    if 'calculate_final_master_signal' in l:
        print(f"--- stock.py call site near line {i+1} ---")
        for j in range(max(0, i-25), min(len(st_lines), i+30)):
            print(f"stock.py:{j+1:4d}: {st_lines[j].rstrip()}")
        break

print("\n==================================================")
print("3. [B-1] Unlimited pattern 'available' grep in app/services/")
print("==================================================")
out_avail, _ = run_cmd('git grep -n "available" app/services/')
print(out_avail)

print("\n==================================================")
print("4. [B-5] data/scan_history/ dir and 2026-08-21_us.json check")
print("==================================================")
scan_dir = os.path.join(backend_dir, r'data\scan_history')
print(f"Directory exists: {os.path.exists(scan_dir)}")
if os.path.exists(scan_dir):
    files = os.listdir(scan_dir)
    print(f"Files in data/scan_history ({len(files)} items):", files)
    for fn in files:
        fp = os.path.join(scan_dir, fn)
        sz = os.path.getsize(fp)
        print(f"  - {fn}: {sz} bytes")
        if '2026-08-21' in fn:
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                print(f"    Content preview (200 chars): {content[:200]}")

print("\n==================================================")
print("5. [B-2] git show 9d55dec -- src/App.tsx")
print("==================================================")
out_show, _ = run_cmd('git show 9d55dec -- src/App.tsx', cwd=frontend_dir)
print(out_show)

out_grep_ui, _ = run_cmd('git grep -n -E "\\|\\| 50|\\?\\? 50|null점" src/', cwd=frontend_dir)
print("\nUI grep residual check:\n", out_grep_ui if out_grep_ui.strip() else "  (0건 - 잔여 없음)")

