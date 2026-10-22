#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""step2_allinone_upgrade.py  (Python 3 표준 라이브러리 전용)

1) 크롬 확장 흡수창(chrome_omni_link_ext/content.js)에 [🧹 지우기] / [🗑️ 전체 지우기] 복원
   - 마커 /* === [RGON-CLEAR-BTNS-START] === */ ~ /* === [RGON-CLEAR-BTNS-END] === */ 로 추가·갱신(멱등)
2) 독대실 HTML 상단 바: Genspark 내부 4대 AI 직통 + 고정 주소 설정 + 독대실 자체 지우기 버튼
   - <!-- === [RGON-STEP1-MOBILE-UI-START] === --> ~ END 블록 교체(없으면 퀵 네비/ body 바로 뒤에 삽입)
3) 무료 브리핑 칩 5종 (rgon_brain_snapshot.json / evolution_memory.json 을 fetch 로 읽어 카드 출력)
   - 상태바 문구 -> v6.2.0-genspark · 항체 R1~R14 (14종)
4) 수정 전 모든 대상 파일 타임스탬프 .bak 백업 / id 보존 검증 / node 가 있으면 JS 문법 검사
5) git add -A -> commit -> pull --rebase -X ours -> push 순차 실행

참고: 백업 파일(*.bak_*)이 저장소에 올라가지 않도록 .git/info/exclude 에 패턴을 추가합니다.
      'pull --rebase -X ours' 는 요청 사항대로 실행하며, 충돌 시 rebase 중 'ours'는 원격(upstream) 쪽입니다.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DEFAULT_ROOT = Path("C:/Users/sangi/Downloads/shin-agent")
ROOT = DEFAULT_ROOT if DEFAULT_ROOT.is_dir() else Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
COMMIT_MSG = "feat(allinone): Genspark AI links + restore Clear/ClearAll buttons + live chips"

HTML_TARGETS = [
    "rgon_alpha_chat.html",
    "dashboard/rgon_alpha_chat.html",
    "docs/rgon_alpha_chat.html",
    "rgon_alpha_audience.html",
]
JS_TARGET = "chrome_omni_link_ext/content.js"

NEW_BADGE = "v6.2.0-genspark · 항체 R1~R14 (14종)"
BADGE_RES = [
    re.compile(r"v6\.\d+\.\d+-(?:step\d+|genspark)\s*[·•∙・|/\-–—]?\s*항체\s*R1~R\d+\s*\(\s*\d+\s*종\s*\)"),
]

HTML_START = "<!-- === [RGON-STEP1-MOBILE-UI-START] === -->"
HTML_END = "<!-- === [RGON-STEP1-MOBILE-UI-END] === -->"
JS_START = "/* === [RGON-CLEAR-BTNS-START] === */"
JS_END = "/* === [RGON-CLEAR-BTNS-END] === */"

