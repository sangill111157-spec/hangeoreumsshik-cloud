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

# 17번 최종 피드 확인
p17 = blogger.posts().get(blogId=BLOG_ID, postId='9009663558624875630').execute()
p01 = blogger.posts().get(blogId=BLOG_ID, postId='8990530060329983304').execute()
p02 = blogger.posts().get(blogId=BLOG_ID, postId='7574070332347419374').execute()

with open('final_round_check.txt', 'w', encoding='utf-8') as out:
    out.write("=== 17번 글 최종 주석 태그 확인 ===\n")
    for line in p17['content'].split('\n'):
        if '※ R은 법정' in line or 'margin-top' in line:
            out.write(line + "\n")
            
    out.write("\n=== 01번 글 내부링크 및 문맥 ===\n")
    for p in re.findall(r'<p>[\s\S]*?</p>', p01['content']):
        if '걷기' in p:
            out.write(p + "\n")
            
    out.write("\n=== 02번 글 내부링크 및 문맥 ===\n")
    for p in re.findall(r'<p>[\s\S]*?</p>', p02['content']):
        if '걷기' in p or '견과' in p:
            out.write(p + "\n")

print("Saved final_round_check.txt")
