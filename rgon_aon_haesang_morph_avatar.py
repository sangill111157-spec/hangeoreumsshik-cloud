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
        anim_css = """
        @keyframes ghostFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-10px) rotate(2deg); }
        }
        .aon-ghost-grp { animation: ghostFloat 3.2s ease-in-out infinite; transform-origin: center; }
        """
        svg_body = """
        <g class="aon-ghost-grp">
            <path d="M40,165 C35,110 45,45 120,45 C195,45 205,110 200,165 C185,155 175,175 160,165 C145,155 135,175 120,165 C105,155 95,175 80,165 C65,155 55,175 40,165 Z"
                  fill="url(#ghostGrad)" stroke="#cbd5e1" stroke-width="3" filter="url(#softShadow)"/>
            <rect x="92" y="85" width="8" height="22" rx="4" fill="#0f172a"/>
            <rect x="140" y="85" width="8" height="22" rx="4" fill="#0f172a"/>
            <polygon points="120,118 115,110 125,110" fill="#f43f5e"/>
            <g stroke="#fb7185" stroke-width="2.5" stroke-linecap="round">
                <line x1="72" y1="106" x2="78" y2="98"/>
                <line x1="80" y1="106" x2="86" y2="98"/>
                <line x1="154" y1="106" x2="160" y2="98"/>
                <line x1="162" y1="106" x2="168" y2="98"/>
            </g>
        </g>
        """

    elif form == "cloud":
        anim_css = """
        @keyframes cloudBounce {
            0%, 100% { transform: translateY(0) scale(1); }
            45% { transform: translateY(-12px) scale(1.03, 0.97); }
            55% { transform: translateY(-12px) scale(0.98, 1.02); }
            90% { transform: translateY(0) scale(1.05, 0.92); }
        }
        .aon-cloud-grp { animation: cloudBounce 2.5s ease-in-out infinite; transform-origin: bottom center; }
        """
        svg_body = """
        <g class="aon-cloud-grp">
            <line x1="95" y1="170" x2="95" y2="195" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
            <line x1="145" y1="170" x2="145" y2="195" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
            <circle cx="93" cy="197" r="5" fill="#0f172a"/>
            <circle cx="147" cy="197" r="5" fill="#0f172a"/>
            <line x1="50" y1="125" x2="28" y2="135" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
            <circle cx="26" cy="136" r="6" fill="#38bdf8"/>
            <line x1="190" y1="125" x2="212" y2="135" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>
            <circle cx="214" cy="136" r="6" fill="#38bdf8"/>
            <path d="M70,150 C50,150 40,130 45,110 C40,90 60,75 80,80 C90,60 120,55 140,70 C155,60 185,65 190,90 C205,100 205,130 190,145 C195,160 175,170 160,165 C145,175 125,175 110,168 C95,175 75,170 70,150 Z"
                  fill="url(#cloudGrad)" stroke="#38bdf8" stroke-width="3.5" filter="url(#softShadow)"/>
            <circle cx="98" cy="112" r="5" fill="#0f172a"/>
            <circle cx="100" cy="110" r="1.5" fill="#ffffff"/>
            <circle cx="142" cy="112" r="5" fill="#0f172a"/>
            <circle cx="144" cy="110" r="1.5" fill="#ffffff"/>
            <path d="M112,125 Q120,135 128,125" stroke="#0f172a" stroke-width="3" fill="none" stroke-linecap="round"/>
            <ellipse cx="86" cy="122" rx="7" ry="4" fill="#f472b6" opacity="0.6"/>
            <ellipse cx="154" cy="122" rx="7" ry="4" fill="#f472b6" opacity="0.6"/>
        </g>
        """

    elif form == "pumpkin":
        anim_css = """
        @keyframes pumpkinDance {
            0%, 100% { transform: rotate(0deg) scale(1); }
            25% { transform: rotate(-5deg) scale(1.02); }
            75% { transform: rotate(5deg) scale(0.98); }
        }
        .aon-pumpkin-grp { animation: pumpkinDance 1.8s ease-in-out infinite; transform-origin: 120px 140px; }
        """
        svg_body = """
        <g class="aon-pumpkin-grp">
            <g transform="translate(120, 26)">
                <rect x="-38" y="-14" width="76" height="24" rx="8" fill="#fb923c" stroke="#c2410c" stroke-width="2"/>
                <text x="0" y="3" font-family="'Pretendard', sans-serif" font-weight="900" font-size="14" fill="#ffffff" text-anchor="middle">" 호 박 "</text>
            </g>
            <line x1="75" y1="165" x2="45" y2="155" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
            <line x1="165" y1="165" x2="195" y2="155" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
            <ellipse cx="120" cy="180" rx="30" ry="25" fill="#38bdf8" stroke="#0284c7" stroke-width="3"/>
            <line x1="105" y1="200" x2="105" y2="218" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
            <line x1="135" y1="200" x2="135" y2="218" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>
            <path d="M115,50 C115,35 125,35 128,30" stroke="#15803d" stroke-width="6" fill="none" stroke-linecap="round"/>
            <ellipse cx="120" cy="105" rx="72" ry="58" fill="url(#pumpkinGrad)" stroke="#c2410c" stroke-width="3.5" filter="url(#softShadow)"/>
            <path d="M85,55 C65,75 65,135 85,155" stroke="#ea580c" stroke-width="3" fill="none" opacity="0.6"/>
            <path d="M155,55 C175,75 175,135 155,155" stroke="#ea580c" stroke-width="3" fill="none" opacity="0.6"/>
            <path d="M120,47 C110,75 110,135 120,163" stroke="#ea580c" stroke-width="2.5" fill="none" opacity="0.5"/>
            <polygon points="95,85 85,102 105,102" fill="#0f172a"/>
            <polygon points="145,85 135,102 155,102" fill="#0f172a"/>
            <path d="M68,110 L78,110 L68,122 L78,122" stroke="#ea580c" stroke-width="3" fill="none" stroke-linecap="round"/>
            <path d="M162,110 L172,110 L162,122 L172,122" stroke="#ea580c" stroke-width="3" fill="none" stroke-linecap="round"/>
            <path d="M88,118 Q120,150 152,118 Z" fill="#0f172a"/>
            <rect x="105" y="120" width="10" height="9" fill="#ffffff" rx="1"/>
            <rect x="125" y="120" width="10" height="9" fill="#ffffff" rx="1"/>
        </g>
        """

    elif form == "orb":
        anim_css = """
        @keyframes orbJelly {
            0%, 100% { transform: scale(1, 1); }
            30% { transform: scale(1.08, 0.92); }
            60% { transform: scale(0.94, 1.06); }
            80% { transform: scale(1.02, 0.98); }
        }
        .aon-orb-grp { animation: orbJelly 3s ease-in-out infinite; transform-origin: 120px 125px; }
        """
        svg_body = """
        <g class="aon-orb-grp">
            <circle cx="120" cy="125" r="75" fill="url(#orbGrad)" stroke="#38bdf8" stroke-width="3.5" filter="url(#softShadow)"/>
            <ellipse cx="95" cy="85" rx="20" ry="10" transform="rotate(-30, 95, 85)" fill="#ffffff" opacity="0.6"/>
            <ellipse cx="98" cy="122" rx="5" ry="14" fill="#0f172a"/>
            <ellipse cx="142" cy="122" rx="5" ry="14" fill="#0f172a"/>
            <path d="M114,136 Q120,143 126,136" stroke="#0f172a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            <circle cx="82" cy="132" r="7" fill="#fb7185" opacity="0.45"/>
            <circle cx="158" cy="132" r="7" fill="#fb7185" opacity="0.45"/>
        </g>
        """

    elif form == "waterfall_suit":
        anim_css = """
        @keyframes waterfallFlow {
            0%, 100% { stroke-dashoffset: 0; opacity: 0.85; }
            50% { stroke-dashoffset: 30; opacity: 1; }
        }
        @keyframes suitHover {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        .aon-suit-grp { animation: suitHover 3.5s ease-in-out infinite; transform-origin: center; }
        .waterfall-line { stroke-dasharray: 12, 6; animation: waterfallFlow 1.5s linear infinite; }
        """
        svg_body = """
        <g class="aon-suit-grp">
            <g stroke="#38bdf8" stroke-width="5" stroke-linecap="round" opacity="0.75" class="waterfall-line">
                <path d="M120,35 C60,40 30,90 25,215" fill="none"/>
                <path d="M120,35 C80,45 45,100 40,215" fill="none"/>
                <path d="M120,35 C180,40 210,90 215,215" fill="none"/>
                <path d="M120,35 C160,45 195,100 200,215" fill="none"/>
            </g>
            <rect x="90" y="165" width="22" height="38" rx="10" fill="#f1f5f9" stroke="#94a3b8" stroke-width="3"/>
            <rect x="128" y="165" width="22" height="38" rx="10" fill="#f1f5f9" stroke="#94a3b8" stroke-width="3"/>
            <rect x="42" y="115" width="35" height="20" rx="10" transform="rotate(25, 42, 115)" fill="#f1f5f9" stroke="#94a3b8" stroke-width="3"/>
            <rect x="165" y="128" width="35" height="20" rx="10" transform="rotate(-25, 165, 128)" fill="#f1f5f9" stroke="#94a3b8" stroke-width="3"/>
            <ellipse cx="120" cy="145" rx="48" ry="42" fill="url(#suitGrad)" stroke="#94a3b8" stroke-width="3.5" filter="url(#softShadow)"/>
            <circle cx="120" cy="95" r="48" fill="#0f172a" stroke="#38bdf8" stroke-width="4"/>
            <circle cx="120" cy="96" r="38" fill="url(#faceGrad)"/>
            <ellipse cx="106" cy="94" rx="3.5" ry="7" fill="#0f172a"/>
            <ellipse cx="134" cy="94" rx="3.5" ry="7" fill="#0f172a"/>
            <path d="M116,104 Q120,109 124,104" stroke="#0f172a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            <path d="M92,98 L96,92 L100,98 L104,92 L108,98" stroke="#f43f5e" stroke-width="2" fill="none" stroke-linecap="round"/>
            <path d="M132,98 L136,92 L140,98 L144,92 L148,98" stroke="#f43f5e" stroke-width="2" fill="none" stroke-linecap="round"/>
        </g>
        """

    elif form == "pouty_booty":
        anim_css = """
        @keyframes bootyWiggle {
            0%, 100% { transform: rotate(0deg); }
            25% { transform: rotate(-6deg) translateX(-3px); }
            75% { transform: rotate(6deg) translateX(3px); }
        }
        .aon-booty-grp { animation: bootyWiggle 1.4s ease-in-out infinite; transform-origin: 120px 100px; }
        """
        svg_body = """
        <g class="aon-booty-grp">
            <path d="M75,105 C40,100 30,115 35,125 C45,130 65,120 75,120" fill="url(#orbGrad)" stroke="#38bdf8" stroke-width="3"/>
            <path d="M165,105 C200,100 210,115 205,125 C195,130 175,120 165,120" fill="url(#orbGrad)" stroke="#38bdf8" stroke-width="3"/>
            <rect x="92" y="175" width="16" height="24" rx="8" fill="#bae6fd" stroke="#38bdf8" stroke-width="3"/>
            <rect x="132" y="175" width="16" height="24" rx="8" fill="#bae6fd" stroke="#38bdf8" stroke-width="3"/>
            <path d="M68,110 C60,65 180,65 172,110 C182,145 160,185 120,185 C80,185 58,145 68,110 Z"
                  fill="url(#orbGrad)" stroke="#38bdf8" stroke-width="3.5" filter="url(#softShadow)"/>
            <path d="M82,148 C92,176 118,176 120,154" stroke="#0284c7" stroke-width="3.5" fill="none" stroke-linecap="round"/>
            <path d="M120,154 C122,176 148,176 158,148" stroke="#0284c7" stroke-width="3.5" fill="none" stroke-linecap="round"/>
            <line x1="120" y1="145" x2="120" y2="168" stroke="#0284c7" stroke-width="3" stroke-linecap="round"/>
            <circle cx="78" cy="95" r="5" fill="#f43f5e" opacity="0.75"/>
            <circle cx="85" cy="85" r="3" fill="#f43f5e" opacity="0.6"/>
            <path d="M155,75 L165,70 M165,75 L155,70" stroke="#f43f5e" stroke-width="2.5" stroke-linecap="round"/>
        </g>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="{width}" height="{height}" class="aon-morph-svg">
    <defs>
        <radialGradient id="ghostGrad" cx="40%" cy="35%" r="65%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="70%" stop-color="#f1f5f9"/>
            <stop offset="100%" stop-color="#cbd5e1"/>
        </radialGradient>
        <radialGradient id="cloudGrad" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="65%" stop-color="#e0f2fe"/>
            <stop offset="100%" stop-color="#bae6fd"/>
        </radialGradient>
        <radialGradient id="pumpkinGrad" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#fdba74"/>
            <stop offset="65%" stop-color="#fb923c"/>
            <stop offset="100%" stop-color="#ea580c"/>
        </radialGradient>
        <radialGradient id="orbGrad" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="45%" stop-color="#e0f2fe"/>
            <stop offset="85%" stop-color="#7dd3fc"/>
            <stop offset="100%" stop-color="#38bdf8"/>
        </radialGradient>
        <radialGradient id="suitGrad" cx="40%" cy="35%" r="65%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="80%" stop-color="#e2e8f0"/>
            <stop offset="100%" stop-color="#cbd5e1"/>
        </radialGradient>
        <radialGradient id="faceGrad" cx="40%" cy="35%" r="65%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="70%" stop-color="#f0f9ff"/>
            <stop offset="100%" stop-color="#e0f2fe"/>
        </radialGradient>
        <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#0284c7" flood-opacity="0.22"/>
        </filter>
        <style>
            {anim_css if animated else ""}
        </style>
    </defs>
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
    cases.append({"case": "pumpkin_title_badge", "ok": '" 호 박 "' in p_svg or '호박' in p_svg})

    b_svg = render_haesang_svg("pouty_booty")
    cases.append({"case": "booty_silhouette_ok", "ok": "aon-booty-grp" in b_svg and "M82,148" in b_svg})

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
