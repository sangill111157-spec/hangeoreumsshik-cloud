# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import re
import json

base_path = Path(r"C:\trading\package\nvda_trading_system\backend")

def analyze_trading_core():
    print("=== 1. 최신 로그 tail 200줄 분석 ===")
    app_log = base_path / "logs" / "app.log"
    server_log = base_path / "logs" / "server_20261013_2028.log"
    
    for lfile in [server_log, app_log]:
        if lfile.exists():
            print(f"\n--- {lfile.name} 최근 로그 분석 ---")
            lines = lfile.read_text(encoding="utf-8", errors="ignore").splitlines()
            print(f"총 {len(lines)}줄")
            # 스캔, 주문, 에러 관련 최근 로그 출력
            keywords = ["장중 스캔", "발굴 종목", "107,246", "스케줄러 가동", "ACCOUNT_STATE_FAIL", "US_BALANCE_INQUIRE_NASD", "BUY", "주문"]
            found = [line for line in lines if any(k in line for k in keywords)]
            print(f"주요 키워드 일치 로그: {len(found)}건")
            for line in found[-15:]:
                print("  ", line)

    print("\n=== 2. 스케줄러 등록 코드 분석 (7대 작업 목록 및 중복 가동 원인) ===")
    # run_scheduler.py 및 app/services/scheduler.py 확인
    for sc_candidate in [base_path / "run_scheduler.py", base_path / "app" / "services" / "scheduler_service.py", base_path / "app" / "services" / "scheduler.py"]:
        if sc_candidate.exists():
            print(f"\n📄 {sc_candidate.name} 분석:")
            text = sc_candidate.read_text(encoding="utf-8", errors="ignore")
            # 7개 작업 등록 관련 부분 찾기
            lines = text.splitlines()
            for idx, l in enumerate(lines):
                if any(w in l for w in ["자동화 작업", "add_job", "CronTrigger", "scheduler.start", "7개"]):
                    print(f"  [{idx+1}] {l.strip()}")

    print("\n=== 3. 자동 매매 및 스캔 후 BUY 진입 로직 분석 (왜 거래 0회인가?) ===")
    # auto_trader.py 또는 stock_scanner.py 검색
    app_dir = base_path / "app"
    for py_file in app_dir.rglob("*.py"):
        if any(k in py_file.name for k in ["auto_trader", "trader", "order", "scanner"]):
            print(f"\n📄 {py_file.relative_to(app_dir)} 분석:")
            text = py_file.read_text(encoding="utf-8", errors="ignore")
            for idx, l in enumerate(text.splitlines()):
                if any(k in l for k in ["threshold", "min_score", "DRY_RUN", "is_paper", "place_order", "buy_signal", "execute_order"]):
                    print(f"  [{idx+1}] {l.strip()[:100]}")

if __name__ == "__main__":
    analyze_trading_core()
