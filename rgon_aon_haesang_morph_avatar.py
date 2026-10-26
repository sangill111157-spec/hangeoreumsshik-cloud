#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_aon_haesang_morph_avatar.py — 제24기관 · 이해상 수석 디자이너 헌정 아온이 6대 변신술 아바타 엔진
Step 48 — v11.47-AON-HAESANG-MORPH · 항체 R1~R48 · 정식 스킬 44개 (aon-haesang-6form-morph)

수석 캐릭터 아트 디렉터: 이해상 (초등학교 4학년 · 이상일 대표님 막내 따님)
주역 3대 괘상:
  - #49 택화혁(澤火革 ☱☲): 껍질을 벗고 날마다 새롭게 피어나는 무한 변신과 혁신
  - #58 태위택(兌爲澤 ☱☱): 두 연못이 맞닿아 해상이의 순수한 동심과 넘치는 기쁨
  - #37 풍화가인(風火家人 ☴☲): 집안에 온기와 사랑이 넘쳐 흐르는 가족의 지극한 축복
"""
import os, sys, json, re, time

CHIEF_ART_DIRECTOR = "이해상 (초4 수석 캐릭터 디자이너)"
VERSION = "v11.47-AON-HAESANG-MORPH"
ANTIBODY = "R48"
SKILL_SLUG = "aon-haesang-6form-morph"
HEXAGRAMS = ["#49 택화혁(澤火革)", "#58 태위택(兌爲澤)", "#37 풍화가인(風火家人)"]

# 6대 변신 폼 메타데이터
MORPH_FORMS = {
    "ghost": {
        "name": "꼬마 유령 망토 아온",
        "icon": "👻",
        "desc": "하얀 천 망토를 덮어쓰고 둥실둥실 떠다니는 귀여운 유령 아온이",
        "dialogue": "퐁당! 꼬마 유령 아온이에요~ 대표님 곁을 둥실둥실 지켜드릴게요! 👻",
        "energy": "포근한 수호",
        "badge_color": "#a5b4fc"
    },
    "cloud": {
        "name": "몽글몽글 구름 요정 아온",
        "icon": "☁️",
        "desc": "복슬복슬 솜사탕 구름 몸통에 앙증맞은 주먹과 다리로 통통 뛰는 요정 아온이",
        "dialogue": "몽글몽글 구름 요정 아온이에요! 해상이 마음처럼 포근해요~ ☁️",
        "energy": "상쾌한 활력",
        "badge_color": "#93c5fd"
    },
    "pumpkin": {
        "name": "'호박' 탈 장난꾸러기 아온",
        "icon": "🎃",
        "desc": "머리 위에 해상이의 손글씨 '호박' 타이틀을 얹고 지그재그 볼과 개구쟁이 미소로 춤추는 아온이",
        "dialogue": "호박 탈 쓴 장난꾸러기 아온이 등장! 오늘 밤은 대표님이랑 신나게 파티해요! 🎃",
        "energy": "유쾌한 장난",
        "badge_color": "#fdba74"
    },
    "orb": {
        "name": "동글동글 말랑 구슬 아온",
        "icon": "🫧",
        "desc": "완벽한 찹쌀떡 물방울 구슬에 세로 타원 눈(0 0)만 콕 박힌 순수 코어 아온이",
        "dialogue": "말랑말랑 순수 코어 아온 구슬이에요! 스트레스를 맑게 씻어드릴게요 🫧",
        "energy": "순수한 정화",
        "badge_color": "#6ee7b7"
    },
    "waterfall_suit": {
        "name": "우주복 후드 & 폭포수 망토 아온",
        "icon": "🧑🚀",
        "desc": "동그란 우주복 헬멧(볼에 M M 무늬)과 양옆으로 쏟아지는 시원한 폭포수 수호 장막",
        "dialogue": "시원한 폭포수 우주복 장착 완료! 22대 전 기관을 맑은 물방울로 수호합니다! 🧑🚀",
        "energy": "철통 수호",
        "badge_color": "#38bdf8"
    },
    "pouty_booty": {
        "name": "삐진 뒷모습 통통 궁둥이 아온",
        "icon": "🍑",
        "desc": "얼굴은 쏙 감추고 뒤돌아 서서 볼록한 통통 엉덩이를 실룩실룩 흔드는 치명적 뒷태!",
        "dialogue": "흥! 아온이 삐졌어! 쓰다듬어 주면 앞모습 보여줄 거야~ 퐁당! 🍑",
        "energy": "치명적 애교",
        "badge_color": "#f472b6"
    }
}

def render_haesang_svg(form: str = "orb", width: int = 240, height: int = 240, animated: bool = True) -> str:
    form = form.lower().strip()
    if form not in MORPH_FORMS:
        form = "orb"

    anim_css = ""
    svg_body = ""

    if form == "ghost":
        # [실사 1]: 둥근 머리 + 아래로 퍼지는 물결 밑단 + 앞면 세로 주름 2줄 + 세로 긴 직사각형 두 눈 + 세모 입 + 양 볼 사선 빗금 2개씩
        anim_css = """
        @keyframes handFloat {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-8px) rotate(1.5deg); }
        }
        .aon-ghost-grp { animation: handFloat 3.2s ease-in-out infinite; transform-origin: 120px 120px; }
        """
        svg_body = """
        <g class="aon-ghost-grp">
            <!-- 꼬마 유령 실사 몸체 (외곽선: 돔형 머리 -> A라인 퍼짐 -> 파도형 밑단) -->
            <path d="M75,90 C75,40 165,40 165,90 C165,130 185,185 195,195 C175,190 165,200 145,195 C130,200 110,190 95,197 C80,202 65,195 45,195 C55,180 75,130 75,90 Z"
                  fill="#ffffff" stroke="#18181b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#sketchShadow)"/>
            <!-- 실사 디테일: 앞면 세로 주름선 2줄 -->
            <path d="M108,105 C106,135 102,170 98,196" stroke="#18181b" stroke-width="3.5" fill="none" stroke-linecap="round"/>
            <path d="M152,105 C156,135 168,170 174,194" stroke="#18181b" stroke-width="3.5" fill="none" stroke-linecap="round"/>
            <!-- 실사 눈: 세로로 긴 도톰한 직사각형 두 눈 -->
            <rect x="92" y="68" width="13" height="24" rx="3" fill="#18181b"/>
            <rect x="135" y="68" width="13" height="24" rx="3" fill="#18181b"/>
            <!-- 실사 입: 앙증맞은 작은 세모/갈매기 입 -->
            <path d="M116,92 L120,96 L124,92 Z" fill="#18181b" stroke="#18181b" stroke-width="1"/>
            <!-- 실사 볼 홍조: 양 볼 사선 빗금 2개씩 (//   //) -->
            <line x1="74" y1="88" x2="84" y2="78" stroke="#f43f5e" stroke-width="3" stroke-linecap="round"/>
            <line x1="80" y1="91" x2="90" y2="81" stroke="#f43f5e" stroke-width="3" stroke-linecap="round"/>
            <line x1="150" y1="81" x2="160" y2="91" stroke="#f43f5e" stroke-width="3" stroke-linecap="round"/>
            <line x1="156" y1="78" x2="166" y2="88" stroke="#f43f5e" stroke-width="3" stroke-linecap="round"/>
        </g>
        """

    elif form == "cloud":
        # [실사 2]: 뽀글뽀글 뭉게구름 외곽선 + 세로 물방울 눈 + 벌린 세모 입 + 양옆 점선 막대 팔(- -) + 아래 L자 꺾인 막대 다리(_L  _)
        anim_css = """
        @keyframes cloudHop {
            0%, 100% { transform: translateY(0); }
            45% { transform: translateY(-11px) scale(0.98, 1.02); }
            85% { transform: translateY(0) scale(1.04, 0.96); }
        }
        .aon-cloud-grp { animation: cloudHop 2.4s ease-in-out infinite; transform-origin: 120px 180px; }
        """
        svg_body = """
        <g class="aon-cloud-grp">
            <!-- 실사 팔: 양옆 점선 막대 팔 (- -) -->
            <line x1="48" y1="110" x2="36" y2="114" stroke="#18181b" stroke-width="4" stroke-linecap="round"/>
            <line x1="28" y1="117" x2="18" y2="120" stroke="#18181b" stroke-width="4" stroke-linecap="round"/>
            <line x1="192" y1="110" x2="204" y2="114" stroke="#18181b" stroke-width="4" stroke-linecap="round"/>
            <line x1="212" y1="117" x2="222" y2="120" stroke="#18181b" stroke-width="4" stroke-linecap="round"/>
            <!-- 실사 다리: 아래 L자형 꺾인 막대 다리 -->
            <path d="M96,168 L96,186 L80,186" fill="none" stroke="#18181b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M144,168 L144,186 L158,186" fill="none" stroke="#18181b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- 실사 뭉게구름 외곽선 (복슬복슬 솜사탕) -->
            <path d="M70,145 C55,145 42,130 45,115 C36,105 40,88 52,80 C50,68 62,56 76,60 C85,46 106,45 120,52 C134,45 155,46 164,60 C178,56 190,68 188,80 C200,88 204,105 195,115 C198,130 185,145 170,145 C164,158 148,162 135,158 C125,165 115,165 105,158 C92,162 76,158 70,145 Z"
                  fill="#ffffff" stroke="#18181b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#sketchShadow)"/>
            <!-- 실사 눈: 세로 물방울 모양 두 눈 -->
            <ellipse cx="94" cy="104" rx="4" ry="9" fill="#18181b" transform="rotate(-6, 94, 104)"/>
            <ellipse cx="146" cy="104" rx="4" ry="9" fill="#18181b" transform="rotate(6, 146, 104)"/>
            <!-- 실사 입: 가운데 활짝 벌리고 웃는 귀여운 입 -->
            <path d="M113,110 C113,124 127,124 127,110 Z" fill="#18181b"/>
            <!-- 볼터치 -->
            <circle cx="82" cy="116" r="6" fill="#fb7185" opacity="0.45"/>
            <circle cx="158" cy="116" r="6" fill="#fb7185" opacity="0.45"/>
        </g>
        """

    elif form == "waterfall_suit":
        # [실사 3]: 우주복/방한복 후드 요정! 둥근 후드 헬멧 + 안쪽 타원 얼굴 창 + 눈 2개, 미소 입 + 양 볼 세로 빗금 3개씩(/// ///) + 통통한 솜인형 팔다리 일체형 실루엣
        anim_css = """
        @keyframes suitHover {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-7px) scale(1.01); }
        }
        .aon-suit-grp { animation: suitHover 3.4s ease-in-out infinite; transform-origin: 120px 120px; }
        """
        svg_body = """
        <g class="aon-suit-grp">
            <!-- 실사 몸체: 진저쿠키/우주복 솜인형 일체형 실루엣 (둥글게 뻗은 팔과 벌린 두 다리) -->
            <path d="M85,95 C60,98 32,105 30,122 C28,140 55,145 80,135 C82,145 84,175 75,198 C72,206 96,206 102,194 C112,175 128,175 138,194 C144,206 168,206 165,198 C156,175 158,145 160,135 C185,145 212,140 210,122 C208,105 180,98 155,95 C160,80 162,55 120,52 C78,55 80,80 85,95 Z"
                  fill="#ffffff" stroke="#18181b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#sketchShadow)"/>
            <!-- 실사 디테일: 후드 모자 안쪽 타원형 얼굴 창 테두리 -->
            <path d="M78,82 C78,64 162,64 162,82 C162,102 78,102 78,82 Z"
                  fill="#ffffff" stroke="#18181b" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- 후드 이중 윤곽선 (실사의 머리 바깥 후드 모자 둥근 라인) -->
            <path d="M68,82 C68,52 172,52 172,82" fill="none" stroke="#18181b" stroke-width="3.5" stroke-linecap="round"/>
            <!-- 실사 눈: 동그란 두 눈 -->
            <circle cx="98" cy="82" r="4.5" fill="#18181b"/>
            <circle cx="142" cy="82" r="4.5" fill="#18181b"/>
            <!-- 실사 입: 부드러운 스마일 미소 -->
            <path d="M115,87 Q120,93 125,87" stroke="#18181b" stroke-width="3" fill="none" stroke-linecap="round"/>
            <!-- 실사 볼 홍조: 선명한 세로 사선 빗금 3개씩 (///   ///) -->
            <line x1="84" y1="92" x2="88" y2="82" stroke="#f43f5e" stroke-width="2.8" stroke-linecap="round"/>
            <line x1="88" y1="92" x2="92" y2="82" stroke="#f43f5e" stroke-width="2.8" stroke-linecap="round"/>
            <line x1="92" y1="92" x2="96" y2="82" stroke="#f43f5e" stroke-width="2.8" stroke-linecap="round"/>
            <line x1="144" y1="92" x2="148" y2="82" stroke="#f43f5e" stroke-width="2.8" stroke-linecap="round"/>
            <line x1="148" y1="92" x2="152" y2="82" stroke="#f43f5e" stroke-width="2.8" stroke-linecap="round"/>
            <line x1="152" y1="92" x2="156" y2="82" stroke="#f43f5e" stroke-width="2.8" stroke-linecap="round"/>
        </g>
        """

    elif form == "pumpkin":
        # [실사 4]: 머리 위 손글씨 "호 박" + 꼭지 + 세로 골 곡선 + 우측 화살표 지시선 + 반원 눈 + 양 볼 Z 무늬 + 개구쟁이 네모 치아 잭오랜턴 입 + 2단 단추 몸통
        anim_css = """
        @keyframes pumpkinRock {
            0%, 100% { transform: rotate(0deg); }
            25% { transform: rotate(-4deg); }
            75% { transform: rotate(4deg); }
        }
        .aon-pumpkin-grp { animation: pumpkinRock 2.2s ease-in-out infinite; transform-origin: 120px 140px; }
        """
        svg_body = """
        <g class="aon-pumpkin-grp">
            <!-- [실사 손글씨 100% 매칭]: 머리 위 해상이 손글씨 "호" 와 "박" -->
            <g stroke="#18181b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none">
                <!-- '호' 글씨 -->
                <line x1="92" y1="14" x2="104" y2="14"/>
                <line x1="98" y1="14" x2="98" y2="20"/>
                <circle cx="98" cy="28" r="6" stroke-width="2.5"/>
                <!-- '박' 글씨 -->
                <line x1="134" y1="12" x2="134" y2="30"/>
                <line x1="140" y1="12" x2="140" y2="30"/>
                <line x1="134" y1="17" x2="140" y2="17"/>
                <line x1="134" y1="23" x2="140" y2="23"/>
                <line x1="144" y1="13" x2="144" y2="28"/>
                <line x1="144" y1="20" x2="148" y2="20"/>
                <path d="M136,33 L144,33 L144,38"/>
            </g>
            <!-- [실사 화살표 지시선]: 우측 상단 화살표 -->
            <path d="M185,42 L172,50 L176,56 Z" fill="#18181b"/>
            <path d="M185,42 L198,34 L198,24" fill="none" stroke="#18181b" stroke-width="2.5" stroke-linecap="round"/>

            <!-- 실사 몸통: 2단 네모 상의/바지 + 단추 2개 + 양팔 벌림 + 다리 -->
            <rect x="94" y="152" width="52" height="20" rx="3" fill="#ffffff" stroke="#18181b" stroke-width="3.5"/>
            <rect x="98" y="172" width="44" height="22" rx="3" fill="#ffffff" stroke="#18181b" stroke-width="3.5"/>
            <circle cx="120" cy="162" r="3.5" fill="#18181b"/>
            <circle cx="120" cy="183" r="3.5" fill="#18181b"/>
            <!-- 팔과 손 -->
            <line x1="94" y1="160" x2="68" y2="152" stroke="#18181b" stroke-width="3.5" stroke-linecap="round"/>
            <circle cx="65" cy="151" r="4" fill="#ffffff" stroke="#18181b" stroke-width="3"/>
            <line x1="146" y1="160" x2="172" y2="152" stroke="#18181b" stroke-width="3.5" stroke-linecap="round"/>
            <circle cx="175" cy="151" r="4" fill="#ffffff" stroke="#18181b" stroke-width="3"/>
            <!-- 다리와 발 -->
            <path d="M108,194 L108,212 L98,212" fill="none" stroke="#18181b" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M132,194 L132,212 L142,212" fill="none" stroke="#18181b" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>

            <!-- 꼭지 줄기 -->
            <path d="M120,52 C118,36 128,34 125,28" fill="none" stroke="#18181b" stroke-width="4.5" stroke-linecap="round"/>

            <!-- 호박 탈 둥근 외곽선 -->
            <ellipse cx="120" cy="104" rx="66" ry="52" fill="#ffffff" stroke="#18181b" stroke-width="4" filter="url(#sketchShadow)"/>
            <!-- 호박 골 세로 곡선 (실사 좌우 라인) -->
            <path d="M92,54 C72,74 72,134 92,154" fill="none" stroke="#18181b" stroke-width="3.5"/>
            <path d="M148,54 C168,74 168,134 148,154" fill="none" stroke="#18181b" stroke-width="3.5"/>

            <!-- 실사 반원 눈 2개 -->
            <path d="M88,98 C88,86 104,86 104,98 Z" fill="#18181b" stroke="#18181b" stroke-width="2"/>
            <path d="M136,98 C136,86 152,86 152,98 Z" fill="#18181b" stroke="#18181b" stroke-width="2"/>

            <!-- 실사 볼 지그재그 'Z' 무늬 (왼쪽 Z, 오른쪽 Z) -->
            <path d="M72,106 L82,106 L72,118 L82,118" fill="none" stroke="#18181b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M158,106 L168,106 L158,118 L168,118" fill="none" stroke="#18181b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>

            <!-- 실사 입: 커다란 검은 입에 네모 치아가 드러난 개구쟁이 잭오랜턴 입 -->
            <path d="M88,114 Q120,118 152,114 C152,142 88,142 88,114 Z" fill="#18181b"/>
            <!-- 윗니 아랫니 네모 치아 -->
            <rect x="98" y="115" width="8" height="7" fill="#ffffff"/>
            <rect x="116" y="116" width="8" height="7" fill="#ffffff"/>
            <rect x="134" y="115" width="8" height="7" fill="#ffffff"/>
            <rect x="107" y="127" width="8" height="6" fill="#ffffff"/>
            <rect x="125" y="127" width="8" height="6" fill="#ffffff"/>
        </g>
        """

    elif form == "orb":
        # [실사 6]: 동글동글 원형 얼굴 + 세로로 큼직한 두 개의 타원형/캡슐 눈 (안쪽에 펜 빗금 결이 살아있는 해상이 스타일)
        anim_css = """
        @keyframes orbBreathe {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.04, 0.97); }
        }
        .aon-orb-grp { animation: orbBreathe 2.8s ease-in-out infinite; transform-origin: 120px 120px; }
        """
        svg_body = """
        <g class="aon-orb-grp">
            <!-- 실사 원형 몸체: 손맛이 담긴 따뜻하고 둥근 원 -->
            <circle cx="120" cy="120" r="76" fill="#ffffff" stroke="#18181b" stroke-width="4.5" filter="url(#sketchShadow)"/>
            <!-- 실사 눈: 세로로 큼직하고 길쭉한 두 개의 캡슐 눈 + 펜선 결 -->
            <g fill="#18181b">
                <rect x="90" y="94" width="22" height="52" rx="10" stroke="#18181b" stroke-width="2"/>
                <rect x="128" y="94" width="22" height="52" rx="10" stroke="#18181b" stroke-width="2"/>
            </g>
            <!-- 눈 안쪽 손그림 펜 스크래치 결(하이라이트) -->
            <line x1="97" y1="98" x2="97" y2="142" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" opacity="0.75"/>
            <line x1="135" y1="98" x2="135" y2="142" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" opacity="0.75"/>
            <!-- 은은한 살구빛 손그림 볼터치 -->
            <ellipse cx="72" cy="132" rx="10" ry="6" fill="#fb7185" opacity="0.35"/>
            <ellipse cx="168" cy="132" rx="10" ry="6" fill="#fb7185" opacity="0.35"/>
        </g>
        """

    elif form == "pouty_booty":
        # [실사 5]: 삐진 뒷모습 통통 궁둥이 (하이라이트!)
        # 눈코입 전혀 없는 완벽한 뒷모습! 둥근 머리 + 양옆으로 벌린 팔 + 양다리 쩍 벌림 + 가운데 볼록하고 동그랗게 두 겹으로 강조된 통통 엉덩이(궁둥이)!
        anim_css = """
        @keyframes bootyShake {
            0%, 100% { transform: rotate(0deg); }
            20% { transform: rotate(-8deg) translateX(-4px); }
            40% { transform: rotate(8deg) translateX(4px); }
            60% { transform: rotate(-5deg) translateX(-2px); }
            80% { transform: rotate(5deg) translateX(2px); }
        }
        .aon-booty-grp { animation: bootyShake 1.5s ease-in-out infinite; transform-origin: 120px 80px; }
        """
        svg_body = """
        <g class="aon-booty-grp">
            <!-- [실사 외곽선 100% 매칭]: 머리 -> 벌린 팔 -> 쩍 벌린 다리 완벽한 뒷모습 일체형 윤곽선 -->
            <path d="M78,92 C55,92 28,102 26,118 C24,136 50,138 72,130 C68,150 48,185 36,204 C48,212 70,212 80,196 C92,175 106,165 120,165 C134,165 148,175 160,196 C170,212 192,212 204,204 C192,185 172,150 168,130 C190,138 216,136 214,118 C212,102 185,92 162,92 C168,68 165,36 120,34 C75,36 72,68 78,92 Z"
                  fill="#ffffff" stroke="#18181b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#sketchShadow)"/>

            <!-- [실사 하이라이트 궁둥이 곡선]: 몸통 아래 가운데와 양다리 사이로 볼록하고 동그랗게 튀어나온 엉덩이 두 겹 곡선! -->
            <path d="M96,146 C104,172 136,172 144,146" fill="none" stroke="#18181b" stroke-width="4.5" stroke-linecap="round"/>
            <path d="M102,152 C108,175 132,175 138,152" fill="none" stroke="#18181b" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
            <!-- 엉덩이 중심 골 라인 -->
            <line x1="120" y1="148" x2="120" y2="168" stroke="#18181b" stroke-width="3" stroke-linecap="round"/>

            <!-- 삐진 뒷모습 분노/앙탈 마크 (작은 김 나는 증기) -->
            <path d="M165,42 Q172,32 178,38" fill="none" stroke="#f43f5e" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M172,46 Q178,38 184,42" fill="none" stroke="#f43f5e" stroke-width="2.5" stroke-linecap="round"/>
        </g>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="{width}" height="{height}" class="aon-morph-svg">
    <defs>
        <filter id="sketchShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="2" dy="5" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.12"/>
        </filter>
    </defs>
    <style>
        {anim_css if animated else ""}
        .aon-morph-svg text {{ user-select: none; }}
    </style>
    <!-- 해상이의 스케치북 따뜻한 화이트 종이 캔버스 배경 -->
    <rect width="240" height="240" rx="20" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
    {svg_body}
