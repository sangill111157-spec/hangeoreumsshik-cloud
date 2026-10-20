# -*- coding: utf-8 -*-
from pathlib import Path

sch_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py")
if sch_file.exists():
    text = sch_file.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    # find def job_hourly_scan
    start_idx = -1
    for idx, l in enumerate(lines):
        if "def job_hourly_scan" in l:
            start_idx = idx
            break
    if start_idx != -1:
        print(f"=== job_hourly_scan (lines {start_idx+1}~{start_idx+120}) ===")
        for idx in range(start_idx, min(start_idx+120, len(lines))):
            print(f"{idx+1}: {lines[idx]}")