# ───────────────────────── 독대실 HTML 블록 ─────────────────────────
HTML_BODY = r'''
<style id="rgon-step2-style">
#rgon-cmd-wrap{box-sizing:border-box;width:100%;margin:0;padding:6px 8px;background:rgba(10,14,24,.96);
  border-bottom:1px solid rgba(255,255,255,.12);color:#eaf0ff;font-size:13px;line-height:1.35}
#rgon-cmd-wrap *{box-sizing:border-box}
#rgon-cmd-bar,#rgon-cmd-tools,#rgon-chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 6px 0}
#rgon-cmd-wrap button,.rgon-bottom-clear button{cursor:pointer;font-size:12px;font-weight:600;line-height:1.2;
  padding:7px 10px;border-radius:999px;color:#eaf0ff;background:rgba(255,255,255,.09);
  border:1px solid rgba(255,255,255,.18);-webkit-tap-highlight-color:transparent}
#rgon-cmd-wrap button:active,.rgon-bottom-clear button:active{background:rgba(255,255,255,.22)}
#rgon-cmd-bar button[data-rgon-act^="ai:"]{flex:1 1 auto}
#rgon-cmd-tools button{flex:1 1 auto}
#rgon-cmd-tools button[data-rgon-act="clear-all"],.rgon-bottom-clear button[data-rgon-act="clear-all"]{border-color:rgba(255,120,120,.55)}
#rgon-chips button{background:rgba(80,140,255,.16);border-color:rgba(120,170,255,.45)}
#rgon-gs-settings{margin:0 0 6px 0}
#rgon-gs-settings summary{cursor:pointer;font-size:12px;font-weight:600;padding:4px 2px}
.rgon-gs-row{display:flex;gap:6px;align-items:center;margin:4px 0}
.rgon-gs-row label{flex:0 0 74px;font-size:12px}
.rgon-gs-row input{flex:1 1 auto;min-width:0;font-size:16px;padding:6px 8px;border-radius:8px;
  border:1px solid rgba(255,255,255,.25);background:rgba(0,0,0,.35);color:#fff}
#rgon-toast{display:none;margin:0 0 6px 0;padding:6px 10px;border-radius:8px;font-size:12px;background:rgba(40,160,90,.28);
  border:1px solid rgba(80,200,130,.5)}
#rgon-brief-cards:empty{display:none}
.rgon-brief-card{margin:6px 0;padding:8px 10px;border-radius:10px;background:rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.16);font-size:12.5px;color:#eaf0ff}
.rgon-brief-card .t{font-weight:700;margin-bottom:4px}
.rgon-brief-card .m{opacity:.65;font-size:11px;margin-bottom:4px}
.rgon-brief-card pre{margin:0;white-space:pre-wrap;word-break:break-word;font:inherit}
.rgon-bottom-clear{display:flex;gap:6px;flex-wrap:wrap;padding:4px 8px;box-sizing:border-box;width:100%}
.rgon-bottom-clear button{flex:1 1 auto}
@media (max-width:768px){
  #rgon-cmd-wrap button{padding:6px 8px;font-size:11.5px}
  #rgon-cmd-bar button[data-rgon-act^="ai:"]{flex:1 1 calc(50% - 6px)}
}
</style>
<div id="rgon-cmd-wrap">
  <div id="rgon-cmd-bar">
    <button type="button" data-rgon-act="copy">📋 지시문 복사</button>
    <button type="button" data-rgon-act="ai:rgon">🔵 르곤(Genspark)</button>
    <button type="button" data-rgon-act="ai:claude">🤖 클로드(Genspark)</button>
    <button type="button" data-rgon-act="ai:gpt">⚡ GPT(Genspark)</button>
    <button type="button" data-rgon-act="ai:grok">🎯 Grok(Genspark)</button>
  </div>
  <div id="rgon-cmd-tools">
    <button type="button" data-rgon-act="clear-input">🧹 입력창 지우기</button>
    <button type="button" data-rgon-act="clear-all">🗑️ 대화·흡수 전체 지우기</button>
  </div>
  <details id="rgon-gs-settings">
    <summary>🔗 내 젠스파크 채팅방 고정 주소 설정</summary>
    <div class="rgon-gs-row"><label for="rgon-url-rgon">🔵 르곤</label><input id="rgon-url-rgon" data-rgon-own="1" type="url" placeholder="https://www.genspark.ai/..."><button type="button" data-rgon-act="save:rgon">저장</button></div>
    <div class="rgon-gs-row"><label for="rgon-url-claude">🤖 클로드</label><input id="rgon-url-claude" data-rgon-own="1" type="url" placeholder="https://www.genspark.ai/..."><button type="button" data-rgon-act="save:claude">저장</button></div>
    <div class="rgon-gs-row"><label for="rgon-url-gpt">⚡ GPT</label><input id="rgon-url-gpt" data-rgon-own="1" type="url" placeholder="https://www.genspark.ai/..."><button type="button" data-rgon-act="save:gpt">저장</button></div>
    <div class="rgon-gs-row"><label for="rgon-url-grok">🎯 Grok</label><input id="rgon-url-grok" data-rgon-own="1" type="url" placeholder="https://www.genspark.ai/..."><button type="button" data-rgon-act="save:grok">저장</button></div>
  </details>
  <div id="rgon-chips" aria-label="무료 실시간 브리핑 칩">
    <button type="button" data-rgon-act="chip:all">📊 6청사 종합브리핑</button>
    <button type="button" data-rgon-act="chip:d1">📈 1청사 NVDA·시트</button>
    <button type="button" data-rgon-act="chip:d3">🎬 3청사 미디어·틱톡</button>
    <button type="button" data-rgon-act="chip:evo">🧬 R1~R14 항체·진화</button>
    <button type="button" data-rgon-act="chip:tts">🔊 전체 음성브리핑(TTS)</button>
  </div>
  <div id="rgon-toast" role="status"></div>
  <div id="rgon-brief-cards"></div>
</div>
<script id="rgon-step2-script">
(function(){
  "use strict";
  if(window.__rgonStep2){return;}
  window.__rgonStep2=true;
  var $=function(id){return document.getElementById(id);};
  var KEYS={rgon:"rgon_gs_url_rgon",claude:"rgon_gs_url_claude",gpt:"rgon_gs_url_gpt",grok:"rgon_gs_url_grok"};
  var DEFAULT_URL="https://www.genspark.ai/agents";
  var GS_OK=/^https:\/\/([a-z0-9-]+\.)?genspark\.ai\//i;
  var CAP_RE=/(omni.*(captur|cache|buffer|queue|absorb)|captured|absorb)/i;
  var KEEP_RE=/token|key|secret|password|github|rgon_gs_url/i;
  var lastAll="";

  function lsGet(k){try{return localStorage.getItem(k)||"";}catch(e){return "";}}
  function lsSet(k,v){try{if(v){localStorage.setItem(k,v);}else{localStorage.removeItem(k);}return true;}catch(e){return false;}}
  function toast(msg){
    var t=$("rgon-toast");if(!t){return;}
    t.textContent=msg;t.style.display="block";
    clearTimeout(toast._t);toast._t=setTimeout(function(){t.style.display="none";},2800);
  }

  /* ── 입력창 / 피드 탐색 ── */
  function userInputs(){
    return [].slice.call(document.querySelectorAll("textarea,input[type=text],input:not([type]),input[type=search]"))
      .filter(function(e){return !e.closest("#rgon-cmd-wrap")&&e.type!=="hidden"&&!e.disabled;});
  }
  function lastInput(){var a=userInputs();return a.length?a[a.length-1]:null;}
  var FEED=["#chat-feed","#chatFeed","#chat-log","#chatLog","#chat-messages","#chatMessages","#messages","#chatBox","#chat-box",
    ".chat-feed",".chat-log",".chat-messages",".messages","[id*='feed' i]","[id*='chat' i][id*='log' i]",
    "[id*='chat' i][id*='msg' i]","[class*='chat' i][class*='feed' i]","[class*='chat' i][class*='messages' i]","#chat"];
  function findFeed(){
    var inp=lastInput();
    for(var i=0;i<FEED.length;i++){
      var els=[];try{els=document.querySelectorAll(FEED[i]);}catch(e){continue;}
      for(var j=0;j<els.length;j++){
        var el=els[j];
        if(el.closest("#rgon-cmd-wrap")||el.closest("#rgon-mobile-quick-nav")||(inp&&el.contains(inp))){continue;}
        return el;
      }
    }
    return null;
  }
  function setEmpty(el){
    var proto=el.tagName==="TEXTAREA"?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
    var d=Object.getOwnPropertyDescriptor(proto,"value");
    if(d&&d.set){d.set.call(el,"");}else{el.value="";}
    el.dispatchEvent(new Event("input",{bubbles:true}));
  }

  /* ── 지우기 ── */
  function clearInput(silent){
    var a=userInputs();
    a.forEach(setEmpty);
    if(a.length){try{a[a.length-1].focus();}catch(e){}}
    if(!silent){toast("🧹 입력창을 비웠습니다.");}
  }
  function purgeStorage(store){
    try{
      var del=[];
      for(var i=0;i<store.length;i++){var k=store.key(i);if(CAP_RE.test(k)&&!KEEP_RE.test(k)){del.push(k);}}
      del.forEach(function(k){store.removeItem(k);});
      return del.length;
    }catch(e){return 0;}
  }
  function clearAll(){
    if(!window.confirm("대화창·흡수 버퍼를 모두 비울까요?\n(젠스파크 주소 설정은 유지됩니다)")){return;}
    clearInput(true);
    [].slice.call(document.querySelectorAll(".rgon-brief-card")).forEach(function(n){n.remove();});
    var feed=findFeed();
    if(feed){feed.textContent="";}
    try{
      var c=window.__omniCaptured;
      if(Array.isArray(c)){c.length=0;}else if(c&&typeof c==="object"){Object.keys(c).forEach(function(k){delete c[k];});}
    }catch(e){}
    var n=purgeStorage(window.localStorage)+purgeStorage(window.sessionStorage);
    lastAll="";
    try{if(window.speechSynthesis){window.speechSynthesis.cancel();}}catch(e){}
    toast("🗑️ 대화·흡수 전체 초기화 완료! (캐시 "+n+"건 삭제)");
  }

  /* ── 복사 ── */
  function copyText(txt){
    if(navigator.clipboard&&window.isSecureContext){
      return navigator.clipboard.writeText(txt).then(function(){return true;},function(){return legacy(txt);});
    }
    return Promise.resolve(legacy(txt));
  }
  function legacy(txt){
    try{
      var ta=document.createElement("textarea");ta.value=txt;ta.setAttribute("readonly","");
      ta.style.cssText="position:fixed;top:-1000px;opacity:0";document.body.appendChild(ta);ta.select();
      var ok=document.execCommand("copy");ta.remove();return ok;
    }catch(e){return false;}
  }
  function directiveText(){
    var inp=lastInput();
    if(inp&&inp.value.trim()){return inp.value.trim();}
    if(typeof window.RGON_DIRECTIVE==="string"&&window.RGON_DIRECTIVE.trim()){return window.RGON_DIRECTIVE.trim();}
    var el=document.querySelector("[id*='directive' i],[id*='instruction' i],[id*='top1' i]");
    if(el&&!el.closest("#rgon-cmd-wrap")){var t=(el.value||el.textContent||"").trim();if(t){return t;}}
    return "";
  }

  /* ── 젠스파크 직통 ── */
  function goAI(name){
    var u=lsGet(KEYS[name]);
    location.href=(u&&GS_OK.test(u))?u:DEFAULT_URL;
  }
  function loadSettings(){
    Object.keys(KEYS).forEach(function(n){var i=$("rgon-url-"+n);if(i){i.value=lsGet(KEYS[n]);}});
  }
  function saveSetting(name){
    var i=$("rgon-url-"+name);if(!i){return;}
    var v=i.value.trim();
    if(v&&!GS_OK.test(v)){toast("⚠️ genspark.ai 주소(https://...)만 저장할 수 있습니다.");return;}
    toast(lsSet(KEYS[name],v)?(v?"✅ 저장했습니다: "+name:"🧹 "+name+" 주소를 삭제했습니다."):"⚠️ 저장 실패(브라우저 저장소 차단)");
  }

  /* ── 브리핑 ── */
  async function getJSON(name){
    var urls=["./"+name,"../"+name];
    for(var i=0;i<urls.length;i++){
      try{var r=await fetch(urls[i],{cache:"no-store"});if(r.ok){return await r.json();}}catch(e){}
    }
    return null;
  }
  function flat(v,p,d,max,out){
    if(v===null||v===undefined||out.length>500){return;}
    if(Array.isArray(v)){
      out.push(p+": ["+v.length+"개]");
      if(d<max){v.slice(0,3).forEach(function(x,i){flat(x,p+"["+i+"]",d+1,max,out);});}
      return;
    }
    if(typeof v==="object"){
      if(d>=max){out.push(p+": {"+Object.keys(v).length+"개 항목}");return;}
      Object.keys(v).forEach(function(k){flat(v[k],p?p+"."+k:k,d+1,max,out);});
      return;
    }
    out.push(p+": "+String(v).replace(/\s+/g," ").slice(0,140));
  }
  function lines(obj,label,max){var o=[];if(obj!==null&&obj!==undefined){flat(obj,label,0,max,o);}return o;}
  function pick(all,re,limit){
    var m=all.filter(function(l){return re.test(l);});
    return m.slice(0,limit);
  }
  function addCard(title,body){
    var card=document.createElement("div");card.className="rgon-brief-card";
    var t=document.createElement("div");t.className="t";t.textContent=title;
    var m=document.createElement("div");m.className="m";
    m.textContent=new Date().toLocaleString("ko-KR")+" · 무료 실시간(JSON)";
    var pre=document.createElement("pre");pre.textContent=body;
    card.appendChild(t);card.appendChild(m);card.appendChild(pre);
    var feed=findFeed();
    (feed||$("rgon-brief-cards")).appendChild(card);
    if(feed){feed.scrollTop=feed.scrollHeight;}
    try{card.scrollIntoView({block:"nearest",behavior:"smooth"});}catch(e){}
  }
  async function brief(kind){
    var snap=await getJSON("rgon_brain_snapshot.json");
    var evo=await getJSON("evolution_memory.json");
    if(snap===null&&evo===null){
      addCard("⚠️ 브리핑 데이터 없음","rgon_brain_snapshot.json / evolution_memory.json 을 읽지 못했습니다.\n같은 폴더에 두 파일이 배포되어 있는지 확인하세요.");
      return;
    }
    var all=[].concat(lines(snap,"snapshot",2),lines(evo,"evolution",2));
    var deep=[].concat(lines(snap,"snapshot",4),lines(evo,"evolution",4));
    var title,body;
    if(kind==="all"||kind==="tts"){
      title="📊 6청사 종합브리핑";body=all.slice(0,22).join("\n");
      lastAll=title+"\n"+body;
      if(kind==="all"){addCard(title,body||"(표시할 항목 없음)");return;}
      speak(lastAll);return;
    }
    var re,limit=18;
    if(kind==="d1"){title="📈 1청사 NVDA·시트";re=/nvda|sheet|시트|stock|trading|주식|1청사|dept1|d1\b/i;}
    else if(kind==="d3"){title="🎬 3청사 미디어·틱톡";re=/media|tiktok|틱톡|video|미디어|3청사|dept3|d3\b/i;}
    else{title="🧬 R1~R14 항체·진화";re=/\bR\d{1,2}\b|antibod|항체|evolution|진화|step|version/i;}
    var m=pick(deep,re,limit);
    body=m.length?m.join("\n"):("일치하는 항목이 없어 상위 항목을 표시합니다.\n"+all.slice(0,10).join("\n"));
    addCard(title,body);
  }
  function speak(text){
    var s=window.speechSynthesis;
    if(!s){toast("⚠️ 이 브라우저는 음성 합성을 지원하지 않습니다.");return;}
    if(s.speaking){s.cancel();toast("🔇 음성 브리핑을 정지했습니다.");return;}
    var u=new SpeechSynthesisUtterance(text.replace(/[\[\]{}]/g," ").slice(0,1200));
    u.lang="ko-KR";u.rate=1.0;
    s.speak(u);toast("🔊 음성 브리핑 재생 중… (다시 누르면 정지)");
  }

  /* ── 하단 입력창 옆 지우기 버튼 ── */
  function mountBottom(){
    if(document.querySelector("[data-rgon-bottom-clear]")){return;}
    var inp=lastInput();if(!inp){return;}
    var row=inp.parentElement;
    if(!row||row===document.body||row===document.documentElement||!row.parentNode){return;}
    var w=document.createElement("div");
    w.className="rgon-bottom-clear";w.setAttribute("data-rgon-bottom-clear","1");
    w.innerHTML='<button type="button" data-rgon-act="clear-input">🧹 입력창 지우기</button>'+
                '<button type="button" data-rgon-act="clear-all">🗑️ 대화·흡수 전체 지우기</button>';
    row.parentNode.insertBefore(w,row);
  }

  /* ── 배지 문구 보정 ── */
  var BADGE_RE=/v6\.\d+\.\d+-(?:step\d+|genspark)\s*[·•∙・|\/\-–—]?\s*항체\s*R1~R\d+\s*\(\s*\d+\s*종\s*\)/g;
  var BADGE_NEW="v6.2.0-genspark · 항체 R1~R14 (14종)";
  function fixBadge(){
    if(!document.body){return;}
    var w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null,false),n,list=[];
    while((n=w.nextNode())){
      var pn=n.parentNode&&n.parentNode.nodeName;
      if(/^(SCRIPT|STYLE|TEXTAREA)$/.test(pn)){continue;}
      BADGE_RE.lastIndex=0;
      if(BADGE_RE.test(n.nodeValue)){list.push(n);}
    }
    list.forEach(function(t){t.nodeValue=t.nodeValue.replace(BADGE_RE,BADGE_NEW);});
  }

  /* ── 이벤트 위임 ── */
  document.addEventListener("click",function(e){
    var b=e.target&&e.target.closest?e.target.closest("[data-rgon-act]"):null;
    if(!b){return;}
    var act=b.getAttribute("data-rgon-act")||"";
    e.preventDefault();
    if(act==="copy"){
      var t=directiveText();
      if(!t){toast("⚠️ 복사할 지시문이 없습니다. 입력창에 내용을 적거나 지시서를 먼저 장전하세요.");return;}
      copyText(t).then(function(ok){toast(ok?"📋 지시문을 복사했습니다.":"⚠️ 복사 실패(브라우저 권한 확인)");});
    }else if(act.indexOf("ai:")===0){goAI(act.slice(3));}
    else if(act.indexOf("save:")===0){saveSetting(act.slice(5));}
    else if(act==="clear-input"){clearInput(false);}
    else if(act==="clear-all"){clearAll();}
    else if(act.indexOf("chip:")===0){brief(act.slice(5)).catch(function(err){toast("⚠️ 브리핑 오류: "+(err&&err.message?err.message:err));});}
  });

  function run(){try{mountBottom();fixBadge();}catch(e){}}
  loadSettings();
  if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",run);}else{run();}
  window.addEventListener("load",run);
  [400,1500,4000].forEach(function(ms){setTimeout(run,ms);});
})();
</script>
'''

