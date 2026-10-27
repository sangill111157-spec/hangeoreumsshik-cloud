# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\nvda.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        # 2. 기술적 분석
        technical = analyzer.analyze(historical_data, stock_info_dict.current_price)"""

replacement = """        # 2. 기술적 분석
        technical = analyzer.analyze("NVDA", historical_data, stock_info_dict.current_price)"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH APPLIED: analyzer.analyze('NVDA', ...)")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)
