# -*- coding: utf-8 -*-
import urllib.request, time, json

def test_endpoint(name, url):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed = time.time() - t0
            data = json.loads(resp.read().decode('utf-8'))
            print(f"=== {name} ===")
            print(f"Status: {resp.status} | Time: {elapsed:.3f}s")
            print("Keys:", list(data.keys()))
            print(json.dumps(data, ensure_ascii=False, indent=2)[:200] + '...\n')
    except Exception as e:
        print(f"Error {name}: {e}")

test_endpoint('/api/risk/score', 'http://127.0.0.1:8000/api/risk/score')
test_endpoint('/api/rebalance/plan', 'http://127.0.0.1:8000/api/rebalance/plan')
