# -*- coding: utf-8 -*-
from pathlib import Path

trader_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\auto_trader.py")
lines = trader_file.read_text(encoding="utf-8", errors="ignore").splitlines()
for i in range(278, min(340, len(lines))):
    print(f"{i+1}: {lines[i]}")
