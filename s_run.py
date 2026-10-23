# -*- coding: utf-8 -*-
"""
step14_fix_5bars_layout.py
RGON 독대실 상단 5대 아코디언 바 레이아웃 보정 (Step 14)
- Python 3 표준 라이브러리 전용
- 독대실 HTML에 <!-- [RGON-5BARS-FIX-V14-START] --> ~ END 블록(CSS+JS)을 주입
  · 5개 바를 전용 도크(#rg5-dock) 한 부모 안에 1→5 순서로 정렬 (#rgyt-wrap은 초록 바 바로 아래로 이동)
  · 숨김/높이 0 찌그러짐 강제 복원, 접힌 빈 박스의 min-height/height/flex 여백 제거
  · 탭 전환 시 재정렬, 바 클릭 시 해당 바만 펼침(나머지 자동 접힘)
- 이후 git add/commit/pull --rebase/push + Windows 완료 메시지 박스
"""
import os, sys, re, shutil, subprocess
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PREFERRED_BASE = r"C:\Users\sangi\Downloads\shin-agent"
V13_START = "<!-- [RGON-YT-SCOUT-V13-START] -->"
START_MARK = "<!-- [RGON-5BARS-FIX-V14-START] -->"
END_MARK = "<!-- [RGON-5BARS-FIX-V14-END] -->"

BAR_CHECK = [
    ("1번 남색 · 4대 AI 분배 컨트롤러", ["4대 AI 분배 컨트롤러", "AI 분배 컨트롤러", "만능 소통창"]),
    ("2번 초록 · 실시간 브리핑 전문", ["실시간 브리핑 전문", "브리핑 전문"]),
    ("3번 청록 · 유튜브 스킬 흡수기", ["rgyt-wrap"]),
    ("4번 주황 · 독대실에서 바로 분배하기", ["독대실에서 바로 분배하기", "바로 분배하기"]),
    ("5번 보라 · 1:1 대화창", ["1:1 대화창", "청사 보좌 지표"]),
]

