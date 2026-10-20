# -*- coding: utf-8 -*-
from pathlib import Path

bat_file = Path(r"C:\trading\package\nvda_trading_system\backend\run_scheduler.bat")
if bat_file.exists():
    print(bat_file.read_text(encoding="utf-8", errors="ignore"))
