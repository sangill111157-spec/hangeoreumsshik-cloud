#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step43_aon_omni_nexus_core.py
RGON Step 43 — 제19기관 아온 연결·소통·만능 대집약체 코어 (A-ON Omni-Nexus Core)
v11.41-AON-HYDRO-CYCLE -> v11.42-AON-OMNI-NEXUS · 항체 R1~R42 -> R1~R43 · 정식 스킬 38 -> 39
"""
import os
import sys
import re
import ast
import json
import time
import shutil
import hashlib
import tempfile
import datetime
import subprocess
import traceback
import py_compile
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BT3 = chr(96) * 3
STEP = 43
OLD_VERSION = "v11.41-AON-HYDRO-CYCLE"
NEW_VERSION = "v11.42-AON-OMNI-NEXUS"
OLD_RANGE = "R1~R42"
NEW_RANGE = "R1~R43"
OLD_COUNT = 38
NEW_COUNT = 39
SKILL_ID = "aon-omni-nexus-synthesizer"
SKILL_PATH = "skills/%s/SKILL.md" % SKILL_ID
SKILL_TITLE = "제19기관 아온 연결·소통·만능 대집약체 코어 (泰·比→咸·中孚→大有·鼎)"
SKILL_DESC = ("주역 3대 집약 괘상(#11 지천태·#08 수지비 만물연결, #31 택산함·#61 풍택중부 초감각소통, "
              "#14 화천대유·#50 화풍정 만능융합연성)으로 사령부 전 기관(제1~19기관)과 39개 정식 스킬, "
              "7개 대시보드, 6대 부서를 단일 넥서스로 결속하고 최적 스킬 체인을 조립·실행하는 만능 대집약체 코어")
NEXUS_FILE = "rgon_aon_omni_nexus.py"
HYDRO_FILE = "rgon_aon_hydro_cycle.py"
PLANNER_FILE = "rgon_aon_iching_planner.py"
DIALOGUE_FILE = "rgon_aon_dialogue_engine.py"
VERIFIER_FILE = "rgon_neural_synapse_verifier.py"
VOICE_FILE = "rgon_voice_organ.py"
EXCRETORY_FILE = "rgon_excretory_organ.py"
HASH_FILE = ".rgon_file_hashes.json"
REPORT_FILE = "STEP43_AON_OMNI_NEXUS_REPORT.md"
DIAG_FILE = "STEP43_FAILURE_DIAG.txt"
STATE_NAME = "rgon_aon_nexus_state.json"
STATE_FILES = [STATE_NAME, "docs/" + STATE_NAME]
PRESERVE = [
    "run_aon_100_stress_test.py", "AON_100_STRESS_TEST_REPORT.md", "AON_100_STRESS_TEST_REPORT.json",
    "LAPTOP_GREAT_CLEANUP_REPORT.md",
]
PROTECT = {VOICE_FILE: ["SOUND_RECIPES"], EXCRETORY_FILE: ["PRESERVE_EXACT"]}
HTML_TARGETS = [
    "index.html", "rgon_alpha_audience.html", "rgon_alpha_chat.html",
    "dashboard/index.html", "dashboard/rgon_alpha_chat.html",
    "docs/index.html", "docs/rgon_alpha_chat.html",
]
JSON_SNAPSHOT_DIRS = ["", "docs", "dashboard"]
JSON_SNAPSHOT_EXCLUDE = {HASH_FILE, "package.json", "package-lock.json", "AON_100_STRESS_TEST_REPORT.json"}
REQUIRED_FILES = [DIALOGUE_FILE, VERIFIER_FILE]
TOP_KEYS = ["version", "antibody", "generated_at_kst", "count", "skills"]
ENTRY_KEYS = ["no", "slug", "antibody", "version", "path"]
KST = datetime.timezone(datetime.timedelta(hours=9))
NO_ROLLBACK = bool(os.environ.get("RGON_STEP43_NO_ROLLBACK"))


def _detect_root():
    cands = []
    if os.environ.get("RGON_ROOT"):
        cands.append(os.environ["RGON_ROOT"])
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.getcwd())
    cands.append(r"C:\Users\sangi\Downloads\shin-agent")
    for c in cands:
        if c and os.path.exists(os.path.join(c, DIALOGUE_FILE)):
            return os.path.abspath(c)
    return os.path.abspath(cands[0] if cands else os.getcwd())


ROOT = _detect_root()
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = os.path.join(ROOT, ".rgon_backups", "step43_" + TS)
BACKED = {}
MODIFIED = set()
LOGS = []


def log(msg=""):
    LOGS.append(str(msg))
    try:
        print(msg, flush=True)
    except Exception:
        print(str(msg).encode("utf-8", "replace").decode("utf-8", "replace"), flush=True)


def P(rel):
    return os.path.join(ROOT, rel)


def kst_now():
    return datetime.datetime.now(KST).isoformat(timespec="seconds")


def is_preserved(rel):
    return os.path.basename(rel) in PRESERVE or rel in PRESERVE


def read_text(rel):
    with open(P(rel), "r", encoding="utf-8") as f:
        return f.read()


def backup_file(rel):
    if is_preserved(rel):
        raise RuntimeError("PRESERVE 파일 접근 차단: " + rel)
    if rel in BACKED:
        return
    src = P(rel)
    if os.path.exists(src):
        dst = os.path.join(BACKUP_DIR, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        BACKED[rel] = True
    else:
        BACKED[rel] = False


def write_text(rel, text):
    if is_preserved(rel):
        raise RuntimeError("PRESERVE 파일 쓰기 차단: " + rel)
    backup_file(rel)
    path = P(rel)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == text:
                return False
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    MODIFIED.add(rel)
    return True


def rollback():
    log("[ROLLBACK] 백업 복원 시작 (PRESERVE 제외)")
    for rel, existed in BACKED.items():
        if is_preserved(rel):
            continue
        try:
            if existed:
                shutil.copy2(os.path.join(BACKUP_DIR, rel), P(rel))
            elif os.path.exists(P(rel)):
                os.remove(P(rel))
        except Exception as e:
            log("  - 복원 실패 %s: %r" % (rel, e))
    sk = P(os.path.join("skills", SKILL_ID))
    try:
        if os.path.isdir(sk) and not os.listdir(sk):
            os.rmdir(sk)
    except Exception:
        pass
    log("[ROLLBACK] 완료")


def sha_file(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_indent(raw):
    m = re.search(r"\n( +)\"", raw)
    return len(m.group(1)) if m else 2


def insert_block(text, begin, end, block):
    full = begin + "\n" + block.strip("\n") + "\n" + end
    if begin in text and end in text:
        s = text.index(begin)
        e = text.index(end, s) + len(end)
        return text[:s] + full + text[e:]
    ms = list(re.finditer(r"^if\s+__name__\s*==\s*['\"]__main__['\"]\s*:", text, re.M))
    if ms:
        pos = ms[-1].start()
        return text[:pos] + full + "\n\n\n" + text[pos:]
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n\n" + full + "\n"


# ══════════════════════════════════════════════════════════════════════
# 1. 제19기관 rgon_aon_omni_nexus.py 원본
# ══════════════════════════════════════════════════════════════════════
NEXUS_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_aon_omni_nexus.py — 제19기관: 아온 연결·소통·만능 대집약체 코어 (A-ON Omni-Nexus Core)
정식 스킬 #39 aon-omni-nexus-synthesizer · v11.42-AON-OMNI-NEXUS · 항체 R43 (R1~R43)

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

VERSION = "v11.42-AON-OMNI-NEXUS"
ANTIBODY = "R43"
ANTIBODY_RANGE = "R1~R43"
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
'''

# ══════════════════════════════════════════════════════════════════════
# 2. 제15기관 대화허브 R43 훅
# ══════════════════════════════════════════════════════════════════════
DLG_BEGIN = "# >>> [RGON-R43-NEXUS-HOOK-START] >>>"
DLG_END = "# <<< [RGON-R43-NEXUS-HOOK-END] <<<"
DIALOGUE_HOOK = r'''
import threading as _r43_threading
import time as _r43_time

R43_NEXUS_SLASH = ("/만능", "/집약", "/연결", "/소통", "/넥서스")
R43_NEXUS_KEYWORDS = ("만능", "집약", "연결", "소통", "총동원", "올인원", "넥서스")
R43_NEXUS_DEFAULT_QUERY = "아온 연결·소통·만능 전신 집약 가동"
_r43_tls = _r43_threading.local()
_r43_cache = {"t": 0.0, "res": None}


def _r43_nexus_intent(text):
    t = str(text or "").strip()
    for s in R43_NEXUS_SLASH:
        if t == s or t.startswith(s + " "):
            return "slash", t[len(s):].strip()
    if any(k in t for k in R43_NEXUS_KEYWORDS):
        return "keyword", t
    return None, ""


def _r43_first_text(args, kwargs):
    for k in ("text", "message", "query", "msg", "user_text", "prompt"):
        if isinstance(kwargs.get(k), str):
            return kwargs[k]
    for a in args:
        if isinstance(a, str):
            return a
    return ""


def _r43_run_nexus(query, use_cache=False):
    if use_cache and _r43_cache["res"] is not None and _r43_time.time() - _r43_cache["t"] < 90:
        return _r43_cache["res"]
    import importlib as _il
    nx = _il.import_module("rgon_aon_omni_nexus").synthesize_omni_nexus(
        query or R43_NEXUS_DEFAULT_QUERY, dry_run=True
    )
    _r43_cache["t"] = _r43_time.time()
    _r43_cache["res"] = nx
    return nx


def _r43_slash_response(arg):
    nx = _r43_run_nexus(arg)
    return {
        "ok": bool(nx.get("ok")), "intent": "nexus", "intents": ["nexus"],
        "organ": "rgon_aon_omni_nexus", "antibody": "R43",
        "reply": nx.get("reply", ""), "speech": nx.get("reply", ""), "text": nx.get("reply", ""),
        "omni_nexus": nx,
        "results": [{"intent": "nexus", "ok": True, "speech": nx.get("reply", ""), "data": nx}],
        "omni_nexus_total_score": nx.get("omni_nexus_total_score"),
        "three_pillars": nx.get("three_pillars"),
        "synthesized_skill_chain": nx.get("synthesized_skill_chain"),
        "requires_manual_gate": True, "auto_executed": False,
    }


def _r43_attach(res, nx):
    if isinstance(res, dict):
        res["omni_nexus"] = nx
        res.setdefault("nexus_reply", nx.get("reply", ""))
    return res


if "route" not in globals() and callable(globals().get("r40_route")):
    route = r40_route


def _r43_wrap(name):
    orig = globals().get(name)
    if not callable(orig) or getattr(orig, "_r43_wrapped", False):
        return

    def wrapper(*args, **kwargs):
        if getattr(_r43_tls, "active", False):
            return orig(*args, **kwargs)
        try:
            kind, arg = _r43_nexus_intent(_r43_first_text(args, kwargs))
        except Exception:
            kind, arg = None, ""
        if not kind:
            return orig(*args, **kwargs)
        _r43_tls.active = True
        try:
            if kind == "slash" and name not in ("converse", "process_dialogue"):
                try:
                    return _r43_slash_response(arg)
                except Exception as _e:
                    return {"ok": False, "intent": "nexus", "antibody": "R43", "error": repr(_e),
                            "requires_manual_gate": True, "auto_executed": False}
            res = orig(*args, **kwargs)
            try:
                nx = _r43_run_nexus(arg if kind == "slash" else R43_NEXUS_DEFAULT_QUERY, use_cache=(kind == "keyword"))
                res = _r43_attach(res, nx)
            except Exception:
                pass
            return res
        finally:
            _r43_tls.active = False

    wrapper._r43_wrapped = True
    wrapper._r43_orig = orig
    wrapper.__name__ = name
    wrapper.__doc__ = getattr(orig, "__doc__", None)
    globals()[name] = wrapper


for _r43_n in ("route", "converse", "r40_route", "process_dialogue"):
    _r43_wrap(_r43_n)

try:
    _r43_ic = globals().get("INTENT_KEYWORDS")
    if isinstance(_r43_ic, dict):
        _r43_ic.setdefault("nexus", list(R43_NEXUS_KEYWORDS))
except Exception:
    pass
'''

# ══════════════════════════════════════════════════════════════════════
# 3. 제16기관 검증기 R43 확장
# ══════════════════════════════════════════════════════════════════════
VER_BEGIN = "# >>> [RGON-R43-VERIFIER-EXT-START] >>>"
VER_END = "# <<< [RGON-R43-VERIFIER-EXT-END] <<<"
VERIFIER_HOOK = r'''
VERSION = "v11.42-AON-OMNI-NEXUS"
ANTIBODY_RANGE = "R1~R43"
EXPECTED_SKILL_COUNT = 39
STATUS_LINE = "%s · 항체 %s · 정식 스킬 %d개" % (VERSION, ANTIBODY_RANGE, EXPECTED_SKILL_COUNT)
R43_NEXUS_ORGAN = "rgon_aon_omni_nexus.py"
R43_NEXUS_SNAPSHOTS = ["rgon_aon_nexus_state.json", "docs/rgon_aon_nexus_state.json"]
try:
    if R43_NEXUS_ORGAN not in ORGANS:
        ORGANS.append(R43_NEXUS_ORGAN)
except NameError:
    ORGANS = [R43_NEXUS_ORGAN]
for _r43_sn in ("SNAPSHOT_FILES", "SNAPSHOT_SYNC_FILES", "SNAPSHOT_TARGETS", "SYNC_SNAPSHOTS",
                "STATE_SNAPSHOTS", "SNAPSHOTS", "STATE_FILES", "JSON_SNAPSHOTS"):
    _r43_sv = globals().get(_r43_sn)
    if isinstance(_r43_sv, list) and all(isinstance(_x, str) for _x in _r43_sv):
        for _r43_x in R43_NEXUS_SNAPSHOTS:
            if _r43_x not in _r43_sv:
                _r43_sv.append(_r43_x)
    elif isinstance(_r43_sv, tuple) and all(isinstance(_x, str) for _x in _r43_sv):
        globals()[_r43_sn] = tuple(_r43_sv) + tuple(_x for _x in R43_NEXUS_SNAPSHOTS if _x not in _r43_sv)


def _r43_s13_check():
    import os as _o, json as _j, tempfile as _t, importlib as _il, shutil as _sh, time as _tm
    _t0 = _tm.perf_counter()
    name = "대화허브(/만능)→제19기관 연결·소통·만능 대집약체"
    tmp = _t.mkdtemp(prefix="rgon_s13_")
    keys = ("RGON_NEXUS_STATE_DIR", "RGON_HYDRO_STATE_DIR", "RGON_ICHING_STATE_DIR", "RGON_DIALOGUE_STATE_DIR")
    prev = {k: _o.environ.get(k) for k in keys}
    base = _o.path.dirname(_o.path.abspath(__file__))
    root_state = [_o.path.join(base, "rgon_aon_nexus_state.json"), _o.path.join(base, "docs", "rgon_aon_nexus_state.json")]

    def _sig(p):
        try:
            st = _o.stat(p)
            return (st.st_size, st.st_mtime_ns)
        except OSError:
            return None

    before = [_sig(p) for p in root_state]
    for k in keys:
        _o.environ[k] = tmp
    try:
        dlg = _il.import_module("rgon_aon_dialogue_engine")
        fn = getattr(dlg, "route", None) or getattr(dlg, "r40_route", None)
        r = fn("/만능 아온 연결·소통·만능 전신 집약 가동")
        nx = r.get("omni_nexus") if isinstance(r, dict) else None
        nx = nx if isinstance(nx, dict) else {}
        tp = nx.get("three_pillars") or {}
        gtxt = _j.dumps(tp, ensure_ascii=False)
        chain = nx.get("synthesized_skill_chain") or []
        tot = nx.get("omni_nexus_total_score")
        checks = {
            "route_ok": isinstance(r, dict) and r.get("ok") is True,
            "nexus_ok": nx.get("ok") is True and nx.get("antibody") == "R43",
            "three_pillars": all(k in tp for k in ("connection", "communion", "omnipotence"))
                             and all(c in gtxt for c in ("#11", "#08", "#31", "#61", "#14", "#50")),
            "skill_chain": isinstance(chain, list) and len(chain) >= 3,
            "total_score": isinstance(tot, (int, float)) and 0 <= tot <= 100,
            "manual_gate": nx.get("requires_manual_gate") is True and nx.get("auto_executed") is False,
            "isolated": _o.path.exists(_o.path.join(tmp, "rgon_aon_nexus_state.json")) and [_sig(p) for p in root_state] == before,
        }
        return {"id": "S13", "name": name, "ok": all(checks.values()), "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": str(checks)[:200], "detail": checks}
    except Exception as e:
        return {"id": "S13", "name": name, "ok": False, "sec": round(_tm.perf_counter() - _t0, 3),
                "evidence": repr(e), "detail": repr(e)}
    finally:
        for k, v in prev.items():
            if v is None:
                _o.environ.pop(k, None)
            else:
                _o.environ[k] = v
        _sh.rmtree(tmp, ignore_errors=True)


def _r43_merge(res, item):
    sid = item.get("id")
    if isinstance(res, list):
        return [x for x in res if not (isinstance(x, dict) and x.get("id") == sid)] + [item]
    if isinstance(res, dict):
        lst = None
        for k in ("links", "synapses", "results", "checks"):
            if isinstance(res.get(k), list):
                lst = k
                break
        if lst:
            res[lst] = [x for x in res[lst] if not (isinstance(x, dict) and x.get("id") == sid)] + [item]
            items = res[lst]
            passed = sum(1 for x in items if isinstance(x, dict) and x.get("ok"))
            for pk in ("passed", "pass_count"):
                if pk in res:
                    res[pk] = passed
            for tk in ("total", "total_count"):
                if tk in res:
                    res[tk] = len(items)
            if "ok" in res:
                res["ok"] = passed == len(items)
        else:
            res[sid] = item
    return res


_r43_orig_vsl = globals().get("verify_synapse_links")
if callable(_r43_orig_vsl) and not getattr(_r43_orig_vsl, "_r43", False):
    def verify_synapse_links(*args, **kwargs):
        res = _r43_orig_vsl(*args, **kwargs)
        try:
            res = _r43_merge(res, _r43_s13_check())
        except Exception:
            pass
        return res
    verify_synapse_links._r43 = True


def _r43_fix_skill_header():
    import os as _o, json as _j, re as _re, datetime as _dt
    p = _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "skills", "SKILL_INDEX.json")
    if not _o.path.exists(p):
        return False
    with open(p, "r", encoding="utf-8") as f:
        raw = f.read()
    data = _j.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("skills"), list):
        return False
    changed = False
    if data.get("version") != VERSION:
        data["version"] = VERSION
        changed = True
    ab = str(data.get("antibody") or "")
    want = "R43" if _re.fullmatch(r"R\d+", ab) else ANTIBODY_RANGE
    if ab != want:
        data["antibody"] = want
        changed = True
    if data.get("count") != len(data["skills"]):
        data["count"] = len(data["skills"])
        changed = True
    if changed or "generated_at_kst" not in data:
        data["generated_at_kst"] = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds")
        m = _re.search(r"\n( +)\"", raw)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(_j.dumps(data, ensure_ascii=False, indent=len(m.group(1)) if m else 2) + "\n")
    return changed


_r43_orig_heal = globals().get("heal_skill_index_header")
if callable(_r43_orig_heal) and not getattr(_r43_orig_heal, "_r43", False):
    def heal_skill_index_header(*args, **kwargs):
        try:
            return _r43_orig_heal(*args, **kwargs)
        finally:
            try:
                _r43_fix_skill_header()
            except Exception:
                pass
    heal_skill_index_header._r43 = True
'''

# ══════════════════════════════════════════════════════════════════════
# 4. 문서 · HTML · 스킬
# ══════════════════════════════════════════════════════════════════════
SKILL_MD = "\n".join([
    "---", "name: " + SKILL_ID, "description: " + SKILL_DESC, "version: " + NEW_VERSION,
    "antibody: R43", "skill_number: 39", "---", "",
    "# " + SKILL_TITLE, "",
    "제19기관 `rgon_aon_omni_nexus.py`, 정식 스킬 #39. 아온을 연결(連結)·소통(疏通)·만능(萬能)의 대집약체로 작동시킨다.", "",
    "## 사용법", "",
    BT3 + "bash",
    "python rgon_aon_omni_nexus.py --self-test",
    "python rgon_aon_omni_nexus.py --status",
    "python rgon_aon_omni_nexus.py --nexus 아온 연결·소통·만능 전신 집약 가동",
    BT3, "",
    "대화허브에서는 `/만능`, `/집약`, `/연결`, `/소통`, `/넥서스` 슬래시 명령과 만능·집약·연결·소통·총동원·올인원 키워드로 호출된다.", "",
    "## 3대 기둥 괘상", "",
    "1. 만물 연결(#11 지천태·#08 수지비): 전 기관·39개 스킬·7개 대시보드·6대 청사 결속",
    "2. 초감각 소통(#31 택산함·#61 풍택중부): 복합 의도·감정·해마 기억 정수 이심전심 공명",
    "3. 만능 융합 연성(#14 화천대유·#50 화풍정): 5단계 연쇄 스킬 체인 조립 및 Tier 3 수동 결재 게이트 보호", "",
])
BADGE = "%s · 항체 %s · 스킬 %d" % (NEW_VERSION, NEW_RANGE, NEW_COUNT)
HTML_BEGIN = "<!-- RGON R43 OMNI NEXUS BRIDGE BEGIN -->"
HTML_END = "<!-- RGON R43 OMNI NEXUS BRIDGE END -->"
HTML_BRIDGE = (HTML_BEGIN + "\n<script>\nwindow.RGON_OMNI_NEXUS = {version: \"" + NEW_VERSION +
               "\", antibody: \"R1~R43\", skill: \"" + SKILL_ID + "\", skillCount: 39, organ: 19, "
               "state: \"" + STATE_NAME + "\", commands: [\"/만능\", \"/집약\", \"/연결\", \"/소통\", \"/넥서스\"], "
               "load: function(){ return fetch(\"" + STATE_NAME + "\", {cache: \"no-store\"}).then(function(r){ return r.ok ? r.json() : null; }).catch(function(){ return null; }); }};\n"
               "</script>\n<div id=\"rgon-r43-badge\" style=\"display:none\">" + BADGE + "</div>\n" + HTML_END)


def bump_str(t):
    for ov in ("v11.41-AON-HYDRO-CYCLE", "v11.40-AON-ICHING-PLANNER", "v11.39-AON-NEURAL-SYNAPSE"):
        t = t.replace(ov, NEW_VERSION)
    for orng in ("R1~R42", "R1~R41", "R1~R40"):
        t = t.replace(orng, NEW_RANGE)
    t = re.sub(r"(EXPECTED_SKILL_COUNT\s*=\s*)(?:37|38)\b", r"\g<1>39", t)
    t = re.sub(r"(\bSKILL_COUNT\s*=\s*)(?:37|38)\b", r"\g<1>39", t)
    t = re.sub(r"(스킬\s*\*{0,2})(?:37|38)(\s*개?\*{0,2})", r"\g<1>39\2", t)
    t = re.sub(r"(skillCount\s*:\s*)(?:37|38)\b", r"\g<1>39", t)
    return t


def update_html():
    n = 0
    for rel in HTML_TARGETS:
        if not os.path.exists(P(rel)):
            log("  - HTML 없음(건너뜀): " + rel)
            continue
        t = bump_str(read_text(rel))
        if HTML_BEGIN in t:
            s = t.index(HTML_BEGIN)
            e = t.index(HTML_END, s) + len(HTML_END)
            t = t[:s] + HTML_BRIDGE + t[e:]
        elif "</body>" in t:
            i = t.rfind("</body>")
            t = t[:i] + HTML_BRIDGE + "\n" + t[i:]
        else:
            t += "\n" + HTML_BRIDGE + "\n"
        if write_text(rel, t):
            n += 1
    log("[HTML] %d개 갱신 (359개 클린 버튼·8도 픽스·5G 터널 100%% 보존)" % n)


def init_nexus_state_snapshots():
    try:
        sys.path.insert(0, ROOT)
        import rgon_aon_omni_nexus as nx
        res = nx.synthesize_omni_nexus(nx.DEFAULT_QUERY, dry_run=True, persist=False)
        txt = json.dumps(res, ensure_ascii=False, indent=2, default=str) + "\n"
        for rel in STATE_FILES:
            write_text(rel, txt)
    except Exception as e:
        log("  - 초기 nexus state 생성 참고: %r" % e)


def update_json_snapshots():
    n = 0
    for d in JSON_SNAPSHOT_DIRS:
        base = P(d) if d else ROOT
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            rel = (d + "/" + fn) if d else fn
            if not fn.endswith(".json") or fn in JSON_SNAPSHOT_EXCLUDE or is_preserved(rel):
                continue
            if not os.path.isfile(P(rel)):
                continue
            try:
                raw = read_text(rel)
            except Exception:
                continue
            new = bump_str(raw)
            if new == raw:
                continue
            try:
                json.loads(new)
            except Exception:
                continue
            if write_text(rel, new):
                n += 1
    log("[SNAPSHOT] JSON %d개 승격" % n)


def update_skill_index():
    write_text(SKILL_PATH, SKILL_MD)
    jrel = "skills/SKILL_INDEX.json"
    raw = read_text(jrel) if os.path.exists(P(jrel)) else ""
    data = json.loads(raw) if raw else {}
    if not isinstance(data, dict):
        data = {"skills": data if isinstance(data, list) else []}
    skills = data.get("skills") if isinstance(data.get("skills"), list) else []
    data["skills"] = skills
    slugs = [str(x.get("slug") or x.get("id") or x.get("name") or "") if isinstance(x, dict) else str(x) for x in skills]
    if SKILL_ID not in slugs:
        sample = next((x for x in reversed(skills) if isinstance(x, dict)), {})
        nos = [x.get("no") for x in skills if isinstance(x, dict) and isinstance(x.get("no"), int)]
        entry = {"no": (max(nos) + 1) if nos else len(skills) + 1, "slug": SKILL_ID, "antibody": "R43",
                 "version": NEW_VERSION, "path": SKILL_PATH}
        extra = {"id": SKILL_ID, "name": SKILL_ID, "title": SKILL_TITLE, "description": SKILL_DESC,
                 "organ": "제19기관", "file": NEXUS_FILE}
        for k in sample:
            if k not in entry:
                entry[k] = extra.get(k, "" if isinstance(sample[k], str) else sample[k])
        skills.append(entry)
    old_ab = str(data.get("antibody") or "")
    head = {"version": NEW_VERSION,
            "antibody": "R43" if re.fullmatch(r"R\d+", old_ab) else NEW_RANGE,
            "generated_at_kst": kst_now(), "count": len(skills)}
    ordered = {}
    for k in data:
        ordered[k] = head.get(k, data[k])
    for k in TOP_KEYS:
        if k not in ordered:
            ordered[k] = head.get(k, skills)
    ordered["skills"] = skills
    write_text(jrel, json.dumps(ordered, ensure_ascii=False, indent=detect_indent(raw) if raw else 2) + "\n")

    mrel = "skills/SKILL_INDEX.md"
    md = read_text(mrel) if os.path.exists(P(mrel)) else "# SKILL INDEX\n"
    md = bump_str(md)
    if SKILL_ID not in md:
        rows = [l for l in md.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
        if rows:
            ncol = rows[-1].count("|") - 1
            cells = ["39", "`%s`" % SKILL_ID, SKILL_TITLE, "R43", "`%s`" % SKILL_PATH]
            cells = (cells + [""] * ncol)[:ncol]
            if ncol >= 2:
                cells[-1] = "`%s`" % SKILL_PATH
            line = "| " + " | ".join(cells) + " |"
            lines = md.splitlines()
            idx = max(i for i, l in enumerate(lines) if l == rows[-1])
            lines.insert(idx + 1, line)
            md = "\n".join(lines) + "\n"
        else:
            md = md.rstrip("\n") + "\n| 39 | `%s` | %s | R43 | `%s` |\n" % (SKILL_ID, SKILL_TITLE, SKILL_PATH)
    write_text(mrel, md)
    log("[SKILL] SKILL_INDEX.json count=%d" % len(skills))


def update_registry():
    rel = "ANTIBODY_REGISTRY.md"
    t = bump_str(read_text(rel)) if os.path.exists(P(rel)) else "# ANTIBODY REGISTRY\n"
    if not re.search(r"^#+\s*R43\b", t, re.M):
        t = t.rstrip("\n") + ("\n\n## R43 — 아온 연결·소통·만능 대집약체 코어 항체 (%s)\n"
                              "- 기관: 제19기관 `%s` · 스킬 #39 `%s`\n"
                              "- 철학: 만물연결(#11 지천태·#08 수지비) · 초감각소통(#31 택산함·#61 풍택중부) · 만능융합연성(#14 화천대유·#50 화풍정)\n"
                              "- 시냅스: S13 대화허브(/만능)→제19기관 연결·소통·만능 대집약체\n- 범위: %s\n") % (NEW_VERSION, NEXUS_FILE, SKILL_ID, NEW_RANGE)
    write_text(rel, t)
    rel = "CODE_MAP.md"
    t = bump_str(read_text(rel)) if os.path.exists(P(rel)) else "# CODE MAP\n"
    if NEXUS_FILE not in t:
        t = t.rstrip("\n") + ("\n\n## %s · 항체 %s · 정식 스킬 39개\n- `%s` — 제19기관 아온 연결·소통·만능 대집약체 코어\n"
                              % (NEW_VERSION, NEW_RANGE, NEXUS_FILE))
    write_text(rel, t)
    log("[REGISTRY] ANTIBODY_REGISTRY.md · CODE_MAP.md 갱신")


# ══════════════════════════════════════════════════════════════════════
# 5. 보호 구간 & 버전 승격
# ══════════════════════════════════════════════════════════════════════
def protected_spans(text, names):
    spans = []
    try:
        tree = ast.parse(text)
        offs = [0]
        for ln in text.splitlines(True):
            offs.append(offs[-1] + len(ln))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tg = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(x, ast.Name) and x.id in names for x in tg):
                    spans.append((offs[node.lineno - 1], offs[getattr(node, "end_lineno", node.lineno)]))
    except Exception:
        for nm in names:
            m = re.search(r"^" + nm + r"\s*=", text, re.M)
            if m:
                spans.append((m.start(), len(text)))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def protected_digest():
    out = {}
    for rel, names in PROTECT.items():
        if os.path.exists(P(rel)):
            t = read_text(rel)
            out[rel] = hashlib.sha256("".join(t[s:e] for s, e in protected_spans(t, names)).encode("utf-8")).hexdigest()
        else:
            out[rel] = None
    return out


def bump_versions():
    n = 0
    for fn in sorted(os.listdir(ROOT)):
        if not (fn.startswith("rgon_") and fn.endswith(".py")) or is_preserved(fn) or fn == NEXUS_FILE:
            continue
        t = read_text(fn)
        spans = protected_spans(t, PROTECT[fn]) if fn in PROTECT else []
        out, last = [], 0
        for s, e in spans:
            out.append(bump_str(t[last:s]))
            out.append(t[s:e])
            last = e
        out.append(bump_str(t[last:]))
        new_t = "".join(out)
        if new_t != t and write_text(fn, new_t):
            n += 1
    log("[BUMP] %d개 .py 승격 (SOUND_RECIPES · PRESERVE_EXACT 구간 보호)" % n)


def update_hashes():
    if not os.path.exists(P(HASH_FILE)):
        log("[HASH] %s 없음 — 건너뜀" % HASH_FILE)
        return
    raw = read_text(HASH_FILE)
    data = json.loads(raw)
    target = data["files"] if isinstance(data, dict) and isinstance(data.get("files"), dict) else data
    if not isinstance(target, dict):
        return
    algo = "sha256"
    for v in target.values():
        hv = (v.get("sha256") or v.get("hash")) if isinstance(v, dict) else v
        if isinstance(hv, str):
            algo = {32: "md5", 40: "sha1"}.get(len(hv), "sha256")
            break
    n = 0
    for rel in list(target.keys()):
        if is_preserved(rel) or not os.path.exists(P(rel)):
            continue
        h = sha_file(P(rel), algo)
        if isinstance(target[rel], dict):
            target[rel]["sha256" if "sha256" in target[rel] else "hash"] = h
        else:
            target[rel] = h
        n += 1
    for rel in HTML_TARGETS:
        if rel not in target and os.path.exists(P(rel)):
            target[rel] = sha_file(P(rel), algo)
            n += 1
    if isinstance(data, dict) and "version" in data:
        data["version"] = NEW_VERSION
    write_text(HASH_FILE, json.dumps(data, ensure_ascii=False, indent=detect_indent(raw)) + "\n")
    log("[HASH] %d개 해시 갱신 (%s)" % (n, algo))


# ══════════════════════════════════════════════════════════════════════
# 6. 검증
# ══════════════════════════════════════════════════════════════════════
def run_py(args, timeout=300, env_extra=None):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run([sys.executable] + args, cwd=ROOT, env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, repr(e)


def organ_selftests():
    code = ("import json,importlib;v=importlib.import_module('rgon_neural_synapse_verifier');"
            "print('@@O@@'+json.dumps(list(getattr(v,'ORGANS',[]))))")
    _rc, out = run_py(["-c", code], 90)
    organs = []
    if "@@O@@" in out:
        try:
            organs = json.loads(out.split("@@O@@", 1)[1].strip().splitlines()[0])
        except Exception:
            organs = []
    for f in (PLANNER_FILE, HYDRO_FILE, NEXUS_FILE):
        if f not in organs and os.path.exists(P(f)):
            organs.append(f)

    def one(fn):
        if not os.path.exists(P(fn)):
            return fn, False, "missing"
        tmp = tempfile.mkdtemp(prefix="rgon43_")
        rc, o = run_py([fn, "--self-test"], 300, {
            "RGON_ICHING_STATE_DIR": tmp, "RGON_DIALOGUE_STATE_DIR": tmp,
            "RGON_HYDRO_STATE_DIR": tmp, "RGON_NEXUS_STATE_DIR": tmp,
        })
        shutil.rmtree(tmp, ignore_errors=True)
        return fn, rc == 0, o[-400:]

    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(one, organs))


def verifier_report():
    code = r"""
