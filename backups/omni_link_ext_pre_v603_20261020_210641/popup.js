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
