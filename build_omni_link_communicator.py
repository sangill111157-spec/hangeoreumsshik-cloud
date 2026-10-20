#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# build_omni_link_communicator.py
# 르곤 AI 만능 소통창 (RGON Omni-Link Hub) 설치·조립 스크립트
#
# 생성/업그레이드 대상 (기본: C:\Users\sangi\Downloads\shin-agent)
#   rgon_aside_extension/manifest.json
#   rgon_aside_extension/background.js
#   rgon_aside_extension/content_aside_bar.js
#   omni_bridge.py, start_omni_bridge.bat (127.0.0.1 전용 로컬 브리지)
#   omni_shared_clipboard.json, omni_dispatch_queue.json, anchongri_exec_queue.json
#   rgon_alpha_chat.html / dashboard/rgon_alpha_chat.html / docs/rgon_alpha_chat.html (패치)
#
# 환경변수 SHIN_AGENT_DIR 로 설치 경로를 바꿀 수 있습니다.

import os
import sys
import re
import json
import time
import shutil
import secrets
import subprocess
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OMNI_VERSION = "6.0.0"
BRIDGE_PORT = 8765
DEFAULT_BASE = r"C:\Users\sangi\Downloads\shin-agent"


def resolve_base():
    env = os.environ.get("SHIN_AGENT_DIR")
    if env:
        return Path(env)
    p = Path(DEFAULT_BASE)
    if os.name != "nt" and not p.exists():
        return Path.home() / "Downloads" / "shin-agent"
    return p


BASE = resolve_base()
EXT_DIR = BASE / "rgon_aside_extension"
STAMP = time.strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = BASE / "backups" / ("omni_link_" + STAMP)

# ----------------------------------------------------------------------------
# manifest.json
# ----------------------------------------------------------------------------
MANIFEST = {
    "manifest_version": 3,
    "name": "RGON Omni-Link Hub (르곤 AI 만능 소통창)",
    "version": OMNI_VERSION,
    "description": "르곤 독대실 ⇄ Claude Opus 5.5 ⇄ GPT-6.1 Sol ⇄ Grok 4.7 ⇄ Google Sheets ⇄ Adobe 멀티탭 신경망 허브",
    "minimum_chrome_version": "116",
    "permissions": ["storage", "activeTab", "tabs", "scripting", "clipboardWrite"],
    "host_permissions": ["<all_urls>"],
    "background": {"service_worker": "background.js"},
    "action": {"default_title": "✨ 르곤 만능 소통창 열기/닫기"},
    "commands": {
        "toggle-omni": {
            "suggested_key": {"default": "Alt+Shift+O"},
            "description": "르곤 만능 소통창 패널 열기/닫기",
        }
    },
    "content_scripts": [
        {
            "matches": ["<all_urls>"],
            "js": ["content_aside_bar.js"],
            "run_at": "document_idle",
            "all_frames": False,
        }
    ],
}

# ----------------------------------------------------------------------------
# background.js (멀티탭 신경망 라우터)
# ----------------------------------------------------------------------------
BACKGROUND_JS = r"""
"use strict";
// RGON Omni-Link v__OMNI_VERSION__ - background service worker (multi-tab neural router)

const OMNI_VERSION = "__OMNI_VERSION__";
const BRIDGE = "http://127.0.0.1:__BRIDGE_PORT__";
const OMNI_TOKEN = "__OMNI_TOKEN__";
const AI_ROLES = ["claude", "gpt", "grok"];
const ROLE_META = {
  rgon: { label: "르곤 독대실", icon: "🏛️" },
  claude: { label: "Claude Opus 5.5", icon: "🧠" },
  gpt: { label: "GPT-6.1 Sol", icon: "⚡" },
  grok: { label: "Grok 4.7", icon: "🎯" },
  sheets: { label: "Google Sheets", icon: "📊" },
  adobe: { label: "Adobe", icon: "🎨" }
};
const DEFAULT_LINKS = {
  studio: "http://127.0.0.1:8501/rgon_alpha_chat.html#studio-v5",
  rgon: "http://127.0.0.1:8501/rgon_alpha_chat.html",
  firefly: "https://firefly.adobe.com/",
  sheets: "https://docs.google.com/spreadsheets/d/1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY/edit#gid=1170771184",
  github: "https://github.com/sangill111157-spec/hangeoreumsshik-cloud/actions"
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let _lock = Promise.resolve();
function withLock(fn) {
  const p = _lock.then(fn, fn);
  _lock = p.catch(() => {});
  return p;
}

async function getStore(key, def) {
  const o = await chrome.storage.local.get(key);
  return o[key] === undefined ? def : o[key];
}
async function setStore(key, val) {
  await chrome.storage.local.set({ [key]: val });
}

// ---------------------------------------------------------------- role mapping
function roleFromText(s) {
  s = String(s || "");
  if (/claude/i.test(s)) return "claude";
  if (/gpt[-\s]?\d|chatgpt/i.test(s)) return "gpt";
  if (/grok/i.test(s)) return "grok";
  return null;
}

function guessRole(tab, reported, override) {
  if (override) return override;
  let u;
  try { u = new URL(tab.url || ""); } catch (_) { return null; }
  const host = u.hostname.toLowerCase();
  if ((host === "127.0.0.1" || host === "localhost") && u.port === "8501") return "rgon";
  if (host === "docs.google.com" && u.pathname.startsWith("/spreadsheets")) return "sheets";
  if (host === "adobe.com" || host.endsWith(".adobe.com")) return "adobe";
  if (host === "claude.ai" || host.endsWith(".claude.ai")) return "claude";
  if (host === "chatgpt.com" || host === "chat.openai.com") return "gpt";
  if (host === "grok.com" || (host === "x.com" && u.pathname.startsWith("/i/grok"))) return "grok";
  if (host === "genspark.ai" || host.endsWith(".genspark.ai")) {
    return reported || roleFromText(tab.title) || null;
  }
  return null;
}

async function scanTabs() {
  const [tabs, rep, ovr] = await Promise.all([
    chrome.tabs.query({}),
    getStore("omni_reported", {}),
    getStore("omni_override", {})
  ]);
  const list = [];
  const byRole = {};
  for (const t of tabs) {
    if (!t.id) continue;
    const r = rep[t.id] ? rep[t.id].role : null;
    const role = guessRole(t, r, ovr[t.id]);
    if (!role) continue;
    const info = {
      tabId: t.id,
      windowId: t.windowId,
      role,
      title: t.title || "",
      url: t.url || "",
      active: !!t.active,
      lastAccessed: t.lastAccessed || 0
    };
    list.push(info);
    (byRole[role] = byRole[role] || []).push(info);
  }
  return { list, byRole };
}

function pickTab(arr) {
  if (!arr || !arr.length) return null;
  return arr.slice().sort((a, b) => (b.lastAccessed || 0) - (a.lastAccessed || 0))[0];
}

async function focusTab(t) {
  try {
    await chrome.tabs.update(t.tabId, { active: true });
    await chrome.windows.update(t.windowId, { focused: true });
    return true;
  } catch (_) { return false; }
}

// ---------------------------------------------------------------- messaging
async function sendToTab(tabId, msg) {
  try {
    return await chrome.tabs.sendMessage(tabId, msg);
  } catch (e) {
    try {
      await chrome.scripting.executeScript({ target: { tabId }, files: ["content_aside_bar.js"] });
      await sleep(400);
      return await chrome.tabs.sendMessage(tabId, msg);
    } catch (e2) {
      return { ok: false, error: String((e2 && e2.message) || e2) };
    }
  }
}

async function dispatch(targets, prompt, autoSend, perRole) {
  const { byRole } = await scanTabs();
  const results = await Promise.all((targets || []).map(async (role) => {
    const t = pickTab(byRole[role]);
    if (!t) return { role, ok: false, error: "열려 있는 탭 없음" };
    const text = (perRole && perRole[role]) || prompt;
    const r = await sendToTab(t.tabId, { type: "OMNI_INJECT_PROMPT", prompt: text, autoSend: autoSend !== false });
    return Object.assign({ role, tabId: t.tabId }, r || { ok: false, error: "응답 없음" });
  }));
  return { ok: results.some((r) => r.ok), results };
}

async function bridgeFetch(path, method, body) {
  const ctl = new AbortController();
  const to = setTimeout(() => ctl.abort(), 4000);
  try {
    const res = await fetch(BRIDGE + path, {
      method: method || "GET",
      headers: { "X-Omni-Token": OMNI_TOKEN, "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
      signal: ctl.signal
    });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    return { ok: false, error: "브리지 오프라인 (start_omni_bridge.bat 실행 필요)" };
  } finally {
    clearTimeout(to);
  }
}

async function storeShared(role, entry) {
  await withLock(async () => {
    const sh = await getStore("omni_shared", { entries: {}, history: [] });
    sh.entries = sh.entries || {};
    sh.history = sh.history || [];
    sh.entries[role] = entry;
    sh.history.unshift({ role, ts: entry.ts, lines: entry.lines, bytes: entry.bytes, lang: entry.lang, hash: entry.hash, url: entry.url });
    sh.history = sh.history.slice(0, 40);
    sh.updated = Date.now();
    try {
      await setStore("omni_shared", sh);
    } catch (e) {
      entry.code = String(entry.code || "").slice(0, 100000);
      await setStore("omni_shared", sh);
    }
  });
  bridgeFetch("/api/shared", "POST", { role, entry }).catch(() => {});
  broadcastAll({ type: "OMNI_STATE_PING", role });
}

async function collect(targets) {
  const { byRole } = await scanTabs();
  const results = await Promise.all((targets || []).map(async (role) => {
    const t = pickTab(byRole[role]);
    if (!t) return { role, ok: false, error: "열려 있는 탭 없음" };
    const r = await sendToTab(t.tabId, { type: "OMNI_GET_LAST_CODE" });
    if (r && r.ok && r.entry) {
      r.entry.role = role;
      await storeShared(role, r.entry);
      return { role, ok: true, lines: r.entry.lines, bytes: r.entry.bytes };
    }
    return { role, ok: false, error: (r && r.error) || "코드 블록 없음" };
  }));
  return { ok: results.some((r) => r.ok), results };
}

async function broadcastAll(msg) {
  try {
    const tabs = await chrome.tabs.query({});
    for (const t of tabs) {
      if (!t.id || !/^https?:/i.test(t.url || "")) continue;
      chrome.tabs.sendMessage(t.id, msg).catch(() => {});
    }
  } catch (_) {}
}

async function openUrl(url) {
  const t = await chrome.tabs.create({ url, active: true });
  return { ok: true, opened: true, tabId: t.id };
}

async function openLink(key) {
  const stored = await getStore("omni_links", {});
  const links = Object.assign({}, DEFAULT_LINKS, stored);
  const { byRole } = await scanTabs();

  if (key === "sheets") {
    const cand = byRole.sheets || [];
    const hit = cand.find((t) => /두뇌장바구니|헌법/.test(t.title));
    if (hit) { await focusTab(hit); return { ok: true, focused: true }; }
    if (links.sheets) return openUrl(links.sheets);
    if (cand.length) { await focusTab(pickTab(cand)); return { ok: true, focused: true }; }
    return { ok: false, needConfig: true, key };
  }
  if (key === "github") {
    const tabs = await chrome.tabs.query({});
    const hit = tabs.find((t) => /github\.com\/.+\/actions/i.test(t.url || ""));
    if (hit) { await focusTab({ tabId: hit.id, windowId: hit.windowId }); return { ok: true, focused: true }; }
    if (links.github) return openUrl(links.github);
    return { ok: false, needConfig: true, key };
  }
  if (key === "studio" || key === "rgon") {
    const t = pickTab(byRole.rgon);
    if (t) {
      await focusTab(t);
      if (key === "studio") sendToTab(t.tabId, { type: "OMNI_SCROLL_STUDIO" });
      return { ok: true, focused: true };
    }
    return openUrl(links[key]);
  }
  if (key === "firefly") {
    const t = pickTab((byRole.adobe || []).filter((x) => /firefly/i.test(x.url)));
    if (t) { await focusTab(t); return { ok: true, focused: true }; }
    return openUrl(links.firefly);
  }
  return { ok: false, error: "알 수 없는 링크: " + key };
}

// ---------------------------------------------------------------- badge
let _badgeTimer = null;
function scheduleBadge() {
  clearTimeout(_badgeTimer);
  _badgeTimer = setTimeout(async () => {
    try {
      const { byRole } = await scanTabs();
      const n = Object.keys(byRole).length;
      await chrome.action.setBadgeText({ text: n ? String(n) : "" });
      await chrome.action.setBadgeBackgroundColor({ color: AI_ROLES.every((r) => byRole[r]) ? "#10b981" : "#7c5cff" });
    } catch (_) {}
  }, 500);
}
chrome.tabs.onUpdated.addListener(() => scheduleBadge());
chrome.tabs.onCreated.addListener(() => scheduleBadge());
chrome.tabs.onRemoved.addListener((tabId) => {
  withLock(async () => {
    const rep = await getStore("omni_reported", {});
    const ovr = await getStore("omni_override", {});
    delete rep[tabId];
    delete ovr[tabId];
    await setStore("omni_reported", rep);
    await setStore("omni_override", ovr);
  }).catch(() => {});
  scheduleBadge();
});

// ---------------------------------------------------------------- commands / install
async function toggleActive() {
  try {
    const [t] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    if (t && t.id) await sendToTab(t.id, { type: "OMNI_TOGGLE" });
  } catch (_) {}
}
chrome.action.onClicked.addListener(() => toggleActive());
chrome.commands.onCommand.addListener((cmd) => { if (cmd === "toggle-omni") toggleActive(); });

chrome.runtime.onInstalled.addListener(async () => {
  try {
    const tabs = await chrome.tabs.query({});
    for (const t of tabs) {
      if (!t.id || !/^https?:/i.test(t.url || "")) continue;
      chrome.scripting.executeScript({ target: { tabId: t.id }, files: ["content_aside_bar.js"] }).catch(() => {});
    }
  } catch (_) {}
  scheduleBadge();
});

// ---------------------------------------------------------------- message router
async function handle(msg, sender) {
  switch (msg && msg.type) {
    case "OMNI_REPORT_ROLE": {
      const id = sender.tab && sender.tab.id;
      if (!id) return { ok: false };
      await withLock(async () => {
        const rep = await getStore("omni_reported", {});
        if (msg.role) rep[id] = { role: msg.role, ts: Date.now() };
        else delete rep[id];
        await setStore("omni_reported", rep);
      });
      scheduleBadge();
      return { ok: true };
    }
    case "OMNI_SET_OVERRIDE": {
      const id = msg.tabId || (sender.tab && sender.tab.id);
      if (!id) return { ok: false };
      await withLock(async () => {
        const ovr = await getStore("omni_override", {});
        if (msg.role) ovr[id] = msg.role;
        else delete ovr[id];
        await setStore("omni_override", ovr);
      });
      scheduleBadge();
      return { ok: true };
    }
    case "OMNI_SCAN": {
      const { list, byRole } = await scanTabs();
      const counts = {};
      Object.keys(byRole).forEach((k) => (counts[k] = byRole[k].length));
      return { ok: true, version: OMNI_VERSION, list, counts, selfTabId: sender.tab ? sender.tab.id : null };
    }
    case "OMNI_DISPATCH":
      return dispatch(msg.targets, msg.prompt, msg.autoSend, msg.perRole);
    case "OMNI_COLLECT":
      return collect(msg.targets && msg.targets.length ? msg.targets : AI_ROLES);
    case "OMNI_STORE_SHARED":
      if (!msg.role || !msg.entry) return { ok: false, error: "invalid" };
      await storeShared(msg.role, msg.entry);
      return { ok: true };
    case "OMNI_GET_SHARED":
      return { ok: true, shared: await getStore("omni_shared", { entries: {}, history: [] }) };
    case "OMNI_FOCUS": {
      const { byRole } = await scanTabs();
      const t = pickTab(byRole[msg.role]);
      if (!t) return { ok: false, error: "열려 있는 탭 없음" };
      await focusTab(t);
      return { ok: true };
    }
    case "OMNI_OPEN":
      if (!/^https?:\/\//i.test(String(msg.url || ""))) return { ok: false, error: "http(s) URL만 허용" };
      return openUrl(msg.url);
    case "OMNI_OPEN_LINK":
      return openLink(msg.key);
    case "OMNI_SET_LINK": {
      if (!/^https?:\/\//i.test(String(msg.url || ""))) return { ok: false, error: "http(s) URL만 허용" };
      await withLock(async () => {
        const l = await getStore("omni_links", {});
        l[msg.key] = msg.url;
        await setStore("omni_links", l);
      });
      return { ok: true };
    }
    case "OMNI_GET_LINKS":
      return { ok: true, links: Object.assign({}, DEFAULT_LINKS, await getStore("omni_links", {})) };
    case "OMNI_SAVE": {
      const r = await bridgeFetch("/api/save", "POST", { role: msg.role, filename: msg.filename, code: msg.code, lang: msg.lang });
      return r.ok ? Object.assign({ ok: true }, r.data) : { ok: false, error: r.error || (r.data && r.data.error) || "저장 실패" };
    }
    case "OMNI_QUEUE": {
      const r = await bridgeFetch("/api/queue", "POST", { role: msg.role, filename: msg.filename, code: msg.code });
      return r.ok ? Object.assign({ ok: true }, r.data) : { ok: false, error: r.error || (r.data && r.data.error) || "큐 등록 실패" };
    }
    case "OMNI_BRIDGE_POLL": {
      const r = await bridgeFetch("/api/dispatch/next", "GET");
      if (r.ok && r.data && r.data.job) {
        const j = r.data.job;
        const d = await dispatch(j.targets || [], j.prompt || "", j.autoSend, j.perRole);
        return { ok: true, job: j, results: d.results };
      }
      return { ok: !!r.ok, job: null };
    }
    case "OMNI_BRIDGE_STATUS": {
      const h = await bridgeFetch("/api/health", "GET");
      if (!h.ok) return { ok: false, bridge: false, error: h.error || "브리지 응답 오류" };
      const s = await bridgeFetch("/api/status", "GET");
      return { ok: true, bridge: true, health: h.data, status: s.data || {} };
    }
    default:
      return { ok: false, error: "unknown message type" };
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  handle(msg, sender)
    .then(sendResponse)
    .catch((e) => sendResponse({ ok: false, error: String((e && e.message) || e) }));
  return true;
});

scheduleBadge();
"""

