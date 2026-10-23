/* [RGON-SHADOW-OPEN-START] */
;(function () {
  try {
    if (typeof Element === 'undefined' || !Element.prototype.attachShadow) return;
    if (Element.prototype.__rgonShadowPatched) return;
    var orig = Element.prototype.attachShadow;
    Object.defineProperty(Element.prototype, '__rgonShadowPatched', { value: true });
    Element.prototype.attachShadow = function (init) {
      var opts = Object.assign({}, init || {}, { mode: 'open' });
      return orig.call(this, opts);
    };
  } catch (e) {}
})();
/* [RGON-SHADOW-OPEN-END] */
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

/* [RGON-4BTN-V12-START] step12 자동 생성 블록 - 수동 편집 금지 */
;(function () {
  'use strict';
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  if (window.__RGON_4BTN_V12__) return;
  window.__RGON_4BTN_V12__ = true;

  var MARK = 'data-rgon-v12';
  var CODE_SEL = 'textarea, pre, code, [contenteditable="true"]';
  var CARD_SEL = '[class*="card" i], [class*="item" i], [class*="result" i], [data-card], article, li, details';

  function txt(el) { return ((el && (el.innerText || el.textContent)) || '').replace(/\s+/g, ' ').trim(); }
  function ours(b) { return b.hasAttribute(MARK) || !!b.closest('[' + MARK + ']'); }
  function isSave(b) { return !ours(b) && txt(b).indexOf('shin-agent 저장') !== -1; }
  function isQueue(b) { return !ours(b) && txt(b).indexOf('안총리') !== -1; }
  function is(b) { var t = txt(b); return !ours(b) && t.indexOf('복사') !== -1 && t.indexOf('흡수') === -1; }
  function isTopAbsorb(b) {
    var t = txt(b);
    return !ours(b) && (t.indexOf('이 탭 코드 흡수') !== -1 || t.indexOf('화면 텍스트 흡수') !== -1);
  }

  /* ---------- DOM 탐색 (open shadow root 포함) ---------- */
  var observed = new WeakSet();
  function roots() {
    var out = [document];
    (function walk(r) {
      var all = r.querySelectorAll('*');
      for (var i = 0; i < all.length; i++) {
        if (all[i].shadowRoot) { out.push(all[i].shadowRoot); walk(all[i].shadowRoot); }
      }
    })(document);
    return out;
  }
  function buttons(pred) {
    var res = [];
    roots().forEach(function (r) {
      r.querySelectorAll('button, [role="button"]').forEach(function (b) { if (pred(b)) res.push(b); });
    });
    return res;
  }
  function css(el, obj) { for (var k in obj) el.style.setProperty(k, obj[k], 'important'); }

  var BTN_CSS = {
    'overflow': 'visible', 'text-overflow': 'clip', 'white-space': 'normal',
    'word-break': 'keep-all', 'overflow-wrap': 'anywhere',
    'padding': '7px 10px', 'font-size': '12px', 'line-height': '1.3',
    'min-width': '0', 'max-width': 'none', 'width': '100%', 'height': 'auto',
    'min-height': '32px', 'box-sizing': 'border-box', 'text-align': 'center'
  };
  function styleBtn(b) {
    css(b, BTN_CSS);
    b.querySelectorAll('*').forEach(function (c) {
      css(c, { 'overflow': 'visible', 'text-overflow': 'clip', 'white-space': 'normal', 'max-width': 'none' });
    });
  }

  /* ---------- 카드 컨테이너 찾기 ---------- */
  function countSaves(el, saves) { var n = 0; saves.forEach(function (s) { if (el.contains(s)) n++; }); return n; }
  function hasTop(el, tops) { return tops.some(function (t) { return el.contains(t); }); }
  function findCard(btn, saves, tops) {
    var A = null, el = btn.parentElement, depth = 0;
    while (el && el !== document.body && el !== document.documentElement && depth < 8) {
      if (countSaves(el, saves) > 1 || hasTop(el, tops)) break;
      if (el.querySelector(CODE_SEL)) { A = el; break; }
      el = el.parentElement; depth++;
    }
    var C = btn.closest(CARD_SEL);
    if (C && C !== document.body && countSaves(C, saves) === 1 && !hasTop(C, tops) &&
        (!A || C.contains(A))) return C;
    return A || btn.parentElement;
  }

  /* ---------- 지우기 동작 ---------- */
  function setVal(f, v) {
    var proto = f.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    var d = Object.getOwnPropertyDescriptor(proto, 'value');
    if (d && d.set) d.set.call(f, v); else f.value = v;
    f.dispatchEvent(new Event('input', { bubbles: true }));
    f.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function clearFields(scope) {
    scope.querySelectorAll('textarea, input[type="text"], input[type="search"], input:not([type])')
      .forEach(function (f) { if (!ours(f)) setVal(f, ''); });
    scope.querySelectorAll('pre').forEach(function (p) { p.textContent = ''; });
    scope.querySelectorAll('code').forEach(function (c) { if (!c.closest('pre')) c.textContent = ''; });
    scope.querySelectorAll('[contenteditable="true"]').forEach(function (c) { c.textContent = ''; });
  }
  function hideCard(card) {
    clearFields(card);
    css(card, { 'display': 'none' });
    card.setAttribute('data-rgon-v12-hidden', '1');
    card.__rgonV12Snap = txt(card);
  }
  function toast(msg) {
    try {
      var t = document.createElement('div');
      t.setAttribute(MARK, 'toast');
      t.textContent = msg;
      css(t, { 'position': 'fixed', 'left': '50%', 'bottom': '18px', 'transform': 'translateX(-50%)',
        'background': '#222', 'color': '#fff', 'padding': '8px 14px', 'border-radius': '8px',
        'font-size': '12px', 'z-index': '2147483647', 'opacity': '0.95' });
      document.body.appendChild(t);
      setTimeout(function () { t.remove(); }, 1600);
    } catch (e) {}
  }
  function clearAll(ask) {
    if (ask && !window.confirm('흡수창의 모든 카드와 입력창을 비울까요?')) return;
    var saves = buttons(isSave), tops = buttons(isTopAbsorb);
    saves.forEach(function (s) { hideCard(findCard(s, saves, tops)); });
    roots().forEach(function (r) {
      r.querySelectorAll('textarea').forEach(function (f) { if (!ours(f)) setVal(f, ''); });
    });
    try {
      var keys = window.RGON_V12_STORAGE_KEYS;  /* 필요 시 저장소 키 배열 지정 */
      if (Array.isArray(keys) && keys.length && window.chrome && chrome.storage && chrome.storage.local) {
        chrome.storage.local.remove(keys);
      }
    } catch (e) {}
    try { window.dispatchEvent(new CustomEvent('rgon:clear-all')); } catch (e) {}
    toast('🗑️ 흡수창을 모두 비웠습니다');
  }

  function makeBtn(label, kind, onClick) {
    var b = document.createElement('button');
    b.type = 'button';
    b.setAttribute(MARK, kind);
    b.textContent = label;
    b.title = label;
    styleBtn(b);
    css(b, { 'cursor': 'pointer', 'border-radius': '6px', 'border': '1px solid rgba(127,127,127,.35)',
      'background': kind === 'all' || kind === 'top' ? '#fdecec' : '#f3f4f6', 'color': '#222' });
    b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); onClick(b); });
    return b;
  }

  /* ---------- 카드별 버튼 배치 ---------- */
  function ensureRow(saveBtn) {
    var row = saveBtn.parentElement;
    if (!row) return null;
    if (row.hasAttribute(MARK) && row.getAttribute(MARK) === 'btnrow') return row;
    var nonBtn = Array.prototype.filter.call(row.children, function (c) {
      return !(c.matches('button, [role="button"]'));
    }).length;
    if (row.querySelector('textarea, pre, code, input, select') || nonBtn > 2) {
      var wrap = document.createElement('div');
      wrap.setAttribute(MARK, 'btnrow');
      row.insertBefore(wrap, saveBtn);
      Array.prototype.slice.call(row.children).forEach(function (c) {
        if (c !== wrap && c.matches && c.matches('button, [role="button"]') &&
            (is(c) || isSave(c) || isQueue(c))) wrap.appendChild(c);
      });
      row = wrap;
    }
    return row;
  }
  function decorate(saveBtn, saves, tops) {
    var row = ensureRow(saveBtn);
    if (!row) return;
    css(row, { 'display': 'grid', 'grid-template-columns': 'repeat(auto-fit, minmax(96px, 1fr))',
      'gap': '6px', 'width': '100%', 'overflow': 'visible', 'flex': '1 1 100%',
      'min-width': '0', 'box-sizing': 'border-box', 'grid-column': '1 / -1' });
    var p = row.parentElement;
    if (p && getComputedStyle(p).display.indexOf('flex') !== -1) css(p, { 'flex-wrap': 'wrap' });
    Array.prototype.forEach.call(row.querySelectorAll('button, [role="button"]'), styleBtn);

    var next = row.nextElementSibling;
    if (next && next.getAttribute(MARK) === 'row') return;
    var er = document.createElement('div');
    er.setAttribute(MARK, 'row');
    css(er, { 'display': 'grid', 'grid-template-columns': '1fr 1fr', 'gap': '6px', 'width': '100%',
      'margin-top': '6px', 'grid-column': '1 / -1', 'flex': '1 1 100%', 'box-sizing': 'border-box' });
    er.appendChild(makeBtn('🧹 이 카드 지우기', 'one', function () {
      var s = buttons(isSave), t = buttons(isTopAbsorb);
      hideCard(findCard(saveBtn, s, t));
      toast('🧹 카드를 지웠습니다');
    }));
    er.appendChild(makeBtn('🗑️ 전체 카드 지우기', 'all', function () { clearAll(true); }));
    row.insertAdjacentElement('afterend', er);
  }

  function decorateTop(tops) {
    var seen = new Set();
    tops.forEach(function (b) {
      var p = b.parentElement;
      if (!p || seen.has(p)) return;
      seen.add(p);
      if (p.querySelector('[' + MARK + '="top"]')) return;
      var last = tops.filter(function (x) { return x.parentElement === p; }).pop() || b;
      var nb = makeBtn('🗑️ 흡수창 전체 비우기', 'top', function () { clearAll(true); });
      css(nb, { 'width': 'auto' });
      last.insertAdjacentElement('afterend', nb);
      if (getComputedStyle(p).display.indexOf('flex') !== -1) css(p, { 'flex-wrap': 'wrap', 'gap': '6px' });
    });
  }

  function unhideIfRefilled() {
    roots().forEach(function (r) {
      r.querySelectorAll('[data-rgon-v12-hidden="1"]').forEach(function (c) {
        var now = txt(c);
        if (now && now !== c.__rgonV12Snap) {
          c.style.removeProperty('display');
          c.removeAttribute('data-rgon-v12-hidden');
        }
      });
    });
  }

  function scan() {
    try {
      var saves = buttons(isSave), tops = buttons(isTopAbsorb);
      saves.forEach(function (s) { decorate(s, saves, tops); });   /* 모든 카드 반복 */
      if (tops.length) decorateTop(tops);
      unhideIfRefilled();
      roots().forEach(observe);
    } catch (e) { console.warn('[RGON-V12]', e); }
  }

  var timer = null;
  function schedule() { clearTimeout(timer); timer = setTimeout(scan, 200); }
  function observe(r) {
    if (observed.has(r)) return;
    observed.add(r);
    new MutationObserver(schedule).observe(r === document ? document.documentElement : r,
      { childList: true, subtree: true, characterData: true });
  }

  window.RGON_V12 = { scan: scan, clearAll: clearAll };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan);
  else scan();
})();
/* [RGON-4BTN-V12-END] */
