# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, threading
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [B-1] git grep for weights and redistribution in app/")
print("==================================================")
out_grep, _ = run_cmd('git grep -n -E "0\\.25|WEIGHT_REDISTRIBUTION|get_weights_for_modules|available_weights_sum|BASE_WEIGHTS" app/')
print(out_grep)

print("\n==================================================")
print("2. [B-5] 7 Dataclasses available field declaration")
print("==================================================")
out_dc, _ = run_cmd('git grep -n "available: bool" app/services/')
print(out_dc)

print("\n==================================================")
print("3. [결함 45] investor_analysis.py overall_confidence implementation")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\investor_analysis.py'), 'r', encoding='utf-8') as f:
    inv_lines = f.readlines()
for i, l in enumerate(inv_lines):
    if '_calculate_confidence' in l or 'overall_confidence' in l or 'confidence =' in l:
        print(f"--- investor_analysis.py near line {i+1} ---")
        for j in range(max(0, i-5), min(len(inv_lines), i+20)):
            print(f"{j+1:4d}: {inv_lines[j].rstrip()}")
        break

