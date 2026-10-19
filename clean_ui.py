#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_TARGETS = ["dashboard/rgon_alpha_chat.html", "rgon_alpha_chat.html", "docs/rgon_alpha_chat.html"]
SW_TARGETS   = ["dashboard/sw.js", "sw.js", "docs/sw.js"]
BOOT_TARGETS = ["dashboard/pwa_bootstrap.js", "pwa_bootstrap.js", "docs/pwa_bootstrap.js"]
FUNC   = "showRealAsideControllerModal"
STAMP  = time.strftime("%Y%m%d%H%M%S")
CHECK  = "--check" in sys.argv
BACKUP = ROOT / "_backup_clean_ui" / STAMP

CONFIG = {
    "fn": FUNC,
    "links": [
        {"no": "①", "name": "1청사 퀀트",   "url": "/departments/dept_closet.html"},
        {"no": "②", "name": "3청사 미디어", "url": "/departments/dept_media.html"},
        {"no": "③", "name": "Suno 작곡창",  "url": "https://suno.com/create"},
        {"no": "④", "name": "유튜브 업로드", "url": "https://studio.youtube.com"},
        {"no": "⑤", "name": "틱톡 업로드",  "url": "https://www.tiktok.com/tiktokstudio/upload"},
    ],
    "copies": [
        {"key": "title", "label": "📋 20:30 제목 복사", "dest": "④유튜브·⑤틱톡 제목 입력칸",
         "fallback": "엄마는 나를 기다리다 밥을 식혔다 #어머니 #감동 #한걸음씩 #효도 #눈물"},
        {"key": "pin", "label": "💬 고정댓글 복사", "dest": "유튜브·틱톡 고정댓글 입력칸",
         "fallback": "엄마한테, 말 없이 이 영상만 보내세요. 오늘 밤 숙면 주파수 432Hz는 프로필에 열어두었습니다."},
        {"key": "suno", "label": "🎵 Suno 62BPM 복사", "dest": "③Suno 작곡 스타일 입력칸",
         "fallback": "Intimate Korean emotional ballad, 62 BPM, A minor, solo warm felt piano and deep cello, nostalgic, no vocals, 30s seamless loop"},
    ],
}

DEF_RE = re.compile(
    r"(?:(?:const|let|var)\s+)?(?:async\s+)?function\s+" + FUNC + r"\s*\("
    r"|(?:(?:const|let|var)\s+)?(?:window\.)?" + FUNC +
    r"\s*=\s*(?:async\s*)?(?:function\b[^{]*|\([^)]*\)\s*=>\s*|[A-Za-z_$][\w$]*\s*=>\s*)")
OLD_TEXT_RE = re.compile(r"한꺼번에\s*모두\s*열기")
INLINE_RE   = re.compile(r"<script\b(?![^>]*\bsrc\s*=)([^>]*)>(.*?)</script>[ \t]*\n?", re.I | re.S)
ANY_SCRIPT  = re.compile(r"(<script\b.*?</script>)", re.I | re.S)
EXT_RE      = re.compile(r"<script\b([^>]*?)\bsrc\s*=\s*([\"'])([^\"']+)\2([^>]*)>\s*</script>[ \t]*\n?", re.I)
OLD_BTN_RE  = re.compile(r"<(button|a)\b[^>]*>(?:(?!</\1>).)*?한꺼번에\s*모두\s*열기(?:(?!</\1>).)*?</\1>\s*", re.I | re.S)
BODY_MARK   = re.compile(r"<!-- RGON_CLEAN_UI_START -->.*?<!-- RGON_CLEAN_UI_END -->\s*", re.S)
HEAD_MARK   = re.compile(r"<!-- RGON_SW_GUARD_START -->.*?<!-- RGON_SW_GUARD_END -->\s*", re.S)
SMALL_BLOCK = 30000

def _skip_template(s, i):
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\": i += 2; continue
        if c == "`": return i
        if s.startswith("${", i):
            e = match_brace(s, i + 1)
            if e < 0: return n
            i = e + 1; continue
        i += 1
    return n

def match_brace(s, open_idx):
    depth, i, n = 0, open_idx, len(s)
    while i < n:
        c = s[i]
        if c in "'\"":
            i += 1
            while i < n and s[i] != c and s[i] != "\n":
                i += 2 if s[i] == "\\" else 1
        elif c == "`":
            i = _skip_template(s, i + 1)
        elif s.startswith("//", i):
            j = s.find("\n", i); i = n if j < 0 else j; continue
        elif s.startswith("/*", i):
            j = s.find("*/", i + 2); i = n if j < 0 else j + 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: return i
        i += 1
    return -1

