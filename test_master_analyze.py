# -*- coding: utf-8 -*-
import urllib.request, json

url = 'http://127.0.0.1:8000/api/master/analyze'
req = urllib.request.Request(url, data=b'{}', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        status_code = resp.status
        data = json.loads(resp.read().decode('utf-8'))
        
        print("=== STEP 3 검증 결과 ===")
        print(f"HTTP Status Code: {status_code}")
        
        # master_score
        master_score = data.get('master_score')
        action = data.get('action')
        confidence = data.get('confidence')
        print(f"master_score: {master_score} (Action: {action}, Confidence: {confidence})")
        
        # Bollinger Bands 확인
        pod = data.get('pod_data', {})
        tech = pod.get('technical', {})
        bb = tech.get('bollinger_bands', {})
        print("Bollinger Bands in pod_data:")
        print(f"  Upper:  {bb.get('upper')}")
        print(f"  Middle: {bb.get('middle')}")
        print(f"  Lower:  {bb.get('lower')}")
        
        # stock_info current_price
        stock_info = pod.get('stock_info', {})
        curr_price = stock_info.get('current_price')
        print(f"Current Price: {curr_price}")
        if curr_price:
            fallback_upper = round(curr_price * 1.05, 2)
            print(f"Dummy Fallback Upper Reference (price * 1.05): {fallback_upper}")
            
        with open('master_analyze_response.json', 'w', encoding='utf-8') as out_f:
            json.dump(data, out_f, ensure_ascii=False, indent=2)
            
except Exception as e:
    print(f"Error calling /api/master/analyze: {e}")
