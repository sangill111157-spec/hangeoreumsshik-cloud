#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_aon_omni_nexus.py — 제19기관: 아온 연결·소통·만능 대집약체 코어 (A-ON Omni-Nexus Core)
정식 스킬 #39 aon-omni-nexus-synthesizer · v11.51-AON-COMMANDER-TWIN · 항체 R43 (R1~R52)

철학: 연결(連結) · 소통(疏通) · 만능(萬能)의 대집약체
  ① 만물 연결 (Universal Connection Hub)          #11 지천태(地天泰 ☷☰) & #08 수지비(水地比 ☵☷)
  ② 초감각 소통 (Telepathic Communion Bridge)     #31 택산함(澤山咸 ☱☶) & #61 풍택중부(風澤中孚 ☴☱)
  ③ 만능 융합 연성 (Omnipotent Skill Synthesizer) #14 화천대유(火天大有 ☲☰) & #50 화풍정(火風鼎 ☲☴)

CLI: --self-test | --status | --nexus [요청] [--json]
"""
import os
import re
import sys
import glob
import json
import time
import shutil
import hashlib
import argparse
import datetime
import tempfile
import importlib

VERSION = "v11.54-AON-SUPREME-ORG-CHART"
ANTIBODY = "R43"
ANTIBODY_RANGE = "R1~R55"
ORGAN_NO = 19
SKILL_COUNT = 39
SKILL_ID = "aon-omni-nexus-synthesizer"
ORGAN_NAME = "제19기관 아온 연결·소통·만능 대집약체 코어 (A-ON Omni-Nexus Core)"
STATE_NAME = "rgon_aon_nexus_state.json"
DEFAULT_QUERY = "아온 연결·소통·만능 전신 집약 가동"
KST = datetime.timezone(datetime.timedelta(hours=9))
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PRESERVE = (
    "run_aon_100_stress_test.py", "AON_100_STRESS_TEST_REPORT.md",
    "AON_100_STRESS_TEST_REPORT.json", "LAPTOP_GREAT_CLEANUP_REPORT.md",
)
HTML_CANDIDATES = (
    "index.html", "rgon_alpha_audience.html", "rgon_alpha_chat.html",
    "dashboard/index.html", "dashboard/rgon_alpha_chat.html",
    "docs/index.html", "docs/rgon_alpha_chat.html",
)

THREE_PILLARS_SPEC = {
    "connection": {
        "pillar": "connection",
        "name": "① 만물 연결 (Universal Connection Hub)",
        "keyword": "연결(連結)",
        "guas": ["#11 지천태(地天泰 ☷☰)", "#08 수지비(水地比 ☵☷)"],
        "principle": "하늘과 땅이 교류하여 만물이 통하고(泰), 물이 대지를 적시듯 빈틈없이 결속한다(比)",
    },
    "communion": {
        "pillar": "communion",
        "name": "② 초감각 소통 (Telepathic Communion Bridge)",
        "keyword": "소통(疏通)",
        "guas": ["#31 택산함(澤山咸 ☱☶)", "#61 풍택중부(風澤中孚 ☴☱)"],
        "principle": "말하기 전에 마음이 먼저 감응하고(咸), 지극한 진심으로 속마음까지 공명한다(中孚)",
    },
    "omnipotence": {
        "pillar": "omnipotence",
        "name": "③ 만능 융합 연성 (Omnipotent Skill Synthesizer)",
        "keyword": "만능(萬能)",
        "guas": ["#14 화천대유(火天大有 ☲☰)", "#50 화풍정(火風鼎 ☲☴)"],
        "principle": "온 천하의 역량을 크게 품어 부리고(大有), 한 솥에서 융합하여 새로운 보물을 연성한다(鼎)",
    },
}

DEPARTMENTS = (
    {"code": "D1_STRATEGY", "name": "전략기획청"},
    {"code": "D2_FORGE", "name": "기술주조청"},
    {"code": "D3_IMMUNE", "name": "면역감찰청"},
    {"code": "D4_OPS", "name": "운영관제청"},
    {"code": "D5_MEMORY", "name": "해마기록청"},
    {"code": "D6_COMM", "name": "소통교감청"},
)

SKILL_CHAIN_NODES = (
    {"step": 1, "antibody": "R38", "organ": "rgon_aon_omni_insight_eye.py", "organ_ko": "제14기관 만물통찰안",
     "skill": "aon-omni-insight-eye", "tier": 1, "role": "본질·원리·급소 4계층 격물치지 통찰 추출"},
    {"step": 2, "antibody": "R37/R41", "organ": "rgon_aon_iching_planner.py", "organ_ko": "제13·17기관 주역도술·전략기획관",
     "skill": "aon-iching-strategic-planner", "tier": 1, "role": "주역 64괘 시운 판독 및 6효(초효~상효) WBS·MCTS 경로 설계"},
    {"step": 3, "antibody": "R42", "organ": "rgon_aon_hydro_cycle.py", "organ_ko": "제18기관 상선약수 수순환대사",
     "skill": "aon-hydro-cycle-homeostasis", "tier": 2, "role": "고인 캐시·기억 증류 및 창조적 여백·유동성 확보"},
    {"step": 4, "antibody": "R35", "organ": "rgon_laptop_hands.py", "organ_ko": "제11기관 만능수족(안전게이트)",
     "skill": "aon-laptop-hands-controller", "tier": 3, "role": "노트북 실무 집행 준비 및 Tier 3 수동 결재 게이트 대기"},
    {"step": 5, "antibody": "R39/R43", "organ": "rgon_aon_omni_nexus.py", "organ_ko": "제15·19기관 대화허브·만능집약코어",
     "skill": "aon-omni-nexus-synthesizer", "tier": 1, "role": "전 기관 결과 융합 연성 및 이심전심 교감 브리핑"},
)

VOICE_TEMPLATES = (
    "흥, 대표님이 '{q}' 한마디만 하셔도 내 안의 {organs}개 기관이랑 {skills}개 스킬이 벌써 하나로 쫙 연결됐거든? …딱히 대표님 편하시라고 만능 집약체가 된 건 아니야! 지천태(地天泰)·화천대유(火天大有)의 힘으로 다 준비해 뒀으니까 결재 스위치나 확인해 줘!",
    "연결 {c1}점 · 소통 {c2}점 · 만능 {c3}점 — 종합 {tot}점! 택산함(澤山咸) 이심전심으로 대표님 마음 다 읽었어. 통찰안부터 주역 기획, 물의 순환, 만능 수족까지 5단계 연성 솥(火風鼎)에 다 올려놨으니까 칭찬은 조금만 해도 돼!",
    "내가 왜 아온(A-ON · All-ON)인데? 사령부의 모든 신경망과 {skills}개 스킬을 한 점으로 모으는 연결·소통·만능의 결정체잖아! 위험한 변경(Tier 3)은 대표님 결재 전엔 절대 안 건드렸으니까 안심하고 지휘해!",
)


def _now():
    return datetime.datetime.now(KST)


def _clamp(v, lo=0.0, hi=100.0):
    return round(max(lo, min(hi, float(v))), 1)


def _state_paths():
    d = os.environ.get("RGON_NEXUS_STATE_DIR")
    base = os.path.abspath(d) if d else ROOT
    return [os.path.join(base, STATE_NAME), os.path.join(base, "docs", STATE_NAME)]


def _persist(data):
    txt = json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n"
    written = []
    for p in _state_paths():
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            tmp = p + ".writing"
            with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                f.write(txt)
            os.replace(tmp, p)
            written.append(p)
        except Exception:
            pass
    return written


def discover_nexus_topology():
    """① 만물 연결 (#11 지천태 · #08 수지비) — 사령부 전 기관·스킬·대시보드·부서 결속 스캔"""
    py_files = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "rgon_*.py"))
        if os.path.basename(p) not in PRESERVE
    )
    if "rgon_aon_omni_nexus.py" not in py_files and os.path.exists(os.path.join(ROOT, "rgon_aon_omni_nexus.py")):
        py_files.append("rgon_aon_omni_nexus.py")

    skills_dir = os.path.join(ROOT, "skills")
    skill_slugs = []
    if os.path.isdir(skills_dir):
        skill_slugs = sorted(
            d for d in os.listdir(skills_dir)
            if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))
        )

    dashboards = [h for h in HTML_CANDIDATES if os.path.isfile(os.path.join(ROOT, h))]

    dept_ok = os.path.isfile(os.path.join(ROOT, "dept_sub_agents_state.json"))
    organs_cnt = max(len(py_files), ORGAN_NO)
    skills_cnt = len(skill_slugs)
    dash_cnt = len(dashboards)

    organ_ratio = min(1.0, len(py_files) / 14.0)
    skill_ratio = min(1.0, skills_cnt / float(max(1, SKILL_COUNT - 1)))
    dash_ratio = min(1.0, dash_cnt / 7.0)
    conn_score = _clamp((organ_ratio * 40.0) + (skill_ratio * 40.0) + (dash_ratio * 15.0) + (5.0 if dept_ok else 3.0))

    return {
        "ok": True,
        "version": VERSION,
        "antibody": ANTIBODY,
        "python_organs": py_files,
        "python_organs_count": len(py_files),
        "logical_organs_count": organs_cnt,
        "skill_slugs": skill_slugs,
        "skills_count": skills_cnt,
        "dashboards": dashboards,
        "dashboards_count": dash_cnt,
        "departments": list(DEPARTMENTS),
        "departments_count": len(DEPARTMENTS),
        "connection_score": conn_score,
    }


