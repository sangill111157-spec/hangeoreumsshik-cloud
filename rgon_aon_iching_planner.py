#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rgon_aon_iching_planner.py — 제17기관 아온(A-ON) 주역 64괘 시운 전략 기획관
I-Ching Strategic Action Planner (WOOP · OODA · Stop Rule · 12시진 택시 · 3분기 MCTS 트리)
정식 스킬 #37 aon-iching-strategic-planner · v11.44-AON-CINEMATIC-DISPATCH · 항체 R1~R45

헌법 제2항 · R35 · R41: 금융·실매매·파일삭제·외부배포는 '계획'만 수립하며 절대 자동 실행하지 않는다.
CLI: --self-test | --plan <주제> | --daily | --status [--json]
"""
import os
import re
import sys
import json
import math
import shutil
import hashlib
import argparse
import datetime
import tempfile
import importlib

for _s in ("stdout", "stderr"):
    _st = getattr(sys, _s, None)
    if _st and hasattr(_st, "reconfigure"):
        try:
            _st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

VERSION = "v11.44-AON-CINEMATIC-DISPATCH"
ANTIBODY_RANGE = "R1~R45"
ANTIBODY = "R41"
SKILL_COUNT = 39
SKILL_ID = "aon-iching-strategic-planner"
ORGAN_NAME = "제17기관 아온 주역 64괘 시운 전략 기획관"
STATE_NAME = "rgon_aon_iching_plan.json"
CONFIDENCE_CAP = 85.0
DEFAULT_GOAL = "오늘의 사령부 시운 전략 계획"
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

TRIGRAMS = {"乾": (1, 1, 1), "兌": (1, 1, 0), "離": (1, 0, 1), "震": (1, 0, 0),
            "巽": (0, 1, 1), "坎": (0, 1, 0), "艮": (0, 0, 1), "坤": (0, 0, 0)}
TRIGRAM_ELEM = {"乾": "金", "兌": "金", "離": "火", "震": "木", "巽": "木", "坎": "水", "艮": "土", "坤": "土"}
TRIGRAM_KO = {"乾": "건(천)", "兌": "태(택)", "離": "리(화)", "震": "진(뢰)", "巽": "손(풍)", "坎": "감(수)", "艮": "간(산)", "坤": "곤(지)"}
TRIGRAM_IMAGE = {"乾": "하늘(강건·추진)", "兌": "못(기쁨·소통)", "離": "불(밝음·통찰)", "震": "우레(발동·착수)",
                 "巽": "바람(침투·유연)", "坎": "물(험난·지혜)", "艮": "산(멈춤·축적)", "坤": "땅(포용·순응)"}
ELEM_ACTION = {"木": "기획·성장·신규 콘텐츠 씨앗 뿌리기", "火": "공개·확산·브리핑 발신",
               "土": "정리·축적·기반 다지기", "金": "결단·손절·규칙 집행", "水": "리서치·유동성 확보·복기와 휴식"}
GEN = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CTRL = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
GEN_BY = {v: k for k, v in GEN.items()}
SEASON_ELEM = {1: "木", 2: "木", 3: "土", 4: "火", 5: "火", 6: "土", 7: "金", 8: "金", 9: "土", 10: "水", 11: "水", 12: "土"}
SEASON_DELTA = {"旺": 10, "相": 6, "休": 0, "囚": -6, "死": -10}
TIYONG_RULES = [("용생체", 18, "용생체 대길"), ("체극용", 10, "체극용 길"), ("비화", 8, "비화 길"),
                ("체생용", -6, "체생용 소모"), ("용극체", -14, "용극체 흉/주의")]

_HEX_TABLE = """
乾乾 중천건 乾爲天
坤坤 중지곤 坤爲地
坎震 수뢰둔 水雷屯
艮坎 산수몽 山水蒙
坎乾 수천수 水天需
乾坎 천수송 天水訟
坤坎 지수사 地水師
坎坤 수지비 水地比
巽乾 풍천소축 風天小畜
乾兌 천택리 天澤履
坤乾 지천태 地天泰
乾坤 천지비 天地否
乾離 천화동인 天火同人
離乾 화천대유 火天大有
坤艮 지산겸 地山謙
震坤 뇌지예 雷地豫
兌震 택뢰수 澤雷隨
艮巽 산풍고 山風蠱
坤兌 지택림 地澤臨
巽坤 풍지관 風地觀
離震 화뢰서합 火雷噬嗑
艮離 산화비 山火賁
艮坤 산지박 山地剝
坤震 지뢰복 地雷復
乾震 천뢰무망 天雷无妄
艮乾 산천대축 山天大畜
艮震 산뢰이 山雷頤
兌巽 택풍대과 澤風大過
坎坎 중수감 坎爲水
離離 중화리 離爲火
兌艮 택산함 澤山咸
震巽 뇌풍항 雷風恒
乾艮 천산돈 天山遯
震乾 뇌천대장 雷天大壯
離坤 화지진 火地晉
坤離 지화명이 地火明夷
巽離 풍화가인 風火家人
離兌 화택규 火澤睽
坎艮 수산건 水山蹇
震坎 뇌수해 雷水解
艮兌 산택손 山澤損
巽震 풍뢰익 風雷益
兌乾 택천쾌 澤天夬
乾巽 천풍구 天風姤
兌坤 택지췌 澤地萃
坤巽 지풍승 地風升
兌坎 택수곤 澤水困
坎巽 수풍정 水風井
兌離 택화혁 澤火革
離巽 화풍정 火風鼎
震震 중뢰진 震爲雷
艮艮 중산간 艮爲山
巽艮 풍산점 風山漸
震兌 뇌택귀매 雷澤歸妹
震離 뇌화풍 雷火豐
離艮 화산려 火山旅
巽巽 중풍손 巽爲風
兌兌 중택태 兌爲澤
巽坎 풍수환 風水渙
坎兌 수택절 水澤節
巽兌 풍택중부 風澤中孚
震艮 뇌산소과 雷山小過
坎離 수화기제 水火旣濟
離坎 화수미제 火水未濟
"""
HEXAGRAMS = {}
BITS_TO_NUM = {}
for _i, _line in enumerate([l for l in _HEX_TABLE.strip().splitlines() if l.strip()], 1):
    _ul, _ko, _hj = _line.split()
    _up, _lo = _ul[0], _ul[1]
    _bits = tuple(TRIGRAMS[_lo]) + tuple(TRIGRAMS[_up])
    HEXAGRAMS[_i] = {"number": _i, "ko": _ko, "hanja": _hj, "upper": _up, "lower": _lo, "bits": _bits}
    BITS_TO_NUM[_bits] = _i

POSTURES = {
    "비룡재천": {"hanja": "飛龍在天", "gua": "#01 중천건 九五", "branch": "branch_yang",
              "stance": "공세 전개 — 때가 무르익었다. 핵심 과제에 자원을 집중하라."},
    "지천태·수화기제": {"hanja": "地天泰·水火旣濟", "gua": "#11 지천태 · #63 수화기제", "branch": "branch_zhong",
                  "stance": "태평 수성 — 이룬 질서를 지키며 점진적으로 넓혀라."},
    "몽이양정": {"hanja": "蒙以養正", "gua": "#04 산수몽", "branch": "branch_zhong",
              "stance": "배우며 바름을 기른다 — 파일럿과 학습으로 가설을 검증하라."},
    "산풍고·뇌수해": {"hanja": "山風蠱·雷水解", "gua": "#18 산풍고 · #40 뇌수해", "branch": "branch_yin",
                 "stance": "적폐 정화·병목 해소 — 쌓인 부패와 막힘을 먼저 풀어라."},
    "항룡유회": {"hanja": "亢龍有悔", "gua": "#01 중천건 上九", "branch": "branch_yin",
              "stance": "극성 경계 — 과열을 식히고 이룬 이익을 지켜라."},
    "잠룡물용": {"hanja": "潛龍勿用", "gua": "#01 중천건 初九", "branch": "branch_yin",
              "stance": "때를 기다려라 — 실행을 보류하고 내공을 쌓아라."},
}

BRANCH_META = {
    "branch_yang": {
        "label": "양(陽)·공세", "path": "비룡재천 → #14 화천대유", "guas": ["#01 중천건", "#14 화천대유"],
        "conditions": ["체용·계절 점수가 모두 플러스일 것", "핵심 KPI 선행지표 2개 이상 상승 확인",
                       "Tier3 항목은 대표님 수동 결재 후에만 집행"],
        "stop_rule": "진입 후 손실 -7% 또는 핵심 KPI 2회 연속 미달 시 비중 절반 축소, -10%에서 전량 중단",
    },
    "branch_zhong": {
        "label": "중(中)·점진", "path": "#53 풍산점 → #04 산수몽", "guas": ["#53 풍산점", "#04 산수몽"],
        "conditions": ["전체 자원의 20~30%만 파일럿으로 분할 투입", "1주 단위 가설 검증 후 단계적 확대",
                       "검증 로그를 reasoning_chain과 함께 기록"],
        "stop_rule": "손실 -5% 또는 파일럿 KPI 미달 시 확장 중단 · 원인 복기 후 재설계",
    },
    "branch_yin": {
        "label": "음(陰)·방어/정화", "path": "#63 수화기제 → #18 산풍고 → #60 수택절",
        "guas": ["#63 수화기제", "#18 산풍고", "#60 수택절"],
        "conditions": ["신규 확장·신규 진입 금지", "백혈구·배설 기관으로 적폐/누수 정화 우선",
                       "현금·체력·주의력 등 방어선 확보"],
        "stop_rule": "손절선 -3% 고정 · 정화 완료 전 확장 금지 · 이상징후 시 즉시 전면 중단",
    },
}

SHICHEN = [("자", "子", 23, 1), ("축", "丑", 1, 3), ("인", "寅", 3, 5), ("묘", "卯", 5, 7),
           ("진", "辰", 7, 9), ("사", "巳", 9, 11), ("오", "午", 11, 13), ("미", "未", 13, 15),
           ("신", "申", 15, 17), ("유", "酉", 17, 19), ("술", "戌", 19, 21), ("해", "亥", 21, 23)]
SHICHEN_BLOCKS = [
    {"block": "dawn", "label": "조조(早朝) 인·묘·진시", "hours": "03~09시", "branches": ["인", "묘", "진"],
     "guas": ["#03 수뢰둔", "#42 풍뢰익"], "focus": "기획/브리핑",
     "golden_task": "오늘의 본괘→변괘 확인 · 일일 브리핑 갱신 · Tier1 데이터 수집 착수"},
    {"block": "day", "label": "주간(晝間) 사·오시", "hours": "09~13시", "branches": ["사", "오"],
     "guas": ["#14 화천대유", "#30 중화리"], "focus": "통찰/심판",
     "golden_task": "만물통찰안 분석 · 3분기 트리 판정 · Tier3 결재안 대표님 상신"},
    {"block": "afternoon", "label": "오후(午後) 미·신·유시", "hours": "13~19시", "branches": ["미", "신", "유"],
     "guas": ["#50 화풍정", "#58 중택태"], "focus": "주조/창작",
     "golden_task": "Tier2 유튜브 대본·리서치 리포트 초안 주조 · 뮤즈 위임"},
    {"block": "night", "label": "야간(夜間) 술·해·자·축시", "hours": "19~03시", "branches": ["술", "해", "자", "축"],
     "guas": ["#17 택뢰수", "#24 지뢰복"], "focus": "정화/복기/안식",
     "golden_task": "배설 정화 · 백혈구 점검 · 오늘의 계획 복기 후 안식"},
]


def _as_int(v):
    try:
        if isinstance(v, bool) or v is None:
            return None
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            m = re.search(r"\d+", v)
            return int(m.group(0)) if m else None
    except Exception:
        return None
    return None


def _now(dt=None):
    if isinstance(dt, datetime.datetime):
        return dt
    if isinstance(dt, str):
        try:
            return datetime.datetime.fromisoformat(dt)
        except Exception:
            pass
    return datetime.datetime.now()


def _hex_name(n):
    h = HEXAGRAMS[n]
    return "#%02d %s(%s)" % (n, h["ko"], h["hanja"])


def _norm(t):
    return str(t).replace("為", "爲").replace("既", "旣").replace("豊", "豐")


def _short(v, n=220):
    if v is None:
        return ""
    try:
        s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
    except Exception:
        s = str(v)
    s = s.replace("\n", " ").strip()
    return s if len(s) <= n else s[:n] + "…"


def _to_dict(obj):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    for attr in ("to_dict", "as_dict", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                r = fn()
                if isinstance(r, dict):
                    return r
            except Exception:
                pass
    try:
        return dict(vars(obj))
    except Exception:
        return {"raw": str(obj)}


def _gua_display(obj):
    if obj is None or obj == "":
        return ""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, dict):
        ko = obj.get("ko") or obj.get("name_ko") or obj.get("korean") or obj.get("name")
        hj = obj.get("hanja") or obj.get("name_hanja") or obj.get("zh") or obj.get("chinese")
        num = None
        for k in ("number", "no", "num", "index", "id", "king_wen"):
            num = _as_int(obj.get(k))
            if num and 1 <= num <= 64:
                break
            num = None
        label = str(ko) if ko else ""
        if hj and str(hj) != label:
            label = "%s(%s)" % (label, hj) if label else str(hj)
        base = ("#%02d " % num) if num else ""
        out = (base + label).strip()
        return out or _short(obj, 60)
    return str(obj)


def _resolve_num(obj):
    if obj is None:
        return None
    if isinstance(obj, dict):
        for k in ("number", "no", "num", "index", "id", "king_wen", "kw"):
            n = _as_int(obj.get(k))
            if n and 1 <= n <= 64:
                return n
        bits = obj.get("bits") or obj.get("lines")
        if isinstance(bits, (list, tuple)) and len(bits) == 6:
            try:
                t = tuple(1 if int(b) % 2 else 0 for b in bits)
                if t in BITS_TO_NUM:
                    return BITS_TO_NUM[t]
            except Exception:
                pass
        text = " ".join(str(obj.get(k) or "") for k in ("ko", "hanja", "name", "name_ko", "name_hanja", "title"))
    else:
        text = str(obj)
    text = _norm(text)
    m = re.search(r"#\s*(\d{1,2})", text)
    if m and 1 <= int(m.group(1)) <= 64:
        return int(m.group(1))
    for n in sorted(HEXAGRAMS, key=lambda x: -len(HEXAGRAMS[x]["ko"])):
        h = HEXAGRAMS[n]
        if h["ko"] in text or h["hanja"] in text:
            return n
    return None


def _resolve_moving(d):
    if not isinstance(d, dict):
        return None
    for k in ("moving_line", "dong_yao", "dongyao", "changing_line", "moving", "moving_yao", "yao", "動爻", "동효"):
        v = d.get(k)
        if v is None:
            continue
        if isinstance(v, (list, tuple)) and v:
            v = v[0]
        if isinstance(v, dict):
            v = v.get("position") or v.get("line") or v.get("index") or v.get("yao")
        n = _as_int(v)
        if n and 1 <= n <= 6:
            return n
    return None


def _fallback_cast(seed_text, dt):
    raw = ("%s|%s" % (seed_text, dt.strftime("%Y%m%d%H"))).encode("utf-8")
    h = hashlib.sha256(raw).digest()
    return tuple(h[i] & 1 for i in range(6)), (h[6] % 6) + 1


def _flip(bits, pos):
    b = list(bits)
    b[pos - 1] = 1 - b[pos - 1]
    return tuple(b)


def _derive(bits, moving):
    bits = tuple(bits)
    primary = BITS_TO_NUM[bits]
    h = HEXAGRAMS[primary]
    if moving <= 3:
        yong_t, ti_t = h["lower"], h["upper"]
    else:
        ti_t, yong_t = h["lower"], h["upper"]
    return {
        "primary": primary,
        "transformed": BITS_TO_NUM[_flip(bits, moving)],
        "mutual": BITS_TO_NUM[(bits[1], bits[2], bits[3], bits[2], bits[3], bits[4])],
        "complement": BITS_TO_NUM[tuple(1 - b for b in bits)],
        "inverse": BITS_TO_NUM[tuple(reversed(bits))],
        "ti_trigram": ti_t, "yong_trigram": yong_t,
        "ti_elem": TRIGRAM_ELEM[ti_t], "yong_elem": TRIGRAM_ELEM[yong_t],
    }


def _relation(ti, yong):
    if ti == yong:
        return "비화 길"
    if GEN.get(yong) == ti:
        return "용생체 대길"
    if CTRL.get(ti) == yong:
        return "체극용 길"
    if GEN.get(ti) == yong:
        return "체생용 소모"
    return "용극체 흉/주의"


def _bridge(ti, yong, label):
    if label.startswith("용극체"):
        m = GEN[yong]
        why = "용(%s)이 체(%s)를 극하니 %s 기운으로 통관: %s生%s, %s生%s" % (yong, ti, m, yong, m, m, ti)
    elif label.startswith("체극용"):
        m = GEN[ti]
        why = "체(%s)가 용(%s)을 제압하되 소모를 막도록 %s 기운으로 성과를 거둔다" % (ti, yong, m)
    elif label.startswith("체생용"):
        m = GEN_BY[ti]
        why = "체(%s)의 기운이 용(%s)으로 새니 체를 생하는 %s 기운으로 보강한다" % (ti, yong, m)
    elif label.startswith("용생체"):
        m = yong
        why = "용(%s)이 체(%s)를 생하니 흐름을 그대로 타고 %s 기운을 증폭한다" % (yong, ti, m)
    else:
        m = GEN[ti]
        why = "체·용이 같은 %s 기운으로 뭉치니 %s 기운으로 설기하여 성과로 전환한다" % (ti, m)
    return m, why


def _season_state(ti, month):
    s = SEASON_ELEM.get(int(month), "土")
    if s == ti:
        return "旺", s
    if GEN[s] == ti:
        return "相", s
    if GEN[ti] == s:
        return "休", s
    if CTRL[ti] == s:
        return "囚", s
    return "死", s


def _oracle_relation(d):
    if not isinstance(d, dict):
        return None
    for k in ("ti_yong", "tiyong", "ti_yong_relation", "tiyong_relation", "체용", "relation"):
        v = d.get(k)
        if not v:
            continue
        txt = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
        for key, _delta, label in TIYONG_RULES:
            if key in txt:
                return label
    return None


def _oracle_season(d):
    if not isinstance(d, dict):
        return None
    for k in ("season_state", "season", "wangxiang", "wang_xiang", "seasonal", "seasonal_state", "왕상휴수사"):
        v = d.get(k)
        if not v:
            continue
        txt = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
        for ch in ("旺", "相", "休", "囚", "死"):
            if ch in txt:
                return ch
    return None


def _oracle_text(d):
    if not isinstance(d, dict):
        return ""
    for k in ("aon_speech", "advice", "judgment", "guaci", "meaning", "message", "summary", "interpretation", "oracle", "reading_text"):
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return _short(v, 160)
    return ""


def _call_oracle(q):
    try:
        mod = importlib.import_module("rgon_aon_iching_dao_oracle")
    except Exception as e:
        return None, "oracle import 실패: %r" % (e,)
    try:
        if q:
            fn = getattr(mod, "cast_by_question", None)
            if not callable(fn):
                return None, "cast_by_question 미정의"
            try:
                r = fn(q)
            except TypeError:
                r = fn(question=q)
        else:
            fn = getattr(mod, "cast_by_telemetry", None)
            if callable(fn):
                r = fn()
            else:
                fn = getattr(mod, "cast_by_question", None)
                if not callable(fn):
                    return None, "cast_by_telemetry/cast_by_question 미정의"
                r = fn(DEFAULT_GOAL)
        d = _to_dict(r)
        if isinstance(d, dict) and not (d.get("bengua") or d.get("primary")):
            for k in ("result", "reading", "cast", "data", "oracle", "hexagram"):
                inner = d.get(k)
                if isinstance(inner, dict) and (inner.get("bengua") or inner.get("primary")):
                    d = inner
                    break
        return d, None
    except Exception as e:
        return None, "oracle 호출 실패: %r" % (e,)


def _find_layer(d, tag, depth=0):
    if depth > 3 or d is None:
        return None
    t = tag.lower()
    if isinstance(d, dict):
        for k, v in d.items():
            ks = str(k).lower()
            if ks == t or ks.startswith(t + "_") or ks.startswith(t + " ") or ks == "layer" + t[1:]:
                return v
        for k, v in d.items():
            if isinstance(v, dict) and str(v.get("layer", "")).lower() == t:
                return v
            r = _find_layer(v, tag, depth + 1) if isinstance(v, (dict, list)) else None
            if r is not None:
                return r
    elif isinstance(d, list):
        for it in d:
            if isinstance(it, dict) and str(it.get("layer", it.get("id", ""))).lower() == t:
                return it
        for it in d:
            r = _find_layer(it, tag, depth + 1) if isinstance(it, (dict, list)) else None
            if r is not None:
                return r
    return None


def _call_omni(q):
    try:
        mod = importlib.import_module("rgon_aon_omni_insight_eye")
        fn = getattr(mod, "analyze_omni_insight", None)
        if not callable(fn):
            return {"ok": False, "error": "analyze_omni_insight 미정의"}
        try:
            r = fn(q or DEFAULT_GOAL)
        except TypeError:
            r = fn(query=q or DEFAULT_GOAL)
        d = _to_dict(r) or {}
        return {"ok": True, "L2": _short(_find_layer(d, "L2")), "L4": _short(_find_layer(d, "L4")),
                "summary": _short(d.get("summary") or d.get("verdict") or d.get("insight") or d.get("aon_speech") or ""),
                "keys": [str(k) for k in list(d.keys())[:20]]}
    except Exception as e:
        return {"ok": False, "error": "omni 호출 실패: %r" % (e,)}


def _line_factors(bits, moving):
    p = moving
    v = bits[p - 1]
    yy = "양" if v else "음"
    out = []
    zhong = p in (2, 5)
    out.append({"factor": "득중(得中)", "delta": 5 if zhong else 0,
                "reason": "동효 %d효(%s)가 %s" % (p, yy, "중위(2·5효)를 얻음" if zhong else "중위가 아님")})
    dang = (p % 2 == 1 and v == 1) or (p % 2 == 0 and v == 0)
    out.append({"factor": "당위(當位)", "delta": 4 if dang else -3,
                "reason": "%d효 %s효가 %s" % (p, yy, "제자리(정위)에 있음" if dang else "자리를 잃음(실위)")})
    q = p + 3 if p <= 3 else p - 3
    ying = bits[q - 1] != v
    out.append({"factor": "상응(相應)", "delta": 3 if ying else -2,
                "reason": "%d효와 %d효가 %s" % (p, q, "음양으로 호응" if ying else "같은 성질로 무응(無應)")})
    if bits[1] == 0 and bits[4] == 1:
        out.append({"factor": "이오중정상응(二五中正相應)", "delta": 4,
                    "reason": "2효 음·5효 양이 모두 중정하고 서로 호응 — 군신 화합의 상"})
    return out


def _select_posture(score, moving):
    if moving == 6 and score >= 70:
        return "항룡유회"
    if score >= 80:
        return "비룡재천"
    if score >= 70:
        return "지천태·수화기제"
    if score >= 58:
        return "몽이양정"
    if score >= 45:
        return "산풍고·뇌수해"
    return "잠룡물용"


def _three_branch_tree(score, rec_branch, ti_label, bridge_elem):
    s = score / 100.0
    q = {"branch_yang": 2 * s - 1.0, "branch_zhong": 0.55 - abs(s - 0.62) * 1.5, "branch_yin": 0.9 - 1.6 * s}
    if ti_label.startswith("용극체") or ti_label.startswith("체생용"):
        q["branch_yang"] -= 0.15
        q["branch_yin"] += 0.10
    priors = {b: (0.5 if b == rec_branch else 0.25) for b in q}
    visits = {b: int(round(priors[b] * 64 * (1 + max(q[b], -0.9)))) + 1 for b in q}
    n_total = sum(visits.values())
    ucb = {b: q[b] + 1.25 * priors[b] * math.sqrt(n_total) / (1 + visits[b]) for b in q}
    ex = {b: math.exp(3.0 * ucb[b]) for b in q}
    z = sum(ex.values()) or 1.0
    shares = {b: int(round(100 * ex[b] / z)) for b in q}
    diff = 100 - sum(shares.values())
    shares[rec_branch] += diff
    tree = {}
    for b in ("branch_yang", "branch_zhong", "branch_yin"):
        meta = BRANCH_META[b]
        tree[b] = {
            "label": meta["label"], "path": meta["path"], "guas": list(meta["guas"]),
            "expected_utility": round(q[b] * 100, 1), "prior": priors[b], "visits": visits[b],
            "ucb": round(ucb[b], 4), "recommended_share_pct": shares[b],
            "execution_conditions": list(meta["conditions"]), "stop_rule": meta["stop_rule"],
            "bridge_element": bridge_elem, "is_recommended": b == rec_branch,
        }
    best_ucb = max(ucb, key=lambda b: ucb[b])
    tree["mcts_meta"] = {"algorithm": "LightZero-style PUCT (deterministic simulated visits)",
                         "c_puct": 1.25, "total_visits": n_total, "best_by_ucb": best_ucb,
                         "selection_rule": "시중(時中) 원칙: posture 분기 우선, UCB는 감사 참고치"}
    return tree


def _action_items(goal, posture, rec_branch, bengua, biangua, bridge_elem, stop_rule):
    return [
        {"tier": 1, "label": "Tier 1 (즉시 자율 실행)", "title": "데이터 수집·백혈구/배설 점검·브리핑 갱신",
         "tasks": ["'%s' 관련 텔레메트리·시장 데이터 수집" % goal,
                   "rgon_white_blood_cell 무결성 점검 · rgon_excretory_organ 배설 정화 점검",
                   "일일 브리핑에 %s → %s · 시중처세 '%s' 반영" % (bengua, biangua, posture)],
         "organs": ["rgon_daily_cycle.py", "rgon_white_blood_cell.py", "rgon_excretory_organ.py"],
         "auto_executable": True, "requires_manual_gate": False, "auto_executed": False,
         "status": "즉시 자율 실행 가능 (기획관은 계획만 수립)"},
        {"tier": 2, "label": "Tier 2 (초안 생성 대기)", "title": "유튜브 크리에이터 대본 초안·리서치 리포트 작성",
         "tasks": ["'%s' 주제 유튜브 대본 초안 (훅: %s의 괘상, 결론: %s)" % (goal, bengua, biangua),
                   "리서치 리포트 초안 — 추천 분기 %s · 통관 오행 %s(%s)" % (BRANCH_META[rec_branch]["label"], bridge_elem, ELEM_ACTION.get(bridge_elem, ""))],
         "organs": ["rgon_muse_delegator.py", "rgon_aon_soul_brain.py"],
         "auto_executable": False, "draft_only": True, "requires_manual_gate": False, "auto_executed": False,
         "status": "초안 생성 대기"},
        {"tier": 3, "label": "Tier 3 (대표님 수동 결재 대기)", "title": "금융·실매매·파일삭제·외부배포 결재안",
         "tasks": ["실매매/자금 배분은 추천 분기 비중표를 참고한 결재안만 상신",
                   "파일삭제·외부배포는 변경 목록과 롤백 계획을 첨부하여 상신",
                   "Stop Rule: %s" % stop_rule],
         "gate_scope": ["금융", "실매매", "파일삭제", "외부배포"],
         "constitution": "헌법 제2항 · R35 · R41",
         "auto_executable": False, "requires_manual_gate": True, "auto_executed": False,
         "status": "대표님 수동 결재 대기"},
    ]


def shichen_schedule(dt=None):
    dt = _now(dt)
    h = dt.hour
    idx = ((h + 1) // 2) % 12
    ko, hj, start, end = SHICHEN[idx]
    active_block = None
    for b in SHICHEN_BLOCKS:
        if ko in b["branches"]:
            active_block = b
            break
    return {
        "now": dt.strftime("%Y-%m-%d %H:%M"),
        "active_shichen": "%s시(%s時) %02d~%02d시" % (ko, hj, start, end),
        "active_branch": ko,
        "active_block": active_block["block"] if active_block else None,
        "active_block_label": active_block["label"] if active_block else None,
        "golden_task": active_block["golden_task"] if active_block else "",
        "blocks": [dict(b, active=(b is active_block)) for b in SHICHEN_BLOCKS],
        "shichen_table": [{"branch": s[0], "hanja": s[1], "hours": "%02d~%02d" % (s[2], s[3])} for s in SHICHEN],
    }


def _state_paths():
    d = os.environ.get("RGON_ICHING_STATE_DIR") or os.environ.get("RGON_DIALOGUE_STATE_DIR")
    base = os.path.abspath(d) if d else ROOT
    return [os.path.join(base, STATE_NAME), os.path.join(base, "docs", STATE_NAME)]


def _persist(plan):
    written = []
    for path in _state_paths():
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2, default=str)
            os.replace(tmp, path)
            written.append(path)
        except Exception:
            pass
    return written


def format_plan_reply(p):
    w = p.get("woop_ooda", {})
    post = p.get("posture", {})
    tree = p.get("three_branch_tree", {})
    rec = p.get("recommended_branch")
    lines = [
        "[주역 전략 기획관 · 본괘→변괘 · 시중처세 · 3대 실행안] %s" % VERSION,
        "■ 주제: %s" % p.get("goal"),
        "■ 본괘→변괘: %s → %s (동효 %s효) · 호괘 %s · 착괘 %s · 종괘 %s" % (
            p.get("bengua_name"), p.get("biangua_name"), p.get("moving_line"),
            p.get("hugua_name"), p.get("cuogua_name"), p.get("zonggua_name")),
        "■ 시중처세: %s(%s) — %s" % (post.get("name"), post.get("hanja"), post.get("stance")),
        "■ 전략추진지수: %s/100 · 신뢰도 %s%% (상한 85%%) · 체용 %s · 계절 %s" % (
            p.get("strategy_score"), p.get("confidence_pct"), p.get("ti_yong_relation"), p.get("season_state")),
        "■ WOOP·OODA",
        "  · 관찰(본괘): %s" % w.get("observe_present", {}).get("diagnosis", ""),
        "  · 복병(호괘): %s" % w.get("obstacle_hidden", {}).get("diagnosis", ""),
        "  · 목표(변괘): %s" % w.get("outcome_target", {}).get("diagnosis", ""),
        "  · 플랜B(착괘): %s" % w.get("plan_b_complement", {}).get("diagnosis", ""),
        "  · 시장시선(종괘): %s" % w.get("market_view_inverse", {}).get("diagnosis", ""),
        "  · 통관비책: %s" % w.get("bridge_prescription", {}).get("diagnosis", ""),
        "■ 추천 분기: %s (%s) · 권장 비중 %s%%" % (
            tree.get(rec, {}).get("label"), tree.get(rec, {}).get("path"), tree.get(rec, {}).get("recommended_share_pct")),
        "■ 3대 실행안",
    ]
    for a in p.get("action_items", []):
        gate = " [수동결재 게이트 · 자동실행 없음]" if a.get("requires_manual_gate") else ""
        lines.append("  %s %s — %s%s" % (a.get("label"), a.get("title"), a.get("status"), gate))
    sc = p.get("shichen_schedule", {})
    lines.append("■ 시진: 현재 %s · %s — 골든타임: %s" % (sc.get("active_shichen"), sc.get("active_block_label"), sc.get("golden_task")))
    lines.append("■ Stop Rule: %s" % p.get("stop_rule"))
    return "\n".join(lines)


def build_strategic_plan(goal_or_query="", dt=None, persist=True):
    dt = _now(dt)
    q = goal_or_query if isinstance(goal_or_query, str) else str(goal_or_query or "")
    q = q.strip()
    goal = q or DEFAULT_GOAL
    oracle, oracle_err = _call_oracle(q)
    o = oracle if isinstance(oracle, dict) else {}
    omni = _call_omni(goal)
    fb_bits, fb_moving = _fallback_cast(q or "telemetry", dt)

    p_obj = o.get("bengua") or o.get("primary")
    t_obj = o.get("biangua") or o.get("transformed")
    m_obj = o.get("hugua") or o.get("mutual")
    c_obj = o.get("cuogua") or o.get("complement")
    i_obj = o.get("zonggua") or o.get("inverse")

    pnum = _resolve_num(p_obj) if p_obj is not None else None
    source = "oracle" if pnum else ("oracle-partial" if o else "fallback")
    bits = HEXAGRAMS[pnum]["bits"] if pnum else fb_bits
    moving = _resolve_moving(o)
    if not moving and pnum and t_obj is not None:
        tnum = _resolve_num(t_obj)
        if tnum:
            diff = [i + 1 for i in range(6) if HEXAGRAMS[tnum]["bits"][i] != bits[i]]
            if diff:
                moving = diff[0]
    if not moving:
        moving = fb_moving
    der = _derive(bits, moving)

    bengua = _gua_display(p_obj) or _hex_name(der["primary"])
    biangua = _gua_display(t_obj) or _hex_name(der["transformed"])
    hugua = _gua_display(m_obj) or _hex_name(der["mutual"])
    cuogua = _gua_display(c_obj) or _hex_name(der["complement"])
    zonggua = _gua_display(i_obj) or _hex_name(der["inverse"])

    ti, yong = der["ti_elem"], der["yong_elem"]
    rel = _oracle_relation(o) or _relation(ti, yong)
    season, season_elem = _season_state(ti, dt.month)
    season = _oracle_season(o) or season
    bridge_elem, bridge_why = _bridge(ti, yong, rel)

    chain = [{"factor": "기본점", "delta": 60, "reason": "전략 추진 지수 기준선"}]
    rel_delta = dict((lbl, d) for _k, d, lbl in TIYONG_RULES).get(rel, 0)
    chain.append({"factor": "체용 생극", "delta": rel_delta,
                  "reason": "체(%s·%s) / 용(%s·%s) → %s" % (TRIGRAM_KO[der["ti_trigram"]], ti, TRIGRAM_KO[der["yong_trigram"]], yong, rel)})
    chain.append({"factor": "계절 왕상휴수사", "delta": SEASON_DELTA.get(season, 0),
                  "reason": "%d월 월령 %s 기준 체괘 %s 기운은 %s" % (dt.month, season_elem, ti, season)})
    chain.extend(_line_factors(bits, moving))
    if not omni.get("ok"):
        chain.append({"factor": "만물통찰안 연동", "delta": 0, "reason": "통찰안 미연동 — 가감 없음 (%s)" % omni.get("error", "")})
    else:
        chain.append({"factor": "만물통찰안 연동", "delta": 0, "reason": "L2/L4 복병 신호를 호괘 진단에 결합"})
    score_raw = sum(c["delta"] for c in chain)
    score = max(0, min(100, score_raw))
    confidence = round(min(CONFIDENCE_CAP, 40.0 + score * 0.5), 1)
    posture_name = _select_posture(score, moving)
    post = POSTURES[posture_name]
    rec = post["branch"]
    stop_rule = BRANCH_META[rec]["stop_rule"]
    ph = HEXAGRAMS[der["primary"]]
    woop = {
        "observe_present": {"gua": bengua, "diagnosis": "%s — 상괘 %s 하괘 %s의 국면. %s" % (
            bengua, TRIGRAM_IMAGE[ph["upper"]], TRIGRAM_IMAGE[ph["lower"]], _oracle_text(o) or post["stance"])},
        "obstacle_hidden": {"gua": hugua, "omni_L2": omni.get("L2", ""), "omni_L4": omni.get("L4", ""),
                            "diagnosis": "%s 속에 숨은 복병 — 중간 국면의 내면 변수를 경계. %s" % (
                                hugua, (omni.get("L2") or omni.get("L4") or "")[:120])},
        "outcome_target": {"gua": biangua, "diagnosis": "동효 %d효가 변하여 %s 상태에 도달하는 것을 최종 목표로 삼는다" % (moving, biangua)},
        "plan_b_complement": {"gua": cuogua, "diagnosis": "음양 전도 %s — 본 계획이 막히면 정반대 역발상 경로로 전환" % cuogua},
        "market_view_inverse": {"gua": zonggua, "diagnosis": "%s — 상대·시장 입장에서 본 반응을 선제 대응" % zonggua},
        "bridge_prescription": {"ti_yong": rel, "bridge_element": bridge_elem, "stop_rule": stop_rule,
                                "diagnosis": "%s · 통관 %s: %s · Stop Rule: %s" % (
                                    bridge_why, bridge_elem, ELEM_ACTION.get(bridge_elem, ""), stop_rule)},
    }
    plan = {
        "ok": True, "version": VERSION, "antibody": ANTIBODY_RANGE, "skill_count": SKILL_COUNT,
        "skill_id": SKILL_ID, "organ": ORGAN_NAME,
        "generated_at": dt.isoformat(timespec="seconds"), "goal": goal, "source": source,
        "oracle_error": oracle_err,
        "bengua_name": bengua, "biangua_name": biangua, "hugua_name": hugua,
        "cuogua_name": cuogua, "zonggua_name": zonggua, "moving_line": moving,
        "primary": der["primary"], "transformed": der["transformed"], "mutual": der["mutual"],
        "complement": der["complement"], "inverse": der["inverse"],
        "ti_yong": {"ti": ti, "yong": yong, "ti_trigram": der["ti_trigram"], "yong_trigram": der["yong_trigram"],
                    "relation": rel, "bridge_element": bridge_elem},
        "ti_yong_relation": rel, "season_state": season,
        "woop_ooda": woop, "reasoning_chain": chain,
        "strategy_score": score, "confidence_pct": confidence, "confidence_cap": CONFIDENCE_CAP,
        "posture": {"name": posture_name, "hanja": post["hanja"], "gua": post["gua"], "stance": post["stance"]},
        "recommended_branch": rec,
        "three_branch_tree": _three_branch_tree(score, rec, rel, bridge_elem),
        "stop_rule": stop_rule,
        "shichen_schedule": shichen_schedule(dt),
        "omni_insight": omni,
        "manual_gate_policy": "Tier3(금융·실매매·파일삭제·외부배포)는 requires_manual_gate=True, auto_executed=False",
    }
    plan["action_items"] = _action_items(goal, posture_name, rec, bengua, biangua, bridge_elem, stop_rule)
    plan["reply"] = format_plan_reply(plan)
    if persist:
        plan["state_files"] = _persist(plan)
    return plan


def daily_plan(dt=None, persist=True):
    return build_strategic_plan("", dt=dt, persist=persist)


def status():
    for path in _state_paths():
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                return {"ok": True, "version": VERSION, "state_file": path, "goal": d.get("goal"),
                        "bengua_name": d.get("bengua_name"), "biangua_name": d.get("biangua_name"),
                        "strategy_score": d.get("strategy_score"), "posture": d.get("posture", {}).get("name"),
                        "generated_at": d.get("generated_at")}
            except Exception as e:
                return {"ok": False, "version": VERSION, "error": repr(e)}
    return {"ok": True, "version": VERSION, "state_file": None, "note": "아직 저장된 계획 없음"}


def self_test():
    checks = []
    tmp = tempfile.mkdtemp(prefix="rgon_iching_st_")
    old = os.environ.get("RGON_ICHING_STATE_DIR")
    os.environ["RGON_ICHING_STATE_DIR"] = tmp
    try:
        checks.append(("64괘 테이블", len(HEXAGRAMS) == 64 and len(BITS_TO_NUM) == 64))
        p = build_strategic_plan("반도체 투자와 유튜브 성장 전략", dt=datetime.datetime(2026, 10, 25, 10, 0))
        checks.append(("계획 ok", p.get("ok") is True and bool(p.get("bengua_name"))))
        checks.append(("WOOP 6요소", all(k in p["woop_ooda"] for k in (
            "observe_present", "obstacle_hidden", "outcome_target", "plan_b_complement",
            "market_view_inverse", "bridge_prescription"))))
        checks.append(("점수 범위", 0 <= p["strategy_score"] <= 100 and p["confidence_pct"] <= 85.0))
        checks.append(("reasoning_chain 합산", max(0, min(100, sum(c["delta"] for c in p["reasoning_chain"]))) == p["strategy_score"]))
        checks.append(("3분기 트리", all(b in p["three_branch_tree"] for b in ("branch_yang", "branch_zhong", "branch_yin"))))
        checks.append(("추천 분기", p["recommended_branch"] in p["three_branch_tree"]))
        t3 = [a for a in p["action_items"] if a["tier"] == 3]
        checks.append(("Tier3 수동게이트", len(p["action_items"]) == 3 and bool(t3) and t3[0]["requires_manual_gate"] is True and t3[0]["auto_executed"] is False))
        checks.append(("자동실행 0건", all(a.get("auto_executed") is False for a in p["action_items"])))
        checks.append(("시진", shichen_schedule(datetime.datetime(2026, 1, 1, 4))["active_block"] == "dawn"
                       and shichen_schedule(datetime.datetime(2026, 1, 1, 0))["active_block"] == "night"
                       and shichen_schedule(datetime.datetime(2026, 1, 1, 10))["active_block"] == "day"
                       and shichen_schedule(datetime.datetime(2026, 1, 1, 15))["active_block"] == "afternoon"))
        checks.append(("상태파일 격리", os.path.exists(os.path.join(tmp, STATE_NAME))))
        d = daily_plan(persist=False)
        checks.append(("일일계획", d.get("ok") is True))
        checks.append(("응답 포맷", "[주역 전략 기획관" in p["reply"]))
    except Exception as e:
        checks.append(("예외 없음", False))
        checks.append(("trace", repr(e)))
    finally:
        if old is None:
            os.environ.pop("RGON_ICHING_STATE_DIR", None)
        else:
            os.environ["RGON_ICHING_STATE_DIR"] = old
        shutil.rmtree(tmp, ignore_errors=True)
    passed = sum(1 for _n, v in checks if v is True)
    total = sum(1 for _n, v in checks if isinstance(v, bool))
    return {"ok": passed == total, "version": VERSION, "passed": passed, "total": total,
            "checks": [{"name": n, "ok": v} for n, v in checks]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=ORGAN_NAME)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--plan", nargs="*")
    ap.add_argument("--daily", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        r = self_test()
        print(json.dumps(r, ensure_ascii=False, indent=2))
        print("SELF-TEST %s %d/%d" % ("PASS" if r["ok"] else "FAIL", r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    if a.plan is not None or a.daily:
        p = build_strategic_plan(" ".join(a.plan or []) if a.plan is not None else "")
        print(json.dumps(p, ensure_ascii=False, indent=2, default=str) if a.json else p["reply"])
        return 0
    print(json.dumps(status(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