def strip_defs(body, warns):
    count, pos = 0, 0
    while True:
        m = DEF_RE.search(body, pos)
        if not m: break
        ob = body.find("{", m.end() - 1 if body[m.end() - 1:m.end()] == "{" else m.end())
        cb = match_brace(body, ob) if ob >= 0 else -1
        if cb < 0:
            warns.append("옛 함수의 끝을 찾지 못해 건너뛴 정의가 있습니다")
            pos = m.end(); continue
        end = cb + 1
        tail = re.match(r"\s*;?", body[end:])
        end += tail.end() if tail else 0
        body = body[:m.start()] + body[end:]
        count += 1; pos = m.start()
    return body, count

def only_comments(s):
    return not re.sub(r"/\*.*?\*/|//[^\n]*", "", s, flags=re.S).strip()

HEAD_GUARD = """<!-- RGON_SW_GUARD_START -->
<script>
(function(){
  if(!/^(127\\.0\\.0\\.1|localhost|\\[::1\\])$/.test(location.hostname) || !("serviceWorker" in navigator)) return;
  var fake={update:function(){},unregister:function(){return Promise.resolve(true);},addEventListener:function(){},installing:null,waiting:null,active:null};
  try{ navigator.serviceWorker.register=function(){ return Promise.resolve(fake); }; }catch(e){}
  var KEY="rgon_sw_purged___STAMP__";
  Promise.all([
    navigator.serviceWorker.getRegistrations().then(function(rs){
      return Promise.all(rs.map(function(r){return r.unregister();})).then(function(){return rs.length;});
    }),
    ("caches" in window) ? caches.keys().then(function(ks){
      return Promise.all(ks.map(function(k){return caches.delete(k);})).then(function(){return ks.length;});
    }) : Promise.resolve(0)
  ]).then(function(c){
    if((c[0]||c[1]||navigator.serviceWorker.controller) && !sessionStorage.getItem(KEY)){
      sessionStorage.setItem(KEY,"1"); location.reload();
    }
  }).catch(function(){});
})();
</script>
<!-- RGON_SW_GUARD_END -->
"""

