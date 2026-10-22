# -*- coding: utf-8 -*-
"""
upgrade_omni_link_v603.py
RGON Omni-Link Hub v6.0.2 -> v6.0.3 업그레이드 스크립트

[v6.0.3 변경 사항]
 1) [📡 신경망] 탭 하단: '✏️ 직접 쓰기' 커스텀 신경망 역할 지정
    - #roleSel 마지막 옵션 __custom__ 추가, #customRoleName 입력창 노출
    - omni_custom_roles / omni_override 저장
    - 램프 목록 / 작업 분배 / 흡수기 대상에 동적 확장
 2) [⚡ 작업 분배] 탭: 체크박스 + 단독 발사 + 체크 선택 발사 + 전체 발사 구조
    - 독대실(rgon_alpha_chat.html) HTML_BLOCK 분배 컨트롤러도 동일 반영
 3) v6.0.2 기능 100% 유지
    - 🗑️ 전체 지우기 / 📋 새로 붙여넣기 / #autoclear / #autoCleanAbs
    - 🗑️ 흡수함 전체 비우기 / 카드별 ✕ 삭제 / Copy 접두어 제거
    - 로컬 브리지 8765 백그라운드 재기동 + 200 OK 검증
"""
import os
import re
import sys
import json
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OMNI_VERSION = "6.0.3"
BRIDGE_PORT = 8765

BASE = Path(__file__).resolve().parent
PREV_SCRIPT = BASE / "upgrade_omni_link_v602.py"

_EXT_CANDIDATES = ["omni_link_ext", "omni_link_extension", "rgon_omni_link", "omni_link"]
EXT_DIR = None
for _c in _EXT_CANDIDATES:
    if (BASE / _c / "manifest.json").exists():
        EXT_DIR = BASE / _c
        break
if EXT_DIR is None:
    EXT_DIR = BASE / "omni_link_ext"

BRIDGE_PY = BASE / "omni_bridge.py"
CHAT_HTML = BASE / "rgon_alpha_chat.html"
BACKUP_DIR = BASE / "backups"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def fill(s: str) -> str:
    return s.replace("__OMNI_VERSION__", OMNI_VERSION).replace("__PORT__", str(BRIDGE_PORT))


# =====================================================================
# manifest.json
# =====================================================================
MANIFEST = {
    "manifest_version": 3,
    "name": "RGON Omni-Link Hub",
    "version": OMNI_VERSION,
    "description": "RGON Omni-Link Hub v" + OMNI_VERSION + " - Custom Neural & Solo/Check Dispatch",
    "permissions": ["storage", "tabs", "scripting", "clipboardRead", "clipboardWrite", "alarms"],
    "host_permissions": ["<all_urls>"],
    "background": {"service_worker": "background.js"},
    "action": {"default_popup": "popup.html", "default_title": "RGON Omni-Link v" + OMNI_VERSION},
}