FIX_BLOCK = r"""<!-- [RGON-5BARS-FIX-V14-START] -->
<style id="rg5-style">
#rg5-dock{display:flex!important;flex-direction:column!important;gap:6px;flex:0 0 auto!important;width:100%;box-sizing:border-box;padding:6px 8px;margin:0;min-height:0!important;height:auto!important;position:relative;z-index:3;visibility:visible!important;opacity:1!important}
#rg5-dock.rg5-scroll{max-height:78vh;overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
#rg5-dock>.rg5-shell{display:block!important;flex:0 0 auto!important;min-height:0;margin:0!important;visibility:visible!important;opacity:1!important}
#rg5-dock .rg5-head{visibility:visible!important;opacity:1!important}
#rg5-dock #rgyt-wrap{margin:0!important}
.rg5-shell.rg5-opening{animation:rg5in .28s ease}
@keyframes rg5in{from{opacity:.55;transform:translateY(-3px)}to{opacity:1;transform:none}}
</style>
<script id="rg5-script">
(function(){
'use strict';
if(window.__RG5_FIX_V14__)return;window.__RG5_FIX_V14__=true;
var DEBUG=/[?&]rg5debug=1/.test(location.search);
var EXCLUSIVE=true;
var BARS=[
 {n:1,name:'4대 AI 분배 컨트롤러 & 만능 소통창',phrases:['4대 AI 분배 컨트롤러','AI 분배 컨트롤러','만능 소통창']},
 {n:2,name:'르곤-알파 실시간 브리핑 전문',phrases:['실시간 브리핑 전문','브리핑 전문']},
 {n:3,name:'유튜브 최신 트렌드 & AI 스킬 흡수기',sel:'#rgyt-bar',phrases:['유튜브 최신 트렌드']},
 {n:4,name:'독대실에서 바로 분배하기',phrases:['독대실에서 바로 분배하기','바로 분배하기']},
 {n:5,name:'르곤-알파 1:1 대화창 & 6대 청사 보좌 지표',phrases:['1:1 대화창','청사 보좌 지표']}
];
var TAB_PHRASES=['1번 알파 대화창','알파 대화창','2번 AI 지시','AI 지시·분배','AI 지시/분배','AI 지시ㆍ분배'];
var TITLE_PHRASES=['1:1 전담 독대실','전담 독대실'];
var SKIP={SCRIPT:1,STYLE:1,NOSCRIPT:1,TEMPLATE:1,TEXTAREA:1,OPTION:1,SELECT:1,TITLE:1,SVG:1,svg:1,path:1};
var INPUTS='input,textarea,select,iframe,video,canvas';
var MEDIA='img,video,canvas,iframe,svg,input,textarea,select,button,audio,object,embed,picture';
var MAJOR_RE=/(^|[\s_-])(tab|tabs|pane|page|screen|view|layout|main|app|root)([\s_-]|$)/i;
var PANEL_HIDDEN_BAD=/(tab|pane|page|screen|view)/i;
var PANEL_VISIBLE_RE=/(acc|panel|collapse|drawer|body)/i;
var COPY_PROPS=['background-color','background-image','color','border-top-color','border-right-color','border-bottom-color','border-left-color','border-top-width','border-right-width','border-bottom-width','border-left-width','border-top-style','border-right-style','border-bottom-style','border-left-style','border-top-left-radius','border-top-right-radius','border-bottom-left-radius','border-bottom-right-radius','box-shadow','padding-top','padding-right','padding-bottom','padding-left','font-size','font-weight'];
var G={},busy=false,obs=null,SYNTH=false,mtimer=null,runs=0;

function log(){if(DEBUG&&window.console)console.log.apply(console,['[RG5]'].concat([].slice.call(arguments)));}
function norm(s){return String(s||'').replace(/\s+/g,' ').trim();}
function css(el){return window.getComputedStyle(el);}
function imp(el,p,v){if(el.style.getPropertyValue(p)!==v||el.style.getPropertyPriority(p)!=='important')el.style.setProperty(p,v,'important');}
function clsOf(el){return (el.id||'')+' '+(typeof el.className==='string'?el.className:(el.getAttribute('class')||''));}
function within(el,list){for(var i=0;i<list.length;i++){var o=list[i];if(o&&el.contains(o))return true;}return false;}
function arrowLead(s){return /^[▶▼►▸▾▷⏵]/.test(s);}
function leadOf(n,ph){var i=n.indexOf(ph);if(i<0)return -1;return n.slice(0,i).replace(/[\s▶▼►▸▾▷⏵\[\]【】()]/g,'').length;}
function clickable(el){if(!el||el===document.body||el.nodeType!==1)return false;if(el.hasAttribute('onclick')||/^(BUTTON|SUMMARY|A)$/.test(el.tagName)||el.getAttribute('role')==='button')return true;try{return css(el).cursor==='pointer';}catch(e){return false;}}
function lca(a,b){var s=[];for(var x=a;x;x=x.parentElement)s.push(x);for(var y=b;y;y=y.parentElement)if(s.indexOf(y)>=0)return y;return null;}
function domOrder(a,b){return (a.compareDocumentPosition(b)&4)?-1:1;}
function hiddenAnc(el){for(var x=el.parentElement;x&&x!==document.documentElement;x=x.parentElement){var c=css(x);if(c.display==='none'||c.visibility==='hidden')return x;}return null;}
function rowFlex(el){var c=css(el);return (/flex/.test(c.display)&&/^row/.test(c.flexDirection))||/grid/.test(c.display);}
function hasDeeper(el,ph){for(var c=el.firstElementChild;c;c=c.nextElementSibling){if(norm(c.textContent).indexOf(ph)>=0)return true;}return false;}

function shortList(){var out=[],all=document.body.getElementsByTagName('*');for(var i=0;i<all.length;i++){var el=all[i];if(SKIP[el.tagName])continue;var t=el.textContent;if(!t||t.length>700)continue;var n=norm(t);if(!n||n.length>240)continue;out.push([el,n]);}return out;}

function findBy(phrases,list,opt){
 opt=opt||{};
 for(var p=0;p<phrases.length;p++){
  var ph=phrases[p],best=null,bs=1e9;
  for(var i=0;i<list.length;i++){
   var el=list[i][0],n=list[i][1],L=leadOf(n,ph);
   if(L<0||L>(opt.maxLead||18))continue;
   if(opt.exclude&&el.closest(opt.exclude))continue;
   if(hasDeeper(el,ph))continue;
   var par=el.parentElement,sc=L*4+n.length/40;
   if(arrowLead(n)||(par&&arrowLead(norm(par.textContent))&&norm(par.textContent).length<=n.length+8))sc-=60;
   if(clickable(el)||clickable(par))sc-=30;
   if(sc<bs){bs=sc;best=el;}
  }
  if(best)return best;
 }
 return null;
}

function findTabs(list){
 var res=[];
 list.forEach(function(it){
  var el=it[0],n=it[1];if(n.length>40||el.closest('#rg5-dock'))return;
  for(var k=0;k<TAB_PHRASES.length;k++){
   if(n.indexOf(TAB_PHRASES[k])>=0){
    if(!hasDeeper(el,TAB_PHRASES[k])){var b=el;while(b.parentElement&&!clickable(b)&&norm(b.parentElement.textContent).length<=40)b=b.parentElement;if(res.indexOf(b)<0)res.push(b);}
    break;
   }
  }
 });
 return res;
}
function isTabClick(t){for(var x=t,i=0;x&&x!==document.body&&i<5;x=x.parentElement,i++){var n=norm(x.textContent);if(n.length>40)return false;for(var k=0;k<TAB_PHRASES.length;k++)if(n.indexOf(TAB_PHRASES[k])>=0)return true;}return false;}

function climbHead(seed,foreign){
 var h=seed;
 while(!clickable(h)){
  var p=h.parentElement;
  if(!p||p===document.body||p.id==='rg5-dock'||p.classList.contains('rg5-shell'))break;
  if(within(p,foreign))break;
  if(norm(p.textContent).length>240||p.querySelector(INPUTS))break;
  h=p;
 }
 return h;
}
function climbUnit(head,foreign){
 var u=head,dt=head.closest('details');
 if(dt&&dt!==document.body&&!within(dt,foreign))u=dt;
 for(var g=0;g<12;g++){
  var p=u.parentElement;
  if(!p||p===document.body||p===document.documentElement||p.id==='rg5-dock'||p.classList.contains('rg5-shell'))break;
  if(/^(MAIN|HEADER|FOOTER|NAV|FORM)$/.test(p.tagName))break;
  if(within(p,foreign))break;
  if(p.children.length>6||MAJOR_RE.test(clsOf(p)))break;
  if(p.offsetHeight>window.innerHeight*0.6&&u.offsetHeight<p.offsetHeight*0.5)break;
  u=p;
 }
 return u;
}
function chainOf(head,unit){var a=[];for(var x=head;x;x=x.parentElement){a.push(x);if(x===unit)break;}return a;}
function refIds(head,unit){
 var ids=[];
 chainOf(head,unit).forEach(function(el){
  ['aria-controls','data-target','data-bs-target','data-panel','data-toggle-target','href'].forEach(function(a){var v=el.getAttribute(a);if(v){v=v.replace(/^#/,'');if(/^[A-Za-z][\w-]*$/.test(v))ids.push(v);}});
  var oc=el.getAttribute('onclick');if(oc){var m,re=/['"]#?([A-Za-z][\w-]*)['"]/g;while((m=re.exec(oc)))ids.push(m[1]);}
 });
 return ids;
}
function findPanels(head,unit,foreign){
 var out=[];
 refIds(head,unit).forEach(function(id){var el=document.getElementById(id);if(!el||el===unit||unit.contains(el)||el.contains(unit)||within(el,foreign)||out.indexOf(el)>=0)return;out.push(el);});
 if(out.length)return out;
 if(norm(unit.textContent).length>240||unit.querySelector(INPUTS))return out;
 var ns=unit.nextElementSibling;
 while(ns&&out.length<2){
  if(SKIP[ns.tagName]||ns.id==='rg5-dock'||ns.classList.contains('rg5-shell')||within(ns,foreign))break;
  var c=css(ns),cl=clsOf(ns),hidden=(c.display==='none'||c.maxHeight==='0px');
  if(hidden&&!PANEL_HIDDEN_BAD.test(cl)){out.push(ns);ns=ns.nextElementSibling;continue;}
  if(!hidden&&PANEL_VISIBLE_RE.test(cl)&&!PANEL_HIDDEN_BAD.test(cl)){out.push(ns);ns=ns.nextElementSibling;continue;}
  break;
 }
 return out;
}

function resolve(need,list,tabs,title){
 var fixedForeign=tabs.concat(title?[title]:[]),seeds={},heads={};
 BARS.forEach(function(b){
  var g=G[b.n];
  if(g&&document.body.contains(g.head)){seeds[b.n]=g.head;return;}
  var m=document.querySelector('[data-rg5-head="'+b.n+'"]');
  if(m){seeds[b.n]=m;return;}
  if(b.sel){var s=document.querySelector(b.sel);if(s){seeds[b.n]=s;return;}}
  seeds[b.n]=findBy(b.phrases,list,{exclude:'#rgyt-body'});
 });
 BARS.forEach(function(b){
  var s=seeds[b.n];if(!s)return;
  if(b.sel||s.hasAttribute('data-rg5-head')){heads[b.n]=s;return;}
  var others=[];BARS.forEach(function(o){if(o.n!==b.n&&seeds[o.n])others.push(seeds[o.n]);});
  heads[b.n]=climbHead(s,others.concat(fixedForeign));
 });
 need.forEach(function(b){
  var h=heads[b.n];if(!h)return;
  var others=[];BARS.forEach(function(o){if(o.n!==b.n&&heads[o.n])others.push(heads[o.n]);});
  var foreign=others.concat(fixedForeign);
  var unit=(b.n===3&&document.getElementById('rgyt-wrap'))||climbUnit(h,foreign);
  var panels=(b.n===3)?[]:findPanels(h,unit,foreign);
  h.setAttribute('data-rg5-head',b.n);unit.setAttribute('data-rg5-unit',b.n);
  G[b.n]={n:b.n,name:b.name,head:h,unit:unit,panels:panels,open:false,shell:null,styled:false};
  log('resolved',b.n,h,unit,panels);
 });
}

function getDock(){var d=document.getElementById('rg5-dock');if(!d){d=document.createElement('div');d.id='rg5-dock';d.setAttribute('data-rgon','5bars-v14');}return d;}
function badAnchor(a,units){if(!a||a===document.body||a===document.documentElement)return true;if(norm(a.textContent).length>300)return true;for(var i=0;i<units.length;i++){if(units[i].contains(a)||a.contains(units[i]))return true;}return false;}
function placeDock(d,tabs,title,groups){
 if(d.parentElement&&!hiddenAnc(d))return;
 var units=groups.map(function(g){return g.unit;}),anchor=null;
 if(!d.parentElement){
  if(tabs.length>=2){var best=null,bl=1e9;for(var i=0;i<tabs.length;i++)for(var j=i+1;j<tabs.length;j++){var c=lca(tabs[i],tabs[j]);if(!c)continue;var l=norm(c.textContent).length;if(l<bl&&!badAnchor(c,units)){bl=l;best=c;}}anchor=best;}
  else if(tabs.length===1){anchor=tabs[0].parentElement;if(badAnchor(anchor,units))anchor=null;}
  if(!anchor&&title&&!badAnchor(title,units))anchor=title;
  if(anchor){
   while(anchor.parentElement&&anchor.parentElement!==document.body&&rowFlex(anchor.parentElement))anchor=anchor.parentElement;
   anchor.parentNode.insertBefore(d,anchor.nextSibling);
  }else{
   var vis=units.filter(function(u){return !hiddenAnc(u);}).sort(domOrder);
   var first=vis[0]||units.slice().sort(domOrder)[0];
   if(first&&first.parentNode)first.parentNode.insertBefore(d,first);else document.body.insertBefore(d,document.body.firstChild);
  }
 }
 for(var k=0;k<12;k++){var H=hiddenAnc(d);if(!H||H===document.body)break;H.parentNode.insertBefore(d,H);}
 var p=d.parentElement;
 if(p){var pc=css(p);if(/flex/.test(pc.display)&&/^column/.test(pc.flexDirection)){if(/space|end/.test(pc.justifyContent))imp(p,'justify-content','flex-start');d.classList.add('rg5-scroll');}}
}

function snap(el){var c=css(el),o={};COPY_PROPS.forEach(function(p){o[p]=c.getPropertyValue(p);});return o;}
function restoreStyle(el,o){var c=css(el);COPY_PROPS.forEach(function(p){if(c.getPropertyValue(p)!==o[p])el.style.setProperty(p,o[p]);});}
function moveIn(g,d,idx){
 var sh=g.shell||document.querySelector('.rg5-shell[data-rg5-n="'+g.n+'"]');
 if(!sh){sh=document.createElement('div');sh.className='rg5-shell';sh.setAttribute('data-rg5-n',g.n);}
 g.shell=sh;
 var members=[g.unit].concat(g.panels);
 var inPlace=members.every(function(m,i){return m.parentElement===sh&&sh.children[i]===m;});
 var snaps=null;
 if(!inPlace){
  if(!g.styled)snaps=[[g.head,snap(g.head)],[g.unit,snap(g.unit)]];
  members.forEach(function(m){sh.appendChild(m);});
 }
 if(d.children[idx]!==sh)d.insertBefore(sh,d.children[idx]||null);
 if(snaps){snaps.forEach(function(s){restoreStyle(s[0],s[1]);});g.styled=true;}
}
function ensureVisible(g){
 chainOf(g.head,g.unit).forEach(function(el){
  if(el.hasAttribute('hidden'))el.removeAttribute('hidden');
  var c=css(el);
  if(c.display==='none')imp(el,'display','block');
  if(c.visibility!=='visible')imp(el,'visibility','visible');
  if(parseFloat(c.opacity)<1)imp(el,'opacity','1');
  if(el.offsetHeight===0){if(c.maxHeight==='0px')imp(el,'max-height','none');if(c.height==='0px')imp(el,'height','auto');}
 });
 imp(g.unit,'flex-shrink','0');
 g.head.classList.add('rg5-head');
}

function emptyBox(el){if(norm(el.textContent))return false;if(el.matches(MEDIA)||el.querySelector(MEDIA))return false;return true;}
function restoreGaps(){[].forEach.call(document.querySelectorAll('[data-rg5-gap]'),function(el){if(!emptyBox(el)){['min-height','height','flex'].forEach(function(p){el.style.removeProperty(p);});el.removeAttribute('data-rg5-gap');}});}
function killGaps(d){
 var els=document.body.querySelectorAll('div,section,main,article,aside');
 for(var i=0;i<els.length;i++){
  var el=els[i];
  if(el===d||el.hasAttribute('data-rg5-gap')||el.closest('#rg5-dock'))continue;
  if(el.offsetHeight<48||!emptyBox(el))continue;
  var c=css(el);
  if(c.display==='none'||c.position==='fixed'||c.position==='absolute'||c.position==='sticky')continue;
  if(c.backgroundImage&&c.backgroundImage!=='none')continue;
  el.setAttribute('data-rg5-gap','1');
  imp(el,'min-height','0px');imp(el,'height','auto');imp(el,'flex','0 0 auto');
  log('gap removed',el);
 }
 var bc=css(document.body);
 if(/flex/.test(bc.display)&&/^column/.test(bc.flexDirection)&&/space|end/.test(bc.justifyContent))imp(document.body,'justify-content','flex-start');
}

function detectOpen(g){
 if(g.unit.tagName==='DETAILS')return g.unit.open;
 if(g.n===3){var w=document.getElementById('rgyt-wrap');return w?w.classList.contains('open'):null;}
 var ae=g.head.getAttribute('aria-expanded');if(ae==='true'||ae==='false')return ae==='true';
 if(g.panels.length)return g.panels.some(function(p){var c=css(p);return c.display!=='none'&&c.visibility!=='hidden'&&c.maxHeight!=='0px'&&p.offsetHeight>4;});
 if(g.head!==g.unit){var hb=g.head;while(hb.parentElement&&hb.parentElement!==g.unit)hb=hb.parentElement;return g.unit.offsetHeight>hb.offsetHeight+30;}
 return null;
}
function clickTarget(g){var h=g.head;if(h.matches('[onclick],summary,button,[role=button]'))return h;return h.querySelector('[onclick],summary')||h;}
function afterToggle(g){
 var st=detectOpen(g);g.open=(st===null)?!g.open:st;
 if(!g.open)return;
 if(EXCLUSIVE){
  BARS.forEach(function(b){
   var o=G[b.n];if(!o||o===g)return;
   var s=detectOpen(o),isO=(s===null)?o.open:s;
   if(isO){SYNTH=true;try{clickTarget(o).click();}catch(e){}finally{SYNTH=false;}var s2=detectOpen(o);o.open=(s2===null)?false:s2;}
  });
 }
 if(g.shell){g.shell.classList.remove('rg5-opening');void g.shell.offsetWidth;g.shell.classList.add('rg5-opening');setTimeout(function(){g.shell&&g.shell.classList.remove('rg5-opening');},400);}
 setTimeout(function(){try{g.head.scrollIntoView({behavior:'smooth',block:'nearest'});}catch(e){}},80);
}

function report(groups){
 var found=groups.map(function(g){return g.n;});
 window.RG5_REPORT={found:found,missing:BARS.filter(function(b){return found.indexOf(b.n)<0;}).map(function(b){return b.n+'번 '+b.name;}),runs:runs};
 if(runs===1||DEBUG)console.log('[RG5] 상단 5대 바 정렬',window.RG5_REPORT);
 if(DEBUG)groups.forEach(function(g){g.shell&&(g.shell.style.outline='1px dashed #f0f');});
}
function startObs(){
 if(!window.MutationObserver)return;
 if(!obs)obs=new MutationObserver(function(){clearTimeout(mtimer);mtimer=setTimeout(function(){fix('light');},250);});
 obs.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['style','class','hidden']});
}
function fix(mode){
 if(busy||!document.body)return;
 busy=true;if(obs)obs.disconnect();runs++;
 try{
  var need=BARS.filter(function(b){var g=G[b.n];return !(g&&document.body.contains(g.head)&&document.body.contains(g.unit));});
  var dock=getDock(),tabs=[],title=null;
  if(mode!=='light'||!dock.parentElement){
   var list=shortList();tabs=findTabs(list);title=findBy(TITLE_PHRASES,list,{maxLead:12});
   if(need.length)resolve(need,list,tabs,title);
  }
  var groups=BARS.map(function(b){return G[b.n];}).filter(Boolean);
  if(groups.length){
   placeDock(dock,tabs,title,groups);
   groups.forEach(function(g,idx){moveIn(g,dock,idx);ensureVisible(g);});
  }
  restoreGaps();
  if(mode!=='light')killGaps(dock);
  report(groups);
 }catch(e){if(window.console)console.warn('[RG5] fix error',e);}
 finally{busy=false;startObs();}
}

document.addEventListener('click',function(e){
 if(SYNTH)return;
 var t=e.target;if(!t||t.nodeType!==1)return;
 for(var i=0;i<BARS.length;i++){var g=G[BARS[i].n];if(g&&g.head.contains(t)){setTimeout(function(){afterToggle(g);},60);return;}}
 if(isTabClick(t))[60,300,800].forEach(function(ms){setTimeout(function(){fix('full');},ms);});
},false);
window.addEventListener('load',function(){fix('full');setTimeout(function(){fix('full');},300);});
window.addEventListener('orientationchange',function(){setTimeout(function(){fix('full');},300);});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){fix('full');});
fix('full');
[100,500,1200,2500].forEach(function(ms){setTimeout(function(){fix('full');},ms);});
window.RG5_FIX=function(){fix('full');return window.RG5_REPORT;};
})();
</script>
<!-- [RGON-5BARS-FIX-V14-END] -->"""


