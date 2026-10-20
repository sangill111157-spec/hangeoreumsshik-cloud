# -*- coding: utf-8 -*-
import sys, os, hashlib, glob

scratch_dir = r'C:\trading\package\nvda_trading_system\backend\scratch'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print(f"{'Filename':35s} | {'Length':10s} | {'SHA256'}")
print("-" * 115)

targets = [
    'p42_all_transmission.txt',
    'p42_sizing_gitlog.txt',
    'p42_full_run.txt',
    'p43_route_gate_investigation.txt',
    'p43_patch_diff.txt',
    'p43_patch_test_run.txt',
    'p43_full_run.txt'
]

for fname in targets:
    p = os.path.join(scratch_dir, fname)
    if os.path.exists(p):
        with open(p, 'rb') as f:
            b = f.read()
        sha = hashlib.sha256(b).hexdigest()
        print(f"{fname:35s} | {len(b):10d} | {sha}")