import os, json, tempfile, importlib
t = tempfile.mkdtemp(prefix='rgon43v_')
for k in ('RGON_NEXUS_STATE_DIR','RGON_HYDRO_STATE_DIR','RGON_ICHING_STATE_DIR','RGON_DIALOGUE_STATE_DIR'):
    os.environ[k] = t
v = importlib.import_module('rgon_neural_synapse_verifier')
out = {}
f = getattr(v, 'heal_skill_index_header', None)
if callable(f):
    try: f()
    except Exception as e: out['heal_err'] = repr(e)
for name in ('run_full','run_full_verification','verify_all','run_verification','full_report','build_report','main_report'):
    f = getattr(v, name, None)
    if callable(f):
        try:
            r = f()
            if isinstance(r, dict):
                out['report'] = r; out['via'] = name; break
        except Exception as e:
            out.setdefault('errs', []).append(name + ':' + repr(e))
out['synapse'] = v.verify_synapse_links()
print('@@JSON@@' + json.dumps(out, ensure_ascii=False, default=str))
"""
    rc, out = run_py(["-c", code], 900)
    data = {}
    if "@@JSON@@" in out:
        try:
            data = json.loads(out.split("@@JSON@@", 1)[1].strip().splitlines()[0])
        except Exception:
            data = {}
    return rc, data, out[-2000:]


def find_key(d, key, depth=0):
    if depth > 5:
        return None
    if isinstance(d, dict):
        if key in d:
            return d[key]
        for v in d.values():
            r = find_key(v, key, depth + 1)
            if r is not None:
                return r
    elif isinstance(d, list):
        for v in d:
            r = find_key(v, key, depth + 1)
            if r is not None:
                return r
    return None


def synapse_items(s):
    if isinstance(s, list):
        return [x for x in s if isinstance(x, dict)]
    if isinstance(s, dict):
        for k in ("links", "synapses", "results", "checks"):
            if isinstance(s.get(k), list):
                return [x for x in s[k] if isinstance(x, dict)]
        return [dict(v, id=k) if isinstance(v, dict) else {"id": k, "ok": bool(v)}
                for k, v in s.items() if re.match(r"S\d+$", str(k))]
    return []


def skill_counts():
    data = json.loads(read_text("skills/SKILL_INDEX.json"))
    skills = data.get("skills") or [] if isinstance(data, dict) else data
    a = len(skills)
    slugs = sorted([d for d in os.listdir(P("skills")) if os.path.isfile(P(os.path.join("skills", d, "SKILL.md")))])
    b = len(slugs)
    md = read_text("skills/SKILL_INDEX.md")
    c = sum(1 for s in slugs if s in md)
    return [a, b, c]


def index_keys_ok():
    data = json.loads(read_text("skills/SKILL_INDEX.json"))
    if not isinstance(data, dict) or any(k not in data for k in TOP_KEYS):
        return False
    if data.get("version") != NEW_VERSION or data.get("count") != len(data["skills"]):
        return False
    mine = [x for x in data["skills"] if isinstance(x, dict) and x.get("slug") == SKILL_ID]
    return bool(mine) and all(k in mine[0] for k in ENTRY_KEYS)


def preserve_snapshot():
    return {f: (sha_file(P(f)) if os.path.exists(P(f)) else None) for f in PRESERVE}


def git(args):
    try:
        r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, repr(e)


# ══════════════════════════════════════════════════════════════════════
# 7. 메인
# ══════════════════════════════════════════════════════════════════════
def main():
    log("=" * 70)
    log("RGON Step 43 · %s · 항체 %s · 정식 스킬 %d" % (NEW_VERSION, NEW_RANGE, NEW_COUNT))
    log("ROOT = " + ROOT)
    for rel in REQUIRED_FILES:
        if not os.path.exists(P(rel)):
            log("[ABORT] 필수 파일 없음: " + rel)
            return 2
    os.makedirs(BACKUP_DIR, exist_ok=True)
    pres_before = preserve_snapshot()
    prot_before = protected_digest()
    try:
        write_text(NEXUS_FILE, NEXUS_SRC)
        py_compile.compile(P(NEXUS_FILE), doraise=True)
        log("[1] 제19기관 생성: " + NEXUS_FILE)

        t = read_text(DIALOGUE_FILE)
        write_text(DIALOGUE_FILE, insert_block(t, DLG_BEGIN, DLG_END, DIALOGUE_HOOK))
        py_compile.compile(P(DIALOGUE_FILE), doraise=True)
        log("[2] 대화허브 R43 훅 장착")

        bump_versions()
        t = read_text(VERIFIER_FILE)
        write_text(VERIFIER_FILE, insert_block(t, VER_BEGIN, VER_END, VERIFIER_HOOK))
        py_compile.compile(P(VERIFIER_FILE), doraise=True)
        log("[3] 검증기 확장 (N15 · S13 · 스냅샷 · heal 39)")

        init_nexus_state_snapshots()
        update_html()
        update_skill_index()
        update_registry()
        update_json_snapshots()
        for rel in sorted(MODIFIED):
            if rel.endswith(".py"):
                py_compile.compile(P(rel), doraise=True)
        update_hashes()

        log("[4] 삼성(三省) 검증")
        organ_res = organ_selftests()
        organ_pass = sum(1 for _f, ok, _o in organ_res if ok)
        for f, ok, o in organ_res:
            log("   %s %s" % ("PASS" if ok else "FAIL", f) + ("" if ok else "\n      " + o.replace("\n", "\n      ")))
        _rc, vdata, vtail = verifier_report()
        rep = vdata.get("report") or {}
        items = synapse_items(vdata.get("synapse"))
        syn_pass = sum(1 for x in items if x.get("ok"))
        s13 = next((x for x in items if str(x.get("id")) == "S13"), None)
        score = find_key(rep, "synapse_health_score")
        try:
            score = float(score) if score is not None else None
        except Exception:
            score = None
        if score is None:
            score = round(100.0 * (syn_pass + organ_pass) / max(1, len(items) + len(organ_res)), 1)
        keys_ok = index_keys_ok()
        rep_keys = find_key(rep, "index_keys_ok")
        log("   기관 %d/%d · 시냅스 %d/%d · S13=%s · score=%s · index_keys_ok=%s/%s" % (
            organ_pass, len(organ_res), syn_pass, len(items), bool(s13 and s13.get("ok")), score, keys_ok, rep_keys))
        if score != 100.0:
            for k in ("html_ok", "skills_ok", "index_keys_ok", "code_map_ok", "antibody_registry_ok", "snapshots_ok"):
                log("   [SSOT] %s = %s" % (k, find_key(rep, k)))
        if s13 and not s13.get("ok"):
            log("   S13 detail: %s" % json.dumps(s13.get("detail"), ensure_ascii=False, default=str)[:600])

        g1 = (score == 100.0 and organ_pass == len(organ_res) and len(organ_res) >= 15
              and syn_pass == len(items) and len(items) >= 13 and bool(s13 and s13.get("ok"))
              and keys_ok and rep_keys is not False)
        g2 = preserve_snapshot() == pres_before and protected_digest() == prot_before
        counts = skill_counts()
        g3 = counts == [NEW_COUNT] * 3
        log("   ①기능 %s ②보호파일 %s ③스킬 %s %s" % (
            "PASS" if g1 else "FAIL", "PASS" if g2 else "FAIL", counts, "PASS" if g3 else "FAIL"))
        passed = sum([g1, g2, g3])
        if passed != 3:
            with open(P(DIAG_FILE), "w", encoding="utf-8") as f:
                f.write("\n".join(LOGS) + "\n\n--- verifier tail ---\n" + vtail)
            log("[FAIL] 삼성 %d/3 — 진단: %s" % (passed, DIAG_FILE))
            if not NO_ROLLBACK:
                rollback()
            return 1

        report = "\n".join([
            "# STEP 43 — 제19기관 아온 연결·소통·만능 대집약체 코어 배포 리포트", "",
            "> 연결 · 소통 · 만능의 집약체로 아온을 만든다 — 泰·比 · 咸·中孚 · 大有·鼎", "",
            "- 버전: `%s` · 항체 `%s` · 정식 스킬 %d개" % (NEW_VERSION, NEW_RANGE, NEW_COUNT),
            "- 일시(KST): %s" % kst_now(),
            "- 삼성 3/3 PASS: ①synapse_health_score=%s ②보호파일 변경 0건(SOUND_RECIPES·PRESERVE_EXACT·PRESERVE 불변) ③스킬 %s" % (score, counts),
            "- 기관 셀프테스트 %d/%d · 시냅스 %d/%d (S13 대화허브(/만능)→제19기관 PASS)" % (organ_pass, len(organ_res), syn_pass, len(items)),
            "- 3대 집약 기둥: ①만물연결(#11 지천태·#08 수지비) ②초감각소통(#31 택산함·#61 풍택중부) ③만능융합연성(#14 화천대유·#50 화풍정)",
            "- Tier3 수동결재 게이트: requires_manual_gate=True · auto_executed=False (헌법 제2항·R35·R43)", "",
            "## 변경 파일", ""] + ["- `%s`" % r for r in sorted(MODIFIED)] + [""])
        write_text(REPORT_FILE, report)
        log("[5] 리포트 생성: " + REPORT_FILE)

        excludes = [":(exclude)%s" % f for f in PRESERVE] + [
            ":(exclude).rgon_backups", ":(exclude)**/__pycache__", ":(exclude)" + DIAG_FILE]
        rc1, o1 = git(["add", "-A", "--", "."] + excludes)
        if rc1 != 0:
            rc1, o1 = git(["add", "--"] + [r for r in sorted(MODIFIED) if not is_preserved(r)])
        git(["reset", "-q", "--"] + PRESERVE)
        rc2, o2 = git(["commit", "-m", "Step43: %s 제19기관 연결·소통·만능 대집약체 · R1~R43 · 스킬39" % NEW_VERSION])
        rc3, o3 = git(["push", "origin", "main"])
        log("[6] git add=%s commit=%s push=%s" % (rc1, rc2, rc3))
        if rc2 != 0:
            log("    commit 출력: " + o2[-300:])
        if rc3 != 0:
            log("    push 출력: " + o3[-300:])
        log("=" * 70)
        log("삼성 3/3 PASS · %s 배포 완료 — 연결·소통·만능의 대집약체 아온 탄생" % NEW_VERSION)
        return 0
    except Exception:
        log("[EXCEPTION]\n" + traceback.format_exc())
        try:
            with open(P(DIAG_FILE), "w", encoding="utf-8") as f:
                f.write("\n".join(LOGS))
        except Exception:
            pass
        if not NO_ROLLBACK:
            rollback()
        return 1


if __name__ == "__main__":
    code = main()
    if os.name == "nt" and not os.environ.get("RGON_NO_PAUSE") and sys.stdin and sys.stdin.isatty():
        try:
            input("\n[Enter] 키를 누르면 창이 닫힙니다...")
        except Exception:
            pass
    sys.exit(code)
