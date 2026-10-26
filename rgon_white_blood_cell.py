# -*- coding: utf-8 -*-
"""
rgon_white_blood_cell.py
RGON 백혈구(WBC: White Blood Cell) 자가치유 면역 엔진 (v11.51-AON-COMMANDER-TWIN / 항체 R18)

6대 면역 기능:
  1. fingerprint(exc, context) : 오류 지문 채취 & 동일 지문 3회 이상 반복 경보 억제
  2. patrol(root_dir)          : Python AST / JSON / HTML 마커 무결성 순찰 & 0~100 건강 점수
  3. auto_restore(file_path)   : 손상 파일 격리 후 가장 최근 정상 백업본으로 자동 복원
  4. run_safely / shield / adapt_dict : 상선약수(上善若水) 우회 실행 (프로세스 중단 방지)
  5. link_hexagram()           : rgon_hexagram_engine.py 연동 (점검 강화 모드 판단)
  6. CLI                       : --patrol / --status / --heal <file> / --self-test
"""
from __future__ import annotations

import argparse
import ast
import datetime
import functools
import hashlib
import importlib.util
import json
import os
import py_compile
import re
import shutil
import sys
import traceback

WBC_VERSION = "v11.51-AON-COMMANDER-TWIN"
ANTIBODY_RANGE = "R1~R52"
LEDGER_FILENAME = "rgon_immune_ledger.json"
HEXAGRAM_FILENAME = "rgon_hexagram_engine.py"
PRINCIPLE = "만물은 하나로 이어져 있으며, 한 걸음씩 나아가면 반드시 이루어진다."

PROTECTED_EXTS = (".html", ".js")
PROTECTED_NAMES = ("manifest.json",)
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".rgon_backup", ".rgon_backups", ".idea", ".vscode", "backups", "archive", "old_backups",
}

CAUTION_HEX_NUMBERS = {6, 12, 23, 29, 36, 39, 47}
CAUTION_KEYWORDS = ("송", "비", "박", "감", "명이", "蹇", "곤", "험", "경계", "주의", "신중", "점검")

DEFAULT_ANTIBODIES = [
    {"id": "R1",  "title": "단일 진실 공급원(SSOT) 준수 및 중복 상태 금지", "step": 1},
    {"id": "R2",  "title": "전 영역 UTF-8 입출력 명시 (Windows cp949 인코딩 오류 면역)", "step": 2},
    {"id": "R3",  "title": "작업 전 타임스탬프 백업 강제 및 원본 보존", "step": 3},
    {"id": "R4",  "title": "마커 기반 멱등(Idempotent) 패치로 재실행 안전 보장", "step": 4},
    {"id": "R5",  "title": "외부 네트워크·서브프로세스 타임아웃 및 안전 기본값", "step": 5},
    {"id": "R6",  "title": "로컬 브리지(8765) 오프라인 시 정적 폴백 동작 보장", "step": 6},
    {"id": "R7",  "title": "모바일·데스크톱 아코디언 바 겹침 방지 및 접힘 기본값", "step": 7},
    {"id": "R8",  "title": "실시간 브리핑 바 독립 데이터 경로 유지 및 잔상 차단", "step": 8},
    {"id": "R9",  "title": "단일 클린 엔진 통합 및 구 패치 블록 정리", "step": 9},
    {"id": "R10", "title": "실제 실행 경로(Downloads\\shin-agent) 자동 탐색 및 동기화", "step": 10},
    {"id": "R11", "title": "Shadow DOM open 전환 및 흡수기 4버튼 정밀 타겟팅", "step": 11},
    {"id": "R12", "title": "흡수기 버튼 단일 배지(V12) 정리 및 중복 렌더링 차단", "step": 12},
    {"id": "R13", "title": "유튜브 트렌드 & AI 스킬 흡수기 V13 정적 JSON 폴백 연동", "step": 13},
    {"id": "R14", "title": "MutationObserver·setInterval DOM 재배치 루프 영구 금지", "step": 14},
    {"id": "R15", "title": "단발성 placeOnce(data-placed=1) 정적 배치 원칙", "step": 15},
    {"id": "R16", "title": "카파시 4대 원칙(CLAUDE.md) + CODE_MAP.md + 보호 파일 해시 잠금", "step": 16},
    {"id": "R17", "title": "창립자 만물일체·한걸음씩 철학 + 명심보감·도덕경·주역 64괘 엔진", "step": 17},
    {"id": "R18", "title": "백혈구(WBC) 자가치유 면역 엔진 — 오류 지문·AST/JSON 순찰·백업 복원·상선약수 우회·중복 경보 억제", "step": 18},
    {"id": "R19", "title": "Top 100 영양분 3스푼(Markdown 정제기 · 표준 SKILL.md 자동 주조기 · 3자 찬반 심판기) 통합 및 지식 자가 증식", "step": 19},
    {"id": "R28", "step": 28, "title": "아온(A-ON) K-아이 성장형 디지털 육신", "name": "아온(A-ON) 성장형 디지털 육신", "rule": "R28: 미래형 K-스타일 성장형 디지털 육신 아온(A-ON·芽溫, 산수몽 #04·풍산점 #53·지천태 #11) — 순수 CSS 애니메이션으로 루프 없이 생동감을 구현하고 시스템 진화에 맞춰 4단계로 점진 성장", "status": "active"},
    {"id": "R29", "step": 29, "title": "캐릭터 디테일 TOP 1 마스터 & 아온(A-ON) 3D 물방울 졸라맨 육신", "name": "아온(A-ON) 3D 물방울 졸라맨 육신", "rule": "R29: 캐릭터 디테일 TOP 1 스킬 마스터 & 아온(A-ON·芽溫) 3D 물방울 졸라맨 육신 — 디즈니 7대 모션 법칙(스쿼시&스트레치·시차·팔로스루) + 8-Stop 3D Liquid-Glass/Claymorphism 입체 필터 + 관절형 졸라맨 팔다리 통합", "status": "active"},
    {"id": "R31", "step": 31, "title": "배설기관(신장·대장) 노폐물 배출 & 엔트로피 정화 엔진", "name": "배설기관 엔트로피 정화", "rule": "R31: 배설기관(신장·대장·뇌척수액 정화, 주역 #18 산풍고·#40 뇌수해) — ECC config-gc + reclaim-code-entropy + autoDream 기반으로 캐시·구백업·중복 마커·컨텍스트 찌꺼기를 안전 배출하여 엔트로피 0% 유지", "status": "active"},
    {"id": "R32", "step": 31, "title": "배설기관(신장·대장) 노폐물 배출 & 엔트로피 정화 엔진", "name": "배설기관 엔트로피 정화", "rule": "R32: 메타 뮤즈(Muse) 3대 대행 기관 — 비동기 위임 작업큐(Muse Wonder) · 3등급 안전 승인 게이트(HITL) · 아온 다이내믹 아일랜드(Muse Charm) 통합", "status": "active"},
]
def _kst_now():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    ).replace(tzinfo=None)


