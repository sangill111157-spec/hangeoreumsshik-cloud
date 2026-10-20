# -*- coding: utf-8 -*-
import urllib.request, json, time

time.sleep(2)

req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

print("NORMAL_LIVE_SIGNAL_FULL_DUMP_WITH_COMPONENTS:")
print(json.dumps(data, indent=2, ensure_ascii=False))

