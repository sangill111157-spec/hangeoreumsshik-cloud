"use strict";
// RGON Omni-Link v6.0.0 - background service worker (multi-tab neural router)

const OMNI_VERSION = "6.0.6";
const BRIDGE = "http://127.0.0.1:8765";
const OMNI_TOKEN = "9c5330679c10470c340860488caed5c6";
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

// ---- v6.0.2: 흡수함 자동 삭제 / Copy 정화 헬퍼 (OMNI_V602_HELPERS)
const ROUND_WINDOW_MS = 30 * 60 * 1000;
const COPY_RE = /^Copy\s*/i;

async function isAutoClean() {
  return (await getStore("omni_autoclean", true)) !== false;
}

function sanitizeEntry(e) {
  if (!e || typeof e.code !== "string" || e.kind === "page" || e.kind === "selection" || !COPY_RE.test(e.code)) return false;
  e.code = e.code.replace(COPY_RE, "");
  e.lines = e.code.split("\n").length;
  e.bytes = new TextEncoder().encode(e.code).length;
  return true;
}

function emptyShared() {
  return { entries: {}, history: [], updated: Date.now() };
}

async function loadShared() {
  return withLock(async () => {
    const sh = await getStore("omni_shared", { entries: {}, history: [] });
    sh.entries = sh.entries || {};
    sh.history = sh.history || [];
    let dirty = false;
    for (const k of Object.keys(sh.entries)) {
      if (sanitizeEntry(sh.entries[k])) dirty = true;
    }
    if (dirty) await setStore("omni_shared", sh);
    return sh;
  });
}

async function clearShared(role, wait) {
  const sh = await withLock(async () => {
    let cur;
    if (!role) {
      cur = emptyShared();
    } else {
      cur = await getStore("omni_shared", emptyShared());
      cur.entries = cur.entries || {};
      cur.history = (cur.history || []).filter((h) => h.role !== role);
      delete cur.entries[role];
      cur.updated = Date.now();
    }
    await setStore("omni_shared", cur);
    return cur;
  });
  const p = bridgeFetch("/api/shared/replace", "POST", { shared: sh });
  if (wait) await p;
  broadcastAll({ type: "OMNI_STATE_PING", role: role || "*" });
  return sh;
}

async function maybeAutoClean() {
  await setStore("omni_round_ts", Date.now());
  if (await isAutoClean()) {
    await clearShared(null, true);
    return true;
  }
  return false;
}


// ---- v6.0.3: 커스텀 신경망 역할 (Custom Neural Roles) 지원 ----
async function getCustomRoles() {
  const o = await chrome.storage.local.get("omni_custom_roles");
  return o.omni_custom_roles || {};
}
async function setCustomRoles(roles) {
  await chrome.storage.local.set({ omni_custom_roles: roles });
}

// ---------------------------------------------------------------- role mapping
function roleFromText(s) {
  s = String(s || "");
  if (/claude/i.test(s)) return "claude";
  if (/gpt[-\s]?\d|chatgpt/i.test(s)) return "gpt";
  if (/grok/i.test(s)) return "grok";
  return null;
}

function guessRole(tab, reported, override, customRoles) {
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
  if (customRoles) {
    for (const [ckey, cmeta] of Object.entries(customRoles)) {
      if (!cmeta) continue;
      if (cmeta.url && tab.url && (tab.url === cmeta.url || tab.url.startsWith(cmeta.url))) return ckey;
      if (cmeta.origin && u.origin && u.origin.toLowerCase() === cmeta.origin.toLowerCase()) return ckey;
    }
  }
  return null;
}

