# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')

from app.services.data_collector import create_data_collector
from app.services.technical_analysis import TechnicalAnalyzer

dc = create_data_collector()
stock_info = dc.get_stock_info("NVDA")
historical = dc.get_historical_data("NVDA", period="1y")
ta = TechnicalAnalyzer()
tech = ta.analyze("NVDA", historical, stock_info.current_price)

bb = tech.bollinger_bands
ma20 = tech.moving_averages.ma_20

print("=== Bollinger Bands vs MA20 vs Current Price ===")
print(f"Lower Band:    {bb.lower_band:.4f}")
print(f"Middle Band:   {bb.middle_band:.4f}")
print(f"Upper Band:    {bb.upper_band:.4f}")
print(f"MA20:          {ma20:.4f}")
print(f"Current Price: {stock_info.current_price:.4f}")
print()
print(f"Condition 1: Lower ({bb.lower_band:.2f}) < Middle ({bb.middle_band:.2f}) < Upper ({bb.upper_band:.2f}) -> {bb.lower_band < bb.middle_band < bb.upper_band}")
print(f"Condition 2: Middle ({bb.middle_band:.2f}) == MA20 ({ma20:.2f}) -> {abs(bb.middle_band - ma20) < 0.001}")
print(f"Condition 3: Middle != Current Price -> {bb.middle_band != stock_info.current_price} (Diff: {abs(bb.middle_band - stock_info.current_price):.2f})")