def _now_iso():
    return _kst_now().isoformat(timespec="seconds")


def _console_utf8():
    for name in ("stdout", "stderr"):
        st = getattr(sys, name, None)
        if st is not None and hasattr(st, "reconfigure"):
            try:
                st.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def resolve_root(root_dir=None):
    if root_dir and os.path.isdir(root_dir):
        return os.path.abspath(root_dir)
    try:
        here = os.path.abspath(os.path.dirname(__file__))
        if os.path.isdir(here):
            return here
    except Exception:
        pass
    for cand in (
        r"C:\Users\sangi\Downloads\shin-agent",
        r"C:\Users\user\shin-agent",
        os.getcwd(),
    ):
        if cand and os.path.isdir(cand):
            return os.path.abspath(cand)
    return os.path.abspath(os.getcwd())


def is_protected_file(path):
    base = os.path.basename(path).lower()
    if base in PROTECTED_NAMES:
        return True
    return any(base.endswith(ext) for ext in PROTECTED_EXTS)


def _rel(path, root):
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except Exception:
        return path.replace("\\", "/")


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


# =====================================================================
# 면역 원장 (rgon_immune_ledger.json)
# =====================================================================
def ledger_path(root_dir=None):
    return os.path.join(resolve_root(root_dir), LEDGER_FILENAME)


def _default_ledger():
    return {
        "schema": "rgon.immune.ledger.v1",
        "version": WBC_VERSION,
        "current_step": 18,
        "antibody_range": ANTIBODY_RANGE,
        "principle": PRINCIPLE,
        "updated_at_kst": _now_iso(),
        "health_score": 100,
        "inspection_mode": "standard",
        "today_hexagram": {},
        "suppressed_count": 0,
        "antibodies": list(DEFAULT_ANTIBODIES),
        "fingerprints": {},
        "healed_events": [],
        "bypass_log": [],
        "patrol_history": [],
    }


def load_ledger(root_dir=None):
    path = ledger_path(root_dir)
    base = _default_ledger()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                base.update(loaded)
        except Exception:
            pass
    existing = {}
    for item in base.get("antibodies", []):
        if isinstance(item, dict) and item.get("id"):
            existing[item["id"]] = item
    for ab in DEFAULT_ANTIBODIES:
        merged = dict(ab)
        prev = existing.get(ab["id"])
        if isinstance(prev, dict):
            merged.update(prev)
        merged["title"] = (ab.get("title") or ab.get("name") or ab.get("rule") or ab.get("id", ""))
        merged["step"] = ab.get("step", 27)
        existing[ab["id"]] = merged
    def _ab_key(k):
        m = re.search(r"(\d+)", str(k))
        return int(m.group(1)) if m else 999
    base["antibodies"] = [existing[k] for k in sorted(existing.keys(), key=_ab_key)]
    base["version"] = WBC_VERSION
    base["current_step"] = max(int(base.get("current_step") or 18), 18)
    base["antibody_range"] = ANTIBODY_RANGE
    base["principle"] = PRINCIPLE
    if not isinstance(base.get("fingerprints"), dict):
        base["fingerprints"] = {}
    if not isinstance(base.get("healed_events"), list):
        base["healed_events"] = []
    if not isinstance(base.get("bypass_log"), list):
        base["bypass_log"] = []
    if not isinstance(base.get("patrol_history"), list):
        base["patrol_history"] = []
    return base


def save_ledger(ledger, root_dir=None):
    root = resolve_root(root_dir)
    path = ledger_path(root)
    ledger["version"] = WBC_VERSION
    ledger["antibody_range"] = ANTIBODY_RANGE
    ledger["updated_at_kst"] = _now_iso()
    ledger["healed_events"] = ledger.get("healed_events", [])[-120:]
    ledger["bypass_log"] = ledger.get("bypass_log", [])[-120:]
    ledger["patrol_history"] = ledger.get("patrol_history", [])[-40:]
    text = json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    json.loads(text)
    tmp = path + ".wbc_tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)
    return path


