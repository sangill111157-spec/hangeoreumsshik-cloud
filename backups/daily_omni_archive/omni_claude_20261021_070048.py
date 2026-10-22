#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step2_mobile_clean_layout.py
RGON dashboard STEP 2 : mobile clean layout (UI / CSS only)

Targets (under C:\\Users\\sangi\\Downloads\\shin-agent):
  rgon_alpha_chat.html, dashboard/rgon_alpha_chat.html, docs/rgon_alpha_chat.html
  pwa_bootstrap.js,     dashboard/pwa_bootstrap.js,     docs/pwa_bootstrap.js

What it does
  1. "5G 터널 추적 ON" badge: nowrap / width:max-content / word-break:keep-all.
     On mobile widths (max-width:768px) in the dokdae page it is pinned small in the bottom-right corner
     with pointer-events:none, so it never covers the content or blocks a button.
  2. Omni-Link controller and the blue "AI 만능 소통창 열기" box are moved into ONE collapsed
     <details id="rgon-omni-top-drawer">. A 🔵 👑 르곤 (Gemini 4 Argon) row is guaranteed next to
     Claude / GPT / Grok. On mobile, "확장프로그램 확인 중..." becomes the mobile direct-mode text.
  3. The top command buttons, the Adobe free-3 box and the voice settings are moved into
     <details id="rgon-tools-drawer" class="rgon-compact-drawer">.
     The elements are only moved, never rebuilt, so IDs, onclick handlers, listeners and the
     STUDIO v5 script keep working. Fixed-position modals inside them are hoisted to <body>.
  4. #dokdae-feed gets min-height:45vh; max-height:62vh; overflow-y:auto.

Safety
  - Only the markers RGON_STEP2_* are added. The RGON_AUTO_SYNC_MASTER block and the STUDIO v5
    script are never touched. Before writing, the script checks that stripping its own additions
    gives back exactly the original text.
  - A <file>.bak_step2 backup is made first (an existing backup is never overwritten).
  - Re-running is safe: previous STEP2 blocks are replaced.

Usage:  python step2_mobile_clean_layout.py [BASE_DIR]
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

BASE = r"C:\Users\sangi\Downloads\shin-agent"
if len(sys.argv) > 1:
    BASE = sys.argv[1]

HTML_FILES = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
PWA_FILES = ["pwa_bootstrap.js", "dashboard/pwa_bootstrap.js", "docs/pwa_bootstrap.js"]

OMNI_SUMMARY = "📡 4대 AI (👑르곤 · 🧠Claude · ⚡GPT · 🔥Grok) 분배 컨트롤러 & 만능 소통창 펼치기 ▼"
TOOLS_SUMMARY = "🧰 6대 기관 지휘 · Adobe STUDIO v5 · 음성 도구함 펼치기 ▼"
MOBILE_TEXT = "📱 모바일 직결 모드 (클릭 시 지시문 복사 및 독대실 전달)"
RGON_LABEL = "🔵 👑 르곤 (Gemini 4 Argon)"

# ---------------------------------------------------------------------------
# Static CSS (injected into the <head> of the dokdae HTML files)
# ---------------------------------------------------------------------------
STATIC_CSS = r"""
details.rgon-compact-drawer{margin:6px 0;border-radius:10px;border:1px solid rgba(99,102,241,0.35);background:rgba(15,23,42,0.85);padding:6px 10px;color:#e0e7ff;box-sizing:border-box;max-width:100%;}
details.rgon-compact-drawer>summary{cursor:pointer;font-size:12.5px;font-weight:600;line-height:1.45;list-style:none;color:#c7d2fe;user-select:none;-webkit-user-select:none;padding:3px 0;word-break:keep-all;}
details.rgon-compact-drawer>summary::-webkit-details-marker{display:none;}
details.rgon-compact-drawer[open]>summary{margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid rgba(99,102,241,0.25);}
details.rgon-compact-drawer>.rgon-drawer-body{max-height:58vh;overflow-y:auto;-webkit-overflow-scrolling:touch;}
#dokdae-feed,.rgon-feed-main{min-height:45vh !important;max-height:62vh !important;overflow-y:auto !important;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;}
@media (max-width:768px){#dokdae-feed,.rgon-feed-main{min-height:48vh !important;max-height:62vh !important;}}
.rgon-tunnel-badge,#tunnelBadge,#tunnel-badge,#rgon-tunnel-badge,.tunnel-badge,[id*="tunnel"][id*="badge" i],[class*="tunnel"][class*="badge" i]{white-space:nowrap !important;width:max-content !important;max-width:90vw !important;word-break:keep-all !important;overflow-wrap:normal !important;writing-mode:horizontal-tb !important;}
@media (max-width:768px){.rgon-tunnel-badge,#tunnelBadge,#tunnel-badge,#rgon-tunnel-badge,.tunnel-badge,[id*="tunnel"][id*="badge" i],[class*="tunnel"][class*="badge" i]{position:fixed !important;top:auto !important;left:auto !important;right:6px !important;bottom:6px !important;transform:none !important;margin:0 !important;padding:2px 7px !important;font-size:10px !important;line-height:1.25 !important;opacity:0.72 !important;pointer-events:none !important;z-index:40 !important;}}
"""

