import sys
import os
import json

sys.path.insert(0, r"C:\trading\package\nvda_trading_system\backend")

from app.services.stock_scanner import get_stock_scanner

scanner = get_stock_scanner()
res = scanner.scan_watchlist(market="US")
print("=== SCAN_WATCHLIST 1 RUN RESULT ===")
print(json.dumps(res, indent=2, default=str))
