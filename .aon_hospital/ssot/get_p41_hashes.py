# -*- coding: utf-8 -*-
import sys, os, hashlib, glob

scratch_dir = r'C:\trading\package\nvda_trading_system\backend\scratch'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print(f"{'Filename':30s} | {'Length':10s} | {'SHA256'}")
print("-" * 110)

for p in sorted(glob.glob(os.path.join(scratch_dir, 'p41_*.txt'))):
    fname = os.path.basename(p)
    with open(p, 'rb') as f:
        b = f.read()
    sha = hashlib.sha256(b).hexdigest()
    print(f"{fname:30s} | {len(b):10d} | {sha}")
