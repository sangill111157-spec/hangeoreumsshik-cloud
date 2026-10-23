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
