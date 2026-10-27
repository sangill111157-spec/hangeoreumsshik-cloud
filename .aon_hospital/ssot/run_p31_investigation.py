# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. Find auto_trader.py across all drives")
print("==================================================")
# Search in common candidate directories
search_roots = [r'C:\trading', r'C:\Users\sangi\Downloads', r'C:\Users\sangi\OneDrive\Desktop', r'C:\Users\sangi\Documents']
found_paths = []
for sroot in search_roots:
    if os.path.exists(sroot):
        for root, dirs, files in os.walk(sroot):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'venv', '.venv', '__pycache__', 'AppData']]
            if 'auto_trader.py' in files:
                full_p = os.path.join(root, 'auto_trader.py')
                found_paths.append(full_p)

print("Found auto_trader.py files:")
for p in found_paths:
    size = os.path.getsize(p)
    with open(p, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"  - {p} (Size: {size} bytes, SHA256: {sha})")

print("\n==================================================")
print("2. git rev-parse --show-toplevel & base commit history")
print("==================================================")
res_top = subprocess.run('git rev-parse --show-toplevel', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git rev-parse --show-toplevel:", res_top.stdout.strip())

res_log_dfa = subprocess.run('git log --oneline dfa41f5..8a3641d', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\ngit log --oneline dfa41f5..8a3641d:")
print(res_log_dfa.stdout)

res_log_all = subprocess.run('git log --oneline -n 12', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\ngit log --oneline -n 12:")
print(res_log_all.stdout)

print("\n==================================================")
print("3. test_scheduler_sizing.py File Hash & Line Count")
print("==================================================")
sizing_path = os.path.join(backend_dir, 'tests', 'test_scheduler_sizing.py')
if os.path.exists(sizing_path):
    with open(sizing_path, 'r', encoding='utf-8') as f:
        sizing_content = f.read()
    lines_count = len(sizing_content.splitlines())
    sha_sizing = hashlib.sha256(sizing_content.encode('utf-8')).hexdigest()
    print(f"File: {sizing_path}")
    print(f"Line Count: {lines_count} lines")
    print(f"Byte Size: {len(sizing_content.encode('utf-8'))} bytes")
    print(f"SHA256: {sha_sizing}")

print("\n==================================================")
print("4. Root vs tests/ directory test files inspection")
print("==================================================")
root_test_files = [f for f in os.listdir(backend_dir) if f.startswith('test_') and f.endswith('.py')]
tests_dir_files = [f for f in os.listdir(os.path.join(backend_dir, 'tests')) if f.startswith('test_') and f.endswith('.py')]

print(f"Root test files ({len(root_test_files)}):", sorted(root_test_files))
print(f"tests/ test files ({len(tests_dir_files)}):", sorted(tests_dir_files))
