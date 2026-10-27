import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
backend = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend)

os.environ['KIS_APP_KEY'] = 'mock_key'
os.environ['KIS_APP_SECRET'] = 'mock_secret'
os.environ['SECRET_KEY'] = 'mock_secret_key'
os.environ['ENABLE_LIVE_ORDERS'] = 'False'

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
resp = client.get("/api/stock/NVDA/signal")
print("Status:", resp.status_code)
data = resp.json()
print("Full Response:")
print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n=== Calculation Breakdown ===")
weights = data.get("weights_used", {})
components = data.get("components", [])

comp_map = {
    "5대 투자자": "investor_analysis",
    "멀티전략": "pod_signals",
    "기술적": "technical",
    "AI 뉴스": "llm_news",
    "기관/13F": "institutional",
    "옵션 플로우": "options_flow",
    "다크풀": "darkpool"
}

calc_sum = 0.0
for comp in components:
    name = comp.get("name")
    score = comp.get("score")
    w_key = comp_map.get(name)
    w = weights.get(w_key, 0.0)
    term = (score if score is not None else 0.0) * w
    calc_sum += term
    print(f"Component '{name}' ({w_key}): score={score} (repr={repr(score)}), weight={w} -> term={term}")

print(f"\nCalculated sum(comp.score * weight) = {calc_sum:.6f}")
print(f"master_score in response = {data.get('master_score')}")
print(f"raw_score in response = {data.get('raw_score')}")
print(f"Difference = {calc_sum - data.get('master_score', 0):.6f}")
