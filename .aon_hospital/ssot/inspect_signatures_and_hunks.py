# -*- coding: utf-8 -*-
import sys, os, subprocess, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [1cdbedf Hunk Headers] git show 1cdbedf --unified=0")
print("==================================================")
stdout, _ = run_cmd("git show 1cdbedf --unified=0")
for line in stdout.split('\n'):
    if line.startswith("@@") or line.startswith("diff --git") or line.startswith("---") or line.startswith("+++"):
        print(line)

print("\n==================================================")
print("2. [calculate_final_master_signal Signature] master_signal.py:485-515")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()
for i in range(485, min(520, len(ms_lines))):
    print(f"{i+1:4d}: {ms_lines[i].rstrip()}")

print("\n==================================================")
print("3. [portfolio_manager.py:500-530]")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\portfolio_manager.py'), 'r', encoding='utf-8', errors='replace') as f:
    pm_lines = f.readlines()
for i in range(500, min(535, len(pm_lines))):
    print(f"{i+1:4d}: {pm_lines[i].rstrip()}")

print("\n==================================================")
print("4. [master_signal.py:775-800]")
print("==================================================")
for i in range(775, min(805, len(ms_lines))):
    print(f"{i+1:4d}: {ms_lines[i].rstrip()}")

print("\n==================================================")
print("5. [telegram_command_listener.py:60-80]")
print("==================================================")
tcl_path = os.path.join(backend_dir, r'telegram_command_listener.py')
if os.path.exists(tcl_path):
    with open(tcl_path, 'r', encoding='utf-8', errors='replace') as f:
        tcl_lines = f.readlines()
    for i in range(55, min(85, len(tcl_lines))):
        print(f"{i+1:4d}: {tcl_lines[i].rstrip()}")
else:
    print("telegram_command_listener.py does not exist")

