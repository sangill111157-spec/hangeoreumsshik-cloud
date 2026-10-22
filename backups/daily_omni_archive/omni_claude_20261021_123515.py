#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step4_unify_solo_dispatch.py
Patches rgon_alpha_chat.html (root, dashboard/, docs/):
  1. The closed omni drawer takes only its title row; #dokdae-feed gets flex:1 1 auto and min-height:320px.
     "v6.0.3" -> "v6.0.8" and "(Claude / GPT / Grok)" -> "(르곤 / Claude / GPT / Grok)" in the controller text, applied at runtime.
  2. The legacy bundle buttons in "독대실에서 바로 분배하기" are hidden and replaced with the same 4-AI structure
     as the top controller (checkboxes, select/clear all, 2x2 solo buttons, fire-checked / fire-all).
     Firing goes three ways: top-controller function or button, window.postMessage, and POST to the local bridge.
Safe to re-run (the blocks are replaced). Backups go to backups/step4_<timestamp>/.
Usage: python step4_unify_solo_dispatch.py [BASE_DIR] [--no-git] [--no-node-check]
"""
import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_pos = [a for a in sys.argv[1:] if not a.startswith("--")]
BASE = Path(_pos[0] if _pos else r"C:\Users\sangi\Downloads\shin-agent")
NO_GIT = "--no-git" in sys.argv
NO_NODE = "--no-node-check" in sys.argv

TARGETS = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
COMMIT_MSG = "feat(v6.0.8-step4): unify solo dispatch buttons & fix drawer empty gap"

CSS = r"""
#rgon-omni-drawer:not([open]),#rgon-omni-top-drawer:not([open]){min-height:0 !important;height:auto !important;flex:0 0 auto !important;}
#rgon-omni-drawer:not([open])>*:not(summary),#rgon-omni-top-drawer:not([open])>*:not(summary){display:none !important;}
#dokdae-feed{flex:1 1 auto !important;min-height:320px !important;}
[data-r4-legacy="1"]{display:none !important;}
[data-r4-keep="1"]{display:inline-block !important;visibility:visible !important;opacity:1 !important;margin:6px 0 0 !important;}
.r4-panel{width:100% !important;flex:0 0 100% !important;box-sizing:border-box !important;max-width:100% !important;margin:8px 0;padding:8px;border:1px solid rgba(99,102,241,0.35);border-radius:10px;background:rgba(15,23,42,0.6);color:#e0e7ff;}
.r4-chk-row{display:flex;flex-direction:column;gap:4px;margin-bottom:6px;}
.r4-chk{display:flex;align-items:center;gap:6px;font-size:13px;word-break:keep-all;cursor:pointer;}
.r4-mini-row{display:flex;gap:6px;margin-bottom:6px;}
.r4-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;}
.r4-exec{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px;}
.r4-btn{cursor:pointer;border:1px solid rgba(129,140,248,0.5);background:rgba(30,41,59,0.9);color:#e0e7ff;border-radius:8px;padding:8px 6px;font-size:12.5px;line-height:1.3;word-break:keep-all;white-space:normal;min-width:0;}
.r4-mini{padding:5px 10px;font-size:12px;}
.r4-exec .r4-btn{flex:1 1 140px;font-weight:700;}
.r4-btn:active{transform:scale(0.98);}
"""

JS = r"""
;(function () {
  'use strict';
  if (window.__RGON_STEP4_SOLO__) { return; }
  window.__RGON_STEP4_SOLO__ = true;

  var PANEL_ID = 'rgon-step4-solo-panel';
  var BRIDGE = 'http://127.0.0.1:8765/api/dispatch';
  var ALL_ROLES = ['rgon', 'claude', 'gpt', 'grok'];
  var ROLES = [
    { role: 'rgon', label: '🔵👑 르곤 (Gemini 4 Argon)', checked: true },
    { role: 'claude', label: '🧠 Claude', checked: false },
    { role: 'gpt', label: '⚡ GPT', checked: false },
    { role: 'grok', label: '🎯 Grok', checked: false }
  ];
  var DRAWER_SEL = '#rgon-omni-drawer,#rgon-omni-top-drawer';
  var HEAD_RE = /독대실에서\s*바로\s*분배하기/;
  var LEGACY_RE = /동시\s*발사|Grok\s*카피\s*발사/;
  var COLLECT_RE = /AI\s*탭\s*코드\s*수거/;
  var CTL_RE = /Omni-?Link|분배\s*컨트롤러|컨트롤러/;
  var TEXT_FIX_RE = /v6\.0\.3|\(\s*Claude\s*\/\s*GPT\s*\/\s*Grok\s*\)/;

  /* ---------------- helpers ---------------- */
  function mk(tag, props, text) {
    var e = document.createElement(tag);
    if (props) {
      for (var k in props) { if (Object.prototype.hasOwnProperty.call(props, k)) { e.setAttribute(k, props[k]); } }
    }
    if (text !== undefined && text !== null) { e.textContent = text; }
    return e;
  }
  function toast(msg) {
    try {
      var t = document.getElementById('rgon-step4-toast');
      if (!t) {
        t = mk('div', { id: 'rgon-step4-toast' });
        t.style.cssText = 'position:fixed;left:50%;bottom:70px;transform:translateX(-50%);z-index:2147483646;max-width:90vw;padding:8px 14px;border-radius:10px;background:rgba(30,41,59,0.96);color:#e2e8f0;font-size:13px;text-align:center;box-shadow:0 4px 18px rgba(0,0,0,0.4);transition:opacity .25s;opacity:0;pointer-events:none;';
        document.body.appendChild(t);
      }
      t.textContent = msg;
      t.style.opacity = '1';
      clearTimeout(t.__h);
      t.__h = setTimeout(function () { t.style.opacity = '0'; }, 2800);
    } catch (e) {}
  }
  function btnText(el) {
    return String((el.tagName === 'INPUT') ? el.value : el.textContent || '');
  }

  /* ---------------- panel ---------------- */
  function buildPanel() {
    var p = mk('div', { id: PANEL_ID, 'class': 'r4-panel' });
    var chkRow = mk('div', { 'class': 'r4-chk-row' });
    ROLES.forEach(function (r) {
      var lab = mk('label', { 'class': 'r4-chk' });
      var cb = mk('input', { type: 'checkbox', 'class': 'r4-role-chk', value: r.role });
      if (r.checked) { cb.checked = true; cb.setAttribute('checked', 'checked'); }
      lab.appendChild(cb);
      lab.appendChild(mk('span', null, r.label));
      chkRow.appendChild(lab);
    });
    p.appendChild(chkRow);

    var mini = mk('div', { 'class': 'r4-mini-row' });
    mini.appendChild(mk('button', { type: 'button', 'class': 'r4-btn r4-mini', 'data-r4': 'all' }, '☑ 전체 선택'));
    mini.appendChild(mk('button', { type: 'button', 'class': 'r4-btn r4-mini', 'data-r4': 'none' }, '☐ 전체 해제'));
    p.appendChild(mini);

    var grid = mk('div', { 'class': 'r4-grid' });
    ROLES.forEach(function (r) {
      grid.appendChild(mk('button', { type: 'button', 'class': 'r4-btn r4-solo', 'data-solo': r.role }, r.label + ' 단독 발사'));
    });
    p.appendChild(grid);

    var exec = mk('div', { 'class': 'r4-exec' });
    exec.appendChild(mk('button', { type: 'button', 'class': 'r4-btn', 'data-r4': 'checked' }, '🚀 체크 선택 발사'));
    exec.appendChild(mk('button', { type: 'button', 'class': 'r4-btn', 'data-r4': 'fireall' }, '🌐 4대 AI 전체 발사'));
    p.appendChild(exec);

    p.addEventListener('click', onPanelClick);
    return p;
  }
  function checkedRoles(panel) {
    var out = [];
    var list = panel.querySelectorAll('.r4-role-chk');
    for (var i = 0; i < list.length; i++) { if (list[i].checked) { out.push(list[i].value); } }
    return out;
  }
  function setAll(panel, flag) {
    var list = panel.querySelectorAll('.r4-role-chk');
    for (var i = 0; i < list.length; i++) { list[i].checked = flag; }
  }
  function onPanelClick(ev) {
    try {
      var panel = ev.currentTarget;
      var t = ev.target;
      var b = (t && t.closest) ? t.closest('button') : null;
      if (!b || !panel.contains(b)) { return; }
      ev.preventDefault();
      ev.stopPropagation();
      var solo = b.getAttribute('data-solo');
      if (solo) { fire([solo]); return; }
      var act = b.getAttribute('data-r4');
      if (act === 'all' || act === 'none') { setAll(panel, act === 'all'); return; }
      if (act === 'checked') {
        var c = checkedRoles(panel);
        if (!c.length) { toast('⚠️ 발사할 대상을 1개 이상 체크하세요.'); return; }
        fire(c);
        return;
      }
      if (act === 'fireall') { fire(ALL_ROLES.slice()); }
    } catch (e) { try { console.warn('[step4]', e); } catch (_) {} }
  }

  /* ---------------- dispatch (triple wiring) ---------------- */
  function readText() {
    var panel = document.getElementById(PANEL_ID);
    var ta = null;
    if (panel) {
      var cur = panel.parentElement;
      var n = 0;
      while (cur && cur !== document.body && n < 8 && !ta) {
        var list = cur.querySelectorAll('textarea');
        for (var i = 0; i < list.length; i++) {
          if (!panel.contains(list[i]) && !list[i].closest(DRAWER_SEL)) { ta = list[i]; break; }
        }
        cur = cur.parentElement;
        n++;
      }
    }
    if (!ta) { ta = document.getElementById('dokdae-input'); }
    if (!ta) { ta = document.querySelector('textarea'); }
    return ta ? String(ta.value || '').trim() : '';
  }
  function findTopSolo(role) {
    var sel = '[data-solo="' + role + '"]';
    var drawers = document.querySelectorAll(DRAWER_SEL);
    for (var i = 0; i < drawers.length; i++) {
      var b = drawers[i].querySelector(sel);
      if (b) { return b; }
    }
    var all = document.querySelectorAll(sel);
    for (var j = 0; j < all.length; j++) {
      if (!all[j].closest('#' + PANEL_ID)) { return all[j]; }
    }
    return null;
  }
  function callTop(roles, text) {
    try {
      var api = window.RGON_OMNI;
      if (api && typeof api.fire === 'function') { api.fire(roles, text); return 1; }
    } catch (e) {}
    var names = ['rgonOmniFire', 'omniFire', 'fireOmni', 'rgonFire'];
    for (var i = 0; i < names.length; i++) {
      try {
        if (typeof window[names[i]] === 'function') { window[names[i]](roles, text); return 1; }
      } catch (e) {}
    }
    var drawer = document.querySelector(DRAWER_SEL);
    if (drawer) {
      var tta = drawer.querySelector('textarea');
      if (tta && !String(tta.value || '').trim()) {
        tta.value = text;
        try { tta.dispatchEvent(new Event('input', { bubbles: true })); } catch (e) {}
      }
    }
    var clicked = 0;
    roles.forEach(function (r) {
      var b = findTopSolo(r);
      if (b) { try { b.click(); clicked++; } catch (e) {} }
    });
    return clicked;
  }
  function postBridge(roles, text) {
    if (typeof fetch !== 'function') { return; }
    try {
      fetch(BRIDGE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roles: roles, prompt: text, text: text, source: 'dokdae-step4', ts: Date.now() })
      }).then(function (res) {
        return res.json().catch(function () { return null; });
      }).then(function (j) {
        if (j && j.source === 'rgon-safety-shield') { toast('ℹ️ 로컬 브릿지(8765) 응답 없음 - 상단 컨트롤러/메시지 경로만 사용됨'); }
      }).catch(function () {
        toast('ℹ️ 로컬 브릿지(8765) 연결 실패 - 상단 컨트롤러/메시지 경로만 사용됨');
      });
    } catch (e) {}
  }
  function fire(roles) {
    var text = readText();
    if (!text) { toast('⚠️ 발사할 지시문을 입력하세요.'); return; }
    try { callTop(roles, text); } catch (e) {}
    try { window.postMessage({ type: 'RGON_OMNI_DISPATCH', roles: roles, prompt: text, text: text }, '*'); } catch (e) {}
    postBridge(roles, text);
    toast('🚀 발사 요청 전송: ' + roles.join(' · '));
  }

  /* ---------------- locate section / place panel ---------------- */
  function findHeading() {
    var w;
    try {
      w = document.createTreeWalker(document.body, 5, { acceptNode: function (n) {
        if (n.nodeType === 1) {
          return /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|TEMPLATE)$/.test(n.tagName) ? 2 : 3;
        }
        return HEAD_RE.test(n.nodeValue || '') ? 1 : 3;
      } });
    } catch (e) { return null; }
    var node;
    while ((node = w.nextNode())) {
      var p = node.parentElement;
      if (p && !p.closest('#' + PANEL_ID) && !p.closest(DRAWER_SEL)) { return p; }
    }
    return null;
  }
  function legacyIn(root) {
    var out = [];
    var list = root.querySelectorAll('button,a,[role="button"],input[type="button"]');
    for (var i = 0; i < list.length; i++) {
      if (LEGACY_RE.test(btnText(list[i])) && !list[i].closest('#' + PANEL_ID)) { out.push(list[i]); }
    }
    return out;
  }
  function findSection() {
    var h = findHeading();
    if (!h) { return null; }
    var feed = document.getElementById('dokdae-feed');
    var cur = h;
    var n = 0;
    while (cur && cur !== document.body && n < 7) {
      if (feed && cur.contains(feed)) { break; }
      var l = legacyIn(cur);
      if (l.length) { return { heading: h, root: cur, legacy: l }; }
      cur = cur.parentElement;
      n++;
    }
    return { heading: h, root: h.parentElement, legacy: [] };
  }
  function commonAncestor(list) {
    var cur = list[0].parentElement;
    while (cur && cur !== document.body) {
      var ok = true;
      for (var i = 1; i < list.length; i++) { if (!cur.contains(list[i])) { ok = false; break; } }
      if (ok) { return cur; }
      cur = cur.parentElement;
    }
    return null;
  }
  function hasCollect(root) {
    var list = root.querySelectorAll('button,a,[role="button"],input[type="button"]');
    for (var i = 0; i < list.length; i++) { if (COLLECT_RE.test(btnText(list[i]))) { return true; } }
    return false;
  }
  function hideEl(el) {
    if (el.getAttribute('data-r4-legacy') === '1') { return; }
    el.setAttribute('data-r4-legacy', '1');
    el.style.setProperty('display', 'none', 'important');
  }
  function place(panel, sec) {
    var feed = document.getElementById('dokdae-feed');
    var legacy = sec.legacy;
    if (legacy.length) {
      var lca = commonAncestor(legacy);
      var safe = !!lca && lca !== document.body && lca !== document.documentElement &&
        !lca.querySelector('textarea') && !hasCollect(lca) && !lca.contains(sec.heading) &&
        !(feed && lca.contains(feed));
      if (safe && lca.parentNode) {
        lca.parentNode.insertBefore(panel, lca);
        if (String(lca.innerText || '').trim() === '') { hideEl(lca); }
        return;
      }
      var first = legacy[0];
      if (first.parentNode) {
        first.parentNode.insertBefore(panel, first);
        var par = first.parentElement;
        try {
          if (par && /flex/.test(getComputedStyle(par).display)) { par.style.setProperty('flex-wrap', 'wrap', 'important'); }
        } catch (e) {}
        return;
      }
    }
    var h = sec.heading;
    if (h && h.parentNode) { h.parentNode.insertBefore(panel, h.nextSibling); }
  }

  /* ---------------- text fix / gap fix ---------------- */
  function isCtl(node) {
    var el = node.parentElement;
    for (var i = 0; i < 6 && el; i++) {
      if (el.id === 'rgon-omni-drawer' || el.id === 'rgon-omni-top-drawer') { return true; }
      var tc = el.textContent || '';
      if (tc.length < 2500 && CTL_RE.test(tc)) { return true; }
      el = el.parentElement;
    }
    return false;
  }
  function fixCtlText() {
    var w;
    try { w = document.createTreeWalker(document.body, 4, null); } catch (e) { return; }
    var hits = [];
    var n;
    while ((n = w.nextNode())) {
      var v = n.nodeValue;
      if (!v || v.length > 400 || !TEXT_FIX_RE.test(v)) { continue; }
      var p = n.parentElement;
      if (!p || /^(SCRIPT|STYLE|TEXTAREA|NOSCRIPT)$/.test(p.tagName) || p.closest('#dokdae-feed')) { continue; }
      if (isCtl(n)) { hits.push(n); }
    }
    hits.forEach(function (t) {
      t.nodeValue = t.nodeValue
        .replace(/v6\.0\.3/g, 'v6.0.8')
        .replace(/\(\s*Claude\s*\/\s*GPT\s*\/\s*Grok\s*\)/g, '(👑르곤 / 🧠Claude / ⚡GPT / 🎯Grok)');
    });
  }
  function fixGap() {
    var feed = document.getElementById('dokdae-feed');
    if (feed) { feed.style.setProperty('flex', '1 1 auto', 'important'); }
    var drawers = document.querySelectorAll(DRAWER_SEL);
    for (var i = 0; i < drawers.length; i++) {
      var p = drawers[i].parentElement;
      var n = 0;
      while (p && p !== document.body && n < 3) {
        if (feed && p.contains(feed)) { break; }
        p.style.setProperty('min-height', '0', 'important');
        p.style.setProperty('height', 'auto', 'important');
        p.style.setProperty('flex', '0 0 auto', 'important');
        p = p.parentElement;
        n++;
      }
    }
  }

  /* ---------------- ensure / boot ---------------- */
  function ensure() {
    if (!document.body) { return; }
    fixGap();
    fixCtlText();
    var sec = findSection();
    if (!sec) { return; }
    sec.legacy.forEach(hideEl);
    var panel = document.getElementById(PANEL_ID);
    if (!panel || !panel.isConnected) {
      panel = buildPanel();
      place(panel, sec);
    }
    if (sec.root) {
      var list = sec.root.querySelectorAll('button,a,[role="button"],input[type="button"]');
      for (var i = 0; i < list.length; i++) {
        if (COLLECT_RE.test(btnText(list[i])) && !list[i].closest('#' + PANEL_ID)) { list[i].setAttribute('data-r4-keep', '1'); }
      }
    }
  }
  function safeEnsure() {
    try { ensure(); } catch (e) { try { console.warn('[step4]', e); } catch (_) {} }
  }

  var timer = null;
  function schedule() {
    if (timer) { return; }
    timer = setTimeout(function () { timer = null; safeEnsure(); }, 300);
  }
  function boot() {
    safeEnsure();
    [400, 1200, 2500, 5000].forEach(function (ms) { setTimeout(safeEnsure, ms); });
    try {
      var mo = new MutationObserver(function (muts) {
        var feed = document.getElementById('dokdae-feed');
        for (var i = 0; i < muts.length; i++) {
          var t = muts[i].target;
          if (!(feed && t && feed.contains(t))) { schedule(); return; }
        }
      });
      mo.observe(document.body, { childList: true, subtree: true, characterData: true });
    } catch (e) {}
  }
  window.addEventListener('load', safeEnsure);
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', boot); }
  else { boot(); }

  window.RGON_STEP4_SOLO = { ensure: safeEnsure, fire: fire };
})();
"""

STYLE_RE = re.compile(r"""<style\b[^>]*\bid\s*=\s*["']rgon-step4-solo-css["'][^>]*>.*?</style\s*>\n?""", re.S | re.I)
SCRIPT_RE = re.compile(r"""<script\b[^>]*\bid\s*=\s*["']rgon-step4-solo-unify["'][^>]*>.*?</script\s*>\n?""", re.S | re.I)
SCRIPT_SPAN_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.S | re.I)


