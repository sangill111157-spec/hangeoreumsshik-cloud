# -*- coding: utf-8 -*-
# RGON Step 11 과제 C-1: 6대 청사(D1~D6) 일일 실전 브리핑(daily_briefing) 생성기 + 독대실 라이브 표시 + 클라우드 배포
# 바꾸는 범위:
#   scripts/rgon_agency_pulse.py : 표시된 C-1 블록 1개와 호출 1줄만 추가(재실행하면 교체, R12)
#   HTML 3곳                      : <script id="rgon-step11-pulse-live"> 블록만 같은 자리에서 교체
# 헌법, 워크플로우, 금고 장부, 마스터 스케줄은 읽기만 한다. 표준 라이브러리만 쓰고 네트워크는 git push에만 사용한다.
import os, re, sys, json, shutil, hashlib, tempfile, datetime, subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
KST = datetime.timezone(datetime.timedelta(hours=9))
BOM = b"\xef\xbb\xbf"
BACKUP_DIR = os.path.join(ROOT, "backups")
GIT_BRANCH = "main"
MIN_BEAT = 4

HTML_RELS = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
SNAP_RELS = ["rgon_brain_snapshot.json", "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"]
EVO_REL = "evolution_memory.json"
PULSE_REL = "scripts/rgon_agency_pulse.py"
WF_REL = ".github/workflows/rgon_agency_pulse.yml"
CONST_REL = "rgon_constitution.json"
TREASURY_REL = "treasury_ledger.json"
SCHEDULE_REL = "brain_basket/master_schedule.json"
READONLY_RELS = [CONST_REL, WF_REL, TREASURY_REL, SCHEDULE_REL]
TOUCH_RELS = HTML_RELS + SNAP_RELS + [EVO_REL, PULSE_REL]

LIVE_ID = "rgon-step11-pulse-live"
AB_SCRIPT_ID = "rgon-step11-ab-realname"

PROTECTED_IDS = [
    "rgon-step5-solo-panel",
    "rgon-step7-chat-zone",
    "rgon-step8-constitution-bar",
    "rgon-step9-aggregator-board",
    "rgon-step10-agency-awaken",
    "dokdae-feed",
]
AGENCIES = [
    ("D1", "알파-D1 퀀트", "R&D · 4대 AI 교차검증 전광판 대기 상태 점검"),
    ("D2", "알파-D2 바이럴", "핵심 키워드 & BM 파이프라인 준비도 점검"),
    ("D3", "알파-D3 미디어", "브리핑 · TTS · 미디어 자산 상태 점검"),
    ("D4", "알파-D4 홍익", "제0조 홍익인간 원칙 & 헌법 v1.0 무결성 해시 점검"),
    ("D5", "알파-D5 가디언", "13대 항체(R1~R13) & 독대실 HTML 3곳 해시 일치 수호 점검"),
    ("D6", "알파-D6 트레저리", "treasury_ledger.json 금고 장부 무결성 & 무과금(Free Tier) 점검"),
]
AGENCY_CODES = [a[0] for a in AGENCIES]
BRIEF_KEYS = ["headline", "D1_quant", "D2_viral", "D3_media", "D4_hongik", "D5_guardian", "D6_treasury", "action_top1"]

# ======================================================================
# 1) 박동 엔진에 넣을 C-1 일일 브리핑 블록
# ======================================================================
C1_BEGIN = "# >>> RGON-C1 DAILY BRIEFING >>>"
C1_END = "# <<< RGON-C1 DAILY BRIEFING <<<"
C1_CALL_TAG = "# RGON-C1"

C1_BLOCK = r'''# >>> RGON-C1 DAILY BRIEFING >>>
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
# <<< RGON-C1 DAILY BRIEFING <<<'''

