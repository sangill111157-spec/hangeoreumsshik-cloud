# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

target_words = [
    "US_BALANCE_INQUIRE_NASD",
    "107,246.38",
    "107246",
    "자동화 작업 등록됨",
    "장중 스캔 완료",
    "일일 마감 리포트",
    "손절 전역 스캔 3회",
    "주간 성과 리포트"
]

base_dirs = [
    Path("C:/Users/sangi/Downloads"),
    Path("C:/Users/sangi/Desktop"),
    Path("C:/Users/sangi/Documents"),
    Path("C:/Users/sangi/OneDrive"),
    Path("C:/Users/sangi"),
]

print("=== 검색 시작 ===")
matched_files = []

for b in base_dirs:
    if not b.exists():
        continue
    print(f"Checking {b}...")
    for root, dirs, files in os.walk(b):
        # 제외할 디렉토리
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", "env", "AppData", "Local", "Cache"]]
        for f in files:
            if f.endswith((".py", ".log", ".txt", ".json", ".env")):
                fpath = Path(root) / f
                try:
                    # 크기가 너무 크면 10MB 이하만
                    if fpath.stat().st_size > 10 * 1024 * 1024:
                        continue
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                    for w in target_words:
                        if w in text:
                            print(f"[FOUND] {w} -> {fpath}")
                            matched_files.append((w, str(fpath)))
                            break
                except Exception:
                    pass

print("=== 검색 완료 ===")
print(f"총 {len(matched_files)}건 발견")
