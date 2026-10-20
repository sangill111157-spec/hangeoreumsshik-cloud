#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# upgrade_omni_link_v602.py
# RGON Omni-Link Hub v6.0.1 -> v6.0.2 업그레이드 스크립트
#
#  [🧲 흡수기] 탭 신규 기능
#   1) #autoCleanAbs 체크박스 (기본 ON, chrome.storage.local "omni_autoclean")
#        ON  : 작업 분배(OMNI_DISPATCH) 시 이전 omni_shared.entries 선삭제
#              AI 탭 전체 수거 / 새 응답 자동 흡수 시 옛 잔여 항목 정리
#        OFF : 기존처럼 누적 유지
#   2) #absClearAll [🗑️ 흡수함 전체 비우기] + 카드별 [✕ 삭제] (data-act="del")
#   3) 저장된 omni_shared 의 선두 "Copy" 접두어를 로드/저장/렌더링 시 자동 제거
#   4) omni_bridge.py 에 /api/shared/replace 추가 (omni_shared_clipboard.json 동기화)
#   5) v6.0.1 기능 100% 유지 (전체 지우기 / 새로 붙여넣기 / #autoclear / Gemini->rgon /
#      독대실 HTML 패치 / 브리지 8765 백그라운드 재기동 + 200 OK 검증)
#
# 환경변수 SHIN_AGENT_DIR 로 설치 경로를 바꿀 수 있습니다.

import os
import re
import sys
import json
import time
import shutil
import secrets
import subprocess
import tempfile
import importlib.util
import urllib.request
import urllib.error
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

NEW_VERSION = "6.0.2"
BRIDGE_PORT = 8765
DEFAULT_BASE = r"C:\Users\sangi\Downloads\shin-agent"