# ---------------------------------------------------------------------------
# JS module 1: tunnel badge fix (also appended to pwa_bootstrap.js)
# ---------------------------------------------------------------------------
TUNNEL_JS = r"""
;(function () {
  'use strict';
  if (window.__RGON_STEP2_TUNNEL__) { return; }
  window.__RGON_STEP2_TUNNEL__ = true;

  var RE = /5G\s*터널\s*추적/;
  var STYLE_ID = 'rgon-step2-tunnel-style';
  var CSS = '.rgon-tunnel-badge{white-space:nowrap !important;width:max-content !important;max-width:90vw !important;word-break:keep-all !important;overflow-wrap:normal !important;writing-mode:horizontal-tb !important;box-sizing:border-box !important;}' +
    '@media (max-width:768px){html.rgon-dokdae-page .rgon-tunnel-badge{position:fixed !important;top:auto !important;left:auto !important;right:6px !important;bottom:6px !important;transform:none !important;margin:0 !important;padding:2px 7px !important;font-size:10px !important;line-height:1.25 !important;opacity:0.72 !important;pointer-events:none !important;z-index:40 !important;}}';

  function isDokdae() {
    try { return /rgon_alpha_chat/i.test(location.pathname) || !!document.getElementById('dokdae-feed'); }
    catch (e) { return false; }
  }
  function norm(el) { return (el.textContent || '').replace(/\s+/g, ' ').trim(); }
  function ensureStyle() {
    if (document.getElementById(STYLE_ID)) { return; }
    var host = document.head || document.documentElement;
    if (!host) { return; }
    var st = document.createElement('style');
    st.id = STYLE_ID;
    st.textContent = CSS;
    host.appendChild(st);
  }
  function tag(el) {
    var base = norm(el);
    var cur = el;
    var n = 0;
    while (cur && cur !== document.body && cur !== document.documentElement && n < 4) {
      if (n > 0 && norm(cur) !== base) { break; }
      cur.classList.add('rgon-tunnel-badge');
      cur = cur.parentElement;
      n++;
    }
  }
  function tagNode(node) {
    var el = node.parentElement;
    if (!el || el.classList.contains('rgon-tunnel-badge')) { return; }
    if (norm(el).length > 80) {
      var sp = document.createElement('span');
      node.parentNode.insertBefore(sp, node);
      sp.appendChild(node);
      el = sp;
    }
    tag(el);
  }
  function scan() {
    if (!document.body) { return; }
    ensureStyle();
    if (isDokdae()) { document.documentElement.classList.add('rgon-dokdae-page'); }
    var w;
    try {
      w = document.createTreeWalker(document.body, 5, { acceptNode: function (n) {
        if (n.nodeType === 1) {
          var t = n.tagName;
          if (t === 'SCRIPT' || t === 'STYLE' || t === 'NOSCRIPT' || t === 'TEXTAREA' || n.id === 'dokdae-feed') { return 2; }
          return 3;
        }
        var v = n.nodeValue;
        return (v && v.length < 100 && RE.test(v)) ? 1 : 3;
      } });
    } catch (e) { return; }
    var hits = [];
    var node;
    while ((node = w.nextNode())) { hits.push(node); }
    hits.forEach(tagNode);
  }

  var timer = null;
  function sched() {
    if (timer) { return; }
    timer = setTimeout(function () {
      timer = null;
      try { scan(); } catch (e) {}
    }, 350);
  }
  function boot() {
    try { scan(); } catch (e) {}
    setTimeout(function () { try { scan(); } catch (e) {} }, 600);
    setTimeout(function () { try { scan(); } catch (e) {} }, 1800);
    var n = 0;
    var iv = setInterval(function () {
      try { scan(); } catch (e) {}
      if (++n >= 20) { clearInterval(iv); }
    }, 3000);
    try {
      var mo = new MutationObserver(sched);
      mo.observe(document.body, { childList: true, subtree: true });
    } catch (e) {}
  }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', boot); }
  else { boot(); }
})();
"""

