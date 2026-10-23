#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step3_master_workstation.py
 (1) 독대실 3단 반응형 레이아웃 + 하단 입력창 찌그러짐 완전 복구
 (2) 원터치 자동복사+AI방 이동 / 클립보드 붙여넣기 / 모바일 즉시 반영(GitHub API·텔레그램)
 (3) 크롬 확장(core.js / content.js / popup.js) 흡수창 [🧹 지우기] [🗑️ 전체 지우기] 복원
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
EXT_DIRNAME = "chrome_omni_link_ext"
EXT_FILES = ["core.js", "content.js", "popup.js"]
PRUNE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

HTML_START = "<!-- === [RGON-STEP1-MOBILE-UI-START] === -->"
HTML_END = "<!-- === [RGON-STEP1-MOBILE-UI-END] === -->"
EXT_START = "/* === [RGON-EXT-CLEAR-START] === */"
EXT_END = "/* === [RGON-EXT-CLEAR-END] === */"

COMMIT_MSG = "feat(workstation): 3-tier mobile UI + fix input squeeze + 1-click AI relay + core.js clear buttons"

REQUIRED_NEW_IDS = {
    "rgonws-style", "rgonws-top", "rgonws-row1", "rgonws-rail", "rgonws-drawer",
    "rgonws-cards", "rgonws-modal", "rgonws-toast", "rgonws-script",
}

ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.I)
HTML_BLOCK_RE = re.compile(re.escape(HTML_START) + r".*?" + re.escape(HTML_END), re.S)
EXT_BLOCK_RE = re.compile(r"\n?" + re.escape(EXT_START) + r".*?" + re.escape(EXT_END) + r"\n?", re.S)
SCRIPT_SPAN_RE = re.compile(r"<script\b.*?</script\s*>", re.S | re.I)
BOTTOM_CLEAR_RE = re.compile(
    r'<(button|span|div)\b[^>]*\bclass\s*=\s*["\'][^"\']*\brgon-bottom-clear\b[^"\']*["\'][^>]*>'
    r'(?:(?!<\1\b).)*?</\1\s*>',
    re.S | re.I,
)