BODY_BLOCK = r"""<!-- RGON_CLEAN_UI_START -->
<style id="rgon-clean-ui-style">
#rgon-aside-modal{position:fixed;inset:0;z-index:2147483000;display:none;align-items:flex-end;justify-content:center;background:rgba(3,3,10,.64);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
#rgon-aside-modal.open{display:flex}
#rgon-aside-modal .rgon-panel{width:100%;max-width:680px;max-height:88vh;overflow:auto;box-sizing:border-box;padding:18px 18px calc(18px + env(safe-area-inset-bottom));border-radius:20px 20px 0 0;border:2px solid #d4af37;background:linear-gradient(160deg,#0f172a,#1e1b4b);color:#f3e3a6;font-family:system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;box-shadow:0 -10px 40px rgba(0,0,0,.85)}
@media(min-width:600px){#rgon-aside-modal{align-items:center}#rgon-aside-modal .rgon-panel{border-radius:20px}}
#rgon-aside-modal .rgon-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
#rgon-aside-modal .rgon-head b{font-size:15px;color:#facc15}
#rgon-aside-modal .rgon-x{background:#450a0a;border:1px solid #f87171;color:#fca5a5;border-radius:10px;padding:6px 14px;font-size:13px;font-weight:bold;cursor:pointer;font-family:inherit}
#rgon-aside-modal .rgon-cap{font-size:12px;color:#cbd5e1;margin:10px 2px 6px}
#rgon-aside-modal .rgon-row5{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
#rgon-aside-modal .rgon-row3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
#rgon-aside-modal .rgon-link,#rgon-aside-modal .rgon-copy{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;min-height:58px;padding:8px 6px;box-sizing:border-box;border-radius:12px;border:1px solid rgba(232,210,138,.35);background:rgba(255,255,255,.06);color:#f3e3a6;text-decoration:none;font-size:12.5px;font-weight:bold;line-height:1.25;text-align:center;word-break:keep-all;cursor:pointer;font-family:inherit}
#rgon-aside-modal .rgon-link .n{font-size:15px;color:#38bdf8}
#rgon-aside-modal .rgon-copy{background:rgba(232,210,138,.14);color:#fde047}
#rgon-aside-modal .rgon-link:active,#rgon-aside-modal .rgon-copy:active{transform:scale(.96)}
#rgon-aside-modal .rgon-copy.done{border-color:#3ddc84;color:#b8ffd2;background:#0f3a22}
#rgon-paste-toast{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom));transform:translate(-50%,160%);z-index:2147483600;width:calc(100% - 24px);max-width:560px;box-sizing:border-box;padding:14px 16px;border-radius:14px;background:#0f3a22;border:2px solid #3ddc84;color:#c9ffdc;font:500 13px/1.45 system-ui,sans-serif;transition:transform .28s;box-shadow:0 12px 35px rgba(0,0,0,.7)}
#rgon-paste-toast.show{transform:translate(-50%,0)}
#rgon-paste-toast.fail{background:#3a1414;border-color:#ff7b7b;color:#ffd0d0}
#rgon-paste-toast .pv{margin-top:6px;padding:8px;border-radius:8px;background:rgba(0,0,0,.35);font-size:12px;max-height:84px;overflow:auto;white-space:pre-wrap;-webkit-user-select:text;user-select:text;color:#fde047}
#rgon-paste-toast .hint{margin-top:4px;font-size:12px;opacity:.95}
</style>
<script>
(function(){
  "use strict";
  var CFG = __RGON_CFG__;
  function today(){ var d=new Date(); return d.getFullYear()+"."+String(d.getMonth()+1).padStart(2,"0")+"."+String(d.getDate()).padStart(2,"0"); }
  function fill(t){ return String(t).replace(/\{날짜\}/g, today()); }
  function sourceText(key, fallback){
    var el=document.querySelector('[data-rgon-copy="'+key+'"]');
    if(el){ var v=/^(INPUT|TEXTAREA)$/.test(el.tagName)?el.value:el.innerText; if(v&&v.trim()) return v.trim(); }
    try{ var s=localStorage.getItem("rgon_copy_"+key); if(s&&s.trim()) return s.trim(); }catch(e){}
    return fill(fallback);
  }
  function legacyCopy(text){
    return new Promise(function(ok,fail){
      var ta=document.createElement("textarea"); ta.value=text; ta.setAttribute("readonly","");
      ta.style.cssText="position:fixed;top:-1000px;opacity:0"; document.body.appendChild(ta);
      ta.select(); ta.setSelectionRange(0,text.length);
      var r=false; try{ r=document.execCommand("copy"); }catch(e){}
      ta.remove(); r?ok():fail(new Error("복사 실패"));
    });
  }
  function copyText(text){
    if(navigator.clipboard && window.isSecureContext){
      return navigator.clipboard.writeText(text).catch(function(){ return legacyCopy(text); });
    }
    return legacyCopy(text);
  }
  var toastTimer=null;
  function toast(title, preview, ok){
    var t=document.getElementById("rgon-paste-toast");
    if(!t){ t=document.createElement("div"); t.id="rgon-paste-toast"; t.setAttribute("role","status"); t.setAttribute("aria-live","polite"); document.body.appendChild(t); }
    t.className = ok===false ? "fail" : "";
    t.textContent="";
    var h=document.createElement("b"); h.textContent=title;
    var hint=document.createElement("div"); hint.className="hint";
    hint.textContent = ok===false ? "아래 문구를 길게 눌러 직접 복사해 주십시오" : "👉 지금 해당 입력칸을 클릭하고 키보드 [Ctrl + V] (또는 우클릭 ➔ 붙여넣기)를 누르세요!";
    var pv=document.createElement("div"); pv.className="pv"; pv.textContent=preview;
    t.appendChild(h); t.appendChild(hint); t.appendChild(pv);
    void t.offsetWidth; t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer=setTimeout(function(){ t.classList.remove("show"); }, ok===false?9000:5500);
  }
  function findByText(sel, words){
    return Array.prototype.filter.call(document.querySelectorAll(sel), function(el){
      var t=el.textContent||""; return words.every(function(w){ return t.indexOf(w)>-1; });
    });
  }
  function purgeOld(){
    var oldBar = document.getElementById("real-aside-action-bar");
    if(oldBar) oldBar.remove();
    findByText("button,a,[role=button]", ["한꺼번에","모두 열기"]).forEach(function(el){
      if(!el.closest("#rgon-aside-modal")) el.remove();
    });
  }
  function build(){
    var m=document.getElementById("rgon-aside-modal"); if(m) return m;
    m=document.createElement("div"); m.id="rgon-aside-modal";
    m.setAttribute("role","dialog"); m.setAttribute("aria-modal","true"); m.setAttribute("aria-label","어사이드 실전 지휘 패널");
    var p=document.createElement("div"); p.className="rgon-panel";

    var head=document.createElement("div"); head.className="rgon-head";
    var tt=document.createElement("b"); tt.textContent="💻 노트북 어사이드 실전 지휘 패널 (클린 완성본)";
    var x=document.createElement("button"); x.type="button"; x.className="rgon-x"; x.textContent="✖ 닫기"; x.onclick=hide;
    head.appendChild(tt); head.appendChild(x); p.appendChild(head);

    var c1=document.createElement("div"); c1.className="rgon-cap"; c1.textContent="① 필요한 작업 창만 골라서 바로 열기"; p.appendChild(c1);
    var r5=document.createElement("div"); r5.className="rgon-row5";
    CFG.links.forEach(function(L){
      var a=document.createElement("a"); a.className="rgon-link"; a.href=L.url; a.target="_blank"; a.rel="noopener";
      var n=document.createElement("span"); n.className="n"; n.textContent=L.no;
      var s=document.createElement("span"); s.textContent=L.name;
      a.appendChild(n); a.appendChild(s); r5.appendChild(a);
    });
    p.appendChild(r5);

    var c2=document.createElement("div"); c2.className="rgon-cap"; c2.textContent="② 원클릭 문구 복사 후 해당 창에서 [Ctrl + V] 붙여넣기"; p.appendChild(c2);
    var r3=document.createElement("div"); r3.className="rgon-row3";
    CFG.copies.forEach(function(B){
      var b=document.createElement("button"); b.type="button"; b.className="rgon-copy"; b.textContent=B.label;
      b.onclick=function(){
        var text=sourceText(B.key, B.fallback);
        copyText(text).then(function(){
          toast("✅ 복사 완료 — "+B.dest+"에 붙여넣기 하십시오", text, true);
          b.classList.add("done"); b.textContent="✅ 복사됨 (Ctrl+V)";
          setTimeout(function(){ b.classList.remove("done"); b.textContent=B.label; }, 1800);
        }).catch(function(){ toast("자동 복사가 브라우저에서 차단되었습니다", text, false); });
      };
      r3.appendChild(b);
    });
    p.appendChild(r3);

    m.appendChild(p);
    m.addEventListener("click", function(e){ if(e.target===m) hide(); });
    document.body.appendChild(m);
    return m;
  }
  function show(){ purgeOld(); build().classList.add("open"); document.documentElement.style.overflow="hidden"; }
  function hide(){ var m=document.getElementById("rgon-aside-modal"); if(m) m.classList.remove("open"); document.documentElement.style.overflow=""; }
  document.addEventListener("keydown", function(e){ if(e.key==="Escape") hide(); });

  function isVisible(el){ var r=el.getBoundingClientRect(); return r.width>0 && r.height>0; }
  function inFixed(el){ while(el && el!==document.body){ var p=getComputedStyle(el).position; if(p==="fixed"||p==="sticky") return true; el=el.parentElement; } return false; }
  function alignBadge(){
    var badges=[];
    document.querySelectorAll("body *").forEach(function(el){
      if(el.closest("#rgon-aside-modal,#rgon-paste-toast")) return;
      var t=(el.textContent||"").replace(/\s+/g," ").trim();
      if(t.length>40 || t.indexOf("터널")<0) return;
      var pos=getComputedStyle(el).position; if(pos==="fixed"||pos==="absolute") badges.push(el);
    });
    if(!badges.length) return false;
    var btn=findByText("a,button,[role=button]", ["본관","복귀"]).filter(isVisible)[0];
    badges.forEach(function(b){
      var s=b.style, imp="important";
      s.setProperty("position","fixed",imp);
      if(btn && inFixed(btn)){
        var r=btn.getBoundingClientRect();
        s.setProperty("top",Math.round(r.top)+"px",imp);
        s.setProperty("right",Math.round(innerWidth - r.left + 12)+"px",imp);
        s.setProperty("left","auto",imp); s.setProperty("bottom","auto",imp);
      }else{
        s.setProperty("top","14px",imp); s.setProperty("right","155px",imp);
      }
      s.setProperty("transform","none",imp);
      s.setProperty("font-size","11px",imp);
      s.setProperty("z-index","9990",imp);
    });
    return true;
  }
  function install(){ window[CFG.fn]=show; window.rgonCloseAsideModal=hide; }
  install();
  document.addEventListener("DOMContentLoaded", function(){ install(); purgeOld(); alignBadge(); });
  addEventListener("load", function(){ install(); purgeOld(); alignBadge(); setInterval(purgeOld, 500); });
})();
</script>
<!-- RGON_CLEAN_UI_END -->
"""

