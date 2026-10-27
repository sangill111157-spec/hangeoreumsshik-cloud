# -*- coding: utf-8 -*-
"""
rgon_aon_empire_asset_hub.py [제36기관: 아온 한걸음씩 6대 자산 제국 마스터 통합 허브]
================================================================================
버전: v11.62-AON-13SHORTS-OMNI-ENGINE
소유: 기술총리 안총리 & 36대 기관 만능 참모 아온이 (이상일 대표님 직속)
항체: R60_EMPIRE_ASSET_HUB_LOCK
주역: #14 화천대유(火天大有) - 만물을 풍요롭게 포용하고 대성하는 군자의 대유

[6대 비즈니스 자산 제국]
1. DistroKid 정식 배급 2대 정규앨범 27곡 (가을과 겨울 사이 12곡 + 잔상 15곡, 24개 플랫폼)
2. 유튜브 3대 공식 채널 (@한걸음씩-r4i, @Booster_Playlist, @TheCaféHour)
3. 틱톡 본진 (@boosterplaylist · 팔로워 2,125명) 및 메타 3형제(릴스·스레드·페북 원스톱)
4. 구글 블로거 (https://connect-ai-shin.blogspot.com/ · 3조 2교대 건강 7대 DNA)
5. 클로드 오퍼스 5.5 모션 스튜디오 5대 프리셋 자동 연동
6. 텔레그램-카카오 원격 소통 브릿지 & 온·오프라인 5G 직통 브레인
================================================================================
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# 시스템 인코딩 방어
for _stream in ("stdout", "stderr"):
    _s = getattr(sys, _stream, None)
    if _s and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

VERSION = "v11.62-AON-13SHORTS-OMNI-ENGINE"
ORGAN_ID = 36
ORGAN_NAME = "아온 한걸음씩 6대 자산 제국 마스터 통합 허브"
SKILL_NAME = "aon-empire-asset-hub"
ANTIBODY = "R60_EMPIRE_ASSET_HUB_LOCK"
HEXAGRAM = "#14 화천대유(火天大有)"

ROOT = Path(__file__).resolve().parent
ASSET_LEDGER_PATH = ROOT / "commander_6empire_assets.json"

# 내장 백업 원장 (JSON 파일 누락 시 100% 무중단 폴백)
FALLBACK_LEDGER: Dict[str, Any] = {
    "version": VERSION,
    "owner": "이상일 대표님 (사령관)",
    "title": "한걸음씩 6대 비즈니스 자산 제국 마스터 원장",
    "distrokid": {
        "artist_label": "한걸음씩",
        "delivery_status": "24개 글로벌 스트리밍 플랫폼 전달 완료 (Spotify, Apple Music, YouTube Music, Melon, Genie 등)",
        "total_albums": 2,
        "total_tracks": 27,
        "albums": [
            {
                "album_id": "ALBUM-01",
                "title": "가을과 겨울 사이",
                "type": "정규 1집 (Regular Album Vol.1)",
                "upload_date": "2026-10-03",
                "release_date": "2026-11-06",
                "upc": "700563848544",
                "track_count": 12,
                "tracks": [
                    {"no": 1, "title": "막차"},
                    {"no": 2, "title": "창을 닫지 마"},
                    {"no": 3, "title": "첫 입김"},
                    {"no": 4, "title": "오늘은 여기까지"},
                    {"no": 5, "title": "밥은 먹었니"},
                    {"no": 6, "title": "식어 가는 차"},
                    {"no": 7, "title": "가로등 아래서"},
                    {"no": 8, "title": "남겨 둔 자리"},
                    {"no": 9, "title": "보내지 않은 말"},
                    {"no": 10, "title": "불은 꺼지지 않아"},
                    {"no": 11, "title": "난로 옆에서"},
                    {"no": 12, "title": "내일의 아침"}
                ],
                "description": "계절이 바뀌는 길목, 차가운 바람 속 따뜻한 온기와 일상의 위로를 건네는 한걸음씩 감성 정규 1집"
            },
            {
                "album_id": "ALBUM-02",
                "title": "잔상",
                "type": "정규 2집 (Regular Album Vol.2)",
                "upload_date": "2026-10-14",
                "release_date": "2026-11-27",
                "upc": "700486463268",
                "track_count": 15,
                "tracks": [
                    {"no": 1, "title": "답장은 천천히"},
                    {"no": 2, "title": "한 칸 사이"},
                    {"no": 3, "title": "먼저 끊지 마"},
                    {"no": 4, "title": "읽고도 모른 척"},
                    {"no": 5, "title": "우리 아닌 우리"},
                    {"no": 6, "title": "반 박자 늦게"},
                    {"no": 7, "title": "새벽의 온도"},
                    {"no": 8, "title": "잔상"},
                    {"no": 9, "title": "취소한 문장"},
                    {"no": 10, "title": "괜찮은 척의 속도"},
                    {"no": 11, "title": "우회전"},
                    {"no": 12, "title": "조금 덜 선명해"},
                    {"no": 13, "title": "내 쪽으로"},
                    {"no": 14, "title": "다음 계절의 나"},
                    {"no": 15, "title": "아침의 편"}
                ],
                "description": "지나간 시간과 마음에 남은 여운을 섬세하고 깊은 멜로디로 어루만지는 정규 2집"
            }
        ],
        "released_singles": [
            {"title": "영혼의 무게 (The Weight of a Soul)", "status": "기발매 히트곡"},
            {"title": "모두의 응원가 (Everyone's Anthem)", "status": "기발매 히트곡"},
            {"title": "원인과 결과, 결국 사랑", "status": "기발매 히트곡"},
            {"title": "사냥꾼의 새벽 (Hunter's Dawn)", "status": "기발매 테마곡"}
        ]
    },
    "youtube": {
        "total_channels": 3,
        "channels": [
            {
                "id": "CH-01",
                "name": "한걸음씩",
                "handle": "@한걸음씩-r4i",
                "slogan": "🌱 한마디가 당신의 인생을 바꿉니다",
                "category": "감성·인생 AI MV 및 정식 발매 음원 본진",
                "url": "https://www.youtube.com/@한걸음씩-r4i"
            },
            {
                "id": "CH-02",
                "name": "부스터 플리 | 운동·드라이브 음악",
                "handle": "@Booster_Playlist",
                "slogan": "⚡ 1시간 에너지 러닝·야간 드라이브 Phonk/Workout",
                "category": "운동·드라이브·고에너지 플레이리스트",
                "url": "https://www.youtube.com/@Booster_Playlist"
            },
            {
                "id": "CH-03",
                "name": "The Café Hour",
                "handle": "@TheCaféHour",
                "slogan": "☕ 음악으로 채우는 카페의 하루 (MORNING·AFTERNOON·EVENING)",
                "category": "1~1.5시간 편안한 카페 재즈 & 보사노바",
                "url": "https://www.youtube.com/@TheCaféHour"
            }
        ]
    },
    "sns": {
        "tiktok": {
            "name": "부스터플리",
            "handle": "@boosterplaylist",
            "followers": 2125,
            "likes": 8793,
            "max_views": "2.2만 회",
            "role": "AI 음악 3채널 통합 숏폼 바이럴 본진",
            "url": "https://www.tiktok.com/@boosterplaylist"
        },
        "meta_3brothers": {
            "platforms": ["인스타그램 (릴스)", "스레드 (Threads)", "페이스북 (Facebook)"],
            "one_stop_guide": "인스타그램 릴스 업로드 시 [페이스북에 추천 공유] 및 [스레드 자동 공유] 스위치 ON -> 3초 만에 3대 SNS 동시 배포"
        }
    },
    "blogger": {
        "title": "불규칙한 삶 속 건강 챙기기",
        "url": "https://connect-ai-shin.blogspot.com/",
        "subtitle": "교대근무를 하며 건강과 식습관을 관리해온 경험을 기록합니다",
        "author": "이상일 대표님",
        "topics_dna": [
            "3조 2교대(12시간) 야간근무 식사·생활습관 변화",
            "출근 전·근무 중·퇴근 후 3단계 식사 타이밍 루틴",
            "야간작업 특수건강진단(산업안전보건법 제130조) 실전 이용기",
            "근로기준법 제56조 야간·휴일 근로수당 계산 가이드",
            "500ml 눈금 텀블러 3번(1.5L) 물 마시기 루틴",
            "강직성 척추염과 75kg 체중을 이겨낸 '하루 15분 걷기(한 걸음씩)' 습관",
            "주식 초보 급등주 실패에서 배운 원칙 투자 교훈"
        ]
    }
}


def load_empire_ledger() -> Dict[str, Any]:
    """6대 자산 마스터 원장을 로드한다. 파일이 없으면 내장 폴백 원장 반환."""
    if ASSET_LEDGER_PATH.exists():
        try:
            with open(ASSET_LEDGER_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "distrokid" in data:
                    return data
        except Exception:
            pass
    return FALLBACK_LEDGER


def calculate_dday(target_date_str: str, base_date: Optional[datetime.date] = None) -> Dict[str, Any]:
    """실시간 D-Day를 계산한다 (예: 2026-11-06 -> D-10)."""
    if base_date is None:
        base_date = datetime.date.today()
    try:
        target = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
        diff = (target - base_date).days
        if diff > 0:
            dday_label = f"D-{diff}"
        elif diff == 0:
            dday_label = "D-Day (오늘 발매!)"
        else:
            dday_label = f"D+{-diff} (발매 완료)"
        return {
            "target_date": target_date_str,
            "base_date": base_date.strftime("%Y-%m-%d"),
            "diff_days": diff,
            "label": dday_label
        }
    except Exception as e:
        return {"target_date": target_date_str, "diff_days": 0, "label": "D-Day 계산 불가", "error": str(e)}


def get_distrokid_albums(base_date: Optional[datetime.date] = None) -> Dict[str, Any]:
    """DistroKid 2대 정규앨범(27곡) 현황 및 실시간 D-Day를 반환한다."""
    ledger = load_empire_ledger()
    dk = ledger.get("distrokid", {})
    albums = []
    for alb in dk.get("albums", []):
        dday_info = calculate_dday(alb.get("release_date", ""), base_date)
        albums.append({
            "album_id": alb.get("album_id"),
            "title": alb.get("title"),
            "type": alb.get("type"),
            "upload_date": alb.get("upload_date"),
            "release_date": alb.get("release_date"),
            "dday": dday_info["label"],
            "diff_days": dday_info["diff_days"],
            "upc": alb.get("upc"),
            "track_count": alb.get("track_count"),
            "tracks": alb.get("tracks", []),
            "description": alb.get("description")
        })
    return {
        "artist_label": dk.get("artist_label", "한걸음씩"),
        "delivery_status": dk.get("delivery_status"),
        "total_albums": len(albums),
        "total_tracks": sum(len(a.get("tracks", [])) for a in albums),
        "albums": albums,
        "released_singles": dk.get("released_singles", [])
    }


def get_youtube_channels() -> Dict[str, Any]:
    """유튜브 3대 공식 채널 현황을 반환한다."""
    ledger = load_empire_ledger()
    chs = ledger.get("youtube_channels") or ledger.get("youtube", {}).get("channels", [])
    return {
        "total_channels": len(chs),
        "channels": chs
    }


def get_sns_hub() -> Dict[str, Any]:
    """틱톡 및 메타 3형제 SNS 바이럴 허브 현황을 반환한다."""
    ledger = load_empire_ledger()
    hub = ledger.get("sns_viral_hub") or ledger.get("sns", {})
    return hub


def get_blogger_info() -> Dict[str, Any]:
    """구글 블로거 현황 및 7대 핵심 포스팅 DNA를 반환한다."""
    ledger = load_empire_ledger()
    b = ledger.get("google_blogger") or ledger.get("blogger", {})
    # 호환성 보장
    url = b.get("blog_url") or b.get("url", "https://connect-ai-shin.blogspot.com/")
    topics = b.get("core_topics") or b.get("topics_dna", [])
    return {
        "title": b.get("title", "불규칙한 삶 속 건강 챙기기"),
        "url": url,
        "blog_url": url,
        "subtitle": b.get("theme") or b.get("subtitle", "교대근무를 하며 건강과 식습관을 관리해온 경험을 기록합니다"),
        "author": b.get("author", "이상일 대표님"),
        "topics_dna": topics,
        "core_topics": topics
    }


def generate_blog_post(topic: str = "3조 2교대 건강 관리") -> Dict[str, Any]:
    """
    대표님 고유 문체(3조 2교대 실전 경험 + 내부링크 + 면책고지)로 블로그 포스팅 초안 생성.
    """
    blogger = get_blogger_info()
    title_topic = topic.replace("블로그 글 써줘", "").replace("블로그 글 써줘:", "").replace("주제:", "").strip()
    if not title_topic:
        title_topic = "3조 2교대 야간근무 속 수면과 식습관 15분 관리법"

    post_title = f"[교대근무 실전기] {title_topic} — 강직성 척추염과 12시간 야간근무를 버텨낸 3가지 원칙"
    content_html = f"""
