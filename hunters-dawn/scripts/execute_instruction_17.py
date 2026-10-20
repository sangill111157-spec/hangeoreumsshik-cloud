import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://connect-ai-shin.blogspot.com"
FEED_URL = f"{BASE_URL}/feeds/posts/default?max-results=50"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=================================================================")
print("📋 [작업 지시서 #17] 전수 정밀 파싱 및 실시간 데이터 수집")
print("=================================================================")

def get_url_data(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)

status, xml_text = get_url_data(FEED_URL)
root = ET.fromstring(xml_text)
ns = {'atom': 'http://www.w3.org/2005/Atom'}
entries = root.findall('atom:entry', ns)

posts = []
for idx, e in enumerate(reversed(entries), 1):
    title = e.find('atom:title', ns).text or ""
    pub = e.find('atom:published', ns).text[:10]
    links = e.findall('atom:link', ns)
    href = [l.attrib['href'] for l in links if l.attrib.get('rel') == 'alternate'][0]
    content = e.find('atom:content', ns).text or ""
    
    # Categories / Labels
    categories = [c.attrib.get('term') for c in e.findall('atom:category', ns) if c.attrib.get('term')]
    
    # Images count
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
    
    posts.append({
        'num': idx,
        'pub': pub,
        'title': title,
        'url': href,
        'content': content,
        'labels': categories,
        'images': imgs
    })

print(f"✅ 총 {len(posts)}개 포스트 및 메타데이터 파싱 완료.\n")

# 1. A-3 면책 문구 원문 첫 문장 전수 파싱
print("-----------------------------------------------------------------")
print("📌 [1. A-3 재제출] 면책 문구 실제 첫 문장 원문 추출")
for p in posts:
    num = p['num']
    title = p['title']
    content = p['content']
    
    # Clean text to find disclaimer
    # Search for disclaimer paragraph at the bottom
    lines = [line.strip() for line in re.sub(r'<[^>]+>', '\n', content).split('\n') if line.strip()]
    
    disclaimer_first_sentence = "❌ 면책 문구 미발견"
    for line in reversed(lines):
        if any(kw in line for kw in ["이 글은", "본 글은", "의학적", "투자", "참고"]):
            # Get first sentence
            sentences = re.split(r'(?<=[.!?])\s+', line)
            if sentences:
                disclaimer_first_sentence = sentences[0].strip()
            break
            
    cat_type = "재테크" if num in [7, 10, 13] else "건강"
    print(f"[{num:02d}회차] ({cat_type}) '{title[:20]}...'")
    print(f"   ▶ 면책 문구 첫 문장 원문: \"{disclaimer_first_sentence}\"")

# 2. A-4 교정된 스캔 (문장 단위 원문 추출)
print("\n-----------------------------------------------------------------")
print("📌 [2. A-4 교정된 스캔] 문장 단위 금칙어 및 맥락 스캔")
forbidden_kws = ["완치", "치료", "낫는다", "약 대신", "약 끊", "삼성전자", "테슬라", "원금 보장", "수익률"]

found_sentences = []
for p in posts:
    num = p['num']
    content = p['content']
    clean_text = re.sub(r'<[^>]+>', ' ', content)
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    
    for s in sentences:
        s_clean = s.strip()
        for kw in forbidden_kws:
            if kw in s_clean:
                found_sentences.append({
                    'num': num,
                    'kw': kw,
                    'sentence': s_clean
                })

if found_sentences:
    for item in found_sentences:
        print(f"⚠️ [{item['num']:02d}회차] 매칭 단어: '{item['kw']}'")
        print(f"   ▶ 원문 문장: \"{item['sentence']}\"")
else:
    print("✅ 문장 단위 스캔 결과: 금칙 표현 적발 0건!")

# 3. A-6 라벨 및 이미지 장수 전수 조사
print("\n-----------------------------------------------------------------")
print("📌 [3. A-6 재검증] 이미지 장수 및 Blogger 실제 라벨 전수 결과")
all_labels = {}
for p in posts:
    img_cnt = len(p['images'])
    lbl_str = ", ".join(p['labels']) if p['labels'] else "없음 (라벨 미부착)"
    print(f"[{p['num']:02d}회차] 이미지 수: {img_cnt}장 | Blogger 실제 라벨: [{lbl_str}]")
    
    for l in p['labels']:
        all_labels[l] = all_labels.get(l, 0) + 1

print("\n📊 Blogger 실제 라벨 통계:")
for l_name, cnt in all_labels.items():
    l_url = f"{BASE_URL}/search/label/{urllib.parse.quote(l_name)}"
    print(f" - 라벨명: '{l_name}' ({cnt}편) | URL: {l_url}")

print("\n=================================================================")
print("파싱 및 분석 완료!")
