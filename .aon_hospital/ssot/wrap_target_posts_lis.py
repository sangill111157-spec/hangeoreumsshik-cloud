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

def wrap_consecutive_lis(html):
    """
    HTML 내에서 <ul> 또는 <ol>로 감싸지지 않은 연속된 <li> 태그 묶음들을 
    각각 <ul>...</ul>로 감싼다.
    사이에 다른 태그나 텍스트가 있으면 별개의 <ul>로 분리된다.
    """
    # 이미 <ul>이나 <ol> 내부에 있는 li는 그대로 두고,
    # 그렇지 않은 연속된 <li>...</li> 블록을 <ul>로 래핑
    
    # 1. <ul>...</ul>, <ol>...</ol> 내부를 보호하기 위해 임시 치환하거나,
    # 정규표현식으로 처리.
    
    # 간단하고 안전한 방식:
    # <ul>/ol 외부의 (?:(?:<li\b[^>]*>.*?</li>|\s*)+) 패턴 매칭
    
    # 먼저 <ul>/ol 블록을 보존 토큰으로 치환
    placeholders = {}
    def repl_existing_list(m):
        key = f"__EXISTING_LIST_{len(placeholders)}__"
        placeholders[key] = m.group(0)
        return key

    # <ul>...</ul> 또는 <ol>...</ol> (중첩 고려 가능하도록)
    # 기존 글들에는 ul이 없거나 거의 없었음
    temp_html = re.sub(r'<(ul|ol)\b[^>]*>[\s\S]*?</\1>', repl_existing_list, html, flags=re.IGNORECASE)

    # 이제 남아있는 연속된 <li>...</li> 블록 찾기
    # (공백, 개행 포함)
    def wrap_lis(m):
        matched_str = m.group(0).strip()
        return f"\n<ul>\n{matched_str}\n</ul>\n"

    # 연속된 하나 이상의 <li>...</li>
    # li 안에 p, strong, a 등이 있을 수 있으므로 .*?</li>
    orphan_pattern = re.compile(r'(?:<li\b[^>]*>[\s\S]*?</li>(?:\s*))+', re.IGNORECASE)
    
    result_html = orphan_pattern.sub(wrap_lis, temp_html)

    # 기존 리스트 복원
    for key, val in placeholders.items():
        result_html = result_html.replace(key, val)

    return result_html

target_posts = [
    {"num": "04", "id": "4072797504508800553", "title": "교대근무자의 무너진 식사 리듬"},
    {"num": "09", "id": "6417301061070016808", "title": "교대근무자가 챙겨 먹기 좋은 간단한 도시락·간식"},
    {"num": "15", "id": "4150316841132855829", "title": "물 많이 마시기, 나만의 루틴 만들기"}
]

for p_info in target_posts:
    post = blogger.posts().get(blogId=BLOG_ID, postId=p_info['id']).execute()
    old_content = post['content']
    new_content = wrap_consecutive_lis(old_content)
    
    # orphan li 검사
    orphan_lis_old = len(re.findall(r'<li\b', old_content)) - len(re.findall(r'<ul\b', old_content))*0 # 간단 체크
    ul_count = len(re.findall(r'<ul\b', new_content))
    li_count = len(re.findall(r'<li\b', new_content))
    
    print(f"[{p_info['num']}번 글 - {p_info['id']}]")
    print(f"  총 <li> 수: {li_count}개 | 생성된 <ul> 묶음: {ul_count}개")
    
    # API로 저장
    blogger.posts().patch(blogId=BLOG_ID, postId=p_info['id'], body={'content': new_content}).execute()
    print(f"  Post {p_info['num']} successfully updated in Blogger API.")

