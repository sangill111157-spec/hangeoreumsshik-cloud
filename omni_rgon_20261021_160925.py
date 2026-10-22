#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step7_untrap_chat_from_tools.py
RGON v6.0.8 - Step 7 : 음성 도구함 <details> 서랍에 갇힌 대화 피드 구출 + 세로 글자 깨짐 수정

대상 파일
  shin-agent/rgon_alpha_chat.html
  shin-agent/dashboard/rgon_alpha_chat.html
  shin-agent/docs/rgon_alpha_chat.html

동작 순서
  1) 파일마다 backups/step7_<timestamp>/ 에 원본 백업
  2) 정적 구출: HTML을 오프셋 트리로 분석해 '음성 도구함' <details> 안에서
     #dokdae-feed, '충성! 이상일 대표님' 메시지 컨테이너, '6대 청사 실시간 보좌 지표' 서랍을 찾음.
     도구 버튼이 섞이지 않는 가장 바깥 컨테이너까지만 잘라 #rgon-step7-chat-zone(폭 100%)으로 옮기고,
     그 영역은 하단 입력창(르곤-알파에게… / 알파에게 전송) 바로 위에 둠.
  3) 런타임 구출: 페이지가 동적으로 그리는 요소도 구출함.
     step2가 다시 서랍 안으로 집어넣으려 하면 appendChild/insertBefore/append 등 가드와
     MutationObserver가 막음. 이미 알려진 step2 함수 이름이 있으면 호출 직후 재구출함.
  4) 세로 깨짐: 르곤-알파 / 대시보드 총괄사령관 / 듣기 / 시간 요소와 짧은 헤더 행에 가로 정렬 강제 적용.
  5) #rgon-step5-solo-panel 은 이동하거나 수정하지 않음. (inject_runtime 전 기준으로 개수 검증)
  6) node --check 로 인라인 스크립트를 검사함. 수정 후 실패가 늘면 그 파일은 저장하지 않음.
  7) git add -A / commit / push origin main