# =====================================================================
# core.js (popup + background 공용)
# =====================================================================
CORE_JS = r'''// RGON Omni-Link core v__OMNI_VERSION__
const OMNI_VERSION = "__OMNI_VERSION__";
const BRIDGE = "http://127.0.0.1:__PORT__";

const BUILTIN_ROLES = {
  claude: { label: "Claude", icon: "🧠", patterns: ["https://claude.ai/*"] },
  gpt:    { label: "GPT",    icon: "⚡", patterns: ["https://chatgpt.com/*", "https://chat.openai.com/*"] },
  grok:   { label: "Grok",   icon: "🎯", patterns: ["https://grok.com/*", "https://x.com/i/grok*"] }
};

function sget(keys) { return new Promise(r => chrome.storage.local.get(keys, r)); }
function sset(obj)  { return new Promise(r => chrome.storage.local.set(obj, r)); }

// ---- Copy 접두어 제거 (v6.0.2 유지) ----
function cleanCopy(t) {
  if (!t) return "";
  let s = String(t).replace(/\r\n/g, "\n");
  s = s.replace(/^\s*(?:(?:Copy(?: code)?|Copied!?|복사|코드 복사)\s*\n?)+/i, "");
  s = s.split("\n").filter(l =>
    !/^\s*(?:Copy(?: code)?|Copied!?|코드 복사|복사)\s*$/i.test(l) &&
    !/^\s*[\w+#.-]{1,20}\s+Copy(?: code)?\s*$/i.test(l)
  ).join("\n");
  return s.trim();
}

async function getAllRoles() {
  const st = await sget(["omni_custom_roles", "omni_override"]);
  const customs = st.omni_custom_roles || {};
  const ov = st.omni_override || {};
  const list = [];
  for (const [k, v] of Object.entries(BUILTIN_ROLES)) {
    list.push({ key: k, label: v.label, icon: v.icon, custom: false,
                patterns: v.patterns, override: ov[k] || null });
  }
  for (const [k, v] of Object.entries(customs)) {
    let pats = [];
    if (v.origin && /^https?:\/\//.test(v.origin)) pats = [v.origin + "/*"];
    list.push({ key: k, label: v.label, icon: "🧩", custom: true,
                patterns: pats, override: ov[k] || null });
  }
  return list;
}

async function resolveTab(role) {
  if (role.override && role.override.tabId != null) {
    try { const t = await chrome.tabs.get(role.override.tabId); if (t) return t; } catch (e) {}
  }
  if (role.patterns && role.patterns.length) {
    try {
      const tabs = await chrome.tabs.query({ url: role.patterns });
      if (tabs.length) {
        tabs.sort((a, b) => (b.lastAccessed || 0) - (a.lastAccessed || 0));
        return tabs[0];
      }
    } catch (e) {}
  }
  return null;
}

async function getRoleStatus() {
  const roles = await getAllRoles();
  return Promise.all(roles.map(async r => {
    const t = await resolveTab(r);
    return Object.assign({}, r, { alive: !!t, tabId: t ? t.id : null,
      tabTitle: t ? (t.title || "") : "", tabUrl: t ? (t.url || "") : "" });
  }));
}

// ---- 역할 지정 (내장 + ✏️ 직접 쓰기) ----
async function assignRole(roleKey, customName, tab) {
  const st = await sget(["omni_custom_roles", "omni_override"]);
  const customs = st.omni_custom_roles || {};
  const ov = st.omni_override || {};
  let key = roleKey, label;
  if (roleKey === "__custom__") {
    const name = (customName || "").trim();
    if (!name) throw new Error("커스텀 신경망 이름을 입력하세요");
    const exist = Object.entries(customs).find(([k, v]) => v.label === name);
    if (exist) {
      key = exist[0];
    } else {
      const norm = name.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
      key = "custom_" + (norm ? norm + "_" : "") + Date.now().toString(36);
    }
    let origin = "";
    try { origin = new URL(tab.url).origin; } catch (e) {}
    customs[key] = { label: name, icon: "🧩", origin: origin,
                     createdAt: (customs[key] && customs[key].createdAt) || Date.now() };
    label = name;
  } else {
    if (!BUILTIN_ROLES[roleKey]) throw new Error("알 수 없는 역할: " + roleKey);
    label = BUILTIN_ROLES[roleKey].label;
  }
  ov[key] = { tabId: tab.id, windowId: tab.windowId, url: tab.url, title: tab.title, label: label };
  await sset({ omni_custom_roles: customs, omni_override: ov });
  syncRolesToBridge();
  return key;
}

async function removeRole(key) {
  const st = await sget(["omni_custom_roles", "omni_override"]);
  const customs = st.omni_custom_roles || {};
  const ov = st.omni_override || {};
  delete ov[key];
  if (customs[key]) delete customs[key];
  const s = (await sget(["omni_settings"])).omni_settings || {};
  if (Array.isArray(s.checked)) s.checked = s.checked.filter(x => x !== key);
  if (Array.isArray(s.absChecked)) s.absChecked = s.absChecked.filter(x => x !== key);
  await sset({ omni_custom_roles: customs, omni_override: ov, omni_settings: s });
  syncRolesToBridge();
}

async function syncRolesToBridge() {
  try {
    const roles = await getAllRoles();
    await fetch(BRIDGE + "/roles", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: OMNI_VERSION,
        roles: roles.map(r => ({ key: r.key, label: r.label, icon: r.icon, custom: r.custom })) })
    });
  } catch (e) {}
}

// ---- 페이지 주입 함수 (자기완결형) ----
function __omniInject(text, roleKey) {
  const vis = el => el && el.getClientRects().length > 0 && el.getBoundingClientRect().height > 0;
  const sels = {
    claude: ['div.ProseMirror[contenteditable="true"]', '[contenteditable="true"]'],
    gpt:    ['#prompt-textarea', 'div.ProseMirror[contenteditable="true"]', 'textarea'],
    grok:   ['textarea', 'div[contenteditable="true"]']
  };
  const generic = ['#prompt-textarea', 'div.ProseMirror[contenteditable="true"]',
    'textarea:not([readonly])', 'div[contenteditable="true"]', '[role="textbox"]', 'input[type="text"]'];
  const list = (sels[roleKey] || []).concat(generic);
  let box = null;
  for (const s of list) {
    const els = [...document.querySelectorAll(s)].filter(vis);
    if (els.length) { box = els[els.length - 1]; break; }
  }
  if (!box) return { ok: false, err: "입력창을 찾지 못함" };
  box.focus();
  if (box.tagName === "TEXTAREA" || box.tagName === "INPUT") {
    const proto = box.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, "value").set.call(box, text);
    box.dispatchEvent(new Event("input", { bubbles: true }));
    box.dispatchEvent(new Event("change", { bubbles: true }));
  } else {
    document.execCommand("selectAll", false, null);
    document.execCommand("delete", false, null);
    const ok = document.execCommand("insertText", false, text);
    if (!ok || !box.innerText.trim()) {
      box.textContent = text;
      box.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: text }));
    }
  }
  return new Promise(resolve => {
    let tries = 0;
    const sendSels = ['button[data-testid="send-button"]', '#composer-submit-button',
      'button[aria-label="Send message"]', 'button[aria-label="Send Message"]',
      'button[aria-label*="Send"]', 'button[aria-label*="보내기"]', 'button[aria-label*="전송"]',
      'button[aria-label="Submit"]', 'button[type="submit"]'];
    const tick = () => {
      tries++;
      let btn = null;
      for (const s of sendSels) {
        const b = [...document.querySelectorAll(s)].filter(x => vis(x) && !x.disabled &&
          x.getAttribute("aria-disabled") !== "true");
        if (b.length) { btn = b[b.length - 1]; break; }
      }
      if (btn) { btn.click(); resolve({ ok: true, via: "button" }); return; }
      if (tries >= 20) {
        box.dispatchEvent(new KeyboardEvent("keydown",
          { key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true }));
        resolve({ ok: true, via: "enter" }); return;
      }
      setTimeout(tick, 250);
    };
    setTimeout(tick, 350);
  });
}

function __omniAbsorb(roleKey) {
  const sels = {
    claude: ['.font-claude-response', '.font-claude-message'],
    gpt:    ['[data-message-author-role="assistant"]'],
    grok:   ['.message-bubble', '[class*="response-content"]']
  };
  const generic = ['[data-message-author-role="assistant"]', '.markdown', '.prose',
    '[class*="assistant"]', 'article'];
  for (const s of (sels[roleKey] || []).concat(generic)) {
    const els = [...document.querySelectorAll(s)].filter(e => e.innerText && e.innerText.trim().length);
    if (els.length) return { ok: true, text: els[els.length - 1].innerText, sel: s };
  }
  return { ok: false, err: "응답 블록을 찾지 못함" };
}

async function runInTab(tabId, func, args) {
  const res = await chrome.scripting.executeScript({ target: { tabId }, func, args, world: "MAIN" });
  return res && res[0] ? res[0].result : null;
}

function pickRoles(roles, targets) {
  const all = targets === "__all__" || (Array.isArray(targets) && targets.includes("__all__"));
  if (all) return roles;
  const arr = Array.isArray(targets) ? targets : [targets];
  return roles.filter(r => arr.includes(r.key));
}

// ---- 발사 ----
async function omniDispatch(text, targets) {
  const pick = pickRoles(await getAllRoles(), targets);
  const results = await Promise.all(pick.map(async r => {
    const tab = await resolveTab(r);
    if (!tab) return { role: r.key, label: r.label, ok: false, err: "연결된 탭 없음" };
    try {
      const out = await runInTab(tab.id, __omniInject, [text, r.custom ? "generic" : r.key]);
      return { role: r.key, label: r.label, ok: !!(out && out.ok), err: out && out.err, via: out && out.via };
    } catch (e) {
      return { role: r.key, label: r.label, ok: false, err: String(e.message || e) };
    }
  }));
  await sset({ omni_last_dispatch: { ts: Date.now(), results } });
  return results;
}

// ---- 흡수 ----
async function omniAbsorb(targets) {
  const pick = pickRoles(await getAllRoles(), targets);
  const st = await sget(["omni_settings", "omni_absorbed"]);
  const settings = st.omni_settings || {};
  let box = settings.autoCleanAbs ? [] : (st.omni_absorbed || []);
  const results = await Promise.all(pick.map(async r => {
    const tab = await resolveTab(r);
    if (!tab) return { role: r.key, label: r.label, icon: r.icon, ok: false, err: "연결된 탭 없음" };
    try {
      const out = await runInTab(tab.id, __omniAbsorb, [r.custom ? "generic" : r.key]);
      if (out && out.ok) return { role: r.key, label: r.label, icon: r.icon, ok: true, text: cleanCopy(out.text) };
      return { role: r.key, label: r.label, icon: r.icon, ok: false, err: out && out.err };
    } catch (e) {
      return { role: r.key, label: r.label, icon: r.icon, ok: false, err: String(e.message || e) };
    }
  }));
  for (const x of results) {
    if (x.ok && x.text) {
      box.unshift({ id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
        role: x.role, label: x.label, icon: x.icon, text: x.text, ts: Date.now() });
    }
  }
  box = box.slice(0, 200);
  await sset({ omni_absorbed: box });
  return { results, absorbed: box };
}
'''

