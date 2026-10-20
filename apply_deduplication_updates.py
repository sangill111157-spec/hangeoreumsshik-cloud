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

# 링크 URL
WALK_URL = "https://connect-ai-shin.blogspot.com/2026/08/3.html" # 14번 글
NUTS_URL = "https://connect-ai-shin.blogspot.com/2026/07/blog-post_28.html" # 09번 글

# 1. 01번 글 (Post ID: 8990530060329983304)
# 수정 대상: <p><strong>네 번째</strong>, 가벼운 걷기를 병행했어요. ...</p>
p01 = blogger.posts().get(blogId=BLOG_ID, postId='8990530060329983304').execute()
c01 = p01['content']
target01 = "<p><strong>네 번째</strong>, 가벼운 걷기를 병행했어요. 퇴근 후에 무리한 운동은 무리였지만, 30분 정도 천천히 걷는 건 지속할 수 있었어요. 특히 야간 근무 퇴근 후 잠깐 걸으면 오히려 수면 질이 좋아지더라고요.</p>"
repl01 = f'<p><strong>네 번째</strong>, 퇴근 후 15~20분 가벼운 걷기를 병행했습니다. 무리한 운동 대신 천천히 걷는 루틴을 만들면서 긴장이 풀리고 수면의 질이 크게 개선되었습니다. (자세한 실천 요령은 <a href="{WALK_URL}">3교대 걷기 습관 실천 팁 글</a>을 참고해 보세요.)</p>'
if target01 in c01:
    c01 = c01.replace(target01, repl01)
    blogger.posts().patch(blogId=BLOG_ID, postId='8990530060329983304', body={'content': c01}).execute()
    print("Post 01 updated.")
else:
    print("Post 01 target not found or already updated.")

# 2. 02번 글 (Post ID: 7574070332347419374)
# 수정 대상 1 (견과류): <p>대신 <strong>비율을 바꾸는</strong> 쪽으로 접근했습니다. 일주일에 가공식품을 먹는 횟수를 기록해보고, 그 중 2~3번을 삶은 달걀 + 방울토마토 + 견과류로 대체했어요. ...</p>
# 수정 대상 2 (걷기): <h2>4. 가벼운 걷기 병행</h2> 하단 단락들
p02 = blogger.posts().get(blogId=BLOG_ID, postId='7574070332347419374').execute()
c02 = p02['content']

old_nuts_02 = "<p>대신 <strong>비율을 바꾸는</strong> 쪽으로 접근했습니다. 일주일에 가공식품을 먹는 횟수를 기록해보고, 그 중 2~3번을 삶은 달걀 + 방울토마토 + 견과류로 대체했어요. 이걸 미리 소분해서 가방에 넣고 다녔습니다. 거창한 도시락이 아니라 그냥 소분 간식 수준이었지만, 한 끼의 질이 달라졌어요.</p>"
new_nuts_02 = f'<p>대신 <strong>비율을 바꾸는</strong> 쪽으로 접근했습니다. 주 2~3회는 컵라면 대신 삶은 달걀, 방울토마토, 무염 견과류 소분 팩을 가방에 챙겨 다니며 야간 허기를 달랬습니다. (상세한 간식 구성법은 <a href="{NUTS_URL}">교대근무자 간단 도시락·간식 가이드</a>를 참고하시기 바랍니다.)</p>'

old_walk_02 = '<p>처음엔 운동이 너무 부담스러웠어요. 야간 퇴근하면 눕고 싶지, 헬스장 갈 체력이 없었거든요. 그래서 일단 <strong>걷기</strong>만 했습니다.</p>\n\n<p>퇴근 후 집까지 걸어가는 거리를 조금 더 늘리거나, 가까운 공원을 한 바퀴 도는 식으로요. 30분이 목표였는데, 어떤 날은 15분밖에 못 걸은 날도 있었어요. 그래도 이어갔습니다.</p>\n\n<p>신기하게도 야간 퇴근 후 조금 걷고 자면, 그냥 바로 누워 잘 때보다 오히려 수면 질이 나았어요. 잠들기까지 걸리는 시간이 짧아졌고, 중간에 깨는 횟수도 줄었습니다.</p>'
new_walk_02 = f'<p>처음엔 고강도 운동 대신 퇴근 후 15~20분간 가볍게 <strong>걷기</strong>만 실천했습니다. 신기하게도 가볍게 걷고 잠자리에 들면 뇌의 피로가 풀려 수면의 질이 훨씬 좋아졌습니다. (구체적인 동선 설계와 실천법은 <a href="{WALK_URL}">3교대 걷기 습관 팁 글</a>에 정리해 두었습니다.)</p>'

