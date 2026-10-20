# -*- coding: utf-8 -*-
# 1. technical_analysis.py
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\technical_analysis.py', 'r', encoding='utf-8') as f:
    t_lines = f.readlines()
for i, line in enumerate(t_lines):
    if 'overall_signal' in line and ('strong_buy' in line.lower() or 'buy' in line.lower() or 'def ' in line):
        for j in range(max(0, i-2), min(len(t_lines), i+20)):
            print(f"technical_analysis.py {j+1:4d}: {t_lines[j]}", end='')
        print('\n---')
        break

# 2. stock.py components construction (lines 660~715)
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    s_lines = f.readlines()
for i in range(650, 715):
    print(f"stock.py {i+1:4d}: {s_lines[i]}", end='')
