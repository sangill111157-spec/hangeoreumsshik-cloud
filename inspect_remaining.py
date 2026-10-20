# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import urllib.request, json, time, subprocess

def run_cmd(cmd, cwd=r'C:\trading\package\nvda_trading_system\backend'):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. INSPECT DEF AROUND LINES 757, 765, 779, 780 in stock.py")
print("==================================================")
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8', errors='replace') as f:
    stock_lines = f.readlines()

for idx in [757, 765, 779, 780]:
    start = max(0, idx - 15)
    end = min(len(stock_lines), idx + 10)
    print(f"\n--- Around Line {idx} in stock.py ---")
    for i in range(start, end):
        print(f"{i+1:4d}: {stock_lines[i].rstrip()}")

print("\n==================================================")
print("2. _detect_unavailable_modules FULL SOURCE")
print("==================================================")
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()

in_detect = False
for i, l in enumerate(ms_lines):
    if 'def _detect_unavailable_modules' in l:
        in_detect = True
    if in_detect:
        print(f"{i+1:4d}: {l.rstrip()}")
        if l.startswith("    def ") and 'def _detect_unavailable_modules' not in l:
            break

print("\n==================================================")
print("3. KIS Broker rt_cd vs rt_code and result dict generation")
print("==================================================")
out, _ = run_cmd('git grep -n -E "rt_cd|rt_code" app/')
print(out)

print("\n==================================================")
print("4. Frontend api.ts full interface for StockSignal / MasterSignal")
print("==================================================")
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\services\api.ts', 'r', encoding='utf-8', errors='replace') as f:
    api_ts_lines = f.readlines()

for i, l in enumerate(api_ts_lines):
    if any(k in l for k in ['MasterSignal', 'StockSignal', 'SignalResponse', 'MasterSignalResult', 'Coverage', 'coverage', 'interface', 'type ']):
        print(f"{i+1:4d}: {l.rstrip()}")
