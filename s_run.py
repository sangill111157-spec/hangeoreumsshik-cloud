#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step8_fix_briefing_bar_and_cleanup.py
- '🛰️ 르곤-알파 실시간 브리핑 전문 (자동)' 바가 열려도 본문이 안 보이던 버그 수리
  (본문/자식 요소에 걸린 display:none · max-height:0 · visibility:hidden · height:0 강제 해제)
- 본문이 비었거나 30자 미만이면(그리고 열릴 때마다) rgon_brain_snapshot.json / evolution_memory.json 을
  fetch(no-store)로 읽어 한국어 브리핑 전문으로 자동 렌더링
- [📋 브리핑] 버튼 → 3번 바 즉시 열림(나머지 3개 닫힘) + 최신 브리핑 표시
- 잔여 UI 정리: [1번 알파 대화창 | 2번 AI 지시·분배] 줄, 빈 파란 타원 버튼, 하단 금색 잔여 박스
- 비파괴 패치: 타임스탬프 백업 + 멱등(STEP8 블록만 교체), Step7 블록은 그대로 유지
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
REPO = "sangill111157-spec/hangeoreumsshik-cloud"
COMMIT_MSG = "fix(ui): Step 8 fix realtime briefing bar content display and clean stray UI elements"

BEGIN = "<!-- STEP8_BEGIN -->"
END = "<!-- STEP8_END -->"
BLOCK_RE = re.compile(r"\n?<!-- STEP8_BEGIN -->.*?<!-- STEP8_END -->\n?", re.S)

# ----------------------------------------------------------------------------
# 주입 CSS
# ----------------------------------------------------------------------------
CSS = r"""
details.s7-bar[data-s7="3"][open]>.s7-body{display:block!important;visibility:visible!important;opacity:1!important;height:auto!important;max-height:max(320px,var(--s7-h,70dvh))!important;overflow-y:auto!important;padding:12px!important}
details.s7-bar[data-s7="3"][open]>.s7-body>div:not([data-s7-dup]):not([data-s8-hidden]),
details.s7-bar[data-s7="3"][open]>.s7-body>pre:not([data-s8-hidden]),
details.s7-bar[data-s7="3"][open]>.s7-body>section:not([data-s8-hidden]),
details.s7-bar[data-s7="3"][open]>.s7-body>article:not([data-s8-hidden]){display:block!important;visibility:visible!important;opacity:1!important;height:auto!important;max-height:none!important}
#s8-brief{margin:0 0 10px;border:1px solid #2ecc71;border-radius:8px;background:#0b1410;color:#d7ffe6;padding:8px;box-sizing:border-box}
#s8-brief .s8-tools{display:flex;gap:6px;margin-bottom:6px}
#s8-brief .s8-tools button{flex:1 1 0;min-height:36px;padding:6px 8px;border-radius:8px;border:1px solid #2ecc71;background:#10241a;color:#eafff2;font-weight:700;font-size:12px;cursor:pointer}
#s8-brief .s8-pre{margin:0;white-space:pre-wrap;word-break:break-word;font:12.5px/1.6 ui-monospace,Consolas,"Malgun Gothic",monospace;max-height:none;overflow:visible;color:inherit;background:transparent;border:0;padding:0}
[data-s8-hidden]{display:none!important}
"""

