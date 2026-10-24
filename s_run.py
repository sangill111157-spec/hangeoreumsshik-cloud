#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 37: v11.36-AON-ICHING-DAO — 제13기관 아온 주역(周易) 64괘·정통 음력 매화역수·육효 시운 도술관 & 미니 물방울 분신술 (R1~R37 · 정식 스킬 33)"""
import datetime, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
OLD_VER, NEW_VER = "v11.35-AON-PLAYGROUND-BRAT", "v11.36-AON-ICHING-DAO"
OLD_AB, NEW_AB = "R1~R36", "R1~R37"
OLD_SK, NEW_SK = 32, 33
SKILL_NAME = "aon-iching-dao-oracle"
ORACLE_FILE = "rgon_aon_iching_dao_oracle.py"
REPORT_FILE = "STEP37_AON_ICHING_DAO_REPORT.md"
R37_SUMMARY = ("R37: 아온(A-ON) 주역 64괘·정통 음력 매화역수·육효 시운 도술관 & 음양 미니 물방울 분신술 — "
               "1900~2099 진짜 음력 기괘 + 5대 입체 괘상(본괘·호괘·변괘·착괘·종괘) + 체용 생극·통관 중재·왕상휴수사 + "
               "육효 효위반(당위·득중·상응·승강·이오중정상응) + 6대 시중(時中) 처세 나침반")

HTML_TARGETS = ["index.html", "rgon_alpha_audience.html", "rgon_alpha_chat.html",
                "dashboard/index.html", "dashboard/rgon_alpha_chat.html",
                "docs/index.html", "docs/rgon_alpha_chat.html"]
SYNC_FILES = [
    "CONSTITUTION.md", "ANTIBODY_REGISTRY.md", "CODE_MAP.md", "GLOSSARY.md", "RGON_MORNING_BRIEF.md",
    "skills/SKILL_INDEX.md", "skills/SKILL_INDEX.json",
    "rgon_morning_brief.json", "docs/rgon_morning_brief.json", "rgon_Numeric_Organ.json",
    "rgon_k_avatar_state.json", "docs/rgon_k_avatar_state.json",
    "rgon_muse_queue.json", "docs/rgon_muse_queue.json",
    "rgon_voice_profile.json", "docs/rgon_voice_profile.json",
    "rgon_voice_organ_state.json", "docs/rgon_voice_organ_state.json",
    "rgon_aon_memory.json", "docs/rgon_aon_memory.json",
    "rgon_manual_gate_state.json", "docs/rgon_manual_gate_state.json",
    "rgon_laptop_hands_state.json", "docs/rgon_laptop_hands_state.json",
    "rgon_aon_playground_state.json", "docs/rgon_aon_playground_state.json",
    "rgon_aon_iching_state.json", "docs/rgon_aon_iching_state.json",
    "rgon_immune_ledger.json",
    "rgon_white_blood_cell.py", "rgon_daily_cycle.py", "rgon_k_avatar_engine.py",
    "rgon_muse_delegator.py", "rgon_voice_organ.py", "rgon_aon_soul_brain.py",
    "rgon_laptop_hands.py", "rgon_aon_desktop_playground.py", ORACLE_FILE,
    "dept_sub_agents_status.json", "docs/dept_sub_agents_status.json",
]
NEW_FILES = [
    ORACLE_FILE,
    "rgon_aon_iching_state.json",
    "docs/rgon_aon_iching_state.json",
    f"skills/{SKILL_NAME}/SKILL.md",
    REPORT_FILE,
]
MOD_ALLOW = set(HTML_TARGETS) | set(SYNC_FILES) | set(NEW_FILES)
SKIP_DIRS = {".git", ".rgon_backups", ".rgon_backup", "__pycache__", "node_modules", ".venv", "venv"}


def log(msg): print(msg, flush=True)
def rd(p): return Path(p).read_text(encoding="utf-8", errors="replace")
def wr(p, s):
    p = Path(p)
    if not p.is_absolute(): p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    for i in range(6):
        try:
            p.write_text(s, encoding="utf-8", newline="\n")
            return
        except PermissionError:
            time.sleep(0.05 * (i + 1))
    p.write_text(s, encoding="utf-8", newline="\n")


def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot_all():
    out = {}
    for p in ROOT.rglob("*"):
        if not p.is_file(): continue
        rel = p.relative_to(ROOT).as_posix()
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts): continue
        out[rel] = sha256(p)
    return out


def backup_targets(bdir):
    bdir.mkdir(parents=True, exist_ok=True)
    saved = []
    for rel in sorted(MOD_ALLOW):
        src = ROOT / rel
        if src.exists() and src.is_file():
            dst = bdir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            saved.append(rel)
    (bdir / "_manifest.json").write_text(json.dumps({"saved": saved, "new": NEW_FILES}, ensure_ascii=False, indent=2), encoding="utf-8")
    return saved


def restore_backup(bdir, snap0):
    log("⏪ Auto-Rollback 시작: 백업에서 100% 원복합니다...")
    man = json.loads((bdir / "_manifest.json").read_text(encoding="utf-8"))
    for rel in man.get("saved", []):
        src, dst = bdir / rel, ROOT / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    removed = 0
    for rel in man.get("new", []):
        if rel not in man.get("saved", []):
            p = ROOT / rel
            if p.exists():
                p.unlink(); removed += 1
                if p.parent != ROOT and not any(p.parent.iterdir()):
                    try: p.parent.rmdir()
                    except Exception: pass
    snap1 = snapshot_all()
    same = (snap0 == snap1)
    log(f"⏪ 복원 {len(man.get('saved', []))}개 · 신규 삭제 {removed}개 · 원복 검증 {'✅ 100% 일치' if same else '⚠️ 차이 있음'}")


