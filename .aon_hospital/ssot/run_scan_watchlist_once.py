import sys, os
sys.path.insert(0, r"C:\trading\package\nvda_trading_system\backend")
sys.stdout.reconfigure(encoding='utf-8')

from app.services.stock_scanner import get_stock_scanner

scanner = get_stock_scanner()
print("[SCAN_START] Calling scan_watchlist('US')...")
res = scanner.scan_watchlist("US")
print("[SCAN_DONE] Result:", res)