<div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #2d3748;">
  <p>안녕하세요. <strong>불규칙한 삶 속 건강 챙기기</strong> 블로그를 운영하는 <strong>한걸음씩</strong>입니다.</p>
  
  <p>저는 오랜 기간 <strong>3조 2교대(12시간 주야 맞교대)</strong> 현장에서 근무하며, 망가지는 수면 패턴과 불규칙한 식사 속에서 강직성 척추염과 75kg 체중을 극복해왔습니다. 오늘 다룰 주제는 많은 동료분들이 질문 주시는 <strong>『{title_topic}』</strong>에 대한 저의 실제 경험과 루틴입니다.</p>

  <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />

  <h3 style="color: #1a202c; border-left: 4px solid #3182ce; padding-left: 10px;">1. 12시간 교대근무의 현실: 왜 의지보다 '시스템'인가?</h3>
  <p>야간근무(밤 7시 ~ 아침 7시)를 해보신 분들은 잘 아실 겁니다. 새벽 3시가 넘어가면 뇌의 인지 기능이 급격히 저하되고, 위장 운동이 멈추면서 기름진 야식이 당기게 됩니다. 하지만 이때 야식을 먹으면 퇴근 후 아침 수면의 질이 완전히 무너집니다.</p>
  <p>저는 이를 막기 위해 <strong>출근 전 든든한 식사 -> 근무 중 견과류/따뜻한 차 -> 퇴근 후 가벼운 단백질 음료</strong>의 3단계 타이밍을 철칙으로 삼았습니다.</p>

  <h3 style="color: #1a202c; border-left: 4px solid #3182ce; padding-left: 10px;">2. 500ml 눈금 텀블러와 하루 15분 걷기 루틴</h3>
  <p>현장에서 가장 소홀해지기 쉬운 것이 바로 <strong>'수분 섭취'</strong>와 <strong>'관절 스트레칭'</strong>입니다.</p>
  <ul>
    <li><strong>수분 섭취:</strong> 500ml 눈금 텀블러에 미온수를 담아 야간 근무 중 딱 3번(총 1.5L) 비우는 루틴을 유지합니다.</li>
    <li><strong>하루 15분 걷기:</strong> 퇴근 후 집 앞 공원이나 트레드밀에서 딱 15분, 욕심내지 않고 '한 걸음씩' 걷습니다. 강직성 척추염 환자에게 무리한 러닝은 독이지만, 꾸준한 15분 보행은 굳어가는 척추를 부드럽게 풀어줍니다.</li>
  </ul>

  <h3 style="color: #1a202c; border-left: 4px solid #3182ce; padding-left: 10px;">3. 법적 권리와 수당도 건강의 일부입니다</h3>
  <p>몸만 챙긴다고 건강해지는 것이 아닙니다. <strong>산업안전보건법 제130조에 따른 야간작업 특수건강진단</strong>을 매년 빠짐없이 수검하여 혈당과 간수치 추적 관리를 받아야 하며, <strong>근로기준법 제56조에 따른 야간·휴일 수당</strong>이 올바르게 정산되었는지 스스로 챙기는 마음의 여유가 스트레스를 줄여줍니다.</p>

  <div style="background-color: #f7fafc; border: 1px solid #cbd5e0; border-radius: 8px; padding: 16px; margin: 24px 0;">
    <h4 style="margin-top: 0; color: #2b6cb0;">📌 관련 글 함께 읽기</h4>
    <p style="margin-bottom: 0;">
      👉 <a href="https://connect-ai-shin.blogspot.com/" target="_blank" style="color: #3182ce; text-decoration: underline;">
        [이전 글] 3조 2교대 야간근무 식사·수면 루틴과 특수건강진단 실전 후기
      </a>
    </p>
  </div>

  <p style="font-size: 0.9em; color: #718096; background: #edf2f7; padding: 12px; border-radius: 6px;">
    ⚠️ <strong>면책 고지 (Disclaimer):</strong><br />
    본 포스팅은 전문 의료인의 의학적 진단 및 치료를 대신할 수 없으며, 작성자 개인이 3조 2교대 현장에서 근무하며 체득한 주관적 경험과 생활 습관 기록입니다. 건강상의 이상이 있을 경우 반드시 전문의와 상담하시기 바랍니다.
  </p>
