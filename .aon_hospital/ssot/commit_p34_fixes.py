# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Commit 1: Isolate stop loss state file in tests
res_add1 = subprocess.run('git add tests/conftest.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
res_com1 = subprocess.run('git commit -m "fix(security): isolate STOP_LOSS_STATE_FILE and TradingScheduler in conftest autouse fixture"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit 1 result:")
print(res_com1.stdout)

# Commit 2: Fix rebalance.py encoding
res_add2 = subprocess.run('git add app/api/routes/rebalance.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
res_com2 = subprocess.run('git commit -m "fix(encoding): restore corrupted Korean comment in rebalance.py"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\nCommit 2 result:")
print(res_com2.stdout)

# Git status & log
print("\nGit log (last 4):")
res_log = subprocess.run('git log --oneline -n 4', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_log.stdout)

print("\nGit status -s -uall:")
res_st = subprocess.run('git status -s -uall', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_st.stdout)