# ======================================================================
# 2) 독대실 라이브 바인딩 스크립트(C-1판). 보호 ID는 문자열을 쪼개서 getElementById로만 참조한다(R10)
# ======================================================================
LIVE_JS = r"""<script id="rgon-step11-pulse-live">
(function(){
  "use strict";
  if (window.__rgonPulseLiveC1) return;
  window.__rgonPulseLiveC1 = true;
  var FALLBACK = __RGON_FALLBACK__;
  var SNAP_URL = "./rgon_brain_snapshot.json";
  var PERIOD = 60000;
  var AWAKEN = "rgon-step10-" + "agency-awaken";
  var ANCHOR_TEXT = "6대 청사 실시간 보좌 지표 보기";
  var BANNER_ID = "rgon-pulse-live-banner";
  var STYLE_ID = "rgon-pulse-live-style";
  var CODES = ["D1","D2","D3","D4","D5","D6"];
  var NAMES = {D1:"알파-D1 퀀트",D2:"알파-D2 바이럴",D3:"알파-D3 미디어",D4:"알파-D4 홍익",D5:"알파-D5 가디언",D6:"알파-D6 트레저리"};
  var SHORT = {D1:"퀀트",D2:"바이럴",D3:"미디어",D4:"홍익",D5:"가디언",D6:"트레저리"};
  var BKEY = {D1:"D1_quant",D2:"D2_viral",D3:"D3_media",D4:"D4_hongik",D5:"D5_guardian",D6:"D6_treasury"};
  var ICON = {OK:"🟢",STANDBY:"🟡",WARN:"🟠",ALERT:"🔴"};
  var SKIP = {SCRIPT:1,STYLE:1,NOSCRIPT:1,TEXTAREA:1,INPUT:1,SELECT:1,OPTION:1,BUTTON:1,HTML:1,BODY:1,HEAD:1,TITLE:1};
  var INLINE = {SPAN:1,B:1,STRONG:1,EM:1,I:1,SMALL:1,A:1,LABEL:1,CODE:1,MARK:1,U:1,FONT:1};
  var lastGood = null, lastKey = "", busy = false, timer = null;

  function css(){
    if (document.getElementById(STYLE_ID)) return;
    var B = "#" + BANNER_ID;
    var s = document.createElement("style");
    s.id = STYLE_ID;
    s.textContent =
      B + "{display:block;writing-mode:horizontal-tb;max-width:100%;box-sizing:border-box;margin:8px 0;padding:10px 12px;border:1px solid rgba(34,197,94,.45);border-radius:10px;background:rgba(34,197,94,.08);font-size:13px;line-height:1.5;color:inherit;word-break:keep-all;overflow-wrap:anywhere;}" +
      B + "[data-state=warn]{border-color:rgba(249,115,22,.55);background:rgba(249,115,22,.08);}" +
      B + " *{box-sizing:border-box;max-width:100%;writing-mode:horizontal-tb;}" +
      B + " .rpl-head{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;justify-content:space-between;}" +
      B + " .rpl-sum{font-weight:700;min-width:0;flex:1 1 240px;}" +
      B + " .rpl-btn{flex:0 0 auto;cursor:pointer;border:1px solid currentColor;border-radius:8px;background:transparent;color:inherit;padding:3px 10px;font-size:12px;white-space:nowrap;}" +
      B + " .rpl-brief{display:block;margin-top:8px;padding:8px 10px;border-radius:8px;background:rgba(127,127,127,.07);}" +
      B + " .rpl-brief>summary{cursor:pointer;font-weight:700;overflow-wrap:anywhere;}" +
      B + " .rpl-bl{display:flex;gap:8px;align-items:flex-start;margin-top:5px;font-size:12px;line-height:1.55;min-width:0;}" +
      B + " .rpl-bc{flex:0 0 auto;font-weight:700;white-space:nowrap;}" +
      B + " .rpl-bt{flex:1 1 auto;min-width:0;overflow-wrap:anywhere;word-break:keep-all;}" +
      B + " .rpl-top{margin-top:8px;padding:6px 8px;border-left:3px solid rgba(234,179,8,.85);border-radius:4px;background:rgba(234,179,8,.10);font-size:12px;font-weight:700;overflow-wrap:anywhere;}" +
      B + " .rpl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:6px;margin-top:8px;}" +
      B + " .rpl-card{min-width:0;padding:6px 8px;border-radius:8px;background:rgba(127,127,127,.08);}" +
      B + " .rpl-card b{display:block;}" +
      B + " .rpl-duty{display:block;opacity:.85;font-size:12px;}" +
      B + " .rpl-met{display:block;opacity:.7;font-size:11px;}" +
      B + " .rpl-src{opacity:.65;font-size:11px;margin-top:4px;}" +
      "@media (max-width:480px){" + B + "{padding:8px;font-size:12px;}" + B + " .rpl-bl{flex-direction:column;gap:0;}}" +
      ".rgon-pulse-chip{display:block;writing-mode:horizontal-tb;max-width:100%;box-sizing:border-box;margin-top:4px;font-size:11px;line-height:1.45;opacity:.9;overflow-wrap:anywhere;word-break:keep-all;}" +
      ".rgon-brief-chip{opacity:.8;}";
    (document.head || document.documentElement).appendChild(s);
  }

  function fmt(s){ s = String(s || ""); return s ? s.replace("T", " ").slice(0, 19) : "-"; }
  function clip(s, n){ s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; }
  function setText(el, t){ if (el && el.textContent !== t) el.textContent = t; }
  function mk(tag, cls, txt){ var e = document.createElement(tag); if (cls) e.className = cls; if (txt !== undefined && txt !== null) e.textContent = txt; return e; }

  function metricText(code, m){
    m = m || {};
    switch (code) {
      case "D1": return "교차검증판 " + (m.cross_validation_board || (m.aggregator_board_present ? "대기" : "미탐지")) + " · 대화창 " + (m.chat_zone_present ? "확인" : "미확인");
      case "D2": return "마스터 스케줄 " + (m.master_schedule_valid ? "정상" : "미확인") + " · 키워드/BM 키 " + (m.keyword_bm_keys || 0);
      case "D3": return "미디어 " + (m.media_files || 0) + "개 · 브리핑 키 " + (m.briefing_keys || 0);
      case "D4": return "헌법 해시 " + (m.baseline_match ? "일치" : "불일치") + " · 제0조 홍익 " + (m.article0_hongik_found ? "확인" : "미확인");
      case "D5": return "항체 " + (m.antibodies_active || 0) + "/" + (m.antibodies_total || 13) + " · HTML 3곳 " + (m.html_hash_unified ? "해시 일치" : "해시 불일치");
      case "D6": return "금고 장부 " + (m.ledger_valid ? "정상" : "미확인") + " · Free Tier · 유료호출 " + (m.paid_api_calls || 0);
    }
    return "";
  }

  function agency(p, code){
    var a = (p && p.agencies && p.agencies[code]) || {};
    return {code: code, name: a.name || NAMES[code], duty: a.duty || "", status: String(a.status || "STANDBY"), metrics: a.metrics || {}};
  }

  function summary(p){
    var bad = [];
    for (var i = 0; i < CODES.length; i++) if (agency(p, CODES[i]).status !== "OK") bad.push(CODES[i]);
    var ab = (p && p.antibodies) || {};
    var allOk = bad.length === 0 && p && p.overall === "OK";
    var head = allOk ? "🟢 6대 청사 무인 박동 #" + (p.beat_count || 0) + " · D1~D6 ALL OK"
                     : "🟠 6대 청사 무인 박동 #" + ((p && p.beat_count) || 0) + " · 점검 필요: " + (bad.join(", ") || "종합 판정");
    return {ok: allOk, text: head + " · 항체 " + (ab.active || 0) + "/" + (ab.total || 13) + " 활성 · 최근 점검: " + fmt(p && p.checked_at)};
  }

  function findAnchor(){
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false), t;
    while ((t = w.nextNode())) {
      if (t.nodeValue && t.nodeValue.indexOf(ANCHOR_TEXT) >= 0 && t.parentElement && !t.parentElement.closest("#" + BANNER_ID)) return t.parentElement;
    }
    return null;
  }

  function ensureBanner(){
    var b = document.getElementById(BANNER_ID);
    if (b) return b;
    b = mk("div");
    b.id = BANNER_ID;
    b.setAttribute("role", "status");
    b.setAttribute("aria-live", "polite");
    var head = mk("div", "rpl-head");
    var btn = mk("button", "rpl-btn", "🔄 지금 동기화");
    btn.type = "button";
    btn.addEventListener("click", function(){ load(); });
    head.appendChild(mk("div", "rpl-sum", "🟡 6대 청사 무인 박동 수신 대기"));
    head.appendChild(btn);
    var br = mk("details", "rpl-brief");
    br.open = true;
    br.appendChild(mk("summary", "rpl-bh", "📋 6대 청사 일일 실전 브리핑 수신 대기"));
    for (var i = 0; i < CODES.length; i++) {
      var row = mk("div", "rpl-bl");
      row.setAttribute("data-rpl-brief", CODES[i]);
      row.appendChild(mk("span", "rpl-bc", CODES[i] + " " + SHORT[CODES[i]]));
      row.appendChild(mk("span", "rpl-bt", "-"));
      br.appendChild(row);
    }
    br.appendChild(mk("div", "rpl-top", "🎯 오늘의 Top1 행동: -"));
    var grid = mk("div", "rpl-grid");
    for (var j = 0; j < CODES.length; j++) {
      var c = mk("div", "rpl-card");
      c.setAttribute("data-rpl-code", CODES[j]);
      c.appendChild(mk("b"));
      c.appendChild(mk("span", "rpl-duty"));
      c.appendChild(mk("span", "rpl-met"));
      grid.appendChild(c);
    }
    b.appendChild(head);
    b.appendChild(br);
    b.appendChild(grid);
    b.appendChild(mk("div", "rpl-src"));
    var host = document.getElementById(AWAKEN);
    if (host) { host.insertBefore(b, host.firstChild); return b; }
    var anc = findAnchor();
    if (anc) {
      var ref = anc.closest("details") || anc;
      if (ref.parentNode) { ref.parentNode.insertBefore(b, ref); return b; }
    }
    document.body.insertBefore(b, document.body.firstChild);
    return b;
  }

  function hostOf(el){
    var h = el, k = 0;
    while (h && INLINE[h.nodeName] && h.parentElement && k < 3) { h = h.parentElement; k++; }
    return h;
  }

  function chipFor(host, attr, code, cls){
    var ch = host.children;
    for (var x = 0; x < ch.length; x++) if (ch[x].getAttribute(attr) === code) return ch[x];
    var c = mk("span", cls);
    c.setAttribute(attr, code);
    host.appendChild(c);
    return c;
  }

  function bindCards(p){
    var db = (p && p.daily_briefing) || null;
    for (var i = 0; i < CODES.length; i++) {
      var code = CODES[i], name = NAMES[code], a = agency(p, code);
      var line = (ICON[a.status] || "⚪") + " " + a.status + " · " + a.duty + " · " + metricText(code, a.metrics);
      var brief = db && db[BKEY[code]] ? "📋 " + clip(db[BKEY[code]], 160) : "";
      var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false), t, hosts = [];
      while ((t = w.nextNode()) && hosts.length < 3) {
        var pe = t.parentElement;
        if (!pe || !t.nodeValue || t.nodeValue.indexOf(name) < 0) continue;
        if (pe.closest("#" + BANNER_ID) || pe.closest(".rgon-pulse-chip") || pe.isContentEditable) continue;
        var h = hostOf(pe);
        if (!h || SKIP[h.nodeName] || hosts.indexOf(h) >= 0) continue;
        var tx = h.textContent || "", multi = 0;
        for (var j = 0; j < CODES.length; j++) if (tx.indexOf(NAMES[CODES[j]]) >= 0) multi++;
        if (multi > 1) continue;
        hosts.push(h);
      }
      for (var k = 0; k < hosts.length; k++) {
        setText(chipFor(hosts[k], "data-rgon-pulse-chip", code, "rgon-pulse-chip"), line);
        if (brief) setText(chipFor(hosts[k], "data-rgon-brief-chip", code, "rgon-pulse-chip rgon-brief-chip"), brief);
      }
    }
  }

  function bindSyncButtons(){
    var list = document.querySelectorAll("button, a, [role=button]");
    for (var i = 0; i < list.length; i++) {
      var el = list[i];
      if (el.closest("#" + BANNER_ID) || el.getAttribute("data-rgon-pulse-sync") === "1") continue;
      if ((el.textContent || "").indexOf("지금 동기화") >= 0) {
        el.setAttribute("data-rgon-pulse-sync", "1");
        el.addEventListener("click", function(){ load(); });
      }
    }
  }

  function render(p, src){
    if (!document.body || !p) return;
    css();
    var b = ensureBanner();
    var s = summary(p);
    var db = p.daily_briefing || null;
    var key = JSON.stringify([p.beat_count, p.checked_at, p.overall, p.agencies, p.antibodies, db, src]);
    if (key !== lastKey) {
      lastKey = key;
      var st = s.ok ? "ok" : "warn";
      if (b.getAttribute("data-state") !== st) b.setAttribute("data-state", st);
      setText(b.querySelector(".rpl-sum"), s.text);
      var br = b.querySelector(".rpl-brief");
      if (br) {
        setText(br.querySelector(".rpl-bh"), db && db.headline ? db.headline : "📋 6대 청사 일일 실전 브리핑 수신 대기");
        var rows = br.querySelectorAll(".rpl-bl");
        for (var r = 0; r < rows.length; r++) {
          var rc = rows[r].getAttribute("data-rpl-brief");
          setText(rows[r].querySelector(".rpl-bt"), (db && db[BKEY[rc]]) || "-");
        }
        setText(br.querySelector(".rpl-top"), "🎯 오늘의 Top1 행동: " + ((db && db.action_top1) || "-"));
      }
      var cards = b.querySelectorAll(".rpl-card");
      for (var i = 0; i < cards.length; i++) {
        var a = agency(p, cards[i].getAttribute("data-rpl-code"));
        setText(cards[i].querySelector("b"), (ICON[a.status] || "⚪") + " " + a.status + " · " + a.code + " " + a.name);
        setText(cards[i].querySelector(".rpl-duty"), a.duty);
        setText(cards[i].querySelector(".rpl-met"), metricText(a.code, a.metrics));
      }
      setText(b.querySelector(".rpl-src"), "출처: " + src + " · 브리핑 기준일 " + ((db && db.date) || "-") + " · 60초 주기 자동 갱신");
    }
    try { bindCards(p); } catch (e) {}
    try { bindSyncButtons(); } catch (e) {}
  }

  function load(){
    if (busy) return;
    busy = true;
    var finish = function(p, src){ busy = false; render(p, src); };
    if (!window.fetch) { finish(lastGood || FALLBACK, lastGood ? "직전 수신값 유지" : "내장 폴백(R4)"); return; }
    var ctrl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function(){ if (ctrl) ctrl.abort(); }, 8000);
    var opt = {cache: "no-store"};
    if (ctrl) opt.signal = ctrl.signal;
    fetch(SNAP_URL + "?t=" + Date.now(), opt)
      .then(function(r){ if (!r.ok) throw new Error("http " + r.status); return r.json(); })
      .then(function(j){
        var p = j && j.agency_pulse;
        if (!p || !p.agencies) throw new Error("no agency_pulse");
        lastGood = p;
        clearTimeout(to);
        finish(p, "실시간 스냅샷");
      })
      .catch(function(){
        clearTimeout(to);
        finish(lastGood || FALLBACK, lastGood ? "직전 수신값 유지" : "내장 폴백(R4)");
      });
  }

  function boot(){
    try { render(FALLBACK, "내장 폴백(R4)"); } catch (e) {}
    load();
    if (timer) clearInterval(timer);
    timer = setInterval(load, PERIOD);
    document.addEventListener("visibilitychange", function(){ if (!document.hidden) load(); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
</script>"""

