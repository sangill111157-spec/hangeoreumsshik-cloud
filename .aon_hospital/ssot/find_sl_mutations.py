# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. Find all tests modifying STOP_LOSS_STATE_FILE or saving stop loss state")
print("================================================================================")

res1 = subprocess.run('git grep -n "_save_stop_loss_state\\|job_stop_loss_monitor" tests/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Tests calling _save_stop_loss_state or job_stop_loss_monitor:")
print(res1.stdout)
