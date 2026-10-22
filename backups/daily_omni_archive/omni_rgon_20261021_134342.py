#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step5_untrap_dokdae_and_solo.py  (RGON v6.0.8 / STEP 5)

Patches 3 files:
  rgon_alpha_chat.html, dashboard/rgon_alpha_chat.html, docs/rgon_alpha_chat.html

1) #dokdae-feed (and #dokdae-input) are rescued at runtime from <details> / header flex rows.
   #rgon-tools-drawer is placed full width right above the feed.
2) Vertical-text bug in the feed (name / role badge / listen button / time) is fixed with CSS + runtime tagging.
3) Legacy bundle buttons in "독대실에서 바로 분배하기" are hidden (static + runtime) and replaced
   by the 4-AI solo dispatch UI (top controller delegation + postMessage + POST 8765).
"""
import os
import re
import sys
import json
import shutil
import tempfile
import datetime
import subprocess
import html as htmlmod
from bisect import bisect_right

DEFAULT_BASE = r"C:\Users\sangi\Downloads\shin-agent"
TARGETS = [
    "rgon_alpha_chat.html",
    os.path.join("dashboard", "rgon_alpha_chat.html"),
    os.path.join("docs", "rgon_alpha_chat.html"),
]

STYLE_ID = "rgon-step5-css"
SCRIPT_ID = "rgon-step5-untrap"
PANEL_ID = "rgon-step5-solo-panel"
PANEL_BEGIN = "<!-- RGON_STEP5_PANEL_BEGIN -->"
PANEL_END = "<!-- RGON_STEP5_PANEL_END -->"
GIT_MSG = "fix(v6.0.8-step5): untrap dokdae-feed from tools drawer, fix vertical text & unify solo dispatch"
DONE_MARK = "[STEP 5 UNTRAP DOKDAE & SOLO UNIFY COMPLETE]"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def info(msg):
    print("[step5] " + msg)


def warn(msg):
    print("[step5][WARN] " + msg)


def err(msg):
    print("[step5][ERROR] " + msg, file=sys.stderr)


PANEL_INNER = """
<div class="r5-title">🎯 4대 AI 발사 대상 (상단 컨트롤러 v6.0.8 동일 구조)</div>
<div class="r5-checks">
<label class="r5-chk"><input type="checkbox" class="r5-chk-input" value="rgon"> <span>🔵👑 르곤 (Gemini 4 Argon)</span></label>
<label class="r5-chk"><input type="checkbox" class="r5-chk-input" value="claude" checked> <span>🧠 Claude</span></label>
<label class="r5-chk"><input type="checkbox" class="r5-chk-input" value="gpt" checked> <span>⚡ GPT</span></label>
<label class="r5-chk"><input type="checkbox" class="r5-chk-input" value="grok"> <span>🎯 Grok</span></label>
</div>
<div class="r5-mini">
<button type="button" class="r5-btn r5-mini-btn" data-r5-act="all">☑ 전체 선택</button>
<button type="button" class="r5-btn r5-mini-btn" data-r5-act="none">☐ 전체 해제</button>
</div>
<div class="r5-grid">
<button type="button" class="r5-btn r5-solo" data-role="rgon">🔵👑 르곤 (Gemini 4 Argon) 단독</button>
<button type="button" class="r5-btn r5-solo" data-role="claude">🧠 Claude 단독</button>
<button type="button" class="r5-btn r5-solo" data-role="gpt">⚡ GPT 단독</button>
<button type="button" class="r5-btn r5-solo" data-role="grok">🎯 Grok 단독</button>
</div>
<div class="r5-run">
<button type="button" class="r5-btn r5-green" data-r5-act="selected">🚀 체크 선택 발사</button>
<button type="button" class="r5-btn r5-teal" data-r5-act="fire-all">🌐 전체 발사</button>
</div>
"""

STATIC_PANEL = (
    PANEL_BEGIN + "\n"
    + '<div id="' + PANEL_ID + '" class="r5-panel" data-step5="static">'
    + PANEL_INNER + "</div>\n" + PANEL_END + "\n"
)

CSS = r"""
/* RGON_STEP5_STYLE_BEGIN */
#rgon-tools-drawer{width:100% !important;max-width:100% !important;flex:0 0 100% !important;flex-basis:100% !important;box-sizing:border-box !important;}
#dokdae-feed{width:100% !important;max-width:100% !important;flex:1 1 auto !important;min-height:320px !important;box-sizing:border-box !important;overflow-y:auto !important;}
#rgon-omni-drawer:not([open]),#rgon-omni-top-drawer:not([open]){min-height:0 !important;height:auto !important;flex:0 0 auto !important;}
#dokdae-feed,#dokdae-feed *{writing-mode:horizontal-tb !important;}
#dokdae-feed button,#dokdae-feed time,#dokdae-feed .badge,
#dokdae-feed [class*="badge"],#dokdae-feed [class*="author"],#dokdae-feed [class*="sender"],
#dokdae-feed [class*="name"],#dokdae-feed [class*="time"],#dokdae-feed [class*="stamp"],
#dokdae-feed [class*="chip"],#dokdae-feed [class*="speak"],#dokdae-feed [class*="tts"],
#dokdae-feed [class*="listen"],#dokdae-feed .r5-nowrap{white-space:nowrap !important;word-break:keep-all !important;}
#dokdae-feed .r5-nowrap{flex:0 0 auto !important;width:max-content !important;max-width:none !important;}
#dokdae-feed .r5-msg-head,#dokdae-feed [class*="msg-head"],#dokdae-feed [class*="bubble-head"],
#dokdae-feed [class*="msg-meta"],#dokdae-feed [class*="message-meta"]{display:flex !important;flex-wrap:wrap !important;align-items:center !important;gap:6px !important;}
#rgon-step5-solo-panel{width:100% !important;flex:0 0 100% !important;box-sizing:border-box !important;margin:8px 0;padding:10px;border:1px solid rgba(99,102,241,.4);border-radius:12px;background:rgba(15,23,42,.88);color:#e2e8f0;font-size:13px;}
#rgon-step5-solo-panel .r5-title{font-weight:700;margin-bottom:8px;word-break:keep-all;}
#rgon-step5-solo-panel .r5-checks{display:flex;flex-direction:column;gap:6px;}
#rgon-step5-solo-panel .r5-chk{display:flex;align-items:center;gap:8px;cursor:pointer;word-break:keep-all;}
#rgon-step5-solo-panel .r5-mini{display:flex;gap:6px;margin:8px 0;flex-wrap:wrap;}
#rgon-step5-solo-panel .r5-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;}
#rgon-step5-solo-panel .r5-run{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;}
#rgon-step5-solo-panel .r5-btn{cursor:pointer;border-radius:8px;border:1px solid rgba(148,163,184,.45);background:rgba(30,41,59,.92);color:#e2e8f0;padding:8px 10px;font-size:12px;font-weight:600;line-height:1.3;word-break:keep-all;white-space:normal;writing-mode:horizontal-tb;}
#rgon-step5-solo-panel .r5-mini-btn{white-space:nowrap;}
#rgon-step5-solo-panel .r5-solo{width:100%;}
#rgon-step5-solo-panel .r5-green{background:#16a34a;border-color:#22c55e;color:#fff;flex:1 1 auto;}
#rgon-step5-solo-panel .r5-teal{background:#0d9488;border-color:#14b8a6;color:#fff;flex:1 1 auto;}
#rgon-step5-solo-panel .r5-btn:active{transform:translateY(1px);}
[data-step5-legacy="1"]{display:none !important;}
#rgon-step5-toast{position:fixed;left:50%;bottom:84px;transform:translateX(-50%);max-width:92vw;padding:9px 14px;border-radius:10px;background:rgba(2,6,23,.94);color:#e2e8f0;border:1px solid rgba(99,102,241,.55);font-size:12px;z-index:2147483000;opacity:0;pointer-events:none;transition:opacity .2s ease;word-break:keep-all;}
#rgon-step5-toast.r5-toast-on{opacity:1;}
/* RGON_STEP5_STYLE_END */
"""

JS_TEMPLATE = r"""
/* RGON_STEP5_BEGIN */
(function () {
  'use strict';
  if (window.__RGON_STEP5__) { return; }
  window.__RGON_STEP5__ = { version: 'step5', organize: null, fire: null };

  var ROLES = ['rgon', 'claude', 'gpt', 'grok'];
  var LABELS = {
    rgon: '🔵👑 르곤 (Gemini 4 Argon)',
    claude: '🧠 Claude',
    gpt: '⚡ GPT',
    grok: '🎯 Grok'
  };
  var PANEL_ID = 'rgon-step5-solo-panel';
  var TOAST_ID = 'rgon-step5-toast';
  var STORE_KEY = 'rgon_omni_checked_step5';
  var BRIDGE_URL = 'http://127.0.0.1:8765/api/dispatch';
  var PANEL_HTML = __PANEL_HTML__;
  var LEGACY_RE = /(GPT\s*동시\s*발사|Grok\s*카피\s*발사)/i;
  var TITLE_RE = /1:1\s*(전담|총괄)|전담\s*독대실|총괄\s*독대/;
  var NAME_RE = /(르곤\s*[-\u2010-\u2015]?\s*알파|대시보드\s*총괄\s*사령관|총괄\s*사령관|^[^가-힣A-Za-z0-9]*듣기[^가-힣A-Za-z0-9]*$|^[^0-9]{0,6}\d{1,2}:\d{2}(:\d{2})?\s*$)/;
  var REPL = [
    [/v6\.0\.3/g, 'v6.0.8'],
    [/\(\s*Claude\s*\/\s*GPT\s*\/\s*Grok\s*\)/g, '(👑르곤 / 🧠Claude / ⚡GPT / 🎯Grok)']
  ];

  function byId(id) { return document.getElementById(id); }
  function inPanel(el) { return !!(el && el.closest && el.closest('#' + PANEL_ID)); }
  function cleanText(el) { return ((el && el.textContent) || '').replace(/\s+/g, ' ').trim(); }

  function toast(msg, ms) {
    try {
      var t = byId(TOAST_ID);
      if (!t) {
        t = document.createElement('div');
        t.id = TOAST_ID;
        t.setAttribute('role', 'status');
        (document.body || document.documentElement).appendChild(t);
      }
      t.textContent = msg;
      t.className = 'r5-toast-on';
      clearTimeout(toast._t);
      toast._t = setTimeout(function () { t.className = ''; }, ms || 3500);
    } catch (e) {}
  }

  function isRowFlex(el) {
    try {
      var cs = window.getComputedStyle(el);
      return /flex/.test(cs.display) && /^row/.test(cs.flexDirection);
    } catch (e) { return false; }
  }

  function hasTitle(root, feed) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    var n, c = 0;
    while ((n = w.nextNode()) && c < 300) {
      c++;
      if (feed && feed.contains(n)) { continue; }
      if (TITLE_RE.test(n.nodeValue || '')) { return true; }
    }
    return false;
  }

  function isHeaderish(a, feed, input) {
    if (!a || a === document.body || a === document.documentElement) { return false; }
    if (input && a.contains(input)) { return false; }
    var tag = (a.tagName || '').toUpperCase();
    if (tag === 'HEADER') { return true; }
    var cls = (typeof a.className === 'string' ? a.className : '') + ' ' + (a.id || '');
    if (/(^|[\s_-])(header|topbar|titlebar|navbar)([\s_-]|$)/i.test(cls)) { return true; }
    if (isRowFlex(a)) {
      if (a.querySelector('#rgon-tools-drawer')) { return true; }
      if (hasTitle(a, feed)) { return true; }
    }
    return false;
  }

  function untrapFeed() {
    var feed = byId('dokdae-feed');
    if (!feed) { return null; }
    var input = byId('dokdae-input');
    var trap = null;
    var p = feed.parentElement;
    while (p && p !== document.body && p !== document.documentElement) {
      if (p.tagName === 'DETAILS' || isHeaderish(p, feed, input)) { trap = p; }
      p = p.parentElement;
    }
    if (!trap) { return feed; }
    var par = trap.parentNode;
    var placed = false;
    if (input && !trap.contains(input)) {
      var top = par;
      while (top && top !== document.documentElement && !top.contains(input)) { top = top.parentNode; }
      if (top && top.contains(input)) {
        var ib = input;
        while (ib.parentNode && ib.parentNode !== top) { ib = ib.parentNode; }
        if (ib.parentNode === top && !ib.contains(feed)) {
          top.insertBefore(feed, ib);
          placed = true;
        }
      }
    }
    if (!placed && par) { par.insertBefore(feed, trap.nextSibling); }
    feed.setAttribute('data-r5-untrapped', '1');
    return feed;
  }

  function untrapInput(feed) {
    var input = byId('dokdae-input');
    if (!input) { return; }
    var outer = null;
    var p = input.parentElement;
    while (p && p !== document.body) {
      if (p.tagName === 'DETAILS') { outer = p; }
      p = p.parentElement;
    }
    if (!outer) { return; }
    var area = input;
    while (area.parentElement && area.parentElement !== outer &&
           !area.parentElement.querySelector('details, #dokdae-feed')) {
      area = area.parentElement;
    }
    if (feed && feed.parentNode && !outer.contains(feed)) {
      feed.parentNode.insertBefore(area, feed.nextSibling);
    } else if (outer.parentNode) {
      outer.parentNode.insertBefore(area, outer.nextSibling);
    }
  }

  function placeDrawer(feed) {
    var d = byId('rgon-tools-drawer');
    if (!d || !feed || !feed.parentNode || d.contains(feed)) { return; }
    var before = (d.compareDocumentPosition(feed) & 4) !== 0;
    if (d.parentNode !== feed.parentNode || !before) {
      feed.parentNode.insertBefore(d, feed);
    }
  }

  function fixBubbles(feed) {
    var all = feed.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.getAttribute('data-r5')) { continue; }
      var tg = el.tagName;
      if (tg === 'SCRIPT' || tg === 'STYLE' || tg === 'TEXTAREA') { continue; }
      if (el.children.length > 1) { continue; }
      var txt = cleanText(el);
      if (!txt || txt.length > 40) { continue; }
      if (!NAME_RE.test(txt)) { continue; }
      el.setAttribute('data-r5', '1');
      el.classList.add('r5-nowrap');
      var row = el.parentElement;
      while (row && row !== feed && row.children.length < 2) { row = row.parentElement; }
      if (row && row !== feed && cleanText(row).length <= 90) {
        row.classList.add('r5-msg-head');
      }
    }
  }

  function fixTexts() {
    if (!document.body) { return; }
    var roots = [];
    Array.prototype.forEach.call(
      document.querySelectorAll('#rgon-omni-drawer, #rgon-omni-top-drawer'),
      function (e) { roots.push(e); }
    );
    var feed = byId('dokdae-feed');
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
    var n;
    while ((n = w.nextNode())) {
      var v = n.nodeValue;
      if (!v || !/분배\s*컨트롤러/.test(v)) { continue; }
      var pe = n.parentElement;
      if (!pe || (feed && feed.contains(pe))) { continue; }
      var root = pe.closest('details, section, fieldset') || pe.parentElement || pe;
      if (roots.indexOf(root) < 0) { roots.push(root); }
    }
    roots.forEach(function (r) {
      var tw = document.createTreeWalker(r, NodeFilter.SHOW_TEXT, null, false);
      var list = [];
      var t;
      while ((t = tw.nextNode())) {
        var s = t.nodeValue;
        if (!s) { continue; }
        if (s.indexOf('v6.0.3') < 0 && s.indexOf('Claude') < 0) { continue; }
        var pt = t.parentNode && t.parentNode.tagName;
        if (pt === 'SCRIPT' || pt === 'STYLE' || pt === 'TEXTAREA' || pt === 'NOSCRIPT') { continue; }
        if (feed && feed.contains(t)) { continue; }
        list.push(t);
      }
      list.forEach(function (tn) {
        var orig = tn.nodeValue;
        var cur = orig;
        REPL.forEach(function (pair) { cur = cur.replace(pair[0], pair[1]); });
        if (cur !== orig) { tn.nodeValue = cur; }
      });
    });
  }

  function loadState() {
    try {
      var o = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
      return (o && typeof o === 'object') ? o : null;
    } catch (e) { return null; }
  }
  function saveState(panel) {
    try {
      var o = {};
      Array.prototype.forEach.call(panel.querySelectorAll('input.r5-chk-input'), function (i) {
        o[i.value] = !!i.checked;
      });
      localStorage.setItem(STORE_KEY, JSON.stringify(o));
    } catch (e) {}
  }
  function restoreState(panel) {
    var o = loadState();
    if (!o) { return; }
    Array.prototype.forEach.call(panel.querySelectorAll('input.r5-chk-input'), function (i) {
      if (typeof o[i.value] === 'boolean') { i.checked = o[i.value]; }
    });
  }
  function checkedRoles(panel) {
    var out = [];
    ROLES.forEach(function (r) {
      var i = panel.querySelector('input.r5-chk-input[value="' + r + '"]');
      if (i && i.checked) { out.push(r); }
    });
    return out;
  }

  function readVal(el) { return (el && typeof el.value === 'string') ? el.value : ''; }

  function getPrompt(panel) {
    var list = [];
    var main = byId('dokdae-input');
    if (main) { list.push(main); }
    var sec = panel.closest ? panel.closest('details') : null;
    if (sec) {
      Array.prototype.forEach.call(sec.querySelectorAll('textarea, input[type="text"]'), function (e) { list.push(e); });
    }
    Array.prototype.forEach.call(
      document.querySelectorAll('#rgon-omni-drawer textarea, #rgon-omni-top-drawer textarea'),
      function (e) { list.push(e); }
    );
    for (var i = 0; i < list.length; i++) {
      if (inPanel(list[i])) { continue; }
      var v = readVal(list[i]);
      if (v.trim()) { return { text: v, el: list[i] }; }
    }
    return { text: '', el: main || null };
  }

  function topAreas() {
    var out = [];
    Array.prototype.forEach.call(
      document.querySelectorAll('#rgon-omni-drawer textarea, #rgon-omni-top-drawer textarea'),
      function (a) { if (!inPanel(a)) { out.push(a); } }
    );
    return out;
  }

  function syncPromptToTop(text) {
    topAreas().forEach(function (a) {
      if (a.value !== text) {
        a.value = text;
        try {
          a.dispatchEvent(new Event('input', { bubbles: true }));
          a.dispatchEvent(new Event('change', { bubbles: true }));
        } catch (e) {}
      }
    });
  }

  function topSoloButton(role) {
    var nodes = document.querySelectorAll(
      '#rgon-omni-drawer [data-solo="' + role + '"], #rgon-omni-drawer button[data-role="' + role + '"], ' +
      '#rgon-omni-top-drawer [data-solo="' + role + '"], #rgon-omni-top-drawer button[data-role="' + role + '"]'
    );
    for (var i = 0; i < nodes.length; i++) {
      if (!inPanel(nodes[i])) { return nodes[i]; }
    }
    return null;
  }

  function delegateTop(roles) {
    var clicked = false;
    roles.forEach(function (r) {
      var b = topSoloButton(r);
      if (b) {
        try { b.click(); clicked = true; } catch (e) {}
      }
    });
    return clicked;
  }

  function postBridge(roles, text, reqId) {
    if (typeof fetch !== 'function') { return Promise.resolve({ ok: false, reason: 'no-fetch' }); }
    var ctl = (typeof AbortController === 'function') ? new AbortController() : null;
    var tm = ctl ? setTimeout(function () { try { ctl.abort(); } catch (e) {} }, 8000) : 0;
    var opts = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roles: roles, prompt: text, text: text, req_id: reqId, source: 'rgon-step5' })
    };
    if (ctl) { opts.signal = ctl.signal; }
    return fetch(BRIDGE_URL, opts).then(function (res) {
      clearTimeout(tm);
      return res.json().then(function (j) { return { res: res, j: j }; }, function () { return { res: res, j: null }; });
    }).then(function (pack) {
      if (pack.j && pack.j.source === 'rgon-safety-shield') { return { ok: false, reason: 'shield' }; }
      return { ok: !!pack.res.ok, status: pack.res.status };
    }).catch(function (e) {
      clearTimeout(tm);
      return { ok: false, reason: String((e && e.message) || e) };
    });
  }

  function fire(panel, roles) {
    var list = ROLES.filter(function (r) { return roles.indexOf(r) >= 0; });
    if (!list.length) { toast('⚠️ 발사 대상을 체크하세요.'); return; }
    var got = getPrompt(panel);
    if (!got.text || !got.text.trim()) {
      toast('⚠️ 발사할 지시문을 입력하세요.');
      var f = got.el || byId('dokdae-input');
      if (f && f.focus) { try { f.focus(); } catch (e0) {} }
      return;
    }
    var text = got.text;
    var reqId = 'r5-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8);
    var viaTop = false;
    var viaMsg = false;
    try {
      syncPromptToTop(text);
      viaTop = delegateTop(list);
    } catch (e1) { viaTop = false; }
    try {
      window.postMessage({
        type: 'RGON_OMNI_DISPATCH',
        roles: list.slice(),
        prompt: text,
        text: text,
        req_id: reqId,
        source: 'rgon-step5'
      }, '*');
      viaMsg = true;
    } catch (e2) { viaMsg = false; }
    var names = list.map(function (r) { return LABELS[r]; }).join(' · ');
    toast('🚀 ' + names + ' 발사 요청 전송 중…');
    postBridge(list, text, reqId).then(function (r) {
      toast('🚀 ' + names + ' 발사 요청 완료 · 상단 위임 ' + (viaTop ? '✓' : '–') +
        ' · 확장 메시지 ' + (viaMsg ? '✓' : '–') +
        ' · 로컬 브릿지 ' + (r && r.ok ? '✓' : '✗(8765 미응답)'), 5200);
    });
  }

  function legacyButtons() {
    var out = [];
    Array.prototype.forEach.call(document.querySelectorAll('button, [role="button"]'), function (b) {
      if (inPanel(b)) { return; }
      if (b.closest && b.closest('#rgon-omni-drawer, #rgon-omni-top-drawer')) { return; }
      if (LEGACY_RE.test(cleanText(b))) { out.push(b); }
    });
    return out;
  }

  function hideLegacy(b) {
    if (b.getAttribute('data-step5-legacy') === '1' && b.hidden) { return; }
    b.setAttribute('data-step5-legacy', '1');
    b.hidden = true;
    try { b.style.setProperty('display', 'none', 'important'); } catch (e) {}
  }

  function findHeadingAnchor() {
    var cands = document.querySelectorAll('summary, h1, h2, h3, h4, h5, div, span, b, strong, p');
    for (var i = 0; i < cands.length; i++) {
      var c = cands[i];
      if (inPanel(c)) { continue; }
      var t = cleanText(c);
      if (t.length < 80 && /독대실에서\s*바로\s*분배하기/.test(t)) {
        var host = c.closest('details') || c.parentElement;
        if (host) { return host; }
      }
    }
    return null;
  }

  function bindPanel(panel) {
    if (panel.getAttribute('data-r5-bound') === '1') { return; }
    panel.setAttribute('data-r5-bound', '1');
    restoreState(panel);
    panel.addEventListener('change', function (ev) {
      var t = ev.target;
      if (t && t.classList && t.classList.contains('r5-chk-input')) { saveState(panel); }
    });
    panel.addEventListener('click', function (ev) {
      var t = (ev.target && ev.target.closest) ? ev.target.closest('[data-r5-act], [data-role]') : null;
      if (!t || !panel.contains(t)) { return; }
      var act = t.getAttribute('data-r5-act');
      var role = t.getAttribute('data-role');
      ev.preventDefault();
      if (act === 'all' || act === 'none') {
        Array.prototype.forEach.call(panel.querySelectorAll('input.r5-chk-input'), function (i) {
          i.checked = (act === 'all');
        });
        saveState(panel);
        return;
      }
      if (act === 'selected') { fire(panel, checkedRoles(panel)); return; }
      if (act === 'fire-all') { fire(panel, ROLES.slice()); return; }
      if (role) { fire(panel, [role]); }
    });
  }

  function ensurePanel() {
    var legacy = legacyButtons();
    legacy.forEach(hideLegacy);
    var panel = byId(PANEL_ID);
    if (!panel) {
      var host = null;
      var before = null;
      if (legacy.length) {
        before = legacy[0];
        host = before.parentNode;
      } else {
        host = findHeadingAnchor();
      }
      if (!host) { return null; }
      panel = document.createElement('div');
      panel.id = PANEL_ID;
      panel.className = 'r5-panel';
      panel.setAttribute('data-step5', 'runtime');
      panel.innerHTML = PANEL_HTML;
      if (before) { host.insertBefore(panel, before); } else { host.appendChild(panel); }
    } else if (!panel.querySelector('[data-role]')) {
      panel.innerHTML = PANEL_HTML;
      panel.removeAttribute('data-r5-bound');
    }
    bindPanel(panel);
    return panel;
  }

  function keepCollect() {
    Array.prototype.forEach.call(document.querySelectorAll('button'), function (b) {
      if (inPanel(b)) { return; }
      if (/AI\s*탭\s*코드\s*수거/.test(b.textContent || '')) {
        b.setAttribute('data-step5-keep', '1');
        if (b.hidden) { b.hidden = false; }
        if (b.style && b.style.display === 'none') { b.style.removeProperty('display'); }
      }
    });
  }

  var timer = 0;
  var busy = false;
  var lastTexts = 0;

  function organize() {
    if (busy) { return; }
    busy = true;
    try {
      var feed = untrapFeed();
      untrapInput(feed);
      if (feed) {
        placeDrawer(feed);
        fixBubbles(feed);
      }
      ensurePanel();
      keepCollect();
      var now = Date.now();
      if (now - lastTexts > 1500) { lastTexts = now; fixTexts(); }
    } catch (e) {}
    busy = false;
  }

  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(organize, 90);
  }

  function start() {
    organize();
    [150, 400, 1000, 2500, 5000, 9000].forEach(function (ms) { setTimeout(organize, ms); });
    try {
      new MutationObserver(schedule).observe(document.documentElement, { childList: true, subtree: true });
    } catch (e) {}
    setInterval(organize, 2500);
  }

  window.__RGON_STEP5__.organize = organize;
  window.__RGON_STEP5__.fire = function (roles) {
    var p = byId(PANEL_ID) || ensurePanel();
    if (p) { fire(p, roles && roles.length ? roles : ROLES.slice()); }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
  window.addEventListener('load', schedule);
})();
/* RGON_STEP5_END */
"""


def ascii_escape(s):
    out = []
    for ch in s:
        o = ord(ch)
        if o < 128:
            out.append(ch)
        elif o <= 0xFFFF:
            out.append("\\u%04x" % o)
        else:
            o -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
    return "".join(out)


def html_ascii(s):
    return "".join(c if ord(c) < 128 else "&#x%X;" % ord(c) for c in s)


def build_js():
    panel_js = json.dumps(PANEL_INNER.strip()).replace("</", "<\\/")
    js = JS_TEMPLATE.replace("__PANEL_HTML__", panel_js)
    return ascii_escape(js.strip() + "\n")


def check_safe(js):
    low = js.lower()
    for bad in ("</script", "<!--", "-->"):
        if bad in low:
            raise ValueError("unsafe sequence in injected JS: " + bad)


def node_check(js):
    node = shutil.which("node")
    if not node:
        return None, "node not found"
    fd, name = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(js)
        r = subprocess.run([node, "--check", name], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        return r.returncode == 0, (r.stderr or r.stdout or "").strip()
    finally:
        try:
            os.unlink(name)
        except OSError:
            pass


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if bom else raw
    try:
        txt = body.decode("utf-8")
        enc = "utf-8"
    except UnicodeDecodeError:
        txt = body.decode("cp949")
        enc = "cp949"
    crlf = txt.count("\r\n")
    lf = txt.count("\n") - crlf
    nl = "\r\n" if crlf > lf else "\n"
    return txt.replace("\r\n", "\n"), enc, bom, nl


def write_text(path, txt, enc, bom, nl):
    data = txt.replace("\n", nl).encode(enc)
    if bom and enc == "utf-8":
        data = b"\xef\xbb\xbf" + data
    tmp = path + ".step5.tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


SPAN_RE = re.compile(r"<!--.*?-->|<script\b.*?</script\s*>|<style\b.*?</style\s*>", re.S | re.I)


def skip_spans(html):
    starts, ends = [], []
    for m in SPAN_RE.finditer(html):
        starts.append(m.start())
        ends.append(m.end())
    return starts, ends


def in_spans(pos, sp):
    i = bisect_right(sp[0], pos) - 1
    return i >= 0 and pos < sp[1][i]


def find_close_tag(html, tag):
    sp = skip_spans(html)
    last = -1
    for m in re.finditer(r"</\s*" + tag + r"\s*>", html, re.I):
        if not in_spans(m.start(), sp):
            last = m.start()
    return last


STEP4_STYLE_RE = re.compile(
    r"[ \t]*<style\b[^>]*\bid\s*=\s*[\"']rgon-step4-solo-css[\"'][^>]*>.*?</style\s*>[ \t]*\n?", re.S | re.I)
STEP4_SCRIPT_RE = re.compile(
    r"[ \t]*<script\b[^>]*\bid\s*=\s*[\"']rgon-step4-solo-unify[\"'][^>]*>.*?</script\s*>[ \t]*\n?", re.S | re.I)
STEP5_STYLE_RE = re.compile(
    r"[ \t]*<style\b[^>]*\bid\s*=\s*[\"']" + STYLE_ID + r"[\"'][^>]*>.*?</style\s*>[ \t]*\n?", re.S | re.I)
STEP5_SCRIPT_RE = re.compile(
    r"[ \t]*<script\b[^>]*\bid\s*=\s*[\"']" + SCRIPT_ID + r"[\"'][^>]*>.*?</script\s*>[ \t]*\n?", re.S | re.I)
PANEL_RE = re.compile(re.escape(PANEL_BEGIN) + r".*?" + re.escape(PANEL_END) + r"[ \t]*\n?", re.S)

BUTTON_RE = re.compile(
    r"(?P<open><button\b(?:\"[^\"]*\"|'[^']*'|[^>\"'])*>)(?P<inner>.*?)</button\s*>", re.S | re.I)
TAG_STRIP_RE = re.compile(r"<[^>]*>")
LEGACY_PY = re.compile(r"GPT\s*동시\s*발사|Grok\s*카피\s*발사", re.I)
COUNT_TAGS = ["div", "details", "summary", "button", "section", "span", "label", "input",
              "textarea", "script", "style", "header", "main", "form", "select", "option"]


def strip_step5(html):
    html = STEP5_STYLE_RE.sub("", html)
    html = STEP5_SCRIPT_RE.sub("", html)
    html = PANEL_RE.sub("", html)
    return html


def strip_ours(html):
    html = STEP4_STYLE_RE.sub("", html)
    html = STEP4_SCRIPT_RE.sub("", html)
    return strip_step5(html)


def tag_counts(html):
    out = {}
    for t in COUNT_TAGS:
        out[t] = (len(re.findall(r"<" + t + r"\b", html, re.I)),
                  len(re.findall(r"</" + t + r"\s*>", html, re.I)))
    return out


def add_hide(open_tag):
    if "data-step5-legacy" in open_tag:
        return open_tag
    m = re.search(r"(\sstyle\s*=\s*)([\"'])(.*?)\2", open_tag, re.S | re.I)
    if m:
        new_style = m.group(1) + m.group(2) + "display:none !important;" + m.group(3) + m.group(2)
        t = open_tag[:m.start()] + new_style + open_tag[m.end():]
    else:
        t = open_tag[:-1] + ' style="display:none !important">'
    extra = ""
    if not re.search(r"\shidden\b", t, re.I):
        extra += " hidden"
    extra += ' data-step5-legacy="1"'
    return t[:-1] + extra + ">"


def hide_legacy(html):
    sp = skip_spans(html)
    out = []
    last = 0
    outlen = 0
    count = 0
    first = None
    for m in BUTTON_RE.finditer(html):
        if in_spans(m.start(), sp):
            continue
        txt = htmlmod.unescape(TAG_STRIP_RE.sub("", m.group("inner")))
        txt = re.sub(r"\s+", " ", txt)
        if not LEGACY_PY.search(txt):
            continue
        seg = html[last:m.start("open")]
        out.append(seg)
        outlen += len(seg)
        if first is None:
            first = outlen
        new_open = add_hide(m.group("open"))
        out.append(new_open)
        outlen += len(new_open)
        last = m.end("open")
        count += 1
    out.append(html[last:])
    return "".join(out), first, count


def patch_html(original, enc, css_block, script_block):
    base = strip_ours(original)
    removed4 = (len(STEP4_STYLE_RE.findall(original)) + len(STEP4_SCRIPT_RE.findall(original)))
    h, first, nhid = hide_legacy(base)
    has_panel = False
    if first is not None:
        panel = STATIC_PANEL if enc == "utf-8" else html_ascii(STATIC_PANEL)
        h = h[:first] + panel + h[first:]
        has_panel = True

    head_pos = find_close_tag(h, "head")
    if head_pos >= 0:
        h = h[:head_pos] + css_block + h[head_pos:]
        inject = script_block
    else:
        inject = css_block + script_block
    body_pos = find_close_tag(h, "body")
    if body_pos >= 0:
        h = h[:body_pos] + inject + h[body_pos:]
    else:
        h = h + "\n" + inject

    for rid in (STYLE_ID, SCRIPT_ID):
        if len(re.findall(r"\bid\s*=\s*[\"']" + rid + r"[\"']", h)) != 1:
            raise RuntimeError("verification failed: block id %s count != 1" % rid)
    if h.count(PANEL_BEGIN) != (1 if has_panel else 0):
        raise RuntimeError("verification failed: static panel marker count mismatch")
    if h.count('data-step5-legacy="1"') < nhid:
        raise RuntimeError("verification failed: legacy hide attribute count mismatch")
    if tag_counts(strip_step5(h)) != tag_counts(base):
        raise RuntimeError("verification failed: tag balance changed")
    for ident in ("dokdae-feed", "dokdae-input", "rgon-tools-drawer"):
        pat = r"\bid\s*=\s*[\"']" + ident + r"[\"']"
        if len(re.findall(pat, h)) != len(re.findall(pat, base)):
            raise RuntimeError("verification failed: id %s count changed" % ident)
    return h, {"legacy_hidden": nhid, "static_panel": has_panel, "step4_blocks_removed": removed4}


def run_git(base, args):
    return subprocess.run(["git"] + args, cwd=base, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=180)


def git_publish(base):
    if not os.path.isdir(os.path.join(base, ".git")):
        warn("no .git folder in BASE - git step skipped")
        return
    try:
        for args in (["add", "-A"], ["commit", "-m", GIT_MSG], ["push", "origin", "main"]):
            r = run_git(base, args)
            out = ((r.stdout or "") + (r.stderr or "")).strip()
            tail = out[-400:] if out else ""
            if r.returncode != 0:
                if args[0] == "commit" and "nothing to commit" in out.lower():
                    info("git commit: nothing to commit")
                    continue
                warn("git %s failed (rc=%s): %s" % (" ".join(args[:2]), r.returncode, tail))
                if args[0] == "push":
                    return
            else:
                info("git %s ok" % args[0])
    except FileNotFoundError:
        warn("git executable not found - git step skipped")
    except subprocess.TimeoutExpired:
        warn("git command timed out")


def main():
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base = os.path.abspath(args[0]) if args else DEFAULT_BASE
    no_git = "--no-git" in flags
    no_node = "--no-node-check" in flags
    dry = "--dry-run" in flags

    targets = []
    for rel in TARGETS:
        p = os.path.join(base, rel)
        if os.path.isfile(p):
            targets.append((rel, p))
        else:
            warn("target not found, skipped: " + p)
    if not targets:
        err("no target files found under " + base)
        return 1

    try:
        js = build_js()
        check_safe(js)
        check_safe(CSS)
    except ValueError as e:
        err(str(e))
        return 2

    if not no_node:
        ok, msg = node_check(js)
        if ok is None:
            warn("node not available - JS syntax check skipped (" + msg + ")")
        elif not ok:
            err("node --check failed for injected JS:\n" + msg)
            return 3
        else:
            info("node --check passed for injected JS")

    css_block = '<style id="' + STYLE_ID + '">' + CSS + "</style>\n"
    script_block = '<script id="' + SCRIPT_ID + '">\n' + js + "</script>\n"

    plans = []
    for rel, p in targets:
        try:
            txt, enc, bom, nl = read_text(p)
            new, stats = patch_html(txt, enc, css_block, script_block)
            if enc != "utf-8":
                try:
                    new.encode(enc)
                except UnicodeEncodeError:
                    raise RuntimeError("non-encodable characters for " + enc)
            plans.append((rel, p, txt, new, enc, bom, nl, stats))
            info("planned %s: legacy buttons hidden=%d, static panel=%s, step4 blocks replaced=%d"
                 % (rel, stats["legacy_hidden"], stats["static_panel"], stats["step4_blocks_removed"]))
        except Exception as e:
            err("patch failed for %s: %s" % (rel, e))
            return 4

    if dry:
        info("--dry-run: no files written")
        print(DONE_MARK)
        return 0

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = os.path.join(base, "backups", "step5_" + stamp)
    try:
        os.makedirs(bdir, exist_ok=True)
        for rel, p, *_ in plans:
            shutil.copy2(p, os.path.join(bdir, rel.replace(os.sep, "__").replace("/", "__")))
        info("backup saved to " + bdir)
    except OSError as e:
        err("backup failed: %s" % e)
        return 5

    written = []
    try:
        for rel, p, old, new, enc, bom, nl, stats in plans:
            write_text(p, new, enc, bom, nl)
            written.append((p, rel))
            chk, _, _, _ = read_text(p)
            if chk != new:
                raise RuntimeError("read-back mismatch: " + rel)
            info("patched " + rel)
    except Exception as e:
        err("write failed: %s - restoring originals" % e)
        for p, rel in written + [(pl[1], pl[0]) for pl in plans if (pl[1], pl[0]) not in written]:
            src = os.path.join(bdir, rel.replace(os.sep, "__").replace("/", "__"))
            try:
                if os.path.isfile(src):
                    shutil.copy2(src, p)
            except OSError:
                pass
            try:
                if os.path.isfile(p + ".step5.tmp"):
                    os.unlink(p + ".step5.tmp")
            except OSError:
                pass
        return 5

    if no_git:
        info("--no-git: git step skipped")
    else:
        git_publish(base)

    print("")
    info("Reload the page (Ctrl+F5 / mobile hard refresh) to see the rescued #dokdae-feed layout.")
    print(DONE_MARK)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
Copy