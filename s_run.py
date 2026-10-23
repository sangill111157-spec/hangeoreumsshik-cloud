#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step6_perfect_distributor.py
 모바일 독대실 스크린샷 3장(11:25)에서 나온 5대 결함 수리
  (수리 1) 빈 파란 화면 제거 + [💬 1번 대화창 모드 | ⚡ 2번 분배창 모드] 2-탭 스위치
           (2번 탭 → 1번 대화창·지표·하단입력바 숨김 + <details>.open = true 강제)
           (제목줄을 직접 열고 닫아도 탭 상태와 자동 동기화)
  (수리 2) 분배창 내부 순서 재배치: 템플릿/붙여넣기/지우기(3분할 1줄) → G1/G2/헌법
           → 사령관 지시문 → 발사 버튼 → 전광판(2x2 그리드)
  (수리 3) 모바일/확장 미응답 환경에서는 발사 버튼 클릭 시 자동복사 후 Genspark 방으로 이동,
           '⚠️ 확장프로그램 응답 없음' 대신 '📱 모바일 직통 발사 모드' 안내 표시
  (수리 4) 버튼 줄바꿈 정리 / (수리 5) 모드 전환 시 빈 공간·배너 잔재 제거
 Step 4 블록(상단 7버튼 · 갈색 4분할 · ☰ 서랍)은 한 글자도 건드리지 않음
 Step 5 블록(min-height 원인)은 Step 6 블록으로 대체
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
S6_START = "<!-- === [RGON-STEP6-DISTRIBUTOR-START] === -->"
S6_END = "<!-- === [RGON-STEP6-DISTRIBUTOR-END] === -->"

COMMIT_MSG = "fix(ui): Step 6 fix blue blank screen + reorder distributor input first + mobile Genspark launch"

REQUIRED_NEW_IDS = {"rgons6-style", "rgons6-script"}

ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.I)
ONCLICK_RE = re.compile(r"\bonclick\s*=", re.I)
S4_BLOCK_RE = re.compile(re.escape(S4_START) + r".*?" + re.escape(S4_END), re.S)
S5_BLOCK_RE = re.compile(r"\n?" + re.escape(S5_START) + r".*?" + re.escape(S5_END) + r"\n?", re.S)
S6_BLOCK_RE = re.compile(r"\n?" + re.escape(S6_START) + r".*?" + re.escape(S6_END) + r"\n?", re.S)

