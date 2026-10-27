# -*- coding: utf-8 -*-
from pathlib import Path
import json
import os
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

# 14번 글 조회 테스트
p14 = blogger.posts().get(blogId=BLOG_ID, postId='5231103442822204831').execute()
print(f"Successfully retrieved post 14: {p14.get('title')}")
