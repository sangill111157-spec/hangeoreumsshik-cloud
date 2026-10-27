# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\master.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                "bollinger_bands": {
                    "upper": tech.bollinger_bands.upper if hasattr(tech.bollinger_bands, 'upper') else stock_info.current_price * 1.05,
                    "middle": tech.bollinger_bands.middle if hasattr(tech.bollinger_bands, 'middle') else stock_info.current_price,
                    "lower": tech.bollinger_bands.lower if hasattr(tech.bollinger_bands, 'lower') else stock_info.current_price * 0.95
                },"""

replacement = """                "bollinger_bands": {
                    "upper": tech.bollinger_bands.upper_band,
                    "middle": tech.bollinger_bands.middle_band,
                    "lower": tech.bollinger_bands.lower_band
                },"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("STEP 3 PATCH APPLIED SUCCESSFULLY")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)
