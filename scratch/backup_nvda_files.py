# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

nvda_base = Path(r"C:\trading\package\nvda_trading_system\backend\app\services")
targets = [
    nvda_base / "scheduler.py",
    nvda_base / "auto_trader.py",
    nvda_base / "kis_broker.py",
    nvda_base / "account_state.py"
]

print("=== 1. 원본 파일 백업 (.bak_v110) ===")
for t in targets:
    if t.exists():
        bak = t.with_suffix(t.suffix + ".bak_v110")
        shutil.copy2(t, bak)
        print(f"  ✅ 백업 완료: {bak.name} ({bak.stat().st_size} bytes)")
    else:
        print(f"  ⚠️ 대상 파일 없음: {t}")
