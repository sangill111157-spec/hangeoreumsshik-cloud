# -*- coding: utf-8 -*-
"""
rgon_aon_opus_motion_studio.py [제35기관: 클로드 오퍼스 5.5 모션 그래픽 스튜디오]
================================================================================
버전: v11.61-AON-GDRIVE-5TB-DECIMAL
소유: 기술총리 안총리 & 35대 기관 만능 참모 아온이 (이상일 대표님 직속)
항체: R59_REAL_LLM_INBOX_OPUS_MOTION_ZERO_CANNED_LOCK

[핵심 기능]
1. 결정론적 Canvas 모션 그래픽 스튜디오 메타데이터 & 시크 제어
2. 3대 내장 프리셋:
   - hangeoreum_shorts (9:16 키네틱 타이포 + 실시간 구독자 카운트업)
   - nvda_chart_motion (16:9 엔비디아 NVDA 퀀트 매매 차트 드로잉)
   - haesang_aon_mv (9:16 우주복 아온이 캐릭터 점프 + 16밴드 오디오 스펙트럼)
3. 4단 스토리보드 (Anthropic Claude Motion 규격):
   - Hook (0~2s) -> Story (2~5s) -> Data Count-up Chart (5~8s) -> Logo CTA (8~10s)
4. MediaRecorder WebM 실시간 캡처 지원 및 소통창 인라인 iframe 렌더링
================================================================================
"""

import sys
import os
import json
import math
from typing import Dict, Any, List

VERSION = "v11.61-AON-GDRIVE-5TB-DECIMAL"
ORGAN_ID = 35
ORGAN_NAME = "아온 클로드 오퍼스 5.5 모션 그래픽 스튜디오"
SKILL_NAME = "aon-opus-motion-studio"
ANTIBODY = "R60_EMPIRE_ASSET_HUB_LOCK"

PRESETS = {
    "hangeoreum_album1": {
        "title": "🍁 [한걸음씩 정규1집] 《가을과 겨울 사이》 (11/6 발매 · 12트랙 MV)",
        "ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 늦가을 새벽 바람 & 막차 전철역 네온",
            "story": "2~5s: 12트랙 감성 멜로디 파형 & 가사 키네틱 타이포",
            "data_chart": "5~8s: 24개 글로벌 플랫폼 D-Day 카운트다운",
            "logo_cta": "8~10s: 한걸음씩 공식 유튜브 & 멜론/스포티파이 스트리밍"
        }
    },
    "hangeoreum_album2": {
        "title": "🥃 [한걸음씩 정규2집] 《잔상》 (11/27 발매 · 15트랙 MV)",
        "ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 비 내리는 창가 잔상 & 아날로그 필름 노이즈",
            "story": "2~5s: 15트랙 서정적 스트링 오케스트레이션",
            "data_chart": "5~8s: 트랙리스트 타임스탬프 15곡 자동 롤링",
            "logo_cta": "8~10s: 전 세계 24개 스트리밍 플랫폼 정식 발매"
        }
    },
    "booster_playlist": {
        "title": "⚡ [부스터 플리 & 틱톡 @boosterplaylist] 네온 이퀄라이저",
        "ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 1시간 Phonk & Workout 비트 폭발",
            "story": "2~5s: 네온 사이버펑크 펄스 & 런닝 페이스 드로잉",
            "data_chart": "5~8s: 틱톡 팔로워 2,125명 & 최고조회 2.2만회 카운트업",
            "logo_cta": "8~10s: @boosterplaylist 팔로우 & 유튜브 풀버전 링크"
        }
    },
    "cafe_hour": {
        "title": "☕ [The Café Hour] 빗소리·창가 카페 재즈 라운지",
        "ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 모닝 카페 에스프레소 & 빗소리 앰비언스",
            "story": "2~5s: 편안한 재즈 피아노 & 보사노바 스펙트럼",
            "data_chart": "5~8s: MORNING · AFTERNOON · EVENING 1.5시간 타임라인",
            "logo_cta": "8~10s: The Café Hour (@TheCaféHour) 구독 & 힐링 플레이"
        }
    },
    "blogger_health": {
        "title": "📝 [건강 블로그 connect-ai-shin] 3조 2교대 건강 자동 칼럼",
        "ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 3조 2교대 12시간 야간근무 건강 관리의 핵심",
            "story": "2~5s: 500ml 텀블러 3번(1.5L) & 퇴근 후 15분 걷기 루틴",
            "data_chart": "5~8s: 특수건강진단(130조) & 야간수당(56조) 실전 가이드",
            "logo_cta": "8~10s: connect-ai-shin.blogspot.com 공식 블로그 발행"
        }
    },
    "hangeoreum_shorts": {
        "title": "한걸음 쇼츠 (9:16 키네틱 타이포 & 구독자 카운트업)",
        "ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 한걸음씩 클라우드 키네틱 타이포 임팩트",
            "story": "2~5s: 36대 기관 무결점 자율 신경망 & 56스킬 가동",
            "data_chart": "5~8s: 실시간 구독자 카운트업 128,400명 (달성률 100%)",
            "logo_cta": "8~10s: 유튜브 구독 & 알림설정 펄스 버튼"
        }
    },
    "nvda_chart_motion": {
        "title": "NVDA 차트 (16:9 엔비디아 실시간 퀀트 매매 드로잉)",
        "ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: NVIDIA NVDA AI 반도체 시그널",
            "story": "2~5s: STRONG BUY 알고리즘 신뢰도 99.4%",
            "data_chart": "5~8s: 체결가 $148.50 드로잉 (+18.42%)",
            "logo_cta": "8~10s: 오토트레이딩 시스템 승인 ⚡"
        }
    },
    "haesang_aon_mv": {
        "title": "아온 우주뮤비 (9:16 우주복 아온이 & 16-Band 오디오 스펙트럼)",
        "ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 우주 헬멧 바이저 오픈 & 별빛 파티클",
            "story": "2~5s: 아온이 스페이스 점프 & 은하수 유영",
            "data_chart": "5~8s: 16-Band 오디오 스펙트럼 비트싱크 이퀄라이저",
            "logo_cta": "8~10s: 이해상 디자이너 x 클로드 오퍼스 5.5 콜라보 🚀"
        }
    }
}

