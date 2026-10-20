import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\stock_scanner.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i in range(20, 55):
        print(f"{i+1}: {lines[i]}", end='')