# ─────────────────────────────────────────────────────────────
# 독대실 HTML 블록 (CSS + 마크업 + JS)
# ─────────────────────────────────────────────────────────────
HTML_BLOCK_BODY = r"""<style id="rgonws-style">
#rgonws-top{position:sticky;top:0;left:0;right:0;z-index:2147483000;flex:0 0 auto;background:rgba(13,17,23,.97);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);border-bottom:1px solid rgba(212,175,55,.45);padding:6px 8px;box-sizing:border-box;width:100%;max-width:100vw;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif}
#rgonws-top *,#rgonws-modal *,.rgonws-dock *{box-sizing:border-box}
.rgonws-row{display:flex;gap:6px;align-items:center;width:100%}
#rgonws-row1{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
#rgonws-rail{overflow-x:auto;white-space:nowrap;display:flex;gap:6px;margin-top:6px;padding-bottom:2px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
#rgonws-row1::-webkit-scrollbar,#rgonws-rail::-webkit-scrollbar,.rgonws-dock::-webkit-scrollbar{display:none}
.rgonws-btn{white-space:nowrap!important;word-break:keep-all!important;flex:0 0 auto!important;width:auto!important;min-width:0;display:inline-flex;align-items:center;gap:3px;border:1px solid rgba(212,175,55,.7);background:#161b22;color:#f5d76e;border-radius:999px;padding:6px 11px;font-size:13px;line-height:1.2;font-weight:600;cursor:pointer;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.rgonws-btn:active{transform:scale(.96);background:#2a2410}
.rgonws-ai{border-color:#58a6ff;color:#cde6ff}
#rgonws-drawer{display:none;margin-top:8px;padding:8px;border:1px solid rgba(212,175,55,.35);border-radius:12px;background:#0f141b}
#rgonws-drawer.open{display:block}
.rgonws-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:6px 10px;margin-bottom:8px}
.rgonws-grid label{display:flex;flex-direction:column;gap:3px;font-size:12px;color:#c9d1d9}
.rgonws-grid input,#rgonws-modal input,#rgonws-modal textarea{width:100%;padding:7px 9px;border-radius:8px;border:1px solid #30363d;background:#0d1117;color:#e6edf3;font-size:13px}
.rgonws-note{font-size:11px;color:#8b949e;margin:4px 0 6px}
#rgonws-cards{display:none;margin-top:8px;max-height:48vh;overflow:auto;-webkit-overflow-scrolling:touch}
#rgonws-cards.open{display:block}
.rgonws-cards-head{display:flex;align-items:center;gap:8px;color:#f5d76e;font-size:13px;margin-bottom:6px;position:sticky;top:0;background:#0d1117;padding:4px 0}
.rgonws-cards-head span{flex:1 1 auto;color:#8b949e;font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rgonws-card{background:#161b22;border:1px solid #30363d;border-left:3px solid #d4af37;border-radius:10px;padding:8px 10px;margin-bottom:6px;color:#e6edf3;font-size:13px}
.rgonws-card-t{font-weight:700;color:#f5d76e;margin-bottom:4px}
.rgonws-card pre{margin:0;white-space:pre-wrap;word-break:break-word;font-family:inherit;font-size:12px;color:#c9d1d9}
.rgonws-dock{display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;width:100%!important;flex:0 0 100%!important;max-width:100%;gap:6px;overflow-x:auto;padding:4px 0 6px;scrollbar-width:none}
.rgonws-dock .rgonws-btn{font-size:12px;padding:5px 10px}
textarea.rgonws-input-fix,input.rgonws-input-fix{flex:1 1 0% !important;min-width:160px!important;width:100%!important;max-width:none!important}
.rgon-bottom-clear{display:none!important}
@media (max-width:820px){body:not(.rgonws-show-legacy) .rgonws-legacy{display:none!important}}
body.rgonws-hide-legacy .rgonws-legacy{display:none!important}
#rgonws-modal{position:fixed;inset:0;z-index:2147483600;background:rgba(0,0,0,.6);display:none;align-items:flex-end;justify-content:center}
#rgonws-modal.open{display:flex}
.rgonws-modal-box{width:100%;max-width:720px;max-height:92vh;overflow:auto;background:#0d1117;border:1px solid rgba(212,175,55,.5);border-radius:16px 16px 0 0;padding:12px}
.rgonws-modal-title{color:#f5d76e;font-weight:700;margin-bottom:8px}
#rgonws-deploy-text{min-height:38vh;font-family:ui-monospace,Consolas,monospace;font-size:12px}
.rgonws-wrap{flex-wrap:wrap;margin-top:8px}
.rgonws-wrap input{flex:1 1 200px;width:auto}
#rgonws-deploy-log{margin-top:8px;font-size:12px;color:#8b949e;white-space:pre-wrap;word-break:break-all}
#rgonws-toast{position:fixed;left:50%;bottom:90px;transform:translateX(-50%) translateY(20px);background:#161b22;color:#f5d76e;border:1px solid #d4af37;padding:8px 14px;border-radius:999px;font-size:13px;z-index:2147483647;opacity:0;pointer-events:none;transition:.2s;white-space:nowrap;max-width:92vw;overflow:hidden;text-overflow:ellipsis}
#rgonws-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
<div id="rgonws-top">
  <div id="rgonws-row1" class="rgonws-row">
    <button type="button" class="rgonws-btn" data-act="copy">📋 복사</button>
    <button type="button" class="rgonws-btn" data-act="paste">📥 붙여넣기</button>
    <button type="button" class="rgonws-btn rgonws-ai" data-ai="rgon">🔵 르곤</button>
    <button type="button" class="rgonws-btn rgonws-ai" data-ai="claude">🤖 클로드</button>
    <button type="button" class="rgonws-btn rgonws-ai" data-ai="gpt">⚡ GPT</button>
    <button type="button" class="rgonws-btn rgonws-ai" data-ai="grok">🎯 Grok</button>
    <button type="button" class="rgonws-btn" data-act="settings">⚙️ 설정</button>
  </div>
  <div id="rgonws-rail" class="rgonws-row">
    <button type="button" class="rgonws-btn" data-act="brief">📊 6청사 종합브리핑</button>
    <button type="button" class="rgonws-btn" data-act="tts">🔊 음성 아나운서(TTS)</button>
    <button type="button" class="rgonws-btn" data-act="top1">🧠 Top1 지시서 장전</button>
    <button type="button" class="rgonws-btn" data-act="tg">✈️ 로건봇 텔레그램 발송</button>
    <button type="button" class="rgonws-btn" data-act="f-nvda">📈 1청사 NVDA·시트</button>
    <button type="button" class="rgonws-btn" data-act="f-media">🎬 3청사 미디어·틱톡</button>
    <button type="button" class="rgonws-btn" data-act="f-immune">🧬 R1~R14 항체·진화</button>
    <button type="button" class="rgonws-btn" data-act="deploy">🚀 모바일 즉시 반영(GitHub/텔레그램)</button>
    <button type="button" class="rgonws-btn" data-act="legacy">🔽 기존 대형패널 토글</button>
  </div>
  <div id="rgonws-drawer">
    <div class="rgonws-grid">
      <label>🔵 르곤 채팅방 URL<input id="rgonws-url-rgon" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <label>🤖 클로드 채팅방 URL<input id="rgonws-url-claude" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <label>⚡ GPT 채팅방 URL<input id="rgonws-url-gpt" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <label>🎯 Grok 채팅방 URL<input id="rgonws-url-grok" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <label>🔑 GitHub PAT (선택)<input id="rgonws-gh-pat" type="password" autocomplete="off" placeholder="github_pat_..."></label>
      <label>📦 GitHub 저장소 (owner/repo)<input id="rgonws-gh-repo" type="text" autocomplete="off" placeholder="owner/shin-agent"></label>
      <label>🌿 브랜치<input id="rgonws-gh-branch" type="text" placeholder="main"></label>
      <label>🤖 텔레그램 봇 토큰 (선택)<input id="rgonws-tg-token" type="password" autocomplete="off" placeholder="123456:ABC..."></label>
      <label>💬 텔레그램 chat_id<input id="rgonws-tg-chat" type="text" placeholder="123456789"></label>
      <label>📊 브리핑 JSON 경로 (선택)<input id="rgonws-brief-url" type="text" placeholder="data/rgon_briefing.json"></label>
    </div>
    <div class="rgonws-note">🔒 모든 값은 이 기기 브라우저 localStorage에만 저장되며 GitHub/텔레그램 API 호출 외에는 어디에도 전송되지 않습니다.</div>
    <div class="rgonws-row">
      <button type="button" class="rgonws-btn" data-act="save">💾 저장</button>
      <button type="button" class="rgonws-btn" data-act="settings">닫기</button>
    </div>
  </div>
  <div id="rgonws-cards"></div>
</div>
<div id="rgonws-modal" aria-hidden="true">
  <div class="rgonws-modal-box">
    <div class="rgonws-modal-title">🚀 모바일 즉시 반영 — 원격 PC 접속 없이</div>
    <textarea id="rgonws-deploy-text" placeholder="다른 AI 방에서 복사해 온 코드/명령을 여기에 붙여넣으세요"></textarea>
    <div class="rgonws-row rgonws-wrap">
      <input id="rgonws-deploy-path" type="text" placeholder="커밋 경로 (예: dashboard/rgon_alpha_chat.html)">
      <input id="rgonws-deploy-msg" type="text" placeholder="커밋 메시지 (선택)">
    </div>
    <div class="rgonws-row rgonws-wrap">
      <button type="button" class="rgonws-btn" data-act="d-paste">📥 클립보드</button>
      <button type="button" class="rgonws-btn" data-act="d-gh">☁️ GitHub 직접 커밋</button>
      <button type="button" class="rgonws-btn" data-act="d-tg">✈️ 텔레그램 → 집PC 문지기</button>
      <button type="button" class="rgonws-btn" data-act="d-close">닫기</button>
    </div>
    <div class="rgonws-note">텔레그램 전송분은 집 PC의 rgon_auto_watcher.py가 #RGON_EXEC 태그로 수신·처리합니다.</div>
    <div id="rgonws-deploy-log"></div>
  </div>
</div>
<div id="rgonws-toast"></div>
<script id="rgonws-script">
(function(){
'use strict';
if(window.__rgonWS3)return;window.__rgonWS3=true;
var LS={get:function(k,d){try{var v=localStorage.getItem(k);return v==null?(d||''):v;}catch(e){return d||'';}},set:function(k,v){try{localStorage.setItem(k,v);}catch(e){}},del:function(k){try{localStorage.removeItem(k);}catch(e){}}};
var DEFAULT_URL='https://www.genspark.ai/agents';
var MOBILE_Q=window.matchMedia('(max-width: 820px)');
function $(s,r){return (r||document).querySelector(s);}
function $$(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function ours(el){return !!(el&&el.closest&&el.closest('#rgonws-top,#rgonws-modal,.rgonws-dock,#rgonws-toast'));}
function visible(el){return !!(el&&(el.offsetWidth||el.offsetHeight||el.getClientRects().length));}
function toast(msg,ms){var t=$('#rgonws-toast');if(!t)return;t.textContent=msg;t.classList.add('show');clearTimeout(toast._t);toast._t=setTimeout(function(){t.classList.remove('show');},ms||2200);}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}

/* ── 입력창 탐색/값 설정 ── */
var INPUT_SEL=['#userInput','#chatInput','#messageInput','#msgInput','#promptInput','#prompt','#input','#question'];
function findInput(){
  for(var i=0;i<INPUT_SEL.length;i++){var el=$(INPUT_SEL[i]);if(el&&!ours(el)&&/^(TEXTAREA|INPUT)$/.test(el.tagName))return el;}
  var best=null,bestY=-1;

  $$('textarea').forEach(function(t){if(ours(t)||!visible(t))return;var r=t.getBoundingClientRect();if(r.bottom>bestY){bestY=r.bottom;best=t;}});
  if(best)return best;
  var any=$$('textarea').filter(function(t){return !ours(t);});
  return any[any.length-1]||null;
}
function setVal(el,v){
  if(!el)return;
  var proto=el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
  var d=Object.getOwnPropertyDescriptor(proto,'value');
  if(d&&d.set)d.set.call(el,v);else el.value=v;
  el.dispatchEvent(new Event('input',{bubbles:true}));
  el.dispatchEvent(new Event('change',{bubbles:true}));
}
function currentText(){var el=findInput();var v=el?String(el.value||'').trim():'';return v||String(LS.get('rgon_loaded_directive','')).trim();}

/* ── 클립보드 ── */
function legacy(s){try{var ta=document.createElement('textarea');ta.value=s;ta.setAttribute('readonly','');ta.style.cssText='position:fixed;left:-9999px;top:0;opacity:0';document.body.appendChild(ta);ta.select();ta.setSelectionRange(0,ta.value.length);var ok=document.execCommand('copy');ta.remove();return ok;}catch(e){return false;}}
function copyText(s){
  if(navigator.clipboard&&window.isSecureContext){return navigator.clipboard.writeText(s).then(function(){return true;},function(){return legacy(s);});}
  return Promise.resolve(legacy(s));
}
function readClip(){if(navigator.clipboard&&navigator.clipboard.readText)return navigator.clipboard.readText();return Promise.reject(new Error('unsupported'));}
function clipFail(){alert('클립보드 읽기 권한이 막혀 있습니다.\n\n입력창을 길게 눌러 [붙여넣기]를 선택하거나,\n브라우저 사이트 설정에서 클립보드 권한을 허용해 주세요.\n(HTTPS 또는 localhost 에서만 동작합니다)');}
function pasteToInput(){
  return readClip().then(function(txt){
    if(!txt){toast('📭 클립보드가 비어 있습니다');return;}
    var el=findInput();if(!el){toast('입력창을 찾지 못했습니다');return;}
    var cur=String(el.value||'');
    setVal(el,cur?cur.replace(/\s*$/,'')+'\n'+txt:txt);el.focus();
    toast('📥 붙여넣기 완료 ('+txt.length+'자)');
  }).catch(clipFail);
}
function copyCurrent(){var t=currentText();if(!t){toast('복사할 내용이 없습니다');return;}copyText(t).then(function(ok){toast(ok?('📋 '+t.length+'자 복사 완료'):'⚠️ 복사 실패');});}

/* ── 원터치 릴레이 (자동복사 → AI방 이동) ── */
var AI_KEYS={rgon:'rgon_url_rgon',claude:'rgon_url_claude',gpt:'rgon_url_gpt',grok:'rgon_url_grok'};
var AI_NAMES={rgon:'르곤',claude:'클로드',gpt:'GPT',grok:'Grok'};
function relay(ai){
  var url=String(LS.get(AI_KEYS[ai],'')).trim()||DEFAULT_URL;
  var txt=currentText();
  var go=function(){window.location.href=url;};
  if(!txt){toast('➡️ '+AI_NAMES[ai]+' 방으로 이동');setTimeout(go,250);return;}
  copyText(txt).then(function(ok){
    toast(ok?('📋 '+txt.length+'자 자동복사 → '+AI_NAMES[ai]+' 이동'):'⚠️ 자동복사 실패 — 이동 후 수동 붙여넣기',1400);
    setTimeout(go,ok?450:1300);
  });
}

/* ── 브리핑 JSON ── */
var BRIEF_CANDIDATES=['rgon_briefing.json','data/rgon_briefing.json','dashboard/rgon_briefing.json','docs/rgon_briefing.json','../rgon_briefing.json','../data/rgon_briefing.json','briefing.json','data/briefing.json','rgon_six_ministries.json'];
var lastCardsText='';
function loadBrief(){
  var list=[];var custom=String(LS.get('rgon_brief_url','')).trim();if(custom)list.push(custom);list=list.concat(BRIEF_CANDIDATES);
  var i=0;
  function next(){
    if(i>=list.length)return Promise.reject(new Error('no brief json'));
    var u=list[i++];var sep=u.indexOf('?')<0?'?':'&';
    return fetch(u+sep+'_t='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error('http');return r.json();}).then(function(j){return {url:u,data:j};}).catch(next);
  }
  return next();
}
function toItems(data){
  if(Array.isArray(data))return data.map(function(v,i){return {key:String(i+1),val:v};});
  if(data&&typeof data==='object'){
    var arrKey=['items','cards','ministries','briefings','data','list'].filter(function(k){return Array.isArray(data[k]);})[0];
    if(arrKey)return toItems(data[arrKey]);
    return Object.keys(data).map(function(k){return {key:k,val:data[k]};});
  }
  return [{key:'brief',val:data}];
}
function titleOf(it){var v=it.val;if(v&&typeof v==='object'){return v.title||v.name||v.ministry||v.label||v.id||it.key;}return it.key;}
function bodyOf(it){
  var v=it.val;if(v==null)return '';if(typeof v!=='object')return String(v);
  var t=v.summary||v.text||v.content||v.message||v.brief||v.desc||v.description;
  if(t&&typeof t!=='object')return String(t);
  try{return JSON.stringify(v,null,1).slice(0,900);}catch(e){return String(v);}
}
var FILTERS={
  'f-nvda':{name:'📈 1청사 NVDA·시트',re:/1\s*청사|NVDA|엔비디아|nvidia|시트|sheet/i},
  'f-media':{name:'🎬 3청사 미디어·틱톡',re:/3\s*청사|미디어|틱톡|tiktok|media|youtube|유튜브|쇼츠/i},
  'f-immune':{name:'🧬 R1~R14 항체·진화',re:/\bR(1[0-4]|[1-9])\b|항체|진화|antibody|evol/i}
};
function closeBtn(){return '<button type="button" class="rgonws-btn" data-act="cards-close">✖</button>';}
function showCards(filterKey){
  var box=$('#rgonws-cards');box.classList.add('open');
  box.innerHTML='<div class="rgonws-card">⏳ 브리핑 불러오는 중…</div>';
  loadBrief().then(function(b){
    var items=toItems(b.data);var f=filterKey?FILTERS[filterKey]:null;
    if(f){items=items.filter(function(it){var s;try{s=it.key+' '+JSON.stringify(it.val);}catch(e){s=it.key;}return f.re.test(s);});}
    var head='<div class="rgonws-cards-head"><b>'+(f?esc(f.name):'📊 6청사 종합브리핑')+'</b><span>'+esc(b.url)+' · '+esc(new Date().toLocaleTimeString())+'</span>'+closeBtn()+'</div>';
    if(!items.length){box.innerHTML=head+'<div class="rgonws-card">해당 필터에 맞는 항목이 없습니다.</div>';lastCardsText='';return;}
    lastCardsText=items.map(function(it){return titleOf(it)+'. '+bodyOf(it);}).join('\n');
    box.innerHTML=head+items.slice(0,60).map(function(it){return '<div class="rgonws-card"><div class="rgonws-card-t">'+esc(titleOf(it))+'</div><pre>'+esc(bodyOf(it))+'</pre></div>';}).join('');
  }).catch(function(){
    box.innerHTML='<div class="rgonws-cards-head"><b>📊 브리핑</b><span></span>'+closeBtn()+'</div><div class="rgonws-card">브리핑 JSON을 찾지 못했습니다. ⚙️ 설정에서 JSON 경로를 지정하세요.</div>';
  });
}

/* ── TTS ── */
function tts(){
  if(!('speechSynthesis' in window)){toast('이 브라우저는 음성합성을 지원하지 않습니다');return;}
  if(speechSynthesis.speaking||speechSynthesis.pending){speechSynthesis.cancel();toast('⏹ 음성 정지');return;}
  var speak=function(txt){
    txt=String(txt||'').replace(/[{}\[\]"]/g,' ').slice(0,4000);
    if(!txt.trim()){toast('읽을 내용이 없습니다');return;}
    var chunks=txt.match(/[^.!?。\n]{1,180}[.!?。\n]?/g)||[txt];
    var vs=speechSynthesis.getVoices().filter(function(v){return /ko/i.test(v.lang);});
    chunks.forEach(function(c){var u=new SpeechSynthesisUtterance(c);u.lang='ko-KR';u.rate=1.05;if(vs[0])u.voice=vs[0];speechSynthesis.speak(u);});
    toast('🔊 음성 브리핑 재생 (다시 누르면 정지)');
  };
  if(lastCardsText){speak(lastCardsText);return;}
  loadBrief().then(function(b){speak(toItems(b.data).map(function(it){return titleOf(it)+'. '+bodyOf(it);}).join('\n'));}).catch(function(){speak(currentText());});
}

/* ── 기존 버튼 연동 ── */
function findForeignButton(re){return $$('button,a,[role="button"]').filter(function(b){return !ours(b)&&re.test((b.textContent||'')+' '+(b.id||''));})[0]||null;}
function top1(){
  var b=findForeignButton(/top\s*-?\s*1|톱\s*1|1\s*순위/i);
  if(b){b.click();toast('🧠 기존 Top1 지시서 버튼 실행');return;}
  loadBrief().then(function(br){
    var d=br.data||{};
    var t=d.top1||d.top1_directive||d.top_directive||(Array.isArray(d.directives)?d.directives[0]:null);
    if(t&&typeof t==='object')t=t.text||t.directive||JSON.stringify(t,null,1);
    if(!t)throw new Error('none');
    t=String(t);LS.set('rgon_loaded_directive',t);
    var el=findInput();if(el){setVal(el,t);el.focus();}
    toast('🧠 Top1 지시서 장전 완료');
  }).catch(function(){toast('Top1 지시서를 찾지 못했습니다');});
}

/* ── 텔레그램 ── */
function tgSend(text,asDoc,caption){
  var tok=String(LS.get('rgon_tg_token','')).trim(),chat=String(LS.get('rgon_tg_chat','')).trim();
  if(!tok||!chat)return Promise.reject(new Error('⚙️ 설정에서 텔레그램 봇 토큰/chat_id를 입력하세요'));
  var base='https://api.telegram.org/bot'+tok;
  var done=function(r){return r.json().then(function(j){if(!j.ok)throw new Error(j.description||'telegram error');return j;});};
  if(!asDoc&&text.length<=4000){
    return fetch(base+'/sendMessage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_id:chat,text:text,disable_web_page_preview:true})}).then(done);
  }
  var fd=new FormData();fd.append('chat_id',chat);fd.append('caption',String(caption||'#RGON_EXEC').slice(0,1000));
  fd.append('document',new Blob([text],{type:'text/plain'}),'rgon_payload.txt');
  return fetch(base+'/sendDocument',{method:'POST',body:fd}).then(done);
}
function tgBrief(){
  var b=findForeignButton(/로건봇|텔레그램|telegram/i)||findForeignButton(/공유|share/i);
  if(b){b.click();toast('✈️ 기존 텔레그램/공유 실행');return;}
  var txt=lastCardsText||currentText();if(!txt){toast('보낼 내용이 없습니다');return;}
  tgSend('📊 [로건봇 브리핑]\n'+txt).then(function(){toast('✈️ 텔레그램 발송 완료');}).catch(function(){
    if(navigator.share){navigator.share({title:'르곤 브리핑',text:txt}).catch(function(){});return;}
    copyText(txt);
    window.open('https://t.me/share/url?url='+encodeURIComponent(location.href)+'&text='+encodeURIComponent(txt.slice(0,3000)),'_blank');
  });
}

/* ── GitHub Contents API ── */
function b64utf8(s){var bytes=new TextEncoder().encode(s);var bin='';for(var i=0;i<bytes.length;i+=0x8000){bin+=String.fromCharCode.apply(null,bytes.subarray(i,i+0x8000));}return btoa(bin);}
function ghCommit(path,content,msg){
  var pat=String(LS.get('rgon_gh_pat','')).trim(),repo=String(LS.get('rgon_gh_repo','')).trim(),br=String(LS.get('rgon_gh_branch','main')).trim()||'main';
  if(!pat||!/^[^\/\s]+\/[^\/\s]+$/.test(repo))return Promise.reject(new Error('⚙️ 설정에서 GitHub PAT와 저장소(owner/repo)를 입력하세요'));
  path=String(path||'').trim().replace(/^\/+/,'');
  if(!path)return Promise.reject(new Error('커밋 경로를 입력하세요'));
  var api='https://api.github.com/repos/'+repo+'/contents/'+path.split('/').map(encodeURIComponent).join('/');
  var h={'Authorization':'Bearer '+pat,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'};
  return fetch(api+'?ref='+encodeURIComponent(br),{headers:h,cache:'no-store'}).then(function(r){
    if(r.status===404)return null;if(!r.ok)throw new Error('조회 실패 HTTP '+r.status);return r.json();
  }).then(function(cur){
    var body={message:msg||('mobile: update '+path),content:b64utf8(content),branch:br};
    if(cur&&cur.sha)body.sha=cur.sha;
    return fetch(api,{method:'PUT',headers:Object.assign({'Content-Type':'application/json'},h),body:JSON.stringify(body)});
  }).then(function(r){return r.json().then(function(j){if(!r.ok)throw new Error((j&&j.message)||('HTTP '+r.status));return j;});});
}

/* ── 모바일 즉시 반영 모달 ── */
function dlog(m){var l=$('#rgonws-deploy-log');if(l)l.textContent='['+new Date().toLocaleTimeString()+'] '+m+'\n'+l.textContent;}
function openDeploy(){
  var m=$('#rgonws-modal');m.classList.add('open');m.setAttribute('aria-hidden','false');
  var ta=$('#rgonws-deploy-text'),p=$('#rgonws-deploy-path');
  if(p&&!p.value)p.value=LS.get('rgon_deploy_path','');
  var t=currentText();
  if(t&&ta&&!ta.value){ta.value=t;}
  else if(ta&&!ta.value){readClip().then(function(c){if(c)ta.value=c;}).catch(function(){});}
}
function closeDeploy(){var m=$('#rgonws-modal');m.classList.remove('open');m.setAttribute('aria-hidden','true');}
function deployGH(){
  var txt=$('#rgonws-deploy-text').value,path=$('#rgonws-deploy-path').value.trim(),msg=$('#rgonws-deploy-msg').value.trim();
  if(!txt.trim()){dlog('⚠️ 내용이 비어 있습니다');return;}
  if(!confirm('GitHub의 ['+(path||'?')+'] 파일 전체를 이 내용으로 덮어써 커밋합니다. 진행할까요?'))return;
  LS.set('rgon_deploy_path',path);dlog('☁️ GitHub 커밋 중…');
  ghCommit(path,txt,msg).then(function(j){var c=j&&j.commit;dlog('✅ 커밋 완료 '+(c?(String(c.sha).slice(0,7)+' '+(c.html_url||'')):''));toast('☁️ GitHub 커밋 완료');})
  .catch(function(e){dlog('❌ '+e.message);});
}
function deployTG(){
  var txt=$('#rgonws-deploy-text').value,path=$('#rgonws-deploy-path').value.trim();
  if(!txt.trim()){dlog('⚠️ 내용이 비어 있습니다');return;}
  LS.set('rgon_deploy_path',path);
  var head='#RGON_EXEC'+(path?(' path='+path):'');
  dlog('✈️ 텔레그램 전송 중…');
  tgSend(head+'\n\n'+txt,(head.length+txt.length)>3900,head).then(function(){dlog('✅ 문지기로 전송 완료');toast('✈️ 집PC 문지기 전송 완료');})
  .catch(function(e){dlog('❌ '+e.message);});
}

/* ── 설정 ── */
var FIELDS={'rgonws-url-rgon':'rgon_url_rgon','rgonws-url-claude':'rgon_url_claude','rgonws-url-gpt':'rgon_url_gpt','rgonws-url-grok':'rgon_url_grok','rgonws-gh-pat':'rgon_gh_pat','rgonws-gh-repo':'rgon_gh_repo','rgonws-gh-branch':'rgon_gh_branch','rgonws-tg-token':'rgon_tg_token','rgonws-tg-chat':'rgon_tg_chat','rgonws-brief-url':'rgon_brief_url'};
function loadSettings(){Object.keys(FIELDS).forEach(function(id){var el=document.getElementById(id);if(el)el.value=LS.get(FIELDS[id],id==='rgonws-gh-branch'?'main':'');});}
function saveSettings(){Object.keys(FIELDS).forEach(function(id){var el=document.getElementById(id);if(el)LS.set(FIELDS[id],String(el.value||'').trim());});toast('💾 설정 저장 완료 (이 기기에만 보관)');}
function toggleSettings(){var d=$('#rgonws-drawer');var o=d.classList.toggle('open');if(o)loadSettings();}

/* ── 기존 대형 황금 패널 / PC 컨트롤러 접기 ── */
var LEGACY_TEXT=/대화창에\s*호출|실시간\s*브리핑|PC\s*전용|PC\s*컨트롤|원격\s*PC|컨트롤러/i;
var LEGACY_ATTR_SEL='[class*="gold" i],[id*="gold" i],[class*="pc-ctrl" i],[id*="pc-ctrl" i],[class*="pc_ctrl" i],[id*="pcctrl" i],[class*="controller" i],[id*="controller" i],[class*="big-panel" i],[id*="big-panel" i]';
function markLegacy(){
  var input=findInput(),top=$('#rgonws-top');
  var cands=[];
  try{cands=$$(LEGACY_ATTR_SEL);}catch(e){}

  $$('button,a').forEach(function(b){if(LEGACY_TEXT.test(b.textContent||''))cands.push(b);});
  cands.forEach(function(el){
    if(ours(el)||el.classList.contains('rgonws-legacy')||el===document.body||el===document.documentElement)return;
    if(input&&el.contains(input))return;
    if(top&&el.contains(top))return;
    var target=el,p=el.parentElement,lv=0;
    while(p&&p!==document.body&&lv<2){
      if(input&&p.contains(input))break;
      if(top&&p.contains(top))break;
      if(p.querySelectorAll('button').length>12||p.querySelector('textarea'))break;
      target=p;p=p.parentElement;lv++;
    }
    target.classList.add('rgonws-legacy');
  });
}
function toggleLegacy(){
  markLegacy();var B=document.body.classList;
  if(MOBILE_Q.matches){B.toggle('rgonws-show-legacy');B.remove('rgonws-hide-legacy');toast(B.contains('rgonws-show-legacy')?'🔼 기존 대형패널 표시':'🔽 기존 대형패널 접기');}
  else{B.toggle('rgonws-hide-legacy');toast(B.contains('rgonws-hide-legacy')?'🔽 기존 대형패널 접기':'🔼 기존 대형패널 표시');}
}

/* ── 하단 입력 도크 (찌그러짐 복구) ── */
function isRowFlex(el){
  if(!el||el===document.body||el===document.documentElement)return false;
  var cs=getComputedStyle(el);
  return cs.display.indexOf('flex')>=0&&cs.flexDirection.indexOf('row')===0;
}
function fixInput(){

  $$('.rgon-bottom-clear').forEach(function(n){if(!ours(n))n.remove();});
  var el=findInput();if(!el)return;
  el.classList.add('rgonws-input-fix');
  var row=el.parentElement;
  if(!isRowFlex(row)){row=el;}
  else{while(row.parentElement&&isRowFlex(row.parentElement))row=row.parentElement;}
  if(!row.parentNode)return;
  var dock=$('.rgonws-dock');
  if(dock&&dock.nextElementSibling===row)return;
  if(!dock){
    dock=document.createElement('div');dock.className='rgonws-dock';
    dock.innerHTML='<button type="button" class="rgonws-btn" data-act="clear-input">🧹 입력창 비우기</button>'+
                   '<button type="button" class="rgonws-btn" data-act="paste">📥 클립보드 붙여넣기</button>'+
                   '<button type="button" class="rgonws-btn" data-act="reset-all">🗑️ 전체 초기화</button>';
  }
  row.parentNode.insertBefore(dock,row);
}
function clearInput(){var el=findInput();if(el){setVal(el,'');el.focus();}toast('🧹 입력창 비움');}
function resetAll(){
  if(!confirm('입력창 · 장전 지시문 · 브리핑 카드 · 음성을 모두 초기화할까요?'))return;
  var el=findInput();if(el)setVal(el,'');
  LS.del('rgon_loaded_directive');lastCardsText='';
  var c=$('#rgonws-cards');if(c){c.classList.remove('open');c.innerHTML='';}
  try{speechSynthesis.cancel();}catch(e){}
  toast('🗑️ 전체 초기화 완료');
}

/* ── 이벤트 ── */
document.addEventListener('click',function(e){
  var b=e.target&&e.target.closest?e.target.closest('[data-act],[data-ai]'):null;
  if(!b||!ours(b))return;
  e.preventDefault();
  var ai=b.getAttribute('data-ai');if(ai){relay(ai);return;}
  switch(b.getAttribute('data-act')){
    case 'copy':copyCurrent();break;
    case 'paste':pasteToInput();break;
    case 'settings':toggleSettings();break;
    case 'save':saveSettings();break;
    case 'brief':showCards(null);break;
    case 'tts':tts();break;
    case 'top1':top1();break;
    case 'tg':tgBrief();break;
    case 'f-nvda':case 'f-media':case 'f-immune':showCards(b.getAttribute('data-act'));break;
    case 'deploy':openDeploy();break;
    case 'legacy':toggleLegacy();break;
    case 'cards-close':var c=$('#rgonws-cards');c.classList.remove('open');c.innerHTML='';break;
    case 'clear-input':clearInput();break;
    case 'reset-all':resetAll();break;
    case 'd-paste':readClip().then(function(t){$('#rgonws-deploy-text').value=t||'';dlog('📥 클립보드 '+(t||'').length+'자');}).catch(clipFail);break;
    case 'd-gh':deployGH();break;
    case 'd-tg':deployTG();break;
    case 'd-close':closeDeploy();break;
  }
},false);
document.addEventListener('click',function(e){if(e.target&&e.target.id==='rgonws-modal')closeDeploy();},false);

function init(){
  var top=$('#rgonws-top');
  if(top&&document.body.firstElementChild!==top)document.body.insertBefore(top,document.body.firstChild);
  ['#rgonws-modal','#rgonws-toast'].forEach(function(s){var n=$(s);if(n&&n.parentNode!==document.body)document.body.appendChild(n);});
  loadSettings();fixInput();markLegacy();
  var to;
  try{new MutationObserver(function(){clearTimeout(to);to=setTimeout(function(){fixInput();markLegacy();},350);}).observe(document.body,{childList:true,subtree:true});}catch(e){}
  window.addEventListener('resize',function(){clearTimeout(to);to=setTimeout(fixInput,250);});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
</script>"""