# ----------------------------------------------------------------------------
# content_aside_bar.js (배지 + 글래스모피즘 패널 + 주입기 + 흡수기)
# ----------------------------------------------------------------------------
CONTENT_JS = r"""
(() => {
"use strict";
if (window.top !== window) return;
const VER = "__OMNI_VERSION__";

// 이전 인스턴스(재주입/확장 리로드) 정리
try { window.dispatchEvent(new CustomEvent("rgon-omni-kill")); } catch (_) {}
const oldHost = document.getElementById("rgon-omni-host");
if (oldHost) oldHost.remove();

const ROLE_META = {
  rgon: { label: "르곤 독대실", icon: "🏛️" },
  claude: { label: "Claude Opus 5.5", icon: "🧠" },
  gpt: { label: "GPT-6.1 Sol", icon: "⚡" },
  grok: { label: "Grok 4.7", icon: "🎯" },
  sheets: { label: "Google Sheets", icon: "📊" },
  adobe: { label: "Adobe", icon: "🎨" }
};
const ROLE_ORDER = ["rgon", "claude", "gpt", "grok", "sheets", "adobe"];
const AI_ROLES = ["claude", "gpt", "grok"];
const GROK_PREFIX = "[광고 카피라이터 모드] 아래 지시를 바탕으로 짧고 강렬한 카피 5안을 제시해 주세요.\n\n";
const IS_RGON = /^(127\.0\.0\.1|localhost)$/.test(location.hostname) && location.port === "8501";
const IS_AI_HOST = /(^|\.)(genspark\.ai|claude\.ai|chatgpt\.com|openai\.com|grok\.com)$|^x\.com$/.test(location.hostname);

const state = { role: null, tabId: null, open: false, scan: null, autoAbsorb: true, lastHash: null, dead: false, reported: undefined };
const intervals = [];
let observer = null;
let arenaCache = {};
let bc = null;
try { bc = new BroadcastChannel("rgon_omni_link"); } catch (_) {}

function teardown() {
  state.dead = true;
  intervals.forEach(clearInterval);
  if (observer) { try { observer.disconnect(); } catch (_) {} }
  try { if (bc) bc.close(); } catch (_) {}
  const h = document.getElementById("rgon-omni-host");
  if (h) h.remove();
}
window.addEventListener("rgon-omni-kill", teardown, { once: true });

// ------------------------------------------------------------------ utils
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c]));
const trunc = (s, n) => { s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; };
const fmtKB = (b) => (b / 1024).toFixed(1) + " KB";
function hashStr(s) { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return String(h >>> 0); }
function stamp(ts) {
  const d = new Date(ts || Date.now()); const p = (n) => String(n).padStart(2, "0");
  return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + "_" + p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
}
function extFor(lang) {
  const m = { python: "py", py: "py", javascript: "js", js: "js", jsx: "js", node: "js", typescript: "ts", ts: "ts", json: "json", html: "html", css: "css", markdown: "md", md: "md", yaml: "yml", yml: "yml", csv: "csv" };
  return m[String(lang || "").toLowerCase()] || "txt";
}
function rt(msg) {
  return new Promise((res) => {
    try {
      chrome.runtime.sendMessage(msg, (r) => {
        if (chrome.runtime.lastError) res({ ok: false, error: chrome.runtime.lastError.message });
        else res(r || { ok: false, error: "no response" });
      });
    } catch (e) { res({ ok: false, error: String((e && e.message) || e) }); }
  });
}
function visible(el) {
  if (!el || !el.getBoundingClientRect) return false;
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  return r.width > 20 && r.height > 10 && cs.visibility !== "hidden" && cs.display !== "none";
}

// ------------------------------------------------------------------ model detection (genspark 등)
const MODEL_RE = { claude: /claude/gi, gpt: /gpt[-\s]?\d|chatgpt/gi, grok: /grok/gi };
function detectModelRole() {
  const byTitle = (s) => {
    if (/claude/i.test(s)) return "claude";
    if (/gpt[-\s]?\d|chatgpt/i.test(s)) return "gpt";
    if (/grok/i.test(s)) return "grok";
    return null;
  };
  let r = byTitle(document.title || "");
  if (r) return r;
  const cands = document.querySelectorAll("button, [role='button'], [role='combobox'], [aria-haspopup]");
  for (const c of cands) {
    const t = (c.innerText || "").trim();
    if (!t || t.length > 60) continue;
    r = byTitle(t);
    if (r && visible(c)) return r;
  }
  const body = (document.body && document.body.innerText || "").slice(0, 200000);
  let best = null, bestN = 0;
  for (const k of Object.keys(MODEL_RE)) {
    const n = (body.match(MODEL_RE[k]) || []).length;
    if (n > bestN) { best = k; bestN = n; }
  }
  return best;
}
async function detectAndReport() {
  if (!IS_AI_HOST) return;
  const r = detectModelRole();
  if (r !== state.reported) {
    state.reported = r;
    await rt({ type: "OMNI_REPORT_ROLE", role: r });
  }
}

// ------------------------------------------------------------------ prompt injection
function findInput() {
  const sel = "textarea, [contenteditable='true'], [contenteditable='plaintext-only'], [role='textbox']";
  const all = [...document.querySelectorAll(sel)].filter((e) => visible(e) && !e.disabled && !e.readOnly);
  if (!all.length) return null;
  const ph = (e) => {
    let s = (e.getAttribute("placeholder") || e.getAttribute("aria-placeholder") || e.getAttribute("data-placeholder") || e.getAttribute("aria-label") || "");
    const c = e.querySelector && e.querySelector("[data-placeholder]");
    if (c) s += " " + (c.getAttribute("data-placeholder") || "");
    return s;
  };
  const hit = all.find((e) => ph(e).includes("무엇이든 물어보고 만들어보세요"));
  if (hit) return hit;
  const scored = all.map((e) => {
    const r = e.getBoundingClientRect();
    let s = Math.min(r.width, 800) / 10 + (r.top / Math.max(innerHeight, 1)) * 30;
    if (e.tagName === "TEXTAREA") s += 10;
    if (/ask|message|prompt|물어|질문|입력|메시지|reply/i.test(ph(e))) s += 40;
    return { e, s };
  });
  scored.sort((a, b) => b.s - a.s);
  return scored[0].e;
}
async function setText(el, text) {
  el.focus();
  if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
    const proto = el.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    setter.call(el, text);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    return "native-setter";
  }
  const sel = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(el);
  sel.removeAllRanges();
  sel.addRange(range);
  let ok = false;
  try { ok = document.execCommand("insertText", false, text); } catch (_) {}
  if (!ok || !(el.innerText || "").trim()) {
    el.textContent = text;
    el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: text }));
    return "textContent";
  }
  return "execCommand";
}
function findSendBtn(input) {
  const scope = input.closest("form") || (input.parentElement && input.parentElement.parentElement && input.parentElement.parentElement.parentElement && input.parentElement.parentElement.parentElement.parentElement) || document;
  const sels = ["button[type='submit']", "button[aria-label*='send' i]", "button[aria-label*='전송']", "button[aria-label*='보내']", "button[aria-label*='제출']", "button[data-testid*='send' i]", "[role='button'][aria-label*='send' i]", "button[class*='send' i]"];
  for (const root of [scope, document]) {
    for (const s of sels) {
      const b = [...root.querySelectorAll(s)].find((x) => visible(x) && !x.disabled && x.getAttribute("aria-disabled") !== "true");
      if (b) return b;
    }
  }
  return null;
}
async function sendIt(input) {
  await sleep(350);
  const b = findSendBtn(input);
  if (b) { b.click(); return "button-click"; }
  input.focus();
  const opt = { key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true, cancelable: true };
  input.dispatchEvent(new KeyboardEvent("keydown", opt));
  input.dispatchEvent(new KeyboardEvent("keypress", opt));
  input.dispatchEvent(new KeyboardEvent("keyup", opt));
  return "enter-key";
}
async function injectPrompt(prompt, autoSend) {
  const el = findInput();
  if (!el) return { ok: false, error: "입력창을 찾지 못함 (textarea / contenteditable 없음)" };
  const method = await setText(el, String(prompt || ""));
  await sleep(150);
  let sent = false, sendMethod = null;
  if (autoSend) { sendMethod = await sendIt(el); sent = true; }
  return { ok: true, method, sent, sendMethod };
}

// ------------------------------------------------------------------ code absorber
function langFromNode(n) {
  let el = n;
  for (let i = 0; el && i < 3; i++, el = el.parentElement) {
    const cls = (el.className && el.className.toString()) || "";
    const m = cls.match(/(?:language|lang)-([\w+#-]+)/i);
    if (m) return m[1].toLowerCase();
    const d = el.getAttribute && (el.getAttribute("data-language") || el.getAttribute("data-lang"));
    if (d) return d.toLowerCase();
  }
  return null;
}
function guessLang(code) {
  const t = code.trim();
  if (/^[\[{]/.test(t)) { try { JSON.parse(t); return "json"; } catch (_) {} }
  if (/^\s*<!doctype html|^\s*<html/i.test(t)) return "html";
  if (/^\s*(from\s+[\w.]+\s+import|import\s+[\w.]+\s*$|def\s+\w+\(|class\s+\w+\s*[:(])/m.test(t)) return "python";
  if (/\b(function|const|let|=>|require\(|import .* from)/.test(t)) return "javascript";
  return "text";
}
function lastJsonInText() {
  const txt = (document.body && document.body.innerText || "").slice(-60000);
  const end = txt.lastIndexOf("}");
  if (end < 0) return null;
  const starts = [];
  const re = /(^|\n)\s*\{/g;
  let m;
  while ((m = re.exec(txt)) && starts.length < 400) starts.push(m.index + m[0].lastIndexOf("{"));
  for (let i = starts.length - 1, tries = 0; i >= 0 && tries < 20; i--, tries++) {
    if (starts[i] > end) continue;
    const cand = txt.slice(starts[i], end + 1);
    try { JSON.parse(cand); return cand; } catch (_) {}
  }
  return null;
}
function buildEntry(code, lang, kind, blockCount) {
  if (code.length > 400000) code = code.slice(0, 400000);
  const lines = code.split("\n").length;
  const bytes = new TextEncoder().encode(code).length;
  const names = new Set();
  const add = (re) => { let m; re.lastIndex = 0; while ((m = re.exec(code)) && names.size < 200) names.add(m[1]); };
  add(/^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)/gm);
  add(/\bfunction\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(/g);
  add(/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>/g);
  add(/^\s*class\s+([A-Za-z_]\w*)/gm);
  const tryCount = (code.match(/\btry\b/g) || []).length;
  const hasEntry = /__name__\s*==\s*['"]__main__['"]|module\.exports|\bexport\s+(?:default|const|function|class)\b|\bmain\s*\(/.test(code);
  const funcs = [...names];
  const score = Math.round(Math.min(funcs.length, 30) * 3 + Math.min(tryCount, 10) * 2 + (hasEntry ? 5 : 0) + Math.min(lines, 600) / 40 + (lang === "text" ? -5 : 0));
  return { code, lang, kind, lines, bytes, funcs: funcs.slice(0, 30), funcCount: funcs.length, tryCount, hasEntry, score, blockCount: blockCount || 1, hash: hashStr(code), ts: Date.now(), url: location.href, title: document.title };
}
function extractLastCode() {
  const raw = [...document.querySelectorAll("pre code, pre, .cm-content")];
  const blocks = [];
  for (const n of raw) {
    if (n.closest("#rgon-omni-host")) continue;
    if (n.tagName === "PRE" && n.querySelector("code")) continue;
    let txt = n.matches(".cm-content") ? (n.innerText || "") : (n.textContent || "");
    if (!txt.includes("\n") && n.innerText) txt = n.innerText;
    txt = txt.replace(/\u00a0/g, " ").replace(/\r\n/g, "\n");
    if (txt.trim().length < 2) continue;
    blocks.push({ n, txt });
  }
  if (blocks.length) {
    const b = blocks[blocks.length - 1];
    const code = b.txt.replace(/\s+$/, "");
    return buildEntry(code, langFromNode(b.n) || guessLang(code), "code", blocks.length);
  }
  const j = lastJsonInText();
  if (j) return buildEntry(j, "json", "json", 1);
  return null;
}
function absorbPageText() {
  const selTxt = String(window.getSelection() || "").trim();
  let text = selTxt;
  if (!text) {
    const root = document.querySelector("main, article, [role='main']") || document.body;
    text = (root.innerText || "").trim().slice(0, 60000);
  }
  if (!text) return null;
  const e = buildEntry(text, "text", "page", 1);
  e.kind = selTxt ? "selection" : "page";
  return e;
}
async function copyText(text) {
  try { await navigator.clipboard.writeText(text); return true; } catch (_) {}
  try {
    const ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    const ok = document.execCommand("copy");
    ta.remove();
    return ok;
  } catch (_) { return false; }
}
function downloadBlob(name, text) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
  a.download = name;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}

// ------------------------------------------------------------------ UI (Shadow DOM, dark glassmorphism)
const host = document.createElement("div");
host.id = "rgon-omni-host";
host.style.cssText = "all:initial;position:fixed;top:0;right:0;z-index:2147483647;";
const root = host.attachShadow({ mode: "open" });
const $ = (s) => root.querySelector(s);
const $$ = (s) => [...root.querySelectorAll(s)];

root.innerHTML = `
<style>
:host{all:initial}
*{box-sizing:border-box;font-family:"Pretendard","Noto Sans KR","Segoe UI",system-ui,sans-serif}
.badge{position:fixed;top:12px;right:12px;z-index:2147483647;display:flex;align-items:center;gap:8px;padding:8px 14px;border-radius:999px;color:#fff;font-size:13px;font-weight:700;cursor:pointer;user-select:none;background:linear-gradient(135deg,rgba(124,92,255,.88),rgba(0,200,255,.78));border:1px solid rgba(255,255,255,.35);box-shadow:0 8px 30px rgba(80,60,255,.38);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.badge .cnt{background:rgba(0,0,0,.38);border-radius:999px;padding:1px 8px;font-size:12px}
.badge.flash{animation:fl .9s ease 2}
@keyframes fl{50%{transform:scale(1.08);box-shadow:0 0 0 7px rgba(0,255,170,.35)}}
.panel{position:fixed;top:56px;right:12px;width:440px;max-width:calc(100vw - 24px);height:calc(100vh - 72px);z-index:2147483646;color:#e9ecff;background:rgba(14,17,34,.76);backdrop-filter:blur(20px) saturate(160%);-webkit-backdrop-filter:blur(20px) saturate(160%);border:1px solid rgba(255,255,255,.14);border-radius:18px;box-shadow:0 22px 64px rgba(0,0,0,.55);display:flex;flex-direction:column;transform:translateX(calc(100% + 30px));opacity:0;pointer-events:none;transition:transform .28s cubic-bezier(.2,.8,.2,1),opacity .2s;overflow:hidden}
.panel.open{transform:none;opacity:1;pointer-events:auto}
header{display:flex;align-items:center;gap:8px;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.1);background:linear-gradient(90deg,rgba(124,92,255,.25),rgba(0,200,255,.12))}
header b{font-size:14px}header small{opacity:.65;font-size:11px;flex:1}
header .x{background:none;border:0;color:#fff;font-size:16px;cursor:pointer}
.tabs{display:flex;gap:4px;padding:8px 10px 0}
.tabs button{flex:1;padding:8px 4px;font-size:11.5px;color:#cfd4ff;background:rgba(255,255,255,.05);border:1px solid transparent;border-bottom:0;border-radius:10px 10px 0 0;cursor:pointer}
.tabs button.on{background:rgba(124,92,255,.35);color:#fff;border-color:rgba(255,255,255,.18)}
.body{flex:1;overflow:auto;padding:12px 14px}
.pane{display:none}.pane.on{display:block}
.lamp{display:flex;align-items:center;gap:10px;padding:8px 10px;margin-bottom:7px;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08)}
.lamp.on{border-color:rgba(16,185,129,.55);background:rgba(16,185,129,.1)}
.lamp .lt{flex:1;min-width:0}.lamp .lt b{display:block;font-size:13px}.lamp .lt small{display:block;opacity:.7;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
button.b{padding:7px 11px;font-size:12px;color:#fff;background:rgba(124,92,255,.5);border:1px solid rgba(255,255,255,.2);border-radius:9px;cursor:pointer}
button.b:hover{background:rgba(124,92,255,.8)}
button.b.g{background:rgba(16,185,129,.5)}button.b.o{background:rgba(245,158,11,.5)}button.b.c{background:rgba(0,180,255,.45)}
.row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:8px 0}
textarea,input[type=text],select{width:100%;color:#fff;background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:8px;font-size:12.5px}
textarea{min-height:130px;resize:vertical}
select{width:auto}
label{font-size:12px;opacity:.85;display:flex;align-items:center;gap:5px}
.out{font-size:12px;line-height:1.6;margin-top:8px;padding:8px 10px;border-radius:10px;background:rgba(0,0,0,.25);min-height:20px}
.card{padding:10px;margin:8px 0;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1)}
.card .ch{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}.card .ch small{opacity:.7;font-size:11px}
pre.pv{max-height:130px;overflow:auto;margin:0 0 6px;padding:8px;font-size:11px;line-height:1.4;background:rgba(0,0,0,.45);border-radius:8px;color:#c7f9cc;white-space:pre-wrap;word-break:break-all}
.meta{font-size:11px;opacity:.75;margin-bottom:6px}
.btns{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
table.cmp{width:100%;border-collapse:collapse;font-size:12px;margin:6px 0}
table.cmp th,table.cmp td{padding:5px 6px;border-bottom:1px solid rgba(255,255,255,.1);text-align:center}
table.cmp td.w{background:rgba(16,185,129,.25);font-weight:700}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.grid .b{padding:12px 8px;font-size:12.5px}
.toast{position:fixed;right:18px;bottom:22px;max-width:360px;padding:10px 14px;border-radius:12px;color:#fff;font-size:12.5px;background:rgba(20,24,48,.92);border:1px solid rgba(255,255,255,.2);opacity:0;transform:translateY(10px);transition:.25s;pointer-events:none;z-index:2147483647}
.toast.on{opacity:1;transform:none}
h4{margin:6px 0;font-size:12.5px;color:#b9c0ff}
</style>
<div class="badge" id="badge">✨ 르곤 만능 소통창 (Omni-Link) <span class="cnt" id="cnt">0</span></div>
<aside class="panel" id="panel">
  <header><b>✨ 르곤 AI 만능 소통창</b><small>RGON Omni-Link Hub v${VER}</small><button class="x" id="close">✕</button></header>
  <nav class="tabs">
    <button data-tab="1" class="on">📡 신경망</button>
    <button data-tab="2">⚡ 작업 분배</button>
    <button data-tab="3">🧲 흡수기</button>
    <button data-tab="4">🎬 STUDIO</button>
  </nav>
  <div class="body">
    <section class="pane on" data-pane="1">
      <div class="row"><b style="font-size:12px">이 탭 역할:</b> <span id="selfRole">확인 중…</span>
        <select id="roleSel"><option value="">자동 감지</option><option value="rgon">르곤 독대실</option><option value="claude">Claude Opus 5.5</option><option value="gpt">GPT-6.1 Sol</option><option value="grok">Grok 4.7</option><option value="sheets">Google Sheets</option><option value="adobe">Adobe</option></select>
        <button class="b" id="roleSave">지정</button></div>
      <div id="lamps"></div>
      <div class="row"><button class="b c" id="rescan">🔄 다시 스캔</button><small style="opacity:.6;font-size:11px">3초마다 자동 갱신 · 단축키 Alt+Shift+O</small></div>
    </section>
    <section class="pane" data-pane="2">
      <div class="row"><select id="preset"><option value="">— 지시문 템플릿 —</option><option value="design">코드 설계 요청</option><option value="review">코드 리뷰/개선</option><option value="ad">10초 광고 카피</option></select></div>
      <textarea id="prompt" placeholder="사령관 지시문을 입력하세요. 열려 있는 Claude / GPT / Grok 탭 입력창에 자동으로 꽂아 넣습니다."></textarea>
      <div class="row"><label><input type="checkbox" id="autosend" checked> 자동 전송</label><label><input type="checkbox" id="grokPrefix" checked> Grok 카피 모드 접두어</label></div>
      <div class="row"><button class="b g" id="fireCG">🚀 Claude + GPT 동시 발사</button><button class="b o" id="fireGrok">🎯 Grok 카피 발사</button><button class="b" id="fireAll">🌐 3종 전체 발사</button></div>
      <div class="out" id="fireOut">대기 중…</div>
    </section>
    <section class="pane" data-pane="3">
      <div class="row"><button class="b g" id="absThis">🧲 이 탭 코드 흡수 + 복사</button><button class="b c" id="absAll">🔄 AI 탭 전체 수거</button><button class="b" id="absPage">📄 화면 텍스트 흡수</button></div>
      <div class="row"><label><input type="checkbox" id="autoAbs" checked> 응답 완료 감지 시 자동 흡수 (Claude/GPT/Grok 탭)</label></div>
      <div class="out" id="absOut">대기 중…</div>
      <div id="arena"></div>
    </section>
    <section class="pane" data-pane="4">
      <div class="grid">
        <button class="b g" data-link="studio">🎬 STUDIO v5<br><small>10초 광고 MP4</small></button>
        <button class="b" data-link="rgon">🏛️ 르곤 독대실</button>
        <button class="b c" data-link="sheets">📊 두뇌장바구니_헌법<br><small>Google Sheets</small></button>
        <button class="b o" data-link="github">⚙️ GitHub Actions<br><small>외부 주방</small></button>
        <button class="b" data-link="firefly">🎨 Adobe Firefly</button>
        <button class="b" id="cfgLinks">🔧 링크 설정</button>
      </div>
      <div class="row"><button class="b c" id="chkStatus">🩺 상태 확인</button></div>
      <div class="out" id="statusOut">상태 확인을 눌러주세요.</div>
    </section>
  </div>
</aside>
<div class="toast" id="toast"></div>`;

(document.body || document.documentElement).appendChild(host);

function toast(msg, ms) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("on");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove("on"), ms || 2600);
}
function flashBadge() {
  const b = $("#badge");
  b.classList.remove("flash");
  void b.offsetWidth;
  b.classList.add("flash");
}
function togglePanel(force) {
  state.open = typeof force === "boolean" ? force : !state.open;
  $("#panel").classList.toggle("open", state.open);
  if (state.open) { refreshScan(); renderArena(); }
}

function fmtResults(results) {
  return (results || []).map((r) => {
    const m = ROLE_META[r.role] || { label: r.role, icon: "" };
    if (r.ok) return `✅ ${m.icon} ${esc(m.label)}: ${r.sent ? "입력 + 전송 완료" : "입력 완료 (전송 대기)"} <small>(${esc(r.method || "")}${r.sendMethod ? " / " + esc(r.sendMethod) : ""})</small>`;
    return `⚠️ ${m.icon} ${esc(m.label)}: ${esc(r.error || "실패")}`;
  }).join("<br>") || "결과 없음";
}

// ------------------------------------------------------------------ tab 1: neural link
function renderLamps() {
  const scan = state.scan;
  if (!scan) return;
  const html = ROLE_ORDER.map((role) => {
    const m = ROLE_META[role];
    const tabs = scan.list.filter((t) => t.role === role);
    const on = tabs.length > 0;
    const first = tabs.slice().sort((a, b) => (b.lastAccessed || 0) - (a.lastAccessed || 0))[0];
    return `<div class="lamp ${on ? "on" : "off"}"><span>${on ? "🟢" : "⚫"}</span><div class="lt"><b>${m.icon} ${esc(m.label)}</b><small>${on ? esc(trunc(first.title, 46)) + (tabs.length > 1 ? " (+" + (tabs.length - 1) + ")" : "") : "연결 안 됨"}</small></div>${on ? `<button class="b" data-focus="${role}">이동</button>` : ""}</div>`;
  }).join("");
  $("#lamps").innerHTML = html;
  const n = ROLE_ORDER.filter((r) => scan.list.some((t) => t.role === r)).length;
  $("#cnt").textContent = String(n);
  const me = state.role ? ROLE_META[state.role] : null;
  $("#selfRole").textContent = me ? me.icon + " " + me.label : "일반 페이지";
}
async function refreshScan() {
  if (state.dead) return;
  const r = await rt({ type: "OMNI_SCAN" });
  if (!r || !r.ok) return;
  state.scan = r;
  state.tabId = r.selfTabId;
  const me = r.list.find((t) => t.tabId === r.selfTabId);
  const nr = me ? me.role : null;
  if (nr !== state.role) { state.role = nr; onRoleChange(); }
  renderLamps();
}

// ------------------------------------------------------------------ auto absorb (completion detection)
function isGenerating() {
  return [...document.querySelectorAll("button[aria-label],[role='button'][aria-label]")].some((b) => /stop|중지|중단|정지/i.test(b.getAttribute("aria-label") || "") && visible(b));
}
async function autoAbsorbTick(retry) {
  if (state.dead || !state.autoAbsorb || !AI_ROLES.includes(state.role)) return;
  if (isGenerating() && retry < 6) { setTimeout(() => autoAbsorbTick(retry + 1), 1500); return; }
  const e = extractLastCode();
  if (!e || e.hash === state.lastHash) return;
  state.lastHash = e.hash;
  e.role = state.role;
  const r = await rt({ type: "OMNI_STORE_SHARED", role: state.role, entry: e });
  if (r && r.ok) {
    flashBadge();
    toast("🧲 " + ROLE_META[state.role].label + " 코드 자동 흡수 (" + e.lines + "줄)");
    try { if (bc) bc.postMessage({ type: "shared-updated", role: state.role, hash: e.hash, ts: e.ts }); } catch (_) {}
  }
}
function startObserver() {
  if (observer || !document.body) return;
  let firstTs = 0, tm = null;
  observer = new MutationObserver(() => {
    if (!state.autoAbsorb) return;
    const now = Date.now();
    if (!firstTs) firstTs = now;
    clearTimeout(tm);
    const wait = now - firstTs > 15000 ? 0 : 3000;
    tm = setTimeout(() => { firstTs = 0; autoAbsorbTick(0); }, wait);
  });
  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
}
function stopObserver() {
  if (observer) { try { observer.disconnect(); } catch (_) {} observer = null; }
}
function onRoleChange() {
  if (AI_ROLES.includes(state.role)) startObserver(); else stopObserver();
}

// ------------------------------------------------------------------ tab 2: dispatch
async function fire(targets) {
  const base = $("#prompt").value.trim();
  if (!base) { toast("지시문을 입력하세요."); return; }
  const autoSend = $("#autosend").checked;
  const perRole = {};
  if ($("#grokPrefix").checked && targets.includes("grok")) perRole.grok = GROK_PREFIX + base;
  $("#fireOut").textContent = "발사 중…";
  const r = await rt({ type: "OMNI_DISPATCH", targets, prompt: base, autoSend, perRole });
  $("#fireOut").innerHTML = r && r.results ? fmtResults(r.results) : "⚠️ " + esc((r && r.error) || "실패");
}

// ------------------------------------------------------------------ tab 3: absorber + arena
async function getShared() {
  try {
    const o = await chrome.storage.local.get("omni_shared");
    return o.omni_shared || { entries: {}, history: [] };
  } catch (_) { return { entries: {}, history: [] }; }
}
function cardHTML(role, e) {
  const m = ROLE_META[role] || { label: role === "page" ? "화면 텍스트" : role, icon: "📄" };
  const fn = "omni_" + role + "_" + stamp(e.ts) + "." + extFor(e.lang);
  return `<div class="card" data-role="${esc(role)}"><div class="ch"><b>${m.icon} ${esc(m.label)}</b><small>${esc(e.lang || "text")} · ${e.lines}줄 · ${fmtKB(e.bytes)}</small></div>
<pre class="pv">${esc(String(e.code || "").slice(0, 700))}${String(e.code || "").length > 700 ? "\n…" : ""}</pre>
<div class="meta">함수/클래스 ${e.funcCount || 0}개${e.funcs && e.funcs.length ? ": " + esc(e.funcs.slice(0, 6).join(", ")) : ""}</div>
<input type="text" class="fn" value="${esc(fn)}">
<div class="btns"><button class="b" data-act="copy">📋 복사</button><button class="b g" data-act="save">💾 shin-agent 저장</button><button class="b o" data-act="queue">📮 안총리 실행 큐</button></div></div>`;
}
function compareHTML(a, b) {
  const rows = [
    ["줄 수", a.lines, b.lines, "num"],
    ["용량", fmtKB(a.bytes), fmtKB(b.bytes), a.bytes === b.bytes ? 0 : (a.bytes > b.bytes ? 1 : -1)],
    ["함수/클래스 수", a.funcCount || 0, b.funcCount || 0, "num"],
    ["예외처리(try)", a.tryCount || 0, b.tryCount || 0, "num"],
    ["진입점/export", a.hasEntry ? "있음" : "없음", b.hasEntry ? "있음" : "없음", (a.hasEntry ? 1 : 0) - (b.hasEntry ? 1 : 0)],
    ["참고 점수", a.score, b.score, "num"]
  ];
  const cls = (v, side) => (v > 0 && side === 0) || (v < 0 && side === 1) ? "w" : "";
  const body = rows.map((r) => {
    let v = r[3];
    if (v === "num") v = Number(r[1]) === Number(r[2]) ? 0 : (Number(r[1]) > Number(r[2]) ? 1 : -1);
    return `<tr><th>${r[0]}</th><td class="${cls(v, 0)}">${r[1]}</td><td class="${cls(v, 1)}">${r[2]}</td></tr>`;
  }).join("");
  const win = a.score === b.score ? "동점" : (a.score > b.score ? "🧠 Claude" : "⚡ GPT");
  return `<h4>⚔️ Best-of-Breed 아레나: Claude Opus 5.5 vs GPT-6.1 Sol</h4><table class="cmp"><tr><th></th><th>🧠 Claude</th><th>⚡ GPT</th></tr>${body}</table><div class="meta">🏆 단순 휴리스틱 기준 참고 추천: <b>${win}</b> (실제 실행·검토 후 선택하세요)</div>`;
}
async function renderArena() {
  if (state.dead) return;
  const sh = await getShared();
  const en = sh.entries || {};
  arenaCache = en;
  let html = "";
  if (en.claude && en.gpt) html += compareHTML(en.claude, en.gpt);
  const order = ["claude", "gpt", "grok"].concat(Object.keys(en).filter((k) => !["claude", "gpt", "grok"].includes(k)));
  const cards = order.filter((k) => en[k]).map((k) => cardHTML(k, en[k])).join("");
  html += cards || `<div class="out">아직 흡수된 결과물이 없습니다.</div>`;
  $("#arena").innerHTML = html;
}
async function storeEntry(role, e) {
  e.role = role;
  const r = await rt({ type: "OMNI_STORE_SHARED", role, entry: e });
  try { if (bc) bc.postMessage({ type: "shared-updated", role, hash: e.hash, ts: e.ts }); } catch (_) {}
  return r;
}

// ------------------------------------------------------------------ tab 4: links & status
async function openLink(key) {
  let r = await rt({ type: "OMNI_OPEN_LINK", key });
  if (r && r.needConfig) {
    const label = key === "sheets" ? "Google Sheets 『두뇌장바구니_헌법』" : "GitHub Actions 외부 주방";
    const url = window.prompt(label + " URL을 입력하세요 (한 번만 저장됩니다):", "https://");
    if (url && /^https?:\/\//i.test(url)) {
      await rt({ type: "OMNI_SET_LINK", key, url });
      r = await rt({ type: "OMNI_OPEN_LINK", key });
    } else { toast("URL이 입력되지 않았습니다."); return; }
  }
  if (!r || !r.ok) toast("⚠️ " + ((r && r.error) || "열기 실패"));
}
async function checkStatus() {
  $("#statusOut").textContent = "확인 중…";
  const [r, s] = await Promise.all([rt({ type: "OMNI_BRIDGE_STATUS" }), rt({ type: "OMNI_SCAN" })]);
  const lines = [];
  if (r && r.bridge) {
    const st = r.status || {};
    lines.push("🟢 로컬 브리지 연결됨 (" + esc((r.health && r.health.base) || "") + ")");
    const mp4 = st.studio_mp4 || [];
    lines.push(mp4.length ? "🎬 최신 MP4: " + esc(mp4[0].name) + " (" + esc(mp4[0].size_kb) + " KB, " + esc(mp4[0].mtime_str) + ")" : "🎬 shin-agent 안에서 MP4를 찾지 못했습니다.");
    lines.push("📮 실행 큐 대기: " + (st.exec_queue_pending || 0) + "건 · 📥 분배 큐: " + (st.dispatch_queue_pending || 0) + "건");
  } else {
    lines.push("🔴 로컬 브리지 오프라인 — shin-agent 폴더의 start_omni_bridge.bat 를 실행하세요. (저장·큐·파일 공유 기능에만 필요)");
  }
  if (s && s.ok) {
    const has = (k) => s.list.some((t) => t.role === k);
    lines.push((has("sheets") ? "🟢" : "⚫") + " Google Sheets 탭 · " + (has("rgon") ? "🟢" : "⚫") + " 독대실 탭 · " + (has("adobe") ? "🟢" : "⚫") + " Adobe 탭");
  }
  $("#statusOut").innerHTML = lines.join("<br>");
}

// ------------------------------------------------------------------ wiring
$("#badge").addEventListener("click", () => togglePanel());
$("#close").addEventListener("click", () => togglePanel(false));

$$(".tabs button").forEach((b) => b.addEventListener("click", () => {

  $$(".tabs button").forEach((x) => x.classList.toggle("on", x === b));

  $$(".pane").forEach((p) => p.classList.toggle("on", p.dataset.pane === b.dataset.tab));
  if (b.dataset.tab === "3") renderArena();
}));
$("#rescan").addEventListener("click", refreshScan);
$("#roleSave").addEventListener("click", async () => {
  await rt({ type: "OMNI_SET_OVERRIDE", role: $("#roleSel").value });
  await refreshScan();
  toast("이 탭 역할을 저장했습니다.");
});
$("#lamps").addEventListener("click", async (ev) => {
  const b = ev.target.closest("[data-focus]");
  if (b) await rt({ type: "OMNI_FOCUS", role: b.dataset.focus });
});
$("#preset").addEventListener("change", (ev) => {
  const p = {
    design: "다음 기능을 구현하는 단일 Python 스크립트를 설계·작성해 주세요. 코드 블록 하나로, 주요 함수에는 주석을, main 진입점을 포함해 주세요:\n\n",
    review: "아래 코드를 리뷰하고 버그·예외처리·성능을 개선한 전체 코드를 코드 블록 하나로 출력해 주세요:\n\n",
    ad: "10초 광고 영상(STUDIO v5)용 한국어 카피를 훅-혜택-CTA 구조로 작성해 주세요:\n\n"
  }[ev.target.value];
  if (p) $("#prompt").value = p + $("#prompt").value;
  ev.target.value = "";
});
$("#fireCG").addEventListener("click", () => fire(["claude", "gpt"]));
$("#fireGrok").addEventListener("click", () => fire(["grok"]));
$("#fireAll").addEventListener("click", () => fire(["claude", "gpt", "grok"]));

$("#autoAbs").addEventListener("change", (ev) => {
  state.autoAbsorb = ev.target.checked;
  try { chrome.storage.local.set({ omni_autoabsorb: state.autoAbsorb }); } catch (_) {}
});
$("#absThis").addEventListener("click", async () => {
  const e = extractLastCode();
  if (!e) { $("#absOut").textContent = "⚠️ 이 탭에서 코드 블록(pre code)이나 JSON을 찾지 못했습니다."; return; }
  const key = state.role || "local";
  state.lastHash = e.hash;
  await storeEntry(key, e);
  const ok = await copyText(e.code);
  $("#absOut").innerHTML = `✅ ${esc(key)} 코드 흡수: ${e.lines}줄 · ${fmtKB(e.bytes)} · ${esc(e.lang)} ${ok ? "· 클립보드 복사됨" : "· (복사 실패)"}`;
  renderArena();
});
$("#absAll").addEventListener("click", async () => {
  $("#absOut").textContent = "수거 중…";
  const r = await rt({ type: "OMNI_COLLECT", targets: AI_ROLES });
  $("#absOut").innerHTML = (r.results || []).map((x) => {
    const m = ROLE_META[x.role];
    return x.ok ? `✅ ${m.icon} ${esc(m.label)}: ${x.lines}줄 · ${fmtKB(x.bytes)}` : `⚠️ ${m.icon} ${esc(x.role)}: ${esc(x.error || "실패")}`;
  }).join("<br>") || "결과 없음";
  renderArena();
});
$("#absPage").addEventListener("click", async () => {
  const e = absorbPageText();
  if (!e) { $("#absOut").textContent = "⚠️ 흡수할 텍스트가 없습니다."; return; }
  await storeEntry("page", e);
  $("#absOut").innerHTML = `✅ ${e.kind === "selection" ? "선택 영역" : "화면 텍스트"} 흡수: ${e.lines}줄 · ${fmtKB(e.bytes)}`;
  renderArena();
});
$("#arena").addEventListener("click", async (ev) => {
  const btn = ev.target.closest("[data-act]");
  if (!btn) return;
  const card = btn.closest(".card");
  const role = card.dataset.role;
  const e = arenaCache[role];
  if (!e) return;
  const fn = card.querySelector(".fn").value.trim();
  if (btn.dataset.act === "copy") {
    toast((await copyText(e.code)) ? "📋 복사 완료" : "⚠️ 복사 실패");
  } else if (btn.dataset.act === "save") {
    const r = await rt({ type: "OMNI_SAVE", role, filename: fn, code: e.code, lang: e.lang });
    if (r && r.ok) { toast("💾 저장 완료: " + r.path, 4500); }
    else { downloadBlob(fn, e.code); toast("브리지 오프라인 → 브라우저 다운로드 폴더로 저장했습니다.", 4500); }
  } else if (btn.dataset.act === "queue") {
    const r = await rt({ type: "OMNI_QUEUE", role, filename: fn, code: e.code });
    toast(r && r.ok ? "📮 안총리 실행 큐에 등록했습니다 (자동 실행되지 않음)" : "⚠️ " + ((r && r.error) || "큐 등록 실패"), 4000);
  }
});

$$("[data-link]").forEach((b) => b.addEventListener("click", () => openLink(b.dataset.link)));
$("#cfgLinks").addEventListener("click", async () => {
  const cur = await rt({ type: "OMNI_GET_LINKS" });
  const l = (cur && cur.links) || {};
  const s = window.prompt("Google Sheets 『두뇌장바구니_헌법』 URL:", l.sheets || "https://");
  if (s && /^https?:\/\//i.test(s)) await rt({ type: "OMNI_SET_LINK", key: "sheets", url: s });
  const g = window.prompt("GitHub Actions 외부 주방 URL:", l.github || "https://");
  if (g && /^https?:\/\//i.test(g)) await rt({ type: "OMNI_SET_LINK", key: "github", url: g });
  toast("링크 설정을 저장했습니다.");
});
$("#chkStatus").addEventListener("click", checkStatus);

// ------------------------------------------------------------------ extension messages
chrome.runtime.onMessage.addListener((msg, _s, send) => {
  if (state.dead || !msg || typeof msg.type !== "string") return false;
  (async () => {
    switch (msg.type) {
      case "OMNI_INJECT_PROMPT": return injectPrompt(msg.prompt, msg.autoSend !== false);
      case "OMNI_GET_LAST_CODE": {
        const e = extractLastCode();
        return e ? { ok: true, entry: e } : { ok: false, error: "코드 블록(pre code)·JSON 없음" };
      }
      case "OMNI_TOGGLE": togglePanel(); return { ok: true };
      case "OMNI_PING": return { ok: true, role: state.role, ver: VER };
      case "OMNI_STATE_PING": if (state.open) renderArena(); return { ok: true };
      case "OMNI_SCROLL_STUDIO": {
        const el = document.querySelector("#studio-v5, #studioV5, [id*='studio' i]");
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
        return { ok: true };
      }
      default: return { ok: false, error: "unknown" };
    }
  })().then(send).catch((e) => send({ ok: false, error: String((e && e.message) || e) }));
  return true;
});
try {
  chrome.storage.onChanged.addListener((ch, area) => {
    if (state.dead || area !== "local") return;
    if (ch.omni_shared) {
      if (state.open) renderArena();
      if (IS_RGON) window.postMessage({ source: "rgon-omni-ext", type: "OMNI_SHARED_UPDATED", payload: { updated: Date.now() } }, location.origin);
    }
  });
  chrome.storage.local.get("omni_autoabsorb").then((o) => {
    if (typeof o.omni_autoabsorb === "boolean") { state.autoAbsorb = o.omni_autoabsorb; $("#autoAbs").checked = state.autoAbsorb; }
  }).catch(() => {});
} catch (_) {}
if (bc) bc.onmessage = (ev) => { if (ev.data && ev.data.type === "shared-updated" && state.open) renderArena(); };

// ------------------------------------------------------------------ rgon page <-> extension (window.postMessage)
if (IS_RGON) {
  window.addEventListener("message", async (ev) => {
    if (state.dead || ev.source !== window || ev.origin !== location.origin) return;
    const d = ev.data;
    if (!d || d.source !== "rgon-omni-page" || typeof d.type !== "string") return;
    const reply = (payload) => window.postMessage({ source: "rgon-omni-ext", type: "OMNI_REPLY", id: d.id, payload }, location.origin);
    const clean = (arr) => (Array.isArray(arr) ? arr : []).filter((x) => AI_ROLES.includes(x));
    try {
      switch (d.type) {
        case "OMNI_PING": return reply({ ok: true, ver: VER, role: state.role });
        case "OMNI_TOGGLE": togglePanel(); return reply({ ok: true });
        case "OMNI_SCAN": return reply(await rt({ type: "OMNI_SCAN" }));
        case "OMNI_DISPATCH": {
          const targets = clean(d.targets);
          const prompt = String(d.prompt || "").slice(0, 50000);
          if (!targets.length || !prompt.trim()) return reply({ ok: false, error: "대상 또는 지시문이 없습니다." });
          const perRole = {};
          if (d.grokPrefix && targets.includes("grok")) perRole.grok = GROK_PREFIX + prompt;
          return reply(await rt({ type: "OMNI_DISPATCH", targets, prompt, autoSend: d.autoSend !== false, perRole }));
        }
        case "OMNI_COLLECT": {
          const t = clean(d.targets);
          return reply(await rt({ type: "OMNI_COLLECT", targets: t.length ? t : AI_ROLES }));
        }
        case "OMNI_GET_SHARED": return reply(await rt({ type: "OMNI_GET_SHARED" }));
        case "OMNI_OPEN_LINK": return reply(await rt({ type: "OMNI_OPEN_LINK", key: String(d.key || "") }));
        case "OMNI_FOCUS": return reply(await rt({ type: "OMNI_FOCUS", role: String(d.role || "") }));
        default: return reply({ ok: false, error: "unknown" });
      }
    } catch (e) {
      reply({ ok: false, error: String((e && e.message) || e) });
    }
  });
  // 로컬 브리지 분배 큐 폴링 (독대실 탭에서만 수행)
  intervals.push(setInterval(async () => {
    if (state.dead) return;
    const r = await rt({ type: "OMNI_BRIDGE_POLL" });
    if (r && r.job) {
      toast("📥 브리지 분배 작업 수신 → 탭에 주입했습니다.");
      window.postMessage({ source: "rgon-omni-ext", type: "OMNI_JOB_DISPATCHED", payload: r }, location.origin);
    }
  }, 3000));
}

// ------------------------------------------------------------------ init
detectAndReport();
refreshScan();
intervals.push(setInterval(() => { if (!document.hidden) refreshScan(); }, 5000));
intervals.push(setInterval(() => { if (!document.hidden) detectAndReport(); }, 4000));
})();
"""

