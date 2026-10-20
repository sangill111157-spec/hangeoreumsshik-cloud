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

# =============================================================================
# EXPERIMENT 1: ALL EXTERNAL APIS FAIL / THROW EXCEPTIONS (FULL FALLBACK MATRIX)
# =============================================================================
print("=============================================================================")
print("EXPERIMENT 1: ALL EXTERNAL APIS FAIL (FULL NETWORK / DATA EXCEPTION)")
print("=============================================================================")

fallback_input = {
    "investor_analysis": {"available": False, "overall_signal": "HOLD", "overall_confidence": 50, "bull_count": 0, "bear_count": 0},
    "pod_signals": [],  # no pods available
    "pod_composite_signal": "HOLD",
    "technical": {"available": False, "overall_signal": "HOLD", "confidence": 50},
    "llm_news": {"available": False, "news_composite_score": 50.0, "news_signal": "HOLD", "sentiment_label": "HOLD", "total_news_analyzed": 0},
    "institutional": {"available": False, "institutional_ownership_pct": None},
    "options_flow": {"available": False, "options_composite_score": 50.0, "options_signal": "HOLD"},
    "darkpool": {"available": False, "darkpool_composite_score": 50.0, "darkpool_signal": "HOLD"},
    "events": {"available": False, "upcoming_events": [], "earnings_season": False, "has_regulatory_event": False},
    "correlation": {"available": False, "macro_score": 50.0},
    "symbol": "NVDA",
    "stock_price": 214.72,
    "account_balance": 100000.0
}

res_fallback = engine.calculate_final_master_signal(**fallback_input)
print(f"Fallback Coverage: {res_fallback.coverage}")
print(f"Fallback Signal: {res_fallback.signal} ({res_fallback.signal_ko})")
print(f"Fallback Master Score: {res_fallback.master_score}")
print(f"Fallback Raw Score: {res_fallback.raw_score}")
print(f"Unavailable Modules ({len(res_fallback.unavailable_modules)}): {res_fallback.unavailable_modules}")
print("\nComponent Breakdown under Full Fallback:")
for comp in res_fallback.components:
    print(f" - {comp.name}: score={comp.score}, signal={comp.signal}, confidence={comp.confidence}")


# =============================================================================
# EXPERIMENT 2: FORCED BUY SIGNAL -> SIZING & CEILING PATH AUDIT MATRIX
# =============================================================================
print("\n=============================================================================")
print("EXPERIMENT 2: FORCED BUY SIGNAL -> SIZING & CEILING PATH AUDIT MATRIX")
print("=============================================================================")

# Strong bullish inputs across all 7 modules
bull_input_template = {
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
    "symbol": "NVDA"
}

# Test grid across different account balances and stock prices
test_cases = [
    {"balance": 10000.0, "price": 100.0},
    {"balance": 10000.0, "price": 214.72},
    {"balance": 10000.0, "price": 500.0},
    {"balance": 100000.0, "price": 100.0},
    {"balance": 100000.0, "price": 214.72},
    {"balance": 100000.0, "price": 500.0},
    {"balance": 1000000.0, "price": 100.0},
    {"balance": 1000000.0, "price": 214.72},
    {"balance": 1000000.0, "price": 500.0},
]

print(f"{'Balance':>10} | {'Price':>8} | {'Score':>6} | {'Signal':>10} | {'Conf':>5} | {'Kelly%':>7} | {'Shares':>7} | {'Position$':>11} | {'Acct%':>6} | {'StopLoss':>8} | {'CeilingReason'}")
print("-" * 115)

for tc in test_cases:
    inp = bull_input_template.copy()
    inp["account_balance"] = tc["balance"]
    inp["stock_price"] = tc["price"]
    
    res = engine.calculate_final_master_signal(**inp)
    k = res.kelly
    print(f"${tc['balance']:>9,.0f} | ${tc['price']:>7.2f} | {res.master_score:>6.2f} | {res.signal:>10} | {res.confidence:>5} | {k.kelly_percentage:>6.2f}% | {k.recommended_shares:>7} | ${k.position_value:>10,.2f} | {k.account_percentage:>5.2f}% | ${k.stop_loss:>7.2f} | {getattr(k, 'ceiling_reason', 'N/A')}")