HTML_BLOCK = HTML_START + "\n" + HTML_BLOCK_BODY + "\n" + HTML_END

# ─────────────────────────────────────────────────────────────
# 크롬 확장 흡수창 지우기 블록
# ─────────────────────────────────────────────────────────────
EXT_BLOCK_BODY = r""";(function(){
  try{
    if(typeof window==='undefined'||typeof document==='undefined')return;
    if(window.__rgonExtClearV3)return;window.__rgonExtClearV3=true;
    var IS_EXT=(location.protocol==='chrome-extension:');
    var HOST_SEL='[id*="omni" i],[class*="omni" i],[id*="absorb" i],[class*="absorb" i],[data-omni],[data-rgon-absorb]';
    function setVal(el,v){
      var proto=el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
      var d=Object.getOwnPropertyDescriptor(proto,'value');
      if(d&&d.set)d.set.call(el,v);else el.value=v;
      el.dispatchEvent(new Event('input',{bubbles:true}));
      el.dispatchEvent(new Event('change',{bubbles:true}));
    }
    function isRowFlex(el){
      if(!el||el===document.body||el===document.documentElement)return false;
      var cs=getComputedStyle(el);
      return cs.display.indexOf('flex')>=0&&cs.flexDirection.indexOf('row')===0;
    }
    function eligible(t){
      if(t.dataset.rgonClearBound==='1')return false;
      if(t.closest('.rgon-ext-clear-bar'))return false;
      if(IS_EXT)return true;
      var hint=(t.getAttribute('placeholder')||'')+' '+(t.id||'')+' '+(t.name||'');
      return !!t.closest(HOST_SEL)||/흡수|absorb|omni/i.test(hint);
    }
    function panelOf(t){return t.closest(HOST_SEL)||t.closest('form')||(IS_EXT?document.body:t.parentElement);}
    function makeBtn(label,title,fn){
      var b=document.createElement('button');b.type='button';b.textContent=label;b.title=title;
      b.style.cssText='white-space:nowrap;flex:0 0 auto;padding:4px 10px;border-radius:8px;border:1px solid #d4af37;background:#161b22;color:#f5d76e;font-size:12px;cursor:pointer;line-height:1.2;word-break:keep-all';
      b.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();fn();});
      return b;
    }
    function bind(t){
      t.dataset.rgonClearBound='1';
      var bar=document.createElement('div');bar.className='rgon-ext-clear-bar';
      bar.style.cssText='display:flex;gap:6px;width:100%;box-sizing:border-box;margin:4px 0;flex-wrap:nowrap;flex:0 0 100%';
      bar.appendChild(makeBtn('🧹 지우기','이 흡수창 비우기',function(){setVal(t,'');t.focus();}));
      bar.appendChild(makeBtn('🗑️ 전체 지우기','패널 내 모든 입력 + 저장된 흡수 버퍼 초기화',function(){
        if(!confirm('흡수창 전체를 지울까요? (저장된 흡수 버퍼 포함)'))return;
        var p=panelOf(t)||document.body;
        Array.prototype.forEach.call(p.querySelectorAll('textarea,input[type="text"],input:not([type])'),function(x){setVal(x,'');});
        if(IS_EXT){
          try{
            if(window.chrome&&chrome.storage&&chrome.storage.local){
              chrome.storage.local.get(null,function(all){
                var ks=Object.keys(all||{}).filter(function(k){return /absorb|흡수|buffer|draft|pending/i.test(k);});
                if(ks.length)chrome.storage.local.remove(ks);
              });
            }
          }catch(e){}
          try{Object.keys(localStorage).forEach(function(k){if(/absorb|흡수/i.test(k))localStorage.removeItem(k);});}catch(e){}
        }
      }));
      var anchor=t,p=t.parentElement;
      while(p&&isRowFlex(p)){anchor=p;p=p.parentElement;}
      if(anchor.parentNode)anchor.parentNode.insertBefore(bar,anchor);
    }
    function scan(){Array.prototype.forEach.call(document.querySelectorAll('textarea'),function(t){try{if(eligible(t))bind(t);}catch(e){}});}
    function start(){
      scan();
      try{var to;new MutationObserver(function(){clearTimeout(to);to=setTimeout(scan,300);}).observe(document.documentElement,{childList:true,subtree:true});}catch(e){}
    }
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
  }catch(e){}
})();"""

