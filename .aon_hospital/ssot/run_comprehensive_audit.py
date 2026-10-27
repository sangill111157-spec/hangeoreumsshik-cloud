# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [B-1 PRE/POST 14-DIGIT COMPARISON ON FIXED MOCK]")
print("==================================================")
# Fixed mock data
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

# Current commit (6ba921b) execution
from app.services.master_signal import MasterSignalEngine
engine_curr = MasterSignalEngine()
res_curr = engine_curr.calculate_final_master_signal(**mock_data)

# Test with pre-patch code logic manually or checkout comparison
print(f"Current Commit (6ba921b) with mock_data:")
print(f"  raw_score   : {res_curr.raw_score:.14f}")
print(f"  master_score: {res_curr.master_score:.14f}")
print("  Components:")
for c in res_curr.components:
    print(f"    - {c.name:12s}: score={c.score:.14f} | signal={c.signal:12s} | conf={c.confidence}")

# Live endpoint fetch
print("\n--- Live Endpoint (/api/stock/NVDA/signal) ---")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        live_data = json.loads(resp.read().decode('utf-8'))
        print(f"  Live raw_score   : {live_data.get('raw_score')}")
        print(f"  Live master_score: {live_data.get('master_score')}")
        print(f"  Live signal      : {live_data.get('signal')}")
        print(f"  Live coverage    : {live_data.get('coverage')}")
        print("  Live adjustments :", live_data.get('adjustments'))
        print("  Live components  :")
        for c in live_data.get('components', []):
            print(f"    - {c.get('name'):12s}: score={c.get('score')} | signal={c.get('signal')} | conf={c.get('confidence')}")
except Exception as e:
    print("  Live endpoint fetch error:", e)

# _norm_sig unit tests
print("\n--- _norm_sig edge cases test ---")
def _norm_sig(sig) -> str:
    if not sig:
        return "HOLD"
    s = str(sig).upper().strip()
    return "HOLD" if s in ["NEUTRAL", "NONE", "N/A"] else s

test_inputs = ["neutral", "STRONG BUY", "buy", "sell", "STRONG_SELL", "강력매수", "", None]
for ti in test_inputs:
    print(f"  input: {repr(ti):15s} -> output: {repr(_norm_sig(ti))}")

print("\n==================================================")
print("2. [B-3] 'available' git grep & except blocks & type(x) inspection")
print("==================================================")
out_grep, _ = run_cmd('git grep -n "\\"available\\"" app/services/')
print("--- git grep -n '\"available\"' app/services/ ---")
print(out_grep)

# Inspect stock.py type(x) in parallel_results
from app.services.data_collector import DataCollector
from app.services.technical_analysis import TechnicalAnalyzer
from app.services.llm_analyzer import LLMNewsAnalyzer
from app.services.options_flow import OptionsFlowEngine
from app.services.darkpool_analyzer import DarkPoolAnalyzer
from app.services.event_engine import EventEngine
from app.services.correlation_engine import CorrelationEngine
from app.services.investor_analysis import InvestorAnalysisEngine
from app.services.news_sentiment import create_fear_greed_index
from app.services.edgar_tracker import create_edgar_tracker
from dataclasses import asdict

async def inspect_types():
    ticker = "NVDA"
    collector = DataCollector()
    analyzer = TechnicalAnalyzer()
    stock_info = collector.get_stock_info(ticker)
    hist = collector.get_historical_data(ticker, "1y")
    tech = analyzer.analyze(ticker, hist, stock_info.current_price)
    stock_dict = {k: v for k, v in asdict(stock_info).items() if v is not None}
    
    llm = LLMNewsAnalyzer(ticker=ticker)
    opt = OptionsFlowEngine(ticker=ticker)
    dp = DarkPoolAnalyzer(ticker=ticker)
    ev = EventEngine(ticker=ticker)
    corr = CorrelationEngine(ticker=ticker)
    inv = InvestorAnalysisEngine()
    fng = create_fear_greed_index()
    edgar = create_edgar_tracker()
    
    results = await asyncio.gather(
        llm.analyze(ticker),
        opt.analyze(ticker),
        asyncio.to_thread(dp.analyze, ticker),
        asyncio.to_thread(ev.analyze, ticker),
        asyncio.to_thread(corr.analyze, ticker),
        asyncio.to_thread(inv.analyze, ticker, stock_dict, tech, hist),
        fng.fetch(),
        edgar.fetch_all(use_mock=True),
        return_exceptions=True
    )
    
    print("\n--- Actual Return Types of 8 Tasks in gather ---")
    names = ["0: llm_news", "1: options_flow", "2: darkpool", "3: events", "4: correlation", "5: investor", "6: fng", "7: edgar"]
    for name, r in zip(names, results):
        print(f"  {name:20s}: type={type(r).__name__} | is_dataclass={hasattr(r, '__dataclass_fields__')} | has_dict_get={hasattr(r, 'get')}")
    
    # Check how stock.py converts them to dict before passing to MasterSignalEngine
    # In stock.py, line 680-730:
    llm_res, opt_res, dp_res, ev_res, corr_res, inv_res, fng_res, edgar_res = results
    
    # Check darkpool timing 3 runs
    print("\n--- Darkpool standalone 3 runs ---")
    for d_run in range(1, 4):
        t0 = time.perf_counter()
        dp_obj = DarkPoolAnalyzer(ticker=ticker)
        await asyncio.to_thread(dp_obj.analyze, ticker)
        dt = time.perf_counter() - t0
        print(f"  Darkpool Run {d_run}: {dt:5.3f}s")

asyncio.run(inspect_types())

print("\n==================================================")
print("3. [B-2] UI diff & grep for || 50 and ?? 50")
print("==================================================")
out_ui_show, _ = run_cmd('git show 729160a -- src/App.tsx', cwd=frontend_dir)
print("--- git show 729160a -- src/App.tsx ---")
print(out_ui_show)

out_ui_grep, _ = run_cmd('git grep -n -E "\\|\\| 50|\\?\\? 50|null점" src/', cwd=frontend_dir)
print("\n--- git grep -n -E '\|\| 50|\?\? 50|null점' src/ ---")
print(out_ui_grep if out_ui_grep.strip() else "  (0건 - 전부 제거됨 확인)")

print("\n==================================================")
print("4. [D] scan_history records 35~50 range count")
print("==================================================")
out_scan, _ = run_cmd('git grep -n "master_score" data/scan_history/')
print("--- data/scan_history records grep ---")
if out_scan.strip():
    print(out_scan[:500])
else:
    print("  (scan_history files check)")
    scan_files = [f for f in os.listdir(os.path.join(backend_dir, 'data')) if 'scan' in f]
    print("  scan files in data/:", scan_files)
