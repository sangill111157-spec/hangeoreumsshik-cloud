import sys, os, json, dataclasses
sys.stdout.reconfigure(encoding='utf-8')
backend = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend)

os.environ['KIS_APP_KEY'] = 'mock'
os.environ['KIS_APP_SECRET'] = 'mock'
os.environ['SECRET_KEY'] = 'mock'
os.environ['ENABLE_LIVE_ORDERS'] = 'False'

from app.services.master_signal import create_master_engine, MasterSignalEngine, BASE_WEIGHTS

engine = create_master_engine("NVDA")

# Base bullish input
base_bull_input = {
    "investor_analysis": {"score": 85.0, "overall_signal": "STRONG_BUY", "overall_confidence": 85, "available": True},
    "pod_signals": [
        {"pod_name": "Momentum Pod", "signal": "STRONG_BUY", "confidence": 85, "score": 85.0, "available": True},
        {"pod_name": "Value Pod", "signal": "BUY", "confidence": 75, "score": 75.0, "available": True},
        {"pod_name": "Sentiment Pod", "signal": "BUY", "confidence": 80, "score": 80.0, "available": True},
        {"pod_name": "Institutional Pod", "signal": "STRONG_BUY", "confidence": 90, "score": 90.0, "available": True},
        {"pod_name": "Technical Pod", "signal": "STRONG_BUY", "confidence": 85, "score": 85.0, "available": True}
    ],
    "pod_composite_signal": "STRONG_BUY",
    "technical": {"trend": "strong_uptrend", "rsi": {"value": 25}, "macd": {"histogram": 1.5}, "confidence": 85, "available": True},
    "llm_news": {"news_composite_score": 82.0, "news_signal": "STRONG_BUY", "confidence": 85, "available": True},
    "institutional": {"available": True, "nvda": {"investors": [{"transaction_type": "NEW"}, {"transaction_type": "INCREASED"}]}, "filings_count": 8, "agreement_ratio": 0.8},
    "options_flow": {"options_composite_score": 88.0, "options_signal": "STRONG_BUY", "confidence": 90, "available": True},
    "darkpool": {"darkpool_composite_score": 80.0, "darkpool_signal": "STRONG_BUY", "confidence": 75, "available": True},
    "events": {"upcoming_events": [], "earnings_season": False, "has_regulatory_event": False, "available": False},
    "correlation": {"available": False, "macro_score": 50.0},
    "symbol": "NVDA",
    "stock_price": 214.72,
    "account_balance": 100000.0
}

# =============================================================================
# PART 1: 7x1 DROP-ONE MATRIX EXPERIMENT
# =============================================================================
print("=============================================================================")
print("PART 1: 7x1 DROP-ONE MATRIX EXPERIMENT (ONE MODULE DISABLED AT A TIME)")
print("=============================================================================")

modules = [
    ("investor_analysis", "5대 투자자 (20%)"),
    ("pod_signals", "멀티전략 Pod (20%)"),
    ("technical", "기술적 분석 (15%)"),
    ("options_flow", "옵션 플로우 (15%)"),
    ("llm_news", "AI 뉴스 (12%)"),
    ("darkpool", "다크풀 (10%)"),
    ("institutional", "기관/13F (8%)")
]

print(f"{'Dropped Module':<22} | {'Coverage':>8} | {'Score':>6} | {'Signal':>10} | {'Unavail Modules':<25} | {'Renormalized Weights'}")
print("-" * 115)

for mod_key, mod_name in modules:
    inp = json.loads(json.dumps(base_bull_input))
    if mod_key == "pod_signals":
        inp["pod_signals"] = []
    elif mod_key == "institutional":
        inp["institutional"] = {"available": False}
    else:
        inp[mod_key]["available"] = False

    res = engine.calculate_final_master_signal(**inp)
    w_str = ", ".join(f"{k[:3]}:{v:.2f}" for k, v in res.weights_used.items())
    score_str = f"{res.master_score:.2f}" if res.master_score is not None else "None"
    print(f"{mod_name:<22} | {res.coverage*100:>7.1f}% | {score_str:>6} | {res.signal:>10} | {str(res.unavailable_modules):<25} | {w_str}")

# Also test dropping top two heaviest modules: Investor (20%) + Pods (20%)
print("\n--- Special Test: Dropping TOP TWO heaviest modules (Investor 20% + Pods 20% = 40% loss) ---")
inp_two = json.loads(json.dumps(base_bull_input))
inp_two["investor_analysis"]["available"] = False
inp_two["pod_signals"] = []
res_two = engine.calculate_final_master_signal(**inp_two)
print(f"Top 2 Dropped (40% loss) | Coverage: {res_two.coverage*100:.1f}% | Score: {res_two.master_score} | Signal: {res_two.signal} | Unavailable: {res_two.unavailable_modules}")
print(f"Weights used: {res_two.weights_used}")

# Dropping 3 modules (loss > 40%, e.g. Investor 20% + Pods 20% + Tech 15% = 55% loss)
print("\n--- Special Test: Dropping 3 modules (55% loss, coverage = 45% < 60% threshold) ---")
inp_three = json.loads(json.dumps(base_bull_input))
inp_three["investor_analysis"]["available"] = False
inp_three["pod_signals"] = []
inp_three["technical"]["available"] = False
res_three = engine.calculate_final_master_signal(**inp_three)
print(f"3 Dropped (55% loss)     | Coverage: {res_three.coverage*100:.1f}% | Score: {res_three.master_score} | Signal: {res_three.signal} | Unavailable: {res_three.unavailable_modules}")