def resolve_base():
    env = os.environ.get("SHIN_AGENT_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    if (here / "rgon_aside_extension").exists():
        return here
    p = Path(DEFAULT_BASE)
    if os.name != "nt" and not p.exists():
        return Path.home() / "Downloads" / "shin-agent"
    return p


BASE = resolve_base()
EXT_DIR = BASE / "rgon_aside_extension"
STAMP = time.strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = BASE / "backups" / ("omni_v602_" + STAMP)

MANIFEST_P = EXT_DIR / "manifest.json"
BG_P = EXT_DIR / "background.js"
CT_P = EXT_DIR / "content_aside_bar.js"
BRIDGE_P = BASE / "omni_bridge.py"
SHARED_P = BASE / "omni_shared_clipboard.json"
HTML_RELS = ("rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html")

HTML_BEGIN = "<!-- OMNI-LINK:BEGIN -->"
HTML_END = "<!-- OMNI-LINK:END -->"

# v6.0.1 이 적용되어 있어야 하는 표식들
V601_CT_MARKERS = ('id="clearPrompt"', 'id="autoclear"', "gemini|argon", r'code = code.replace(/^Copy\s*/i, "")')

# ----------------------------------------------------------------------------
# background.js 에 들어갈 코드 조각
# ----------------------------------------------------------------------------
JS_BG_HELPERS = r"""// ---- v6.0.2: 흡수함 자동 삭제 / Copy 정화 헬퍼 (OMNI_V602_HELPERS)
const ROUND_WINDOW_MS = 30 * 60 * 1000;
const COPY_RE = /^Copy\s*/i;

async function isAutoClean() {
  return (await getStore("omni_autoclean", true)) !== false;
}

function sanitizeEntry(e) {
  if (!e || typeof e.code !== "string" || e.kind === "page" || e.kind === "selection" || !COPY_RE.test(e.code)) return false;
  e.code = e.code.replace(COPY_RE, "");
  e.lines = e.code.split("\n").length;
  e.bytes = new TextEncoder().encode(e.code).length;
  return true;
}

function emptyShared() {
  return { entries: {}, history: [], updated: Date.now() };
}

async function loadShared() {
  return withLock(async () => {
    const sh = await getStore("omni_shared", { entries: {}, history: [] });
    sh.entries = sh.entries || {};
    sh.history = sh.history || [];
    let dirty = false;
    for (const k of Object.keys(sh.entries)) {
      if (sanitizeEntry(sh.entries[k])) dirty = true;
    }
    if (dirty) await setStore("omni_shared", sh);
    return sh;
  });
}

async function clearShared(role, wait) {
  const sh = await withLock(async () => {
    let cur;
    if (!role) {
      cur = emptyShared();
    } else {
      cur = await getStore("omni_shared", emptyShared());
      cur.entries = cur.entries || {};
      cur.history = (cur.history || []).filter((h) => h.role !== role);
      delete cur.entries[role];
      cur.updated = Date.now();
    }
    await setStore("omni_shared", cur);
    return cur;
  });
  const p = bridgeFetch("/api/shared/replace", "POST", { shared: sh });
  if (wait) await p;
  broadcastAll({ type: "OMNI_STATE_PING", role: role || "*" });
  return sh;
}

async function maybeAutoClean() {
  await setStore("omni_round_ts", Date.now());
  if (await isAutoClean()) {
    await clearShared(null, true);
    return true;
  }
  return false;
}

"""

JS_BG_STORE_SHARED = r"""async function storeShared(role, entry, opts) {
  sanitizeEntry(entry);
  let trimmed = false;
  const sh = await withLock(async () => {
    const cur = await getStore("omni_shared", { entries: {}, history: [] });
    cur.entries = cur.entries || {};
    cur.history = cur.history || [];
    if (opts && opts.trimStale && (await isAutoClean())) {
      const roundTs = await getStore("omni_round_ts", 0);
      const limit = Math.max(roundTs, (entry.ts || Date.now()) - ROUND_WINDOW_MS);
      for (const k of Object.keys(cur.entries)) {
        const ets = (cur.entries[k] && cur.entries[k].ts) || 0;
        if (k !== role && ets < limit) { delete cur.entries[k]; trimmed = true; }
      }
      if (trimmed) cur.history = cur.history.filter((h) => h.role === role || !!cur.entries[h.role]);
    }
    cur.entries[role] = entry;
    cur.history.unshift({ role, ts: entry.ts, lines: entry.lines, bytes: entry.bytes, lang: entry.lang, hash: entry.hash, url: entry.url });
    cur.history = cur.history.slice(0, 40);
    cur.updated = Date.now();
    try {
      await setStore("omni_shared", cur);
    } catch (e) {
      entry.code = String(entry.code || "").slice(0, 100000);
      await setStore("omni_shared", cur);
    }
    return cur;
  });
  if (trimmed) bridgeFetch("/api/shared/replace", "POST", { shared: sh }).catch(() => {});
  else bridgeFetch("/api/shared", "POST", { role, entry }).catch(() => {});
  broadcastAll({ type: "OMNI_STATE_PING", role });
}
"""

JS_BG_COLLECT = r"""async function collect(targets) {
  const { byRole } = await scanTabs();
  const got = [];
  const results = await Promise.all((targets || []).map(async (role) => {
    const t = pickTab(byRole[role]);
    if (!t) return { role, ok: false, error: "열려 있는 탭 없음" };
    const r = await sendToTab(t.tabId, { type: "OMNI_GET_LAST_CODE" });
    if (r && r.ok && r.entry) {
      r.entry.role = role;
      sanitizeEntry(r.entry);
      got.push({ role, entry: r.entry });
      return { role, ok: true, lines: r.entry.lines, bytes: r.entry.bytes };
    }
    return { role, ok: false, error: (r && r.error) || "코드 블록 없음" };
  }));
  let cleaned = false;
  if (got.length) {
    if (await isAutoClean()) { await clearShared(null, true); cleaned = true; }
    for (const g of got) await storeShared(g.role, g.entry);
  }
  return { ok: results.some((x) => x.ok), results, cleaned };
}
"""

JS_BG_CASES = r"""    case "OMNI_GET_SHARED":
      return { ok: true, shared: await loadShared() };
    case "OMNI_CLEAR_SHARED":
      await clearShared(msg.role ? String(msg.role) : null);
      return { ok: true, cleared: msg.role || "all" };
    case "OMNI_SET_AUTOCLEAN":
      await setStore("omni_autoclean", msg.value !== false);
      return { ok: true, value: msg.value !== false };
    case "OMNI_GET_AUTOCLEAN":
      return { ok: true, value: await isAutoClean() };
"""

# ----------------------------------------------------------------------------
# content_aside_bar.js 에 들어갈 코드 조각
# ----------------------------------------------------------------------------
JS_CT_GETSHARED = r"""const COPY_RE = /^Copy\s*/i;
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
"""

JS_CT_INIT = r"""// ===== v6.0.2 흡수함 관리: 자동 삭제 토글 / 전체 비우기 / 개별 삭제 =====
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

"""

# ----------------------------------------------------------------------------
# omni_bridge.py 신규 라우트 (/api/shared/replace)
# ----------------------------------------------------------------------------
BRIDGE_ROUTE = (
    '{I}if path == "/api/shared/replace":\n'
    '{I}    sh = data.get("shared")\n'
    '{I}    if not isinstance(sh, dict) or not isinstance(sh.get("entries", {}), dict):\n'
    '{I}        return self._send(400, {"ok": False, "error": "invalid shared"})\n'
    '{I}    sh.setdefault("entries", {})\n'
    '{I}    sh.setdefault("history", [])\n'
    '{I}    sh["updated"] = time.time()\n'
    '{I}    with LOCK:\n'
    '{I}        save_json(SHARED, sh)\n'
    '{I}    return self._send(200, {"ok": True, "entries": len(sh["entries"])})\n'
)

SAFE_LOG_OLD = '        sys.stderr.write("[bridge] " + (fmt % args) + "\\n")'
SAFE_LOG_NEW = (
    '        try:  # OMNI_SAFE_LOG\n'
    '            sys.stderr.write("[bridge] " + (fmt % args) + "\\n")\n'
    '        except Exception:\n'
    '            pass'
)


# ----------------------------------------------------------------------------
# 공용 유틸
# ----------------------------------------------------------------------------
class PatchError(Exception):
    pass


def log(msg=""):
    print(msg, flush=True)


def read_text(path):
    raw = Path(path).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def atomic_write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".omni_", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        last = None
        for _ in range(5):
            try:
                os.replace(tmp, path)
                last = None
                break
            except PermissionError as e:
                last = e
                time.sleep(0.4)
        if last:
            raise last
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_text(path, text, bom=False):
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    atomic_write_bytes(path, data)


BACKED = []


def backup_file(path):
    path = Path(path)
    if not path.exists():
        return False
    rel = path.relative_to(BASE)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)
    BACKED.append(path)
    return True