def info(msg=""):
    print(msg, flush=True)


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
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    try:
        text, enc = raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        text, enc = raw.decode("cp949"), "cp949"
    crlf = "\r\n" in text
    return text.replace("\r\n", "\n"), {"bom": bom, "crlf": crlf, "enc": enc}


def write_text(path, text, meta):
    if meta["crlf"]:
        text = text.replace("\n", "\r\n")
    data = text.encode(meta["enc"])
    if meta["bom"]:
        data = b"\xef\xbb\xbf" + data
    Path(path).write_bytes(data)


def strip_blocks(text):
    return SCRIPT_RE.sub("", STYLE_RE.sub("", text))


def patch_html(text, js, css):
    base = strip_blocks(text)
    block = ('<style id="rgon-step4-solo-css">\n' + css.strip("\n") + "\n</style>\n"
             '<script id="rgon-step4-solo-unify">\n' + js + "\n</script>\n")
    spans = [m.span() for m in SCRIPT_SPAN_RE.finditer(base)]
    idx = None
    for m in re.finditer(r"</body\s*>", base, re.I):
        if not any(a <= m.start() < b for a, b in spans):
            idx = m.start()
    if idx is None:
        new = base.rstrip("\n") + "\n" + block
    else:
        new = base[:idx] + block + base[idx:]
    if strip_blocks(new) != base:
        raise RuntimeError("verification failed: removing the step4 blocks does not restore the original")
    if new.count("<style id=\"rgon-step4-solo-css\">") != 1 or new.count("<script id=\"rgon-step4-solo-unify\">") != 1:
        raise RuntimeError("verification failed: duplicate step4 blocks")
    return new


