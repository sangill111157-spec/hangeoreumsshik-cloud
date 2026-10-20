# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. Search all test_scheduler_sizing.py across drives")
print("================================================================================")
search_dirs = [r'C:\trading', r'C:\Users\sangi\Downloads', r'C:\Users\sangi\OneDrive\Desktop']
found_files = []
for sd in search_dirs:
    if os.path.exists(sd):
        for root, dirs, files in os.walk(sd):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv', '.venv', '__pycache__', 'AppData']]
            if 'test_scheduler_sizing.py' in files:
                fp = os.path.join(root, 'test_scheduler_sizing.py')
                found_files.append(fp)

for fp in found_files:
    with open(fp, 'rb') as f:
        content = f.read()
    sha = hashlib.sha256(content).hexdigest()
    lines_count = len(content.splitlines())
    print(f"Path: {fp}")
    print(f"  Lines: {lines_count}, Bytes: {len(content)}, SHA256: {sha}")

print("\n================================================================================")
print("2. test_scheduler_sizing.py exact functions & lines (1 to end)")
print("================================================================================")
main_sizing = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
with open(main_sizing, 'r', encoding='utf-8', errors='replace') as f:
    s_lines = f.readlines()

def_list = []
for idx, l in enumerate(s_lines, 1):
    if re.match(r'^\s*def test_', l):
        def_list.append((idx, l.strip()))

print(f"Total def test_ count in test_scheduler_sizing.py: {len(def_list)}")
print("First 5 def test_:")
for idx, fn in def_list[:5]:
    print(f"  Line {idx:4d}: {fn}")
print("Last 5 def test_:")
for idx, fn in def_list[-5:]:
    print(f"  Line {idx:4d}: {fn}")

# Check calculate_master_signal line number
for idx, fn in def_list:
    if "calculate_master_signal" in fn:
        print(f"\nExact line for calculate_master_signal: Line {idx} ({fn})")