HTML_BLOCK = HTML_START + "\n" + HTML_BODY.strip("\n") + "\n" + HTML_END + "\n"

# ───────────────────────── 확장프로그램 content.js 블록 ─────────────────────────
JS_BODY = r'''
;(function () {
  try {
    if (window.__rgonClearBtnsInstalled) { return; }
    window.__rgonClearBtnsInstalled = true;

    var CAP_RE = /(omni.*(captur|cache|buffer|queue|absorb)|captured|absorb)/i;
    var KEEP_RE = /token|key|secret|password|github|rgon_gs_url/i;
    var FIELD_SEL = 'textarea,input:not([type=button]):not([type=submit]):not([type=checkbox]):not([type=radio]):not([type=hidden]):not([type=file])';

    function findPanel() {
      var p = document.getElementById('omni');
      if (p) { return p; }
      var btns = document.querySelectorAll('button');
      for (var i = 0; i < btns.length; i++) {
        if (/shin-agent\s*저장/.test(btns[i].textContent || '')) {
          var el = btns[i].parentElement, hops = 0;
          while (el && el !== document.body && hops < 6) {
            if (el.querySelector('textarea,input[type=text]')) { return el; }
            el = el.parentElement; hops++;
          }
          return btns[i].parentElement;
        }
      }
      return null;
    }

    function status(panel, msg) {
      var s = panel.querySelector('[data-rgon-clear-status]');
      if (!s) { return; }
      s.textContent = msg;
      clearTimeout(status._t);
      status._t = setTimeout(function () { s.textContent = ''; }, 3000);
    }

    function setEmpty(el) {
      var proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      var d = Object.getOwnPropertyDescriptor(proto, 'value');
      if (d && d.set) { d.set.call(el, ''); } else { el.value = ''; }
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function ownFields(panel) {
      return [].slice.call(panel.querySelectorAll(FIELD_SEL)).filter(function (e) {
        return !e.closest('[data-rgon-clear-wrap]');
      });
    }

    function clearSelection(panel) {
      [].slice.call(panel.querySelectorAll('input[type=checkbox]:checked')).forEach(function (c) { c.checked = false; });
      [].slice.call(panel.querySelectorAll('.selected,[aria-selected="true"]')).forEach(function (n) {
        n.classList.remove('selected'); n.setAttribute('aria-selected', 'false');
      });
    }

    function clearPreview(panel) {
      [].slice.call(panel.querySelectorAll('[id*="preview" i],[class*="preview" i],[data-omni-preview]')).forEach(function (n) {
        if (!n.closest('[data-rgon-clear-wrap]')) { n.textContent = ''; }
      });
    }

    function purge(store) {
      var n = 0;
      try {
        var del = [];
        for (var i = 0; i < store.length; i++) {
          var k = store.key(i);
          if (CAP_RE.test(k) && !KEEP_RE.test(k)) { del.push(k); }
        }
        del.forEach(function (k) { store.removeItem(k); });
        n = del.length;
      } catch (e) {}
      return n;
    }

    function clearCurrent(panel) {
      ownFields(panel).forEach(setEmpty);
      clearSelection(panel);
      clearPreview(panel);
      status(panel, '🧹 현재 입력창을 비웠습니다.');
    }

    function clearEverything(panel) {
      if (!window.confirm('흡수창 입력·목록·캡처 버퍼를 모두 초기화할까요?')) { return; }
      ownFields(panel).forEach(setEmpty);
      clearSelection(panel);
      clearPreview(panel);
      [].slice.call(panel.querySelectorAll('[id*="captured" i],[class*="captured-list" i],[id*="absorb-list" i]')).forEach(function (n) {
        if (!n.closest('[data-rgon-clear-wrap]')) { n.textContent = ''; }
      });
      try {
        var c = window.__omniCaptured;
        if (Array.isArray(c)) { c.length = 0; }
        else if (c && typeof c === 'object') { Object.keys(c).forEach(function (k) { delete c[k]; }); }
      } catch (e) {}
      purge(window.localStorage); purge(window.sessionStorage);
      try {
        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
          chrome.storage.local.get(null, function (all) {
            var del = Object.keys(all || {}).filter(function (k) { return CAP_RE.test(k) && !KEEP_RE.test(k); });
            if (del.length) { chrome.storage.local.remove(del); }
          });
        }
      } catch (e) {}
      status(panel, '🗑️ 흡수창 전체 초기화 완료!');
    }

    function mkBtn(label, handler) {
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = label;
      b.style.cssText = 'cursor:pointer;margin:4px 4px 0 0;padding:5px 9px;font-size:12px;border-radius:6px;' +
        'border:1px solid #888;background:#2b2f3a;color:#fff;';
      b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); handler(); });
      return b;
    }

    function ensure() {
      var panel = findPanel();
      if (!panel || panel.querySelector('[data-rgon-clear-wrap]')) { return; }
      var wrap = document.createElement('div');
      wrap.setAttribute('data-rgon-clear-wrap', '1');
      wrap.style.cssText = 'display:flex;flex-wrap:wrap;align-items:center;margin-top:6px;';
      wrap.appendChild(mkBtn('🧹 지우기', function () { clearCurrent(panel); }));
      wrap.appendChild(mkBtn('🗑️ 전체 지우기', function () { clearEverything(panel); }));
      var st = document.createElement('span');
      st.setAttribute('data-rgon-clear-status', '1');
      st.style.cssText = 'font-size:12px;margin-left:6px;opacity:.9;';
      wrap.appendChild(st);
      panel.appendChild(wrap);
    }

    var timer = null;
    function schedule() {
      if (timer) { return; }
      timer = setTimeout(function () { timer = null; try { ensure(); } catch (e) {} }, 200);
    }
    ensure();
    new MutationObserver(schedule).observe(document.documentElement, { childList: true, subtree: true });
  } catch (err) { /* 확장 UI 보조 기능 - 실패해도 본 기능에 영향 없음 */ }
})();
'''
JS_BLOCK = JS_START + "\n" + JS_BODY.strip("\n") + "\n" + JS_END + "\n"


