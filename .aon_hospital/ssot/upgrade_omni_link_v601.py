#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# upgrade_omni_link_v601.py
# RGON Omni-Link Hub v6.0.0 -> v6.0.1 업그레이드 스크립트
#
#  1) 작업 분배 입력창: [🗑️ 전체 지우기] / [📋 새로 붙여넣기] / [발사 후 입력창 자동 비우기] (확장 패널 + 독대실 HTML_BLOCK)
#  2) extractLastCode(): Genspark 복사 버튼 텍스트 "Copy" 접두어 제거
#  3) detectModelRole(): Gemini / Gemini 4 Argon 표시 탭을 grok 으로 오인하지 않고 rgon 으로 처리
#  4) 독대실 HTML 패치: 문자열 길이 비교 제거(CRLF 대응), STUDIO v5 / firefly 보존만 확인 후 <body> 직후 삽입
#  5) omni_bridge.py 토큰 <-> background.js OMNI_TOKEN 동기화, 8765 포트 정리/재기동(CREATE_NO_WINDOW), /api/health 검증
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
import urllib.request
import urllib.error
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

NEW_VERSION = "6.0.1"
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
BACKUP_DIR = BASE / "backups" / ("omni_v601_" + STAMP)

MANIFEST_P = EXT_DIR / "manifest.json"
BG_P = EXT_DIR / "background.js"
CT_P = EXT_DIR / "content_aside_bar.js"
BRIDGE_P = BASE / "omni_bridge.py"
HTML_RELS = ("rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html")

HTML_BEGIN = "<!-- OMNI-LINK:BEGIN -->"
HTML_END = "<!-- OMNI-LINK:END -->"