# ----------------------------------------------------------------------------
# 주입 JS
# ----------------------------------------------------------------------------
JS = r"""
(function(){
'use strict';
if(window.__STEP8__) return; window.__STEP8__=true;
var REPO='__REPO__';
var BASES=['./','../','./docs/','./dashboard/','/'];
var FILES={snap:'rgon_brain_snapshot.json',evo:'evolution_memory.json'};
var BAR3_KEY='실시간 브리핑 전문';
var bar3=null, token=0, lastAt=0, hooked=false, busy=false, bar3Wired=false;

function norm(s){return (s||'').replace(/\s+/g,' ').trim();}
function inUi(el){return !!(el.closest&&el.closest('#s7-root,#s7-modal,#s7-toast,#s8-brief,script,style'));}
function isOverlay(el){return !!(el.closest&&el.closest('#s7-modal,[id*=drawer i],[id*=modal i],[class*=drawer i],[class*=modal i],[role=dialog]'));}
function setI(el,p,v){el.style.setProperty(p,v,'important');}
function isObj(v){return v&&typeof v==='object';}

/* ================= 3번 바 찾기 ================= */
function findBar3(){
  var b=document.querySelector('details.s7-bar[data-s7="3"]'); if(b) return b;
  var ds=document.querySelectorAll('details');
  for(var i=0;i<ds.length;i++){
    var sm=ds[i].querySelector(':scope>summary');
    if(sm&&sm.textContent.indexOf(BAR3_KEY)>-1) return ds[i];
  }
  return null;
}
function bodyOf(bar){return bar.querySelector(':scope>.s7-body')||bar;}

/* ================= 숨김 제약 강제 해제 ================= */
var SKIP={SCRIPT:1,STYLE:1,TEMPLATE:1,NOSCRIPT:1,OPTION:1,OPTGROUP:1,HEAD:1,META:1,LINK:1,SUMMARY:1,BR:1};
var INLINE={SPAN:1,B:1,I:1,STRONG:1,EM:1,A:1,CODE:1,SMALL:1,LABEL:1,U:1,S:1,MARK:1,SUB:1,SUP:1,FONT:1};
var DISP={TABLE:'table',TR:'table-row',TD:'table-cell',TH:'table-cell',THEAD:'table-header-group',TBODY:'table-row-group',LI:'list-item'};
function forceVisible(){
  if(!bar3||!bar3.open) return;
  var body=bodyOf(bar3), isS7=(body!==bar3);
  if(getComputedStyle(bar3).display==='none') setI(bar3,'display','block');
  if(isS7){
    body.hidden=false; body.removeAttribute('hidden');
    setI(body,'display','block'); setI(body,'visibility','visible'); setI(body,'opacity','1');
    setI(body,'height','auto'); setI(body,'max-height','max(320px,var(--s7-h,70dvh))');
    setI(body,'overflow-y','auto'); setI(body,'padding','12px');
  }
  var els=body.querySelectorAll('*');
  for(var i=0;i<els.length;i++){
    var el=els[i];
    if(SKIP[el.tagName]||el.closest('#s8-brief')) continue;
    if(el.hasAttribute('data-s7-dup')||el.hasAttribute('data-s7-hidden')||el.hasAttribute('data-s8-hidden')) continue;
    if(el.tagName==='INPUT'&&el.type==='hidden') continue;
    if(!(el.textContent||'').trim()&&!el.querySelector('img,svg,canvas,input,textarea,button,select')) continue;
    if(el.hasAttribute('hidden')){el.hidden=false;el.removeAttribute('hidden');}
    var cs=getComputedStyle(el);
    if(cs.display==='none') setI(el,'display',INLINE[el.tagName]?'inline':(DISP[el.tagName]||'block'));
    if(cs.visibility==='hidden') setI(el,'visibility','visible');
    if(parseFloat(cs.opacity)===0) setI(el,'opacity','1');
    if(cs.maxHeight==='0px') setI(el,'max-height','none');
    if(cs.height==='0px'&&el.children.length) setI(el,'height','auto');
  }
}

/* ================= JSON 로드 ================= */
function fetchJson(name){
  var urls=BASES.map(function(b){return b+name+'?_='+Date.now();});
  urls.push('https://raw.githubusercontent.com/'+REPO+'/main/'+name+'?_='+Date.now());
  var i=0;
  function next(){
    if(i>=urls.length) return Promise.resolve(null);
    var u=urls[i++];
    return fetch(u,{cache:'no-store'})
      .then(function(r){if(!r.ok) throw new Error('http'); return r.text();})
      .then(function(t){return {data:JSON.parse(t.replace(/^\uFEFF/,'')),src:u};})
      .catch(next);
  }
  return next();
}

/* ================= 데이터 → 한국어 브리핑 ================= */
var TIME_RE=/(sync|updat|generat|snapshot|saved|last|time|date|stamp|ts$|동기화|갱신|시각)/i;
var VER_RE=/version|^ver$|_ver$|버전|generation/i;
function toMs(v){
  if(typeof v==='number') return v<1e12?v*1000:v;
  if(typeof v==='string'){
    if(/^\d{10,13}$/.test(v)) return toMs(+v);
    var d=Date.parse(v); if(!isNaN(d)) return d;
  }
  return null;
}
function fmtTime(v){
  var ms=toMs(v); if(ms==null) return String(v);
  var s;
  try{s=new Date(ms).toLocaleString('ko-KR',{timeZone:'Asia/Seoul',hour12:false});}catch(e){s=new Date(ms).toString();}
  var diff=Math.round((Date.now()-ms)/60000), rel='';
  if(diff>=0) rel=diff<1?' · 방금 전':diff<60?' · '+diff+'분 전':diff<1440?' · '+Math.floor(diff/60)+'시간 전':' · '+Math.floor(diff/1440)+'일 전';
  return s+' KST'+rel;
}
function bfs(root,test,maxD){
  var q=[{v:root,d:0}];
  while(q.length){
    var n=q.shift(), v=n.v;
    if(!isObj(v)||Array.isArray(v)) continue;
    var keys=Object.keys(v), i;
    for(i=0;i<keys.length;i++){ if(test(keys[i],v[keys[i]])) return v[keys[i]]; }
    if(n.d<maxD){ for(i=0;i<keys.length;i++){ if(isObj(v[keys[i]])) q.push({v:v[keys[i]],d:n.d+1}); } }
  }
  return undefined;
}
function findTime(o){return bfs(o,function(k,v){return TIME_RE.test(k)&&(typeof v==='string'||typeof v==='number')&&toMs(v)!=null;},3);}
function findVer(o){return bfs(o,function(k,v){return VER_RE.test(k)&&(typeof v==='string'||typeof v==='number');},3);}
function findBox(o,re,maxD){return bfs(o,function(k,v){return re.test(k)&&isObj(v);},maxD);}
function without(o,keys){var c={};Object.keys(o).forEach(function(k){if(keys.indexOf(k)<0) c[k]=o[k];});return c;}
var BRIEF_KEYS=['summary','desc','description','lesson','insight','change','event','action','note','rule','title','name','label','text','content','message','status','state','value'];
function brief(v,max){
  max=max||90; var t='';
  if(v==null) t='';
  else if(!isObj(v)) t=String(v);
  else if(Array.isArray(v)) t=v.slice(0,3).map(function(x){return brief(x,40);}).join(', ')+(v.length>3?' …(+'+(v.length-3)+')':'');
  else{
    var parts=[], i;
    for(i=0;i<BRIEF_KEYS.length&&parts.length<2;i++){
      var x=v[BRIEF_KEYS[i]]; if(x!=null&&!isObj(x)) parts.push(String(x));
    }
    if(!parts.length){
      Object.keys(v).slice(0,3).forEach(function(k){var y=v[k]; if(y==null||isObj(y)) return; parts.push(k+'='+y);});
    }
    t=parts.join(' · ');
  }
  t=t.replace(/\s+/g,' ').trim();
  return t.length>max?t.slice(0,max-1)+'…':t;
}
function stateIcon(v){
  var t=v;
  if(isObj(v)&&!Array.isArray(v)){
    var ks=['status','state','ok','active','enabled','result','level'];
    t=undefined;
    for(var i=0;i<ks.length;i++){ if(v[ks[i]]!=null){t=v[ks[i]];break;} }
  }
  if(t===true) return '✅'; if(t===false) return '❌';
  var s=String(t==null?'':t).toLowerCase();
  if(/^(ok|pass|passed|active|on|true|good|green|enabled|ready|armed)$|정상|활성|완료|통과|✅|🟢/.test(s)) return '✅';
  if(/^(fail|failed|off|false|error|bad|red|disabled)$|실패|오류|비활성|위험|❌|🔴/.test(s)) return '❌';
  if(/warn|주의|대기|경고|🟡|pending/.test(s)) return '⚠️';
  return '▪️';
}
function listFrom(c){
  var out=[];
  if(Array.isArray(c)){
    c.forEach(function(it,i){
      var id=isObj(it)?(it.id||it.code||it.name||it.key||it.title||it.label):null;
      out.push([id!=null?String(id):null,it,i]);
    });
  }else if(isObj(c)){
    Object.keys(c).forEach(function(k,i){out.push([k,c[k],i]);});
  }
  return out;
}
function getAntibodies(s){
  var c=findBox(s,/antibod|항체|immun/i,3), out=[];
  if(c){
    out=listFrom(c).map(function(p){return [p[0]||('R'+(p[2]+1)),p[1]];});
  }else{
    (function collect(o,d){
      if(!isObj(o)||Array.isArray(o)||d>3) return;
      Object.keys(o).forEach(function(k){
        if(/^R\d{1,2}$/i.test(k)) out.push([k.toUpperCase(),o[k]]); else collect(o[k],d+1);
      });
    })(s,0);
  }
  if(out.length&&out.every(function(p){return /^R\d{1,2}$/i.test(p[0]);})){
    out.sort(function(a,b){return parseInt(a[0].replace(/\D/g,''),10)-parseInt(b[0].replace(/\D/g,''),10);});
  }
  return out;
}
function getSix(s){
  var c=findBox(s,/청사|cheongsa|chungsa|six|indicator|palace|bureau|tower/i,3);
  if(!c) return [];
  return listFrom(c).slice(0,6).map(function(p){return [p[0]||((p[2]+1)+'청사'),p[1]];});
}
function itemTime(it){
  if(!isObj(it)) return null;
  var ks=['time','timestamp','at','date','ts','created_at','updated_at','when','시각'];
  for(var i=0;i<ks.length;i++){ if(it[ks[i]]!=null&&toMs(it[ks[i]])!=null) return it[ks[i]]; }
  return null;
}
function getEvo(e){
  var arr=null;
  if(Array.isArray(e)) arr=e;
  else if(isObj(e)){
    arr=bfs(e,function(k,v){return /evolution|history|log|entries|records|timeline|events|진화|기록/i.test(k)&&Array.isArray(v);},2);
    if(!arr){
      var c=findBox(e,/evolution|history|진화|기록/i,2);
      if(c&&!Array.isArray(c)) arr=Object.keys(c).map(function(k){return isObj(c[k])?Object.assign({id:k},c[k]):{id:k,text:String(c[k])};});
    }
  }
  return arr;
}
function topKeys(o,title,L){
  if(!isObj(o)||Array.isArray(o)) return;
  L.push(''); L.push(title);
  Object.keys(o).slice(0,12).forEach(function(k){L.push('  · '+k+': '+(brief(o[k],80)||'(비어 있음)'));});
}
function compose(snap,evo){
  var L=[], s=snap?snap.data:null, e=evo?evo.data:null;
  L.push('🛰️ 르곤-알파 실시간 브리핑 전문 (자동)');
  L.push('══════════════════════');
  L.push('🕒 화면 갱신: '+fmtTime(Date.now()));
  if(!s&&!e){
    L.push('');
    L.push('⚠️ rgon_brain_snapshot.json / evolution_memory.json 을 불러오지 못했습니다.');
    L.push('   · 네트워크 연결과 GitHub Pages 배포 상태를 확인하세요.');
    L.push('   · [🔄 새로고침]으로 다시 시도할 수 있습니다.');
    return L.join('\n');
  }
  var t=(s&&findTime(s)); if(t==null&&e&&!Array.isArray(e)) t=findTime(e);
  L.push('');
  L.push('🔄 최신 동기화 시각: '+(t!=null?fmtTime(t):'정보 없음'));
  var v=(s&&findVer(s)); if(v==null&&e&&!Array.isArray(e)) v=findVer(e);
  L.push('🧠 두뇌 버전: '+(v!=null?v:'정보 없음'));

  var missing=false;
  L.push(''); L.push('🛡️ 항체 R1~R14 상태');
  var ab=s?getAntibodies(s):[];
  if(ab.length){
    var okc=0;
    ab.forEach(function(p){
      var ic=stateIcon(p[1]); if(ic==='✅') okc++;
      var tx=(typeof p[1]==='boolean')?'':brief(p[1],80);
      L.push('  '+ic+' '+p[0]+(tx?' — '+tx:''));
    });
    L.push('  ▶ 정상 '+okc+' / 전체 '+ab.length);
  }else{L.push('  (항체 데이터 없음)'); missing=true;}

  L.push(''); L.push('🏛️ 1~6청사 실시간 요약');
  var six=s?getSix(s):[];
  if(six.length){
    six.forEach(function(p){
      var val=p[1], tx;
      if(isObj(val)&&!Array.isArray(val)) tx=brief(without(val,['name','title','label','id']),110)||brief(val,110);
      else tx=brief(val,110);
      L.push('  🏛️ '+p[0]+(tx?' — '+tx:''));
    });
  }else{L.push('  (청사 데이터 없음)'); missing=true;}

  L.push(''); L.push('🧬 최근 진화 기록');
  var evs=e?getEvo(e):null;
  if(evs&&evs.length){
    var withT=evs.filter(function(x){return itemTime(x)!=null;});
    var ord=evs.slice();
    if(withT.length===evs.length){ ord.sort(function(a,b){return toMs(itemTime(a))-toMs(itemTime(b));}); }
    var last=ord.slice(-8).reverse();
    last.forEach(function(it){
      var tt=itemTime(it);
      var tx=isObj(it)?brief(without(it,['time','timestamp','at','date','ts','created_at','updated_at','when','시각']),110):brief(it,110);
      L.push('  • '+(tt!=null?'['+fmtTime(tt).replace(/ KST.*$/,'')+'] ':'')+(tx||'(내용 없음)'));
    });
    L.push('  ▶ 누적 '+evs.length+'건 중 최근 '+last.length+'건 표시');
  }else{L.push('  (진화 기록 없음)'); if(e) missing=true;}

  if(missing){
    if(s) topKeys(s,'📦 rgon_brain_snapshot 주요 항목',L);
    if(e&&!Array.isArray(e)) topKeys(e,'📦 evolution_memory 주요 항목',L);
  }
  L.push('');
  L.push('출처: '+(snap?snap.src.replace(/\?.*$/,''):'—')+(evo?'  |  '+evo.src.replace(/\?.*$/,''):''));
  return L.join('\n');
}

/* ================= 브리핑 박스 ================= */
function copyText(t){
  try{ if(navigator.clipboard&&navigator.clipboard.writeText) return navigator.clipboard.writeText(t); }catch(e){}
  var ta=document.createElement('textarea'); ta.value=t; document.body.appendChild(ta); ta.select();
  try{document.execCommand('copy');}catch(e){} ta.remove(); return Promise.resolve();
}
function ensureBox(){
  var body=bodyOf(bar3), box=document.getElementById('s8-brief');
  if(box&&box.parentNode!==body){box.remove();box=null;}
  if(!box){
    box=document.createElement('div'); box.id='s8-brief';
    var tools=document.createElement('div'); tools.className='s8-tools';
    var b1=document.createElement('button'); b1.type='button'; b1.textContent='🔄 새로고침';
    b1.addEventListener('click',function(ev){ev.stopPropagation();renderBriefing(true);});
    var b2=document.createElement('button'); b2.type='button'; b2.textContent='📋 전문 복사';
    b2.addEventListener('click',function(ev){
      ev.stopPropagation();
      var p=box.querySelector('.s8-pre'); copyText(p?p.textContent:'');
      b2.textContent='✅ 복사됨'; setTimeout(function(){b2.textContent='📋 전문 복사';},1500);
    });
    tools.appendChild(b1); tools.appendChild(b2);
    var pre=document.createElement('pre'); pre.className='s8-pre';
    box.appendChild(tools); box.appendChild(pre);
    if(body===bar3){var sm=bar3.querySelector(':scope>summary'); bar3.insertBefore(box,sm?sm.nextSibling:bar3.firstChild);}
    else body.insertBefore(box,body.firstChild);
  }
  return box;
}
function renderBriefing(force){
  if(!bar3) return;
  var now=Date.now();
  if(!force&&now-lastAt<700) return;
  lastAt=now;
  var box=ensureBox(), pre=box.querySelector('.s8-pre'), my=++token;
  if(!pre.textContent) pre.textContent='⏳ 최신 브리핑을 불러오는 중...';
  Promise.all([fetchJson(FILES.snap),fetchJson(FILES.evo)]).then(function(r){
    if(my!==token) return;
    pre.textContent=compose(r[0],r[1]);
    forceVisible();
  }).catch(function(){
    if(my!==token) return;
    pre.textContent='⚠️ 브리핑 렌더링 중 오류가 발생했습니다. [🔄 새로고침]을 눌러 주세요.';
  });
}

/* ================= 3번 바 열기(아코디언 연동) ================= */
function openBriefing(){
  bar3=bar3||findBar3(); if(!bar3) return;
  if(typeof window.s7Open==='function'&&bar3.classList.contains('s7-bar')) window.s7Open(3);
  else{
    document.querySelectorAll('details.s7-bar').forEach(function(o){if(o!==bar3){o.open=false;o.removeAttribute('open');}});
  }
  bar3.open=true;
  forceVisible(); renderBriefing(false);
  try{bar3.scrollIntoView({block:'start',behavior:'smooth'});}catch(e){}
}
window.s8Open=openBriefing;

function wireBar3(){
  if(!bar3||bar3Wired) return; bar3Wired=true;
  bar3.addEventListener('toggle',function(){
    if(bar3.open){forceVisible();renderBriefing(false);}
  });
  var tmr=null;
  new MutationObserver(function(muts){
    var relevant=muts.some(function(m){
      var n=m.target; if(n.nodeType!==1) n=n.parentElement;
      return !(n&&n.closest&&n.closest('#s8-brief'));
    });
    if(!relevant) return;
    clearTimeout(tmr);
    tmr=setTimeout(function(){if(bar3.open) forceVisible();},250);
  }).observe(bar3,{attributes:true,attributeFilter:['open'],childList:true,subtree:true});
  var sm=bar3.querySelector(':scope>summary');
  if(sm) sm.addEventListener('click',function(){setTimeout(function(){if(bar3.open) forceVisible();},60);});
  if(bar3.open){forceVisible();renderBriefing(true);}
}

/* ================= 잔여 UI 정리 ================= */
function parseRGB(s){
  if(!s) return null;
  var m=s.match(/rgba?\(([^)]+)\)/); if(!m) return null;
  var p=m[1].split(/[\s,\/]+/).filter(Boolean).map(parseFloat);
  var a=p.length>3?p[3]:1; if(a>1) a=a/100;
  return {r:p[0],g:p[1],b:p[2],a:a};
}
function isBlue(c){return !!c&&c.a>0.2&&c.b>c.r+40&&c.b>=c.g;}
function isGold(c){return !!c&&c.a>0.2&&c.r>=170&&c.g>=120&&c.g<=230&&c.b<=100&&(c.r-c.b)>=110;}
function hideEl(el,tag){el.style.setProperty('display','none','important');el.setAttribute('data-s8-hidden',tag);}

function hideTabs(){
  var cand=[].slice.call(document.querySelectorAll('button,[role=tab],a,[onclick],div,span'));
  var A=[],B=[];
  cand.forEach(function(el){
    if(inUi(el)||isOverlay(el)||el.closest('[data-s8-hidden],[data-s7-removed]')) return;
    var t=norm(el.textContent); if(t.length>40) return;
    var ctl=el.closest('button,[role=tab],a,[onclick]')||el;
    if(inUi(ctl)||isOverlay(ctl)) return;
    if(t.indexOf('1번')>-1&&t.indexOf('알파 대화창')>-1&&A.indexOf(ctl)<0) A.push(ctl);
    if(t.indexOf('2번')>-1&&/AI 지시|지시·분배|지시/.test(t)&&B.indexOf(ctl)<0) B.push(ctl);
  });
  if(!A.length&&!B.length) return;
  if(A.length&&B.length){
    var p=A[0].parentElement;
    while(p&&p!==document.body&&!p.contains(B[0])) p=p.parentElement;
    if(p&&p!==document.body&&!p.contains(document.getElementById('s7-root'))&&norm(p.textContent).length<=100){
      hideEl(p,'tabs'); return;
    }
  }
  A.concat(B).forEach(function(c){hideEl(c,'tab-btn');});
}

function hideStrays(){
  var root=document.getElementById('s7-root'); if(!root) return;
  var bar0=root.querySelector('details.s7-bar[data-s7="0"]');
  var rr=root.getBoundingClientRect();
  var els=document.body.querySelectorAll('div,button,span,a,section,form,aside,label');
  var golds=[];
  for(var i=0;i<els.length;i++){
    var el=els[i];
    if(el.closest('#s7-root')||el.contains(root)||isOverlay(el)||el.closest('[data-s8-hidden],[data-s7-removed],[data-s7-hidden]')) continue;
    var cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden') continue;
    var r=el.getBoundingClientRect(); if(r.width<8||r.height<6) continue;
    var fixed=(cs.position==='fixed');
    var after=!!(root.compareDocumentPosition(el)&Node.DOCUMENT_POSITION_FOLLOWING);
    if(!(after||fixed)) continue;
    if(!fixed&&r.top<rr.top-4) continue;

    /* (1) 빈 파란 타원 버튼 */
    var txt=(el.textContent||'').replace(/\s+/g,'');
    if(!txt&&r.height>=14&&r.width>=20&&r.height<=80&&!el.querySelector('img,svg,canvas,input,textarea,select,video')){
      var pb=getComputedStyle(el,'::before').content, pa=getComputedStyle(el,'::after').content;
      var hasPseudo=function(c){return c&&c!=='none'&&c!=='normal'&&c!=='""'&&c!=="''";};
      if(!hasPseudo(pb)&&!hasPseudo(pa)){
        var rad=parseFloat(cs.borderTopLeftRadius)||0;
        var bg=parseRGB(cs.backgroundColor), bc=parseRGB(cs.borderTopColor);
        var blue=isBlue(bg)||((parseFloat(cs.borderTopWidth)||0)>0&&isBlue(bc));
        if(blue&&rad>=Math.min(r.height/2,12)){hideEl(el,'blue-oval');continue;}
      }
    }
    /* (2) 금색 테두리 잔여 박스 */
    var goldSide=false;
    if(((parseFloat(cs.borderTopWidth)||0)>=1&&isGold(parseRGB(cs.borderTopColor)))||((parseFloat(cs.borderLeftWidth)||0)>=1&&isGold(parseRGB(cs.borderLeftColor)))) goldSide=true;
    if(goldSide){
      if(/수거|전광판/.test(el.textContent||'')) continue;
      if(el.querySelector('details.s7-bar')) continue;
      golds.push(el);
    }
  }
  golds=golds.filter(function(g){return !golds.some(function(o){return o!==g&&o.contains(g);});});
  golds.forEach(function(g){
    var inp=g.querySelector('textarea,input[type=text],input:not([type])');
    var b0=bar0?bodyOf(bar0):null;
    if(inp&&b0&&!b0.querySelector('textarea,input[type=text],input:not([type])')){
      b0.appendChild(g);
      setI(g,'position','sticky'); setI(g,'bottom','0'); setI(g,'top','auto'); setI(g,'left','auto'); setI(g,'right','auto');
      setI(g,'transform','none'); setI(g,'width','auto'); setI(g,'margin','0'); setI(g,'z-index','5');
      g.setAttribute('data-s8-moved','1');
    }else{
      hideEl(g,'gold-box');
    }
  });
}

function cleanup(){
  if(busy) return; busy=true;
  try{hideTabs();}catch(e){}
  try{hideStrays();}catch(e){}
  try{if(bar3&&bar3.open) forceVisible();}catch(e){}
  busy=false;
}
window.s8Cleanup=cleanup;

/* ================= 훅 / 초기화 ================= */
function hook(){
  if(hooked) return; hooked=true;
  document.addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('button,a,[role=button],[onclick]');
    if(!b||inUi(b)||isOverlay(b)) return;
    var t=norm(b.textContent);
    if(t.length>16||t.indexOf('브리핑')<0) return;
    setTimeout(openBriefing,40);
  },true);
  var root=document.getElementById('s7-root');
  if(root) root.addEventListener('toggle',function(ev){
    var d=ev.target; if(!d||!d.classList||!d.classList.contains('s7-bar')) return;
    setTimeout(cleanup,60);
  },true);
}
function setup(){
  bar3=findBar3();
  wireBar3(); hook(); cleanup();
  [600,1500,3000,6000,10000].forEach(function(ms){setTimeout(cleanup,ms);});
  var tmr=null;
  new MutationObserver(function(muts){
    var rel=muts.some(function(m){
      var n=m.target; if(n.nodeType!==1) n=n.parentElement;
      return !(n&&n.closest&&n.closest('#s8-brief,#s7-toast'));
    });
    if(!rel) return;
    clearTimeout(tmr); tmr=setTimeout(cleanup,900);
  }).observe(document.body,{childList:true,subtree:true});
}
function init(){
  var tries=0;
  (function wait(){
    var b=findBar3(), root=document.getElementById('s7-root');
    if((b&&root)||tries>=24) setup(); else{tries++;setTimeout(wait,500);}
  })();
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
else init();
})();
"""


# ----------------------------------------------------------------------------
# 유틸
# ----------------------------------------------------------------------------
def build_block():
    js = JS.replace("__REPO__", REPO)
    return "\n%s\n<style id=\"s8-style\">%s</style>\n<script id=\"s8-script\">%s</script>\n%s\n" % (
        BEGIN, CSS, js, END)


def patch_file(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        orig = f.read()
    if "STEP7_BEGIN" not in orig:
        print("  ⚠ Step7 블록이 없습니다(%s) — Step8은 단독 동작(대체 탐색)으로 적용합니다." % os.path.basename(path))
    html = BLOCK_RE.sub("", orig)
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
    print("  ✓ 패치 완료: %s (백업 %s)" % (path, os.path.basename(bak)))
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