if old_nuts_02 in c02:
    c02 = c02.replace(old_nuts_02, new_nuts_02)
if old_walk_02 in c02:
    c02 = c02.replace(old_walk_02, new_walk_02)

blogger.posts().patch(blogId=BLOG_ID, postId='7574070332347419374', body={'content': c02}).execute()
print("Post 02 updated.")

# 3. 04번 글 (Post ID: 4072797504508800553)
# 수정 대상: 견과류 간식 서술 압축
p04 = blogger.posts().get(blogId=BLOG_ID, postId='4072797504508800553').execute()
c04 = p04['content']

old_p04_sec = '<p><strong>미리 준비해서 가져가는 것:</strong></p>\n<li>삶은 달걀 2개 (출근 전 미리 준비)</li>\n<li>방울토마토 한 줌 (지퍼백에 소분)</li>\n<li>견과류 믹스 한 주먹 (편의점에서 사도 됨)</li>\n\n<p>이게 전부예요. 귀찮아 보이지만, 달걀 2개 삶는 데 10분 걸리고, 그걸 가방에 넣는 데 2분 걸립니다. 이 12분 투자가 야간 새벽 중간의 폭식을 막아줬어요.</p>'
new_p04_sec = f'<p>야간 근무 중 폭식을 막기 위해 삶은 달걀 2개, 방울토마토, 무염 견과류 한 줌을 지퍼백에 챙겨 다녔습니다. 출근 전 10분 투자로 준비한 건강 간식이 새벽 허기를 깔끔하게 달래주었습니다. (구체적인 소분 요령과 팁은 <a href="{NUTS_URL}">교대근무자 간단 도시락·간식 글</a>을 참고하세요.)</p>'

if old_p04_sec in c04:
    c04 = c04.replace(old_p04_sec, new_p04_sec)
    blogger.posts().patch(blogId=BLOG_ID, postId='4072797504508800553', body={'content': c04}).execute()
    print("Post 04 updated.")
else:
    print("Post 04 section not matched, checking alternate replacement...")

# 4. 06번 글 (Post ID: 4823281676221008235)
# 수정 대상 1 (걷기): <h2 ...>1. 퇴근 후 아침 걷기의 효과</h2> 하단 단락 압축
# 수정 대상 2 (견과류): <h2 ...>2. 잘 자기 위해 아침 식사를 바꾸다</h2> 내 견과류 링크
p06 = blogger.posts().get(blogId=BLOG_ID, postId='4823281676221008235').execute()
c06 = p06['content']

old_walk_06 = '<p>보통 야간 근무를 마치고 나면 조금이라도 빨리 누워야 더 많이 잘 수 있다고 생각하기 쉽습니다. 그래서 저도 예전에는 아침 6시 퇴근 후 씻지도 않고 바로 침대로 직행하곤 했어요. 하지만 그렇게 억지로 누우면 뇌가 아직 각성 상태에 있어서 오히려 잠이 들기까지 한 시간 이상 뒤척이는 경우가 많았습니다.</p>\n\n<p>그래서 저는 반대로 <strong>퇴근 후 가벼운 걷기</strong>를 루틴에 포함시켰습니다. 집까지 약 20~30분 정도 천천히 걷거나, 집 근처 공원을 가볍게 한 바퀴 돌고 들어가는 것이었는데요. </p>\n\n<p>의아하게 생각할 수도 있습니다. 이미 몸이 피곤한 상태에서 또 몸을 쓰는 게 말이 안 된다고 느낄 수 있으니까요. 하지만 가벼운 속도로 산책하듯 걸으면 긴장되어 있던 몸의 근육이 이완되고, 야간 근무 중 쌓였던 뇌의 스트레스가 풀리는 효과가 있었습니다. 특히 아침 걷기를 한 날은 뇌가 수면을 취할 준비를 서서히 마친 상태가 되어, 침대에 누웠을 때 잠드는 시간이 눈에 띄게 단축되는 것을 경험했습니다.</p>'
new_walk_06 = f'<p>야간 근무 직후 바로 눕기보다 <strong>퇴근 후 15~20분간 가볍게 걷는 루틴</strong>을 도입했습니다. 산책하듯 천천히 걸으면 근무 중 긴장했던 근육이 이완되고 뇌 스트레스가 완화되어 침대에 누웠을 때 훨씬 빠르게 숙면에 들 수 있었습니다. (퇴근길 동선 설계 등 상세 실천법은 <a href="{WALK_URL}">3교대 걷기 습관 실천 팁</a>을 참고하세요.)</p>'

