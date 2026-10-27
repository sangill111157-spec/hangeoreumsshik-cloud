# -*- coding: utf-8 -*-
import urllib.request, json

def call_and_print(name, url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"=== {name} (Status: {resp.status}) ===")
            lines = json.dumps(data, indent=2, ensure_ascii=False).split('\n')
            for l in lines[:10]:
                print(l)
    except Exception as e:
        print(f"=== {name} Error: {e} ===")

call_and_print("/api/risk/score", "http://127.0.0.1:8000/api/risk/score")
print()
call_and_print("/api/rebalance/plan", "http://127.0.0.1:8000/api/rebalance/plan")

with open(r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx', 'r', encoding='utf-8') as f:
    app_text = f.read()

print('\n=== grep riskError / rebalanceError in App.tsx ===')
for i, l in enumerate(app_text.split('\n')):
    if any(k in l for k in ['riskError', 'rebalanceError', 'setRiskError', 'setRebalanceError']):
        print(f"Line {i+1:4d}: {l.strip()}")
