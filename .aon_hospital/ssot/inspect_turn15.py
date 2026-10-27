# -*- coding: utf-8 -*-
import sys, os, subprocess, json, urllib.request, time
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [결함 48 원인 조사] stock.py routes gather & _sd flow for investor & technical")
print("==================================================")
with open(os.path.join(backend_dir, r'app\api\routes\stock.py'), 'r', encoding='utf-8') as f:
    st_lines = f.readlines()
for i, l in enumerate(st_lines):
    if 'get_stock_master_signal' in l or 'gather(' in l:
        print(f"--- stock.py near line {i+1} ---")
        for j in range(i, min(len(st_lines), i + 65)):
            print(f"{j+1:4d}: {st_lines[j].rstrip()}")
        break

print("\n==================================================")
print("2. [결함 49 조사] master_signal.py confidence calculation source")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()
for i, l in enumerate(ms_lines):
    if 'confidence =' in l or 'master_confidence' in l or 'def calculate_final_master_signal' in l:
        if 'def calculate_final_master_signal' in l:
            print(f"--- master_signal.py calculate_final_master_signal from line {i+1} ---")
            for j in range(i, min(len(ms_lines), i + 75)):
                print(f"{j+1:4d}: {ms_lines[j].rstrip()}")
            break

print("\n==================================================")
print("3. [결함 41 조사] stock_scanner.py _analyze_secondary_filters")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\stock_scanner.py'), 'r', encoding='utf-8') as f:
    sc_lines = f.readlines()
for i, l in enumerate(sc_lines):
    if 'def _analyze_secondary_filters' in l or '_calculate_simple_score' in l:
        print(f"--- stock_scanner.py near line {i+1} ---")
        for j in range(i, min(len(sc_lines), i + 45)):
            print(f"{j+1:4d}: {sc_lines[j].rstrip()}")
        break

