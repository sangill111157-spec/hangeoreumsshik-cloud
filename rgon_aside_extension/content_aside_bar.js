(() => {
"use strict";
if (window.top !== window) return;
const VER = "6.0.8";

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
const AI_ROLES = ['rgon', 'claude', 'gpt', 'grok'];
const GROK_PREFIX = "[광고 카피라이터 모드] 아래 지시를 바탕으로 짧고 강렬한 카피 5안을 제시해 주세요.\n\n";
const IS_RGON = /^(127\.0\.0\.1|localhost)$/.test(location.hostname) && location.port === "8501";
const IS_AI_HOST = /(^|\.)(genspark\.ai|claude\.ai|chatgpt\.com|openai\.com|grok\.com)$|^x\.com$/.test(location.hostname);

// ===== v6.0.8 3중 체크 상태 영구 보존 엔진 (메모리 + localStorage + chrome.storage) =====
const STORAGE_KEY_V606 = "rgon_omni_checked_v606";
window.__RGON_CHECKED__ = window.__RGON_CHECKED__ || null;

function initCheckedStore() {
  if (window.__RGON_CHECKED__ !== null) return window.__RGON_CHECKED__;
  let saved = null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY_V606);
    if (raw) saved = JSON.parse(raw);
  } catch (_) {}
  window.__RGON_CHECKED__ = Object.assign({ claude: true, gpt: true, grok: false }, saved || {});
  try {
    chrome.storage.local.get(STORAGE_KEY_V606).then(o => {
      if (o && o[STORAGE_KEY_V606]) {
        Object.assign(window.__RGON_CHECKED__, o[STORAGE_KEY_V606]);
      }
    }).catch(() => {});
  } catch (_) {}
  return window.__RGON_CHECKED__;
}

function setRoleChecked(role, boolVal) {
  initCheckedStore();
  window.__RGON_CHECKED__[role] = !!boolVal;
  try { localStorage.setItem(STORAGE_KEY_V606, JSON.stringify(window.__RGON_CHECKED__)); } catch (_) {}
  try { chrome.storage.local.set({ [STORAGE_KEY_V606]: window.__RGON_CHECKED__ }); } catch (_) {}
}

function isRoleChecked(role) {
  initCheckedStore();
  if (window.__RGON_CHECKED__[role] !== undefined) {
    return window.__RGON_CHECKED__[role] === true;
  }
  const def = (role === "claude" || role === "gpt");
  window.__RGON_CHECKED__[role] = def;
  try { localStorage.setItem(STORAGE_KEY_V606, JSON.stringify(window.__RGON_CHECKED__)); } catch (_) {}
  return def;
}

