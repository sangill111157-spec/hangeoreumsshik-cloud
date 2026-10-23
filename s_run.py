#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step4_ultra_clean_ui.py
 모바일 독대실 UI 초슬림 개편
  (1) 상단 초록 상태바 숨김 (정보는 사이드 서랍 하단에 작게 표시)
  (2) 갈색 4층 버튼 → 1층 4분할 그리드 (원본 DOM/id/onclick 100% 보존 + 대리 클릭)
  (3) 상단 7버튼 1줄 고정 + 나머지 전부 우측 ☰ 슬라이드 서랍으로 수납
  (4) 하단 입력창: 지우기 바 제거, 넓은 폭 1줄 유지
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

HTML_START = "<!-- === [RGON-STEP1-MOBILE-UI-START] === -->"
HTML_END = "<!-- === [RGON-STEP1-MOBILE-UI-END] === -->"

COMMIT_MSG = "feat(ui): Step 4 ultra-clean header + 1-row 4-col brown bar + side drawer"

REQUIRED_NEW_IDS = {
    "rgons4-style", "rgons4-top", "rgons4-bar", "rgons4-quad", "rgons4-cards",
    "rgons4-backdrop", "rgons4-drawer", "rgons4-toast", "rgons4-script",
}

ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.I)
HTML_BLOCK_RE = re.compile(re.escape(HTML_START) + r".*?" + re.escape(HTML_END), re.S)
SCRIPT_SPAN_RE = re.compile(r"<script\b.*?</script\s*>", re.S | re.I)
BOTTOM_CLEAR_RE = re.compile(
    r'<(button|span|div)\b[^>]*\bclass\s*=\s*["\'][^"\']*\b(?:rgon-bottom-clear|rgonws-dock)\b[^"\']*["\'][^>]*>'
    r'(?:(?!<\1\b).)*?</\1\s*>',
    re.S | re.I,
)

