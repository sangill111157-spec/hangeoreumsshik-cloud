# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
scratch_dir = os.path.join(backend_dir, 'scratch')

with open(os.path.join(scratch_dir, 'collect_now.txt'), 'r', encoding='utf-8') as f:
    coll_text = f.read()

with open(os.path.join(scratch_dir, 'pytest_full.txt'), 'r', encoding='utf-8') as f:
    pyt_text = f.read()

print("=== collect_now.txt Summary ===")
coll_lines = [l for l in coll_text.splitlines() if l.strip()]
print(f"Total lines in collect_now.txt: {len(coll_lines)}")
print("First 10 items:")
for l in coll_lines[:10]:
    print(" ", l)
print("Last 10 items:")
for l in coll_lines[-10:]:
    print(" ", l)

print("\n=== pytest_full.txt Summary ===")
pyt_lines = pyt_text.splitlines()
print(f"Total lines in pytest_full.txt: {len(pyt_lines)}")
print("Last 10 lines of pytest_full.txt:")
for l in pyt_lines[-10:]:
    print(" ", l)
