# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [B-1] Source of correlation -2.0 adjustment in master_signal.py")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

for i, l in enumerate(ms_lines):
    if 'correlation' in l or 'macro_score' in l or 'regime' in l or 'raw_score' in l:
        if any(w in l for w in ['adjust', 'adjustment', '- 2', 'macro_adjustment', 'final_score', 'master_score =']):
            print(f"master_signal.py:{i+1:4d}: {l.rstrip()}")

print("\n==================================================")
print("2. [B-2 / 결함 38] Coverage calculation & WEIGHT_REDISTRIBUTION in master_signal.py")
print("==================================================")
for i, l in enumerate(ms_lines):
    if 'WEIGHT_REDISTRIBUTION' in l or 'coverage =' in l or 'get_weights_for_modules' in l:
        print(f"master_signal.py:{i+1:4d}: {l.rstrip()}")
        for j in range(i, min(len(ms_lines), i + 25)):
            print(f"  {j+1:4d}: {ms_lines[j].rstrip()}")
        break

print("\n==================================================")
print("3. [B-3 / 결함 37] stock_scanner.py internal score vs get_master_signal")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\stock_scanner.py'), 'r', encoding='utf-8') as f:
    ss_lines = f.readlines()

for i, l in enumerate(ss_lines):
    if 'def _analyze_secondary_filters' in l:
        print(f"--- stock_scanner.py _analyze_secondary_filters near line {i+1} ---")
        for j in range(i, min(len(ss_lines), i + 40)):
            print(f"stock_scanner.py:{j+1:4d}: {ss_lines[j].rstrip()}")
        break

print("\n==================================================")
print("4. [A-5 조건] last_price conversion inside try block in kis_broker.py")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\kis_broker.py'), 'r', encoding='utf-8') as f:
    kb_lines = f.readlines()

for i, l in enumerate(kb_lines):
    if 'last_price = float(' in l:
        print(f"--- kis_broker.py near line {i+1} ---")
        for j in range(max(0, i-5), min(len(kb_lines), i+15)):
            print(f"kis_broker.py:{j+1:4d}: {kb_lines[j].rstrip()}")
        break

