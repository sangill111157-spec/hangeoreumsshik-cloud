# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib, json

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [P0-2] git show 772b5af^:data/stop_loss_state.json")
print("================================================================================")
res_git_sl = subprocess.run('git show 772b5af^:data/stop_loss_state.json', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git show 772b5af^:data/stop_loss_state.json Output:")
print(res_git_sl.stdout)

print("\n================================================================================")
print("2. [P0-3] Python Process Inspection (PIDs & CommandLines)")
print("================================================================================")
cmd_ps = 'powershell -Command "Get-CimInstance Win32_Process -Filter \\"Name like \'%python%\'\\" | Select-Object ProcessId, CommandLine, CreationDate"'
res_ps = subprocess.run(cmd_ps, cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_ps.stdout)

print("\n================================================================================")
print("3. [P0-3] git grep -n '_save_stop_loss_state' app/")
print("================================================================================")
res_grep_save = subprocess.run('git grep -n "_save_stop_loss_state" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_grep_save.stdout)

print("\n================================================================================")
print("4. [P0-4] git log --oneline -6 (Exact Commit History)")
print("================================================================================")
res_log6 = subprocess.run('git log --oneline -6', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_log6.stdout)
