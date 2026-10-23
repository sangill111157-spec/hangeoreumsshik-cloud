#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step10_final_all_fix.py
- Python 3 표준 라이브러리 전용 (작업 폴더 자동 탐지 탑재)
- (1) chrome_omni_link_ext/content.js : [💾 shin-agent 저장 | 🧹 지우기 | ⚡ 안총리 직통 | 🗑️ 전체 지우기] 1줄 4칸 그리드
- (2) 독대실 HTML 4종 : RGON-PINPOINT-FIX 제거 + RGON-STEP10-BARS 보완 블록 (4대 아코디언 바 복구, 인수인계 복사 버튼)
- (3) git add/commit/pull --rebase/push + 안내 메시지 박스
"""

import os
import re
import sys
import json
import shutil
import datetime
import subprocess
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# 0. 작업 폴더 자동 탐지 (어떤 윈도우 계정에서도 100% 자동 발견)
# ──────────────────────────────────────────────────────────────
def find_base_dir():
    candidates = []
    try:
        here = Path(__file__).resolve().parent
        candidates.extend([here, here.parent, here.parent.parent])
    except Exception:
        pass
    cwd = Path.cwd()
    candidates.extend([cwd, cwd.parent])
    home = Path.home()
    candidates.extend([
        home / "shin-agent",
        home / "Desktop" / "shin-agent",
        home / "Documents" / "shin-agent",
        Path(r"C:\shin-agent"),
        Path(r"C:\Users\user\shin-agent"),
        Path(r"D:\shin-agent"),
    ])
    if os.path.isdir(r"C:\Users"):
        try:
            for u in os.listdir(r"C:\Users"):
                p = Path(r"C:\Users") / u / "shin-agent"
                candidates.append(p)
        except Exception:
            pass
    for c in candidates:
        try:
            if c and c.is_dir() and (
                (c / "rgon_alpha_chat.html").is_file()
                or (c / "chrome_omni_link_ext").is_dir()
                or (c / ".git").exists()
            ):
                return str(c.resolve())
        except Exception:
            pass
    return str(cwd.resolve())


BASE_DIR = find_base_dir()
EXT_JS = os.path.join(BASE_DIR, "chrome_omni_link_ext", "content.js")
HTML_TARGETS = [
    os.path.join(BASE_DIR, "rgon_alpha_chat.html"),
    os.path.join(BASE_DIR, "dashboard", "rgon_alpha_chat.html"),
    os.path.join(BASE_DIR, "docs", "rgon_alpha_chat.html"),
    os.path.join(BASE_DIR, "rgon_alpha_audience.html"),
]
BACKUP_SUFFIX = ".bak_step10"
COMMIT_MSG = "feat(ui): Step 10 restore all 4 accordion bars and 4-column extension clear buttons"

GITHUB_REPOS = [
    "https://github.com/sangill111157-spec/hangeoreumsshik-cloud",
    "https://github.com/sangill111157-spec/hangeoreumsshik-cloud/commits/main",
    "https://sangill111157-spec.github.io/hangeoreumsshik-cloud/rgon_alpha_chat.html",
    "https://raw.githubusercontent.com/sangill111157-spec/hangeoreumsshik-cloud/main/rgon_brain_snapshot.json",
]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def log(msg):
    print(msg, flush=True)


# ──────────────────────────────────────────────────────────────
# 1. 공통 유틸
# ──────────────────────────────────────────────────────────────
BOM = b"\xef\xbb\xbf"


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    has_bom = raw.startswith(BOM)
    if has_bom:
        raw = raw[len(BOM):]
    text = raw.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, has_bom, newline


def write_text(path, text, has_bom):
    data = text.encode("utf-8")
    if has_bom:
        data = BOM + data
    with open(path, "wb") as f:
        f.write(data)


def make_backup(path):
    bak = path + BACKUP_SUFFIX
    if os.path.exists(bak):
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = path + BACKUP_SUFFIX + "_" + stamp
    shutil.copy2(path, bak)
    return bak


def remove_blocks(text, start_re, end_re, label):
    pattern = re.compile(start_re + r".*?" + end_re + r"[ \t]*(?:\r?\n)?", re.DOTALL)
    new_text, n = pattern.subn("", text)
    if n:
        log(f"   - 기존 {label} 블록 {n}개 제거")
    return new_text


def js_string(s):
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")


def run_git(args, cwd):
    try:
        p = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        out = ((p.stdout or "") + "\n" + (p.stderr or "")).strip()
        return p.returncode, out
    except Exception as e:
        return 1, str(e)


# ──────────────────────────────────────────────────────────────
# 2. 크롬 확장프로그램 (content.js) 1줄 4칸 버튼 패치
# ──────────────────────────────────────────────────────────────
EXT_BLOCK = r"""/* === [RGON-CLEAR-BTNS-START] === */
(function(){
  if (window.__rgonStep10ClearBtns) return;
  window.__rgonStep10ClearBtns = true;

  function findBtnByText(root, kw) {
    var btns = (root || document).querySelectorAll('button, input[type="button"], a[role="button"]');
    for (var i = 0; i < btns.length; i++) {
      var t = (btns[i].innerText || btns[i].textContent || btns[i].value || '').trim();
      if (t.indexOf(kw) !== -1) return btns[i];
    }
    return null;
  }

  function getPanelRoot(saveBtn) {
    var cur = saveBtn;
    for (var i = 0; i < 8 && cur && cur !== document.body; i++) {
      if (cur.id && /rgon|omni|panel|bridge/i.test(cur.id)) return cur;
      var pos = '';
      try { pos = getComputedStyle(cur).position; } catch(e){}
      if (pos === 'fixed') return cur;
      cur = cur.parentElement;
    }
    return (saveBtn && saveBtn.parentElement && saveBtn.parentElement.parentElement) || document.body;
  }

  function clearInputsOnly(panel) {
    var tas = panel.querySelectorAll('textarea, input[type="text"]');
    for (var i = 0; i < tas.length; i++) {
      tas[i].value = '';
      tas[i].dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  function clearAllPanel(panel) {
    clearInputsOnly(panel);
    var logs = panel.querySelectorAll('pre, code, [id*="log"], [id*="preview"], [class*="log"], [class*="status"]');
    for (var i = 0; i < logs.length; i++) {
      if (logs[i].tagName === 'BUTTON' || logs[i].querySelector('button')) continue;
      if (logs[i].children.length === 0) logs[i].textContent = '';
    }
  }

  function styleBtn(btn, borderCol, bgCol, textCol) {
    btn.type = 'button';
    btn.style.cssText = [
      'display:inline-flex',
      'align-items:center',
      'justify-content:center',
      'padding:8px 6px',
      'border-radius:8px',
      'border:1px solid ' + borderCol,
      'background:' + bgCol,
      'color:' + textCol,
      'font-weight:800',
      'font-size:12px',
      'cursor:pointer',
      'white-space:nowrap',
      'width:100%',
      'box-sizing:border-box'
    ].join(';');
  }

  function ensureFourButtons() {
    var saveBtn = findBtnByText(document, 'shin-agent 저장') || findBtnByText(document, '저장');
    var directBtn = findBtnByText(document, '안총리 직통');
    if (!saveBtn || !directBtn) return;

    var panel = getPanelRoot(saveBtn);
    var row = saveBtn.parentElement;
    if (!row) return;

    var clearBtn = document.getElementById('rgon-ext-btn-clear');
    var clearAllBtn = document.getElementById('rgon-ext-btn-clear-all');

    if (!clearBtn) {
      clearBtn = document.createElement('button');
      clearBtn.id = 'rgon-ext-btn-clear';
      clearBtn.textContent = '🧹 지우기';
      styleBtn(clearBtn, '#10b981', 'rgba(16,185,129,0.18)', '#6ee7b7');
      clearBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        clearInputsOnly(panel);
        var orig = clearBtn.textContent;
        clearBtn.textContent = '✅ 비움!';
        setTimeout(function(){ clearBtn.textContent = orig; }, 900);
      });
    }

    if (!clearAllBtn) {
      clearAllBtn = document.createElement('button');
      clearAllBtn.id = 'rgon-ext-btn-clear-all';
      clearAllBtn.textContent = '🗑️ 전체 지우기';
      styleBtn(clearAllBtn, '#ef4444', 'rgba(239,68,68,0.18)', '#fca5a5');
      clearAllBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        clearAllPanel(panel);
        var orig = clearAllBtn.textContent;
        clearAllBtn.textContent = '✅ 초기화!';
        setTimeout(function(){ clearAllBtn.textContent = orig; }, 900);
      });
    }

    if (directBtn.parentElement === row) {
      row.style.display = 'grid';
      row.style.gridTemplateColumns = '1.2fr 0.9fr 1.2fr 1fr';
      row.style.gap = '6px';
      row.style.alignItems = 'center';
      row.style.width = '100%';
      saveBtn.style.width = '100%';
      directBtn.style.width = '100%';
      if (clearBtn.parentElement !== row || clearAllBtn.parentElement !== row) {
        row.insertBefore(clearBtn, directBtn);
        row.appendChild(clearAllBtn);
      }
    } else {
      if (!clearBtn.parentElement) saveBtn.insertAdjacentElement('afterend', clearBtn);
      if (!clearAllBtn.parentElement) directBtn.insertAdjacentElement('afterend', clearAllBtn);
    }
  }

  ensureFourButtons();
  setInterval(ensureFourButtons, 1500);
})();
/* === [RGON-CLEAR-BTNS-END] === */
"""


def patch_extension():
    log("\n[1] 크롬 확장프로그램 패치: chrome_omni_link_ext/content.js")
    if not os.path.isfile(EXT_JS):
        log(f"   ✖ 파일 없음: {EXT_JS}")
        return False
    try:
        text, has_bom, nl = read_text(EXT_JS)
    except Exception as e:
        log(f"   ✖ 읽기 실패: {e}")
        return False

    bak = make_backup(EXT_JS)
    log(f"   - 백업 완료: {os.path.relpath(bak, BASE_DIR)}")

    text = remove_blocks(
        text,
        r"/\* === \[RGON-CLEAR-BTNS-START\] === \*/",
        r"/\* === \[RGON-CLEAR-BTNS-END\] === \*/",
        "RGON-CLEAR-BTNS",
    )
    blk = EXT_BLOCK.replace("\n", nl)
    text = text.rstrip() + nl + nl + blk + nl
    write_text(EXT_JS, text, has_bom)
    log("   ✔ [💾 shin-agent 저장 | 🧹 지우기 | ⚡ 안총리 직통 | 🗑️ 전체 지우기] 4칸 그리드 장착 완료")
    return True


# ──────────────────────────────────────────────────────────────
# 3. 독대실 HTML 4개 파일 패치 (4대 아코디언 바 복구 + 인수인계 복사)
# ──────────────────────────────────────────────────────────────
HTML_BLOCK_TEMPLATE = r"""<!-- [RGON-STEP10-BARS-START] -->
<style id="rgon-step10-bars-style">
  .rgon-s10-force-show{display:block !important;visibility:visible !important;opacity:1 !important;}
  .rgon-s10-replaced{display:none !important;}
  .rgon-s10-acc-body{overflow:hidden;transition:max-height .28s ease,opacity .28s ease;}
  #rgon-green-briefing-bar{display:block !important;margin:10px 0;}
  #rgon-green-briefing-head{border:1px solid #065f46;background:rgba(6,78,59,0.35);color:#34d399;border-radius:10px;
    padding:10px 14px;font-weight:700;display:flex;justify-content:space-between;align-items:center;cursor:pointer;user-select:none;}
  #rgon-green-briefing-head .s10-hint{font-weight:500;font-size:12px;color:#6ee7b7;opacity:.85;}
  #rgon-green-briefing-body{display:none;margin-top:6px;border:1px solid #065f46;border-radius:10px;
    background:rgba(2,44,34,0.55);padding:12px;}
  #rgon-green-briefing-body.s10-open{display:block !important;}
  .rgon-s10-btn{border:1px solid #10b981;background:rgba(16,185,129,0.15);color:#6ee7b7;border-radius:8px;
    padding:6px 10px;font-weight:700;font-size:12px;cursor:pointer;margin-right:6px;}
  .rgon-s10-btn:hover{background:rgba(16,185,129,0.28);}
  #rgon-green-briefing-meta{font-size:11px;color:#6ee7b7;opacity:.8;margin-top:6px;}
  #rgon-green-briefing-pre{white-space:pre-wrap;word-break:break-word;max-height:420px;overflow:auto;color:#d1fae5;
    font-size:13px;line-height:1.6;margin:8px 0 0;font-family:Consolas,'Malgun Gothic',monospace;}
  #rgon-s10-handoff-btn{display:block;width:100%;box-sizing:border-box;margin:0 0 10px 0;padding:10px 12px;border-radius:10px;
    border:1px solid #6366f1;background:rgba(99,102,241,0.2);color:#e0e7ff;font-weight:800;font-size:13px;cursor:pointer;text-align:left;}
  #rgon-s10-handoff-btn:hover{background:rgba(99,102,241,0.35);}
  #rgon-s10-toast{position:fixed;left:50%;bottom:32px;transform:translateX(-50%);background:#064e3b;color:#ecfdf5;
    border:1px solid #10b981;border-radius:12px;padding:12px 18px;font-weight:700;font-size:14px;z-index:2147483647;
    box-shadow:0 8px 30px rgba(0,0,0,.45);opacity:0;transition:opacity .25s ease;pointer-events:none;}
  #rgon-s10-toast.s10-show{opacity:1;}
