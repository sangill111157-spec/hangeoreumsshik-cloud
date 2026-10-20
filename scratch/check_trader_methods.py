# -*- coding: utf-8 -*-
from pathlib import Path

trader_file = Path(r"C:\trading\package\nvda_trading_system\backend\app\services\auto_trader.py")
lines = trader_file.read_text(encoding="utf-8", errors="ignore").splitlines()
for idx, l in enumerate(lines):
    if "def execute" in l or "def place" in l or "def buy" in l or "def run_paper" in l:
        print(f"[{idx+1}] {l}")