# ---------------------------------------------------------------------------
# JS module 2: drawers + rgon row + mobile status text (HTML only)
# ---------------------------------------------------------------------------
LAYOUT_JS = r"""
;(function () {
  'use strict';
  if (window.__RGON_STEP2_LAYOUT__) { return; }
  window.__RGON_STEP2_LAYOUT__ = true;

  var UA = (navigator && navigator.userAgent) || '';
  var IS_MOBILE = (!/Chrome/.test(UA)) || /Mobile|Android|iPhone/i.test(UA);
  var OMNI_ID = 'rgon-omni-top-drawer';
  var TOOLS_ID = 'rgon-tools-drawer';
  var OMNI_SUMMARY = __OMNI_SUMMARY__;
  var TOOLS_SUMMARY = __TOOLS_SUMMARY__;
  var MOBILE_TEXT = __MOBILE_TEXT__;
  var RGON_LABEL = __RGON_LABEL__;
  var DRAWER_STYLE = 'margin:6px 0;border-radius:10px;border:1px solid rgba(99,102,241,0.35);background:rgba(15,23,42,0.85);padding:6px 10px;';
  var OMNI_RE = /Omni-?Link\s*분배\s*컨트롤러|AI\s*만능\s*소통창\s*열기|확장\s*프로그램\s*확인\s*중/;
  var TOOLS_RE = /한마디\s*올인원|6대\s*기관\s*목표|6대\s*서브\s*에이전트|무늬만\s*버튼|[13]\s*청사|6대\s*청사\s*릴레이|Adobe\s*무료\s*3대장|청년\s*보이스|음성\s*설정/;
  var STATUS_RE = /확장\s*프로그램\s*확인\s*중\s*\.{0,3}|확장\s*프로그램\s*(?:미감지|미설치)[^\n]*/;
  var SKIP_IDS = { 'rgon-autosync-badge': 1, 'rgon-autosync-fallback': 1, 'rgon-autosync-toast': 1, 'rgon-step2-toast': 1 };
  var GUARD_SEL = '#' + OMNI_ID + ',#' + TOOLS_ID + ',#rgon-autosync-badge,#rgon-autosync-fallback';
  var T0 = Date.now();

  /* ---------------- helpers ---------------- */
  function toast(msg) {
    try {
      var t = document.getElementById('rgon-step2-toast');
      if (!t) {
        t = document.createElement('div');
        t.id = 'rgon-step2-toast';
        t.style.cssText = 'position:fixed;left:50%;bottom:64px;transform:translateX(-50%);z-index:2147483646;max-width:90vw;padding:8px 14px;border-radius:10px;background:rgba(30,41,59,0.96);color:#e2e8f0;font-size:13px;text-align:center;box-shadow:0 4px 18px rgba(0,0,0,0.4);transition:opacity .25s;opacity:0;pointer-events:none;';
        document.body.appendChild(t);
      }
      t.textContent = msg;
      t.style.opacity = '1';
      clearTimeout(t.__h);
      t.__h = setTimeout(function () { t.style.opacity = '0'; }, 2600);
    } catch (e) {}
  }

  function getFeed() {
    var f = document.getElementById('dokdae-feed');
    if (f) { return f; }
    var sels = ['#chat-feed', '#chatFeed', '#feed', '#messages', '#chat-messages', '#chatMessages',
      '.dokdae-feed', '.chat-feed', '[id*="dokdae"][id*="feed"]', '[id*="chat"][id*="feed"]'];
    for (var i = 0; i < sels.length; i++) {
      var el = null;
      try { el = document.querySelector(sels[i]); } catch (e) {}
      if (el) { return el; }
    }
    return null;
  }
  function tagFeed(feed) {
    if (feed && !feed.classList.contains('rgon-feed-main')) { feed.classList.add('rgon-feed-main'); }
  }

  function inOverlay(el) {
    var cur = el;
    var n = 0;
    while (cur && cur !== document.body && cur !== document.documentElement && n < 30) {
      var sig = (cur.id || '') + ' ' + ((cur.getAttribute && cur.getAttribute('class')) || '');
      if (/modal|overlay|dialog|popup|toast|backdrop|lightbox/i.test(sig)) { return true; }
      var pos = '';
      try { pos = getComputedStyle(cur).position; } catch (e) {}
      if (pos === 'fixed') { return true; }
      cur = cur.parentElement;
      n++;
    }
    return false;
  }

  /* ---------------- anchor collection ---------------- */
  function accept(el, text, feed, res) {
    if (!el || !text) { return; }
    if (el.closest('#' + OMNI_ID + ',#' + TOOLS_ID)) { return; }
    if (feed && (feed.contains(el) || !(el.compareDocumentPosition(feed) & 4))) { return; }
    if (inOverlay(el)) { return; }
    if (OMNI_RE.test(text)) { res.omni.push(el); return; }
    if (TOOLS_RE.test(text) && !el.closest('h1,h2')) { res.tools.push(el); }
  }
  function collect(feed) {
    var res = { omni: [], tools: [] };
    var w;
    try {
      w = document.createTreeWalker(document.body, 5, { acceptNode: function (n) {
        if (n.nodeType === 1) {
          var t = n.tagName;
          if (t === 'SCRIPT' || t === 'STYLE' || t === 'NOSCRIPT' || t === 'TEXTAREA' || t === 'TEMPLATE' || t === 'OPTION') { return 2; }
          if (n === feed || n.id === OMNI_ID || n.id === TOOLS_ID || SKIP_IDS[n.id]) { return 2; }
          return 3;
        }
        var v = n.nodeValue;
        if (!v || v.length > 200) { return 3; }
        return (OMNI_RE.test(v) || TOOLS_RE.test(v)) ? 1 : 3;
      } });
    } catch (e) { return res; }
    var node;
    while ((node = w.nextNode())) {
      if (node.parentElement) { accept(node.parentElement, node.nodeValue, feed, res); }
    }
    var ins = document.querySelectorAll('input[type="button"],input[type="submit"]');
    for (var i = 0; i < ins.length; i++) { accept(ins[i], ins[i].value, feed, res); }
    return res;
  }

  /* ---------------- block computation ---------------- */
  function exclusiveBlock(anchor, others, feed) {
    var cur = anchor;
    for (var guard = 0; guard < 25; guard++) {
      var p = cur.parentElement;
      if (!p || p === document.body || p === document.documentElement) { break; }
      if (feed && p.contains(feed)) { break; }
      if (p.querySelector('h1')) { break; }
      if (p.querySelector(GUARD_SEL)) { break; }
      if (p.querySelector('#dokdae-input,#dokdae-text,#dokdae-msg,textarea[id*="dokdae"]')) { break; }
      if ((p.textContent || '').length > 8000) { break; }
      var bad = false;
      for (var i = 0; i < others.length; i++) {
        if (p.contains(others[i])) { bad = true; break; }
      }
      if (bad) { break; }
      var pos = '';
      try { pos = getComputedStyle(p).position; } catch (e) {}
      if (pos === 'fixed' || pos === 'sticky') { break; }
      cur = p;
    }
    return cur;
  }
  function uniqueBlocks(anchors, others, feed) {
    var blocks = [];
    anchors.forEach(function (a) {
      var b = exclusiveBlock(a, others, feed);
      if (blocks.indexOf(b) === -1) { blocks.push(b); }
    });
    var out = blocks.filter(function (b) {
      return !blocks.some(function (o) { return o !== b && o.contains(b); });
    });
    out.sort(function (a, b) { return (a.compareDocumentPosition(b) & 4) ? -1 : 1; });
    return out;
  }

  /* ---------------- drawers ---------------- */
  function ensureDrawer(id, summaryText, openDefault, before) {
    var d = document.getElementById(id);
    if (d) { return d; }
    if (!before || !before.parentNode) { return null; }
    d = document.createElement('details');
    d.id = id;
    d.className = 'rgon-compact-drawer';
    d.setAttribute('style', DRAWER_STYLE);
    var s = document.createElement('summary');
    s.textContent = summaryText;
    var body = document.createElement('div');
    body.className = 'rgon-drawer-body';
    d.appendChild(s);
    d.appendChild(body);
    before.parentNode.insertBefore(d, before);
    function sync() {
      var t = s.textContent;
      s.textContent = d.open ? t.replace(/펼치기 ▼\s*$/, '접기 ▲') : t.replace(/접기 ▲\s*$/, '펼치기 ▼');
    }
    d.addEventListener('toggle', sync);
    if (openDefault) { d.open = true; sync(); }
    return d;
  }
  function hoist(block) {
    var all = block.querySelectorAll('*');
    var list = [];
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var pos = '';
      try { pos = getComputedStyle(el).position; } catch (e) {}
      if (pos === 'fixed' && !list.some(function (x) { return x.contains(el); })) { list.push(el); }
    }
    list.forEach(function (el) { document.body.appendChild(el); });
  }
  function moveBlocks(drawer, blocks) {
    var body = drawer.querySelector('.rgon-drawer-body');
    if (!body) { return; }
    blocks.forEach(function (b) {
      if (b.parentNode && !drawer.contains(b) && !b.contains(drawer)) {
        hoist(b);
        body.appendChild(b);
      }
    });
  }

  /* ---------------- rgon row ---------------- */
  function sigOf(el) {
    var s = '';
    if (el.attributes) {
      for (var i = 0; i < el.attributes.length; i++) {
        var a = el.attributes[i];
        if (a.name !== 'style' && a.name !== 'class') { s += ' ' + a.value; }
      }
    }
    return s + ' ' + (el.textContent || '');
  }
  function prepClone(root) {
    var nodes = [root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));
    nodes.forEach(function (el) {
      if (el.tagName === 'INPUT' && el.type === 'checkbox') {
        el.removeAttribute('checked');
        el.checked = false;
        el.setAttribute('data-rgon-step2', '1');
      }
      for (var i = 0; i < el.attributes.length; i++) {
        var a = el.attributes[i];
        var n = a.name;
        var v = a.value;
        if (n === 'class' || n === 'style' || !/claude/i.test(v)) { continue; }
        var nv = v;
        if (n === 'href') {
          nv = v.replace(/https?:\/\/[^\s'"]*claude[^\s'"]*/gi, 'https://gemini.google.com/app');
        } else if (n === 'id' || n === 'for' || n === 'name' || n === 'value' || n === 'title' || n === 'aria-label' || n.indexOf('data-') === 0) {
          nv = v.replace(/claude/gi, 'rgon');
        } else {
          nv = v.replace(/(['"])claude\1/gi, '$1rgon$1');
        }
        if (nv !== v) { el.setAttribute(n, nv); }
      }
      for (var c = el.firstChild; c; c = c.nextSibling) {
        if (c.nodeType !== 3) { continue; }
        var t = c.nodeValue;
        if (/claude/i.test(t)) {
          t = t.replace(/(?:🟠\s*)?(?:🧠\s*)?Claude(?:\s*\([^)]*\))?/i, ' ' + RGON_LABEL + ' ');
        }
        t = t.replace(/\(?설계\s*[·ㆍ]\s*코드\)?/g, '').replace(/(?:🟠|🧠)/g, '');
        if (t !== c.nodeValue) { c.nodeValue = t; }
      }
      if (el.tagName === 'BUTTON' || el.tagName === 'A' || el.getAttribute('role') === 'button') {
        if (!el.getAttribute('onclick')) { el.setAttribute('data-rgon-step2-solo', '1'); }
      }
    });
  }
  function firstCheckRow(row) {
    var kids = row.parentNode ? row.parentNode.children : [];
    for (var i = 0; i < kids.length; i++) {
      if (kids[i] === row || kids[i].querySelector('input[type="checkbox"]')) { return kids[i]; }
    }
    return row;
  }
  function cloneRow(row, body) {
    var c = row.cloneNode(true);
    prepClone(c);
    c.setAttribute('data-rgon-step2-row', '1');
    row.parentNode.insertBefore(c, firstCheckRow(row));
    var btns = body.querySelectorAll('button,a,[role="button"],input[type="button"]');
    for (var i = 0; i < btns.length; i++) {
      var b = btns[i];
      if (row.contains(b) || b.closest('[data-rgon-step2-row]') || !b.parentNode) { continue; }
      if (/claude/i.test(sigOf(b))) {
        var cb = b.cloneNode(true);
        prepClone(cb);
        cb.setAttribute('data-rgon-step2-row', '1');
        b.parentNode.insertBefore(cb, b);
      }
    }
  }
  function buildScratchRow(body) {
    var row = document.createElement('div');
    row.setAttribute('data-rgon-step2-row', '1');
    row.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:8px;padding:6px 8px;margin:4px 0;border:1px solid rgba(255,255,255,0.15);border-radius:8px;';
    var lab = document.createElement('label');
    lab.style.cssText = 'display:flex;align-items:center;gap:6px;flex:1;min-width:0;cursor:pointer;';
    var cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.className = 'role-chk tgt-chk';
    cb.value = 'rgon';
    cb.setAttribute('data-role', 'rgon');
    cb.setAttribute('data-rgon-step2', '1');
    var sp = document.createElement('span');
    sp.textContent = RGON_LABEL;
    lab.appendChild(cb);
    lab.appendChild(sp);
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn ghost solo-fire-btn';
    btn.setAttribute('data-solo', 'rgon');
    btn.setAttribute('data-rgon-step2-solo', '1');
    btn.style.whiteSpace = 'nowrap';
    btn.textContent = '🚀 단독 발사';
    row.appendChild(lab);
    row.appendChild(btn);
    body.insertBefore(row, body.firstChild);
  }
  function ensureRgonRow(drawer) {
    var body = drawer.querySelector('.rgon-drawer-body');
    if (!body) { return; }
    var real = body.querySelector('input[type="checkbox"][value="rgon"]:not([data-rgon-step2])');
    var mine = body.querySelectorAll('[data-rgon-step2-row]');
    var i;
    if (real) {
      for (i = 0; i < mine.length; i++) {
        if (mine[i].parentNode) { mine[i].parentNode.removeChild(mine[i]); }
      }
      return;
    }
    if (mine.length) { return; }
    if (/Gemini\s*4\s*Argon/.test(body.textContent || '')) { return; }
    var boxes = body.querySelectorAll('input[type="checkbox"]');
    var claude = null;
    for (var j = 0; j < boxes.length; j++) {
      var holder = boxes[j].closest('label') || boxes[j].parentElement;
      if (/claude/i.test(sigOf(boxes[j]) + ' ' + (holder ? holder.textContent : ''))) { claude = boxes[j]; break; }
    }
    if (claude) {
      var row = claude;
      while (row.parentElement && row.parentElement !== body &&
             row.parentElement.querySelectorAll('input[type="checkbox"]').length === 1) {
        row = row.parentElement;
      }
      if (row !== claude && (row.textContent || '').trim()) { cloneRow(row, body); return; }
    }
    if (Date.now() - T0 < 4000) { return; }
    buildScratchRow(body);
  }

  /* fallback for clone/scratch solo buttons that have no inline handler */
  function fireFallback(role) {
    var text = '';
    var ta = document.getElementById('dokdae-input') || document.querySelector('#' + OMNI_ID + ' textarea') || document.querySelector('textarea');
    if (ta) { text = ta.value || ''; }
    try { window.dispatchEvent(new CustomEvent('rgon-omni-fire', { detail: { roles: [role], text: text, source: 'step2-layout' } })); } catch (e) {}
    try {
      if (window.RGON_OMNI && typeof window.RGON_OMNI.fire === 'function') { window.RGON_OMNI.fire([role], text); }
    } catch (e) {}
    if (text && navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        toast('📋 지시문 복사 완료 — 르곤(Gemini)에 붙여넣으세요');
      }, function () { toast('👑 르곤 단독 발사 요청을 전달했습니다'); });
    } else {
      toast('👑 르곤 단독 발사 요청을 전달했습니다');
    }
  }
  document.addEventListener('click', function (ev) {
    try {
      var t = ev.target;
      var b = (t && t.closest) ? t.closest('[data-rgon-step2-solo="1"]') : null;
      if (!b || b.getAttribute('onclick')) { return; }
      fireFallback(b.getAttribute('data-solo') || 'rgon');
    } catch (e) {}
  }, true);

  /* ---------------- mobile status text ---------------- */
  function fixStatus(root) {
    if (!IS_MOBILE || !root) { return; }
    var w;
    try { w = document.createTreeWalker(root, 4, null); } catch (e) { return; }
    var hits = [];
    var n;
    while ((n = w.nextNode())) {
      if (n.nodeValue && STATUS_RE.test(n.nodeValue)) { hits.push(n); }
    }
    hits.forEach(function (t) {
      var p = t.parentElement;
      if (p && /^(SCRIPT|STYLE|TEXTAREA)$/.test(p.tagName)) { return; }
      t.nodeValue = t.nodeValue.replace(STATUS_RE, MOBILE_TEXT);
    });
  }

  /* ---------------- watcher on the omni drawer ---------------- */
  var watched = null;
  var wobs = null;
  var wTimer = null;
  var WOPT = { childList: true, subtree: true, characterData: true };
  function watch(drawer) {
    if (watched === drawer) { return; }
    watched = drawer;
    if (wobs) { wobs.disconnect(); }
    try {
      wobs = new MutationObserver(function () {
        if (wTimer) { return; }
        wTimer = setTimeout(function () {
          wTimer = null;
          wobs.disconnect();
          try { fixStatus(drawer); ensureRgonRow(drawer); } catch (e) {}
          wobs.observe(drawer, WOPT);
        }, 150);
      });
      wobs.observe(drawer, WOPT);
    } catch (e) {}
  }

  /* ---------------- organize ---------------- */
  function organize() {
    if (!document.body) { return; }
    var feed = getFeed();
    tagFeed(feed);
    var g = collect(feed);
    if (g.omni.length || g.tools.length) {
      var ob = uniqueBlocks(g.omni, g.tools, feed);
      var tb = uniqueBlocks(g.tools, g.omni, feed);
      if (ob.length) {
        var d1 = ensureDrawer(OMNI_ID, OMNI_SUMMARY, false, ob[0]);
        if (d1) { moveBlocks(d1, ob); }
      }
      if (tb.length) {
        var d2 = ensureDrawer(TOOLS_ID, TOOLS_SUMMARY, (!IS_MOBILE && window.innerWidth >= 1100), tb[0]);
        if (d2) { moveBlocks(d2, tb); }
      }
    }
    var omni = document.getElementById(OMNI_ID);
    if (omni) {
      fixStatus(omni);
      ensureRgonRow(omni);
      watch(omni);
    }
  }
  function safeOrganize() { try { organize(); } catch (e) { try { console.warn('[step2]', e); } catch (_) {} } }

  function boot() {
    safeOrganize();
    [400, 1200, 2500, 5000, 9000].forEach(function (ms) { setTimeout(safeOrganize, ms); });
    var pending = null;
    try {
      var obs = new MutationObserver(function () {
        if (pending) { return; }
        pending = setTimeout(function () { pending = null; safeOrganize(); }, 500);
      });
      obs.observe(document.body, { childList: true, subtree: true });
      setTimeout(function () { try { obs.disconnect(); } catch (e) {} }, 30000);
    } catch (e) {}
  }
  window.addEventListener('load', safeOrganize);
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', boot); }
  else { boot(); }
})();
"""

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def info(msg=""):
    print(msg)