# =====================================================================
# background.js
# =====================================================================
BACKGROUND_JS = r'''// RGON Omni-Link background v__OMNI_VERSION__
importScripts("core.js");

function boot() {
  chrome.alarms.create("omni_keepalive", { periodInMinutes: 0.5 });
  syncRolesToBridge();
}
chrome.runtime.onInstalled.addListener(boot);
chrome.runtime.onStartup.addListener(boot);
chrome.alarms.onAlarm.addListener(a => { if (a.name === "omni_keepalive") pollBridge(); });

let polling = false;
async function pollBridge() {
  if (polling) return;
  polling = true;
  try {
    const r = await fetch(BRIDGE + "/poll", { cache: "no-store" });
    if (r.ok) {
      const data = await r.json();
      for (const job of (data.jobs || [])) await handleJob(job);
    }
  } catch (e) {} finally { polling = false; }
}

async function handleJob(job) {
  let result = {};
  try {
    if (job.type === "dispatch") result = await omniDispatch(job.text || "", job.targets || ["claude", "gpt"]);
    else if (job.type === "absorb") result = (await omniAbsorb(job.targets || "__all__")).results;
    else if (job.type === "roles") { await syncRolesToBridge(); result = { ok: true }; }
  } catch (e) { result = { ok: false, err: String(e.message || e) }; }
  try {
    await fetch(BRIDGE + "/result", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: job.id, type: job.type, result }) });
  } catch (e) {}
}
setInterval(pollBridge, 1500);

chrome.runtime.onMessage.addListener((msg, sender, send) => {
  (async () => {
    try {
      switch (msg.cmd) {
        case "dispatch": send({ ok: true, results: await omniDispatch(msg.text, msg.targets) }); break;
        case "absorb":   { const r = await omniAbsorb(msg.targets); send({ ok: true, results: r.results }); break; }
        case "roles":    send({ ok: true, roles: await getRoleStatus() }); break;
        case "sync":     await syncRolesToBridge(); send({ ok: true }); break;
        default: send({ ok: false, err: "unknown cmd" });
      }
    } catch (e) { send({ ok: false, err: String(e.message || e) }); }
  })();
  return true;
});
'''

