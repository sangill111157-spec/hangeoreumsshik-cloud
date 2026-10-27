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
print("1. [B-2] 'available' key grep across backend")
print("==================================================")
out_avail, _ = run_cmd('git grep -n "\\"available\\"" app/services/')
print("--- git grep -n '\"available\"' app/services/ ---")
print(out_avail)

print("\n==================================================")
print("2. [B-2] institutional score production point in stock.py & master_signal.py")
print("==================================================")
out_inst, _ = run_cmd('git grep -n -E "inst_score|institutional" app/api/routes/stock.py app/services/master_signal.py')
print(out_inst)

print("\n==================================================")
print("3. [B-2] Normal vs Exception return statements in all modules")
print("==================================================")
# Check stock.py around lines 615-660 (the unpack & fallback area)
with open(os.path.join(backend_dir, r'app\api\routes\stock.py'), 'r', encoding='utf-8', errors='replace') as f:
    st_lines = f.readlines()
for i in range(614, 675):
    print(f"stock.py:{i+1:4d}: {st_lines[i].rstrip()}")

print("\n==================================================")
print("4. [D-3 PREP] ComponentScore signal generation lines in master_signal.py")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()
for i in range(538, 598):
    print(f"master_signal:{i+1:4d}: {ms_lines[i].rstrip()}")

