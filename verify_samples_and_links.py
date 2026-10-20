# -*- coding: utf-8 -*-
import urllib.request
import json
import re

# 1. 17번 글 margin-top:4px 조정
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SECRETS_DIR = Path(r'C:\Users\sangi\.connectai\secrets')
blog_token = SECRETS_DIR / 'token.json'
creds = Credentials.from_authorized_user_file(
    str(blog_token), ['https://www.googleapis.com/auth/blogger']
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(blog_token, 'w') as f:
        f.write(creds.to_json())

blogger = build('blogger', 'v3', credentials=creds)
BLOG_ID = '5189765270915724664'

p17 = blogger.posts().get(blogId=BLOG_ID, postId='9009663558624875630').execute()
c17 = p17['content']
if 'margin-top:-8px' in c17:
    c17 = c17.replace('margin-top:-8px', 'margin-top:4px')
    blogger.posts().patch(blogId=BLOG_ID, postId='9009663558624875630', body={'content': c17}).execute()
    print("Post 17 footnote margin updated to margin-top:4px.")

# 2. 09번 글 원문 li 전체 텍스트 추출 및 카운트
p09 = blogger.posts().get(blogId=BLOG_ID, postId='6417301061070016808').execute()
c09 = p09['content']
uls_09 = re.findall(r'<ul\b[^>]*>([\s\S]*?)</ul>', c09, re.IGNORECASE)
all_lis_09 = re.findall(r'<li\b[^>]*>([\s\S]*?)</li>', c09, re.IGNORECASE)

print(f"\n=== 09번 글 실측 ===")
print(f"전체 li 개수: {len(all_lis_09)}개, ul 블록 수: {len(uls_09)}개")
for u_i, u_c in enumerate(uls_09, 1):
    u_lis = re.findall(r'<li\b[^>]*>([\s\S]*?)</li>', u_c, re.IGNORECASE)
    print(f"  [블록 {u_i}] {len(u_lis)}개 li:")
    for l_i, l_txt in enumerate(u_lis, 1):
        clean_txt = re.sub(r'<[^>]+>', '', l_txt).strip()
        print(f"    ({l_i}) {clean_txt[:50]}")

# 3. 표본 3편 (06번, 10번, 13번) 원문 li/ul 실측 및 텍스트 전수 출력
sample_posts = [
    {"num": "06", "id": "4823281676221008235", "title": "교대근무자의 수면 관리 — 야간 근무 후 잘 자는 법"},
    {"num": "10", "id": "3175842432832314058", "title": "매일 시세를 못 보는 직장인의 장기 투자 관리 방법"},
    {"num": "13", "id": "6898563342743144149", "title": "초보 때 저지른 실수와 거기서 배운 것"}
]

print("\n=== 표본 3편 (06, 10, 13) 정밀 원문 실측 ===")
for sp in sample_posts:
    p_obj = blogger.posts().get(blogId=BLOG_ID, postId=sp['id']).execute()
    cnt = p_obj['content']
    uls = re.findall(r'<ul\b[^>]*>([\s\S]*?)</ul>', cnt, re.IGNORECASE)
    all_lis = re.findall(r'<li\b[^>]*>([\s\S]*?)</li>', cnt, re.IGNORECASE)
    
    print(f"\n[{sp['num']}번 글] ID: {sp['id']} | Title: {sp['title']}")
    print(f"  -> 전체 li 수: {len(all_lis)}개 | ul 블록 수: {len(uls)}개")
    for u_idx, u_content in enumerate(uls, 1):
        b_lis = re.findall(r'<li\b[^>]*>([\s\S]*?)</li>', u_content, re.IGNORECASE)
        print(f"  [블록 {u_idx}] ({len(b_lis)}개 li):")
        for b_li_idx, b_li_txt in enumerate(b_lis, 1):
            c_txt = re.sub(r'<[^>]+>', '', b_li_txt).strip()
            print(f"    ({b_li_idx}) {c_txt}")

# 4. 작업 C 표본 (01, 02, 06번) 압축 문맥 및 내부링크 URL 검증
c_samples = [
    {"num": "01", "id": "8990530060329983304", "title": "만성피로와 뱃살에 시달리던 3교대 직장인이 식습관을 바꾼 3개월 기록"},
    {"num": "02", "id": "7574070332347419374", "title": "허리둘레 36에서 32로, 몸무게 75에서 68kg — 무엇을 바꿨나"},
    {"num": "06", "id": "4823281676221008235", "title": "교대근무자의 수면 관리 — 야간 근무 후 잘 자는 법"}
]

print("\n=== 작업 C 표본 (01, 02, 06) 압축 문맥 및 내부 링크 검증 ===")
for cs in c_samples:
    p_obj = blogger.posts().get(blogId=BLOG_ID, postId=cs['id']).execute()
    cnt = p_obj['content']
    print(f"\n[{cs['num']}번 글] ID: {cs['id']}")
    
    # 걷기 관련 내부링크 (14번 글)
    walk_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', cnt)
    for href, anchor in walk_links:
        print(f"  [내부링크 발견] Anchor: '{anchor}' -> Href: '{href}'")
        
    # 걷기 / 견과류 주변 문맥 출력
    paras = re.findall(r'<p>[\s\S]*?</p>', cnt)
    for p_tag in paras:
        if '걷기' in p_tag or '견과' in p_tag:
            clean_p = re.sub(r'<[^>]+>', '', p_tag).strip()
            print(f"  [문맥 단락] {p_tag}")

