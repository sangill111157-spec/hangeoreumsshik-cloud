# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Call MasterSignalEngine directly to verify D-3 in-process
from app.services.master_signal import MasterSignalEngine
engine = MasterSignalEngine()

mock_data = {
    "investor_analysis": {"overall_signal": "buy", "overall_confidence": 70},
    "pod_signals": [{"signal": "buy", "confidence": 70}],
    "technical": {"overall_signal": "buy", "confidence": 75},
    "llm_news": {"sentiment_label": "NEUTRAL", "news_composite_score": 50, "total_news_analyzed": 5},
    "institutional": {"available": True},
    "options_flow": {"options_signal": "strong_buy", "options_composite_score": 70, "available": True},
    "darkpool": {"darkpool_signal": "sell", "darkpool_composite_score": 40, "available": True},
    "events": {},
    "correlation": {},
    "symbol": "NVDA"
}

res = engine.calculate_final_master_signal(**mock_data)
print("--- [Direct Engine D-3 In-Process Verification] ---")
print("master_score:", res.master_score)
print("raw_score   :", res.raw_score)
print("Components normalized signals:")
for c in res.components:
    print(f"  - {c.name:12s}: signal={c.signal:12s} is_upper={c.signal.isupper()} is_not_neutral={c.signal != 'NEUTRAL'}")
