# -*- coding: utf-8 -*-
"""
[RULE_DATE / REASON / EXPIRY_CONDITION]
- Rule Date: 2026-11-02
- Reason: Naver DIA+/C-Rank SEO optimization with S1 Humanizer 25 AI Cliches Purge.
- Expiry Condition: Permanent (2026 D-Day Release Lifecycle).

[INPUT / OUTPUT / KILL_SWITCH_CMD]
- Input: CapCut 41:14 raw metadata + 12 tracks inventory
- Output: Humanized Naver Blog Post package (.md, .html, manifest.json)
- Kill Switch Command: S1_BLOG_DISABLED=1
"""
import os, sys, json
import s1_humanizer


ROOT_DIR = r"C:\Users\sangi\Downloads\shin-agent"
OUT_DIR = os.path.join(ROOT_DIR, "studio_vault", "NAVER_BLOG_OUT")
os.makedirs(OUT_DIR, exist_ok=True)

POST_TITLE = "[음반 발매] 11월 6일, 차가운 계절의 문턱에서 전하는 12편의 온기 — 한걸음씩 정규 1집 『가을과 겨울 사이』 전곡 감상 가이드"

POST_MD = """# [음반 발매] 11월 6일, 차가운 계절의 문턱에서 전하는 12편의 온기 — 한걸음씩 정규 1집 『가을과 겨울 사이』 전곡 감상 가이드

*발행일: 2026년 11월 6일 (D-Day) | 아티스트: 한걸음씩 (Hang-eo-reum-sshik) | 레이블: 한걸음씩 / SUN-ONE AON Records*

---

## 🍂 1. 차가운 바람이 불어올 때, 우리에게 필요한 작은 온기

11월의 첫 주가 지나가며 아침저녁으로 옷깃을 여미게 되는 계절이 찾아왔습니다.  
유난히 길고 분주했던 하루 끝, 만원 지하철과 차가운 승강장에 서 있을 때 문득 가슴 한구석이 서늘해지는 기분을 느껴보신 적이 있나요?

세상은 끊임없이 더 빨리 달리라고, 더 높은 곳을 향해 쉬지 말고 나아가라고 재촉하지만, 정작 우리 마음이 진정으로 갈망하는 것은 거창한 성공이 아니라 **"오늘 하루도 정말 수고 많았어"**라는 다정한 말 한마디일지도 모릅니다.

오는 **2026년 11월 6일(금) 00:00**, 일상의 작은 쉼표와 온기를 전하는 아티스트 **'한걸음씩'**의 첫 번째 정규 앨범 **『가을과 겨울 사이 (Between Autumn and Winter)』**(총 12곡, 41분 14초)가 전 세계 24개 음원 사이트와 유튜브에 공식 공개됩니다.

---

## ☕ 2. 왜 '가을과 겨울 사이'인가? — 음악에 담긴 이야기

이 앨범은 화려한 전자음이나 자극적인 후크송이 아닌, 어쿠스틱 기타와 따뜻한 피아노, 그리고 나지막이 읊조리는 진솔한 목소리로 채워져 있습니다.

> *"최고의 선은 물과 같아서 만물을 이롭게 하되 다투지 않는다(上善若水)."*

이상일 총괄 프로듀서의 '상선약수' 철학을 모태로 삼아, 다투지 않고 낮은 곳으로 흐르며 메마른 땅을 적시는 물처럼 사람들의 지친 마음에 스며드는 음악을 만들고자 했습니다.

대표님이 캡컷(CapCut)으로 41분 동안 직접 장면 하나하나의 호흡과 감정선을 연출하신 원본 영상을 바탕으로, 유튜브 방송 표준 음량(-14.0 LUFS)과 하이파이 320kbps 무손실 오디오로 정밀 마스터링하여 듣는 내내 귀와 마음이 편안하도록 주조되었습니다.

---

## 🎧 3. 『가을과 겨울 사이』 12곡 전곡 트랙리스트 & 감상 포인트

| 트랙 | 곡명 | 시간 | 감상 포인트 & 한 줄 이야기 |
| :---: | :--- | :---: | :--- |
| **01** | **막차 (Last Train)** | 03:29 | 지친 귀갓길, 차창 밖 도심 불빛을 보며 고단한 하루의 무게를 내려놓는 힐링 발라드 |
| **02** | **창을 닫지 마 (Don't Close)** | 03:09 | 서늘한 바람이 불어와도 마음의 문마저 닫지 말라는 다정한 응원 |
| **03** | **첫 입김 (First Breath)** | 03:23 | 겨울의 문턱에서 하얗게 피어나는 입김 속에 담긴 순수한 설렘 |
| **04** | **오늘은 여기까지 (That's All)** | 04:17 | 모든 짐을 혼자 짊어지려 하지 마세요. 오늘은 여기까지 쉬어가도 괜찮습니다 |
| **05** | **밥은 먹었니 (Have You Eaten)** | 03:18 | 세상에서 가장 소박하지만 가장 위대한 사랑의 안부 |
| **06** | **식어 가는 차 (Cooling Tea)** | 03:08 | 뜨거웠던 열정이 지나간 자리에 남는 더 깊고 은은한 배려 |
| **07** | **가로등 아래서 (Streetlight)** | 03:26 | 어두운 골목길을 묵묵히 지켜주는 노란 불빛의 위로 |
| **08** | **남겨둔 자리 (Reserved Seat)** | 03:46 | 세상이 차가워도 언제든 돌아와 쉴 수 있는 따뜻한 품 |
| **09** | **보내지 않은 말 (Unsent Words)** | 03:44 | 차마 전하지 못하고 가슴에 묻어둔 침묵의 기도 |
| **10** | **불은 꺼지지 않아 (The Light)** | 03:18 | 어둠 속에서도 꿈을 잃지 않는 이들을 위한 희망의 등대 |
| **11** | **난로 옆에서 (Beside Stove)** | 03:18 | 타닥타닥 타오르는 장작 소리와 따스한 온기의 안식 |
| **12** | **내일의 아침 (Tomorrow)** | 03:19 | 눈물겨운 어둠을 뚫고 찬란하게 밝아오는 새날의 약속 |

---

## 🎬 4. 공식 감상처 및 스트리밍 안내

* **유튜브 공식 풀버전 (41분 14초 FHD 전곡 듣기):**  
  공식 채널 **[@한걸음씩-r4i](https://www.youtube.com/@%ED%95%9C%EA%B1%B8%EC%9D%8C%EC%84%A9-r4i)**에서 11월 6일 00시 전격 공개
* **글로벌 24개 음원 스트리밍 플랫폼 (DistroKid 정식 발매):**  
  * **국내:** 멜론(MelOn), 지니(Genie), 벅스(Bugs), 플로(FLO), 바이브(VIBE)
  * **해외:** 스포티파이(Spotify), 애플뮤직(Apple Music), 유튜브 뮤직(YouTube Music), 아마존 뮤직 등
  * **공식 발매 UPC:** `700563848544`

---

## 🌿 5. 상선약수(上善若水) 33% 사회 환원 약속

한걸음씩과 SUN-ONE AON 사령부는 이번 정규 1집 음원 및 유튜브 수익의 **33%를 도움이 필요한 이웃과 미래 세대 교육 장학금으로 환원**합니다. 여러분께서 음악을 듣고 머물러주시는 매 순간이 세상에 따뜻한 선한 영향력으로 다시 흘러가게 됩니다.

차가운 계절의 문턱, 이 12편의 음악이 여러분의 마음에 작지만 꺼지지 않는 난로가 되어주기를 소망합니다.  
감사합니다.

#한걸음씩 #가을과겨울사이 #정규1집 #포크발라드 #인디음악 #풀앨범 #힐링음악 #가을노래 #겨울노래 #음반추천 #상선약수
"""

