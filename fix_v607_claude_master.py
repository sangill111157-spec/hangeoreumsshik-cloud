#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_v607_claude_master.py
RGON Aside Extension v6.0.6 -> v6.0.7 patcher (Python standard library only)

What it does:
  * Guarantees the #targetCheckList container in the "작업 분배" tab.
  * Always renders claude / gpt / grok + custom-role rows (no early return on 0 === 0).
  * Rows are built only when the role list changes. refreshScan() only updates the lamp
    badge text (textContent), so the checkboxes are never destroyed or overwritten.
  * Saves check state to localStorage "rgon_omni_checked_v607".
  * Wires select-all / clear-all / checked fire / fire-all / per-row solo fire.
  * Cleans up old duplicate renderDispatchTargets patch blocks.
  * Bumps the version to 6.0.7 in manifest.json / background.js / content_aside_bar.js.
  * Verifies with `node --check`; restores the backups automatically on failure.
"""
import os
import re
import sys
import json
import shutil
import tempfile
import subprocess
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_DIR = r"C:\Users\sangi\Downloads\shin-agent\rgon_aside_extension"
if len(sys.argv) > 1:
    BASE_DIR = sys.argv[1]

CONTENT_PATH = os.path.join(BASE_DIR, "content_aside_bar.js")
BG_PATH = os.path.join(BASE_DIR, "background.js")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")

OLD_VER = "6.0.6"
NEW_VER = "6.0.7"

MARK_BEGIN = "/* RGON_V607_BEGIN */"
MARK_END = "/* RGON_V607_END */"

SHIM_NAMES = ["renderTargets", "renderDispatchTargets"]

CONTAINER_HTML_TEMPLATE = (
    "<div id=QtargetCheckListQ "
    "style=Qdisplay:flex;flex-direction:column;gap:6px;margin-top:8px;Q></div>"
)

# ---------------------------------------------------------------------------
# JS module (inserted inside the main IIFE so it can reach fire / state / log)
# ---------------------------------------------------------------------------
JS_MODULE = r"""
var __v607Api = null;
var __v607LastScan = null;

function __v607Sync() {
  try {
    if (__v607Api && typeof __v607Api.sync === 'function') { __v607Api.sync(); }
  } catch (e) {
    try { console.warn('[v6.0.7] sync error:', e); } catch (_) {}
  }
}