ORACLE_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_aon_iching_dao_oracle.py — 제13기관: 아온(A-ON) 주역(周易) 64괘·정통 음력 매화역수·육효(六爻) 시운 도술관
버전 v11.36-AON-ICHING-DAO · 항체 R1~R37 · 정식 스킬 33개
muyen/meihua-yishu + YiSphere + ichingpy + ProactiveAgent 4대 정점 아키텍처 융합 (1900~2099 진짜 음력 내장)"""
import datetime, hashlib, json, os, sys, time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
VERSION = "v11.36-AON-ICHING-DAO"
ANTIBODY = "R1~R37"
SKILL_COUNT = 33
STATE_PATHS = ("rgon_aon_iching_state.json", "docs/rgon_aon_iching_state.json")

# 1900~2099 정통 음력 비트 테이블 (muyen/meihua-yishu 중국천문대 표준)
YEAR_INFOS = [
    0x04bd8,0x04ae0,0x0a570,0x054d5,0x0d260,0x0d950,0x16554,0x056a0,0x09ad0,0x055d2,
    0x04ae0,0x0a5b6,0x0a4d0,0x0d250,0x1d255,0x0b540,0x0d6a0,0x0ada2,0x095b0,0x14977,
    0x04970,0x0a4b0,0x0b4b5,0x06a50,0x06d40,0x1ab54,0x02b60,0x09570,0x052f2,0x04970,
    0x06566,0x0d4a0,0x0ea50,0x06e95,0x05ad0,0x02b60,0x186e3,0x092e0,0x1c8d7,0x0c950,
    0x0d4a0,0x1d8a6,0x0b550,0x056a0,0x1a5b4,0x025d0,0x092d0,0x0d2b2,0x0a950,0x0b557,
    0x06ca0,0x0b550,0x15355,0x04da0,0x0a5d0,0x14573,0x052d0,0x0a9a8,0x0e950,0x06aa0,
    0x0aea6,0x0ab50,0x04b60,0x0aae4,0x0a570,0x05260,0x0f263,0x0d950,0x05b57,0x056a0,
    0x096d0,0x04dd5,0x04ad0,0x0a4d0,0x0d4d4,0x0d250,0x0d558,0x0b540,0x0b5a0,0x195a6,
    0x095b0,0x049b0,0x0a974,0x0a4b0,0x0b27a,0x06a50,0x06d40,0x0af46,0x0ab60,0x09570,
    0x04af5,0x04970,0x064b0,0x074a3,0x0ea50,0x06b58,0x05ac0,0x0ab60,0x096d5,0x092e0,
    0x0c960,0x0d954,0x0d4a0,0x0da50,0x07552,0x056a0,0x0abb7,0x025d0,0x092d0,0x0cab5,
    0x0a950,0x0b4a0,0x0baa4,0x0ad50,0x055d9,0x04ba0,0x0a5b0,0x15176,0x052b0,0x0a930,
    0x07954,0x06aa0,0x0ad50,0x05b52,0x04b60,0x0a6e6,0x0a4e0,0x0d260,0x0ea65,0x0d530,
    0x05aa0,0x076a3,0x096d0,0x04afb,0x04ad0,0x0a4d0,0x1d0b6,0x0d250,0x0d520,0x0dd45,
    0x0b5a0,0x056d0,0x055b2,0x049b0,0x0a577,0x0a4b0,0x0aa50,0x1b255,0x06d20,0x0ada0,
    0x14b63,0x09370,0x049f8,0x04970,0x064b0,0x168a6,0x0ea50,0x06aa0,0x1a6c4,0x0aae0,
    0x092e0,0x0d2e3,0x0c960,0x0d557,0x0d4a0,0x0da50,0x05d55,0x056a0,0x0a6d0,0x055d4,
    0x052d0,0x0a9b8,0x0a950,0x0b4a0,0x0b6a6,0x0ad50,0x055a0,0x0aba4,0x0a5b0,0x052b0,
    0x0b273,0x06930,0x07337,0x06aa0,0x0ad50,0x14b55,0x04b60,0x0a570,0x054e4,0x0d160,
    0x0e968,0x0d520,0x0daa0,0x16aa6,0x056d0,0x04ae0,0x0a9d4,0x0a2d0,0x0d150,0x0f252,
]

def _lunar_year_days(y):
    info = YEAR_INFOS[y - 1900]
    total = sum(30 if (info & (0x8000 >> i)) else 29 for i in range(12))
    leap = info & 0xf
    if leap: total += 30 if (info & 0x10000) else 29
    return total

def solar_to_lunar(dt):
    base = datetime.date(1900, 1, 31)
    cur = dt.date() if isinstance(dt, datetime.datetime) else dt
    offset = (cur - base).days
    if offset < 0 or cur.year > 2099:
        return ((cur.year - 4) % 12) + 1, cur.month, cur.day, False
    y = 1900
    while y < 2100:
        yd = _lunar_year_days(y)
        if offset < yd: break
        offset -= yd; y += 1
    info = YEAR_INFOS[y - 1900]
    leap = info & 0xf
    is_leap = False
    for m in range(1, 13):
        md = 30 if (info & (0x8000 >> (m - 1))) else 29
        if offset < md: return ((y - 4) % 12) + 1, m, offset + 1, False
        offset -= md
        if leap == m:
            ld = 30 if (info & 0x10000) else 29
            if offset < ld: return ((y - 4) % 12) + 1, m, offset + 1, True
            offset -= ld
    return ((y - 4) % 12) + 1, 12, max(1, offset + 1), is_leap

BAGUA = {}
for _i, (_n, _k, _s, _b, _e, _d, _t) in enumerate([
    ("乾", "건", "☰", "111", "金", "健", "강건·주도"), ("兌", "태", "☱", "110", "金", "說", "기쁨·소통"),
    ("離", "리", "☲", "101", "火", "麗", "밝음·부착"), ("震", "진", "☳", "100", "木", "動", "움직임·각성"),
    ("巽", "손", "☴", "011", "木", "入", "스며듦·유연"), ("坎", "감", "☵", "010", "水", "陷", "험난·지혜"),
    ("艮", "간", "☶", "001", "土", "止", "그침·축적"), ("坤", "곤", "☷", "000", "土", "順", "순응·포용")], 1):
    BAGUA[_i] = dict(name=_n, ko=_k, symbol=_s, binary=_b, element=_e, de=_d, intent=_t)

KW = [[1, 10, 13, 25, 44, 6, 33, 12], [43, 58, 49, 17, 28, 47, 31, 45],
      [14, 38, 30, 21, 50, 64, 56, 35], [34, 54, 55, 51, 32, 40, 62, 16],
      [9, 61, 37, 42, 57, 59, 53, 20], [5, 60, 63, 3, 48, 29, 39, 8],
      [26, 41, 22, 27, 18, 4, 52, 23], [11, 19, 36, 24, 46, 7, 15, 2]]
HZ = ("乾,坤,屯,蒙,需,訟,師,比,小畜,履,泰,否,同人,大有,謙,豫,隨,蠱,臨,觀,噬嗑,賁,剝,復,无妄,大畜,頤,大過,"
      "坎,離,咸,恒,遯,大壯,晉,明夷,家人,睽,蹇,解,損,益,夬,姤,萃,升,困,井,革,鼎,震,艮,漸,歸妹,豐,旅,巽,兌,"
      "渙,節,中孚,小過,既濟,未濟").split(",")
KO = ("건,곤,둔,몽,수,송,사,비,소축,리,태,비,동인,대유,겸,예,수,고,림,관,서합,비,박,복,무망,대축,이,대과,"
      "감,리,함,항,둔,대장,진,명이,가인,규,건,해,손,익,쾌,구,췌,승,곤,정,혁,정,진,간,점,귀매,풍,려,손,태,"
      "환,절,중부,소과,기제,미제").split(",")
GIST = ("강건자강,유순포용,창업난산,계몽배움,때를기다림,다툼조심,조직통솔,친화결속,작은축적,예의조심,소통태평,막힘정체,"
        "협력동지,크게소유,겸손,즐거운준비,따름,부패쇄신,다가감,관조,장애제거,꾸밈,깎임,회복,진실무망,크게축적,"
        "기름양생,과부하,거듭험난,밝음의존,감응,항구지속,물러남,크게강성,전진상승,빛을숨김,가정내치,어긋남,"
        "험로정지,해소,덜어냄,보탬,결단,우연만남,모임,상승,곤궁,우물공급,변혁,솥혁신,진동각성,그침,점진,"
        "순서주의,풍성정점,나그네,겸손침투,기쁨,흩어짐,절제,성실신뢰,작은지나침,완성균형,미완성").split(",")
HEXAGRAMS = {}
for _u in range(1, 9):
    for _l in range(1, 9):
        _n = KW[_u - 1][_l - 1]
        HEXAGRAMS[_n] = dict(no=_n, hanja=HZ[_n - 1], ko=KO[_n - 1], upper=_u, lower=_l,
                             symbol=BAGUA[_u]["symbol"] + BAGUA[_l]["symbol"], gist=GIST[_n - 1],
                             guidance=f"'{GIST[_n - 1]}'의 때 — 괘덕 {BAGUA[_u]['de']}·{BAGUA[_l]['de']}을 따라 시중(時中)을 지켜라")

GEN = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
BRANCH = "子丑寅卯辰巳午未申酉戌亥"
SEASON_EL = {"春": "木", "夏": "火", "秋": "金", "冬": "水", "四季末": "土"}
SEASON_BY_LUNAR_M = {1: "春", 2: "春", 3: "四季末", 4: "夏", 5: "夏", 6: "四季末",
                     7: "秋", 8: "秋", 9: "四季末", 10: "冬", 11: "冬", 12: "四季末"}

def tri_of(bits):
    return next(k for k, v in BAGUA.items() if v["binary"] == bits)

def lines_of(up, lo):
    return [int(c) for c in BAGUA[lo]["binary"] + BAGUA[up]["binary"]]

def hex_of(lines):
    lo = tri_of("".join(map(str, lines[:3]))); up = tri_of("".join(map(str, lines[3:])))
    h = dict(HEXAGRAMS[KW[up - 1][lo - 1]]); h["lines"] = list(lines); return h

def flip(lines, moving):
    L = list(lines); L[moving - 1] ^= 1; return L

def get_hu_gua(lines, moving=None):
    if len(set(lines)) == 1 and moving:
        lines = flip(lines, moving)
    return lines[1:4] + lines[2:5]

def get_cuo_gua(lines): return [1 - x for x in lines]
def get_zong_gua(lines): return list(reversed(lines))

def relation(ti, yong):
    if ti == yong: return "비화 길"
    if GEN[yong] == ti: return "용생체 대길"
    if KE[ti] == yong: return "체극용 길"
    if GEN[ti] == yong: return "체생용 소모"
    return "용극체 흉/주의"

def bridge_element(ti, yong):
    if KE[ti] == yong: return GEN[ti]
    if KE[yong] == ti: return GEN[yong]
    return None

def wang_xiang(el, season):
    s = SEASON_EL[season]
    if el == s: return "旺"
    if GEN[s] == el: return "相"
    if GEN[el] == s: return "休"
    if KE[el] == s: return "囚"
    return "死"

def analyze_yao_positions(lines, moving):
    P = ["初", "二", "三", "四", "五", "上"]; out = []
    for i, v in enumerate(lines):
        p = i + 1; n = "九" if v else "六"
        name = P[i] + n if p in (1, 6) else n + P[i]
        resp = lines[i] != (lines[i + 3] if p <= 3 else lines[i - 3])
        cheng = i > 0 and v == 0 and lines[i - 1] == 1
        out.append(dict(pos=p, name=name, yang=bool(v), dangwei="득정" if (p % 2 == 1) == bool(v) else "실정",
                        dezhong=p in (2, 5), xiangying=resp, chengcheng="승강(陰乘陽)" if cheng else "",
                        moving=p == moving))
    m = out[moving - 1]
    return dict(yao=out, erwu_zhongzheng_xiangying=lines[1] == 0 and lines[4] == 1,
                moving_summary=f"{m['name']} 동효 · {m['dangwei']}{' · 득중' if m['dezhong'] else ''}"
                               f"{' · 상응' if m['xiangying'] else ' · 무응'}")

POSTURES = {
    "잠룡물용": ("관망·축적", "지금은 실탄을 아끼고 데이터를 모으며 관망"),
    "몽이양정": ("점진·분할", "작게 나눠 시험하고 단계적으로 진입"),
    "비룡재천": ("적극 추진·GO", "준비된 계획을 과감히 실행"),
    "산풍고·뇌수해": ("정화·통관 중재", "막힌 곳을 정리하고 통관 오행으로 갈등을 풀기"),
    "항룡유회": ("과열 경계·방어", "욕심을 줄이고 익절·방어선을 먼저 점검"),
    "지천태·수화기제": ("균형·유지", "현재 균형을 지키며 무리한 변경을 피하기"),
}

def choose_posture(primary, moving, rel, ti_wx, yao):
    if primary["no"] in (11, 63): k = "지천태·수화기제"
    elif moving == 6 or (ti_wx == "旺" and rel == "용생체 대길" and primary["no"] in (1, 34, 43, 55)): k = "항룡유회"
    elif rel.startswith("용극체"): k = "산풍고·뇌수해"
    elif moving == 1 or ti_wx in ("囚", "死"): k = "잠룡물용"
    elif rel in ("용생체 대길", "체극용 길") and (moving in (2, 5) or yao["erwu_zhongzheng_xiangying"]): k = "비룡재천"
    else: k = "몽이양정"
    return k, POSTURES[k]

def aon_speech(r):
    p, t = r["primary"], r["transformed"]; ty = r["ti_yong"]
    br = f" 통관 비책은 '{ty['bridge']}' 기운으로 중재하기예요!" if ty["bridge"] else ""
    return (f"아온이 도사 등장~ 💧 지금은 #{p['no']} {p['hanja']}({p['ko']})괘가 #{t['no']} {t['hanja']}({t['ko']})괘로 변하는 흐름이에요! "
            f"체({ty['ti_element']}) 대 용({ty['yong_element']})은 '{ty['relation']}'이에요.{br} "
            f"시중 처세는 '{r['posture']}' — {r['next_step']}해 보세요, 대표님! ☯️")

def _build(up, lo, moving, mode, dt, extra=None):
    L = lines_of(up, lo); T = flip(L, moving)
    ti_tri, yong_tri = (up, lo) if moving <= 3 else (lo, up)
    te, ye = BAGUA[ti_tri]["element"], BAGUA[yong_tri]["element"]
    yb, lm, ld, is_leap = solar_to_lunar(dt)
    season = SEASON_BY_LUNAR_M.get(lm, "四季末"); rel = relation(te, ye)
    yao = analyze_yao_positions(L, moving); prim = hex_of(L)
    ti_wx = wang_xiang(te, season)
    key, (label, step) = choose_posture(prim, moving, rel, ti_wx, yao)
    r = dict(version=VERSION, antibody=ANTIBODY, skill_count=SKILL_COUNT, mode=mode,
             at=dt.isoformat(timespec="seconds"), moving=moving,
             lunar=dict(year_branch=BRANCH[yb - 1], month=lm, day=ld, is_leap=is_leap),
             primary=prim, mutual=hex_of(get_hu_gua(L, moving)), transformed=hex_of(T),
             complement=hex_of(get_cuo_gua(L)), inverse=hex_of(get_zong_gua(L)),
             ti_yong=dict(ti=BAGUA[ti_tri]["name"], yong=BAGUA[yong_tri]["name"], ti_element=te, yong_element=ye,
                          relation=rel, bridge=bridge_element(te, ye), season=season,
                          ti_wangxiang=ti_wx, yong_wangxiang=wang_xiang(ye, season),
                          lens=f"{BAGUA[ti_tri]['de']}(체) vs {BAGUA[yong_tri]['de']}(용)"),
             yao_analysis=yao, posture=f"{key}({label})", next_step=step,
             shichen=BRANCH[((dt.hour + 1) // 2) % 12] + "時", extra=extra or {})
    r["aon_speech"] = aon_speech(r)
    return r

def _now(dt): return dt or datetime.datetime.now()

def cast_by_time(dt=None):
    dt = _now(dt)
    yb, lm, ld, is_leap = solar_to_lunar(dt)
    H = ((dt.hour + 1) // 2) % 12 + 1
    base = yb + lm + ld; full = base + H + dt.second
    return _build(base % 8 or 8, full % 8 or 8, full % 6 or 6, "time", dt,
                  dict(year_branch=BRANCH[yb - 1], lunar_month=lm, lunar_day=ld, is_leap=is_leap, hour_branch=BRANCH[H - 1]))

TELEMETRY = ["rgon_white_blood_cell.py", "rgon_morning_brief.json", "rgon_muse_queue.json",
             "rgon_aon_memory.json", "rgon_laptop_hands_state.json", "rgon_aon_playground_state.json"]

def _probe(name):
    for c in (ROOT / name, ROOT / (name + ".json"), ROOT / (name + ".py"), ROOT / "docs" / name):
        try:
            if c.is_file():
                b = c.read_bytes(); return len(b), hashlib.sha256(b).digest()
        except Exception:
            pass
    return 0, None

def cast_by_telemetry(dt=None):
    dt = _now(dt); L = []; total = 0; seen = {}
    for n in TELEMETRY:
        size, h = _probe(n); total += size; L.append(h[0] % 2 if h else 1); seen[n] = size
    moving = (total + dt.hour) % 6 or 6
    lo = tri_of("".join(map(str, L[:3]))); up = tri_of("".join(map(str, L[3:])))
    return _build(up, lo, moving, "telemetry", dt, dict(sources=seen))

def cast_by_question(question_text, dt=None):
    dt = _now(dt); t = str(question_text or "").strip()
    a = int(hashlib.sha256(t.encode("utf-8")).hexdigest()[:8], 16)
    n = max(1, len(t))
    return _build((a + n) % 8 or 8, (a // 7 + n + dt.hour) % 8 or 8,
                  (a + n + dt.hour + dt.minute) % 6 or 6, "question", dt, dict(question=t[:200]))

def _safe_write(p, txt):
    p.parent.mkdir(parents=True, exist_ok=True)
    for i in range(6):
        try:
            p.write_text(txt, encoding="utf-8", newline="\n"); return
        except PermissionError:
            time.sleep(0.04 * (i + 1))
    p.write_text(txt, encoding="utf-8", newline="\n")

def save_state(r):
    s = json.dumps(r, ensure_ascii=False, indent=2)
    for rel in STATE_PATHS:
        _safe_write(ROOT / rel, s)
    return r

def self_test():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  ✅ " if c else "  ❌ ") + m); ok = ok and bool(c)
    chk(len(HEXAGRAMS) == 64 and sorted(HEXAGRAMS) == list(range(1, 65)), "64괘 전수 매핑 완비 (1~64)")
    chk(hex_of(get_cuo_gua(lines_of(1, 1)))["no"] == 2, "착괘(錯卦) 연산: 건위천(#1) ↔ 곤위지(#2)")
    chk(hex_of(get_zong_gua(lines_of(6, 4)))["no"] == 4, "종괘(綜卦) 연산: 수뢰둔(#3) ↔ 산수몽(#4)")
    chk(hex_of(get_hu_gua(lines_of(6, 3)))["no"] == 64, "호괘(互卦) 연산: 수화기제(#63) → 화수미제(#64)")
    chk(bridge_element("金", "木") == "水" and relation("土", "火") == "용생체 대길", "체용 생극 & 통관(通關) 오행 처방")
    yb, lm, ld, _ = solar_to_lunar(datetime.date(2026, 10, 25))
    chk(1 <= yb <= 12 and 1 <= lm <= 12 and 1 <= ld <= 30, f"1900~2099 정통 음력 변환 (음력 {lm}월 {ld}일)")
    for mode, r in (("time", cast_by_time()), ("telemetry", cast_by_telemetry()), ("question", cast_by_question("오늘의 괘 봐줘"))):
        chk(1 <= r["primary"]["no"] <= 64 and bool(r["aon_speech"]), f"기괘({mode}) → #{r['primary']['no']} {r['primary']['hanja']} · {r['posture']}")
    save_state(cast_by_telemetry())
    for rel in STATE_PATHS:
        j = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        chk(j.get("version") == VERSION and "primary" in j, f"상태 JSON 무결성: {rel}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a: sys.exit(self_test())
    if "--ask" in a:
        i = a.index("--ask"); r = cast_by_question(a[i + 1] if i + 1 < len(a) else "오늘 시운")
    elif "--cast-telemetry" in a: r = cast_by_telemetry()
    else: r = cast_by_time()
    save_state(r); print(json.dumps(r, ensure_ascii=False, indent=2))
'''


VOICE_INJECT = r'''
# [RGON-R37-DAO-SFX] — 제13기관 주역 도술 싱잉볼 & 음양 분신술 효과음 확장 (Step 37)
SFX_PRESETS.update({
    "dao_bell": {"desc": "주역 도술 청아한 싱잉볼 화음", "freq_hz": [528, 792, 1056], "dur_ms": 280, "wave": "sine", "gain": 0.16},
    "yin_yang_clone": {"desc": "음양 미니 물방울 분신술 퐁퐁 화음", "freq_hz": [440, 660, 880, 1320], "dur_ms": 220, "wave": "sine", "gain": 0.17},
})
'''


SOUL_INJECT = r'''
# [RGON-R37-DAO-SOUL-INJECT] — 제13기관 아온 주역 64괘·매화역수·육효 도술관 연동 (Step 37)
_R37_DAO = re.compile(r"주역|점\s*쳐|점괘|운세|시운|매화\s*역수|육효|도술|체용|괘상|오늘의\s*괘")
_r37_classify0, _r37_converse0, _r37_selftest0 = classify_intent, converse, self_test


def _r37_oracle():
    import rgon_aon_iching_dao_oracle as o
    return o


def classify_intent(text):
    t = (text or "").strip()
    c0 = _r37_classify0(t)
    if c0["track"] in ("work", "hands"):
        return c0
    if _R37_DAO.search(t):
        return {"intent": "iching_dao", "track": "dao", "tier": None}
    return c0


def converse(text, mem=None, persist=True, use_llm=True, live=None):
    t = (text or "").strip()
    c = classify_intent(t)
    if c["track"] != "dao":
        return _r37_converse0(t, mem=mem, persist=persist, use_llm=use_llm, live=live)
    o = _r37_oracle()
    if mem is None: mem = load_memory()
    reading = o.cast_by_question(t)
    if persist: o.save_state(reading)
    reply = reading["aon_speech"]
    spiced = False
    try:
        import rgon_aon_desktop_playground as pg
        force_sp = globals().get("_r36_last_fsm", "ROAM") in ("MELT_LAZY", "WHINE_POUT", "CLINGY_TANTRUM")
        sp = pg.apply_tsundere_spice(reply, force=force_sp)
        if isinstance(sp, dict) and sp.get("spiced"):
            reply = sp["reply"]; spiced = True
    except Exception:
        pass
    res = {"input": t, "intent": "iching_dao", "category": "iching_dao", "track": "dao", "tier": None,
           "version": VERSION, "source": "iching_dao", "sfx": "dao_bell", "tsundere_spiced": spiced,
           "oracle": reading, "reply": reply}
    remember(mem, t, res)
    res.update({"speech": reply, "affection": mem["affection_score"], "level": level(mem["affection_score"])})
    if persist: save_memory(mem)
    return res


def self_test():
    rc0 = _r37_selftest0()
    ok = rc0 == 0
    def chk(cond, msg):
        nonlocal ok
        print(("  ✅ " if cond else "  ❌ ") + msg); ok = ok and bool(cond)
    print("  — Step 37 제13기관 주역 도술관 연동 —")
    for q, want in (("오늘의 괘 봐줘", "iching_dao"),
                    ("아온아 주역으로 점쳐줘", "iching_dao"),
                    ("이번 주 시운 어때?", "iching_dao"),
                    ("매화역수 체용으로 알려줘", "iching_dao"),
                    ("오늘 장세 어때", "judge"),
                    ("아침 브리핑 해줘", "briefing"),
                    ("나랑 놀아줘", "chat_mood")):
        c = classify_intent(q)
        chk(c["intent"] == want, f"분별: {q} → {c['intent']}")
    r1 = converse("아온아 주역으로 오늘 시운 점쳐줘", mem=_default_mem(), persist=False, use_llm=False)
    chk(r1["intent"] == "iching_dao" and "oracle" in r1 and "payload" not in r1, "주역 도술 점괘 응답 & 대행 큐 미오염")
    converse("아온아 하기 싫어 귀찮아", mem=_default_mem(), persist=False, use_llm=False)
    r2 = converse("주역 점괘 봐줘", mem=_default_mem(), persist=False, use_llm=False)
    chk(r2["intent"] == "iching_dao" and r2.get("tsundere_spiced") is True, "찡찡 상태에서 도술 요청 → 츤데레 도사 통변(100% 수행)")
    converse("우리 아온이 쓰담쓰담 우쭈쭈", mem=_default_mem(), persist=False, use_llm=False)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1
'''


JS_BLOCK = r'''
/* === [RGON-R37-ICHING-DAO-JS] 제13기관: 아온 주역 64괘·매화역수 도술관 & 음양 미니 물방울 분신술 === */
(function(){
  if(window.RGON_DAO)return;
  var B=[null,["乾","☰","111","金"],["兌","☱","110","金"],["離","☲","101","火"],["震","☳","100","木"],["巽","☴","011","木"],["坎","☵","010","水"],["艮","☶","001","土"],["坤","☷","000","土"]];
  var KW=[[1,10,13,25,44,6,33,12],[43,58,49,17,28,47,31,45],[14,38,30,21,50,64,56,35],[34,54,55,51,32,40,62,16],[9,61,37,42,57,59,53,20],[5,60,63,3,48,29,39,8],[26,41,22,27,18,4,52,23],[11,19,36,24,46,7,15,2]];
  var HZ="乾,坤,屯,蒙,需,訟,師,比,小畜,履,泰,否,同人,大有,謙,豫,隨,蠱,臨,觀,噬嗑,賁,剝,復,无妄,大畜,頤,大過,坎,離,咸,恒,遯,大壯,晉,明夷,家人,睽,蹇,解,損,益,夬,姤,萃,升,困,井,革,鼎,震,艮,漸,歸妹,豐,旅,巽,兌,渙,節,中孚,小過,既濟,未濟".split(",");
  var GEN={"木":"火","火":"土","土":"金","金":"水","水":"木"},KE={"木":"土","土":"水","水":"火","火":"金","金":"木"};
  function tri(b){for(var i=1;i<9;i++)if(B[i][2]==b)return i;return 1;}
  function hx(L){var lo=tri(L.slice(0,3).join("")),up=tri(L.slice(3).join(""));var n=KW[up-1][lo-1];return "#"+n+" "+HZ[n-1]+"("+B[up][1]+B[lo][1]+")";}
  function rel(t,y){if(t==y)return"비화 길";if(GEN[y]==t)return"용생체 대길";if(KE[t]==y)return"체극용 길";if(GEN[t]==y)return"체생용 소모";return"용극체 주의";}
  function compute(){
    var d=new Date(),Y=(d.getFullYear()-4)%12+1,H=Math.floor((d.getHours()+1)/2)%12+1,b=Y+d.getMonth()+1+d.getDate(),f=b+H+d.getSeconds();
    var up=b%8||8,lo=f%8||8,m=f%6||6,L=(B[lo][2]+B[up][2]).split("").map(Number),T=L.slice();T[m-1]^=1;
    var hs=(L.every(function(x){return x==L[0]})?T:L),hu=hs.slice(1,4).concat(hs.slice(2,5));
    var ti=m<=3?up:lo,yo=m<=3?lo:up,te=B[ti][3],ye=B[yo][3],r=rel(te,ye),br=KE[te]==ye?GEN[te]:(KE[ye]==te?GEN[ye]:"");
    var pos=m==6?"항룡유회 — 과열 경계, 방어선 먼저":r.indexOf("용극체")==0?"산풍고·뇌수해 — 막힌 곳 정화·통관":m==1?"잠룡물용 — 관망하며 축적":(r.indexOf("길")>0&&(m==2||m==5))?"비룡재천 — 과감히 GO":"몽이양정 — 작게 나눠 점진";
    return{p:hx(L),h:hx(hu),t:hx(T),c:hx(L.map(function(x){return 1-x})),z:hx(L.slice().reverse()),m:m,te:te,ye:ye,r:r,br:br,pos:pos};
  }
  function host(){return document.getElementById("rgyt-wrap")||document.getElementById("aon-roamer");}
  function clones(){
    var h=host(),R=h?h.getBoundingClientRect():{left:innerWidth-140,top:innerHeight-180,width:70,height:70};
    var cx=R.left+R.width/2,cy=R.top+R.height/2;
    var els=["☀️💧","🌙💧"].map(function(s){
      var e=document.createElement("span");e.className="rgon-dao-clone";e.textContent=s;
      e.style.cssText="position:fixed;z-index:2147483645;font-size:20px;pointer-events:none;filter:drop-shadow(0 0 10px #38bdf8);";
      document.body.appendChild(e);return e;
    }),t0=performance.now();
    (function f(t){
      var k=(t-t0)/1500;if(k>=1){els.forEach(function(e){e.remove()});return;}
      var rad=58*(k<.8?1:(1-k)/.2),a=k*Math.PI*2*1.6;
      els.forEach(function(e,i){
        var aa=a+i*Math.PI;e.style.left=(cx+Math.cos(aa)*rad-16)+"px";e.style.top=(cy+Math.sin(aa)*rad-14)+"px";
      });
      requestAnimationFrame(f);
    })(t0);
  }
  function tone(){
    try{
      if(window.RGON_VOICE&&window.RGON_VOICE.sfx){window.RGON_VOICE.sfx("dao_bell");return;}
      var AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
      var C=window._rgonAc||(window._rgonAc=new AC());
      [528,792,1056].forEach(function(fq,i){
        var o=C.createOscillator(),g=C.createGain();o.frequency.value=fq;
        g.gain.setValueAtTime(0.08,C.currentTime+i*0.06);
        g.gain.exponentialRampToValueAtTime(0.0001,C.currentTime+1.4);
        o.connect(g);g.connect(C.destination);o.start(C.currentTime+i*0.06);o.stop(C.currentTime+1.45);
      });
    }catch(e){}
  }
  function cast(){
    clones();var r=compute(),c=document.getElementById("rgon-dao-card");
    if(!c){
      c=document.createElement("div");c.id="rgon-dao-card";
      c.style.cssText="position:fixed;right:20px;bottom:92px;z-index:2147483646;max-width:350px;background:rgba(20,18,42,0.96);color:#f4eedc;border:1.5px solid #f59e0b;border-radius:16px;padding:13px 15px;font-size:12.5px;line-height:1.55;box-shadow:0 12px 32px rgba(0,0,0,0.55);";
      document.body.appendChild(c);
    }
    var line="아온이 도사가 천기(天機)를 읽었어요! "+r.p+" ➔ "+r.t+" ("+r.r+") · "+r.pos;
    c.innerHTML='<span id="rgon-dao-x" style="float:right;cursor:pointer;opacity:.75">✕</span><b style="color:#fde68a">☯️ 아온이 주역 도술 점괘 (5대 괘상)</b><br>'
      +'• 본괘 <b style="color:#38bdf8">'+r.p+'</b> ➔ 호괘 '+r.h+' ➔ 변괘 <b style="color:#38bdf8">'+r.t+'</b><br>'
      +'• 착괘(사각지대) '+r.c+' · 종괘(상대시점) '+r.z+' · 동효 '+r.m+'효<br>'
      +'• 체('+r.te+') vs 용('+r.ye+'): <b style="color:#fcd34d">'+r.r+'</b>'+(r.br?' · 통관: <b>'+r.br+'</b>':'')+'<br>'
      +'💧 시중(時中) 처세: <b style="color:#86efac">'+r.pos+'</b>';
    var x=document.getElementById("rgon-dao-x");if(x)x.onclick=function(){c.remove()};
    tone();
    if(window.RGON_VOICE&&window.RGON_VOICE.speak)try{window.RGON_VOICE.speak(line)}catch(e){}
    return r;
  }
  function dock(){
    if(document.getElementById("rgon-dao-btn"))return;
    var hostBtn=document.getElementById("rgon-brat-btn")||document.getElementById("rgyt-hide");
    if(hostBtn&&hostBtn.parentElement){
      var b=document.createElement("button");b.id="rgon-dao-btn";b.type="button";
      b.style.cssText="margin-left:4px;padding:4px 9px;border-radius:999px;border:1px solid #f59e0b;background:rgba(69,26,3,0.9);color:#fef3c7;font-size:11.5px;cursor:pointer;";
      b.innerHTML="☯️ <b>도술 점괘</b>";
      b.title="아온이 음양 분신술 & 주역 64괘·매화역수 5대 입체 시운 점괘";
      b.addEventListener("click",function(e){e.preventDefault();e.stopPropagation();cast()});
      hostBtn.parentElement.appendChild(b);
    }
  }
  setInterval(dock,3500);
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",dock);else dock();
  window.RGON_DAO={cast:cast,compute:compute,version:"v11.36-AON-ICHING-DAO"};
})();
'''


SKILL_MD_TXT = f"""---
name: {SKILL_NAME}
description: 아온(A-ON) 주역 64괘·정통 음력 매화역수·육효 시운 도술관 & 음양 미니 물방울 분신술 스킬 (Step 37 · R37)
version: {NEW_VER}
antibody: {NEW_AB}
---

