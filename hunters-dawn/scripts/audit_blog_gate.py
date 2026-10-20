import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://connect-ai-shin.blogspot.com"
FEED_URL = f"{BASE_URL}/feeds/posts/default?max-results=50"

print("=================================================================")
print("📋 [안실장 작업 지시서 #16] A그룹 실시간 전수 검증 스크립트 가동")
print("=================================================================")

# 1. Fetch Posts from Feed
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_url_status(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)

# Fetch Feed XML
print("\n[Step 1] 블로그 Feed 및 15개 포스트 본문 전수 수집 중...")
status, xml_text = get_url_status(FEED_URL)
if status != 200:
    print(f"Error fetching feed: HTTP {status}")
    sys.exit(1)

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
    posts.append({
        'num': idx,
        'pub': pub,
        'title': title,
        'url': href,
        'content': content
    })

print(f"총 {len(posts)}개 포스트 본문 수집 완료.\n")

# A-1. 정책 페이지 실접근 검증
print("-----------------------------------------------------------------")
print("🔍 [A-1] 정책 페이지 실접근 검증 (소개 / 개인정보처리방침 / 연락처)")
policy_pages = [
    ("소개 (About)", f"{BASE_URL}/p/about.html"),
    ("개인정보처리방침 (Privacy Policy)", f"{BASE_URL}/p/privacy-policy.html"),
    ("연락처 (Contact)", f"{BASE_URL}/p/contact.html"),
    ("메인 페이지 (Main)", BASE_URL)
]

page_results = {}
for name, p_url in policy_pages:
    st, html_data = get_url_status(p_url)
    page_results[name] = {
        'url': p_url,
        'status': st,
        'has_content': len(html_data) > 200
    }
    print(f" - {name}: HTTP {st} | URL: {p_url}")

# A-2. 개인정보처리방침 필수 항목 점검
print("\n-----------------------------------------------------------------")
print("🔍 [A-2] 개인정보처리방침 필수 항목 점검")
privacy_url = f"{BASE_URL}/p/privacy-policy.html"
p_st, p_html = get_url_status(privacy_url)

required_terms = {
    "애드센스/쿠키 고지 (AdSense/Cookie)": ["adsense", "cookie", "쿠키", "광고"],
    "제3자 광고 게재 고지 (Third-Party Ads)": ["third-party", "제3자", "타사"],
    "EU 사용자 동의 (GDPR)": ["gdpr", "eu", "유럽"],
    "연락 이메일 (Contact Email)": ["email", "gmail.com", "이메일", "@"]
}

if p_st == 200 and len(p_html) > 100:
    for term_name, keywords in required_terms.items():
        found = any(k in p_html.lower() for k in keywords)
        print(f" - {term_name}: {'✅ 존재' if found else '❌ 누락'}")
else:
    print(f" ❌ 개인정보처리방침 페이지 접근 불가 (HTTP {p_st})")

# A-3. 15편 전수 면책 문구 점검
print("\n-----------------------------------------------------------------")
print("🔍 [A-3] 15편 전수 면책 문구 점검 (건강/의학 조언, 재테크/투자 권유)")

health_disclaimer_kw = ["의학적", "전문가", "치료 목적이 아님", "조언이 아점", "참고", "개인 경험", "의사와 상의", "책임지지 않"]
invest_disclaimer_kw = ["투자 권유가 아님", "개인의 의견", "투자의 책임", "투자 권유", "손실", "참고용"]

disclaimer_table = []
for p in posts:
    num = p['num']
    title = p['title']
    content = p['content']
    
    # Categorize
    is_invest = num in [7, 10, 13]
    cat_type = "재테크" if is_invest else "건강"
    
    has_disclaimer = False
    if is_invest:
        has_disclaimer = any(k in content for k in invest_disclaimer_kw)
    else:
        has_disclaimer = any(k in content for k in health_disclaimer_kw)
        
    disclaimer_table.append({
        'num': num,
        'cat': cat_type,
        'title': title,
        'pass': has_disclaimer
    })
    print(f" - {num:02d}회차 [{cat_type}] '{title[:25]}...': {'O' if has_disclaimer else 'X'}")

# A-4. 금칙 표현 전수 스캔
print("\n-----------------------------------------------------------------")
print("🔍 [A-4] 금칙 표현 전수 스캔 (치료/완치/약 중단/특정 종목/보장)")

forbidden_patterns = [
    (r"(완치|치료되었|낫는다|병이 났다)", "치료·완치 강한 주장"),
    (r"(약(을)? 끊|약 대신|약 복용 중단)", "약 대체·중단 표현"),
    (r"(삼성전자|현대차|SK하이닉스|테슬라|엔비디아|비트코인|코인)", "특정 종목·자산 직접 언급"),
    (r"(원금 보장|수익률 \d+%|무조건 번다|100% 수익)", "수익률 보장·선동 표현"),
    (r"(타이레놀|아스피린|게보린|노스카나|특정 브랜드명)", "특정 의약품/제품 브랜드명")
]

forbidden_findings = []
for p in posts:
    num = p['num']
    title = p['title']
    content = p['content']
    
    # Clean HTML tags for scan
    clean_text = re.sub(r'<[^>]+>', '', content)
    
    for pattern, rule_desc in forbidden_patterns:
        matches = re.findall(pattern, clean_text)
        if matches:
            forbidden_findings.append({
                'num': num,
                'title': title,
                'rule': rule_desc,
                'matches': list(set(matches))
            })
            print(f" ⚠️ 적발 [{num:02d}회차] 규칙: {rule_desc} -> 단어: {set(matches)}")

if not forbidden_findings:
    print(" ✅ 금칙 표현 적발 건 없음!")

# A-5. 모바일 표 렌더링 검수 (02회차)
print("\n-----------------------------------------------------------------")
print("🔍 [A-5] 모바일 표 렌더링 및 overflow-x:auto 검수 (02회차)")
post_2 = [p for p in posts if p['num'] == 2][0]
has_table = "<table" in post_2['content'].lower()
has_overflow = "overflow-x" in post_2['content'].lower() or "overflow-x:auto" in post_2['content'].lower()
print(f" - 02회차 <table> 존재 여부: {'예' if has_table else '아니오'}")
print(f" - overflow-x:auto 래퍼 존재 여부: {'예' if has_overflow else '아니오 (보완 필요)'}")

# A-6. 라벨 및 404 / 이미지 깨짐 검수
print("\n-----------------------------------------------------------------")
print("🔍 [A-6] 사이트 탐색성 및 이미지/링크 상태 점검")
broken_images = []
for p in posts:
    imgs = re.findall(r'src=["\'](http[^"\']+)["\']', p['content'])
    for img_url in imgs:
        img_st, _ = get_url_status(img_url)
        if img_st != 200:
            broken_images.append((p['num'], img_url, img_st))

if broken_images:
    print(f" ⚠️ 이미지 깨짐 적발: {len(broken_images)}건")
    for num, i_url, i_st in broken_images:
        print(f"   [{num:02d}회차] URL: {i_url} (HTTP {i_st})")
else:
    print(" ✅ 15개 포스트 내 모든 이미지 HTTP 200 OK (깨짐 없음!)")

print("\n=================================================================")
print("전수 검증 완료!")
