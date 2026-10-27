# -*- coding: utf-8 -*-
import urllib.request
import json
import re
from html.parser import HTMLParser

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
    
    posts.append({
        'post_id': post_id,
        'title': title,
        'published': published,
        'url': alt_url,
        'content': content,
        'categories': categories
    })

posts_sorted = sorted(posts, key=lambda x: x['published'])

def find_orphan_lis(html):
    """
    HTML 내에서 <ul> 또는 <ol> 태그 내부에 있지 않은 <li> 태그들을 검출
    """
    # 간단한 태그 스택 검사기
    # 태그를 순차 파싱하며 li가 열렸을 때 스택 상위(조상)에 ul 또는 ol이 있는지 검사
    tag_regex = re.compile(r'<\s*(/)?\s*([a-zA-Z0-9]+)([^>]*)>')
    
    stack = []
    orphan_lis = []
    all_lis_count = len(re.findall(r'<li\b', html, re.IGNORECASE))
    
    # 텍스트 내에서 위치 추적
    for m in tag_regex.finditer(html):
        is_closing = bool(m.group(1))
        tag_name = m.group(2).lower()
        full_tag = m.group(0)
        
        # self-closing tags
        if full_tag.endswith('/>') or tag_name in ['img', 'br', 'hr', 'input', 'meta', 'link']:
            continue
            
        if not is_closing:
            if tag_name == 'li':
                # 스택에 ul이나 ol이 있는지 확인
                in_list = any(t in ['ul', 'ol'] for t in stack)
                if not in_list:
                    # 앞뒤 문맥 100자 추출
                    start_pos = max(0, m.start() - 50)
                    end_pos = min(len(html), m.end() + 100)
                    snippet = html[start_pos:end_pos].replace('\n', ' ')
                    orphan_lis.append({
                        'snippet': snippet,
                        'pos': m.start()
                    })
            stack.append(tag_name)
        else:
            # closing
            if tag_name in stack:
                # 가장 최근 해당 태그 팝
                for i in range(len(stack) - 1, -1, -1):
                    if stack[i] == tag_name:
                        stack.pop(i)
                        break

    return orphan_lis, all_lis_count

report = []
for idx, p in enumerate(posts_sorted, 1):
    orphans, total_lis = find_orphan_lis(p['content'])
    report.append({
        'num': idx,
        'post_id': p['post_id'],
        'title': p['title'],
        'url': p['url'],
        'total_lis': total_lis,
        'orphan_count': len(orphans),
        'orphans': orphans
    })

with open('orphan_li_report.txt', 'w', encoding='utf-8') as out:
    out.write("=== 전체 16편 글 orphan <li> 검사 결과 ===\n\n")
    for r in report:
        out.write(f"[{r['num']:02d}번 글] Post ID: {r['post_id']} | Orphan <li>: {r['orphan_count']}개 / 전체 <li>: {r['total_lis']}개\n")
        out.write(f"제목: {r['title']}\n")
        out.write(f"URL: {r['url']}\n")
        if r['orphan_count'] > 0:
            out.write("검출된 orphan <li> 문맥:\n")
            for o_idx, o in enumerate(r['orphans'], 1):
                out.write(f"  ({o_idx}) {o['snippet']}\n")
        out.write("-" * 70 + "\n")

print("Finished scanning orphan <li>. Results written to orphan_li_report.txt")