# ----------------------------------------------------------------------------
# omni_bridge.py (127.0.0.1 전용 로컬 브리지: 저장 / 큐 / 공유 메모리 / 분배 큐)
# ----------------------------------------------------------------------------
BRIDGE_PY = r"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# omni_bridge.py - RGON Omni-Link local bridge (127.0.0.1 only, token protected)
# 이 브리지는 파일 저장 / 큐 기록 / 공유 메모리 / 분배 큐만 담당하며, 받은 코드를 절대 실행하지 않습니다.
import hmac
import json
import os
import re
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__BASE_JSON__)
TOKEN = __TOKEN_JSON__
PORT = __BRIDGE_PORT__
VERSION = "__OMNI_VERSION__"

SHARED = BASE / "omni_shared_clipboard.json"
DISPATCH = BASE / "omni_dispatch_queue.json"
EXEC_Q = BASE / "anchongri_exec_queue.json"
QUEUE_DIR = BASE / "omni_queue"
LOCK = threading.Lock()
MAX_BODY = 8 * 1024 * 1024
ALLOWED_EXT = {"py", "js", "ts", "json", "html", "css", "md", "txt", "yml", "csv"}
LANG_EXT = {"python": "py", "javascript": "js", "typescript": "ts", "json": "json", "html": "html",
            "css": "css", "markdown": "md", "yaml": "yml", "csv": "csv"}
