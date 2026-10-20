import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\telegram_notifier.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:120], 1):
        print(f"{i}: {line}", end='')
