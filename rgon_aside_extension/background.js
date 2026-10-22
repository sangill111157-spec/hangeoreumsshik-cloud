"use strict";
// RGON Omni-Link v6.0.0 - background service worker (multi-tab neural router)

const OMNI_VERSION = "6.0.0";
const BRIDGE = "http://127.0.0.1:8765";
const OMNI_TOKEN = "bfd63676bb00046db6e55eaf2d631652";
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