# =====================================================================
# 1. 오류 지문 채취 (Fingerprint) & 3회 이상 반복 경보 억제
# =====================================================================
def compute_fingerprint(exc, context="", tb_str=""):
    exc_type = type(exc).__name__ if isinstance(exc, BaseException) else str(exc)
    msg = str(exc) if exc is not None else ""
    norm_msg = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", msg)
    norm_msg = re.sub(r"\d+", "N", norm_msg)[:160]
    top_loc = ""
    if tb_str:
        lines = [ln.strip() for ln in tb_str.splitlines() if "File " in ln]
        if lines:
            top_loc = re.sub(r"line \d+", "line L", lines[-1])[:160]
    raw = "%s|%s|%s|%s" % (exc_type, context, top_loc, norm_msg)
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


def fingerprint(exc, context="runtime", root_dir=None, threshold=3):
    root = resolve_root(root_dir)
    tb_str = ""
    try:
        if isinstance(exc, BaseException) and exc.__traceback__ is not None:
            tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        else:
            tb_str = traceback.format_exc()
    except Exception:
        tb_str = ""
    fp = compute_fingerprint(exc, context=context, tb_str=tb_str)
    ledger = load_ledger(root)
    fps = ledger.setdefault("fingerprints", {})
    rec = fps.get(fp) or {
        "fingerprint": fp,
        "exc_type": type(exc).__name__ if isinstance(exc, BaseException) else "Error",
        "context": str(context),
        "sample_message": str(exc)[:240],
        "first_seen_kst": _now_iso(),
        "last_seen_kst": _now_iso(),
        "count": 0,
        "suppressed": False,
        "known_remedy": _suggest_remedy(exc),
    }
    rec["count"] = int(rec.get("count", 0)) + 1
    rec["last_seen_kst"] = _now_iso()
    rec["sample_message"] = str(exc)[:240]
    suppressed = rec["count"] >= int(threshold)
    rec["suppressed"] = suppressed
    if suppressed:
        ledger["suppressed_count"] = int(ledger.get("suppressed_count", 0)) + 1
    fps[fp] = rec
    try:
        save_ledger(ledger, root)
    except Exception:
        pass
    return {
        "fingerprint": fp,
        "count": rec["count"],
        "suppressed": suppressed,
        "should_alert": not suppressed,
        "remedy": rec.get("known_remedy", ""),
    }


def _suggest_remedy(exc):
    name = type(exc).__name__ if isinstance(exc, BaseException) else str(exc)
    table = {
        "UnicodeDecodeError": "R2 항체: open(..., encoding='utf-8', errors='replace') 적용",
        "UnicodeEncodeError": "R2 항체: 콘솔 UTF-8 재설정 및 utf-8 인코딩 명시",
        "JSONDecodeError": "R18 항체: 손상 JSON 백업 복원(auto_restore) 또는 안전 기본값 우회",
        "SyntaxError": "R18 항체: 최근 정상 스냅샷/백업에서 자동 복원(auto_restore)",
        "FileNotFoundError": "R10/R18 항체: 경로 자동 탐색(resolve_root) 또는 기본 파일 생성",
        "KeyError": "R18 상선약수: adapt_dict 안전 키 매핑 및 기본값 반환",
        "TimeoutError": "R5/R18 항체: 타임아웃 우회 후 캐시/폴백 데이터 사용",
    }
    return table.get(name, "R18 상선약수(上善若水): 안전 기본값 우회 및 면역 원장 기록")


