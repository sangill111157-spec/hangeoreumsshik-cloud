# -*- coding: utf-8 -*-
import sys, os, time, json, urllib.request, statistics
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# [A] 7개 모듈 개별 소요시간 계측 (python 내부 직접 호출)
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')

from app.services.stock_data import StockDataService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.news_sentiment import NewsSentimentService
from app.services.options_flow import OptionsFlowService
from app.services.darkpool_tracker import DarkPoolTracker
from app.services.institutional_tracker import InstitutionalTracker
from app.services.fear_greed import FearGreedIndex
from app.services.edgar_tracker import EdgarTracker
from app.services.multi_strategy import MultiStrategyEngine
from app.services.investor_analysis import InvestorAnalysisEngine

print("==================================================")
print("A. MODULE EXECUTION TIME BENCHMARK (Individual)")
print("==================================================")
symbol = "NVDA"

def time_fn(name, fn, *args, **kwargs):
    t0 = time.perf_counter()
    try:
        res = fn(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        print(f"  - {name:25s}: {elapsed:6.3f}s (Success)")
        return elapsed, res
    except Exception as e:
        elapsed = time.perf_counter() - t0
        print(f"  - {name:25s}: {elapsed:6.3f}s (Error: {e})")
        return elapsed, None

time_fn("StockDataService.get_stock_info", StockDataService().get_stock_info, symbol)
time_fn("TechnicalAnalysisService", TechnicalAnalysisService().analyze, symbol, "1y")
time_fn("NewsSentimentService", NewsSentimentService().analyze_news, symbol)
time_fn("OptionsFlowService", OptionsFlowService().analyze_options_flow, symbol)
time_fn("DarkPoolTracker", DarkPoolTracker().analyze_darkpool, symbol)
time_fn("InstitutionalTracker", InstitutionalTracker().get_institutional_holdings, symbol)
time_fn("FearGreedIndex", FearGreedIndex().get_fear_greed_index)
time_fn("EdgarTracker", EdgarTracker().get_company_filings, symbol)
time_fn("MultiStrategyEngine", MultiStrategyEngine().calculate_all_pods, symbol)
time_fn("InvestorAnalysisEngine", InvestorAnalysisEngine().analyze, symbol, "1y")

print("\n==================================================")
print("B. LIVE /signal ENDPOINT 3-RUN TEST (With 60s gap / timestamps)")
print("==================================================")
def fetch_signal(sym="NVDA"):
    url = f"http://127.0.0.1:8000/api/stock/{sym}/signal"
    t0 = time.perf_counter()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        elapsed = time.perf_counter() - t0
        data = json.loads(resp.read().decode('utf-8'))
        return elapsed, data

# First fetch
e1, d1 = fetch_signal()
print(f"Run 1: {e1:6.3f}s | master_score: {d1.get('master_score')} | coverage: {d1.get('coverage')} | components count: {len(d1.get('components', []))}")
print(f"       timestamp: {d1.get('components', [{}])[0].get('timestamp', 'N/A')}")

# Second fetch (immediate)
e2, d2 = fetch_signal()
print(f"Run 2: {e2:6.3f}s | master_score: {d2.get('master_score')} | coverage: {d2.get('coverage')}")

# Third fetch (after 3s)
time.sleep(3)
e3, d3 = fetch_signal()
print(f"Run 3: {e3:6.3f}s | master_score: {d3.get('master_score')} | coverage: {d3.get('coverage')}")

print("\n==================================================")
print("C. FAULT INJECTION: COMPONENTS RAW JSON COMPARISON")
print("==================================================")
print("--- [CONTROL RUN (Normal)] ---")
print(json.dumps({
    "master_score": d1.get("master_score"),
    "raw_score": d1.get("raw_score"),
    "coverage": d1.get("coverage"),
    "available_module_count": d1.get("available_module_count"),
    "unavailable_modules": d1.get("unavailable_modules"),
    "components": d1.get("components")
}, indent=2, ensure_ascii=False))

# Fault injection on Darkpool
from app.services.master_signal import MasterSignalEngine
ms_engine = MasterSignalEngine()
# Mock normal inputs
from test_controlled_fault import get_mock_payload