def ascii_escape(js):
    out = []
    for ch in js:
        cp = ord(ch)
        if cp < 128:
            out.append(ch)
        elif cp < 0x10000:
            out.append("\\u%04x" % cp)
        else:
            cp -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (cp >> 10), 0xDC00 + (cp & 0x3FF)))
    return "".join(out)


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


def build_js_all():
    layout = (LAYOUT_JS
              .replace("__OMNI_SUMMARY__", json.dumps(OMNI_SUMMARY))
              .replace("__TOOLS_SUMMARY__", json.dumps(TOOLS_SUMMARY))
              .replace("__MOBILE_TEXT__", json.dumps(MOBILE_TEXT))
              .replace("__RGON_LABEL__", json.dumps(RGON_LABEL)))
    js = TUNNEL_JS.strip("\n") + "\n\n" + layout.strip("\n")
    return ascii_escape(js)


def build_js_tunnel():
    return ascii_escape(TUNNEL_JS.strip("\n"))


def check_js_safe(js, label):
    low = js.lower()
    if "</script" in low or "<!--" in js or "-->" in js:
        raise ValueError("generated JS (%s) contains an HTML-sensitive sequence" % label)
    if "RGON_AUTO_SYNC_MASTER" in js:
        raise ValueError("generated JS (%s) must not reference the auto-sync block" % label)