const state = { targetChecked: { claude: true, gpt: true, grok: false }, _lastTgtKey: '', role: null, tabId: null, open: false, scan: null, autoAbsorb: true, lastHash: null, dead: false, reported: undefined };
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
    const gemBtns = document.querySelectorAll("button, [role='button'], [role='combobox'], [aria-haspopup]");
  for (const g of gemBtns) {
    const gt = (g.innerText || "").trim();
    if (gt && gt.length <= 60 && /gemini|argon/i.test(gt) && visible(g)) return "rgon";
  }
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
  const sel = "textarea, [contenteditable='true'], [contenteditable='plaintext-only'], [role='textbox'], input[type='search'], input#search, #search-input input, #textbox, input[type='text']:not([readonly]):not([disabled])";
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
    let code = b.txt.replace(/\s+$/, "");
    code = code.replace(/^Copy\s*/i, "");
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
button.b.sm{padding:3px 8px;font-size:11px;border-radius:7px;background:rgba(220,60,60,.55)}
button.b.sm:hover{background:rgba(220,60,60,.85)}
.card .ch .rt{display:flex;align-items:center;gap:6px}
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
        <select id="roleSel"><option value="">자동 감지</option><option value="rgon">르곤 독대실</option><option value="claude">Claude Opus 5.5</option><option value="gpt">GPT-6.1 Sol</option><option value="grok">Grok 4.7</option><option value="sheets">Google Sheets</option><option value="adobe">Adobe</option><option value="__custom__">✏️ 직접 쓰기…</option></select><input type="text" id="customRoleInput" placeholder="역할명 직접 입력" style="display:none;width:110px;padding:4px 6px;font-size:12px;margin-left:4px">
        <button class="b" id="roleSave">지정</button></div>
      <div id="lamps"></div>
      <div class="row"><button class="b c" id="rescan">🔄 다시 스캔</button><small style="opacity:.6;font-size:11px">3초마다 자동 갱신 · 단축키 Alt+Shift+O</small></div>
    </section>
    <section class="pane" data-pane="2">
      <div class="row"><select id="preset"><option value="">— 지시문 템플릿 —</option><option value="design">코드 설계 요청</option><option value="review">코드 리뷰/개선</option><option value="ad">10초 광고 카피</option></select><button class="b" id="clearPrompt" type="button">🗑️ 전체 지우기</button><button class="b c" id="pastePrompt" type="button">📋 새로 붙여넣기</button></div>
      <textarea id="prompt" placeholder="사령관 지시문을 입력하세요. 열려 있는 Claude / GPT / Grok 탭 입력창에 자동으로 꽂아 넣습니다."></textarea>
      <div class="row"><label><input type="checkbox" id="autosend" checked> 자동 전송</label><label><input type="checkbox" id="grokPrefix" checked> Grok 카피 모드 접두어</label><label><input type="checkbox" id="autoclear" checked> 발사 후 입력창 자동 비우기</label></div>
      <div id="dispatchTargets" style="margin:8px 0;padding:8px 10px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1)">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <div style="font-size:11.5px;font-weight:700;color:#b9c0ff">🎯 발사 대상 선택 (체크박스 선택 또는 단독 발사)</div>
        <div style="display:flex;gap:4px">
          <button class="b sm" id="btnSelectAll" style="padding:2px 6px;font-size:11px" type="button">☑️ 전체 선택</button>
          <button class="b sm" id="btnUnselectAll" style="padding:2px 6px;font-size:11px" type="button">☐ 전체 해제</button>
        </div>
      </div>
        <div id="targetCheckList" style="display:flex;flex-wrap:wrap;gap:8px"></div>
      </div>
      <div class="row">
        <button class="b g" id="fireChecked">🚀 체크 선택 발사</button>
        <button class="b" id="fireAll">🌐 전체 발사</button>
      </div>
      <div class="out" id="fireOut">대기 중…</div>
    </section>
    <section class="pane" data-pane="3">
      <div class="row"><button class="b g" id="absThis">🧲 이 탭 코드 흡수 + 복사</button><button class="b c" id="absAll">🔄 AI 탭 전체 수거</button><button class="b" id="absPage">📄 화면 텍스트 흡수</button><button class="b o" id="absClearAll" type="button">🗑️ 흡수함 전체 비우기</button></div>
      <div class="row"><label><input type="checkbox" id="autoAbs" checked> 응답 완료 감지 시 자동 흡수 (Claude/GPT/Grok 탭)</label></div>
      <div class="row"><label><input type="checkbox" id="autoCleanAbs" checked> ☑ 새 작업 발사/수거 시 이전 흡수함 자동 삭제 (ON/OFF)</label></div>
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
      <div id="studioCustomGrid" style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0"></div>
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
  const customs = scan.customRoles || {};
  const allRoles = Object.assign({}, ROLE_META, customs);
  const activeOrder = ROLE_ORDER.concat(Object.keys(customs).filter(k => !ROLE_ORDER.includes(k)));

  const html = activeOrder.map((role) => {
    const m = allRoles[role] || { label: role, icon: "🔮" };
    const tabs = (scan.list || []).filter((t) => t.role === role);
    const on = tabs.length > 0;
    const first = on ? tabs.slice().sort((a, b) => (b.lastAccessed || 0) - (a.lastAccessed || 0))[0] : null;
    const isCustom = !!customs[role];

    return `<div class="lamp ${on ? "on" : "off"}">
      <span>${on ? "🟢" : "⚫"}</span>
      <div class="lt">
        <b>${m.icon || "🔮"} ${esc(m.label)}</b>
        <small>${on ? esc(trunc(first.title || m.url || "", 44)) + (tabs.length > 1 ? " (+" + (tabs.length - 1) + ")" : "") : (m.url ? esc(trunc(m.url, 44)) : "연결 안 됨")}</small>
      </div>
      <div style="display:flex;gap:4px;align-items:center">
        ${on ? `<button class="b" data-focus="${esc(role)}">이동</button>` : (m.url ? `<button class="b c" data-focus="${esc(role)}">열기</button>` : "")}
        ${isCustom ? `<button class="b sm" data-del-custom="${esc(role)}" title="이 커스텀 신경망 삭제">✕</button>` : ""}
      </div>
    </div>`;
  }).join("");
  $("#lamps").innerHTML = html;

  const connectedCount = activeOrder.filter((r) => (scan.list || []).some((t) => t.role === r)).length;
  $("#cnt").textContent = String(connectedCount);

  // 상단 '이 탭 역할:' 즉시 표시
  const me = state.role ? allRoles[state.role] : null;
  $("#selfRole").textContent = me ? `${me.icon || "🔮"} ${me.label}` : "일반 페이지";

  updateRoleSelect(customs);
  renderStudioCustomLinks(customs);
}

