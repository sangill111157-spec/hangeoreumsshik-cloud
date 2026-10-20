# -*- coding: utf-8 -*-
import urllib.request, json, time

time.sleep(2)

print("==================================================")
print("1. [B-1 / B-2 / 결함 111·114] Normal Live Signal Full Dump (Expected Confidence: 65, Inst: 54)")
print("==================================================")
req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal")
with urllib.request.urlopen(req) as resp:
    data_live = json.loads(resp.read().decode('utf-8'))

print("NORMAL_LIVE_SIGNAL_FULL_DUMP:")
print(json.dumps(data_live, indent=2, ensure_ascii=False))

# Assertions
assert data_live["confidence"] == 65, f"Confidence mismatch: {data_live['confidence']} != 65"
assert data_live["raw_score"] == data_live["master_score"], f"Master score does not equal raw score after -2 removal: {data_live['master_score']} != {data_live['raw_score']}"
assert len(data_live["adjustments"]) == 0, f"Adjustments not empty: {data_live['adjustments']}"
assert data_live["components"][4]["confidence"] == 54, f"Institutional conf is not 54: {data_live['components'][4]['confidence']}"
print("\n[NORMAL LIVE ASSERT PASSED]: confidence is 65, institutional is 54, adjustments is empty (-2 removed)!")