EXT_BLOCK = EXT_START + "\n" + EXT_BLOCK_BODY + "\n" + EXT_END

# ─────────────────────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────────────────────
REPORT = []


def log(msg):
    print(msg)
    REPORT.append(msg)


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
            f.write("# RGON step3 backups\n" + "\n".join(add) + "\n")
        log(f"🛡️ .git/info/exclude 에 {add} 추가")
    else:
        log("🛡️ .git/info/exclude 백업 제외 규칙 이미 존재")


NODE = shutil.which("node")


def node_check_path(path: Path):
    if not NODE:
        return None, "node 미설치"
    try:
        r = subprocess.run([NODE, "--check", str(path)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except Exception as e:
        return False, str(e)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def node_check_code(code: str, suffix=".js"):
    if not NODE:
        return None, "node 미설치"
    fd, tmp = tempfile.mkstemp(suffix=suffix, prefix="rgon_chk_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)
        return node_check_path(Path(tmp))
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def script_spans(text):
    return [(m.start(), m.end()) for m in SCRIPT_SPAN_RE.finditer(text)]


def remove_static_bottom_clear(text):
    spans = script_spans(text)
    removed = 0

    def repl(m):
        nonlocal removed
        s, e = m.start(), m.end()
        if any(a <= s < b or a < e <= b for a, b in spans):
            return m.group(0)
        if ID_RE.search(m.group(0)):
            return m.group(0)
        removed += 1
        return ""

    return BOTTOM_CLEAR_RE.sub(repl, text), removed


# ─────────────────────────────────────────────────────────────
# HTML 패치
# ─────────────────────────────────────────────────────────────
def patch_html(p: Path):
    text, enc, bom = read_text(p)
    outside_before = HTML_BLOCK_RE.sub("", text)
    ids_before = set(ID_RE.findall(outside_before))

    if HTML_BLOCK_RE.search(text):
        first = [True]

        def repl(_m):
            if first[0]:
                first[0] = False
                return HTML_BLOCK
            return ""

        new = HTML_BLOCK_RE.sub(repl, text)
        mode = "블록 교체"
    else:
        idx = text.lower().rfind("</body>")
        if idx >= 0:
            new = text[:idx] + HTML_BLOCK + "\n" + text[idx:]
        else:
            new = text + "\n" + HTML_BLOCK + "\n"
        mode = "신규 삽입"

    new, removed = remove_static_bottom_clear(new)

    ids_after = set(ID_RE.findall(new))
    missing = ids_before - ids_after
    if missing:
        log(f"❌ [{p.relative_to(ROOT)}] 기존 id 손실 감지 → 중단: {sorted(missing)[:10]}")
        return False
    lack = REQUIRED_NEW_IDS - ids_after
    if lack:
        log(f"❌ [{p.relative_to(ROOT)}] 신규 id 누락 → 중단: {sorted(lack)}")
        return False

    m = re.search(r'<script id="rgonws-script">(.*?)</script>', new, re.S)
    ok, msg = node_check_code(m.group(1) if m else "")
    if ok is False:
        log(f"❌ [{p.relative_to(ROOT)}] JS 문법 오류 → 중단\n{msg}")
        return False
    if ok is None:
        log(f"⚠️ node 미설치 → [{p.relative_to(ROOT)}] 문법검사 생략")

    if new == text:
        log(f"⏭️ [{p.relative_to(ROOT)}] 변경 없음")
        return True

    b = backup(p)
    write_text(p, new, enc, bom)
    log(f"✅ [{p.relative_to(ROOT)}] {mode} 완료 (id {len(ids_before)}개 보존, "
        f"정적 rgon-bottom-clear {removed}개 제거, 백업: {b.name})")
    return True


# ─────────────────────────────────────────────────────────────
# 확장 JS 패치
# ─────────────────────────────────────────────────────────────
def find_ext_dirs():
    found = []
    main = ROOT / EXT_DIRNAME
    if main.is_dir():
        found.append(main.resolve())
    for dirpath, dirnames, _files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in PRUNE_DIRS and "backup" not in d.lower() and not d.startswith(".")]
        for d in dirnames:
            if d == EXT_DIRNAME:
                full = (Path(dirpath) / d).resolve()
                if "backup" in str(full).lower():
                    continue
                if full not in found:
                    found.append(full)
    return found


def patch_ext_js(p: Path):
    rel = p.relative_to(ROOT) if str(p).startswith(str(ROOT)) else p
    text, enc, bom = read_text(p)
    orig_ok, _ = node_check_path(p)

    base = EXT_BLOCK_RE.sub("\n", text).rstrip()
    new = base + "\n\n" + EXT_BLOCK + "\n"

    if orig_ok is True:
        ok, msg = node_check_code(new)
        if ok is False:
            log(f"❌ [{rel}] 패치 후 문법 오류 → 중단\n{msg}")
            return False
    else:
        ok, msg = node_check_code(EXT_BLOCK)
        if ok is False:
            log(f"❌ [{rel}] 삽입 블록 문법 오류 → 중단\n{msg}")
            return False
        if orig_ok is False:
            log(f"⚠️ [{rel}] 원본이 node --check 비호환(ESM 등) → 삽입 블록만 검사 통과")
        else:
            log(f"⚠️ node 미설치 → [{rel}] 문법검사 생략")

    if new == text:
        log(f"⏭️ [{rel}] 변경 없음")
        return True

    b = backup(p)
    write_text(p, new, enc, bom)
    log(f"✅ [{rel}] 🧹 지우기 / 🗑️ 전체 지우기 장착 (백업: {b.name})")
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
    log(f"🏛️ RGON STEP3 마스터 워크스테이션 패치 시작 — 루트: {ROOT}")
    ensure_git_exclude()

    html_ok = html_fail = 0
    for rel in HTML_TARGETS:
        p = ROOT / rel
        if not p.is_file():
            log(f"⏭️ [{rel}] 없음 → 건너뜀")
            continue
        try:
            if patch_html(p):
                html_ok += 1
            else:
                html_fail += 1
        except Exception as e:
            html_fail += 1
            log(f"❌ [{rel}] 예외: {e}")

    ext_ok = ext_fail = 0
    ext_dirs = find_ext_dirs()
    if not ext_dirs:
        log(f"⏭️ {EXT_DIRNAME}/ 폴더를 찾지 못함 → 확장 패치 생략")
    for d in ext_dirs:
        hit = False
        for name in EXT_FILES:
            p = d / name
            if p.is_file():
                hit = True
                try:
                    if patch_ext_js(p):
                        ext_ok += 1
                    else:
                        ext_fail += 1
                except Exception as e:
                    ext_fail += 1
                    log(f"❌ [{p}] 예외: {e}")
        if not hit:
            log(f"⏭️ [{d}] core.js/content.js/popup.js 없음")

    log(f"📋 결과: HTML 성공 {html_ok} / 실패 {html_fail} · 확장 JS 성공 {ext_ok} / 실패 {ext_fail}")

    if html_fail or ext_fail:
        log("⚠️ 실패 항목이 있어도 성공한 파일은 동기화합니다 (실패 파일은 원본 그대로 유지됨).")
    if html_ok or ext_ok:
        git_sync()
    else:
        log("ℹ️ 반영된 파일이 없어 Git 동기화 생략")

    log("🏁 완료 — 크롬 확장은 chrome://extensions 에서 [새로고침]을 눌러 적용하세요.")


if __name__ == "__main__":
    main()
