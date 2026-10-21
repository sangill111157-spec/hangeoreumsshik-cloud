# -*- coding: utf-8 -*-
"""
step10_awaken_6agencies_and_clean_r12.py
STEP 10 - (1) 항체 장부 정화: R1~R12 딱 12종 통일  (2) 6대 청사 D1~D6 실시간 장부 직결 & UI 문구 정돈

[폭발반경 R1] 로컬 파일 수정만 수행 / 외부 발송 없음 / 수거 코드 실행 없음.
  - 전 대상 파일을 backups/step10_<timestamp>/ 에 원본 백업 후 수정
  - 주입 JS 는 node --check 통과 + 위험 API 정적 가드 통과 후에만 파일 접촉
  - Minimal Diff 증명: 'HTML 은 주입분만 제거하면 원본과 정확히 동일' 해야 쓰기 진행
  - R10: 보호 ID 검사는 태그의 실제 id 속성 개수로만 판정 (주입 블록에는 보호 ID 리터럴을 넣지 않음)
  - 쓰기 후 검증 실패 시 즉시 자동 롤백
"""
import copy
import datetime
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
VERSION_TAG = "v6.1.0-step10"
COMMIT_MSG = ("feat(v6.1.0-step10): awaken 6 agencies D1-D6 with live data & clean R1-R12 antibodies")

SCRIPT_ID = "rgon-step10-agency-awaken"
PROTECTED_IDS = ["rgon-step5-solo-panel", "rgon-step7-chat-zone", "rgon-step8-constitution-bar",
                 "rgon-step9-aggregator-board", "dokdae-feed"]