# ─────────────────────────────────────────────────────────────
# Step 6 블록 (CSS + JS)
# ─────────────────────────────────────────────────────────────
S6_BODY = r"""<style id="rgons6-style">
#rgons5-toggle{display:none!important}
.rgons5-unclip{min-height:0!important}
#rgons6-tabs{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px;width:100%;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif}
#rgons6-tabs.rgons6-solo{position:sticky;top:0;z-index:9000;background:rgba(13,17,23,.97);padding:6px}
#rgons6-tabs button{min-width:0;white-space:nowrap!important;overflow:hidden;text-overflow:ellipsis;padding:8px 4px;border-radius:10px;border:1px solid #30363d;background:#0f141b;color:#8b949e;font-size:12px;font-weight:700;line-height:1.2;cursor:pointer;font-family:inherit;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
#rgons6-tabs button:active{transform:scale(.97)}
#rgons6-tabs button.on[data-mode="chat"]{border-color:#58a6ff;background:#0c2d48;color:#cde6ff;box-shadow:inset 0 -2px 0 #58a6ff}
#rgons6-tabs button.on[data-mode="dist"]{border-color:#d4af37;background:#2a2410;color:#f5d76e;box-shadow:inset 0 -2px 0 #d4af37}
#rgons6-tabs .s{display:none}
@media (max-width:430px){#rgons6-tabs .f{display:none}#rgons6-tabs .s{display:inline}}
.rgons6-off,.rgons6-empty,.rgons6-warn-off{display:none!important}
.rgons6-dist:not([open]){min-height:0!important;height:auto!important;flex:0 0 auto!important}
body.rgons6-mode-dist .rgons6-dist{position:relative!important;z-index:50!important;margin-bottom:16px!important;max-height:none!important;overflow:visible!important;min-height:0!important;height:auto!important;flex:0 0 auto!important}
body.rgons6-mode-dist .rgons6-unclip{overflow:visible!important;height:auto!important;max-height:none!important;min-height:0!important}
@media (max-width:820px){
  body.rgons6-mode-dist{height:auto!important;min-height:100vh;min-height:100dvh;overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch}
  html:has(body.rgons6-mode-dist){height:auto!important;overflow-y:visible!important}
}
.rgons6-order{display:flex;flex-direction:column;gap:8px;margin:8px 0;width:100%;box-sizing:border-box}
.rgons6-tools,.rgons6-grow{display:grid;gap:6px;width:100%;box-sizing:border-box}
.rgons6-tools>*,.rgons6-grow>*{min-width:0!important;width:100%!important;max-width:100%!important;margin:0!important;white-space:nowrap!important;overflow:hidden;text-overflow:ellipsis;box-sizing:border-box;font-size:12px!important;word-break:keep-all}
textarea.rgons6-cmd{min-height:110px!important;height:130px!important;max-height:45vh!important;width:100%!important;box-sizing:border-box;resize:vertical}
.rgons6-launch button,.rgons6-launch a{white-space:nowrap!important;word-break:keep-all}
.rgons6-grid2{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
.rgons6-grid2>:not(.rgons6-card){grid-column:1/-1}
.rgons6-card{min-width:0!important;width:auto!important;margin:0!important;min-height:0!important;max-height:200px;overflow:auto;font-size:12px;box-sizing:border-box}
.rgons6-card textarea{min-height:56px!important;height:72px!important}
#rgons6-direct-note{margin:6px 0;padding:7px 10px;border-radius:10px;border:1px solid #2ea043;background:#0f2a17;color:#7ee787;font-size:12px;line-height:1.35;font-family:inherit}
#rgons6-toast{position:fixed;left:50%;bottom:92px;transform:translateX(-50%) translateY(16px);background:#161b22;color:#f5d76e;border:1px solid #d4af37;padding:8px 14px;border-radius:999px;font-size:13px;z-index:10003;opacity:0;pointer-events:none;transition:.2s;white-space:nowrap;max-width:92vw;overflow:hidden;text-overflow:ellipsis}
#rgons6-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
#rgons6-sheet{position:fixed;inset:0;z-index:10002;background:rgba(0,0,0,.55);display:none;align-items:flex-end;justify-content:center}
#rgons6-sheet.open{display:flex}
.rgons6-sheet-box{width:100%;max-width:560px;background:#0d1117;border:1px solid rgba(212,175,55,.5);border-radius:16px 16px 0 0;padding:12px 12px calc(12px + env(safe-area-inset-bottom));font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif}
.rgons6-sheet-t{color:#f5d76e;font-weight:700;font-size:14px;margin-bottom:4px}
.rgons6-sheet-n{color:#8b949e;font-size:11.5px;margin-bottom:8px}
.rgons6-sheet-g{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-bottom:8px}
.rgons6-sheet-g a{display:block;text-align:center;white-space:nowrap;padding:10px 4px;border-radius:10px;border:1px solid #58a6ff;background:#0c2d48;color:#cde6ff;font-weight:700;font-size:13px;text-decoration:none}
.rgons6-sheet-g a.done{opacity:.55;border-style:dashed}
.rgons6-sheet-x{width:100%;padding:9px;border-radius:10px;border:1px solid #30363d;background:#161b22;color:#e6edf3;font-size:13px;cursor:pointer}
</style>
<script id="rgons6-script">
(function(){
'use strict';
if(window.__rgonS6)return;window.__rgonS6=true;
var LS={get:function(k,d){try{var v=localStorage.getItem(k);return v==null?(d||''):v;}catch(e){return d||'';}}};
var DEFAULT_URL='https://www.genspark.ai/agents';
var NAMES={rgon:'🔵 르곤',claude:'🧠 Claude',gpt:'⚡ GPT',grok:'🎯 Grok'};
function $(s,r){return (r||document).querySelector(s);}
function $$(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function txt(el){return String((el&&el.textContent)||'').replace(/\s+/g,' ').trim();}
function btxt(b){return txt(b)||String((b&&b.value)||'');}
function visible(el){return !!(el&&(el.offsetWidth||el.offsetHeight||el.getClientRects().length));}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
var OURS='#rgons6-tabs,#rgons6-sheet,#rgons6-toast,#rgons6-direct-note,#rgons4-top,#rgons4-drawer,#rgons4-backdrop,#rgons4-toast,#rgons5-toggle,#rgonws-top,#rgonws-modal,#rgonws-toast';
function ours(el){return !!(el&&el.closest&&el.closest(OURS));}
function innermost(a){return a.filter(function(x){return !a.some(function(o){return o!==x&&x.contains(o);});});}
function outermost(a){return a.filter(function(x){return !a.some(function(o){return o!==x&&o.contains(x);});});}
function lca(arr){if(!arr.length)return null;var a=arr[0];while(a&&!arr.every(function(x){return a.contains(x);}))a=a.parentElement;return a;}
var BTN='button,a,[role="button"],input[type="button"],input[type="submit"]';
var CLICK='button,a,[role="button"],[onclick],[aria-expanded],[data-toggle],[data-bs-toggle]';
var RE={
  dist:/독대실에서\s*바로\s*분배/,ctrl:/(4대\s*AI\s*)?분배\s*컨트롤러/,
  tpl:/지시문\s*템플릿/,paste:/새로\s*붙여넣기/,clear:/전체\s*지우기/,
  g:/(^|[^A-Za-z0-9])G[12]([^0-9]|$)|헌법/,
  solo:/단독/,sel:/선택\s*발사|체크\s*선택/,all:/전체\s*발사/,
  board:/교차\s*검증\s*집결\s*전광판|집결\s*전광판/,
  warn:/확장\s*프로그램\s*응답\s*없음/,
  ind:/6대\s*청사[^\n]{0,14}지표/,greet:/르곤\s*-?\s*알파/,greetW:/안녕|반갑|무엇을|대기|명령|지시를|도와|준비/,
  send:/알파에게\s*전송/,sendId:/^(send|sendBtn|send-btn|sendButton|btnSend|btn-send)$/i,brief:/대화창에\s*호출/
};
var FEED_SEL='#chatMessages,#chat-messages,#messages,#messageList,#message-list,#chatBox,#chat-box,#chatLog,#chat-log,#chatContainer,#chat-container,#chatArea,#chat-area,#conversation,#chatFeed,#chat-feed,[class*="messages" i],[id*="messages" i],[class*="chat-feed" i],[class*="chat-log" i]';
var S={d:null,mode:null,red:[],input:null,ta:null,launchUnit:null,warnSeen:false,lastText:'',st:0};

function toast(m,ms){var t=$('#rgons6-toast');if(!t){t=document.createElement('div');t.id='rgons6-toast';document.body.appendChild(t);}t.textContent=m;t.classList.add('show');clearTimeout(toast._t);toast._t=setTimeout(function(){t.classList.remove('show');},ms||2200);}
function setVal(el,v){
  if(!el)return;
  var proto=el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
  var d=Object.getOwnPropertyDescriptor(proto,'value');
  if(d&&d.set)d.set.call(el,v);else el.value=v;
  el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));
}
function legacy(s){try{var ta=document.createElement('textarea');ta.value=s;ta.setAttribute('readonly','');ta.style.cssText='position:fixed;left:-9999px;top:0;opacity:0';document.body.appendChild(ta);ta.select();ta.setSelectionRange(0,ta.value.length);var ok=document.execCommand('copy');ta.remove();return ok;}catch(e){return false;}}
function copyText(s){if(navigator.clipboard&&window.isSecureContext){return navigator.clipboard.writeText(s).then(function(){return true;},function(){return legacy(s);});}return Promise.resolve(legacy(s));}
function readClip(){if(navigator.clipboard&&navigator.clipboard.readText)return navigator.clipboard.readText();return Promise.reject(new Error('unsupported'));}
function clipFail(){alert('클립보드 읽기 권한이 막혀 있습니다.\n\n지시문 칸을 길게 눌러 [붙여넣기]를 선택하거나,\n사이트 설정에서 클립보드 권한을 허용해 주세요.\n(HTTPS 또는 localhost 에서만 동작)');}

/* ── 노란 2번 분배창 탐색 ── */
function findDistBy(re){
  var sums=$$('summary').filter(function(s){return !ours(s)&&re.test(txt(s))&&s.parentElement&&s.parentElement.tagName==='DETAILS';});
  if(sums.length){var s=sums[0];return {kind:'details',toggle:s,panel:s.parentElement,content:s.parentElement};}
  var hits=innermost($$('button,a,[role="button"],[onclick],[aria-expanded],h2,h3,h4,div,span,strong,b').filter(function(el){if(ours(el))return false;var x=txt(el);return x.length>0&&x.length<=160&&re.test(x);}));
  if(!hits.length)return null;
  var t=hits[0].closest(CLICK)||hits[0];
  var c=null,ac=t.getAttribute('aria-controls');if(ac)c=document.getElementById(ac);
  if(!c)c=t.nextElementSibling;
  if(!c&&t.parentElement&&t.parentElement.children.length<=2)c=t.parentElement.nextElementSibling;
  if(c&&(ours(c)||c.querySelector(OURS)))c=null;
  var panel=(c&&c.parentElement===t.parentElement&&t.parentElement!==document.body)?t.parentElement:(c||t);
  return {kind:'toggle',toggle:t,panel:panel,content:c};
}
function findDist(){return findDistBy(RE.dist)||findDistBy(RE.ctrl);}
function inDist(el){return !!(S.d&&el&&(S.d.panel.contains(el)||(S.d.content&&S.d.content.contains(el))));}
function distQ(sel){var r=[];if(!S.d)return r;[S.d.panel,S.d.content].forEach(function(n){if(n)$$(sel,n).forEach(function(x){if(r.indexOf(x)<0)r.push(x);});});return r;}
function isOpen(d){
  if(!d||!document.contains(d.toggle))return false;
  if(d.kind==='details')return !!d.panel.open;
  var ae=d.toggle.getAttribute('aria-expanded');if(ae==='true')return true;if(ae==='false')return false;
  return !!(d.content&&visible(d.content)&&d.content.offsetHeight>30);
}
function openDist(d){if(!d)return;if(d.kind==='details'){if(!d.panel.open)d.panel.open=true;}else if(!isOpen(d)){d.toggle.click();}}
function closeDist(d){if(!d)return;if(d.kind==='details'){if(d.panel.open)d.panel.open=false;}else if(isOpen(d)){d.toggle.click();}}
function bindDist(d){
  if(d.panel.__rgons6b)return;d.panel.__rgons6b=true;
  if(d.kind==='details'){d.panel.addEventListener('toggle',function(){setTimeout(sync,10);});return;}
  try{var mo=new MutationObserver(function(){clearTimeout(S.st);S.st=setTimeout(sync,60);});
    [d.toggle,d.content].forEach(function(n){if(n)mo.observe(n,{attributes:true,attributeFilter:['style','hidden','open','aria-expanded']});});}catch(e){}
}

/* ── 메인 입력창 ── */
function findInput(){
  if(S.input&&document.contains(S.input)&&S.input.closest('.rgons6-off'))return S.input;
  var ids=['#userInput','#chatInput','#messageInput','#msgInput','#promptInput','#prompt','#input','#question'];
  for(var i=0;i<ids.length;i++){var el=$(ids[i]);if(el&&!ours(el)&&!inDist(el)&&/^(TEXTAREA|INPUT)$/.test(el.tagName))return el;}
  var best=null,by=-1;

  $$('textarea').forEach(function(t){
    if(ours(t)||inDist(t))return;
    if(!visible(t)&&!t.closest('.rgons6-off'))return;
    var r=t.getBoundingClientRect();if(r.bottom>by){by=r.bottom;best=t;}
  });
  return best;
}

/* ── 빨간 1번: 지표 + 대화 피드 + 하단 입력바 ── */
function excluded(el){
  if(!el||el===document.body||el===document.documentElement||ours(el))return true;
  if(el.querySelector(OURS))return true;
  if(S.d&&[S.d.panel,S.d.toggle,S.d.content].some(function(x){return x&&(el.contains(x)||x.contains(el));}))return true;
  return false;
}
function climb(el,maxLv){var t=el,p=el.parentElement,lv=0;while(p&&lv<maxLv&&!excluded(p)&&p.children.length<=3){t=p;p=p.parentElement;lv++;}return t;}
function findIndicator(){
  var hits=innermost($$('summary,button,a,[role="button"],[onclick],h2,h3,h4,h5,div,span,p,strong,b').filter(function(el){if(ours(el))return false;var s=txt(el);return s.length>0&&s.length<=120&&RE.ind.test(s);}));
  var out=[];
  hits.forEach(function(h){if(inDist(h))return;var det=h.closest('details');var u=(det&&!excluded(det))?det:climb(h.closest(CLICK)||h,4);if(!excluded(u))out.push(u);});
  return out;
}
function findFeed(){
  var c=outermost($$(FEED_SEL).filter(function(el){return !excluded(el)&&!inDist(el);}));
  if(c.length)return [c[0]];
  var g=innermost($$('div,p,span,li,article').filter(function(el){if(ours(el)||inDist(el))return false;var s=txt(el);return s.length>=8&&s.length<=500&&RE.greet.test(s)&&RE.greetW.test(s);}));
  if(!g.length)return [];
  var el=g[0],t=null,p=el;
  while(p&&!excluded(p)){t=p;if(p!==el&&/(auto|scroll)/.test(getComputedStyle(p).overflowY))break;p=p.parentElement;}
  return t?[t]:[];
}
function inputRow(inp,core){
  if(!inp||inDist(inp))return null;
  var t=inp,p=inp.parentElement,lv=0;
  while(p&&lv<5&&!excluded(p)&&!core.some(function(r){return p.contains(r);})&&txt(p).length<300){t=p;p=p.parentElement;lv++;}
  return t;
}
function computeRed(){
  var core=findIndicator().concat(findFeed());
  var row=inputRow(S.input,core);
  S.red=outermost(core.concat(row?[row]:[])).filter(function(el){return !excluded(el)||el===row;});
}

/* ── 분배창 내부 재배치 (수리 2·4) ── */
function keyBtns(root,re){return innermost($$(BTN,root).filter(function(b){return !ours(b)&&re.test(btxt(b));}));}
function pickTa(root,boardT){
  var best=null,bs=-1e9;

  $$('textarea',root).forEach(function(t){
    if(ours(t))return;var s=0,h=(t.placeholder||'')+' '+(t.id||'')+' '+(t.name||'');
    if(/사령관|지시문|지시|command|prompt/i.test(h))s+=100;
    if(boardT){var p=t.parentElement,lv=0;while(p&&p!==root&&lv<4){if(p.contains(boardT)){s-=60;break;}p=p.parentElement;lv++;}}
    if(t.readOnly)s-=40;s+=Math.min(t.rows||2,10);
    if(s>bs){bs=s;best=t;}
  });
  return best;
}
function unitOf(el,content,avoid){
  var t=el,p=el.parentElement;
  while(p&&p!==content&&content.contains(p)&&!avoid.some(function(a){return a&&!t.contains(a)&&p.contains(a);})){t=p;p=p.parentElement;}
  return t;
}
function isEmpty(el){return !txt(el)&&!el.querySelector('input,textarea,select,button,img,canvas,svg,iframe,video,a');}
function markEmpty(p,content){while(p&&p!==content&&content.contains(p)){if(isEmpty(p))p.classList.add('rgons6-empty');else break;p=p.parentElement;}}
var AI_RE=/르곤|rgon|claude|클로드|gpt|grok/i;
function gridify(board){
  var found=null;
  [board].concat($$('*',board)).some(function(el){
    var kids=Array.prototype.filter.call(el.children,function(k){return AI_RE.test(txt(k).slice(0,60));});
    if(kids.length>=3&&kids.length<=8){found=el;kids.forEach(function(k){k.classList.add('rgons6-card');});return true;}
    return false;
  });
  if(found)found.classList.add('rgons6-grid2');
}
function reorder(){
  var d=S.d;if(!d)return;var content=d.content;
  if(!content){S.ta=S.ta&&document.contains(S.ta)?S.ta:pickTa(d.panel,null);return;}
  var ex=content.__rgons6Order;
  if(ex&&content.contains(ex)){
    S.ta=(content.__rgons6Ta&&document.contains(content.__rgons6Ta))?content.__rgons6Ta:pickTa(content,null);
    S.launchUnit=content.__rgons6Launch||null;return;
  }
  var tpl=$$('select',content).filter(function(s){return !ours(s)&&Array.prototype.some.call(s.options,function(o){return RE.tpl.test(o.text);});})[0]||keyBtns(content,RE.tpl)[0]||null;
  var paste=keyBtns(content,RE.paste)[0]||null;
  var clear=keyBtns(content,RE.clear)[0]||null;
  var gs=keyBtns(content,RE.g);
  var boardT=innermost($$('*',content).filter(function(el){if(ours(el))return false;var s=txt(el);return s.length>0&&s.length<=80&&RE.board.test(s);}))[0]||null;
  var ta=pickTa(content,boardT);
  var launch=keyBtns(content,RE.solo).concat(keyBtns(content,RE.sel),keyBtns(content,RE.all));
  if(!ta&&!launch.length){S.ta=null;return;}
  var order=document.createElement('div');order.className='rgons6-order';
  content.insertBefore(order,d.kind==='details'?d.toggle.nextSibling:content.firstChild);
  content.__rgons6Order=order;
  var parents=[];
  function mv(el,into){if(!el||el===content||el.contains(order)||order.contains(el))return false;if(el.parentElement)parents.push(el.parentElement);into.appendChild(el);return true;}
  var top=[tpl,paste,clear].filter(Boolean);
  if(top.length){var tr=document.createElement('div');tr.className='rgons6-tools';tr.style.gridTemplateColumns=top.length===3?'minmax(0,1.3fr) minmax(0,1fr) minmax(0,1fr)':'repeat('+top.length+',minmax(0,1fr))';order.appendChild(tr);top.forEach(function(x){mv(x,tr);});}
  if(gs.length){var gr=document.createElement('div');gr.className='rgons6-grow';gr.style.gridTemplateColumns='repeat('+Math.min(gs.length,3)+',minmax(0,1fr))';order.appendChild(gr);gs.forEach(function(x){mv(x,gr);});}
  var lc=null;
  if(launch.length){
    var cbs=$$('input[type="checkbox"]',content).filter(function(c){return !order.contains(c)&&!!aiOf(cbLabel(c));});
    var bad=function(x){return !x||x===content||!content.contains(x)||order.contains(x)||(ta&&x.contains(ta))||(boardT&&x.contains(boardT));};
    lc=lca(launch.concat(cbs));if(bad(lc))lc=lca(launch);if(bad(lc))lc=null;
  }
  if(ta){ta.classList.add('rgons6-cmd');mv(unitOf(ta,content,[boardT,order].concat(launch)),order);}
  var lu=null;
  if(lc){lu=unitOf(lc,content,[ta,boardT,order]);lu.classList.add('rgons6-launch');mv(lu,order);}
  if(boardT){var bu=unitOf(boardT,content,[ta,order].concat(launch));if(mv(bu,order))gridify(bu);}
  parents.forEach(function(p){markEmpty(p,content);});
  content.__rgons6Ta=ta;content.__rgons6Launch=lu;S.ta=ta;S.launchUnit=lu;
}

/* ── 모바일 직통 발사 (수리 3) ── */
function aiOf(s){s=String(s||'');if(/르곤|rgon/i.test(s))return 'rgon';if(/claude|클로드/i.test(s))return 'claude';if(/grok|그록/i.test(s))return 'grok';if(/gpt|지피티/i.test(s))return 'gpt';return null;}
function cbLabel(cb){
  var l=cb.closest('label');
  if(!l&&cb.id){try{l=document.querySelector('label[for="'+(window.CSS&&CSS.escape?CSS.escape(cb.id):cb.id)+'"]');}catch(e){}}
  var s=(l?txt(l):'')+' '+(cb.value||'')+' '+(cb.name||'')+' '+(cb.id||'');
  if(!l&&cb.parentElement)s+=' '+txt(cb.parentElement).slice(0,40);
  return s;
}
function checkedTargets(){var out=[];distQ('input[type="checkbox"]').forEach(function(c){if(!c.checked)return;var k=aiOf(cbLabel(c));if(k&&out.indexOf(k)<0)out.push(k);});return out;}
function urlOf(k){return String(LS.get('rgon_url_'+k,'')).trim()||DEFAULT_URL;}
function extAlive(){var d=document.documentElement;try{return !!(window.__RGON_OMNI_READY||window.__rgonOmniReady||window.__rgonExtReady||d.hasAttribute('data-rgon-omni')||d.hasAttribute('data-rgon-ext')||d.hasAttribute('data-omni-link'));}catch(e){return false;}}
function isMobile(){return /Android|iPhone|iPad|iPod|Mobile|SamsungBrowser/i.test(navigator.userAgent||'')||(!!window.matchMedia&&matchMedia('(pointer:coarse)').matches&&window.innerWidth<900);}
function directMode(){var f=LS.get('rgon_direct_launch','');if(f==='1')return true;if(f==='0')return false;if(extAlive())return false;return isMobile()||S.warnSeen;}
function distText(){
  var v=S.ta?String(S.ta.value||'').trim():'';if(v)return v;
  var i=S.input?String(S.input.value||'').trim():'';return i||String(LS.get('rgon_loaded_directive','')).trim();
}
function openSheet(targets,ok,n){
  var sh=$('#rgons6-sheet');if(!sh){sh=document.createElement('div');sh.id='rgons6-sheet';document.body.appendChild(sh);}
  sh.innerHTML='<div class="rgons6-sheet-box"><div class="rgons6-sheet-t">🚀 순차 발사 — '+(n?(ok?(n+'자 클립보드 복사 완료'):'⚠️ 자동복사 실패'):'지시문 없음')+'</div>'+
    '<div class="rgons6-sheet-n">버튼마다 새 탭에서 해당 AI 방이 열립니다. 각 방에서 붙여넣기 후 전송하세요. (누를 때마다 지시문 재복사)</div>'+
    '<div class="rgons6-sheet-g">'+targets.map(function(k){return '<a target="_blank" rel="noopener" data-k="'+k+'" href="'+esc(urlOf(k))+'">'+NAMES[k]+' 열기</a>';}).join('')+'</div>'+
    '<button type="button" class="rgons6-sheet-x" data-close="1">✕ 닫기</button></div>';
  sh.classList.add('open');
}
function launch(kind,label){
  var text=distText();S.lastText=text;
  var targets=kind==='solo'?[aiOf(label)]:kind==='all'?['rgon','claude','gpt','grok']:checkedTargets();
  targets=targets.filter(Boolean);
  if(!targets.length){toast('🎯 발사 대상 AI를 체크하세요');return;}
  var p=text?copyText(text):Promise.resolve(false);
  if(targets.length===1){
    var k=targets[0];
    p.then(function(ok){
      toast(text?(ok?('📋 '+text.length+'자 자동복사 → '+NAMES[k]+' 이동'):'⚠️ 자동복사 실패 — 이동 후 수동 붙여넣기'):('➡️ '+NAMES[k]+' 방으로 이동 (지시문 없음)'),1500);
      setTimeout(function(){window.location.href=urlOf(k);},(text&&!ok)?1300:450);
    });
    return;
  }
  p.then(function(ok){openSheet(targets,ok,text.length);});
}
function distPaste(){
  readClip().then(function(c){
    if(!c){toast('📭 클립보드가 비어 있습니다');return;}
    if(!S.ta){toast('사령관 지시문 칸을 찾지 못했습니다');return;}
    setVal(S.ta,c);S.ta.focus();toast('📋 '+c.length+'자 붙여넣기 완료');
  }).catch(clipFail);
}
function clearBoard(){

  $$('.rgons6-card').forEach(function(card){

    $$('textarea,input[type="text"]',card).forEach(function(x){setVal(x,'');});

    $$('pre,[class*="result" i],[class*="output" i],[class*="answer" i],[id*="result" i],[id*="output" i],[id*="answer" i]',card).forEach(function(x){if(!x.querySelector('[id]'))x.textContent='';});
  });
}
function distClear(){
  if(S.ta&&String(S.ta.value||'').trim()){
    if(!confirm('사령관 지시문과 전광판을 모두 비울까요?'))return;
    setVal(S.ta,'');
  }
  clearBoard();toast('🗑️ 지시문·전광판 비움');
}

/* ── 경고 배너 → 모바일 안내 교체 ── */
function warnUnits(){
  var ws=innermost($$('div,p,span,small,strong,b,li,em').filter(function(el){if(ours(el))return false;var s=txt(el);return s.length>0&&s.length<=220&&RE.warn.test(s);}));
  return ws.map(function(w){
    var t=w,p=w.parentElement;
    while(p&&p!==document.body&&!(S.d&&(p===S.d.panel||p===S.d.content))&&!p.querySelector('textarea,select,.rgons6-order')&&p.querySelectorAll(BTN).length<=1&&txt(p).length<=txt(t).length+24){t=p;p=p.parentElement;}
    return t;
  });
}
function handleWarn(){
  var units=warnUnits();S.warnSeen=units.length>0;
  var direct=directMode();

  $$('.rgons6-warn-off').forEach(function(u){if(!direct||units.indexOf(u)<0)u.classList.remove('rgons6-warn-off');});
  if(direct)units.forEach(function(u){u.classList.add('rgons6-warn-off');});
  var note=$('#rgons6-direct-note');
  if(direct&&S.d){
    if(!note){note=document.createElement('div');note.id='rgons6-direct-note';note.textContent='📱 모바일 직통 발사 모드 활성 (클릭 시 지시문 자동 복사 후 Genspark 채팅방으로 이동)';}
    var ref=(S.launchUnit&&document.contains(S.launchUnit))?S.launchUnit:(units[0]||null);
    if(ref&&ref.parentNode){if(ref.nextSibling!==note)ref.parentNode.insertBefore(note,ref.nextSibling);}
    else{var host=S.d.content||S.d.panel;var o=host.__rgons6Order;
      if(o&&host.contains(o)){if(note.parentNode!==o)o.appendChild(note);}
      else if(note.parentNode!==host)host.appendChild(note);}
    note.style.display='';
  }else if(note){note.style.display='none';}
}

/* ── 모드 (수리 1·5) ── */
function ensureTabs(){
  var bar=$('#rgons6-tabs');
  if(!bar){
    bar=document.createElement('div');bar.id='rgons6-tabs';
    bar.innerHTML='<button type="button" data-mode="chat"><span class="f">💬 1번: 알파 1:1 대화창 모드</span><span class="s">💬 1번 알파 대화창</span></button>'+
                  '<button type="button" data-mode="dist"><span class="f">⚡ 2번: 4대 AI 지시·분배창 모드</span><span class="s">⚡ 2번 AI 지시·분배</span></button>';
  }
  var quad=$('#rgons4-quad'),top=$('#rgons4-top');
  if(quad&&quad.parentNode){bar.classList.remove('rgons6-solo');if(quad.nextElementSibling!==bar)quad.parentNode.insertBefore(bar,quad.nextSibling);}
  else if(top){bar.classList.remove('rgons6-solo');if(bar.parentNode!==top)top.appendChild(bar);}
  else{bar.classList.add('rgons6-solo');if(document.body.firstElementChild!==bar)document.body.insertBefore(bar,document.body.firstChild);}
}
function applyMode(m){
  S.mode=m;var dist=(m==='dist');var B=document.body.classList;
  B.toggle('rgons6-mode-dist',dist);B.toggle('rgons6-mode-chat',!dist);

  $$('.rgons6-off').forEach(function(el){if(!dist||S.red.indexOf(el)<0)el.classList.remove('rgons6-off');});
  if(dist)S.red.forEach(function(el){el.classList.add('rgons6-off');});

  $$('#rgons6-tabs [data-mode]').forEach(function(b){var on=b.getAttribute('data-mode')===m;b.classList.toggle('on',on);b.setAttribute('aria-pressed',on?'true':'false');});

  $$('.rgons6-unclip').forEach(function(el){el.classList.remove('rgons6-unclip');});
  if(dist&&S.d){var p=S.d.panel.parentElement;while(p&&p!==document.body&&p!==document.documentElement){p.classList.add('rgons6-unclip');p=p.parentElement;}}
}
function focusDist(){
  if(!S.d)return;var top=$('#rgons4-top')||$('#rgons6-tabs');var el=S.d.toggle;
  el.style.scrollMarginTop=((top?top.offsetHeight:0)+6)+'px';
  try{el.scrollIntoView({block:'start',behavior:'smooth'});}catch(e){el.scrollIntoView(true);}
}
function switchMode(m){
  if(!S.d)scan();
  if(m==='dist'){
    if(!S.d){toast('⚡ 분배창을 찾지 못했습니다');applyMode('chat');return;}
    reorder();openDist(S.d);S.input=findInput();computeRed();applyMode('dist');handleWarn();
    setTimeout(focusDist,90);
  }else{
    if(S.d)closeDist(S.d);applyMode('chat');
    try{window.scrollTo({top:0,behavior:'smooth'});}catch(e){window.scrollTo(0,0);}
  }
}
function sync(){
  if(!S.d){if(S.mode!=='chat')applyMode('chat');return;}
  var want=isOpen(S.d)?'dist':'chat';
  if(want===S.mode)return;
  if(want==='dist'){reorder();computeRed();}
  applyMode(want);
  if(want==='dist')setTimeout(focusDist,90);
}

/* ── 스캔 ── */
function scan(){
  ensureTabs();
  var d=findDist();
  if(d){if(!S.d||S.d.toggle!==d.toggle||!document.contains(S.d.panel)){S.d=d;bindDist(d);}}
  else S.d=null;
  if(S.d){S.d.panel.classList.add('rgons6-dist');reorder();}

  $$('.rgons6-empty').forEach(function(el){if(!isEmpty(el))el.classList.remove('rgons6-empty');});
  S.input=findInput();
  computeRed();
  if(S.mode===null)S.mode=(S.d&&isOpen(S.d))?'dist':'chat';
  applyMode(S.mode);
  handleWarn();
  sync();
}

/* ── 이벤트 ── */
document.addEventListener('click',function(e){
  var t=e.target;if(!t||!t.closest)return;
  var tab=t.closest('#rgons6-tabs [data-mode]');
  if(tab){e.preventDefault();switchMode(tab.getAttribute('data-mode'));return;}
  var sh=t.closest('#rgons6-sheet');
  if(sh){
    if(t.id==='rgons6-sheet'||t.closest('[data-close]')){e.preventDefault();sh.classList.remove('open');return;}
    var a=t.closest('a[data-k]');if(a){if(S.lastText)copyText(S.lastText);a.classList.add('done');}
    return;
  }
  if(t.closest('[data-quad="brief"],[data-act="brief"]')){setTimeout(function(){switchMode('chat');},30);return;}
  if(S.d&&S.d.toggle.contains(t)){setTimeout(sync,80);setTimeout(sync,400);return;}
  var b=t.closest(BTN+',[onclick]');
  if(!b||ours(b))return;
  var s=btxt(b);
  if(inDist(b)){
    if(RE.paste.test(s)){e.preventDefault();e.stopImmediatePropagation();distPaste();return;}
    if(RE.clear.test(s)){setTimeout(distClear,60);return;}
    var kind=RE.all.test(s)?'all':RE.sel.test(s)?'sel':(RE.solo.test(s)&&aiOf(s))?'solo':null;
    if(kind&&directMode()){e.preventDefault();e.stopImmediatePropagation();launch(kind,s);}
    return;
  }
  if(RE.send.test(s)||RE.sendId.test(b.id||'')||RE.brief.test(s)){if(S.mode==='dist')setTimeout(function(){switchMode('chat');},30);}
},true);
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){var sh=$('#rgons6-sheet');if(sh)sh.classList.remove('open');}
},false);

function init(){
  scan();
  var to;
  try{
    new MutationObserver(function(ms){
      if(ms.every(function(m){var n=m.target&&m.target.nodeType===3?m.target.parentElement:m.target;return !!(n&&ours(n));}))return;
      clearTimeout(to);to=setTimeout(scan,350);
    }).observe(document.body,{childList:true,subtree:true,characterData:true});
  }catch(e){}
  window.addEventListener('resize',function(){clearTimeout(to);to=setTimeout(scan,300);});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(init,150);});
else setTimeout(init,150);
})();
</script>"""

