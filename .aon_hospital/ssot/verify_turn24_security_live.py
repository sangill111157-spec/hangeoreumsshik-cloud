# -*- coding: utf-8 -*-
import urllib.request, urllib.error, json, time

time.sleep(2)

print("==================================================")
print("1. [E-1 / B-1 / 결함 81] Production Route Parameter Invalidation Live Test")
print("==================================================")
# Call production route with malicious force_unavailable query parameter
req_prod = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal?force_unavailable=investor_analysis,technical")
with urllib.request.urlopen(req_prod) as resp:
    data_prod = json.loads(resp.read().decode('utf-8'))

print("PROD_SIGNAL_DUMP_WITH_IGNORED_PARAM:")
print(json.dumps(data_prod, indent=2, ensure_ascii=False))

# Assert force_unavailable was ignored -> coverage: 1.0, unavailable: []
assert data_prod["coverage"] == 1.0, f"Production route did not ignore parameter! Coverage: {data_prod['coverage']}"
assert len(data_prod["unavailable_modules"]) == 0, f"Unavailable modules not empty: {data_prod['unavailable_modules']}"
assert data_prod["kelly"]["stop_loss"] is None, f"Stop loss not null on 0 allocation: {data_prod['kelly']['stop_loss']}"
print("\n[PROD ROUTE SECURITY ASSERT PASSED]: force_unavailable parameter completely ignored, coverage is 1.0, stop_loss is null!")

print("\n==================================================")
print("2. [E-1 / B-1 / 결함 86] /test-signal Endpoint 404 Live Test in Production Mode")
print("==================================================")
test_url = "http://127.0.0.1:8000/api/stock/NVDA/test-signal"
try:
    with urllib.request.urlopen(test_url) as resp:
        res_data = resp.read()
        print("ERROR: Test endpoint accessible in production mode!")
        status_code = 200
except urllib.error.HTTPError as e:
    status_code = e.code
    err_body = e.read().decode('utf-8')
    print(f"HTTP Status Code: {status_code} (Expected: 404)")
    print(f"Error Response Body: {err_body}")

assert status_code == 404, f"Test endpoint was not blocked! Status: {status_code}"
print("\n[TEST ENDPOINT ACCESS CONTROL ASSERT PASSED]: /test-signal returned 404 Not Found in production mode!")

