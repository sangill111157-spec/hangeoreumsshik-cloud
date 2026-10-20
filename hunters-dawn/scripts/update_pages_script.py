import os
import sys
import json
import urllib.request
import urllib.parse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

TOKEN_PATH = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.json'
TOKEN_PICKLE = r'c:\Users\sangi\Downloads\shin-agent\hunters-dawn\token.pickle'
BLOG_ID = "484838686708681313" # connect-ai-shin.blogspot.com or query pages

print("=================================================================")
print("📋 [작업 지시서 #18] Blogger 페이지 (About / Contact) 업데이트 진행")
print("=================================================================")

# Load credentials
creds = None
if os.path.exists(TOKEN_PICKLE):
    import pickle
    with open(TOKEN_PICKLE, 'rb') as f:
        creds = pickle.load(f)
elif os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/blogger'])

if not creds:
    print("Blogger API OAuth Token not found directly, using direct page inspection...")
else:
    print("Blogger API Credentials loaded!")

# 1. Representative Approved About Page HTML
ABOUT_HTML = """<h2>블로그 소개</h2>

<p>안녕하세요. 불규칙한 3교대 근무를 하며 건강과 식습관을 관리해온 기록을 남기고 있는 3교대 직장인 길잡이입니다.</p>

<p>오랫동안 밤낮이 바뀌는 생활을 반복하면서 만성피로와 소화 문제, 무너진 식사 리듬으로 고생했어요. 체중이 75kg, 허리둘레가 36인치까지 늘었을 때는 '이미 늦은 게 아닐까' 하는 생각까지 들었답니다. 또한 20여 년간 강직성 척추염을 병원 치료를 받으며 관리해오고 있어, 일상 속 건강 관리가 얼마나 중요한지 오래 체감해왔습니다.</p>

<p>건강 정보를 찾아봐도 새벽에 퇴근해 낮에 자야 하는 사람에게 맞는 이야기는 드물었어요. 하루 한 시간 운동하라거나 식단을 철저히 지키라는 조언은 맞는 말이지만, 교대근무 현실에서 그대로 지켜내기가 쉽지 않았습니다. 그래서 제가 직접 시도해보고 실패도 해가며 겪은 과정을 그대로 남겨두기로 했어요. 비슷한 근무 환경에 계신 분들이 조금 덜 헤매셨으면 하는 마음입니다.</p>

<h3>이 블로그에서 다루는 이야기</h3>

<p>주로 다루는 주제는 식습관을 바꾸며 겪은 변화, 야간 근무 후의 수면 관리, 교대 패턴에 맞춘 식사 리듬 잡기, 도시락과 간식 준비, 병원 진료와 건강검진을 놓치지 않는 방법, 그리고 불규칙한 생활 속 스트레스 관리입니다. 여기에 더해 매일 시세를 확인하기 어려운 교대근무자로서 장기 투자를 어떻게 이어왔는지에 대한 경험도 함께 기록하고 있어요.</p>

<h3>글을 쓸 때 지키는 것</h3>

<p>이곳의 모든 글은 제가 겪은 일을 정리한 개인 기록이에요. 의학적 조언이나 진단이 아니며, 건강과 관련된 판단은 반드시 전문 의료진과 상의하셔야 합니다. 재테크 글 역시 개인의 경험담일 뿐 특정 상품이나 종목에 대한 투자 권유가 아니랍니다.</p>

<p>또한 특정 제품이나 브랜드를 추천하지 않고, 효과를 과장하거나 단정하는 표현은 쓰지 않으려 합니다. 제 경우에는 이랬다는 기록일 뿐, 같은 방법이 모두에게 맞는다고 말씀드릴 수는 없으니까요.</p>

<h3>연락</h3>

<p>블로그 내용에 대한 문의나 비슷한 경험 공유는 언제든 환영합니다.</p>

<p>이메일: sangill111157@gmail.com</p>

<p>연락처 페이지: <a href="https://connect-ai-shin.blogspot.com/p/contact.html">문의하기</a></p>

<p>읽어주셔서 감사합니다. 오늘도 무탈한 하루 보내시길 바랍니다.</p>"""

# 2. Contact Page HTML (Preserving 100% original text, ONLY removing 3 emojis)
CONTACT_ORIGINAL_TEXT = """안녕하세요, 3교대 직장인 길잡이 블로그를 운영하고 있습니다.

이메일 문의
블로그 내용에 대한 문의나 경험 공유, 기타 제안사항이 있으시면 아래 이메일로 편하게 연락해 주세요.

이메일: sangill111157@gmail.com

안내 사항
- 문의 주신 내용은 확인하는 대로 성심껏 답변드리겠습니다 (통상 2~3영업일 소요).
- 문의 제목에 대략적인 주제를 적어주시면 더 빠른 답변이 가능합니다.
- 광고·스팸성 메일이나 부적절한 내용은 별도 안내 없이 처리될 수 있습니다.

참고 및 유의사항
- 본 블로그의 모든 정보는 개인의 경험과 정보 공유 목적이며, 의학적 조언이나 진단·치료를 대신할 수 없습니다.
- 제품 추천·판매, 다단계 등 상업적 목적의 문의는 사양합니다.

소중한 연락 감사드립니다."""

CONTACT_HTML = """<h2>문의하기</h2>

<p>안녕하세요, 3교대 직장인 길잡이 블로그를 운영하고 있습니다.</p>

<h3>이메일 문의</h3>
<p>블로그 내용에 대한 문의나 경험 공유, 기타 제안사항이 있으시면 아래 이메일로 편하게 연락해 주세요.</p>
<p><b>이메일:</b> sangill111157@gmail.com</p>

<h3>안내 사항</h3>
<ul>
  <li>문의 주신 내용은 확인하는 대로 성심껏 답변드리겠습니다 (통상 2~3영업일 소요).</li>
  <li>문의 제목에 대략적인 주제를 적어주시면 더 빠른 답변이 가능합니다.</li>
  <li>광고·스팸성 메일이나 부적절한 내용은 별도 안내 없이 처리될 수 있습니다.</li>
</ul>

<h3>참고 및 유의사항</h3>
<ul>
  <li>본 블로그의 모든 정보는 개인의 경험과 정보 공유 목적이며, 의학적 조언이나 진단·치료를 대신할 수 없습니다.</li>
  <li>제품 추천·판매, 다단계 등 상업적 목적의 문의는 사양합니다.</li>
</ul>

<p>소중한 연락 감사드립니다.</p>"""

print("✅ About 및 Contact HTML 구축 준비 완료!")
