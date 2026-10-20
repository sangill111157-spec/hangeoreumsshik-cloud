# -*- coding: utf-8 -*-
files = [
    (r'C:\trading\package\nvda_trading_system\backend\app\services\event_engine.py', 150, 170),
    (r'C:\trading\package\nvda_trading_system\backend\app\services\darkpool_analyzer.py', 160, 175),
    (r'C:\trading\package\nvda_trading_system\backend\app\services\correlation_engine.py', 195, 215),
    (r'C:\trading\package\nvda_trading_system\backend\app\services\options_flow.py', 190, 205),
]

for p, s, e in files:
    print(f"=== {p} lines {s}~{e} ===")
    with open(p, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i in range(s-1, min(len(lines), e)):
        print(f"{i+1:4d}: " + lines[i].encode('ascii', errors='backslashreplace').decode('ascii'), end='')
    print('\n')