# ───────────────────────── 공통 유틸 ─────────────────────────
def say(msg=""):
    print(msg, flush=True)


def human(n):
    n = float(n)
    for u in ("B", "KB", "MB"):
        if n < 1024 or u == "MB":
            return f"{int(n)}B" if u == "B" else f"{n:.1f}{u}"
        n /= 1024


def read_file(path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if bom else raw
    try:
        return body.decode("utf-8"), "utf-8", bom
    except UnicodeDecodeError:
        return body.decode("cp949"), "cp949", False


def write_file(path, text, enc, bom):
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode(enc))


def backup(path):
    b = path.with_name(path.name + f".bak_{STAMP}")
    shutil.copy2(path, b)
    return b


def ids_of(src):
    return set(re.findall(r"""\bid\s*=\s*["']([^"']+)["']""", src))


def node_check(js_text):
    node = shutil.which("node")
    if not node:
        return None, "node 없음(문법 검사 생략)"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(js_text)
        tmp = f.name
    try:
        flags = 0x08000000 if os.name == "nt" else 0
        p = subprocess.run([node, "--check", tmp], capture_output=True, timeout=30, creationflags=flags)
        if p.returncode == 0:
            return True, "node --check 통과"
        return False, (p.stderr or b"").decode("utf-8", "replace").strip()[:200]
    except Exception as e:
        return None, f"검사 생략({e})"
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ───────────────────────── HTML 패치 ─────────────────────────
def patch_html(path):
    src, enc, bom = read_file(path)
    orig = src
    notes = []

    badge_n = 0
    for rx in BADGE_RES:
        src, n = rx.subn(NEW_BADGE, src)
        badge_n += n
    notes.append(f"배지 문구 치환 {badge_n}곳")

    block_rx = re.compile(re.escape(HTML_START) + r"[\s\S]*?" + re.escape(HTML_END) + r"\n?")
    old_block = block_rx.search(src)
    if old_block:
        src = src[:old_block.start()] + HTML_BLOCK + src[old_block.end():]
        notes.append("기존 STEP1-MOBILE-UI 블록 교체")
        check_base = src_without = orig[:old_block.start()] + orig[old_block.end():]
    else:
        nav = re.search(r"""<nav\b[^>]*\bid\s*=\s*["']rgon-mobile-quick-nav["'][\s\S]*?</nav\s*>""", src, re.I)
        if nav:
            pos = nav.end()
            notes.append("퀵 네비게이션 바로 아래에 삽입")
        else:
            body = re.search(r"<body[^>]*>", src, re.I)
            pos = body.end() if body else 0
            notes.append("body 시작 부분에 삽입" if body else "문서 맨 앞에 삽입")
        src = src[:pos] + "\n" + HTML_BLOCK + src[pos:]
        check_base = orig

    if src == orig:
        return None, "변경 없음(이미 최신)"
    lost = ids_of(check_base) - ids_of(src)
    if lost:
        return None, f"id 보존 검증 실패 → 원본 유지 (누락: {sorted(lost)[:5]})"
    if len(src) < len(check_base):
        return None, "결과가 원본보다 작아 중단 → 원본 유지"
    write_file(path, src, enc, bom)
    return True, " / ".join(notes)