def log(*a):
    print("[STEP14]", *a, flush=True)


def looks_like_project(d):
    try:
        return os.path.isdir(d) and (os.path.isfile(os.path.join(d, "rgon_alpha_chat.html"))
                                     or any(f.lower().startswith("rgon_") and f.lower().endswith(".html") for f in os.listdir(d)))
    except Exception:
        return False


def find_base_dir():
    if os.path.isdir(PREFERRED_BASE):
        return PREFERRED_BASE
    home = os.path.expanduser("~")
    cands = [os.path.dirname(os.path.abspath(__file__)), os.getcwd()] + \
            [os.path.join(home, s, "shin-agent") for s in ("Downloads", "Desktop", "Documents", "")]
    for c in cands:
        if looks_like_project(c):
            return c
    skip = {"node_modules", ".git", "AppData", "__pycache__", "venv", ".venv"}
    for root in [os.path.join(home, s) for s in ("Downloads", "Desktop", "Documents")] + [home]:
        if not os.path.isdir(root):
            continue
        base_depth = root.rstrip("\\/").count(os.sep)
        for cur, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
            if cur.count(os.sep) - base_depth >= 3:
                dirs[:] = []
            if os.path.basename(cur).lower().startswith("shin-agent") or "rgon_alpha_chat.html" in files:
                return cur
    return os.path.dirname(os.path.abspath(__file__))