AI_ROLES = ("claude", "gpt", "grok")
ORIGINS = ("http://127.0.0.1:8501", "http://localhost:8501")


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def safe_name(name, lang):
    name = os.path.basename(str(name or "").replace("\\", "/"))
    name = re.sub(r"[^\w.\-]", "_", name, flags=re.UNICODE).lstrip(".")
    stem, ext = os.path.splitext(name)
    ext = ext.lower().lstrip(".")
    if ext not in ALLOWED_EXT:
        stem = (name or "omni_code").replace(".", "_")
        ext = LANG_EXT.get(str(lang or "").lower(), "txt")
    stem = (stem or "omni_code")[:80]
    return stem, ext


def unique_path(folder, stem, ext):
    p = Path(folder) / (stem + "." + ext)
    n = 1
    while p.exists():
        p = Path(folder) / ("%s_%d.%s" % (stem, n, ext))
        n += 1
    return p


def write_text_file(folder, filename, code, lang):
    stem, ext = safe_name(filename, lang)
    Path(folder).mkdir(parents=True, exist_ok=True)
    p = unique_path(folder, stem, ext)
    if p.resolve().parent != Path(folder).resolve():
        raise ValueError("invalid path")
    tmp = p.with_name(p.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(str(code))
    os.replace(tmp, p)
    return p


def queue_items(q):
    if isinstance(q, list):
        return q
    if isinstance(q, dict):
        for k in ("queue", "items", "jobs"):
            if isinstance(q.get(k), list):
                return q[k]
        q["queue"] = []
        return q["queue"]
    return []


def find_mp4(limit=5):
    out = []
    root = str(BASE)
    for dp, dn, fn in os.walk(root):
        depth = dp[len(root):].count(os.sep)
        if depth >= 3:
            dn[:] = []
        else:
            dn[:] = [d for d in dn if d not in ("backups", "node_modules", ".git", "__pycache__")]
        for f in fn:
            if f.lower().endswith(".mp4"):
                p = os.path.join(dp, f)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                out.append({"name": os.path.relpath(p, root), "size_kb": round(st.st_size / 1024), "mtime": st.st_mtime,
                            "mtime_str": time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))})
    out.sort(key=lambda x: x["mtime"], reverse=True)
    return out[:limit]


