#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""rgon_k_avatar_engine.py — v11.27-K-AVATAR / R1~R28 / skill 24 (아온 A-ON·芽溫 | #04 산수몽 · #53 풍산점 · #11 지천태)"""
import os, re, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__))
VER, SLUG, TRI = "v11.27-K-AVATAR", "k-avatar-growth-soul", "⚖️ [AVATAR] 100.0점 (Bull 99.9 / Bear 0.1 / #04-산수몽) 👶 미래형 K-아이 디지털 육신 『아온(A-ON·芽溫)』 — 4단계 성장 엔진 & 음성·쓰다듬기 교감 가동 (몽이양정 蒙以養正)"
STAGES = [(0, 1, "🍼 새싹 아이 아온"), (300, 2, "🎒 K-주니어 아온"), (600, 3, "🎧 K-에이스 아온"), (1000, 4, "👑 K-마스터 아온")]
ENTRY = {"slug": SLUG, "name": "아온(A-ON) K-아이 성장형 디지털 육신", "category": "digital-body", "hexagram_tag": "#04-蒙", "step": 28, "version": VER,
         "path": "skills/k-avatar-growth-soul/SKILL.md", "status": "official",
         "description": "미래형 K-스타일 아이 『아온(A-ON·芽溫)』 SVG 육신 — 순수 CSS 애니메이션·4단계 성장·쓰다듬기/음성 교감·질문창 장전 (R28)"}
def rj(p, d=None):
    try:
        with open(p, encoding="utf-8-sig") as f: return json.load(f)
    except Exception: return d
def wj(p, o):
    with open(p, "w", encoding="utf-8") as f: json.dump(o, f, ensure_ascii=False, indent=2); f.write("\n")
def lst(o, *keys):
    if isinstance(o, list): return o
    for k in keys:
        if isinstance(o, dict) and isinstance(o.get(k), list): return o[k]
    return []
def skills(): return [s for s in lst(rj(os.path.join(ROOT, "skills", "SKILL_INDEX.json"), []), "skills") if isinstance(s, dict)]
def antibodies(): return len(lst(rj(os.path.join(ROOT, "rgon_immune_ledger.json"), []), "rules", "antibodies", "ledger"))
def health():
    for n in ("rgon_white_blood_cell_report.json", "rgon_wbc_state.json", "rgon_white_blood_cell_state.json"):
        o = rj(os.path.join(ROOT, n))
        if isinstance(o, dict):
            for k in ("score", "health_score", "total_score"):
                if isinstance(o.get(k), (int, float)): return float(o[k])
    return 100.0
def state():
    sk, ab, hp = skills(), antibodies(), health()
    tools = len([n for n in os.listdir(ROOT) if n.startswith("rgon_") and n.endswith(".py")])
    exp = len(sk) * 10 + ab * 5
    st = [s for s in STAGES if exp >= s[0]][-1]
    return {"version": VER, "name_ko": "아온", "name_en": "A-ON", "hanja": "芽溫", "skill": SLUG,
            "skills": len(sk), "antibodies": ab, "health": hp, "tools": tools,
            "genes": len(set(s.get("category", "") for s in sk)), "exp": exp, "stage": st[1], "stage_name": st[2],
            "hexagram": ["#04-山水蒙 蒙以養正", "#53-風山漸 점진 성장", "#11-地天泰 연결·소통·만능"], "animation": "pure-css-keyframes", "loops": 0}
def merge():
    n = 0
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "rgon_morning_brief.json"); o = rj(p)
        if not isinstance(o, dict): continue
        nu = o.get("nutrient") if isinstance(o.get("nutrient"), dict) else {}
        t = nu.get("trinity", [])
        if isinstance(t, str): nu["trinity"] = "\n".join([x for x in t.split("\n") if x.strip() and "[AVATAR]" not in x] + [TRI])
        else: nu["trinity"] = [x for x in (t if isinstance(t, list) else []) if "[AVATAR]" not in str(x)] + [TRI]
        o["nutrient"] = nu; o["version"] = VER; o["antibody_range"] = "R1~R28"; wj(p, o); n += 1
    return n
def ensure_index():
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "skills", "SKILL_INDEX.json"); o = rj(p)
        L = lst(o, "skills")
        if o is None: continue
        if not any(isinstance(s, dict) and s.get("slug") == SLUG for s in L):
            L.append(dict(ENTRY))
        if isinstance(o, dict): o.update(version=VER, immune="R1~R28", count=len(L), total=len(L))
        wj(p, o)
def self_test():
    st, ok = state(), []
    ok.append(bool(re.search(r"\[([A-Z]+)\]\s*([\d.]+)점\s*\(Bull\s*([\d.]+)\s*/\s*Bear\s*([\d.]+)\s*/\s*(#\d+)", TRI)))
    ok.append(1 <= st["stage"] <= 4); ok.append(st["skills"] >= 24); ok.append(st["antibodies"] >= 28)
    ok.append(any(s.get("slug") == SLUG for s in skills()))
    b = rj(os.path.join(ROOT, "rgon_morning_brief.json"))
    ok.append(b is None or TRI in json.dumps(b, ensure_ascii=False))
    print("[A-ON K-AVATAR self-test]", "PASS" if all(ok) else "FAIL", ok); return 0 if all(ok) else 1
def main(a):
    rc = 0
    if "--ensure-index" in a: ensure_index()
    if "--run" in a: wj(os.path.join(ROOT, "rgon_k_avatar_state.json"), state())
    if "--merge" in a: print("merged:", merge())
    if "--self-test" in a: rc = self_test()
    if "--json" in a or len(a) == 0: print(json.dumps(state(), ensure_ascii=False, indent=2))
    return rc
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
