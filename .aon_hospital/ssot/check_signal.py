# -*- coding: utf-8 -*-
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    req = urllib.request.urlopen('http://127.0.0.1:8000/api/stock/NVDA/signal')
    data = json.loads(req.read().decode('utf-8'))
    print('=== /signal Response ===')
    print('master_score:', data.get('master_score'))
    print('final_signal:', data.get('final_signal'))
    print('confidence:', data.get('confidence'))
    print('components type:', type(data.get('components')))
    print('\n=== Components List ===')
    comps = data.get('components', [])
    if isinstance(comps, list):
        for c in comps:
            print(f"- name: {c.get('name')}, score: {c.get('score')}, signal: {c.get('signal')}, weight: {c.get('weight')}")
    elif isinstance(comps, dict):
        for k, v in comps.items():
            print(f"- {k}: {v}")
except Exception as e:
    print('Error:', e)