# =====================================================================
# popup.html
# =====================================================================
POPUP_HTML = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>RGON Omni-Link v__OMNI_VERSION__</title>
<style>
body{width:440px;margin:0;font-family:"Malgun Gothic","Segoe UI",sans-serif;background:#0d1117;color:#e6edf3;font-size:13px}
header{padding:8px 10px;background:#161b22;display:flex;justify-content:space-between;align-items:center;gap:6px}
.tabs{display:flex;border-bottom:1px solid #30363d}
.tabs button{flex:1;background:#161b22;color:#c9d1d9;border:0;border-radius:0;padding:8px;cursor:pointer}
.tabs button.on{background:#1f6feb;color:#fff}
.pane{display:none;padding:10px}.pane.on{display:block}
button{background:#21262d;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:5px 8px;cursor:pointer;font-size:12px}
button:hover{background:#30363d}
button.pri{background:#238636;border-color:#2ea043}
button.warn{background:#5a2323;border-color:#a33}
select,input[type=text],textarea{width:100%;box-sizing:border-box;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;font-size:12px}
textarea{height:120px;resize:vertical}
.row{display:flex;gap:6px;align-items:center;margin:6px 0;flex-wrap:wrap}
.lamp{display:flex;justify-content:space-between;align-items:center;padding:5px;border-bottom:1px solid #21262d;gap:6px}
.lamp small{color:#8b949e}
.tgt{display:flex;justify-content:space-between;align-items:center;padding:4px 6px;background:#161b22;border-radius:6px;margin:4px 0;gap:6px}
.tgt label{flex:1;cursor:pointer}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:6px;margin:6px 0}
.card pre{white-space:pre-wrap;word-break:break-word;max-height:160px;overflow:auto;margin:4px 0;font-size:12px;font-family:Consolas,monospace}
.sub{color:#8b949e;font-size:11px;margin:8px 0 2px}
#status{font-size:11px;color:#8b949e;padding:4px 10px 8px;min-height:16px}
.hide{display:none!important}
hr{border:0;border-top:1px solid #30363d;margin:8px 0}
</style></head>
<body>
<header><b>🛰️ RGON Omni-Link Hub</b><span id="ver"></span><span id="bridgeLamp">⚪ Bridge</span></header>
<div class="tabs">
  <button data-pane="neural" class="on">📡 신경망</button>
  <button data-pane="dispatch">⚡ 작업 분배</button>
  <button data-pane="absorb">🧲 흡수기</button>
</div>

<!-- 📡 신경망 -->
<section id="neural" class="pane on">
  <div class="sub">신경망 램프</div>
  <div id="lamps"></div>
  <hr>
  <div class="sub">역할 지정 (선택한 탭 ← 역할)</div>
  <div class="row"><select id="tabSel"></select></div>
  <div class="row" style="flex-wrap:nowrap">
    <select id="roleSel">
      <option value="claude">🧠 Claude</option>
      <option value="gpt">⚡ GPT</option>
      <option value="grok">🎯 Grok</option>
      <option value="__custom__">✏️ 직접 쓰기 (이름 직접 입력)</option>
    </select>
    <button id="assignRole" class="pri" style="white-space:nowrap">지정</button>
  </div>
  <div class="row hide" id="customRow">
    <input type="text" id="customRoleName" placeholder="새 신경망 이름 입력 (예: Claude Sonnet 5.5, Suno, Perplexity)">
  </div>
</section>

<!-- ⚡ 작업 분배 -->
<section id="dispatch" class="pane">
  <textarea id="prompt" placeholder="발사할 작업 지시를 입력하세요..."></textarea>
  <div class="row">
    <button id="clearPrompt">🗑️ 전체 지우기</button>
    <button id="pastePrompt">📋 새로 붙여넣기</button>
    <label><input type="checkbox" id="autoclear"> 발사 후 자동 지우기</label>
  </div>
  <div class="row">
    <button id="selAllTargets">☑️ 전체 선택</button>
    <button id="unselAllTargets">☐ 전체 해제</button>
  </div>
  <div id="targets">
    <div class="tgt"><label><input type="checkbox" class="tgt-chk" value="claude" checked> 🧠 Claude</label><span data-lamp="claude"></span><button data-solo="claude">🧠 Claude 단독 발사</button></div>
    <div class="tgt"><label><input type="checkbox" class="tgt-chk" value="gpt" checked> ⚡ GPT</label><span data-lamp="gpt"></span><button data-solo="gpt">⚡ GPT 단독 발사</button></div>
    <div class="tgt"><label><input type="checkbox" class="tgt-chk" value="grok"> 🎯 Grok</label><span data-lamp="grok"></span><button data-solo="grok">🎯 Grok 단독 발사</button></div>
    <div id="customTargets"></div>
  </div>
  <div class="row">
    <button id="fireChecked" class="pri">🚀 체크한 대상만 발사</button>
    <button id="fireAll" class="pri">🌐 전체 선택 발사</button>
  </div>
  <div id="fireLog" style="font-size:12px"></div>
</section>

<!-- 🧲 흡수기 -->
<section id="absorb" class="pane">
  <div class="row">
    <button id="absSelAll">☑️ 전체 선택</button>
    <button id="absUnselAll">☐ 전체 해제</button>
  </div>
  <div id="absTargets"></div>
  <div class="row">
    <button id="doAbsorb" class="pri">🧲 선택 대상 수거</button>
    <button id="doAbsorbAll">🌐 전체 수거</button>
  </div>
  <div class="row"><label><input type="checkbox" id="autoCleanAbs"> 자동 삭제 ON (수거 전 기존 흡수함 비우기)</label></div>
  <div class="row">
    <button id="clearAbs" class="warn">🗑️ 흡수함 전체 비우기</button>
    <button id="copyAllAbs">📋 전체 복사</button>
  </div>
  <div id="cards"></div>
</section>

<div id="status"></div>
<script src="core.js"></script>
<script src="popup.js"></script>
</body></html>
'''

# =====================================================================
# popup.js
# =====================================================================
POPUP_JS = r'''// RGON Omni-Link popup v__OMNI_VERSION__
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
function status(m) { $("#status").textContent = m; }
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g,
  c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function send(msg) {
  return new Promise(r => chrome.runtime.sendMessage(msg, resp =>
    r(resp || { ok: false, err: (chrome.runtime.lastError && chrome.runtime.lastError.message) || "no response" })));
}
async function getSettings() { return (await sget(["omni_settings"])).omni_settings || {}; }
async function patchSettings(p) { const s = await getSettings(); Object.assign(s, p); await sset({ omni_settings: s }); return s; }

$("#ver").textContent = "v" + OMNI_VERSION;

function showPane(name) {

  $$(".tabs button").forEach(x => x.classList.toggle("on", x.dataset.pane === name));

  $$(".pane").forEach(p => p.classList.toggle("on", p.id === name));
  if (name === "absorb") renderCards();
}

$$(".tabs button").forEach(b => b.onclick = () => showPane(b.dataset.pane));

// ================= 📡 신경망 =================
let ROLES = [];

async function loadTabs() {
  const tabs = await chrome.tabs.query({});
  const [cur] = await chrome.tabs.query({ active: true, currentWindow: true });
  const sel = $("#tabSel"); sel.innerHTML = "";
  tabs.filter(t => /^https?:/.test(t.url || "")).forEach(t => {
    const o = document.createElement("option");
    o.value = t.id;
    const isCur = cur && t.id === cur.id;
    o.textContent = (isCur ? "▶ 현재 탭: " : "") + (t.title || t.url).slice(0, 60);
    if (isCur) o.selected = true;
    sel.appendChild(o);
  });
  if (!sel.options.length) {
    const o = document.createElement("option"); o.value = ""; o.textContent = "(지정 가능한 http/https 탭 없음)";
    sel.appendChild(o);
  }
}

$("#roleSel").onchange = () => {
  const c = $("#roleSel").value === "__custom__";
  $("#customRow").classList.toggle("hide", !c);
  if (c) $("#customRoleName").focus();
};

$("#assignRole").onclick = async () => {
  try {
    const tabId = parseInt($("#tabSel").value, 10);
    if (!tabId) throw new Error("지정할 탭이 없습니다");
    const tab = await chrome.tabs.get(tabId);
    const role = $("#roleSel").value;
    const name = $("#customRoleName").value.trim();
    const key = await assignRole(role, name, tab);
    if (role === "__custom__") {
      const s = await getSettings();
      const ch = Array.isArray(s.checked) ? s.checked : currentChecked();
      if (!ch.includes(key)) ch.push(key);
      const ab = Array.isArray(s.absChecked) ? s.absChecked : null;
      if (ab && !ab.includes(key)) ab.push(key);
      await patchSettings({ checked: ch, absChecked: ab || undefined });
      $("#customRoleName").value = "";
      status("✅ 🧩 커스텀 신경망 등록: " + name + " (" + key + ")");
    } else {
      status("✅ 지정 완료: " + key + " ← " + (tab.title || tab.url));
    }
    await refreshAll();
  } catch (e) { status("❌ " + e.message); }
};
$("#customRoleName").addEventListener("keydown", e => { if (e.key === "Enter") $("#assignRole").click(); });

async function refreshRoles() {
  const r = await send({ cmd: "roles" });
  ROLES = r.ok ? r.roles : await getRoleStatus();
}

function renderLamps() {
  const box = $("#lamps"); box.innerHTML = "";
  ROLES.forEach(r => {
    const d = document.createElement("div"); d.className = "lamp";
    d.innerHTML = `<span>${r.alive ? "🟢" : "🔴"} ${esc(r.icon)} ${esc(r.label)} <small>${esc((r.tabTitle || "").slice(0, 26))}</small></span>
      <span style="white-space:nowrap"><button data-go="${esc(r.key)}">이동</button>
      <button class="warn" data-del="${esc(r.key)}">✕ 역할 삭제</button></span>`;
    box.appendChild(d);
  });
  box.querySelectorAll("[data-go]").forEach(b => b.onclick = () => goRole(b.dataset.go));
  box.querySelectorAll("[data-del]").forEach(b => b.onclick = async () => {
    const r = ROLES.find(x => x.key === b.dataset.del);
    if (r && r.custom && !confirm(`'${r.label}' 커스텀 신경망을 삭제할까요?`)) return;
    await removeRole(b.dataset.del);
    status("🗑️ 역할 삭제: " + (r ? r.label : b.dataset.del));
    await refreshAll();
  });
}

async function goRole(key) {
  const r = ROLES.find(x => x.key === key);
  const t = r && await resolveTab(r);
  if (!t) { status("🔴 연결된 탭 없음: " + (r ? r.label : key)); return; }
  await chrome.tabs.update(t.id, { active: true });
  await chrome.windows.update(t.windowId, { focused: true });
}

// ================= ⚡ 작업 분배 =================
function currentChecked() { return $$(".tgt-chk").filter(c => c.checked).map(c => c.value); }
async function saveChecked() { await patchSettings({ checked: currentChecked() }); }

function renderTargets(checked) {
  const box = $("#customTargets"); box.innerHTML = "";
  ROLES.filter(r => r.custom).forEach(r => {
    const d = document.createElement("div"); d.className = "tgt";
    d.innerHTML = `<label><input type="checkbox" class="tgt-chk" value="${esc(r.key)}"> 🧩 ${esc(r.label)}</label>
      <span>${r.alive ? "🟢" : "🔴"}</span>
      <button data-solo="${esc(r.key)}">🧩 ${esc(r.label)} 단독 발사</button>`;
    box.appendChild(d);
  });
  if (Array.isArray(checked)) $$(".tgt-chk").forEach(c => c.checked = checked.includes(c.value));

  $$(".tgt-chk").forEach(c => c.onchange = saveChecked);

  $$("[data-solo]").forEach(b => b.onclick = () => {
    const r = ROLES.find(x => x.key === b.dataset.solo);
    fire([b.dataset.solo], (r ? r.label : b.dataset.solo) + " 단독");
  });
  ROLES.filter(r => !r.custom).forEach(r => {
    const s = document.querySelector(`[data-lamp="${r.key}"]`);
    if (s) s.textContent = r.alive ? "🟢" : "🔴";
  });
}

$("#selAllTargets").onclick = () => { $$(".tgt-chk").forEach(c => c.checked = true); saveChecked(); };
$("#unselAllTargets").onclick = () => { $$(".tgt-chk").forEach(c => c.checked = false); saveChecked(); };
$("#fireChecked").onclick = () => fire(currentChecked(), "체크 선택");
$("#fireAll").onclick = () => fire("__all__", "🌐 전체");

async function saveDraft() { await sset({ omni_draft: $("#prompt").value }); }
$("#prompt").addEventListener("input", saveDraft);
$("#clearPrompt").onclick = async () => { $("#prompt").value = ""; await saveDraft(); status("🗑️ 입력창 전체 지움"); $("#prompt").focus(); };
$("#pastePrompt").onclick = async () => {
  try {
    const t = await navigator.clipboard.readText();
    $("#prompt").value = cleanCopy(t);
    await saveDraft();
    status("📋 클립보드 새로 붙여넣기 완료 (" + $("#prompt").value.length + "자)");
  } catch (e) { status("❌ 클립보드 읽기 실패: " + e.message); }
};
$("#autoclear").onchange = () => patchSettings({ autoclear: $("#autoclear").checked });

async function fire(targets, mode) {
  const text = $("#prompt").value;
  if (!text.trim()) { status("⚠️ 발사할 내용이 비어 있습니다"); return; }
  if (Array.isArray(targets) && !targets.length) { status("⚠️ 체크된 대상이 없습니다"); return; }
  status(`🚀 ${mode} 발사 중...`);
  const r = await send({ cmd: "dispatch", text, targets });
  if (!r.ok) { status("❌ " + r.err); return; }
  $("#fireLog").innerHTML = r.results.map(x =>
    `<div>${x.ok ? "✅" : "❌"} ${esc(x.label)} ${x.ok ? "(" + esc(x.via || "") + ")" : esc(x.err || "")}</div>`
  ).join("") || "<div>대상 없음</div>";
  status(`${mode} 발사 완료: ${r.results.filter(x => x.ok).length}/${r.results.length}`);
  const s = await getSettings();
  if (s.autoclear) { $("#prompt").value = ""; await saveDraft(); }
}

// ================= 🧲 흡수기 =================
function absChecked() { return $$(".abs-chk").filter(c => c.checked).map(c => c.value); }

function renderAbsTargets(saved) {
  const box = $("#absTargets"); box.innerHTML = "";
  ROLES.forEach(r => {
    const d = document.createElement("div"); d.className = "tgt";
    const on = Array.isArray(saved) ? saved.includes(r.key) : true;
    d.innerHTML = `<label><input type="checkbox" class="abs-chk" value="${esc(r.key)}" ${on ? "checked" : ""}>
      ${r.alive ? "🟢" : "🔴"} ${esc(r.icon)} ${esc(r.label)}</label>`;
    box.appendChild(d);
  });

  $$(".abs-chk").forEach(c => c.onchange = () => patchSettings({ absChecked: absChecked() }));
}
$("#absSelAll").onclick = () => { $$(".abs-chk").forEach(c => c.checked = true); patchSettings({ absChecked: absChecked() }); };
$("#absUnselAll").onclick = () => { $$(".abs-chk").forEach(c => c.checked = false); patchSettings({ absChecked: absChecked() }); };

async function absorb(targets, mode) {
  if (Array.isArray(targets) && !targets.length) { status("⚠️ 수거 대상이 없습니다"); return; }
  status(`🧲 ${mode} 수거 중...`);
  const r = await send({ cmd: "absorb", targets });
  if (!r.ok) { status("❌ " + r.err); return; }
  const fails = r.results.filter(x => !x.ok).map(x => x.label + ":" + (x.err || "실패"));
  status(`🧲 수거 완료 ${r.results.filter(x => x.ok).length}/${r.results.length}` + (fails.length ? " | " + fails.join(", ") : ""));
  renderCards();
}
$("#doAbsorb").onclick = () => absorb(absChecked(), "선택");
$("#doAbsorbAll").onclick = () => absorb("__all__", "전체");
$("#autoCleanAbs").onchange = () => {
  patchSettings({ autoCleanAbs: $("#autoCleanAbs").checked });
  status("자동 삭제 " + ($("#autoCleanAbs").checked ? "ON" : "OFF"));
};
$("#clearAbs").onclick = async () => {
  if (!confirm("흡수함을 전체 비울까요?")) return;
  await sset({ omni_absorbed: [] }); renderCards(); status("🗑️ 흡수함 전체 비움");
};
$("#copyAllAbs").onclick = async () => {
  const { omni_absorbed = [] } = await sget(["omni_absorbed"]);
  const txt = omni_absorbed.map(c => `[${c.label}]\n${c.text}`).join("\n\n----------\n\n");
  try { await navigator.clipboard.writeText(txt); status("📋 전체 복사 완료 (" + omni_absorbed.length + "건)"); }
  catch (e) { status("❌ 복사 실패: " + e.message); }
};

async function renderCards() {
  const { omni_absorbed = [] } = await sget(["omni_absorbed"]);
  const box = $("#cards");
  if (!omni_absorbed.length) { box.innerHTML = '<div style="color:#8b949e">흡수함이 비어 있습니다</div>'; return; }
  box.innerHTML = "";
  omni_absorbed.forEach(c => {
    const d = document.createElement("div"); d.className = "card";
    d.innerHTML = `<div class="row" style="justify-content:space-between"><b>${esc(c.icon || "🧩")} ${esc(c.label)}</b>
      <small>${new Date(c.ts).toLocaleString()}</small></div>
      <pre>${esc(c.text)}</pre>
      <div class="row"><button data-cp="${esc(c.id)}">📋 복사</button>
      <button data-tp="${esc(c.id)}">⚡ 분배창으로</button>
      <button class="warn" data-rm="${esc(c.id)}">✕ 삭제</button></div>`;
    box.appendChild(d);
  });
  const find = id => omni_absorbed.find(x => x.id === id);
  box.querySelectorAll("[data-cp]").forEach(b => b.onclick = async () => {
    const c = find(b.dataset.cp); if (!c) return;
    await navigator.clipboard.writeText(c.text); status("📋 복사: " + c.label);
  });
  box.querySelectorAll("[data-tp]").forEach(b => b.onclick = async () => {
    const c = find(b.dataset.tp); if (!c) return;
    $("#prompt").value = c.text; await saveDraft(); showPane("dispatch"); status("⚡ 분배창으로 이동: " + c.label);
  });
  box.querySelectorAll("[data-rm]").forEach(b => b.onclick = async () => {
    const { omni_absorbed: cur = [] } = await sget(["omni_absorbed"]);
    await sset({ omni_absorbed: cur.filter(x => x.id !== b.dataset.rm) });
    renderCards(); status("✕ 카드 삭제");
  });
}

chrome.storage.onChanged.addListener((ch, area) => {
  if (area === "local" && ch.omni_absorbed && $("#absorb").classList.contains("on")) renderCards();
});

// ================= 공통 =================
async function checkBridge() {
  try {
    const r = await fetch(BRIDGE + "/health", { cache: "no-store" });
    const j = await r.json();
    $("#bridgeLamp").textContent = (r.status === 200 ? "🟢" : "🟡") + " Bridge " + (j.version || "");
  } catch (e) { $("#bridgeLamp").textContent = "🔴 Bridge"; }
}

async function refreshAll() {
  await refreshRoles();
  renderLamps();
  const s = await getSettings();
  renderTargets(s.checked);
  renderAbsTargets(s.absChecked);
}

(async () => {
  const s = await getSettings();
  $("#autoclear").checked = !!s.autoclear;
  $("#autoCleanAbs").checked = !!s.autoCleanAbs;
  const { omni_draft = "" } = await sget(["omni_draft"]);
  $("#prompt").value = omni_draft;
  await loadTabs();
  await refreshAll();
  renderCards();
  checkBridge();
  send({ cmd: "sync" });
})();
'''

# =====================================================================
# 로컬 브리지 (8765)
# =====================================================================
BRIDGE_CODE = r'''# -*- coding: utf-8 -*-
# RGON Omni-Link Local Bridge v__OMNI_VERSION__ (port __PORT__)
import os, json, time, threading, itertools
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

VERSION = "__OMNI_VERSION__"
PORT = __PORT__
BASE = os.path.dirname(os.path.abspath(__file__))
ROLES_FILE = os.path.join(BASE, "omni_roles.json")
PID_FILE = os.path.join(BASE, "omni_bridge.pid")

LOCK = threading.Lock()
JOBS = []
RESULTS = {}
COUNTER = itertools.count(int(time.time()) % 1000000)
ROLES = {"roles": [
    {"key": "claude", "label": "Claude", "icon": "🧠", "custom": False},
    {"key": "gpt", "label": "GPT", "icon": "⚡", "custom": False},
    {"key": "grok", "label": "Grok", "icon": "🎯", "custom": False},
]}
try:
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        _r = json.load(f)
        if isinstance(_r, dict) and isinstance(_r.get("roles"), list):
            ROLES = _r
except Exception:
    pass


class H(BaseHTTPRequestHandler):
    server_version = "OmniBridge/" + VERSION

    def log_message(self, *a):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/health"):
            return self._json({"ok": True, "service": "omni-bridge", "version": VERSION,
                               "queued": len(JOBS), "port": PORT})
        if u.path == "/poll":
            with LOCK:
                jobs = JOBS[:]
                JOBS.clear()
            return self._json({"ok": True, "jobs": jobs})
        if u.path == "/result":
            jid = (q.get("id") or [""])[0]
            with LOCK:
                has = jid in RESULTS
                r = RESULTS.get(jid)
            return self._json({"ok": True, "done": has, "result": r})
        if u.path == "/roles":
            return self._json({"ok": True, "roles": ROLES.get("roles", [])})
        return self._json({"ok": False, "err": "not found"}, 404)

    def do_POST(self):
        global ROLES
        u = urlparse(self.path)
        d = self._body()
        if u.path in ("/dispatch", "/absorb"):
            jid = str(next(COUNTER))
            job = {"id": jid, "type": u.path[1:], "text": d.get("text", ""),
                   "targets": d.get("targets") or (["claude", "gpt"] if u.path == "/dispatch" else "__all__"),
                   "ts": time.time()}
            with LOCK:
                JOBS.append(job)
            return self._json({"ok": True, "id": jid})
        if u.path == "/result":
            with LOCK:
                RESULTS[str(d.get("id"))] = d.get("result")
                if len(RESULTS) > 300:
                    for k in list(RESULTS)[:100]:
                        RESULTS.pop(k, None)
            return self._json({"ok": True})
        if u.path == "/roles":
            if isinstance(d.get("roles"), list):
                ROLES = {"roles": d["roles"], "version": d.get("version", ""), "ts": time.time()}
                try:
                    with open(ROLES_FILE, "w", encoding="utf-8") as f:
                        json.dump(ROLES, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass
            return self._json({"ok": True})
        if u.path == "/shutdown":
            self._json({"ok": True, "msg": "shutting down"})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        return self._json({"ok": False, "err": "not found"}, 404)


if __name__ == "__main__":
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    srv.daemon_threads = True
    print("[OmniBridge] v%s listening on 127.0.0.1:%d" % (VERSION, PORT), flush=True)
    try:
        srv.serve_forever()
    finally:
        srv.server_close()
'''

# =====================================================================
# 독대실 HTML_BLOCK
# =====================================================================
HTML_START = "<!-- OMNI-LINK-CTRL-START v__OMNI_VERSION__ -->"
HTML_END = "<!-- OMNI-LINK-CTRL-END -->"
HTML_BLOCK = r'''<!-- OMNI-LINK-CTRL-START v__OMNI_VERSION__ -->
<div id="omniCtrl" style="font-family:'Malgun Gothic',sans-serif;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:10px;padding:8px 10px;margin:6px;font-size:13px">
  <style>
    #omniCtrl button{background:#21262d;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:12px;margin:2px}
    #omniCtrl button:hover{background:#30363d}
    #omniCtrl .pri{background:#238636;border-color:#2ea043}
    #omniCtrl label{margin-right:8px;cursor:pointer}
    #omniCtrl textarea{width:100%;box-sizing:border-box;height:60px;background:#010409;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px}
  </style>
  <div style="display:flex;justify-content:space-between;align-items:center">
    <b>🛰️ Omni-Link 분배 컨트롤러 v__OMNI_VERSION__</b><span id="omniBridge">⚪ 8765</span>
  </div>
  <textarea id="omniPrompt" placeholder="발사할 내용 (비우면 독대실 입력창 내용 사용)"></textarea>
  <div>
    <label><input type="checkbox" class="omni-chk" value="claude" checked> 🧠 Claude</label>
    <label><input type="checkbox" class="omni-chk" value="gpt" checked> ⚡ GPT</label>
    <label><input type="checkbox" class="omni-chk" value="grok"> 🎯 Grok</label>
    <span id="omniCustom"></span>
  </div>
  <div>
    <button id="omniSelAll">☑️ 전체 선택</button>
    <button id="omniUnselAll">☐ 전체 해제</button>
    <button data-omni-solo="claude">🧠 Claude 단독</button>
    <button data-omni-solo="gpt">⚡ GPT 단독</button>
    <button data-omni-solo="grok">🎯 Grok 단독</button>
    <span id="omniCustomSolo"></span>
  </div>
  <div>
    <button id="omniFireChecked" class="pri">🚀 체크 선택 발사</button>
    <button id="omniFireAll" class="pri">🌐 전체 발사</button>
    <button id="omniClear">🗑️ 전체 지우기</button>
    <label><input type="checkbox" id="omniAutoClear"> 발사 후 자동 지우기</label>
  </div>
  <div id="omniLog" style="font-size:12px;color:#8b949e;min-height:16px"></div>
  <script>
  (function(){
    var BR = "http://127.0.0.1:__PORT__";
    var $ = function(id){ return document.getElementById(id); };
    var root = $("omniCtrl");
    function esc(s){ return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];}); }
    function log(m){ $("omniLog").textContent = m; }
    function getText(){
      var t = $("omniPrompt").value;
      if(!t.trim()){
        var alt = document.querySelector("textarea:not(#omniPrompt), #userInput, #input");
        if(alt) t = alt.value || alt.innerText || "";
      }
      return t;
    }
    function checked(){ return Array.prototype.slice.call(root.querySelectorAll(".omni-chk:checked")).map(function(c){return c.value;}); }
    async function waitResult(id, label){
      for(var i=0;i<40;i++){
        await new Promise(function(r){setTimeout(r,1000);});
        try{
          var j = await (await fetch(BR+"/result?id="+encodeURIComponent(id))).json();
          if(j.done){
            var rs = Array.isArray(j.result) ? j.result : [];
            log(label+" 결과: "+(rs.map(function(x){return (x.ok?"✅":"❌")+x.label+(x.ok?"":"("+(x.err||"")+")");}).join("  ")||"대상 없음"));
            return;
          }
        }catch(e){}
      }
      log("⏱️ "+label+": 확장 응답 대기 시간 초과 (Omni-Link 확장이 켜져 있는지 확인)");
    }
    async function fire(targets, label){
      var text = getText();
      if(!text.trim()){ log("⚠️ 발사할 내용이 없습니다"); return; }
      if(Array.isArray(targets) && !targets.length){ log("⚠️ 체크된 대상이 없습니다"); return; }
      try{
        var r = await fetch(BR+"/dispatch",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:text,targets:targets})});
        var j = await r.json();
        log("🚀 "+label+" 발사 접수 (#"+j.id+") → 확장 전달 대기...");
        if($("omniAutoClear").checked) $("omniPrompt").value = "";
        waitResult(j.id, label);
      }catch(e){ log("❌ 브리지(__PORT__) 연결 실패: "+e.message); }
    }
    $("omniSelAll").onclick = function(){ root.querySelectorAll(".omni-chk").forEach(function(c){c.checked=true;}); };
    $("omniUnselAll").onclick = function(){ root.querySelectorAll(".omni-chk").forEach(function(c){c.checked=false;}); };
    $("omniFireChecked").onclick = function(){ fire(checked(), "체크 선택"); };
    $("omniFireAll").onclick = function(){ fire("__all__", "🌐 전체"); };
    $("omniClear").onclick = function(){ $("omniPrompt").value = ""; log("🗑️ 지움"); };
    root.addEventListener("click", function(e){
      var b = e.target.closest("[data-omni-solo]");
      if(b) fire([b.getAttribute("data-omni-solo")], b.textContent.trim());
    });
    async function loadRoles(){
      try{
        var j = await (await fetch(BR+"/roles",{cache:"no-store"})).json();
        var prev = checked();
        var cs = (j.roles||[]).filter(function(r){return r.custom;});
        $("omniCustom").innerHTML = cs.map(function(r){
          return '<label><input type="checkbox" class="omni-chk" value="'+esc(r.key)+'"'+(prev.indexOf(r.key)>=0?" checked":"")+'> 🧩 '+esc(r.label)+'</label>';
        }).join("");
        $("omniCustomSolo").innerHTML = cs.map(function(r){
          return '<button data-omni-solo="'+esc(r.key)+'">🧩 '+esc(r.label)+' 단독</button>';
        }).join("");
        $("omniBridge").textContent = "🟢 8765";
      }catch(e){ $("omniBridge").textContent = "🔴 8765"; }
    }
    loadRoles(); setInterval(loadRoles, 15000);
  })();
  </script>
</div>
<!-- OMNI-LINK-CTRL-END -->'''


# =====================================================================
# 유틸
# =====================================================================
def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"  ✍️  {path.relative_to(BASE) if BASE in path.parents else path}  ({len(content):,} bytes)")


def backup():
    BACKUP_DIR.mkdir(exist_ok=True)
    if EXT_DIR.exists():
        dst = BACKUP_DIR / f"{EXT_DIR.name}_pre_v603_{STAMP}"
        shutil.copytree(EXT_DIR, dst)
        print(f"  📦 확장 백업: {dst}")
    for f in (BRIDGE_PY, CHAT_HTML):
        if f.exists():
            dst = BACKUP_DIR / f"{f.stem}_pre_v603_{STAMP}{f.suffix}"
            shutil.copy2(f, dst)
            print(f"  📦 백업: {dst}")


def install_extension():
    EXT_DIR.mkdir(parents=True, exist_ok=True)
    write(EXT_DIR / "manifest.json", json.dumps(MANIFEST, ensure_ascii=False, indent=2))
    write(EXT_DIR / "core.js", fill(CORE_JS))
    write(EXT_DIR / "background.js", fill(BACKGROUND_JS))
    write(EXT_DIR / "popup.html", fill(POPUP_HTML))
    write(EXT_DIR / "popup.js", fill(POPUP_JS))
    write(EXT_DIR / "omni_version.json", json.dumps(
        {"version": OMNI_VERSION, "installed": STAMP, "bridge_port": BRIDGE_PORT}, indent=2))


def patch_chat_html():
    block = fill(HTML_BLOCK)
    if CHAT_HTML.exists():
        raw = CHAT_HTML.read_bytes()
        try:
            html = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            html = raw.decode("cp949", errors="replace")
        html = re.sub(r"<!--\s*OMNI[-_ ]?LINK[^>]*START[^>]*-->.*?<!--\s*OMNI[-_ ]?LINK[^>]*END[^>]*-->\s*",
                      "", html, flags=re.S | re.I)
        m = re.search(r"<body[^>]*>", html, flags=re.I)
        if m:
            html = html[:m.end()] + "\n" + block + "\n" + html[m.end():]
        else:
            html = block + "\n" + html
    else:
        html = ("<!doctype html>\n<html lang=\"ko\"><head><meta charset=\"utf-8\">"
                "<title>RGON Alpha 독대실</title></head>\n<body style=\"background:#010409;margin:0\">\n"
                + block + "\n</body></html>\n")
    write(CHAT_HTML, html)


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def graceful_shutdown():
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{BRIDGE_PORT}/shutdown", data=b"{}",
                                     headers={"Content-Type": "application/json"}, method="POST")
        _opener().open(req, timeout=2).read()
        print("  🔻 기존 브리지 graceful shutdown 요청 완료")
        time.sleep(1.0)
    except Exception:
        pass


def kill_port(port: int):
    pids = set()
    if os.name == "nt":
        try:
            out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True,
                                 text=True, errors="ignore").stdout
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[1].endswith(f":{port}") and parts[4].isdigit():
                    pids.add(parts[4])
        except Exception as e:
            print(f"  ⚠️ netstat 실패: {e}")
        for pid in pids:
            if pid not in ("0", str(os.getpid())):
                subprocess.run(["taskkill", "/PID", pid, "/F", "/T"], capture_output=True)
                print(f"  🔪 포트 {port} 점유 프로세스 종료: PID {pid}")
    else:
        try:
            out = subprocess.run(["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True).stdout
            for pid in out.split():
                subprocess.run(["kill", "-9", pid], capture_output=True)
                print(f"  🔪 포트 {port} 점유 프로세스 종료: PID {pid}")
        except Exception:
            pass
    time.sleep(0.8)


def start_bridge():
    py = Path(sys.executable)
    log = open(BASE / "omni_bridge.log", "a", encoding="utf-8")
    if os.name == "nt":
        pyw = py.with_name("pythonw.exe")
        exe = str(pyw if pyw.exists() else py)
        flags = 0x00000008 | 0x00000200 | 0x08000000  # DETACHED | NEW_GROUP | NO_WINDOW
        subprocess.Popen([exe, str(BRIDGE_PY)], cwd=str(BASE), stdout=log, stderr=log,
                         stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
    else:
        subprocess.Popen([str(py), str(BRIDGE_PY)], cwd=str(BASE), stdout=log, stderr=log,
                         stdin=subprocess.DEVNULL, start_new_session=True, close_fds=True)
    print("  🚀 브리지 백그라운드 기동 요청")


def verify_bridge(timeout=20):
    url = f"http://127.0.0.1:{BRIDGE_PORT}/health"
    end = time.time() + timeout
    last = None
    while time.time() < end:
        try:
            with _opener().open(url, timeout=2) as r:
                body = json.loads(r.read().decode("utf-8"))
                if r.status == 200:
                    return True, body
        except Exception as e:
            last = e
        time.sleep(0.5)
    return False, last


# =====================================================================
# MAIN
# =====================================================================
def main():
    print("=" * 66)
    print(f"  🛰️  RGON Omni-Link Hub 업그레이드 → v{OMNI_VERSION}")
    print("=" * 66)
    print(f"  📁 BASE     : {BASE}")
    print(f"  🧩 EXT_DIR  : {EXT_DIR}")
    print(f"  📜 v6.0.2   : {'발견' if PREV_SCRIPT.exists() else '미발견 (신규 생성 모드)'}")

    print("\n[1/5] 백업")
    backup()

    print("\n[2/5] 크롬 확장 파일 설치")
    install_extension()

    print("\n[3/5] 로컬 브리지 작성")
    write(BRIDGE_PY, fill(BRIDGE_CODE))

    print("\n[4/5] 독대실 HTML_BLOCK 패치")
    patch_chat_html()

    print(f"\n[5/5] 브리지 {BRIDGE_PORT} 재기동 + 200 OK 검증")
    graceful_shutdown()
    kill_port(BRIDGE_PORT)
    start_bridge()
    ok, info = verify_bridge()
    if ok:
        ver = info.get("version")
        mark = "✅" if ver == OMNI_VERSION else "⚠️ (버전 불일치)"
        print(f"  {mark} 200 OK  /health → {json.dumps(info, ensure_ascii=False)}")
    else:
        print(f"  ❌ 브리지 응답 없음: {info}  → {BASE / 'omni_bridge.log'} 확인")

    print("\n" + "-" * 66)
    print("  📌 다음 단계")
    print("   1) chrome://extensions → 'RGON Omni-Link Hub' 🔄 새로고침")
    print(f"      (처음이면 '압축해제된 확장 프로그램 로드' → {EXT_DIR})")
    print("   2) [📡 신경망] 하단 역할 선택 → '✏️ 직접 쓰기' → 이름 입력 → [지정]")
    print("   3) [⚡ 작업 분배] 체크박스 / 단독 발사 / 🚀 체크 발사 / 🌐 전체 발사")
    print(f"   4) 독대실: {CHAT_HTML}")
    print("-" * 66)
    print("OMNI-LINK v6.0.3 CUSTOM NEURAL & SOLO/CHECK DISPATCH READY!")


if __name__ == "__main__":
    main()
Copy