def pending_count(path):
    items = queue_items(load_json(path, []))
    return sum(1 for i in items if isinstance(i, dict) and i.get("status") in (None, "pending"))


class Handler(BaseHTTPRequestHandler):
    server_version = "OmniBridge/6"

    def log_message(self, fmt, *args):
        sys.stderr.write("[bridge] " + (fmt % args) + "\n")

    def _origin_ok(self):
        o = self.headers.get("Origin")
        return (not o) or o.startswith("chrome-extension://") or o in ORIGINS

    def _cors(self):
        o = self.headers.get("Origin")
        if o and self._origin_ok():
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "X-Omni-Token, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _auth(self):
        if not self._origin_ok():
            return False
        got = (self.headers.get("X-Omni-Token") or "").encode("utf-8")
        return hmac.compare_digest(got, TOKEN.encode("utf-8"))

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return {}
        if n > MAX_BODY:
            raise ValueError("body too large")
        return json.loads(self.rfile.read(n).decode("utf-8"))

    def do_OPTIONS(self):
        if not self._origin_ok():
            return self._send(403, {"ok": False, "error": "origin"})
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if not self._auth():
            return self._send(401, {"ok": False, "error": "unauthorized"})
        path = self.path.split("?")[0]
        try:
            if path == "/api/health":
                return self._send(200, {"ok": True, "version": VERSION, "base": str(BASE)})
            if path == "/api/status":
                return self._send(200, {"ok": True, "studio_mp4": find_mp4(),
                                        "exec_queue_pending": pending_count(EXEC_Q),
                                        "dispatch_queue_pending": pending_count(DISPATCH)})
            if path == "/api/shared":
                return self._send(200, {"ok": True, "shared": load_json(SHARED, {"entries": {}, "history": []})})
            if path == "/api/dispatch/next":
                with LOCK:
                    q = load_json(DISPATCH, [])
                    items = queue_items(q)
                    job = next((j for j in items if isinstance(j, dict) and j.get("status") == "pending"), None)
                    if job:
                        job["status"] = "sent"
                        job["sent_at"] = time.time()
                        save_json(DISPATCH, q)
                return self._send(200, {"ok": True, "job": job})
            return self._send(404, {"ok": False, "error": "not found"})
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})

    def do_POST(self):
        if not self._auth():
            return self._send(401, {"ok": False, "error": "unauthorized"})
        path = self.path.split("?")[0]
        try:
            data = self._body()
            if path == "/api/shared":
                role = str(data.get("role") or "")[:40]
                entry = data.get("entry")
                if not role or not isinstance(entry, dict):
                    return self._send(400, {"ok": False, "error": "invalid"})
                with LOCK:
                    sh = load_json(SHARED, {"entries": {}, "history": []})
                    sh.setdefault("entries", {})[role] = entry
                    hist = sh.setdefault("history", [])
                    hist.insert(0, {"role": role, "ts": entry.get("ts"), "lines": entry.get("lines"),
                                    "bytes": entry.get("bytes"), "lang": entry.get("lang"), "hash": entry.get("hash")})
                    sh["history"] = hist[:40]
                    sh["updated"] = time.time()
                    save_json(SHARED, sh)
                return self._send(200, {"ok": True})
            if path == "/api/save":
                p = write_text_file(BASE, data.get("filename"), data.get("code", ""), data.get("lang"))
                return self._send(200, {"ok": True, "path": str(p)})
            if path == "/api/queue":
                p = write_text_file(QUEUE_DIR, data.get("filename"), data.get("code", ""), None)
                with LOCK:
                    q = load_json(EXEC_Q, [])
                    items = queue_items(q)
                    job = {"id": uuid.uuid4().hex[:12], "source": "omni-link", "role": str(data.get("role") or ""),
                           "file": str(p), "status": "pending", "ts": time.time()}
                    items.append(job)
                    save_json(EXEC_Q, q)
                return self._send(200, {"ok": True, "id": job["id"], "path": str(p)})
            if path == "/api/dispatch":
                targets = [t for t in (data.get("targets") or []) if t in AI_ROLES]
                prompt = str(data.get("prompt") or "")[:50000]
                if not targets or not prompt.strip():
                    return self._send(400, {"ok": False, "error": "targets/prompt required"})
                per = data.get("perRole") if isinstance(data.get("perRole"), dict) else {}
                per = {k: str(v)[:60000] for k, v in per.items() if k in AI_ROLES}
                with LOCK:
                    q = load_json(DISPATCH, [])
                    items = queue_items(q)
                    job = {"id": uuid.uuid4().hex[:12], "targets": targets, "prompt": prompt, "perRole": per,
                           "autoSend": data.get("autoSend") is not False, "status": "pending", "ts": time.time()}
                    items.append(job)
                    del items[:-200]
                    save_json(DISPATCH, q)
                return self._send(200, {"ok": True, "id": job["id"]})
            return self._send(404, {"ok": False, "error": "not found"})
        except Exception as e:
            return self._send(500, {"ok": False, "error": str(e)})