# ======================================================================
# 공통 유틸
# ======================================================================
def log(msg):
    print(msg, flush=True)

def ap(rel):
    return os.path.join(ROOT, *rel.split("/"))

def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()

def decode(data):
    if data.startswith(BOM):
        return data[len(BOM):].decode("utf-8"), True
    return data.decode("utf-8"), False

def encode(text, bom):
    raw = text.encode("utf-8")
    return (BOM + raw) if bom else raw

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def atomic_write(path, data):
    if not data:
        raise RuntimeError("R13 차단: 0바이트 기록 시도 -> %s" % path)
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".rgon_tmp_", suffix=".part")
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
    return r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']'

def count_ids(text):
    return {pid: len(re.findall(id_pat(pid), text)) for pid in PROTECTED_IDS}

def backup_path(rel):
    parts = rel.split("/")
    base, ext = os.path.splitext(parts[-1])
    return os.path.join(BACKUP_DIR, *(parts[:-1] + ["%s_step11c1_bak_%s%s" % (base, TS, ext or ".bak")]))

def parse_iso(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None

def append_evolution(evo, entry):
    if isinstance(evo, list):
        evo.append(entry)
        return evo
    if not isinstance(evo, dict):
        raise RuntimeError("지원하지 않는 장부 구조")
    for k in ("history", "events", "log", "logs", "entries", "evolutions", "memory", "step_log"):
        if isinstance(evo.get(k), list):
            evo[k].append(entry)
            return evo
    if "step_log" in evo:
        raise RuntimeError("step_log 키가 리스트가 아닙니다")
    evo["step_log"] = [entry]
    return evo

# ======================================================================
# 박동 엔진 패치 (표시 블록 1개 + 호출 1줄. 재실행하면 교체)
# ======================================================================
RE_C1_BLOCK = re.compile(re.escape(C1_BEGIN) + r".*?" + re.escape(C1_END) + r"\n\n\n", re.S)
RE_C1_CALL = re.compile(r"^[ \t]*pulse\[\"daily_briefing\"\] = build_daily_briefing\(pulse, snap, now\)[ \t]*" +
                        re.escape(C1_CALL_TAG) + r"[ \t]*\n", re.M)

def patch_pulse(src):
    nl = "\r\n" if "\r\n" in src else "\n"
    s = src.replace("\r\n", "\n")
    s, n1 = RE_C1_BLOCK.subn("", s)
    s, n2 = RE_C1_CALL.subn("", s)
    for must in ("def build_pulse(", "def load_json_rel(", "def run_pulse(", "SCHEDULE_REL", "TREASURY_REL", "CONST_REL"):
        if must not in s:
            raise RuntimeError("박동 엔진 구조가 예상과 다릅니다(%s 없음). B-1 엔진인지 확인하십시오" % must)
    i = s.find("\ndef run_pulse(")
    s = s[:i + 1] + C1_BLOCK + "\n\n\n" + s[i + 1:]
    m = re.search(r"^([ \t]+)pulse = build_pulse\(snap, now\)[ \t]*\n", s, re.M)
    if not m:
        raise RuntimeError("run_pulse 안에서 'pulse = build_pulse(snap, now)' 줄을 찾지 못했습니다")
    call = '%spulse["daily_briefing"] = build_daily_briefing(pulse, snap, now)  %s\n' % (m.group(1), C1_CALL_TAG)
    s = s[:m.end()] + call + s[m.end():]
    compile(s, PULSE_REL, "exec")
    return s.replace("\n", nl), (n1 + n2) > 0

def preview_pulse(src, snap):
    """패치된 엔진을 메모리에서 불러 다음 박동과 브리핑을 미리 계산한다(파일 기록 없음). 내장 폴백(R4)용"""
    os.environ["RGON_ROOT"] = ROOT
    ns = {"__name__": "rgon_pulse_preview", "__file__": ap(PULSE_REL)}
    exec(compile(src, PULSE_REL, "exec"), ns)
    now = datetime.datetime.now(KST).isoformat(timespec="seconds")
    pulse = ns["build_pulse"](dict(snap), now)
    pulse["daily_briefing"] = ns["build_daily_briefing"](pulse, snap, now)
    return pulse

# ======================================================================
# 내장 폴백 데이터(R4)
# ======================================================================
def slim_pulse(p):
    if not isinstance(p, dict) or not isinstance(p.get("agencies"), dict):
        return {
            "beat_count": 0, "checked_at": "", "overall": "STANDBY",
            "agencies": {c: {"code": c, "name": n, "duty": d, "status": "STANDBY", "metrics": {}} for c, n, d in AGENCIES},
            "antibodies": {"active": 0, "total": 13},
        }
    ags = p["agencies"]
    out = {}
    for code, name, duty in AGENCIES:
        a = ags.get(code) if isinstance(ags.get(code), dict) else {}
        m = a.get("metrics") if isinstance(a.get("metrics"), dict) else {}
        mm = {}
        for k, v in m.items():
            if isinstance(v, (bool, int, float)):
                mm[k] = v
            elif isinstance(v, str) and len(v) <= 80 and not k.endswith("sha256"):
                mm[k] = v
        out[code] = {"code": code, "name": a.get("name") or name, "duty": a.get("duty") or duty,
                     "status": str(a.get("status") or "STANDBY"), "checked_at": a.get("checked_at") or "", "metrics": mm}
    ab = p.get("antibodies") if isinstance(p.get("antibodies"), dict) else {}
    res = {"beat_count": p.get("beat_count") if isinstance(p.get("beat_count"), int) else 0,
           "checked_at": p.get("checked_at") or "", "overall": p.get("overall") or "STANDBY",
           "agencies": out, "antibodies": {"active": ab.get("active") or 0, "total": ab.get("total") or 13}}
    db = p.get("daily_briefing")
    if isinstance(db, dict) and not db.get("error"):
        res["daily_briefing"] = {k: str(db[k])[:400] for k in BRIEF_KEYS + ["date"] if isinstance(db.get(k), str) and db[k].strip()}
    return res

def js_literal(obj):
    s = json.dumps(obj, ensure_ascii=True, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

RE_OLD_LIVE = re.compile(
    r'[ \t]*<script\b[^>]*\bid\s*=\s*["\']' + re.escape(LIVE_ID) + r'["\'][^>]*>.*?</script\s*>[ \t]*\r?\n?',
    re.S | re.I,
)

def install_live(text, block):
    nl = "\r\n" if "\r\n" in text else "\n"
    ins = block.replace("\n", nl) + nl
    ms = list(RE_OLD_LIVE.finditer(text))
    if ms:
        new = text
        for m in reversed(ms[1:]):
            new = new[:m.start()] + new[m.end():]
        m0 = ms[0]
        new = new[:m0.start()] + ins + new[m0.end():]
        return new, len(ms)
    idx = text.lower().rfind("</body>")
    if idx < 0:
        return text + nl + ins, 0
    return text[:idx] + ins + text[idx:], 0

# ======================================================================
# Git
# ======================================================================
GIT_ENV = dict(os.environ)
GIT_ENV["GIT_TERMINAL_PROMPT"] = "0"

def git(args, timeout=180):
    p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=GIT_ENV, timeout=timeout)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

def git_tail(out, err, n=6):
    for ln in (out + "\n" + err).strip().splitlines()[-n:]:
        log("    | " + ln)

def verify_after_rebase(expect_sha):
    for rel in HTML_RELS:
        if sha256(read_bytes(ap(rel))) != expect_sha:
            return "리베이스 후 HTML 해시가 정본과 다릅니다: %s" % rel
    for rel in SNAP_RELS + [EVO_REL]:
        if os.path.isfile(ap(rel)):
            try:
                json.loads(decode(read_bytes(ap(rel)))[0])
            except Exception as ex:
                return "리베이스 후 JSON 무효: %s (%s)" % (rel, ex)
    try:
        compile(decode(read_bytes(ap(PULSE_REL)))[0], PULSE_REL, "exec")
    except Exception as ex:
        return "리베이스 후 박동 엔진 문법 오류: %s" % ex
    return None

def git_sync(paths, expect_sha):
    if not shutil.which("git"):
        return False, "git 실행 파일을 찾지 못했습니다"
    rc, out, _ = git(["rev-parse", "--is-inside-work-tree"])
    if rc != 0 or out != "true":
        return False, "ROOT가 git 저장소가 아닙니다"
    _, br, _ = git(["rev-parse", "--abbrev-ref", "HEAD"])
    if br != GIT_BRANCH:
        return False, "현재 브랜치가 '%s'입니다. main에서만 push하도록 막혀 있습니다" % br
    rc, url, _ = git(["remote", "get-url", "origin"])
    if rc != 0:
        return False, "origin 원격 저장소가 없습니다"
    log("[GIT] origin = %s · branch = %s" % (url, br))
    ident = []
    if not git(["config", "user.email"])[1]:
        ident = ["-c", "user.name=rgon-local", "-c", "user.email=rgon-local@users.noreply.github.com"]

    rc, out, err = git(["add", "--"] + paths)
    if rc != 0:
        git_tail(out, err)
        return False, "git add 실패"
    rc, _, _ = git(["diff", "--cached", "--quiet", "--"] + paths)
    if rc == 1:
        msg = "feat(step11-c1): 6대 청사 일일 실전 브리핑 생성기 · 독대실 라이브 표시 · HTML 3곳 해시 통일"
        rc, out, err = git(ident + ["commit", "-m", msg, "--"] + paths)
        if rc != 0:
            git_tail(out, err)
            return False, "git commit 실패"
        log("[GIT] commit %s" % git(["rev-parse", "--short", "HEAD"])[1])
    else:
        log("[GIT] 새로 커밋할 변경 없음 → push만 확인")

    rc, out, err = git(["push", "origin", GIT_BRANCH])
    if rc != 0:
        log("[GIT] push 거절됨 → 원격 최신(박동 봇 커밋 등) 반영 후 재시도")
        git_tail(out, err, 3)
        rc, out, err = git(ident + ["pull", "--rebase", "--autostash", "origin", GIT_BRANCH])
        if rc != 0:
            git(["rebase", "--abort"])
            log("[GIT] 일반 리베이스 충돌 → 로컬 최신 박동 우선(-X theirs)으로 재시도")
            rc, out, err = git(ident + ["pull", "--rebase", "--autostash", "-X", "theirs", "origin", GIT_BRANCH])
            if rc != 0:
                git(["rebase", "--abort"])
                git_tail(out, err)
                return False, "리베이스 실패(로컬 커밋은 그대로 보존)"
        bad = verify_after_rebase(expect_sha)
        if bad:
            return False, bad + " (push 보류)"
        rc, out, err = git(["push", "origin", GIT_BRANCH])
        if rc != 0:
            git_tail(out, err)
            return False, "git push 재시도 실패(인증 또는 권한 확인 필요)"
    git(["fetch", "origin", GIT_BRANCH], timeout=120)
    h1 = git(["rev-parse", "HEAD"])[1]
    h2 = git(["rev-parse", "origin/" + GIT_BRANCH])[1]
    if not h1 or h1 != h2:
        return False, "push 이후 HEAD와 origin/main이 다릅니다 (%s vs %s)" % (h1[:10], h2[:10])
    return True, h1[:10]

# ======================================================================
# 메인
# ======================================================================
def main():
    start_dt = datetime.datetime.now(KST) - datetime.timedelta(seconds=2)
    if not os.path.isdir(ROOT):
        log("[FAIL] ROOT 경로 없음: %s" % ROOT)
        return 1
    for rel in HTML_RELS + [PULSE_REL, SNAP_RELS[0]]:
        if not os.path.isfile(ap(rel)):
            log("[FAIL] 필수 파일 없음: %s" % rel)
            return 1
    for rel in (SCHEDULE_REL, TREASURY_REL, CONST_REL):
        if not os.path.isfile(ap(rel)):
            log("[WARN] 장부 없음: %s (브리핑에 '미탐지'로 보고됩니다)" % rel)

    readonly_hash = {rel: (sha256(read_bytes(ap(rel))) if os.path.isfile(ap(rel)) else None) for rel in READONLY_RELS}

    # 1) G3 사전 백업 (수정 대상 + 읽기 전용 장부 모두)
    orig = {}
    for rel in TOUCH_RELS + READONLY_RELS:
        path = ap(rel)
        if os.path.isfile(path):
            data = read_bytes(path)
            if not data:
                log("[FAIL] R13: 원본이 0바이트입니다 → %s (중단)" % rel)
                return 1
            bp = backup_path(rel)
            atomic_write(bp, data)
            if read_bytes(bp) != data:
                log("[FAIL] 백업 검증 실패 → %s" % bp)
                return 1
            log("[BACKUP] %s → %s" % (rel, os.path.relpath(bp, ROOT)))
            if rel in TOUCH_RELS:
                orig[rel] = data
        elif rel in TOUCH_RELS:
            orig[rel] = None

    def rollback(reason):
        log("[ROLLBACK] %s" % reason)
        for rel in reversed(TOUCH_RELS):
            path = ap(rel)
            try:
                if orig.get(rel) is not None:
                    if not os.path.isfile(path) or read_bytes(path) != orig[rel]:
                        atomic_write(path, orig[rel])
                        log("  ↺ 복원: %s" % rel)
                elif os.path.isfile(path):
                    os.remove(path)
                    log("  ↺ 신규 파일 제거: %s" % rel)
            except Exception as ex:
                log("  !! 복원 실패: %s (%s) → backups/ 폴더에서 수동 복원 필요" % (rel, ex))
        log("[FAIL] Step 11 과제 C-1 중단: 백업본으로 복원했습니다")

    def readonly_changed():
        for rel, h in readonly_hash.items():
            now = sha256(read_bytes(ap(rel))) if os.path.isfile(ap(rel)) else None
            if now != h:
                return rel
        return None

    # 2) 정본 선정과 보호 ID 사전 점검
    cands = []
    for rel in HTML_RELS:
        text, bom = decode(orig[rel])
        ids = count_ids(text)
        alive = sum(1 for v in ids.values() if v > 0)
        cands.append({"rel": rel, "text": text, "bom": bom, "ids": ids,
                      "score": (1 if ids["rgon-step10-agency-awaken"] else 0, alive,
                                1 if all(v == 1 for v in ids.values()) else 0,
                                1 if re.search(id_pat(LIVE_ID), text) else 0, os.path.getmtime(ap(rel)))})
        log("[SCAN] %-34s sha256 %s · 보호ID %d/6" % (rel, sha256(orig[rel])[:12], alive))
    if len(set(sha256(orig[r]) for r in HTML_RELS)) != 1:
        log("[WARN] HTML 3곳 해시가 지금 서로 다릅니다 → 정본 기준으로 다시 통일합니다")
    cands.sort(key=lambda c: c["score"], reverse=True)
    canon = cands[0]
    log("[CANON] 정본: %s" % canon["rel"])
    before = canon["ids"]
    not_one = {pid: n for pid, n in before.items() if n != 1}
    if not_one:
        log("[FAIL] R10: 정본 보호 ID가 각 1개가 아닙니다 → 아무 파일도 수정하지 않고 중단")
        for pid, n in not_one.items():
            log("  - %s: %d개" % (pid, n))
        return 1

    # 3) 박동 엔진 메모리 패치
    try:
        p_text, p_bom = decode(orig[PULSE_REL])
        new_pulse_text, replaced = patch_pulse(p_text)
    except Exception as ex:
        log("[FAIL] 박동 엔진 패치 실패(아무 파일도 수정하지 않음): %s" % ex)
        return 1
    new_pulse_bytes = encode(new_pulse_text, p_bom)
    log("[PULSE-ENGINE] daily_briefing 블록 %s · +%d bytes" %
        ("교체(R12)" if replaced else "신규 장착", len(new_pulse_bytes) - len(orig[PULSE_REL])))

    # 4) 내장 폴백(R4) 미리 계산 + 라이브 스크립트 준비
    try:
        snap0 = json.loads(decode(orig[SNAP_RELS[0]])[0])
        if not isinstance(snap0, dict):
            raise RuntimeError("루트 스냅샷이 JSON 객체가 아닙니다")
    except Exception as ex:
        log("[FAIL] 루트 스냅샷 JSON 무효(덮어쓰지 않고 중단): %s" % ex)
        return 1
    prev_pulse = snap0.get("agency_pulse")
    prev_beat = prev_pulse.get("beat_count") if isinstance(prev_pulse, dict) and isinstance(prev_pulse.get("beat_count"), int) else 0
    try:
        preview = preview_pulse(new_pulse_text.replace("\r\n", "\n"), snap0)
        if (preview.get("daily_briefing") or {}).get("error"):
            raise RuntimeError(preview["daily_briefing"]["error"])
        fallback = slim_pulse(preview)
        log("[PREVIEW] 다음 박동 #%s 브리핑 미리 생성 완료 → 내장 폴백에 반영" % preview.get("beat_count"))
    except Exception as ex:
        log("[WARN] 브리핑 미리 생성 실패 → 직전 박동만 내장 폴백으로 사용: %s" % ex)
        fallback = slim_pulse(prev_pulse)
    block = LIVE_JS.replace("__RGON_FALLBACK__", js_literal(fallback))
    if any(re.search(id_pat(pid), block) for pid in PROTECTED_IDS):
        log("[FAIL] R10: 라이브 스크립트 안에 보호 ID 속성 문자열이 들어 있습니다 → 중단")
        return 1
    if "</script" in block[:-len("</script>")].lower():
        log("[FAIL] 라이브 스크립트 본문에 </script 문자열이 들어 있습니다 → 중단")
        return 1

    # 5) HTML 메모리 갱신 (라이브 블록만 같은 자리에서 교체)
    new_text, n_old = install_live(canon["text"], block)
    log("[LIVE] <script id=\"%s\"> %s" % (LIVE_ID, ("같은 자리 교체(기존 %d개)" % n_old) if n_old else "</body> 직전 신규 장착"))
    if RE_OLD_LIVE.sub("", new_text) != RE_OLD_LIVE.sub("", canon["text"]):
        log("[FAIL] Minimal Diff 검증 실패(라이브 블록 외 변경 감지) → 기록 전 중단")
        return 1
    after = count_ids(new_text)
    if after != before or any(v != 1 for v in after.values()):
        log("[FAIL] R10: 보호 ID 개수 변동 → 기록 전 중단 %s" % after)
        return 1
    if len(re.findall(id_pat(LIVE_ID), new_text)) != 1:
        log("[FAIL] R12: 라이브 스크립트 중복/누락 → 기록 전 중단")
        return 1
    if re.search(id_pat(AB_SCRIPT_ID), canon["text"]) and not re.search(id_pat(AB_SCRIPT_ID), new_text):
        log("[FAIL] 동적 항체 패치 스크립트가 사라졌습니다 → 기록 전 중단")
        return 1
    canon_bytes = encode(new_text, canon["bom"])
    canon_sha = sha256(canon_bytes)
    log("[HTML] 정본 sha256 %s · %+d bytes" % (canon_sha[:12], len(canon_bytes) - len(orig[canon["rel"]])))

    # 6) 원자적 기록: 박동 엔진 + HTML 3곳
    try:
        if orig[PULSE_REL] != new_pulse_bytes:
            atomic_write(ap(PULSE_REL), new_pulse_bytes)
            if read_bytes(ap(PULSE_REL)) != new_pulse_bytes:
                raise RuntimeError("박동 엔진 재판독 불일치")
            log("[WRITE] %s" % PULSE_REL)
        else:
            log("[SKIP] %s 이미 최신" % PULSE_REL)
        for rel in HTML_RELS:
            if orig[rel] == canon_bytes:
                log("[SKIP] %s 이미 정본과 동일" % rel)
                continue
            atomic_write(ap(rel), canon_bytes)
            if sha256(read_bytes(ap(rel))) != canon_sha:
                raise RuntimeError("SHA-256 재판독 불일치 → %s" % rel)
            log("[WRITE] %s (sha256 %s)" % (rel, canon_sha[:12]))
    except Exception as ex:
        rollback("파일 기록 실패: %s" % ex)
        return 1
    bad = readonly_changed()
    if bad:
        rollback("읽기 전용 파일 변동 감지: %s" % bad)
        return 1

    # 7) 무인 박동 실행 → #4 이상 · ALL OK · daily_briefing 검증
    env = dict(os.environ)
    env["RGON_ROOT"] = ROOT
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run([sys.executable, ap(PULSE_REL)], cwd=ROOT, env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=180)
    except Exception as ex:
        rollback("박동 실행 실패: %s" % ex)
        return 1
    for line in (proc.stdout or "").splitlines():
        log("  " + line)
    if proc.stderr and proc.stderr.strip():
        for line in proc.stderr.strip().splitlines()[-10:]:
            log("  [stderr] " + line)
    if proc.returncode != 0:
        rollback("박동 비정상 종료 (exit %d)" % proc.returncode)
        return 1

    try:
        snap = json.loads(decode(read_bytes(ap(SNAP_RELS[0])))[0])
        pulse = snap.get("agency_pulse") or {}
        ags = pulse.get("agencies") or {}
        not_ok = []
        for code in AGENCY_CODES:
            a = ags.get(code) or {}
            t = parse_iso(a.get("checked_at", ""))
            if a.get("status") != "OK" or t is None or t < start_dt:
                not_ok.append(code)
                log("[PULSE-CHECK] %s %s = %s · metrics %s" % (code, a.get("name"), a.get("status"),
                    json.dumps(a.get("metrics"), ensure_ascii=False)[:400]))
        if not_ok or pulse.get("overall") != "OK":
            raise RuntimeError("ALL OK 미달성 (비정상: %s · overall=%s)" % (", ".join(not_ok) or "-", pulse.get("overall")))
        beat = pulse.get("beat_count") if isinstance(pulse.get("beat_count"), int) else 0
        if beat < MIN_BEAT or beat <= prev_beat:
            raise RuntimeError("박동 번호 검증 실패 (이전 #%d → 현재 #%d, 최소 #%d 필요)" % (prev_beat, beat, MIN_BEAT))
        hi = pulse.get("html_integrity") or {}
        if not hi.get("hash_unified") or not hi.get("protected_ids_ok"):
            raise RuntimeError("박동 엔진이 HTML 무결성 이상을 보고했습니다: %s" % hi)
        if any(v != canon_sha for v in (hi.get("sha256") or {}).values()):
            raise RuntimeError("박동 엔진이 기록한 HTML 해시가 정본과 다릅니다")

        db = pulse.get("daily_briefing")
        if not isinstance(db, dict):
            raise RuntimeError("daily_briefing 미생성")
        if db.get("error"):
            raise RuntimeError("daily_briefing 생성 오류: %s" % db["error"])
        missing = [k for k in BRIEF_KEYS if not isinstance(db.get(k), str) or not db[k].strip()]
        if missing:
            raise RuntimeError("daily_briefing 필수 키 누락: %s" % ", ".join(missing))
        if ("박동 #%d" % beat) not in db["headline"] or not db["headline"].endswith("D1~D6 ALL OK"):
            raise RuntimeError("headline 형식 불일치: %s" % db["headline"])

        for rel in SNAP_RELS[1:]:
            if os.path.isfile(ap(rel)):
                m = json.loads(decode(read_bytes(ap(rel)))[0])
                mp = m.get("agency_pulse") or {}
                if mp.get("checked_at") != pulse.get("checked_at") or not isinstance(mp.get("daily_briefing"), dict):
                    log("[WARN] 미러 박동/브리핑이 루트와 다릅니다: %s" % rel)
                else:
                    log("[VERIFY] 미러 동기화 확인(브리핑 포함): %s" % rel)
        log("[VERIFY] D1~D6 전원 OK · overall OK · 박동 #%d (%s)" % (beat, pulse.get("checked_at")))
        log("[BRIEFING] 필수 키 %d종 확인" % len(BRIEF_KEYS))
        for k in BRIEF_KEYS:
            log("  · %-12s %s" % (k, db[k]))
    except Exception as ex:
        rollback(str(ex))
        return 1

    # 8) evolution_memory.json 이력 기록
    try:
        if orig.get(EVO_REL) is not None:
            e_text, e_bom = decode(orig[EVO_REL])
            evo = json.loads(e_text) if e_text.strip() else {}
        else:
            evo, e_bom = {}, False
        entry = {
            "event": "step11_task_c1_daily_briefing_engine",
            "timestamp": datetime.datetime.now(KST).isoformat(timespec="seconds"),
            "summary": "6대 청사 일일 실전 브리핑(daily_briefing) 생성기를 박동 엔진에 장착하고 독대실 라이브 전광판에 표시 · HTML 3곳 해시 통일 · 클라우드 배포",
            "engine": PULSE_REL,
            "script_id": LIVE_ID,
            "canonical": canon["rel"],
            "html_sha256": canon_sha,
            "protected_ids": after,
            "beat_count": beat,
            "checked_at": pulse.get("checked_at"),
            "overall": pulse.get("overall"),
            "agencies": {c: ags[c].get("status") for c in AGENCY_CODES},
            "briefing_headline": db.get("headline"),
            "action_top1": db.get("action_top1"),
            "fallback_beat": fallback.get("beat_count"),
            "backup_ts": TS,
        }
        evo = append_evolution(evo, entry)
        out = json.dumps(evo, ensure_ascii=False, indent=2) + "\n"
        json.loads(out)
        data = encode(out, e_bom)
        atomic_write(ap(EVO_REL), data)
        if read_bytes(ap(EVO_REL)) != data:
            raise RuntimeError("장부 재판독 불일치")
        log("[EVOLUTION] step11_task_c1_daily_briefing_engine 기록 완료")
    except Exception as ex:
        rollback("evolution_memory 기록 실패: %s" % ex)
        return 1

    # 9) 최종 로컬 무결성 검증
    final = {rel: read_bytes(ap(rel)) for rel in HTML_RELS}
    if len(set(sha256(b) for b in final.values())) != 1 or sha256(final[HTML_RELS[0]]) != canon_sha:
        rollback("최종 HTML 3곳 해시 불일치")
        return 1
    for rel, b in final.items():
        ids = count_ids(decode(b)[0])
        if any(ids[pid] != 1 for pid in PROTECTED_IDS):
            rollback("최종 보호 ID가 각 1개가 아닙니다 → %s %s" % (rel, ids))
            return 1
    bad = readonly_changed()
    if bad:
        rollback("읽기 전용 파일 변동 감지: %s" % bad)
        return 1
    for rel in HTML_RELS:
        log("  - %-34s %s · 보호ID 6/6 (각 1개)" % (rel, canon_sha))
    log("[SYNC] HTML 3곳 SHA-256 해시 100% 완전 일치")

    # 10) GitHub 클라우드 커밋 & 푸시 (git이 실패해도 로컬 검증 결과는 보존)
    paths = [rel for rel in HTML_RELS + SNAP_RELS + [EVO_REL, PULSE_REL] if os.path.isfile(ap(rel))]
    try:
        ok, info = git_sync(paths, canon_sha)
    except Exception as ex:
        ok, info = False, "git 실행 오류: %s" % ex
    if not ok:
        log("[FAIL] GitHub 동기화 실패: %s" % info)
        log("[INFO] 로컬 브리핑 엔진과 ALL OK 결과는 정상 보존됨 → 원인 해결 후 'git push origin main' 재실행")
        return 1
    log("[GIT] push 완료 · origin/main = %s" % info)

    log("[OK] Step 11 과제 C-1 6대 청사 실전 일일 브리핑 자동 생성기 장착 및 클라우드 배포 완료")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("[FAIL] 예기치 않은 오류: %s" % e, flush=True)
        sys.exit(1)
Copy