async function scanTabs() {
  const [tabs, rep, ovr, customs] = await Promise.all([
    chrome.tabs.query({}),
    getStore("omni_reported", {}),
    getStore("omni_override", {}),
    getStore("omni_custom_roles", {})
  ]);
  const list = [];
  const byRole = {};
  for (const t of tabs) {
    if (!t.id) continue;
    const r = rep[t.id] ? rep[t.id].role : null;
    const role = guessRole(t, r, ovr[t.id], customs);
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
  return { list, byRole, customRoles: customs };
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
  if ((targets || []).some((r) => pickTab(byRole[r]))) await maybeAutoClean();
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

async function storeShared(role, entry, opts) {
  sanitizeEntry(entry);
  let trimmed = false;
  const sh = await withLock(async () => {
    const cur = await getStore("omni_shared", { entries: {}, history: [] });
    cur.entries = cur.entries || {};
    cur.history = cur.history || [];
    if (opts && opts.trimStale && (await isAutoClean())) {
      const roundTs = await getStore("omni_round_ts", 0);
      const limit = Math.max(roundTs, (entry.ts || Date.now()) - ROUND_WINDOW_MS);
      for (const k of Object.keys(cur.entries)) {
        const ets = (cur.entries[k] && cur.entries[k].ts) || 0;
        if (k !== role && ets < limit) { delete cur.entries[k]; trimmed = true; }
      }
      if (trimmed) cur.history = cur.history.filter((h) => h.role === role || !!cur.entries[h.role]);
    }
    cur.entries[role] = entry;
    cur.history.unshift({ role, ts: entry.ts, lines: entry.lines, bytes: entry.bytes, lang: entry.lang, hash: entry.hash, url: entry.url });
    cur.history = cur.history.slice(0, 40);
    cur.updated = Date.now();
    try {
      await setStore("omni_shared", cur);
    } catch (e) {
      entry.code = String(entry.code || "").slice(0, 100000);
      await setStore("omni_shared", cur);
    }
    return cur;
  });
  if (trimmed) bridgeFetch("/api/shared/replace", "POST", { shared: sh }).catch(() => {});
  else bridgeFetch("/api/shared", "POST", { role, entry }).catch(() => {});
  broadcastAll({ type: "OMNI_STATE_PING", role });
}

async function collect(targets) {
  const { byRole } = await scanTabs();
  const got = [];
  const results = await Promise.all((targets || []).map(async (role) => {
    const t = pickTab(byRole[role]);
    if (!t) return { role, ok: false, error: "열려 있는 탭 없음" };
    const r = await sendToTab(t.tabId, { type: "OMNI_GET_LAST_CODE" });
    if (r && r.ok && r.entry) {
      r.entry.role = role;
      sanitizeEntry(r.entry);
      got.push({ role, entry: r.entry });
      return { role, ok: true, lines: r.entry.lines, bytes: r.entry.bytes };
    }
    return { role, ok: false, error: (r && r.error) || "코드 블록 없음" };
  }));
  let cleaned = false;
  if (got.length) {
    if (await isAutoClean()) { await clearShared(null, true); cleaned = true; }
    for (const g of got) await storeShared(g.role, g.entry);
  }
  return { ok: results.some((x) => x.ok), results, cleaned };
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
    case "OMNI_GET_CUSTOM_ROLES":
      return { ok: true, customRoles: await getCustomRoles() };
    case "OMNI_SET_CUSTOM_ROLE": {
      const cr = await getCustomRoles();
      if (msg.roleKey && msg.roleMeta) {
        cr[msg.roleKey] = msg.roleMeta;
        await setCustomRoles(cr);
      }
      return { ok: true, customRoles: cr };
    }
    case "OMNI_DEL_CUSTOM_ROLE": {
      const cr = await getCustomRoles();
      if (msg.roleKey && cr[msg.roleKey]) {
        delete cr[msg.roleKey];
        await setCustomRoles(cr);
      }
      return { ok: true, customRoles: cr };
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
      const { list, byRole, customRoles } = await scanTabs();
      const counts = {};
      Object.keys(byRole).forEach((k) => (counts[k] = byRole[k].length));
      return { ok: true, version: OMNI_VERSION, list, counts, customRoles, selfTabId: sender.tab ? sender.tab.id : null };
    }
    case "OMNI_DISPATCH":
      return dispatch(msg.targets, msg.prompt, msg.autoSend, msg.perRole);
    case "OMNI_COLLECT":
      return collect(msg.targets && msg.targets.length ? msg.targets : AI_ROLES);
    case "OMNI_STORE_SHARED":
      if (!msg.role || !msg.entry) return { ok: false, error: "invalid" };
      await storeShared(msg.role, msg.entry, { trimStale: !!msg.auto });
      return { ok: true };
    case "OMNI_GET_SHARED":
      return { ok: true, shared: await loadShared() };
    case "OMNI_CLEAR_SHARED":
      await clearShared(msg.role ? String(msg.role) : null);
      return { ok: true, cleared: msg.role || "all" };
    case "OMNI_SET_AUTOCLEAN":
      await setStore("omni_autoclean", msg.value !== false);
      return { ok: true, value: msg.value !== false };
    case "OMNI_GET_AUTOCLEAN":
      return { ok: true, value: await isAutoClean() };
            case "OMNI_FOCUS": {
      const { byRole, customRoles } = await scanTabs();
      const t = pickTab(byRole[msg.role]);
      if (t) {
        await focusTab(t);
        return { ok: true, focused: true };
      }
      const cmeta = (customRoles && customRoles[msg.role]) || (await getStore("omni_custom_roles", {}))[msg.role];
      if (cmeta && cmeta.url) {
        return openUrl(cmeta.url);
      }
      return { ok: false, error: "열려 있는 탭 없음" };
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