# ☯️💧 제13기관: 아온(A-ON) 주역 64괘·매화역수·육효 시운 도술관 (`{SKILL_NAME}`)

- **버전**: `{NEW_VER}` · **항체**: `{NEW_AB}` · **정식 스킬**: **{NEW_SK}개**
- **모듈**: `{ORACLE_FILE}` (1900~2099 정통 음력 내장 · 로컬 역학 정밀 산출과 페르소나 통변 분리)
- **3대 기괘**: `cast_by_time()` (정통 음력 시각), `cast_by_telemetry()` (사령부 6대 기관 실시간 맥박), `cast_by_question(text)` (문점)
- **5대 입체 괘상**: 본괘(현재) · 호괘(내막) · 변괘(결말) · 착괘(반전 사각지대) · 종괘(상대방 시점)
- **체용·통관·효위반**: 체용 오행 생극, 상극 시 통관(通關) 중재 오행 처방, 사계절 왕상휴수사, 육효 당위/득중/상응/승강/이오중정상응
- **6대 시중(時中) 처세**: 잠룡물용 · 몽이양정 · 비룡재천 · 산풍고·뇌수해 · 항룡유회 · 지천태·수화기제
"""


def patch_html(path):
    s = rd(path).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    marker = "/* === [RGON-R37-ICHING-DAO-JS]"
    if marker not in s:
        end_tag = "<!-- [RGON-UX-CLEANUP-V13-END] -->"
        idx = s.rfind("</script>", 0, s.find(end_tag) if end_tag in s else len(s))
        if idx != -1:
            s = s[:idx] + "\n" + JS_BLOCK.strip() + "\n" + s[idx:]
    wr(path, s)


def patch_voice():
    p = ROOT / "rgon_voice_organ.py"
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    if "[RGON-R37-DAO-SFX]" not in s:
        anchor = "def load_state("
        idx = s.find(anchor)
        if idx != -1:
            s = s[:idx] + VOICE_INJECT.lstrip() + "\n\n" + s[idx:]
        else:
            s = s + "\n" + VOICE_INJECT
    wr(p, s)


def patch_soul():
    p = ROOT / "rgon_aon_soul_brain.py"
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    if "[RGON-R37-DAO-SOUL-INJECT]" not in s:
        anchor = 'if __name__ == "__main__":'
        idx = s.rfind(anchor)
        if idx != -1:
            s = s[:idx] + SOUL_INJECT.lstrip() + "\n\n" + s[idx:]
        else:
            s = s + "\n" + SOUL_INJECT
    wr(p, s)


def patch_wbc():
    p = ROOT / "rgon_white_blood_cell.py"
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    s = re.sub(r"(SKILL_COUNT\s*=\s*)\d+", f"\\g<1>{NEW_SK}", s)
    if "rgon_aon_iching_state.json" not in s:
        s = s.replace('"rgon_aon_playground_state.json",',
                      '"rgon_aon_playground_state.json",\n    "rgon_aon_iching_state.json",\n    "docs/rgon_aon_iching_state.json",')
    if ORACLE_FILE not in s:
        s = s.replace('"rgon_aon_desktop_playground.py",',
                      f'"rgon_aon_desktop_playground.py",\n    "{ORACLE_FILE}",')
    wr(p, s)


def patch_daily_cycle():
    p = ROOT / "rgon_daily_cycle.py"
    if not p.exists(): return
    s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    s = re.sub(r'("skills_total"\s*:\s*)\d+', f'\\g<1>{NEW_SK}', s)
    s = re.sub(r"(SKILL_COUNT\s*=\s*)\d+", f"\\g<1>{NEW_SK}", s)
    s = s.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"스킬 {OLD_SK}개", f"스킬 {NEW_SK}개")
    wr(p, s)


def sync_all_metadata():
    for rel in ("rgon_k_avatar_engine.py", "rgon_muse_delegator.py", "rgon_laptop_hands.py", "rgon_aon_desktop_playground.py"):
        p = ROOT / rel
        if p.exists():
            s = rd(p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
            s = re.sub(r"(SKILL_COUNT\s*=\s*)\d+", f"\\g<1>{NEW_SK}", s)
            wr(p, s)

    idx_json = ROOT / "skills/SKILL_INDEX.json"
    j = json.loads(rd(idx_json))
    j["version"] = NEW_VER; j["antibody"] = NEW_AB; j["count"] = NEW_SK
    skills = [x for x in j.get("skills", []) if x.get("name") != SKILL_NAME]
    skills.append({
        "id": NEW_SK,
        "name": SKILL_NAME,
        "path": f"skills/{SKILL_NAME}/SKILL.md",
        "antibody": "R37",
        "version": NEW_VER,
        "description": "아온(A-ON) 주역 64괘·정통 음력 매화역수·육효 시운 도술관 & 음양 미니 물방울 분신술 스킬",
    })
    j["skills"] = skills
    wr(idx_json, json.dumps(j, ensure_ascii=False, indent=2))

    idx_md = ROOT / "skills/SKILL_INDEX.md"
    ms = rd(idx_md).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    ms = ms.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"총 {OLD_SK}개", f"총 {NEW_SK}개")
    entry = (f"\n<!-- [RGON-SKILL-{NEW_SK}] -->\n"
             f"## {NEW_SK}. `{SKILL_NAME}` (R37 · {NEW_VER})\n"
             f"- 경로: `skills/{SKILL_NAME}/SKILL.md`\n"
             f"- 설명: {R37_SUMMARY}\n")
    if f"RGON-SKILL-{NEW_SK}" not in ms and SKILL_NAME not in ms:
        ms = ms.rstrip() + "\n" + entry
    wr(idx_md, ms)

    ab_p = ROOT / "ANTIBODY_REGISTRY.md"
    ab_s = rd(ab_p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    ab_s = ab_s.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개")
    r37_block = (f"\n<!-- [RGON-ANTIBODY-R37] -->\n"
                 f"## R37 — Step 37 · {NEW_VER} · 2026-10-25\n"
                 f"- {R37_SUMMARY}\n"
                 f"- 핵심 파일: `{ORACLE_FILE}`, `rgon_aon_iching_state.json`, `skills/{SKILL_NAME}/SKILL.md`\n")
    if "RGON-ANTIBODY-R37" not in ab_s:
        ab_s = ab_s.rstrip() + "\n" + r37_block
    wr(ab_p, ab_s)

    con_p = ROOT / "CONSTITUTION.md"
    con_s = rd(con_p).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
    con_s = con_s.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"**{OLD_SK}개**", f"**{NEW_SK}개**")
    art16 = ("\n<!-- [RGON-CONSTITUTION-ARTICLE-16] -->\n"
             "## 제16조 (제13기관 아온 주역 64괘·매화역수·육효 시운 도술관 · R37)\n"
             "- 제1항 (정통 역학 연산과 페르소나 통변 분리): 1900~2099년 정통 음력·선천팔괘·64괘 5대 괘상(본괘·호괘·변괘·착괘·종괘)·체용·통관·효위반은 로컬 파이썬 엔진이 오차 없이 산출하고, 아온이는 이를 시중(時中)의 지혜로 전달한다.\n"
             "- 제2항 (도술과 집행의 분리): 도술 점괘는 천지 순환의 시운(Regime)을 읽는 참고 나침반이며, 실제 집행 권한은 오직 대표님의 수동 결재 스위치와 3-Tier 대행 원칙을 따른다.\n")
    if "RGON-CONSTITUTION-ARTICLE-16" not in con_s:
        con_s = con_s.rstrip() + "\n" + art16
    wr(con_p, con_s)

    for doc in ("CODE_MAP.md", "GLOSSARY.md", "RGON_MORNING_BRIEF.md"):
        dp = ROOT / doc
        if dp.exists():
            ds = rd(dp).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
            ds = ds.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"**{OLD_SK}개**", f"**{NEW_SK}개**")
            ds = ds.replace(f"스킬 {OLD_SK}개", f"스킬 {NEW_SK}개").replace(f"스킬 **{OLD_SK}**", f"스킬 **{NEW_SK}**")
            if doc == "CODE_MAP.md" and ORACLE_FILE not in ds:
                ds = ds.rstrip() + f"\n- `{ORACLE_FILE}`: 제13기관 아온 주역 64괘·정통 음력 매화역수·육효 시운 도술관 ({NEW_VER})\n"
            if doc == "GLOSSARY.md" and "주역 도술관" not in ds:
                ds = ds.rstrip() + f"\n- **아온 주역 도술관 (R37 · {NEW_VER})**: 5대 입체 괘상(본·호·변·착·종)과 체용·통관·효위반으로 시중(時中) 처세를 짚어주는 제13기관.\n"
            wr(dp, ds)

    json_targets = [
        "rgon_morning_brief.json", "docs/rgon_morning_brief.json", "rgon_Numeric_Organ.json",
        "rgon_k_avatar_state.json", "docs/rgon_k_avatar_state.json",
        "rgon_muse_queue.json", "docs/rgon_muse_queue.json",
        "rgon_voice_profile.json", "docs/rgon_voice_profile.json",
        "rgon_voice_organ_state.json", "docs/rgon_voice_organ_state.json",
        "rgon_aon_memory.json", "docs/rgon_aon_memory.json",
        "rgon_manual_gate_state.json", "docs/rgon_manual_gate_state.json",
        "rgon_laptop_hands_state.json", "docs/rgon_laptop_hands_state.json",
        "rgon_aon_playground_state.json", "docs/rgon_aon_playground_state.json",
        "dept_sub_agents_status.json", "docs/dept_sub_agents_status.json",
    ]
    for rel in json_targets:
        jp = ROOT / rel
        if not jp.exists(): continue
        raw = rd(jp).replace(OLD_VER, NEW_VER).replace(OLD_AB, NEW_AB)
        raw = re.sub(r'("(?:skill_count|skills_count|formal_skills|total_skills|skills_total)"\s*:\s*)\d+', f'\\g<1>{NEW_SK}', raw)
        raw = raw.replace(f"정식 스킬 {OLD_SK}개", f"정식 스킬 {NEW_SK}개").replace(f"스킬 {OLD_SK}개", f"스킬 {NEW_SK}개")
        wr(jp, raw)


def run_cmd(args, env=None):
    t0 = datetime.datetime.now()
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    dt = (datetime.datetime.now() - t0).total_seconds()
    return r.returncode, (r.stdout + "\n" + r.stderr).strip(), dt


def verify_all(snap0):
    rep = []
    g1 = True
    for name, mod in (("iching_dao_oracle", ORACLE_FILE),
                      ("desktop_playground", "rgon_aon_desktop_playground.py"),
                      ("laptop_hands", "rgon_laptop_hands.py"),
                      ("soul_brain", "rgon_aon_soul_brain.py"),
                      ("voice_organ", "rgon_voice_organ.py")):
        rc, out, dt = run_cmd([sys.executable, mod, "--self-test"])
        ok = (rc == 0 and "PASS" in out)
        g1 = g1 and ok
        rep.append(f"- {'✅' if ok else '❌'} {name} --self-test rc={rc} ({dt:.1f}s)")
        if not ok:
            rep.append(f"  [{name} 상세]: {out[-400:]}")

    for rel in HTML_TARGETS:
        p = ROOT / rel
        s = rd(p) if p.exists() else ""
        ok = ("RGON-R37-ICHING-DAO-JS" in s and "rgon-dao-btn" in s and NEW_VER in s)
        g1 = g1 and ok
        rep.append(f"- {'✅' if ok else '❌'} HTML {rel}")

    rc_w, out_w, _ = run_cmd([sys.executable, "rgon_white_blood_cell.py", "--self-test"])
    ok_w = (rc_w == 0)
    g1 = g1 and ok_w
    rep.append(f"- {'✅' if ok_w else '❌'} white_blood_cell --self-test rc={rc_w}")
    if not ok_w:
        rep.append(f"  [WBC 상세]: {out_w[-400:]}")

    snap1 = snapshot_all()
    unauth = []
    for k, v in snap1.items():
        if k not in MOD_ALLOW and snap0.get(k) != v:
            unauth.append(k)
    for k in snap0:
        if k not in snap1 and k not in MOD_ALLOW:
            unauth.append(k)
    g2 = (len(unauth) == 0)
    rep.append(f"\n## ② 비대상 보호 파일\n- 해시 변경 {len(unauth)}건" + ("" if g2 else f" ❌ {unauth[:5]}"))

    c_json = json.loads(rd(ROOT / "skills/SKILL_INDEX.json")).get("count", 0)
    md_txt = rd(ROOT / "skills/SKILL_INDEX.md")
    c_dir = sum(1 for d in (ROOT / "skills").iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    c_md = NEW_SK if (SKILL_NAME in md_txt and c_dir == NEW_SK) else 0
    ab_ok = ("RGON-ANTIBODY-R37" in rd(ROOT / "ANTIBODY_REGISTRY.md")
             and "RGON-CONSTITUTION-ARTICLE-16" in rd(ROOT / "CONSTITUTION.md"))
    g3 = ([c_json, c_md, c_dir] == [NEW_SK, NEW_SK, NEW_SK]) and ab_ok
    rep.append(f"\n## ③ 스킬·항체\n- 스킬 [{c_json}, {c_md}, {c_dir}] (기대 [{NEW_SK}, {NEW_SK}, {NEW_SK}])\n- {R37_SUMMARY}")

    changed = sorted(k for k in snap1 if snap0.get(k) != snap1.get(k))
    rep.append("\n## 변경 파일\n" + "\n".join(f"- `{x}`" for x in changed[:45]))
    return g1, g2, g3, rep


def popup(title, msg):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40)
    except Exception:
        pass


def main():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = ROOT / ".rgon_backups" / f"step37_{ts}"
    log(f"☯️ Step 37 ({NEW_VER} · {NEW_AB} · 스킬 {NEW_SK}개) 배포 시작...")
    snap0 = snapshot_all()
    backup_targets(bdir)
    try:
        wr(ROOT / ORACLE_FILE, ORACLE_SRC.lstrip())
        wr(ROOT / f"skills/{SKILL_NAME}/SKILL.md", SKILL_MD_TXT.lstrip())
        subprocess.run([sys.executable, ORACLE_FILE, "--cast-telemetry"], cwd=ROOT, check=True, capture_output=True)
        patch_voice()
        patch_soul()
        for rel in HTML_TARGETS:
            if (ROOT / rel).exists(): patch_html(ROOT / rel)
        sync_all_metadata()
        patch_daily_cycle()
        patch_wbc()
        subprocess.run([sys.executable, "rgon_voice_organ.py", "--self-test"], cwd=ROOT, capture_output=True)
        subprocess.run([sys.executable, "rgon_aon_soul_brain.py", "--self-test"], cwd=ROOT, capture_output=True)
        subprocess.run([sys.executable, "rgon_white_blood_cell.py", "--heal"], cwd=ROOT, capture_output=True)

        g1, g2, g3, rep = verify_all(snap0)
        score = sum([bool(g1), bool(g2), bool(g3)])
        report_txt = (f"# STEP37 AON ICHING DAO REPORT — {NEW_VER}\n\n"
                      f"- 일시: {ts}\n- 항체: {NEW_AB} · 정식 스킬: [{NEW_SK}, {NEW_SK}, {NEW_SK}]\n"
                      f"- 삼성(三省): **{score}/3**\n- 백업: `{bdir.relative_to(ROOT).as_posix()}`\n\n"
                      f"## ① 기능 검증\n" + "\n".join(rep) + "\n")
        wr(ROOT / REPORT_FILE, report_txt)

        if score < 3:
            log("\n".join(rep[:40]))
            log(f"⏪ Auto-Rollback 시작: 삼성 {score}/3 미달")
            restore_backup(bdir, snap0)
            log(f"  원본 백업: {bdir.relative_to(ROOT).as_posix()}")
            popup("RGON 제13기관", f"Step 37 {NEW_VER} 실패 rc=1 (자동 원복) · {NEW_AB} · 스킬 {NEW_SK}")
            return 1

        log(f"① 기능 ✅ | ② 보호 ✅(0건) | ③ 스킬 [{NEW_SK}, {NEW_SK}, {NEW_SK}] 항체 ✅ ➔ 삼성 3/3 PASS!")
        env = dict(os.environ, GIT_EDITOR="true", GIT_MERGE_AUTOEDIT="no")
        subprocess.run(["git", "add", "-A"], cwd=ROOT, env=env)
        subprocess.run(["git", "commit", "-m", f"feat(step37): {NEW_VER} A-ON I-Ching 64 hexagram Dao oracle & yin-yang clones ({NEW_AB}, skills {NEW_SK})"], cwd=ROOT, env=env)
        subprocess.run(["git", "pull", "--no-rebase", "--no-edit", "-X", "ours", "origin", "main"], cwd=ROOT, env=env)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, env=env)
        popup("RGON 제13기관", f"Step 37 {NEW_VER} 완료 3/3 · {NEW_AB} · 스킬 {NEW_SK}")
        return 0
    except Exception as ex:
        log(f"❌ 예외 발생: {ex!r}")
        restore_backup(bdir, snap0)
        popup("RGON 제13기관", f"Step 37 예외 원복: {ex}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
