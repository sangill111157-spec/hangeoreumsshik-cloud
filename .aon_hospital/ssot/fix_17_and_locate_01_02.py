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

# 1. 17번 글 h3 태그 margin-top:16px 복원
POST_17_ID = '9009663558624875630'
p17 = blogger.posts().get(blogId=BLOG_ID, postId=POST_17_ID).execute()
c17 = p17['content']

# h3만 정확히 margin-top:16px로 치환
c17_fixed = c17.replace('<h3 style="color:#333; margin-top:4px;">(1) 1차 검사 항목</h3>', '<h3 style="color:#333; margin-top:16px;">(1) 1차 검사 항목</h3>')
c17_fixed = c17_fixed.replace('<h3 style="color:#333; margin-top:4px;">(2) 2차 정밀 검사 항목 (필요시)</h3>', '<h3 style="color:#333; margin-top:16px;">(2) 2차 정밀 검사 항목 (필요시)</h3>')

p17['content'] = c17_fixed
blogger.posts().update(blogId=BLOG_ID, postId=POST_17_ID, body=p17).execute()
print("Post 17 h3 margin-top:16px restored.")

# 2. 01번 글 구조 전체 분석
p01 = blogger.posts().get(blogId=BLOG_ID, postId='8990530060329983304').execute()
c01 = p01['content']

with open('post_01_full_sections.txt', 'w', encoding='utf-8') as out:
    out.write("=== 01번 글 전체 섹션 및 문맥 분석 ===\n")
    # h2 태그로 섹션 분할
    sections = re.split(r'(<h2[^>]*>.*?</h2>)', c01)
    for sec in sections:
        out.write(sec + "\n---\n")

# 3. 02번 글 구조 전체 분석
p02 = blogger.posts().get(blogId=BLOG_ID, postId='7574070332347419374').execute()
c02 = p02['content']
with open('post_02_full_sections.txt', 'w', encoding='utf-8') as out:
    out.write("=== 02번 글 전체 섹션 및 문맥 분석 ===\n")
    sections = re.split(r'(<h2[^>]*>.*?</h2>)', c02)
    for sec in sections:
        out.write(sec + "\n---\n")

print("Saved section analyses.")
