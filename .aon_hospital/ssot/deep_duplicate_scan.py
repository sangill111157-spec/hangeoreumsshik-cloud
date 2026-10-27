# -*- coding: utf-8 -*-
import urllib.request
import json
import re

feed_url = 'https://connect-ai-shin.blogspot.com/feeds/posts/default?alt=json&max-results=50'
req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    feed_data = json.loads(resp.read().decode('utf-8'))

entries = feed_data.get('feed', {}).get('entry', [])
posts = []
for entry in entries:
    title = entry.get('title', {}).get('$t', '')
    id_str = entry.get('id', {}).get('$t', '')
    post_id = id_str.split('post-')[-1] if 'post-' in id_str else id_str
    published = entry.get('published', {}).get('$t', '')
    content = entry.get('content', {}).get('$t', '')
    links = {link.get('rel'): link.get('href') for link in entry.get('link', [])}
    alt_url = links.get('alternate', '')
    posts.append({
        'post_id': post_id,
        'title': title,
        'published': published,
        'url': alt_url,
        'content': content
    })

posts_sorted = sorted(posts, key=lambda x: x['published'])

with open('deep_duplicate_scan.txt', 'w', encoding='utf-8') as out:
    out.write("=== 1. '퇴근 후 걷기' / '걷기' 관련 비대표글 상세 문맥 (대표글: 14번) ===\n")
    # 비대표글 중 걷기 관련 언급 글 확인
    for idx, p in enumerate(posts_sorted, 1):
        if idx == 14:
            continue # 대표글 제외
        
        # 걷기/산책/걸음 등
        matches = re.findall(r'(?:<p>|<li>)[^<]*(?:걷기|산책|걸었|걸으|걸음)[^<]*(?:</p>|</li>)', p['content'])
        if matches:
            out.write(f"[{idx:02d}번 글] Post ID: {p['post_id']} | Title: {p['title']} | URL: {p['url']}\n")
            for m in matches:
                out.write(f"  {m}\n")
            out.write("\n")

    out.write("\n" + "="*70 + "\n\n")
    out.write("=== 2. '견과류' 관련 비대표글 상세 문맥 (대표글: 09번) ===\n")
    for idx, p in enumerate(posts_sorted, 1):
        if idx == 9:
            continue # 대표글 제외
        
        matches = re.findall(r'(?:<p>|<li>)[^<]*(?:견과)[^<]*(?:</p>|</li>)', p['content'])
        if matches:
            out.write(f"[{idx:02d}번 글] Post ID: {p['post_id']} | Title: {p['title']} | URL: {p['url']}\n")
            for m in matches:
                out.write(f"  {m}\n")
            out.write("\n")

print("Deep scan complete.")
