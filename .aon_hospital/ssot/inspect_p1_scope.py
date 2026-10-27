# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('=== master_signal.py lines 570~615 ===')
for i in range(569, 615):
    print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')

with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    s_lines = f.readlines()

print('\n=== stock.py /signal handler passing to master engine (lines 665~690) ===')
for i in range(665, 690):
    print(f"{i+1:4d}: " + s_lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