# ---------------------------------------------------------------------------
# HTML patching
# ---------------------------------------------------------------------------
STYLE_BEGIN = "<!-- RGON_STEP2_STYLE_BEGIN -->"
STYLE_END = "<!-- RGON_STEP2_STYLE_END -->"
SCRIPT_BEGIN = "<!-- RGON_STEP2_SCRIPT_BEGIN -->"
SCRIPT_END = "<!-- RGON_STEP2_SCRIPT_END -->"

STRIP_STYLE_RE = re.compile(r"\n?" + re.escape(STYLE_BEGIN) + r".*?" + re.escape(STYLE_END) + r"\n?", re.S)
STRIP_SCRIPT_RE = re.compile(r"\n?" + re.escape(SCRIPT_BEGIN) + r".*?" + re.escape(SCRIPT_END) + r"\n?", re.S)
SCRIPT_SPAN_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.I | re.S)


def strip_html(text):
    return STRIP_SCRIPT_RE.sub("", STRIP_STYLE_RE.sub("", text))


def find_tag(text, pattern, last=False):
    spans = [m.span() for m in SCRIPT_SPAN_RE.finditer(text)]
    found = None
    for m in re.finditer(pattern, text, re.I):
        inside = any(a <= m.start() < b for a, b in spans)
        if inside:
            continue
        if not last:
            return m
        found = m
    return found


