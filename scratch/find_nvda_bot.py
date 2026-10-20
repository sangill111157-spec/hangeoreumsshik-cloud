# -*- coding: utf-8 -*-
import subprocess
import os
import sys
from pathlib import Path

def find_nvda_bot():
    print("=== 1. 현재 실행 중인 Python 프로세스 조사 ===")
    try:
        cmd = 'powershell -NoProfile -Command "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Path, CommandLine | Format-List"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='ignore')
        print(res.stdout[:2000])
    except Exception as e:
        print("Error getting processes:", e)

    print("\n=== 2. C:\\Users\\sangi 디렉토리 내 트레이딩 봇 후보 폴더/파일 탐색 ===")
    keywords = ["nvda", "trading", "quant", "kis", "stock", "scheduler"]
    base_user = Path("C:/Users/sangi")
    
    # 주요 디렉토리 탐색
    search_dirs = [
        base_user / "Downloads",
        base_user / "Desktop",
        base_user / "Documents",
        base_user / "Projects",
        base_user / "workspace",
        base_user
    ]
    
    found_candidates = []
    for d in search_dirs:
        if not d.exists():
            continue
        try:
            for item in d.iterdir():
                name_l = item.name.lower()
                if any(k in name_l for k in ["nvda", "trading", "kis", "stock", "shin"]):
                    found_candidates.append(item)
        except Exception:
            pass

    for c in sorted(set(found_candidates)):
        print(f"후보: {c}")

if __name__ == "__main__":
    find_nvda_bot()
