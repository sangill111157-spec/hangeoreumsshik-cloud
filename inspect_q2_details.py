# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== 1. App.tsx lines 270~295 ===')
for i in range(270, 295):
    print(f"Line {i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== 2. App.tsx lines 415~428 ===')
for i in range(415, 428):
    print(f"Line {i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
