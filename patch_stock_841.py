# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\stock.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        stock_info = collector.get_stock_info(ticker)
        historical_data = collector.get_historical_data(ticker, period="1y")
        current_price = stock_info.current_price

        technical = analyzer.analyze(historical_data, current_price)"""

replacement = """        stock_info = collector.get_stock_info(ticker)
        historical_data = collector.get_historical_data(ticker, period="1y")
        current_price = stock_info.current_price

        technical = analyzer.analyze(ticker, historical_data, current_price)"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH STEP 1 APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)
