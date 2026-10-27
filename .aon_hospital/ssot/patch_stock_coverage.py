# -*- coding: utf-8 -*-
import sys

stock_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py'
with open(stock_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Add coverage & available_module_count to response dict
for i, l in enumerate(lines):
    if '"weights_used": result.weights_used,' in l:
        lines[i] = l + '            "coverage": result.coverage,\n            "available_module_count": result.available_module_count,\n'
        break

with open(stock_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("PATCH stock.py response fields SUCCESS")
