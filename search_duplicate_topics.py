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

print("=== 1. '퇴근 후 걷기' / '걷기' 관련 검색 ===")
# 대표글: 14번 (https://connect-ai-shin.blogspot.com/2026/08/3.html)
p14_url = posts_sorted[13]['url']
print(f"대표글 14번 URL: {p14_url}")

with open('duplicate_search_walking_nuts.txt', 'w', encoding='utf-8') as out:
    out.write("=== 1. '걷기' 관련 검색 결과 ===\n")
    for idx, p in enumerate(posts_sorted, 1):
        # 걷기 검색
        matches = re.findall(r'[^.!?\n]*걷기[^.!?\n]*[.!?]', p['content'])
        out.write(f"[{idx:02d}번 글] Post ID: {p['post_id']} | Title: {p['title']} | 매칭 문장수: {len(matches)}\n")
        for m in matches:
            out.write(f"  - {m.strip()}\n")
        out.write("\n")

    out.write("\n" + "="*70 + "\n\n")
    out.write("=== 2. '견과류' / '견과' 관련 검색 결과 ===\n")
    # 대표글: 09번 (https://connect-ai-shin.blogspot.com/2026/07/blog-post_28.html)
    p09_url = posts_sorted[8]['url']
    out.write(f"대표글 09번 URL: {p09_url}\n\n")
    for idx, p in enumerate(posts_sorted, 1):
        matches = re.findall(r'[^.!?\n]*견과[^.!?\n]*[.!?]', p['content'])
        out.write(f"[{idx:02d}번 글] Post ID: {p['post_id']} | Title: {p['title']} | 매칭 문장수: {len(matches)}\n")
        for m in matches:
            out.write(f"  - {m.strip()}\n")
        out.write("\n")

print("Duplicate search completed. Saved to duplicate_search_walking_nuts.txt")