# ───────────────────────── content.js 패치 ─────────────────────────
def patch_content_js(path):
    src, enc, bom = read_file(path)
    orig = src
    rx = re.compile(re.escape(JS_START) + r"[\s\S]*?" + re.escape(JS_END) + r"\n?")
    m = rx.search(src)
    if m:
        new = src[:m.start()] + JS_BLOCK + src[m.end():]
        action = "기존 RGON-CLEAR-BTNS 블록 갱신"
    else:
        sep = "" if src.endswith("\n") or not src else "\n"
        new = src + sep + "\n" + JS_BLOCK
        action = "파일 하단에 블록 추가"
    if new == orig:
        return None, "변경 없음(이미 최신)"
    ok, msg = node_check(new)
    if ok is False:
        return None, f"JS 문법 검사 실패 → 원본 유지: {msg}"
    write_file(path, new, enc, bom)
    return True, f"{action} ({msg})"


# ───────────────────────── Git 동기화 ─────────────────────────
def git(args, timeout=180):
    flags = 0x08000000 if os.name == "nt" else 0
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    p = subprocess.run(["git"] + args, cwd=str(ROOT), capture_output=True, timeout=timeout,
                       creationflags=flags, env=env)
    dec = lambda b: (b or b"").decode("utf-8", "replace").strip()
    return p.returncode, dec(p.stdout), dec(p.stderr)


