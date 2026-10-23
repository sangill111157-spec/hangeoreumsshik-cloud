# -*- coding: utf-8 -*-
"""
step11_final_all_fix.py
────────────────────────────────────────────────────────────────────
1) 실제 Git 저장소(BASE_DIR) 자동 탐색  (rgon_alpha_chat.html + .git)
2) PC 내 모든 shin-agent / 안총리 / Omni-Link 확장프로그램 탐색 → 4칸 버튼 패치
   - Chrome/Edge/Whale Preferences 에서 '실제로 로드된' 압축해제 확장 경로 우선 탐색
   - Shadow DOM(open/closed) 관통, 사이드패널/팝업 페이지 스크립트까지 패치
3) 독대실 HTML 4개 파일: 구형 블록 제거 + 초록 브리핑 바 + 인수인계 복사 버튼
4) git add / commit / pull --rebase / push + 완료 안내창
Python 3 표준 라이브러리 전용
사용법:  python step11_final_all_fix.py            (자동 탐색)
         python step11_final_all_fix.py "D:\경로\hangeoreumsshik-cloud"   (수동 지정)
"""
import os
import sys
import re
import json
import shutil
import subprocess
import datetime
import traceback
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ────────────────────────────────────────────────────────────────
# 상수
# ────────────────────────────────────────────────────────────────
REPO_KEY = "hangeoreumsshik-cloud"
REPO_URL = "https://github.com/sangill111157-spec/hangeoreumsshik-cloud"
COMMITS_URL = "https://github.com/sangill111157-spec/hangeoreumsshik-cloud/commits/main"
PAGES_URL = "https://sangill111157-spec.github.io/hangeoreumsshik-cloud/rgon_alpha_chat.html"
RAW_SNAPSHOT_URL = "https://raw.githubusercontent.com/sangill111157-spec/hangeoreumsshik-cloud/main/rgon_brain_snapshot.json"

HTML_TARGETS = [
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
    "rgon_alpha_audience.html",
]
OLD_HTML_BLOCKS = ["RGON-PINPOINT-FIX", "RGON-BAR3-STABLE", "RGON-STEP10-BARS", "RGON-STEP11"]

EXT_KEYWORDS = ("shin-agent", "안총리", "omni-link", "omni link", "omnilink")
JS_REMOVE_NAME_HINTS = ("STEP10", "STEP11", "4BTN", "CLEAR", "ERASE", "GRID", "SHADOW-OPEN", "BTN")

TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_ROOT = Path.home() / "rgon_backups" / f"step11_{TS}"

SKIP_DIR_NAMES = {
    "windows", "program files", "program files (x86)", "programdata", "appdata",
    "$recycle.bin", "system volume information", "recovery", "perflogs", "msocache",
    "node_modules", ".git", "__pycache__", "venv", ".venv", "env", "site-packages",
    "anaconda3", "miniconda3", "msys64", "cygwin64", "intel", "amd", "nvidia",
    "windowsapps", "packages", "cache", ".cache", ".npm", ".cargo", ".rustup",
    "go", ".gradle", ".m2", ".vscode", ".idea", "dist-packages",
}
DIR_BUDGET = {"left": 600000}

LOG = []


def log(msg=""):
    print(msg)
    LOG.append(str(msg))


# ────────────────────────────────────────────────────────────────
# 파일 입출력 유틸
# ────────────────────────────────────────────────────────────────
def read_text(p):
    raw = Path(p).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    for enc in ("utf-8", "cp949"):
        try:
            return raw.decode(enc), bom
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), bom


def write_text(p, text, bom=False):
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    Path(p).write_bytes(data)


def quick_text(p, limit=3 * 1024 * 1024):
    try:
        with open(p, "rb") as f:
            return f.read(limit).decode("utf-8", errors="replace")
    except Exception:
        return ""


def has_kw(text):
    low = text.lower()
    return any(k in low for k in EXT_KEYWORDS)


def backup(p):
    p = Path(p)
    try:
        rel = str(p.resolve()).replace(":", "").lstrip("\\/")
        dest = BACKUP_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        return dest
    except Exception as e:
        log(f"   ⚠️ 백업 실패({p}): {e}")
        return None


def iter_dirs(root, max_depth, visited):
    """깊이 제한 + 무거운 폴더 제외 + 중복 방지 디렉터리 순회"""
    root = Path(root)
    stack = [(root, 0)]
    while stack:
        d, depth = stack.pop()
        if DIR_BUDGET["left"] <= 0:
            return
        DIR_BUDGET["left"] -= 1
        try:
            key = os.path.normcase(str(d.resolve()))
        except Exception:
            key = os.path.normcase(str(d))
        if key in visited:
            continue
        visited.add(key)
        yield d
        if depth >= max_depth:
            continue
        try:
            entries = list(os.scandir(d))
        except Exception:
            continue
        for e in entries:
            try:
                name = e.name.lower()
                if name in SKIP_DIR_NAMES or name.startswith("$") or name.startswith("."):
                    continue
                if e.is_dir(follow_symlinks=False):
                    stack.append((Path(e.path), depth + 1))
            except OSError:
                continue


