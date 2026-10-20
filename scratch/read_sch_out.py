# -*- coding: utf-8 -*-
from pathlib import Path

base_path = Path(r"C:\trading\package\nvda_trading_system\backend")
log_file = base_path / "data" / "scheduler_output.log"
py_file = base_path / "run_scheduler.py"

print("=== run_scheduler.py ===")
if py_file.exists():
    lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    for idx, l in enumerate(lines[:100]):
        print(f"{idx+1}: {l}")

print("\n=== data/scheduler_output.log (최근 50줄) ===")
if log_file.exists():
    lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    print(f"총 {len(lines)}줄")
    for l in lines[-50:]:
        print(l)