def restore_all():
    for p in BACKED:
        try:
            src = BACKUP_DIR / p.relative_to(BASE)
            if src.exists():
                shutil.copy2(src, p)
        except Exception as e:
            log("   ⚠️ 복원 실패: %s (%s)" % (p, e))


def patch_str(text, old, new, marker, label):
    if marker in text:
        log("   ↩️  이미 적용됨(건너뜀): " + label)
        return text
    n = text.count(old)
    if n != 1:
        raise PatchError("앵커를 찾지 못했거나 중복(%d): %s" % (n, label))
    log("   ✅ 적용: " + label)
    return text.replace(old, new, 1)


def patch_re(text, pattern, func, marker, label, flags=0):
    if marker in text:
        log("   ↩️  이미 적용됨(건너뜀): " + label)
        return text
    ms = list(re.finditer(pattern, text, flags))
    if len(ms) != 1:
        raise PatchError("앵커를 찾지 못했거나 중복(%d): %s" % (len(ms), label))
    m = ms[0]
    log("   ✅ 적용: " + label)
    return text[:m.start()] + func(m) + text[m.end():]


def validate_js(files):
    node = shutil.which("node")
    if not node:
        log("   ⚠️ node 를 찾지 못해 JS 문법 검증을 건너뜁니다.")
        return True
    ok = True
    with tempfile.TemporaryDirectory(prefix="omni_chk_") as td:
        for name, text in files.items():
            p = Path(td) / name
            p.write_text(text, encoding="utf-8")
            r = subprocess.run([node, "--check", str(p)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode == 0:
                log("   ✅ node --check 통과: " + name)
            else:
                ok = False
                log("   ❌ node --check 실패: " + name + "\n" + (r.stderr or r.stdout))
    return ok


# ----------------------------------------------------------------------------
# 파일별 패치 계산 (메모리 상에서만 수행)
# ----------------------------------------------------------------------------
def build_content(text):
    text = text.replace("\r\n", "\n")
    # v6.0.0 초판의 reply 오타가 남아 있으면 함께 교정 (멱등)
    text = text.replace('source: "rgon-omni-ext", OMNI_REPLY"', 'source: "rgon-omni-ext", type: "OMNI_REPLY"')

    for mk in V601_CT_MARKERS:
        if mk not in text:
            raise PatchError("v6.0.1 표식을 찾지 못했습니다 (%s). 먼저 upgrade_omni_link_v601.py 를 실행하세요." % mk)

    # (1) UI: 흡수함 전체 비우기 버튼
    text = patch_str(
        text,
        '<button class="b" id="absPage">📄 화면 텍스트 흡수</button></div>',
        '<button class="b" id="absPage">📄 화면 텍스트 흡수</button>'
        '<button class="b o" id="absClearAll" type="button">🗑️ 흡수함 전체 비우기</button></div>',
        'id="absClearAll"', "[1-a] 흡수기 상단 [🗑️ 흡수함 전체 비우기] 버튼 (#absClearAll)")
    # (1) UI: 자동 삭제 ON/OFF 체크박스
    text = patch_str(
        text,
        '<div class="row"><label><input type="checkbox" id="autoAbs" checked> 응답 완료 감지 시 자동 흡수 (Claude/GPT/Grok 탭)</label></div>',
        '<div class="row"><label><input type="checkbox" id="autoAbs" checked> 응답 완료 감지 시 자동 흡수 (Claude/GPT/Grok 탭)</label></div>\n'
        '      <div class="row"><label><input type="checkbox" id="autoCleanAbs" checked> ☑ 새 작업 발사/수거 시 이전 흡수함 자동 삭제 (ON/OFF)</label></div>',
        'id="autoCleanAbs"', "[1-b] 자동 삭제 ON/OFF 체크박스 (#autoCleanAbs)")
    # (2) CSS: 소형 삭제 버튼
    text = patch_str(
        text,
        'h4{margin:6px 0;font-size:12.5px;color:#b9c0ff}',
        'h4{margin:6px 0;font-size:12.5px;color:#b9c0ff}\n'
        'button.b.sm{padding:3px 8px;font-size:11px;border-radius:7px;background:rgba(220,60,60,.55)}\n'
        'button.b.sm:hover{background:rgba(220,60,60,.85)}\n'
        '.card .ch .rt{display:flex;align-items:center;gap:6px}',
        'button.b.sm{', "[2-a] 소형 [✕ 삭제] 버튼 CSS")
    # (2) 카드 헤더 우측 [✕ 삭제]
    text = patch_str(
        text,
        '<small>${esc(e.lang || "text")} · ${e.lines}줄 · ${fmtKB(e.bytes)}</small></div>',
        '<span class="rt"><small>${esc(e.lang || "text")} · ${e.lines}줄 · ${fmtKB(e.bytes)}</small>'
        '<button class="b sm" data-act="del" type="button" title="이 항목만 삭제">✕ 삭제</button></span></div>',
        'data-act="del"', "[2-b] 카드 헤더 우측 [✕ 삭제] 버튼 (data-act=\"del\")")
    # (3) 렌더링 시 Copy 제거
    text = patch_str(
        text,
        r'<pre class="pv">${esc(String(e.code || "").slice(0, 700))}${String(e.code || "").length > 700 ? "\n…" : ""}</pre>',
        r'<pre class="pv">${esc(cleanCode(e).slice(0, 700))}${cleanCode(e).length > 700 ? "\n…" : ""}</pre>',
        "cleanCode(e).slice(0, 700)", "[3-a] 카드 미리보기 렌더링 시 Copy 정화")
    # (3) 로드 시 Copy 제거 (getShared 교체)
    text = patch_re(
        text,
        r"^async function getShared\(\) \{\n.*?^\}\n",
        lambda m: JS_CT_GETSHARED,
        "function cleanEntry(", "[3-b] getShared() 로드 시 Copy 정화 + 저장소 재기록", re.M | re.S)
    # (3) 저장 시 Copy 제거
    text = patch_str(
        text,
        "async function storeEntry(role, e) {\n  e.role = role;",
        "async function storeEntry(role, e) {\n  cleanEntry(e);\n  e.role = role;",
        "cleanEntry(e);", "[3-c] storeEntry() 저장 시 Copy 정화")
    # (1-b) 자동 흡수 표식 (오래된 잔여 항목 정리 대상)
    text = patch_str(
        text,
        'const r = await rt({ type: "OMNI_STORE_SHARED", role: state.role, entry: e });',
        'const r = await rt({ type: "OMNI_STORE_SHARED", role: state.role, entry: e, auto: true });',
        "entry: e, auto: true", "[1-c] 자동 흡수 시 옛 잔여 항목 정리 플래그 전달")
    # (1)(2) 핸들러 블록
    text = patch_re(
        text,
        r"^// -+ init$",
        lambda m: JS_CT_INIT + m.group(0),
        "v6.0.2 흡수함 관리", "[1-d][2-c] 자동 삭제 토글 / 전체 비우기 / 개별 삭제 핸들러", re.M)
    text = re.sub(r'const VER = "[^"]*";', 'const VER = "%s";' % NEW_VERSION, text, count=1)
    return text


def build_background(text):
    text = text.replace("\r\n", "\n")
    m = re.search(r'const OMNI_TOKEN = "([^"]*)";', text)
    if not m:
        raise PatchError("background.js 에서 OMNI_TOKEN 선언을 찾지 못했습니다.")
    token = m.group(1)
    if not re.fullmatch(r"[0-9a-fA-F]{16,}", token):
        token = secrets.token_hex(16)
        text = text[:m.start()] + 'const OMNI_TOKEN = "%s";' % token + text[m.end():]
        log("   🔐 background.js 토큰이 비정상이라 새로 발급했습니다.")

    text = patch_re(
        text, r"^// -+ role mapping$",
        lambda mm: JS_BG_HELPERS + mm.group(0),
        "OMNI_V602_HELPERS", "[bg-1] 자동 삭제 / 정화 헬퍼 함수", re.M)
    text = patch_re(
        text, r"^async function storeShared\(role, entry\) \{\n.*?^\}\n",
        lambda mm: JS_BG_STORE_SHARED,
        "opts.trimStale", "[bg-2] storeShared(): 정화 + 자동 흡수 시 옛 잔여 항목 정리", re.M | re.S)
    text = patch_re(
        text, r"^async function collect\(targets\) \{\n.*?^\}\n",
        lambda mm: JS_BG_COLLECT,
        "const got = [];", "[bg-3] collect(): 수거 성공 시 이전 흡수함 비우고 새 결과만 저장", re.M | re.S)
    text = patch_re(
        text,
        r"^async function dispatch\(targets, prompt, autoSend, perRole\) \{\n  const \{ byRole \} = await scanTabs\(\);\n",
        lambda mm: mm.group(0) + "  if ((targets || []).some((r) => pickTab(byRole[r]))) await maybeAutoClean();\n",
        "await maybeAutoClean()", "[bg-4] dispatch(): 발사 직전 흡수함 자동 삭제", re.M)
    text = patch_str(
        text,
        "await storeShared(msg.role, msg.entry);",
        "await storeShared(msg.role, msg.entry, { trimStale: !!msg.auto });",
        "{ trimStale: !!msg.auto }", "[bg-5] OMNI_STORE_SHARED: auto 플래그 전달")
    text = patch_re(
        text,
        r'^ *case "OMNI_GET_SHARED":\n *return \{ ok: true, shared: await getStore\("omni_shared", \{ entries: \{\}, history: \[\] \}\) \};\n',
        lambda mm: JS_BG_CASES,
        'case "OMNI_CLEAR_SHARED"', "[bg-6] OMNI_CLEAR_SHARED / OMNI_SET_AUTOCLEAN 메시지", re.M)
    text = re.sub(r'const OMNI_VERSION = "[^"]*";', 'const OMNI_VERSION = "%s";' % NEW_VERSION, text, count=1)
    return text, token


def build_bridge(text, token):
    text = text.replace("\r\n", "\n")
    new, n = re.subn(r'(?m)^TOKEN = ".*"[ \t]*$', lambda m: "TOKEN = " + json.dumps(token), text)
    if n != 1:
        raise PatchError("omni_bridge.py 에서 TOKEN 선언을 찾지 못했습니다 (발견 %d개)." % n)
    text = new
    text = re.sub(r'(?m)^VERSION = "[^"]*"', 'VERSION = "%s"' % NEW_VERSION, text, count=1)
    if "OMNI_SAFE_LOG" not in text and SAFE_LOG_OLD in text:
        text = text.replace(SAFE_LOG_OLD, SAFE_LOG_NEW, 1)
    text = patch_re(
        text,
        r'^( +)if path == "/api/shared":\n( +)role = str\(data\.get\("role"\) or ""\)\[:40\]',
        lambda m: BRIDGE_ROUTE.replace("{I}", m.group(1)) + m.group(0),
        '"/api/shared/replace"', "[br-1] 브리지 /api/shared/replace 라우트", re.M)
    return text


def build_manifest(text):
    m = json.loads(text)
    m["version"] = NEW_VERSION
    perms = list(m.get("permissions", []))
    if "clipboardRead" not in perms:
        perms.append("clipboardRead")
    m["permissions"] = perms
    return json.dumps(m, ensure_ascii=False, indent=2) + "\n"


# ----------------------------------------------------------------------------
# omni_shared_clipboard.json 의 Copy 접두어 정화
# ----------------------------------------------------------------------------
COPY_RX = re.compile(r"^Copy\s*", re.I)


def sanitize_shared_file():
    if not SHARED_P.exists():
        return 0
    try:
        data = json.loads(read_text(SHARED_P)[0])
    except Exception as e:
        log("   ⚠️ omni_shared_clipboard.json 을 읽지 못해 건너뜁니다: %s" % e)
        return 0
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, dict):
        return 0
    n = 0
    for e in entries.values():
        if (isinstance(e, dict) and isinstance(e.get("code"), str)
                and e.get("kind") not in ("page", "selection") and COPY_RX.match(e["code"])):
            e["code"] = COPY_RX.sub("", e["code"], count=1)
            e["lines"] = len(e["code"].split("\n"))
            e["bytes"] = len(e["code"].encode("utf-8"))
            n += 1
    if n:
        atomic_write_text(SHARED_P, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return n


# ----------------------------------------------------------------------------
# 독대실 HTML: v6.0.1 블록 유지 확인 (없거나 구버전이면 v6.0.1 스크립트의 patch_html 로 복구)
# ----------------------------------------------------------------------------
def load_v601():
    for p in (Path(__file__).resolve().parent / "upgrade_omni_link_v601.py", BASE / "upgrade_omni_link_v601.py"):
        if p.exists():
            try:
                spec = importlib.util.spec_from_file_location("upgrade_omni_link_v601", str(p))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
            except Exception as e:
                log("   ⚠️ upgrade_omni_link_v601.py 로드 실패: %s" % e)
    return None


def ensure_html(path):
    html, _ = read_text(path)
    good = (html.count(HTML_BEGIN) == 1 and html.count(HTML_END) == 1
            and "omniClearBtn" in html and "omniAutoClear" in html)
    low = html.lower()
    studio, firefly = low.count("studio"), low.count("firefly")
    if good:
        return "유지(변경 없음)", studio, firefly
    mod = load_v601()
    if mod is None:
        raise RuntimeError("OMNI-LINK 블록이 없거나 구버전인데 upgrade_omni_link_v601.py 를 찾지 못했습니다.")
    mod.BASE = BASE
    mod.BACKUP_DIR = BACKUP_DIR
    mode, _ = mod.patch_html(path)
    html2, _ = read_text(path)
    outside = re.sub(re.escape(HTML_BEGIN) + r".*?" + re.escape(HTML_END) + r"[ \t]*\r?\n?", "", html2, flags=re.S).lower()
    if outside.count("studio") != studio or outside.count("firefly") != firefly:
        raise RuntimeError("복구 후 STUDIO v5 / firefly 보존 확인 실패")
    return "v6.0.1 블록으로 복구(" + mode + ")", studio, firefly


# ----------------------------------------------------------------------------
# 브리지: 포트 정리 / 재기동 / 헬스체크 (v6.0.1 로직 유지)
# ----------------------------------------------------------------------------
def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout or "")
    except Exception:
        return -1, ""


def find_listen_pids(port):
    pids = set()
    if os.name == "nt":
        _, out = run_cmd(["netstat", "-ano", "-p", "TCP"])
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[0].upper() == "TCP" and parts[1].rsplit(":", 1)[-1] == str(port) and parts[2].endswith(":0"):
                try:
                    pids.add(int(parts[-1]))
                except ValueError:
                    pass
    else:
        _, out = run_cmd(["lsof", "-ti", "tcp:%d" % port, "-sTCP:LISTEN"])
        for tok in out.split():
            if tok.isdigit():
                pids.add(int(tok))
    return pids


def process_cmdline(pid):
    if os.name == "nt":
        rc, out = run_cmd(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                           "(Get-CimInstance Win32_Process -Filter 'ProcessId=%d').CommandLine" % pid])
        if out.strip():
            return out.strip()
        rc, out = run_cmd(["wmic", "process", "where", "ProcessId=%d" % pid, "get", "CommandLine", "/value"])
        return out.strip()
    try:
        return Path("/proc/%d/cmdline" % pid).read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
    except Exception:
        _, out = run_cmd(["ps", "-p", str(pid), "-o", "args="])
        return out.strip()