</div>
""".strip()

    return {
        "ok": True,
        "topic": title_topic,
        "title": post_title,
        "blog_url": blogger.get("url"),
        "author": blogger.get("author"),
        "html_content": content_html,
        "summary": f"'{title_topic}' 주제로 3조 2교대 실전 경험, 500ml 텀블러, 15분 걷기, 내부링크 및 법적 면책고지가 완비된 블로그 초안이 생성되었습니다."
    }


def generate_sns_promotions(target_name: str = "가을과 겨울 사이") -> Dict[str, Any]:
    """
    선택 곡/앨범/채널에 맞춘 4대 SNS(틱톡·인스타 릴스·스레드·유튜브) 맞춤형 홍보 캡션 및 메타 3초 가이드 생성.
    """
    target = target_name.strip()
    if not target or "음원" in target or "앨범" in target:
        target = "가을과 겨울 사이"

    tiktok_copy = f"""
🎧 바람이 차가워지는 지금, 꼭 들어야 할 플레이리스트
차가운 공기 속 첫 입김이 번질 때 마음을 따뜻하게 안아주는 노래 🍁
전 곡 멜론·스포티파이·애플뮤직 발매 완료!

👉 프로필 링크에서 풀버전 감상하기!
#부스터플리 #한걸음씩 #가을과겨울사이 #음악추천 #플레이리스트 #퇴근길음악 #감성노래 #잔상 #노동요
""".strip()

    reels_copy = f"""