# ----------------------------------------------------------------------------
# 독대실 HTML_BLOCK (v6.0.1: 편의 버튼 + 자동 비우기 추가)
# ----------------------------------------------------------------------------
HTML_BLOCK = HTML_BEGIN + r"""
<div id="omniLinkController" style="margin:10px auto;max-width:1100px;padding:12px 16px;border-radius:16px;color:#e9ecff;background:linear-gradient(135deg,rgba(60,40,160,.88),rgba(0,110,160,.78));border:1px solid rgba(255,255,255,.25);box-shadow:0 8px 28px rgba(60,40,200,.3);font-family:'Pretendard','Noto Sans KR',system-ui,sans-serif">
  <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center">
    <button id="omniOpenBtn" type="button" style="padding:10px 16px;font-size:14px;font-weight:700;color:#fff;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.45);border-radius:12px;cursor:pointer">[✨ AI 만능 소통창 (르곤⇄클로드⇄GPT⇄그록 직결 허브) 열기]</button>
    <span id="omniExtState" style="font-size:12px;opacity:.9">확장프로그램 확인 중…</span>
  </div>
  <details style="margin-top:8px">
    <summary style="cursor:pointer;font-size:13px">⚡ 독대실에서 바로 분배하기 (Claude / GPT / Grok)</summary>
    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px">
      <select id="omniPreset" style="padding:7px 10px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(0,0,0,.35);color:#fff">
        <option value="" style="color:#000">— 지시문 템플릿 —</option>
        <option value="design" style="color:#000">코드 설계 요청</option>
        <option value="review" style="color:#000">코드 리뷰/개선</option>
        <option value="ad" style="color:#000">10초 광고 카피</option>
      </select>
      <button type="button" id="omniClearBtn" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(220,60,60,.55);color:#fff;cursor:pointer">🗑️ 전체 지우기</button>
      <button type="button" id="omniPasteBtn" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(0,150,255,.5);color:#fff;cursor:pointer">📋 새로 붙여넣기</button>
    </div>
    <textarea id="omniPrompt" rows="4" placeholder="사령관 지시문 — 열려 있는 AI 탭 입력창에 자동으로 주입됩니다." style="width:100%;box-sizing:border-box;margin-top:8px;padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,.3);background:rgba(0,0,0,.35);color:#fff"></textarea>
    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px">
      <label style="font-size:12px"><input type="checkbox" id="omniAutoSend" checked> 자동 전송</label>
      <label style="font-size:12px"><input type="checkbox" id="omniAutoClear" checked> 발사 후 입력창 자동 비우기</label>
      <button type="button" data-omni-fire="claude,gpt" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(16,185,129,.55);color:#fff;cursor:pointer">🚀 Claude + GPT 동시 발사</button>
      <button type="button" data-omni-fire="grok" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(245,158,11,.55);color:#fff;cursor:pointer">🎯 Grok 카피 발사</button>
      <button type="button" id="omniCollectBtn" style="padding:7px 12px;border-radius:9px;border:1px solid rgba(255,255,255,.4);background:rgba(0,150,255,.5);color:#fff;cursor:pointer">🧲 AI 탭 코드 수거</button>
    </div>
    <pre id="omniOut" style="white-space:pre-wrap;font-size:12px;margin:8px 0 0;padding:8px;border-radius:10px;background:rgba(0,0,0,.3)">대기 중…</pre>
  </details>
</div>
<script>
(function () {
  var pending = {}, seq = 0;
  var stateEl = document.getElementById("omniExtState");
  var outEl = document.getElementById("omniOut");
  var promptEl = document.getElementById("omniPrompt");
  function call(type, data) {
    return new Promise(function (resolve) {
      var id = "o" + (++seq);
      pending[id] = resolve;
      window.postMessage(Object.assign({ source: "rgon-omni-page", type: type, id: id }, data || {}), location.origin);
      setTimeout(function () {
        if (pending[id]) { delete pending[id]; resolve({ ok: false, error: "확장프로그램 응답 없음 (RGON Omni-Link 확장 로드/새로고침 확인)" }); }
      }, 8000);
    });
  }
  window.addEventListener("message", function (ev) {
    if (ev.source !== window || ev.origin !== location.origin) return;
    var d = ev.data;
    if (!d || d.source !== "rgon-omni-ext") return;
    if (d.type === "OMNI_REPLY" && pending[d.id]) { var f = pending[d.id]; delete pending[d.id]; f(d.payload || {}); }
    else if (d.type === "OMNI_SHARED_UPDATED") { summarize(); }
    else if (d.type === "OMNI_JOB_DISPATCHED") { outEl.textContent = "📥 브리지 작업이 탭에 주입되었습니다."; }
  });
  function fmt(results) {
    return (results || []).map(function (r) {
      return (r.ok ? "✅ " : "⚠️ ") + r.role + ": " + (r.ok ? (r.sent ? "입력+전송 완료" : "입력 완료") : (r.error || "실패"));
    }).join("\n") || "결과 없음";
  }
  async function summarize() {
    var r = await call("OMNI_GET_SHARED");
    var en = (r.shared && r.shared.entries) || {};
    var parts = ["claude", "gpt", "grok"].filter(function (k) { return en[k]; }).map(function (k) {
      return k + ": " + en[k].lines + "줄 / " + (en[k].bytes / 1024).toFixed(1) + "KB / 함수 " + (en[k].funcCount || 0) + "개";
    });
    if (parts.length) outEl.textContent = "🧲 흡수 현황\n" + parts.join("\n");
  }
  document.getElementById("omniOpenBtn").addEventListener("click", async function () {
    var r = await call("OMNI_TOGGLE");
    if (!r.ok) stateEl.textContent = "⚠️ " + (r.error || "확장프로그램 미연결");
  });

  // ---- v6.0.1 편의 기능: 템플릿 / 전체 지우기 / 새로 붙여넣기 / 발사 후 자동 비우기
  var PRESETS = {
    design: "다음 기능을 구현하는 단일 Python 스크립트를 설계·작성해 주세요. 코드 블록 하나로, 주요 함수에는 주석을, main 진입점을 포함해 주세요:\n\n",
    review: "아래 코드를 리뷰하고 버그·예외처리·성능을 개선한 전체 코드를 코드 블록 하나로 출력해 주세요:\n\n",
    ad: "10초 광고 영상(STUDIO v5)용 한국어 카피를 훅-혜택-CTA 구조로 작성해 주세요:\n\n"
  };
  document.getElementById("omniPreset").addEventListener("change", function (ev) {
    var p = PRESETS[ev.target.value];
    if (p) { promptEl.value = p + promptEl.value; promptEl.focus(); }
    ev.target.value = "";
  });
  document.getElementById("omniClearBtn").addEventListener("click", function () {
    promptEl.value = "";
    promptEl.focus();
  });
  document.getElementById("omniPasteBtn").addEventListener("click", async function () {
    promptEl.value = "";
    promptEl.focus();
    try {
      var t = await navigator.clipboard.readText();
      promptEl.value = t;
      promptEl.focus();
      outEl.textContent = "📋 클립보드 내용을 붙여넣었습니다 (" + t.length + "자)";
    } catch (e) {
      outEl.textContent = "⚠️ 클립보드 읽기 권한이 필요합니다. 입력창에서 Ctrl+V 로 붙여넣어 주세요.";
    }
  });

  document.querySelectorAll("[data-omni-fire]").forEach(function (b) {
    b.addEventListener("click", async function () {
      var targets = b.getAttribute("data-omni-fire").split(",");
      var prompt = promptEl.value;
      if (!prompt.trim()) { outEl.textContent = "지시문을 입력하세요."; return; }
      outEl.textContent = "발사 중…";
      var r = await call("OMNI_DISPATCH", { targets: targets, prompt: prompt, autoSend: document.getElementById("omniAutoSend").checked, grokPrefix: targets.indexOf("grok") >= 0 });
      outEl.textContent = r.results ? fmt(r.results) : "⚠️ " + (r.error || "실패");
      var allOk = !!(r.results && r.results.length && r.results.every(function (x) { return x && x.ok; }));
      if (allOk && document.getElementById("omniAutoClear").checked) {
        promptEl.value = "";
        promptEl.focus();
      }
    });
  });
  document.getElementById("omniCollectBtn").addEventListener("click", async function () {
    outEl.textContent = "수거 중…";
    var r = await call("OMNI_COLLECT", { targets: ["claude", "gpt", "grok"] });
    outEl.textContent = (r.results || []).map(function (x) {
      return (x.ok ? "✅ " : "⚠️ ") + x.role + ": " + (x.ok ? (x.lines + "줄 / " + (x.bytes / 1024).toFixed(1) + "KB") : (x.error || "실패"));
    }).join("\n") || ("⚠️ " + (r.error || "결과 없음"));
  });
  call("OMNI_PING").then(function (r) {
    stateEl.textContent = r.ok ? "🟢 확장프로그램 연결됨 v" + r.ver : "🔴 확장프로그램 미연결 — chrome://extensions 에서 rgon_aside_extension 로드/새로고침";
    if (r.ok) summarize();
  });
})();
</script>
""" + HTML_END + "\n"

