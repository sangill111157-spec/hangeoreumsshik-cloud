import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\risk.py', 'r', encoding='utf-8') as f:
    print("=== risk.py ===")
    print(f.read()[:800])

with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    print("=== stock.py ===")
    print(f.read()[:800])

with open(r'C:\trading\package\nvda_trading_system\backend\app\services\risk_monitor.py', 'r', encoding='utf-8') as f:
    print("=== risk_monitor.py defs ===")
    for line in f:
        if line.strip().startswith('def '):
            print(line.strip())
