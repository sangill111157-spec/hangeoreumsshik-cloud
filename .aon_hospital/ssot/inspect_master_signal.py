# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def calculate_final_master_signal' in line or 'def _build_components' in line or 'components' in line:
        for j in range(i, min(len(lines), i+45)):
            print(f"{j+1:4d}: {lines[j]}", end='')
        print('\n---')
        break