H10_BEGIN = "<!-- RGON-STEP10-AWAKEN:BEGIN -->"
H10_END = "<!-- RGON-STEP10-AWAKEN:END -->"
HTML_FILES = ["rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
JSON_NAMES = ["evolution_memory.json", "rgon_brain_snapshot.json"]

# 주입 JS 에 존재하면 안 되는 위험 API (이 파일 안에서는 문자열을 쪼개 Self-Match 방지)
FORBIDDEN_API_RES = [
    re.compile(r"\binner" + r"HTML\b"),
    re.compile(r"\bouter" + r"HTML\b"),
    re.compile(r"\bnew\s+Func" + r"tion\b"),
    re.compile(r"\bev" + r"al\s*\("),
    re.compile(r"document\.wri" + r"te"),
    re.compile(r"insertAdjacent" + r"HTML"),
    re.compile(r"\bimportScripts\b"),
]

# ----------------------------------------------------------------------------
# 1. 항체 정의
# ----------------------------------------------------------------------------
CANON = {
    1: "R1_NO_POWERSHELL_QUOTE_TRAP",
    8: "R8_APPROVAL_BEFORE_CODE",
    9: "R9_SINGLE_PY_BLOCK_FOR_ABSORBER",
    10: "R10_NO_SELF_MATCH_IN_GUARD",
    11: "R11_CROSS_VALIDATION_MIN_DIFF_TOP1",
    12: "R12_SINGLE_FINAL_OUTPUT_ONLY",
}
TEXTS = {
    8: "G1 대표님 명시적 승인(Y) 전 실행 스크립트/코드 선발급 절대 금지",
    9: "흡수기(AI 탭 코드 수거) 사용 시 마지막 블록 오수거 방지를 위해 단일 python 코드 블록 1개만 출력",
    10: "검증 스크립트 내부 문자열이 자기 자신의 카운트 검사를 실패시키는 자기모순(Self-Match) 금지",
    11: "교차검증 시 기계적 테스트 통과 후보 중 변경량(diff)이 가장 작은 Top 1 선택 및 거부권(Veto) 우선",
    12: "중복 인사말·반복 설명 금지, 깊이 사고 후 최종 1회만 단순 요약 보고",
}
ID_KEYS = ("id", "name", "code", "key")
TEXT_KEYS = ("rule", "description", "text", "desc", "summary")
VERSION_KEYS = ("version", "brain_version", "evolution_version", "system_version")
AB_KEY_RE = re.compile(r"antibod|항체", re.I)
COUNT_KEY_RE = re.compile(
    r"(antibod|항체).*(count|total|num|size|개수|수)$|(count|total|num|size)_?(of_?)?(antibod|항체)", re.I)
RID_RE = re.compile(r"^\s*R(\d+)((?:_[A-Za-z0-9_]+)?)(?![A-Za-z0-9_])")

# ----------------------------------------------------------------------------
# 2. 런타임 JS (독대실 HTML 인라인 주입 - textContent 전용, 코드 실행/HTML 문자열 주입 없음)
# ----------------------------------------------------------------------------
AWAKEN_JS = r'''
(function () {
'use strict';
if (window.__rgon10Awaken) { return; }
window.__rgon10Awaken = true;

var FEED_ID = "dokdae-" + "feed";
var BOARD9_ID = "rgon-step9-aggregator-" + "board";
var STAMP_ATTR = "data-rgon10-stamp";
var AG = [
  { id: "D1", name: "알파-퀀트" },
  { id: "D2", name: "알파-바이럴" },
  { id: "D3", name: "알파-미디어" },
  { id: "D4", name: "알파-홍익" },
  { id: "D5", name: "알파-가디언" },
  { id: "D6", name: "알파-트레저리" }
];
var PHRASE = /정상\s*상주\s*중\s*\(\s*점검\s*대기\s*\)/;
var FIX = [
  [/(항체\s*)?R1\s*[~∼～]\s*R(?:7|11)(?![0-9])(?:\s*\(\s*\d+\s*종\s*\))?/g, function (m, p) { return (p || "") + "R1~R12 (12종)"; }],
  [/v6\.0\.[78](?![0-9])/gi, "v6.1.0"],
  [/(독대실에서\s*바로\s*분배하기\s*)\(\s*Claude\s*\/\s*GPT\s*\/\s*Grok\s*\)/g, function (m, p) { return p + "(👑르곤 / 🧠Claude / ⚡GPT / 🎯Grok)"; }]
];
var FILES = [
  ["const", "rgon_constitution.json"],
  ["snap", "rgon_brain_snapshot.json"],
  ["sched", "brain_basket/master_schedule.json"],
  ["ledger", "treasury_ledger.json"]
];
var PREFIXES = ["", "../"];
var DEFAULT_NOTE = " (장부 읽기 실패 · 기본값 표시)";
var DATA = {}, RAW = {}, LOADED = {}, LINES = null, ready = false;
var entries = [], lastStamp = {}, pending = null, pendTimer = null, scanTimer = null;

function pad(n) { return (n < 10 ? "0" : "") + n; }
function hhmmss() {
  var d = new Date();
  return pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
}
function own(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
function toast(msg) {
  var t = document.createElement("div");
  t.textContent = msg;
  t.setAttribute("data-rgon10-skip", "1");
  t.style.cssText = "position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:2147483001;background:#111827;color:#fff;padding:8px 14px;border-radius:8px;font:12px system-ui,sans-serif;max-width:90vw";
  document.body.appendChild(t);
  setTimeout(function () { if (t.parentNode) { t.parentNode.removeChild(t); } }, 2600);
}

/* ---------- 실시간 장부 로딩 (읽기 전용 fetch) ---------- */
function tryFetch(name, i) {
  if (i >= PREFIXES.length || typeof fetch !== "function") { return Promise.resolve(null); }
  return fetch(PREFIXES[i] + name, { cache: "no-store" })
    .then(function (r) { return r.ok ? r.text() : null; })
    .then(function (t) {
      if (t) {
        try { return { data: JSON.parse(t.replace(/^\uFEFF/, "")), raw: t }; } catch (e) { /* 다음 후보 */ }
      }
      return tryFetch(name, i + 1);
    }, function () { return tryFetch(name, i + 1); });
}
function loadAll() {
  var jobs = FILES.map(function (f) {
    return tryFetch(f[1], 0).then(function (res) {
      if (res) { DATA[f[0]] = res.data; RAW[f[0]] = res.raw; LOADED[f[0]] = true; }
      else { LOADED[f[0]] = false; }
    });
  });
  return Promise.all(jobs);
}

/* ---------- 장부 해석 ---------- */
function abNums(node, inAb, depth, set) {
  var i, k, m, it, ks, v;
  if (depth > 8 || node === null || typeof node !== "object") { return; }
  if (Array.isArray(node)) {
    for (i = 0; i < node.length; i++) {
      it = node[i];
      if (inAb) {
        if (typeof it === "string") {
          m = /^\s*R(\d+)(?![A-Za-z0-9])/.exec(it);
          if (m) { set[m[1]] = 1; }
        } else if (it && typeof it === "object" && !Array.isArray(it)) {
          ks = ["id", "name", "code", "key"];
          for (k = 0; k < ks.length; k++) {
            v = it[ks[k]];
            if (typeof v === "string") {
              m = /^\s*R(\d+)(?![A-Za-z0-9])/.exec(v);
              if (m) { set[m[1]] = 1; break; }
            }
          }
        }
      }
      abNums(it, inAb, depth + 1, set);
    }
    return;
  }
  for (k in node) {
    if (!own(node, k)) { continue; }
    if (inAb) {
      m = /^R(\d+)(?![A-Za-z0-9])/.exec(k);
      if (m) { set[m[1]] = 1; }
    }
    abNums(node[k], inAb || /antibod|항체/i.test(k), depth + 1, set);
  }
}
function abCount() {
  var set = {}, n = 0, k;
  abNums(DATA.snap, false, 0, set);
  for (k in set) { if (own(set, k)) { n++; } }
  return n;
}
function genOf() {
  var raw = RAW.snap || "", re = /GEN-(\d+)/g, m, best = 0, n;
  while ((m = re.exec(raw)) !== null) {
    n = parseInt(m[1], 10);
    if (n > best) { best = n; }
  }
  return best || 1;
}
function findSpend(node, depth) {
  var k, r;
  if (depth > 6 || node === null || typeof node !== "object") { return null; }
  for (k in node) {
    if (!own(node, k)) { continue; }
    if (typeof node[k] === "number" && /(api.*(spend|spent|cost|expense|지출|비용))|((spend|spent|cost|expense|지출|비용).*api)/i.test(k)) {
      return node[k];
    }
    r = findSpend(node[k], depth + 1);
    if (r !== null) { return r; }
  }
  return null;
}
function mk(ok, text, note) {
  return (ok ? "🟢 " : "🟡 ") + text + (ok ? "" : (note || DEFAULT_NOTE));
}
function buildLines() {
  var L = {}, c = DATA["const"], b9, gen, nAb, imm, ver, spend, m;
  b9 = !!document.getElementById(BOARD9_ID);
  gen = genOf();
  nAb = LOADED.snap ? abCount() : 0;

  if (!LOADED.snap) {
    L.D1 = mk(false, "R&D 가동 중 · 진화단계 GEN-1 · 4대 AI 교차검증 전광판 활성");
  } else if (!b9) {
    L.D1 = mk(false, "R&D 가동 중 · 진화단계 GEN-" + gen + " · 4대 AI 교차검증 전광판", " 미탐지");
  } else {
    L.D1 = mk(true, "R&D 가동 중 · 진화단계 GEN-" + gen + " · 4대 AI 교차검증 전광판 활성");
  }
  L.D2 = mk(!!LOADED.sched, "홍보·BM 대기 · 두뇌장바구니 시트 연동 · 일일 키워드 수확 준비");
  L.D3 = mk(!!LOADED.sched, "미디어 스튜디오 · STUDIO v5 MP4 & 청년보이스 TTS 대기");

  imm = !!(c && c.immutable === true);
  m = (c && typeof c.version === "string") ? /^(\d+\.\d+)/.exec(c.version) : null;
  ver = m ? m[1] : "1.0";
  if (!LOADED["const"]) {
    L.D4 = mk(false, "제0조 홍익인간 헌법 v1.0 수호 중 · 불변 잠금(immutable) 정상");
  } else if (imm) {
    L.D4 = mk(true, "제0조 홍익인간 헌법 v" + ver + " 수호 중 · 불변 잠금(immutable) 정상");
  } else {
    L.D4 = "🔴 제0조 홍익인간 헌법 v" + ver + " · ⚠️ 불변 잠금(immutable) 이상 감지 - 대표님 확인 필요";
  }

  if (!LOADED.snap) {
    L.D5 = mk(false, "5-Gate 보안 감찰 · 항체 R1~R12(12종) 활성 · R2/R3 폭탄 차단");
  } else if (nAb === 12) {
    L.D5 = mk(true, "5-Gate 보안 감찰 · 항체 R1~R12(12종) 활성 · R2/R3 폭탄 차단");
  } else {
    L.D5 = "🟡 5-Gate 보안 감찰 · 항체 " + nAb + "종 확인 (기대 R1~R12 12종) · R2/R3 폭탄 차단";
  }

  spend = LOADED.ledger ? findSpend(DATA.ledger, 0) : null;
  if (LOADED.ledger && spend !== null && spend > 0) {
    L.D6 = "🟡 무자본 레버리지 정산 · ⚠️ API 지출 " + spend + "원 감지 - 금고 확인 필요";
  } else {
    L.D6 = mk(!!LOADED.ledger, "무자본 레버리지 정산 · API 지출 0원 · 금고 무결성 100%");
  }
  return L;
}

/* ---------- DOM 탐색 ---------- */
function namesIn(txt) {
  var out = [], i;
  for (i = 0; i < AG.length; i++) { if (txt.indexOf(AG[i].name) >= 0) { out.push(AG[i]); } }
  return out;
}
function agencyOf(start) {
  var cur = start, best = null, i, nm;
  for (i = 0; i < 14 && cur && cur !== document.body && cur !== document.documentElement; i++) {
    nm = namesIn(cur.textContent || "");
    if (nm.length === 1) { best = { card: cur, ag: nm[0] }; }
    else if (nm.length > 1) { break; }
    cur = cur.parentElement;
  }
  return best;
}
function collectTextNodes() {
  var feed = document.getElementById(FEED_ID), out = [], w;
  w = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
    acceptNode: function (n) {
      var t;
      if (n.nodeType === 1) {
        t = n.tagName.toUpperCase();
        if (n === feed || t === "SCRIPT" || t === "STYLE" || t === "NOSCRIPT" || t === "TEXTAREA" ||
            t === "INPUT" || t === "SELECT" || n.hasAttribute("data-rgon10-skip") || n.isContentEditable) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_SKIP;
      }
      return (n.nodeValue && n.nodeValue.length > 1) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
    }
  }, false);
  while (w.nextNode()) { out.push(w.currentNode); }
  return out;
}

/* ---------- 카드 상태창 렌더 ---------- */
function putStamp(ent, t) {
  var host = ent.tn.parentNode, sp;
  if (!host || host.nodeType !== 1) { host = ent.card; }
  sp = host.querySelector("span[" + STAMP_ATTR + "]");
  if (!sp) {
    sp = document.createElement("span");
    sp.setAttribute(STAMP_ATTR, "1");
    sp.style.cssText = "margin-left:6px;color:#93c5fd;font-size:11px;white-space:nowrap";
    host.appendChild(sp);
  }
  sp.textContent = "⏱ 점검 " + t;
}
function paint(ent) {
  var t = ent.pre + ((LINES && LINES[ent.id]) || "") + ent.suf;
  if (ent.tn.nodeValue !== t) { ent.tn.nodeValue = t; }
  if (lastStamp[ent.id]) { putStamp(ent, lastStamp[ent.id]); }
}
function register(tn) {
  var m = PHRASE.exec(tn.nodeValue), hit = agencyOf(tn.parentElement), ent;
  if (!m || !hit) { return; }
  ent = {
    tn: tn, id: hit.ag.id, card: hit.card,
    pre: tn.nodeValue.slice(0, m.index),
    suf: tn.nodeValue.slice(m.index + m[0].length)
  };
  entries.push(ent);
  paint(ent);
}
function scan() {
  var nodes, i, j, tn, v, nv;
  if (!document.body) { return; }
  nodes = collectTextNodes();
  entries = entries.filter(function (e) { return e.tn.isConnected; });
  for (i = 0; i < nodes.length; i++) {
    tn = nodes[i];
    v = tn.nodeValue;
    nv = v;
    for (j = 0; j < FIX.length; j++) { nv = nv.replace(FIX[j][0], FIX[j][1]); }
    if (nv !== v) { tn.nodeValue = nv; v = nv; }
    if (ready && LINES && PHRASE.test(v)) { register(tn); }
  }
}
function schedule() {
  if (scanTimer) { return; }
  scanTimer = setTimeout(function () { scanTimer = null; try { scan(); } catch (e) { /* 무시 */ } }, 250);
}
function paintAll() {
  entries = entries.filter(function (e) { return e.tn.isConnected; });
  entries.forEach(paint);
}

/* ---------- 점검·직보 / 일제 점호 ---------- */
function addReport(now, ids, viaAll) {
  var feed = document.getElementById(FEED_ID), card, hd, i, row, stamped = {}, src, sl, ft, srcNames;
  if (!feed) { toast("독대실 피드를 찾지 못해 점호 카드를 추가하지 못했습니다"); return; }
  for (i = 0; i < ids.length; i++) { stamped[ids[i]] = 1; }
  card = document.createElement("div");
  card.setAttribute("data-rgon10-report", "1");
  card.style.cssText = "margin:8px 0;padding:10px 12px;border:1px solid #1e3a8a;border-radius:10px;background:#0b1220;color:#e2e8f0;font:13px/1.55 system-ui,'Malgun Gothic',sans-serif";
  hd = document.createElement("div");
  hd.style.cssText = "font-weight:700;margin-bottom:6px";
  hd.textContent = "📋 6대 청사 종합 점호 보고 · " + now + (viaAll ? " (전원 일제 점검)" : " (개별 점검·직보)");
  card.appendChild(hd);
  for (i = 0; i < AG.length; i++) {
    row = document.createElement("div");
    row.style.cssText = "padding:3px 0;border-bottom:1px solid #1e293b";
    row.textContent = AG[i].id + " " + AG[i].name + " — " + ((LINES && LINES[AG[i].id]) || "-") +
      (stamped[AG[i].id] ? "  ⏱ " + now : "");
    card.appendChild(row);
  }
  srcNames = [["const", "rgon_constitution.json"], ["snap", "rgon_brain_snapshot.json"],
              ["sched", "master_schedule.json"], ["ledger", "treasury_ledger.json"]];
  src = [];
  for (i = 0; i < srcNames.length; i++) { src.push((LOADED[srcNames[i][0]] ? "✅ " : "⚠️ ") + srcNames[i][1]); }
  ft = document.createElement("div");
  ft.style.cssText = "margin-top:6px;font-size:11px;color:#94a3b8";
  ft.textContent = "장부 출처: " + src.join(" · ") + " · R0 읽기 전용 점호 (코드 실행 없음)";
  card.appendChild(ft);
  sl = feed;
  sl.appendChild(card);
  try { sl.scrollTop = sl.scrollHeight; } catch (e) { /* 무시 */ }
}
function runCheck(ids, viaAll) {
  var now = hhmmss();
  loadAll().then(function () {
    var i;
    ready = true;
    LINES = buildLines();
    for (i = 0; i < ids.length; i++) { lastStamp[ids[i]] = now; }
    scan();
    paintAll();
    addReport(now, ids, viaAll);
  });
}
function flush() {
  var p = pending, ids = [], k, i;
  pending = null;
  pendTimer = null;
  if (!p) { return; }
  if (p.all) { for (i = 0; i < AG.length; i++) { ids.push(AG[i].id); } }
  else { for (k in p.ids) { if (own(p.ids, k)) { ids.push(k); } } }
  if (ids.length) { runCheck(ids, p.all); }
}
function onClick(ev) {
  var t = ev.target, btn, label, all, one, hit;
  if (!t || !t.closest) { return; }
  btn = t.closest("button, [role='button'], a, input[type='button'], input[type='submit']");
  if (!btn || btn.hasAttribute("data-rgon10-skip")) { return; }
  label = String(btn.value || "") + " " + String(btn.textContent || "");
  all = /일제\s*점검/.test(label);
  one = !all && /점검\s*[·∙・•‧.\-]?\s*직보/.test(label);
  if (!all && !one) { return; }
  if (!pending) {
    pending = { all: false, ids: {} };
    pendTimer = setTimeout(flush, 180);
  }
  if (all) { pending.all = true; }
  else {
    hit = agencyOf(btn);
    if (hit) { pending.ids[hit.ag.id] = 1; } else { pending.all = true; }
  }
}

/* ---------- 부팅 ---------- */
function refresh() {
  loadAll().then(function () {
    ready = true;
    LINES = buildLines();
    scan();
    paintAll();
  });
}
function boot() {
  try { scan(); } catch (e) { /* 배지 교정 실패는 무시 */ }
  refresh();
  document.addEventListener("click", onClick, true);
  try {
    new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true, characterData: true });
  } catch (e2) { /* 무시 */ }
  setInterval(refresh, 60000);
}
if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", boot); } else { boot(); }
})();
'''

# ----------------------------------------------------------------------------
# 3. 공통 유틸
# ----------------------------------------------------------------------------
NODE = None


def log(msg):
    print(msg)


def fatal(msg, code=1):
    print("[FATAL] " + msg)
    sys.exit(code)


def abspath(rel):
    return os.path.join(ROOT, *rel.split("/"))


def read_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8-sig"), raw.startswith(b"\xef\xbb\xbf")


def to_bytes(text, bom):
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        try:
            os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
        except OSError:
            pass
    tmp = path + ".step10.tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def count_tag_id(text, ident):
    """태그의 실제 id 속성만 카운트 (스크립트·주석 속 문자열 제외 -> R10 Self-Match 방지)."""
    pat = re.compile(r'<[A-Za-z][^<>]*?\sid\s*=\s*(["\'])' + re.escape(ident) + r"\1", re.S)
    return len(pat.findall(text))


def protected_counts(text):
    return {pid: count_tag_id(text, pid) for pid in PROTECTED_IDS}


def node_check(code, suffix=".js"):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "chk" + suffix)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
        r = subprocess.run([NODE, "--check", p], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        return r.returncode == 0, (r.stderr or r.stdout or "").strip()


def guard_js(name, js):
    for rx in FORBIDDEN_API_RES:
        m = rx.search(js)
        if m:
            fatal("%s 에 금지 API 포함 (%s) - 중단" % (name, m.group(0)))


# ----------------------------------------------------------------------------
# 4. 항체 장부 정화 (R1~R12 딱 12종)
# ----------------------------------------------------------------------------
def parse_rid(s):
    """'R3', 'R3_XXX', 'R3_XXX: 설명' -> (번호, 긴키여부, 토큰). 아니면 None."""
    if not isinstance(s, str):
        return None
    m = RID_RE.match(s)
    if not m:
        return None
    return int(m.group(1)), bool(m.group(2)), "R%s%s" % (m.group(1), m.group(2))


def ident_of(e):
    if isinstance(e, str):
        return parse_rid(e)
    if isinstance(e, dict):
        found = [parse_rid(e.get(k)) for k in ID_KEYS]
        found = [x for x in found if x]
        for x in found:
            if x[1]:
                return x
        return found[0] if found else None
    return None


def classify_item(k, v):
    pv = ident_of(v) if (k is None or isinstance(v, dict)) else None
    if pv and pv[1]:
        return pv
    if k is not None:
        pk = parse_rid(k)
        if pk:
            return pk
    return pv


def container_items(cont):
    if isinstance(cont, dict):
        return list(cont.items())
    return [(None, v) for v in cont]


def container_has_rid(cont):
    return any(classify_item(k, v) for k, v in container_items(cont))


def find_containers(obj, depth=0, in_ab=False, out=None):
    if out is None:
        out = []
    if depth > 6 or not isinstance(obj, dict):
        return out
    for k, v in obj.items():
        ab = in_ab or bool(isinstance(k, str) and AB_KEY_RE.search(k))
        if ab and isinstance(v, (dict, list)) and container_has_rid(v):
            out.append((obj, k))
        elif isinstance(v, dict):
            find_containers(v, depth + 1, ab, out)
    return out


def distinct_ns(cont):
    ns = set()
    for k, v in container_items(cont):
        m = classify_item(k, v)
        if m:
            ns.add(m[0])
    return ns


def rename_value(v, old, new):
    if old == new:
        return v
    if isinstance(v, dict):
        for k in ID_KEYS:
            r = parse_rid(v.get(k))
            if r and r[2] == old:
                v[k] = new
        return v
    if isinstance(v, str):
        m = RID_RE.match(v)
        if m and ("R%s%s" % (m.group(1), m.group(2))) == old:
            lead = len(v) - len(v.lstrip())
            return v[:lead] + new + v[m.end():]
    return v


def rename_entry(k, v, old, new):
    k2 = new if (k is not None and parse_rid(k)) else k
    return k2, rename_value(v, old, new)


def make_entry(sample, aid, text, is_dict):
    if isinstance(sample, str):
        return text if is_dict else "%s: %s" % (aid, text)
    entry = {}
    if isinstance(sample, dict):
        for k in ID_KEYS:
            if k in sample:
                entry[k] = aid
                break
        else:
            if not is_dict:
                entry["id"] = aid
        tk = next((k for k in TEXT_KEYS if k in sample), "rule")
        entry[tk] = text
        if "status" in sample:
            entry["status"] = "ACTIVE"
    else:
        if not is_dict:
            entry["id"] = aid
        entry["rule"] = text
        entry["status"] = "ACTIVE"
    entry["since"] = VERSION_TAG
    return entry


def process_container(cont, primary, tag):
    is_dict = isinstance(cont, dict)
    items = container_items(cont)
    meta = [classify_item(k, v) for k, v in items]
    first_long, first_short = {}, {}
    for i, m in enumerate(meta):
        if not m or not (1 <= m[0] <= 12):
            continue
        (first_long if m[1] else first_short).setdefault(m[0], i)

    out, present, sample = [], set(), None
    for i, (k, v) in enumerate(items):
        m = meta[i]
        if not m or not (1 <= m[0] <= 12):
            out.append((k, v))
            continue
        n = m[0]
        if m[1]:
            if first_long[n] != i:
                log("  [DEDUP] %s 중복 항체 제거: %s" % (tag, m[2]))
                continue
            new = CANON.get(n, m[2])
            if new != m[2]:
                log("  [RENAME] %s %s -> %s" % (tag, m[2], new))
            present.add(n)
        else:
            if primary and n not in first_long and first_short[n] == i:
                new = CANON.get(n) or ("R%d_LEGACY_MIGRATED" % n)
                log("  [PROMOTE] %s 정식 키가 없어 짧은 키 승격: %s -> %s (원본 내용 보존)" % (tag, m[2], new))
                present.add(n)
            else:
                log("  [CLEAN] %s 짧은 껍데기 키 제거: %s" % (tag, m[2]))
                continue
        k2, v2 = rename_entry(k, v, m[2], new)
        if sample is None:
            sample = v2
        out.append((k2, v2))

    if primary:
        for n in range(1, 13):
            if n in present:
                continue
            if n not in TEXTS:
                raise ValueError("항체 R%d 의 정식/짧은 키가 모두 없어 복원할 수 없습니다" % n)
            aid = CANON[n]
            val = make_entry(sample, aid, TEXTS[n], is_dict)
            out.append((aid, val) if is_dict else (None, val))
            log("  [ADD] %s 신규 항체 등록: %s" % (tag, aid))

    if is_dict:
        new_d = {}
        for k, v in out:
            if k in new_d:
                raise ValueError("키 충돌: " + str(k))
            new_d[k] = v
        cont.clear()
        cont.update(new_d)
    else:
        cont[:] = [v for _, v in out]


def drop_count_keys(node):
    if isinstance(node, dict):
        for k in [k for k, v in node.items()
                  if isinstance(v, int) and not isinstance(v, bool) and isinstance(k, str) and COUNT_KEY_RE.search(k)]:
            del node[k]
        for v in node.values():
            drop_count_keys(v)
    elif isinstance(node, list):
        for v in node:
            drop_count_keys(v)


def fix_counts(node):
    n = 0
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, int) and not isinstance(v, bool) and isinstance(k, str) and COUNT_KEY_RE.search(k):
                if v != 12:
                    node[k] = 12
                    n += 1
            else:
                n += fix_counts(v)
    elif isinstance(node, list):
        for v in node:
            n += fix_counts(v)
    return n


