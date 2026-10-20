# -*- coding: utf-8 -*-
import urllib.request, json, time

time.sleep(2)

print("==================================================")
print("1. [B-4 / B-1] Normal Live Endpoint Verification")
print("==================================================")
req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal")
with urllib.request.urlopen(req) as resp:
    data_normal = json.loads(resp.read().decode('utf-8'))

print("NORMAL_LIVE_SIGNAL_FULL_DUMP:")
print(json.dumps(data_normal, indent=2, ensure_ascii=False))

print("\n==================================================")
print("2. [E-3 / B-2] Live Force-Unavailable Injection (investor_analysis, technical)")
print("==================================================")
req_unavail = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal?force_unavailable=investor_analysis,technical")
with urllib.request.urlopen(req_unavail) as resp:
    data_unavail = json.loads(resp.read().decode('utf-8'))

print("FORCE_UNAVAILABLE_LIVE_SIGNAL_FULL_DUMP:")
print(json.dumps(data_unavail, indent=2, ensure_ascii=False))