POST_HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{POST_TITLE}</title>
<style>
body {{ font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; line-height: 1.8; color: #333; max-width: 840px; margin: 40px auto; padding: 0 20px; }}
h1 {{ font-size: 24px; color: #1e293b; border-bottom: 2px solid #f59e0b; padding-bottom: 12px; }}
h2 {{ font-size: 20px; color: #0f172a; margin-top: 32px; border-left: 4px solid #0284c7; padding-left: 10px; }}
blockquote {{ background: #f8fafc; border-left: 4px solid #f59e0b; margin: 20px 0; padding: 12px 18px; color: #475569; font-style: italic; }}
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }}
th, td {{ border: 1px solid #cbd5e1; padding: 10px 12px; text-align: left; }}
th {{ background: #f1f5f9; color: #0f172a; font-weight: bold; }}
.badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; background: #fef08a; color: #854d0e; font-size: 12px; font-weight: bold; }}
.tag {{ color: #0284c7; font-weight: 500; margin-right: 6px; }}
</style>
</head>
<body>
<h1>{POST_TITLE}</h1>
<p><em>발행일: 2026년 11월 6일 (D-Day) | 아티스트: 한걸음씩 | 레이블: 한걸음씩 / SUN-ONE AON Records</em></p>
<hr>
<h2>🍂 1. 차가운 바람이 불어올 때, 우리에게 필요한 작은 온기</h2>
<p>11월의 첫 주가 지나가며 아침저녁으로 옷깃을 여미게 되는 계절이 찾아왔습니다. 유난히 길고 분주했던 하루 끝, 만원 지하철과 차가운 승강장에 서 있을 때 문득 가슴 한구석이 서늘해지는 기분을 느껴보신 적이 있나요?</p>
<p>세상은 끊임없이 더 빨리 달리라고 재촉하지만, 정작 우리 마음이 진정으로 갈망하는 것은 <strong>"오늘 하루도 정말 수고 많았어"</strong>라는 다정한 말 한마디일지도 모릅니다.</p>
<p>오는 <strong>2026년 11월 6일(금) 00:00</strong>, 아티스트 <strong>'한걸음씩'</strong>의 첫 번째 정규 앨범 <strong>『가을과 겨울 사이』</strong>(총 12곡, 41분 14초)가 전 세계 24개 음원 사이트와 유튜브에 공식 공개됩니다.</p>
<h2>☕ 2. 왜 '가을과 겨울 사이'인가? — 음악에 담긴 이야기</h2>
<blockquote>"최고의 선은 물과 같아서 만물을 이롭게 하되 다투지 않는다(上善若水)."</blockquote>
<p>이상일 총괄 프로듀서의 '상선약수' 철학을 모태로 삼아, 다투지 않고 낮은 곳으로 흐르며 메마른 땅을 적시는 물처럼 사람들의 지친 마음에 스며드는 음악을 만들고자 했습니다. 41분 풀영상과 하이파이 -14.0 LUFS 방송 음량 표준화로 감상의 안락함을 극대화했습니다.</p>
<h2>🎧 3. 『가을과 겨울 사이』 12곡 전곡 트랙리스트 & 감상 포인트</h2>
<table>
<thead><tr><th>트랙</th><th>곡명</th><th>재생시간</th><th>감상 포인트</th></tr></thead>
<tbody>
<tr><td>01</td><td><strong>막차 (Last Train)</strong></td><td>03:29</td><td>지친 귀갓길, 고단한 하루의 무게를 내려놓는 힐링 발라드</td></tr>
<tr><td>02</td><td><strong>창을 닫지 마</strong></td><td>03:09</td><td>서늘한 바람 속에서도 마음의 문을 닫지 말라는 응원</td></tr>
<tr><td>03</td><td><strong>첫 입김</strong></td><td>03:23</td><td>겨울의 문턱에서 하얗게 피어나는 순수한 설렘</td></tr>
<tr><td>04</td><td><strong>오늘은 여기까지</strong></td><td>04:17</td><td>번아웃에 지친 현대인에게 건네는 따뜻한 쉼표</td></tr>
<tr><td>05</td><td><strong>밥은 먹었니</strong></td><td>03:18</td><td>세상에서 가장 소박하고 위대한 사랑의 안부</td></tr>
<tr><td>06</td><td><strong>식어 가는 차</strong></td><td>03:08</td><td>열정이 지나간 자리에 남는 은은한 배려</td></tr>
<tr><td>07</td><td><strong>가로등 아래서</strong></td><td>03:26</td><td>어두운 골목길을 묵묵히 비춰주는 노란 불빛의 위로</td></tr>
<tr><td>08</td><td><strong>남겨둔 자리</strong></td><td>03:46</td><td>세상이 차가워도 언제든 돌아와 쉴 수 있는 품</td></tr>
<tr><td>09</td><td><strong>보내지 않은 말</strong></td><td>03:44</td><td>차마 전하지 못하고 가슴에 묻어둔 침묵의 기도</td></tr>
<tr><td>10</td><td><strong>불은 꺼지지 않아</strong></td><td>03:18</td><td>어둠 속에서도 꿈을 잃지 않는 이들을 위한 희망</td></tr>
<tr><td>11</td><td><strong>난로 옆에서</strong></td><td>03:18</td><td>타닥타닥 타오르는 장작 소리와 따스한 온기</td></tr>
<tr><td>12</td><td><strong>내일의 아침</strong></td><td>03:19</td><td>어둠을 뚫고 찬란하게 밝아오는 새날의 약속</td></tr>
</tbody>
</table>
<h2>🎬 4. 공식 감상처 및 스트리밍 안내</h2>
<p>유튜브 공식 채널 <strong>@한걸음씩-r4i</strong> 및 멜론, 지니, 스포티파이, 애플뮤직 등 24개 플랫폼 동시 발매 (UPC: 700563848544)</p>
<h2>🌿 5. 상선약수(上善若水) 33% 사회 환원 약속</h2>
<p>음원 및 유튜브 수익의 33%는 도움이 필요한 이웃과 미래 세대 장학금으로 환원됩니다.</p>
</body>
</html>
"""

def generate_blog_package():
    md_path = os.path.join(OUT_DIR, "NOV06_NAVER_BLOG_POST_PACKAGE.md")
    html_path = os.path.join(OUT_DIR, "NOV06_NAVER_BLOG_POST_PACKAGE.html")
    
    h_md = s1_humanizer.humanize_text(POST_MD)["humanized_text"]
    h_html = s1_humanizer.humanize_text(POST_HTML)["humanized_text"]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(h_md)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(h_html)
        
    print(f"Saved Naver Blog Package -> {md_path} and {html_path}")

def generate_smarteditor_staging_script():
    # Staging script for SmartEditor ONE via Ego-Lite
    routine = {
        "engine": "Ego-Lite SmartEditor ONE Draft Staging",
        "target_platform": "blog.naver.com",
        "post_title": POST_TITLE,
        "content_file_md": os.path.join(OUT_DIR, "NOV06_NAVER_BLOG_POST_PACKAGE.md"),
        "content_file_html": os.path.join(OUT_DIR, "NOV06_NAVER_BLOG_POST_PACKAGE.html"),
        "tags": ["한걸음씩", "가을과겨울사이", "정규1집", "포크발라드", "인디음악", "힐링음악", "상선약수"],
        "status": "STAGED_READY_FOR_PUBLISH"
    }
    manifest_path = os.path.join(OUT_DIR, "NAVER_BLOG_STAGING_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(routine, f, ensure_ascii=False, indent=2)
    print(f"Saved Naver Blog Staging Manifest -> {manifest_path}")

if __name__ == "__main__":
    generate_blog_package()
    generate_smarteditor_staging_script()

