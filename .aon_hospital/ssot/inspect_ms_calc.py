# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Let's inspect calculate_kelly around line 430-445
print("Inspecting calculate_kelly in master_signal.py...")
lines = ms_c.split('\n')
for i, line in enumerate(lines):
    if "def calculate_kelly(" in line:
        for j in range(i, min(len(lines), i + 65)):
            print(f"{j+1:3d}: {lines[j]}")
        break
