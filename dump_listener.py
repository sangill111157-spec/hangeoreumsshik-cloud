import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(230, 330):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}", end='')