# ----------------------------------------------------------------------------
# content_aside_bar.js 에 삽입할 코드 조각
# ----------------------------------------------------------------------------
JS_HANDLERS = r"""
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
"""

JS_FIRE_AFTER = r"""  const fired = !!(r && r.results && r.results.length && r.results.every((x) => x && x.ok));
  const acEl = $("#autoclear");
  if (fired && acEl && acEl.checked) { const pEl = $("#prompt"); pEl.value = ""; pEl.focus(); }
  else if (r && r.results && r.results.some((x) => x && x.ok) && !fired) toast("일부 대상 실패 — 재시도를 위해 입력창을 유지했습니다.", 3500);
"""

JS_GEMINI = r"""  const gemBtns = document.querySelectorAll("button, [role='button'], [role='combobox'], [aria-haspopup]");
  for (const g of gemBtns) {
    const gt = (g.innerText || "").trim();
    if (gt && gt.length <= 60 && /gemini|argon/i.test(gt) && visible(g)) return "rgon";
  }
  let r = byTitle(document.title || "");"""


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
    # (1) 편의 버튼 UI
    text = patch_str(
        text,
        '<option value="ad">10초 광고 카피</option></select></div>',
        '<option value="ad">10초 광고 카피</option></select>'
        '<button class="b" id="clearPrompt" type="button">🗑️ 전체 지우기</button>'
        '<button class="b c" id="pastePrompt" type="button">📋 새로 붙여넣기</button></div>',
        'id="clearPrompt"', "[1-a] 템플릿 옆 🗑️ 전체 지우기 / 📋 새로 붙여넣기 버튼")
    text = patch_str(
        text,
        'id="grokPrefix" checked> Grok 카피 모드 접두어</label></div>',
        'id="grokPrefix" checked> Grok 카피 모드 접두어</label>'
        '<label><input type="checkbox" id="autoclear" checked> 발사 후 입력창 자동 비우기</label></div>',
        'id="autoclear"', "[1-b] ☑ 발사 후 입력창 자동 비우기 (#autoclear)")
    # (1) 발사 성공 시 자동 비우기
    text = patch_re(
        text,
        r'(?m)^[ \t]*\$\("#fireOut"\)\.innerHTML = r && r\.results \? fmtResults\(r\.results\) :[^\n]*\n',
        lambda m: m.group(0) + JS_FIRE_AFTER,
        "const fired =", "[1-c] fire() 성공 시 #prompt 자동 비우기")
    # (1) 버튼 핸들러
    text = patch_re(
        text,
        r'(?m)^\$\("#fireAll"\)\.addEventListener\([^\n]*\n',
        lambda m: m.group(0) + JS_HANDLERS,
        '$("#clearPrompt")', "[1-d] 전체 지우기 / 새로 붙여넣기 핸들러")
    # (2) Copy 접두어 제거
    text = patch_str(
        text,
        'const code = b.txt.replace(/\\s+$/, "");',
        'let code = b.txt.replace(/\\s+$/, "");\n    code = code.replace(/^Copy\\s*/i, "");',
        'code = code.replace(/^Copy\\s*/i, "")', "[2] extractLastCode() 'Copy' 접두어 제거")
    # (3) Gemini 오인 방지
    text = patch_str(
        text,
        'let r = byTitle(document.title || "");',
        JS_GEMINI,
        "gemini|argon", "[3] detectModelRole() Gemini / Argon -> rgon 처리")
    # 버전 표기
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
    text = re.sub(r'const OMNI_VERSION = "[^"]*";', 'const OMNI_VERSION = "%s";' % NEW_VERSION, text, count=1)
    return text, token