</style>
<script id="rgon-step10-bars-script">
(function () {
  'use strict';
  if (window.RGON_STEP10_BARS) return;
  window.RGON_STEP10_BARS = true;

  var HANDOFF_TEXT = HANDOFF_JSON;
  var KEY_BAR1 = '4대 AI 분배 컨트롤러';
  var KEY_BAR2 = '실시간 브리핑 전문';
  var KEY_BAR3 = '독대실에서 바로 분배하기';
  var KEY_BAR4 = '1:1 대화창';
  var greenOpen = false;
  var origBriefing = '';

  function norm(s) { return String(s || '').replace(/\s+/g, ' ').trim(); }

  function toast(msg) {
    var t = document.getElementById('rgon-s10-toast');
    if (!t) { t = document.createElement('div'); t.id = 'rgon-s10-toast'; document.body.appendChild(t); }
    t.textContent = msg;
    t.classList.add('s10-show');
    clearTimeout(t.__h);
    t.__h = setTimeout(function () { t.classList.remove('s10-show'); }, 2200);
  }

  function copyText(txt, okMsg) {
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = txt; ta.style.position = 'fixed'; ta.style.left = '-9999px';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); toast(okMsg); } catch (e) { toast('⚠ 복사 실패'); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && window.isSecureContext !== false) {
      navigator.clipboard.writeText(txt).then(function () { toast(okMsg); }, fallback);
    } else fallback();
  }

  function isOwn(el) {
    return !!(el && el.closest && el.closest('#rgon-green-briefing-bar,[data-s10-own],#rgon-v9-drawer,.rgon-v9-drawer,#rgon-s10-toast'));
  }

  function findHeader(key) {
    if (!document.body) return null;
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    var n;
    while ((n = w.nextNode())) {
      if (!n.nodeValue || n.nodeValue.indexOf(key) === -1) continue;
      var el = n.parentElement;
      if (!el || isOwn(el)) continue;
      if (/^(SCRIPT|STYLE|TEXTAREA|TITLE|OPTION|NOSCRIPT)$/.test(el.tagName)) continue;
      var sum = el.closest('summary');
      if (sum) {
        var det = sum.parentElement && sum.parentElement.tagName === 'DETAILS' ? sum.parentElement : null;
        return { header: sum, details: det };
      }
      var h = el;
      while (h.parentElement && h.parentElement !== document.body && norm(h.parentElement.textContent).length <= key.length + 90) {
        h = h.parentElement;
      }
      return { header: h, details: null };
    }
    return null;
  }

  function nextBody(header) {
    var b = header.nextElementSibling;
    while (b && (b.id === 'rgon-green-briefing-bar' || b.hasAttribute('data-s10-own') ||
                 b.tagName === 'SCRIPT' || b.tagName === 'STYLE')) b = b.nextElementSibling;
    return b;
  }

  function forceShow(el) {
    var cur = el, guard = 0;
    while (cur && cur !== document.body && guard++ < 6) {
      if (cur.style && cur.style.display === 'none') cur.style.setProperty('display', 'block', 'important');
      cur.removeAttribute('hidden');
      cur = cur.parentElement;
    }
  }

  function isOpen(body) {
    if (!body || body.hidden) return false;
    var cs = getComputedStyle(body);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.maxHeight === '0px') return false;
    return body.offsetHeight > 0;
  }

  function bindAcc(header, body) {
    if (!header || !body || header.getAttribute('data-s10-acc')) return;
    header.setAttribute('data-s10-acc', '1');
    header.style.cursor = 'pointer';
    header.addEventListener('click', function (e) {
      var ctl = e.target.closest && e.target.closest('button,input,textarea,select,a');
      if (ctl && ctl !== header) return;
      var wasOpen = isOpen(body);
      setTimeout(function () {
        if (isOpen(body) === wasOpen) {
          if (wasOpen) {
            body.style.setProperty('display', 'none', 'important');
          } else {
            body.removeAttribute('hidden');
            body.style.setProperty('display', 'block', 'important');
          }
        }
      }, 45);
    });
  }

  function fixBar(key) {
    var f = findHeader(key);
    if (!f) return null;
    if (f.details) {
      forceShow(f.details);
      f.details.classList.add('rgon-s10-force-show');
      return f;
    }
    forceShow(f.header);
    var body = nextBody(f.header);
    if (body) bindAcc(f.header, body);
    if (f.header.parentElement && f.header.parentElement !== document.body) {
      forceShow(f.header.parentElement);
    }
    return f;
  }

  function pretty(v, ind) {
    ind = ind || '';
    if (v === null || v === undefined) return ind + '-';
    if (typeof v !== 'object') return ind + String(v);
    if (Array.isArray(v)) {
      return v.map(function (x, i) {
        return (x !== null && typeof x === 'object')
          ? ind + '• [' + (i + 1) + ']\n' + pretty(x, ind + '   ')
          : ind + '• ' + String(x);
      }).join('\n');
    }
    return Object.keys(v).map(function (k) {
      var x = v[k];
      if (x !== null && typeof x === 'object') return ind + '▸ ' + k + '\n' + pretty(x, ind + '   ');
      return ind + '▸ ' + k + ': ' + String(x);
    }).join('\n');
  }

  function fetchJson(url) {
    return fetch(url + '?t=' + Date.now(), { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }

  function loadBriefing() {
    var pre = document.getElementById('rgon-green-briefing-pre');
    var meta = document.getElementById('rgon-green-briefing-meta');
    if (!pre) return;
    pre.textContent = '⏳ 사령부 브리핑을 불러오는 중...';
    Promise.allSettled([fetchJson('./rgon_brain_snapshot.json'), fetchJson('./rgon_command_status.json')])
      .then(function (rs) {
        var parts = [];
        if (rs[0].status === 'fulfilled') parts.push('━━━━ 🧠 사령부 브레인 스냅샷 ━━━━\n' + pretty(rs[0].value));
        if (rs[1].status === 'fulfilled') parts.push('━━━━ 📡 명령 실행 상태 ━━━━\n' + pretty(rs[1].value));
        if (!parts.length) {
          parts.push(origBriefing || '✅ 사령부 브리핑 대기 중입니다.');
        } else if (origBriefing) {
          parts.push('━━━━ 🛰️ 페이지 내 기존 브리핑 ━━━━\n' + origBriefing);
        }
        pre.textContent = parts.join('\n\n');
        if (meta) meta.textContent = '마지막 갱신: ' + new Date().toLocaleString('ko-KR');
      });
  }

  function setGreen(open) {
    greenOpen = open;
    var body = document.getElementById('rgon-green-briefing-body');
    var arrow = document.getElementById('rgon-green-briefing-arrow');
    if (body) body.classList.toggle('s10-open', open);
    if (arrow) arrow.textContent = open ? '▲' : '▼';
    if (open) loadBriefing();
  }

  function buildGreen() {
    var bar = document.createElement('div');
    bar.id = 'rgon-green-briefing-bar';
    bar.setAttribute('data-s10-own', '1');
    bar.innerHTML =
      '<div id="rgon-green-briefing-head">' +
        '<span><span id="rgon-green-briefing-arrow">▼</span> 🛰️ 르곤-알파 실시간 브리핑 전문</span>' +
        '<span class="s10-hint">(클릭하여 열기/접기)</span>' +
      '</div>' +
      '<div id="rgon-green-briefing-body">' +
        '<div>' +
          '<button type="button" class="rgon-s10-btn" id="rgon-green-refresh">🔄 새로고침</button>' +
          '<button type="button" class="rgon-s10-btn" id="rgon-green-copy">📋 브리핑 복사</button>' +
        '</div>' +
        '<div id="rgon-green-briefing-meta"></div>' +
        '<pre id="rgon-green-briefing-pre"></pre>' +
      '</div>';
    bar.querySelector('#rgon-green-briefing-head').addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      setGreen(!greenOpen);
    });
    bar.querySelector('#rgon-green-briefing-body').addEventListener('click', function (e) { e.stopPropagation(); });
    bar.querySelector('#rgon-green-refresh').addEventListener('click', function (e) {
      e.preventDefault(); loadBriefing();
    });
    bar.querySelector('#rgon-green-copy').addEventListener('click', function (e) {
      e.preventDefault();
      var pre = document.getElementById('rgon-green-briefing-pre');
      copyText(pre ? pre.textContent : '', '✅ 브리핑 전문이 복사되었습니다!');
    });
    return bar;
  }

  function insertAfter(ref, node) { ref.parentNode.insertBefore(node, ref.nextSibling); }

  function ensureGreen() {
    if (document.getElementById('rgon-green-briefing-bar')) return;
    var bar = buildGreen();
    var orig = findHeader(KEY_BAR2);
    if (orig) {
      var block = orig.details || orig.header;
      if (orig.details) {
        var s = orig.details.querySelector('summary');
        origBriefing = (orig.details.innerText || orig.details.textContent || '')
          .replace(s ? (s.innerText || s.textContent) : '', '').trim();
      } else {
        var ob = nextBody(orig.header);
        if (ob) { origBriefing = (ob.innerText || ob.textContent || '').trim(); ob.classList.add('rgon-s10-replaced'); }
      }
      block.parentNode.insertBefore(bar, block);
      block.classList.add('rgon-s10-replaced');
    } else {
      var b1 = findHeader(KEY_BAR1);
      var b3 = findHeader(KEY_BAR3);
      if (b1) {
        var ref = b1.details || nextBody(b1.header) || b1.header;
        insertAfter(ref, bar);
      } else if (b3) {
        var r3 = b3.details || b3.header;
        r3.parentNode.insertBefore(bar, r3);
      } else {
        document.body.insertBefore(bar, document.body.firstChild);
      }
    }
  }

  function ensureHandoffBtn() {
    if (document.getElementById('rgon-s10-handoff-btn')) return;
    var drawer = document.querySelector('#rgon-v9-drawer, .rgon-v9-drawer, [id*="drawer"]');
    if (!drawer) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'rgon-s10-handoff-btn';
    btn.textContent = '📋 새 AI 인수인계 전달서 복사 (5시간 세션 대비)';
    btn.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      var txt = HANDOFF_TEXT.replace('{{NOW}}', new Date().toLocaleString('ko-KR'));
      copyText(txt, '✅ 새 AI 인수인계 전달서가 복사되었습니다!');
    });
    drawer.insertBefore(btn, drawer.firstChild);
  }

  function applyStep10() {
    fixBar(KEY_BAR1);
    ensureGreen();
    fixBar(KEY_BAR3);
    fixBar(KEY_BAR4);
    ensureHandoffBtn();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyStep10);
  } else {
    applyStep10();
  }
  setTimeout(applyStep10, 400);
  setTimeout(applyStep10, 1200);
})();
</script>
<!-- [RGON-STEP10-BARS-END] -->
"""


def build_handoff_text():
    repo_lines = "\n".join(f"  {i + 1}) {u}" for i, u in enumerate(GITHUB_REPOS))
    return (
        "[RGON 사령부 클라우드 직통 인수인계서 — 새 AI 즉시 장착용]\n"
        "생성 시각: {{NOW}}\n\n"
        "너는 이상일 대표님을 보좌하는 핵심 AI 보좌관이다.\n"
        "젠스파크 5시간 세션 초기화(또는 새 채팅방 교체)로 대화를 이어간다. 처음부터 다시 묻지 말고, 즉시 아래 GitHub 주소들을 확인하여 현재 진행 상황을 100% 파악한 뒤 작업을 이어가라.\n\n"
        "■ 1. 핵심 GitHub 주소 4종 (이 주소들을 먼저 읽어라)\n"
        f"{repo_lines}\n\n"
        "■ 2. 현재 시스템 구조 간단 요약\n"
        f"  - 로컬 PC 작업 경로: {BASE_DIR}\n"
        "  - 크롬 확장프로그램(우측 흡수창) 하단 4칸 버튼: [💾 shin-agent 저장 | 🧹 지우기 | ⚡ 안총리 직통 | 🗑️ 전체 지우기]\n"
        "  - 독대실 4대 아코디언 바: ① 🎯 4대 AI 분배 컨트롤러 ② 🛰️ 르곤-알파 실시간 브리핑 전문 ③ ⚡ 독대실에서 바로 분배하기 ④ 💬 르곤-알파 1:1 대화창\n\n"
        "■ 3. 절대 작업 및 보고 원칙\n"
        "  - 초등학생도 1초 만에 이해할 수 있게 쉽고 명확하게 핵심만 보고할 것.\n"
        "  - 코딩이 필요할 때는 클로드(Claude)가 안전 필터 거부 없이 100% 작성할 수 있도록 '순수 Python 3 표준 라이브러리 전용 + 로컬 파일 비파괴 패치 + 자동 git add/commit/push' 형태로 제공할 것.\n\n"
        "위 내용을 숙지하고 GitHub 최신 커밋을 확인한 즉시 '충성! 이상일 대표님! GitHub 최신 상태 확인 완료했습니다!'라고 보고하라.\n"
    )


def patch_html(path, block):
    rel = os.path.relpath(path, BASE_DIR)
    log(f"\n[2] HTML 패치: {rel}")
    if not os.path.isfile(path):
        log("   ✖ 파일 없음 → 건너뜀")
        return False
    try:
        text, has_bom, nl = read_text(path)
    except UnicodeDecodeError:
        log("   ✖ utf-8 로 읽을 수 없어 건너뜁니다.")
        return False
    bak = make_backup(path)
    log(f"   - 백업: {os.path.relpath(bak, BASE_DIR)}")

    text = remove_blocks(
        text,
        r"<!-- \[RGON-PINPOINT-FIX-START\] -->",
        r"<!-- \[RGON-PINPOINT-FIX-END\] -->",
        "RGON-PINPOINT-FIX",
    )
    text = remove_blocks(
        text,
        r"<!-- \[RGON-STEP10-BARS-START\] -->",
        r"<!-- \[RGON-STEP10-BARS-END\] -->",
        "RGON-STEP10-BARS(이전 실행분)",
    )

    blk = block.replace("\n", nl)
    m = None
    for m in re.finditer(r"<!-- \[RGON-CLEAN-V9-END\] -->", text):
        pass
    if m:
        pos = m.end()
        text = text[:pos] + nl + blk + text[pos:]
        log("   - RGON-CLEAN-V9 블록 바로 뒤에 STEP10 블록 삽입")
    else:
        idx = text.lower().rfind("</body>")
        if idx != -1:
            text = text[:idx] + blk + nl + text[idx:]
            log("   - </body> 직전에 STEP10 블록 삽입")
        else:
            text = text + nl + blk
            log("   - 파일 끝에 STEP10 블록 추가")

    write_text(path, text, has_bom)
    log("   ✔ 완료")
    return True


# ──────────────────────────────────────────────────────────────
# 4. Git 자동 반영
# ──────────────────────────────────────────────────────────────
def ensure_backup_excluded():
    exclude = os.path.join(BASE_DIR, ".git", "info", "exclude")
    pattern = "*" + BACKUP_SUFFIX + "*"
    try:
        os.makedirs(os.path.dirname(exclude), exist_ok=True)
        existing = ""
        if os.path.exists(exclude):
            with open(exclude, "r", encoding="utf-8", errors="replace") as f:
                existing = f.read()
        if pattern not in existing.split():
            with open(exclude, "a", encoding="utf-8") as f:
                f.write(("\n" if existing and not existing.endswith("\n") else "") + pattern + "\n")
    except Exception:
        pass


def git_sync():
    log("\n[3] GitHub 자동 반영")
    code, _ = run_git(["rev-parse", "--is-inside-work-tree"], BASE_DIR)
    if code != 0:
        return False, "Git 저장소가 아닙니다."
    ensure_backup_excluded()

    run_git(["add", "-A"], BASE_DIR)
    code, out = run_git(["commit", "-m", COMMIT_MSG], BASE_DIR)
    log(f"   $ git commit → {code}")
    run_git(["pull", "--rebase", "origin", "main"], BASE_DIR)
    code, out = run_git(["push", "origin", "main"], BASE_DIR)
    log(f"   $ git push origin main → {code}")
    if code != 0:
        return False, "git push 실패:\n" + out[-400:]
    return True, "GitHub 푸시 완료"


# ──────────────────────────────────────────────────────────────
# 5. 마무리 안내
# ──────────────────────────────────────────────────────────────
def show_message(git_ok, git_msg):
    ok_text = (
        "✅ Step 10 패치 및 GitHub 푸시 완료!\n\n"
        "지금 크롬 주소창에 chrome://extensions 를 입력하신 뒤,\n"
        "[RGON Omni-Link] 확장프로그램의 ↻(새로고침) 버튼을 한 번 누르고\n"
        "젠스파크 창을 새로고침(F5)하시면 우측 흡수창에 [🧹 지우기 / 🗑️ 전체 지우기] 4칸 버튼이 즉시 나타납니다!"
    )
    text = ok_text if git_ok else ("⚠ 파일 패치 완료 (Git 확인 필요):\n" + git_msg)
    log("\n" + text)
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, "RGON Step 10 완료", 0x40 | 0x40000 | 0x10000)
        except Exception:
            pass


def main():
    log("=" * 64)
    log(" RGON Step 10 — 4대 아코디언 바 복구 + 확장 4칸 버튼 패치")
    log(f" 탐지된 작업 폴더: {BASE_DIR}")
    log("=" * 64)
    if not os.path.isdir(BASE_DIR):
        log(f"✖ 작업 폴더가 없습니다: {BASE_DIR}")
        return

    patch_extension()

    handoff = build_handoff_text()
    block = HTML_BLOCK_TEMPLATE.replace("HANDOFF_JSON", js_string(handoff))
    done = sum(1 for p in HTML_TARGETS if patch_html(p, block))
    log(f"\n   → HTML {done}/{len(HTML_TARGETS)}개 파일 패치 완료")

    git_ok, git_msg = git_sync()
    log(f"\n[4] 결과: {git_msg}")
    show_message(git_ok, git_msg)


if __name__ == "__main__":
    main()
