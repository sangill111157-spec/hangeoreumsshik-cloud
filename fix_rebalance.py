with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'risk_after' in line and 'risk_before' in line:
        print(f"Line {i+1}: {repr(line)}")