def kill_pid(pid):
    if os.name == "nt":
        run_cmd(["taskkill", "/PID", str(pid), "/F"])
    else:
        try:
            os.kill(pid, 15)
        except Exception:
            pass


_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def health(token, timeout=3):
    req = urllib.request.Request("http://127.0.0.1:%d/api/health" % BRIDGE_PORT, headers={"X-Omni-Token": token})
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return 0, None


def probe_replace_route(token):
    """부작용 없이 /api/shared/replace 라우트 존재 확인 (잘못된 본문 -> 400 이면 라우트 존재)."""
    req = urllib.request.Request(
        "http://127.0.0.1:%d/api/shared/replace" % BRIDGE_PORT,
        data=json.dumps({"shared": "probe"}).encode("utf-8"), method="POST",
        headers={"X-Omni-Token": token, "Content-Type": "application/json"})
    try:
        with _OPENER.open(req, timeout=4) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def start_bridge():
    exe = sys.executable
    if os.name == "nt":
        d = Path(exe)
        if d.name.lower() == "pythonw.exe" and (d.parent / "python.exe").exists():
            exe = str(d.parent / "python.exe")
    logf = open(BASE / "omni_bridge.log", "ab")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    else:
        kw["start_new_session"] = True
    try:
        p = subprocess.Popen([exe, "-u", str(BRIDGE_P)], cwd=str(BASE), stdin=subprocess.DEVNULL,
                             stdout=logf, stderr=logf, env=env, close_fds=True, **kw)
    finally:
        logf.close()
    return p


