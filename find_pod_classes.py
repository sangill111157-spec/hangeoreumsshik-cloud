import sys
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if line.startswith("class ") or (i >= 240 and i <= 275):
            print(f"{i}: {line.strip()}")