def build_style_block():
    css = STATIC_CSS.strip("\n")
    return STYLE_BEGIN + '\n<style id="rgon-step2-style">\n' + css + "\n</style>\n" + STYLE_END


def build_script_block(js_all):
    return (SCRIPT_BEGIN + '\n<script id="rgon-step2-layout">\n/* RGON_STEP2_BEGIN */\n'
            + js_all + "\n/* RGON_STEP2_END */\n</script>\n" + SCRIPT_END)


def patch_html(text, js_all):
    base = strip_html(text)
    style_block = build_style_block()
    script_block = build_script_block(js_all)

    m = find_tag(base, r"</head\s*>")
    if m:
        idx = m.start()
    else:
        mh = find_tag(base, r"<head\b[^>]*>")
        idx = mh.end() if mh else 0
    new = base[:idx] + "\n" + style_block + "\n" + base[idx:]

    mb = find_tag(new, r"</body\s*>", last=True)
    if mb:
        idx = mb.start()
        new = new[:idx] + "\n" + script_block + "\n" + new[idx:]
    else:
        new = new.rstrip("\n") + "\n" + script_block + "\n"

    if strip_html(new) != base:
        raise RuntimeError("verification failed: stripping the STEP2 additions does not restore the original")
    if text.count("RGON_AUTO_SYNC_MASTER_BEGIN") != new.count("RGON_AUTO_SYNC_MASTER_BEGIN"):
        raise RuntimeError("verification failed: RGON_AUTO_SYNC_MASTER block count changed")
    if text.count("RGON_AUTO_SYNC_MASTER_END") != new.count("RGON_AUTO_SYNC_MASTER_END"):
        raise RuntimeError("verification failed: RGON_AUTO_SYNC_MASTER end marker count changed")
    return new


