# -*- coding: utf-8 -*-
import sys, os, time, json, urllib.request, statistics
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')

from app.services.master_signal import MasterSignalEngine, BASE_WEIGHTS

print("==================================================")
print("1. FAULT INJECTION: CONTROL VS FAULT COMPONENTS RAW JSON")
print("==================================================")
engine = MasterSignalEngine()

# [1] Fixed Controlled Inputs matching the snapshot
investor_analysis = {"overall_confidence": 70, "overall_signal": "BUY", "bull_count": 2, "bear_count": 0}
pod_signals = [
    {"signal": "HOLD", "confidence": 62},
    {"signal": "HOLD", "confidence": 40},
    {"signal": "HOLD", "confidence": 45},
    {"signal": "STRONG_BUY", "confidence": 70},
    {"signal": "BUY", "confidence": 70}
]
technical = {"overall_signal": "BUY", "confidence": 75, "trend": "NEUTRAL", "rsi": {"value": 60}}
llm_news = {"news_composite_score": 53.0, "sentiment_label": "HOLD", "total_news_analyzed": 20}
institutional = {"institutional_score": 50, "available": True}
options_flow = {"available": True, "options_composite_score": 70.0, "options_signal": "STRONG_BUY"}
darkpool = {"available": True, "darkpool_composite_score": 40.0, "darkpool_signal": "SELL"}
events = {"upcoming_events": []}
correlation = {"sector_momentum_score": 50, "macro_indicator_score": 50}

# Control Run (All 7 available)
res_control = engine.calculate_final_master_signal(
    symbol="NVDA",
    investor_analysis=investor_analysis,
    pod_signals=pod_signals,
    technical=technical,
    llm_news=llm_news,
    institutional=institutional,
    options_flow=options_flow,
    darkpool=darkpool,
    events=events,
    correlation=correlation,
    pod_composite_signal="HOLD"
)

# Fault Run 1: Darkpool unavailable (available=False)
res_darkpool_fail = engine.calculate_final_master_signal(
    symbol="NVDA",
    investor_analysis=investor_analysis,
    pod_signals=pod_signals,
    technical=technical,
    llm_news=llm_news,
    institutional=institutional,
    options_flow=options_flow,
    darkpool={"available": False},
    events=events,
    correlation=correlation,
    pod_composite_signal="HOLD"
)

def format_res(r):
    return {
        "master_score": r.master_score,
        "raw_score": r.raw_score,
        "signal": r.signal,
        "confidence": r.confidence,
        "coverage": r.coverage,
        "available_module_count": r.available_module_count,
        "unavailable_modules": r.unavailable_modules,
        "weights_used": r.weights_used,
        "components": [
            {
                "name": c.name,
                "score": c.score,
                "signal": c.signal,
                "weight": r.weights_used.get(c.name, 0.0),
                "confidence": c.confidence
            }
            for c in r.components
        ]
    }

print("--- [CONTROL RUN RAW JSON] ---")
print(json.dumps(format_res(res_control), indent=2, ensure_ascii=False))

print("\n--- [DARKPOOL FAULT INJECTION RAW JSON] ---")
print(json.dumps(format_res(res_darkpool_fail), indent=2, ensure_ascii=False))

print("\n==================================================")
print("2. DEFECT 9 VERIFICATION (Fallback returns score 50 without available=False)")
print("==================================================")
# Fallback dict returned by fallback handler: {"options_composite_score": 50, "options_signal": "HOLD"}
options_fallback = {"options_composite_score": 50, "options_signal": "HOLD"}
res_defect9 = engine.calculate_final_master_signal(
    symbol="NVDA",
    investor_analysis=investor_analysis,
    pod_signals=pod_signals,
    technical=technical,
    llm_news=llm_news,
    institutional=institutional,
    options_flow=options_fallback, # Fallback dict!
    darkpool=darkpool,
    events=events,
    correlation=correlation,
    pod_composite_signal="HOLD"
)
print("Defect 9 Test Results:")
print("  options_flow input:", options_fallback)
print("  coverage:", res_defect9.coverage)
print("  available_module_count:", res_defect9.available_module_count)
print("  unavailable_modules:", res_defect9.unavailable_modules)
print("  options_flow component in result:", [c for c in res_defect9.components if c.name == "옵션 플로우"])

print("\n==================================================")
print("3. MODULE EXECUTION TIME (7 modules + F&G + EDGAR)")
print("==================================================")
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

symbol = "NVDA"
times = {}
def measure(name, fn, *args):
    t0 = time.perf_counter()
    try:
        fn(*args)
        elapsed = time.perf_counter() - t0
        times[name] = elapsed
        print(f"  {name:25s}: {elapsed:6.3f}s")
    except Exception as e:
        elapsed = time.perf_counter() - t0
        times[name] = elapsed
        print(f"  {name:25s}: {elapsed:6.3f}s (Error: {e})")

measure("StockDataService", StockDataService().get_stock_info, symbol)
measure("TechnicalAnalysis", TechnicalAnalysisService().analyze, symbol, "1y")
measure("NewsSentiment", NewsSentimentService().analyze_news, symbol)
measure("OptionsFlow", OptionsFlowService().analyze_options_flow, symbol)
measure("DarkPoolTracker", DarkPoolTracker().analyze_darkpool, symbol)
measure("InstitutionalTracker", InstitutionalTracker().get_institutional_holdings, symbol)
measure("FearGreedIndex", FearGreedIndex().get_fear_greed_index)
measure("EdgarTracker", EdgarTracker().get_company_filings, symbol)
measure("MultiStrategyEngine", MultiStrategyEngine().calculate_all_pods, symbol)
measure("InvestorAnalysis", InvestorAnalysisEngine().analyze, symbol, "1y")

print(f"\nSequential Total Sum of Times: {sum(times.values()):.3f}s")
print(f"Max Module Time (Bottleneck): {max(times.items(), key=lambda x: x[1])}")
