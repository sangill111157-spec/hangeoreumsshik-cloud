# -*- coding: utf-8 -*-
# Check current master_signal.py calculate_final_master_signal signature & lines 520~560
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== master_signal.py lines 520~560 ===')
for i in range(520, 560):
    print(f"{i+1:4d}: {lines[i]}", end='')

print('\n\n=== MasterSignalResult definition (lines 140~175) ===')
for i in range(140, 175):
    print(f"{i+1:4d}: {lines[i]}", end='')