def main():
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as e:
        print("포트 %d 를 열 수 없습니다 (이미 실행 중일 수 있음): %s" % (PORT, e))
        return 1
    print("RGON Omni-Link bridge v%s listening on http://127.0.0.1:%d (base=%s)" % (VERSION, PORT, BASE))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""

BAT_TEXT = (
    "@echo off\n"
    "chcp 65001 >nul\n"
    "cd /d \"%~dp0\"\n"
    "echo Starting RGON Omni-Link bridge on 127.0.0.1:" + str(BRIDGE_PORT) + " ...\n"
    "python omni_bridge.py\n"
    "pause\n"
).replace("\n", "\r\n")

# ----------------------------------------------------------------------------
# 독대실 HTML 삽입 블록 (STUDIO v5 / 어도비 3대장 블록은 건드리지 않고 상단에 추가만 함)
# ----------------------------------------------------------------------------
HTML_BEGIN = "<!-- OMNI-LINK:BEGIN -->"
HTML_END = "<!-- OMNI-LINK:END -->"
HTML_BLOCK = HTML_BEGIN + r"""
<div id="omniLinkController" style="margin:10px auto;max-width:1100px;padding:12px 16px;border-radius:16px;color:#e9ecff;background:linear-gradient(135deg,rgba(60,40,160,.88),rgba(0,110,160,.78));border:1px solid rgba(255,255,255,.25);box-shadow:0 8px 28px rgba(60,40,200,.3);font-family:'Pretendard','Noto Sans KR',system-ui,sans-serif">
  <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center">
    <button id="omniOpenBtn" type="button" style="padding:10px 16px;font-size:14px;font-weight:700;color:#fff;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.45);border-radius:12px;cursor:pointer">[✨ AI 만능 소통창 (르곤⇄클로드⇄GPT⇄그록 직결 허브) 열기]</button>
    <span id="omniExtState" style="font-size:12px;opacity:.9">확장프로그램 확인 중…</span>
  </div>
  <details style="margin-top:8px">
    <summary style="cursor:pointer;font-size:13px">⚡ 독대실에서 바로 분배하기 (Claude / GPT / Grok)</summary>
    <textarea id="omniPrompt" rows="4" placeholder="사령관 지시문 — 열려 있는 AI 탭 입력창에 자동으로 주입됩니다." style="width:100%;box-sizing:border-box;margin-top:8px;padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,.3);background:rgba(0,0,0,.35);color:#fff"></textarea>
    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px">
      <label style="font-size:12px"><input type="checkbox" id="omniAutoSend" checked> 자동 전송</label>
      <button type="button" data-omni-fire="claude,gpt" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(16,185,129,.55);color:#fff;cursor:pointer">🚀 Claude + GPT 동시 발사</button>
      <button type="button" data-omni-fire="grok" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(245,158,11,.55);color:#fff;cursor:pointer">🎯 Grok 카피 발사</button>
      <button type="button" id="omniCollectBtn" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(0,150,255,.5);color:#fff;cursor:pointer">🧲 AI 탭 코드 수거</button>
    </div>
    <pre id="omniOut" style="white-space:pre-wrap;font-size:12px;margin:8px 0 0;padding:8px;border-radius:10px;background:rgba(0,0,0,.3)">대기 중…</pre>
  </details>
</div>
<script>
(function () {
  var pending = {}, seq = 0;
  var stateEl = document.getElementById("omniExtState");
  var outEl = document.getElementById("omniOut");
  function call(type, data) {
    return new Promise(function (resolve) {
      var id = "o" + (++seq);
      pending[id] = resolve;
      window.postMessage(Object.assign({ source: "rgon-omni-page", type: type, id: id }, data || {}), location.origin);
      setTimeout(function () {
        if (pending[id]) { delete pending[id]; resolve({ ok: false, error: "확장프로그램 응답 없음 (RGON Omni-Link 확장 로드/새로고침 확인)" }); }
      }, 8000);
    });
  }
  window.addEventListener("message", function (ev) {
    if (ev.source !== window || ev.origin !== location.origin) return;
    var d = ev.data;
    if (!d || d.source !== "rgon-omni-ext") return;
    if (d.type === "OMNI_REPLY" && pending[d.id]) { var f = pending[d.id]; delete pending[d.id]; f(d.payload || {}); }
    else if (d.type === "OMNI_SHARED_UPDATED") { summarize(); }
    else if (d.type === "OMNI_JOB_DISPATCHED") { outEl.textContent = "📥 브리지 작업이 탭에 주입되었습니다."; }
  });
  function fmt(results) {
    return (results || []).map(function (r) {
      return (r.ok ? "✅ " : "⚠️ ") + r.role + ": " + (r.ok ? (r.sent ? "입력+전송 완료" : "입력 완료") : (r.error || "실패"));
    }).join("\n") || "결과 없음";
  }
  async function summarize() {
    var r = await call("OMNI_GET_SHARED");
    var en = (r.shared && r.shared.entries) || {};
    var parts = ["claude", "gpt", "grok"].filter(function (k) { return en[k]; }).map(function (k) {
      return k + ": " + en[k].lines + "줄 / " + (en[k].bytes / 1024).toFixed(1) + "KB / 함수 " + (en[k].funcCount || 0) + "개";
    });
    if (parts.length) outEl.textContent = "🧲 흡수 현황\n" + parts.join("\n");
  }
  document.getElementById("omniOpenBtn").addEventListener("click", async function () {
    var r = await call("OMNI_TOGGLE");
    if (!r.ok) stateEl.textContent = "⚠️ " + (r.error || "확장프로그램 미연결");
  });
  document.querySelectorAll("[data-omni-fire]").forEach(function (b) {
    b.addEventListener("click", async function () {
      var targets = b.getAttribute("data-omni-fire").split(",");
      var prompt = document.getElementById("omniPrompt").value;
      if (!prompt.trim()) { outEl.textContent = "지시문을 입력하세요."; return; }
      outEl.textContent = "발사 중…";
      var r = await call("OMNI_DISPATCH", { targets: targets, prompt: prompt, autoSend: document.getElementById("omniAutoSend").checked, grokPrefix: targets.indexOf("grok") >= 0 });
      outEl.textContent = r.results ? fmt(r.results) : "⚠️ " + (r.error || "실패");
    });
  });
  document.getElementById("omniCollectBtn").addEventListener("click", async function () {
    outEl.textContent = "수거 중…";
    var r = await call("OMNI_COLLECT", { targets: ["claude", "gpt", "grok"] });
    outEl.textContent = (r.results || []).map(function (x) {
      return (x.ok ? "✅ " : "⚠️ ") + x.role + ": " + (x.ok ? (x.lines + "줄 / " + (x.bytes / 1024).toFixed(1) + "KB") : (x.error || "실패"));
    }).join("\n") || ("⚠️ " + (r.error || "결과 없음"));
  });
  call("OMNI_PING").then(function (r) {
    stateEl.textContent = r.ok ? "🟢 확장프로그램 연결됨 v" + r.ver : "🔴 확장프로그램 미연결 — chrome://extensions 에서 rgon_aside_extension 로드/새로고침";
    if (r.ok) summarize();
  });
})();
</script>
""" + HTML_END + "\n"


