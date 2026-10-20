import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i in range(125, 145):
        print(f"{i+1}: {repr(lines[i])}")
