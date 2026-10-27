# -*- coding: utf-8 -*-
import sys, os, subprocess, json

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [결함 49 & 50] master_signal.py confidence calculation lines 520-565")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()
for i, l in enumerate(ms_lines):
    if 'confidence =' in l or 'master_confidence' in l or '# 5. 신뢰도 계산' in l or 'base_confidence' in l:
        print(f"--- master_signal.py near line {i+1} ---")
        for j in range(max(0, i-5), min(len(ms_lines), i+35)):
            print(f"{j+1:4d}: {ms_lines[j].rstrip()}")
        break

print("\n==================================================")
print("2. [결함 25] Frontend UI master_score / masterSignal references (7 locations)")
print("==================================================")
app_tsx = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_tsx, 'r', encoding='utf-8') as f:
    app_lines = f.readlines()
for i, l in enumerate(app_lines):
    if 'master_score' in l or 'masterSignal' in l or 'data?.master_score' in l or 'master_confidence' in l:
        print(f"{i+1:4d}: {l.rstrip()[:120]}")

print("\n==================================================")
print("3. [B-3] stock.py lines 745-770 (inst_available and master call)")
print("==================================================")
with open(os.path.join(backend_dir, r'app\api\routes\stock.py'), 'r', encoding='utf-8') as f:
    st_lines = f.readlines()
for i, l in enumerate(st_lines):
    if 'inst_available' in l or 'institutional =' in l:
        print(f"--- stock.py near line {i+1} ---")
        for j in range(max(0, i-5), min(len(st_lines), i+25)):
            print(f"{j+1:4d}: {st_lines[j].rstrip()}")
        break

