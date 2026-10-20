# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== master_signal.py: calculate_final_master_signal signature (lines 475~495) ===')
for i in range(474, 495):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== portfolio_manager.py line 513 surrounding ===')
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\portfolio_manager.py', 'r', encoding='utf-8') as f:
    p_lines = f.readlines()
for i in range(505, 520):
    print(f"{i+1:4d}: " + p_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