def strip_for_compare(obj):
    o = copy.deepcopy(obj)
    for parent, key in find_containers(o):
        parent[key] = "<AB>"
    for k in VERSION_KEYS:
        o.pop(k, None)
    drop_count_keys(o)
    return o


def audit_json(obj):
    """정화 결과 검사: 짧은 키 0개, 주 컨테이너는 R1~R12 정확히 1개씩, 정식 이름 일치, 버전 태그 일치."""
    conts = find_containers(obj)
    if not conts:
        raise ValueError("항체 컨테이너 소실")
    best, best_n = None, -1
    for parent, key in conts:
        cont = parent[key]
        ns_all = []
        for k, v in container_items(cont):
            m = classify_item(k, v)
            if not m:
                continue
            if 1 <= m[0] <= 12:
                if not m[1]:
                    raise ValueError("짧은 껍데기 키 잔존: " + m[2])
                ns_all.append(m)
        if len(ns_all) > best_n:
            best, best_n = ns_all, len(ns_all)
    nums = sorted(m[0] for m in best)
    if nums != list(range(1, 13)):
        raise ValueError("주 컨테이너가 R1~R12 딱 12종이 아닙니다: %s" % nums)
    for m in best:
        if m[0] in CANON and m[2] != CANON[m[0]]:
            raise ValueError("정식 이름 불일치: %s != %s" % (m[2], CANON[m[0]]))
    vk = [k for k in VERSION_KEYS if k in obj]
    if not vk or any(obj[k] != VERSION_TAG for k in vk):
        raise ValueError("버전 태그 불일치")


