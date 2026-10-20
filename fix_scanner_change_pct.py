# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

ss_path = os.path.join(backend_dir, r'app\services\stock_scanner.py')
with open(ss_path, 'r', encoding='utf-8') as f:
    ss_content = f.read()

# Fix change_percent reference in stock_scanner.py
ss_content_new = ss_content.replace("stock_info.change_percent", "getattr(stock_info, 'change_percent', ((stock_info.current_price - stock_info.previous_close) / stock_info.previous_close * 100.0) if getattr(stock_info, 'previous_close', 0) > 0 else 0.0)")

if ss_content != ss_content_new:
    with open(ss_path, 'w', encoding='utf-8') as f:
        f.write(ss_content_new)
    print("stock_scanner.py change_percent calculation fixed!")
    subprocess.run('git add app/services/stock_scanner.py', cwd=backend_dir, shell=True)
    res_c = subprocess.run('git commit -m "fix(scanner): compute change_percent safely from current_price and previous_close"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print("Commit Output:\n", res_c.stdout)

