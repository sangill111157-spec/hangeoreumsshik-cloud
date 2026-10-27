# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

reb_path = os.path.join(backend_dir, 'app', 'api', 'routes', 'rebalance.py')
with open(reb_path, 'rb') as f:
    reb_raw = f.read()

lines = reb_raw.splitlines()
for i in range(80, min(100, len(lines))):
    print(f"{i+1:3d} (bytes): {repr(lines[i])}")
    print(f"{i+1:3d} (str)  : {lines[i].decode('utf-8', errors='replace')}")