function updateRoleSelect(customs) {
  const sel = $("#roleSel");
  if (!sel) return;
  let html = `<option value="">자동 감지</option>
    <option value="rgon">르곤 독대실</option>
    <option value="claude">Claude Opus 5.5</option>
    <option value="gpt">GPT-6.1 Sol</option>
    <option value="grok">Grok 4.7</option>
    <option value="sheets">Google Sheets</option>
    <option value="adobe">Adobe</option>`;
  for (const [k, v] of Object.entries(customs || {})) {
    html += `<option value="${esc(k)}">${v.icon || "🔮"} ${esc(v.label)}</option>`;
  }
  html += `<option value="__custom__">✏️ 직접 쓰기…</option>`;
  sel.innerHTML = html;
  sel.value = state.role || "";
}

function renderStudioCustomLinks(customs) {
  const cont = $("#studioCustomGrid");
  if (!cont) return;
  const list = Object.entries(customs || {});
  if (!list.length) { cont.innerHTML = ""; return; }
  cont.innerHTML = list.map(([k, v]) =>
    `<button class="b" data-focus="${esc(k)}" style="flex:1;min-width:130px;padding:8px">${v.icon || "🔮"} ${esc(v.label)}</button>`
  ).join("");
}

async function __v607_origRefreshScan() {
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
  const r = await rt({ type: "OMNI_STORE_SHARED", role: state.role, entry: e, auto: true });
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
  const fired = !!(r && r.results && r.results.length && r.results.every((x) => x && x.ok));
  const acEl = $("#autoclear");
  if (fired && acEl && acEl.checked) { const pEl = $("#prompt"); pEl.value = ""; pEl.focus(); }
  else if (r && r.results && r.results.some((x) => x && x.ok) && !fired) toast("일부 대상 실패 — 재시도를 위해 입력창을 유지했습니다.", 3500);
}