def log_tail(n=12):
    try:
        lines = (BASE / "omni_bridge.log").read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join("      | " + x for x in lines[-n:])
    except Exception:
        return ""


def ensure_bridge(token, bridge_changed):
    code, body = health(token)
    if code == 200 and body and body.get("version") == NEW_VERSION and not bridge_changed:
        log("   ♻️  실행 중인 브리지를 재사용합니다 (v%s, 토큰 일치)." % NEW_VERSION)
        return code, body

    pids = find_listen_pids(BRIDGE_PORT)
    for pid in sorted(pids):
        cmd = process_cmdline(pid)
        if "omni_bridge" in cmd.lower():
            log("   🧹 기존 브리지 종료: PID %d" % pid)
            kill_pid(pid)
        else:
            log("   ❌ 포트 %d 를 다른 프로세스(PID %d)가 점유 중이라 종료하지 않았습니다: %s" % (BRIDGE_PORT, pid, cmd[:120] or "알 수 없음"))
            return 0, None
    for _ in range(25):
        if not find_listen_pids(BRIDGE_PORT):
            break
        time.sleep(0.2)
    else:
        log("   ❌ 포트 %d 가 해제되지 않았습니다." % BRIDGE_PORT)
        return 0, None

    p = start_bridge()
    log("   🚀 브리지 백그라운드 기동 (PID %d, CREATE_NO_WINDOW) — 로그: %s" % (p.pid, BASE / "omni_bridge.log"))

    code, body = 0, None
    for _ in range(40):
        if p.poll() is not None:
            log("   ❌ 브리지 프로세스가 즉시 종료되었습니다 (exit %s)\n%s" % (p.returncode, log_tail()))
            return 0, None
        code, body = health(token)
        if code == 200:
            break
        time.sleep(0.3)
    return code, body


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    log("=" * 64)
    log("✨ RGON Omni-Link Hub v6.0.1 → v%s 업그레이드 (흡수함 자동 삭제 / 비우기)" % NEW_VERSION)
    log("   대상 폴더: %s" % BASE)
    log("=" * 64)

    for p in (MANIFEST_P, BG_P, CT_P, BRIDGE_P):
        if not p.exists():
            log("❌ 필수 파일이 없습니다: %s\n   먼저 build_omni_link_communicator.py 와 upgrade_omni_link_v601.py 를 실행하세요." % p)
            return 1

    log("[1/7] 패치 계산 및 사전 검증 (디스크는 아직 변경하지 않음)")
    try:
        man_old, _ = read_text(MANIFEST_P)
        bg_old, _ = read_text(BG_P)
        ct_old, _ = read_text(CT_P)
        br_old, _ = read_text(BRIDGE_P)
        new_bg, token = build_background(bg_old)
        new_ct = build_content(ct_old)
        new_br = build_bridge(br_old, token)
        new_man = build_manifest(man_old)
    except PatchError as e:
        log("❌ " + str(e))
        log("   기존 파일은 변경되지 않았습니다.")
        return 1
    except Exception as e:
        log("❌ 패치 계산 실패: %s (기존 파일 변경 없음)" % e)
        return 1

    if not validate_js({"background.js": new_bg, "content_aside_bar.js": new_ct}):
        log("❌ JS 문법 오류 — 기존 파일을 건드리지 않고 중단합니다.")
        return 1
    try:
        compile(new_br, "omni_bridge.py", "exec")
        log("   ✅ omni_bridge.py 컴파일 통과 / manifest.json 파싱 통과")
    except Exception as e:
        log("❌ omni_bridge.py 검증 실패: %s" % e)
        return 1

    log("[2/7] 원자적 백업 → %s" % BACKUP_DIR)
    n_bak = 0
    for p in (MANIFEST_P, BG_P, CT_P, BRIDGE_P, SHARED_P):
        n_bak += 1 if backup_file(p) else 0
    log("   백업된 파일: %d개 (HTML은 변경이 필요할 때만 개별 백업)" % n_bak)

    log("[3/7] 확장프로그램 / 브리지 파일 적용 + 토큰 동기화")
    try:
        atomic_write_text(MANIFEST_P, new_man)
        atomic_write_text(BG_P, new_bg)
        atomic_write_text(CT_P, new_ct)
        atomic_write_text(BRIDGE_P, new_br)
        bg_now, ct_now, br_now = read_text(BG_P)[0], read_text(CT_P)[0], read_text(BRIDGE_P)[0]
        bg_t = re.search(r'const OMNI_TOKEN = "([^"]*)";', bg_now).group(1)
        br_t = re.search(r'(?m)^TOKEN = "([^"]*)"', br_now).group(1)
        if not bg_t or bg_t != br_t or bg_t != token:
            raise RuntimeError("토큰 불일치 감지")
        log("   🔐 토큰 동기화 확인: background.js == omni_bridge.py (…%s)" % token[-4:])
        checks = [
            ('id="autoCleanAbs"' in ct_now, "#autoCleanAbs"),
            ('id="absClearAll"' in ct_now, "#absClearAll"),
            ('data-act="del"' in ct_now, "data-act=del"),
            ('id="clearPrompt"' in ct_now and 'id="autoclear"' in ct_now and "gemini|argon" in ct_now, "v6.0.1 기능 유지"),
            ('case "OMNI_CLEAR_SHARED"' in bg_now and "await maybeAutoClean()" in bg_now, "background 자동 삭제"),
            ('"/api/shared/replace"' in br_now, "bridge replace 라우트"),
        ]
        for ok_, name in checks:
            if not ok_:
                raise RuntimeError("적용 검증 실패: " + name)
        if not validate_js({"background.js": bg_now, "content_aside_bar.js": ct_now}):
            raise RuntimeError("적용 후 JS 검증 실패")
        compile(br_now, "omni_bridge.py", "exec")
    except Exception as e:
        log("❌ 적용 실패: %s — 백업에서 복원합니다." % e)
        restore_all()
        return 1

    log("[4/7] omni_shared_clipboard.json 의 'Copy' 접두어 정화")
    try:
        n = sanitize_shared_file()
        log("   ✅ 정화된 항목: %d개" % n if n else "   ↩️  정화할 항목 없음")
    except Exception as e:
        log("   ⚠️ 정화 실패(원본 유지): %s" % e)

    log("[5/7] 독대실 HTML 점검 (STUDIO v5 · firefly · OMNI-LINK 블록 유지 확인)")
    html_ok = 0
    for rel in HTML_RELS:
        p = BASE / rel
        if not p.exists():
            log("   ⏭️  없음(건너뜀): " + rel)
            continue
        try:
            status, studio, firefly = ensure_html(p)
            html_ok += 1
            log("   ✅ %s: %s (studio %d · firefly %d)" % (rel, status, studio, firefly))
        except Exception as e:
            log("   ❌ 점검/복구 실패: %s — %s" % (rel, e))

    log("[6/7] 로컬 브리지 재기동 및 연결 검증 (127.0.0.1:%d)" % BRIDGE_PORT)
    bridge_changed = br_old.replace("\r\n", "\n") != new_br
    code, body = ensure_bridge(token, bridge_changed)

    ok = False
    if code == 200 and body and body.get("ok"):
        ok = True
        log("   🟢 로컬 브리지 연결됨 (200 OK) — v%s · base=%s" % (body.get("version"), body.get("base")))
        bad, _ = health(token[::-1] if token != token[::-1] else "x" * len(token))
        log("   🔒 잘못된 토큰 차단 확인: HTTP %s" % bad)
        rc = probe_replace_route(token)
        if rc == 400:
            log("   🧪 /api/shared/replace 라우트 확인: HTTP 400 (라우트 존재, 잘못된 본문 거부)")
        else:
            ok = False
            log("   🔴 /api/shared/replace 라우트 확인 실패: HTTP %s\n%s" % (rc, log_tail()))
    else:
        log("   🔴 로컬 브리지 연결 실패 (HTTP %s)\n%s" % (code, log_tail()))

    log("[7/7] 요약")
    log("   - 확인된 독대실 HTML 파일 수: %d" % html_ok)
    log("   - 확장프로그램 반영: chrome://extensions → RGON Omni-Link → 새로고침(↻) 후, 열려 있는 AI 탭을 새로고침하세요.")
    log("   - 자동 삭제 토글은 [🧲 흡수기] 탭의 '☑ 새 작업 발사/수거 시 이전 흡수함 자동 삭제 (ON/OFF)' 입니다 (기본 ON).")
    log("   - 백업 위치: %s" % BACKUP_DIR)
    log("   - 브리지 로그: %s" % (BASE / "omni_bridge.log"))
    if not ok:
        log("⚠️ 파일 업그레이드는 적용되었지만 브리지 검증에 실패했습니다. 위 로그를 확인 후 다시 실행하세요.")
        return 2
    log("OMNI-LINK v6.0.2 UPGRADE COMPLETE!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
