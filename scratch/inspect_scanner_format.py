# -*- coding: utf-8 -*-
from pathlib import Path

scanner_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\stock_scanner.py")
if scanner_file.exists():
    text = scanner_file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for idx, l in enumerate(lines):
        if "def scan_watchlist" in l or "candidates.append" in l or "'candidates':" in l:
            print(f"[{idx+1}] {l}")