계절이 바뀌는 길목에서,
당신의 하루 끝에 작은 온기를 건넵니다. 🌱

한걸음씩 정규 앨범 《{target}》
차가운 바람이 불어올 때, 창을 닫기 전 잠시 귀 기울여보세요.

🎧 Global Streaming on Spotify, Apple Music, Melon
🔗 프로필 상단 링크에서 전곡 감상

#한걸음씩 #가을과겨울사이 #잔상 #감성음악 #인디음악 #플레이리스트추천 #위로글귀 #밤편지 #퇴근길 #새벽감성
""".strip()

    threads_copy = f"""
일교차가 심해지니까 퇴근길 바람이 꽤 차갑네요. 🍂
이맘때쯤 혼자 이어폰 꽂고 걷다가 울컥해지는 순간이 있잖아요.

이번에 정성껏 주조한 정규 앨범 《{target}》 수록곡들인데,
'오늘은 여기까지'랑 '밥은 먹었니' 들으시면서 오늘 하루의 짐을 잠시 내려놓으셨으면 좋겠습니다.
여러분은 요즘 퇴근길에 어떤 노래 들으세요? ☕
""".strip()

    yt_desc = f"""
[Official Audio / MV] 한걸음씩 정규 앨범 《{target}》 Full Album Playlist
"🌱 한마디가 당신의 인생을 바꿉니다."

