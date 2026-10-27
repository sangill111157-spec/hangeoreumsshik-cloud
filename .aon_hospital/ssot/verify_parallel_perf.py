# -*- coding: utf-8 -*-
import urllib.request, json, time, statistics

print("=== Measuring Parallel /signal Performance & Consistency ===")
times = []
scores = []
responses = []

for i in range(3):
    t0 = time.perf_counter()
    url = 'http://127.0.0.1:8000/api/stock/NVDA/signal'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        elapsed = time.perf_counter() - t0
        d = json.loads(resp.read().decode('utf-8'))
        times.append(elapsed)
        scores.append(d.get('master_score', 0))
        responses.append(d)
        print(f"Run {i+1}: Status {resp.status} in {elapsed:.3f}s | master_score: {d.get('master_score')} | coverage: {d.get('coverage')} | available_count: {d.get('available_module_count')}")

mean_time = statistics.mean(times)
std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0

print(f"\nAverage Response Time: {mean_time:.3f}s (Previous sequential was 26.51s!)")
print(f"Scores across 3 runs: {scores} (Standard deviation: {std_score:.4f})")

print("\n=== Components in Run 1 (Parallel execution) ===")
for c in responses[0].get('components', []):
    print(f"  {c.get('name'):12s}: score={c.get('score')}, signal={c.get('signal')}, confidence={c.get('confidence')}")
