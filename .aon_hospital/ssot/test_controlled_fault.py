# -*- coding: utf-8 -*-
import sys
sys.path.append(r'C:\trading\package\nvda_trading_system\backend')
from app.services.master_signal import MasterSignalEngine

engine = MasterSignalEngine()

# Fixed controlled snapshot data
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

print("=== 1. Controlled Run: All 7 Modules Available ===")
r_all = engine.calculate_final_master_signal(
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
print("master_score:", r_all.master_score)
print("coverage:", r_all.coverage)
print("available_module_count:", r_all.available_module_count)
print("unavailable_modules:", r_all.unavailable_modules)
for c in r_all.components:
    print(f"  {c.name:12s}: score={c.score:6.2f}, weight={r_all.weights_used.get(c.name, 0):.4f}")

print("\n=== 2. Controlled Run: Darkpool Failed (available=False) ===")
r_darkpool_fail = engine.calculate_final_master_signal(
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
print("master_score:", r_darkpool_fail.master_score)
print("coverage:", r_darkpool_fail.coverage)
print("available_module_count:", r_darkpool_fail.available_module_count)
print("unavailable_modules:", r_darkpool_fail.unavailable_modules)
for c in r_darkpool_fail.components:
    print(f"  {c.name:12s}: score={c.score:6.2f}, weight={r_darkpool_fail.weights_used.get(c.name, 0):.4f}")
print("Expected mathematical score: (61.5185 - 40 * 0.10) / 0.90 = 63.9094 -> 63.91")
