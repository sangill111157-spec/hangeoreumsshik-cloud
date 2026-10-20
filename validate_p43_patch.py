# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

venv_py = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
venv_pytest = os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Run pytest on test_auto_trader_toggle.py
r_toggle = subprocess.run([venv_pytest, 'tests/test_auto_trader_toggle.py', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
f_patch_test = os.path.join(scratch_dir, 'p43_patch_test_run.txt')
with open(f_patch_test, 'w', encoding='utf-8') as f:
    f.write(r_toggle.stdout + "\n")

# Run full pytest suite to scratch/p43_full_run.txt
f_full = os.path.join(scratch_dir, 'p43_full_run.txt')
cmd_full = f'"{venv_pytest}" tests/ -v -rs > "{f_full}" 2>&1'
subprocess.run(cmd_full, cwd=backend_dir, shell=True)

# Run git diff --stat
r_diff = subprocess.run('git diff --stat', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
f_diff = os.path.join(scratch_dir, 'p43_patch_diff.txt')
with open(f_diff, 'w', encoding='utf-8') as f:
    f.write(r_diff.stdout + "\n")

print("P43 patch validation completed.")
