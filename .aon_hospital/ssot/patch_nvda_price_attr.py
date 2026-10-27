# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\nvda.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = "result.nvda_price"
replacement = "result.current_price"

if target in content:
    content = content.replace(target, replacement)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH APPLIED: result.nvda_price -> result.current_price")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)
