# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [결함 14 확장] Market scanner code and scan_history/2026-08-21_us.json")
print("==================================================")
out_scan_src, _ = run_cmd('git grep -n -E "final_candidates|master_score" app/services/*scan*.py app/services/*market*.py app/api/routes/*scan*.py')
print("Scanner filter source lines:\n", out_scan_src)

# Check 2026-08-21_us.json full content
json_path = os.path.join(backend_dir, r'data\scan_history\2026-08-21_us.json')
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        print("\n--- data/scan_history/2026-08-21_us.json full content ---")
        print(f.read())

print("\n==================================================")
print("2. [B-5] git show ed5c03d --stat and diff")
print("==================================================")
out_ed5, _ = run_cmd('git show ed5c03d --stat')
print("--- git show ed5c03d --stat ---")
print(out_ed5)

out_ed5_diff, _ = run_cmd('git show ed5c03d -p')
print("--- git show ed5c03d diff ---")
print(out_ed5_diff)

print("\n==================================================")
print("3. [B-3] git show 9d55dec -- src/App.tsx diff")
print("==================================================")
out_9d5, _ = run_cmd('git show 9d55dec -- src/App.tsx', cwd=frontend_dir)
print("--- git show 9d55dec -- src/App.tsx ---")
print(out_9d5)

# Check all 4 lines (973, 1973, 2032, 2223) in src/App.tsx
with open(os.path.join(frontend_dir, r'src\App.tsx'), 'r', encoding='utf-8') as f:
    app_lines = f.readlines()
print("\n--- Verified Lines in src/App.tsx (973, 1973, 2032, 2223) ---")
for idx in [972, 1972, 2031, 2222]:
    if idx < len(app_lines):
        print(f"Line {idx+1:4d}: {app_lines[idx].rstrip()}")

print("\n==================================================")
print("4. [B-4] LLM News & Options Flow Blocking Removal PoC (3 runs)")
print("==================================================")
from app.services.llm_analyzer import LLMNewsAnalyzer
from app.services.options_flow import OptionsFlowEngine

async def run_blocking_removal_poc():
    ticker = "NVDA"
    for r in range(1, 4):
        t0 = time.perf_counter()
        llm = LLMNewsAnalyzer(ticker=ticker)
        # to_thread test
        await asyncio.to_thread(llm.analyze, ticker)
        dt_llm = time.perf_counter() - t0
        
        t0 = time.perf_counter()
        opt = OptionsFlowEngine(ticker=ticker)
        await asyncio.to_thread(opt.analyze, ticker)
        dt_opt = time.perf_counter() - t0
        print(f"PoC Run {r}: LLM News (to_thread)={dt_llm:5.3f}s | Options Flow (to_thread)={dt_opt:5.3f}s")

asyncio.run(run_blocking_removal_poc())

print("\n==================================================")
print("5. [B-1] 14-Digit Re-Verification on ed5c03d")
print("==================================================")
from app.services.master_signal import MasterSignalEngine
mock_data = {
    "investor_analysis": {"overall_signal": "BUY", "overall_confidence": 70, "bull_count": 3, "bear_count": 1},
    "pod_signals": [
        {"pod_name": "growth", "signal": "BUY", "confidence": 70, "score": 30.0},
        {"pod_name": "value", "signal": "STRONG_BUY", "confidence": 80, "score": 75.0},
        {"pod_name": "momentum", "signal": "HOLD", "confidence": 50, "score": 10.0},
        {"pod_name": "quality", "signal": "BUY", "confidence": 75, "score": 40.0},
        {"pod_name": "safety", "signal": "HOLD", "confidence": 40, "score": -10.0}
    ],
    "technical": {"overall_signal": "buy", "confidence": 75, "trend": "BULLISH", "rsi": {"value": 58}},
    "llm_news": {"sentiment_label": "NEUTRAL", "news_composite_score": 50.0, "total_news_analyzed": 5},
    "institutional": {"available": True},
    "options_flow": {"options_signal": "strong_buy", "options_composite_score": 70.0, "available": True},
    "darkpool": {"darkpool_signal": "sell", "darkpool_composite_score": 40.0, "available": True},
    "events": {},
    "correlation": {},
    "symbol": "NVDA"
}
engine = MasterSignalEngine()
res = engine.calculate_final_master_signal(**mock_data)
print(f"ed5c03d Re-Verification:")
print(f"  raw_score   : {res.raw_score:.14f}")
print(f"  master_score: {res.master_score:.14f}")
print(f"  signal      : {res.signal}")

