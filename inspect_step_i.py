# -*- coding: utf-8 -*-
with open(r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def print_fn_body(start_line, max_lines=40):
    for i in range(start_line-1, min(len(lines), start_line-1+max_lines)):
        if i > start_line-1 and lines[i].strip().startswith('@router.'):
            break
        print(f"{i+1:4d}: {lines[i]}", end='')

print("=== 1. get_stock_price (line 85) ===")
print_fn_body(85, 30)

print("\n=== 2. get_stock_technical (line 179) ===")
print_fn_body(179, 30)

print("\n=== 3. get_stock_investor_analysis (line 230) ===")
print_fn_body(230, 30)

print("\n=== 4. /api/stock/{ticker}/signal handler (line 554) ===")
print_fn_body(554, 75)