# ---------------------------------------------------------------------------
# pwa_bootstrap.js patching
# ---------------------------------------------------------------------------
JS_BEGIN = "/* RGON_STEP2_BEGIN */"
JS_END = "/* RGON_STEP2_END */"
STRIP_JS_RE = re.compile(r"\n*[ \t]*" + re.escape(JS_BEGIN) + r".*?" + re.escape(JS_END) + r"[ \t]*\n?", re.S)


def patch_js(text, js_tunnel):
    base = STRIP_JS_RE.sub("", text)
    block = JS_BEGIN + "\n" + js_tunnel + "\n" + JS_END
    new = base.rstrip("\n") + "\n\n" + block + "\n"
    if STRIP_JS_RE.sub("", new).rstrip("\n") != base.rstrip("\n"):
        raise RuntimeError("verification failed: pwa_bootstrap.js original content changed")
    return new


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    info("=" * 66)
    info(" RGON STEP 2 : MOBILE CLEAN LAYOUT (UI / CSS only)")
    info(" base dir: " + BASE)
    info("=" * 66)

    if not os.path.isdir(BASE):
        info("[ERROR] base directory not found: " + BASE)
        sys.exit(1)

    try:
        js_all = build_js_all()
        js_tunnel = build_js_tunnel()
        check_js_safe(js_all, "html")
        check_js_safe(js_tunnel, "pwa")
    except Exception as e:
        info("[ERROR] " + str(e))
        sys.exit(2)

    plans = []  # (path, original_text, new_text, meta, kind)
    for rel in HTML_FILES:
        path = os.path.normpath(os.path.join(BASE, *rel.split("/")))
        if not os.path.isfile(path):
            info("[SKIP] not found: " + rel)
            continue
        try:
            text, meta = read_text(path)
            plans.append((path, text, patch_html(text, js_all), meta, "html"))
        except Exception as e:
            info("[ABORT] %s : %s" % (rel, e))
            info("        No file was modified.")
            sys.exit(3)

    for rel in PWA_FILES:
        path = os.path.normpath(os.path.join(BASE, *rel.split("/")))
        if not os.path.isfile(path):
            info("[SKIP] not found: " + rel)
            continue
        try:
            text, meta = read_text(path)
            plans.append((path, text, patch_js(text, js_tunnel), meta, "js"))
        except Exception as e:
            info("[ABORT] %s : %s" % (rel, e))
            info("        No file was modified.")
            sys.exit(3)

    if not plans:
        info("[ERROR] none of the target files exist.")
        sys.exit(1)

    # backups first
    for path, _, _, _, _ in plans:
        bak = path + ".bak_step2"
        if os.path.exists(bak):
            info("[BACKUP] kept existing: " + os.path.relpath(bak, BASE))
        else:
            shutil.copy2(path, bak)
            info("[BACKUP] " + os.path.relpath(bak, BASE))

    # write all; restore on failure
    written = []
    try:
        for path, old, new, meta, kind in plans:
            write_text(path, new, meta)
            written.append((path, old, meta))
    except Exception as e:
        info("[ERROR] write failed (%r), restoring the originals" % (e,))
        for path, old, meta in written:
            try:
                write_text(path, old, meta)
            except Exception:
                pass
        sys.exit(4)

    info("")
    for path, _, _, _, kind in plans:
        info("[OK] %-6s %s" % (kind.upper(), os.path.relpath(path, BASE)))

    info("")
    info("Applied:")
    info("  1) 5G tunnel badge : nowrap / max-content / keep-all. On mobile (<=768px) in the dokdae page it is pinned small in the bottom-right and never blocks taps.")
    info("  2) #rgon-omni-top-drawer : closed by default. A 르곤 row is guaranteed. On mobile the status text becomes the mobile direct-mode text.")
    info("  3) #rgon-tools-drawer : command buttons / Adobe STUDIO v5 / voice settings are moved in (IDs and handlers kept).")
    info("  4) #dokdae-feed : min-height 45vh / max-height 62vh / overflow-y auto.")
    info("")
    info("Next steps:")
    info("  - Syntax tip: node --check pwa_bootstrap.js")
    info("  - Push to GitHub (git add / commit / push) so GitHub Pages serves the new files.")
    info("  - Hard-refresh the mobile page once to clear the cache.")
    info("  - Restore: copy <file>.bak_step2 back over the patched file.")
    info("")
    info("[STEP 2 MOBILE CLEAN LAYOUT COMPLETE]")


if __name__ == "__main__":
    main()
Copy