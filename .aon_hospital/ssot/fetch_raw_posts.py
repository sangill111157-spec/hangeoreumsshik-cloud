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

# 전체 글 가져오기
posts_res = blogger.posts().list(blogId=BLOG_ID, status=['LIVE'], maxResults=50).execute()
items = posts_res.get('items', [])
items_sorted = sorted(items, key=lambda x: x['published'])

with open('posts_raw_content.json', 'w', encoding='utf-8') as f:
    json.dump([{
        'index': i+1,
        'id': p['id'],
        'title': p['title'],
        'url': p['url'],
        'published': p['published'],
        'content': p['content']
    } for i, p in enumerate(items_sorted)], f, ensure_ascii=False, indent=2)

print("Saved all raw posts to posts_raw_content.json")
