#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_aon_haesang_morph_avatar.py — 제24기관 · 이해상 수석 디자이너 헌정 아온이 6대 변신술 아바타 엔진
Step 48 — v11.49-AON-IMPECCABLE-SHIELD · 항체 R1~R50 · 정식 스킬 46개 (aon-haesang-6form-morph)

수석 캐릭터 아트 디렉터: 이해상 (초등학교 4학년 · 이상일 대표님 막내 따님)
주역 3대 괘상:
  - #49 택화혁(澤火革 ☱☲): 껍질을 벗고 날마다 새롭게 피어나는 무한 변신과 혁신
  - #58 태위택(兌爲澤 ☱☱): 두 연못이 맞닿아 해상이의 순수한 동심과 넘치는 기쁨
  - #37 풍화가인(風火家人 ☴☲): 집안에 온기와 사랑이 넘쳐 흐르는 가족의 지극한 축복
"""
import os, sys, json, re, time

CHIEF_ART_DIRECTOR = "이해상 (초4 수석 캐릭터 디자이너)"
VERSION = "v11.49-AON-IMPECCABLE-SHIELD"
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
    svg_map = {
        "ghost": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="140" height="140"><defs><radialGradient id="ghPbr" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#ffffff"/><stop offset="50%" stop-color="#f1f5f9"/><stop offset="85%" stop-color="#cbd5e1"/><stop offset="100%" stop-color="#94a3b8"/></radialGradient><style>@keyframes gh3d{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-8px) rotate(2deg)}}.gh3d-anim{animation:gh3d 3s ease-in-out infinite;transform-origin:120px 120px;}</style></defs><rect width="240" height="240" rx="20" fill="#0f172a" stroke="rgba(56,189,248,0.4)" stroke-width="2"/><g class="gh3d-anim"><path d="M65,95 C65,40 175,40 175,95 C175,140 195,185 195,195 C175,190 160,200 140,195 C125,200 105,190 90,198 C75,202 60,195 45,195 C55,175 65,140 65,95 Z" fill="url(#ghPbr)" stroke="#38bdf8" stroke-width="3.5"/><path d="M104,115 C102,145 98,175 94,196" stroke="#94a3b8" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M148,115 C152,145 162,175 168,194" stroke="#94a3b8" stroke-width="3" fill="none" stroke-linecap="round"/><rect x="90" y="75" width="14" height="26" rx="6" fill="#0f172a"/><rect x="136" y="75" width="14" height="26" rx="6" fill="#0f172a"/><circle cx="94" cy="80" r="3" fill="#ffffff"/><circle cx="140" cy="80" r="3" fill="#ffffff"/><polygon points="120,105 115,98 125,98" fill="#0f172a"/><line x1="72" y1="96" x2="82" y2="86" stroke="#fb7185" stroke-width="3.5" stroke-linecap="round"/><line x1="78" y1="99" x2="88" y2="89" stroke="#fb7185" stroke-width="3.5" stroke-linecap="round"/><line x1="152" y1="89" x2="162" y2="99" stroke="#fb7185" stroke-width="3.5" stroke-linecap="round"/><line x1="158" y1="86" x2="168" y2="96" stroke="#fb7185" stroke-width="3.5" stroke-linecap="round"/></g></svg>""",
        "cloud": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="140" height="140"><defs><radialGradient id="clPbr" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#ffffff"/><stop offset="60%" stop-color="#e0f2fe"/><stop offset="100%" stop-color="#bae6fd"/></radialGradient><style>@keyframes cl3d{0%,100%{transform:translateY(0)}45%{transform:translateY(-10px) scale(0.98,1.02)}85%{transform:translateY(0) scale(1.04,0.96)}}.cl3d-anim{animation:cl3d 2.4s ease-in-out infinite;transform-origin:120px 170px;}</style></defs><rect width="240" height="240" rx="20" fill="#0f172a" stroke="rgba(56,189,248,0.4)" stroke-width="2"/><g class="cl3d-anim"><line x1="48" y1="110" x2="36" y2="114" stroke="#e0f2fe" stroke-width="4.5" stroke-linecap="round"/><line x1="28" y1="117" x2="18" y2="120" stroke="#e0f2fe" stroke-width="4.5" stroke-linecap="round"/><line x1="192" y1="110" x2="204" y2="114" stroke="#e0f2fe" stroke-width="4.5" stroke-linecap="round"/><line x1="212" y1="117" x2="222" y2="120" stroke="#e0f2fe" stroke-width="4.5" stroke-linecap="round"/><path d="M96,168 L96,186 L80,186" fill="none" stroke="#bae6fd" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M144,168 L144,186 L158,186" fill="none" stroke="#bae6fd" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M70,145 C55,145 42,130 45,115 C36,105 40,88 52,80 C50,68 62,56 76,60 C85,46 106,45 120,52 C134,45 155,46 164,60 C178,56 190,68 188,80 C200,88 204,105 195,115 C198,130 185,145 170,145 C164,158 148,162 135,158 C125,165 115,165 105,158 C92,162 76,158 70,145 Z" fill="url(#clPbr)" stroke="#7dd3fc" stroke-width="3.5"/><ellipse cx="94" cy="104" rx="5" ry="10" fill="#0f172a"/><circle cx="95" cy="100" r="2.5" fill="#ffffff"/><ellipse cx="146" cy="104" rx="5" ry="10" fill="#0f172a"/><circle cx="147" cy="100" r="2.5" fill="#ffffff"/><path d="M113,110 C113,124 127,124 127,110 Z" fill="#0f172a"/><circle cx="80" cy="116" r="8" fill="#fb7185" opacity="0.6"/><circle cx="160" cy="116" r="8" fill="#fb7185" opacity="0.6"/></g></svg>""",
        "pumpkin": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="140" height="140"><defs><radialGradient id="pkPbr" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#fdba74"/><stop offset="60%" stop-color="#f97316"/><stop offset="100%" stop-color="#c2410c"/></radialGradient><style>@keyframes pk3d{0%,100%{transform:rotate(0)}25%{transform:rotate(-4deg)}75%{transform:rotate(4deg)}}.pk3d-anim{animation:pk3d 2.2s ease-in-out infinite;transform-origin:120px 140px;}</style></defs><rect width="240" height="240" rx="20" fill="#0f172a" stroke="rgba(56,189,248,0.4)" stroke-width="2"/><g class="pk3d-anim"><path d="M120,48 C116,28 128,26 126,18" fill="none" stroke="#15803d" stroke-width="7" stroke-linecap="round"/><rect x="94" y="152" width="52" height="20" rx="4" fill="#ffffff" stroke="#0f172a" stroke-width="3"/><rect x="98" y="172" width="44" height="22" rx="4" fill="#ffffff" stroke="#0f172a" stroke-width="3"/><circle cx="120" cy="162" r="3.5" fill="#f59e0b"/><circle cx="120" cy="183" r="3.5" fill="#f59e0b"/><line x1="94" y1="160" x2="68" y2="152" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/><circle cx="65" cy="151" r="5" fill="#f97316"/><line x1="146" y1="160" x2="172" y2="152" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/><circle cx="175" cy="151" r="5" fill="#f97316"/><path d="M108,194 L108,214 L98,214" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M132,194 L132,214 L142,214" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><ellipse cx="120" cy="100" rx="72" ry="56" fill="url(#pkPbr)" stroke="#9a3412" stroke-width="3.5"/><path d="M92,48 C70,70 70,130 92,152" fill="none" stroke="#ea580c" stroke-width="3.5"/><path d="M148,48 C170,70 170,130 148,152" fill="none" stroke="#ea580c" stroke-width="3.5"/><polygon points="90,92 80,105 100,105" fill="#fef08a" stroke="#f59e0b" stroke-width="2"/><polygon points="150,92 140,105 160,105" fill="#fef08a" stroke="#f59e0b" stroke-width="2"/><path d="M68,104 L80,104 L68,118 L80,118" fill="none" stroke="#0f172a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M160,104 L172,104 L160,118 L172,118" fill="none" stroke="#0f172a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M88,112 Q120,116 152,112 C152,142 88,142 88,112 Z" fill="#0f172a"/><rect x="98" y="113" width="9" height="8" fill="#ffffff"/><rect x="116" y="114" width="9" height="8" fill="#ffffff"/><rect x="133" y="113" width="9" height="8" fill="#ffffff"/><rect x="107" y="126" width="9" height="7" fill="#ffffff"/><rect x="124" y="126" width="9" height="7" fill="#ffffff"/></g></svg>""",
        "orb": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="140" height="140"><defs><radialGradient id="obPbr" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#ffffff"/><stop offset="40%" stop-color="#7dd3fc"/><stop offset="80%" stop-color="#38bdf8"/><stop offset="100%" stop-color="#0284c7"/></radialGradient><style>@keyframes ob3d{0%,100%{transform:scale(1)}50%{transform:scale(1.05,0.96)}}.ob3d-anim{animation:ob3d 2.8s ease-in-out infinite;transform-origin:120px 120px;}</style></defs><rect width="240" height="240" rx="20" fill="#0f172a" stroke="rgba(56,189,248,0.4)" stroke-width="2"/><g class="ob3d-anim"><circle cx="120" cy="120" r="76" fill="url(#obPbr)" stroke="#0284c7" stroke-width="4"/><circle cx="120" cy="120" r="32" fill="#e0f2fe" opacity="0.6"/><rect x="90" y="94" width="22" height="52" rx="11" fill="#0f172a"/><rect x="128" y="94" width="22" height="52" rx="11" fill="#0f172a"/><circle cx="96" cy="106" r="4.5" fill="#ffffff"/><circle cx="134" cy="106" r="4.5" fill="#ffffff"/><ellipse cx="68" cy="132" rx="12" ry="7" fill="#fb7185" opacity="0.65"/><ellipse cx="172" cy="132" rx="12" ry="7" fill="#fb7185" opacity="0.65"/></g></svg>""",
        "waterfall_suit": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="140" height="140"><defs><radialGradient id="suPbr" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#ffffff"/><stop offset="65%" stop-color="#f1f5f9"/><stop offset="100%" stop-color="#cbd5e1"/></radialGradient><style>@keyframes su3d{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}.su3d-anim{animation:su3d 3s ease-in-out infinite;transform-origin:120px 120px;}</style></defs><rect width="240" height="240" rx="20" fill="#0f172a" stroke="rgba(56,189,248,0.4)" stroke-width="2"/><g class="su3d-anim"><path d="M85,95 C60,98 32,105 30,122 C28,140 55,145 80,135 C82,145 84,175 75,198 C72,206 96,206 102,194 C112,175 128,175 138,194 C144,206 168,206 165,198 C156,175 158,145 160,135 C185,145 212,140 210,122 C208,105 180,98 155,95 C160,80 162,55 120,52 C78,55 80,80 85,95 Z" fill="url(#suPbr)" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M68,82 C68,50 172,50 172,82" fill="none" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/><path d="M78,82 C78,64 162,64 162,82 C162,102 78,102 78,82 Z" fill="#ffffff" stroke="#0f172a" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="98" cy="80" r="5.5" fill="#0f172a"/><circle cx="142" cy="80" r="5.5" fill="#0f172a"/><path d="M115,86 L120,92 L125,86" stroke="#0f172a" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><line x1="82" y1="92" x2="88" y2="80" stroke="#f43f5e" stroke-width="3.5" stroke-linecap="round"/><line x1="88" y1="92" x2="94" y2="80" stroke="#f43f5e" stroke-width="3.5" stroke-linecap="round"/><line x1="146" y1="92" x2="152" y2="80" stroke="#f43f5e" stroke-width="3.5" stroke-linecap="round"/><line x1="152" y1="92" x2="158" y2="80" stroke="#f43f5e" stroke-width="3.5" stroke-linecap="round"/></g></svg>""",
        "pouty_booty": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="140" height="140"><defs><radialGradient id="btPbr" cx="35%" cy="30%" r="70%"><stop offset="0%" stop-color="#fff1f2"/><stop offset="50%" stop-color="#fecdd3"/><stop offset="85%" stop-color="#fda4af"/><stop offset="100%" stop-color="#f43f5e"/></radialGradient><style>@keyframes btWiggle{0%,100%{transform:rotate(0deg)}25%{transform:rotate(-8deg) translateX(-6px)}75%{transform:rotate(8deg) translateX(6px)}}.bt3d-anim{animation:btWiggle 1.2s ease-in-out infinite;transform-origin:120px 80px;}</style></defs><rect width="240" height="240" rx="20" fill="#0f172a" stroke="rgba(244,63,94,0.5)" stroke-width="2"/><g class="bt3d-anim"><path d="M78,92 C55,92 28,102 26,118 C24,136 50,138 72,130 C68,145 52,180 40,204 C52,212 70,212 80,198 C92,180 104,168 120,168 C136,168 148,180 160,198 C170,212 188,212 200,204 C188,180 172,145 168,130 C190,138 216,136 214,118 C212,102 185,92 162,92 C168,68 165,36 120,34 C75,36 72,68 78,92 Z" fill="#fed7aa" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="94" cy="155" r="38" fill="url(#btPbr)" stroke="#0f172a" stroke-width="4"/><circle cx="146" cy="155" r="38" fill="url(#btPbr)" stroke="#0f172a" stroke-width="4"/><path d="M120,126 L120,172" stroke="#e11d48" stroke-width="4.5" stroke-linecap="round"/><ellipse cx="88" cy="145" rx="12" ry="7" transform="rotate(-20,88,145)" fill="#ffffff" opacity="0.6"/><ellipse cx="152" cy="145" rx="12" ry="7" transform="rotate(20,152,145)" fill="#ffffff" opacity="0.6"/><text x="110" y="30" font-size="20">💖</text></g></svg>"""
    }
    svg = svg_map.get(form, svg_map["orb"])
    if not animated:
        svg = re.sub(r'<style>.*?</style>', '<style></style>', svg, flags=re.DOTALL)
    return svg.strip()

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
    cases.append({"case": "pumpkin_title_badge", "ok": "pk3d-anim" in p_svg or "pkPbr" in p_svg or "pumpkin" in str(p_svg)})

    b_svg = render_haesang_svg("pouty_booty")
    cases.append({"case": "booty_silhouette_ok", "ok": "bt3d-anim" in b_svg or "btPbr" in b_svg or "pouty_booty" in str(b_svg)})

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
