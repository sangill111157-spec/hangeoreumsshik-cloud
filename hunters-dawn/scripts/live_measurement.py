import urllib.request
import urllib.parse
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)

print("=================================================================")
print("🔍 라이브 블로그 실제 접근 실측 (LIVE MEASUREMENT)")
print("=================================================================")

# 1. Check Contact Page
c_st, c_html = fetch_url('https://connect-ai-shin.blogspot.com/p/contact.html')
print(f"1. Contact Page (/p/contact.html): HTTP {c_st}")
if c_st == 200:
    # Check Emojis
    has_e1 = '📧' in c_html
    has_e2 = '📌' in c_html
    has_e3 = '😊' in c_html
    print(f"   - 이모지 존재 여부: 📧={has_e1}, 📌={has_e2}, 😊={has_e3}")

# 2. Check About Page
a_st, a_html = fetch_url('https://connect-ai-shin.blogspot.com/p/about.html')
print(f"2. About Page (/p/about.html): HTTP {a_st}")

# 3. Check Pages Feed
f_st, f_json = fetch_url('https://connect-ai-shin.blogspot.com/feeds/pages/default?alt=json')
print(f"3. Blogger Pages Feed: HTTP {f_st}")
if f_st == 200:
    data = json.loads(f_json)
    entries = data.get('feed', {}).get('entry', [])
    print(f"   ▶ 게시된 페이지 총 수: {len(entries)}개")
    for e in entries:
        t = e.get('title', {}).get('$t', '')
        links = e.get('link', [])
        href = [l.get('href') for l in links if l.get('rel') == 'alternate'][0]
        st, body = fetch_url(href)
        print(f"     - Title: '{t}' | HTTP {st} | URL: {href}")

# 4. Check 02 Post Table
p2_st, p2_html = fetch_url('https://connect-ai-shin.blogspot.com/2026/07/36-32-75-68kg.html')
print(f"4. 02회차 포스트: HTTP {p2_st}")
if p2_st == 200:
    has_overflow = 'overflow-x' in p2_html
    print(f"   - 02회차 overflow-x 래퍼 여부: {'존재' if has_overflow else '없음'}")

print("=================================================================")
