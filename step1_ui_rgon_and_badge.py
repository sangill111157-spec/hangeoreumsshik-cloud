#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step1_ui_rgon_and_badge.py
RGON Aside Extension  v6.0.7 -> v6.0.8  (STEP 1: UI-only patch)

Uses only the Python standard library (open / re / json / shutil, plus os / sys).

What it does
  1. Adds { role:'rgon', icon:'🔵', label:'👑 르곤 보좌관 (Gemini 4 Argon)', def:false } as the FIRST entry of
     DEFAULT_ROLES (content_aside_bar.js incl. the RGON_V607 block, and background.js).
     - Registers the gemini alias so the rgon row's connection badge can count Gemini tabs.
     - Adds an <option value="rgon"> next to the claude option (#roleSel).
     - Clones single-line claude role entries (lamps / role tables) when the pattern is recognisable.
     - Removes `role !== 'rgon'` style exclusions.
     - Does NOT touch ensureTargetRows / updateTargetRowStatus, so the v6.0.7 checkbox-preserving
       structure (rows built once, refreshScan updates only the badge textContent) stays intact.
  2. Appends a FAB module (RGON_V608_FAB_BEGIN ~ END) to content_aside_bar.js:
     - compact translucent pill (padding 5px 10px; font-size 12px; opacity 0.78), full label on :hover
     - mouse drag (>= 5px = move instead of click), position kept in localStorage "rgon_omni_fab_pos"
  3. Version 6.0.7 -> 6.0.8 in manifest.json / background.js / content_aside_bar.js.
  4. Originals are backed up once as <file>.bak_step1 (an existing backup is never overwritten).

Usage:  python step1_ui_rgon_and_badge.py [EXTENSION_DIR]
"""
import os
import re
import sys
import json
import shutil

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = r"C:\Users\sangi\Downloads\shin-agent\rgon_aside_extension"
if len(sys.argv) > 1:
    BASE = sys.argv[1]

CONTENT = os.path.join(BASE, "content_aside_bar.js")
BACKGROUND = os.path.join(BASE, "background.js")
MANIFEST = os.path.join(BASE, "manifest.json")

OLD_VER = "6.0.7"
NEW_VER = "6.0.8"
VER_RE = re.compile(r"(?<![\d.])" + re.escape(OLD_VER) + r"(?![\d.])")

RGON_LABEL = "👑 르곤 보좌관 (Gemini 4 Argon)"
RGON_ICON = "🔵"
RGON_ENTRY = "{ role: 'rgon', icon: '" + RGON_ICON + "', label: '" + RGON_LABEL + "', def: false }"
RGON_PRESENT_RE = re.compile(r"""(['"])rgon\1|\brgon\s*:""")

FAB_BEGIN = "/* RGON_V608_FAB_BEGIN */"
FAB_END = "/* RGON_V608_FAB_END */"

# ---------------------------------------------------------------------------
# FAB module (appended as an independent IIFE at the end of content_aside_bar.js)
# ---------------------------------------------------------------------------
FAB_JS = r"""/* RGON_V608_FAB_BEGIN */
;(function () {
  'use strict';
  try {
    if (window.__RGON_V608_FAB__) { return; }
    window.__RGON_V608_FAB__ = true;
  } catch (e) {}

  var POS_KEY = 'rgon_omni_fab_pos';
  var STYLE_ID = 'rgon-v608-fab-style';
  var KEY_TEXT = /르곤\s*만능\s*소통창|Omni-?Link/i;
  var ID_SELECTORS = [
    '#rgon-omni-fab', '#rgon-omni-toggle', '#omni-fab', '#rgon-fab',
    '[id*="omni"][id*="fab"]', '[id*="omni"][id*="toggle"]'
  ];
  var OBS = { childList: true, characterData: true, subtree: true };
  var CSS = [
    '.rgon-fab-compact{padding:5px 10px !important;font-size:12px !important;line-height:1.3 !important;',
    'white-space:nowrap !important;width:auto !important;min-width:0 !important;max-width:none !important;',
    'height:auto !important;min-height:0 !important;border-radius:999px !important;box-sizing:border-box !important;',
    'cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none;',
    'transition:opacity .2s ease, box-shadow .2s ease;}',
    '.rgon-fab-compact:hover{opacity:1 !important;}',
    '.rgon-fab-compact.rgon-fab-dragging{cursor:grabbing;opacity:1 !important;transition:none;}',
    '.rgon-fab-compact .rgon-fab-full{display:inline-block;max-width:0;overflow:hidden;opacity:0;',
    'white-space:nowrap;margin:0;vertical-align:middle;',
    'transition:max-width .28s ease, opacity .2s ease, margin .28s ease;}',
    '.rgon-fab-compact:hover .rgon-fab-full,.rgon-fab-compact.rgon-fab-dragging .rgon-fab-full{',
    'max-width:340px;opacity:1;margin:0 6px;}',
    '.rgon-fab-compact .rgon-fab-n{display:inline-block;min-width:16px;padding:0 5px;margin-left:4px;',
    'border-radius:999px;background:rgba(255,255,255,.22);text-align:center;font-weight:700;}'
  ].join('');

  var current = null;
  var tries = 0;

  /* ---------- small helpers ---------- */
  function mk(cls, text) {
    var s = document.createElement('span');
    s.className = cls;
    s.textContent = text;
    return s;
  }
  function hasOurClass(n) {
    var c = n && n.classList;
    return !!(c && (c.contains('rgon-fab-ic') || c.contains('rgon-fab-full') || c.contains('rgon-fab-n')));
  }
  function clamp(v, lo, hi) { return Math.min(Math.max(v, lo), hi); }
  function setImp(el, name, val) { el.style.setProperty(name, val, 'important'); }

  /* ---------- stored position ---------- */
  function loadPos() {
    try {
      var raw = localStorage.getItem(POS_KEY);
      if (!raw) { return null; }
      var o = JSON.parse(raw);
      if (o && typeof o.top === 'number' && (typeof o.left === 'number' || typeof o.right === 'number')) { return o; }
    } catch (e) {}
    return null;
  }
  function savePos(o) {
    try { localStorage.setItem(POS_KEY, JSON.stringify(o)); } catch (e) {}
  }
  function applyPos(el, pos) {
    var w = el.offsetWidth || 40;
    var h = el.offsetHeight || 24;
    var vw = window.innerWidth;
    var vh = window.innerHeight;
    setImp(el, 'top', clamp(pos.top, 0, Math.max(0, vh - h)) + 'px');
    setImp(el, 'bottom', 'auto');
    if (typeof pos.right === 'number') {
      setImp(el, 'right', clamp(pos.right, 0, Math.max(0, vw - w)) + 'px');
      setImp(el, 'left', 'auto');
    } else {
      setImp(el, 'left', clamp(pos.left, 0, Math.max(0, vw - w)) + 'px');
      setImp(el, 'right', 'auto');
    }
  }
  function defaultPos(el) {
    setImp(el, 'right', '2px');
    setImp(el, 'left', 'auto');
  }

  /* ---------- style ---------- */
  function ensureStyle(el) {
    try {
      var root = el.getRootNode ? el.getRootNode() : document;
      var host = (root && root.nodeType === 11) ? root : (document.head || document.documentElement);
      if (host.querySelector('#' + STYLE_ID)) { return; }
      var st = document.createElement('style');
      st.id = STYLE_ID;
      st.textContent = CSS;
      host.appendChild(st);
    } catch (e) {}
  }

  /* ---------- compact the label: icon / full label / count ---------- */
  function splitText(v) {
    var m = /^\s*(✨\uFE0F?)?\s*([\s\S]*?)\s*(\d+)?\s*$/.exec(v);
    if (!m) { return null; }
    return { ic: m[1], label: m[2], n: m[3] };
  }
  function processTextNode(tn) {
    var p = tn.parentNode;
    if (!p || p.nodeType !== 1 || hasOurClass(p)) { return false; }
    var v = tn.nodeValue;
    if (!v || !v.trim()) { return false; }
    var s = splitText(v);
    if (!s) { return false; }
    var frag = document.createDocumentFragment();
    if (s.ic) { frag.appendChild(mk('rgon-fab-ic', '✨')); }
    if (s.label) { frag.appendChild(mk('rgon-fab-full', s.label)); }
    if (s.n) { frag.appendChild(mk('rgon-fab-n', s.n)); }
    if (!frag.childNodes.length) { return false; }
    p.replaceChild(frag, tn);
    return true;
  }
  function compact(el) {
    if (!el || !el.isConnected) { return; }
    (function walk(node, depth) {
      var kids = Array.prototype.slice.call(node.childNodes);
      for (var i = 0; i < kids.length; i++) {
        var k = kids[i];
        if (k.nodeType === 3) {
          processTextNode(k);
        } else if (k.nodeType === 1 && depth < 2 && !hasOurClass(k) && !/^(SCRIPT|STYLE|SVG)$/i.test(k.tagName)) {
          walk(k, depth + 1);
        }
      }
    })(el, 0);
    if (el.querySelector('.rgon-fab-full') && !el.querySelector('.rgon-fab-ic')) {
      el.insertBefore(mk('rgon-fab-ic', '✨'), el.firstChild);
    }
  }

  /* ---------- drag (>= 5px = move, otherwise a normal click) ---------- */
  function bindDrag(el) {
    var st = null;
    var suppress = false;

    function onMove(ev) {
      if (!st) { return; }
      var dx = ev.clientX - st.x;
      var dy = ev.clientY - st.y;
      if (!st.moved) {
        if (Math.sqrt(dx * dx + dy * dy) < 5) { return; }
        st.moved = true;
        el.classList.add('rgon-fab-dragging');
      }
      try { ev.preventDefault(); } catch (e) {}
      var nl = clamp(st.left + dx, 0, Math.max(0, window.innerWidth - st.w));
      var nt = clamp(st.top + dy, 0, Math.max(0, window.innerHeight - st.h));
      setImp(el, 'left', nl + 'px');
      setImp(el, 'top', nt + 'px');
      setImp(el, 'right', 'auto');
      setImp(el, 'bottom', 'auto');
    }
    function onUp() {
      window.removeEventListener('mousemove', onMove, true);
      window.removeEventListener('mouseup', onUp, true);
      var s = st;
      st = null;
      if (!s || !s.moved) { return; }
      el.classList.remove('rgon-fab-dragging');
      suppress = true;
      setTimeout(function () { suppress = false; }, 80);
      var r = el.getBoundingClientRect();
      var vw = window.innerWidth;
      var pos;
      if (r.left + r.width / 2 > vw / 2) {
        pos = { top: Math.round(r.top), right: Math.round(Math.max(0, vw - r.right)) };
      } else {
        pos = { top: Math.round(r.top), left: Math.round(Math.max(0, r.left)) };
      }
      savePos(pos);
      applyPos(el, pos);
    }

    el.addEventListener('mousedown', function (ev) {
      if (ev.button !== 0) { return; }
      var r = el.getBoundingClientRect();
      st = { x: ev.clientX, y: ev.clientY, left: r.left, top: r.top, w: r.width, h: r.height, moved: false };
      window.addEventListener('mousemove', onMove, true);
      window.addEventListener('mouseup', onUp, true);
    }, true);

    window.addEventListener('click', function (ev) {
      if (!suppress) { return; }
      var path = ev.composedPath ? ev.composedPath() : [];
      if (path.indexOf(el) !== -1) {
        suppress = false;
        ev.preventDefault();
        ev.stopPropagation();
        ev.stopImmediatePropagation();
      }
    }, true);
  }

  /* ---------- find the launcher ---------- */
  function getRoots() {
    var roots = [document];
    try {
      var all = document.querySelectorAll('*');
      for (var i = 0; i < all.length && i < 8000; i++) {
        if (all[i].shadowRoot) { roots.push(all[i].shadowRoot); }
      }
    } catch (e) {}
    return roots;
  }
  function isFixed(el) {
    try { return getComputedStyle(el).position === 'fixed'; } catch (e) { return false; }
  }
  function looksLikeFab(el) {
    return !!el && (el.textContent || '').length < 200;
  }
  function findFab() {
    var roots = getRoots();
    var i, j, el;
    for (i = 0; i < roots.length; i++) {
      for (j = 0; j < ID_SELECTORS.length; j++) {
        try { el = roots[i].querySelector(ID_SELECTORS[j]); } catch (e) { el = null; }
        if (el && looksLikeFab(el)) { return el; }
      }
    }
    for (i = 0; i < roots.length; i++) {
      var walker;
      try { walker = document.createTreeWalker(roots[i], NodeFilter.SHOW_TEXT, null); } catch (e) { continue; }
      var node, guard = 0;
      while ((node = walker.nextNode()) && guard++ < 30000) {
        var v = node.nodeValue;
        if (!v || v.length > 120 || !KEY_TEXT.test(v)) { continue; }
        var cur = node.parentElement;
        var up = 0;
        while (cur && up < 4) {
          if (isFixed(cur)) {
            if (looksLikeFab(cur)) { return cur; }
            break;
          }
          cur = cur.parentElement;
          up++;
        }
      }
    }
    return null;
  }

  /* ---------- attach ---------- */
  function attach(el) {
    if (el.__rgonV608Fab) { return; }
    el.__rgonV608Fab = true;
    ensureStyle(el);
    el.classList.add('rgon-fab-compact');
    el.style.opacity = '0.78';
    if (!el.getAttribute('title')) {
      el.setAttribute('title', '✨ 르곤 만능 소통창 (Omni-Link) — 드래그로 이동');
    }
    compact(el);
    var mo = new MutationObserver(function () {
      mo.disconnect();
      try { compact(el); } catch (e) {}
      try { mo.observe(el, OBS); } catch (e) {}
    });
    mo.observe(el, OBS);
    var saved = loadPos();
    if (saved) { applyPos(el, saved); } else { defaultPos(el); }
    bindDrag(el);
  }

  function tick() {
    try {
      if (current && !current.isConnected) { current = null; }
      if (!current) {
        var f = findFab();
        if (f) { current = f; attach(f); }
      } else {
        if (!current.classList.contains('rgon-fab-compact')) { current.classList.add('rgon-fab-compact'); }
        ensureStyle(current);
      }
    } catch (e) {}
    tries++;
    var delay = current ? 2000 : (tries < 20 ? 1000 : 4000);
    setTimeout(tick, delay);
  }

  window.addEventListener('resize', function () {
    try {
      if (!current) { return; }
      var p = loadPos();
      if (p) { applyPos(current, p); }
    } catch (e) {}
  });

  tick();
})();
/* RGON_V608_FAB_END */"""


# ---------------------------------------------------------------------------
# file helpers
# ---------------------------------------------------------------------------
def info(msg=""):
    print(msg)


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
        enc = "utf-8"
    except UnicodeDecodeError:
        text = raw.decode("cp949")
        enc = "cp949"
    crlf = "\r\n" in text
    return text.replace("\r\n", "\n"), {"bom": bom, "crlf": crlf, "enc": enc}


def write_text(path, text, meta):
    if meta.get("crlf"):
        text = text.replace("\n", "\r\n")
    data = text.encode(meta.get("enc", "utf-8"))
    if meta.get("bom"):
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def bracket_delta(s):
    return (s.count("(") - s.count(")"),
            s.count("[") - s.count("]"),
            s.count("{") - s.count("}"))


def find_matching(s, open_idx):
    """Return the index of the bracket closing s[open_idx] (string/comment aware), or None."""
    close_of = {"[": "]", "{": "}", "(": ")"}
    stack = []
    i, n = open_idx, len(s)
    while i < n:
        ch = s[i]
        nx = s[i + 1] if i + 1 < n else ""
        if ch == "/" and nx == "/":
            j = s.find("\n", i)
            i = n if j < 0 else j
            continue
        if ch == "/" and nx == "*":
            j = s.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if ch in "'\"`":
            q = ch
            i += 1
            while i < n and s[i] != q:
                if s[i] == "\\":
                    i += 1
                i += 1
            i += 1
            continue
        if ch in close_of:
            stack.append(close_of[ch])
        elif ch in ")]}":
            if not stack or stack.pop() != ch:
                return None
            if not stack:
                return i
        i += 1
    return None


# ---------------------------------------------------------------------------
# role patching
# ---------------------------------------------------------------------------
DR_RE = re.compile(r"\bDEFAULT_ROLES\s*[:=]\s*(?:Object\.freeze\(\s*)?([\[{])")


def insert_default_roles(s):
    """Put the rgon entry first in every DEFAULT_ROLES definition. Returns (text, added, skipped_notes)."""
    pos, added, notes = 0, 0, []
    while True:
        m = DR_RE.search(s, pos)
        if not m:
            break
        o = m.end(1) - 1
        c = find_matching(s, o)
        if c is None:
            notes.append("DEFAULT_ROLES bracket matching failed (char %d)" % o)
            pos = m.end()
            continue
        body = s[o + 1:c]
        if RGON_PRESENT_RE.search(body):
            pos = c
            continue
        opener = s[o]
        if opener == "{":
            entry = "rgon: " + RGON_ENTRY
        elif re.search(r"\brole\s*:", body):
            entry = RGON_ENTRY
        elif "{" not in body and re.search(r"""['"]claude['"]""", body):
            entry = "'rgon'"
        else:
            notes.append("DEFAULT_ROLES has an unknown shape, add rgon manually (char %d)" % o)
            pos = c
            continue
        mi = re.match(r"[ \t]*\n([ \t]*)", body)
        if body.strip() == "":
            ins = " " + entry + " "
        elif mi:
            ins = "\n" + mi.group(1) + entry + ","
        else:
            ins = " " + entry + ","
        s = s[:o + 1] + ins + s[o + 1:]
        pos = c + len(ins)
        added += 1
    return s, added, notes


def patch_aliases(s):
    cnt = 0
    m = re.search(r"\bvar\s+KEY_ALIAS\s*=\s*\{", s)
    if m:
        c = find_matching(s, m.end() - 1)
        if c and "rgon" not in s[m.end():c]:
            s = s[:m.end()] + " gemini: 'rgon', argon: 'rgon'," + s[m.end():]
            cnt += 1
    m = re.search(r"\bvar\s+URL_ALIAS\s*=\s*\[", s)
    if m:
        c = find_matching(s, m.end() - 1)
        if c and "rgon" not in s[m.end():c]:
            s = s[:m.end()] + " [/gemini\\.google\\.com/i, 'rgon']," + s[m.end():]
            cnt += 1
    return s, cnt


EXCLUSION_PATTERNS = [
    re.compile(r"""\.filter\(\s*function\s*\(\s*\w+\s*\)\s*\{\s*return\s+[\w$.]+\s*!==?\s*(['"])rgon\1\s*;?\s*\}\s*\)"""),
    re.compile(r"""\.filter\(\s*\(?\s*\w+\s*\)?\s*=>\s*[\w$.]+\s*!==?\s*(['"])rgon\1\s*\)"""),
    re.compile(r"""\s*&&\s*[\w$.]+\s*!==?\s*(['"])rgon\1"""),
    re.compile(r"""[\w$.]+\s*!==?\s*(['"])rgon\1\s*&&\s*"""),
]


def strip_exclusions(s):
    total = 0
    for pat in EXCLUSION_PATTERNS:
        s, n = pat.subn("", s)
        total += n
    return s, total


OPT_RE = re.compile(r"""<option\b([^<>]*?)value=(\\?["'])claude\2([^<>]*)>([^<]*)</option>""")


def insert_options(s):
    if re.search(r"""value=\\?["']rgon\\?["']""", s):
        return s, 0
    cnt = [0]

    def repl(m):
        pre, q, post = m.group(1), m.group(2), m.group(3)
        post = re.sub(r"""\s*\bselected\b(?:=\\?["'][^"']*\\?["'])?""", "", post)
        pre = re.sub(r"""\s*\bselected\b(?:=\\?["'][^"']*\\?["'])?""", "", pre)
        new = "<option" + pre + "value=" + q + "rgon" + q + post + ">" + RGON_ICON + " " + RGON_LABEL + "</option>"
        cnt[0] += 1
        return new + m.group(0)

    s = OPT_RE.sub(repl, s)
    return s, cnt[0]


ICON_FIELD_RE = re.compile(r"""(\b(?:icon|emoji|lamp|dot)\s*:\s*)(['"`])(?:(?!\2).)*\2""")
LABEL_FIELD_RE = re.compile(r"""(\b(?:label|name|title|text|display|displayName)\s*:\s*)(['"`])(?:(?!\2).)*\2""")
CLAUDE_Q_RE = re.compile(r"""(['"])claude\1""")
GPT_KEY_RE = re.compile(r"""^\s*(['"]?)(?:gpt|chatgpt)\1\s*:""")
GPT_Q_RE = re.compile(r"""(['"])(?:gpt|chatgpt)\1""")


def transform_claude_line(line, keyed):
    new = line
    if keyed:
        new = re.sub(r"""^(\s*)(['"]?)claude\2""", r"\1\2rgon\2", new, count=1)
        if re.search(r""":\s*(true|false)\s*,?\s*$""", new):
            new = re.sub(r""":\s*(true|false)(\s*,?\s*)$""", r": false\2", new)
    new = CLAUDE_Q_RE.sub(r"\1rgon\1", new)
    new = re.sub(r"""https?://[^'"\s]*claude[^'"\s]*""", "https://gemini.google.com/app", new, flags=re.I)
    new = re.sub(r"claude\.ai", "gemini.google.com", new, flags=re.I)
    has_icon_field = bool(ICON_FIELD_RE.search(line))
    new = ICON_FIELD_RE.sub(lambda m: m.group(1) + "'" + RGON_ICON + "'", new)

    def label_repl(m):
        orig = m.group(0)
        mq = re.search(r"""(['"`])(.*)\1""", orig)
        val = mq.group(2) if mq else ""
        lead = (not has_icon_field) and val[:1] and ord(val[0]) > 0x2000
        text = (RGON_ICON + " " + RGON_LABEL) if lead else RGON_LABEL
        return m.group(1) + "'" + text + "'"

    new = LABEL_FIELD_RE.sub(label_repl, new)
    if re.search("claude", new, re.I):
        return None
    if new == line:
        return None
    if not new.rstrip().endswith(","):
        new = new.rstrip() + ","
    return new


def clone_role_lines(s):
    """Clone single-line claude entries (array objects or key: value maps) that sit next to a gpt entry."""
    lines = s.split("\n")
    out, added, skipped = [], 0, []
    n = len(lines)
    for i, line in enumerate(lines):
        keyed = bool(re.match(r"""^\s*(['"]?)claude\1\s*:""", line))
        objline = line.strip().startswith("{") and CLAUDE_Q_RE.search(line)
        if keyed or objline:
            nxt = lines[i + 1:i + 4]
            near = "\n".join(lines[max(0, i - 4):i + 6])
            gpt_next = any((GPT_KEY_RE.match(x) if keyed else GPT_Q_RE.search(x)) for x in nxt)
            if gpt_next and not RGON_PRESENT_RE.search(near):
                cloned = transform_claude_line(line, keyed)
                if cloned:
                    out.append(cloned)
                    added += 1
                else:
                    skipped.append(i + 1)
        out.append(line)
    return "\n".join(out), added, skipped


def report_candidates(s, fname, limit=20):
    lines = s.split("\n")
    shown = 0
    for i, line in enumerate(lines):
        if re.search("claude", line, re.I) and not RGON_PRESENT_RE.search("\n".join(lines[max(0, i - 6):i + 7])):
            if shown == 0:
                info("   [check] %s: lines mentioning claude with no nearby rgon (review if the 5th AI is still missing)" % fname)
            info("      L%-5d %s" % (i + 1, line.strip()[:110]))
            shown += 1
            if shown >= limit:
                info("      ... (more omitted)")
                break
    leftovers = []
    for i, line in enumerate(lines):
        if RGON_PRESENT_RE.search(line) and re.search(r"\b(continue|skip|exclude|includes|indexOf)\b|!==?", line):
            leftovers.append((i + 1, line.strip()[:110]))
    for ln, txt in leftovers[:15]:
        info("   [check] %s L%d (possible rgon exclusion): %s" % (fname, ln, txt))


# ---------------------------------------------------------------------------
# per-file patchers
# ---------------------------------------------------------------------------
def patch_roles_common(s, fname, stats):
    s, added, notes = insert_default_roles(s)
    stats["default_roles"] = added
    for note in notes:
        info("   [warn] %s: %s" % (fname, note))
    s, n_excl = strip_exclusions(s)
    stats["exclusions_removed"] = n_excl
    s, n_clone, skipped = clone_role_lines(s)
    stats["cloned_lines"] = n_clone
    if skipped:
        info("   [warn] %s: could not auto-clone the claude entries on lines %s (add rgon there manually)"
             % (fname, ", ".join(str(x) for x in skipped)))
    return s


def patch_content(src):
    stats = {}
    s = re.sub(r"\n*;?[ \t]*/\* RGON_V608_FAB_BEGIN \*/.*?/\* RGON_V608_FAB_END \*/\n*", "\n", src, flags=re.S)
    base = bracket_delta(s)
    s, n_ver = VER_RE.subn(NEW_VER, s)
    stats["version_refs"] = n_ver
    s = patch_roles_common(s, "content_aside_bar.js", stats)
    s, stats["aliases"] = patch_aliases(s)
    s, stats["options"] = insert_options(s)
    if bracket_delta(s) != base:
        raise RuntimeError("bracket balance changed in content_aside_bar.js, aborting without writing")
    s = s.rstrip("\n") + "\n\n" + FAB_JS + "\n"
    return s, stats


def patch_background(src):
    stats = {}
    base = bracket_delta(src)
    s, n_ver = VER_RE.subn(NEW_VER, src)
    stats["version_refs"] = n_ver
    s = patch_roles_common(s, "background.js", stats)
    if bracket_delta(s) != base:
        raise RuntimeError("bracket balance changed in background.js, aborting without writing")
    return s, stats


def patch_manifest(src):
    s, n = re.subn(r'("version"\s*:\s*")[^"]*(")', r"\g<1>" + NEW_VER + r"\g<2>", src, count=1)
    s = VER_RE.sub(NEW_VER, s)
    data = json.loads(s)
    if data.get("version") != NEW_VER:
        raise RuntimeError("failed to set the manifest.json version")
    return s, n


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    info("=" * 64)
    info(" RGON Aside Extension  v%s -> v%s  (STEP 1 UI PATCH)" % (OLD_VER, NEW_VER))
    info(" folder: " + BASE)
    info("=" * 64)

    for p in (CONTENT, BACKGROUND, MANIFEST):
        if not os.path.isfile(p):
            info("[ERROR] file not found: " + p)
            sys.exit(1)

    originals = {}
    for p in (CONTENT, BACKGROUND, MANIFEST):
        originals[p] = read_text(p)

    # backups (an existing .bak_step1 is the true original, so never overwrite it)
    for p in (CONTENT, BACKGROUND, MANIFEST):
        bak = p + ".bak_step1"
        if os.path.exists(bak):
            info("[BACKUP] already exists, kept: " + os.path.basename(bak))
        else:
            shutil.copy2(p, bak)
            info("[BACKUP] " + os.path.basename(bak))

    # compute everything in memory first
    try:
        c_text, c_meta = originals[CONTENT]
        b_text, b_meta = originals[BACKGROUND]
        m_text, m_meta = originals[MANIFEST]
        new_c, c_stats = patch_content(c_text)
        new_b, b_stats = patch_background(b_text)
        new_m, _ = patch_manifest(m_text)
    except Exception as e:
        info("[ERROR] patch computation failed, no file was modified: %r" % (e,))
        sys.exit(2)

    # write
    try:
        write_text(CONTENT, new_c, c_meta)
        write_text(BACKGROUND, new_b, b_meta)
        write_text(MANIFEST, new_m, m_meta)
    except Exception as e:
        info("[ERROR] write failed, restoring the originals: %r" % (e,))
        for p, (t, meta) in originals.items():
            try:
                write_text(p, t, meta)
            except Exception:
                pass
        sys.exit(3)

    info("")
    info("[content_aside_bar.js]")
    info("   - version refs 6.0.7 -> 6.0.8   : %d" % c_stats["version_refs"])
    info("   - DEFAULT_ROLES rgon inserted   : %d" % c_stats["default_roles"])
    info("   - alias (KEY/URL_ALIAS) patched : %d" % c_stats["aliases"])
    info("   - <option value=rgon> inserted  : %d" % c_stats["options"])
    info("   - cloned role lines             : %d" % c_stats["cloned_lines"])
    info("   - rgon exclusions removed       : %d" % c_stats["exclusions_removed"])
    info("   - FAB module (compact + drag)   : appended")
    info("[background.js]")
    info("   - version refs 6.0.7 -> 6.0.8   : %d" % b_stats["version_refs"])
    info("   - DEFAULT_ROLES rgon inserted   : %d" % b_stats["default_roles"])
    info("   - cloned role lines             : %d" % b_stats["cloned_lines"])
    info("   - rgon exclusions removed       : %d" % b_stats["exclusions_removed"])
    info("[manifest.json]")
    info("   - version -> %s" % NEW_VER)

    info("")
    report_candidates(new_c, "content_aside_bar.js")
    report_candidates(new_b, "background.js")

    info("")
    info("Next: run `node --check content_aside_bar.js` and `node --check background.js` in the extension folder,")
    info("      then reload the extension at chrome://extensions and refresh the pages.")
    info("[STEP 1 UI PATCH COMPLETE]")


if __name__ == "__main__":
    main()