def patch_memory_json(text):
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise ValueError("최상위 JSON 이 객체(dict)가 아닙니다")
    orig = copy.deepcopy(obj)
    conts = find_containers(obj)
    if not conts:
        raise ValueError("항체 컨테이너(antibodies 등)를 찾지 못했습니다. 최상위 키: %s" % list(obj.keys())[:20])
    sizes = [len(distinct_ns(p[k])) for p, k in conts]
    pi = sizes.index(max(sizes))
    for i, (parent, key) in enumerate(conts):
        process_container(parent[key], i == pi, key)
    nfix = fix_counts(obj)
    if nfix:
        log("  [COUNT] 항체 개수 필드 %d개를 12 로 보정" % nfix)
    found = False
    for k in VERSION_KEYS:
        if k in obj:
            obj[k] = VERSION_TAG
            found = True
    if not found:
        obj["version"] = VERSION_TAG

    if strip_for_compare(orig) != strip_for_compare(obj):
        raise ValueError("항체/버전/개수 외 기존 데이터가 변형되었습니다 - 중단")
    audit_json(obj)

    m = re.search(r'\n(\t+| +)"', text)
    indent = m.group(1) if m else 2
    if isinstance(indent, str) and indent.startswith(" "):
        indent = len(indent)
    out = json.dumps(obj, ensure_ascii=False, indent=indent) + "\n"
    if "\r\n" in text:
        out = out.replace("\n", "\r\n")
    return out


