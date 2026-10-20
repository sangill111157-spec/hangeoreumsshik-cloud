# -*- coding: utf-8 -*-
import os, sys, json, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 1. Test with ENABLE_TEST_ENDPOINTS = "true"
os.environ["ENABLE_TEST_ENDPOINTS"] = "true"
from app.core.config import settings
settings.ENABLE_TEST_ENDPOINTS = True
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("==================================================")
print("1. [B-1 ② / 결함 122] Route BUY Live Response Dump (HTTP 200 OK)")
print("==================================================")
resp_buy = client.get("/api/stock/NVDA/test-signal?mode=buy")
print(f"Status Code: {resp_buy.status_code}")
assert resp_buy.status_code == 200
buy_json = resp_buy.json()
print("ROUTE_BUY_LIVE_RESPONSE_JSON:")
print(json.dumps(buy_json, indent=2, ensure_ascii=False))

# Assertions for BUY response
assert buy_json["signal"] == "BUY"
assert buy_json["raw_score"] == 76.1
assert buy_json["master_score"] == 76.1
assert buy_json["kelly"]["recommended_shares"] == 13
assert buy_json["kelly"]["position_value"] == 2819.05
assert buy_json["kelly"]["ceiling_applied"] is True
assert buy_json["kelly"]["ceiling_reason"] == "stage1_dry_run"
assert buy_json["kelly"]["ceiling_shares"] == 13
assert buy_json["kelly"]["stop_loss"] == 199.5
print("\n[ROUTE BUY LIVE RESPONSE ASSERTS PASSED: 100% Exact & Reproducible]!")

print("\n==================================================")
print("2. [A-4 / 결함 120] Route UNAVAILABLE Live Response Dump (Coverage = 0.65)")
print("==================================================")
resp_unavail = client.get("/api/stock/NVDA/test-signal?force_unavailable=investor_analysis,options_flow")
print(f"Status Code: {resp_unavail.status_code}")
assert resp_unavail.status_code == 200
unavail_json = resp_unavail.json()
print("ROUTE_UNAVAILABLE_LIVE_RESPONSE_JSON:")
print(json.dumps(unavail_json, indent=2, ensure_ascii=False))
assert unavail_json["coverage"] == 0.65
assert unavail_json["unavailable_modules"] == ["investor_analysis", "options_flow"]
assert unavail_json["available_module_count"] == 5
print("\n[ROUTE UNAVAILABLE RESPONSE ASSERTS PASSED: Coverage 0.65 Verified]!")

print("\n==================================================")
print("3. [보안 격리] ENABLE_TEST_ENDPOINTS Disabled Test (HTTP 404 Expected)")
print("==================================================")
settings.ENABLE_TEST_ENDPOINTS = False
resp_404 = client.get("/api/stock/NVDA/test-signal")
print(f"Disabled Status Code: {resp_404.status_code} (Expected: 404)")
assert resp_404.status_code == 404
print("[TEST ENDPOINTS ISOLATION ASSERT PASSED: 404 in Production]!")

# Reset
settings.ENABLE_TEST_ENDPOINTS = True

