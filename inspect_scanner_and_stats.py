# -*- coding: utf-8 -*-
import sys, os, subprocess, json

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Inspect _calculate_simple_score in stock_scanner.py
ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_lines = f.readlines()

print("==================================================")
print("1. [결함 41 & 62] stock_scanner.py _calculate_simple_score and secondary filter lines")
print("==================================================")
for idx, l in enumerate(ss_lines):
    if 'def _calculate_simple_score' in l or 'def _analyze_secondary_filters' in l:
        print(f"--- Line {idx+1}: {l.strip()} ---")
        for j in range(idx, min(idx + 30, len(ss_lines))):
            print(f"{j+1:4d}: {ss_lines[j]}", end='')

# 2. Get git show --stat for the last 10 commits
print("\n==================================================")
print("2. [B-5] git show --stat for recent commits")
print("==================================================")
res_stat = subprocess.run('git log --stat -n 6', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8')
print(res_stat.stdout)