def node_check(js):
    node = shutil.which("node")
    if not node:
        return None, "node not found"
    tmp_dir = BASE / "backups"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp = tmp_dir / "_step4_check.js"
    try:
        tmp.write_text(js, encoding="utf-8", newline="\n")
        p = subprocess.run([node, "--check", str(tmp)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return p.returncode == 0, (p.stderr or p.stdout or "").strip()
    finally:
        try:
            tmp.unlink()
        except Exception:
            pass


def run_git(args, timeout=120):
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    p = subprocess.run(["git"] + args, cwd=str(BASE), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout, env=env)
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def git_publish(rels):
    info("")
    info("[git] add / commit / push")
    try:
        rc, out = run_git(["add", "--"] + rels)
        if rc != 0:
            info("[git] add failed: " + out)
            return False
        rc, out = run_git(["commit", "-m", COMMIT_MSG])
        if rc != 0:
            if "nothing to commit" in out.lower() or "no changes added" in out.lower():
                info("[git] nothing new to commit, pushing anyway")
            else:
                info("[git] commit failed: " + out)
                return False
        else:
            info("[git] committed")
        rc, out = run_git(["push", "origin", "main"], timeout=180)
        if rc != 0:
            info("[git] push failed: " + out)
            return False
        info("[git] pushed to origin/main")
        return True
    except FileNotFoundError:
        info("[git] git was not found in PATH, skipped")
    except subprocess.TimeoutExpired:
        info("[git] timed out")
    except Exception as e:
        info("[git] error: %r" % (e,))
    return False


def main():
    info("=" * 64)
    info(" RGON STEP 4 : UNIFY SOLO DISPATCH + DRAWER GAP FIX")
    info(" base: " + str(BASE))
    info("=" * 64)
    if not BASE.is_dir():
        info("[ERROR] base directory not found: " + str(BASE))
        raise SystemExit(1)

    js = ascii_escape(JS.strip("\n"))
    low = js.lower()
    if "</script" in low or "<!--" in js or "-->" in js:
        info("[ERROR] generated JS contains an HTML-sensitive sequence")
        raise SystemExit(2)

    ok, msg = node_check(js)
    if ok is None:
        if NO_NODE:
            info("[WARN] node check skipped: " + msg)
        else:
            info("[ABORT] " + msg + ". Install Node.js or use --no-node-check.")
            raise SystemExit(3)
    else:
        info("[node --check] injected JS : " + ("PASS" if ok else "FAIL"))
        if not ok:
            info(msg)
            info("[ABORT] syntax check failed. No file was modified.")
            raise SystemExit(3)

    plans = []
    for rel in TARGETS:
        path = BASE.joinpath(*rel.split("/"))
        if not path.is_file():
            info("[SKIP] not found: " + rel)
            continue
        try:
            orig, meta = read_text(path)
            plans.append((rel, path, orig, patch_html(orig, js, CSS), meta))
        except Exception as e:
            info("[ABORT] %s : %s" % (rel, e))
            info("        No file was modified.")
            raise SystemExit(4)
    if not plans:
        info("[ERROR] none of the target files exist.")
        raise SystemExit(1)

    bdir = BASE / "backups" / ("step4_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    for rel, path, _, _, _ in plans:
        dest = bdir.joinpath(*rel.split("/"))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    info("[BACKUP] " + str(bdir.relative_to(BASE)))

    written = []
    try:
        for rel, path, orig, new, meta in plans:
            write_text(path, new, meta)
            written.append((path, orig, meta))
            info("[OK] " + rel)
    except Exception as e:
        info("[ERROR] write failed (%r), restoring the originals" % (e,))
        for path, orig, meta in written:
            try:
                write_text(path, orig, meta)
            except Exception:
                pass
        raise SystemExit(5)

    if not NO_GIT:
        git_publish([rel for rel, _, _, _, _ in plans])
    else:
        info("[git] skipped (--no-git)")

    info("")
    info("Hard-refresh the page once to clear the cache.")
    info("[STEP 4 SOLO DISPATCH UNIFY COMPLETE]")


if __name__ == "__main__":
    main()
Copy