SAFE_LOG_OLD = '        sys.stderr.write("[bridge] " + (fmt % args) + "\\n")'
SAFE_LOG_NEW = (
    '        try:  # OMNI_SAFE_LOG\n'
    '            sys.stderr.write("[bridge] " + (fmt % args) + "\\n")\n'
    '        except Exception:\n'
    '            pass'
)


def build_bridge(text, token):
    text = text.replace("\r\n", "\n")
    new, n = re.subn(r'(?m)^TOKEN = ".*"[ \t]*$', lambda m: "TOKEN = " + json.dumps(token), text)
    if n != 1:
        raise PatchError("omni_bridge.py 에서 TOKEN 선언을 찾지 못했습니다 (발견 %d개)." % n)
    text = new
    text = re.sub(r'(?m)^VERSION = "[^"]*"', 'VERSION = "%s"' % NEW_VERSION, text, count=1)
    if "OMNI_SAFE_LOG" not in text and SAFE_LOG_OLD in text:
        text = text.replace(SAFE_LOG_OLD, SAFE_LOG_NEW, 1)
        log("   ✅ 적용: [5-a] 브리지 로그 출력 안전화 (백그라운드 실행 대비)")
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
# 독대실 HTML 패치 (CRLF 안전, 보존 확인은 STUDIO / firefly 키워드 개수만)
# ----------------------------------------------------------------------------
BLOCK_RE = re.compile(re.escape(HTML_BEGIN) + r".*?" + re.escape(HTML_END) + r"[ \t]*\r?\n?", re.S)


