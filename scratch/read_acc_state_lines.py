# -*- coding: utf-8 -*-
from pathlib import Path

acc_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\account_state.py")
lines = acc_file.read_text(encoding="utf-8", errors="ignore").splitlines()
for i in range(125, min(175, len(lines))):
    print(f"{i+1}: {lines[i]}")
