// RGON Omni-Link core v6.0.3
const OMNI_VERSION = "6.0.3";
const BRIDGE = "http://127.0.0.1:8765";

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
