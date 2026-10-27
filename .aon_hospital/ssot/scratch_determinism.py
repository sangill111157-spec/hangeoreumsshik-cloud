import sys, os, json, dataclasses
sys.stdout.reconfigure(encoding='utf-8')
backend = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend)

os.environ['KIS_APP_KEY'] = 'mock'
os.environ['KIS_APP_SECRET'] = 'mock'
os.environ['SECRET_KEY'] = 'mock'
os.environ['ENABLE_LIVE_ORDERS'] = 'False'

from app.services.master_signal import create_master_engine, MasterSignalEngine, BASE_WEIGHTS

# 1. Determinism Test
print("=== 1. DETERMINISM TEST (3 CONSECUTIVE CALLS WITH FIXED INPUT) ===")
engine = create_master_engine("NVDA")

fixed_input = {
    "investor_analysis": {"score": 60.0, "overall_signal": "HOLD", "confidence": 70, "available": True},
    "pod_signals": [
        {"pod_name": "Momentum Pod", "signal": "HOLD", "confidence": 52, "score": 5.0, "available": True},
        {"pod_name": "Value Pod", "signal": "HOLD", "confidence": 40, "score": 0.0, "available": True},
        {"pod_name": "Sentiment Pod", "signal": "HOLD", "confidence": 45, "score": -20.0, "available": True},
        {"pod_name": "Institutional Pod", "signal": "STRONG_BUY", "confidence": 70, "score": 80.0, "available": True},
        {"pod_name": "Technical Pod", "signal": "BUY", "confidence": 70, "score": 50.0, "available": True}
    ],
    "pod_composite_signal": "HOLD",
    "technical": {"trend": "neutral", "rsi": {"value": 50}, "macd": {"histogram": 0}, "confidence": 50, "available": True},
    "llm_news": {"news_composite_score": 53.0, "news_signal": "HOLD", "confidence": 50, "available": True},
    "institutional": {"available": True, "filings_count": 5, "agreement_ratio": 0.5},
    "options_flow": {"options_composite_score": 70.0, "options_signal": "BUY", "confidence": 85, "available": True},
    "darkpool": {"darkpool_composite_score": 40.0, "darkpool_signal": "HOLD", "confidence": 60, "available": True},
    "events": {"upcoming_events": [], "earnings_season": False, "has_regulatory_event": False, "available": False},
    "correlation": {"available": False, "macro_score": 50.0},
    "symbol": "NVDA",
    "stock_price": 214.72,
    "account_balance": 100000.0
}

results = []
for i in range(3):
    res = engine.calculate_final_master_signal(**fixed_input)
    d = dataclasses.asdict(res)
    # Exclude timestamp for bitwise/exact dict comparison
    d_no_time = {k: v for k, v in d.items() if k != 'timestamp'}
    results.append(d_no_time)
    print(f"Run {i+1}: master_score={res.master_score}, raw_score={res.raw_score}, signal={res.signal}, confidence={res.confidence}, shares={res.kelly.recommended_shares}")

is_identical = (results[0] == results[1] == results[2])
print(f"\nExact Determinism Check: {'PASSED (Bitwise Identical)' if is_identical else 'FAILED'}")

# 2. Check Backtester import in master_signal
print("\n=== 2. BACKTESTER IMPORT CHECK IN MASTER_SIGNAL.PY ===")
with open(os.path.join(backend, 'app/services/master_signal.py'), 'r', encoding='utf-8') as f:
    ms_code = f.read()

has_bt_import = 'backtester' in ms_code
print(f"Does master_signal.py import or reference backtester?: {has_bt_import}")
