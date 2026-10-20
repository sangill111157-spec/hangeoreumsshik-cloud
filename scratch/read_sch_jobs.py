# -*- coding: utf-8 -*-
from pathlib import Path

sch_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py")
if sch_file.exists():
    lines = sch_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    print(f"=== scheduler.py 라인 2300~2410 ===")
    for idx in range(2300, min(2410, len(lines))):
        print(f"{idx+1}: {lines[idx]}")
