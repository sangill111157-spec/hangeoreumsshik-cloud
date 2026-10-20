# -*- coding: utf-8 -*-
import sys, os, subprocess, json, urllib.request

try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Live /signal Response Status: 200 OK")
        print("  master_score:", data.get("master_score"))
        print("  raw_score   :", data.get("raw_score"))
        print("  coverage    :", data.get("coverage"))
        print("  signal      :", data.get("signal"))
        print("  components  :")
        for c in data.get("components", []):
            print(f"    - {c.get('name'):12s}: score={c.get('score')} | signal={c.get('signal'):12s} | conf={c.get('confidence')}")
except Exception as e:
    print("Live /signal call error:", e)