def exclude_backups():
    info = ROOT / ".git" / "info"
    try:
        info.mkdir(parents=True, exist_ok=True)
        ex = info / "exclude"
        cur = ex.read_text(encoding="utf-8", errors="replace") if ex.exists() else ""
        add = [p for p in ("*.bak", "*.bak_*") if p not in cur.splitlines()]
        if add:
            with open(ex, "a", encoding="utf-8", newline="") as f:
                f.write(("" if cur.endswith("\n") or not cur else "\n") + "\n".join(add) + "\n")
    except OSError:
        pass


def git_sync():
    say("\n[GitHub 클라우드 동기화]")
    if not shutil.which("git"):
        say("  ❌ git 명령을 찾을 수 없습니다.")
        return False
    if not (ROOT / ".git").exists():
        say("  ❌ 루트 폴더가 git 저장소가 아닙니다.")
        return False
    exclude_backups()
    steps = [
        ("git add -A", ["add", "-A"]),
        (f'git commit -m "{COMMIT_MSG}"', ["commit", "-m", COMMIT_MSG]),
        ("git pull --rebase -X ours origin main", ["pull", "--rebase", "-X", "ours", "origin", "main"]),
        ("git push origin main", ["push", "origin", "main"]),
    ]
    for label, args in steps:
        try:
            rc, out, err = git(args)
        except Exception as e:
            say(f"  ❌ {label}: {type(e).__name__}: {e}")
            return False
        text = (out + "\n" + err).strip()
        if rc == 0:
            say(f"  ✅ {label}")
        elif args[0] == "commit" and re.search(r"nothing to commit|nothing added|변경 사항 없음", text, re.I):
            say(f"  ➖ {label}: 커밋할 변경 없음 (계속 진행)")
        else:
            say(f"  ❌ {label} (종료코드 {rc})")
            for ln in text.splitlines()[-6:]:
                say(f"      {ln[:160]}")
            return False
    say("  🎉 GitHub Pages 반영 요청 완료 (배포까지 1~2분 걸릴 수 있습니다).")
    return True


