#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_voice_organ.py — 제9기관: 성대·청각 음성 교감 기관 (v11.42-AON-OMNI-NEXUS, R1~R43)
주역 #51 진위뢰(震爲雷 ☳☳) · #61 풍택중부(風澤中孚 ☴☱).
의도 분별은 제10기관 rgon_aon_soul_brain.converse()에 위임한다 (감정·일상 대화는 대행 큐에 넣지 않음)."""
import os, sys, json
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "v11.42-AON-OMNI-NEXUS"
ANTIBODY = "R1~R43"
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import rgon_aon_soul_brain as soul

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

SFX_PRESETS = dict(SOUND_RECIPES)

def parse_voice_command(text, persist=True, use_llm=True):
    r = soul.converse(text, persist=persist, use_llm=use_llm)
    out = {"intent": r["intent"], "category": r["category"], "speech": r["speech"], "reply": r["reply"],
           "affection": r["affection"], "level": r["level"], "source": r.get("source")}
    if r["intent"] == "delegate":
        out["tier"] = r["tier"]; out["payload"] = r["payload"]
    if r.get("open"): out["open"] = r["open"]
    if r["intent"] == "chat": out.update({"sfx": "waterdrop_pop", "joy": True})
    return out

def state():
    return {"version": VERSION, "antibody": ANTIBODY, "organ": "제9기관 성대·청각 음성 교감 기관",
            "brain": "제10기관 rgon_aon_soul_brain", "iching": ICHING,
            "voice_profile": VOICE_PROFILE, "sound_recipes": SOUND_RECIPES}

def save():
    s = json.dumps(state(), ensure_ascii=False, indent=2)
    for r in ("rgon_voice_profile.json", "docs/rgon_voice_profile.json"):
        p = ROOT / r; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(s, encoding="utf-8")

def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m); ok = ok and bool(c)
    chk(len(SOUND_RECIPES) == 6, "사운드 레시피 6종")
    wd = SOUND_RECIPES["waterdrop_pop"]["notes"][0]
    chk(wd["f0"] == 520 and wd["f1"] == 1180 and abs(wd["dur"] - 0.14) < 1e-9, "waterdrop_pop 520→1180Hz 0.14s")
    for k, r in SOUND_RECIPES.items():
        e = r["env"]
        good = all(20 <= n["f0"] <= 20000 and 20 <= n["f1"] <= 20000 and n["dur"] > 0 for n in r["notes"])
        chk(good and 0 < e["a"] < 0.1 and e["d"] > 0 and 0 < e["peak"] <= 0.5, f"{k} 주파수/엔벨로프")
    chk(VOICE_PROFILE["pitch"] == 1.18 and VOICE_PROFILE["rate"] == 1.05 and VOICE_PROFILE["lang"] == "ko-KR", "K-아이 보이스 프로필")
    qa = [("아침 브리핑 해줘", "briefing", None), ("오늘 장세 어때", "judge", None),
          ("엔비디아 주식 10주 매수 주문 넣어줘", "delegate", 3), ("유튜브 숏폼 대본 초안 작성해줘", "delegate", 2),
          ("너 오늘 기분 어때", "chat", None), ("대표님 사랑해", "chat", None), ("결재 보여줘", "muse", None)]
    for q, want, tier in qa:
        r = parse_voice_command(q, persist=False, use_llm=False)
        good = r["intent"] == want and (tier is None or r.get("tier") == tier) and bool(r.get("speech"))
        if want == "chat": good = good and "payload" not in r
        chk(good, f"안총리 질문: {q} → {r['intent']}" + (f" T{r.get('tier')}" if r.get("tier") else ""))
    save()
    for r in ("rgon_voice_profile.json", "docs/rgon_voice_profile.json"):
        try:
            j = json.loads((ROOT / r).read_text(encoding="utf-8")); chk(j.get("version") == VERSION, f"JSON 무결성 {r}")
        except Exception as ex:
            chk(False, f"JSON 무결성 {r}: {ex!r}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1
# [RGON-R39-DIALOGUE-SFX] — 제15기관 올인원 대화 허브 공명 차임 효과음 확장 (Step 39)
try:
    if "SFX_PRESETS" in globals() and isinstance(SFX_PRESETS, dict):
        SFX_PRESETS.setdefault("dialogue_chime", {"freq": [587.33, 880.0, 1174.66], "dur": 0.20, "type": "sine", "desc": "대화 이해 공명 차임"})
        SFX_PRESETS.setdefault("memory_pin", {"freq": [659.25, 987.77], "dur": 0.16, "type": "triangle", "desc": "해마 원칙 각인 핀"})
except Exception:
    pass


# ==== [RGON-R40-SYNAPSE-VOICE-START] ====
# R40 시냅스 ⑩ — 통합 SFX 레지스트리 (SOUND_RECIPES는 절대 건드리지 않음)
try:
    SFX_PRESETS
except NameError:
    SFX_PRESETS = {}

_R40_SFX_DEFAULTS = {
    "dialogue_chime": {"notes": [784, 1046, 1318], "env": "chime", "dur": 0.45,
                       "desc": "대화 허브 차임", "r40": True},
    "insight_ping": {"notes": [1568, 2093], "env": "ping", "dur": 0.25,
                     "desc": "만물통찰안 핑", "r40": True},
    "dao_bell": {"notes": [392, 587, 784], "env": "bell", "dur": 1.2,
                 "desc": "주역도술관 종", "r40": True},
}
R40_UNIFIED_SFX_MAP = {k: SFX_PRESETS.get(k, v) for k, v in _R40_SFX_DEFAULTS.items()}
SFX_PRESETS.update(R40_UNIFIED_SFX_MAP)


def get_unified_sfx_registry():
    rec = globals().get("SOUND_RECIPES")
    return {"version": "v11.42-AON-OMNI-NEXUS", "antibody": "R1~R43",
            "sfx_presets": sorted(SFX_PRESETS.keys()),
            "sound_recipes": sorted(rec.keys()) if isinstance(rec, dict) else [],
            "r40_unified": sorted(R40_UNIFIED_SFX_MAP.keys())}
# ==== [RGON-R40-SYNAPSE-VOICE-END] ====


if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(self_test())
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        print(json.dumps(parse_voice_command(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2)); sys.exit(0)
    save(); print(json.dumps(state(), ensure_ascii=False)[:400]); sys.exit(0)


# [RGON-R36-BRAT-SFX] — 제12기관 게으름·찡찡·보채기·헤벌쭉 4종 감정 효과음 확장 (Step 36)
SFX_PRESETS.update({
    "lazy_yawn": {"desc": "게으름뱅이 하품 (나른한 하강 슬라이드)", "freq_hz": [520, 390, 280], "dur_ms": 260, "wave": "sine", "gain": 0.14},
    "whine_pout": {"desc": "하기 싫어 찡찡 투정 (뾰로통 워블 버즈)", "freq_hz": [460, 410, 470, 380], "dur_ms": 190, "wave": "triangle", "gain": 0.16},
    "clingy_boing": {"desc": "심심해 보채기 통통 점프 (2연속 스프링 보잉)", "freq_hz": [540, 820, 580, 920], "dur_ms": 180, "wave": "sine", "gain": 0.18},
    "spoiled_giggle": {"desc": "쓰담쓰담 헤벌쭉 꺄르르 아르페지오", "freq_hz": [587, 740, 880, 1175], "dur_ms": 220, "wave": "sine", "gain": 0.17},
})


# [RGON-R37-DAO-SFX] — 제13기관 주역 도술 싱잉볼 & 음양 분신술 효과음 확장 (Step 37)
SFX_PRESETS.update({
    "dao_bell": {"desc": "주역 도술 청아한 싱잉볼 화음", "freq_hz": [528, 792, 1056], "dur_ms": 280, "wave": "sine", "gain": 0.16},
    "yin_yang_clone": {"desc": "음양 미니 물방울 분신술 퐁퐁 화음", "freq_hz": [440, 660, 880, 1320], "dur_ms": 220, "wave": "sine", "gain": 0.17},
})


# [RGON-R38-INSIGHT-SFX] — 제14기관 만물 격물치지 영롱한 안광 효과음 확장 (Step 38)
SFX_PRESETS.update({
    "insight_flash": {"desc": "만물 이치를 꿰뚫는 크리스탈 혜안 화음", "freq_hz": [660, 990, 1320, 1760], "dur_ms": 250, "wave": "sine", "gain": 0.15},
})