def log(msg):
    print(msg, flush=True)


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".omni_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def render(template, token):
    return (template.replace("__OMNI_VERSION__", OMNI_VERSION)
            .replace("__BRIDGE_PORT__", str(BRIDGE_PORT))
            .replace("__OMNI_TOKEN__", token)
            .replace("__BASE_JSON__", json.dumps(str(BASE)))
            .replace("__TOKEN_JSON__", json.dumps(token)))


def backup_file(path):
    path = Path(path)
    if not path.exists():
        return False
    rel = path.relative_to(BASE)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)
    return True


def validate_js(files):
    node = shutil.which("node")
    if not node:
        log("⚠️ node 를 찾지 못해 JS 문법 검증을 건너뜁니다. (Node.js 설치 후 재실행 권장)")
        return True
    ok = True
    with tempfile.TemporaryDirectory(prefix="omni_chk_") as td:
        for name, text in files.items():
            p = Path(td) / name
            p.write_text(text, encoding="utf-8")
            r = subprocess.run([node, "--check", str(p)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode == 0:
                log("   ✅ node --check 통과: " + name)
            else:
                ok = False
                log("   ❌ node --check 실패: " + name + "\n" + (r.stderr or r.stdout))
    return ok


def patch_html(path):
    raw = path.read_bytes()
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        log("   ⚠️ UTF-8이 아니어서 건너뜀: " + str(path))
        return False
    stripped = re.sub(re.escape(HTML_BEGIN) + r".*?" + re.escape(HTML_END) + r"\s*", "", html, flags=re.S)
    m = re.search(r"<body[^>]*>", stripped, flags=re.I)
    if m:
        new = stripped[:m.end()] + "\n" + HTML_BLOCK + stripped[m.end():]
    else:
        new = HTML_BLOCK + stripped
    if new.replace(HTML_BLOCK, "", 1).replace("\n", "", 1) != stripped and new.replace(HTML_BLOCK, "", 1) != stripped:
        raise RuntimeError("HTML 보존 검증 실패: " + str(path))
    for kw in ("studio", "STUDIO", "firefly", "Firefly"):
        if stripped.count(kw) != new.count(kw) - HTML_BLOCK.count(kw):
            raise RuntimeError("기존 블록 보존 검증 실패(" + kw + "): " + str(path))
    backup_file(path)
    atomic_write(path, new)
    return True


def main():
    log("=" * 64)
    log("✨ RGON Omni-Link Hub v%s 설치·조립 시작" % OMNI_VERSION)
    log("   대상 폴더: %s" % BASE)
    log("=" * 64)
    try:
        BASE.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log("❌ 설치 폴더를 만들 수 없습니다: %s" % e)
        return 1

    token = secrets.token_hex(16)
    background = render(BACKGROUND_JS, token).lstrip("\n")
    content = render(CONTENT_JS, token).lstrip("\n")
    bridge = render(BRIDGE_PY, token)
    manifest_text = json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n"

    log("[1/5] 사전 검증 (적용 전 문법 검사)")
    if not validate_js({"background.js": background, "content_aside_bar.js": content}):
        log("❌ JS 문법 오류 — 기존 파일을 건드리지 않고 중단합니다.")
        return 1
    try:
        compile(bridge, "omni_bridge.py", "exec")
        json.loads(manifest_text)
        log("   ✅ omni_bridge.py 컴파일 / manifest.json 파싱 통과")
    except Exception as e:
        log("❌ 검증 실패: %s" % e)
        return 1

    log("[2/5] 기존 파일 백업 → %s" % BACKUP_DIR)
    targets = [
        EXT_DIR / "manifest.json", EXT_DIR / "background.js", EXT_DIR / "content_aside_bar.js",
        BASE / "omni_bridge.py", BASE / "start_omni_bridge.bat",
        BASE / "omni_shared_clipboard.json", BASE / "omni_dispatch_queue.json", BASE / "anchongri_exec_queue.json",
    ]
    n_bak = sum(1 for t in targets if backup_file(t))
    log("   백업된 기존 파일: %d개" % n_bak)

    log("[3/5] 확장프로그램 v6 / 로컬 브리지 적용 (원자적 교체)")
    try:
        atomic_write(EXT_DIR / "manifest.json", manifest_text)
        atomic_write(EXT_DIR / "background.js", background)
        atomic_write(EXT_DIR / "content_aside_bar.js", content)
        atomic_write(BASE / "omni_bridge.py", bridge)
        atomic_write(BASE / "start_omni_bridge.bat", BAT_TEXT)
        if not (BASE / "omni_shared_clipboard.json").exists():
            atomic_write(BASE / "omni_shared_clipboard.json", json.dumps({"entries": {}, "history": [], "updated": 0}, ensure_ascii=False, indent=2))
        if not (BASE / "omni_dispatch_queue.json").exists():
            atomic_write(BASE / "omni_dispatch_queue.json", "[]\n")
        if not (BASE / "anchongri_exec_queue.json").exists():
            atomic_write(BASE / "anchongri_exec_queue.json", "[]\n")
        log("   ✅ manifest.json / background.js / content_aside_bar.js / omni_bridge.py / start_omni_bridge.bat")
    except Exception as e:
        log("❌ 파일 쓰기 실패: %s\n   백업 폴더에서 복원할 수 있습니다: %s" % (e, BACKUP_DIR))
        return 1

    log("[4/5] 독대실 HTML 패치 (STUDIO v5 · 어도비 3대장 블록 보존)")
    patched = 0
    for rel in ("rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"):
        p = BASE / rel
        if not p.exists():
            log("   ⏭️  없음(건너뜀): " + rel)
            continue
        try:
            if patch_html(p):
                patched += 1
                log("   ✅ 패치 완료: " + rel)
        except Exception as e:
            log("   ❌ 패치 실패(원본 유지): %s — %s" % (rel, e))

    log("[5/5] 설치 후 재검증")
    if not validate_js({"background.js": (EXT_DIR / "background.js").read_text(encoding="utf-8"),
                        "content_aside_bar.js": (EXT_DIR / "content_aside_bar.js").read_text(encoding="utf-8")}):
        log("❌ 설치 후 검증 실패 — 백업 폴더에서 복원하세요: %s" % BACKUP_DIR)
        return 1

    log("")
    log("📌 다음 단계")
    log("  1) Chrome → chrome://extensions → 개발자 모드 → 'rgon_aside_extension' 로드 (이미 로드했다면 새로고침 ↻)")
    log("  2) 저장·큐·MP4 상태 기능을 쓰려면 start_omni_bridge.bat 실행 (기존 브리지가 켜져 있으면 껐다가 다시 실행)")
    log("  3) 이미 열려 있던 AI 탭은 새로고침 후 우측 상단 '✨ 르곤 만능 소통창' 배지를 확인하세요. (단축키 Alt+Shift+O)")
    log("  ※ 안총리 실행 큐는 '기록만' 하며 코드를 자동 실행하지 않습니다. 실행 전 내용을 검토하세요.")
    log("  ※ 독대실 HTML 패치 수: %d" % patched)
    log("OMNI-LINK AI COMMUNICATOR READY!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
