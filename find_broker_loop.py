import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if any(k in line for k in ['_get_us_balance', 'get_orderable_cash_usd', 'Event loop', 'loop', 'httpx', 'AsyncClient']):
            print(f"{i+1}: {line.strip()[:140]}")