def windows_user_dirs():
    res = []
    base = Path("C:/Users")
    try:
        for u in base.iterdir():
            if u.is_dir() and u.name.lower() not in ("public", "default", "default user", "all users"):
                res.append(u)
    except Exception:
        pass
    return res


# ────────────────────────────────────────────────────────────────
# 1) BASE_DIR 자동 탐색
# ────────────────────────────────────────────────────────────────
def is_repo(d):
    try:
        return (d / "rgon_alpha_chat.html").is_file() and (d / ".git").exists()
    except OSError:
        return False


def remote_matches(d):
    try:
        g = d / ".git"
        cfg = None
        if g.is_dir():
            cfg = g / "config"
        elif g.is_file():
            m = re.search(r"gitdir:\s*(.+)", g.read_text(encoding="utf-8", errors="replace"))
            if m:
                gd = Path(m.group(1).strip())
                if not gd.is_absolute():
                    gd = (d / gd).resolve()
                cfg = gd / "config"
                if not cfg.is_file():
                    cfg = gd.parent.parent / "config"
        if cfg and cfg.is_file():
            if REPO_KEY in cfg.read_text(encoding="utf-8", errors="replace"):
                return True
    except Exception:
        pass
    if shutil.which("git"):
        try:
            r = subprocess.run(["git", "-C", str(d), "config", "--get", "remote.origin.url"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
            return REPO_KEY in (r.stdout or "")
        except Exception:
            pass
    return False


def repo_mtime(d):
    for f in (d / ".git" / "index", d / "rgon_alpha_chat.html"):
        try:
            return f.stat().st_mtime
        except Exception:
            continue
    return 0


def find_base_dir():
    log("🔎 [1/4] 실제 Git 저장소(BASE_DIR) 탐색 중...")
    override = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("RGON_BASE_DIR")
    if override:
        p = Path(override).expanduser()
        if is_repo(p):
            log(f"   ✅ 수동 지정 경로 사용: {p}")
            return p.resolve(), [p.resolve()]
        log(f"   ⚠️ 수동 지정 경로가 저장소가 아닙니다(무시): {p}")

    found = {}  # path -> is_quick
    home = Path.home()
    here = Path(__file__).resolve().parent
    quick_roots = []
    for base in (here, Path.cwd()):
        quick_roots.append(base)
        quick_roots.extend(list(base.parents)[:3])
    quick_roots += [
        home / "shin-agent", home / REPO_KEY, home / "Desktop", home / "Documents",
        home / "바탕 화면", home / "문서", home / "OneDrive", home / "OneDrive" / "Desktop",
        home / "OneDrive" / "바탕 화면", home / "Downloads",
        Path("C:/shin-agent"), Path("C:/trading"), Path("D:/shin-agent"), Path("D:/trading"),
        Path("C:/" + REPO_KEY), Path("D:/" + REPO_KEY),
    ]
    visited = set()
    for r in quick_roots:
        try:
            if not r.is_dir():
                continue
        except OSError:
            continue
        for d in iter_dirs(r, 3, visited):
            if is_repo(d):
                found[d.resolve()] = True

    if not any(remote_matches(p) for p in found):
        log("   … 빠른 탐색에서 원격 일치 저장소가 없어 전체 드라이브 탐색을 진행합니다.")
        visited2 = set()
        broad = [(home, 5)]
        for u in windows_user_dirs():
            if os.path.normcase(str(u)) != os.path.normcase(str(home)):
                broad.append((u, 4))
        broad += [(Path("C:/"), 3), (Path("D:/"), 3), (Path("E:/"), 2)]
        for r, depth in broad:
            try:
                if not r.is_dir():
                    continue
            except OSError:
                continue
            for d in iter_dirs(r, depth, visited2):
                if is_repo(d):
                    found.setdefault(d.resolve(), False)

    if not found:
        return None, []

    ranked = sorted(found.keys(),
                    key=lambda p: (remote_matches(p), found[p], repo_mtime(p)),
                    reverse=True)
    log("   발견된 저장소 후보:")
    for p in ranked:
        log(f"     - {p}  (원격일치={remote_matches(p)})")
    log(f"   ✅ BASE_DIR = {ranked[0]}")
    return ranked[0], ranked


# ────────────────────────────────────────────────────────────────
# 2) 크롬 확장프로그램 JS (Shadow DOM 강제 open + 4칸 버튼)
# ────────────────────────────────────────────────────────────────
SHADOW_OPEN_BLOCK = r"""/* [RGON-SHADOW-OPEN-START] */
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
"""

EXT_4BTN_BLOCK = r"""/* [RGON-4BTN-V11-START] */
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
"""

JS_BLOCK_RE = re.compile(
    r"[ \t]*(?:/\*|//)[ \t]*=*[ \t]*\[(RGON-[A-Z0-9_\-]+?)-START\][ \t]*=*[ \t]*(?:\*/)?"
    r".*?"
    r"(?:/\*|//)[ \t]*=*[ \t]*\[\1-END\][ \t]*=*[ \t]*(?:\*/)?[ \t]*\r?\n?",
    re.S,
)
USE_STRICT_RE = re.compile(r"^(\s*(?:(?://[^\n]*\n)|(?:/\*.*?\*/)|\s)*)(['\"]use strict['\"];?[^\n]*\n)", re.S)


def chrome_unpacked_ext_dirs():
    """Chrome / Edge / Whale 프로필 Preferences 에서 실제 로드된 압축해제 확장 경로 추출"""
    res = {}
    user_homes = [Path.home()] + windows_user_dirs()
    bases = []
    for h in user_homes:
        la = h / "AppData" / "Local"
        bases += [la / "Google" / "Chrome" / "User Data",
                  la / "Microsoft" / "Edge" / "User Data",
                  la / "Naver" / "Naver Whale" / "User Data"]
    seen_b = set()
    for b in bases:
        k = os.path.normcase(str(b))
        if k in seen_b:
            continue
        seen_b.add(k)
        try:
            if not b.is_dir():
                continue
            profiles = [p for p in b.iterdir() if p.is_dir()]
        except Exception:
            continue
        for prof in profiles:
            for fn in ("Secure Preferences", "Preferences"):
                f = prof / fn
                if not f.is_file():
                    continue
                try:
                    data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    continue
                settings = ((data.get("extensions") or {}).get("settings") or {})
                for eid, info in settings.items():
                    if not isinstance(info, dict):
                        continue
                    p = info.get("path")
                    if p and os.path.isabs(p):
                        pp = Path(p)
                        if pp.is_dir():
                            res[pp.resolve()] = f"{b.parent.name}/{prof.name}"
    return res


def load_manifest(d):
    try:
        t, _ = read_text(d / "manifest.json")
        t = re.sub(r"^\s*//.*$", "", t, flags=re.M)
        return json.loads(t)
    except Exception:
        return {}


def ext_targets(d):
    """확장 폴더 하나에서 패치할 js 목록 반환: [(path, 사유)]"""
    m = load_manifest(d)
    bg = m.get("background") or {}
    bg_files = set()
    if isinstance(bg, dict):
        if bg.get("service_worker"):
            bg_files.add((d / bg["service_worker"]).resolve())
        for s in bg.get("scripts") or []:
            bg_files.add((d / s).resolve())

    cands = []
    cj = d / "content.js"
    if cj.is_file():
        cands.append((cj, True, "content.js"))
    for cs in m.get("content_scripts") or []:
        if isinstance(cs, dict):
            for js in cs.get("js") or []:
                cands.append((d / js, True, "manifest content_scripts"))

    pages = []
    sp = (m.get("side_panel") or {}).get("default_path") if isinstance(m.get("side_panel"), dict) else None
    act = m.get("action") or m.get("browser_action") or {}
    pop = act.get("default_popup") if isinstance(act, dict) else None
    for h in (sp, pop):
        if h:
            pages.append(d / h)
    try:
        pages += list(d.glob("*.html"))
    except Exception:
        pass
    seen_pages = set()
    for h in pages:
        try:
            if not h.is_file():
                continue
            hk = h.resolve()
        except Exception:
            continue
        if hk in seen_pages:
            continue
        seen_pages.add(hk)
        ht, _ = read_text(h)
        html_kw = has_kw(ht)
        for src in re.findall(r"<script[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", ht, flags=re.I):
            if re.match(r"^(https?:)?//", src) or src.startswith("chrome"):
                continue
            src = src.split("?")[0].split("#")[0]
            p = (d / src.lstrip("/")) if src.startswith("/") else (h.parent / src)
            cands.append((p, not html_kw, f"페이지 스크립트({h.name})"))

    result, seen = [], set()
    for p, need_kw, why in cands:
        try:
            rp = p.resolve()
        except Exception:
            continue
        if rp in seen or rp in bg_files or not rp.is_file():
            continue
        seen.add(rp)
        name = rp.name.lower()
        if name.endswith(".min.js") or any(x in name for x in (
                "jquery", "react", "vue", "lodash", "chart", "bootstrap", "purify", "marked", "highlight", "polyfill")):
            continue
        try:
            if rp.stat().st_size > 3 * 1024 * 1024:
                continue
        except Exception:
            continue
        if need_kw and not has_kw(quick_text(rp)):
            continue
        result.append((rp, why))
    return result


def find_extension_dirs(base_dir):
    log("\n🔎 [3/4] PC 내 shin-agent / 안총리 / Omni-Link 확장프로그램 탐색 중...")
    ext_dirs = {}
    loaded = chrome_unpacked_ext_dirs()
    for p, prof in loaded.items():
        if (p / "manifest.json").is_file():
            ext_dirs[p] = f"브라우저에 로드됨({prof})"
    if loaded:
        log(f"   브라우저에 등록된 압축해제 확장 {len(loaded)}개 확인")

    home = Path.home()
    roots = [(base_dir, 4), (base_dir.parent, 3), (home, 5)]
    for u in windows_user_dirs():
        roots.append((u, 5))
    roots += [(Path("C:/shin-agent"), 6), (Path("C:/trading"), 6),
              (Path("D:/shin-agent"), 6), (Path("D:/trading"), 6),
              (Path("C:/"), 2), (Path("D:/"), 3)]
    visited = set()
    for r, depth in roots:
        try:
            if not r.is_dir():
                continue
        except OSError:
            continue
        for d in iter_dirs(r, depth, visited):
            try:
                if (d / "manifest.json").is_file():
                    rd = d.resolve()
                    ext_dirs.setdefault(rd, "폴더 탐색")
            except OSError:
                continue
    return ext_dirs


def patch_js_file(p):
    text, bom = read_text(p)
    removed, kept = [], []

    def repl(m):
        name = m.group(1)
        if any(h in name.upper() for h in JS_REMOVE_NAME_HINTS):
            removed.append(name)
            return ""
        kept.append(name)
        return m.group(0)

    body = JS_BLOCK_RE.sub(repl, text)
    nl = "\r\n" if "\r\n" in text else "\n"
    shadow = SHADOW_OPEN_BLOCK.replace("\n", nl)
    block = EXT_4BTN_BLOCK.replace("\n", nl)

    m = USE_STRICT_RE.match(body)
    if m:
        body = body[:m.end()] + shadow + body[m.end():]
    else:
        body = shadow + body
    new = body.rstrip() + nl + nl + block
    if new != text:
        backup(p)
        write_text(p, new, bom)
    return removed, kept


# ────────────────────────────────────────────────────────────────
# 3) 독대실 HTML 블록
# ────────────────────────────────────────────────────────────────
HTML_BLOCK = r"""<!-- [RGON-STEP11-START] -->
<style id="rgon-step11-style">
#rgon-green-briefing-bar{display:block !important;visibility:visible !important;opacity:1 !important;height:auto !important;max-height:none !important;overflow:visible !important;margin:8px 0 !important;border-radius:12px;background:#0b2e1b;border:1px solid #1f8f4e;box-shadow:0 2px 8px rgba(0,0,0,.25);position:relative;z-index:1;box-sizing:border-box;width:100%;}
#rgon-green-briefing-bar .rgon-gb-head{display:flex;align-items:center;gap:8px;width:100%;padding:12px 14px;margin:0;background:linear-gradient(90deg,#14532d,#16a34a);color:#ecfdf5;font-weight:700;font-size:15px;border:0;border-radius:12px;cursor:pointer;text-align:left;-webkit-tap-highlight-color:transparent;font-family:inherit;box-sizing:border-box;}
#rgon-green-briefing-bar.open .rgon-gb-head{border-radius:12px 12px 0 0;}
#rgon-green-briefing-bar .rgon-gb-arrow{display:inline-block;transition:transform .15s ease;}
#rgon-green-briefing-bar.open .rgon-gb-arrow{transform:rotate(90deg);}
#rgon-green-briefing-bar .rgon-gb-body{display:none;padding:10px 12px 12px;color:#d1fae5;font-size:13px;line-height:1.6;}
#rgon-green-briefing-bar.open .rgon-gb-body{display:block;}
#rgon-green-briefing-bar .rgon-gb-tools{display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;}
#rgon-green-briefing-bar .rgon-gb-reload{background:#166534;color:#ecfdf5;border:1px solid #22c55e;border-radius:8px;padding:5px 10px;font-size:12px;cursor:pointer;font-family:inherit;}
#rgon-green-briefing-bar .rgon-gb-meta{font-size:11px;color:#86efac;}
#rgon-green-briefing-bar .rgon-gb-text{white-space:pre-wrap;word-break:break-word;background:rgba(0,0,0,.25);border-radius:8px;padding:10px;margin-bottom:8px;max-height:55vh;overflow:auto;}
#rgon-green-briefing-bar details summary{cursor:pointer;color:#86efac;margin:4px 0;}
#rgon-green-briefing-bar .rgon-gb-pre{white-space:pre-wrap;word-break:break-all;background:rgba(0,0,0,.35);border-radius:8px;padding:10px;font-size:11.5px;max-height:50vh;overflow:auto;margin:6px 0 0;color:#bbf7d0;}
.rgon-handoff-wrap{display:block !important;width:100%;margin:0 0 8px 0;box-sizing:border-box;}
.rgon-handoff-btn{display:block;width:100%;padding:11px 12px;border:0;border-radius:10px;background:linear-gradient(90deg,#1d4ed8,#7c3aed);color:#fff;font-weight:700;font-size:14px;cursor:pointer;font-family:inherit;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
.rgon-copy-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:2147483647;display:flex;align-items:center;justify-content:center;padding:16px;}
.rgon-copy-overlay .rgon-copy-box{background:#111827;color:#f9fafb;border-radius:12px;padding:12px;width:100%;max-width:560px;}
.rgon-copy-overlay textarea{width:100%;height:50vh;box-sizing:border-box;font-size:12px;background:#030712;color:#e5e7eb;border:1px solid #374151;border-radius:8px;padding:8px;}
.rgon-copy-overlay button{margin-top:8px;width:100%;padding:10px;border:0;border-radius:8px;background:#2563eb;color:#fff;font-weight:700;}
</style>
<script>
(function () {
  'use strict';
  if (window.__RGON_STEP11__) return;
  window.__RGON_STEP11__ = true;

  var BAR_ID = 'rgon-green-briefing-bar';
  var SNAP_LOCAL = './rgon_brain_snapshot.json';
  var SNAP_RAW = '__RAW_SNAPSHOT_URL__';
  var LINKS = {
    repo: '__REPO_URL__',
    commits: '__COMMITS_URL__',
    pages: '__PAGES_URL__',
    raw: '__RAW_SNAPSHOT_URL__'
  };
  var FIRST_TEXT = '4대 AI 분배 컨트롤러';
  var NEXT_TEXT = '독대실에서 바로 분배하기';
  var DRAWER_TEXTS = ['지우기 도구', '입력창 비우기'];
  var TEXT_KEYS = ['briefing_full', 'full_briefing', 'briefing', 'brief', 'summary', 'report', 'content', 'text', 'message'];
  var TIME_KEYS = ['updated_at', 'updatedAt', 'generated_at', 'generatedAt', 'timestamp', 'last_updated', 'time', 'date'];
  var state = { loaded: false, loading: false, snapshot: null, src: '' };

  function findTextEl(needles) {
    if (!document.body) return null;
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    var n;
    while ((n = w.nextNode())) {
      var v = n.nodeValue;
      if (!v || v.length > 400) continue;
      for (var i = 0; i < needles.length; i++) {
        if (v.indexOf(needles[i]) !== -1) {
          var p = n.parentElement;
          if (!p) break;
          if (p.closest('script,style,textarea,noscript,#' + BAR_ID + ',.rgon-handoff-wrap,.rgon-copy-overlay')) break;
          return p;
        }
      }
    }
    return null;
  }

  function pickKey(obj, keys) {
    if (!obj || typeof obj !== 'object') return null;
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (obj[k] !== undefined && obj[k] !== null && obj[k] !== '') return { k: k, v: obj[k] };
    }
    return null;
  }

  /* ── 초록 브리핑 바 ── */
  function buildBar() {
    var bar = document.createElement('div');
    bar.id = BAR_ID;
    bar.setAttribute('data-rgon', 'step11');
    bar.innerHTML =
      '<button type="button" class="rgon-gb-head" aria-expanded="false">' +
        '<span class="rgon-gb-arrow">▶</span><span class="rgon-gb-title">🛰️ 르곤-알파 실시간 브리핑 전문</span>' +
      '</button>' +
      '<div class="rgon-gb-body">' +
        '<div class="rgon-gb-tools"><button type="button" class="rgon-gb-reload">🔄 새로고침</button><span class="rgon-gb-meta"></span></div>' +
        '<div class="rgon-gb-content">아직 불러오지 않았습니다.</div>' +
      '</div>';
    var head = bar.querySelector('.rgon-gb-head');
    head.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var open = !bar.classList.contains('open');
      bar.classList.toggle('open', open);
      head.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) loadSnapshot(false);
    });
    bar.querySelector('.rgon-gb-reload').addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      loadSnapshot(true);
    });
    return bar;
  }

  function enforceVisible(bar) {
    if (bar.hasAttribute('hidden')) bar.removeAttribute('hidden');
    var s = bar.style;
    [['display', 'block'], ['visibility', 'visible'], ['opacity', '1']].forEach(function (pv) {
      if (s.getPropertyValue(pv[0]) !== pv[1] || s.getPropertyPriority(pv[0]) !== 'important') {
        s.setProperty(pv[0], pv[1], 'important');
      }
    });
  }
  function watchBar(bar) {
    if (bar.__rgonWatched) return;
    bar.__rgonWatched = true;
    try {
      new MutationObserver(function () { enforceVisible(bar); })
        .observe(bar, { attributes: true, attributeFilter: ['style', 'hidden', 'class'] });
    } catch (e) {}
  }

  function blockOf(el) {
    var acc = el.closest('details, [class*="accordion" i], [class*="collapse" i], [class*="bar" i], section');
    if (acc && acc !== document.body) return acc;
    var cur = el;
    while (cur.parentElement && cur.parentElement !== document.body && cur.parentElement.children.length === 1) cur = cur.parentElement;
    return cur;
  }

  function placeBar() {
    if (!document.body) return;
    var bar = document.getElementById(BAR_ID) || buildBar();
    var nextEl = findTextEl([NEXT_TEXT]);
    var firstEl = findTextEl([FIRST_TEXT]);
    var ref = null, where = 'before';
    if (nextEl && firstEl && !nextEl.contains(firstEl) && !firstEl.contains(nextEl)) {
      var cur = nextEl;
      while (cur.parentElement && cur.parentElement !== document.documentElement && !cur.parentElement.contains(firstEl)) {
        cur = cur.parentElement;
      }
      ref = cur; where = 'before';
    } else if (nextEl) {
      ref = blockOf(nextEl); where = 'before';
    } else if (firstEl) {
      ref = blockOf(firstEl); where = 'after';
    }
    if (ref === bar || (ref && bar.contains(ref))) ref = null;
    if (ref && ref.parentElement) {
      if (where === 'before') {
        if (ref.previousElementSibling !== bar) ref.parentElement.insertBefore(bar, ref);
      } else {
        if (ref.nextElementSibling !== bar) ref.parentElement.insertBefore(bar, ref.nextSibling);
      }
    } else if (!bar.isConnected) {
      document.body.insertBefore(bar, document.body.firstChild);
    }
    enforceVisible(bar);
    watchBar(bar);
  }

  function fetchJson(url) {
    var u = url + (url.indexOf('?') === -1 ? '?' : '&') + 't=' + Date.now();
    return fetch(u, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.text();
    }).then(function (t) {
      try { return { data: JSON.parse(t), src: url }; } catch (e) { throw new Error('JSON 파싱 실패'); }
    });
  }

  function render(bar, res) {
    var d = res.data;
    var box = bar.querySelector('.rgon-gb-content');
    var meta = bar.querySelector('.rgon-gb-meta');
    var frag = document.createDocumentFragment();
    var t = pickKey(d, TIME_KEYS);
    meta.textContent = (t ? '🕒 ' + t.v + ' · ' : '') + '출처: ' + (res.src === SNAP_LOCAL ? '로컬 ./rgon_brain_snapshot.json' : 'GitHub raw');
    var main = pickKey(d, TEXT_KEYS);
    if (main) {
      var p = document.createElement('div');
      p.className = 'rgon-gb-text';
      p.textContent = typeof main.v === 'string' ? main.v : JSON.stringify(main.v, null, 2);
      frag.appendChild(p);
    }
    var det = document.createElement('details');
    if (!main) det.open = true;
    var sm = document.createElement('summary');
    sm.textContent = '📦 스냅샷 JSON 전문 보기';
    var pre = document.createElement('pre');
    pre.className = 'rgon-gb-pre';
    pre.textContent = JSON.stringify(d, null, 2);
    det.appendChild(sm);
    det.appendChild(pre);
    frag.appendChild(det);
    box.innerHTML = '';
    box.appendChild(frag);
  }

  function loadSnapshot(force) {
    var bar = document.getElementById(BAR_ID);
    if (!bar) return;
    if (state.loading || (state.loaded && !force)) return;
    state.loading = true;
    var box = bar.querySelector('.rgon-gb-content');
    var meta = bar.querySelector('.rgon-gb-meta');
    if (!state.loaded) box.textContent = '⏳ 브리핑을 불러오는 중…';
    meta.textContent = '⏳ 갱신 중…';
    fetchJson(SNAP_LOCAL)
      .catch(function () { return fetchJson(SNAP_RAW); })
      .then(function (res) {
        state.loaded = true; state.snapshot = res.data; state.src = res.src;
        render(bar, res);
      })
      .catch(function (e) {
        if (!state.loaded) box.textContent = '⚠️ 브리핑 스냅샷을 불러오지 못했습니다: ' + (e && e.message ? e.message : e);
        meta.textContent = '';
      })
      .then(function () { state.loading = false; });
  }

  /* ── 인수인계 전달서 ── */
  function buildHandoffText() {
    var lines = [];
    lines.push('[르곤-알파 · 새 AI 인수인계 전달서]');
    lines.push('작성 시각: ' + new Date().toLocaleString('ko-KR'));
    var st = state.snapshot ? pickKey(state.snapshot, TIME_KEYS) : null;
    if (st) lines.push('최신 두뇌 스냅샷 시각: ' + st.v);
    lines.push('');
    lines.push('안녕하세요. 지금부터 르곤-알파(한거름식 클라우드) 프로젝트를 이어받아 주실 AI께 드리는 인수인계입니다.');
    lines.push('아래 4개 주소를 순서대로 먼저 열람해 현재 코드 · 커밋 이력 · 실서비스 화면 · 두뇌 스냅샷 상태를 파악한 뒤 작업을 이어가 주세요.');
    lines.push('');
    lines.push('1) GitHub 저장소: ' + LINKS.repo);
    lines.push('2) 최신 커밋 이력: ' + LINKS.commits);
    lines.push('3) 모바일 독대실(실서비스): ' + LINKS.pages);
    lines.push('4) 두뇌 스냅샷 JSON 원문: ' + LINKS.raw);
    lines.push('');
    lines.push('작업 원칙:');
    lines.push('- 기존 기능을 깨뜨리지 않도록 수정 전후를 비교해 주세요.');
    lines.push('- 수정본은 생략 없는 전체 코드로 제공해 주세요.');
    lines.push('- 변경 사항은 커밋 메시지로 명확히 남겨 주세요.');
    return lines.join('\n');
  }

  function legacy(text) {
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try { ta.setSelectionRange(0, text.length); } catch (e) {}
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta);
      if (ok) resolve(); else reject(new Error('복사 실패'));
    });
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () { return legacy(text); });
    }
    return legacy(text);
  }
  function showManual(text) {
    var ov = document.createElement('div');
    ov.className = 'rgon-copy-overlay';
    ov.innerHTML = '<div class="rgon-copy-box"><div style="margin-bottom:6px;font-weight:700">자동 복사가 막혀 있습니다. 아래 내용을 길게 눌러 전체 선택 후 복사하세요.</div><textarea readonly></textarea><button type="button">닫기</button></div>';
    ov.querySelector('textarea').value = text;
    ov.querySelector('button').addEventListener('click', function () { ov.remove(); });
    document.body.appendChild(ov);
  }

  function buildHandoffWrap() {
    var wrap = document.createElement('div');
    wrap.className = 'rgon-handoff-wrap';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rgon-handoff-btn';
    btn.textContent = '📋 새 AI 인수인계 전달서 복사';
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var text = buildHandoffText();
      copyText(text).then(function () {
        btn.textContent = '✅ 복사 완료! 새 AI 대화창에 붙여넣으세요';
        setTimeout(function () { btn.textContent = '📋 새 AI 인수인계 전달서 복사'; }, 1800);
      }).catch(function () { showManual(text); });
    });
    wrap.appendChild(btn);
    return wrap;
  }

  function placeHandoff() {
    var anchor = findTextEl(DRAWER_TEXTS);
    if (!anchor) return;
    var block = anchor.closest('button,[role="button"],a,li,h1,h2,h3,h4,h5,h6,label,summary') || anchor;
    while (block.parentElement && block.parentElement !== document.body && block.parentElement.children.length === 1) {
      block = block.parentElement;
    }
    if (!block.parentElement) return;
    var wrap = document.querySelector('.rgon-handoff-wrap') || buildHandoffWrap();
    if (block.previousElementSibling !== wrap) block.parentElement.insertBefore(wrap, block);
  }

  var pending = null;
  function tick() {
    pending = null;
    try { placeBar(); } catch (e) { try { console.warn('[RGON step11] bar', e); } catch (x) {} }
    try { placeHandoff(); } catch (e) { try { console.warn('[RGON step11] handoff', e); } catch (x) {} }
  }
  function schedule() { if (!pending) pending = setTimeout(tick, 200); }
  function init() {
    tick();
    try { new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true }); } catch (e) {}
    var n = 0;
    var iv = setInterval(function () { tick(); if (++n > 20) clearInterval(iv); }, 1000);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
</script>
<!-- [RGON-STEP11-END] -->
"""


def html_block_regex(name):
    n = re.escape(name)
    return re.compile(
        r"[ \t]*<!--\s*=*\s*\[" + n + r"-START\]\s*=*\s*-->.*?<!--\s*=*\s*\[" + n + r"-END\]\s*=*\s*-->[ \t]*\r?\n?",
        re.S,
    )


def build_html_block(nl):
    b = (HTML_BLOCK
         .replace("__REPO_URL__", REPO_URL)
         .replace("__COMMITS_URL__", COMMITS_URL)
         .replace("__PAGES_URL__", PAGES_URL)
         .replace("__RAW_SNAPSHOT_URL__", RAW_SNAPSHOT_URL))
    return b.replace("\n", nl)


def patch_html_files(base_dir):
    log("\n🛠️ [2/4] 독대실 HTML 패치")
    patched = []
    for rel in HTML_TARGETS:
        p = base_dir / rel
        if not p.is_file():
            log(f"   ⏭️ 없음(건너뜀): {rel}")
            continue
        text, bom = read_text(p)
        nl = "\r\n" if "\r\n" in text else "\n"
        new = text
        for name in OLD_HTML_BLOCKS:
            rx = html_block_regex(name)
            cnt = len(rx.findall(new))
            if cnt:
                new = rx.sub("", new)
                log(f"   🧽 {rel}: [{name}] 블록 {cnt}개 제거")
            if re.search(r"\[" + re.escape(name) + r"-START\]", new):
                log(f"   ⚠️ {rel}: [{name}-START] 는 있으나 END 마커가 없어 자동 제거하지 못했습니다. 수동 확인 필요")
        block = build_html_block(nl)
        idx = new.lower().rfind("</body>")
        if idx == -1:
            new = new.rstrip() + nl + block + nl
        else:
            new = new[:idx] + block + nl + new[idx:]
        has_first = "4대 AI 분배 컨트롤러" in text
        has_next = "독대실에서 바로 분배하기" in text
        has_drawer = ("지우기 도구" in text) or ("입력창 비우기" in text)
        log(f"   🔍 {rel}: 정적 텍스트 확인 → 컨트롤러={has_first}, 바로분배={has_next}, 지우기도구={has_drawer} "
            f"(False 여도 동적 렌더링이면 런타임에 자동 배치)")
        if new != text:
            backup(p)
            write_text(p, new, bom)
            patched.append(str(p))
            log(f"   ✅ 패치 완료: {p}")
        else:
            log(f"   ➖ 변경 없음: {p}")
    return patched


# ────────────────────────────────────────────────────────────────
# 4) Git
# ────────────────────────────────────────────────────────────────
def run_git(args, cwd, timeout=300):
    try:
        r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        log(f"   $ git {' '.join(args)}  → rc={r.returncode}")
        if out:
            for line in out.splitlines()[:25]:
                log(f"     {line}")
        return r.returncode, out
    except FileNotFoundError:
        log("   ❌ git 명령을 찾을 수 없습니다.")
        return 127, "git not found"
    except subprocess.TimeoutExpired:
        log(f"   ❌ git {' '.join(args)} 시간 초과")
        return 124, "timeout"


def git_sync(base_dir):
    log("\n🚀 [4/4] Git 반영")
    if not shutil.which("git"):
        return False, "git 미설치 (PATH에 git 없음)"
    run_git(["add", "-A"], base_dir)
    rc, _ = run_git(["diff", "--cached", "--quiet"], base_dir)
    if rc == 1:
        msg = "step11: 확장 4칸 지우개 버튼(Shadow DOM 관통) + 초록 브리핑 바 복구 + 인수인계 복사 버튼"
        rc, out = run_git(["commit", "-m", msg], base_dir)
        if rc != 0:
            return False, "commit 실패 (git user.name / user.email 설정 확인)"
    else:
        log("   ➖ 커밋할 변경 사항 없음 (이미 반영된 상태일 수 있음)")
    rc, out = run_git(["pull", "--rebase", "origin", "main"], base_dir)
    if rc != 0:
        run_git(["rebase", "--abort"], base_dir)
        return False, "pull --rebase 실패 (충돌 가능) → rebase 를 취소했습니다. 로그를 확인하세요."
    rc, out = run_git(["push", "origin", "main"], base_dir)
    if rc != 0:
        return False, "push 실패 (인증/네트워크 확인)"
    rc, out = run_git(["log", "-1", "--oneline"], base_dir)
    return True, f"푸시 성공 · 최신 커밋: {out.strip()}"


# ────────────────────────────────────────────────────────────────
# 안내창
# ────────────────────────────────────────────────────────────────
def show_box(title, text, error=False):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except Exception:
            pass
        (messagebox.showerror if error else messagebox.showinfo)(title, text, parent=root)
        root.destroy()
        return
    except Exception:
        pass
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, (0x10 if error else 0x40) | 0x40000)
        return
    except Exception:
        pass
    print(f"\n[{title}]\n{text}")


def save_log():
    try:
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        f = BACKUP_ROOT / "step11_log.txt"
        f.write_text("\n".join(LOG), encoding="utf-8")
        return f
    except Exception:
        return None


# ────────────────────────────────────────────────────────────────
# main
# ────────────────────────────────────────────────────────────────
def main():
    log("=" * 70)
    log(f"  RGON step11 최종 통합 패치  ({TS})")
    log("=" * 70)

    base_dir, _cands = find_base_dir()
    if not base_dir:
        msg = ("rgon_alpha_chat.html 과 .git 이 함께 있는 저장소 폴더를 찾지 못했습니다.\n\n"
               "저장소 폴더 경로를 직접 지정해 다시 실행해 주세요:\n"
               'python step11_final_all_fix.py "D:\\경로\\hangeoreumsshik-cloud"')
        log("❌ " + msg)
        show_box("RGON step11 - 저장소 탐색 실패", msg, error=True)
        return

    html_patched = patch_html_files(base_dir)

    ext_dirs = find_extension_dirs(base_dir)
    js_patched = []
    for d, why in sorted(ext_dirs.items(), key=lambda x: str(x[0])):
        try:
            targets = ext_targets(d)
        except Exception as e:
            log(f"   ⚠️ 분석 실패 {d}: {e}")
            continue
        if not targets:
            continue
        log(f"\n   📦 확장 폴더: {d}  [{why}]")
        for p, reason in targets:
            try:
                removed, kept = patch_js_file(p)
                js_patched.append(str(p))
                log(f"     ✅ 패치: {p}  ({reason})")
                if removed:
                    log(f"        🧽 구형 블록 제거: {', '.join(removed)}")
                if kept:
                    log(f"        ℹ️ 유지한 기타 RGON 블록: {', '.join(kept)}")
            except Exception as e:
                log(f"     ❌ 패치 실패: {p} → {e}")
    if not js_patched:
        log("   ⚠️ 키워드(shin-agent/안총리/Omni-Link)를 가진 확장프로그램 스크립트를 찾지 못했습니다.")

    ok, git_msg = git_sync(base_dir)
    log(("   ✅ " if ok else "   ❌ ") + git_msg)

    logf = save_log()
    shown = js_patched[:12]
    more = f"\n   … 외 {len(js_patched) - 12}개" if len(js_patched) > 12 else ""
    summary = (
        f"(1) 패치된 BASE_DIR\n   {base_dir}\n\n"
        f"    HTML 패치 {len(html_patched)}개\n"
        + "".join(f"   - {Path(h).relative_to(base_dir)}\n" for h in html_patched)
        + f"\n(2) 패치된 확장프로그램 스크립트 {len(js_patched)}개\n"
        + ("".join(f"   - {p}\n" for p in shown) + more if js_patched else "   (없음)\n")
        + f"\n(3) Git: {'✅ ' if ok else '❌ '}{git_msg}\n\n"
        "다음 단계:\n"
        " ① chrome://extensions → 해당 확장 '새로고침(↻)'\n"
        " ② 대상 웹페이지 F5 (사이드패널이면 패널을 닫았다가 다시 열기)\n"
        " ③ 모바일은 GitHub Pages 반영(1~2분) 후 새로고침\n\n"
        f"백업/로그: {BACKUP_ROOT}" + (f"\n로그 파일: {logf}" if logf else "")
    )
    log("\n" + "=" * 70)
    log(summary)
    log("=" * 70)
    show_box("RGON step11 패치 완료" if ok else "RGON step11 패치 완료 (Git 확인 필요)", summary, error=not ok)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        err = traceback.format_exc()
        log("❌ 예기치 못한 오류:\n" + err)
        save_log()
        show_box("RGON step11 오류", err[-1800:], error=True)
    finally:
        try:
            input("\n엔터 키를 누르면 창이 닫힙니다...")
        except Exception:
            pass