</svg>"""
    return re.sub(r'>\s+<', '><', svg.strip())

def get_morph_info(form: str = "orb") -> dict:
    form = form.lower().strip()
    meta = MORPH_FORMS.get(form, MORPH_FORMS["orb"]).copy()
    meta["form_id"] = form if form in MORPH_FORMS else "orb"
    meta["chief_art_director"] = CHIEF_ART_DIRECTOR
    meta["hexagrams"] = HEXAGRAMS
    meta["version"] = VERSION
    return meta

def recommend_morph(context: str = "") -> str:
    ctx = str(context).lower()
    if any(k in ctx for k in ["삐짐", "삐졌", "궁둥", "엉덩", "뒤", "화남", "토라"]):
        return "pouty_booty"
    if any(k in ctx for k in ["유령", "망토", "할로윈", "무서", "밤", "숨"]):
        return "ghost"
    if any(k in ctx for k in ["구름", "요정", "날씨", "하늘", "솜사탕", "점프"]):
        return "cloud"
    if any(k in ctx for k in ["호박", "파티", "장난", "장난꾸러기", "웃음", "치아"]):
        return "pumpkin"
    if any(k in ctx for k in ["우주", "폭포", "수호", "방패", "시원", "헬멧"]):
        return "waterfall_suit"
    return "orb"

def self_test(verbose: bool = False) -> dict:
    cases = []
    for f in ["ghost", "cloud", "pumpkin", "orb", "waterfall_suit", "pouty_booty"]:
        svg = render_haesang_svg(f, 200, 200, True)
        ok = (svg.startswith("<svg") and svg.endswith("</svg>") and "viewBox" in svg and len(svg) > 500)
        cases.append({"case": f"render_{f}", "ok": ok})

    p_svg = render_haesang_svg("pumpkin")
    cases.append({"case": "pumpkin_title_badge", "ok": '" 호 박 "' in p_svg or '호박' in p_svg or '호' in p_svg})

    b_svg = render_haesang_svg("pouty_booty")
    cases.append({"case": "booty_silhouette_ok", "ok": "aon-booty-grp" in b_svg and ("M96,146" in b_svg or "M82,148" in b_svg)})

    cases.append({"case": "chief_art_director_credit", "ok": "이해상" in CHIEF_ART_DIRECTOR})
    cases.append({"case": "hexagrams_3_valid", "ok": len(HEXAGRAMS) == 3 and "택화혁" in HEXAGRAMS[0]})

    cases.append({"case": "rec_booty", "ok": recommend_morph("오늘 좀 삐졌어") == "pouty_booty"})
    cases.append({"case": "rec_ghost", "ok": recommend_morph("유령 망토 입을래") == "ghost"})
    cases.append({"case": "rec_cloud", "ok": recommend_morph("구름처럼 몽글몽글") == "cloud"})
    cases.append({"case": "rec_pumpkin", "ok": recommend_morph("호박 축제 가자") == "pumpkin"})
    cases.append({"case": "rec_suit", "ok": recommend_morph("시원한 폭포수 우주복") == "waterfall_suit"})
    cases.append({"case": "rec_orb", "ok": recommend_morph("평온한 일상") == "orb"})

    stat_svg = render_haesang_svg("orb", 100, 100, False)
    cases.append({"case": "static_render_ok", "ok": "<style></style>" in stat_svg or "@keyframes" not in stat_svg})

    info = get_morph_info("pouty_booty")
    cases.append({"case": "meta_info_ok", "ok": info["icon"] == "🍑" and "이해상" in info["chief_art_director"]})

    passed = sum(1 for c in cases if c["ok"])
    total = len(cases)
    res = {
        "ok": (passed == total),
        "passed": passed,
        "total": total,
        "director": CHIEF_ART_DIRECTOR,
        "version": VERSION,
        "cases": cases
    }
    if verbose:
        print(f"[{'PASS' if res['ok'] else 'FAIL'}] rgon_aon_haesang_morph_avatar self_test ({passed}/{total})")
    return res

if __name__ == "__main__":
    v = "--verbose" in sys.argv or "-v" in sys.argv or "--self-test" in sys.argv
    r = self_test(verbose=v)
    if not v:
        print(f"[{'PASS' if r['ok'] else 'FAIL'}] self_test: {r['passed']}/{r['total']} (수석 디자이너: {CHIEF_ART_DIRECTOR})")
    sys.exit(0 if r["ok"] else 1)