def find_html_targets(base):
    found = []
    for d in [base, os.path.join(base, "dashboard"), os.path.join(base, "docs")]:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if not (os.path.isfile(fp) and f.lower().endswith(".html")):
                continue
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                    src = fh.read()
            except Exception:
                continue
            name_hit = f.lower().startswith("rgon_") and "chat" in f.lower()
            if name_hit or V13_START in src or START_MARK in src or ("RGON" in src and "독대" in src):
                found.append(fp)
    return found


def inspect(src):
    rows = []
    for label, phrases in BAR_CHECK:
        rows.append("%s %s" % ("✅" if any(p in src for p in phrases) else "❔", label))
    return rows


def patch_html(fp):
    with open(fp, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()
    bak = fp + ".bak_step14"
    if not os.path.exists(bak):
        shutil.copy2(fp, bak)
    pat = re.compile(re.escape(START_MARK) + r".*?" + re.escape(END_MARK), re.S)
    src = pat.sub("", src).rstrip() + "\n" if START_MARK in src else src
    idx = src.lower().rfind("</body>")
    new = (src[:idx] + FIX_BLOCK + "\n" + src[idx:]) if idx >= 0 else (src + "\n" + FIX_BLOCK + "\n")
    with open(fp, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    rows = inspect(new)
    log("패치 완료:", fp)
    for r in rows:
        log("   ", r)
    return rows


def git(base, *args):
    try:
        p = subprocess.run(["git"] + list(args), cwd=base, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        log("git", " ".join(args), "->", p.returncode, (p.stdout + p.stderr).strip()[-300:])
        return p.returncode == 0
    except Exception as e:
        log("git 실행 실패:", e)
        return False


def git_sync(base):
    if not os.path.isdir(os.path.join(base, ".git")):
        log("Git 저장소가 아니어서 동기화를 건너뜁니다.")
        return False
    git(base, "add", "-A")
    git(base, "commit", "-m", "Step14: 독대실 상단 5대 아코디언 바 레이아웃 보정 " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    if not git(base, "pull", "--rebase", "origin", "main"):
        git(base, "rebase", "--abort")
        log("pull --rebase 실패 → 리베이스 취소 후 push 시도")
    return git(base, "push", "origin", "main")


def msgbox(title, text):
    log(text)
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x40000)
        except Exception:
            pass


def main():
    base = find_base_dir()
    log("작업 폴더:", base)
    targets = find_html_targets(base)
    if not targets:
        msgbox("RGON Step 14", "독대실 HTML을 찾지 못했습니다.\n작업 폴더: %s" % base)
        return
    summary = []
    for fp in targets:
        try:
            rows = patch_html(fp)
            summary.append("• %s  (%s)" % (os.path.relpath(fp, base), " ".join(r.split(" ")[0] for r in rows)))
        except Exception as e:
            log("패치 실패:", fp, e)
            summary.append("• %s  (실패: %s)" % (os.path.relpath(fp, base), e))
    pushed = git_sync(base)
    msgbox("RGON Step 14 완료",
           "🧭 상단 5대 아코디언 바 레이아웃 보정 완료\n\n작업 폴더: %s\n패치한 HTML %d개 (바 1~5 원문 탐지 ✅/❔):\n%s\n\n"
           "Git 푸시: %s\n\n확인: 페이지 새로고침 → 남색·초록·청록·주황·보라 순서\n"
           "진단: 주소 뒤에 ?rg5debug=1 을 붙이거나 콘솔에서 RG5_FIX() 실행\n"
           "되돌리기: *.html.bak_step14 파일로 복원"
           % (base, len(targets), "\n".join(summary), "성공" if pushed else "건너뜀/실패(로그 확인)"))


if __name__ == "__main__":
    main()
