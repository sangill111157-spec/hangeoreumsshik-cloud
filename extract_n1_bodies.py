# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== 1. get_stock_technical (around line 175~225) ===')
for i in range(174, 225):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

print('\n=== 2. get_stock_investor_analysis (around line 225~285) ===')
for i in range(225, 285):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