def get_preset_meta(preset_key: str = "hangeoreum_shorts") -> Dict[str, Any]:
    return PRESETS.get(preset_key, PRESETS["hangeoreum_shorts"])

def simulate_frame(preset_key: str, t: float) -> Dict[str, Any]:
    """결정론적 렌더링 프레임 상태 계산 (window.seek(t) 검증용)"""
    meta = get_preset_meta(preset_key)
    duration = meta["duration"]
    clamped_t = max(0.0, min(float(t), duration))
    
    if clamped_t < 2.0:
        phase = "Hook"
    elif clamped_t < 5.0:
        phase = "Story"
    elif clamped_t < 8.0:
        phase = "Data Count-up Chart"
    else:
        phase = "Logo CTA"
        
    return {
        "preset": preset_key,
        "time": round(clamped_t, 3),
        "phase": phase,
        "resolution": f"{meta['width']}x{meta['height']}",
        "ratio": meta["ratio"]
    }

def get_motion_preview_media(preset_key: str = "hangeoreum_shorts") -> Dict[str, Any]:
    """채팅창 말풍선 인라인 렌더링용 미디어 객체 생성"""
    meta = get_preset_meta(preset_key)
    return {
        "type": "motion_studio",
        "studio_url": "rgon_motion_preview.html",
        "preset": preset_key,
        "title": meta["title"],
        "ratio": meta["ratio"],
        "width": meta["width"],
        "height": meta["height"],
        "duration": meta["duration"],
        "storyboard": meta["storyboard"]
    }

def run_self_test() -> bool:
    """제35기관 무결점 시뮬레이션 및 자율 검증 (100.0점)"""
    print(f"[{ORGAN_NAME}] 자율 검증 시작: {VERSION} ({ANTIBODY})")
    passes = 0
    total = 20

    # 1~6: 프리셋 메타데이터 무결성
    for k in ["hangeoreum_shorts", "nvda_chart_motion", "haesang_aon_mv"]:
        m = get_preset_meta(k)
        if m["duration"] == 10.0 and "storyboard" in m:
            passes += 2
        else:
            print(f"FAIL: preset {k}")

    # 7~14: 결정론적 시크 프레임 시뮬레이션
    test_cases = [
        ("hangeoreum_shorts", 0.5, "Hook"),
        ("hangeoreum_shorts", 3.2, "Story"),
        ("hangeoreum_shorts", 6.1, "Data Count-up Chart"),
        ("hangeoreum_shorts", 9.4, "Logo CTA"),
        ("nvda_chart_motion", 1.0, "Hook"),
        ("nvda_chart_motion", 4.0, "Story"),
        ("nvda_chart_motion", 7.5, "Data Count-up Chart"),
        ("haesang_aon_mv", 8.8, "Logo CTA")
    ]
    for p, t, expected_phase in test_cases:
        st = simulate_frame(p, t)
        if st["phase"] == expected_phase:
            passes += 1
        else:
            print(f"FAIL: simulate {p} at {t}s -> {st['phase']} != {expected_phase}")

    # 15~18: HTML 파일 실존 및 필수 규격 점검
    html_path = os.path.join(os.path.dirname(__file__), "rgon_motion_preview.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "window.seek" in content: passes += 1
        if "MediaRecorder" in content: passes += 1
        if ("hangeoreum_shorts" in content or "hangeoreum_album1" in content): passes += 1
        if "nvda_chart_motion" in content: passes += 1
    else:
        print("FAIL: rgon_motion_preview.html not found")

    # 19~20: 미디어 객체 생성 검증
    media = get_motion_preview_media("hangeoreum_shorts")
    if media["type"] == "motion_studio" and media["studio_url"] == "rgon_motion_preview.html":
        passes += 2

    score = (passes / total) * 100.0
    print(f"[{ORGAN_NAME}] 검증 결과: {passes}/{total} 통과 ({score:.1f}점)")
    return score >= 100.0

if __name__ == "__main__":
    success = run_self_test()
    sys.exit(0 if success else 1)
