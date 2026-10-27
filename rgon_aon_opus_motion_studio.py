# -*- coding: utf-8 -*-
"""
rgon_aon_opus_motion_studio.py [제35기관: 클로드 오퍼스 5.5 모션 그래픽 스튜디오]
================================================================================
버전: v11.58-AON-LIVE-BRAIN-MOTION
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

VERSION = "v11.58-AON-LIVE-BRAIN-MOTION"
ORGAN_ID = 35
ORGAN_NAME = "아온 클로드 오퍼스 5.5 모션 그래픽 스튜디오"
SKILL_NAME = "aon-opus-motion-studio"
ANTIBODY = "R59_REAL_LLM_INBOX_OPUS_MOTION_ZERO_CANNED_LOCK"

PRESETS = {
    "hangeoreum_shorts": {
        "title": "한걸음 쇼츠 (9:16 키네틱 타이포 & 구독자 카운트업)",
        "ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "duration": 10.0,
        "storyboard": {
            "hook": "0~2s: 한걸음씩 클라우드 키네틱 타이포 임팩트",
            "story": "2~5s: 35대 기관 무결점 자율 신경망 & 55스킬 가동",
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
        if "hangeoreum_shorts" in content: passes += 1
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
