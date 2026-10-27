import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\stock_scanner.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "def " in line:
            print(f"{i+1}: {line.strip()}")
