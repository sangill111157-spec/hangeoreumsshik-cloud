# -*- coding: utf-8 -*-
from pathlib import Path

sch_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py")
lines = sch_file.read_text(encoding="utf-8", errors="ignore").splitlines()
for i in range(1015, min(1035, len(lines))):
    print(f"{i+1}: {lines[i]}")
