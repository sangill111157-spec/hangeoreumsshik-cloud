# -*- coding: utf-8 -*-
import urllib.request, json

url_nvda = 'http://127.0.0.1:8000/api/nvda/signal'
url_stock = 'http://127.0.0.1:8000/api/stock/NVDA/signal'

print("=== 1. Calling /api/nvda/signal ===")
try:
    with urllib.request.urlopen(url_nvda, timeout=30) as resp:
        print(f"Status Code: {resp.status}")
        data_nvda = json.loads(resp.read().decode('utf-8'))
        print(json.dumps(data_nvda, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error calling /api/nvda/signal: {e}")
    data_nvda = {}

print("\n=== 2. Calling /api/stock/NVDA/signal ===")
try:
    with urllib.request.urlopen(url_stock, timeout=30) as resp:
        print(f"Status Code: {resp.status}")
        data_stock = json.loads(resp.read().decode('utf-8'))
        print(json.dumps(data_stock, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error calling /api/stock/NVDA/signal: {e}")
    data_stock = {}

print("\n=== 3. Two Endpoints Comparison ===")
print(f"{'Metric':20s} | {'/api/nvda/signal':20s} | {'/api/stock/NVDA/signal':20s}")
print("-" * 70)
print(f"{'Price':20s} | {str(data_nvda.get('price')):20s} | {str(data_stock.get('price')):20s}")
print(f"{'Overall Signal':20s} | {str(data_nvda.get('signal')):20s} | {str(data_stock.get('overall_signal') or data_stock.get('signal')):20s}")
print(f"{'Confidence/Score':20s} | {str(data_nvda.get('confidence')):20s} | {str(data_stock.get('overall_confidence') or data_stock.get('confidence')):20s}")
print(f"{'Bull Count':20s} | {str(data_nvda.get('bull_count')):20s} | {str(data_stock.get('bull_count')):20s}")
print(f"{'Bear Count':20s} | {str(data_nvda.get('bear_count')):20s} | {str(data_stock.get('bear_count')):20s}")

with open('signal_comparison.json', 'w', encoding='utf-8') as f:
    json.dump({'nvda_signal': data_nvda, 'stock_signal': data_stock}, f, ensure_ascii=False, indent=2)
