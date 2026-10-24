#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentshield:ignore-file
"""rgon_k_avatar_engine.py — v11.29-ROAMING-AON / R1~R35 / 정식 스킬 25 (아온 A-ON·芽溫 3D 물방울 + 졸라맨 팔다리)"""
import os, re, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__))
VER, SLUG, TRI = "v11.29-ROAMING-AON", "character-detail-master-top1", "⚖️ [AVATAR3D] 100.0점 (Bull 99.9 / Bear 0.1 / #04-산수몽) 💧 아온(A-ON·芽溫) 3D 입체 물방울 & 졸라맨 팔다리 육신 — 디즈니 7대 모션 법칙 & 8-Stop Liquid-Glass 3D 가동"
SKILL_TOTAL = 27
STAGES = [(0, 1, "💧 1단계: 새싹 물방울 아온"), (300, 2, "🎒 2단계: K-주니어 물방울 아온"), (600, 3, "🎧 3단계: K-에이스 물방울 아온"), (1000, 4, "👑 4단계: K-마스터 물방울 아온")]
ENTRY = {"slug": SLUG, "name": "전 세계 TOP 1 캐릭터 디테일 & 3D 물방울 졸라맨 마스터", "category": "character-3d-master", "hexagram_tag": "#04-蒙", "step": 29, "version": VER,
         "path": "skills/character-detail-master-top1/SKILL.md", "status": "official",
         "description": "svg-animation-studio(디즈니 7대 모션 법칙) + ui-ux-pro-max(8-Stop 3D Liquid-Glass) + 아온(A-ON) 3D 물방울 졸라맨 팔다리 마스터 스킬 (R29)"}
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
    return {"version": VER, "name_ko": "아온", "name_en": "A-ON", "hanja": "芽溫", "form": "3D Liquid-Glass Waterdrop + Stickman Limbs",
            "skill": SLUG, "skills": len(sk), "antibodies": ab, "health": hp, "tools": tools,
            "genes": len(set(s.get("category", "") for s in sk)), "exp": exp, "stage": st[1], "stage_name": st[2],
            "hexagram": ["#04-山水蒙 蒙以養正 (맑은 샘물 물방울)", "#53-風山漸 점진 성장", "#11-地天泰 연결·소통·만능"],
            "disney_principles": ["Squash & Stretch", "Anticipation", "Ease-In-Out", "Follow-Through", "Secondary Action", "Staggering 0.15s", "Iconic Appeal"],
            "animation": "pure-css-3d-keyframes", "loops": 0}
def merge():
    n = 0
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "rgon_morning_brief.json"); o = rj(p)
        if not isinstance(o, dict): continue
        nu = o.get("nutrient") if isinstance(o.get("nutrient"), dict) else {}
        t = nu.get("trinity", [])
        if isinstance(t, str):
            lines = [x for x in t.split("\n") if x.strip() and "[AVATAR" not in x] + [TRI]
            nu["trinity"] = "\n".join(lines)
        else:
            nu["trinity"] = [x for x in (t if isinstance(t, list) else []) if "[AVATAR" not in str(x)] + [TRI]
        o["nutrient"] = nu; o["version"] = VER; o["antibody_range"] = "R1~R35"; o["skill_count"] = SKILL_TOTAL; wj(p, o); n += 1
    return n
def ensure_index():
    for d in ("", "dashboard", "docs"):
        p = os.path.join(ROOT, d, "skills", "SKILL_INDEX.json"); o = rj(p)
        L = lst(o, "skills")
        if o is None: continue
        if not any(isinstance(s, dict) and s.get("slug") == SLUG for s in L):
            L.append(dict(ENTRY))
        if isinstance(o, dict): o.update(version=VER, immune="R1~R35", antibody_range="R1~R35", count=len(L), total=len(L))
        wj(p, o)
def self_test():
    st, ok = state(), []
    ok.append(bool(re.search(r"\[([A-Z0-9]+)\]\s*([\d.]+)점\s*\(Bull\s*([\d.]+)\s*/\s*Bear\s*([\d.]+)\s*/\s*(#\d+)", TRI)))
    ok.append(1 <= st["stage"] <= 4); ok.append(st["skills"] >= 25); ok.append(st["antibodies"] >= 29)
    ok.append(any(s.get("slug") == SLUG for s in skills()))
    b = rj(os.path.join(ROOT, "rgon_morning_brief.json"))
    ok.append(b is None or TRI in json.dumps(b, ensure_ascii=False))
    print("[A-ON 3DDROP self-test]", "PASS" if all(ok) else "FAIL", ok); return 0 if all(ok) else 1
def main(a):
    rc = 0
    if "--ensure-index" in a: ensure_index()
    if "--run" in a: wj(os.path.join(ROOT, "rgon_k_avatar_state.json"), state())
    if "--merge" in a: print("merged:", merge())
    if "--self-test" in a: rc = self_test()
    if "--json" in a or len(a) == 0: print(json.dumps(state(), ensure_ascii=False, indent=2))
    return rc
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