def patch_html(path):
    html, bom = read_text(path)
    stripped = BLOCK_RE.sub("", html)
    had_old = stripped != html
    low = stripped.lower()
    base_counts = {k: low.count(k) for k in ("studio", "firefly")}

    eol = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"
    block = HTML_BLOCK.replace("\r\n", "\n").replace("\n", eol)

    start_search = low.find("</head>")
    start_search = start_search if start_search >= 0 else 0
    m = re.compile(r"<body\b[^>]*>", re.I).search(stripped, start_search) or re.compile(r"<body\b[^>]*>", re.I).search(stripped)
    if m:
        new_html = stripped[:m.end()] + eol + block + stripped[m.end():]
    else:
        new_html = block + stripped
        log("   ⚠️ <body> 태그를 찾지 못해 파일 맨 앞에 삽입합니다: " + str(path.name))

    backup_file(path)
    atomic_write_text(path, new_html, bom)

    # ---- 쓰기 후 검증: 마커 1쌍 / <body> 직후 / STUDIO·firefly 보존 (길이 비교 없음)
    try:
        back, _ = read_text(path)
        if back.count(HTML_BEGIN) != 1 or back.count(HTML_END) != 1:
            raise RuntimeError("OMNI-LINK 마커가 정확히 1쌍이 아닙니다.")
        if m:
            bm = re.compile(r"<body\b[^>]*>", re.I).search(back, back.lower().find("</head>") if "</head>" in back.lower() else 0) \
                or re.compile(r"<body\b[^>]*>", re.I).search(back)
            gap = back[bm.end():back.index(HTML_BEGIN)]
            if gap.strip():
                raise RuntimeError("OMNI-LINK 블록이 <body> 직후에 위치하지 않습니다.")
        outside = BLOCK_RE.sub("", back).lower()
        for k, v in base_counts.items():
            if outside.count(k) != v:
                raise RuntimeError("기존 '%s' 블록 보존 확인 실패 (원본 %d개 / 현재 %d개)" % (k, v, outside.count(k)))
        if base_counts["studio"] == 0:
            log("   ⚠️ 원본에서 'studio' 문자열을 찾지 못했습니다 (보존 확인 대상 없음): " + path.name)
        if base_counts["firefly"] == 0:
            log("   ⚠️ 원본에서 'firefly' 문자열을 찾지 못했습니다 (보존 확인 대상 없음): " + path.name)
    except Exception:
        src = BACKUP_DIR / path.relative_to(BASE)
        if src.exists():
            shutil.copy2(src, path)
        raise
    return "교체" if had_old else "신규 삽입", eol == "\r\n"


