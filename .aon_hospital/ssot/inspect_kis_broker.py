# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. kis_broker.py L130-160 exact source")
print("================================================================================")
kb_path = os.path.join(backend_dir, 'app', 'services', 'kis_broker.py')
with open(kb_path, 'r', encoding='utf-8', errors='replace') as f:
    kb_lines = f.readlines()

for i in range(129, min(160, len(kb_lines))):
    print(f"{i+1:4d}: {kb_lines[i]}", end="")
