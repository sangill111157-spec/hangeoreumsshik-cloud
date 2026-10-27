import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[175:230], 176):
        print(f"{i}: {line}", end='')
