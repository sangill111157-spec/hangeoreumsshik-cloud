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
print("=== Real BollingerBands Values ===")
print(f"upper_band:     {bb.upper_band:.2f}")
print(f"middle_band:    {bb.middle_band:.2f}")
print(f"lower_band:     {bb.lower_band:.2f}")
print(f"current_price:  {stock_info.current_price:.2f}")
print(f"dummy fallback (price * 1.05): {stock_info.current_price * 1.05:.2f}")
