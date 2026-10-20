# -*- coding: utf-8 -*-
import sys, os, subprocess, collections, hashlib

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')
os.makedirs(scratch_dir, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. [Task 1] kis_broker.py Git Log, Hash Comparison & Chokepoint Grep")
print("================================================================================")
res_klog = subprocess.run('git log --oneline -- app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git log --oneline -- app/services/kis_broker.py:")
print(res_klog.stdout)

res_khash = subprocess.run('git hash-object app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
res_krev = subprocess.run('git rev-parse HEAD:app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"git hash-object app/services/kis_broker.py    : {res_khash.stdout.strip()}")
print(f"git rev-parse HEAD:app/services/kis_broker.py : {res_krev.stdout.strip()}")

res_kgrep_assert = subprocess.run('git grep -n "_assert_order_allowed" app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\ngit grep -n '_assert_order_allowed' app/services/kis_broker.py:")
print(res_kgrep_assert.stdout)

res_kgrep_post = subprocess.run('git grep -n "def \\|\\.post(" app/services/kis_broker.py', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\ngit grep -n 'def | .post(' app/services/kis_broker.py:")
print(res_kgrep_post.stdout)

print("\n================================================================================")
print("2. [Task 2] safety_guard Killswitch Wiring Inspection across app/")
print("================================================================================")
res_sg = subprocess.run('git grep -n "safety_guard\\|SafetyGuard\\|can_trade\\|check_trade_allowed" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("git grep -n 'safety_guard|SafetyGuard|can_trade|check_trade_allowed' app/:")
print(res_sg.stdout if res_sg.stdout else "(None found)")

sg_file = os.path.join(backend_dir, 'app', 'services', 'safety_guard.py')
if os.path.exists(sg_file):
    with open(sg_file, 'r', encoding='utf-8', errors='replace') as f:
        sg_lines = f.readlines()
    print("\n--- app/services/safety_guard.py L100-125 ---")
    for i in range(99, min(125, len(sg_lines))):
        print(f"{i+1:4d}: {sg_lines[i]}", end="")
    print("\n--- app/services/safety_guard.py L280-315 ---")
    for i in range(279, min(315, len(sg_lines))):
        print(f"{i+1:4d}: {sg_lines[i]}", end="")

print("\n================================================================================")
print("3. [Task 3] auto_trader.py execute_trade DRY_RUN Full Branch Source (L240-335)")
print("================================================================================")
at_file = os.path.join(backend_dir, 'app', 'services', 'auto_trader.py')
with open(at_file, 'r', encoding='utf-8', errors='replace') as f:
    at_lines = f.readlines()

for i in range(240, min(335, len(at_lines))):
    print(f"{i+1:4d}: {at_lines[i]}", end="")

print("\n================================================================================")
print("4. [Task 3] collect_p37.txt Counter Raw Script Output")
print("================================================================================")
col_path = os.path.join(scratch_dir, 'collect_p37.txt')
with open(col_path, 'r', encoding='utf-8', errors='replace') as f:
    c_lines = f.readlines()

colon_lines = [l.strip() for l in c_lines if "::" in l]
counter = collections.Counter(l.split("::")[0].strip() for l in colon_lines)

print(f"Total files with tests: {len(counter)}")
for fname, cnt in sorted(counter.items()):
    print(f"  {fname:45s}: {cnt:3d}")
print(f"-------------------------------------------------------------")
print(f"  {'SUM of Counter':45s}: {sum(counter.values()):3d}")
