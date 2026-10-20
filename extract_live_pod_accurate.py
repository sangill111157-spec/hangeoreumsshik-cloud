# -*- coding: utf-8 -*-
import asyncio, json, sys
sys.path.append(r'C:\trading\package\nvda_trading_system\backend')

from app.services.pod_manager import create_pod_manager, get_pod_manager
from app.services.news_sentiment import create_fear_greed_index, get_fear_greed_index
from app.services.edgar_tracker import create_edgar_tracker, get_edgar_tracker

async def run_pod():
    pod_mgr = get_pod_manager() or create_pod_manager()
    fng_service = get_fear_greed_index() or create_fear_greed_index()
    fng_data = await fng_service.fetch()
    fng_signal = fng_service.get_investment_signal(fng_data)
    edgar_tracker = get_edgar_tracker() or create_edgar_tracker()
    await edgar_tracker.fetch_all(use_mock=True)

    portfolio_data = {
        "nvda": {
            "investors": [
                {"Name": "Warren Buffett", "transaction_type": "INCREASED", "value": 8500000},
                {"Name": "Jim Simons", "transaction_type": "INCREASED", "value": 125000000}
            ]
        },
        "overlaps": edgar_tracker.get_overlapping_stocks(min_investors=2),
        "recent_buys": [
            {"ticker": b.ticker, "current_value": b.current_value, "transaction_type": b.transaction_type.value}
            for b in edgar_tracker.get_recent_buys(limit=5)
        ]
    }
    pod_data = {
        "stock_info": {"ticker": "NVDA", "current_price": 218.23},
        "technical": {
            "rsi": {"value": 72.0},
            "macd": {"histogram": 0.59},
            "trend": "NEUTRAL",
            "bollinger_bands": {"upper": 225.0, "middle": 215.0, "lower": 205.0},
            "moving_averages": {"ma_20": 210.0, "ma_50": 200.0, "ma_200": 180.0},
            "confidence": 75
        },
        "sentiment": {"overall_score": 0.06, "sentiment_label": "BULLISH"},
        "fear_greed": {"value": fng_data.value, "label": fng_data.label, "signal": fng_signal.get("signal", "HOLD")},
        "portfolio": portfolio_data
    }
    master_pod = await pod_mgr.analyze_all(pod_data)
    print("=== LIVE PodManager.analyze_all Raw Result ===")
    print("master_score:", master_pod.master_score)
    print("signal:", getattr(master_pod.signal, "value", master_pod.signal))
    print("confidence:", master_pod.confidence)
    print("\nIndividual 5 Pod Signals:")
    for s in master_pod.pod_signals:
        sig_val = getattr(s.signal, "value", s.signal)
        print(f"  pod_id: {s.pod_id:6s} | pod_name: {s.pod_name:18s} | signal: {sig_val:10s} | score: {s.score:6.1f} | confidence: {s.confidence}")

asyncio.run(run_pod())