old_nuts_06 = '<li>대신 야간 근무 중간 시간인 새벽 2~3시에 미리 준비해 간 삶은 달걀 2개와 견과류, 방울토마토 등으로 미리 허기를 달래 두었습니다.</li>'
new_nuts_06 = f'<li>대신 야간 근무 중간 시간인 새벽 2~3시에 미리 준비해 간 삶은 달걀, 견과류, 방울토마토(<a href="{NUTS_URL}">간단 간식 준비법 참고</a>) 등으로 미리 허기를 달래 두었습니다.</li>'

if old_walk_06 in c06:
    c06 = c06.replace(old_walk_06, new_walk_06)
if old_nuts_06 in c06:
    c06 = c06.replace(old_nuts_06, new_nuts_06)

blogger.posts().patch(blogId=BLOG_ID, postId='4823281676221008235', body={'content': c06}).execute()
print("Post 06 updated.")

# 5. 11번 글 (Post ID: 8415417029048376390)
# 수정 대상: 퇴근 후 가벼운 걷기 내부 링크 연결
p11 = blogger.posts().get(blogId=BLOG_ID, postId='8415417029048376390').execute()
c11 = p11['content']
old_walk_11 = '식습관(야식 통제, 물 1.5리터 이상 섭취)과 퇴근 후 가벼운 걷기 같은 생활 관리를 집요하게 병행했습니다.'
new_walk_11 = f'식습관(야식 통제, 물 1.5리터 이상 섭취)과 <a href="{WALK_URL}">퇴근 후 가벼운 걷기</a> 같은 생활 관리를 집요하게 병행했습니다.'
if old_walk_11 in c11:
    c11 = c11.replace(old_walk_11, new_walk_11)
    blogger.posts().patch(blogId=BLOG_ID, postId='8415417029048376390', body={'content': c11}).execute()
    print("Post 11 updated.")

# 6. 12번 글 (Post ID: 3697517922690251482)
# 수정 대상: 걷기 관련 섹션 압축 및 내부 링크
p12 = blogger.posts().get(blogId=BLOG_ID, postId='3697517922690251482').execute()
c12 = p12['content']
old_walk_12 = '<p>앞선 글들에서도 퇴근 후 수면이나 건강 관리를 위한 걷기의 유용성을 여러 번 말씀드렸는데요. 걷기는 제가 스트레스를 흘려보내는 데 가장 자주 쓴 방법이기도 합니다.</p>\n\n<li>몸을 가볍게 움직이며 걷는 행위는 마음의 긴장을 풀고 답답했던 기분을 환기하는 데 큰 도움이 됩니다.</li>\n<li>복잡한 생각이나 직장에서 쌓인 스트레스가 머릿속을 지배할 때, 이어폰을 빼고 주변 풍경을 보며 천천히 발을 내딛는 것에만 집중해 봅니다.</li>\n<li>20~30분 정도 걸으며 이마에 땀이 살짝 맺히기 시작할 때쯤이면 머릿속을 복잡하게 만들던 걱정이나 화가 한결 누그러지고, 마음이 평온해지는 것을 몸소 느낄 수 있습니다.</li>'
new_walk_12 = f'<p>걷기는 교대근무로 곤두선 스트레스를 흘려보내는 데 가장 효과적인 방법이었습니다. 퇴근길이나 비번 날 15~20분간 천천히 걸으며 발걸음에 집중하면 복잡했던 걱정이 누그러지고 마음에 여유가 생깁니다. (일상 속 구체적인 걷기 루틴은 <a href="{WALK_URL}">3교대 걷기 습관 실천 가이드</a>를 참고하세요.)</p>'

old_next_12 = "<p>다음 글에서는 제 몸무게를 75kg에서 68kg으로 되돌리는 데 가장 큰 공헌을 한, 돈 한 푼 들지 않았던 '걷기'를 일상에서 습관으로 정착시킨 구체적인 실천 요령을 다뤄보겠습니다.</p>"
new_next_12 = f"<p>이어지는 글에서는 제 체중과 컨디션 관리에 큰 역할을 한 <a href=\"{WALK_URL}\">'걷기 습관화 실천 요령'</a>을 자세히 확인하실 수 있습니다.</p>"

if old_walk_12 in c12:
    c12 = c12.replace(old_walk_12, new_walk_12)
if old_next_12 in c12:
    c12 = c12.replace(old_next_12, new_next_12)

blogger.posts().patch(blogId=BLOG_ID, postId='3697517922690251482', body={'content': c12}).execute()
print("Post 12 updated.")
