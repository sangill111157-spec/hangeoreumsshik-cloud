# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("1. Untrack data/*.json & Clean up root artifacts")
print("==================================================")

# 1) Untrack 5 json files from git
data_files = [
    'data/micro_live_7d_tracker.json',
    'data/performance_log.json',
    'data/scheduler_log.json',
    'data/stop_loss_state.json',
    'data/trade_log.json'
]

for df in data_files:
    res = subprocess.run(f'git rm --cached {df}', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(f"git rm --cached {df}: {res.stdout.strip()} {res.stderr.strip()}")

# 2) Update .gitignore to include data/*.json and unversioned data
gi_path = os.path.join(backend_dir, '.gitignore')
with open(gi_path, 'r', encoding='utf-8') as f:
    gi_lines = f.read().splitlines()

if "data/*.json" not in gi_lines:
    gi_lines.append("data/*.json")
    gi_lines.append("pytest_p27_full.txt")
    with open(gi_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(gi_lines) + "\n")
    print("Updated .gitignore with data/*.json")

# 3) Remove pytest_p27_full.txt if present
p27_file = os.path.join(backend_dir, 'pytest_p27_full.txt')
if os.path.exists(p27_file):
    os.remove(p27_file)
    print(f"Removed {p27_file}")

# 4) Git commit data untracking & gitignore update
res_add = subprocess.run('git add .gitignore', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
res_commit = subprocess.run('git commit -m "chore(git): untrack runtime data json files and update gitignore"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\nGit commit result:")
print(res_commit.stdout)

print("\n==================================================")
print("2. git status -s -uall after cleanup")
print("==================================================")
res_st = subprocess.run('git status -s -uall', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git status -s -uall:")
print(res_st.stdout)

print("\n==================================================")
print("3. SSOT Grep for ENABLE_LIVE_ORDERS & ALLOW_ORDER_EXECUTION")
print("==================================================")
res_grep_tokens = subprocess.run('git grep -n "ENABLE_LIVE_ORDERS\\|ALLOW_ORDER_EXECUTION" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_grep_tokens.stdout)
