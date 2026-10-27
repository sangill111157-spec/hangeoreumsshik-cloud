import yfinance as yf
import json

ticker = yf.Ticker("JPM")
fast = ticker.fast_info
info = {
    "last_price": getattr(fast, "last_price", None),
    "previous_close": getattr(fast, "previous_close", None),
    "last_volume": getattr(fast, "last_volume", None),
    "timezone": getattr(fast, "timezone", None),
    "currency": getattr(fast, "currency", None),
    "exchange": getattr(fast, "exchange", None),
}
print("=== YFINANCE JPM DATA ===")
print(json.dumps(info, indent=2))
