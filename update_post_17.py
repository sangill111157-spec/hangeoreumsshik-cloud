# -*- coding: utf-8 -*-
from pathlib import Path
import json
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
POST_17_ID = '9009663558624875630'

p17 = blogger.posts().get(blogId=BLOG_ID, postId=POST_17_ID).execute()
content = p17['content']

# 1. 조문 교체
old_law = '이 결과표에는 <strong>산업안전보건법 시행규칙 제209조</strong>에 따른 건강관리구분이 알파벳 기호로 표시됩니다.'
new_law = '이 결과표에는 <strong>고용노동부 고시 「근로자 건강진단 실시기준」 별표 4</strong>에 따른 건강관리구분이 알파벳 기호로 표시됩니다.'
if old_law in content:
    content = content.replace(old_law, new_law)
    print("Replaced law citation successfully.")
else:
    # 혹시 태그 차이가 있을 경우
    content = content.replace('산업안전보건법 시행규칙 제209조', '고용노동부 고시 「근로자 건강진단 실시기준」 별표 4')
    print("Replaced law citation with fallback.")

# 2. 표 하단에 R 및 U 관련 명확한 법정 주석 추가
old_r_row = """<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>R</strong></td>
<td style="border:1px solid #ddd; padding:8px;">2차 건강진단 대상자 (재검 필요)</td>
<td style="border:1px solid #ddd; padding:8px;">기한 내 2차 정밀검사 수검</td>
</tr>
</table>"""

new_r_row = """<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>R</strong></td>
<td style="border:1px solid #ddd; padding:8px;">2차 건강진단 대상자 (검진기관 재검 통보)</td>
<td style="border:1px solid #ddd; padding:8px;">통보 기한 내 2차 정밀검진 수검</td>
</tr>
<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>U</strong></td>
<td style="border:1px solid #ddd; padding:8px;">판정 보류 / 판정 불능</td>
<td style="border:1px solid #ddd; padding:8px;">검사 누락 항목 추가 검사 후 재판정</td>
</tr>
</table>
<p style="font-size:0.9em; color:#666; margin-top:-8px;"><em>※ R은 법정 건강관리구분이 아닌 검진기관의 2차 검진(재검) 안내 표기이며, 법령(별표 4)상 정식 구분 기호는 A, C1, C2, D1, D2 및 U(판정불능)입니다.</em></p>"""

if old_r_row in content:
    content = content.replace(old_r_row, new_r_row)
    print("Updated table with U and R footnote successfully.")
else:
    # fallback
    content = content.replace('</table>', '</table>\n<p style="font-size:0.9em; color:#666; margin-top:-8px;"><em>※ R은 법정 건강관리구분이 아닌 검진기관의 2차 검진(재검) 안내 표기이며, 법령(별표 4)상 정식 구분 기호는 A, C1, C2, D1, D2 및 U(판정불능)입니다.</em></p>')
    print("Added footnote with fallback.")

blogger.posts().patch(blogId=BLOG_ID, postId=POST_17_ID, body={'content': content}).execute()
print("Post 17 successfully patched in Blogger API.")
