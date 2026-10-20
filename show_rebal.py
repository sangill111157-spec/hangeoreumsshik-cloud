with open(r'C:\trading\package\nvda_trading_system\backend\app\services\rebalance_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(80, 92):
    print(f"{i+1}: {repr(lines[i])}")
