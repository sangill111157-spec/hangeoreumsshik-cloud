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
// RGON Omni-Link popup v6.0.3
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