# ----------------------------------------------------------------------------
# 브리지: 포트 정리 / 재기동 / 헬스체크
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
            # 현지화된 상태 문자열을 피하기 위해 '외부 주소가 :0' 인 행을 LISTEN 으로 간주
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
    # 1) 이미 새 버전·동일 토큰으로 떠 있으면 재사용
    code, body = health(token)
    if code == 200 and body and body.get("version") == NEW_VERSION and not bridge_changed:
        log("   ♻️  실행 중인 브리지를 재사용합니다 (v%s, 토큰 일치)." % NEW_VERSION)
        return code, body

    # 2) 8765 점유 프로세스 정리 (omni_bridge 만 종료, 그 외 프로세스는 건드리지 않음)
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

    # 3) 백그라운드 기동
    p = start_bridge()
    log("   🚀 브리지 백그라운드 기동 (PID %d, CREATE_NO_WINDOW) — 로그: %s" % (p.pid, BASE / "omni_bridge.log"))

    # 4) 헬스체크
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
    log("✨ RGON Omni-Link Hub v6.0.0 → v%s 업그레이드" % NEW_VERSION)
    log("   대상 폴더: %s" % BASE)
    log("=" * 64)

    for p in (MANIFEST_P, BG_P, CT_P, BRIDGE_P):
        if not p.exists():
            log("❌ 필수 파일이 없습니다: %s\n   먼저 build_omni_link_communicator.py (v6.0.0)를 실행하세요." % p)
            return 1

    log("[1/6] 패치 계산 및 사전 검증 (디스크는 아직 변경하지 않음)")
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

    log("[2/6] 원자적 백업 → %s" % BACKUP_DIR)
    n_bak = 0
    for p in [MANIFEST_P, BG_P, CT_P, BRIDGE_P]:
        n_bak += 1 if backup_file(p) else 0
    log("   백업된 파일: %d개 (HTML은 패치 직전에 개별 백업)" % n_bak)

    log("[3/6] 확장프로그램 / 브리지 파일 적용 + 토큰 동기화")
    try:
        atomic_write_text(MANIFEST_P, new_man)
        atomic_write_text(BG_P, new_bg)
        atomic_write_text(CT_P, new_ct)
        atomic_write_text(BRIDGE_P, new_br)
        bg_t = re.search(r'const OMNI_TOKEN = "([^"]*)";', read_text(BG_P)[0]).group(1)
        br_t = re.search(r'(?m)^TOKEN = "([^"]*)"', read_text(BRIDGE_P)[0]).group(1)
        if not bg_t or bg_t != br_t or bg_t != token:
            raise RuntimeError("토큰 불일치 감지")
        log("   🔐 토큰 동기화 확인: background.js == omni_bridge.py (…%s)" % token[-4:])
        if not validate_js({"background.js": read_text(BG_P)[0], "content_aside_bar.js": read_text(CT_P)[0]}):
            raise RuntimeError("적용 후 JS 검증 실패")
    except Exception as e:
        log("❌ 적용 실패: %s — 백업에서 복원합니다." % e)
        restore_all()
        return 1

    log("[4/6] 독대실 HTML 패치 (<body> 직후 삽입, STUDIO v5 / firefly 보존 확인)")
    patched = 0
    for rel in HTML_RELS:
        p = BASE / rel
        if not p.exists():
            log("   ⏭️  없음(건너뜀): " + rel)
            continue
        try:
            mode, crlf = patch_html(p)
            patched += 1
            log("   ✅ %s 완료: %s (%s 줄바꿈)" % (mode, rel, "CRLF" if crlf else "LF"))
        except Exception as e:
            log("   ❌ 패치 실패(원본 복원됨): %s — %s" % (rel, e))

    log("[5/6] 로컬 브리지 재기동 및 연결 검증 (127.0.0.1:%d)" % BRIDGE_PORT)
    bridge_changed = br_old.replace("\r\n", "\n") != new_br
    code, body = ensure_bridge(token, bridge_changed)

    ok = False
    if code == 200 and body and body.get("ok"):
        ok = True
        log("   🟢 로컬 브리지 연결됨 (200 OK) — v%s · base=%s" % (body.get("version"), body.get("base")))
        bad, _ = health(token[::-1] if token != token[::-1] else "x" * len(token))
        log("   🔒 잘못된 토큰 차단 확인: HTTP %s" % bad)
    else:
        log("   🔴 로컬 브리지 연결 실패 (HTTP %s)\n%s" % (code, log_tail()))

    log("[6/6] 요약")
    log("   - HTML 패치 파일 수: %d" % patched)
    log("   - 확장프로그램 반영: chrome://extensions → RGON Omni-Link → 새로고침(↻) 후, 열려 있는 AI 탭을 새로고침하세요.")
    log("   - 백업 위치: %s" % BACKUP_DIR)
    log("   - 브리지 로그: %s" % (BASE / "omni_bridge.log"))
    if not ok:
        log("⚠️ 파일 업그레이드는 적용되었지만 브리지 검증에 실패했습니다. 위 로그를 확인 후 다시 실행하세요.")
        return 2
    log("OMNI-LINK v6.0.1 UPGRADE COMPLETE!")
    return 0


if __name__ == "__main__":
    sys.exit(main())