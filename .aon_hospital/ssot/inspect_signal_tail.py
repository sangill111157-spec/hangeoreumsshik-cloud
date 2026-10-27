# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== stock.py lines 640~720 ===')
for i in range(640, 720):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
