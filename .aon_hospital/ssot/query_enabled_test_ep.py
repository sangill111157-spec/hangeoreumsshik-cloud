# -*- coding: utf-8 -*-
import urllib.request, json, time

time.sleep(2)

print("==================================================")
print("1. [E-3 / B-1 / 결함 86] /test-signal Enabled (ENABLE_TEST_ENDPOINTS=True) Live 200 Test")
print("==================================================")
req_test = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/test-signal?force_unavailable=investor_analysis,technical")
with urllib.request.urlopen(req_test) as resp:
    data_test = json.loads(resp.read().decode('utf-8'))
    status_code = resp.status

print(f"HTTP Status Code: {status_code} (Expected: 200)")
print("TEST_SIGNAL_ENABLED_RESPONSE:")
print(json.dumps(data_test, indent=2, ensure_ascii=False))
assert status_code == 200
assert data_test["coverage"] == 0.65
assert len(data_test["unavailable_modules"]) == 2
print("[ASSERT PASSED]: /test-signal returns 200 with coverage 0.65 when ENABLE_TEST_ENDPOINTS=True!")

