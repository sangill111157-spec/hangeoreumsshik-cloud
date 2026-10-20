# -*- coding: utf-8 -*-
from pathlib import Path
import re

base_path = Path(r"C:\trading\package\nvda_trading_system\backend")

def inspect_kis_errors():
    rec_file = base_path / "app" / "services" / "reconciler.py"
    kis_file = base_path / "app" / "services" / "kis_broker.py"
    
    print("=== 1. US_BALANCE_INQUIRE_NASD 호출 위치 탐색 ===")
    for py_file in (base_path / "app").rglob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        if "US_BALANCE_INQUIRE" in text or "US balance inquiry error" in text:
            print(f"📄 {py_file.name}:")
            for idx, l in enumerate(text.splitlines()):
                if "US_BALANCE" in l or "inquire" in l or "Fail-Closed" in l:
                    print(f"  [{idx+1}] {l.strip()[:110]}")

    print("\n=== 2. 실패율 21.7% 경고 로직 탐색 ===")
    for py_file in (base_path / "app").rglob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        if "실패율" in text or "failure_rate" in text or "연속 실패" in text:
            print(f"📄 {py_file.name}:")
            for idx, l in enumerate(text.splitlines()):
                if any(w in l for w in ["실패율", "failure_rate", "연속 실패", "Fail-Closed", "ACCOUNT_STATE_FAIL"]):
                    print(f"  [{idx+1}] {l.strip()[:110]}")

if __name__ == "__main__":
    inspect_kis_errors()
