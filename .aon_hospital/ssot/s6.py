#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step6_final_polish.py (RGON v6.0.8 / STEP 6 FINAL POLISH)

Fixes the remaining 3 UI issues seen in mobile screenshots:
1) Picture 1: Forces #dokdae-feed (and the chat message container) completely OUTSIDE
   any <details> drawer (including the '🧰 6대 기관 지휘 · 음성 도구함' drawer) so the
   chat feed is ALWAYS visible even when all drawers are closed.
2) Picture 2: Ensures the top 'Omni-Link 분배 컨트롤러 v6.0.8' box ALWAYS includes
   the 4th pillar checkbox ('🔵👑 르곤 (Gemini 4 Argon)') and solo button
   ('🔵👑 르곤 (Gemini 4 Argon) 단독'), matching the bottom panel 100%.
3) Picture 3: Removes any fixed height / min-height gap inside #rgon-omni-drawer
   and its parent wrappers so there is zero empty dark space.
"""
import os
import re
import sys
import shutil
import tempfile
import datetime
import subprocess

DEFAULT_BASE = r"C:\Users\sangi\Downloads\shin-agent"
TARGETS = [
    "rgon_alpha_chat.html",
    os.path.join("dashboard", "rgon_alpha_chat.html"),
    os.path.join("docs", "rgon_alpha_chat.html"),
]

STYLE_ID = "rgon-step6-polish-css"
SCRIPT_ID = "rgon-step6-polish-js"
GIT_MSG = "fix(v6.0.8-step6): rescue dokdae-feed outside details, add rgon to top controller & remove dark gap"
DONE_MARK = "[STEP 6 FINAL POLISH COMPLETE]"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CSS = r"""
/* RGON_STEP6_STYLE_BEGIN */
html, body {
  min-height: 0 !important;
}
details,
#rgon-omni-drawer,
#rgon-omni-top-drawer,
#rgon-tools-drawer {
  min-height: 0 !important;
  height: auto !important;
  flex: 0 0 auto !important;
}
details:not([open]) {
  min-height: 0 !important;
  height: auto !important;
  padding-bottom: 4px !important;
}
#dokdae-feed,
.rgon-rescued-feed {
  display: flex !important;
  flex-direction: column !important;
  width: 100% !important;
  max-width: 100% !important;
  flex: 1 1 auto !important;
  min-height: 280px !important;
  margin: 8px 0 !important;
  padding: 10px !important;
  box-sizing: border-box !important;
  visibility: visible !important;
  opacity: 1 !important;
}
#dokdae-feed *,
.rgon-rescued-feed * {
  writing-mode: horizontal-tb !important;
}
/* RGON_STEP6_STYLE_END */
"""

JS = r"""
/* RGON_STEP6_BEGIN */
(function () {
  'use strict';
  if (window.__RGON_STEP6__) return;
  window.__RGON_STEP6__ = true;

  function findChatFeedElement() {
    var feed = document.getElementById('dokdae-feed');
    if (feed) return feed;

    var all = document.querySelectorAll('div, section, main');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var txt = (el.textContent || '');
      if (txt.indexOf('충성! 이상일 대표님!') !== -1 && txt.indexOf('대시보드 총괄사령관') !== -1) {
        if (el.children.length <= 6) {
          return el.parentElement || el;
        }
      }
    }
    return null;
  }

  function findBottomInputBar() {
    var inp = document.getElementById('dokdae-input');
    if (!inp) {
      var inputs = document.querySelectorAll('input, textarea');
      for (var i = 0; i < inputs.length; i++) {
        var ph = (inputs[i].getAttribute('placeholder') || '');
        if (ph.indexOf('르곤-알파에게') !== -1 || ph.indexOf('단독 지시') !== -1) {
          inp = inputs[i];
          break;
        }
      }
    }
    if (!inp) return null;
    var bar = inp;
    while (bar.parentElement && bar.parentElement !== document.body) {
      var p = bar.parentElement;
      if (p.tagName === 'BODY' || p.tagName === 'MAIN' || p.querySelector('details')) {
        break;
      }
      bar = p;
    }
    return bar;
  }

  function rescueChatFeedOutsideDrawers() {
    var feed = findChatFeedElement();
    if (!feed) return;
    feed.classList.add('rgon-rescued-feed');

    var insideDetails = feed.closest('details');
    var inputBar = findBottomInputBar();

    if (insideDetails) {
      var topDetails = insideDetails;
      var p = insideDetails.parentElement;
      while (p && p !== document.body) {
        if (p.tagName === 'DETAILS') topDetails = p;
        p = p.parentElement;
      }
      if (inputBar && inputBar.parentNode) {
        inputBar.parentNode.insertBefore(feed, inputBar);
      } else if (topDetails.parentNode) {
        topDetails.parentNode.insertBefore(feed, topDetails.nextSibling);
      }
    } else if (inputBar && inputBar.parentNode && feed.parentNode !== inputBar.parentNode) {
      var parentStyle = window.getComputedStyle(feed.parentElement);
      if (parentStyle && parentStyle.display === 'flex' && parentStyle.flexDirection === 'row') {
        inputBar.parentNode.insertBefore(feed, inputBar);
      }
    }
  }

  function ensureTopControllerHasRgon() {
    var boxes = document.querySelectorAll('#rgon-omni-drawer, #rgon-omni-top-drawer, details, div');
    for (var i = 0; i < boxes.length; i++) {
      var box = boxes[i];
      if (box.id === 'rgon-step5-solo-panel' || box.closest('#rgon-step5-solo-panel')) continue;

      var claudeSoloBtn = null;
      var btns = box.querySelectorAll('button');
      for (var j = 0; j < btns.length; j++) {
        var btxt = (btns[j].textContent || '').trim();
        if (btxt.indexOf('Claude 단독') !== -1 && !btns[j].closest('#rgon-step5-solo-panel')) {
          claudeSoloBtn = btns[j];
          break;
        }
      }
      if (!claudeSoloBtn) continue;

      var hostCard = claudeSoloBtn.closest('div') ? claudeSoloBtn.parentElement : box;
      if (!hostCard) continue;

      var hasRgonBtn = false;
      var siblingBtns = hostCard.parentElement ? hostCard.parentElement.querySelectorAll('button') : hostCard.querySelectorAll('button');
      for (var k = 0; k < siblingBtns.length; k++) {
        if ((siblingBtns[k].textContent || '').indexOf('르곤') !== -1 && (siblingBtns[k].textContent || '').indexOf('단독') !== -1) {
          hasRgonBtn = true;
          break;
        }
      }
      if (!hasRgonBtn && claudeSoloBtn.parentNode) {
        var rgonBtn = document.createElement('button');
        rgonBtn.type = 'button';
        rgonBtn.className = claudeSoloBtn.className;
        rgonBtn.style.cssText = claudeSoloBtn.style.cssText;
        rgonBtn.setAttribute('data-solo', 'rgon');
        rgonBtn.setAttribute('data-role', 'rgon');
        rgonBtn.textContent = '🔵👑 르곤 (Gemini 4 Argon) 단독';
        rgonBtn.addEventListener('click', function () {
          if (window.__RGON_STEP5__ && typeof window.__RGON_STEP5__.fire === 'function') {
            window.__RGON_STEP5__.fire(['rgon']);
          } else {
            var ta = document.querySelector('#rgon-omni-drawer textarea') || document.querySelector('textarea');
            var t = ta ? ta.value : '';
            window.postMessage({ type: 'RGON_OMNI_DISPATCH', roles: ['rgon'], prompt: t, text: t }, '*');
          }
        });
        claudeSoloBtn.parentNode.insertBefore(rgonBtn, claudeSoloBtn);
      }

      var cardRoot = claudeSoloBtn.closest('#rgon-omni-drawer') || hostCard.parentElement || hostCard;
      var labels = cardRoot.querySelectorAll('label');
      var claudeLabel = null;
      var hasRgonChk = false;
      for (var m = 0; m < labels.length; m++) {
        if (labels[m].closest('#rgon-step5-solo-panel')) continue;
        var ltxt = (labels[m].textContent || '');
        if (ltxt.indexOf('르곤') !== -1) hasRgonChk = true;
        if (ltxt.indexOf('Claude') !== -1 && !claudeLabel) claudeLabel = labels[m];
      }
      if (!hasRgonChk && claudeLabel && claudeLabel.parentNode) {
        var rgonLabel = document.createElement('label');
        rgonLabel.className = claudeLabel.className;
        rgonLabel.style.cssText = claudeLabel.style.cssText || 'display:inline-flex;align-items:center;gap:5px;margin-right:8px;cursor:pointer;';
        rgonLabel.innerHTML = '<input type="checkbox" value="rgon" data-role="rgon" checked> <span>🔵👑 르곤 (Gemini 4 Argon)</span>';
        claudeLabel.parentNode.insertBefore(rgonLabel, claudeLabel);
      }
      break;
    }
  }

  function removeEmptyDarkGaps() {
    var drawers = document.querySelectorAll('details, #rgon-omni-drawer, #rgon-tools-drawer');
    for (var i = 0; i < drawers.length; i++) {
      var d = drawers[i];
      d.style.setProperty('min-height', '0', 'important');
      d.style.setProperty('height', 'auto', 'important');
      d.style.setProperty('flex', '0 0 auto', 'important');
    }
  }

  function tick() {
    try {
      rescueChatFeedOutsideDrawers();
      ensureTopControllerHasRgon();
      removeEmptyDarkGaps();
    } catch (e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tick);
  } else {
    tick();
  }
  setTimeout(tick, 200);
  setTimeout(tick, 700);
  setInterval(tick, 1200);
})();
/* RGON_STEP6_END */
"""


def node_check(js_code):
    node = shutil.which("node")
    if not node:
        return True
    fd, path = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(js_code)
        r = subprocess.run([node, "--check", path], capture_output=True, text=True)
        if r.returncode != 0:
            print("[step6][ERROR] node --check failed:\n" + (r.stderr or ""), file=sys.stderr)
            return False
        print("[step6] node --check passed for injected JS")
        return True
    finally:
        if os.path.exists(path):
            os.unlink(path)


def patch_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    html = re.sub(
        r'<style[^>]*id=["\']' + re.escape(STYLE_ID) + r'["\'][^>]*>.*?</style>\s*',
        "",
        html,
        flags=re.S | re.I,
    )
    html = re.sub(
        r'<script[^>]*id=["\']' + re.escape(SCRIPT_ID) + r'["\'][^>]*>.*?</script>\s*',
        "",
        html,
        flags=re.S | re.I,
    )

    block = (
        f'\n<style id="{STYLE_ID}">\n{CSS.strip()}\n</style>\n'
        f'<script id="{SCRIPT_ID}">\n{JS.strip()}\n</script>\n'
    )

    if "</body>" in html:
        idx = html.rfind("</body>")
        html = html[:idx] + block + html[idx:]
    else:
        html += block

    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("[step6] patched " + filepath)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else DEFAULT_BASE
    if not node_check(JS):
        return 3

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = os.path.join(base, "backups", "step6_" + stamp)
    os.makedirs(bdir, exist_ok=True)

    for rel in TARGETS:
        p = os.path.join(base, rel)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(bdir, rel.replace(os.sep, "__").replace("/", "__")))
            patch_file(p)

    subprocess.run(["git", "add", "-A"], cwd=base)
    subprocess.run(["git", "commit", "-m", GIT_MSG], cwd=base)
    subprocess.run(["git", "push", "origin", "main"], cwd=base)
    print(DONE_MARK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
