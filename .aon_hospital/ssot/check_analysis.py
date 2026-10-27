# -*- coding: utf-8 -*-
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    req = urllib.request.urlopen('http://127.0.0.1:8000/api/stock/NVDA/analysis')
    data = json.loads(req.read().decode('utf-8'))
    print('Keys:', list(data.keys()))
    print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print('Error:', e)
