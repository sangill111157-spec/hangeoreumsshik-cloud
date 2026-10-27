# -*- coding: utf-8 -*-
import sys, os, subprocess, json, inspect

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. Gitignore and Check-ignore Check")
print("==================================================")
res_gi = subprocess.run('git check-ignore -v h.txt h_full.txt', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git check-ignore -v h.txt h_full.txt:")
print(res_gi.stdout)
print(res_gi.stderr)

res_gi_full = subprocess.run('git ls-files --others --ignored --exclude-standard', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git ls-files --others --ignored --exclude-standard:")
print(res_gi_full.stdout[:2000])

gitignore_path = os.path.join(backend_dir, '.gitignore')
if os.path.exists(gitignore_path):
    print("\n--- .gitignore full content ---")
    with open(gitignore_path, 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())
else:
    print(".gitignore NOT FOUND at backend_dir")

print("\n==================================================")
print("2. calculate_master_signal grep & branches")
print("==================================================")
res_grep_cms = subprocess.run('git grep -n "calculate_master_signal" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git grep -n 'calculate_master_signal' app/:")
print(res_grep_cms.stdout)

print("\n==================================================")
print("3. Scheduler & Telegram Notifier Inspection")
print("==================================================")
res_grep_sched = subprocess.run('git grep -n "Scheduler" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Scheduler class search:")
print(res_grep_sched.stdout)

res_grep_send = subprocess.run('git grep -n "_send_telegram" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\n_send_telegram grep:")
print(res_grep_send.stdout)

res_grep_tn = subprocess.run('git grep -n "TelegramNotifier" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\nTelegramNotifier grep:")
print(res_grep_tn.stdout)
