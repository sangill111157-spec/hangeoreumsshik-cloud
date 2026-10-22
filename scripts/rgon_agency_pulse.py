# -*- coding: utf-8 -*-
"""RGON 6대 청사(D1~D6) 무인 박동(Heartbeat) 엔진
- 표준 라이브러리만 사용하고 네트워크와 유료 API는 쓰지 않는다.
- 독대실 HTML 3곳과 rgon_constitution.json은 읽기 전용이다(무접촉).
- rgon_brain_snapshot.json(루트/dashboard/docs)의 agency_pulse만 원자적으로 갱신한다(R13).
"""
import os, re, sys, json, hashlib, tempfile, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.environ.get("RGON_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = datetime.timezone(datetime.timedelta(hours=9))
BOM = b"\xef\xbb\xbf"

HTML_RELS = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
SNAP_RELS = ["rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"]
CONST_REL = "rgon_constitution.json"
TREASURY_REL = "treasury_ledger.json"
SCHEDULE_REL = "brain_basket/master_schedule.json"
AB_SCRIPT_ID = "rgon-step11-ab-realname"

PROTECTED_IDS = [
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "rgon-step10-agency-awaken",
    "dokdae-feed",
]

ANTIBODIES = {
    1: "PS 따옴표 함정 방지",
    2: "모바일 가로폭 보호",
    3: "체크박스 선택 보존",
    4: "정적 JSON 폴백",
    5: "서랍 빈여백 제거",
    6: "세로 글자 깨짐 방지",
    7: "배지 깜빡임 방지",
    8: "승인(Y) 전 코드 금지",
    9: "단일 코드블록 원칙",
    10: "자기참조 오판 방지",
    11: "최소 변경 Top1 선택",
    12: "중복 반복출력 금지",
    13: "0바이트 덮어쓰기 금지",
}

AGENCIES = [
    ("D1", "알파-D1 퀀트", "R&D · 4대 AI 교차검증 전광판 대기 상태 점검"),
    ("D2", "알파-D2 바이럴", "핵심 키워드 & BM 파이프라인 준비도 점검"),
    ("D3", "알파-D3 미디어", "브리핑 · TTS · 미디어 자산 상태 점검"),
    ("D4", "알파-D4 홍익", "제0조 홍익인간 원칙 & 헌법 v1.0 무결성 해시 점검"),
    ("D5", "알파-D5 가디언", "13대 항체(R1~R13) & 독대실 HTML 3곳 해시 일치 수호 점검"),
    ("D6", "알파-D6 트레저리", "treasury_ledger.json 금고 장부 무결성 & 무과금(Free Tier) 점검"),
]

RANK = {"OK": 0, "STANDBY": 1, "WARN": 2, "ALERT": 3}
MEDIA_DIRS = ["media", "assets", "audio", "tts", "briefings", "briefing",
              "dashboard/media", "docs/media", "dashboard/audio", "docs/audio"]
MEDIA_EXT = {".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".webm", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def p(rel):
    return os.path.join(ROOT, *rel.split("/"))


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def decode(data):
    if data.startswith(BOM):
        return data[len(BOM):].decode("utf-8"), True
    return data.decode("utf-8"), False


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    if not data:
        raise RuntimeError("R13 차단: 0바이트 기록 시도 -> %s" % path)
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".rgon_pulse_", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if os.path.getsize(tmp) != len(data):
            raise RuntimeError("임시파일 크기 불일치 -> %s" % path)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass
    if os.path.getsize(path) != len(data):
        raise RuntimeError("기록 후 크기 검증 실패 -> %s" % path)


def id_pat(pid):
    return r"\bid\s*=\s*[\"']" + re.escape(pid) + r"[\"']"


def count_ids(text):
    return {pid: len(re.findall(id_pat(pid), text)) for pid in PROTECTED_IDS}


def load_json_rel(rel):
    path = p(rel)
    info = {"exists": False, "valid": False, "obj": None, "sha256": None, "bytes": 0, "bom": False, "error": None}
    if not os.path.isfile(path):
        return info
    raw = read_bytes(path)
    info.update({"exists": True, "bytes": len(raw), "sha256": sha256(raw)})
    try:
        txt, bom = decode(raw)
        info["bom"] = bom
        if not txt.strip():
            info["error"] = "empty"
            return info
        info["obj"] = json.loads(txt)
        info["valid"] = True
    except Exception as ex:
        info["error"] = str(ex)[:160]
    return info


def worst(statuses):
    return max(statuses, key=lambda s: RANK.get(s, 3)) if statuses else "OK"


def key_hits(obj, pattern, depth=0, limit=5):
    n = 0
    if depth > limit:
        return 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if re.search(pattern, str(k)):
                n += 1
            n += key_hits(v, pattern, depth + 1, limit)
    elif isinstance(obj, list):
        for v in obj[:500]:
            n += key_hits(v, pattern, depth + 1, limit)
    return n


def scan_html():
    files = {}
    for rel in HTML_RELS:
        path = p(rel)
        if not os.path.isfile(path):
            files[rel] = {"exists": False}
            continue
        raw = read_bytes(path)
        txt = decode(raw)[0]
        files[rel] = {
            "exists": True,
            "sha256": sha256(raw),
            "bytes": len(raw),
            "ids": count_ids(txt),
            "ab_script": bool(re.search(id_pat(AB_SCRIPT_ID), txt)),
        }
    ex = [f for f in files.values() if f.get("exists")]
    full = len(ex) == len(HTML_RELS)
    return {
        "files": files,
        "all_exist": full,
        "hash_unified": full and len(set(f["sha256"] for f in ex)) == 1,
        "ids_ok": full and all(all(v >= 1 for v in f["ids"].values()) for f in ex),
        "ab_script_all": full and all(f["ab_script"] for f in ex),
    }


def scan_media():
    found, count, seen = [], 0, 0
    for rel in MEDIA_DIRS:
        d = p(rel)
        if not os.path.isdir(d):
            continue
        found.append(rel)
        for base, dirs, names in os.walk(d):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for nm in names:
                seen += 1
                if os.path.splitext(nm)[1].lower() in MEDIA_EXT:
                    count += 1
            if seen >= 5000:
                break
        if seen >= 5000:
            break
    return found, count


def check_antibodies(snap):
    recs = snap.get("antibody_realnames") if isinstance(snap, dict) else None
    ok, bad = [], []
    table = {}
    if isinstance(recs, list):
        for r in recs:
            if isinstance(r, dict) and isinstance(r.get("id"), str):
                table[r["id"]] = r
    for n, name in ANTIBODIES.items():
        r = table.get("R%d" % n)
        (ok if (r and r.get("name") == name) else bad).append("R%d" % n)
    return ok, bad


def build_pulse(snap, now):
    # R10: 직전 박동 기록(agency_pulse)을 뺀 상태로 점검한다(자기참조 오판 방지)
    base_snap = {k: v for k, v in snap.items() if k not in ("agency_pulse", "agency_pulse_updated")}
    prev = snap.get("agency_pulse") if isinstance(snap.get("agency_pulse"), dict) else {}
    prev_base = prev.get("baseline") if isinstance(prev.get("baseline"), dict) else {}

    html = scan_html()
    const = load_json_rel(CONST_REL)
    treasury = load_json_rel(TREASURY_REL)
    schedule = load_json_rel(SCHEDULE_REL)
    ab_ok, ab_bad = check_antibodies(base_snap)
    media_dirs, media_count = scan_media()

    agencies = {}

    # D1 퀀트
    f0 = [f for f in html["files"].values() if f.get("exists")]
    board = bool(f0) and all(f["ids"]["rgon-step9-aggregator-board"] >= 1 for f in f0)
    chat = bool(f0) and all(f["ids"]["rgon-step7-chat-zone"] >= 1 for f in f0)
    d1 = "OK" if (board and chat) else "WARN"
    agencies["D1"] = {"metrics": {"aggregator_board_present": board, "chat_zone_present": chat,
                                  "cross_validation_board": "대기(STANDBY-READY)" if board else "미탐지"}, "status": d1}

    # D2 바이럴
    kw = key_hits(base_snap, r"(?i)(keyword|키워드|(^|[_\-\s])bm($|[_\-\s])|pipeline|파이프라인)")
    if schedule["exists"] and not schedule["valid"]:
        d2 = "WARN"
    elif schedule["valid"] or kw > 0:
        d2 = "OK"
    else:
        d2 = "STANDBY"
    agencies["D2"] = {"metrics": {"master_schedule_exists": schedule["exists"], "master_schedule_valid": schedule["valid"],
                                  "keyword_bm_keys": kw}, "status": d2}

    # D3 미디어
    br = key_hits(base_snap, r"(?i)(brief|브리핑|tts|media|미디어)")
    d3 = "OK" if (media_count > 0 or br > 0) else "STANDBY"
    agencies["D3"] = {"metrics": {"media_dirs": media_dirs, "media_files": media_count, "briefing_keys": br}, "status": d3}

    # D4 홍익
    hongik = False
    if const["valid"]:
        hongik = "홍익" in json.dumps(const["obj"], ensure_ascii=False)
    baseline = prev_base.get("constitution_sha256")
    if os.environ.get("RGON_PULSE_RESET_BASELINE") == "1" or not baseline:
        baseline = const["sha256"]
    same = bool(const["sha256"]) and const["sha256"] == baseline
    if not const["exists"]:
        d4 = "ALERT"
    elif not const["valid"] or not same:
        d4 = "ALERT"
    elif not hongik:
        d4 = "WARN"
    else:
        d4 = "OK"
    agencies["D4"] = {"metrics": {"constitution_exists": const["exists"], "constitution_valid": const["valid"],
                                  "constitution_sha256": const["sha256"], "baseline_match": same,
                                  "article0_hongik_found": hongik}, "status": d4}

    # D5 가디언
    d5_flags = [html["hash_unified"], html["ids_ok"], len(ab_bad) == 0]
    d5 = "OK" if all(d5_flags) else ("ALERT" if not html["all_exist"] else "WARN")
    agencies["D5"] = {"metrics": {"html_all_exist": html["all_exist"], "html_hash_unified": html["hash_unified"],
                                  "protected_ids_ok": html["ids_ok"], "ab_realname_script_all": html["ab_script_all"],
                                  "antibodies_active": len(ab_ok), "antibodies_total": 13,
                                  "antibodies_need_check": ab_bad}, "status": d5}

    # D6 트레저리
    if not treasury["exists"]:
        d6 = "STANDBY"
    elif not treasury["valid"]:
        d6 = "WARN"
    else:
        d6 = "OK"
    agencies["D6"] = {"metrics": {"ledger_exists": treasury["exists"], "ledger_valid": treasury["valid"],
                                  "ledger_sha256": treasury["sha256"], "free_tier": True,
                                  "paid_api_calls": 0, "network_used": False}, "status": d6}

    for code, name, duty in AGENCIES:
        a = agencies[code]
        agencies[code] = {"code": code, "name": name, "duty": duty, "status": a["status"],
                          "checked_at": now, "metrics": a["metrics"]}

    beat = prev.get("beat_count") if isinstance(prev.get("beat_count"), int) else 0
    return {
        "version": "1.0",
        "engine": "scripts/rgon_agency_pulse.py",
        "runner": "github-actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "local",
        "checked_at": now,
        "beat_count": beat + 1,
        "overall": worst([a["status"] for a in agencies.values()]),
        "network_used": False,
        "paid_api_calls": 0,
        "agencies": agencies,
        "html_integrity": {
            "hash_unified": html["hash_unified"],
            "protected_ids_ok": html["ids_ok"],
            "sha256": {rel: f.get("sha256") for rel, f in html["files"].items()},
        },
        "antibodies": {
            "active": len(ab_ok),
            "total": 13,
            "list": [{"id": "R%d" % n, "name": ANTIBODIES[n],
                      "status": "활성" if ("R%d" % n) in ab_ok else "점검필요"} for n in range(1, 14)],
        },
        "constitution": {"version": "v1.0", "sha256": const["sha256"]},
        "baseline": {"constitution_sha256": baseline},
    }


def dump(obj, bom):
    raw = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    json.loads(raw.decode("utf-8"))
    return (BOM + raw) if bom else raw


def html_hashes():
    out = {}
    for rel in HTML_RELS:
        path = p(rel)
        out[rel] = sha256(read_bytes(path)) if os.path.isfile(path) else None
    return out


# >>> RGON-C1 DAILY BRIEFING >>>
# Step 11 과제 C-1: 6대 청사 일일 실전 브리핑(daily_briefing) 생성기 (표준 라이브러리만 사용, 장부는 읽기만 함)
C1_EVO_REL = "evolution_memory.json"
C1_TASK_HINTS = ("title", "task", "tasks", "todo", "action", "subject", "topic", "goal", "target", "mission", "name",
                 "과제", "할일", "업무", "제목", "목표", "임무")
C1_KW_HINTS = ("keyword", "keywords", "키워드", "tag", "tags", "bm", "pipeline", "파이프라인")
C1_DATE_HINTS = ("date", "day", "due", "when", "scheduled", "deadline", "날짜", "일자", "마감")
C1_STATUS_KEYS = ("status", "state", "done", "completed", "상태", "완료")
C1_BRIEF_KEYS = ("headline", "D1_quant", "D2_viral", "D3_media", "D4_hongik", "D5_guardian", "D6_treasury", "action_top1")
C1_ICON = {"OK": "🟢", "STANDBY": "🟡", "WARN": "🟠", "ALERT": "🔴"}


def _c1_clean(s, n=48):
    s = re.sub(r"\s+", " ", str(s)).strip()
    s = re.sub(r"[<>`]", "", s)
    return (s[:n - 1] + "…") if len(s) > n else s


def _c1_hit(key, hints):
    k = str(key).lower()
    toks = [t for t in re.split(r"[^0-9a-z가-힣]+", k) if t]
    return k in hints or any(t in hints for t in toks) or any(len(h) >= 4 and h in k for h in hints)


def _c1_walk(o, depth=0):
    if depth > 7:
        return
    if isinstance(o, dict):
        yield o
        for v in o.values():
            for x in _c1_walk(v, depth + 1):
                yield x
    elif isinstance(o, list):
        for v in o[:1000]:
            for x in _c1_walk(v, depth + 1):
                yield x


def _c1_strs(v):
    if isinstance(v, str):
        return [v] if v.strip() else []
    if isinstance(v, list):
        return [x for x in v[:20] if isinstance(x, str) and x.strip()]
    return []


def _c1_schedule(today):
    info = load_json_rel(SCHEDULE_REL)
    res = {"exists": info["exists"], "valid": info["valid"], "today": [], "pending": [], "keywords": []}
    if not info["valid"]:
        return res
    compact = today.replace("-", "")
    seen_t, seen_k = set(), set()

    def add_task(c, bucket):
        if c and c not in seen_t:
            seen_t.add(c)
            res[bucket].append(c)

    for d in _c1_walk(info["obj"]):
        tasks, kws, dates, stat = [], [], [], ""
        for k, v in d.items():
            ks = str(k)
            if today in ks or compact in ks:
                for t in _c1_strs(v):
                    add_task(_c1_clean(t), "today")
                continue
            if _c1_hit(k, C1_KW_HINTS):
                kws.extend(_c1_strs(v))
            elif _c1_hit(k, C1_DATE_HINTS) and isinstance(v, (str, int)):
                dates.append(str(v))
            elif ks.lower() in C1_STATUS_KEYS:
                stat += " " + str(v).lower()
            elif _c1_hit(k, C1_TASK_HINTS):
                tasks.extend(_c1_strs(v))
        for kw in kws:
            c = _c1_clean(kw, 24)
            if c and c not in seen_k:
                seen_k.add(c)
                res["keywords"].append(c)
        if not tasks:
            continue
        done = any(w in stat for w in ("done", "complete", "완료", "true", "closed"))
        if done:
            continue
        is_today = any(today in x or compact in x for x in dates)
        for t in tasks:
            add_task(_c1_clean(t), "today" if is_today else "pending")
    return res


def _c1_evolution():
    info = load_json_rel(C1_EVO_REL)
    events = []
    if info["valid"]:
        for d in _c1_walk(info["obj"]):
            ev = d.get("event")
            if isinstance(ev, str) and ev.strip():
                events.append(ev.strip())
    return {"valid": info["valid"], "count": len(events),
            "step11": sum(1 for e in events if e.startswith("step11")),
            "latest": _c1_clean(events[-1], 60) if events else ""}


def _c1_treasury():
    info = load_json_rel(TREASURY_REL)
    res = {"exists": info["exists"], "valid": info["valid"], "sha": (info["sha256"] or "")[:12],
           "records": 0, "balance": None}
    if not info["valid"]:
        return res
    o = info["obj"]
    if isinstance(o, list):
        res["records"] = len(o)
    elif isinstance(o, dict):
        res["records"] = sum(len(v) for v in o.values() if isinstance(v, list))
    for d in _c1_walk(o):
        if res["balance"] is not None:
            break
        for k, v in d.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool) and \
                    re.search(r"(?i)(balance|잔액|잔고|total|합계)", str(k)):
                res["balance"] = (_c1_clean(k, 20), v)
                break
    return res


def _c1_constitution():
    info = load_json_rel(CONST_REL)
    txt = json.dumps(info["obj"], ensure_ascii=False) if info["valid"] else ""
    return {"valid": info["valid"], "sha": (info["sha256"] or "")[:12],
            "gates": sorted(set(re.findall(r"(?<![A-Za-z0-9])G([1-5])(?![0-9])", txt))),
            "gate_word": bool(re.search(r"(?i)5\s*-?\s*gate|게이트", txt))}


def _c1_build(pulse, now):
    codes = ["D1", "D2", "D3", "D4", "D5", "D6"]
    ags = pulse.get("agencies") or {}
    st = {c: str((ags.get(c) or {}).get("status") or "STANDBY") for c in codes}
    mt = {c: (ags.get(c) or {}).get("metrics") or {} for c in codes}
    ic = {c: C1_ICON.get(st[c], "⚪") + " " + st[c] for c in codes}
    bad = [c for c in codes if st[c] != "OK"]
    all_ok = not bad and pulse.get("overall") == "OK"
    beat = pulse.get("beat_count") if isinstance(pulse.get("beat_count"), int) else 0
    today = str(now)[:10]
    sch = _c1_schedule(today)
    evo = _c1_evolution()
    tre = _c1_treasury()
    con = _c1_constitution()
    hi = pulse.get("html_integrity") or {}
    ab = pulse.get("antibodies") or {}
    target = (sch["today"] or sch["pending"] or ["다음 Step 지시서 교차검증 준비"])[0]

    headline = "👑 [RGON 6대 청사 일일 실전 브리핑] 박동 #%d · %s" % (
        beat, "D1~D6 ALL OK" if all_ok else "점검 필요: " + ", ".join(bad or ["종합 판정"]))

    d1 = "%s · 4대 AI 교차검증 전광판 %s · Minimal Diff Top1(R11) 심판 가동 · 누적 진화 %d건(Step 11 %d건) · 최신 이력 %s · R&D 핵심 타겟: %s" % (
        ic["D1"], "대기" if mt["D1"].get("aggregator_board_present") else "미탐지",
        evo["count"], evo["step11"], evo["latest"] or "-", target)

    if not sch["exists"]:
        d2 = "%s · master_schedule.json 미탐지 → 오늘 일정 등록 필요" % ic["D2"]
    elif not sch["valid"]:
        d2 = "%s · master_schedule.json JSON 무효 → 점검 필요" % ic["D2"]
    else:
        if sch["today"]:
            tasks = "오늘 과제 %d건: %s" % (len(sch["today"]), " / ".join(sch["today"][:3]))
        elif sch["pending"]:
            tasks = "오늘 날짜 과제 없음 · 대기 과제 %d건: %s" % (len(sch["pending"]), " / ".join(sch["pending"][:3]))
        else:
            tasks = "미완료 과제 0건"
        d2 = "%s · %s · 핵심 키워드: %s · BM 파이프라인 %s" % (
            ic["D2"], tasks, ", ".join(sch["keywords"][:5]) or "미등록",
            "준비 완료" if st["D2"] == "OK" else "준비 중")

    mf = mt["D3"].get("media_files") or 0
    d3 = "%s · 독대실 HTML 3곳 %s · 미디어 자산 %d개 · 브리핑 키 %d · 콘텐츠 준비도: %s" % (
        ic["D3"], "동기화 완료" if hi.get("hash_unified") else "동기화 점검 필요", mf,
        mt["D3"].get("briefing_keys") or 0,
        "미디어+텍스트 브리핑 출고 가능" if mf > 0 else "텍스트 브리핑 출고 가능(미디어 자산 보강 권장)")

    if con["gates"]:
        gate = "5-Gate 조항 %d/5 확인(%s)" % (len(con["gates"]), ",".join("G" + g for g in con["gates"]))
    elif con["gate_word"]:
        gate = "5-Gate 조항 확인"
    else:
        gate = "5-Gate 표기 미탐지(헌법 해시 봉인으로 수호)"
    d4 = "%s · 제0조 홍익인간 %s · 헌법 v1.0 해시 %s %s · %s" % (
        ic["D4"], "확인" if mt["D4"].get("article0_hongik_found") else "미확인", con["sha"] or "-",
        "기준선 일치(무변경)" if mt["D4"].get("baseline_match") else "기준선 불일치", gate)

    d5 = "%s · 13대 항체 %d/%d 활성 · 독대실 3곳 SHA-256 %s · 보호 ID 6/6 %s" % (
        ic["D5"], ab.get("active") or 0, ab.get("total") or 13,
        "100% 일치" if hi.get("hash_unified") else "불일치",
        "철통 수호" if hi.get("protected_ids_ok") else "점검 필요")

    if not tre["exists"]:
        ledger = "금고 장부 미탐지(대기)"
    elif not tre["valid"]:
        ledger = "금고 장부 JSON 무효(점검 필요)"
    else:
        bal = (" · %s %s" % (tre["balance"][0], format(tre["balance"][1], ","))) if tre["balance"] else ""
        ledger = "금고 장부 무결(sha %s · 기록 %d건%s)" % (tre["sha"], tre["records"], bal)
    d6 = "%s · %s · 유료 API 호출 %d회 · 비용 0원 · %s" % (
        ic["D6"], ledger, mt["D6"].get("paid_api_calls") or 0, "Free Tier 100%")

    if not all_ok:
        action = "RGON_Run.bat 원클릭으로 %s 점검·복구 지시서부터 실행(R11 최소 변경 Top1)" % ", ".join(bad or ["종합 판정"])
    elif sch["today"]:
        action = "RGON_Run.bat 원클릭으로 오늘 1순위 과제 「%s」 실행 후 박동 #%d 확인" % (sch["today"][0], beat + 1)
    elif sch["pending"]:
        action = "RGON_Run.bat 원클릭으로 대기 과제 1순위 「%s」 착수 후 박동 #%d 확인" % (sch["pending"][0], beat + 1)
    else:
        action = "RGON_Run.bat 원클릭으로 다음 Step 지시서 발사 → 4대 AI 교차검증 Top1 채택 후 박동 #%d 확인" % (beat + 1)

    out = {"date": today, "generated_at": now, "headline": headline,
           "D1_quant": d1, "D2_viral": d2, "D3_media": d3, "D4_hongik": d4,
           "D5_guardian": d5, "D6_treasury": d6, "action_top1": action}
    out["lines"] = [out[k] for k in C1_BRIEF_KEYS]
    return out


def build_daily_briefing(pulse, snap, now):
    try:
        return _c1_build(pulse, now)
    except Exception as ex:
        b = {k: "브리핑 생성 오류(점검 필요)" for k in C1_BRIEF_KEYS}
        b.update({"error": _c1_clean(ex, 160), "generated_at": now})
        return b
# <<< RGON-C1 DAILY BRIEFING <<<


def run_pulse():
    if not os.path.isdir(ROOT):
        print("[PULSE-FAIL] ROOT 없음: %s" % ROOT)
        return 1
    before = html_hashes()
    now = datetime.datetime.now(KST).isoformat(timespec="seconds")

    root_info = load_json_rel(SNAP_RELS[0])
    if root_info["exists"] and (not root_info["valid"] or not isinstance(root_info["obj"], dict)):
        print("[PULSE-FAIL] 루트 스냅샷이 유효한 JSON 객체가 아닙니다. 덮어쓰지 않고 멈춥니다(R13).")
        return 2
    snap = root_info["obj"] if root_info["exists"] else {}

    pulse = build_pulse(snap, now)
    pulse["daily_briefing"] = build_daily_briefing(pulse, snap, now)  # RGON-C1
    snap["agency_pulse"] = pulse
    snap["agency_pulse_updated"] = now
    atomic_write(p(SNAP_RELS[0]), dump(snap, root_info["bom"]))
    print("[PULSE] 기록: %s" % SNAP_RELS[0])

    for rel in SNAP_RELS[1:]:
        path = p(rel)
        if os.path.isfile(path):
            info = load_json_rel(rel)
            if info["valid"] and isinstance(info["obj"], dict):
                obj = info["obj"]
                obj["agency_pulse"] = pulse
                obj["agency_pulse_updated"] = now
                atomic_write(path, dump(obj, info["bom"]))
                print("[PULSE] 미러 기록: %s" % rel)
            else:
                print("[PULSE-WARN] 미러 JSON 무효, 원본 그대로 두고 건너뜀: %s" % rel)
        elif os.path.isdir(os.path.dirname(path)):
            atomic_write(path, dump(snap, root_info["bom"]))
            print("[PULSE] 미러 신규 생성: %s" % rel)

    after = html_hashes()
    if before != after:
        print("[PULSE-FAIL] 박동 중에 HTML 해시 변동이 감지되었습니다(이 엔진은 HTML을 쓰지 않습니다): %s" % after)
        return 3

    for code, name, duty in AGENCIES:
        print("[PULSE] %s %-12s %-7s | %s" % (code, name, pulse["agencies"][code]["status"], duty))
    print("[PULSE] 항체 %d/13 활성 · HTML 3곳 해시 일치=%s · 종합=%s"
          % (pulse["antibodies"]["active"], pulse["html_integrity"]["hash_unified"], pulse["overall"]))
    print("[PULSE-OK] 6대 청사 무인 박동 #%d 완료 (%s)" % (pulse["beat_count"], now))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_pulse())
    except Exception as e:
        print("[PULSE-FAIL] 예기치 않은 오류: %s" % e)
        sys.exit(1)
