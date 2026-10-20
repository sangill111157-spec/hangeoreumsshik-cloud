# -*- coding: utf-8 -*-
import sys

ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'if master_score >= 80:' in l:
        lines[i] = '        if master_score is None:\n            pass\n        elif master_score >= 80:\n'
        break

with open(ms_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("PATCH signal check for master_score None SUCCESS")
