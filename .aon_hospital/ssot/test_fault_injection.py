# -*- coding: utf-8 -*-
import sys, json

# Import master_signal service directly
sys.path.append(r'C:\trading\package\nvda_trading_system\backend')
from app.services.master_signal import MasterSignalEngine, ComponentScore

engine = MasterSignalEngine()

# Dummy sub-module results matching live NVDA
investor_analysis = {"overall_confidence": 70, "overall_signal": "BUY", "bull_count": 2, "bear_count": 0}
pod_signals = [
    {"signal": "HOLD", "confidence": 62},
    {"signal": "HOLD", "confidence": 40},
    {"signal": "HOLD", "confidence": 45},
    {"signal": "STRONG_BUY", "confidence": 70},
    {"signal": "BUY", "confidence": 70}
]
technical = {"overall_signal": "BUY", "confidence": 75, "trend": "BULLISH", "rsi": {"value": 60}}
llm_news = {"news_composite_score": 53.0, "sentiment_label": "BULLISH", "total_news_analyzed": 20}
institutional = {"institutional_score": 50}
options_flow = {"available": True, "options_composite_score": 70.0, "options_signal": "STRONG_BUY"}
darkpool = {"available": True, "darkpool_composite_score": 40.0, "darkpool_signal": "SELL"}
events = {"upcoming_events": []}
correlation = {"sector_momentum_score": 50, "macro_indicator_score": 50}

print("=== 1. Test Partial Failure (darkpool fail) ===")
# Inject darkpool failure by setting darkpool available=False / unavailable
res_darkpool_fail = engine.calculate_final_master_signal(
    symbol="NVDA",
    investor_analysis=investor_analysis,
    pod_signals=pod_signals,
    technical=technical,
    llm_news=llm_news,
    institutional=institutional,
    options_flow=options_flow,
    darkpool={"available": False},  # darkpool failed
    events=events,
    correlation=correlation,
    pod_composite_signal="HOLD"
)
print("coverage:", res_darkpool_fail.coverage)
print("available_module_count:", res_darkpool_fail.available_module_count)
print("unavailable_modules:", res_darkpool_fail.unavailable_modules)
print("master_score:", res_darkpool_fail.master_score)
print("weights_used:", res_darkpool_fail.weights_used)

print("\n=== 2. Test Below-Threshold Failure (investor + pod fail -> coverage 55%) ===")
res_sub_threshold = engine.calculate_final_master_signal(
    symbol="NVDA",
    investor_analysis={},  # unavailable
    pod_signals=[],        # unavailable
    technical=technical,
    llm_news=llm_news,
    institutional=institutional,
    options_flow=options_flow,
    darkpool=darkpool,
    events=events,
    correlation=correlation,
    pod_composite_signal="HOLD"
)
print("coverage:", res_sub_threshold.coverage)
print("available_module_count:", res_sub_threshold.available_module_count)
print("unavailable_modules:", res_sub_threshold.unavailable_modules)
print("signal:", res_sub_threshold.signal)
print("master_score:", res_sub_threshold.master_score)
print("raw_score:", res_sub_threshold.raw_score)

# 3. Check signal_map definition
print("\n=== 3. signal_map definition in master_signal.py ===")
with open(r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py', 'r', encoding='utf-8') as f:
    ms_lines = f.readlines()
for i in range(175, 195):
    print(f"Line {i+1:4d}: {ms_lines[i]}", end='')