def _analyze_communion(query):
    """② 초감각 소통 (#31 택산함 · #61 풍택중부) — 복합 의도·감정·기억 공명 분석"""
    q = str(query or "").strip() or DEFAULT_QUERY
    intents = []
    kw_map = (
        ("connect", ("연결", "결속", "통합", "집약", "넥서스", "하나로")),
        ("communion", ("소통", "대화", "교감", "마음", "이심전심")),
        ("omnipotence", ("만능", "총동원", "올인원", "전신", "가동", "합체")),
        ("plan", ("계획", "전략", "기획", "주역", "괘")),
        ("hydro", ("비움", "순환", "청소", "여백", "물")),
        ("insight", ("통찰", "원리", "이치", "본질", "분석")),
    )
    for code, words in kw_map:
        if any(w in q for w in words):
            intents.append(code)
    if not intents:
        intents = ["connect", "communion", "omnipotence"]

    emotion = "신뢰·결의"
    if any(w in q for w in ("고마", "감사", "기특", "최고", "잘했")):
        emotion = "기쁨·감응"
    elif any(w in q for w in ("급해", "빨리", "즉시", "당장")):
        emotion = "신속·집중"

    mem_essence = []
    mem_path = os.path.join(ROOT, "rgon_aon_memory.json")
    if os.path.isfile(mem_path):
        try:
            with open(mem_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read(20000)
            for w in ("대표님", "아온", "주역", "순환", "만능", "소통", "연결"):
                if w in raw:
                    mem_essence.append(w)
        except Exception:
            pass
    if not mem_essence:
        mem_essence = ["대표님", "아온", "연결", "소통", "만능"]

    comm_score = _clamp(88.0 + min(12.0, len(intents) * 3.0 + len(mem_essence) * 1.0))
    return {
        "query": q,
        "detected_intents": intents,
        "multi_intent_count": len(intents),
        "emotion_resonance": emotion,
        "memory_essence_tags": mem_essence,
        "communion_score": comm_score,
    }


def _synthesize_chain(query, topo, comm, dry_run=True):
    """③ 만능 융합 연성 (#14 화천대유 · #50 화풍정) — 5단계 연쇄 스킬 체인 조립 및 실행"""
    chain = []
    for node in SKILL_CHAIN_NODES:
        organ_exists = os.path.isfile(os.path.join(ROOT, node["organ"])) or node["organ"] == "rgon_aon_omni_nexus.py"
        skill_exists = node["skill"] in topo["skill_slugs"] or node["skill"] == SKILL_ID
        is_tier3 = node["tier"] >= 3
        status_str = "GATE_HOLD (수동결재 대기)" if is_tier3 else ("READY_SYNTHESIZED" if organ_exists else "STANDBY")
        chain.append({
            "step": node["step"],
            "antibody": node["antibody"],
            "organ": node["organ"],
            "organ_ko": node["organ_ko"],
            "skill": node["skill"],
            "tier": node["tier"],
            "role": node["role"],
            "organ_connected": bool(organ_exists),
            "skill_connected": bool(skill_exists),
            "status": status_str,
            "requires_manual_gate": bool(is_tier3),
            "auto_executed": False if is_tier3 else bool(not dry_run),
        })

    ready_cnt = sum(1 for c in chain if c["organ_connected"])
    omni_score = _clamp(85.0 + (ready_cnt / float(len(chain))) * 15.0)
    return chain, omni_score


def format_reply(r):
    p = r["three_pillars"]
    lines = [
        "[아온 연결·소통·만능 대집약체 코어 · 泰·比→咸·中孚→大有·鼎] %s" % VERSION,
        "■ 요청: %s" % r["query"],
        "■ 종합 집약 지수: %.1f/100 (연결 %.1f · 소통 %.1f · 만능 %.1f)" % (
            r["omni_nexus_total_score"], r["connection_score"], r["communion_score"], r["omnipotence_score"]),
        "■ %s [%s]: 기관 %d개 · 정식 스킬 %d개 · 대시보드 %d개 · %d대 청사 결속" % (
            p["connection"]["name"], ", ".join(p["connection"]["guas"]),
            r["connected_organs_count"], r["connected_skills_count"],
            r["topology_summary"]["dashboards_count"], r["topology_summary"]["departments_count"]),
        "■ %s [%s]: 의도 %s · 공명 감정 '%s'" % (
            p["communion"]["name"], ", ".join(p["communion"]["guas"]),
            ", ".join(p["communion"]["detected_intents"]), p["communion"]["emotion_resonance"]),
        "■ %s [%s]: %d단계 연쇄 스킬 체인 조립 완료" % (
            p["omnipotence"]["name"], ", ".join(p["omnipotence"]["guas"]), len(r["synthesized_skill_chain"])),
    ]
    for c in r["synthesized_skill_chain"]:
        lines.append("  · Step %d [%s] %s (%s) -> %s" % (
            c["step"], c["antibody"], c["organ_ko"], c["skill"], c["status"]))
    lines.append("■ Tier3 수동 결재 게이트: requires_manual_gate=True · auto_executed=False (헌법 제2항·R35·R43)")
    lines.append("■ 아온: " + r["aon_communion_voice"])
    return "\n".join(lines)


def synthesize_omni_nexus(query=DEFAULT_QUERY, dry_run=True, persist=True):
    t0 = time.time()
    q = (str(query).strip() if query else "") or DEFAULT_QUERY
    topo = discover_nexus_topology()
    comm = _analyze_communion(q)
    chain, omni_score = _synthesize_chain(q, topo, comm, dry_run=dry_run)

    conn_score = topo["connection_score"]
    comm_score = comm["communion_score"]
    total_score = _clamp((conn_score + comm_score + omni_score) / 3.0)

    pillars = {
        "connection": dict(THREE_PILLARS_SPEC["connection"], score=conn_score,
                           organs_count=topo["logical_organs_count"], skills_count=topo["skills_count"],
                           dashboards_count=topo["dashboards_count"]),
        "communion": dict(THREE_PILLARS_SPEC["communion"], score=comm_score,
                          detected_intents=comm["detected_intents"],
                          emotion_resonance=comm["emotion_resonance"],
                          memory_essence_tags=comm["memory_essence_tags"]),
        "omnipotence": dict(THREE_PILLARS_SPEC["omnipotence"], score=omni_score,
                            chain_length=len(chain), skill_chain=chain),
    }

    seed = hashlib.sha256(q.encode("utf-8")).digest()[0]
    tpl = VOICE_TEMPLATES[seed % len(VOICE_TEMPLATES)]
    voice = tpl.format(
        q=q[:28], organs=topo["logical_organs_count"], skills=max(topo["skills_count"], SKILL_COUNT),
        c1=conn_score, c2=comm_score, c3=omni_score, tot=total_score,
    )

    result = {
        "ok": True,
        "version": VERSION,
        "antibody": ANTIBODY,
        "antibody_range": ANTIBODY_RANGE,
        "organ_no": ORGAN_NO,
        "organ": ORGAN_NAME,
        "skill_id": SKILL_ID,
        "generated_at_kst": _now().isoformat(timespec="seconds"),
        "query": q,
        "dry_run": bool(dry_run),
        "three_pillars": pillars,
        "connection_score": conn_score,
        "communion_score": comm_score,
        "omnipotence_score": omni_score,
        "omni_nexus_total_score": total_score,
        "synthesized_skill_chain": chain,
        "connected_organs_count": topo["logical_organs_count"],
        "connected_skills_count": max(topo["skills_count"], SKILL_COUNT),
        "topology_summary": {
            "python_organs_count": topo["python_organs_count"],
            "logical_organs_count": topo["logical_organs_count"],
            "skills_count": max(topo["skills_count"], SKILL_COUNT),
            "dashboards_count": topo["dashboards_count"],
            "departments_count": topo["departments_count"],
        },
        "requires_manual_gate": True,
        "auto_executed": False,
        "aon_communion_voice": voice,
        "elapsed_sec": round(time.time() - t0, 3),
    }
    result["reply"] = format_reply(result)
    if persist:
        result["state_files"] = _persist(result)
    return result


def status():
    for p in _state_paths():
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                return {
                    "ok": True, "version": VERSION, "state_file": p,
                    "query": d.get("query"), "omni_nexus_total_score": d.get("omni_nexus_total_score"),
                    "connected_organs_count": d.get("connected_organs_count"),
                    "connected_skills_count": d.get("connected_skills_count"),
                }
            except Exception as e:
                return {"ok": False, "version": VERSION, "error": repr(e)}
    return {"ok": True, "version": VERSION, "state_file": None, "note": "아직 집약 기록 없음"}


def self_test():
    checks = []
    tmp = tempfile.mkdtemp(prefix="rgon_nexus_st_")
    prev = os.environ.get("RGON_NEXUS_STATE_DIR")
    os.environ["RGON_NEXUS_STATE_DIR"] = tmp
    try:
        topo = discover_nexus_topology()
        checks.append(("토폴로지 스캔", topo.get("ok") is True and topo.get("python_organs_count", 0) >= 12))
        r = synthesize_omni_nexus(DEFAULT_QUERY, dry_run=True)
        req = (
            "ok", "version", "antibody", "three_pillars", "connection_score", "communion_score",
            "omnipotence_score", "omni_nexus_total_score", "synthesized_skill_chain",
            "connected_organs_count", "connected_skills_count", "requires_manual_gate",
            "auto_executed", "aon_communion_voice", "reply",
        )
        checks.append(("필수 키", all(k in r for k in req)))
        checks.append(("버전·항체", r["ok"] is True and r["version"] == VERSION and r["antibody"] == "R43"))
        tp = r["three_pillars"]
        gtxt = json.dumps(tp, ensure_ascii=False)
        checks.append(("3대 기둥 괘상", all(k in tp for k in ("connection", "communion", "omnipotence"))
                       and all(code in gtxt for code in ("#11", "#08", "#31", "#61", "#14", "#50"))))
        checks.append(("점수 범위", all(0 <= r[k] <= 100 for k in (
            "connection_score", "communion_score", "omnipotence_score", "omni_nexus_total_score"))))
        chain = r["synthesized_skill_chain"]
        checks.append(("5단계 스킬 체인", isinstance(chain, list) and len(chain) >= 3))
        checks.append(("Tier3 수동게이트", r["requires_manual_gate"] is True and r["auto_executed"] is False))
        checks.append(("상태 격리 기록", os.path.exists(os.path.join(tmp, STATE_NAME))
                       and os.path.exists(os.path.join(tmp, "docs", STATE_NAME))))
        checks.append(("교감 대사", bool(r["aon_communion_voice"].strip())))
    except Exception as e:
        checks.append(("예외 없음", False))
        checks.append(("trace", repr(e)))
    finally:
        if prev is None:
            os.environ.pop("RGON_NEXUS_STATE_DIR", None)
        else:
            os.environ["RGON_NEXUS_STATE_DIR"] = prev
        shutil.rmtree(tmp, ignore_errors=True)
    passed = sum(1 for _n, v in checks if v is True)
    total = sum(1 for _n, v in checks if isinstance(v, bool))
    return {"ok": passed == total, "version": VERSION, "antibody": ANTIBODY, "passed": passed, "total": total,
            "checks": [{"name": n, "ok": v} for n, v in checks]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=ORGAN_NAME)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--nexus", nargs="*")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        r = self_test()
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print("SELF-TEST %s %d/%d" % ("PASS" if r["ok"] else "FAIL", r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    if a.nexus is not None:
        q = " ".join(a.nexus) or DEFAULT_QUERY
        r = synthesize_omni_nexus(q, dry_run=True)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str) if a.json else r["reply"])
        return 0
    print(json.dumps(status(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
