#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step5_fix_overlap_accordion.py
 모바일 독대실: (노란 2번) '⚡ 독대실에서 바로 분배하기' / 분배 컨트롤러 펼칠 때
 (빨간 1번) '🛰️ 6대 청사 실시간 보좌 지표' + '르곤-알파' 대화창이 가리는 현상 해결
  (A) 분배기 열림 → 1번 영역 자동 접힘 / 분배기 닫힘·⚡알파에게 전송·📋브리핑 → 자동 복귀
  (B) 1번 영역 시작점에 [🔽 숨기기] ↔ [🔼 다시 보기] 슬림 토글 바
  (C) 모바일 body/메인 컨테이너 overflow·height 보정 + 분배 패널 z-index 50 보호
 Step 4 블록(상단 7버튼 · 갈색 4분할 · ☰ 서랍)은 한 글자도 건드리지 않음
 Python 3 표준 라이브러리 전용
"""
import os
import re
import sys
import shutil
import tempfile
import datetime
import subprocess
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────
# 기본 설정
# ─────────────────────────────────────────────────────────────
ROOT_DEFAULT = Path(r"C:/Users/sangi/Downloads/shin-agent")
ROOT = ROOT_DEFAULT if ROOT_DEFAULT.is_dir() else Path.cwd()
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

HTML_TARGETS = [
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
    "rgon_alpha_audience.html",
]

S4_START = "<!-- === [RGON-STEP1-MOBILE-UI-START] === -->"
S4_END = "<!-- === [RGON-STEP1-MOBILE-UI-END] === -->"
S5_START = "<!-- === [RGON-STEP5-ACCORDION-START] === -->"
S5_END = "<!-- === [RGON-STEP5-ACCORDION-END] === -->"

COMMIT_MSG = "fix(ui): Step 5 prevent chat area from covering AI distributor panel"

REQUIRED_NEW_IDS = {"rgons5-style", "rgons5-script"}

ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.I)
S4_BLOCK_RE = re.compile(re.escape(S4_START) + r".*?" + re.escape(S4_END), re.S)
S5_BLOCK_RE = re.compile(r"\n?" + re.escape(S5_START) + r".*?" + re.escape(S5_END) + r"\n?", re.S)

# ─────────────────────────────────────────────────────────────
# Step 5 블록 (CSS + JS)
# ─────────────────────────────────────────────────────────────
S5_BODY = r"""<style id="rgons5-style">
#rgons5-toggle{display:flex;width:100%;box-sizing:border-box;margin:6px 0;padding:0 2px;position:relative;z-index:51;flex:0 0 auto}
#rgons5-toggle-btn{flex:1 1 auto;width:100%;min-width:0;white-space:nowrap!important;overflow:hidden;text-overflow:ellipsis;padding:7px 10px;border-radius:10px;border:1px dashed rgba(212,175,55,.8);background:#161b22;color:#f5d76e;font-size:12.5px;font-weight:700;line-height:1.25;cursor:pointer;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
#rgons5-toggle-btn:active{transform:scale(.98)}
body.rgons5-chat-collapsed #rgons5-toggle-btn{border-style:solid;background:#2a2410}
.rgons5-collapsed{display:none!important}
body.rgons5-dist-open .rgons5-dist-panel.rgons5-is-open{position:relative!important;z-index:50!important;margin-bottom:14px!important;max-height:none!important;overflow:visible!important}
@media (max-width:820px){
  body{min-height:100vh;min-height:100dvh!important;overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch}
  body.rgons5-dist-open,body.rgons5-chat-collapsed{height:auto!important}
  html:has(body.rgons5-dist-open),html:has(body.rgons5-chat-collapsed){height:auto!important;overflow-y:visible!important}
  body.rgons5-dist-open .rgons5-unclip,body.rgons5-chat-collapsed .rgons5-unclip{overflow:visible!important;height:auto!important;max-height:none!important;min-height:100dvh}
  body.rgons5-dist-open .rgons5-unclip .rgons5-unclip,body.rgons5-chat-collapsed .rgons5-unclip .rgons5-unclip{min-height:0}
}
</style>
<script id="rgons5-script">
(function(){
'use strict';
if(window.__rgonS5)return;window.__rgonS5=true;
function $(s,r){return (r||document).querySelector(s);}
function $$(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function txt(el){return String((el&&el.textContent)||'').replace(/\s+/g,' ').trim();}
function visible(el){return !!(el&&(el.offsetWidth||el.offsetHeight||el.getClientRects().length));}
var OURS='#rgons5-toggle,#rgons4-top,#rgons4-drawer,#rgons4-backdrop,#rgons4-toast,#rgonws-top,#rgonws-modal,#rgonws-toast';
function ours(el){return !!(el&&el.closest&&el.closest(OURS));}
function follows(a,b){return !!(a&&b&&a!==b&&(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING)&&!a.contains(b)&&!b.contains(a));}
function innermost(arr){return arr.filter(function(x){return !arr.some(function(o){return o!==x&&x.contains(o);});});}
function outermost(arr){return arr.filter(function(x){return !arr.some(function(o){return o!==x&&o.contains(x);});});}

var DIST_RE=/독대실에서\s*바로\s*분배/;
var CTRL_RE=/(4대\s*AI\s*)?분배\s*컨트롤러|AI\s*분배기/;
var IND_RE=/6대\s*청사[^\n]{0,14}지표/;
var GREET_RE=/르곤\s*-?\s*알파/;
var GREET_WORD_RE=/안녕|반갑|무엇을|대기|명령|지시를|도와|준비/;
var SEND_RE=/알파에게\s*전송|^\s*⚡?\s*전송\s*$/;
var SEND_ID_RE=/^(send|sendBtn|send-btn|sendButton|btnSend|btn-send)$/i;
var BRIEF_RE=/대화창에\s*호출/;
var CLICK_SEL='button,a,[role="button"],[onclick],[aria-expanded],[data-toggle],[data-bs-toggle]';
var FEED_SEL='#chatMessages,#chat-messages,#messages,#messageList,#message-list,#chatBox,#chat-box,#chatLog,#chat-log,#chatContainer,#chat-container,#chatArea,#chat-area,#conversation,#chatFeed,#chat-feed,[class*="messages" i],[id*="messages" i],[class*="chat-feed" i],[class*="chat-log" i]';
var LABEL_HIDE='🔽 1번 대화창·지표 숨기기 (분배창 크게 보기)';
var LABEL_SHOW='🔼 1번 대화창·지표 다시 보기';

var S={dists:[],red:[],input:null,anchor:null,collapsed:false,reason:'',prevOpen:null,ct:0};

/* ── 노란 2번: 분배기 / 컨트롤러 탐색 ── */
function resolveDist(el){
  var sum=el.closest('summary');
  if(sum&&sum.parentElement&&sum.parentElement.tagName==='DETAILS'){
    return {kind:'details',toggle:sum,content:sum.parentElement,panel:sum.parentElement};
  }
  var t=el.closest(CLICK_SEL)||el;
  var c=null,ac=t.getAttribute('aria-controls');
  if(ac)c=document.getElementById(ac);
  if(!c)c=t.nextElementSibling;
  if(!c&&t.parentElement&&t.parentElement.children.length<=2)c=t.parentElement.nextElementSibling;
  if(c&&(ours(c)||c.querySelector(OURS)))c=null;
  var panel=c||t;
  if(c&&c.parentElement===t.parentElement&&t.parentElement!==document.body&&t.parentElement.children.length<=3)panel=t.parentElement;
  return {kind:'toggle',toggle:t,content:c,panel:panel};
}
function findDists(){
  var hits=$$('summary,button,a,[role="button"],[onclick],[aria-expanded],h1,h2,h3,h4,h5,div,span,p,strong,b,label').filter(function(el){
    if(ours(el))return false;var s=txt(el);
    return s.length>0&&s.length<=160&&(DIST_RE.test(s)||CTRL_RE.test(s));
  });
  hits=innermost(hits);
  var out=[];
  hits.forEach(function(h){var d=resolveDist(h);if(!out.some(function(o){return o.toggle===d.toggle;}))out.push(d);});
  return out;
}
function isOpen(d){
  if(!d||!document.contains(d.toggle)||!visible(d.toggle))return false;
  if(d.kind==='details')return !!d.panel.open;
  var ae=d.toggle.getAttribute('aria-expanded');
  if(ae==='true')return true;if(ae==='false')return false;
  if(d.content&&visible(d.content)&&d.content.offsetHeight>30)return true;
  return /^\s*▼/.test(txt(d.toggle));
}
function inDist(el){return S.dists.some(function(d){return d.toggle.contains(el)||(d.content&&d.content.contains(el));});}

/* ── 메인 입력창 ── */
function findInput(){
  var ids=['#userInput','#chatInput','#messageInput','#msgInput','#promptInput','#prompt','#input','#question'];
  for(var i=0;i<ids.length;i++){var el=$(ids[i]);if(el&&!ours(el)&&/^(TEXTAREA|INPUT)$/.test(el.tagName))return el;}
  var best=null,by=-1;

  $$('textarea').forEach(function(t){if(ours(t)||inDist(t)||!visible(t))return;var r=t.getBoundingClientRect();if(r.bottom>by){by=r.bottom;best=t;}});
  return best;
}

/* ── 빨간 1번: 6대 청사 지표 + 대화 피드 ── */
function excluded(el){
  if(!el||el===document.body||el===document.documentElement||ours(el))return true;
  if(el.querySelector(OURS))return true;
  if(S.input&&(el===S.input||el.contains(S.input)))return true;
  return S.dists.some(function(d){return [d.toggle,d.content].some(function(x){return x&&(el.contains(x)||x.contains(el));});});
}
function climb(el,maxLv){
  var t=el,p=el.parentElement,lv=0;
  while(p&&lv<maxLv&&!excluded(p)&&p.children.length<=3){t=p;p=p.parentElement;lv++;}
  return t;
}
function afterAnchor(el){return !S.anchor||follows(S.anchor,el);}
function findIndicator(){
  var hits=$$('summary,button,a,[role="button"],[onclick],h2,h3,h4,h5,div,span,p,strong,b').filter(function(el){
    if(ours(el))return false;var s=txt(el);return s.length>0&&s.length<=120&&IND_RE.test(s);
  });
  var out=[];
  innermost(hits).forEach(function(h){
    if(!afterAnchor(h))return;
    var det=h.closest('details');
    var u=(det&&!excluded(det))?det:climb(h.closest(CLICK_SEL)||h,4);
    if(!excluded(u))out.push(u);
  });
  return out;
}
function findFeed(){
  var c=outermost($$(FEED_SEL).filter(function(el){return !excluded(el)&&afterAnchor(el);}));
  if(c.length)return [c[0]];
  var g=innermost($$('div,p,span,li,article').filter(function(el){
    if(ours(el))return false;var s=txt(el);
    return s.length>=8&&s.length<=500&&GREET_RE.test(s)&&GREET_WORD_RE.test(s)&&afterAnchor(el);
  }));
  if(!g.length)return [];
  var el=g[0],t=null,p=el;
  while(p&&!excluded(p)){
    t=p;
    if(p!==el){var cs=getComputedStyle(p);if(/(auto|scroll)/.test(cs.overflowY))break;}
    p=p.parentElement;
  }
  return t?[t]:[];
}

/* ── 토글 바 ── */
function placeBar(){
  var bar=$('#rgons5-toggle');
  if(!bar){
    bar=document.createElement('div');bar.id='rgons5-toggle';
    var b=document.createElement('button');b.type='button';b.id='rgons5-toggle-btn';bar.appendChild(b);
  }
  var ref=S.red.slice().sort(function(a,b){return follows(a,b)?-1:1;})[0];
  if(ref&&ref.parentNode){if(bar.nextElementSibling!==ref)ref.parentNode.insertBefore(bar,ref);}
  else if(S.dists.length){var p=S.dists[S.dists.length-1].panel;if(p.parentNode&&p.nextElementSibling!==bar)p.parentNode.insertBefore(bar,p.nextSibling);}
  bar.style.display=S.red.length?'':'none';
}
function apply(){
  S.red.forEach(function(el){el.classList.toggle('rgons5-collapsed',S.collapsed);});
  document.body.classList.toggle('rgons5-chat-collapsed',S.collapsed&&S.red.length>0);
  var b=$('#rgons5-toggle-btn');if(b)b.textContent=S.collapsed?LABEL_SHOW:LABEL_HIDE;
  if(S.collapsed)markUnclip();
}
function collapse(reason){if(!S.collapsed){S.collapsed=true;S.reason=reason;}apply();}
function expand(){S.collapsed=false;S.reason='';apply();}

/* ── 잘림 방지 (C) ── */
function markUnclip(){
  var nodes=S.dists.map(function(d){return d.panel;});
  nodes.forEach(function(n){var p=n&&n.parentElement;while(p&&p!==document.body&&p!==document.documentElement){p.classList.add('rgons5-unclip');p=p.parentElement;}});
}
function focusPanel(d){
  if(!d)return;var top=$('#rgons4-top');
  d.toggle.style.scrollMarginTop=((top?top.offsetHeight:0)+8)+'px';
  try{d.toggle.scrollIntoView({block:'start',behavior:'smooth'});}catch(e){d.toggle.scrollIntoView(true);}
}

/* ── 상태 변화 감지 (A) ── */
function check(){
  var open=false,first=null;
  S.dists.forEach(function(d){
    var o=isOpen(d);d.panel.classList.add('rgons5-dist-panel');d.panel.classList.toggle('rgons5-is-open',o);
    if(o){open=true;if(!first)first=d;}
  });
  document.body.classList.toggle('rgons5-dist-open',open);
  if(S.prevOpen===null){S.prevOpen=open;if(open)markUnclip();return;}
  if(open===S.prevOpen)return;
  S.prevOpen=open;
  if(open){markUnclip();collapse('auto');setTimeout(function(){focusPanel(first);},80);}
  else{expand();}
}
function bindDist(d){
  if(d.toggle.__rgons5)return;d.toggle.__rgons5=true;
  if(d.kind==='details')d.panel.addEventListener('toggle',function(){setTimeout(check,20);});
  try{
    var mo=new MutationObserver(function(){clearTimeout(S.ct);S.ct=setTimeout(check,60);});
    [d.toggle,d.content].forEach(function(n){if(n)mo.observe(n,{attributes:true,attributeFilter:['class','style','hidden','open','aria-expanded']});});
  }catch(e){}
}

/* ── 스캔 ── */
function scan(){
  S.dists=findDists();S.dists.forEach(bindDist);
  S.anchor=S.dists.length?S.dists[0].toggle:null;
  S.input=findInput();
  var old=S.red;
  S.red=outermost(findIndicator().concat(findFeed()));
  old.forEach(function(el){if(S.red.indexOf(el)<0)el.classList.remove('rgons5-collapsed');});
  placeBar();apply();check();
}

/* ── 이벤트 ── */
document.addEventListener('click',function(e){
  var t=e.target;if(!t||!t.closest)return;
  if(t.closest('#rgons5-toggle-btn')){
    e.preventDefault();
    if(S.collapsed)expand();
    else{collapse('manual');var d=S.dists.filter(isOpen)[0];if(d)setTimeout(function(){focusPanel(d);},60);}
    return;
  }
  if(t.closest('[data-quad="brief"],[data-act="brief"]')){setTimeout(expand,30);return;}
  var b=t.closest('button,a,[role="button"],[onclick],input[type="submit"],input[type="button"]');
  if(!b||ours(b))return;
  if(S.dists.some(function(d){return d.toggle===b||d.toggle.contains(t);})){setTimeout(check,80);setTimeout(check,400);return;}
  if(inDist(b))return;
  var s=txt(b)||String(b.value||'');
  if(SEND_RE.test(s)||SEND_ID_RE.test(b.id||'')||BRIEF_RE.test(s))setTimeout(expand,30);
},true);
document.addEventListener('keydown',function(e){
  if(e.key!=='Enter'||e.shiftKey||e.isComposing)return;
  var el=e.target;if(!el||el!==S.input)return;
  if(String(el.value||'').trim())setTimeout(expand,30);
},true);

function init(){
  scan();
  var to;
  try{
    new MutationObserver(function(ms){
      if(ms.every(function(m){return ours(m.target)||(m.target&&m.target.id==='rgons5-toggle');}))return;
      clearTimeout(to);to=setTimeout(scan,400);
    }).observe(document.body,{childList:true,subtree:true});
  }catch(e){}
  window.addEventListener('resize',function(){clearTimeout(to);to=setTimeout(scan,300);});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(init,120);});
else setTimeout(init,120);
})();
</script>"""

S5_BLOCK = S5_START + "\n" + S5_BODY + "\n" + S5_END

# ─────────────────────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────────────────────
def log(msg):
    print(msg)


def rel(p: Path):
    try:
        return p.relative_to(ROOT)
    except ValueError:
        return p


def read_text(p: Path):
    data = p.read_bytes()
    bom = data.startswith(b"\xef\xbb\xbf")
    for enc in ("utf-8-sig", "cp949"):
        try:
            return data.decode(enc), enc, bom
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), "utf-8-sig", bom


def write_text(p: Path, text: str, enc: str, bom: bool):
    if enc == "utf-8-sig":
        raw = text.encode("utf-8")
        if bom:
            raw = b"\xef\xbb\xbf" + raw
    else:
        raw = text.encode(enc, errors="replace")
    p.write_bytes(raw)


def backup(p: Path) -> Path:
    b = p.with_name(f"{p.name}.bak_{TS}")
    shutil.copy2(p, b)
    return b


def ensure_git_exclude():
    git_dir = ROOT / ".git"
    if not git_dir.is_dir():
        log("ℹ️ .git 폴더 없음 → exclude 설정 생략")
        return
    info = git_dir / "info"
    info.mkdir(parents=True, exist_ok=True)
    ex = info / "exclude"
    cur = ex.read_text(encoding="utf-8", errors="replace") if ex.exists() else ""
    lines = [l.strip() for l in cur.splitlines()]
    add = [pat for pat in ("*.bak*", "*.bak_*") if pat not in lines]
    if add:
        with ex.open("a", encoding="utf-8") as f:
            if cur and not cur.endswith("\n"):
                f.write("\n")
            f.write("# RGON backups\n" + "\n".join(add) + "\n")
        log(f"🛡️ .git/info/exclude 에 {add} 추가")
    else:
        log("🛡️ .git/info/exclude 백업 제외 규칙 유지 중")


NODE = shutil.which("node")


def node_check_code(code: str):
    if not NODE:
        return None, "node 미설치"
    fd, tmp = tempfile.mkstemp(suffix=".js", prefix="rgon_s5_chk_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)
        r = subprocess.run([NODE, "--check", tmp], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        return r.returncode == 0, (r.stderr or r.stdout).strip()
    except Exception as e:
        return False, str(e)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────
# HTML 패치
# ─────────────────────────────────────────────────────────────
def patch_html(p: Path):
    text, enc, bom = read_text(p)
    base = S5_BLOCK_RE.sub("\n", text) if S5_BLOCK_RE.search(text) else text
    had_s5 = base != text

    ids_before = set(ID_RE.findall(base))
    onclick_before = len(re.findall(r"\bonclick\s*=", base, re.I))
    s4_before = S4_BLOCK_RE.search(base)
    s4_text_before = s4_before.group(0) if s4_before else None
    if not s4_before:
        log(f"⚠️ [{rel(p)}] Step4 블록 없음 → Step5는 독립 동작으로 삽입 (Step4 먼저 실행 권장)")

    if s4_before:
        idx = s4_before.end()
        new = base[:idx] + "\n" + S5_BLOCK + base[idx:]
        where = "Step4 블록 직후"
    else:
        idx = base.lower().rfind("</body>")
        if idx >= 0:
            new = base[:idx] + S5_BLOCK + "\n" + base[idx:]
        else:
            new = base + "\n" + S5_BLOCK + "\n"
        where = "</body> 직전"

    ids_after = set(ID_RE.findall(new))
    missing = ids_before - ids_after
    if missing:
        log(f"❌ [{rel(p)}] 기존 id 손실 감지 → 중단: {sorted(missing)[:10]}")
        return False
    lack = REQUIRED_NEW_IDS - ids_after
    if lack:
        log(f"❌ [{rel(p)}] 신규 id 누락 → 중단: {sorted(lack)}")
        return False
    if len(re.findall(r"\bonclick\s*=", new, re.I)) < onclick_before:
        log(f"❌ [{rel(p)}] 기존 onclick 핸들러 감소 → 중단")
        return False
    s4_after = S4_BLOCK_RE.search(new)
    if s4_text_before is not None and (not s4_after or s4_after.group(0) != s4_text_before):
        log(f"❌ [{rel(p)}] Step4 블록 변형 감지 → 중단")
        return False

    m = re.search(r'<script id="rgons5-script">(.*?)</script>', new, re.S)
    ok, msg = node_check_code(m.group(1) if m else "")
    if ok is False:
        log(f"❌ [{rel(p)}] JS 문법 오류 → 중단\n{msg}")
        return False
    if ok is None:
        log(f"⚠️ node 미설치 → [{rel(p)}] 문법검사 생략")

    if new == text:
        log(f"⏭️ [{rel(p)}] 변경 없음")
        return True

    b = backup(p)
    write_text(p, new, enc, bom)
    log(f"✅ [{rel(p)}] Step5 블록 {'교체' if had_s5 else '삽입'} ({where}, "
        f"기존 id {len(ids_before)}개·onclick {onclick_before}개 보존, Step4 무변경, 백업: {b.name})")
    return True


# ─────────────────────────────────────────────────────────────
# Git 동기화
# ─────────────────────────────────────────────────────────────
def git(*args):
    r = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    print(f"$ git {' '.join(args)}  (rc={r.returncode})")
    if out:
        print("  " + out.replace("\n", "\n  "))
    return r, out


def untrack_backups():
    r, out = git("ls-files")
    if r.returncode != 0:
        return
    baks = [l for l in out.splitlines() if re.search(r"\.bak", l)]
    for i in range(0, len(baks), 50):
        git("rm", "--cached", "-q", "--", *baks[i:i + 50])
    if baks:
        log(f"🧽 추적 중이던 백업 {len(baks)}개 인덱스에서 제외")


def git_sync():
    if not (ROOT / ".git").exists():
        log("ℹ️ Git 저장소 아님 → 동기화 생략")
        return
    if not shutil.which("git"):
        log("⚠️ git 미설치 → 동기화 생략")
        return
    untrack_backups()
    git("add", "-A")
    r, out = git("commit", "-m", COMMIT_MSG)
    if r.returncode != 0 and "nothing to commit" not in out and "변경 사항 없음" not in out:
        log("⚠️ 커밋 실패 (위 로그 확인)")
    r, out = git("pull", "--rebase", "-X", "ours", "origin", "main")
    if r.returncode != 0:
        git("rebase", "--abort")
        log("❌ pull --rebase 실패 → rebase 중단, push 생략 (수동 확인 필요)")
        return
    r, out = git("push", "origin", "main")
    log("☁️ GitHub push 완료" if r.returncode == 0 else "❌ push 실패 (위 로그 확인)")


# ─────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────
def main():
    log(f"🏛️ RGON STEP5 분배창 가림 해소 패치 시작 — 루트: {ROOT}")
    ensure_git_exclude()

    ok_n = fail_n = 0
    for r in HTML_TARGETS:
        p = ROOT / r
        if not p.is_file():
            log(f"⏭️ [{r}] 없음 → 건너뜀")
            continue
        try:
            if patch_html(p):
                ok_n += 1
            else:
                fail_n += 1
        except Exception as e:
            fail_n += 1
            log(f"❌ [{r}] 예외: {e}")

    log(f"📋 결과: 성공 {ok_n} / 실패 {fail_n}")
    if fail_n:
        log("⚠️ 실패 파일은 원본 그대로 유지됩니다. 성공한 파일만 동기화합니다.")
    if ok_n:
        git_sync()
    else:
        log("ℹ️ 반영된 파일이 없어 Git 동기화 생략")

    log("🏁 완료 — 모바일 새로고침(캐시 무시) 후 [⚡ 독대실에서 바로 분배하기]를 펼쳐 "
        "1번 대화창·지표 자동 접힘과 [🔽/🔼] 토글 바를 확인하세요.")


if __name__ == "__main__":
    main()