# ─────────────────────────────────────────────────────────────
# Step 4 초슬림 블록 (CSS + 마크업 + JS)
# ─────────────────────────────────────────────────────────────
HTML_BLOCK_BODY = r"""<style id="rgons4-style">
#rgons4-top{position:sticky;top:0;left:0;right:0;z-index:9000;flex:0 0 auto;width:100%;max-width:100vw;box-sizing:border-box;padding:5px 6px 6px;background:rgba(13,17,23,.97);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);border-bottom:1px solid rgba(212,175,55,.4);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif}
#rgons4-top *,#rgons4-drawer *{box-sizing:border-box}
#rgons4-bar{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:4px;width:100%}
.rgons4-b{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;min-width:0;width:100%;padding:5px 1px;border-radius:10px;border:1px solid rgba(212,175,55,.65);background:#161b22;color:#f5d76e;cursor:pointer;white-space:nowrap!important;overflow:hidden;-webkit-tap-highlight-color:transparent;touch-action:manipulation;font-family:inherit}
.rgons4-b .e{font-size:15px;line-height:1.1}
.rgons4-b .t{font-size:10.5px;line-height:1.15;font-weight:600;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rgons4-b.ai{border-color:#58a6ff;color:#cde6ff}
.rgons4-b.more{border-color:#8b949e;color:#e6edf3}
.rgons4-b:active,.rgons4-q:active,.rgons4-chip:active{transform:scale(.95)}
#rgons4-quad{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:6px;width:100%}
.rgons4-q{min-width:0;white-space:nowrap!important;overflow:hidden;text-overflow:ellipsis;padding:7px 2px;border-radius:10px;border:1px solid #8b5a2b;background:linear-gradient(180deg,#4a3320,#2e2014);color:#f5deb3;font-size:12.5px;font-weight:700;cursor:pointer;font-family:inherit;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
@media (min-width:640px){.rgons4-b{flex-direction:row;gap:4px;padding:7px 4px}.rgons4-b .t{font-size:12.5px}.rgons4-q{font-size:13.5px}}
#rgons4-cards{display:none;margin-top:6px;max-height:45vh;overflow:auto;-webkit-overflow-scrolling:touch}
#rgons4-cards.open{display:block}
.rgons4-cards-head{display:flex;align-items:center;gap:8px;position:sticky;top:0;background:#0d1117;padding:4px 0;color:#f5d76e;font-size:13px}
.rgons4-cards-head span{flex:1 1 auto;color:#8b949e;font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rgons4-card{background:#161b22;border:1px solid #30363d;border-left:3px solid #d4af37;border-radius:10px;padding:8px 10px;margin-bottom:6px;color:#e6edf3;font-size:13px}
.rgons4-card-t{font-weight:700;color:#f5d76e;margin-bottom:4px}
.rgons4-card pre{margin:0;white-space:pre-wrap;word-break:break-word;font-family:inherit;font-size:12px;color:#c9d1d9}
#rgons4-backdrop{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.55);opacity:0;pointer-events:none;transition:opacity .22s}
#rgons4-backdrop.open{opacity:1;pointer-events:auto}
#rgons4-drawer{position:fixed;top:0;right:0;width:300px;max-width:85vw;height:100vh;height:100dvh;z-index:10000;background:#0d1117;border-left:1px solid rgba(212,175,55,.45);transform:translateX(105%);transition:transform .25s ease;display:flex;flex-direction:column;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif;color:#e6edf3;box-shadow:-8px 0 24px rgba(0,0,0,.45)}
#rgons4-drawer.open{transform:translateX(0)}
.rgons4-dh{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border-bottom:1px solid #21262d;flex:0 0 auto}
.rgons4-dh b{color:#f5d76e;font-size:15px}
.rgons4-db{flex:1 1 auto;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:8px 12px 16px}
.rgons4-sec{margin:10px 0 14px}
.rgons4-sec h4{margin:0 0 6px;font-size:12.5px;color:#d4af37;font-weight:700}
.rgons4-chips{display:flex;flex-wrap:wrap;gap:6px}
.rgons4-chip{white-space:nowrap!important;flex:0 0 auto;padding:6px 10px;border-radius:999px;border:1px solid rgba(212,175,55,.65);background:#161b22;color:#f5d76e;font-size:12.5px;font-weight:600;cursor:pointer;font-family:inherit;-webkit-tap-highlight-color:transparent}
.rgons4-chip.danger{border-color:#f85149;color:#ffb3ad}
.rgons4-chip.wide{flex:1 1 100%;text-align:center}
.rgons4-f{display:flex;flex-direction:column;gap:3px;font-size:11.5px;color:#c9d1d9;margin-bottom:6px}
.rgons4-f input,#rgons4-deploy-text{width:100%;padding:7px 9px;border-radius:8px;border:1px solid #30363d;background:#010409;color:#e6edf3;font-size:13px;font-family:inherit}
#rgons4-deploy-text{min-height:120px;font-family:ui-monospace,Consolas,monospace;font-size:12px;margin-bottom:6px}
#rgons4-deploy-log{margin-top:6px;font-size:11px;color:#8b949e;white-space:pre-wrap;word-break:break-all;max-height:110px;overflow:auto}
.rgons4-note{font-size:10.5px;color:#8b949e;margin:4px 0}
.rgons4-foot{flex:0 0 auto;border-top:1px solid #21262d;padding:8px 12px calc(8px + env(safe-area-inset-bottom));font-size:10.5px;color:#7ee787}
#rgons4-status-raw{color:#6e7681;margin-top:2px;max-height:48px;overflow:hidden;word-break:break-all}
#rgons4-toast{position:fixed;left:50%;bottom:92px;transform:translateX(-50%) translateY(16px);background:#161b22;color:#f5d76e;border:1px solid #d4af37;padding:8px 14px;border-radius:999px;font-size:13px;z-index:10002;opacity:0;pointer-events:none;transition:.2s;white-space:nowrap;max-width:92vw;overflow:hidden;text-overflow:ellipsis}
#rgons4-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.rgons4-status-hide{display:none!important}
body:not(.rgons4-show-legacy) .rgons4-hide{display:none!important}
.rgon-bottom-clear,.rgonws-dock{display:none!important}
textarea.rgons4-input-fix,input.rgons4-input-fix{flex:1 1 0% !important;min-width:160px!important;width:100%!important;max-width:none!important}
body.rgons4-lock{overflow:hidden!important}
</style>
<div id="rgons4-top">
  <div id="rgons4-bar">
    <button type="button" class="rgons4-b" data-act="copy" title="입력창/장전 지시문 복사"><span class="e">📋</span><span class="t">복사</span></button>
    <button type="button" class="rgons4-b" data-act="paste" title="클립보드 붙여넣기"><span class="e">📥</span><span class="t">붙임</span></button>
    <button type="button" class="rgons4-b ai" data-ai="rgon" title="자동복사 후 르곤 방 이동"><span class="e">🔵</span><span class="t">르곤</span></button>
    <button type="button" class="rgons4-b ai" data-ai="claude" title="자동복사 후 클로드 방 이동"><span class="e">🤖</span><span class="t">클로드</span></button>
    <button type="button" class="rgons4-b ai" data-ai="gpt" title="자동복사 후 GPT 방 이동"><span class="e">⚡</span><span class="t">GPT</span></button>
    <button type="button" class="rgons4-b ai" data-ai="grok" title="자동복사 후 Grok 방 이동"><span class="e">🎯</span><span class="t">Grok</span></button>
    <button type="button" class="rgons4-b more" data-act="drawer" title="더보기"><span class="e">☰</span><span class="t">더보기</span></button>
  </div>
  <div id="rgons4-quad">
    <button type="button" class="rgons4-q" data-quad="brief">📋 브리핑</button>
    <button type="button" class="rgons4-q" data-quad="tts">🔊 음성</button>
    <button type="button" class="rgons4-q" data-quad="top1">🧠 Top1</button>
    <button type="button" class="rgons4-q" data-quad="tg">✈️ 로건봇</button>
  </div>
  <div id="rgons4-cards"></div>
</div>
<div id="rgons4-backdrop"></div>
<aside id="rgons4-drawer" aria-hidden="true">
  <div class="rgons4-dh"><b>☰ 더보기</b><button type="button" class="rgons4-chip" data-act="drawer-close">✕ 닫기</button></div>
  <div class="rgons4-db">
    <div class="rgons4-sec">
      <h4>🧹 지우기 도구</h4>
      <div class="rgons4-chips">
        <button type="button" class="rgons4-chip" data-act="clear-input">🧹 입력창 비우기</button>
        <button type="button" class="rgons4-chip danger" data-act="reset-all">🗑️ 대화·흡수 전체 초기화</button>
      </div>
    </div>
    <div class="rgons4-sec">
      <h4>📊 청사별 세부 브리핑</h4>
      <div class="rgons4-chips">
        <button type="button" class="rgons4-chip" data-act="brief">📊 6청사 종합</button>
        <button type="button" class="rgons4-chip" data-act="f-nvda">📈 1청사 NVDA·시트</button>
        <button type="button" class="rgons4-chip" data-act="f-media">🎬 3청사 미디어·틱톡</button>
        <button type="button" class="rgons4-chip" data-act="f-immune">🧬 R1~R14 항체·진화</button>
        <button type="button" class="rgons4-chip" data-act="tts">🔊 TTS 읽기</button>
      </div>
    </div>
    <div class="rgons4-sec">
      <h4>🚀 모바일 즉시 반영 (GitHub / 텔레그램)</h4>
      <textarea id="rgons4-deploy-text" placeholder="다른 AI 방에서 복사해 온 코드/명령"></textarea>
      <label class="rgons4-f">커밋 경로<input id="rgons4-deploy-path" type="text" placeholder="dashboard/rgon_alpha_chat.html"></label>
      <label class="rgons4-f">커밋 메시지 (선택)<input id="rgons4-deploy-msg" type="text" placeholder="mobile: update"></label>
      <div class="rgons4-chips">
        <button type="button" class="rgons4-chip" data-act="d-paste">📥 클립보드</button>
        <button type="button" class="rgons4-chip" data-act="d-gh">☁️ GitHub 커밋</button>
        <button type="button" class="rgons4-chip" data-act="d-tg">✈️ 집PC 문지기</button>
      </div>
      <div class="rgons4-note">텔레그램 전송분은 집 PC rgon_auto_watcher.py가 #RGON_EXEC 태그로 수신·처리합니다.</div>
      <div id="rgons4-deploy-log"></div>
    </div>
    <div class="rgons4-sec">
      <h4>🔗 내 젠스파크 채팅방 고정 주소</h4>
      <label class="rgons4-f">🔵 르곤<input id="rgons4-url-rgon" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <label class="rgons4-f">🤖 클로드<input id="rgons4-url-claude" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <label class="rgons4-f">⚡ GPT<input id="rgons4-url-gpt" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <label class="rgons4-f">🎯 Grok<input id="rgons4-url-grok" type="url" placeholder="https://www.genspark.ai/agents?id=..."></label>
      <button type="button" class="rgons4-chip wide" data-act="save">💾 주소 저장</button>
    </div>
    <div class="rgons4-sec">
      <h4>🔑 GitHub PAT / 텔레그램 봇 설정</h4>
      <label class="rgons4-f">GitHub PAT (선택)<input id="rgons4-gh-pat" type="password" autocomplete="off" placeholder="github_pat_..."></label>
      <label class="rgons4-f">저장소 (owner/repo)<input id="rgons4-gh-repo" type="text" autocomplete="off" placeholder="owner/shin-agent"></label>
      <label class="rgons4-f">브랜치<input id="rgons4-gh-branch" type="text" placeholder="main"></label>
      <label class="rgons4-f">텔레그램 봇 토큰 (선택)<input id="rgons4-tg-token" type="password" autocomplete="off" placeholder="123456:ABC..."></label>
      <label class="rgons4-f">텔레그램 chat_id<input id="rgons4-tg-chat" type="text" placeholder="123456789"></label>
      <label class="rgons4-f">브리핑 JSON 경로 (선택)<input id="rgons4-brief-url" type="text" placeholder="data/rgon_briefing.json"></label>
      <button type="button" class="rgons4-chip wide" data-act="save">💾 설정 저장</button>
      <div class="rgons4-note">🔒 모든 값은 이 기기 localStorage에만 저장되며 GitHub/텔레그램 API 호출 외 외부 전송 0%.</div>
      <button type="button" class="rgons4-chip wide" data-act="legacy">🔽 기존 원본 패널(갈색 4층·PC 컨트롤러) 보기/숨기기</button>
    </div>
  </div>
  <div class="rgons4-foot">
    <div>🟢 실시간 동기화 ON · v6.2.0 · R1~R14</div>
    <div id="rgons4-status-raw"></div>
  </div>
</aside>
<div id="rgons4-toast"></div>
<script id="rgons4-script">
(function(){
'use strict';
if(window.__rgonS4)return;window.__rgonS4=true;
var LS={get:function(k,d){try{var v=localStorage.getItem(k);return v==null?(d||''):v;}catch(e){return d||'';}},set:function(k,v){try{localStorage.setItem(k,v);}catch(e){}},del:function(k){try{localStorage.removeItem(k);}catch(e){}}};
var DEFAULT_URL='https://www.genspark.ai/agents';
function $(s,r){return (r||document).querySelector(s);}
function $$(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));}
function ours(el){return !!(el&&el.closest&&el.closest('#rgons4-top,#rgons4-drawer,#rgons4-backdrop,#rgons4-toast'));}
function visible(el){return !!(el&&(el.offsetWidth||el.offsetHeight||el.getClientRects().length));}
function txt(el){return String((el&&el.textContent)||'').replace(/\s+/g,' ').trim();}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function toast(m,ms){var t=$('#rgons4-toast');if(!t)return;t.textContent=m;t.classList.add('show');clearTimeout(toast._t);toast._t=setTimeout(function(){t.classList.remove('show');},ms||2200);}

/* ── 입력창 ── */
var INPUT_SEL=['#userInput','#chatInput','#messageInput','#msgInput','#promptInput','#prompt','#input','#question'];
function findInput(){
  for(var i=0;i<INPUT_SEL.length;i++){var el=$(INPUT_SEL[i]);if(el&&!ours(el)&&/^(TEXTAREA|INPUT)$/.test(el.tagName))return el;}
  var best=null,by=-1;

  $$('textarea').forEach(function(t){if(ours(t)||!visible(t))return;var r=t.getBoundingClientRect();if(r.bottom>by){by=r.bottom;best=t;}});
  if(best)return best;
  var any=$$('textarea').filter(function(t){return !ours(t);});return any[any.length-1]||null;
}
function setVal(el,v){
  if(!el)return;
  var proto=el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
  var d=Object.getOwnPropertyDescriptor(proto,'value');
  if(d&&d.set)d.set.call(el,v);else el.value=v;
  el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));
}
function currentText(){var el=findInput();var v=el?String(el.value||'').trim():'';return v||String(LS.get('rgon_loaded_directive','')).trim();}
function fixInput(){

  $$('.rgon-bottom-clear,.rgonws-dock').forEach(function(n){if(!ours(n))n.remove();});
  var el=findInput();if(el)el.classList.add('rgons4-input-fix');
}

/* ── 클립보드 ── */
function legacy(s){try{var ta=document.createElement('textarea');ta.value=s;ta.setAttribute('readonly','');ta.style.cssText='position:fixed;left:-9999px;top:0;opacity:0';document.body.appendChild(ta);ta.select();ta.setSelectionRange(0,ta.value.length);var ok=document.execCommand('copy');ta.remove();return ok;}catch(e){return false;}}
function copyText(s){if(navigator.clipboard&&window.isSecureContext){return navigator.clipboard.writeText(s).then(function(){return true;},function(){return legacy(s);});}return Promise.resolve(legacy(s));}
function readClip(){if(navigator.clipboard&&navigator.clipboard.readText)return navigator.clipboard.readText();return Promise.reject(new Error('unsupported'));}
function clipFail(){alert('클립보드 읽기 권한이 막혀 있습니다.\n\n입력창을 길게 눌러 [붙여넣기]를 선택하거나,\n사이트 설정에서 클립보드 권한을 허용해 주세요.\n(HTTPS 또는 localhost 에서만 동작)');}
function pasteToInput(){
  return readClip().then(function(t){
    if(!t){toast('📭 클립보드가 비어 있습니다');return;}
    var el=findInput();if(!el){toast('입력창을 찾지 못했습니다');return;}
    var cur=String(el.value||'');setVal(el,cur?cur.replace(/\s*$/,'')+'\n'+t:t);el.focus();
    toast('📥 붙여넣기 완료 ('+t.length+'자)');
  }).catch(clipFail);
}
function copyCurrent(){var t=currentText();if(!t){toast('복사할 내용이 없습니다');return;}copyText(t).then(function(ok){toast(ok?('📋 '+t.length+'자 복사 완료'):'⚠️ 복사 실패');});}

/* ── 원터치 릴레이 ── */
var AI_KEYS={rgon:'rgon_url_rgon',claude:'rgon_url_claude',gpt:'rgon_url_gpt',grok:'rgon_url_grok'};
var AI_NAMES={rgon:'르곤',claude:'클로드',gpt:'GPT',grok:'Grok'};
function relay(ai){
  var url=String(LS.get(AI_KEYS[ai],'')).trim()||DEFAULT_URL;var t=currentText();
  var go=function(){window.location.href=url;};
  if(!t){toast('➡️ '+AI_NAMES[ai]+' 방으로 이동');setTimeout(go,250);return;}
  copyText(t).then(function(ok){toast(ok?('📋 '+t.length+'자 자동복사 → '+AI_NAMES[ai]+' 이동'):'⚠️ 자동복사 실패 — 이동 후 수동 붙여넣기',1400);setTimeout(go,ok?450:1300);});
}

/* ── 브리핑 JSON ── */
var BRIEF_CANDIDATES=['rgon_briefing.json','data/rgon_briefing.json','dashboard/rgon_briefing.json','docs/rgon_briefing.json','../rgon_briefing.json','../data/rgon_briefing.json','briefing.json','data/briefing.json','rgon_six_ministries.json'];
var lastCardsText='';
function loadBrief(){
  var list=[];var c=String(LS.get('rgon_brief_url','')).trim();if(c)list.push(c);list=list.concat(BRIEF_CANDIDATES);var i=0;
  function next(){
    if(i>=list.length)return Promise.reject(new Error('no brief'));
    var u=list[i++];var sep=u.indexOf('?')<0?'?':'&';
    return fetch(u+sep+'_t='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error('http');return r.json();}).then(function(j){return {url:u,data:j};}).catch(next);
  }
  return next();
}
function toItems(d){
  if(Array.isArray(d))return d.map(function(v,i){return {key:String(i+1),val:v};});
  if(d&&typeof d==='object'){
    var k=['items','cards','ministries','briefings','data','list'].filter(function(x){return Array.isArray(d[x]);})[0];
    if(k)return toItems(d[k]);
    return Object.keys(d).map(function(x){return {key:x,val:d[x]};});
  }
  return [{key:'brief',val:d}];
}
function titleOf(it){var v=it.val;if(v&&typeof v==='object')return v.title||v.name||v.ministry||v.label||v.id||it.key;return it.key;}
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
function closeBtn(){return '<button type="button" class="rgons4-chip" data-act="cards-close">✕</button>';}
function showCards(fk){
  var box=$('#rgons4-cards');box.classList.add('open');box.innerHTML='<div class="rgons4-card">⏳ 브리핑 불러오는 중…</div>';
  loadBrief().then(function(b){
    var items=toItems(b.data),f=fk?FILTERS[fk]:null;
    if(f)items=items.filter(function(it){var s;try{s=it.key+' '+JSON.stringify(it.val);}catch(e){s=it.key;}return f.re.test(s);});
    var head='<div class="rgons4-cards-head"><b>'+(f?esc(f.name):'📊 6청사 종합브리핑')+'</b><span>'+esc(b.url)+' · '+esc(new Date().toLocaleTimeString())+'</span>'+closeBtn()+'</div>';
    if(!items.length){box.innerHTML=head+'<div class="rgons4-card">해당 항목이 없습니다.</div>';lastCardsText='';return;}
    lastCardsText=items.map(function(it){return titleOf(it)+'. '+bodyOf(it);}).join('\n');
    box.innerHTML=head+items.slice(0,60).map(function(it){return '<div class="rgons4-card"><div class="rgons4-card-t">'+esc(titleOf(it))+'</div><pre>'+esc(bodyOf(it))+'</pre></div>';}).join('');
  }).catch(function(){
    box.innerHTML='<div class="rgons4-cards-head"><b>📊 브리핑</b><span></span>'+closeBtn()+'</div><div class="rgons4-card">브리핑 JSON을 찾지 못했습니다. ☰ 더보기 → 설정에서 경로를 지정하세요.</div>';
  });
}

/* ── TTS ── */
function tts(){
  if(!('speechSynthesis' in window)){toast('이 브라우저는 음성합성을 지원하지 않습니다');return;}
  if(speechSynthesis.speaking||speechSynthesis.pending){speechSynthesis.cancel();toast('⏹ 음성 정지');return;}
  var speak=function(s){
    s=String(s||'').replace(/[{}\[\]"]/g,' ').slice(0,4000);
    if(!s.trim()){toast('읽을 내용이 없습니다');return;}
    var ch=s.match(/[^.!?。\n]{1,180}[.!?。\n]?/g)||[s];
    var vs=speechSynthesis.getVoices().filter(function(v){return /ko/i.test(v.lang);});
    ch.forEach(function(c){var u=new SpeechSynthesisUtterance(c);u.lang='ko-KR';u.rate=1.05;if(vs[0])u.voice=vs[0];speechSynthesis.speak(u);});
    toast('🔊 음성 재생 (다시 누르면 정지)');
  };
  if(lastCardsText){speak(lastCardsText);return;}
  loadBrief().then(function(b){speak(toItems(b.data).map(function(it){return titleOf(it)+'. '+bodyOf(it);}).join('\n'));}).catch(function(){speak(currentText());});
}

/* ── 텔레그램 / GitHub ── */
function tgSend(text,asDoc,caption){
  var tok=String(LS.get('rgon_tg_token','')).trim(),chat=String(LS.get('rgon_tg_chat','')).trim();
  if(!tok||!chat)return Promise.reject(new Error('☰ 설정에서 텔레그램 봇 토큰/chat_id를 입력하세요'));
  var base='https://api.telegram.org/bot'+tok;
  var done=function(r){return r.json().then(function(j){if(!j.ok)throw new Error(j.description||'telegram error');return j;});};
  if(!asDoc&&text.length<=4000)return fetch(base+'/sendMessage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_id:chat,text:text,disable_web_page_preview:true})}).then(done);
  var fd=new FormData();fd.append('chat_id',chat);fd.append('caption',String(caption||'#RGON_EXEC').slice(0,1000));
  fd.append('document',new Blob([text],{type:'text/plain'}),'rgon_payload.txt');
  return fetch(base+'/sendDocument',{method:'POST',body:fd}).then(done);
}
function b64utf8(s){var by=new TextEncoder().encode(s);var bin='';for(var i=0;i<by.length;i+=0x8000)bin+=String.fromCharCode.apply(null,by.subarray(i,i+0x8000));return btoa(bin);}
function ghCommit(path,content,msg){
  var pat=String(LS.get('rgon_gh_pat','')).trim(),repo=String(LS.get('rgon_gh_repo','')).trim(),br=String(LS.get('rgon_gh_branch','main')).trim()||'main';
  if(!pat||!/^[^\/\s]+\/[^\/\s]+$/.test(repo))return Promise.reject(new Error('☰ 설정에서 GitHub PAT와 저장소(owner/repo)를 입력하세요'));
  path=String(path||'').trim().replace(/^\/+/,'');if(!path)return Promise.reject(new Error('커밋 경로를 입력하세요'));
  var api='https://api.github.com/repos/'+repo+'/contents/'+path.split('/').map(encodeURIComponent).join('/');
  var h={'Authorization':'Bearer '+pat,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'};
  return fetch(api+'?ref='+encodeURIComponent(br),{headers:h,cache:'no-store'}).then(function(r){
    if(r.status===404)return null;if(!r.ok)throw new Error('조회 실패 HTTP '+r.status);return r.json();
  }).then(function(cur){
    var body={message:msg||('mobile: update '+path),content:b64utf8(content),branch:br};if(cur&&cur.sha)body.sha=cur.sha;
    return fetch(api,{method:'PUT',headers:Object.assign({'Content-Type':'application/json'},h),body:JSON.stringify(body)});
  }).then(function(r){return r.json().then(function(j){if(!r.ok)throw new Error((j&&j.message)||('HTTP '+r.status));return j;});});
}
function dlog(m){var l=$('#rgons4-deploy-log');if(l)l.textContent='['+new Date().toLocaleTimeString()+'] '+m+'\n'+l.textContent;}
function deployGH(){
  var t=$('#rgons4-deploy-text').value,p=$('#rgons4-deploy-path').value.trim(),m=$('#rgons4-deploy-msg').value.trim();
  if(!t.trim()){dlog('⚠️ 내용이 비어 있습니다');return;}
  if(!confirm('GitHub의 ['+(p||'?')+'] 파일 전체를 이 내용으로 덮어써 커밋합니다. 진행할까요?'))return;
  LS.set('rgon_deploy_path',p);dlog('☁️ GitHub 커밋 중…');
  ghCommit(p,t,m).then(function(j){var c=j&&j.commit;dlog('✅ 커밋 완료 '+(c?String(c.sha).slice(0,7):''));toast('☁️ GitHub 커밋 완료');}).catch(function(e){dlog('❌ '+e.message);});
}
function deployTG(){
  var t=$('#rgons4-deploy-text').value,p=$('#rgons4-deploy-path').value.trim();
  if(!t.trim()){dlog('⚠️ 내용이 비어 있습니다');return;}
  LS.set('rgon_deploy_path',p);var head='#RGON_EXEC'+(p?(' path='+p):'');dlog('✈️ 텔레그램 전송 중…');
  tgSend(head+'\n\n'+t,(head.length+t.length)>3900,head).then(function(){dlog('✅ 문지기로 전송 완료');toast('✈️ 집PC 문지기 전송 완료');}).catch(function(e){dlog('❌ '+e.message);});
}

/* ── 기존 4대 갈색 버튼: 원본 보존 + 대리 클릭 ── */
var CLICKABLE='button,a,[role="button"],[onclick]';
var QUAD={
  brief:{re:/대화창에\s*호출|실시간\s*브리핑[^\n]{0,14}호출/},
  tts:{re:/음성\s*아나운서|듣기\s*\/\s*정지/},
  top1:{re:/Top\s*1[^\n]{0,14}장전|자율\s*진화[^\n]{0,10}Top\s*1/i},
  tg:{re:/로건봇[^\n]{0,16}(공유|브리핑)|텔레그램\)?\s*브리핑\s*공유/}
};
var origCache={};
function findOrig(key){
  var c=origCache[key];if(c&&document.contains(c))return c;
  var re=QUAD[key].re;
  var cands=$$(CLICKABLE).filter(function(b){return !ours(b)&&re.test(txt(b));});
  cands=cands.filter(function(x){return !cands.some(function(o){return o!==x&&x.contains(o);});});
  origCache[key]=cands[0]||null;return origCache[key];
}
function findForeign(re){return $$(CLICKABLE).filter(function(b){return !ours(b)&&re.test(txt(b)+' '+(b.id||''));})[0]||null;}
function top1Fallback(){
  loadBrief().then(function(br){
    var d=br.data||{};var t=d.top1||d.top1_directive||d.top_directive||(Array.isArray(d.directives)?d.directives[0]:null);
    if(t&&typeof t==='object')t=t.text||t.directive||JSON.stringify(t,null,1);
    if(!t)throw new Error('none');
    t=String(t);LS.set('rgon_loaded_directive',t);var el=findInput();if(el){setVal(el,t);el.focus();}
    toast('🧠 Top1 지시서 장전 완료');
  }).catch(function(){toast('Top1 지시서를 찾지 못했습니다');});
}
function tgFallback(){
  var t=lastCardsText||currentText();if(!t){toast('보낼 내용이 없습니다');return;}
  tgSend('📊 [로건봇 브리핑]\n'+t).then(function(){toast('✈️ 텔레그램 발송 완료');}).catch(function(){
    if(navigator.share){navigator.share({title:'르곤 브리핑',text:t}).catch(function(){});return;}
    copyText(t);window.open('https://t.me/share/url?url='+encodeURIComponent(location.href)+'&text='+encodeURIComponent(t.slice(0,3000)),'_blank');
  });
}
var FALLBACK={brief:function(){showCards(null);},tts:tts,top1:top1Fallback,tg:tgFallback};
function quad(key){
  var o=findOrig(key);
  if(o){try{o.click();return;}catch(e){}}
  FALLBACK[key]();
}

/* ── 원본 패널 숨김 (DOM 삭제 없음) ── */
function topEl(){return $('#rgons4-top');}
function directText(el){var s='';Array.prototype.forEach.call(el.childNodes,function(n){if(n.nodeType===3)s+=n.nodeValue;});return s.trim();}
function hideUnit(el,cls){
  var t=el,p=el.parentElement,lv=0,top=topEl();
  while(p&&p!==document.body&&lv<3){
    if(ours(p)||p.querySelector('textarea')||(top&&p.contains(top)))break;
    if(p.querySelectorAll('button,a,[role="button"]').length>1)break;
    if(txt(p).length>txt(t).length+40)break;
    t=p;p=p.parentElement;lv++;
  }
  t.classList.add(cls);return t;
}
function collapseEmpty(nodes,cls){
  nodes.forEach(function(n){
    var p=n.parentElement,lv=0,top=topEl();
    while(p&&p!==document.body&&lv<2){
      if(ours(p)||p.querySelector('textarea')||(top&&p.contains(top))||directText(p))break;
      var kids=Array.prototype.slice.call(p.children);
      if(!kids.length||!kids.every(function(k){return k.classList.contains(cls)||k.classList.contains('rgons4-status-hide')||/^(SCRIPT|STYLE|BR)$/.test(k.tagName);}))break;
      p.classList.add(cls);p=p.parentElement;lv++;
    }
  });
}
var PC_RE=/PC\s*전용|PC\s*컨트롤|원격\s*PC|컨트롤러/i;
function hideLegacy(){
  var done=[];
  Object.keys(QUAD).forEach(function(k){var o=findOrig(k);if(o&&!o.closest('.rgons4-hide'))done.push(hideUnit(o,'rgons4-hide'));});
  var input=findInput();

  $$('button,a').forEach(function(b){
    if(ours(b)||b.closest('.rgons4-hide')||!PC_RE.test(txt(b)))return;
    if(input&&b.contains(input))return;
    done.push(hideUnit(b,'rgons4-hide'));
  });
  collapseEmpty(done,'rgons4-hide');
}

/* ── 상단 초록 상태바 숨김 ── */
var STATUS_RE=/자동\s*동기화|실시간\s*동기화|v\d+\.\d+(\.\d+)?-step\d*|항체\s*R1\s*~\s*R1\d/i;
var CHAT_ZONE='[class*="message" i],[class*="msg" i],[class*="bubble" i],[id*="messages" i],[class*="chat-log" i],[id*="chat-log" i],[class*="history" i]';
function hideStatus(){
  var raw=$('#rgons4-status-raw');

  $$('div,header,section,nav,p,span,small,strong,b,marquee').forEach(function(el){
    if(ours(el)||el.closest('.rgons4-status-hide')||!visible(el))return;
    var s=txt(el);if(!s||s.length>300||!STATUS_RE.test(s))return;
    if(el.querySelector('textarea,input,select')||el.querySelectorAll('button').length>2)return;
    if(el.closest(CHAT_ZONE))return;
    var cs=getComputedStyle(el),r=el.getBoundingClientRect();
    if(!(r.top<320||cs.position==='fixed'||cs.position==='sticky'))return;
    var t=el,p=el.parentElement,top=topEl();
    while(p&&p!==document.body&&!ours(p)){
      if(p.querySelector('textarea,input')||(top&&p.contains(top)))break;
      if(txt(p).length>txt(t).length+30)break;
      t=p;p=p.parentElement;
    }
    t.classList.add('rgons4-status-hide');
    if(raw&&raw.textContent.indexOf(s.slice(0,40))<0)raw.textContent=(raw.textContent?raw.textContent+' | ':'')+s.slice(0,160);
  });
}

/* ── 서랍 ── */
function openDrawer(){
  $('#rgons4-drawer').classList.add('open');$('#rgons4-drawer').setAttribute('aria-hidden','false');
  $('#rgons4-backdrop').classList.add('open');document.body.classList.add('rgons4-lock');loadSettings();
  var ta=$('#rgons4-deploy-text'),p=$('#rgons4-deploy-path');if(p&&!p.value)p.value=LS.get('rgon_deploy_path','');
  if(ta&&!ta.value){var c=currentText();if(c)ta.value=c;}
}
function closeDrawer(){
  $('#rgons4-drawer').classList.remove('open');$('#rgons4-drawer').setAttribute('aria-hidden','true');
  $('#rgons4-backdrop').classList.remove('open');document.body.classList.remove('rgons4-lock');
}

/* ── 설정 ── */
var FIELDS={'rgons4-url-rgon':'rgon_url_rgon','rgons4-url-claude':'rgon_url_claude','rgons4-url-gpt':'rgon_url_gpt','rgons4-url-grok':'rgon_url_grok','rgons4-gh-pat':'rgon_gh_pat','rgons4-gh-repo':'rgon_gh_repo','rgons4-gh-branch':'rgon_gh_branch','rgons4-tg-token':'rgon_tg_token','rgons4-tg-chat':'rgon_tg_chat','rgons4-brief-url':'rgon_brief_url'};
function loadSettings(){Object.keys(FIELDS).forEach(function(id){var el=document.getElementById(id);if(el)el.value=LS.get(FIELDS[id],id==='rgons4-gh-branch'?'main':'');});}
function saveSettings(){Object.keys(FIELDS).forEach(function(id){var el=document.getElementById(id);if(el)LS.set(FIELDS[id],String(el.value||'').trim());});toast('💾 저장 완료 (이 기기에만 보관)');}

/* ── 지우기 ── */
function clearInput(){var el=findInput();if(el){setVal(el,'');}toast('🧹 입력창 비움');closeDrawer();}
function resetAll(){
  if(!confirm('입력창 · 장전 지시문 · 브리핑 카드 · 음성 · 흡수 버퍼 · 대화 기록을 모두 초기화할까요?'))return;
  var el=findInput();if(el)setVal(el,'');
  LS.del('rgon_loaded_directive');lastCardsText='';
  var c=$('#rgons4-cards');if(c){c.classList.remove('open');c.innerHTML='';}
  try{speechSynthesis.cancel();}catch(e){}
  try{Object.keys(localStorage).forEach(function(k){if(/absorb|흡수/i.test(k))localStorage.removeItem(k);});}catch(e){}
  var cb=findForeign(/대화\s*(전체\s*)?(초기화|지우기|삭제)|전체\s*지우기|clear\s*chat|reset\s*chat/i);
  if(cb){try{cb.click();}catch(e){}}
  else{try{Object.keys(localStorage).forEach(function(k){if(/chat_?history|rgon_chat|rgon_messages/i.test(k))localStorage.removeItem(k);});}catch(e){}}
  closeDrawer();toast('🗑️ 대화·흡수 전체 초기화 완료');
}

/* ── 이벤트 ── */
document.addEventListener('click',function(e){
  var t=e.target;if(!t||!t.closest)return;
  if(t.id==='rgons4-backdrop'){closeDrawer();return;}
  var b=t.closest('[data-act],[data-ai],[data-quad]');if(!b||!ours(b))return;
  e.preventDefault();
  var ai=b.getAttribute('data-ai');if(ai){relay(ai);return;}
  var q=b.getAttribute('data-quad');if(q){quad(q);return;}
  var a=b.getAttribute('data-act');
  switch(a){
    case 'copy':copyCurrent();break;
    case 'paste':pasteToInput();break;
    case 'drawer':openDrawer();break;
    case 'drawer-close':closeDrawer();break;
    case 'save':saveSettings();break;
    case 'brief':closeDrawer();showCards(null);break;
    case 'f-nvda':case 'f-media':case 'f-immune':closeDrawer();showCards(a);break;
    case 'tts':closeDrawer();tts();break;
    case 'cards-close':var c=$('#rgons4-cards');c.classList.remove('open');c.innerHTML='';break;
    case 'clear-input':clearInput();break;
    case 'reset-all':resetAll();break;
    case 'd-paste':readClip().then(function(s){$('#rgons4-deploy-text').value=s||'';dlog('📥 클립보드 '+(s||'').length+'자');}).catch(clipFail);break;
    case 'd-gh':deployGH();break;
    case 'd-tg':deployTG();break;
    case 'legacy':hideLegacy();document.body.classList.toggle('rgons4-show-legacy');toast(document.body.classList.contains('rgons4-show-legacy')?'🔼 원본 패널 표시':'🔽 원본 패널 숨김');break;
  }
},false);
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeDrawer();});

function scan(){fixInput();hideLegacy();hideStatus();}
function init(){
  var top=$('#rgons4-top');
  if(top&&document.body.firstElementChild!==top)document.body.insertBefore(top,document.body.firstChild);
  ['#rgons4-backdrop','#rgons4-drawer','#rgons4-toast'].forEach(function(s){var n=$(s);if(n&&n.parentNode!==document.body)document.body.appendChild(n);});
  loadSettings();scan();
  var to;
  try{new MutationObserver(function(ms){
    if(ms.every(function(m){return ours(m.target);}))return;
    clearTimeout(to);to=setTimeout(scan,350);
  }).observe(document.body,{childList:true,subtree:true});}catch(e){}
  window.addEventListener('resize',function(){clearTimeout(to);to=setTimeout(fixInput,250);});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
</script>"""