# ----------------------------------------------------------------------------
# 5. HTML 패치 (Minimal Diff 증명 포함)
# ----------------------------------------------------------------------------
def build_js():
    return AWAKEN_JS.strip("\n").replace("</", "<\\/")


def build_block(js):
    return (H10_BEGIN + "\n" + '<script id="' + SCRIPT_ID + '">\n' + js + "\n</script>\n" + H10_END)


def patch_html10(text, block_lf):
    eol = "\r\n" if "\r\n" in text else "\n"
    block = block_lf.replace("\n", eol)
    for pid in PROTECTED_IDS:
        if pid in block:
            raise ValueError("주입 블록에 보호 대상 ID 문자열 포함 (Self-Match 위험): " + pid)
    before = protected_counts(text)

    b = text.find(H10_BEGIN)
    e = text.find(H10_END, b) if b >= 0 else -1
    if b >= 0 and e >= 0:
        e_end = e + len(H10_END)
        line_start = (b == 0 or text[b - 1] == "\n")
        t_end = e_end + (len(eol) if (line_start and text.startswith(eol, e_end)) else 0)
        base = text[:b] + text[t_end:]
    else:
        base = text

    ms = list(re.finditer(r"</body\s*>", base, re.I))
    if not ms:
        ms = list(re.finditer(r"</html\s*>", base, re.I))
    idx = ms[-1].start() if ms else len(base)
    ls = base.rfind("\n", 0, idx) + 1
    if base[ls:idx].strip() == "":
        pos, ins = ls, block + eol
    else:
        pos, ins = idx, eol + block + eol
    new = base[:pos] + ins + base[pos:]

    # Minimal Diff 증명: 주입분만 정확히 잘라내면 원본(base)과 바이트 단위로 동일해야 한다
    if new[:pos] + new[pos + len(ins):] != base:
        raise ValueError("Minimal Diff 증명 실패 (HTML)")
    after = protected_counts(new)
    if after != before:
        raise ValueError("보호 블록 ID 개수 변동: %s -> %s" % (before, after))
    if count_tag_id(new, SCRIPT_ID) != 1:
        raise ValueError("주입 스크립트 id 가 정확히 1개가 아닙니다")
    return new, before