🎧 음원 스트리밍 (Global Streaming Platforms):
- Spotify / Apple Music / YouTube Music / Melon / Genie

⏱️ [타임스탬프 Tracklist]
00:00 01. 막차
03:15 02. 창을 닫지 마
06:40 03. 첫 입김
10:05 04. 오늘은 여기까지
13:30 05. 밥은 먹었니
17:02 06. 식어 가는 차
20:45 07. 가로등 아래서
24:10 08. 남겨 둔 자리
27:35 09. 보내지 않은 말
31:00 10. 불은 꺼지지 않아
34:25 11. 난로 옆에서
38:00 12. 내일의 아침

제작: 한걸음씩 (AON Production)
구독과 좋아요, 따뜻한 댓글은 더 좋은 음악을 만드는 큰 힘이 됩니다. 🌿
""".strip()

    meta_guide = """
🚀 [메타 3초 원스톱 배포 가이드]:
1. 인스타그램 앱에서 [릴스 만들기] -> 영상 선택 후 위 '인스타그램 릴스 캡션' 붙여넣기
2. 하단 [추가 옵션] -> [페이스북에 추천 공유] 스위치 ON
3. 하단 [스레드(Threads)에 동시 공유] 스위치 ON
4. [공유하기] 버튼 1번 터치 -> 인스타·페이스북·스레드 3대 SNS 동시 업로드 완료! (3초 컷)
""".strip()

    return {
        "ok": True,
        "target": target,
        "tiktok": tiktok_copy,
        "instagram_reels": reels_copy,
        "threads": threads_copy,
        "youtube_description": yt_desc,
        "meta_3sec_guide": meta_guide
    }


def get_master_summary() -> Dict[str, Any]:
    """대표님의 6대 자산 제국 통합 마스터 브리핑."""
    albums_info = get_distrokid_albums()
    yt_info = get_youtube_channels()
    sns_info = get_sns_hub()
    blogger_info = get_blogger_info()

    return {
        "organ_id": ORGAN_ID,
        "organ_name": ORGAN_NAME,
        "version": VERSION,
        "antibody": ANTIBODY,
        "hexagram": HEXAGRAM,
        "owner": "이상일 대표님 (사령관)",
        "assets_count": 6,
        "distrokid": {
            "artist": albums_info["artist_label"],
            "total_albums": albums_info["total_albums"],
            "total_tracks": albums_info["total_tracks"],
            "album_1": f"《가을과 겨울 사이》 (12곡 · {albums_info['albums'][0]['dday']})",
            "album_2": f"《잔상》 (15곡 · {albums_info['albums'][1]['dday']})"
        },
        "youtube": {
            "channels": [f"{c['name']} ({c['handle']})" for c in yt_info["channels"]]
        },
        "sns": {
            "tiktok": f"{sns_info.get('tiktok', {}).get('handle', '@boosterplaylist')} (팔로워 {sns_info.get('tiktok', {}).get('followers', 2125):,}명)",
            "meta": "인스타·스레드·페북 원스톱 연동 스위치"
        },
        "blogger": {
            "url": blogger_info["url"],
            "title": blogger_info["title"],
            "dna_count": len(blogger_info.get("topics_dna", []))
        }
    }


def self_test() -> int:
    """제36기관 25대 무결성 셀프테스트 수행."""
    passed = 0
    total = 25
    print(f"[{ORGAN_NAME}] 셀프테스트 시작 (버전: {VERSION}, 항체: {ANTIBODY})")

    # 1. 원장 로드 검증
    ledger = load_empire_ledger()
    assert isinstance(ledger, dict), "1. 원장 딕셔너리 로드 실패"
    passed += 1

    # 2. DistroKid 아티스트명
    dk = get_distrokid_albums()
    assert dk["artist_label"] == "한걸음씩", "2. 아티스트명 불일치"
    passed += 1

    # 3. 앨범 수 (2개)
    assert dk["total_albums"] == 2, "3. 앨범 수 불일치"
    passed += 1

    # 4. 총 트랙 수 (27곡)
    assert dk["total_tracks"] == 27, f"4. 총 트랙수 27곡 불일치 (실제: {dk['total_tracks']})"
    passed += 1

    # 5. 정규 1집 타이틀 및 트랙수 (12곡)
    a1 = dk["albums"][0]
    assert a1["title"] == "가을과 겨울 사이" and len(a1["tracks"]) == 12, "5. 정규 1집 불일치"
    passed += 1

    # 6. 정규 1집 1번 트랙 '막차'
    assert a1["tracks"][0]["title"] == "막차", "6. 정규 1집 1번 트랙 불일치"
    passed += 1

    # 7. 정규 1집 UPC 검증
    assert a1["upc"] == "700563848544", "7. 정규 1집 UPC 불일치"
    passed += 1

    # 8. 정규 2집 타이틀 및 트랙수 (15곡)
    a2 = dk["albums"][1]
    assert a2["title"] == "잔상" and len(a2["tracks"]) == 15, "8. 정규 2집 불일치"
    passed += 1

    # 9. 정규 2집 1번 트랙 '답장은 천천히'
    assert a2["tracks"][0]["title"] == "답장은 천천히", "9. 정규 2집 1번 트랙 불일치"
    passed += 1

    # 10. 정규 2집 UPC 검증
    assert a2["upc"] == "700486463268", "10. 정규 2집 UPC 불일치"
    passed += 1

    # 11. D-Day 계산 검증 (테스트 기준일 2026-10-27)
    base_test_date = datetime.date(2026, 10, 27)
    d1 = calculate_dday("2026-11-06", base_test_date)
    assert d1["diff_days"] == 10 and d1["label"] == "D-10", f"11. D-Day 계산 오류: {d1}"
    passed += 1

    # 12. 정규 2집 D-Day 계산 (2026-11-27 -> D-31)
    d2 = calculate_dday("2026-11-27", base_test_date)
    assert d2["diff_days"] == 31 and d2["label"] == "D-31", f"12. D-Day 2집 계산 오류: {d2}"
    passed += 1

    # 13. 유튜브 3채널 검증
    yt = get_youtube_channels()
    assert yt["total_channels"] == 3, "13. 유튜브 채널 3개 불일치"
    passed += 1

    # 14. 유튜브 제1채널 핸들
    assert yt["channels"][0]["handle"] == "@한걸음씩-r4i", "14. 제1채널 핸들 불일치"
    passed += 1

    # 15. 유튜브 제2채널 핸들
    assert yt["channels"][1]["handle"] == "@Booster_Playlist", "15. 제2채널 핸들 불일치"
    passed += 1

    # 16. 유튜브 제3채널 핸들
    assert yt["channels"][2]["handle"] == "@TheCaféHour", "16. 제3채널 핸들 불일치"
    passed += 1

    # 17. 틱톡 팔로워 검증 (2,125명)
    sns = get_sns_hub()
    assert sns["tiktok"]["followers"] == 2125, "17. 틱톡 팔로워 불일치"
    passed += 1

    # 18. 틱톡 핸들 검증 (@boosterplaylist)
    assert sns["tiktok"]["handle"] == "@boosterplaylist", "18. 틱톡 핸들 불일치"
    passed += 1

    # 19. 구글 블로거 URL 검증
    blogger = get_blogger_info()
    assert "https://connect-ai-shin.blogspot.com/" in blogger["url"], "19. 블로거 URL 불일치"
    passed += 1

    # 20. 구글 블로거 7대 DNA 주제 검증
    assert len(blogger["topics_dna"]) == 7, "20. 블로그 7대 주제 수 불일치"
    passed += 1

    # 21. 블로그 초안 생성기 검증 (HTML + 면책고지 + 내부링크)
    post = generate_blog_post("야간근무 수면 루틴")
    assert post["ok"] is True and "면책 고지" in post["html_content"] and "https://connect-ai-shin.blogspot.com/" in post["html_content"], "21. 블로그 초안 생성 오류"
    passed += 1

    # 22. SNS 4대 플랫폼 프로모션 문구 생성 검증
    promo = generate_sns_promotions("가을과 겨울 사이")
    assert promo["ok"] is True and "부스터플리" in promo["tiktok"] and "3초 원스톱" in promo["meta_3sec_guide"], "22. SNS 프로모션 생성 오류"
    passed += 1

    # 23. 타임스탬프 포함 유튜브 설명문 생성 검증
    assert "00:00 01. 막차" in promo["youtube_description"], "23. 타임스탬프 오류"
    passed += 1

    # 24. 통합 마스터 브리핑 검증
    summary = get_master_summary()
    assert summary["assets_count"] == 6 and summary["distrokid"]["total_tracks"] == 27, "24. 통합 요약 오류"
    passed += 1

    # 25. 주역 괘상 및 항체 일치 검증
    assert summary["antibody"] == ANTIBODY and summary["hexagram"] == HEXAGRAM, "25. 괘상/항체 불일치"
    passed += 1

    print(f"[{ORGAN_NAME}] 셀프테스트 100% 통과! (성공: {passed}/{total})")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    elif "--status" in sys.argv or "--summary" in sys.argv:
        print(json.dumps(get_master_summary(), ensure_ascii=False, indent=2))
        sys.exit(0)
    elif "--album" in sys.argv:
        print(json.dumps(get_distrokid_albums(), ensure_ascii=False, indent=2))
        sys.exit(0)
    elif "--youtube" in sys.argv:
        print(json.dumps(get_youtube_channels(), ensure_ascii=False, indent=2))
        sys.exit(0)
    elif "--sns" in sys.argv:
        print(json.dumps(get_sns_hub(), ensure_ascii=False, indent=2))
        sys.exit(0)
    elif "--blog" in sys.argv:
        print(json.dumps(get_blogger_info(), ensure_ascii=False, indent=2))
        sys.exit(0)
    elif "--generate-blog" in sys.argv:
        topic = " ".join([a for a in sys.argv[1:] if a != "--generate-blog"]) or "3조 2교대 건강 관리"
        print(json.dumps(generate_blog_post(topic), ensure_ascii=False, indent=2))
        sys.exit(0)
    elif "--generate-sns" in sys.argv:
        tgt = " ".join([a for a in sys.argv[1:] if a != "--generate-sns"]) or "가을과 겨울 사이"
        print(json.dumps(generate_sns_promotions(tgt), ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        sys.exit(self_test())