"""
import os
import re
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
if not BASE.exists():
    BASE = Path(__file__).resolve().parent

TARGETS = [
    BASE / "rgon_alpha_chat.html",
    BASE / "dashboard" / "rgon_alpha_chat.html",
    BASE / "docs" / "rgon_alpha_chat.html",
]
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = BASE / "backups" / f"step7_{STAMP}"
NODE = shutil.which("node")

ZONE_ID = "rgon-step7-chat-zone"
STEP5_ID = "rgon-step5-solo-panel"
TOOL_PHRASES = ["음성 중지", "청년보이스 테스트", "음성 설정", "Adobe 무료", "한마디 올인원"]
CHAT_PHRASE = "충성! 이상일 대표님"
IND_PHRASE = "6대 청사 실시간 보좌 지표"
FEED_IDS = {"dokdae-feed", "dokdae-messages", "dokdae-chat", "chat-feed", "chatfeed",
            "chat-log", "chatlog", "messages"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr"}

MARK_S = "<!-- RGON-STEP7-UNTRAP START -->"
MARK_E = "<!-- RGON-STEP7-UNTRAP END -->"

# =====================================================================
# 런타임 CSS
# =====================================================================
RUNTIME_CSS = r"""
#rgon-step7-chat-zone{display:block!important;position:relative!important;width:100%!important;max-width:100%!important;flex:1 1 100%!important;min-width:0!important;box-sizing:border-box!important;clear:both!important;margin:8px 0!important;writing-mode:horizontal-tb!important}
#rgon-step7-chat-zone > [data-rgon-untrapped="1"]{width:100%!important;max-width:100%!important;flex:1 1 100%!important;min-width:0!important;box-sizing:border-box!important}
#rgon-step7-chat-zone #dokdae-feed{width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important}
#rgon-step7-chat-zone .rgon-s7-row{display:flex!important;flex-direction:row!important;flex-wrap:wrap!important;align-items:center!important;gap:6px!important;white-space:nowrap!important;word-break:keep-all!important;width:auto!important;max-width:100%!important;writing-mode:horizontal-tb!important}
#rgon-step7-chat-zone .rgon-s7-nw{display:flex!important;flex-direction:row!important;flex-wrap:wrap!important;align-items:center!important;white-space:nowrap!important;word-break:keep-all!important;overflow-wrap:normal!important;width:auto!important;max-width:none!important;flex:0 0 auto!important;writing-mode:horizontal-tb!important}
"""

# =====================================================================
# 런타임 JS
# =====================================================================
RUNTIME_JS = r"""
(function () {
  "use strict";
  if (window.__RGON_STEP7_UNTRAP__) return;
  window.__RGON_STEP7_UNTRAP__ = true;

  var ZONE_ID = "rgon-step7-chat-zone";
  var STEP5_ID = "rgon-step5-solo-panel";
  var TOOL_RE = /음성 중지|청년보이스 테스트|음성 설정|Adobe 무료|한마디 올인원/;
  var PHRASES = ["충성! 이상일 대표님", "6대 청사 실시간 보좌 지표"];
  var FEED_SEL = "#dokdae-feed,#dokdae-messages,#dokdae-chat,#chat-feed,#chatFeed,#chat-log,#chatLog,#messages,[data-rgon-untrapped='1']";
  var N = {
    appendChild: Node.prototype.appendChild,
    insertBefore: Node.prototype.insertBefore,
    append: Element.prototype.append,
    prepend: Element.prototype.prepend,
    before: Element.prototype.before,
    after: Element.prototype.after,
    iae: Element.prototype.insertAdjacentElement
  };
  var busy = false;

  function txt(el) { return (el && el.textContent) || ""; }

  function directSummary(d) {
    for (var c = d.firstElementChild; c; c = c.nextElementSibling) {
      if (c.tagName === "SUMMARY") return c;
    }
    return null;
  }

  function findDrawer() {
    var ds = document.getElementsByTagName("details"), fb = null;
    for (var i = 0; i < ds.length; i++) {
      var s = directSummary(ds[i]);
      if (!s) continue;
      var t = txt(s);
      if (t.indexOf("음성 도구함") >= 0) return ds[i];
      if (!fb && t.indexOf("6대 기관 지휘") >= 0) fb = ds[i];
    }
    return fb;
  }

  function hasStep5(el) {
    return el.id === STEP5_ID || !!(el.querySelector && el.querySelector("#" + STEP5_ID));
  }

  function isIndicator(el) {
    if (el.tagName === "DETAILS") {
      var s = directSummary(el);
      if (s && txt(s).indexOf("보좌 지표") >= 0) return true;
    }
    var t = txt(el);
    return t.indexOf("보좌 지표") >= 0 && t.indexOf("충성!") < 0 && t.length < 600;
  }

  function climb(el, drawer) {
    if (!el || el === drawer || !drawer.contains(el)) return null;
    if (el.id === ZONE_ID) return null;
    var sum = directSummary(drawer);
    if (sum && sum.contains(el)) return null;
    if (el.closest && el.closest("#" + STEP5_ID)) return null;
    while (el.parentElement && el.parentElement !== drawer) {
      var p = el.parentElement;
      if (TOOL_RE.test(txt(p)) || hasStep5(p)) break;
      el = p;
    }
    if (el.tagName === "SUMMARY" || hasStep5(el)) return null;
    return el;
  }

  function collect(drawer) {
    var hits = [], i, n;
    var f = drawer.querySelectorAll(FEED_SEL);
    for (i = 0; i < f.length; i++) hits.push(f[i]);
    var ds = drawer.getElementsByTagName("details");
    for (i = 0; i < ds.length; i++) {
      var s = directSummary(ds[i]);
      if (s && txt(s).indexOf("보좌 지표") >= 0) hits.push(ds[i]);
    }
    var w = document.createTreeWalker(drawer, NodeFilter.SHOW_TEXT, null);
    while ((n = w.nextNode())) {
      var v = n.nodeValue || "", pe = n.parentElement;
      if (!pe || /^(SCRIPT|STYLE|TEMPLATE)$/.test(pe.tagName)) continue;
      for (i = 0; i < PHRASES.length; i++) {
        if (v.indexOf(PHRASES[i]) >= 0) { hits.push(pe); break; }
      }
    }
    var out = [];
    hits.forEach(function (h) {
      var c = climb(h, drawer);
      if (c && out.indexOf(c) < 0) out.push(c);
    });
    out = out.filter(function (a) {
      return !out.some(function (b) { return b !== a && b.contains(a); });
    });
    out.sort(function (a, b) {
      return (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING) ? -1 : 1;
    });
    return out;
  }

  function hasSend(el) {
    if (txt(el).indexOf("알파에게 전송") >= 0) return true;
    return !!(el.querySelector && el.querySelector("input[value*='전송'],button[aria-label*='전송']"));
  }

  function composerRoot(drawer) {
    var els = document.querySelectorAll("textarea,input");
    for (var i = 0; i < els.length; i++) {
      var ph = els[i].getAttribute("placeholder") || "";
      if (ph.indexOf("알파에게") < 0) continue;
      if (drawer && drawer.contains(els[i])) continue;
      var c = els[i];
      while (c.parentElement && c.parentElement !== document.body &&
             !(drawer && c.parentElement.contains(drawer)) && !hasSend(c)) {
        c = c.parentElement;
      }
      return c;
    }
    return null;
  }

  function flexRow(drawer) {
    var p = drawer.parentElement;
    if (!p || p === document.body) return null;
    var cs = getComputedStyle(p);
    if (cs.display.indexOf("flex") >= 0 && cs.flexDirection.indexOf("row") === 0) return p;
    return null;
  }

  function ensureZone(drawer) {
    var zone = document.getElementById(ZONE_ID);
    if (!zone) {
      zone = document.createElement("div");
      zone.id = ZONE_ID;
      zone.setAttribute("data-rgon-untrapped", "1");
    }
    var anchor = composerRoot(drawer);
    if (anchor && anchor.parentNode && anchor !== zone && !zone.contains(anchor)) {
      if (zone.parentNode !== anchor.parentNode || zone.nextElementSibling !== anchor) {
        N.insertBefore.call(anchor.parentNode, zone, anchor);
      }
    } else if (drawer) {
      var ref = flexRow(drawer) || drawer;
      if (ref.parentNode && (zone.parentNode !== ref.parentNode || zone.previousElementSibling !== ref)) {
        N.insertBefore.call(ref.parentNode, zone, ref.nextSibling);
      }
    }
    var p = zone.parentElement;
    if (p) {
      var cs = getComputedStyle(p);
      if (cs.display.indexOf("flex") >= 0 && cs.flexDirection.indexOf("row") === 0) {
        p.style.setProperty("flex-wrap", "wrap", "important");
      }
    }
    return zone;
  }

  function orderZone(zone) {
    var kids = Array.prototype.slice.call(zone.children), firstNon = -1, needs = false;
    kids.forEach(function (k, i) {
      if (isIndicator(k)) { if (firstNon >= 0) needs = true; }
      else if (firstNon < 0) firstNon = i;
    });
    if (!needs) return;
    kids.filter(isIndicator).reverse().forEach(function (k) {
      N.insertBefore.call(zone, k, zone.firstChild);
    });
  }

  function fixBadges(zone) {
    if (!zone) return;
    var els = zone.querySelectorAll("span,b,strong,small,em,i,div,button,time,label,a,p");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.classList.contains("rgon-s7-nw") || el.children.length > 3) continue;
      var t = (el.textContent || "").replace(/\s+/g, " ").trim();
      if (!t || t.length > 24) continue;
      if (t.indexOf("르곤-알파") >= 0 || t.indexOf("총괄사령관") >= 0 ||
          /^(?:\S{0,3}\s*)?듣기$/.test(t) || /(오전|오후)\s*\d{1,2}:\d{2}/.test(t)) {
        el.classList.add("rgon-s7-nw");
        var p = el.parentElement;
        if (p && p !== zone && !p.hasAttribute("data-rgon-untrapped") &&
            (p.textContent || "").trim().length <= 90) {
          p.classList.add("rgon-s7-row");
        }
      }
    }
  }

  function rescue() {
    if (busy) return;
    busy = true;
    try {
      var drawer = findDrawer();
      var zone = document.getElementById(ZONE_ID);
      if (drawer) {
        zone = ensureZone(drawer);
        collect(drawer).forEach(function (el) {
          if (el === zone || el.contains(zone)) return;
          el.setAttribute("data-rgon-untrapped", "1");
          N.appendChild.call(zone, el);
        });
        orderZone(zone);
      }
      fixBadges(zone);
    } catch (e) {
      try { console.warn("[RGON step7] rescue error", e); } catch (x) {}
    } finally {
      busy = false;
    }
  }

  function guarded(n) {
    if (!n || n.nodeType !== 1) return false;
    if (n.id === ZONE_ID || n.getAttribute("data-rgon-untrapped") === "1") return true;
    return !!n.querySelector("#" + ZONE_ID + ",[data-rgon-untrapped='1']");
  }
  function blocked(parent, n) {
    if (busy || !parent || !guarded(n)) return false;
    var d = findDrawer();
    return !!(d && (parent === d || d.contains(parent)));
  }
  Node.prototype.appendChild = function (n) {
    if (blocked(this, n)) return n;
    return N.appendChild.call(this, n);
  };
  Node.prototype.insertBefore = function (n, r) {
    if (blocked(this, n)) return n;
    return N.insertBefore.call(this, n, r);
  };
  Element.prototype.append = function () {
    var self = this;
    var a = Array.prototype.filter.call(arguments, function (x) { return !blocked(self, x); });
    return N.append.apply(this, a);
  };
  Element.prototype.prepend = function () {
    var self = this;
    var a = Array.prototype.filter.call(arguments, function (x) { return !blocked(self, x); });
    return N.prepend.apply(this, a);
  };
  if (N.before) {
    Element.prototype.before = function () {
      var p = this.parentNode;
      var a = Array.prototype.filter.call(arguments, function (x) { return !blocked(p, x); });
      return N.before.apply(this, a);
    };
  }
  if (N.after) {
    Element.prototype.after = function () {
      var p = this.parentNode;
      var a = Array.prototype.filter.call(arguments, function (x) { return !blocked(p, x); });
      return N.after.apply(this, a);
    };
  }
  Element.prototype.insertAdjacentElement = function (pos, el) {
    var pp = String(pos || "").toLowerCase();
    var parent = (pp === "beforebegin" || pp === "afterend") ? this.parentNode : this;
    if (blocked(parent, el)) return el;
    return N.iae.call(this, pos, el);
  };

  var KNOWN = ["rgonStep2Wrap", "rgonStep2Apply", "rgonStep2Layout", "rgonMobileCleanLayout",
               "rgonWrapToolDrawer", "rgonWrapTools", "wrapToolsDrawer", "applyMobileCleanLayout",
               "step2MobileClean"];
  function wrapKnown() {
    KNOWN.forEach(function (k) {
      var f = window[k];
      if (typeof f === "function" && !f.__rgonS7) {
        var g = function () {
          try { return f.apply(this, arguments); }
          finally { setTimeout(rescue, 0); }
        };
        g.__rgonS7 = true;
        try { window[k] = g; } catch (e) {}
      }
    });
  }

  var scheduled = false, runs = 0, winStart = Date.now();
  var raf = window.requestAnimationFrame || function (cb) { return setTimeout(cb, 16); };
  var mo = new MutationObserver(function () {
    if (busy || scheduled) return;
    scheduled = true;
    raf(function () {
      scheduled = false;
      var now = Date.now();
      if (now - winStart > 5000) { winStart = now; runs = 0; }
      if (++runs > 40) return;
      rescue();
    });
  });

  function boot() { wrapKnown(); rescue(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
  window.addEventListener("load", boot);
  [300, 1000, 2500, 5000].forEach(function (t) { setTimeout(boot, t); });
  document.addEventListener("toggle", function (e) {
    if (e.target && e.target.tagName === "DETAILS") rescue();
  }, true);
  try { mo.observe(document.documentElement, { childList: true, subtree: true }); } catch (e) {}
  window.rgonStep7Rescue = rescue;
})();
"""


class Node:
    __slots__ = ("tag", "attrs", "start", "sopen", "end", "parent", "children")

    def __init__(self, tag, attrs, start, sopen, parent):
        self.tag = tag
        self.attrs = attrs
        self.start = start
        self.sopen = sopen
        self.end = sopen
        self.parent = parent
        self.children = []


class TreeBuilder(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.ls = [0] + [m.end() for m in re.finditer("\n", text)]
        self.root = Node("#root", {}, 0, 0, None)
        self.root.end = len(text)
        self.stack = [self.root]
        self.nodes = []

    def _abs(self):
        line, col = self.getpos()
        return self.ls[line - 1] + col

    def _mk(self, tag, attrs):
        s = self._abs()
        raw = self.get_starttag_text() or ""
        n = Node(tag, {k: (v or "") for k, v in attrs}, s, s + len(raw), self.stack[-1])
        self.stack[-1].children.append(n)
        self.nodes.append(n)
        return n

    def handle_starttag(self, tag, attrs):
        n = self._mk(tag, attrs)
        if tag in VOID:
            n.end = n.sopen
        else:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        n = self._mk(tag, attrs)
        n.end = n.sopen

    def handle_endtag(self, tag):
        s = self._abs()
        e = self.text.find(">", s)
        e = len(self.text) if e < 0 else e + 1
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                for j in range(len(self.stack) - 1, i, -1):
                    self.stack[j].end = s
                self.stack[i].end = e
                del self.stack[i:]
                return

    def close(self):
        super().close()
        for n in self.stack[1:]:
            n.end = len(self.text)


def static_untrap(text):
    if re.search(r"""id\s*=\s*["']%s["']""" % ZONE_ID, text):
        return text, ["정적 구출 영역 이미 존재 → 런타임 가드만 갱신"]

    tb = TreeBuilder(text)
    try:
        tb.feed(text)
        tb.close()
    except Exception as e:
        return text, [f"HTML 파싱 실패({e}) → 런타임 구출에 위임"]
    nodes = tb.nodes
    vcache = {}

    def raw(n):
        return text[n.start:n.end]

    def vis(n):
        k = id(n)
        if k not in vcache:
            r = re.sub(r"<script\b.*?</script\s*>|<style\b.*?</style\s*>", "", raw(n), flags=re.S | re.I)
            vcache[k] = re.sub(r"<[^>]+>", "", r)
        return vcache[k]

    def contains(a, b):
        return a.start <= b.start and b.end <= a.end

    def summary_of(d):
        return next((c for c in d.children if c.tag == "summary"), None)

    drawer = None
    for key in ("음성 도구함", "6대 기관 지휘"):
        for n in nodes:
            if n.tag == "details":
                s = summary_of(n)
                if s and key in vis(s):
                    drawer = n
                    break
        if drawer:
            break
    if not drawer:
        return text, ["정적 HTML에 음성 도구함 <details> 없음 → 런타임 구출에 위임"]

    inside = [n for n in nodes if n is not drawer and drawer.sopen <= n.start and n.end <= drawer.end]
    hits = []
    for n in inside:
        nid = (n.attrs.get("id") or "").lower()
        if nid and (nid in FEED_IDS or "feed" in nid):
            hits.append(n)
    for n in inside:
        if n.tag == "details":
            s = summary_of(n)
            if s and "보좌 지표" in vis(s):
                hits.append(n)
    for phrase in (IND_PHRASE, CHAT_PHRASE):
        pos = drawer.sopen
        while True:
            p = text.find(phrase, pos, drawer.end)
            if p < 0:
                break
            pos = p + len(phrase)
            cont = [n for n in inside if n.start <= p < n.end]
            if any(n.tag in ("script", "style", "template") for n in cont):
                continue
            cont = [n for n in cont if n.sopen <= p]
            if cont:
                hits.append(max(cont, key=lambda n: n.start))
                break

    def climb(n):
        if n.tag == "summary" and n.parent is drawer:
            return None
        while n.parent is not None and n.parent is not drawer and n.parent.tag != "#root":
            p = n.parent
            if any(t in vis(p) for t in TOOL_PHRASES) or STEP5_ID in raw(p):
                break
            n = p
        if n is drawer or n.tag == "summary" or STEP5_ID in raw(n):
            return None
        return n

    picked = []
    for h in hits:
        c = climb(h)
        if c and c not in picked:
            picked.append(c)
    picked = [a for a in picked if not any(b is not a and contains(b, a) for b in picked)]
    picked.sort(key=lambda n: n.start)
    if not picked:
        return text, ["음성 도구함 안에서 정적 대화 피드 미발견(동적 렌더링 추정) → 런타임 구출에 위임"]

    def has_send(c):
        return "알파에게 전송" in vis(c) or bool(re.search(r"""value\s*=\s*["'][^"']*전송""", raw(c)))

    I = None
    for n in nodes:
        if n.tag in ("textarea", "input") and "알파에게" in n.attrs.get("placeholder", "") \
                and not contains(drawer, n):
            c = n
            while c.parent and c.parent.tag not in ("#root", "body", "html") \
                    and not contains(c.parent, drawer) and not has_send(c):
                c = c.parent
            if c.start >= drawer.end:
                I = c.start
            break
    where = "하단 입력창 바로 위"
    if I is None:
        p = drawer.parent
        if p and p.tag not in ("#root", "body", "html", "main", "form") and "🏛" in vis(p) \
                and "알파에게" not in raw(p):
            I, where = p.end, "도구 서랍 flex 행 바로 아래"
        else:
            I, where = drawer.end, "음성 도구함 </details> 바로 아래"

    cuts = []
    for n in picked:
        snip = text[n.start:n.end]
        head_len = n.sopen - n.start
        head = snip[:head_len]
        if "data-rgon-untrapped" not in head:
            idx = head.rstrip().rfind(">")
            if idx > 0 and head[idx - 1] == "/":
                idx -= 1
            if idx > 0:
                head = head[:idx] + ' data-rgon-untrapped="1"' + head[idx:]
        cuts.append((n.start, n.end, head + snip[head_len:]))

    zone = (f'\n<div id="{ZONE_ID}" data-rgon-untrapped="1" data-rgon-step7="zone">\n'
            + "\n".join(c[2] for c in cuts) + "\n</div>\n")

    pieces, cur, inserted = [], 0, False
    for s, e, _ in cuts:
        if not inserted and I <= s:
            pieces += [text[cur:I], zone]
            cur, inserted = I, True
        pieces.append(text[cur:s])
        cur = e
    if not inserted:
        pieces += [text[cur:I], zone]
        cur = I
    pieces.append(text[cur:])

    labels = []
    for n in picked:
        nid = n.attrs.get("id")
        tag = f"<{n.tag}{(' #' + nid) if nid else ''}>"
        v = re.sub(r"\s+", " ", vis(n)).strip()[:30]
        labels.append(f"{tag} \"{v}\"")
    return "".join(pieces), [f"정적 구출 {len(picked)}개 → {where}"] + [f"  · {x}" for x in labels]


def inject_runtime(text):
    text = re.sub(re.escape(MARK_S) + r".*?" + re.escape(MARK_E) + r"[ \t]*\r?\n?", "", text, flags=re.S)
    block = (MARK_S + "\n<style id=\"rgon-step7-style\">" + RUNTIME_CSS + "</style>\n"
             + "<script id=\"rgon-step7-script\">" + RUNTIME_JS + "</script>\n" + MARK_E + "\n")
    idx = text.lower().rfind("</body>")
    if idx >= 0:
        return text[:idx] + block + text[idx:]
    return text + "\n" + block


def detect_step2_wrappers(text):
    n = 0
    for m in re.finditer(r"<script\b[^>]*>(.*?)</script\s*>", text, re.S | re.I):
        code = m.group(1)
        if "음성 도구함" in code and re.search(r"appendChild|nextElementSibling|insertBefore|\.append\(", code):
            n += 1
    return n


def node_check(code, module=False):
    if not NODE:
        return True, "node 없음(검증 생략)"
    d = tempfile.mkdtemp(prefix="rgon_s7_")
    try:
        f = Path(d) / ("chk.mjs" if module else "chk.js")
        f.write_text(code, encoding="utf-8")
        r = subprocess.run([NODE, "--check", str(f)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        if r.returncode == 0:
            return True, ""
        lines = [x for x in (r.stderr or r.stdout or "").splitlines() if x.strip()]
        return False, (lines[-1] if lines else "syntax error")
    except Exception as e:
        return True, f"node 실행 실패: {e}"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def inline_failures(text):
    fails = []
    for i, m in enumerate(re.finditer(r"<script\b([^>]*)>(.*?)</script\s*>", text, re.S | re.I)):
        attrs, code = m.group(1), m.group(2)
        if re.search(r"\bsrc\s*=", attrs, re.I) or not code.strip():
            continue
        t = re.search(r"""\btype\s*=\s*["']?([^"'\s>]+)""", attrs, re.I)
        ttype = t.group(1).lower() if t else ""
        if ttype and ttype not in ("text/javascript", "module", "application/javascript"):
            continue
        is_mod = ttype == "module" or bool(re.search(r"(?m)^\s*(?:import\s+[\w{*'\"]|export\s+)", code))
        ok, msg = node_check(code, is_mod)
        if not ok:
            fails.append(f"script#{i}: {msg}")
    return fails


def read_html(p):
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return raw.decode(enc), ("utf-8" if enc != "cp949" else "cp949"), bom
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace"), "utf-8", bom


def write_html(p, text, enc, bom):
    try:
        data = text.encode(enc)
    except UnicodeDecodeError:
        data, bom = text.encode("utf-8"), False
    if bom and enc == "utf-8":
        data = b"\xef\xbb\xbf" + data
    p.write_bytes(data)


def process(p):
    rel = p.relative_to(BASE)
    if not p.exists():
        print(f"\n⏭️  {rel}: 파일 없음 → 건너뜀")
        return False
    print(f"\n📄 {rel}")
    text, enc, bom = read_html(p)
    dst = BACKUP_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)
    print(f"  📦 백업: {dst.relative_to(BASE)}")

    before_fail = inline_failures(text)
    base = re.sub(re.escape(MARK_S) + r".*?" + re.escape(MARK_E) + r"[ \t]*\r?\n?", "", text, flags=re.S)
    step5_before = base.count(STEP5_ID)

    new, report = static_untrap(base)
    for r in report:
        print(f"  🛟 {r}")

    # Verify STEP5_ID count BEFORE injecting RUNTIME_JS (since RUNTIME_JS itself references STEP5_ID once)
    if new.count(STEP5_ID) != step5_before:
        print(f"  ❌ #{STEP5_ID} 개수 변경 감지 → 이 파일은 저장하지 않음")
        return False

    w2 = detect_step2_wrappers(new)
    if w2:
        print(f"  🛡️ step2 재포장 의심 스크립트 {w2}개 감지 → 런타임 가드(appendChild/insertBefore/append/Observer)로 차단")
    new = inject_runtime(new)

    after_fail = inline_failures(new)
    if len(after_fail) > len(before_fail):
        print("  ❌ node --check 실패 증가 → 이 파일은 저장하지 않음")
        for f in after_fail[:5]:
            print(f"     - {f}")
        return False
    write_html(p, new, enc, bom)
    if before_fail:
        print(f"  ⚠️ 기존부터 있던 인라인 스크립트 구문 오류 {len(before_fail)}건 (step7과 무관)")
    print(f"  ✅ node --check: {'통과' if NODE else 'node 없음(생략)'} / #{STEP5_ID} 보존 ({step5_before}회 참조)")
    print("  ✅ 런타임 구출 + 세로 깨짐 방지 CSS 주입 완료")
    return True


def git_sync():
    if not shutil.which("git") or not (BASE / ".git").exists():
        print("\n⚠️ git 저장소가 아니거나 git이 없음 → 커밋/푸시 생략")
        return

    def run(*args):
        r = subprocess.run(["git", *args], cwd=str(BASE), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()

    print("\n🔁 git 동기화")
    code, out = run("add", "-A")
    print(f"  git add -A → {'OK' if code == 0 else out[:200]}")
    code, out = run("commit", "-m",
                    "fix(v6.0.8-step7): untrap chat feed from voice tools drawer & fix vertical badge")
    if code != 0 and "nothing to commit" in out:
        print("  git commit → 변경 없음")
    else:
        print(f"  git commit → {'OK' if code == 0 else out[:200]}")
    code, out = run("push", "origin", "main")
    print(f"  git push origin main → {'OK' if code == 0 else out[-300:]}")


def main():
    print("=" * 64)
    print("  🛰️ RGON Step 7 : 대화 피드 구출 & 세로 배지 깨짐 수정")
    print("=" * 64)
    print(f"  BASE : {BASE}")
    print(f"  node : {NODE or '없음 (node --check 생략)'}")

    ok, msg = node_check(RUNTIME_JS)
    if not ok:
        print(f"❌ 주입 스크립트 자체 node --check 실패: {msg}")
        sys.exit(1)
    print("  ✅ step7 런타임 스크립트 node --check 통과")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    done = sum(1 for p in TARGETS if process(p))
    print(f"\n📊 패치 완료 {done}/{len(TARGETS)}개 파일  |  백업: {BACKUP_DIR.relative_to(BASE)}")
    if done:
        git_sync()
    print("\n[STEP 7 CHAT UNTRAP COMPLETE]")


if __name__ == "__main__":
    main()
Copy