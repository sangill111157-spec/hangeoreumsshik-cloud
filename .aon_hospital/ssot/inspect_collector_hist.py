# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\data_collector.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== data_collector.py get_historical_data (lines 215~260) ===')
for i in range(215, 260):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