// ------------------------------------------------------------------ tab 3: absorber + arena
const COPY_RE = /^Copy\s*/i;
function cleanEntry(e) {
  if (!e || typeof e.code !== "string" || e.kind === "page" || e.kind === "selection" || !COPY_RE.test(e.code)) return false;
  e.code = e.code.replace(COPY_RE, "");
  e.lines = e.code.split("\n").length;
  e.bytes = new TextEncoder().encode(e.code).length;
  return true;
}
function cleanCode(e) {
  const c = String((e && e.code) || "");
  return (e && (e.kind === "page" || e.kind === "selection")) ? c : c.replace(COPY_RE, "");
}
async function getShared() {
  try {
    const o = await chrome.storage.local.get("omni_shared");
    const sh = o.omni_shared || { entries: {}, history: [] };
    sh.entries = sh.entries || {};
    let dirty = false;
    for (const k of Object.keys(sh.entries)) { if (cleanEntry(sh.entries[k])) dirty = true; }
    if (dirty) rt({ type: "OMNI_GET_SHARED" });
    return sh;
  } catch (_) { return { entries: {}, history: [] }; }
}
function cardHTML(role, e) {
  const m = ROLE_META[role] || { label: role === "page" ? "화면 텍스트" : role, icon: "📄" };
  const fn = "omni_" + role + "_" + stamp(e.ts) + "." + extFor(e.lang);
  return `<div class="card" data-role="${esc(role)}"><div class="ch"><b>${m.icon} ${esc(m.label)}</b><span class="rt"><small>${esc(e.lang || "text")} · ${e.lines}줄 · ${fmtKB(e.bytes)}</small><button class="b sm" data-act="del" type="button" title="이 항목만 삭제">✕ 삭제</button></span></div>
<pre class="pv">${esc(cleanCode(e).slice(0, 700))}${cleanCode(e).length > 700 ? "\n…" : ""}</pre>
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
  const order = ['rgon', 'claude', 'gpt', 'grok'].concat(Object.keys(en).filter((k) => !['rgon', 'claude', 'gpt', 'grok'].includes(k)));
  const cards = order.filter((k) => en[k]).map((k) => cardHTML(k, en[k])).join("");
  html += cards || `<div class="out">아직 흡수된 결과물이 없습니다.</div>`;
  $("#arena").innerHTML = html;
}
async function storeEntry(role, e) {
  cleanEntry(e);
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




const roleSaveBtn = $("#roleSave");
if (roleSaveBtn) {
  roleSaveBtn.onclick = async () => {
    let sel = $("#roleSel").value;
    if (sel === "__custom__") {
      const customName = ($("#customRoleInput")?.value || "").trim();
      if (!customName) { toast("신경망 이름을 입력하세요."); return; }
      const roleKey = "custom_" + encodeURIComponent(customName).replace(/%/g, "_");
      const roleMeta = {
        label: customName,
        icon: "🔮",
        url: location.href,
        origin: location.origin,
        title: document.title
      };
      await rt({ type: "OMNI_SET_CUSTOM_ROLE", roleKey, roleMeta });
      sel = roleKey;
    }
    await rt({ type: "OMNI_SET_OVERRIDE", role: sel });
    await refreshScan();
    toast("이 탭 역할을 지정했습니다: " + sel);
  };
}

const fireCheckedBtn = $("#fireChecked");
if (fireCheckedBtn) {
  fireCheckedBtn.onclick = () => {
    const checked = $$(".role-chk:checked, .tgt-chk:checked").map(c => c.value);
    if (!checked.length) { toast("발사할 대상을 1개 이상 체크하세요."); return; }
    fire(checked);
  };
}

$("#dispatchTargets")?.addEventListener("click", (ev) => {
  const solo = ev.target.closest("[data-solo-fire]");
  if (solo) {
    const role = solo.dataset.soloFire;
    fire([role]);
  }
});

// ===== v6.0.8 발사 대상 체크박스 3중 저장소 실시간 동기화 핸들러 =====
$("#dispatchTargets")?.addEventListener("change", (ev) => {
  const chk = ev.target.closest(".role-chk, .tgt-chk");
  if (!chk) return;
  setRoleChecked(chk.value, chk.checked);
});

$("#btnSelectAll")?.addEventListener("click", () => {
  $$(".role-chk, .tgt-chk").forEach(c => {
    c.checked = true;
    setRoleChecked(c.value, true);
  });
  toast("☑️ 전체 대상 선택 완료");
});

$("#btnUnselectAll")?.addEventListener("click", () => {
  $$(".role-chk, .tgt-chk").forEach(c => {
    c.checked = false;
    setRoleChecked(c.value, false);
  });
  toast("☐ 전체 대상 해제 완료");
});




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
$("#lamps")?.addEventListener("click", async (ev) => {
  const focusBtn = ev.target.closest("[data-focus]");
  if (focusBtn) {
    await rt({ type: "OMNI_FOCUS", role: focusBtn.dataset.focus });
    return;
  }
  const delBtn = ev.target.closest("[data-del-custom]");
  if (delBtn) {
    const roleKey = delBtn.dataset.delCustom;
    if (confirm("이 커스텀 신경망 역할을 삭제하시겠습니까?")) {
      await rt({ type: "OMNI_DEL_CUSTOM_ROLE", roleKey });
      toast("커스텀 신경망 삭제 완료");
      await refreshScan();
    }
  }
});

$("#panel")?.addEventListener("click", async (ev) => {
  const focusBtn = ev.target.closest("[data-focus]");
  if (focusBtn && !focusBtn.closest("#lamps")) {
    await rt({ type: "OMNI_FOCUS", role: focusBtn.dataset.focus });
    return;
  }
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
$("#fireCG")?.addEventListener("click", () => fire(["claude", "gpt"]));
$("#fireGrok")?.addEventListener("click", () => fire(["grok"]));
$("#fireAll")?.addEventListener("click", () => fire(['rgon', 'claude', 'gpt', 'grok']));

async function readClip() {
  try { return await navigator.clipboard.readText(); } catch (_) {}
  try {
    const ta = document.createElement("textarea");
    ta.style.cssText = "position:fixed;opacity:0;left:-9999px;top:0";
    document.body.appendChild(ta);
    ta.focus();
    const ok = document.execCommand("paste");
    const v = ta.value;
    ta.remove();
    if (ok && v) return v;
  } catch (_) {}
  return null;
}
$("#clearPrompt").addEventListener("click", () => { const p = $("#prompt"); p.value = ""; p.focus(); });
$("#pastePrompt").addEventListener("click", async () => {
  const p = $("#prompt");
  p.value = "";
  p.focus();
  const t = await readClip();
  if (t === null) { toast("⚠️ 클립보드 읽기 권한이 필요합니다. 입력창에서 Ctrl+V 로 붙여넣어 주세요.", 4200); return; }
  p.value = t;
  p.focus();
  toast("📋 클립보드 내용을 붙여넣었습니다 (" + t.length + "자)");
});

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
        const e = extractLastCode() || absorbPageText();
        return e ? { ok: true, entry: e } : { ok: false, error: "수거할 내용 없음" };
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

// ===== v6.0.2 흡수함 관리: 자동 삭제 토글 / 전체 비우기 / 개별 삭제 =====
try {
  const acEl = $("#autoCleanAbs");
  if (acEl) {
    chrome.storage.local.get("omni_autoclean").then((o) => { acEl.checked = o.omni_autoclean !== false; }).catch(() => {});
    acEl.addEventListener("change", () => {
      try { chrome.storage.local.set({ omni_autoclean: acEl.checked }).catch(() => {}); } catch (_) {}
      toast(acEl.checked ? "🧹 자동 삭제 ON — 새 작업 시 이전 흡수함을 비웁니다." : "📚 자동 삭제 OFF — 흡수 항목을 누적 유지합니다.");
    });
  }
  chrome.storage.onChanged.addListener((ch, area) => {
    if (state.dead || area !== "local") return;
    if (ch.omni_autoclean && acEl) acEl.checked = ch.omni_autoclean.newValue !== false;
    if (ch.omni_shared) {
      const o = ch.omni_shared.oldValue, n = ch.omni_shared.newValue;
      const oc = o && o.entries ? Object.keys(o.entries).length : 0;
      const nc = n && n.entries ? Object.keys(n.entries).length : 0;
      if (state.open && oc > 0 && nc === 0) toast("🧹 이전 흡수함을 비웠습니다.");
    }
  });
} catch (_) {}

const absClearBtn = $("#absClearAll");
if (absClearBtn) {
  absClearBtn.addEventListener("click", async () => {
    const r = await rt({ type: "OMNI_CLEAR_SHARED" });
    if (r && r.ok) {
      arenaCache = {};
      $("#absOut").textContent = "🗑️ 흡수함을 전체 비웠습니다.";
      toast("🗑️ 흡수함 전체 비우기 완료");
    } else {
      toast("⚠️ " + ((r && r.error) || "비우기 실패"));
    }
    await renderArena();
  });
}

$("#arena").addEventListener("click", async (ev) => {
  const btn = ev.target && ev.target.closest ? ev.target.closest('[data-act="del"]') : null;
  if (!btn) return;
  ev.stopPropagation();
  const card = btn.closest(".card");
  const role = card && card.dataset.role;
  if (!role) return;
  const r = await rt({ type: "OMNI_CLEAR_SHARED", role });
  const label = (ROLE_META[role] && ROLE_META[role].label) || role;
  toast(r && r.ok ? "✕ " + label + " 항목 삭제 완료" : "⚠️ " + ((r && r.error) || "삭제 실패"));
  await renderArena();
}, true);

// ------------------------------------------------------------------ init
detectAndReport();
refreshScan();
intervals.push(setInterval(() => { if (!document.hidden) refreshScan(); }, 5000));
intervals.push(setInterval(() => { if (!document.hidden) detectAndReport(); }, 4000));
/* RGON_V607_BEGIN */
var __v607Api = null;
var __v607LastScan = null;

function __v607Sync() {
  try {
    if (__v607Api && typeof __v607Api.sync === 'function') { __v607Api.sync(); }
  } catch (e) {
    try { console.warn('[v6.0.8] sync error:', e); } catch (_) {}
  }
}

__v607Api = (function () {
  var CHECK_KEY = 'rgon_omni_checked_v607';
  var CONTAINER_STYLE = 'display:flex;flex-direction:column;gap:6px;margin-top:8px;';
  var DEFAULT_ROLES = [
    { role: 'rgon', icon: '🔵', label: '👑 르곤 보좌관 (Gemini 4 Argon)', def: false },
    { role: 'claude', icon: '🟠', label: '🧠 Claude (설계·코드)', def: true },
    { role: 'gpt',    icon: '🟢', label: '⚡ GPT (검증·코드)',    def: true },
    { role: 'grok',   icon: '🟣', label: '🔥 Grok (바이럴·카피)', def: false }
  ];
  var KEY_ALIAS = { gemini: 'rgon', argon: 'rgon', chatgpt: 'gpt', openai: 'gpt', anthropic: 'claude', xai: 'grok' };
  var URL_ALIAS = [ [/gemini\.google\.com/i, 'rgon'],
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
    try { console.warn('[v6.0.8]', msg); } catch (e) {}
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
      try { console.warn('[v6.0.8] sync failed:', e); } catch (_) {}
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
/* RGON_V607_END */

})();

/* RGON_V608_FAB_BEGIN */
;(function () {
  'use strict';
  try {
    if (window.__RGON_V608_FAB__) { return; }
    window.__RGON_V608_FAB__ = true;
  } catch (e) {}

  var POS_KEY = 'rgon_omni_fab_pos';
  var STYLE_ID = 'rgon-v608-fab-style';
  var KEY_TEXT = /르곤\s*만능\s*소통창|Omni-?Link/i;
  var ID_SELECTORS = [
    '#rgon-omni-fab', '#rgon-omni-toggle', '#omni-fab', '#rgon-fab',
    '[id*="omni"][id*="fab"]', '[id*="omni"][id*="toggle"]'
  ];
  var OBS = { childList: true, characterData: true, subtree: true };
  var CSS = [
    '.rgon-fab-compact{padding:5px 10px !important;font-size:12px !important;line-height:1.3 !important;',
    'white-space:nowrap !important;width:auto !important;min-width:0 !important;max-width:none !important;',
    'height:auto !important;min-height:0 !important;border-radius:999px !important;box-sizing:border-box !important;',
    'cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none;',
    'transition:opacity .2s ease, box-shadow .2s ease;}',
    '.rgon-fab-compact:hover{opacity:1 !important;}',
    '.rgon-fab-compact.rgon-fab-dragging{cursor:grabbing;opacity:1 !important;transition:none;}',
    '.rgon-fab-compact .rgon-fab-full{display:inline-block;max-width:0;overflow:hidden;opacity:0;',
    'white-space:nowrap;margin:0;vertical-align:middle;',
    'transition:max-width .28s ease, opacity .2s ease, margin .28s ease;}',
    '.rgon-fab-compact:hover .rgon-fab-full,.rgon-fab-compact.rgon-fab-dragging .rgon-fab-full{',
    'max-width:340px;opacity:1;margin:0 6px;}',
    '.rgon-fab-compact .rgon-fab-n{display:inline-block;min-width:16px;padding:0 5px;margin-left:4px;',
    'border-radius:999px;background:rgba(255,255,255,.22);text-align:center;font-weight:700;}'
  ].join('');

  var current = null;
  var tries = 0;

  /* ---------- small helpers ---------- */
  function mk(cls, text) {
    var s = document.createElement('span');
    s.className = cls;
    s.textContent = text;
    return s;
  }
  function hasOurClass(n) {
    var c = n && n.classList;
    return !!(c && (c.contains('rgon-fab-ic') || c.contains('rgon-fab-full') || c.contains('rgon-fab-n')));
  }
  function clamp(v, lo, hi) { return Math.min(Math.max(v, lo), hi); }
  function setImp(el, name, val) { el.style.setProperty(name, val, 'important'); }

  /* ---------- stored position ---------- */
  function loadPos() {
    try {
      var raw = localStorage.getItem(POS_KEY);
      if (!raw) { return null; }
      var o = JSON.parse(raw);
      if (o && typeof o.top === 'number' && (typeof o.left === 'number' || typeof o.right === 'number')) { return o; }
    } catch (e) {}
    return null;
  }
  function savePos(o) {
    try { localStorage.setItem(POS_KEY, JSON.stringify(o)); } catch (e) {}
  }
  function applyPos(el, pos) {
    var w = el.offsetWidth || 40;
    var h = el.offsetHeight || 24;
    var vw = window.innerWidth;
    var vh = window.innerHeight;
    setImp(el, 'top', clamp(pos.top, 0, Math.max(0, vh - h)) + 'px');
    setImp(el, 'bottom', 'auto');
    if (typeof pos.right === 'number') {
      setImp(el, 'right', clamp(pos.right, 0, Math.max(0, vw - w)) + 'px');
      setImp(el, 'left', 'auto');
    } else {
      setImp(el, 'left', clamp(pos.left, 0, Math.max(0, vw - w)) + 'px');
      setImp(el, 'right', 'auto');
    }
  }
  function defaultPos(el) {
    setImp(el, 'right', '2px');
    setImp(el, 'left', 'auto');
  }

  /* ---------- style ---------- */
  function ensureStyle(el) {
    try {
      var root = el.getRootNode ? el.getRootNode() : document;
      var host = (root && root.nodeType === 11) ? root : (document.head || document.documentElement);
      if (host.querySelector('#' + STYLE_ID)) { return; }
      var st = document.createElement('style');
      st.id = STYLE_ID;
      st.textContent = CSS;
      host.appendChild(st);
    } catch (e) {}
  }

  /* ---------- compact the label: icon / full label / count ---------- */
  function splitText(v) {
    var m = /^\s*(✨\uFE0F?)?\s*([\s\S]*?)\s*(\d+)?\s*$/.exec(v);
    if (!m) { return null; }
    return { ic: m[1], label: m[2], n: m[3] };
  }
  function processTextNode(tn) {
    var p = tn.parentNode;
    if (!p || p.nodeType !== 1 || hasOurClass(p)) { return false; }
    var v = tn.nodeValue;
    if (!v || !v.trim()) { return false; }
    var s = splitText(v);
    if (!s) { return false; }
    var frag = document.createDocumentFragment();
    if (s.ic) { frag.appendChild(mk('rgon-fab-ic', '✨')); }
    if (s.label) { frag.appendChild(mk('rgon-fab-full', s.label)); }
    if (s.n) { frag.appendChild(mk('rgon-fab-n', s.n)); }
    if (!frag.childNodes.length) { return false; }
    p.replaceChild(frag, tn);
    return true;
  }
  function compact(el) {
    if (!el || !el.isConnected) { return; }
    (function walk(node, depth) {
      var kids = Array.prototype.slice.call(node.childNodes);
      for (var i = 0; i < kids.length; i++) {
        var k = kids[i];
        if (k.nodeType === 3) {
          processTextNode(k);
        } else if (k.nodeType === 1 && depth < 2 && !hasOurClass(k) && !/^(SCRIPT|STYLE|SVG)$/i.test(k.tagName)) {
          walk(k, depth + 1);
        }
      }
    })(el, 0);
    if (el.querySelector('.rgon-fab-full') && !el.querySelector('.rgon-fab-ic')) {
      el.insertBefore(mk('rgon-fab-ic', '✨'), el.firstChild);
    }
  }

  /* ---------- drag (>= 5px = move, otherwise a normal click) ---------- */
  function bindDrag(el) {
    var st = null;
    var suppress = false;

    function onMove(ev) {
      if (!st) { return; }
      var dx = ev.clientX - st.x;
      var dy = ev.clientY - st.y;
      if (!st.moved) {
        if (Math.sqrt(dx * dx + dy * dy) < 5) { return; }
        st.moved = true;
        el.classList.add('rgon-fab-dragging');
      }
      try { ev.preventDefault(); } catch (e) {}
      var nl = clamp(st.left + dx, 0, Math.max(0, window.innerWidth - st.w));
      var nt = clamp(st.top + dy, 0, Math.max(0, window.innerHeight - st.h));
      setImp(el, 'left', nl + 'px');
      setImp(el, 'top', nt + 'px');
      setImp(el, 'right', 'auto');
      setImp(el, 'bottom', 'auto');
    }
    function onUp() {
      window.removeEventListener('mousemove', onMove, true);
      window.removeEventListener('mouseup', onUp, true);
      var s = st;
      st = null;
      if (!s || !s.moved) { return; }
      el.classList.remove('rgon-fab-dragging');
      suppress = true;
      setTimeout(function () { suppress = false; }, 80);
      var r = el.getBoundingClientRect();
      var vw = window.innerWidth;
      var pos;
      if (r.left + r.width / 2 > vw / 2) {
        pos = { top: Math.round(r.top), right: Math.round(Math.max(0, vw - r.right)) };
      } else {
        pos = { top: Math.round(r.top), left: Math.round(Math.max(0, r.left)) };
      }
      savePos(pos);
      applyPos(el, pos);
    }

    el.addEventListener('mousedown', function (ev) {
      if (ev.button !== 0) { return; }
      var r = el.getBoundingClientRect();
      st = { x: ev.clientX, y: ev.clientY, left: r.left, top: r.top, w: r.width, h: r.height, moved: false };
      window.addEventListener('mousemove', onMove, true);
      window.addEventListener('mouseup', onUp, true);
    }, true);

    window.addEventListener('click', function (ev) {
      if (!suppress) { return; }
      var path = ev.composedPath ? ev.composedPath() : [];
      if (path.indexOf(el) !== -1) {
        suppress = false;
        ev.preventDefault();
        ev.stopPropagation();
        ev.stopImmediatePropagation();
      }
    }, true);
  }

  /* ---------- find the launcher ---------- */
  function getRoots() {
    var roots = [document];
    try {
      var all = document.querySelectorAll('*');
      for (var i = 0; i < all.length && i < 8000; i++) {
        if (all[i].shadowRoot) { roots.push(all[i].shadowRoot); }
      }
    } catch (e) {}
    return roots;
  }
  function isFixed(el) {
    try { return getComputedStyle(el).position === 'fixed'; } catch (e) { return false; }
  }
  function looksLikeFab(el) {
    return !!el && (el.textContent || '').length < 200;
  }
  function findFab() {
    var roots = getRoots();
    var i, j, el;
    for (i = 0; i < roots.length; i++) {
      for (j = 0; j < ID_SELECTORS.length; j++) {
        try { el = roots[i].querySelector(ID_SELECTORS[j]); } catch (e) { el = null; }
        if (el && looksLikeFab(el)) { return el; }
      }
    }
    for (i = 0; i < roots.length; i++) {
      var walker;
      try { walker = document.createTreeWalker(roots[i], NodeFilter.SHOW_TEXT, null); } catch (e) { continue; }
      var node, guard = 0;
      while ((node = walker.nextNode()) && guard++ < 30000) {
        var v = node.nodeValue;
        if (!v || v.length > 120 || !KEY_TEXT.test(v)) { continue; }
        var cur = node.parentElement;
        var up = 0;
        while (cur && up < 4) {
          if (isFixed(cur)) {
            if (looksLikeFab(cur)) { return cur; }
            break;
          }
          cur = cur.parentElement;
          up++;
        }
      }
    }
    return null;
  }

  /* ---------- attach ---------- */
  function attach(el) {
    if (el.__rgonV608Fab) { return; }
    el.__rgonV608Fab = true;
    ensureStyle(el);
    el.classList.add('rgon-fab-compact');
    el.style.opacity = '0.78';
    if (!el.getAttribute('title')) {
      el.setAttribute('title', '✨ 르곤 만능 소통창 (Omni-Link) — 드래그로 이동');
    }
    compact(el);
    var mo = new MutationObserver(function () {
      mo.disconnect();
      try { compact(el); } catch (e) {}
      try { mo.observe(el, OBS); } catch (e) {}
    });
    mo.observe(el, OBS);
    var saved = loadPos();
    if (saved) { applyPos(el, saved); } else { defaultPos(el); }
    bindDrag(el);
  }

  function tick() {
    try {
      if (current && !current.isConnected) { current = null; }
      if (!current) {
        var f = findFab();
        if (f) { current = f; attach(f); }
      } else {
        if (!current.classList.contains('rgon-fab-compact')) { current.classList.add('rgon-fab-compact'); }
        ensureStyle(current);
      }
    } catch (e) {}
    tries++;
    var delay = current ? 2000 : (tries < 20 ? 1000 : 4000);
    setTimeout(tick, delay);
  }

  window.addEventListener('resize', function () {
    try {
      if (!current) { return; }
      var p = loadPos();
      if (p) { applyPos(current, p); }
    } catch (e) {}
  });

  tick();
})();
/* RGON_V608_FAB_END */