# ----------------------------------------------------------------------------
# 6. 메인
# ----------------------------------------------------------------------------
def main():
    global NODE
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    log("=== STEP 10: 항체 장부 정화(R1~R12) + 6대 청사 각성 시작 (R1) ===")
    if not os.path.isdir(ROOT):
        fatal("사령부 폴더가 없습니다: " + ROOT)
    if not os.path.exists(os.path.join(ROOT, ".git")):
        fatal(".git 저장소가 아닙니다: " + ROOT)
    NODE = shutil.which("node")
    if not NODE:
        fatal("node 를 찾을 수 없습니다. node --check 통과 없이는 JS 를 주입할 수 없습니다.")

    # ---- G2: 파일 접촉 전 기계 검증 ----
    js = build_js()
    guard_js("청사 각성 JS", js)
    ok, err = node_check(js)
    if not ok:
        fatal("청사 각성 JS node --check 실패 - 중단:\n" + err)
    log("[G2] 주입 JS node --check 통과 + 금지 API 가드 통과")
    block = build_block(js)

    plan = []

    # ---- 과제 1: 항체 장부 정화 ----
    for name in JSON_NAMES:
        for rel, required in ((name, True), ("dashboard/" + name, False), ("docs/" + name, False)):
            p = abspath(rel)
            if not os.path.isfile(p):
                if required:
                    fatal("필수 파일 없음: " + rel)
                log("[SKIP] 선택 파일 없음: " + rel)
                continue
            log("[JSON] 정화 계산: " + rel)
            try:
                text, bom = read_file(p)
                new_text = patch_memory_json(text)
            except Exception as ex:
                if required:
                    fatal("%s 정화 실패: %s" % (rel, ex))
                log("[SKIP] %s 정화 불가: %s" % (rel, ex))
                continue
            plan.append({"rel": rel, "new": to_bytes(new_text, bom), "kind": "json"})

    # ---- 과제 2: 독대실 HTML 3종 ----
    counts = {}
    for rel in HTML_FILES:
        p = abspath(rel)
        if not os.path.isfile(p):
            fatal("독대실 HTML 없음: " + rel)
        try:
            text, bom = read_file(p)
            new_text, before = patch_html10(text, block)
        except Exception as ex:
            fatal("%s 패치 계산 실패: %s" % (rel, ex))
        counts[rel] = before
        plan.append({"rel": rel, "new": to_bytes(new_text, bom), "kind": "html"})
    log("[G2] 전체 패치 계획 계산 + Minimal Diff 증명 완료 (%d개 파일, 보호 ID 개수 불변 확인)" % len(plan))

    # ---- G3: 사전 백업 ----
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(ROOT, "backups", "step10_" + ts)
    os.makedirs(backup_dir, exist_ok=True)
    existed = {}
    for item in plan:
        src = abspath(item["rel"])
        existed[item["rel"]] = os.path.isfile(src)
        if existed[item["rel"]]:
            dst = os.path.join(backup_dir, *item["rel"].split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    with open(os.path.join(backup_dir, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump({"timestamp": ts, "files": existed}, f, ensure_ascii=False, indent=2)
    log("[G3] 원본 백업 완료: " + backup_dir)

    written = []

    def rollback():
        log("[G3] 범위 위반/오류 감지 -> 자동 롤백 실행")
        for rel in written:
            target = abspath(rel)
            try:
                if existed.get(rel):
                    with open(os.path.join(backup_dir, *rel.split("/")), "rb") as bf:
                        write_bytes(target, bf.read())
                elif os.path.exists(target):
                    os.remove(target)
            except Exception as ex2:
                log("  [ROLLBACK ERROR] %s: %s" % (rel, ex2))

    try:
        for item in plan:
            write_bytes(abspath(item["rel"]), item["new"])
            written.append(item["rel"])
            log("  [WRITE] " + item["rel"])

        # ---- 쓰기 후 범위 대조 검증 ----
        for item in plan:
            with open(abspath(item["rel"]), "rb") as f:
                raw = f.read()
            if raw != item["new"]:
                raise RuntimeError("쓰기 결과 불일치: " + item["rel"])
            text = raw.decode("utf-8-sig")
            if item["kind"] == "json":
                audit_json(json.loads(text))
            else:
                if protected_counts(text) != counts[item["rel"]]:
                    raise RuntimeError("보호 블록 ID 개수 변동: " + item["rel"])
                if count_tag_id(text, SCRIPT_ID) != 1:
                    raise RuntimeError("주입 스크립트 개수 이상: " + item["rel"])
                if H10_BEGIN not in text or H10_END not in text:
                    raise RuntimeError("주입 마커 누락: " + item["rel"])
        log("[G3] 적용 결과가 계약된 diff 범위 안에 있음 (검증 통과)")
    except Exception as ex:
        log("[ERROR] " + str(ex))
        rollback()
        fatal("장착 실패 - 모든 변경을 백업에서 복구했습니다. 백업: " + backup_dir)

    # ---- Git (기존 미추적 파일이 있어도 add -A 로 안전 진행) ----
    def git(*args):
        return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=180)

    try:
        r = git("add", "-A")
        if r.returncode != 0:
            fatal("git add 실패:\n" + (r.stderr or r.stdout), 2)
        r = git("commit", "-m", COMMIT_MSG)
        out = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 and "nothing to commit" not in out.lower():
            fatal("git commit 실패:\n" + out, 2)
        log("[GIT] commit 완료" if r.returncode == 0 else "[GIT] 커밋할 변경 없음 (이미 장착됨)")
        r = git("push", "origin", "main")
        if r.returncode != 0:
            fatal("git push 실패 (파일 장착은 완료, 수동 push 필요):\n" + (r.stderr or r.stdout), 2)
        log("[GIT] push origin main 완료")
    except FileNotFoundError:
        fatal("git 실행 파일을 찾을 수 없습니다.", 2)
    except subprocess.TimeoutExpired:
        fatal("git 명령 시간 초과 (파일 장착은 완료, 수동 git 필요)", 2)

    log("[STEP 10 6-AGENCIES AWAKEN COMPLETE]")


if __name__ == "__main__":
    main()
Copy
