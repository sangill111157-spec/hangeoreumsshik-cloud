# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. Collect count and exact footer")
print("================================================================================")
res_coll = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '--collect-only', '-q'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
lines = res_coll.stdout.splitlines()
print(f"Total raw lines in collect: {len(lines)}")
for l in lines[-3:]:
    print(" ", repr(l))

print("\n================================================================================")
print("2. Git log (last 5 commits)")
print("================================================================================")
res_log = subprocess.run('git log --oneline -n 5', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_log.stdout)

print("\n================================================================================")
print("3. Git status -s -uall")
print("================================================================================")
res_st = subprocess.run('git status -s -uall', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_st.stdout)
