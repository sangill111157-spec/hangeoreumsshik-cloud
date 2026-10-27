# -*- coding: utf-8 -*-
import urllib.request
import json
import re

post_ids = [
    {"num": "04", "id": "4072797504508800553", "title": "교대근무자의 무너진 식사 리듬, 규칙적으로 되돌린 방법"},
    {"num": "09", "id": "6417301061070016808", "title": "교대근무자가 챙겨 먹기 좋은 간단한 도시락·간식"},
    {"num": "15", "id": "4150316841132855829", "title": "물 많이 마시기, 나만의 루틴 만들기"},
    {"num": "17", "id": "9009663558624875630", "title": "교대근무자 특수건강진단 실전 이용기"}
]

with open('verification_04_09_15_17.txt', 'w', encoding='utf-8') as out:
    for p in post_ids:
        pid = p['id']
        url = f'https://connect-ai-shin.blogspot.com/feeds/posts/default/{pid}?alt=json'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        entry = data.get('entry', {})
        title = entry.get('title', {}).get('$t', '')
        content = entry.get('content', {}).get('$t', '')
        
        uls = re.findall(r'<ul\b[^>]*>[\s\S]*?</ul>', content, re.IGNORECASE)
        all_lis = re.findall(r'<li\b', content, re.IGNORECASE)
        
        out.write(f"[{p['num']}번 글] Title: {title} | Post ID: {pid}\n")
        out.write(f"  전체 <li> 수: {len(all_lis)}개 | 생성된 <ul> 블록 수: {len(uls)}개\n")
        out.write("  --- <ul> 블록별 포함 <li> 개수 ---\n")
        for u_idx, ul in enumerate(uls, 1):
            li_in_ul = len(re.findall(r'<li\b', ul, re.IGNORECASE))
            out.write(f"    (블록 {u_idx}) <li> {li_in_ul}개 포함\n")
        out.write("="*70 + "\n\n")

print("Verification written to verification_04_09_15_17.txt")