# =====================================================================
# 2. 주역 64괘 연동 (rgon_hexagram_engine.py)
# =====================================================================
def link_hexagram(root_dir=None):
    root = resolve_root(root_dir)
    hex_path = os.path.join(root, HEXAGRAM_FILENAME)
    info = {
        "available": False,
        "number": None,
        "name": "중천건(重天乾)",
        "summary": "자강불식(自強不息) — 스스로 강건히 쉬지 않고 정진한다",
        "inspection_mode": "standard",
    }
    if not os.path.isfile(hex_path):
        return info
    try:
        spec = importlib.util.spec_from_file_location("rgon_hexagram_engine", hex_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            raw = None
            for fn_name in (
                "get_today_hexagram", "today_hexagram", "daily_hexagram",
                "get_daily_hexagram", "cast_today", "get_hexagram_of_day",
            ):
                fn = getattr(mod, fn_name, None)
                if callable(fn):
                    try:
                        raw = fn()
                        break
                    except TypeError:
                        try:
                            raw = fn(_kst_now().date())
                            break
                        except Exception:
                            pass
            if raw is None and hasattr(mod, "HEXAGRAMS"):
                hx = getattr(mod, "HEXAGRAMS")
                if isinstance(hx, (list, tuple)) and hx:
                    idx = _kst_now().timetuple().tm_yday % len(hx)
                    raw = hx[idx]
            info["available"] = True
            if isinstance(raw, dict):
                num = raw.get("number") or raw.get("no") or raw.get("id") or raw.get("index")
                name = raw.get("name") or raw.get("title") or raw.get("kr") or info["name"]
                summ = (
                    raw.get("wisdom") or raw.get("advice") or raw.get("meaning")
                    or raw.get("summary") or raw.get("action") or info["summary"]
                )
                info.update({"number": num, "name": str(name), "summary": str(summ)})
            elif raw is not None:
                info["summary"] = str(raw)[:200]
    except Exception as e:
        info["error"] = str(e)[:160]

    text_blob = "%s %s" % (info.get("name", ""), info.get("summary", ""))
    num = info.get("number")
    if (isinstance(num, int) and num in CAUTION_HEX_NUMBERS) or any(
        k in text_blob for k in CAUTION_KEYWORDS
    ):
        info["inspection_mode"] = "reinforced"
    return info


# =====================================================================
# 3. 백업 스냅샷 & 손상 파일 자동 복원 (Rollback & Quarantine)
# =====================================================================
def _snapshot_store_dir(root):
    d = os.path.join(root, ".rgon_backup", "wbc_snapshots")
    os.makedirs(d, exist_ok=True)
    return d


def _quarantine_dir(root):
    d = os.path.join(root, ".rgon_backup", "wbc_quarantine")
    os.makedirs(d, exist_ok=True)
    return d


def save_clean_snapshot(file_path, root_dir=None):
    root = resolve_root(root_dir)
    if not os.path.isfile(file_path) or is_protected_file(file_path):
        return None
    r = _rel(file_path, root).replace("/", "__").replace(":", "_")
    dst = os.path.join(_snapshot_store_dir(root), r + ".clean")
    try:
        shutil.copy2(file_path, dst)
        return dst
    except Exception:
        return None


def _is_candidate_valid(candidate_path, target_ext):
    try:
        with open(candidate_path, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
        if target_ext == ".py":
            ast.parse(txt, filename=candidate_path)
            return True
        if target_ext == ".json":
            json.loads(txt)
            return True
        return len(txt) > 0
    except Exception:
        return False


def find_latest_valid_backup(file_path, root_dir=None):
    root = resolve_root(root_dir)
    base = os.path.basename(file_path)
    rel_key = _rel(file_path, root).replace("/", "__").replace(":", "_")
    ext = os.path.splitext(base)[1].lower()
    backup_root = os.path.join(root, ".rgon_backup")
    if not os.path.isdir(backup_root):
        return None
    candidates = []
    for dp, _, fns in os.walk(backup_root):
        if "wbc_quarantine" in dp:
            continue
        for fn in fns:
            if fn.startswith(rel_key + '.') or fn.startswith(base + '.'):
                full = os.path.join(dp, fn)
                try:
                    candidates.append((os.path.getmtime(full), full))
                except Exception:
                    pass
    candidates.sort(key=lambda x: x[0], reverse=True)
    for _, cand in candidates:
        if _is_candidate_valid(cand, ext):
            return cand
    return None


def auto_restore(file_path, reason="corruption_detected", root_dir=None):
    root = resolve_root(root_dir)
    full = file_path if os.path.isabs(file_path) else os.path.join(root, file_path)
    rel_p = _rel(full, root)
    event = {
        "timestamp_kst": _now_iso(),
        "file": rel_p,
        "reason": str(reason)[:200],
        "restored": False,
        "source_backup": None,
        "quarantined_to": None,
    }
    if is_protected_file(full):
        event["note"] = "보호 대상 파일(.html/.js/manifest.json)은 자동 덮어쓰기 금지(R16/R18)"
        _append_heal_event(event, root)
        return event

    cand = find_latest_valid_backup(full, root)
    if not cand:
        event["note"] = "유효한 정상 백업본을 찾지 못함"
        _append_heal_event(event, root)
        return event

    try:
        if os.path.isfile(full):
            qname = rel_p.replace("/", "__") + "." + _kst_now().strftime("%Y%m%d_%H%M%S") + ".corrupt"
            qpath = os.path.join(_quarantine_dir(root), qname)
            shutil.copy2(full, qpath)
            event["quarantined_to"] = _rel(qpath, root)
        shutil.copy2(cand, full)
        event["restored"] = True
        event["source_backup"] = _rel(cand, root)
    except Exception as e:
        event["error"] = str(e)[:200]

    _append_heal_event(event, root)
    return event


def _append_heal_event(event, root):
    try:
        ledger = load_ledger(root)
        ledger.setdefault("healed_events", []).append(event)
        save_ledger(ledger, root)
    except Exception:
        pass


# =====================================================================
# 4. 상선약수(上善若水) 우회 실행기 — 물처럼 막힌 곳을 돌아 흐른다
# =====================================================================
def adapt_dict(data, key_aliases=None, defaults=None):
    """외부 JSON/API 응답 키 이름이 바뀌어도 별칭(alias)과 기본값으로 흡수한다."""
    if not isinstance(data, dict):
        data = {}
    out = dict(data)
    if isinstance(key_aliases, dict):
        for canonical, aliases in key_aliases.items():
            if canonical in out and out[canonical] is not None:
                continue
            for alt in (aliases if isinstance(aliases, (list, tuple)) else [aliases]):
                if alt in data and data[alt] is not None:
                    out[canonical] = data[alt]
                    break
    if isinstance(defaults, dict):
        for k, v in defaults.items():
            if k not in out or out[k] is None:
                out[k] = v
    return out


def run_safely(fn, *args, default=None, fallback=None, context=None, root_dir=None, **kwargs):
    """함수를 안전하게 실행하고, 예외 발생 시 지문 기록 후 fallback/default로 우회한다."""
    ctx = context or getattr(fn, "__name__", "callable")
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        fp_info = fingerprint(exc, context=ctx, root_dir=root_dir)
        root = resolve_root(root_dir)
        try:
            ledger = load_ledger(root)
            ledger.setdefault("bypass_log", []).append({
                "timestamp_kst": _now_iso(),
                "context": str(ctx),
                "exc_type": type(exc).__name__,
                "message": str(exc)[:200],
                "fingerprint": fp_info.get("fingerprint"),
                "suppressed": fp_info.get("suppressed", False),
                "action": "fallback_callable" if callable(fallback) else "default_value",
            })
            save_ledger(ledger, root)
        except Exception:
            pass
        if callable(fallback):
            try:
                return fallback(*args, **kwargs)
            except Exception:
                return default
        return default


def shield(default=None, fallback=None, context=None):
    """데코레이터 형태 상선약수 방어막."""
    def _wrap(fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            return run_safely(
                fn, *args,
                default=default,
                fallback=fallback,
                context=context or fn.__name__,
                **kwargs,
            )
        return _inner
    return _wrap


def install_excepthook(script_name="script", root_dir=None):
    """스크립트 전역 미처리 예외 후크 장착 (백혈구 세이프가드용)."""
    prev_hook = sys.excepthook

    def _wbc_hook(exc_type, exc_value, exc_tb):
        try:
            tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            fp = compute_fingerprint(exc_value, context=script_name, tb_str=tb_str)
            fingerprint(exc_value, context=script_name, root_dir=root_dir)
            sys.stderr.write(
                "[RGON-WBC] 예외 감지 (%s in %s, fp=%s)\n"
                % (getattr(exc_type, "__name__", str(exc_type)), script_name, fp)
            )
        except Exception:
            pass
        if callable(prev_hook):
            prev_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = _wbc_hook
    return _wbc_hook


# =====================================================================
# 5. 백혈구 무결성 순찰 (patrol) — AST / JSON / HTML 마커 / 보호 해시
# =====================================================================
MARKER_PAIR_RE = re.compile(r"\[([A-Z0-9_-]+)-(START|END)\]")


def _check_marker_balance(text):
    counts = {}
    for m in MARKER_PAIR_RE.finditer(text):
        prefix, kind = m.group(1), m.group(2)
        slot = counts.setdefault(prefix, {"START": 0, "END": 0})
        slot[kind] += 1
    unbalanced = []
    for prefix, slot in counts.items():
        if slot["START"] != slot["END"]:
            unbalanced.append("%s(S=%d,E=%d)" % (prefix, slot["START"], slot["END"]))
    return unbalanced


def patrol(root_dir=None, auto_heal=True):
    root = resolve_root(root_dir)
    hex_info = link_hexagram(root)
    py_checked = 0
    json_checked = 0
    html_checked = 0
    py_errors = []
    json_errors = []
    html_marker_warnings = []
    healed_now = []

    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".rgon_backup")]
        for fn in fns:
            full = os.path.join(dp, fn)
            rel_p = _rel(full, root)
            low = fn.lower()
            if low.endswith(".py"):
                py_checked += 1
                try:
                    with open(full, "r", encoding="utf-8-sig", errors="replace") as f:
                        src = f.read()
                    ast.parse(src, filename=rel_p)
                    save_clean_snapshot(full, root)
                except Exception as exc:
                    fingerprint(exc, context="patrol:py:" + rel_p, root_dir=root)
                    healed = False
                    if auto_heal and not is_protected_file(full):
                        ev = auto_restore(full, reason="SyntaxError: " + str(exc)[:120], root_dir=root)
                        healed = bool(ev.get("restored"))
                        if healed:
                            healed_now.append(rel_p)
                    if not healed:
                        py_errors.append({"file": rel_p, "error": str(exc)[:180]})
            elif low.endswith(".json"):
                json_checked += 1
                try:
                    with open(full, "r", encoding="utf-8-sig", errors="replace") as f:
                        raw = f.read()
                    json.loads(raw)
                    if not is_protected_file(full):
                        save_clean_snapshot(full, root)
                except Exception as exc:
                    fingerprint(exc, context="patrol:json:" + rel_p, root_dir=root)
                    healed = False
                    if auto_heal and not is_protected_file(full):
                        ev = auto_restore(full, reason="JSONDecodeError: " + str(exc)[:120], root_dir=root)
                        healed = bool(ev.get("restored"))
                        if healed:
                            healed_now.append(rel_p)
                    if not healed:
                        json_errors.append({"file": rel_p, "error": str(exc)[:180]})
            elif low.endswith(".html"):
                html_checked += 1
                try:
                    with open(full, "r", encoding="utf-8-sig", errors="replace") as f:
                        ht = f.read()
                    unb = _check_marker_balance(ht)
                    if unb:
                        html_marker_warnings.append({"file": rel_p, "unbalanced": unb})
                except Exception:
                    pass

    baseline_path = os.path.join(root, ".rgon_file_hashes.json")
    protected_drift = []
    if os.path.isfile(baseline_path):
        try:
            with open(baseline_path, "r", encoding="utf-8", errors="replace") as f:
                base_data = json.load(f)
            base_files = base_data.get("files", base_data) if isinstance(base_data, dict) else {}
            if isinstance(base_files, dict):
                for r, old_h in base_files.items():
                    if not is_protected_file(r):
                        continue
                    fp = os.path.join(root, r.replace("/", os.sep))
                    if os.path.isfile(fp):
                        with open(fp, "rb") as bf:
                            cur_h = _sha256_bytes(bf.read())
                        if cur_h != old_h:
                            protected_drift.append(r)
        except Exception:
            pass

    penalty = (
        len(py_errors) * 15
        + len(json_errors) * 15
        + len(html_marker_warnings) * 5
        + len(protected_drift) * 10
    )
    health_score = max(0, min(100, 100 - penalty))

    report = {
        "timestamp_kst": _now_iso(),
        "version": WBC_VERSION,
        "health_score": health_score,
        "inspection_mode": hex_info.get("inspection_mode", "standard"),
        "today_hexagram": hex_info,
        "py_checked": py_checked,
        "json_checked": json_checked,
        "html_checked": html_checked,
        "py_errors": py_errors,
        "json_errors": json_errors,
        "html_marker_warnings": html_marker_warnings,
        "protected_drift": protected_drift,
        "healed_now": healed_now,
    }

    ledger = load_ledger(root)
    ledger["health_score"] = health_score
    ledger["inspection_mode"] = report["inspection_mode"]
    ledger["today_hexagram"] = hex_info
    ledger.setdefault("patrol_history", []).append({
        "timestamp_kst": report["timestamp_kst"],
        "health_score": health_score,
        "py_checked": py_checked,
        "json_checked": json_checked,
        "html_checked": html_checked,
        "errors": len(py_errors) + len(json_errors),
        "healed": len(healed_now),
    })
    save_ledger(ledger, root)
    return report


# =====================================================================
# 6. 자가 테스트 (--self-test) & CLI
# =====================================================================
def self_test(root_dir=None):
    root = resolve_root(root_dir)
    sandbox = os.path.join(root, ".rgon_backup", "wbc_selftest")
    os.makedirs(sandbox, exist_ok=True)
    sample = os.path.join(sandbox, "_wbc_dummy_sample.py")
    good_code = "# -*- coding: utf-8 -*-\nVALUE = 42\n"
    with open(sample, "w", encoding="utf-8", newline="\n") as f:
        f.write(good_code)
    save_clean_snapshot(sample, root)

    with open(sample, "w", encoding="utf-8", newline="\n") as f:
        f.write("def broken(:\n    pass\n")
    ev = auto_restore(sample, reason="self_test_syntax_error", root_dir=root)
    with open(sample, "r", encoding="utf-8", errors="replace") as f:
        restored_txt = f.read()
    ast.parse(restored_txt)

    def _boom():
        raise KeyError("simulated_missing_key")

    val = run_safely(_boom, default="WATER_BYPASS_OK", context="self_test_bypass", root_dir=root)
    mapped = adapt_dict({"new_title": "RGON"}, key_aliases={"title": ["new_title", "name"]}, defaults={"score": 100})
    try:
        os.remove(sample)
    except Exception:
        pass
    return {
        "restore_ok": bool(ev.get("restored")) and ("VALUE = 42" in restored_txt),
        "bypass_ok": val == "WATER_BYPASS_OK",
        "adapt_ok": mapped.get("title") == "RGON" and mapped.get("score") == 100,
    }


def format_status(root_dir=None):
    root = resolve_root(root_dir)
    ledger = load_ledger(root)
    hx = ledger.get("today_hexagram") or link_hexagram(root)
    lines = [
        "============================================================",
        " RGON 백혈구(WBC) 자가치유 면역 엔진 상태판 (" + WBC_VERSION + ")",
        "============================================================",
        " 작업 폴더     : " + root,
        " 건강 점수     : %s / 100 (점검 모드: %s)" % (ledger.get("health_score", 100), ledger.get("inspection_mode", "standard")),
        " 항체 범위     : %s (총 %d개)" % (ledger.get("antibody_range", ANTIBODY_RANGE), len(ledger.get("antibodies", []))),
        " 오늘의 괘     : %s — %s" % (hx.get("name", "-"), hx.get("summary", "-")),
        " 지문 기록 수  : %d개 (중복 경보 억제 누적: %d회)" % (len(ledger.get("fingerprints", {})), int(ledger.get("suppressed_count", 0))),
        " 치유 이력 수  : %d건 / 상선약수 우회: %d건" % (len(ledger.get("healed_events", [])), len(ledger.get("bypass_log", []))),
        " 철학 원칙     : " + PRINCIPLE,
        "============================================================",
    ]
    return "\n".join(lines)


def main(argv=None):
    _console_utf8()
    parser = argparse.ArgumentParser(description="RGON 백혈구(WBC) 자가치유 면역 엔진")
    parser.add_argument("--patrol", action="store_true", help="전체 무결성 순찰 실행")
    parser.add_argument("--status", action="store_true", help="현재 면역 원장 상태 출력")
    parser.add_argument("--heal", metavar="FILE", help="지정 파일 백업 복원 시도")
    parser.add_argument("--self-test", action="store_true", help="자가 복원/우회 셀프 테스트")
    parser.add_argument("--root", default=None, help="작업 폴더 경로 지정")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if args.heal:
        ev = auto_restore(args.heal, reason="manual_cli_heal", root_dir=root)
        print(json.dumps(ev, ensure_ascii=False, indent=2))
        return 0 if ev.get("restored") else 1
    if args.self_test:
        res = self_test(root)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if all(res.values()) else 1
    if args.patrol:
        rep = patrol(root, auto_heal=True)
        print(
            "[RGON-WBC] 순찰 완료: 건강 %d/100 | py=%d(오류 %d) | json=%d(오류 %d) | html=%d | 치유=%d"
            % (
                rep["health_score"],
                rep["py_checked"], len(rep["py_errors"]),
                rep["json_checked"], len(rep["json_errors"]),
                rep["html_checked"], len(rep["healed_now"]),
            )
        )
        return 0
    if args.status:
        print(format_status(root))
        return 0

    patrol(root, auto_heal=True)
    print(format_status(root))
    return 0


# ===== RGON-STEP20-START (R20 antibody, v11.51-AON-COMMANDER-TWIN) =====
ANTIBODY_RANGE = "R1~R52"
_RGON_R20_TEXT = "일일 자율 순환 루프(백혈구 순찰 → 영양분 소화·스킬 주조 → 3자 심판 → 주역 64괘 아침 브리핑) 무인 자동화"
try:
    for _nm in ("DEFAULT_ANTIBODIES", "ANTIBODIES", "ANTIBODY_LIST", "ANTIBODY_RULES"):
        _ab = globals().get(_nm)
        if isinstance(_ab, dict) and "R20" not in _ab:
            _smp = next(iter(_ab.values()), None)
            _ab["R20"] = {"id": "R20", "title": _RGON_R20_TEXT, "name": _RGON_R20_TEXT, "step": 20} if isinstance(_smp, dict) else _RGON_R20_TEXT
        elif isinstance(_ab, list):
            _ids = [str(x.get("id", "")) if isinstance(x, dict) else str(x[0] if isinstance(x, tuple) and x else x) for x in _ab]
            if not any(i.startswith("R20") for i in _ids):
                if _ab and isinstance(_ab[0], dict):
                    _ab.append({"id": "R20", "title": _RGON_R20_TEXT, "name": _RGON_R20_TEXT, "desc": _RGON_R20_TEXT, "step": 20})
                elif _ab and isinstance(_ab[0], tuple):
                    _ab.append(("R20", _RGON_R20_TEXT))
                else:
                    _ab.append("R20: " + _RGON_R20_TEXT)
except Exception:
    pass
# ===== RGON-STEP20-END =====


# >>> RGON-STEP21-R21 >>>
ANTIBODY_RANGE = "R1~R52"
_R21 = "@Mindung-EasyAI 양분 흡수 — Matt Pocock(GLOSSARY.md · Spec/Tracer-Bullet Tickets 분업) + ECC(AgentShield 비밀키/설정 보안 스캔)"
for _n in ("DEFAULT_ANTIBODIES", "ANTIBODIES", "ANTIBODY_RULES", "ANTIBODY", "RULES"):
    _d = globals().get(_n)
    if isinstance(_d, dict) and "R21" not in _d:
        _s = next(iter(_d.values()), "")
        _d["R21"] = ({k: ("R21" if k in ("id", "code") else _R21 if isinstance(v, str) else v) for k, v in _s.items()}
                     if isinstance(_s, dict) else _R21)
    elif isinstance(_d, list) and not any("R21" in str(x) for x in _d):
        _d.append({"id": "R21", "title": _R21, "name": _R21, "text": _R21, "step": 21} if _d and isinstance(_d[0], dict) else "R21: " + _R21)
# <<< RGON-STEP21-R21 <<<

# [RGON-STEP22-WBC-R22-START]
ANTIBODY_RANGE = 'R1~R52'
_R22_TXT = '자아성찰 전신 혈관 개통 — 레이더·영양분(SKILL.md)·티켓/AgentShield·백혈구(WBC)·주역64괘·스냅샷/클라우드 JSON 6대 기관 무결점 단일 순환'
for _nm in ('DEFAULT_ANTIBODIES', 'ANTIBODIES', 'ANTIBODY_LIST'):
    _lst = globals().get(_nm)
    if isinstance(_lst, list) and not any('R22' in str(x) for x in _lst):
        _lst.append({'id': 'R22', 'title': _R22_TXT, 'name': _R22_TXT, 'step': 22})
# [RGON-STEP22-WBC-R22-END]


# [RGON-R24-START] Step24 항체 비파괴 주입
R24_ANTIBODY = {"id": "R24", "rule": 'R24: 실전 트레이딩 3자 찬반 심판기(Bull/Bear/Judge) & 주역 64괘 리스크 필터 상시 가동 — 금고 보존(지족불욕·사환예방) 최우선 검증'}
for _n in ("ANTIBODIES", "DEFAULT_ANTIBODIES", "ANTIBODY_RULES", "IMMUNE_RULES", "RULES", "ANTIBODY"):
    _o = globals().get(_n)
    if isinstance(_o, dict) and "R24" not in _o:
        _o["R24"] = R24_ANTIBODY["rule"]
    elif isinstance(_o, list) and not any("R24" in str(_x) for _x in _o):
        _o.append(dict(R24_ANTIBODY) if (_o and isinstance(_o[0], dict)) else R24_ANTIBODY["rule"])
# [RGON-R24-END]


# [STEP27-WBC-IMMUNE-NORMALIZER] DEFAULT_ANTIBODIES 내 모든 항목에 step/title 보장
for _ab in globals().get("DEFAULT_ANTIBODIES", []):
    if isinstance(_ab, dict):
        _aid = str(_ab.get("id", "R27"))
        _num = int("".join(c for c in _aid if c.isdigit()) or 27)
        _ab.setdefault("step", _num)
        _ab.setdefault("title", _ab.get("name") or _ab.get("rule") or _aid)

# [RGON-R33-INJECT] Step 33 — DEFAULT_ANTIBODIES R33 복제 주입
try:
    _R33 = 'R33: 성대·청각 음성 교감 기관 — Web Audio API 무파일 물방울 신디사이저(Procedural SFX) + K-아이 뉴럴 음성 합성(Web Speech TTS) + 핸즈프리 음성 대행 명령(STT) 통합'
    if isinstance(DEFAULT_ANTIBODIES, dict):
        DEFAULT_ANTIBODIES.setdefault("R33", _R33)
    elif isinstance(DEFAULT_ANTIBODIES, list) and not any("R33" in str(_x) for _x in DEFAULT_ANTIBODIES):
        _s = DEFAULT_ANTIBODIES[-1] if DEFAULT_ANTIBODIES else None
        if isinstance(_s, dict):
            _n = {k: v for k, v in _s.items()}
            for _k in list(_n):
                if _k in ("id", "code", "key"): _n[_k] = "R33"
                elif _k in ("text", "desc", "description", "rule", "name", "title"): _n[_k] = _R33
            DEFAULT_ANTIBODIES.append(_n)
        elif isinstance(_s, (list, tuple)):
            DEFAULT_ANTIBODIES.append(type(_s)(["R33", _R33] + list(_s[2:])))
        else:
            DEFAULT_ANTIBODIES.append(_R33)
except NameError:
    DEFAULT_ANTIBODIES = {"R33": 'R33: 성대·청각 음성 교감 기관 — Web Audio API 무파일 물방울 신디사이저(Procedural SFX) + K-아이 뉴럴 음성 합성(Web Speech TTS) + 핸즈프리 음성 대행 명령(STT) 통합'}

# [RGON-R34-INJECT] — DEFAULT_ANTIBODIES R34 복제 주입
try:
    _RX = 'R34: 아온(A-ON) 감성·인격 대화 두뇌 & 해마 기억 기관 — 일상/감정 교감과 업무 대행(Tier 1~3) 정밀 분별 라우터 + K-아이 페르소나 대화 엔진 + 친밀도·해마 기억장 통합'
    if isinstance(DEFAULT_ANTIBODIES, dict):
        DEFAULT_ANTIBODIES.setdefault("R34", _RX)
    elif isinstance(DEFAULT_ANTIBODIES, list) and not any("R34" in str(_x) for _x in DEFAULT_ANTIBODIES):
        _s = DEFAULT_ANTIBODIES[-1] if DEFAULT_ANTIBODIES else None
        if isinstance(_s, dict):
            _n = {k: v for k, v in _s.items()}
            for _k in list(_n):
                if _k in ("id", "code", "key"): _n[_k] = "R34"
                elif _k in ("text", "desc", "description", "rule", "name", "title"): _n[_k] = _RX
            DEFAULT_ANTIBODIES.append(_n)
        elif isinstance(_s, (list, tuple)):
            DEFAULT_ANTIBODIES.append(type(_s)(["R34", _RX] + list(_s[2:])))
        else:
            DEFAULT_ANTIBODIES.append(_RX)
except NameError:
    DEFAULT_ANTIBODIES = {"R34": 'R34: 아온(A-ON) 감성·인격 대화 두뇌 & 해마 기억 기관 — 일상/감정 교감과 업무 대행(Tier 1~3) 정밀 분별 라우터 + K-아이 페르소나 대화 엔진 + 친밀도·해마 기억장 통합'}

# [RGON-R35-INJECT] — DEFAULT_ANTIBODIES R35 복제 주입
try:
    _RX = 'R35: 아온(A-ON) 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치 — Tier 3·금융·파일삭제·외부전송은 마스터 + 카테고리 스위치 수동 ON + 대표님 승인 3중 충족 시에만 집행, 하나라도 OFF면 집행 0건'
    if isinstance(DEFAULT_ANTIBODIES, dict):
        DEFAULT_ANTIBODIES.setdefault("R35", _RX)
    elif isinstance(DEFAULT_ANTIBODIES, list) and not any("R35" in str(_x) for _x in DEFAULT_ANTIBODIES):
        _s = DEFAULT_ANTIBODIES[-1] if DEFAULT_ANTIBODIES else None
        if isinstance(_s, dict):
            _n = {k: v for k, v in _s.items()}
            for _k in list(_n):
                if _k in ("id", "code", "key"): _n[_k] = "R35"
                elif _k in ("text", "desc", "description", "rule", "name", "title"): _n[_k] = _RX
            DEFAULT_ANTIBODIES.append(_n)
        elif isinstance(_s, (list, tuple)):
            DEFAULT_ANTIBODIES.append(type(_s)(["R35", _RX] + list(_s[2:])))
        else:
            DEFAULT_ANTIBODIES.append(_RX)
except NameError:
    DEFAULT_ANTIBODIES = {"R35": 'R35: 아온(A-ON) 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치 — Tier 3·금융·파일삭제·외부전송은 마스터 + 카테고리 스위치 수동 ON + 대표님 승인 3중 충족 시에만 집행, 하나라도 OFF면 집행 0건'}

if __name__ == "__main__":
    sys.exit(main())
