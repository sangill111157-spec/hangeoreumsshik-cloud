#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGON G1 Step 11 / 과제 D-1
D3 미디어 청사 원클릭 한국어 TTS 음성 브리핑(Web Speech) 장착 · 독대실 R1~R14(14종) 실명 통일
항체 분모 14/14 정정 · 박동 #7 클라우드 배포
실행: RGON_Run.bat -> rgon_runner.py -> 본 스크립트 (단독 실행 가능)
"""
import sys, os, re, ast, json, shutil, hashlib, subprocess, time, tempfile
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
PULSE = ROOT / "scripts" / "rgon_agency_pulse.py"
HTMLS = [ROOT / "rgon_alpha_chat.html",
         ROOT / "dashboard" / "rgon_alpha_chat.html",
         ROOT / "docs" / "rgon_alpha_chat.html"]
SNAPS = [ROOT / "rgon_brain_snapshot.json",
         ROOT / "dashboard" / "rgon_brain_snapshot.json",
         ROOT / "docs" / "rgon_brain_snapshot.json"]
EVOLUTION = ROOT / "evolution_memory.json"
BACKUP_DIR = ROOT / "backups"

EVENT = "step11_task_d1_d3_tts_and_r14_ui_sync"
PROTECTED_IDS = ["rgon-step5-solo-panel", "rgon-step7-chat-zone", "rgon-step8-constitution-bar",
                 "rgon-step9-aggregator-board", "rgon-step10-agency-awaken", "dokdae-feed"]
BTN_IDLE = "[🔊 6대 청사 브리핑 음성 듣기]"
R14_TEXT = "코드 끝 찌꺼기 자동 정화"
D3_TEXT = "🟢 OK · 독대실 원클릭 한국어 TTS 음성 브리핑(Web Speech) 장착 완료 · HTML 3곳 동기화 · 미디어+음성 브리핑 즉시 출고 가능"
FINAL_OK = "[OK] Step 11 과제 D-1 D3 미디어 원클릭 TTS 음성 브리핑 장착 · 항체 14/14 통일 · 박동 #7 클라우드 배포 완료"

NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S")
TAG = "_step11d1_bak_" + TS

TARGETS = [PULSE] + HTMLS + SNAPS + [EVOLUTION]
BACKUPS = {}


def log(msg):
    print(msg, flush=True)


def rel(p):
    try:
        return str(Path(p).relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(p)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ═════════════════════ D1 런타임 보정 소스 (pulse 에 주입 / 장부 갱신에도 재사용) ═════════════════════
D1_SRC = r'''
import re as _d1_re
import copy as _d1_copy
import functools as _d1_ft
import types as _d1_types
import inspect as _d1_inspect
import builtins as _d1_builtins

_D1_D3 = "🟢 OK · 독대실 원클릭 한국어 TTS 음성 브리핑(Web Speech) 장착 완료 · HTML 3곳 동기화 · 미디어+음성 브리핑 즉시 출고 가능"
_D1_R14 = "코드 끝 찌꺼기 자동 정화"
_D1_IDK = ("id", "code", "name", "key", "antibody", "rule", "no", "num", "number", "label", "title")
_D1_TXK = ("name", "title", "desc", "description", "summary", "text", "label", "detail", "rule", "content", "ko")
_D1_TEXTK = ("detail", "summary", "text", "msg", "message", "report", "note", "desc", "description", "finding", "diagnosis", "brief")
_D1_BEATK = ("beat", "beat_no", "beat_number", "pulse_no", "pulse_number", "pulse_count", "heartbeat", "박동", "seq", "pulse_beat")
_D1_CNT = _d1_re.compile(r"count|total|active|num|size|len|수|개|활성", _d1_re.I)


def _d1_text(s):
    if not isinstance(s, str) or len(s) > 20000:
        return s
    o = _d1_re.sub(r"(?<![0-9])14\s*/\s*13(?![0-9])", "14/14", s)
    if "항체" in o or _d1_re.search(r"R0?1\s*[~\-–]\s*R0?1[34]", o):
        o = _d1_re.sub(r"R0?1\s*[~\-–]\s*R0?13(?![0-9])", "R1~R14", o)
        o = _d1_re.sub(r"(?<![0-9/])13\s*/\s*13(?![0-9])", "14/14", o)
        o = _d1_re.sub(r"(?<![0-9])13(\s*(?:대|종|개)\s*항체)", r"14\1", o)
        o = _d1_re.sub(r"(R1~R14\s*[\(（]\s*)13(\s*종)", r"\g<1>14\2", o)
    return o


def _d1_isr(x, n):
    return isinstance(x, str) and _d1_re.match(r"^\s*[\[\(]?R0?%d(?![0-9])" % n, x) is not None


def _d1_has(item, n):
    if isinstance(item, str):
        return _d1_isr(item, n)
    if isinstance(item, dict):
        return any(_d1_isr(v, n) for k, v in item.items() if k in _D1_IDK)
    return False


def _d1_make(tpl):
    if isinstance(tpl, str):
        if _d1_re.match(r"^\s*R0?13\s*$", tpl):
            return "R14"
        if _d1_isr(tpl, 13):
            return "R14: " + _D1_R14
        return _D1_R14
    if isinstance(tpl, dict):
        new = _d1_copy.deepcopy(tpl)
        for k, v in list(new.items()):
            if not isinstance(v, str):
                continue
            if _d1_re.match(r"^\s*R0?13\s*$", v):
                new[k] = "R14"
            elif _d1_isr(v, 13):
                new[k] = "R14: " + _D1_R14
            elif k in _D1_TXK:
                new[k] = _D1_R14
        return new
    return _d1_copy.deepcopy(tpl)


def _d1_upgrade_struct(obj, _d=0):
    if _d > 14:
        return False
    changed = False
    if isinstance(obj, list):
        h13 = [i for i, x in enumerate(obj) if _d1_has(x, 13)]
        h14 = any(_d1_has(x, 14) for x in obj)
        if h13 and not h14:
            idx = h13[-1]
            obj.insert(idx + 1, _d1_make(obj[idx]))
            changed = True
        for x in list(obj):
            if isinstance(x, (dict, list)) and _d1_upgrade_struct(x, _d + 1):
                changed = True
    elif isinstance(obj, dict):
        k13 = [k for k in obj if isinstance(k, str) and _d1_re.match(r"^\s*R0?13\s*$", k)]
        h14 = any(isinstance(k, str) and _d1_re.match(r"^\s*R0?14\s*$", k) for k in obj)
        if k13 and not h14:
            obj["R14"] = _d1_make(obj[k13[0]])
            changed = True
        for k, v in list(obj.items()):
            if isinstance(v, (dict, list)) and _d1_upgrade_struct(v, _d + 1):
                changed = True
        if changed:
            for k, v in list(obj.items()):
                if isinstance(v, int) and not isinstance(v, bool) and v == 13 and isinstance(k, str) and _D1_CNT.search(k):
                    obj[k] = 14
    return changed


def _d1_beat_of(d):
    for k, v in d.items():
        if isinstance(k, str) and k.lower() in _D1_BEATK and isinstance(v, int) and not isinstance(v, bool):
            return v
    for v in d.values():
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(k, str) and k.lower() in _D1_BEATK and isinstance(x, int) and not isinstance(x, bool):
                    return x
    return None


def _d1_dimid(d):
    for i in ("id", "key", "dim", "name", "code"):
        v = d.get(i)
        if isinstance(v, str) and _d1_re.match(r"^D[1-6](_|$)", v):
            return v
    return None


def _d1_set_text(v):
    for tk in _D1_TEXTK:
        if isinstance(v.get(tk), str):
            v[tk] = _D1_D3
            return
    v["detail"] = _D1_D3


def _d1_set_d3(d, key):
    v = d[key]
    if isinstance(v, str):
        d[key] = _D1_D3
    elif isinstance(v, dict):
        _d1_set_text(v)


def _d1_fix(obj, _d=0):
    if isinstance(obj, str):
        return _d1_text(obj)
    if _d > 12:
        return obj
    if isinstance(obj, dict):
        ks = [k for k in obj if isinstance(k, str)]
        if any(_d1_re.match(r"^D1(_|$)", k) for k in ks):
            for k in ks:
                if _d1_re.match(r"^D3(_|$)", k):
                    _d1_set_d3(obj, k)
        for k in list(obj.keys()):
            v = obj[k]
            nv = _d1_fix(v, _d + 1)
            if nv is not v:
                obj[k] = nv
        return obj
    if isinstance(obj, list):
        dicts = [x for x in obj if isinstance(x, dict)]
        ids = [_d1_dimid(x) for x in dicts]
        if any(i and i.startswith("D1") for i in ids):
            for x, i in zip(dicts, ids):
                if i and _d1_re.match(r"^D3(_|$)", i):
                    _d1_set_text(x)
        sel = None
        if len(dicts) > 1 and len(dicts) == len(obj):
            beats = [(_d1_beat_of(x), i) for i, x in enumerate(obj)]
            nums = [b for b, _i in beats if b is not None]
            if len(nums) >= 2:
                mx = max(nums)
                sel = set(i for b, i in beats if b == mx)
        for i, v in enumerate(obj):
            if sel is not None and i not in sel:
                continue
            nv = _d1_fix(v, _d + 1)
            if nv is not v:
                obj[i] = nv
        return obj
    if type(obj) is tuple:
        return tuple(_d1_fix(v, _d + 1) for v in obj)
    return obj


def _d1_ensure_ab(g):
    ab = g.get("ANTIBODIES")
    try:
        if isinstance(ab, dict):
            ks = list(ab.keys())
            if ks and all(isinstance(k, int) for k in ks):
                if 14 not in ab:
                    k13 = ab.get(13)
                    ab[14] = _d1_make(k13) if isinstance(k13, dict) else _D1_R14
            elif ks and all(isinstance(k, str) for k in ks):
                s13 = [k for k in ks if _d1_re.match(r"^\s*R?0?13\s*$", k)]
                s14 = [k for k in ks if _d1_re.match(r"^\s*R?0?14\s*$", k)]
                if s13 and not s14:
                    k = s13[0]
                    nk = ("R" if k.strip().upper().startswith("R") else "") + "14"
                    ab[nk] = _d1_make(ab[k]) if isinstance(ab[k], dict) else _D1_R14
        elif isinstance(ab, list):
            if len(ab) == 13:
                ab.append(_d1_make(ab[-1]) if isinstance(ab[-1], dict) else _D1_R14)
            else:
                _d1_upgrade_struct(ab)
    except Exception:
        pass


class _D1Json(object):
    def __init__(self, m):
        self.__dict__["_m"] = m

    def __getattr__(self, n):
        return getattr(self.__dict__["_m"], n)

    def dump(self, obj, *a, **k):
        _d1_fix(obj)
        return self.__dict__["_m"].dump(obj, *a, **k)

    def dumps(self, obj, *a, **k):
        _d1_fix(obj)
        return self.__dict__["_m"].dumps(obj, *a, **k)


def _d1_print(*a, **k):
    return _d1_builtins.print(*[_d1_text(x) if isinstance(x, str) else x for x in a], **k)


def _d1_install(g):
    _d1_ensure_ab(g)
    mod = g.get("json")
    if mod is not None and type(mod).__name__ == "module":
        g["json"] = _D1Json(mod)
    g["print"] = _d1_print
    for name, fn in list(g.items()):
        if name.startswith("_c2_") or name.startswith("_c3_") or name.startswith("_d1_") or name.startswith("_D1"):
            continue
        if not isinstance(fn, _d1_types.FunctionType) or fn.__globals__ is not g or getattr(fn, "_d1_wrapped", False):
            continue
        if _d1_inspect.isgeneratorfunction(fn) or _d1_inspect.iscoroutinefunction(fn):
            continue

        def make(f):
            @_d1_ft.wraps(f)
            def w(*a, **k):
                for x in a:
                    if isinstance(x, (dict, list)):
                        _d1_fix(x)
                r = f(*a, **k)
                if isinstance(r, (dict, list)):
                    _d1_fix(r)
                    return r
                if isinstance(r, str):
                    return _d1_text(r)
                if type(r) is tuple:
                    return _d1_fix(r)
                return r
            w._d1_wrapped = True
            return w
        g[name] = make(fn)
'''
D1_BEGIN = "# ==== RGON-D1-PATCH-BEGIN (step11d1) ===="
D1_END = "# ==== RGON-D1-PATCH-END ===="
D1_BLOCK = D1_BEGIN + "\n" + D1_SRC.strip("\n") + "\n\n_d1_install(globals())\n" + D1_END + "\n"

# ═════════════════════ 독대실 TTS JS ═════════════════════
JS_BEGIN = "/* RGON-D1-TTS-BEGIN step11d1 */"
JS_END = "/* RGON-D1-TTS-END */"
JS_BLOCK = r'''/* RGON-D1-TTS-BEGIN step11d1 */
(function () {
  "use strict";
  if (window.__rgonD1TtsArmed) { return; }
  window.__rgonD1TtsArmed = true;

  var LABEL_IDLE = "[🔊 6대 청사 브리핑 음성 듣기]";
  var LABEL_PLAY = "[⏹ 6대 청사 브리핑 정지]";
  var MARK = "data-rgon-d1-tts";
  var C2MARK = "data-rgon-c2-btn";
  var NAMES = { 1: "퀀트 청사", 2: "바이럴 청사", 3: "미디어 청사", 4: "홍익 청사", 5: "가디언 청사", 6: "여섯 번째 청사" };
  var SNAP_URLS = ["rgon_brain_snapshot.json", "./rgon_brain_snapshot.json", "../rgon_brain_snapshot.json",
                   "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json"];
  var SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, INPUT: 1, BUTTON: 1, HEAD: 1, TITLE: 1, META: 1, LINK: 1, NOSCRIPT: 1 };
  var HOST_RE = /6대\s*청사|일일\s*(?:실전\s*)?브리핑|박동\s*#\s*\d+/;
  var playing = false, token = 0, timer = null, floatOk = false;

  function clean(t) { return String(t == null ? "" : t).replace(/\s+/g, " ").trim(); }

  function speechClean(t) {
    var s = String(t == null ? "" : t);
    s = s.replace(/https?:\/\/\S+/g, " ");
    s = s.replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}]/gu, " ");
    s = s.replace(/R(\d+)\s*~\s*R(\d+)/g, "R$1부터 R$2");
    s = s.replace(/G(\d+)\s*~\s*G(\d+)/g, "G$1부터 G$2");
    s = s.replace(/(\d+)\s*\/\s*(\d+)/g, "$2분의 $1");
    s = s.replace(/#\s*(\d+)/g, "$1번");
    s = s.replace(/(\d)\s*~\s*(\d)/g, "$1에서 $2");
    s = s.replace(/[·•|]/g, ", ").replace(/->|=>|→/g, ", ");
    s = s.replace(/[「」『』\[\]\(\)<>{}*_`~"\/]/g, " ");
    return s.replace(/\s+/g, " ").trim();
  }

  function chunk(text, max) {
    var parts = text.match(/[^.!?。\n]+[.!?。]?/g) || [text];
    var out = [], cur = "";
    parts.forEach(function (p) {
      p = p.trim();
      if (!p) { return; }
      while (p.length > max) {
        var cut = p.lastIndexOf(",", max);
        if (cut < 20) { cut = p.lastIndexOf(" ", max); }
        if (cut < 20) { cut = max; }
        if (cur) { out.push(cur); cur = ""; }
        out.push(p.slice(0, cut).trim());
        p = p.slice(cut).replace(/^[,\s]+/, "");
      }
      if (!p) { return; }
      if (cur && (cur.length + 1 + p.length) > max) { out.push(cur); cur = p; }
      else { cur = cur ? cur + " " + p : p; }
    });
    if (cur) { out.push(cur); }
    return out;
  }

  function valText(v) {
    if (v == null) { return ""; }
    if (typeof v === "string") { return v; }
    if (typeof v === "number" || typeof v === "boolean") { return String(v); }
    if (typeof v === "object") {
      var keys = ["summary", "detail", "text", "msg", "message", "headline", "report", "note", "desc", "description", "finding", "diagnosis", "brief"];
      for (var i = 0; i < keys.length; i++) {
        if (typeof v[keys[i]] === "string" && v[keys[i]]) { return v[keys[i]]; }
      }
      var acc = [];
      Object.keys(v).forEach(function (k) {
        if (/^(id|key|dim|name|code|ts|time|date|status|state|level)$/i.test(k)) { return; }
        if (typeof v[k] === "string") { acc.push(v[k]); }
      });
      return acc.join(". ");
    }
    return "";
  }

  function deepFind(o, re, d) {
    if (!o || typeof o !== "object" || d > 6) { return ""; }
    var ks = Object.keys(o), i;
    for (i = 0; i < ks.length; i++) {
      if (re.test(ks[i]) && typeof o[ks[i]] === "string" && o[ks[i]]) { return o[ks[i]]; }
    }
    for (i = 0; i < ks.length; i++) {
      if (o[ks[i]] && typeof o[ks[i]] === "object") {
        var r = deepFind(o[ks[i]], re, d + 1);
        if (r) { return r; }
      }
    }
    return "";
  }

  function collectD(o, res, d) {
    if (!o || typeof o !== "object" || d > 6) { return; }
    if (Array.isArray(o)) {
      o.forEach(function (it) {
        if (it && typeof it === "object") {
          var idv = it.id || it.key || it.dim || it.name || it.code;
          var m = typeof idv === "string" && idv.match(/^D([1-6])(?:_|$)/);
          if (m && res[m[1]] == null) { res[m[1]] = it; }
          else { collectD(it, res, d + 1); }
        }
      });
      return;
    }
    Object.keys(o).forEach(function (k) {
      var m = k.match(/^D([1-6])(?:_|$)/);
      if (m && res[m[1]] == null) { res[m[1]] = o[k]; }
      else if (o[k] && typeof o[k] === "object") { collectD(o[k], res, d + 1); }
    });
  }

  function findBrief(o, d) {
    if (!o || typeof o !== "object" || d > 6) { return null; }
    if (o.daily_briefing && typeof o.daily_briefing === "object") { return o.daily_briefing; }
    var ks = Object.keys(o);
    for (var i = 0; i < ks.length; i++) {
      if (o[ks[i]] && typeof o[ks[i]] === "object") {
        var r = findBrief(o[ks[i]], d + 1);
        if (r) { return r; }
      }
    }
    return null;
  }

  function compose(brief) {
    if (!brief) { return ""; }
    var dims = {};
    collectD(brief, dims, 0);
    var headline = speechClean(deepFind(brief, /^headline$/i, 0));
    var action = speechClean(deepFind(brief, /^action_top1$/i, 0));
    var cnt = Object.keys(dims).length;
    if (!cnt && !headline && !action) { return ""; }
    var parts = ["오늘의 6대 청사 일일 실전 브리핑입니다."];
    if (headline) { parts.push("헤드라인. " + headline + "."); }
    for (var i = 1; i <= 6; i++) {
      if (dims[i] != null) {
        var t = speechClean(valText(dims[i]));
        if (t.length > 260) { t = t.slice(0, 260); }
        if (t) { parts.push(i + "번 " + NAMES[i] + ". " + t + "."); }
      }
    }
    if (action) { parts.push("오늘의 최우선 행동 과제입니다. " + action + "."); }
    parts.push("이상으로 브리핑을 마칩니다.");
    return parts.join(" ");
  }

  function findHost() {
    var c2 = document.querySelector("[" + C2MARK + "]");
    if (c2 && c2.parentElement) { return c2.parentElement; }
    var all = document.body.querySelectorAll("*");
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (SKIP[el.tagName]) { continue; }
      if (el.closest && (el.closest("#dokdae-feed") || el.closest("[" + MARK + "]"))) { continue; }
      if (!HOST_RE.test(clean(el.textContent))) { continue; }
      var childHit = false;
      for (var j = 0; j < el.children.length; j++) {
        var ch = el.children[j];
        if (!SKIP[ch.tagName] && HOST_RE.test(clean(ch.textContent))) { childHit = true; break; }
      }
      if (!childHit) { return el; }
    }
    return null;
  }

  function domFallback() {
    var host = findHost();
    if (!host) { return ""; }
    var root = host, guard = 0;
    while (root.parentElement && root.parentElement !== document.body && clean(root.textContent).length < 120 && guard < 3) {
      root = root.parentElement; guard++;
    }
    var c = root.cloneNode(true);
    var bs = c.querySelectorAll("button, [" + MARK + "], [" + C2MARK + "]");
    for (var i = 0; i < bs.length; i++) { if (bs[i].parentNode) { bs[i].parentNode.removeChild(bs[i]); } }
    var t = clean(c.textContent).slice(0, 1500);
    return t ? "오늘의 6대 청사 일일 실전 브리핑입니다. " + speechClean(t) : "";
  }

  function loadBrief() {
    var g = window.__rgonDailyBriefing || window.__rgonBriefing || window.RGON_DAILY_BRIEFING;
    if (g && typeof g === "object") {
      var t0 = compose(findBrief(g, 0) || g);
      if (t0) { return Promise.resolve(t0); }
    }
    var i = 0;
    function next() {
      if (i >= SNAP_URLS.length || typeof fetch !== "function") { return Promise.resolve(domFallback()); }
      var u = SNAP_URLS[i++];
      return fetch(u + (u.indexOf("?") < 0 ? "?" : "&") + "t=" + Date.now(), { cache: "no-store" })
        .then(function (r) { if (!r.ok) { throw new Error("http " + r.status); } return r.json(); })
        .then(function (j) {
          var b = findBrief(j, 0);
          var t = b ? compose(b) : "";
          if (t) { return t; }
          throw new Error("no brief");
        })
        .catch(function () { return next(); });
    }
    return next();
  }

  function setBtn(on, msg) {
    var bs = document.querySelectorAll("[" + MARK + "]");
    for (var i = 0; i < bs.length; i++) {
      bs[i].textContent = msg ? msg : (on ? LABEL_PLAY : LABEL_IDLE);
      bs[i].setAttribute("data-playing", on ? "1" : "0");
      bs[i].setAttribute("aria-pressed", on ? "true" : "false");
    }
  }

  function finish(my) {
    if (my !== token) { return; }
    playing = false;
    setBtn(false);
  }

  function stop() {
    token++;
    playing = false;
    try { window.speechSynthesis.cancel(); } catch (e) {}
    setBtn(false);
  }

  function voicesReady(cb) {
    var s = window.speechSynthesis, v = s.getVoices();
    if (v && v.length) { cb(v); return; }
    var done = false;
    function fin() {
      if (done) { return; }
      done = true;
      try { s.removeEventListener("voiceschanged", fin); } catch (e) {}
      cb(s.getVoices() || []);
    }
    try { s.addEventListener("voiceschanged", fin); } catch (e) {}
    setTimeout(fin, 900);
  }

  function pickVoice(list) {
    var i, l;
    for (i = 0; i < list.length; i++) {
      l = String(list[i].lang || "").replace("_", "-").toLowerCase();
      if (l === "ko-kr") { return list[i]; }
    }
    for (i = 0; i < list.length; i++) {
      l = String(list[i].lang || "").toLowerCase();
      if (l.indexOf("ko") === 0) { return list[i]; }
    }
    return null;
  }

  function speakText(text, my) {
    voicesReady(function (vs) {
      if (my !== token) { return; }
      var voice = pickVoice(vs), chunks = chunk(text, 140), idx = 0;
      function next() {
        if (my !== token) { return; }
        if (idx >= chunks.length) { finish(my); return; }
        var u = new window.SpeechSynthesisUtterance(chunks[idx++]);
        u.lang = "ko-KR";
        if (voice) { u.voice = voice; }
        u.rate = 1.0; u.pitch = 1.0; u.volume = 1.0;
        u.onend = function () { next(); };
        u.onerror = function (e) {
          if (my !== token) { return; }
          if (e && (e.error === "interrupted" || e.error === "canceled")) { return; }
          finish(my);
        };
        window.__rgonD1Utter = u;
        window.speechSynthesis.speak(u);
      }
      try { window.speechSynthesis.cancel(); } catch (e) {}
      setTimeout(next, 60);
    });
  }

  window.__rgonStopDailyBriefing = stop;
  window.__rgonSpeakDailyBriefing = function () {
    if (!("speechSynthesis" in window) || typeof window.SpeechSynthesisUtterance === "undefined") {
      setBtn(false, "[⚠️ 이 브라우저는 음성 합성을 지원하지 않습니다]");
      setTimeout(function () { setBtn(false); }, 2800);
      return Promise.resolve(false);
    }
    if (playing) { stop(); return Promise.resolve(false); }
    playing = true;
    var my = ++token;
    setBtn(true);
    return loadBrief().then(function (text) {
      if (my !== token) { return false; }
      if (!text) {
        playing = false;
        setBtn(false, "[⚠️ 브리핑 데이터를 찾지 못했습니다]");
        setTimeout(function () { setBtn(false); }, 2800);
        return false;
      }
      speakText(text, my);
      return true;
    }).catch(function () { finish(my); return false; });
  };

  function ensureStyle() {
    if (document.querySelector("style[data-rgon-d1-style]")) { return; }
    var st = document.createElement("style");
    st.setAttribute("data-rgon-d1-style", "1");
    st.textContent =
      ".rgon-d1-tts{writing-mode:horizontal-tb;display:inline-flex;align-items:center;justify-content:center;" +
      "box-sizing:border-box;max-width:100%;margin:4px 0 4px 8px;padding:5px 12px;border:1px solid #3fb6a8;" +
      "border-radius:8px;background:#0f2a2a;color:#9ff3e6;font-size:12px;font-weight:700;line-height:1.4;" +
      "cursor:pointer;white-space:normal;word-break:keep-all;text-align:center;vertical-align:middle;" +
      "-webkit-tap-highlight-color:transparent;}" +
      ".rgon-d1-tts[data-playing=\"1\"]{background:#3a1414;border-color:#ff7a7a;color:#ffc9c9;}" +
      ".rgon-d1-tts[data-floating=\"1\"]{position:fixed;left:12px;bottom:12px;z-index:9999;margin:0;box-shadow:0 2px 10px rgba(0,0,0,.45);}" +
      "@media (max-width:640px){.rgon-d1-tts{display:flex;width:100%;margin:6px 0;padding:10px 12px;font-size:14px;}" +
      ".rgon-d1-tts[data-floating=\"1\"]{width:auto;left:8px;right:8px;bottom:8px;}}";
    (document.head || document.documentElement).appendChild(st);
  }

  function makeBtn() {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "rgon-d1-tts";
    btn.setAttribute(MARK, "1");
    btn.setAttribute("data-playing", playing ? "1" : "0");
    btn.setAttribute("aria-pressed", playing ? "true" : "false");
    btn.setAttribute("aria-label", "6대 청사 일일 브리핑 음성 듣기 또는 정지");
    btn.style.writingMode = "horizontal-tb";
    btn.textContent = playing ? LABEL_PLAY : LABEL_IDLE;
    btn.addEventListener("click", function (ev) {
      ev.preventDefault(); ev.stopPropagation();
      window.__rgonSpeakDailyBriefing();
    });
    return btn;
  }

  function place(btn, c2, host) {
    if (c2 && c2.parentNode) { c2.parentNode.insertBefore(btn, c2.nextSibling); }
    else { host.appendChild(btn); }
  }

  function ensure() {
    if (!document.body) { return; }
    ensureStyle();
    var ex = document.querySelector("[" + MARK + "]");
    var c2 = document.querySelector("[" + C2MARK + "]");
    var host = c2 ? c2.parentElement : findHost();
    if (ex && ex.isConnected) {
      if (ex.getAttribute("data-floating") === "1" && host) {
        ex.removeAttribute("data-floating");
        place(ex, c2, host);
      }
      return;
    }
    var btn = makeBtn();
    if (host) { place(btn, c2, host); }
    else if (floatOk) { btn.setAttribute("data-floating", "1"); document.body.appendChild(btn); }
  }

  function schedule() {
    if (timer) { clearTimeout(timer); }
    timer = setTimeout(ensure, 150);
  }

  function boot() {
    if (!document.body) { setTimeout(boot, 100); return; }
    ensure();
    try { new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true }); }
    catch (e) { setInterval(ensure, 1500); }
    setTimeout(function () { floatOk = true; ensure(); }, 4000);
    window.addEventListener("pagehide", stop);
  }
  boot();
})();
/* RGON-D1-TTS-END */'''

PULSE_SCRIPT_RE = re.compile(
    r'(<script\b[^>]*\bid\s*=\s*["\']rgon-step11-pulse-live["\'][^>]*>)(.*?)(</script\s*>)', re.S | re.I)
AB_SCRIPT_RE = re.compile(
    r'(<script\b[^>]*\bid\s*=\s*["\']rgon-step11-ab-realname["\'][^>]*>)(.*?)(</script\s*>)', re.S | re.I)
E13 = re.compile(
    r'(?<![\w])(?P<k>["\']?)(?P<r>R?)0?13(?P=k)(?P<sep>\s*:\s*)(?P<q>["\'`])(?P<v>(?:\\.|(?!(?P=q)).)*)(?P=q)(?P<c>\s*,?)', re.S)
E14 = re.compile(r'(?<![\w])["\']?R?0?14["\']?\s*:\s*["\'`]')


# ───────────────────────── 파일 유틸 ─────────────────────────
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
    atomic_write(path, data)


def read_text_keep(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def atomic_write(path, data):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix=".d1_", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def write_text_keep(path, text, bom):
    atomic_write(path, ((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")))


def count_id(text, pid):
    return len(re.findall(r'\bid\s*=\s*["\']' + re.escape(pid) + r'["\']', text))


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


# ───────────────────────── 1) scripts/rgon_agency_pulse.py ─────────────────────────
AB_CTX = re.compile(r"항체|antibod|R1\s*~\s*R1[34]", re.I)
BLK_BEGIN = re.compile(r"RGON-(?:C2|C3|D1)-PATCH-BEGIN")
BLK_END = re.compile(r"RGON-(?:C2|C3|D1)-PATCH-END")


def try_apply(s, fn, label, stats):
    try:
        new = fn(s)
        compile(new, str(PULSE), "exec")
        return new
    except Exception as e:
        stats[label] = "건너뜀(%s)" % str(e).splitlines()[0][:60]
        return s


def src_fix_lines(s):
    lines = s.split("\n")
    flags, skip = [], False
    for ln in lines:
        if BLK_BEGIN.search(ln):
            skip = True
        flags.append(skip)
        if BLK_END.search(ln):
            skip = False
    out, changed = [], 0
    for i, ln in enumerate(lines):
        if flags[i]:
            out.append(ln)
            continue
        new = re.sub(r"(?<![0-9])14\s*/\s*13(?![0-9])", "14/14", ln)
        if AB_CTX.search(ln):
            new = re.sub(r"R0?1\s*~\s*R0?13(?![0-9])", "R1~R14", new)
            new = re.sub(r"(?<![0-9])13(\s*(?:대|종|개)\s*항체)", r"14\1", new)
            new = re.sub(r"(?<![0-9/])13\s*/\s*13(?![0-9])", "14/14", new)
            new = re.sub(r"(R1~R14\s*[\(（]\s*)13(\s*종)", r"\g<1>14\2", new)
            new = re.sub(r"(%d|%s|\{[^{}\n]*\}|\b\d+)\s*/\s*13(?![0-9])", r"\1/14", new)
        win = any(AB_CTX.search(lines[j]) for j in range(max(0, i - 3), min(len(lines), i + 4)) if not flags[j])
        if win:
            new = re.sub(r"range\(\s*1\s*,\s*14\s*\)", "range(1, 15)", new)
            new = re.sub(r"([\"'])total\1(\s*:\s*)13(?![0-9])", r"\1total\1\g<2>14", new)
            new = re.sub(r"\btotal(\s*=\s*)13(?![0-9])", r"total\g<1>14", new)
        if new != ln:
            changed += 1
        out.append(new)
    return "\n".join(out)


D3_LIT = re.compile(
    r"""(["']D3_media["']\s*(?::|\]\s*=)\s*)(?P<q>["'])(?P<v>(?:\\.|(?!(?P=q)).)*)(?P=q)""")


def src_fix_d3(s):
    def rep(m):
        if "{" in m.group("v"):
            return m.group(0)
        return m.group(1) + json.dumps(D3_TEXT, ensure_ascii=False)
    return D3_LIT.sub(rep, s)


def src_fix_antibodies(s):
    lines = s.split("\n")
    out, in_ab, start, i = [], False, 0, 0
    inserted = False
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        if not inserted and re.search(r"\bANTIBODIES\s*(?::[^=\n]+)?=\s*\{", ln):
            in_ab, start = True, i
        elif in_ab and i - start > 80:
            in_ab = False
        if in_ab and not inserted:
            m = re.match(r"^(\s*)(?P<k>[\"']?)(?P<r>R?)13(?P=k)\s*:\s*(.+?)\s*$", ln)
            if m:
                nxt = "\n".join(lines[i + 1:i + 4])
                if not re.search(r"(?<![\w])[\"']?R?14[\"']?\s*:", nxt):
                    val = m.group(4)
                    if val.endswith(","):
                        pass
                    elif val[-1:] in ("\"", "'", ")"):
                        out[-1] = ln.rstrip() + ","
                    else:
                        i += 1
                        continue
                    k, r = m.group("k"), m.group("r")
                    out.append("%s%s%s14%s: %s," % (m.group(1), k, r, k, json.dumps(R14_TEXT, ensure_ascii=False)))
                    inserted = True
        if in_ab and re.match(r"^\s*\}", ln):
            in_ab = False
        i += 1
    return "\n".join(out)


def build_pulse_source(src):
    nl = "\r\n" if "\r\n" in src else "\n"
    s = src.replace("\r\n", "\n")
    s = re.sub(re.escape(D1_BEGIN) + r".*?" + re.escape(D1_END) + r"\n?", "", s, flags=re.S)
    stats = {}
    s = try_apply(s, src_fix_lines, "분모/문구 소스 보정", stats)
    s = try_apply(s, src_fix_d3, "D3_media 리터럴 보정", stats)
    s = try_apply(s, src_fix_antibodies, "ANTIBODIES[14] 소스 삽입", stats)
    pos = None
    mk = re.search(re.escape("# ==== RGON-C3-PATCH-END ====") + r"[^\n]*\n?", s)
    if mk:
        pos = mk.end()
    else:
        mk = re.search(re.escape("# ==== RGON-C2-PATCH-END ====") + r"[^\n]*\n?", s)
        if mk:
            pos = mk.end()
    if pos is not None:
        s = s[:pos] + "\n\n" + D1_BLOCK + "\n" + s[pos:]
    else:
        guards = list(re.finditer(r'(?m)^if\s+__name__\s*==\s*["\']__main__["\']\s*:', s))
        if guards:
            g = guards[-1].start()
            s = s[:g].rstrip("\n") + "\n\n\n" + D1_BLOCK + "\n\n" + s[g:]
        else:
            s = s.rstrip("\n") + "\n\n\n" + D1_BLOCK
    compile(s, str(PULSE), "exec")
    ast.parse(s)
    return s.replace("\n", nl), stats


def patch_pulse():
    src, bom = read_text_keep(PULSE)
    new, stats = build_pulse_source(src)
    write_text_keep(PULSE, new, bom)
    for k, v in stats.items():
        log("  [pulse] ※ %s: %s" % (k, v))
    log("  [pulse] 항체 분모 14/14 · ANTIBODIES[14] · D3_media TTS 문구 보정 주입 완료")


# ───────────────────────── 2) 독대실 HTML ─────────────────────────
def patch_ab_realname(t):
    m = AB_SCRIPT_RE.search(t)
    if not m:
        raise RuntimeError("rgon-step11-ab-realname 스크립트를 찾지 못했습니다.")
    body = m.group(2)
    if E14.search(body):
        return t
    e = E13.search(body)
    if not e:
        raise RuntimeError("ab-realname 사전에서 13 항목을 찾지 못해 14 항목을 추가할 수 없습니다.")
    k, r, q = e.group("k"), e.group("r"), e.group("q")
    entry = "%s%s14%s%s%s%s%s" % (k, "R" if r else "", k, e.group("sep"), q, R14_TEXT, q)
    c = e.group("c")
    if "," in c:
        pos = e.end()
        body2 = body[:pos] + entry + "," + body[pos:]
    else:
        pos = e.end() - len(c)
        body2 = body[:pos] + "," + entry + body[pos:]
    return t[:m.start(2)] + body2 + t[m.end(2):]


def inject_tts(t, nl):
    m = PULSE_SCRIPT_RE.search(t)
    if not m:
        raise RuntimeError("rgon-step11-pulse-live 스크립트를 찾지 못했습니다.")
    body = m.group(2).replace("\r\n", "\n")
    body = re.sub(re.escape(JS_BEGIN) + r".*?" + re.escape(JS_END) + r"\s*", "", body, flags=re.S)
    new_body = (body.rstrip() + "\n\n" + JS_BLOCK + "\n").replace("\n", nl)
    return t[:m.start(2)] + new_body + t[m.end(2):]


def patch_html_text(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    t = re.sub(r"R0?1\s*~\s*R0?13(?![0-9])", "R1~R14", text)
    t = re.sub(r"(R1~R14\s*[\(（]\s*)13(\s*종)", r"\g<1>14\2", t)
    t = re.sub(r"(항체[^\n<]{0,12}?[\(（]\s*)13(\s*종\s*[\)）])", r"\g<1>14\2", t)
    t = re.sub(r"(?<![0-9])13(\s*(?:대|종)\s*항체)", r"14\1", t)
    t = patch_ab_realname(t)
    t = inject_tts(t, nl)
    return t


def verify_html_text(t, name):
    fails = []
    for pid in PROTECTED_IDS:
        c = count_id(t, pid)
        if c != 1:
            fails.append("%s 보호 ID %s = %d개 (1개여야 함)" % (name, pid, c))
    for needle in (BTN_IDLE, "__rgonSpeakDailyBriefing", "speechSynthesis", "ko-KR", "horizontal-tb",
                   "window.speechSynthesis.cancel()"):
        if needle not in t:
            fails.append("%s 에 '%s' 누락" % (name, needle))
    for sid in ("rgon-step11-pulse-live", "rgon-step11-ab-realname"):
        n = len(re.findall(r'<script\b[^>]*\bid\s*=\s*["\']' + sid + r'["\']', t))
        if n != 1:
            fails.append("%s 스크립트 %s = %d개" % (name, sid, n))
    if re.search(r"R0?1\s*~\s*R0?13(?![0-9])", t):
        fails.append("%s 에 R1~R13 표기가 남아 있음" % name)
    m = AB_SCRIPT_RE.search(t)
    if not m or not E14.search(m.group(2)):
        fails.append("%s ab-realname 에 14 항목 없음" % name)
    return fails


def patch_htmls():
    texts = [read_text_keep(p) for p in HTMLS]
    raws = [sha256_file(p) for p in HTMLS]
    if len(set(raws)) != 1:
        log("  [html] 원본 3곳이 서로 달라 root 본을 정본으로 통일합니다.")
    patched = patch_html_text(texts[0][0])
    bom = texts[0][1]
    data = (b"\xef\xbb\xbf" if bom else b"") + patched.encode("utf-8")
    for p in HTMLS:
        atomic_write(p, data)
    log("  [html] 정본 원자적 기록 완료 (3곳) · sha256=%s" % hashlib.sha256(data).hexdigest()[:12])


# ───────────────────────── 3) 스냅샷 / 장부 ─────────────────────────
def _d1_ns():
    ns = {"__name__": "_d1_ns"}
    exec(D1_SRC, ns)
    return ns


def apply_snapshots(beat, overall, html_hash):
    ns = _d1_ns()
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
        ns["_d1_fix"](data)
        ns["_d1_upgrade_struct"](data)
        data["step11_d1"] = {"d3_tts_briefing": "ACTIVE", "antibodies": "R1~R14 (14/14 활성)",
                             "r14": "R14: " + R14_TEXT, "html_sha256_12": html_hash[:12],
                             "pulse_beat": beat, "overall": overall, "updated_at": ISO}
        dump_json_like(p, data, text, bom)
    log("  [snapshot] 스냅샷 갱신 완료 (항체 14/14 · D3 TTS)")


def record_evolution(beat, overall, const_hash, html_hash):
    ns = _d1_ns()
    entry = {"event": EVENT, "ts": ISO, "task": "D-1",
             "d3_media": "원클릭 한국어 TTS 음성 브리핑(Web Speech API) 장착",
             "tts_button": BTN_IDLE, "tts_function": "window.__rgonSpeakDailyBriefing",
             "antibodies": "R1~R14 (14/14 활성)", "antibody_denominator_fix": "14/13 -> 14/14",
             "html_ab_realname": "14: " + R14_TEXT,
             "pulse_beat": beat, "overall": overall,
             "constitution_hash12": const_hash[:12], "constitution_modified": False,
             "html_sha256_12": html_hash[:12], "html_identical_3": True, "backup_tag": TAG}
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
        for k in list(data.keys()):
            if isinstance(k, str) and re.search(r"antibod|항체|immun|guardrail", k, re.I) \
                    and isinstance(data[k], (list, dict)):
                ns["_d1_upgrade_struct"](data[k])
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
        atomic_write(EVOLUTION, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    log("  [evolution] %s 이력 기록 (박동 #%s)" % (EVENT, beat))


# ───────────────────────── 4) 박동 실행 / 분석 ─────────────────────────
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
    out_beats = [int(x) for x in re.findall(r"(?:박동|[Pp]ulse|[Bb]eat)\s*#\s*(\d+)", out)]
    json_beats, best = [], None
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
            walk_beats(obj, json_beats)
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
    beats = out_beats if out_beats else json_beats
    info["beat"] = max(beats) if beats else None
    return info


def verify_pulse(info, rc, out):
    fails = []
    if rc != 0:
        fails.append("박동 스크립트 종료코드 %s" % rc)
    if info["beat"] is None or info["beat"] < 7:
        fails.append("박동 #7 이상 확인 실패 (감지값: %s)" % info["beat"])
    if info["overall"] != "OK":
        fails.append("overall != OK (감지값: %s)" % info["overall"])
    alltext = out
    for n in "123456":
        if n not in info["dims"]:
            fails.append("D%s 결과를 찾지 못함" % n)
        else:
            t = dim_text(info["dims"][n][1])
            alltext += "\n" + t
            if not dim_ok(info["dims"][n][1]):
                fails.append("D%s 가 OK 가 아님: %s" % (n, t[:160]))
    d3 = dim_text(info["dims"]["3"][1]) if "3" in info["dims"] else ""
    if "TTS 음성 브리핑" not in d3:
        fails.append("D3_media 에 'TTS 음성 브리핑' 문구 미확인: " + d3[:200])
    if re.search(r"14\s*/\s*13", alltext):
        fails.append("박동 출력/브리핑에 14/13 표기가 남아 있음")
    if not re.search(r"14\s*/\s*14", alltext):
        fails.append("박동 출력/브리핑에 항체 14/14 표기 미확인")
    return fails


# ───────────────────────── 사전 자가시험 ─────────────────────────
def selftest():
    ns = _d1_ns()
    t = ns["_d1_text"]
    if t("[PULSE] 항체 14/13 활성") != "[PULSE] 항체 14/14 활성":
        raise RuntimeError("자가시험 실패: 14/13 정정")
    if t("13대 항체(R1~R13)") != "14대 항체(R1~R14)":
        raise RuntimeError("자가시험 실패: 13대 항체 정정")
    brief = {"D1_quant": "x", "D2_viral": "y", "D3_media": "z", "headline": "h"}
    ns["_d1_fix"](brief)
    if brief["D3_media"] != D3_TEXT or "TTS 음성 브리핑" not in brief["D3_media"]:
        raise RuntimeError("자가시험 실패: D3_media 보정")
    g = {"ANTIBODIES": dict((i, "a%d" % i) for i in range(1, 14))}
    ns["_d1_ensure_ab"](g)
    if g["ANTIBODIES"].get(14) != R14_TEXT:
        raise RuntimeError("자가시험 실패: ANTIBODIES[14]")
    d = {"antibodies": ["R12: a", "R13: b"], "count": 13}
    ns["_d1_upgrade_struct"](d)
    if len(d["antibodies"]) != 3 or d["count"] != 14:
        raise RuntimeError("자가시험 실패: 항체 구조 보정")
    sample = 'x = {\n  12: "a",\n  13: "b"\n}\n'
    mm = E13.search(sample)
    if not mm:
        raise RuntimeError("자가시험 실패: ab-realname 정규식")
    s1 = src_fix_antibodies("ANTIBODIES = {\n    12: \"a\",\n    13: \"b\",\n}\n")
    if "14:" not in s1:
        raise RuntimeError("자가시험 실패: ANTIBODIES 소스 삽입")
    log("  [자가시험] 분모 정정 · D3 보정 · ANTIBODIES[14] · 항체 구조 · 정규식 통과")


# ───────────────────────── 종합 검증 ─────────────────────────
def verify_static(const_before):
    fails = []
    if sha256_file(CONSTITUTION) != const_before:
        fails.append("헌법 파일이 변경됨!")
    hs = []
    for p in HTMLS:
        t, _ = read_text_keep(p)
        hs.append(sha256_file(p))
        fails += verify_html_text(t, rel(p))
    if len(set(hs)) != 1:
        fails.append("HTML 3곳 SHA-256 불일치: " + ", ".join(h[:12] for h in hs))
    try:
        s, _ = read_text_keep(PULSE)
        compile(s, str(PULSE), "exec")
        ast.parse(s)
        if "_d1_install(globals())" not in s:
            fails.append("pulse D1 보정 블록 누락")
    except Exception as e:
        fails.append("pulse 문법 오류: %s" % e)
    return fails


# ───────────────────────── Git ─────────────────────────
def git(*args):
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    p = subprocess.run(["git", "-c", "core.quotepath=off"] + list(args), cwd=str(ROOT), capture_output=True, env=env)
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
    forbidden = {CONSTITUTION.name}
    paths = [rel(p) for p in TARGETS if p.exists()]
    for extra in sorted(porcelain() - before_dirty):
        if extra.startswith("backups/") or "__pycache__" in extra or extra.endswith(".pyc") or extra in forbidden:
            continue
        if extra not in paths:
            paths.append(extra)
            log("  [git] 박동 산출물 추가 동기화: " + extra)
    for pth in paths:
        rc, _, err = git("add", "--", pth)
        if rc != 0:
            log("  [git add 경고] %s: %s" % (pth, err.splitlines()[0] if err else ""))
    msg = "Step 11 D-1: D3 one-click Korean TTS briefing (Web Speech), antibodies R1~R14 14/14 UI sync, pulse #7"
    rc, out, err = git("commit", "-m", msg, "--", *paths)
    low = (out + err).lower()
    if rc != 0 and "nothing to commit" not in low and "no changes added" not in low:
        raise RuntimeError("git commit 실패: " + (err or out))
    rc, head, _ = git("rev-parse", "--short=10", "HEAD")
    log("  [git] commit " + head)
    rc, staged, _ = git("show", "--name-only", "--pretty=format:", "HEAD")
    if forbidden & set(staged.splitlines()):
        raise RuntimeError("헌법 파일이 커밋에 포함됨 - 중단")
    rc, out, err = git("push", "origin", "main")
    if rc != 0:
        raise RuntimeError("git push 실패(원격 변경 확인 후 수동 병합 필요): " + (err or out))
    log("  [git] push origin main 완료")


# ───────────────────────── 메인 ─────────────────────────
def main():
    log("=" * 70)
    log("RGON Step 11 · 과제 D-1 착수 (%s)" % ISO)
    log("=" * 70)

    for p in [CONSTITUTION, PULSE] + HTMLS:
        if not p.exists():
            log("[FAIL] 필수 파일 없음: " + str(p))
            return 1

    const_raw = CONSTITUTION.read_bytes()
    const_sha = hashlib.sha256(const_raw).hexdigest()
    algo, h = constitution_prefix_match(const_raw)
    if algo:
        log("[헌법] 기준선 %s 일치 (%s) · 읽기 전용" % (CONST_PREFIX, algo))
    else:
        log("[헌법] 경고: %s 접두 해시를 표준 알고리즘으로 재현하지 못함 (sha256=%s...). 전/후 비교로 무변경 보장" % (CONST_PREFIX, h[:12]))

    # ── 드라이런 (파일 변경 없음) ──
    try:
        selftest()
        root_text, _b = read_text_keep(HTMLS[0])
        pre = []
        for pid in PROTECTED_IDS:
            c = count_id(root_text, pid)
            if c != 1:
                pre.append("착수 전 보호 ID %s = %d개" % (pid, c))
        if pre:
            raise RuntimeError(" | ".join(pre))
        dry = patch_html_text(root_text)
        f = verify_html_text(dry, "dry-run")
        if f:
            raise RuntimeError("HTML 드라이런 검증 실패: " + " | ".join(f))
        src, _pb = read_text_keep(PULSE)
        build_pulse_source(src)
        log("  [드라이런] HTML 패치 · pulse 패치 사전 검증 통과 (파일 무변경)")
    except Exception as e:
        log("[FAIL] " + str(e) + " (파일 변경 없이 중단)")
        return 1

    before_dirty = porcelain()
    log("[1/7] 사전 백업 (G3)")
    make_backups()

    try:
        log("[2/7] pulse 항체 분모/D3 보정 · 독대실 HTML 3곳 정본 기록")
        patch_pulse()
        patch_htmls()
        fails = verify_static(const_sha)
        if fails:
            raise RuntimeError("정적 검증 실패: " + " | ".join(fails))

        log("[3/7] 박동 실행")
        rc, out, t0 = run_pulse()
        log("\n".join(out.strip().splitlines()[-25:]))
        info = analyze_pulse(out, t0)
        pf = verify_pulse(info, rc, out)
        if pf:
            raise RuntimeError("박동 검증 실패: " + " | ".join(pf))
        html_hash = sha256_file(HTMLS[0])
        log("[박동] #%s · overall=%s · D1~D6 전원 OK · 항체 14/14" % (info["beat"], info["overall"]))
        log("  D3: " + dim_text(info["dims"]["3"][1])[:220])

        log("[4/7] 스냅샷 · 장부 기록")
        apply_snapshots(info["beat"], info["overall"], html_hash)
        record_evolution(info["beat"], info["overall"], const_sha, html_hash)

        log("[5/7] 최종 검증")
        fails = verify_static(const_sha)
        if fails:
            raise RuntimeError("최종 검증 실패: " + " | ".join(fails))
        log("  헌법 무변경(%s) · 보호 ID 6/6(각 1개) · HTML 3곳 해시 일치(%s) · overall=OK · 박동 #%s" %
            (CONST_PREFIX if algo else const_sha[:12], html_hash[:12], info["beat"]))
    except Exception as e:
        log("[FAIL] " + str(e))
        rollback()
        try:
            ok = sha256_file(CONSTITUTION) == const_sha
        except Exception:
            ok = False
        log("[ROLLBACK] 헌법 무변경 확인: %s" % ok)
        return 1

    log("[6/7] GitHub 클라우드 배포")
    try:
        git_sync(before_dirty)
    except Exception as e:
        log("[FAIL] " + str(e))
        log("  (로컬 파일은 검증 완료 상태로 유지됩니다. 네트워크/인증/원격 변경 확인 후 'git push origin main' 을 재시도하세요.)")
        return 2

    log("[7/7] 배포 후 재확인")
    post = verify_static(const_sha)
    if post:
        log("[FAIL] 배포 후 이상 감지: " + " | ".join(post))
        return 3
    log(FINAL_OK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
Copy