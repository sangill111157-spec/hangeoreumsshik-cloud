# -*- coding: utf-8 -*-
import subprocess
import os
import sys

def check_process():
    print("=== 1. Windows 실행 중인 프로세스 (nvda, trading, scheduler 관련) ===")
    cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*nvda*\' -or $_.CommandLine -like \'*trading*\' -or $_.CommandLine -like \'*scheduler*\' -or $_.CommandLine -like \'*uvicorn*\' } | Select-Object ProcessId, Name, CommandLine | Format-List"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='ignore')
    print(res.stdout)

    print("\n=== 2. 구글 시트 연동 코드 검색 ===")
    from pathlib import Path
    base_path = Path(r"C:\trading\package\nvda_trading_system\backend")
    found_gs = []
    for py_file in (base_path / "app").rglob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        if "sheets" in text.lower() or "google" in text.lower() or "gspread" in text.lower():
            found_gs.append(py_file.name)
    print(f"구글 시트 관련 파일: {found_gs}")

if __name__ == "__main__":
    check_process()