SW_CODE = """// sw.js — clean_ui.py 재생성 (버전 __STAMP__)
const VERSION = "rgon-__STAMP__";
const LOCAL = /^(127\\.0\\.0\\.1|localhost)$/.test(self.location.hostname);
self.addEventListener("install", e => { self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => caches.delete(k)));
    if (LOCAL) { await self.registration.unregister(); return; }
    await self.clients.claim();
  })());
});
"""

BOOT_GUARD = """/* RGON_LOCAL_SW_GUARD_START */
(function(){
  if(/^(127\\.0\\.0\\.1|localhost)$/.test(location.hostname) && "serviceWorker" in navigator){
    var fake={update:function(){},unregister:function(){return Promise.resolve(true);},addEventListener:function(){},installing:null,waiting:null,active:null};
    try{ navigator.serviceWorker.register=function(){ return Promise.resolve(fake); }; }catch(e){}
  }
})();
/* RGON_LOCAL_SW_GUARD_END */
"""

def backup(path):
    dst = BACKUP / path.relative_to(ROOT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)

def write(path, text):
    if CHECK: return
    backup(path)
    path.write_text(text, encoding="utf-8", newline="\n")

def patch_html(path):
    html = path.read_text(encoding="utf-8", errors="replace")
    st = {"defs": 0, "blocks": 0, "dups": 0, "btns": 0, "warns": []}
    html = BODY_MARK.sub("", html)
    html = HEAD_MARK.sub("", html)
    html = re.sub(r'<script id="rgon-master-clean-v125">.*?</script>', '', html, flags=re.S)

    def inline_repl(m):
        attrs, body = m.group(1), m.group(2)
        if not (DEF_RE.search(body) or OLD_TEXT_RE.search(body)):
            return m.group(0)
        new_body, n = strip_defs(body, st["warns"])
        st["defs"] += n
        if only_comments(new_body) or (OLD_TEXT_RE.search(new_body) and len(body) < SMALL_BLOCK):
            st["blocks"] += 1
            return ""
        return f"<script{attrs}>{new_body}</script>\n"
    html = INLINE_RE.sub(inline_repl, html)

    parts = ANY_SCRIPT.split(html)
    for i in range(0, len(parts), 2):
        parts[i], n = OLD_BTN_RE.subn("", parts[i])
        st["btns"] += n
    html = "".join(parts)

    seen = set()
    def ext_repl(m):
        pre, q, src, post = m.groups()
        clean = src.split("#")[0].split("?")[0]
        external = bool(re.match(r"^(https?:)?//|^data:", clean, re.I))
        key = clean if external else clean.rsplit("/", 1)[-1].lower()
        if key in seen:
            st["dups"] += 1
            return ""
        seen.add(key)
        if external: return m.group(0)
        return f"<script{pre}src={q}{clean}?v={STAMP}{q}{post}></script>\n"
    html = EXT_RE.sub(ext_repl, html)

    guard = HEAD_GUARD.replace("__STAMP__", STAMP)
    hm = re.search(r"<head\b[^>]*>", html, re.I)
    html = html[:hm.end()] + "\n" + guard + html[hm.end():] if hm else guard + html

    block = BODY_BLOCK.replace("__RGON_CFG__", json.dumps(CONFIG, ensure_ascii=False))
    bi = html.lower().rfind("</body>")
    html = html[:bi] + block + html[bi:] if bi >= 0 else html + block

    left_defs = sum(len(DEF_RE.findall(b)) for _, b in INLINE_RE.findall(html))
    write(path, html)
    return st, left_defs

def main():
    print(f"\n━━ 르곤-알파 독대실 정리 패치 — {STAMP} ━━")
    for rel in HTML_TARGETS:
        p = ROOT / rel
        if not p.exists(): continue
        st, left = patch_html(p)
        print(f"  ✔ {rel}: 옛 함수 {st['defs']}개 제거, 스크립트 블록 {st['blocks']}개 삭제 → 남은 옛 정의 {left}개")
    for rel in SW_TARGETS:
        p = ROOT / rel
        if p.exists():
            write(p, SW_CODE.replace("__STAMP__", STAMP)); print(f"  ✔ {rel}: 로컬 자동 해제형으로 교체")
    for rel in BOOT_TARGETS:
        p = ROOT / rel
        if not p.exists(): continue
        src = re.sub(r"/\* RGON_LOCAL_SW_GUARD_START \*/.*?/\* RGON_LOCAL_SW_GUARD_END \*/\s*", "",
                     p.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        write(p, BOOT_GUARD + src); print(f"  ✔ {rel}: 로컬 서비스워커 등록 차단 삽입")

if __name__ == "__main__":
    main()
