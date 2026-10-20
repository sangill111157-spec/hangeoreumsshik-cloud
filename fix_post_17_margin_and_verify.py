# -*- coding: utf-8 -*-
from pathlib import Path
import json, re
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

# 1. 17번 글 margin-top:4px 확실하게 교체 및 업데이트
POST_17_ID = '9009663558624875630'
p17 = blogger.posts().get(blogId=BLOG_ID, postId=POST_17_ID).execute()
c17 = p17['content']

print("=== 17번 글 마진 패치 전 확인 ===")
# 정규표현식으로 margin-top 관련 스타일 치환
c17_new = re.sub(r'margin-top:\s*-?\d+px;', 'margin-top:4px;', c17)
# 또는 스타일 문자열 직접 치환
if 'margin-top:-8px' in c17:
    c17_new = c17.replace('margin-top:-8px', 'margin-top:4px')
    print("Found 'margin-top:-8px', replacing...")
else:
    print("Exact 'margin-top:-8px' string search, check regex...")

# blogger.posts().update (전체 객체 교체)를 사용하여 안전하고 확실하게 반영
p17['content'] = c17_new
updated_p17 = blogger.posts().update(blogId=BLOG_ID, postId=POST_17_ID, body=p17).execute()
print("Post 17 update() called.")

# 다시 가져와서 확인
check_p17 = blogger.posts().get(blogId=BLOG_ID, postId=POST_17_ID).execute()
print("=== 17번 글 저장 후 원문 확인 ===")
for line in check_p17['content'].split('\n'):
    if '※ R은 법정' in line or 'margin-top' in line:
        print("Line in 17:", line)


# 2. 01번, 02번 글 원문 재확인
print("\n=== 01번, 02번 글 저장 원문 확인 ===")
for pid, num in [('8990530060329983304', '01'), ('7574070332347419374', '02')]:
    post = blogger.posts().get(blogId=BLOG_ID, postId=pid).execute()
    cnt = post['content']
    print(f"\n[{num}번 글: {post['title']}] (ID: {pid})")
    
    # 링크 태그 출력
    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', cnt)
    for href, anchor in links:
        if 'blogger.googleusercontent' not in href:
            print(f"  -> 내부링크: '{anchor.strip()}' => {href}")
    
    # 걷기/견과류 단락 출력
    paras = re.findall(r'<p>[\s\S]*?</p>', cnt)
    for p in paras:
        if '걷기' in p or '견과' in p:
            print(f"  -> 본문 단락: {p}")

