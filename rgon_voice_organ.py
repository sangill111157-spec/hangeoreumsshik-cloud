#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_voice_organ.py — 제9기관: 성대·청각 음성 교감 기관 (v11.32-AON-VOICE-SYNTH, R1~R33)
주역 #51 진위뢰(震爲雷 ☳☳): 우레처럼 맑은 울림으로 만물을 깨움.
주역 #61 풍택중부(風澤中孚 ☴☱): 鶴鳴在陰 其子和之 — 진실한 목소리로 마음이 서로 통함."""
import os, sys, json, re
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v11.32-AON-VOICE-SYNTH"
ANTIBODY = "R1~R33"
ROOT = Path(__file__).resolve().parent
ICHING = {
    "51": {"name": "진위뢰(震爲雷 ☳☳)", "meaning": "우레처럼 맑은 울림으로 만물을 깨움"},
    "61": {"name": "풍택중부(風澤中孚 ☴☱)", "meaning": "진실한 목소리로 마음이 서로 통함 — 鶴鳴在陰 其子和之"},
}
SOUND_RECIPES = {
    "waterdrop_pop": {"desc": "아온 쓰다듬기/터치 — 맑은 퐁당💧", "wave": "sine",
                      "notes": [{"f0": 520, "f1": 1180, "t": 0.0, "dur": 0.14}],
                      "env": {"a": 0.005, "d": 0.13, "peak": 0.35}},
    "summon_chime": {"desc": "아온 소환 — C5-E5-G5-C6 크리스탈 차임", "wave": "triangle",
                     "notes": [{"f0": f, "f1": f, "t": i * 0.09, "dur": 0.5} for i, f in
                               enumerate([523.25, 659.25, 783.99, 1046.5])],
                     "env": {"a": 0.01, "d": 0.49, "peak": 0.25}},
    "approve_fanfare": {"desc": "뮤즈 Tier 3 결재 승인 — G5-B5-D6-G6 하프 화음", "wave": "triangle",
                        "notes": [{"f0": f, "f1": f, "t": i * 0.07, "dur": 0.7} for i, f in
                                  enumerate([783.99, 987.77, 1174.66, 1567.98])],
                        "env": {"a": 0.008, "d": 0.69, "peak": 0.25}},
    "clean_sweep": {"desc": "배설·정화 완료 — 청량한 상승 하모닉 스윕", "wave": "sine",
                    "notes": [{"f0": 330 * k, "f1": 990 * k, "t": (k - 1) * 0.04, "dur": 0.45} for k in (1, 2, 3)],
                    "env": {"a": 0.02, "d": 0.43, "peak": 0.18}},
    "radar_ping": {"desc": "오감 레이더/3자 심판 알림 — 부드러운 소나 핑", "wave": "sine",
                   "notes": [{"f0": 1320, "f1": 1240, "t": 0.0, "dur": 0.6}],
                   "env": {"a": 0.004, "d": 0.6, "peak": 0.3}},
    "stt_listen": {"desc": "음성 인식 시작/종료 — 듀얼 톤 비프", "wave": "sine",
                   "notes": [{"f0": 880, "f1": 880, "t": 0.0, "dur": 0.08},
                             {"f0": 1320, "f1": 1320, "t": 0.1, "dur": 0.08}],
                   "env": {"a": 0.004, "d": 0.075, "peak": 0.3}},
}
VOICE_PROFILE = {"lang": "ko-KR", "pitch": 1.18, "rate": 1.05, "volume": 1.0, "muted": False,
                 "preferred_voices": ["Microsoft SunHi Online (Natural)", "Google 한국의", "Yuna", "ko-KR"]}
ROUTES = [("briefing", ("브리핑", "아침")), ("judge", ("심판", "종목", "장세")), ("muse", ("결재", "대행"))]
TIER3_KW = ("매수", "매도", "주문", "송금", "이체", "결제", "삭제", "배포", "푸시", "push", "발송", "계약", "리밸런싱", "배분")
TIER2_KW = ("수정", "작성", "생성", "업로드", "편집", "변경", "등록", "정리", "분석", "시뮬레이션", "초안")