HTML_BLOCK = HTML_START + "\n" + HTML_BLOCK_BODY + "\n" + HTML_END

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
    fd, tmp = tempfile.mkstemp(suffix=".js", prefix="rgon_s4_chk_")
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


def remove_static_bottom_clear(text):
    spans = [(m.start(), m.end()) for m in SCRIPT_SPAN_RE.finditer(text)]
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
    ids_before = set(ID_RE.findall(HTML_BLOCK_RE.sub("", text)))

    if HTML_BLOCK_RE.search(text):
        first = [True]

        def repl(_m):
            if first[0]:
                first[0] = False
                return HTML_BLOCK
            return ""

        new = HTML_BLOCK_RE.sub(repl, text)
        mode = "Step4 블록 교체"
    else:
        idx = text.lower().rfind("</body>")
        new = (text[:idx] + HTML_BLOCK + "\n" + text[idx:]) if idx >= 0 else (text + "\n" + HTML_BLOCK + "\n")
        mode = "Step4 블록 신규 삽입"

    new, removed = remove_static_bottom_clear(new)

    ids_after = set(ID_RE.findall(new))
    missing = ids_before - ids_after
    if missing:
        log(f"❌ [{rel(p)}] 기존 id 손실 감지 → 중단: {sorted(missing)[:10]}")
        return False
    lack = REQUIRED_NEW_IDS - ids_after
    if lack:
        log(f"❌ [{rel(p)}] 신규 id 누락 → 중단: {sorted(lack)}")
        return False

    for attr in ("onclick",):
        before_n = len(re.findall(r"\b%s\s*=" % attr, HTML_BLOCK_RE.sub("", text), re.I))
        after_n = len(re.findall(r"\b%s\s*=" % attr, HTML_BLOCK_RE.sub("", new), re.I))
        if after_n < before_n:
            log(f"❌ [{rel(p)}] 기존 {attr} 핸들러 감소({before_n}→{after_n}) → 중단")
            return False

    m = re.search(r'<script id="rgons4-script">(.*?)</script>', new, re.S)
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
    log(f"✅ [{rel(p)}] {mode} (기존 id {len(ids_before)}개 보존, "
        f"정적 지우기바 {removed}개 제거, 백업: {b.name})")
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
    log(f"🏛️ RGON STEP4 초슬림 UI 패치 시작 — 루트: {ROOT}")
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

    log("🏁 완료 — 모바일에서 새로고침(캐시 무시) 후 상단 7버튼 · 갈색 1층 4분할 · ☰ 서랍을 확인하세요.")


if __name__ == "__main__":
    main()
