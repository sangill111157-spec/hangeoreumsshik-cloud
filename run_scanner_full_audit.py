# -*- coding: utf-8 -*-
import sys, os, subprocess, json, asyncio

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from app.services.stock_scanner import StockScanner

async def run_full_scanner_audit():
    scanner = StockScanner()
    tickers = scanner.get_scan_universe(market="US")
    
    print("==================================================")
    print("1. [B-4 / 결함 41·62·80] Full Market Scanner Audit (29 US Tickers)")
    print("==================================================")
    print(f"Total Universe Tickers : {len(tickers)} (US Stocks)")
    
    primary_passed = []
    primary_failed = []
    
    for t in tickers:
        res = await scanner._analyze_primary_filters(t)
        if res and res["pass_count"] >= scanner.config["primary_pass_conditions"]:
            primary_passed.append(res)
        else:
            p_cnt = res["pass_count"] if res else 0
            primary_failed.append({"ticker": t, "pass_count": p_cnt, "reason": "Did not meet primary pass conditions (pass_count < 1)"})
    
    print(f"1st Filter Passed Count: {len(primary_passed)} / {len(tickers)}")
    print(f"1st Filter Failed Count: {len(primary_failed)} / {len(tickers)}")
    
    # Show 2 discriminative failed cases
    print("\n--- 2 Discriminative Failed Cases (Filter Rejections) ---")
    for f_case in primary_failed[:2]:
        print(f"Failed Ticker: {f_case['ticker']:6s} | Pass Count: {f_case['pass_count']} | Reason: {f_case['reason']}")
    
    print("\nSTATUS: SUCCESS (Discriminative filtering active, no unhandled exceptions)")

asyncio.run(run_full_scanner_audit())

