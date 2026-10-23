#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step7_four_bars_and_fast_workflow.py
- 0/1/2/3번 4개 바를 상호 배타적 아코디언으로 구성 (열린 바가 가려지지 않음)
- 중복 DOM 정리, [🚀 코드반영] 원터치 버튼, GitHub 저장소 기본값 세팅
- 비파괴 패치: 타임스탬프 백업 + 멱등(여러 번 실행해도 1세트만 유지)
Python 3 표준 라이브러리 전용
"""
import os
import re
import sys
import shutil
import subprocess
from datetime import datetime

PREFERRED_ROOT = r"C:/Users/sangi/Downloads/shin-agent"
TARGETS = [
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
    "rgon_alpha_audience.html",
]
OLD_REPO = "owner/shin-agent"
NEW_REPO = "sangill111157-spec/hangeoreumsshik-cloud"
BRIDGE_URL = "http://127.0.0.1:8765/queue"
COMMIT_MSG = "feat(ui): Step 7 make 0-1-2-3 all collapsible bars without overlap + 1-click code apply"

BEGIN = "<!-- STEP7_BEGIN -->"
END = "<!-- STEP7_END -->"
BLOCK_RE = re.compile(r"\n?<!-- STEP7_BEGIN -->.*?<!-- STEP7_END -->\n?", re.S)
DUP_KEYS = ["실시간 브리핑 전문", "분배 컨트롤러", "독대실에서 바로 분배"]
TOK = re.compile(r"<details\b[^>]*>|</details\s*>", re.I)

# ----------------------------------------------------------------------------
# 주입 CSS
# ----------------------------------------------------------------------------
CSS = r"""
#s7-root{display:flex;flex-direction:column;gap:6px;margin:6px 0;width:100%;box-sizing:border-box}
#s7-root>details.s7-bar{border:1.5px solid var(--c,#2ecc71);border-radius:10px;background:#0d1117;overflow:hidden;margin:0;box-sizing:border-box}
details.s7-bar[data-s7="3"]{--c:#2ecc71}
details.s7-bar[data-s7="2"]{--c:#3b82f6}
details.s7-bar[data-s7="1"]{--c:#f59e0b}
details.s7-bar[data-s7="0"]{--c:#a855f7}
details.s7-bar>summary{list-style:none;cursor:pointer;padding:10px 12px;font-weight:700;font-size:14px;line-height:1.35;color:#e6edf3;min-height:44px;box-sizing:border-box;display:flex;align-items:center;-webkit-tap-highlight-color:transparent;user-select:none}
details.s7-bar>summary::-webkit-details-marker{display:none}
details.s7-bar[open]>summary{background:rgba(255,255,255,.06);border-bottom:1px solid var(--c)}
details.s7-bar>.s7-body{padding:8px;box-sizing:border-box;max-height:max(320px,var(--s7-h,70dvh));overflow-y:auto;-webkit-overflow-scrolling:touch;position:relative}
details.s7-bar0[open]>.s7-body{display:flex;flex-direction:column;height:max(320px,var(--s7-h,70dvh));padding:0;overflow-y:auto}
details.s7-bar0>.s7-body>*{max-height:none}
.s7-row2{display:grid!important;gap:3px;width:100%;box-sizing:border-box}
.s7-row2>*{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:12px;padding-left:2px!important;padding-right:2px!important}
#s7-apply{background:linear-gradient(135deg,#ef4444,#f97316)!important;color:#fff!important;font-weight:800;border:0;border-radius:8px;cursor:pointer}
#s7-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111c;color:#fff;padding:10px 16px;border-radius:10px;font-size:13px;z-index:2147483000;max-width:90vw;text-align:center;backdrop-filter:blur(6px);border:1px solid #444}
#s7-modal{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:2147483001;display:flex;align-items:center;justify-content:center;padding:12px;box-sizing:border-box}
#s7-modal .s7-card{background:#0d1117;border:1.5px solid #f97316;border-radius:12px;padding:12px;width:min(640px,100%);max-height:92dvh;display:flex;flex-direction:column;gap:8px;color:#e6edf3}
#s7-modal textarea{width:100%;height:36dvh;background:#010409;color:#e6edf3;border:1px solid #30363d;border-radius:8px;padding:8px;font-family:monospace;font-size:12px;box-sizing:border-box}
#s7-modal .s7-btns{display:flex;flex-wrap:wrap;gap:6px}
#s7-modal button{flex:1 1 120px;padding:10px;border-radius:8px;border:1px solid #444;background:#161b22;color:#fff;font-weight:700;cursor:pointer}
"""

# ----------------------------------------------------------------------------
# 주입 JS (__REPO__ / __BRIDGE__ 는 파이썬에서 치환)
# ----------------------------------------------------------------------------
JS = r"""
(function(){
'use strict';
if(window.__STEP7__) return; window.__STEP7__=true;
var REPO='__REPO__', BRIDGE='__BRIDGE__', OLD_REPO='__OLD_REPO__';
var LABELS={
 3:'▶ 🛰️ 르곤-알파 실시간 브리핑 전문 (자동)',
 2:'▶ 🛰️ 4대 AI 분배 컨트롤러 & 만능 소통창',
 1:'▶ ⚡ 독대실에서 바로 분배하기 (👑르곤 / 🧠Claude / ⚡GPT / 🎯Grok)',
 0:'▶ 💬 르곤-알파 1:1 대화창 & 6대 청사 보좌 지표'
};
var KEYS={3:['실시간 브리핑 전문'],2:['분배 컨트롤러'],1:['독대실에서 바로 분배']};
var root=null, bars={}, built=false, row2=null, busy=false;

function norm(s){return (s||'').replace(/\s+/g,' ').trim();}
function inRoot(el){return !!el.closest('#s7-root,#s7-modal,#s7-toast,script,style');}
function matches(t,key){return key.every(function(k){return t.indexOf(k)>-1;});}
function findHeaders(key){
  var out=[], all=document.querySelectorAll('summary,button,div,span,a,h1,h2,h3,h4,h5,p,label,li');
  for(var i=0;i<all.length;i++){
    var el=all[i]; if(inRoot(el)) continue;
    var t=norm(el.textContent); if(t.length<4||t.length>140||!matches(t,key)) continue;
    var childHit=Array.prototype.some.call(el.children,function(c){return matches(norm(c.textContent),key);});
    if(!childHit) out.push(el);
  }
  return out;
}
function toast(msg){
  var t=document.getElementById('s7-toast');
  if(!t){t=document.createElement('div');t.id='s7-toast';document.body.appendChild(t);}
  t.textContent=msg;t.style.display='block';clearTimeout(t.__t);
  t.__t=setTimeout(function(){t.style.display='none';},3200);
}
function looksLikeHeader(p){
  var t=norm(p.textContent); if(t.length>140) return false;
  return [3,2,1].some(function(n){return matches(t,KEYS[n]);});
}
function byId(id){return id?document.getElementById(String(id).replace(/^#/,'')):null;}
function resolvePanel(c){
  var id=c.getAttribute('aria-controls')||c.getAttribute('data-target')||c.getAttribute('data-bs-target');
  var p=byId(id);
  if(!p){
    var oc=c.getAttribute('onclick')||'';
    var m=oc.match(/getElementById\(\s*['"]([^'"]+)['"]/)||oc.match(/\w+\(\s*['"]([^'"]+)['"]/);
    if(m) p=byId(m[1]);
  }
  if(!p||p.contains(c)) p=c.nextElementSibling;
  if(!p&&c.parentElement) p=c.parentElement.nextElementSibling;
  if(p&&looksLikeHeader(p)) p=null;
  return p;
}
function describe(h){
  var sm=h.closest('summary');
  if(sm&&sm.parentElement&&sm.parentElement.tagName==='DETAILS') return {kind:'details',el:sm.parentElement,header:sm};
  var c=h.closest('button,[onclick],[role=button],a')||h;
  return {kind:'plain',header:c,panel:resolvePanel(c)};
}
function refOf(d){return d.kind==='details'?d.el:d.header;}
function unhide(el){
  el.hidden=false; el.removeAttribute('hidden');
  var cs=getComputedStyle(el);
  if(cs.display==='none') el.style.setProperty('display','block','important');
  if(cs.visibility==='hidden') el.style.setProperty('visibility','visible','important');
  if(cs.maxHeight==='0px') el.style.setProperty('max-height','none','important');
  if(cs.height==='0px'&&el.children.length) el.style.setProperty('height','auto','important');
  if(parseFloat(cs.opacity)===0) el.style.setProperty('opacity','1','important');
}
function defix(el,inbar){
  var all=[el].concat([].slice.call(el.querySelectorAll('*')));
  all.forEach(function(x){
    var cs=getComputedStyle(x);
    if(cs.position!=='fixed'&&!(cs.position==='sticky'&&x!==inbar)) return;
    var isBar=(x===inbar);
    x.style.setProperty('position',isBar?'sticky':'static','important');
    x.style.setProperty('top','auto','important');
    x.style.setProperty('left','auto','important');
    x.style.setProperty('right','auto','important');
    x.style.setProperty('bottom',isBar?'0':'auto','important');
    x.style.setProperty('transform','none','important');
    x.style.setProperty('width','auto','important');
    if(isBar){x.style.setProperty('z-index','5','important');x.style.setProperty('background','#0d1117');}
  });
}

/* ---------- 상단 탭줄 제거(숨김) ---------- */
function hideTabs(){
  var a=findHeaders(['1번','알파 대화창'])[0], b=findHeaders(['2번','AI 지시'])[0];
  if(!a||!b) return;
  var sel='button,[role=tab],[onclick],a';
  var ba=a.closest(sel)||a, bb=b.closest(sel)||b, p=ba.parentElement;
  while(p&&!p.contains(bb)) p=p.parentElement;
  if(!p||p===document.body||norm(p.textContent).length>120) return;
  p.style.setProperty('display','none','important'); p.setAttribute('data-s7-removed','tabs');
}

/* ---------- 바 생성 ---------- */
function setArrow(d){
  var sm=d.querySelector(':scope>summary'); if(!sm) return;
  var t=sm.textContent.replace(/^\s*[▶▼]\s*/,'');
  var nt=(d.open?'▼ ':'▶ ')+t;
  if(sm.textContent!==nt) sm.textContent=nt;
}
function mk(n,d){
  var det,sm,body=document.createElement('div');
  body.className='s7-body';
  if(d.kind==='details'){
    det=d.el; sm=d.header; det.open=false; det.removeAttribute('open');
    [].slice.call(det.childNodes).forEach(function(k){if(k!==sm) body.appendChild(k);});
    sm.textContent=LABELS[n]; det.appendChild(body);
  }else{
    det=document.createElement('details'); sm=document.createElement('summary');
    sm.textContent=LABELS[n]; det.appendChild(sm);
    if(d.panel){
      if(root&&d.panel.contains(root)) document.body.insertBefore(root,document.body.firstChild);
      body.appendChild(d.panel); unhide(d.panel);
    }
    det.appendChild(body);
    d.header.style.setProperty('display','none','important'); d.header.setAttribute('data-s7-hidden','1');
  }
  det.classList.add('s7-bar'); det.setAttribute('data-s7',n);
  root.appendChild(det); bars[n]=det; return det;
}

/* ---------- 0번 바 재료 찾기 ---------- */
function findFeed(){
  var ids=['chatFeed','chat-feed','chatLog','chat-log','chatMessages','messages','feed','chatBox','alphaChat','alpha-chat','chat','log'];
  for(var i=0;i<ids.length;i++){var e=document.getElementById(ids[i]); if(e&&!inRoot(e)) return e;}
  var q=document.querySelectorAll('[class*="chat-feed"],[class*="chatFeed"],[class*="chat-log"],[class*="messages"]');
  for(var j=0;j<q.length;j++) if(!inRoot(q[j])) return q[j];
  return null;
}
function findInput(){
  var list=[].slice.call(document.querySelectorAll('textarea,input[type=text],input:not([type])')).filter(function(e){
    return !e.closest('#s7-root,#s7-modal,[id*=drawer i],[id*=modal i],[class*=drawer i],[class*=modal i]');
  });
  if(!list.length) return null;
  var pref=list.filter(function(e){return /chat|msg|message|입력|질문|알파|르곤/i.test((e.id||'')+(e.placeholder||'')+(e.name||''));});
  return (pref[0]||list[list.length-1]);
}
function inputBarOf(inp){
  var e=inp,best=null;
  for(var i=0;i<7&&e&&e!==document.body;i++,e=e.parentElement){
    var cs=getComputedStyle(e);
    if(cs.position==='fixed'||cs.position==='sticky'){best=e;break;}
  }
  if(!best) best=inp.closest('form')||inp.parentElement;
  if(best&&(best.contains(root)||best.querySelector('.s7-bar'))) best=inp.parentElement;
  return best;
}
function lca(list){
  var a=list[0];
  while(a){ if(list.every(function(x){return a.contains(x);})) return a; a=a.parentElement; }
  return null;
}
function lcaValid(L){
  if(!L||L===document.body||L===document.documentElement) return false;
  if(L.contains(root)||L.querySelector('.s7-bar')) return false;
  if(L.textContent.indexOf('로건봇')>-1) return false;
  if(L.querySelector('[id*=drawer i],[id*=modal i],[class*=drawer i]')) return false;
  return true;
}
function buildBar0(){
  var det=document.createElement('details'), sm=document.createElement('summary'), body=document.createElement('div');
  det.className='s7-bar s7-bar0'; det.setAttribute('data-s7','0');
  sm.textContent=LABELS[0]; body.className='s7-body'; det.appendChild(sm); det.appendChild(body);
  root.appendChild(det); bars[0]=det;

  var anchors=[];
  var indH=findHeaders(['6대 청사','지표'])[0];
  if(indH){
    var id=describe(indH);
    if(id.kind==='details') anchors.push(id.el); else {anchors.push(id.header); if(id.panel) anchors.push(id.panel);}
  }
  var feed=findFeed(), inp=findInput(), inbar=inp?inputBarOf(inp):null;
  if(feed) anchors.push(feed);
  if(inbar) anchors.push(inbar);
  anchors=anchors.filter(function(a,i){return a&&anchors.indexOf(a)===i&&!a.contains(root)&&!inRoot(a);});
  if(!anchors.length){body.textContent='대화창 요소를 찾지 못했습니다.';return;}

  var L=anchors.length?lca(anchors):null, moved=[];
  if(lcaValid(L)) moved=[L];
  else moved=anchors.filter(function(a){return !anchors.some(function(o){return o!==a&&o.contains(a);});})
        .sort(function(a,b){return (a.compareDocumentPosition(b)&4)?-1:1;});
  moved.forEach(function(el){
    body.appendChild(el); unhide(el);
    defix(el,inbar);
    el.style.setProperty('margin','0','important');
    el.style.setProperty('max-height','none','important');
    el.style.setProperty('flex','1 1 auto','important');
    el.style.setProperty('min-height','0','important');
    if(el===inbar){el.style.setProperty('flex','0 0 auto','important');}
  });
  if(feed){
    unhide(feed);
    feed.style.setProperty('overflow-y','auto','important');
    feed.style.setProperty('max-height','none','important');
    feed.style.setProperty('min-height','160px','important');
    feed.style.setProperty('flex','1 1 auto','important');
    if(!moved.some(function(m){return m===feed;})) feed.style.setProperty('height','auto','important');
  }
  if(inbar){ inbar.style.setProperty('position','sticky','important'); inbar.style.setProperty('bottom','0','important'); }
}

/* ---------- 아코디언 ---------- */
function barList(){return [3,2,1,0].map(function(n){return bars[n];}).filter(Boolean);}
function layout(){
  if(!root) return;
  var list=barList(); if(!list.length) return;
  var sm=list[0].querySelector(':scope>summary'), sh=sm?sm.offsetHeight||44:44;
  var top=root.getBoundingClientRect().top+window.scrollY;
  var used=top+(sh+8)*list.length+6;
  root.style.setProperty('--s7-h','calc(100dvh - '+Math.round(used)+'px)');
}
function closeOthers(d){barList().forEach(function(o){if(o!==d&&o.open){o.open=false;o.removeAttribute('open');setArrow(o);}});}
function openBar(n){
  var d=bars[n]; if(!d) return;
  closeOthers(d); d.open=true; setArrow(d); layout();
  try{window.scrollTo({top:0,behavior:'smooth'});}catch(e){window.scrollTo(0,0);}
}
window.s7Open=openBar;
function wireAccordion(){
  root.addEventListener('click',function(ev){
    var sm=ev.target.closest&&ev.target.closest('summary'); if(!sm) return;
    var d=sm.parentElement; if(!d||!d.classList.contains('s7-bar')) return;
    if(!d.open) closeOthers(d);
  },true);
  root.addEventListener('toggle',function(ev){
    var d=ev.target; if(!d.classList||!d.classList.contains('s7-bar')) return;
    setArrow(d);
    if(d.open){closeOthers(d);layout();try{window.scrollTo({top:0,behavior:'smooth'});}catch(e){}}
  },true);
  window.addEventListener('resize',layout);
  window.addEventListener('orientationchange',function(){setTimeout(layout,300);});
  barList().forEach(setArrow);
}

/* ---------- 🚀 코드반영 ---------- */
function stamp(){var d=new Date(),p=function(x){return String(x).padStart(2,'0');};
  return d.getFullYear()+p(d.getMonth()+1)+p(d.getDate())+'_'+p(d.getHours())+p(d.getMinutes())+p(d.getSeconds());}
function copyText(t){
  try{ if(navigator.clipboard&&navigator.clipboard.writeText) return navigator.clipboard.writeText(t); }catch(e){}
  var ta=document.createElement('textarea'); ta.value=t; document.body.appendChild(ta); ta.select();
  try{document.execCommand('copy');}catch(e){} ta.remove(); return Promise.resolve();
}
function postBridge(code){
  var ctl=window.AbortController?new AbortController():null;
  var to=setTimeout(function(){if(ctl) ctl.abort();},2500);
  var payload=JSON.stringify({type:'code',source:'rgon_alpha_chat',repo:REPO,ts:Date.now(),code:code});
  return fetch(BRIDGE,{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain;charset=utf-8'},body:payload,signal:ctl?ctl.signal:undefined})
    .then(function(){clearTimeout(to);return true;})
    .catch(function(){clearTimeout(to);return false;});
}
function showApplyModal(code){
  var old=document.getElementById('s7-modal'); if(old) old.remove();
  var m=document.createElement('div'); m.id='s7-modal';
  var card=document.createElement('div'); card.className='s7-card';
  var h=document.createElement('div'); h.style.fontWeight='800'; h.textContent='🚀 코드 즉시반영 (PC 브리지 미연결 → 모바일 경로)';
  var ta=document.createElement('textarea'); ta.value=code;
  var bt=document.createElement('div'); bt.className='s7-btns';
  function btn(label,fn){var b=document.createElement('button');b.type='button';b.textContent=label;b.addEventListener('click',fn);bt.appendChild(b);}
  btn('📋 복사',function(){copyText(ta.value).then(function(){toast('복사 완료');});});
  btn('🐙 GitHub에 올리기',function(){
    var fn='inbox/code_'+stamp()+'.txt';
    var base='https://github.com/'+REPO+'/new/main?filename='+encodeURIComponent(fn);
    var url=base+'&value='+encodeURIComponent(ta.value);
    if(url.length>7000){copyText(ta.value);url=base;toast('코드가 길어 클립보드에 복사됨 — 붙여넣고 Commit 하세요');}
    window.open(url,'_blank');
  });
  btn('✈️ 텔레그램 전송',function(){
    window.open('https://t.me/share/url?url=%20&text='+encodeURIComponent(ta.value.slice(0,3500)),'_blank');
  });
  btn('🔁 브리지 재시도',function(){postBridge(ta.value).then(function(ok){toast(ok?'🚀 PC 브리지 전달 완료':'브리지 연결 실패');if(ok) m.remove();});});
  btn('닫기',function(){m.remove();});
  card.appendChild(h);card.appendChild(ta);card.appendChild(bt);m.appendChild(card);
  m.addEventListener('click',function(e){if(e.target===m) m.remove();});
  document.body.appendChild(m);
}
function applyCode(){
  var getText=(navigator.clipboard&&navigator.clipboard.readText)?navigator.clipboard.readText():Promise.reject();
  getText.catch(function(){return window.prompt('클립보드 읽기 권한이 없습니다. 클로드 코드를 붙여넣어 주세요:')||'';})
  .then(function(txt){
    var code=(txt||'').trim();
    if(!code){toast('클립보드가 비어 있습니다');return;}
    toast('🚀 전달 중...');
    postBridge(code).then(function(ok){
      if(ok){toast('🚀 PC 브리지 큐 전달 완료 ('+code.length+'자)');return;}
      var hooks=['openInstantApply','openApplyModal','showApplyModal','instantApply','openMobileApply','openCodeApply'];
      for(var i=0;i<hooks.length;i++){
        if(typeof window[hooks[i]]==='function'){ try{window[hooks[i]](code);return;}catch(e){} }
      }
      showApplyModal(code);
    });
  });
}

/* ---------- 상단 2층 바 ---------- */
function setupRow2(){
  var h=findHeaders(['로건봇'])[0], btn=h&&(h.closest('button,a,[onclick],[role=button]')||h);
  row2=btn?btn.parentElement:null;
  var nb=document.getElementById('s7-apply');
  if(!nb){
    nb=document.createElement('button'); nb.type='button'; nb.id='s7-apply'; nb.textContent='🚀 코드반영';
    if(btn){nb.className=btn.className; var st=btn.getAttribute('style'); if(st) nb.setAttribute('style',st);}
    nb.addEventListener('click',applyCode);
  }
  if(row2){
    row2.appendChild(nb); row2.classList.add('s7-row2');
    row2.style.gridTemplateColumns='repeat('+row2.children.length+',minmax(0,1fr))';
    [].slice.call(row2.children).forEach(function(c){
      if(c.__s7) return; c.__s7=1; var t=norm(c.textContent);
      if(t.indexOf('브리핑')>-1) c.addEventListener('click',function(){setTimeout(function(){openBar(3);},30);});
      else if(t.indexOf('Top1')>-1) c.addEventListener('click',function(){setTimeout(function(){openBar(1);},80);});
    });
  }else{
    var wrap=document.createElement('div'); wrap.className='s7-row2'; wrap.style.gridTemplateColumns='1fr';
    wrap.appendChild(nb); root.parentNode.insertBefore(wrap,root); row2=wrap;
  }
}

/* ---------- 보정(저장소 기본값·카드·중복 상태줄) ---------- */
function fixRepo(){
  document.querySelectorAll('input,textarea').forEach(function(i){
    var v=i.value||'', hint=((i.id||'')+(i.name||'')+(i.placeholder||'')).toLowerCase();
    if(v.indexOf(OLD_REPO)>-1||(!v&&/repo|github|저장소/.test(hint)&&i.tagName==='INPUT')){
      i.value=v?v.split(OLD_REPO).join(REPO):REPO;
      ['input','change'].forEach(function(ev){i.dispatchEvent(new Event(ev,{bubbles:true}));});
    }
    if(i.placeholder&&i.placeholder.indexOf(OLD_REPO)>-1) i.placeholder=i.placeholder.split(OLD_REPO).join(REPO);
  });
  try{
    var n=localStorage.length, keys=[];
    for(var k=0;k<n;k++) keys.push(localStorage.key(k));
    keys.forEach(function(key){var val=localStorage.getItem(key); if(val&&val.indexOf(OLD_REPO)>-1) localStorage.setItem(key,val.split(OLD_REPO).join(REPO));});
    localStorage.setItem('s7_repo',REPO);
  }catch(e){}
}
function fixCards(){
  var re=/^[🔵🟢🟡🔴🟠🟣⚪⚫]\s*(👑|🧠|⚡|🎯|🔥)/u;
  document.querySelectorAll('div,span,p,b,strong').forEach(function(e){
    if(e.children.length>0||inRoot(e)) return;
    if(!re.test(norm(e.textContent))) return;
    e.style.setProperty('line-height','1.4','important');
    e.style.setProperty('overflow','visible','important');
    e.style.setProperty('height','auto','important');
    e.style.setProperty('white-space','nowrap','important');
    var p=e.parentElement;
    for(var i=0;i<2&&p&&p!==document.body;i++,p=p.parentElement){
      p.style.setProperty('overflow','visible','important');
      p.style.setProperty('min-height','0','important');
      if(i===0) p.style.setProperty('padding-top','4px','important');
    }
  });
}
function dedupeStatus(){
  var re=/^수거\s*\d+\s*\/\s*\d+/, seen=[];
  document.querySelectorAll('div,span,p,small').forEach(function(e){
    if(e.children.length>0||inRoot(e)||e.getAttribute('data-s7-dup')) return;
    if(!re.test(norm(e.textContent))) return;
    var p=e.parentElement;
    if(seen.indexOf(p)>-1){e.style.setProperty('display','none','important');e.setAttribute('data-s7-dup','1');}
    else seen.push(p);
  });
}
function purgeDupes(){
  [3,2,1].forEach(function(n){
    findHeaders(KEYS[n]).forEach(function(h){
      var d=describe(h);
      if(d.kind==='details'){ if(!d.el.classList.contains('s7-bar')&&!inRoot(d.el)) d.el.remove(); }
      else if(d.header.getAttribute('data-s7-hidden')!=='1'){
        if(d.panel&&!inRoot(d.panel)) d.panel.remove(); d.header.remove();
      }
    });
  });
}

/* ---------- 초기화 ---------- */
function build(){
  if(built) return; built=true;
  hideTabs();
  var found={};
  [3,1,2].forEach(function(n){
    var hs=findHeaders(KEYS[n]); if(!hs.length) return;
    var ds=hs.map(describe), keep=ds[0];
    ds.slice(1).forEach(function(d){
      if(d.kind==='details'){ if(d.el!==keep.el&&!d.el.contains(refOf(keep))) d.el.remove(); }
      else if(d.header!==keep.header){ if(d.panel&&d.panel!==keep.panel&&!d.panel.contains(refOf(keep))) d.panel.remove(); d.header.remove(); }
    });
    found[n]=keep;
  });
  root=document.createElement('div'); root.id='s7-root';
  var refs=Object.keys(found).map(function(k){return refOf(found[k]);});
  refs=refs.filter(function(r){return !refs.some(function(o){return o!==r&&o.contains(r);});});
  refs.sort(function(a,b){return (a.compareDocumentPosition(b)&4)?-1:1;});
  if(refs[0]&&refs[0].parentNode) refs[0].parentNode.insertBefore(root,refs[0]);
  else document.body.appendChild(root);
  [3,1,2].forEach(function(n){ if(found[n]) mk(n,found[n]); });
  [3,2,1].forEach(function(n){ if(bars[n]) root.appendChild(bars[n]); });
  buildBar0(); root.appendChild(bars[0]);
  wireAccordion(); setupRow2(); layout();
}
function finish(){
  fixRepo(); fixCards(); dedupeStatus();
  var tmr=null;
  new MutationObserver(function(){
    if(busy) return; clearTimeout(tmr);
    tmr=setTimeout(function(){busy=true;try{purgeDupes();dedupeStatus();fixCards();}catch(e){} busy=false;},700);
  }).observe(document.body,{childList:true,subtree:true});
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('button,a,[onclick]');
    if(b&&/☰|더보기/.test(b.textContent||'')) setTimeout(fixRepo,150);
  },true);
}
function attempt(i){
  var c=[3,1,2].filter(function(n){return findHeaders(KEYS[n]).length;}).length;
  if(c===3||i>=6){build();finish();} else setTimeout(function(){attempt(i+1);},500);
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){attempt(0);});
else attempt(0);
})();
"""


# ----------------------------------------------------------------------------
# 유틸
# ----------------------------------------------------------------------------
def mask_html(html):
    def blank(m):
        return " " * (m.end() - m.start())
    h = re.sub(r"<script\b.*?</script\s*>", blank, html, flags=re.I | re.S)
    h = re.sub(r"<style\b.*?</style\s*>", blank, h, flags=re.I | re.S)
    h = re.sub(r"<!--.*?-->", blank, h, flags=re.S)
    return h


def dedupe_details(html):
    """최상위 <details> 중 완전히 동일한 블록이 반복되면 첫 번째만 남긴다."""
    m = mask_html(html)
    depth, start, spans = 0, None, []
    for t in TOK.finditer(m):
        if t.group(0).startswith("</"):
            depth -= 1
            if depth < 0:
                return html, 0
            if depth == 0:
                spans.append((start, t.end()))
        else:
            if depth == 0:
                start = t.start()
            depth += 1
    if depth != 0:
        return html, 0
    seen, cut = set(), []
    for s, e in spans:
        blk = html[s:e]
        if not any(k in blk for k in DUP_KEYS):
            continue
        key = re.sub(r"\s+", " ", blk)
        if key in seen:
            cut.append((s, e))
        else:
            seen.add(key)
    for s, e in reversed(cut):
        html = html[:s] + html[e:]
    return html, len(cut)


def build_block():
    js = (JS.replace("__REPO__", NEW_REPO)
            .replace("__BRIDGE__", BRIDGE_URL)
            .replace("__OLD_REPO__", OLD_REPO))
    return "\n%s\n<style id=\"s7-style\">%s</style>\n<script id=\"s7-script\">%s</script>\n%s\n" % (
        BEGIN, CSS, js, END)


def patch_file(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        orig = f.read()
    html = BLOCK_RE.sub("", orig)
    html, dups = dedupe_details(html)
    html = html.replace(OLD_REPO, NEW_REPO)
    block = build_block()
    idx = html.lower().rfind("</body>")
    if idx == -1:
        html = html + block
    else:
        html = html[:idx] + block + html[idx:]
    if html == orig:
        print("  = 변경 없음 (이미 최신): %s" % path)
        return False
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = "%s.bak_%s" % (path, ts)
    shutil.copy2(path, bak)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print("  ✓ 패치 완료: %s (중복 블록 제거 %d개, 백업 %s)" % (path, dups, os.path.basename(bak)))
    return True


def ensure_exclude(root):
    gitdir = os.path.join(root, ".git")
    if not os.path.isdir(gitdir):
        return False
    info = os.path.join(gitdir, "info")
    os.makedirs(info, exist_ok=True)
    ex = os.path.join(info, "exclude")
    cur = ""
    if os.path.exists(ex):
        with open(ex, "r", encoding="utf-8", errors="replace") as f:
            cur = f.read()
    add = [p for p in ("*.bak_*", "*.bak") if p not in cur.splitlines()]
    if add:
        with open(ex, "a", encoding="utf-8") as f:
            if cur and not cur.endswith("\n"):
                f.write("\n")
            f.write("\n".join(add) + "\n")
    return True


def run(cmd, cwd):
    print("$ " + " ".join(cmd))
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except FileNotFoundError:
        print("  ✗ git 실행 파일을 찾을 수 없습니다.")
        return 127
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    if out:
        print(out)
    if err:
        print(err)
    return p.returncode


def git_sync(root):
    if not ensure_exclude(root):
        print("⚠ .git 폴더가 없어 GitHub 동기화를 건너뜁니다.")
        return
    run(["git", "add", "-A"], root)
    rc = run(["git", "commit", "-m", COMMIT_MSG], root)
    if rc != 0:
        print("ℹ 커밋할 변경이 없거나 커밋 실패 — 다음 단계로 진행합니다.")
    if run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"], root) != 0:
        print("✗ pull --rebase 실패 → rebase 중단 후 push 생략")
        run(["git", "rebase", "--abort"], root)
        return
    if run(["git", "push", "origin", "main"], root) == 0:
        print("☁ GitHub 동기화 완료")
    else:
        print("✗ push 실패: 인증/네트워크 상태를 확인하세요.")


def main():
    root = PREFERRED_ROOT if os.path.isdir(PREFERRED_ROOT) else os.getcwd()
    print("📁 작업 루트: %s" % root)
    ensure_exclude(root)
    changed = 0
    for rel in TARGETS:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            print("  - 없음(건너뜀): %s" % rel)
            continue
        try:
            if patch_file(p):
                changed += 1
        except Exception as e:  # noqa
            print("  ✗ 실패 %s: %s" % (rel, e))
    print("🛠 패치된 파일: %d개" % changed)
    git_sync(root)


if __name__ == "__main__":
    sys.exit(main())
