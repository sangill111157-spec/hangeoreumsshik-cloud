# -*- coding: utf-8 -*-
import sys, os, subprocess, json

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Inspect _analyze_secondary_filters and _calculate_simple_score in stock_scanner.py
ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_lines = f.readlines()

print("==================================================")
print("1. [결함 41 & 62] stock_scanner.py _analyze_secondary_filters and simple score lines")
print("==================================================")
for idx, l in enumerate(ss_lines):
    if 'def _analyze_secondary_filters' in l:
        print(f"--- _analyze_secondary_filters start at line {idx+1} ---")
        for j in range(idx, min(idx + 50, len(ss_lines))):
            print(f"{j+1:4d}: {ss_lines[j]}", end='')
        break

# 2. Inspect adjustments section in master_signal.py
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()

print("\n==================================================")
print("2. [B-4] master_signal.py adjustments section (lines 338-360)")
print("==================================================")
for idx, l in enumerate(ms_lines):
    if 'def event_to_adjustment' in l:
        print(f"--- event_to_adjustment start at line {idx+1} ---")
        for j in range(idx, min(idx + 35, len(ms_lines))):
            print(f"{j+1:4d}: {ms_lines[j]}", end='')
        break

