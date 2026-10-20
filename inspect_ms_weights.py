# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== BASE_WEIGHTS in master_signal.py (lines 45~95) ===')
for i in range(45, 95):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== get_weights_for_modules in master_signal.py (lines 100~130) ===')
for i in range(95, 130):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
