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

title = "교대근무자 특수건강진단 실전 이용기"
categories = ["직장생활·교대근무"]

content = """<p><strong>카테고리: 직장생활·교대근무 | 작성: 3교대 직장인 길잡이</strong></p>

<hr style="border:none; border-top:1px solid #eee; margin:24px 0;">

<p>3교대 제조 현장에서 일하다 보면 1년에 한 번(또는 배치 주기에 따라 정기적으로) 회사 안내를 받고 병원에 가서 검사를 받게 됩니다. 일반 국민건강보험공단 일반검진과 달리, 야간작업을 하는 근로자라면 법적으로 반드시 받아야 하는 <strong>'야간작업 특수건강진단'</strong>입니다.</p>

<p>처음에는 '회사에서 받으라고 하니까 받는 간단한 피검사' 정도로 생각했었습니다. 하지만 수년간 3교대 생활을 하며 생체리듬이 무너지고 피로가 누적되다 보니, 이 특수건강진단 결과표가 내 몸의 위험 신호를 가장 객관적으로 짚어주는 중요한 지표라는 사실을 알게 되었습니다.</p>

<p>오늘은 제가 현장에서 매년 수검하고 있는 야간작업 특수건강진단의 법적 기준과 실제 검사 과정, 그리고 검진 후 사후관리 조치까지 실전 경험을 바탕으로 알기 쉽게 정리해 보겠습니다.</p>

<hr style="border:none; border-top:1px solid #eee; margin:24px 0;">

<h2 style="border-bottom:1px solid #eee; padding-bottom:4px;">1. 야간작업 특수건강진단 대상 기준과 근거 법령</h2>

<p>모든 근로자가 특수건강진단을 받는 것은 아닙니다. <strong>산업안전보건법 제130조(특수건강진단 등)</strong> 및 <strong>동법 시행규칙 제201조(별표 22)</strong>에 따라 유해인자(야간작업 포함 180여 종)에 노출되는 업무에 종사하는 근로자가 대상입니다.</p>

<p><strong>고용노동부</strong>에서 규정하는 '야간작업' 유해인자 적용 기준은 다음과 같습니다.</p>

<ul>
<li><strong>기준 1</strong>: 6개월간 <strong>밤 12시부터 다음 날 오전 5시까지의 시간을 포함하여 계속되는</strong> 8시간 작업을 <strong>월평균 4회 이상</strong> 수행하는 경우</li>
<li><strong>기준 2</strong>: 6개월간 <strong>오후 10시부터 다음 날 오전 6시 사이</strong>의 시간 중 작업을 <strong>월평균 60시간 이상</strong> 수행하는 경우</li>
</ul>

<p>3교대 생산·제조 현장 근무자라면 대부분 이 두 가지 기준 중 하나 이상에 해당하므로, 사업주는 <strong>한국산업안전보건공단(KOSHA)</strong> 지침 및 법령에 따라 비용을 전액 부담하여 <strong>고용노동부 지정 특수건강진단기관</strong>에서 검진을 실시해야 합니다.</p>

<p>검진 주기는 배치 전 검진을 시작으로, 배치 후 첫 번째 검진은 6개월 이내, 이후에는 <strong>1년마다 정기적</strong>으로 실시하는 것이 원칙입니다.</p>

<hr style="border:none; border-top:1px solid #eee; margin:24px 0;">

<h2 style="border-bottom:1px solid #eee; padding-bottom:4px;">2. 실제 검사 항목과 현장 검진 절차</h2>

<p>특수건강진단은 <strong>고용노동부 고시(특수건강진단·배치전건강진단 및 수시건강진단의 임상검사항목 및 검사방법)</strong>에 정해진 표적 장기 중심의 항목으로 진행됩니다. 야간작업의 대표적인 3대 표적 유해요인은 <strong>수면장애, 심뇌혈관질환, 위장관계 질환</strong>입니다.</p>

<h3 style="color:#333; margin-top:16px;">(1) 1차 검사 항목</h3>
<ul>
<li><strong>문진 및 설문 평가</strong>: 불면증 심각도 척도, 주간 졸림증 척도(ESS), 위식도 역류 및 소화불량 설문, 뇌심혈관 발병 위험도 평가 설문 작성</li>
<li><strong>신체계측 및 기본 검사</strong>: 혈압 측정, 체질량지수(BMI), 복부둘레 측정</li>
<li><strong>혈액 및 생화학 검사</strong>: 공복혈당, 지질 프로파일(총콜레스테롤, 중성지방, HDL/LDL 콜레스테롤), 간기능 검사 등</li>
</ul>

<h3 style="color:#333; margin-top:16px;">(2) 2차 정밀 검사 항목 (필요시)</h3>
<p>1차 검사에서 혈압 수치가 높거나 심전도 이상 소견, 당화혈색소 상승, 극심한 수면 장애 징후가 발견되면 의사의 판단에 따라 2차 정밀 검사가 진행됩니다. 24시간 활동 혈압 측정이나 정밀 수면다원상담, 추가 혈액검사 등이 포함됩니다.</p>

<p>제가 직접 검진을 받을 때 가장 중요하게 느낀 점은 <strong>'설문지 작성의 솔직함'</strong>이었습니다. 밤샘 근무 후 속쓰림이나 불면 증상을 대수롭지 않게 '양호'로 체크하면 정작 필요한 관리 조치를 놓칠 수 있으므로, 실제 느끼는 피로도와 소화 상태를 있는 그대로 작성해야 정확한 평가를 받을 수 있습니다.</p>

<hr style="border:none; border-top:1px solid #eee; margin:24px 0;">

<h2 style="border-bottom:1px solid #eee; padding-bottom:4px;">3. 검진 결과표 판정 등급과 사후관리 조치</h2>

<p>검진이 끝나고 몇 주 후면 회사 보건실 또는 자택으로 <strong>'특수건강진단 개인표'</strong>가 송부됩니다. 이 결과표에는 <strong>산업안전보건법 시행규칙 제209조</strong>에 따른 건강관리구분이 알파벳 기호로 표시됩니다.</p>

<table style="width:100%; border-collapse:collapse; margin:16px 0;">
<tr>
<th style="border:1px solid #ddd; padding:8px; background:#f5f5f5; font-weight:bold;">판정 구분</th>
<th style="border:1px solid #ddd; padding:8px; background:#f5f5f5; font-weight:bold;">상태 정의</th>
<th style="border:1px solid #ddd; padding:8px; background:#f5f5f5; font-weight:bold;">주요 사후관리 조치</th>
</tr>
<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>A</strong></td>
<td style="border:1px solid #ddd; padding:8px;">건강관리상 사후관리가 필요 없는 자 (정상)</td>
<td style="border:1px solid #ddd; padding:8px;">현재 건강 상태 유지</td>
</tr>
<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>C1</strong></td>
<td style="border:1px solid #ddd; padding:8px;">야간작업 등 직업 요인으로 인한 질병 유관찰자</td>
<td style="border:1px solid #ddd; padding:8px;">추적 검사, 작업 환경 관리, 보건 상담</td>
</tr>
<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>C2</strong></td>
<td style="border:1px solid #ddd; padding:8px;">일반 질병(고혈압, 당뇨, 고지혈증 등) 유관찰자</td>
<td style="border:1px solid #ddd; padding:8px;">생활습관 개선 지도, 정기 재검</td>
</tr>
<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>D1 / D2</strong></td>
<td style="border:1px solid #ddd; padding:8px;">직업병(D1) 또는 일반질병(D2) 유소견자</td>
<td style="border:1px solid #ddd; padding:8px;">전문의 정밀 치료, 작업 전환 및 야간근무 제한 검토</td>
</tr>
<tr>
<td style="border:1px solid #ddd; padding:8px; text-align:center;"><strong>R</strong></td>
<td style="border:1px solid #ddd; padding:8px;">2차 건강진단 대상자 (재검 필요)</td>
<td style="border:1px solid #ddd; padding:8px;">기한 내 2차 정밀검사 수검</td>
</tr>
</table>

<p><strong>산업안전보건법 제132조(건강진단에 관한 사업주의 조치의무)</strong>에 따라, 사업주는 건강진단 결과 근로자의 건강을 유지하기 위하여 필요하다고 인정할 때에는 다음과 같은 사후관리 조치를 이행해야 합니다.</p>

<ul>
<li><strong>작업 장소 변경 및 업무 전환</strong>: 건강 상태가 악화된 근로자의 주간 근무 전환 또는 유해 부서 이동</li>
<li><strong>근로시간 단축 및 야간작업 제한</strong>: 질병 위험군에 대한 연속 야간작업 일수 축소</li>
<li><strong>사내 보건관리자 상담</strong>: 정기 혈압·혈당 모니터링 및 식이·수면 보건 교육 지원</li>
<li><strong>고용노동부 보고</strong>: 검진 기관은 검진 결과를 사업장 관할 지방고용노동관서에 보고</li>
</ul>

<hr style="border:none; border-top:1px solid #eee; margin:24px 0;">

<h2 style="border-bottom:1px solid #eee; padding-bottom:4px;">마치며: 특수건강진단을 대하는 직장인의 자세</h2>

<p>저 역시 과거 체중이 늘고 식습관이 무너졌던 시절, 특수건강진단에서 C2(일반질병 유관찰자) 판정과 함께 혈압 및 지질 관리에 주의하라는 권고를 받았습니다. 그때의 경고장을 계기로 식습관을 재정비하고 퇴근 후 걷기 루틴을 실천하면서 다음 해 검진에서 정상 수치를 회복할 수 있었습니다.</p>

<p>특수건강진단은 회사가 시켜서 억지로 받는 형식적인 절차가 아니라, 밤낮이 바뀌는 가혹한 환경 속에서 내 몸의 이상 신호를 법적으로 보장받으며 점검하는 가장 강력한 보호 장치입니다. 결과표를 받으시면 서랍 속에 넣어두지 마시고 내 수치와 권고사항을 꼼꼼히 확인해 보시기를 권합니다.</p>

<hr style="border:none; border-top:1px solid #eee; margin:24px 0;">

<blockquote style="border-left:4px solid #ccc; padding:8px 16px; color:#555; margin:16px 0;">
<p><strong>면책 고지</strong></p>
<p>이 글은 개인의 특수건강진단 수검 경험과 관련 법령 정보를 정리한 것이며, 전문적인 의학적 진단이나 법률 자문이 아닙니다. 사업장별 특수건강진단 실시 주기, 대상 작업 및 사후관리 조치에 관한 구체적인 사항은 사업장 보건관리자, 지정 특수건강진단 기관 또는 고용노동부 고객상담센터(1350)에 문의하시기 바랍니다.</p>
</blockquote>"""

body = {
    'kind': 'blogger#post',
    'title': title,
    'content': content,
    'labels': categories
}

res = blogger.posts().insert(blogId=BLOG_ID, body=body, isDraft=False).execute()
print(f"Published Post 17! Post ID: {res.get('id')}, URL: {res.get('url')}")
