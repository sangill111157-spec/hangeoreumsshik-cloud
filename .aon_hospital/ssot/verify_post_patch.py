# -*- coding: utf-8 -*-
import sys, os, subprocess, json, urllib.request

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from app.services.master_signal import MasterSignalEngine

# 1. Fixed Mock Data Verification
mock_full = {
    "investor_analysis": {"overall_signal": "BUY", "overall_confidence": 70, "bull_count": 3, "bear_count": 1},
    "pod_signals": [
        {"pod_name": "growth", "signal": "BUY", "confidence": 70, "score": 30.0},
        {"pod_name": "value", "signal": "STRONG_BUY", "confidence": 80, "score": 75.0},
        {"pod_name": "momentum", "signal": "HOLD", "confidence": 50, "score": 10.0},
        {"pod_name": "quality", "signal": "BUY", "confidence": 75, "score": 40.0},
        {"pod_name": "safety", "signal": "HOLD", "confidence": 40, "score": -10.0}
    ],
    "technical": {"overall_signal": "BUY", "confidence": 75, "trend": "BULLISH", "rsi": {"value": 58}},
    "llm_news": {"sentiment_label": "HOLD", "news_composite_score": 50.0, "total_news_analyzed": 5},
    "institutional": {"available": True},
    "options_flow": {"options_signal": "STRONG_BUY", "options_composite_score": 70.0, "available": True},
    "darkpool": {"darkpool_signal": "SELL", "darkpool_composite_score": 40.0, "available": True},
    "events": {},
    "correlation": {},
    "symbol": "NVDA"
}

engine = MasterSignalEngine()
res = engine.calculate_final_master_signal(**mock_full)

print("==================================================")
print("1. [Post-Patch Verification] Fixed Mock 14-Digit")
print("==================================================")
print(f"  raw_score   (14자리): {res.raw_score:.14f}")
print(f"  master_score(14자리): {res.master_score:.14f}")
print(f"  signal              : {res.signal}")
print(f"  coverage            : {res.coverage}")
print(f"  components pod_score: {res.components[1].score:.14f}")

print("\n==================================================")
print("2. [Live /signal Endpoint Verification]")
print("==================================================")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Live /signal Response Status: 200 OK")
        print(f"  master_score: {data.get('master_score')}")
        print(f"  raw_score   : {data.get('raw_score')}")
        print(f"  coverage    : {data.get('coverage')}")
        print(f"  signal      : {data.get('signal')}")
except Exception as e:
    print("Live call error:", e)

