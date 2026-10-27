# -*- coding: utf-8 -*-
import os, re

backend_dir = r'C:\trading\package\nvda_trading_system\backend\app'
print('=== Grep calculate_final_master_signal across backend ===')

for root, dirs, files in os.walk(backend_dir):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, backend_dir)
            with open(p, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for i, l in enumerate(lines):
                if 'calculate_final_master_signal' in l:
                    print(f"{rel}:{i+1:4d} | {l.strip()}")
