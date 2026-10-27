# -*- coding: utf-8 -*-
import urllib.request, json

url = 'http://127.0.0.1:8000/api/stock/NVDA/signal'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=35) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Status:", resp.status)
        print("master_score:", data.get("master_score"))
        print("signal:", data.get("signal"))
        print("coverage:", data.get("coverage"))
        print("available_module_count:", data.get("available_module_count"))
        print("unavailable_modules:", data.get("unavailable_modules"))
        print("weights_used:", json.dumps(data.get("weights_used"), indent=2))
except Exception as e:
    print("Error:", e)
