# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import re
import json

base_path = Path(r"C:\trading\package\nvda_trading_system\backend")

def analyze_backend():
    print("=== 1. backend 디렉토리 구조 및 주요 파일 ===")
    for item in sorted(base_path.iterdir()):
        if item.is_dir():
            print(f"📁 {item.name}/")
        else:
            print(f"📄 {item.name} ({item.stat().st_size} bytes)")

    print("\n=== 2. 최신 로그 파일 목록 ===")
    logs_dir = base_path / "logs"
    if logs_dir.exists():
        logs = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        for l in logs[:10]:
            print(f"  로그: {l.name} ({l.stat().st_size / 1024:.1f} KB, 수정시각: {l.stat().st_mtime})")
    
    print("\n=== 3. .env 파일 안전 마스킹 검사 ===")
    env_files = list(base_path.glob("*.env*")) + list(Path(r"C:\trading\package\nvda_trading_system").glob("*.env*"))
    for ef in env_files:
        print(f"  발견된 ENV: {ef}")
        try:
            lines = ef.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line in lines:
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    # 마스킹 처리하여 키 존재 여부만 출력
                    if len(v) > 6:
                        masked = v[:3] + "****" + v[-3:]
                    else:
                        masked = "****"
                    print(f"    - {k} = {masked}")
        except Exception as e:
            print("    Error reading:", e)

if __name__ == "__main__":
    analyze_backend()
