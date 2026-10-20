# -*- coding: utf-8 -*-
import urllib.request
import json
import re
import os
import sys

# Blogger Feed URL
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
    categories = [cat.get('term') for cat in entry.get('category', [])]
    
    # 썸네일 확인
    media_thumb = entry.get('media$thumbnail', {}).get('url', '')
    
    posts.append({
        'post_id': post_id,
        'title': title,
        'published': published,
        'url': alt_url,
        'content': content,
        'categories': categories,
        'media_thumbnail': media_thumb,
        'raw_entry': entry
    })

# 발행일 오름차순 (01번~16번)
posts_sorted = sorted(posts, key=lambda x: x['published'])

with open('feed_analysis_result.txt', 'w', encoding='utf-8') as out:
    out.write(f"총 게시글 수: {len(posts_sorted)}\n\n")
    for idx, p in enumerate(posts_sorted, 1):
        out.write(f"[{idx:02d}번 글]\n")
        out.write(f"Post ID: {p['post_id']}\n")
        out.write(f"Title: {p['title']}\n")
        out.write(f"Published: {p['published']}\n")
        out.write(f"URL: {p['url']}\n")
        out.write(f"Categories: {p['categories']}\n")
        out.write(f"Thumbnail: {p['media_thumbnail']}\n")
        out.write("-" * 60 + "\n")

# 작업 A: 15번 글 (https://connect-ai-shin.blogspot.com/2026/08/blog-post.html) 이미지 확인
print("=== 작업 A: 15번 글 이미지 상태 검사 ===")
target_15 = None
for idx, p in enumerate(posts_sorted, 1):
    if '2026/08/blog-post.html' in p['url'] or idx == 15:
        target_15 = (idx, p)
        break

if target_15:
    idx, p15 = target_15
    print(f"[{idx:02d}번 글] Title: {p15['title']}")
    print(f"Post ID: {p15['post_id']}")
    print(f"URL: {p15['url']}")
    print(f"Thumbnail URL in feed: {p15['media_thumbnail']}")
    
    content = p15['content']
    img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    a_hrefs = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', content)
    
    print("img src:", img_srcs)
    print("a href:", a_hrefs)

