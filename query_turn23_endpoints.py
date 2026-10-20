# -*- coding: utf-8 -*-
import urllib.request, json, time

time.sleep(2)

print("==================================================")
print("1. [B-4 / B-1] Normal Live Endpoint Verification (HOLD Gating & Option Conf 85)")
print("==================================================")
req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal")
with urllib.request.urlopen(req) as resp:
    data_normal = json.loads(resp.read().decode('utf-8'))

print("NORMAL_LIVE_SIGNAL_FULL_DUMP:")
print(json.dumps(data_normal, indent=2, ensure_ascii=False))

print("\n==================================================")
print("2. [E-3 / B-2] Test-Signal Endpoint Verification (force_unavailable=investor_analysis,technical)")
print("==================================================")
req_test = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/test-signal?force_unavailable=investor_analysis,technical")
with urllib.request.urlopen(req_test) as resp:
    data_test = json.loads(resp.read().decode('utf-8'))

print("TEST_SIGNAL_FORCE_UNAVAILABLE_DUMP:")
print(json.dumps(data_test, indent=2, ensure_ascii=False))

