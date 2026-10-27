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
        "ticker": "NVDA",
        "stock_price": 218.23,
        "historical_data": None,
        "sentiment_data": {"overall_score": 0.06, "sentiment_label": "BULLISH"},
        "portfolio_data": portfolio_data,
        "market_trend": "BULLISH",
        "rsi": 72.0,
        "macro_data": {"interest_rate": 5.25, "inflation": 3.1, "gdp_growth": 2.5, "fear_greed_index": fng_data.score, "market_phase": "EXPANSION"},
        "technical_data": {"rsi": 72.0, "macd_signal": "BULLISH", "moving_averages": {"above_20ma": True, "above_50ma": True, "above_200ma": True}}
    }
    master_pod = await pod_mgr.analyze_all(pod_data)
    print("=== LIVE PodManager.analyze_all Raw Result ===")
    print("master_score:", master_pod.master_score)
    print("signal:", master_pod.signal)
    print("confidence:", master_pod.confidence)
    print("\nIndividual Pod Signals:")
    for s in master_pod.pod_signals:
        print(f"  pod_id: {s.pod_id:6s} | pod_name: {s.pod_name:18s} | signal: {s.signal.value:10s} | score: {s.score:6.1f} | confidence: {s.confidence}")

asyncio.run(run_pod())