__v607Api = (function () {
  var CHECK_KEY = 'rgon_omni_checked_v607';
  var CONTAINER_STYLE = 'display:flex;flex-direction:column;gap:6px;margin-top:8px;';
  var DEFAULT_ROLES = [
    { role: 'claude', icon: '🟠', label: '🧠 Claude (설계·코드)', def: true },
    { role: 'gpt',    icon: '🟢', label: '⚡ GPT (검증·코드)',    def: true },
    { role: 'grok',   icon: '🟣', label: '🔥 Grok (바이럴·카피)', def: false }
  ];
  var KEY_ALIAS = { chatgpt: 'gpt', openai: 'gpt', anthropic: 'claude', xai: 'grok' };
  var URL_ALIAS = [
    [/claude\.ai/i, 'claude'],
    [/chatgpt\.com|chat\.openai\.com/i, 'gpt'],
    [/grok\.com|x\.com\/i\/grok|grok\.x\.ai/i, 'grok']
  ];
  var BLACK = /custom|check|select|prompt|config|setting|history|draft|queue|chosen/i;
  var WHITE = /scan|tab|conn|lamp|status|alive|online|open|found|detect|count/i;

  var cachedCustomRaw = null;
  var lastCaptured = null;
  var rootsCache = [];
  var syncTimer = null;

  /* ---------- utils ---------- */
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function textNorm(s) {
    return String(s || '').replace(/[^\uAC00-\uD7A3A-Za-z0-9\s]/g, '').replace(/\s+/g, ' ').trim();
  }
  function getState() {
    try { return (typeof state !== 'undefined') ? state : null; } catch (e) { return null; }
  }

  /* ---------- roots (document + open shadow roots) ---------- */
  function collectRoots() {
    var roots = [document];
    try {
      for (var qi = 0; qi < roots.length && qi < 50; qi++) {
        var all = roots[qi].querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
          if (all[i].shadowRoot) { roots.push(all[i].shadowRoot); }
        }
      }
    } catch (e) {}
    rootsCache = roots;
    return roots;
  }
  function qIn(roots, sel) {
    for (var i = 0; i < roots.length; i++) {
      try {
        var el = roots[i].querySelector(sel);
        if (el) return el;
      } catch (e) {}
    }
    return null;
  }
  function q(sel) {
    var el = qIn(rootsCache.length ? rootsCache : [document], sel);
    if (el && el.isConnected) return el;
    el = qIn(collectRoots(), sel);
    return el;
  }

  /* ---------- role list ---------- */
  function normalizeCustom(raw) {
    var out = [];
    if (!raw) return out;
    var list = [];
    if (Array.isArray(raw)) {
      list = raw;
    } else if (typeof raw === 'object') {
      Object.keys(raw).forEach(function (k) {
        var v = raw[k];
        if (v && typeof v === 'object') { list.push(Object.assign({ role: k }, v)); }
        else { list.push({ role: k, label: (typeof v === 'string' && v) ? v : k }); }
      });
    }
    list.forEach(function (it) {
      var role, label;
      if (typeof it === 'string') { role = it; label = it; }
      else if (it && typeof it === 'object') {
        role = it.role || it.id || it.key || it.name || it.label;
        label = it.label || it.name || it.title || role;
      }
      if (!role) return;
      role = String(role);
      label = String(label || role).replace(/^🔮\s*/, '');
      out.push({ role: role, label: label });
    });
    return out;
  }

  function getAllRoles() {
    var out = DEFAULT_ROLES.map(function (r) {
      return { role: r.role, icon: r.icon, label: r.label, def: r.def };
    });
    var seen = {};
    out.forEach(function (r) { seen['r:' + r.role] = 1; });
    var sources = [];
    var st = getState();
    if (st && st.customRoles) sources.push(st.customRoles);
    sources.push(cachedCustomRaw);
    sources.forEach(function (src) {
      normalizeCustom(src).forEach(function (c) {
        if (seen['r:' + c.role]) return;
        seen['r:' + c.role] = 1;
        out.push({ role: c.role, icon: '🔮', label: c.label, def: false });
      });
    });
    return out;
  }

  /* ---------- checked state (localStorage, synchronous) ---------- */
  function loadChecked() {
    try {
      var raw = localStorage.getItem(CHECK_KEY);
      if (!raw) return {};
      var o = JSON.parse(raw);
      return (o && typeof o === 'object' && !Array.isArray(o)) ? o : {};
    } catch (e) { return {}; }
  }
  function storeChecked(o) {
    try { localStorage.setItem(CHECK_KEY, JSON.stringify(o)); } catch (e) {}
  }
  function saveChecked() {
    var c = q('#targetCheckList');
    if (!c) return;
    var o = loadChecked();
    var boxes = c.querySelectorAll('.role-chk');
    for (var i = 0; i < boxes.length; i++) { o[boxes[i].value] = !!boxes[i].checked; }
    storeChecked(o);
  }

  /* ---------- connection counts (lamp data) ---------- */
  function tabRole(o) {
    var fields = ['role', 'roleKey', 'roleId', 'aiRole', 'assignedRole', 'ai', 'provider', 'platform', 'site'];
    for (var i = 0; i < fields.length; i++) {
      var v = o[fields[i]];
      if (typeof v === 'string' && v) {
        var low = v.toLowerCase();
        if (Object.prototype.hasOwnProperty.call(KEY_ALIAS, low)) return KEY_ALIAS[low];
        return v;
      }
    }
    if (typeof o.url === 'string') {
      for (var j = 0; j < URL_ALIAS.length; j++) {
        if (URL_ALIAS[j][0].test(o.url)) return URL_ALIAS[j][1];
      }
    }
    return null;
  }

  function extractCounts(data) {
    var map = {}, found = false, seen = [];
    var known = {};
    getAllRoles().forEach(function (r) { known['r:' + r.role] = 1; });
    function add(role, n) {
      if (!role || typeof n !== 'number' || isNaN(n)) return;
      found = true;
      map['r:' + role] = (map['r:' + role] || 0) + n;
    }
    function isTabLike(o) {
      return o.tabId != null || typeof o.url === 'string' || typeof o.id === 'number' || o.windowId != null;
    }
    function walk(node, depth) {
      if (!node || typeof node !== 'object' || depth > 3 || seen.indexOf(node) !== -1) return;
      seen.push(node);
      if (Array.isArray(node)) {
        for (var i = 0; i < node.length && i < 200; i++) {
          var el = node[i];
          if (!el || typeof el !== 'object') continue;
          if (Array.isArray(el)) { walk(el, depth + 1); continue; }
          var r = tabRole(el);
          if (r && isTabLike(el)) add(r, 1);
          else if (r && typeof el.count === 'number') add(r, el.count);
          else walk(el, depth + 1);
        }
        return;
      }
      var keys = Object.keys(node);
      for (var j = 0; j < keys.length && j < 200; j++) {
        var k = keys[j], v;
        try { v = node[k]; } catch (e) { continue; }
        if (known['r:' + k]) {
          if (typeof v === 'number') add(k, v);
          else if (Array.isArray(v)) add(k, v.length);
          else if (v && typeof v === 'object') {
            var n = (typeof v.count === 'number') ? v.count
              : (Array.isArray(v.tabs) ? v.tabs.length
              : (v.connected === true ? 1 : 0));
            add(k, n);
          }
        } else if (v && typeof v === 'object' && !BLACK.test(k)) {
          walk(v, depth + 1);
        }
      }
    }
    walk(data, 0);
    return { found: found, map: map };
  }

  function computeCounts() {
    var result = {};
    function merge(ex) {
      if (!ex) return;
      Object.keys(ex.map).forEach(function (k) { result[k] = Math.max(result[k] || 0, ex.map[k]); });
    }
    try {
      var st = getState();
      if (st && typeof st === 'object') {
        Object.keys(st).forEach(function (k) {
          if (WHITE.test(k) && !BLACK.test(k)) {
            var v = st[k];
            if (v && typeof v === 'object') merge(extractCounts(v));
          }
        });
      }
    } catch (e) {}
    try { if (__v607LastScan && typeof __v607LastScan === 'object') merge(extractCounts(__v607LastScan)); } catch (e) {}
    if (lastCaptured && (Date.now() - lastCaptured.t) < 15000) merge(lastCaptured.ex);
    return result;
  }

  function capture(resp) {
    try {
      var ex = extractCounts(resp);
      if (ex && ex.found) lastCaptured = { t: Date.now(), ex: ex };
    } catch (e) {}
  }

  function hookRuntime() {
    try {
      if (!(chrome && chrome.runtime && chrome.runtime.sendMessage) || chrome.runtime.sendMessage.__v607) return;
      var orig = chrome.runtime.sendMessage;
      var wrapped = function () {
        var args = Array.prototype.slice.call(arguments);
        var last = args.length - 1;
        if (last >= 0 && typeof args[last] === 'function') {
          var cb = args[last];
          args[last] = function (resp) { capture(resp); return cb.apply(this, arguments); };
          return orig.apply(chrome.runtime, args);
        }
        var p = orig.apply(chrome.runtime, args);
        if (p && typeof p.then === 'function') { p.then(capture, function () {}); }
        return p;
      };
      wrapped.__v607 = true;
      chrome.runtime.sendMessage = wrapped;
    } catch (e) {}
  }

  /* ---------- container guarantee ---------- */
  function createContainerNear() {
    var roots = collectRoots();
    var target = null;
    for (var r = 0; r < roots.length && !target; r++) {
      var btns;
      try { btns = roots[r].querySelectorAll('button,[role="button"]'); } catch (e) { continue; }
      for (var b = 0; b < btns.length; b++) {
        if (textNorm(btns[b].textContent) !== '전체 해제') continue;
        var anc = btns[b], ok = false;
        for (var k = 0; k < 8 && anc; k++, anc = anc.parentElement) {
          if ((anc.textContent || '').indexOf('발사 대상 선택') !== -1) { ok = true; break; }
        }
        if (ok) { target = btns[b]; break; }
      }
    }
    if (!target) return null;
    var row = target.parentElement;
    for (var h = 0; h < 3 && row && (row.textContent || '').indexOf('전체 선택') === -1; h++) {
      row = row.parentElement;
    }
    if (!row || !row.parentNode) return null;
    var el = target.ownerDocument.createElement('div');
    el.id = 'targetCheckList';
    el.setAttribute('style', CONTAINER_STYLE);
    row.parentNode.insertBefore(el, row.nextSibling);
    return el;
  }

  function findContainer(createIfMissing) {
    var c = q('#targetCheckList');
    if (c) return c;
    if (!createIfMissing) return null;
    var host = q('#dispatchTargets');
    var el;
    if (host) {
      el = host.ownerDocument.createElement('div');
      el.id = 'targetCheckList';
      el.setAttribute('style', CONTAINER_STYLE);
      host.appendChild(el);
      return el;
    }
    return createContainerNear();
  }

  /* ---------- rows: build ONLY when role list changes ---------- */
  function ensureTargetRows() {
    var c = findContainer(true);
    if (!c) return null;
    var roles = getAllRoles();
    var key = roles.map(function (r) { return r.role; }).join('|');
    var okRows = c.querySelectorAll('.target-row[data-v607="1"]').length;
    if (c.getAttribute('data-roles-key') === key && okRows === roles.length && okRows > 0) {
      return c; /* rows already exist -> never touch innerHTML again */
    }
    var saved = loadChecked();
    var old = c.querySelectorAll('.role-chk');
    for (var i = 0; i < old.length; i++) { saved[old[i].value] = !!old[i].checked; }

    var html = '';
    roles.forEach(function (r) {
      var isChecked = Object.prototype.hasOwnProperty.call(saved, r.role) ? !!saved[r.role] : !!r.def;
      html += `<div class="target-row" data-v607="1" data-role="${esc(r.role)}" style="display:flex;align-items:center;justify-content:space-between;gap:8px;padding:6px 8px;border:1px solid rgba(255,255,255,0.15);border-radius:8px;">`
        + `<label style="display:flex;align-items:center;gap:6px;flex:1;min-width:0;cursor:pointer;">`
        + `<input type="checkbox" class="role-chk tgt-chk" value="${esc(r.role)}" ${isChecked ? 'checked' : ''}> `
        + `<span>${esc(r.icon)} ${esc(r.label)}</span> `
        + `<span class="role-lamp-badge" data-lamp="${esc(r.role)}" style="font-size:11px;opacity:0.9;white-space:nowrap;">⚪ 미연결</span>`
        + `</label>`
        + `<button type="button" class="btn ghost solo-fire-btn" data-solo="${esc(r.role)}" style="white-space:nowrap;">🚀 단독 발사</button>`
        + `</div>`;
    });
    c.innerHTML = html;
    c.setAttribute('data-roles-key', key);
    saveChecked();
    return c;
  }

  /* ---------- status only: textContent of badges ---------- */
  function updateTargetRowStatus() {
    var c = q('#targetCheckList');
    if (!c) return;
    var counts = computeCounts();
    var rows = c.querySelectorAll('.target-row');
    for (var i = 0; i < rows.length; i++) {
      var role = rows[i].getAttribute('data-role');
      var badge = rows[i].querySelector('.role-lamp-badge');
      if (!badge) continue;
      var n = counts['r:' + role] || 0;
      var txt = n > 0 ? ('🟢 연결(' + n + ')') : '⚪ 미연결';
      if (badge.textContent !== txt) badge.textContent = txt;
      badge.style.color = n > 0 ? '#4ade80' : '';
    }
  }

  /* ---------- fire helpers ---------- */
  function resolveFire() {
    try { if (typeof fire === 'function') return fire; } catch (e) {}
    try { if (typeof window.fire === 'function') return window.fire; } catch (e) {}
    return null;
  }

  function logMsg(msg) {
    try { if (typeof log === 'function') { log(msg); return; } } catch (e) {}
    try { if (typeof addLog === 'function') { addLog(msg); return; } } catch (e) {}
    try { if (typeof appendLog === 'function') { appendLog(msg); return; } } catch (e) {}
    try {
      var el = q('#logBox') || q('#log') || q('#omniLog') || q('#logArea') || q('#fireLog');
      if (el) {
        if (el.tagName === 'TEXTAREA') { el.value += msg + '\n'; }
        else {
          var d = el.ownerDocument.createElement('div');
          d.textContent = msg;
          el.appendChild(d);
        }
        return;
      }
    } catch (e) {}
    try { console.warn('[v6.0.7]', msg); } catch (e) {}
  }

  function doFire(f, roles) {
    try {
      var r = f(roles);
      if (r && typeof r.then === 'function') {
        r.then(null, function (e) { logMsg('❌ 발사 오류: ' + ((e && e.message) || e)); });
      }
    } catch (e) {
      logMsg('❌ 발사 오류: ' + ((e && e.message) || e));
    }
  }

  function getCheckedRoles(c) {
    var out = [];
    var boxes = c.querySelectorAll('.role-chk:checked');
    for (var i = 0; i < boxes.length; i++) out.push(boxes[i].value);
    return out;
  }
  function getAllRoleKeys(c) {
    var out = [];
    var boxes = c.querySelectorAll('.role-chk');
    for (var i = 0; i < boxes.length; i++) out.push(boxes[i].value);
    return out;
  }
  function setAll(c, flag) {
    var boxes = c.querySelectorAll('.role-chk');
    for (var i = 0; i < boxes.length; i++) boxes[i].checked = flag;
    saveChecked();
  }
  function boxOf(c) {
    var b = c.parentElement;
    for (var i = 0; i < 4 && b; i++) {
      if ((b.textContent || '').indexOf('전체 해제') !== -1) return b;
      b = b.parentElement;
    }
    return c.parentElement;
  }
  function stop(ev) {
    try { ev.preventDefault(); } catch (e) {}
    try { ev.stopPropagation(); } catch (e) {}
    try { ev.stopImmediatePropagation(); } catch (e) {}
  }

  function handleButton(btn, ev) {
    var c = q('#targetCheckList');
    if (!c) return false;
    var f;

    if (btn.classList && btn.classList.contains('solo-fire-btn') && btn.hasAttribute('data-solo')) {
      if (!c.contains(btn)) return false;
      f = resolveFire();
      if (!f) { logMsg('⚠️ fire() 함수를 찾지 못했습니다.'); return false; }
      stop(ev);
      doFire(f, [btn.getAttribute('data-solo')]);
      return true;
    }

    if (c.contains(btn)) return false;
    var label = textNorm(btn.textContent);
    var box = boxOf(c);

    if (box && box.contains(btn) && (label === '전체 선택' || label === '전체 해제')) {
      stop(ev);
      setAll(c, label === '전체 선택');
      return true;
    }

    if (btn.getRootNode && btn.getRootNode() !== c.getRootNode()) return false;

    if (label.indexOf('체크 선택 발사') === 0) {
      var checked = getCheckedRoles(c);
      if (checked.length === 0) {
        stop(ev);
        logMsg('⚠️ 발사할 대상을 1개 이상 체크하세요.');
        return true;
      }
      f = resolveFire();
      if (!f) return false;
      stop(ev);
      doFire(f, checked);
      return true;
    }

    if (label === '전체 발사' || label.indexOf('전체 발사 ') === 0) {
      f = resolveFire();
      if (!f) return false;
      stop(ev);
      doFire(f, getAllRoleKeys(c));
      return true;
    }
    return false;
  }

  /* ---------- events ---------- */
  function onClick(ev) {
    try {
      var path = (ev.composedPath && ev.composedPath()) || [];
      var t = path[0] || ev.target;
      if (t && t.closest) {
        var btn = t.closest('button,[role="button"]');
        if (btn && handleButton(btn, ev)) return;
      }
    } catch (e) {}
    scheduleSync();
  }

  function onChange(ev) {
    try {
      var t = (ev.composedPath && ev.composedPath()[0]) || ev.target;
      if (t && t.classList && t.classList.contains('role-chk') && t.closest && t.closest('#targetCheckList')) {
        saveChecked();
      }
    } catch (e) {}
  }

  function bindChange() {
    var roots = rootsCache.length ? rootsCache : collectRoots();
    roots.forEach(function (r) {
      if (r.__v607Bound) return;
      r.__v607Bound = true;
      try { r.addEventListener('change', onChange, true); } catch (e) {}
    });
  }

  /* ---------- sync: ensureTargetRows -> updateTargetRowStatus ---------- */
  function sync() {
    try {
      ensureTargetRows();
      updateTargetRowStatus();
      bindChange();
    } catch (e) {
      try { console.warn('[v6.0.7] sync failed:', e); } catch (_) {}
    }
  }

  function scheduleSync() {
    if (syncTimer) return;
    syncTimer = setTimeout(function () {
      syncTimer = null;
      sync();
      setTimeout(sync, 250);
    }, 30);
  }

  function loadCustom() {
    try {
      if (chrome && chrome.storage && chrome.storage.local) {
        chrome.storage.local.get(['omni_custom_roles'], function (res) {
          try { if (chrome.runtime && chrome.runtime.lastError) return; } catch (e) {}
          cachedCustomRaw = res ? res.omni_custom_roles : null;
          scheduleSync();
        });
        if (chrome.storage.onChanged) {
          try { if (window.__rgonV607Chg) chrome.storage.onChanged.removeListener(window.__rgonV607Chg); } catch (e) {}
          window.__rgonV607Chg = function (changes, area) {
            if (area === 'local' && changes && changes.omni_custom_roles) {
              cachedCustomRaw = changes.omni_custom_roles.newValue;
              scheduleSync();
            }
          };
          chrome.storage.onChanged.addListener(window.__rgonV607Chg);
        }
      }
    } catch (e) {}
  }

  /* ---------- bootstrap ---------- */
  hookRuntime();
  loadCustom();
  try { if (window.__rgonV607Click) window.removeEventListener('click', window.__rgonV607Click, true); } catch (e) {}
  window.__rgonV607Click = onClick;
  window.addEventListener('click', onClick, true);
  try { if (window.__rgonV607Timer) clearInterval(window.__rgonV607Timer); } catch (e) {}
  window.__rgonV607Timer = setInterval(sync, 3500);
  try {
    if (window.__rgonV607MO) window.__rgonV607MO.disconnect();
    var mo = new MutationObserver(function () { scheduleSync(); });
    mo.observe(document.documentElement, { childList: true });
    if (document.body) mo.observe(document.body, { childList: true });
    window.__rgonV607MO = mo;
  } catch (e) {}
  sync();
  scheduleSync();

  var api = {
    sync: sync,
    ensureTargetRows: ensureTargetRows,
    updateTargetRowStatus: updateTargetRowStatus,
    getAllRoles: getAllRoles,
    computeCounts: computeCounts
  };
  try { window.__RGON_V607 = api; } catch (e) {}
  return api;
})();
"""

JS_REFRESH_WRAPPER = r"""
function refreshScan() {
  var r = __v607_origRefreshScan.apply(this, arguments);
  if (r && typeof r.then === 'function') {
    return r.then(function (v) { __v607LastScan = v; __v607Sync(); return v; },
                  function (e) { __v607Sync(); throw e; });
  }
  __v607LastScan = r;
  __v607Sync();
  return r;
}
"""


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def info(msg):
    print(msg)


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    return text, {"bom": bom, "crlf": crlf}


def write_text(path, text, meta):
    if meta.get("crlf"):
        text = text.replace("\n", "\r\n")
    data = text.encode("utf-8")
    if meta.get("bom"):
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def node_check_text(text, node):
    fd, tmp = tempfile.mkstemp(suffix=".js")
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        p = subprocess.run([node, "--check", tmp], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        return p.returncode == 0, (p.stderr or p.stdout or "").strip()
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass


def node_check_file(path, node):
    p = subprocess.run([node, "--check", path], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, (p.stderr or p.stdout or "").strip()


def is_balanced(code):
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    i, n = 0, len(code)
    while i < n:
        ch = code[i]
        nx = code[i + 1] if i + 1 < n else ""
        if ch == "/" and nx == "/":
            j = code.find("\n", i)
            i = n if j < 0 else j
        elif ch == "/" and nx == "*":
            j = code.find("*/", i + 2)
            i = n if j < 0 else j + 1
        elif ch in "'\"`":
            quote = ch
            i += 1
            while i < n and code[i] != quote:
                if code[i] == "\\":
                    i += 1
                i += 1
        elif ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
        i += 1
    return not stack


# ---------------------------------------------------------------------------
# content_aside_bar.js transformation steps
# ---------------------------------------------------------------------------
def remove_previous_v607(s):
    s = re.sub(r"/\* RGON_V607_BEGIN \*/.*?/\* RGON_V607_END \*/[ \t]*\n?", "", s, flags=re.S)
    s = s.replace("__v607_origRefreshScan", "refreshScan")
    s = re.sub(r"__v607_legacy_(\w+)", r"\1", s)
    return s


HEADER_RE = re.compile(
    r"^[ \t]{0,2}(?://|/\*).*?(?:(?<![A-Za-z])(?:PATCH|HOTFIX|FIXED|FIX)(?![A-Za-z])|패치|핫픽스|보정)",
    re.I,
)
KEY_RE = re.compile(r"renderDispatchTargets|renderTargets|origRefreshScan")
CORE_DEF_RE = re.compile(
    r"\b(?:async\s+)?function\s+(?:refreshScan|fire|init\w*|build\w*|mount\w*|createPanel|togglePanel)\s*\("
)
IIFE_CLOSE_LINE_RE = re.compile(r"^\s*\}\s*(?:\)\s*\(\s*\)|\(\s*\)\s*\))\s*;?\s*(?://.*)?$")


def strip_legacy_blocks(src):
    lines = src.split("\n")
    total = len(lines)
    close_idx = total
    for idx in range(total - 1, -1, -1):
        if IIFE_CLOSE_LINE_RE.match(lines[idx]):
            close_idx = idx
            break
    headers = [i for i, l in enumerate(lines)
               if HEADER_RE.search(l) and i >= total * 0.5 and i < close_idx]
    removed_ranges = []
    descriptions = []
    for n, h in enumerate(headers):
        end = headers[n + 1] if n + 1 < len(headers) else close_idx
        body = "\n".join(lines[h:end])
        if not KEY_RE.search(body):
            continue
        if CORE_DEF_RE.search(body):
            continue
        if not is_balanced(body):
            continue
        defined = set(re.findall(r"\bfunction\s+(\w+)", body))
        defined |= set(re.findall(r"\b(?:const|let|var)\s+(\w+)\s*=", body))
        rest_lines = [l for k, l in enumerate(lines)
                      if not (h <= k < end) and not any(a <= k < b for a, b in removed_ranges)]
        rest = "\n".join(rest_lines)
        unsafe = False
        for name in defined:
            if name in SHIM_NAMES:
                continue
            if re.search(r"\b" + re.escape(name) + r"\b", rest):
                unsafe = True
                break
        if unsafe:
            continue
        removed_ranges.append((h, end))
        descriptions.append("line %d-%d: %s" % (h + 1, end, lines[h].strip()[:80]))
    if not removed_ranges:
        return src, []
    keep = [l for k, l in enumerate(lines) if not any(a <= k < b for a, b in removed_ranges)]
    return "\n".join(keep), descriptions


def insert_static_container(s):
    if re.search(r"id\s*=\s*\\?[\"']targetCheckList\\?[\"']", s):
        return s, "already-present"
    i = s.find("발사 대상 선택")
    if i < 0:
        return s, "heading-not-found"
    j = s.find("전체 해제", i)
    if j < 0 or j - i > 4000:
        return s, "clear-button-not-found"
    k = s.find("</button>", j)
    if k < 0:
        return s, "button-close-not-found"
    m = re.compile(r"\s*</div>").match(s, k + len("</button>"))
    if not m:
        return s, "row-close-not-found"
    ins_pos = m.end()
    row_open = s.rfind("<div", i, j)
    if row_open < 0:
        return s, "row-open-not-found"
    seg = s[row_open:ins_pos]
    if seg.count("<div") != seg.count("</div>"):
        return s, "row-unbalanced"
    ctx = s[max(0, i - 1500):ins_pos]
    qm = re.findall(r"class=(\\?[\"'])", ctx)
    quote = qm[-1] if qm else '"'
    html = CONTAINER_HTML_TEMPLATE.replace("Q", quote)
    return s[:ins_pos] + html + s[ins_pos:], "inserted"


def rename_refresh_scan(s):
    def r1(m):
        return (m.group(1) or "") + "function __v607_origRefreshScan("
    s, c1 = re.subn(r"(\basync\s+)?function\s+refreshScan\s*\(", r1, s)
    s, c2 = re.subn(r"\b(const|let|var)\s+refreshScan\s*=", r"\1 __v607_origRefreshScan =", s)
    return s, c1 + c2


def handle_shims(s):
    shims = []
    for name in SHIM_NAMES:
        pat_fn = re.compile(r"(\basync\s+)?function\s+" + name + r"\s*\(")
        pat_var = re.compile(r"\b(const|let|var)\s+" + name + r"\s*=")
        defined = bool(pat_fn.search(s) or pat_var.search(s))
        referenced = bool(re.search(r"\b" + name + r"\s*\(", s))
        if defined:
            s = pat_fn.sub(lambda m, n=name: (m.group(1) or "") + "function __v607_legacy_" + n + "(", s)
            s = pat_var.sub(lambda m, n=name: m.group(1) + " __v607_legacy_" + n + " =", s)
        if defined or referenced:
            shims.append(name)
    return s, shims


WRAPPED_START_RE = re.compile(
    r"\A\s*(?:(?://[^\n]*\n|/\*.*?\*/)\s*)*(?:[\"']use strict[\"'];?\s*)?;?\s*[!(]\s*"
    r"(?:async\s+)?(?:function\b|\(\s*\)\s*=>|\w+\s*=>)",
    re.S,
)
CLOSE_COL0_RE = re.compile(
    r"^\}\s*(?:\)\s*\(\s*\)|\(\s*\)\s*\))\s*;?[ \t]*(?://[^\n]*)?$", re.M
)
DEF_POS_RE = re.compile(
    r"\b(?:function\s+(?:fire|refreshScan|__v607_origRefreshScan)\s*\(|"
    r"(?:const|let|var)\s+(?:fire|refreshScan|__v607_origRefreshScan)\s*=)"
)


def build_block(hooked, shims):
    parts = [MARK_BEGIN, JS_MODULE.strip("\n")]
    if hooked:
        parts.append(JS_REFRESH_WRAPPER.strip("\n"))
    for name in shims:
        parts.append("function %s() { __v607Sync(); }" % name)
    parts.append(MARK_END)
    return "\n".join(parts) + "\n"


def insert_block(s, block):
    if not WRAPPED_START_RE.match(s):
        return s.rstrip("\n") + "\n\n" + block, "append-eof (file is not IIFE-wrapped)"
    closes = list(CLOSE_COL0_RE.finditer(s))
    if not closes:
        return s.rstrip("\n") + "\n\n" + block, "append-eof (IIFE close not found)"
    dm = DEF_POS_RE.search(s)
    chosen = None
    if dm:
        for c in closes:
            if c.start() > dm.start():
                chosen = c
                break
    if chosen is None:
        chosen = closes[-1]
    pos = chosen.start()
    return s[:pos] + block + "\n" + s[pos:], "inside-iife"


def build_content(raw, strip_legacy, static_html, report):
    s = remove_previous_v607(raw)
    s = s.replace(OLD_VER, NEW_VER)

    if strip_legacy:
        s, removed = strip_legacy_blocks(s)
        report["legacy_removed"] = removed

    if static_html:
        s, status = insert_static_container(s)
        report["static_container"] = status
    else:
        report["static_container"] = "skipped"

    s, hook_count = rename_refresh_scan(s)
    report["refresh_hooked"] = hook_count
    s, shims = handle_shims(s)
    report["shims"] = shims

    block = build_block(hook_count > 0, shims)
    s, where = insert_block(s, block)
    report["insert"] = where
    return s


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    info("=" * 64)
    info(" RGON Aside Extension  v%s -> v%s  (CLAUDE MASTER FIX)" % (OLD_VER, NEW_VER))
    info(" base dir: " + BASE_DIR)
    info("=" * 64)

    for p in (CONTENT_PATH, BG_PATH, MANIFEST_PATH):
        if not os.path.isfile(p):
            info("[ERROR] File not found: " + p)
            sys.exit(1)

    node = shutil.which("node")
    if not node:
        info("[WARN] node was not found, so `node --check` will be skipped. Install Node.js to verify syntax.")

    ts = time.strftime("%Y%m%d_%H%M%S")
    backups = {}
    for p in (CONTENT_PATH, BG_PATH, MANIFEST_PATH):
        b = "%s.bak_v606_%s" % (p, ts)
        shutil.copy2(p, b)
        backups[p] = b
        info("[BACKUP] " + os.path.basename(b))

    def rollback():
        for p, b in backups.items():
            try:
                shutil.copy2(b, p)
            except Exception as e:
                info("[ROLLBACK ERROR] %s: %s" % (p, e))
        info("[ROLLBACK] Restored the original files from the backups.")

    try:
        # ---------------- content_aside_bar.js ----------------
        raw, meta = read_text(CONTENT_PATH)
        attempts = [(True, True), (False, True), (True, False), (False, False)]
        final_text, final_report = None, None
        last_err = ""
        for strip_legacy, static_html in attempts:
            report = {}
            try:
                candidate = build_content(raw, strip_legacy, static_html, report)
            except Exception as e:
                last_err = "build error: %s" % e
                continue
            if node:
                ok, msg = node_check_text(candidate, node)
                if not ok:
                    last_err = msg
                    info("[RETRY] strip_legacy=%s static_html=%s -> node --check failed, trying the next strategy"
                         % (strip_legacy, static_html))
                    continue
            elif not is_balanced(candidate):
                last_err = "bracket balance check failed"
                continue
            final_text, final_report = candidate, report
            break

        if final_text is None:
            info("[ERROR] Could not produce a patch that passes the syntax check.\n" + last_err)
            rollback()
            sys.exit(2)

        write_text(CONTENT_PATH, final_text, meta)
        info("[OK] content_aside_bar.js patched")
        info("     - legacy patch blocks removed : %d" % len(final_report.get("legacy_removed", [])))
        for d in final_report.get("legacy_removed", []):
            info("         · " + d)
        info("     - static #targetCheckList     : " + str(final_report.get("static_container")))
        info("     - refreshScan hook definitions: %s" % final_report.get("refresh_hooked"))
        info("     - render function shims       : %s" % (", ".join(final_report.get("shims", [])) or "none"))
        info("     - module insert position      : " + str(final_report.get("insert")))

        # ---------------- background.js ----------------
        bg, bg_meta = read_text(BG_PATH)
        cnt = bg.count(OLD_VER)
        bg_new = bg.replace(OLD_VER, NEW_VER)
        write_text(BG_PATH, bg_new, bg_meta)
        info("[OK] background.js version references updated: %d" % cnt)

        # ---------------- manifest.json ----------------
        mf, mf_meta = read_text(MANIFEST_PATH)
        mf_new, n = re.subn(r'("version"\s*:\s*")[^"]*(")', r"\g<1>" + NEW_VER + r"\g<2>", mf, count=1)
        mf_new = re.sub(r'("version_name"\s*:\s*"[^"]*?)' + re.escape(OLD_VER), r"\g<1>" + NEW_VER, mf_new)
        data = json.loads(mf_new)
        perms = data.get("permissions")
        if not isinstance(perms, list):
            perms = [] if perms is None else list(perms)
        if "storage" not in perms:
            perms.append("storage")
            data["permissions"] = perms
            mf_new = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            info("[OK] manifest.json: added the 'storage' permission (needed to read omni_custom_roles)")
        else:
            json.loads(mf_new)
        write_text(MANIFEST_PATH, mf_new, mf_meta)
        info("[OK] manifest.json version -> %s (replaced: %d)" % (NEW_VER, n))

        # ---------------- final verification ----------------
        if node:
            all_ok = True
            for p in (CONTENT_PATH, BG_PATH):
                ok, msg = node_check_file(p, node)
                info("[node --check] %s : %s" % (os.path.basename(p), "PASS" if ok else "FAIL"))
                if not ok:
                    info(msg)
                    all_ok = False
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8-sig") as f:
                    json.load(f)
                info("[json check] manifest.json : PASS")
            except Exception as e:
                info("[json check] manifest.json : FAIL (%s)" % e)
                all_ok = False
            if not all_ok:
                rollback()
                sys.exit(3)

    except SystemExit:
        raise
    except Exception as e:
        info("[FATAL] " + repr(e))
        rollback()
        sys.exit(4)

    info("")
    info("Reload the extension at chrome://extensions, then refresh the page.")
    info("[v6.0.7 CLAUDE MASTER FIX COMPLETE]")


if __name__ == "__main__":
    main()
