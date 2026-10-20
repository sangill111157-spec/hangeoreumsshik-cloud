# -*- coding: utf-8 -*-
from pathlib import Path

scanner_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\stock_scanner.py")
lines = scanner_file.read_text(encoding="utf-8", errors="ignore").splitlines()
for i in range(395, min(445, len(lines))):
    print(f"{i+1}: {lines[i]}")
