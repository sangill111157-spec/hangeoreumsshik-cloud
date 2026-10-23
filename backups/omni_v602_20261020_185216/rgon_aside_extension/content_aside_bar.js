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
(() => {
"use strict";
if (window.top !== window) return;
const VER = "6.0.1";

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
      <div class="row"><select id="preset"><option value="">— 지시문 템플릿 —</option><option value="design">코드 설계 요청</option><option value="review">코드 리뷰/개선</option><option value="ad">10초 광고 카피</option></select><button class="b" id="clearPrompt" type="button">🗑️ 전체 지우기</button><button class="b c" id="pastePrompt" type="button">📋 새로 붙여넣기</button></div>
      <textarea id="prompt" placeholder="사령관 지시문을 입력하세요. 열려 있는 Claude / GPT / Grok 탭 입력창에 자동으로 꽂아 넣습니다."></textarea>
      <div class="row"><label><input type="checkbox" id="autosend" checked> 자동 전송</label><label><input type="checkbox" id="grokPrefix" checked> Grok 카피 모드 접두어</label><label><input type="checkbox" id="autoclear" checked> 발사 후 입력창 자동 비우기</label></div>
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
  const fired = !!(r && r.results && r.results.length && r.results.every((x) => x && x.ok));
  const acEl = $("#autoclear");
  if (fired && acEl && acEl.checked) { const pEl = $("#prompt"); pEl.value = ""; pEl.focus(); }
  else if (r && r.results && r.results.some((x) => x && x.ok) && !fired) toast("일부 대상 실패 — 재시도를 위해 입력창을 유지했습니다.", 3500);
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