S6_BLOCK = S6_START + "\n" + S6_BODY + "\n" + S6_END


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
    fd, tmp = tempfile.mkstemp(suffix=".js", prefix="rgon_s6_chk_")
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

    base, n6 = S6_BLOCK_RE.subn("\n", text)
    base, n5 = S5_BLOCK_RE.subn("\n", base)

    ids_before = set(ID_RE.findall(base))
    onclick_before = len(ONCLICK_RE.findall(base))
    s4 = S4_BLOCK_RE.search(base)
    s4_text = s4.group(0) if s4 else None
    if not s4:
        log(f"⚠️ [{rel(p)}] Step4 블록 없음 → Step6 탭 바는 독립 sticky 모드로 동작 (Step4 먼저 실행 권장)")

    if s4:
        idx = s4.end()
        new = base[:idx] + "\n" + S6_BLOCK + base[idx:]
        where = "Step4 블록 직후"
    else:
        idx = base.lower().rfind("</body>")
        new = (base[:idx] + S6_BLOCK + "\n" + base[idx:]) if idx >= 0 else (base + "\n" + S6_BLOCK + "\n")
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
    if len(ONCLICK_RE.findall(new)) < onclick_before:
        log(f"❌ [{rel(p)}] 기존 onclick 핸들러 감소 → 중단")
        return False
    s4_after = S4_BLOCK_RE.search(new)
    if s4_text is not None and (not s4_after or s4_after.group(0) != s4_text):
        log(f"❌ [{rel(p)}] Step4 블록 변형 감지 → 중단")
        return False

    m = re.search(r'<script id="rgons6-script">(.*?)</script>', new, re.S)
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
    log(f"✅ [{rel(p)}] Step6 블록 {'교체' if n6 else '삽입'} ({where}"
        f"{', Step5 블록 대체 제거' if n5 else ''}, 기존 id {len(ids_before)}개·onclick {onclick_before}개 보존, "
        f"Step4 무변경, 백업: {b.name})")
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
    log(f"🏛️ RGON STEP6 완벽 분배창 패치 시작 — 루트: {ROOT}")
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

    log("🏁 완료 — 모바일 새로고침(캐시 무시) 후 [💬 1번 | ⚡ 2번] 탭 전환, 분배창 순서"
        "(템플릿→지시문→발사→전광판 2x2), 발사 버튼 자동복사+Genspark 이동을 확인하세요.\n"
        "   ※ PC에서도 직통 발사를 강제하려면 브라우저 콘솔에서 localStorage.rgon_direct_launch='1' "
        "(확장 우선은 '0')")


if __name__ == "__main__":
    main()
