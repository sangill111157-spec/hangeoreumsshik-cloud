# -*- coding: utf-8 -*-
import sys, os, subprocess, hashlib

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("P0-1: Repository Identity & File Hash Verification")
print("==================================================")

res_toplevel = subprocess.run('git rev-parse --show-toplevel', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"git rev-parse --show-toplevel: {res_toplevel.stdout.strip()}")

res_head = subprocess.run('git rev-parse HEAD', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(f"git rev-parse HEAD: {res_head.stdout.strip()}")

sched_path = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')
print(f"scheduler.py Absolute Path: {sched_path}")

if os.path.exists(sched_path):
    with open(sched_path, 'rb') as f:
        sched_bytes = f.read()
    sha256_hash = hashlib.sha256(sched_bytes).hexdigest()
    print(f"scheduler.py SHA256: {sha256_hash}")
    print(f"scheduler.py Size: {len(sched_bytes)} bytes")

print("\n==================================================")
print("P1-5: send_message full source & parse_mode defaults")
print("==================================================")
tn_path = os.path.join(backend_dir, 'app', 'services', 'telegram_notifier.py')
with open(tn_path, 'r', encoding='utf-8') as f:
    tn_lines = f.readlines()
for i in range(24, min(110, len(tn_lines))):
    print(f"{i+1:4d}: {tn_lines[i]}", end="")

print("\n==================================================")
print("P1-8: order_gate.py full source & ALLOW_ORDER_EXECUTION grep")
print("==================================================")
og_path = os.path.join(backend_dir, 'app', 'core', 'order_gate.py')
if os.path.exists(og_path):
    with open(og_path, 'r', encoding='utf-8') as f:
        print(f.read())
else:
    print(f"{og_path} NOT FOUND, grepping for order_gate...")
    res_og_find = subprocess.run('git grep -n "order_gate" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(res_og_find.stdout)

res_grep_allow = subprocess.run('git grep -n "ALLOW_ORDER_EXECUTION" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\ngit grep -n 'ALLOW_ORDER_EXECUTION' app/:")
print(res_grep_allow.stdout)

res_grep_live_gate = subprocess.run('git grep -n "ENABLE_LIVE_ORDERS" app/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("\ngit grep -n 'ENABLE_LIVE_ORDERS' app/:")
print(res_grep_live_gate.stdout)

print("\n==================================================")
print("P1-6: git status -s -uall data/")
print("==================================================")
res_data_status = subprocess.run('git status -s -uall data/', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(res_data_status.stdout)
