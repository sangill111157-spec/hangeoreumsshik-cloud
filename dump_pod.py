import sys
sys.stdout.reconfigure(encoding='utf-8')

p = r"C:\trading\package\nvda_trading_system\backend\app\services\pod_manager.py"
with open(p, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()
    for i, line in enumerate(lines[120:155], 121):
        print(f"{i}: {line}", end='')
