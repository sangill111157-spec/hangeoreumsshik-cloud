# -*- coding: utf-8 -*-
import os, re

services_dir = r'C:\trading\package\nvda_trading_system\backend\app'
print('=== Searching .empty without try/except or None check ===')

for root, dirs, files in os.walk(services_dir):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for i, l in enumerate(lines):
                if '.empty' in l:
                    # check surrounding 5 lines
                    s = max(0, i-3)
                    e = min(len(lines), i+3)
                    print(f"--- {os.path.relpath(p, services_dir)} Line {i+1} ---")
                    for k in range(s, e):
                        print(f"  {k+1:4d}: {lines[k].strip()}")