def classify_tier(text):
    try:
        import rgon_muse_delegator as md
        for fn in ("classify_tier", "classify_task", "classify"):
            f = getattr(md, fn, None)
            if callable(f):
                r = f(text)
                if isinstance(r, int) and r in (1, 2, 3): return r
                if isinstance(r, dict) and r.get("tier") in (1, 2, 3): return r["tier"]
    except Exception:
        pass
    if any(k in text for k in TIER3_KW): return 3
    if any(k in text for k in TIER2_KW): return 2
    return 1

def _load_json(rel):
    p = ROOT / rel
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return {}

def parse_voice_command(text):
    t = (text or "").strip()
    for intent, kws in ROUTES:
        if any(k in t for k in kws):
            if intent == "briefing":
                b = _load_json("rgon_morning_brief.json")
                summ = b.get("summary") or b.get("headline") or "오늘도 사령부는 정상 가동 중이에요"
                return {"intent": "briefing", "speech": f"대표님, 아침 브리핑이에요. {summ}. 오늘의 괘는 {ICHING['51']['name']}입니다."}
            if intent == "judge":
                return {"intent": "judge", "speech": "3자 심판 요약이에요. 찬성, 반대, 중립 의견을 레이더에서 확인해 주세요.", "open": "judge"}
            return {"intent": "muse", "speech": "뮤즈 대행 보드를 열게요. 결재 대기 작업을 확인해 주세요.", "open": "muse"}
    tier = classify_tier(t)
    return {"intent": "delegate", "payload": {"title": t, "tier": tier, "source": "voice", "status": "PENDING_APPROVAL" if tier == 3 else "DONE"},
            "speech": f"알겠어요! '{t}' 작업을 Tier {tier}로 대행 큐에 올렸어요." + (" 승인해 주셔야 집행해요." if tier == 3 else "")}

def state():
    return {"version": VERSION, "antibody": ANTIBODY, "organ": "제9기관 성대·청각 음성 교감 기관",
            "iching": ICHING, "voice_profile": VOICE_PROFILE, "sound_recipes": SOUND_RECIPES}

def save():
    s = json.dumps(state(), ensure_ascii=False, indent=2) + "\n"
    for r in ("rgon_voice_profile.json", "docs/rgon_voice_profile.json"):
        p = ROOT / r; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(s, encoding="utf-8")

def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m); ok = ok and c
    chk(len(SOUND_RECIPES) == 6, "사운드 레시피 6종")
    wd = SOUND_RECIPES["waterdrop_pop"]["notes"][0]
    chk(wd["f0"] == 520 and wd["f1"] == 1180 and abs(wd["dur"] - 0.14) < 1e-9, "waterdrop_pop 520→1180Hz 0.14s")
    for k, r in SOUND_RECIPES.items():
        e = r["env"]
        good = all(20 <= n["f0"] <= 20000 and 20 <= n["f1"] <= 20000 and n["dur"] > 0 for n in r["notes"])
        good = good and 0 < e["a"] < 0.1 and e["d"] > 0 and 0 < e["peak"] <= 0.5
        chk(good, f"{k} 주파수/엔벨로프")
    chk(VOICE_PROFILE["pitch"] == 1.18 and VOICE_PROFILE["rate"] == 1.05 and VOICE_PROFILE["lang"] == "ko-KR", "K-아이 보이스 프로필")
    chk(parse_voice_command("아침 브리핑 해줘")["intent"] == "briefing", "라우팅: 브리핑")
    chk(parse_voice_command("오늘 장세 어때")["intent"] == "judge", "라우팅: 심판")
    chk(parse_voice_command("결재 보여줘")["intent"] == "muse", "라우팅: 대행")
    d = parse_voice_command("삼성전자 매수 주문 넣어줘")
    chk(d["intent"] == "delegate" and d["payload"]["tier"] == 3, "라우팅: 대행 큐 Tier 3")
    save()
    for r in ("rgon_voice_profile.json", "docs/rgon_voice_profile.json"):
        try: j = json.loads((ROOT / r).read_text(encoding="utf-8")); chk(j.get("version") == VERSION, f"JSON 무결성 {r}")
        except Exception as ex: chk(False, f"JSON 무결성 {r}: {ex}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(self_test())
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        print(json.dumps(parse_voice_command(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2)); sys.exit(0)
    save(); print(json.dumps(state(), ensure_ascii=False)[:400]); sys.exit(0)
