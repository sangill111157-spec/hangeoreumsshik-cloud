# -*- coding: utf-8 -*-
import urllib.request, json

url = 'http://127.0.0.1:8000/api/nvda/analysis?period=1y'
with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"HTTP Status: {resp.status}")
    
    signals = data.get('signals', [])
    print(f"\n=== 1. 5대 투자자 시그널 목록 (총 {len(signals)}개) ===")
    sig_map = {}
    for s in signals:
        inv = s.get('investor')
        sig_map[inv] = s
        print(f"  - {inv:16s}: Signal={s.get('signal'):10s}, Confidence={s.get('confidence')}")
        
    buffett = sig_map.get('Warren Buffett', {})
    buffett_reasons = buffett.get('reasoning', [])
    print("\n=== 2. 버핏 Reasoning ===")
    for r in buffett_reasons:
        print(f"  * {r}")
    has_debt_reason = any("부채비율: 6.6% (건전)" in r or "6.6%" in r for r in buffett_reasons)
    print(f"  -> Check '부채비율: 6.6% (건전)' present: {has_debt_reason}")
    
    dalio = sig_map.get('Ray Dalio', {})
    dalio_metrics = dalio.get('key_metrics', {})
    dalio_beta = dalio_metrics.get('beta')
    print(f"\n=== 3. Dalio Beta ===")
    print(f"  Dalio beta: {dalio_beta} (Expected: 2.21, not 1.0) -> {dalio_beta == 2.21}")
    
    lynch = sig_map.get('Peter Lynch', {})
    lynch_metrics = lynch.get('key_metrics', {})
    lynch_sector = lynch_metrics.get('sector')
    print(f"\n=== 4. Lynch Sector ===")
    print(f"  Lynch sector: '{lynch_sector}' (Expected: 'Technology') -> {lynch_sector == 'Technology'}")
    
    with open('nvda_analysis_verification.json', 'w', encoding='utf-8') as out_f:
        json.dump(data, out_f, ensure_ascii=False, indent=2)
