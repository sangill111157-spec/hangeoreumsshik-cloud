#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_aon_iching_dao_oracle.py — 제13기관: 아온(A-ON) 주역(周易) 64괘·정통 음력 매화역수·육효(六爻) 시운 도술관
버전 v11.64-AON-15SHORTS-SUPER-SENIOR · 항체 R1~R57 · 정식 스킬 33개
muyen/meihua-yishu + YiSphere + ichingpy + ProactiveAgent 4대 정점 아키텍처 융합 (1900~2099 진짜 음력 내장)"""
import datetime, hashlib, json, os, sys, time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
VERSION = "v11.64-AON-15SHORTS-SUPER-SENIOR"
ANTIBODY = "R1~R57"
SKILL_COUNT = 39
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
    d_env = os.environ.get("RGON_ICHING_STATE_DIR", "").strip()
    base_dir = Path(d_env) if d_env else ROOT
    for rel in STATE_PATHS:
        target_p = base_dir / rel if (base_dir / rel).exists() else ROOT / rel
        j = json.loads(target_p.read_text(encoding="utf-8"))
        chk(j.get("version") == VERSION and "primary" in j, f"상태 JSON 무결성: {rel}")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

# ==== [RGON-R40-SYNAPSE-HOOK-START] ====
# R40 시냅스 ① — divine(q) 호환 별칭 + 병렬 검증 시 상태파일 격리
import os as _o40i, json as _j40i
from pathlib import Path as _P40i

if callable(globals().get("cast_by_question")) and not callable(globals().get("divine")):
    def divine(q, *a, **k):
        return cast_by_question(q, *a, **k)


def _r40_ich_dir():
    d = _o40i.environ.get("RGON_ICHING_STATE_DIR", "").strip()
    if not d:
        return None
    p = _P40i(d)
    p.mkdir(parents=True, exist_ok=True)
    return p


_r40_ich_orig_save = globals().get("save_state")
if callable(_r40_ich_orig_save) and not getattr(_r40_ich_orig_save, "_r40", False):
    def save_state(r, *a, **k):
        d = _r40_ich_dir()
        if d is None:
            return _r40_ich_orig_save(r, *a, **k)
        s = _j40i.dumps(r, ensure_ascii=False, indent=2)
        for rel in ("rgon_aon_iching_state.json", "docs/rgon_aon_iching_state.json"):
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(s, encoding="utf-8")
        return r
    save_state._r40 = True
# ==== [RGON-R40-SYNAPSE-HOOK-END] ====


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a: sys.exit(self_test())
    if "--ask" in a:
        i = a.index("--ask"); r = cast_by_question(a[i + 1] if i + 1 < len(a) else "오늘 시운")
    elif "--cast-telemetry" in a: r = cast_by_telemetry()
    else: r = cast_by_time()
    save_state(r); print(json.dumps(r, ensure_ascii=False, indent=2))
