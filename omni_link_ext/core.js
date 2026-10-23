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

/* [RGON-4BTN-V11-START] */
;(function () {
  'use strict';
  try {
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    if (window.__RGON_4BTN_V11__) return;
    window.__RGON_4BTN_V11__ = true;
  } catch (e) { return; }

  var SAVE_STRONG = ['shin-agent 저장', 'shin-agent'];
  var SAVE_WEAK = ['저장'];
  var DIRECT_KEYS = ['안총리 실행 큐', '실행 큐', '안총리 직통', '안총리'];
  var BTN_SEL = 'button, [role="button"], input[type="button"], input[type="submit"]';
  var INPUT_SEL = 'textarea, input[type="text"], input:not([type]), input[type="search"], [contenteditable="true"], [contenteditable=""], [contenteditable="plaintext-only"]';
  var LOG_SEL = 'pre, output, [class*="log" i], [id*="log" i], [class*="preview" i], [id*="preview" i], [class*="output" i], [id*="output" i], [class*="result" i], [id*="result" i], [class*="status" i], [id*="status" i], [class*="history" i], [id*="history" i]';
  var COLS4 = '1.2fr 0.9fr 1.2fr 1fr';
  var COLS3 = '1.2fr 0.9fr 1fr';

  /* ── Shadow DOM 까지 관통하는 루트 수집 / 탐색 ── */
  function collectRoots(root, out, seen) {
    if (!root || seen.has(root)) return out;
    seen.add(root);
    out.push(root);
    var all;
    try { all = root.querySelectorAll('*'); } catch (e) { return out; }
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.shadowRoot) collectRoots(el.shadowRoot, out, seen);
      if (el.tagName === 'IFRAME') {
        try { var d = el.contentDocument; if (d) collectRoots(d, out, seen); } catch (e) {}
      }
    }
    return out;
  }
  function queryAllDeep(sel, root) {
    var roots = collectRoots(root || document, [], new Set());
    var res = [];
    roots.forEach(function (r) {
      try { r.querySelectorAll(sel).forEach(function (e) { res.push(e); }); } catch (e) {}
    });
    return res;
  }
  try { window.__rgonQueryAllDeep = queryAllDeep; } catch (e) {}

  function textOf(el) {
    if (!el) return '';
    var t = (el.tagName === 'INPUT') ? (el.value || '') : (el.innerText || el.textContent || '');
    return String(t).replace(/\s+/g, ' ').trim();
  }
  function isOurs(el) { return !!(el && el.getAttribute && el.getAttribute('data-rgon-added')); }

  function pick(btns, keys, exclude) {
    for (var k = 0; k < keys.length; k++) {
      for (var i = 0; i < btns.length; i++) {
        var b = btns[i];
        if (b === exclude || isOurs(b)) continue;
        var t = textOf(b);
        if (!t || t.length > 40) continue;
        if (t.indexOf(keys[k]) !== -1) return b;
      }
    }
    return null;
  }

  function nearCommon(a, b, levels) {
    var cur = a;
    for (var i = 0; i <= levels && cur; i++) {
      if (cur.contains && cur.contains(b)) return true;
      cur = cur.parentElement;
    }
    return false;
  }

  /* ── 패널 범위 판정 ── */
  function getPanelRoot(el) {
    var rn = el.getRootNode ? el.getRootNode() : null;
    if (rn && rn.host) return rn;                                   // ShadowRoot 전체
    if (location.protocol === 'chrome-extension:') return el.ownerDocument || document; // 사이드패널/팝업
    var doc = el.ownerDocument || document;
    var cur = el.parentElement, firstWithInput = null, fixedAnc = null;
    for (var i = 0; i < 15 && cur && cur !== doc.body && cur !== doc.documentElement; i++) {
      if (!firstWithInput && cur.querySelector(INPUT_SEL)) firstWithInput = cur;
      try {
        var pos = getComputedStyle(cur).position;
        if (pos === 'fixed' || pos === 'sticky') fixedAnc = cur;
      } catch (e) {}
      cur = cur.parentElement;
    }
    return fixedAnc || firstWithInput || el.parentElement || doc.body;
  }

  /* ── 비우기 ── */
  function setVal(el, v) {
    var proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    var d = Object.getOwnPropertyDescriptor(proto, 'value');
    if (d && d.set) d.set.call(el, v); else el.value = v;
    el.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
    el.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
  }
  function clearInputs(scope) {
    var n = 0;
    queryAllDeep(INPUT_SEL, scope).forEach(function (el) {
      try {
        if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
          setVal(el, '');
        } else {
          el.innerHTML = '';
          el.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
        }
        n++;
      } catch (e) {}
    });
    return n;
  }
  function clearLogs(scope, grid) {
    var n = 0;
    queryAllDeep(LOG_SEL, scope).forEach(function (el) {
      try {
        if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.tagName === 'LINK') return;
        if (grid && (el === grid || el.contains(grid) || grid.contains(el))) return;
        if (el.matches(INPUT_SEL)) return;
        if (el.querySelector(BTN_SEL + ',' + INPUT_SEL)) return;
        if (!el.textContent) return;
        el.textContent = '';
        n++;
      } catch (e) {}
    });
    return n;
  }
  function flash(btn, msg) {
    if (btn.__rgonFlash) clearTimeout(btn.__rgonFlash);
    if (!btn.__rgonLabel) btn.__rgonLabel = btn.textContent;
    btn.textContent = msg;
    btn.__rgonFlash = setTimeout(function () { btn.textContent = btn.__rgonLabel; btn.__rgonFlash = null; }, 900);
  }

  function styleCell(el) {
    if (el.getAttribute('data-rgon-styled') === '1') return;
    el.setAttribute('data-rgon-styled', '1');
    var s = el.style;
    s.setProperty('width', '100%', 'important');
    s.setProperty('min-width', '0', 'important');
    s.setProperty('max-width', '100%', 'important');
    s.setProperty('margin', '0', 'important');
    s.setProperty('box-sizing', 'border-box', 'important');
    s.setProperty('white-space', 'nowrap', 'important');
    s.setProperty('overflow', 'hidden', 'important');
    s.setProperty('text-overflow', 'ellipsis', 'important');
    s.setProperty('flex', 'none', 'important');
  }

  function makeBtn(doc, label, kind, ref) {
    var b = doc.createElement('button');
    b.type = 'button';
    b.className = (ref && typeof ref.className === 'string') ? ref.className : '';
    if (ref && ref.style && ref.style.cssText) b.style.cssText = ref.style.cssText;
    b.setAttribute('data-rgon-added', kind);
    b.textContent = label;
    b.title = kind === 'clear' ? '입력칸 즉시 비우기' : '입력칸 + 로그/프리뷰 전체 즉시 초기화';
    b.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var grid = b.closest('.rgon-4grid');
      var scope = getPanelRoot(grid || b);
      clearInputs(scope);
      if (kind === 'clearall') {
        clearLogs(scope, grid);
        try { window.dispatchEvent(new CustomEvent('rgon:clear-all')); } catch (er) {}
      } else {
        try { window.dispatchEvent(new CustomEvent('rgon:clear')); } catch (er) {}
      }
      flash(b, '✅ 비움');
    }, true);
    return b;
  }

  /* ── 1줄 4칸 그리드 구성 ── */
  function enhance(saveBtn, directBtn) {
    var doc = saveBtn.ownerDocument || document;
    var grid = saveBtn.parentElement;
    if (!grid) return;
    if (!grid.classList.contains('rgon-4grid')) {
      var g = doc.createElement('div');
      g.className = 'rgon-4grid';
      g.style.cssText = 'display:grid !important;grid-template-columns:' + COLS4 + ';gap:6px;width:100%;align-items:center;box-sizing:border-box;margin:4px 0;flex:1 1 100%;';
      grid.insertBefore(g, saveBtn);
      grid = g;
    }
    if (!directBtn) directBtn = grid.querySelector(':scope > [data-rgon-direct="1"]');
    var clearBtn = grid.querySelector(':scope > [data-rgon-added="clear"]') || makeBtn(doc, '🧹 지우기', 'clear', saveBtn);
    var allBtn = grid.querySelector(':scope > [data-rgon-added="clearall"]') || makeBtn(doc, '🗑️ 전체 지우기', 'clearall', saveBtn);

    var oldDirectParent = directBtn ? directBtn.parentElement : null;
    saveBtn.setAttribute('data-rgon-save', '1');
    if (directBtn) directBtn.setAttribute('data-rgon-direct', '1');

    var order = [saveBtn, clearBtn];
    if (directBtn) order.push(directBtn);
    order.push(allBtn);

    var same = grid.children.length === order.length;
    if (same) for (var i = 0; i < order.length; i++) { if (grid.children[i] !== order[i]) { same = false; break; } }
    if (!same) order.forEach(function (el) { grid.appendChild(el); });

    order.forEach(styleCell);
    var cols = directBtn ? COLS4 : COLS3;
    if (grid.style.getPropertyValue('grid-template-columns') !== cols) {
      grid.style.setProperty('grid-template-columns', cols, 'important');
    }
    if (oldDirectParent && oldDirectParent !== grid && !oldDirectParent.children.length && !textOf(oldDirectParent)) {
      oldDirectParent.style.setProperty('display', 'none', 'important');
    }
  }

  /* ── 전체 스캔 (루트별로 독립 판정) ── */
  function scan() {
    var roots;
    try { roots = collectRoots(document, [], new Set()); } catch (e) { return; }
    roots.forEach(function (root) {
      var btns;
      try { btns = Array.prototype.slice.call(root.querySelectorAll(BTN_SEL)); } catch (e) { return; }
      if (!btns.length) return;
      var isShadow = !!root.host;
      var isExtPage = location.protocol === 'chrome-extension:';
      var direct = pick(btns, DIRECT_KEYS, null);
      var save = pick(btns, SAVE_STRONG, direct);
      if (!save) {
        var weak = pick(btns, SAVE_WEAK, direct);
        if (weak && (isShadow || isExtPage || (direct && nearCommon(weak, direct, 3)))) save = weak;
      }
      if (!save) return;
      if (direct && !isShadow && !isExtPage && !nearCommon(save, direct, 4)) direct = null;
      try { enhance(save, direct); } catch (e) { try { console.warn('[RGON 4BTN] enhance 실패', e); } catch (x) {} }
    });
  }

  var timer = null;
  function schedule() {
    if (timer) return;
    timer = setTimeout(function () { timer = null; scan(); }, 250);
  }
  try { new MutationObserver(schedule).observe(document.documentElement || document, { childList: true, subtree: true }); } catch (e) {}
  setInterval(scan, 1500);   // Shadow DOM 내부 변화는 MutationObserver 로 안 잡히므로 주기 스캔 병행
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
})();
/* [RGON-4BTN-V11-END] */
