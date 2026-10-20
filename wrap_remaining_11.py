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

# 09번 글 상세 점검
p09 = blogger.posts().get(blogId=BLOG_ID, postId='6417301061070016808').execute()
c09 = p09['content']
uls_09 = re.findall(r'<ul\b[^>]*>[\s\S]*?</ul>', c09, re.IGNORECASE)
lis_09 = re.findall(r'<li\b', c09, re.IGNORECASE)

print("=== 09번 글 실측 상세 ===")
print(f"총 <ul> 블록 수: {len(uls_09)}개, 총 <li> 개수: {len(lis_09)}개")
for idx, ul in enumerate(uls_09, 1):
    items = re.findall(r'<li\b[^>]*>[\s\S]*?</li>', ul, re.IGNORECASE)
    print(f"  [블록 {idx}] ({len(items)}개 li)")
    for it in items:
        # 태그 제거 텍스트 일부
        txt = re.sub(r'<[^>]+>', '', it).strip()
        print(f"    - {txt[:40]}")

# 래핑 함수 (이전과 동일한 정밀 분리 래퍼)
def wrap_consecutive_lis(html):
    placeholders = {}
    def repl_existing_list(m):
        key = f"__EXISTING_LIST_{len(placeholders)}__"
        placeholders[key] = m.group(0)
        return key

    temp_html = re.sub(r'<(ul|ol)\b[^>]*>[\s\S]*?</\1>', repl_existing_list, html, flags=re.IGNORECASE)

    def wrap_lis(m):
        matched_str = m.group(0).strip()
        return f"\n<ul>\n{matched_str}\n</ul>\n"

    orphan_pattern = re.compile(r'(?:<li\b[^>]*>[\s\S]*?</li>(?:\s*))+', re.IGNORECASE)
    result_html = orphan_pattern.sub(wrap_lis, temp_html)

    for key, val in placeholders.items():
        result_html = result_html.replace(key, val)

    return result_html

# 나머지 11편 글 목록
# 01, 02, 05, 06, 07, 08, 10, 11, 12, 13, 14
remaining_posts = [
    {"num": "01", "id": "8990530060329983304", "title": "만성피로와 뱃살에 시달리던 3교대 직장인이 식습관을 바꾼 3개월 기록"},
    {"num": "02", "id": "7574070332347419374", "title": "허리둘레 36에서 32로, 몸무게 75에서 68kg — 무엇을 바꿨나"},
    {"num": "05", "id": "5305806140306993122", "title": "피부 트러블·비염·발뒤꿈치 각질까지 — 몸이 보낸 신호와 생활습관"},
    {"num": "06", "id": "4823281676221008235", "title": "교대근무자의 수면 관리 — 야간 근무 후 잘 자는 법"},
    {"num": "07", "id": "2130301447595973624", "title": "3교대 직장인이 주식(장기 투자)을 시작한 이유와 첫 몇 개월"},
    {"num": "08", "id": "2256816236319252852", "title": "에너지드링크·믹스커피를 줄인 경험과 그 후 변화"},
    {"num": "10", "id": "3175842432832314058", "title": "매일 시세를 못 보는 직장인의 장기 투자 관리 방법"},
    {"num": "11", "id": "8415417029048376390", "title": "3교대 하면서 병원·건강검진 챙기는 현실적인 방법"},
    {"num": "12", "id": "3697517922690251482", "title": "불규칙한 생활 속 스트레스 관리법"},
    {"num": "13", "id": "6898563342743144149", "title": "초보 때 저지른 실수와 거기서 배운 것"},
    {"num": "14", "id": "5231103442822204831", "title": "걷기를 습관으로 만든 방법과 3교대 속 실천 팁"}
]

print("\n=== 나머지 11편 글 <ul> 래핑 시작 ===")
wrap_results = []
for p in remaining_posts:
    post_obj = blogger.posts().get(blogId=BLOG_ID, postId=p['id']).execute()
    old_c = post_obj['content']
    new_c = wrap_consecutive_lis(old_c)
    
    # API 업데이트
    blogger.posts().patch(blogId=BLOG_ID, postId=p['id'], body={'content': new_c}).execute()
    
    # 실측
    uls = re.findall(r'<ul\b[^>]*>[\s\S]*?</ul>', new_c, re.IGNORECASE)
    lis = re.findall(r'<li\b', new_c, re.IGNORECASE)
    
    block_details = []
    for b_i, u_block in enumerate(uls, 1):
        b_lis = len(re.findall(r'<li\b', u_block, re.IGNORECASE))
        block_details.append(f"블록{b_i}({b_lis}개)")
    
    wrap_results.append({
        'num': p['num'],
        'id': p['id'],
        'title': p['title'],
        'li_count': len(lis),
        'ul_count': len(uls),
        'blocks': ", ".join(block_details)
    })
    print(f"[{p['num']}번 글 - {p['id']}] <li> {len(lis)}개 / <ul> {len(uls)}개 -> 완료")

with open('remaining_11_wrapped_report.json', 'w', encoding='utf-8') as out:
    json.dump(wrap_results, out, ensure_ascii=False, indent=2)

print("\nAll 11 posts wrapped successfully. Report saved to remaining_11_wrapped_report.json")
