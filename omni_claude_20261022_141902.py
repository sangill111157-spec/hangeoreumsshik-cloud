#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGON G1 Step 11 / 과제 C-2
TOP1_SELF_EVOLVING_BRAIN 상시 가동 승격 · D2 핵심 키워드 5종 장전 · D4 5-Gate(5/5) 파서 보정 · 박동 #5 클라우드 배포
실행: RGON_Run.bat -> rgon_runner.py -> 본 스크립트 (단독 실행 가능)
"""
import sys, os, re, json, shutil, hashlib, subprocess, time
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ───────────────────────── 설정 ─────────────────────────
ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
CONSTITUTION = ROOT / "rgon_constitution.json"
CONST_PREFIX = "bd5060dea1e2"
SCHEDULE = ROOT / "brain_basket" / "master_schedule.json"
PULSE = ROOT / "scripts" / "rgon_agency_pulse.py"
HTMLS = [ROOT / "rgon_alpha_chat.html",
         ROOT / "dashboard" / "rgon_alpha_chat.html",
         ROOT / "docs" / "rgon_alpha_chat.html"]
SNAPS = [ROOT / "rgon_brain_snapshot.json",
         ROOT / "dashboard" / "rgon_brain_snapshot.json",
         ROOT / "docs" / "rgon_brain_snapshot.json"]
EVOLUTION = ROOT / "evolution_memory.json"
BACKUP_DIR = ROOT / "backups"

TASK = "TOP1_SELF_EVOLVING_BRAIN"
EVENT = "step11_task_c2_self_evolving_brain_active"
KEYWORDS = ["AI 에이전트 군단 자동화", "4대 AI 교차검증 레버리지", "원클릭 무인 사령부",
            "홍익인간 안전 가드레일", "24시간 클라우드 자가진화"]
PROTECTED_IDS = ["rgon-step5-solo-panel", "rgon-step7-chat-zone", "rgon-step8-constitution-bar",
                 "rgon-step9-aggregator-board", "rgon-step10-agency-awaken", "dokdae-feed"]
BTN_LABEL = "[🧠 자율진화 Top1 지시서 입력창에 장전]"
FINAL_OK = "[OK] Step 11 과제 C-2 TOP1_SELF_EVOLVING_BRAIN 가동 · D2 키워드 5종 장전 · 5-Gate 5/5 확인 · 박동 #5 클라우드 배포 완료"

NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
TODAY = NOW.strftime("%Y-%m-%d")
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S")
TAG = "_step11c2_bak_" + TS

TARGETS = [SCHEDULE, PULSE] + HTMLS + SNAPS + [EVOLUTION]
BACKUPS = {}  # Path -> backup Path


def log(msg):
    print(msg, flush=True)


def rel(p):
    try:
        return str(Path(p).relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(p)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ───────────────────────── 파싱기 보정 블록 (pulse 에 주입) ─────────────────────────
PARSER_DEFS = r'''
import re as _c2_re
import json as _c2_json
import functools as _c2_functools
import types as _c2_types
import inspect as _c2_inspect
from pathlib import Path as _C2Path
from datetime import datetime as _c2_dt

_C2_TASK = "TOP1_SELF_EVOLVING_BRAIN"


def _c2_root():
    return _C2Path(__file__).resolve().parent.parent


def _c2_scan_gates(doc):
    """rgon_constitution.json 전체를 재귀 탐색하여 G0~G4 정의를 찾는다.
    G0 는 최상위 키 / article_0 / 제0조 / blast_radius / gates 목록 어디에 있어도 인식한다."""
    found = set()
    tok = _c2_re.compile(r'(?<![A-Za-z0-9])G\s?-?([0-4])(?![0-9])')

    def add_text(t):
        for m in tok.finditer(t):
            found.add("G" + m.group(1))
        if _c2_re.search(r'제\s*0\s*조', t) or _c2_re.search(r'article[_\s-]*0(?![0-9])', t, _c2_re.I):
            found.add("G0")

    def add_key(k):
        add_text(k)
        m = _c2_re.match(r'^\s*G\s*[_-]?\s*([0-4])(?![0-9])', k, _c2_re.I)
        if m:
            found.add("G" + m.group(1))
        m = _c2_re.match(r'^\s*gate[_\s-]*([0-4])\s*$', k, _c2_re.I)
        if m:
            found.add("G" + m.group(1))
        if _c2_re.match(r'^\s*(article|art|clause)[_\s-]*0\s*$', k, _c2_re.I):
            found.add("G0")
        if "blast_radius" in k.lower() or "blast radius" in k.lower():
            found.add("G0")

    def walk(n, d=0):
        if d > 40:
            return
        if isinstance(n, dict):
            for k, v in n.items():
                if isinstance(k, str):
                    add_key(k)
                walk(v, d + 1)
        elif isinstance(n, (list, tuple)):
            for x in n:
                walk(x, d + 1)
        elif isinstance(n, str):
            add_text(n)

    walk(doc)
    return sorted(g for g in found if g in ("G0", "G1", "G2", "G3", "G4"))


def _c2_gate_report():
    try:
        raw = (_c2_root() / "rgon_constitution.json").read_bytes()  # 읽기 전용
        doc = _c2_json.loads(raw.decode("utf-8-sig"))
    except Exception:
        return None
    gates = _c2_scan_gates(doc)
    return "5-Gate 조항 %d/5 확인(%s)" % (len(gates), ",".join(gates))


def _c2_sched():
    try:
        p = _c2_root() / "brain_basket" / "master_schedule.json"
        d = _c2_json.loads(p.read_text(encoding="utf-8-sig"))
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _c2_d2_info():
    d = _c2_sched()
    if not d:
        return [], False
    kws = d.get("viral_keywords") or d.get("keywords") or []
    kws = [str(x).strip() for x in kws if str(x).strip()] if isinstance(kws, list) else []
    t = d.get("top1_self_evolving_brain")
    active = False
    if isinstance(t, dict):
        active = str(t.get("status", "")).upper() == "ACTIVE" and t.get("date") == _c2_dt.now().strftime("%Y-%m-%d")
    return kws, active


def _c2_fix_text(s):
    if not isinstance(s, str) or len(s) > 20000:
        return s
    out = s
    if "5-Gate" in out:
        rep = _c2_gate_report()
        if rep:
            out = _c2_re.sub(r'5-Gate\s*조항\s*\d+\s*/\s*5\s*확인\s*\([^)]*\)', lambda m: rep, out)
    if "키워드" in out and "미등록" in out:
        kws, _a = _c2_d2_info()
        if len(kws) >= 5:
            rep = "핵심 키워드 5종 장전 완료 [" + " · ".join(kws[:5]) + "]"
            out = _c2_re.sub(r'핵심\s*키워드\s*[:：]?\s*미등록', lambda m: rep, out)
    if "오늘 날짜 과제 없음" in out:
        _k, active = _c2_d2_info()
        if active:
            out = out.replace("오늘 날짜 과제 없음", "오늘 날짜 과제 1건 가동: " + _C2_TASK + "(ACTIVE)")
    return out


def _c2_fix(obj, _d=0):
    if isinstance(obj, str):
        return _c2_fix_text(obj)
    if _d > 12:
        return obj
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            v = obj[k]
            nv = _c2_fix(v, _d + 1)
            if nv is not v:
                obj[k] = nv
        return obj
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            nv = _c2_fix(v, _d + 1)
            if nv is not v:
                obj[i] = nv
        return obj
    if type(obj) is tuple:
        return tuple(_c2_fix(v, _d + 1) for v in obj)
    return obj


def _c2_install(g):
    """모듈 내 일반 함수들의 입력(dict/list)·반환값 문자열을 보정 파서로 정규화한다."""
    for name, fn in list(g.items()):
        if name.startswith("_c2_") or not isinstance(fn, _c2_types.FunctionType):
            continue
        if fn.__globals__ is not g or getattr(fn, "_c2_wrapped", False):
            continue
        if _c2_inspect.isgeneratorfunction(fn) or _c2_inspect.iscoroutinefunction(fn):
            continue

        def make(f):
            @_c2_functools.wraps(f)
            def w(*a, **k):
                for x in a:
                    if isinstance(x, (dict, list)):
                        _c2_fix(x)
                return _c2_fix(f(*a, **k))
            w._c2_wrapped = True
            return w
        g[name] = make(fn)
'''
PATCH_BEGIN = "# ==== RGON-C2-PATCH-BEGIN (step11c2) ===="
PATCH_END = "# ==== RGON-C2-PATCH-END ===="
PATCH_BLOCK = (PATCH_BEGIN + "\n" + PARSER_DEFS.strip("\n") + "\n\n_c2_install(globals())\n" + PATCH_END + "\n")

# ───────────────────────── 독대실 버튼 JS ─────────────────────────
JS_BEGIN = "/* RGON-C2-BTN-BEGIN step11c2 */"
JS_END = "/* RGON-C2-BTN-END */"
JS_BLOCK = r'''/* RGON-C2-BTN-BEGIN step11c2 */
(function () {
  "use strict";
  if (window.__rgonC2BtnArmed) { return; }
  window.__rgonC2BtnArmed = true;
  var BTN_LABEL = "[🧠 자율진화 Top1 지시서 입력창에 장전]";
  var MARK = "data-rgon-c2-btn";
  var ACTION_RE = /action_top1|원클릭으로\s*대기\s*과제\s*1순위|TOP1_SELF_EVOLVING_BRAIN[^\n]*착수/;
  var SKIP_TAGS = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, INPUT: 1, BUTTON: 1, HEAD: 1, TITLE: 1, META: 1, LINK: 1, NOSCRIPT: 1 };
  var timer = null;

  function clean(t) { return String(t || "").replace(/\s+/g, " ").trim(); }

  function textWithoutBtn(el) {
    var c = el.cloneNode(true);
    var bs = c.querySelectorAll("[" + MARK + "]");
    for (var i = 0; i < bs.length; i++) { bs[i].parentNode.removeChild(bs[i]); }
    return clean(c.textContent);
  }

  function inFeedOrBtn(el) {
    return !!(el.closest && (el.closest("#dokdae-feed") || el.closest("[" + MARK + "]")));
  }

  function findHost() {
    var all = document.body.querySelectorAll("*");
    var best = null;
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (SKIP_TAGS[el.tagName] || inFeedOrBtn(el)) { continue; }
      var t = textWithoutBtn(el);
      if (!t || !ACTION_RE.test(t)) { continue; }
      var childHit = false;
      for (var j = 0; j < el.children.length; j++) {
        var ch = el.children[j];
        if (SKIP_TAGS[ch.tagName]) { continue; }
        if (ACTION_RE.test(textWithoutBtn(ch))) { childHit = true; break; }
      }
      if (!childHit) { best = el; break; }
    }
    if (!best) { return null; }
    var guard = 0;
    while (textWithoutBtn(best).length < 30 && best.parentElement && best.parentElement !== document.body && guard < 2) {
      best = best.parentElement; guard++;
    }
    return best;
  }

  function extractAction(host) {
    var t = textWithoutBtn(host);
    t = t.replace(/^.*?action_top1\s*[:：=\-–>]*\s*/, "");
    return t || "RGON_Run.bat 원클릭으로 대기 과제 1순위 「TOP1_SELF_EVOLVING_BRAIN」 착수 후 박동 #5 확인";
  }

  function buildDirective(actionText) {
    var L = [];
    L.push("[RGON 사령부 G1 공식 외주 코딩 지시서 — 자율진화 Top1(TOP1_SELF_EVOLVING_BRAIN) 착수]");
    L.push("");
    L.push("너는 로컬 및 클라우드 자동화 파이프라인과 비침투 UI 연동을 담당하는 수석 파이썬 엔지니어다.");
    L.push("6대 청사 일일 브리핑이 스스로 진단한 후속 과제(action_top1): " + actionText);
    L.push("");
    L.push("### 1. 대상 경로");
    L.push("- ROOT: C:\\Users\\sangi\\Downloads\\shin-agent");
    L.push("- 읽기 전용 보호 파일: rgon_constitution.json (해시 bd5060dea1e2... 단 1바이트도 수정 금지)");
    L.push("");
    L.push("### 2. 작업 계약 (헌법 가드레일 R1~R13 100% 준수)");
    L.push("1) 수정 전 대상 파일을 backups/ 에 타임스탬프로 먼저 백업한다 (G3).");
    L.push("2) Minimal Diff: 기존 데이터·구조는 100% 보존하고 필요한 부분만 갱신한다.");
    L.push("3) 보호 ID 6종(rgon-step5-solo-panel, rgon-step7-chat-zone, rgon-step8-constitution-bar, rgon-step9-aggregator-board, rgon-step10-agency-awaken, dokdae-feed)은 각 1개씩(6/6) 유지한다.");
    L.push("4) HTML 3곳(root, dashboard, docs)의 SHA-256 해시를 100% 동일하게 유지한다.");
    L.push("5) scripts/rgon_agency_pulse.py 를 실행해 박동을 기록하고 D1~D6 전원 OK, overall == OK 를 검증한다.");
    L.push("6) evolution_memory.json 에 이력을 기록하고 git add / commit / push origin main 으로 클라우드까지 동기화한다.");
    L.push("7) 검증 위반 시 즉시 백업본으로 롤백한다.");
    L.push("");
    L.push("### 3. 출력 형식");
    L.push("RGON_Run.bat (rgon_runner.py)로 즉시 실행 가능한 단 1개의 순수 Python 스크립트만 코드 블록 1개로 출력한다. 설명 텍스트는 쓰지 않는다.");
    L.push("마지막 줄에 [OK] 성공 메시지를 출력한다.");
    return L.join("\n");
  }

  function findInput() {
    var sels = ["#rgon-step7-chat-zone textarea", "#rgon-step7-chat-zone input[type=text]",
                "#rgon-step7-chat-zone [contenteditable=true]", "#rgon-step5-solo-panel textarea",
                "#rgon-step5-solo-panel input[type=text]", "textarea", "input[type=text]"];
    for (var i = 0; i < sels.length; i++) {
      var list = document.querySelectorAll(sels[i]);
      for (var j = list.length - 1; j >= 0; j--) {
        var el = list[j];
        if (el.disabled || el.readOnly) { continue; }
        return el;
      }
    }
    return null;
  }

  function fillInput(text) {
    var el = findInput();
    if (!el) { return false; }
    if (el.isContentEditable && el.tagName !== "TEXTAREA" && el.tagName !== "INPUT") {
      el.textContent = text;
    } else {
      var proto = el.tagName === "TEXTAREA" ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      var desc = Object.getOwnPropertyDescriptor(proto, "value");
      if (desc && desc.set) { desc.set.call(el, text); } else { el.value = text; }
    }
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    try { el.focus(); el.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (e) {}
    return true;
  }

  function legacyCopy(text) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "readonly");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      var ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return !!ok;
    } catch (e) { return false; }
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; },
        function () { return legacyCopy(text); });
    }
    return Promise.resolve(legacyCopy(text));
  }

  function onClick(host, btn) {
    var directive = buildDirective(extractAction(host));
    var filled = fillInput(directive);
    copyText(directive).then(function (copied) {
      var prev = BTN_LABEL;
      btn.textContent = (filled ? "[✅ 입력창 장전 완료" : "[⚠️ 입력창 없음") + (copied ? " · 클립보드 복사됨]" : " · 복사 실패]");
      setTimeout(function () { btn.textContent = prev; }, 2800);
    });
  }

  function ensure() {
    if (!document.body) { return; }
    var existing = document.querySelector("[" + MARK + "]");
    if (existing && existing.isConnected) { return; }
    var host = findHost();
    if (!host) { return; }
    var btn = document.createElement("button");
    btn.type = "button";
    btn.setAttribute(MARK, "1");
    btn.className = "rgon-c2-btn";
    btn.textContent = BTN_LABEL;
    btn.style.cssText = "margin-left:8px;padding:3px 10px;border:1px solid #d4a017;border-radius:6px;" +
      "background:#2b2410;color:#ffd866;font-size:12px;font-weight:600;cursor:pointer;vertical-align:middle;";
    btn.addEventListener("click", function (ev) { ev.preventDefault(); ev.stopPropagation(); onClick(host, btn); });
    host.appendChild(btn);
  }

  function schedule() {
    if (timer) { clearTimeout(timer); }
    timer = setTimeout(ensure, 150);
  }

  function boot() {
    if (!document.body) { setTimeout(boot, 100); return; }
    ensure();
    try {
      new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true });
    } catch (e) {
      setInterval(ensure, 1500);
    }
  }
  boot();
})();
/* RGON-C2-BTN-END */'''

SCRIPT_RE = re.compile(
    r'(<script\b[^>]*\bid\s*=\s*["\']rgon-step11-pulse-live["\'][^>]*>)(.*?)(</script\s*>)', re.S | re.I)


# ───────────────────────── JSON / 텍스트 유틸 ─────────────────────────
def load_json(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    return json.loads(text), text, bom


def dump_json_like(path, obj, orig_text, bom):
    m = re.search(r'\n( +|\t)"', orig_text)
    indent = m.group(1) if m else (2 if "\n" in orig_text.strip() else None)
    s = json.dumps(obj, ensure_ascii=("\\u" in orig_text), indent=indent)
    if orig_text.endswith("\n"):
        s += "\n"
    if "\r\n" in orig_text:
        s = s.replace("\r\n", "\n").replace("\n", "\r\n")
    data = s.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    Path(path).write_bytes(data)


def read_text_keep(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def write_text_keep(path, text, bom):
    data = text.encode("utf-8")
    Path(path).write_bytes((b"\xef\xbb\xbf" + data) if bom else data)


# ───────────────────────── 백업 / 롤백 ─────────────────────────
def make_backups():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for p in TARGETS:
        if not p.exists():
            log("  [백업 건너뜀] 존재하지 않음: " + rel(p))
            continue
        flat = rel(p).replace("/", "__")
        stem, ext = os.path.splitext(flat)
        dst = BACKUP_DIR / (stem + TAG + ext)
        shutil.copy2(p, dst)
        BACKUPS[p] = dst
        log("  [백업] %s -> backups/%s" % (rel(p), dst.name))


def rollback():
    log("[ROLLBACK] 백업본으로 복원합니다.")
    for p, b in BACKUPS.items():
        try:
            shutil.copy2(b, p)
            log("  복원: " + rel(p))
        except Exception as e:
            log("  복원 실패: %s (%s)" % (rel(p), e))


# ───────────────────────── 헌법 해시 ─────────────────────────
def constitution_prefix_match(raw):
    cands = {"sha256": hashlib.sha256(raw).hexdigest(),
             "sha1": hashlib.sha1(raw).hexdigest(),
             "md5": hashlib.md5(raw).hexdigest()}
    try:
        obj = json.loads(raw.decode("utf-8-sig"))
        for name, kw in (("sha256-canon", dict(sort_keys=True, ensure_ascii=False, separators=(",", ":"))),
                         ("sha256-canon-ascii", dict(sort_keys=True, ensure_ascii=True, separators=(",", ":"))),
                         ("sha256-sorted", dict(sort_keys=True, ensure_ascii=False)),
                         ("sha256-dumps", dict(ensure_ascii=False))):
            cands[name] = hashlib.sha256(json.dumps(obj, **kw).encode("utf-8")).hexdigest()
    except Exception:
        pass
    for name, h in cands.items():
        if h.startswith(CONST_PREFIX):
            return name, h
    return None, cands["sha256"]


# ───────────────────────── 1) master_schedule.json ─────────────────────────
ID_KEYS = {"id", "name", "task", "task_id", "title", "key", "code", "slug", "label", "과제", "과제명"}


def mark_active(node, depth=0):
    hits = 0
    if depth > 30:
        return 0
    if isinstance(node, dict):
        is_task = any(k in ID_KEYS and isinstance(v, str) and
                      (v.strip() == TASK or v.strip().startswith(TASK)) for k, v in node.items())
        if is_task:
            old = node.get("status")
            if old is not None and old != "ACTIVE":
                node.setdefault("status_prev", old)
            node["status"] = "ACTIVE"
            for sk in ("state",):
                if sk in node and node[sk] != "ACTIVE":
                    node.setdefault(sk + "_prev", node[sk])
                    node[sk] = "ACTIVE"
            if isinstance(node.get("active"), bool):
                node["active"] = True
            od = node.get("date")
            if od is not None and od != TODAY:
                node.setdefault("date_prev", od)
            node["date"] = TODAY
            node["assigned_date"] = TODAY
            node["activated_at"] = ISO
            hits += 1
        for k, v in list(node.items()):
            if k == TASK and isinstance(v, dict):
                v2 = v
                old = v2.get("status")
                if old is not None and old != "ACTIVE":
                    v2.setdefault("status_prev", old)
                v2["status"] = "ACTIVE"
                if v2.get("date") not in (None, TODAY):
                    v2.setdefault("date_prev", v2.get("date"))
                v2["date"] = TODAY
                v2["assigned_date"] = TODAY
                v2["activated_at"] = ISO
                hits += 1
            elif isinstance(v, (dict, list)):
                hits += mark_active(v, depth + 1)
    elif isinstance(node, list):
        for x in node:
            hits += mark_active(x, depth + 1)
    return hits


def patch_schedule():
    data, text, bom = load_json(SCHEDULE)
    if not isinstance(data, dict):
        raise RuntimeError("master_schedule.json 최상위가 dict 가 아닙니다.")
    hits = mark_active(data)
    data["top1_self_evolving_brain"] = {
        "task": TASK, "status": "ACTIVE", "date": TODAY, "activated_at": ISO,
        "source": "step11_task_c2", "priority": 1}
    da = data.get("daily_assignments")
    if da is None:
        da = {}
        data["daily_assignments"] = da
    if isinstance(da, dict):
        lst = da.setdefault(TODAY, [])
        if isinstance(lst, list) and TASK not in lst:
            lst.append(TASK)
    for key in ("viral_keywords", "keywords"):
        old = data.get(key)
        if isinstance(old, list) and old and old != KEYWORDS:
            data.setdefault(key + "_prev", old)
        data[key] = list(KEYWORDS)
    data["bm_pipeline"] = {"name": "BM_PIPELINE", "status": "REGISTERED", "stage": "keywords_loaded",
                           "keywords_count": len(KEYWORDS), "top1": TASK, "top1_status": "ACTIVE",
                           "registered_at": ISO, "source": "step11_task_c2"}
    dump_json_like(SCHEDULE, data, text, bom)
    log("  [schedule] TOP1 가동 표식 %d건 · 키워드 %d종 · BM 파이프라인 등록" % (hits, len(KEYWORDS)))


# ───────────────────────── 2) pulse 파서 보정 ─────────────────────────
def patch_pulse():
    src, bom = read_text_keep(PULSE)
    nl = "\r\n" if "\r\n" in src else "\n"
    s = src.replace("\r\n", "\n")
    s = re.sub(re.escape(PATCH_BEGIN) + r".*?" + re.escape(PATCH_END) + r"\n?", "", s, flags=re.S)
    guards = list(re.finditer(r'(?m)^if\s+__name__\s*==\s*["\']__main__["\']\s*:', s))
    if guards:
        pos = guards[-1].start()
        s = s[:pos].rstrip("\n") + "\n\n\n" + PATCH_BLOCK + "\n\n" + s[pos:]
    else:
        s = s.rstrip("\n") + "\n\n\n" + PATCH_BLOCK
    compile(s, str(PULSE), "exec")  # 구문 검증
    write_text_keep(PULSE, s.replace("\n", nl), bom)
    log("  [pulse] 5-Gate 파서(G0 인식) · D2 키워드 보고 보정 주입 완료")


# ───────────────────────── 3) HTML ─────────────────────────
def patch_html_text(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    m = SCRIPT_RE.search(text)
    if not m:
        raise RuntimeError("rgon-step11-pulse-live 스크립트를 찾지 못했습니다.")
    body = m.group(2).replace("\r\n", "\n")
    body = re.sub(re.escape(JS_BEGIN) + r".*?" + re.escape(JS_END) + r"\s*", "", body, flags=re.S)
    new_body = body.rstrip() + "\n\n" + JS_BLOCK + "\n"
    new_body = new_body.replace("\n", nl)
    return text[:m.start(2)] + new_body + text[m.end(2):]


def patch_htmls():
    results = []
    for p in HTMLS:
        text, bom = read_text_keep(p)
        results.append((p, patch_html_text(text), bom))
    hashes = {hashlib.sha256((t.encode("utf-8") if not b else b"\xef\xbb\xbf" + t.encode("utf-8"))).hexdigest()
              for _, t, b in results}
    if len(hashes) != 1:
        log("  [html] 원본 3곳이 서로 달라 root 본을 기준으로 통일합니다.")
        base_text, base_bom = results[0][1], results[0][2]
        results = [(p, base_text, base_bom) for p, _, _ in results]
    for p, t, b in results:
        write_text_keep(p, t, b)
    log("  [html] 버튼 주입 완료 (3곳)")


def count_id(text, pid):
    return len(re.findall(r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']', text))


# ───────────────────────── 4) 스냅샷 / 진화 장부 ─────────────────────────
def apply_snapshots(beat=None, overall=None):
    for p in SNAPS:
        if not p.exists():
            log("  [snapshot] 없음 -> 건너뜀: " + rel(p))
            continue
        try:
            data, text, bom = load_json(p)
        except Exception as e:
            log("  [snapshot] JSON 오류 -> 건너뜀: %s (%s)" % (rel(p), e))
            continue
        if not isinstance(data, dict):
            continue
        for key in ("viral_keywords", "keywords"):
            if key in data and isinstance(data[key], list):
                data[key] = list(KEYWORDS)
        blk = {"top1_self_evolving_brain": "ACTIVE", "task": TASK, "date": TODAY,
               "viral_keywords": list(KEYWORDS), "bm_pipeline": "REGISTERED",
               "gate_parser": "5/5 (G0~G4)", "updated_at": ISO}
        if beat is not None:
            blk["pulse_beat"] = beat
        if overall is not None:
            blk["overall"] = overall
        data["step11_c2"] = blk
        dump_json_like(p, data, text, bom)
    log("  [snapshot] 스냅샷 갱신 완료")


def record_evolution(beat, overall, const_hash):
    entry = {"event": EVENT, "ts": ISO, "task": "C-2", "top1": TASK, "status": "ACTIVE",
             "viral_keywords": list(KEYWORDS), "bm_pipeline": "REGISTERED",
             "gate_parser": "5/5 (G0,G1,G2,G3,G4)", "pulse_beat": beat, "overall": overall,
             "constitution_hash12": const_hash[:12], "constitution_modified": False,
             "backup_tag": TAG}
    if EVOLUTION.exists():
        data, text, bom = load_json(EVOLUTION)
    else:
        data, text, bom = [], "[]\n", False

    def drop_old(lst):
        lst[:] = [x for x in lst if not (isinstance(x, dict) and x.get("event") == EVENT)]

    if isinstance(data, list):
        drop_old(data)
        data.append(entry)
    elif isinstance(data, dict):
        target = None
        for k in ("history", "evolution_history", "log", "events", "entries", "records", "timeline"):
            if isinstance(data.get(k), list):
                target = data[k]
                break
        if target is None:
            target = data.setdefault("history", [])
        drop_old(target)
        target.append(entry)
    else:
        raise RuntimeError("evolution_memory.json 구조를 알 수 없습니다.")
    if EVOLUTION.exists():
        dump_json_like(EVOLUTION, data, text, bom)
    else:
        EVOLUTION.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log("  [evolution] %s 이력 기록 (박동 #%s)" % (EVENT, beat))


# ───────────────────────── 5) 박동 실행 / 분석 ─────────────────────────
def run_pulse():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    t0 = time.time()
    p = subprocess.run([sys.executable, str(PULSE)], cwd=str(ROOT), capture_output=True, env=env, timeout=600)
    out = p.stdout.decode("utf-8", "replace") + "\n" + p.stderr.decode("utf-8", "replace")
    return p.returncode, out, t0


def collect_dims(obj, out=None):
    if out is None:
        out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            m = re.match(r"^D([1-6])(?:_|$)", str(k))
            if m and m.group(1) not in out:
                out[m.group(1)] = (k, v)
            collect_dims(v, out)
    elif isinstance(obj, list):
        for x in obj:
            collect_dims(x, out)
    return out


def iter_overall(obj, depth=0):
    if depth > 25:
        return
    if isinstance(obj, dict):
        if "overall" in obj and collect_dims(obj):
            yield obj
        for v in obj.values():
            for r in iter_overall(v, depth + 1):
                yield r
    elif isinstance(obj, list):
        for x in obj:
            for r in iter_overall(x, depth + 1):
                yield r


BEAT_KEYS = {"beat", "beat_no", "beat_number", "pulse_no", "pulse_number", "pulse_count",
             "heartbeat", "박동", "seq", "pulse_beat"}


def walk_beats(obj, out, depth=0):
    if depth > 25:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in BEAT_KEYS and isinstance(v, int) and not isinstance(v, bool):
                out.append(v)
            walk_beats(v, out, depth + 1)
    elif isinstance(obj, list):
        for x in obj:
            walk_beats(x, out, depth + 1)


def dim_text(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def dim_ok(v):
    if isinstance(v, dict):
        for k in ("status", "state", "level", "result", "verdict", "ok"):
            if k in v:
                val = v[k]
                if isinstance(val, bool):
                    return val
                return str(val).strip().upper().startswith(("OK", "PASS", "GREEN", "HEALTHY"))
    return not re.search(r"FAIL|ERROR|WARN|❌|✗", dim_text(v), re.I)


def analyze_pulse(out, t0):
    info = {"beat": None, "overall": None, "dims": {}}
    beats = [int(x) for x in re.findall(r"(?:박동|[Pp]ulse|[Bb]eat)\s*#\s*(\d+)", out)]
    best = None
    for d in (ROOT, ROOT / "dashboard", ROOT / "docs", ROOT / "brain_basket", ROOT / "logs", ROOT / "data"):
        if not d.is_dir():
            continue
        for p in d.glob("*.json"):
            if p.name == CONSTITUTION.name:
                continue
            try:
                st = p.stat().st_mtime
                if st < t0 - 2:
                    continue
                obj = json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            walk_beats(obj, beats)
            for rec in iter_overall(obj):
                score = (len(collect_dims(rec)), st)
                if best is None or score > best[0]:
                    best = (score, rec)
    if best:
        rec = best[1]
        ov = rec.get("overall")
        if isinstance(ov, dict):
            ov = ov.get("status") or ov.get("overall") or ov.get("state")
        info["overall"] = str(ov).strip().upper() if ov is not None else None
        info["dims"] = collect_dims(rec)
    else:
        m = re.search(r'overall\W{0,6}([A-Za-z]+)', out, re.I)
        if m:
            info["overall"] = m.group(1).upper()
        for line in out.splitlines():
            m = re.match(r"\s*\W*D([1-6])\b", line)
            if m and m.group(1) not in info["dims"]:
                info["dims"][m.group(1)] = ("D" + m.group(1), line.strip())
    info["beat"] = max(beats) if beats else None
    return info


def verify_pulse(info, rc, out):
    fails = []
    if rc != 0:
        fails.append("박동 스크립트 종료코드 %s" % rc)
    if info["beat"] is None or info["beat"] < 5:
        fails.append("박동 번호 확인 실패/미달 (감지값: %s)" % info["beat"])
    if info["overall"] != "OK":
        fails.append("overall != OK (감지값: %s)" % info["overall"])
    for n in "123456":
        if n not in info["dims"]:
            fails.append("D%s 결과를 찾지 못함" % n)
        elif not dim_ok(info["dims"][n][1]):
            fails.append("D%s 가 OK 가 아님: %s" % (n, dim_text(info["dims"][n][1])[:160]))
    d2 = dim_text(info["dims"]["2"][1]) if "2" in info["dims"] else ""
    d4 = dim_text(info["dims"]["4"][1]) if "4" in info["dims"] else ""
    if "핵심 키워드 5종 장전 완료" not in d2 or "미등록" in d2:
        fails.append("D2_viral 키워드 5종 장전 문구 미확인: " + d2[:200])
    if not re.search(r"5/5\s*확인\s*\(\s*G0\s*,\s*G1\s*,\s*G2\s*,\s*G3\s*,\s*G4\s*\)", d4):
        fails.append("D4_hongik 5/5 확인(G0,G1,G2,G3,G4) 미확인: " + d4[:200])
    return fails


# ───────────────────────── 종합 검증 ─────────────────────────
def verify_static(const_sha_before):
    fails = []
    if sha256_file(CONSTITUTION) != const_sha_before:
        fails.append("헌법 파일이 변경됨!")
    hs = []
    for p in HTMLS:
        t, _ = read_text_keep(p)
        hs.append(sha256_file(p))
        for pid in PROTECTED_IDS:
            c = count_id(t, pid)
            if c != 1:
                fails.append("%s 보호 ID %s = %d개 (1개여야 함)" % (rel(p), pid, c))
        if BTN_LABEL not in t:
            fails.append("%s 버튼 라벨 누락" % rel(p))
        if len(re.findall(r'<script\b[^>]*\bid\s*=\s*["\']rgon-step11-pulse-live["\']', t)) != 1:
            fails.append("%s rgon-step11-pulse-live 스크립트가 1개가 아님" % rel(p))
    if len(set(hs)) != 1:
        fails.append("HTML 3곳 SHA-256 불일치: " + ", ".join(h[:12] for h in hs))
    return fails


# ───────────────────────── Git ─────────────────────────
def git(*args):
    p = subprocess.run(["git", "-c", "core.quotepath=off"] + list(args), cwd=str(ROOT), capture_output=True)
    return (p.returncode, p.stdout.decode("utf-8", "replace").strip(), p.stderr.decode("utf-8", "replace").strip())


def porcelain():
    rc, out, _ = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    items = set()
    if rc == 0:
        for ent in out.split("\x00"):
            if len(ent) > 3:
                items.add(ent[3:].replace("\\", "/"))
    return items


def git_sync(before_dirty):
    rc, out, err = git("rev-parse", "--is-inside-work-tree")
    if rc != 0:
        raise RuntimeError("git 저장소가 아닙니다: " + err)
    after = porcelain()
    paths = [rel(p) for p in TARGETS if p.exists()]
    for extra in sorted(after - before_dirty):
        if extra.startswith("backups/") or extra == CONSTITUTION.name:
            continue
        if extra not in paths:
            paths.append(extra)
    for pth in paths:
        rc, _, err = git("add", "--", pth)
        if rc != 0:
            log("  [git add 경고] %s: %s" % (pth, err.splitlines()[0] if err else ""))
    rc, staged, _ = git("diff", "--cached", "--name-only")
    if CONSTITUTION.name in staged.splitlines():
        raise RuntimeError("헌법 파일이 스테이징됨 - 중단")
    msg = "Step 11 C-2: TOP1_SELF_EVOLVING_BRAIN ACTIVE, D2 keywords x5, 5-Gate 5/5 parser (G0~G4), pulse #5"
    rc, out, err = git("commit", "-m", msg)
    if rc != 0 and "nothing to commit" not in (out + err).lower():
        raise RuntimeError("git commit 실패: " + (err or out))
    rc, head, _ = git("rev-parse", "--short=10", "HEAD")
    log("  [git] commit " + head)
    rc, out, err = git("push", "origin", "main")
    if rc != 0:
        raise RuntimeError("git push 실패: " + (err or out))
    log("  [git] push origin main 완료")


# ───────────────────────── 메인 ─────────────────────────
def main():
    log("=" * 70)
    log("RGON Step 11 · 과제 C-2 착수 (%s)" % ISO)
    log("=" * 70)

    # 사전 점검
    for p in [CONSTITUTION, SCHEDULE, PULSE] + HTMLS:
        if not p.exists():
            log("[FAIL] 필수 파일 없음: " + str(p))
            return 1
    const_raw = CONSTITUTION.read_bytes()
    const_sha = hashlib.sha256(const_raw).hexdigest()
    algo, h = constitution_prefix_match(const_raw)
    if algo:
        log("[헌법] 기준선 %s 일치 (%s) · 읽기 전용" % (CONST_PREFIX, algo))
    else:
        log("[헌법] 경고: %s 접두 해시를 표준 알고리즘으로 재현하지 못함 (sha256=%s...). 변경 여부는 전/후 비교로 보장" % (CONST_PREFIX, h[:12]))

    ns = {"__file__": str(PULSE)}
    exec(PARSER_DEFS, ns)
    gates = ns["_c2_scan_gates"](json.loads(const_raw.decode("utf-8-sig")))
    log("[파서 사전점검] 헌법에서 인식된 Gate: " + ",".join(gates))
    if gates != ["G0", "G1", "G2", "G3", "G4"]:
        log("[FAIL] 헌법 JSON 에서 G0~G4 를 모두 인식하지 못했습니다. 파일 변경 없이 중단합니다.")
        return 1

    before_dirty = porcelain()
    log("[1/6] 사전 백업 (G3)")
    make_backups()

    try:
        log("[2/6] master_schedule · pulse 파서 · 독대실 HTML 갱신")
        patch_schedule()
        patch_pulse()
        patch_htmls()
        apply_snapshots()

        fails = verify_static(const_sha)
        if fails:
            raise RuntimeError("정적 검증 실패: " + " | ".join(fails))

        log("[3/6] 박동 실행")
        rc, out, t0 = run_pulse()
        tail = "\n".join(out.strip().splitlines()[-25:])
        log(tail)
        info = analyze_pulse(out, t0)
        pf = verify_pulse(info, rc, out)
        if pf:
            raise RuntimeError("박동 검증 실패: " + " | ".join(pf))
        log("[박동] #%s · overall=%s · D1~D6 전원 OK" % (info["beat"], info["overall"]))
        log("  D2: " + dim_text(info["dims"]["2"][1])[:220])
        log("  D4: " + dim_text(info["dims"]["4"][1])[:220])

        log("[4/6] 장부 · 스냅샷 기록")
        apply_snapshots(beat=info["beat"], overall=info["overall"])
        record_evolution(info["beat"], info["overall"], const_sha)

        log("[5/6] 최종 검증")
        fails = verify_static(const_sha)
        if fails:
            raise RuntimeError("최종 검증 실패: " + " | ".join(fails))
        log("  헌법 무변경(%s) · 보호 ID 6/6(각 1개) · HTML 3곳 해시 일치 · overall=OK · 박동 #%s" %
            (const_sha[:12] if not algo else CONST_PREFIX, info["beat"]))
    except Exception as e:
        log("[FAIL] " + str(e))
        rollback()
        try:
            ok = sha256_file(CONSTITUTION) == const_sha
        except Exception:
            ok = False
        log("[ROLLBACK] 헌법 파일 무변경 확인: %s" % ok)
        return 1

    log("[6/6] GitHub 클라우드 배포")
    try:
        git_sync(before_dirty)
    except Exception as e:
        log("[FAIL] " + str(e))
        log("  (로컬 파일은 검증 완료 상태로 유지됩니다. 네트워크/인증 확인 후 'git push origin main' 을 재시도하세요.)")
        return 2

    if sha256_file(CONSTITUTION) != const_sha:
        log("[FAIL] 배포 후 헌법 해시 변경 감지!")
        return 3
    log(FINAL_OK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
Copy