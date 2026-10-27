# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\nvda.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target_block = """        stock_info_dict = {
            "current_price": stock_info.current_price,
            "pe_ratio": stock_info.pe_ratio,
            "eps": stock_info.eps,
            "week_52_high": stock_info.week_52_high,
            "week_52_low": stock_info.week_52_low,
            "volume": stock_info.volume
        }

        technical = analyzer.analyze(historical_data, stock_info.current_price)
        result = engine.analyze(stock_info_dict, technical, historical_data)"""

replacement_block = """        stock_info_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}

        technical = analyzer.analyze("NVDA", historical_data, stock_info.current_price)
        result = engine.analyze("NVDA", stock_info_dict, technical, historical_data)"""

if target_block in content:
    content = content.replace(target_block, replacement_block, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH 500 APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)