# ───────────────────────── main ─────────────────────────
def main():
    say("=" * 78)
    say(f"RGON STEP2 ALL-IN-ONE 패치 | {datetime.now():%Y-%m-%d %H:%M:%S} | {ROOT}")
    say("=" * 78)

    html_files = [ROOT / p for p in HTML_TARGETS if (ROOT / p).is_file()]
    js_file = ROOT / JS_TARGET
    js_exists = js_file.is_file()
    all_targets = html_files + ([js_file] if js_exists else [])
    if not all_targets:
        sys.exit("패치할 대상 파일을 찾지 못했습니다.")

    say("\n[1] 백업")
    backups = {}
    for p in all_targets:
        try:
            backups[p] = backup(p)
            say(f"  {p.relative_to(ROOT)} → {backups[p].name}")
        except OSError as e:
            sys.exit(f"백업 실패({p}): {e} — 안전을 위해 중단합니다.")

    results = []
    say("\n[2] 크롬 확장 흡수창 지우기 버튼 복원")
    if js_exists:
        try:
            ok, msg = patch_content_js(js_file)
        except Exception as e:
            ok, msg = None, f"{type(e).__name__}: {e}"
        say(f"  {JS_TARGET}: {msg}")
        if ok:
            results.append(js_file)
            say("  ※ chrome://extensions 에서 확장프로그램을 '새로고침'해야 적용됩니다.")
    else:
        say(f"  {JS_TARGET} 파일이 없어 건너뜁니다.")

    say("\n[3] 독대실 HTML (Genspark 직통 + 지우기 버튼 + 브리핑 칩 + 배지)")
    for p in html_files:
        try:
            ok, msg = patch_html(p)
        except Exception as e:
            ok, msg = None, f"{type(e).__name__}: {e}"
        say(f"  {p.relative_to(ROOT)}: {msg}")
        if ok:
            results.append(p)
    missing = [h for h in HTML_TARGETS if not (ROOT / h).is_file()]
    for h in missing:
        say(f"  {h}: 파일 없음(건너뜀)")

    say("\n[변경된 파일]")
    if results:
        for p in results:
            say(f"  - {p.relative_to(ROOT)}  ({human(p.stat().st_size)})  백업: {backups[p].name}")
    else:
        say("  (없음)")

    synced = git_sync()

    say("\n" + "=" * 78)
    say(f"요약: 변경 {len(results)}개 / Git 동기화 {'성공' if synced else '미완료'}")
    say("롤백: 각 파일의 .bak_" + STAMP + " 파일을 원래 이름으로 되돌리세요.")
    say("모바일 확인: https://sangill111157-spec.github.io/hangeoreumsshik-cloud/rgon_alpha_chat.html?v6=step2")
    say("=" * 78)


if __name__ == "__main__":
    main()
