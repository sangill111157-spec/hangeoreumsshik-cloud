# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    s_lines = f.readlines()

print('=== stock.py routes ===')
for i, line in enumerate(s_lines):
    if any(k in line for k in ['"/{ticker}/price"', '"/{ticker}/analysis"', '"/{ticker}/technical"', '"/account/balance"']) and '@router.get' in line:
        print(f'Line {i+1}: {line.strip()}')
        print(f'Line {i+2}: {s_lines[i+1].strip()}')

for p in [r'C:\trading\package\nvda_trading_system\backend\app\api\routes\account.py', r'C:\trading\package\nvda_trading_system\backend\app\api\routes\nvda.py']:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if '/nvda' in line and '@router.get' in line:
                print(f'{p} Line {i+1}: {line.strip()}')
                print(f'Line {i+2}: {lines[i+1].strip()}')
    except Exception as e:
        print(e)
