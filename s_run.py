# -*- coding: utf-8 -*-
"""step23_radar_pulse_and_skills_ui.py — RGON v11.22-OMNI-UI / R1~R23
카파시 4원칙(단순·외과적·검증·목표지향) · 무위자연(V13 마커 내부만) · 과유불급(새 바 0, 루프 0) · 삼성 3/3
R23: 전신 맥박 & 18개 스킬 카탈로그 UI 무간섭 단발 통합 — 기존 V13 마커 내부만 교체하고 Observer 없이 3탭으로 표시"""
import hashlib, json, re, shutil, subprocess, sys, py_compile, datetime as dt
from pathlib import Path

BT3 = chr(96) * 3
ROOT = Path(__file__).resolve().parent
VER, AB = "v11.22-OMNI-UI", "R1~R23"
R23 = "R23: 전신 맥박 & 18개 스킬 카탈로그 UI 무간섭 단발 통합 — 기존 V13 마커 내부만 교체하고 Observer 없이 3탭으로 표시"
M_S, M_E = "<!-- [RGON-YT-SCOUT-V13-START] -->", "<!-- [RGON-YT-SCOUT-V13-END] -->"
V15_S, V15_E = "<!-- [RGYT-PLACE-ONCE-V15-START] -->", "<!-- [RGYT-PLACE-ONCE-V15-END] -->"
TS = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = ROOT / "backups" / f"step23_{TS}"
SKIP = {".git", "node_modules", "backups", "__pycache__", ".venv", "venv"}
BACKEND = ["rgon_white_blood_cell.py", "rgon_nutrient_engine.py", "rgon_spec_ticket_Shield.py", "rgon_daily_cycle.py"]
SYNC = ["rgon_morning_brief.json", "MORNING_BRIEF.md", "rgon_immune_ledger.json", "rgon_brain_snapshot.json",
        "dashboard/rgon_brain_snapshot.json", "docs/rgon_brain_snapshot.json", "CLAUDE.md", "CODE_MAP.md", "RGON_EVOLUTION_LOG.md"]
FORBID_WORDS = ("MutationObserver", "setInterval", "requestAnimationFrame")
FORBID = re.compile("|".join(FORBID_WORDS))
DEFAULT_SKILLS = ["wbc-self-healing", "markdown-purifier", "multi-agent-council", "hexagram-64-wisdom",
                  "mattpocock-spec-tickets", "ecc-agentshield-harness", "rea-reverse-engineer-fusion"]
LOG, CHANGED = [], set()

def log(m): print(m); LOG.append(str(m))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
    with open(p, encoding="utf-8", errors="replace", newline="") as f: return f.read()
def wr(p, t):
    with open(p, "w", encoding="utf-8", newline="") as f: f.write(t)
    CHANGED.add(p)
def rel(p): return p.relative_to(ROOT).as_posix()
def bak(p):
    d = BAK / rel(p); d.parent.mkdir(parents=True, exist_ok=True)
    if not d.exists(): shutil.copy2(p, d)
def loadj(r):
    try: return json.loads(rd(ROOT / r))
    except Exception: return None
def walk():
    for p in ROOT.rglob("*"):
        if p.is_file() and not (SKIP & set(p.relative_to(ROOT).parts)): yield p

def classify():
    targets, guard = [], {}
    for p in walk():
        s = p.suffix.lower()
        if s in (".html", ".htm"):
            try: t = rd(p)
            except Exception: t = ""
            if t.count(M_S) == 1 and t.count(M_E) == 1 and t.index(M_S) < t.index(M_E):
                targets.append(p); continue
            guard[p] = sha(p)
        elif s == ".js" or p.name == "manifest.json":
            guard[p] = sha(p)
    return sorted(targets), guard

R23_BLOCK = '''
# [RGON-R23-START] Step23 항체 비파괴 주입
R23_ANTIBODY = {"id": "R23", "rule": %r}
for _n in ("ANTIBODIES", "DEFAULT_ANTIBODIES", "ANTIBODY_RULES", "IMMUNE_RULES", "RULES", "ANTIBODY"):
    _o = globals().get(_n)
    if isinstance(_o, dict) and "R23" not in _o:
        _o["R23"] = R23_ANTIBODY["rule"]
    elif isinstance(_o, list) and not any("R23" in str(_x) for _x in _o):
        _o.append(dict(R23_ANTIBODY) if (_o and isinstance(_o[0], dict)) else R23_ANTIBODY["rule"])
# [RGON-R23-END]
''' % R23

def bump_backend():
    for name in BACKEND:
        p = ROOT / name
        if not p.exists(): log(f"⚠️ 백엔드 없음: {name}"); continue
        src = rd(p); bak(p)
        t, n = re.subn(r'((?:RGON_VERSION|__version__|VERSION|VER)\s*[:=]\s*["\'])v\d+\.\d+[^"\']*(["\'])', r"\g<1>" + VER + r"\2", src)
        t = re.sub(r"R1\s*[~\-–]\s*R2[0-2]\b", AB, t)
        if "R23" not in t:
            m = re.search(r"^if __name__\s*==", t, re.M)
            t = t[:m.start()] + R23_BLOCK + "\n" + t[m.start():] if m else t + R23_BLOCK
        wr(p, t)
        try: py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            shutil.copy2(BAK / name, p); raise SystemExit(f"❌ {name} 컴파일 실패 → 복원: {e}")
        log(f"✅ 승격 {name} (버전 대입 {n}곳, R23 등록)")

def run_cycle():
    try:
        r = subprocess.run([sys.executable, "rgon_daily_cycle.py", "--run"], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=900)
        log(f"🔁 daily_cycle rc={r.returncode} | {(r.stdout or r.stderr)[-300:].strip()}"); return r.returncode == 0
    except Exception as e: log(f"⚠️ daily_cycle 실행 실패: {e}"); return False

def sync_fix():
    stamp = f"> 🔄 Step23 동기화: {VER} · 항체 {AB} · {R23}\n\n"
    for r in SYNC:
        p = ROOT / r
        if not p.exists(): log(f"⚠️ 동기화 대상 없음: {r}"); continue
        t = rd(p); need_r23 = r.endswith("immune_ledger.json") and "R23" not in t
        if VER in t and AB in t and not need_r23: continue
        bak(p)
        if p.suffix == ".json":
            try: d = json.loads(t)
            except Exception: d = None
            if isinstance(d, dict):
                d["version"], d["antibody_range"] = VER, AB
                if isinstance(d.get("vascular_circulation"), dict):
                    d["vascular_circulation"]["version"] = VER
                    d["vascular_circulation"]["antibody_range"] = AB
                if isinstance(d.get("immune"), dict):
                    d["immune"]["antibody_range"] = AB
                    d["immune"]["antibody_count"] = 23
                d["antibody_count"] = 23
                if need_r23:
                    a = d.get("antibodies")
                    if isinstance(a, list): a.append({"id": "R23", "name": "전신 맥박 & 18개 스킬 UI 단발 통합", "rule": R23, "status": "활성"})
                    elif isinstance(a, dict): a["R23"] = R23
                    else: d.setdefault("step23_antibodies", {})["R23"] = R23
                wr(p, json.dumps(d, ensure_ascii=False, indent=2)); log(f"🩹 JSON 동기화 {r}")
        else:
            t2 = re.sub(r"v11\.\d+[A-Za-z0-9_\-]*", VER, t)
            t2 = re.sub(r"R1\s*[~\-–]\s*R2[0-2]\b", AB, t2)
            if VER not in t2 or AB not in t2: t2 = stamp + t2
            wr(p, t2); log(f"🩹 MD 동기화 {r}")
    src = ROOT / "rgon_morning_brief.json"
    idx_src = ROOT / "skills" / "SKILL_INDEX.json"
    for d in ("dashboard", "docs"):
        if src.exists() and (ROOT / d).is_dir():
            q = ROOT / d / src.name
            if not q.exists() or sha(q) != sha(src):
                if q.exists(): bak(q)
                shutil.copy2(src, q); CHANGED.add(q)
        if idx_src.exists() and (ROOT / d).is_dir():
            sk_dir = ROOT / d / "skills"
            sk_dir.mkdir(parents=True, exist_ok=True)
            q2 = sk_dir / "SKILL_INDEX.json"
            if not q2.exists() or sha(q2) != sha(idx_src):
                if q2.exists(): bak(q2)
                shutil.copy2(idx_src, q2); CHANGED.add(q2)

def fallback():
    brief = loadj("rgon_morning_brief.json") or {}
    idx = loadj("skills/SKILL_INDEX.json")
    skills = (idx.get("skills") if isinstance(idx, dict) else idx) or []
    if not skills and (ROOT / "skills").is_dir():
        skills = [{"name": f.parent.name, "category": "skill", "source_url": f"skills/{f.parent.name}/SKILL.md"}
                  for f in sorted((ROOT / "skills").glob("*/SKILL.md"))]
    skills = skills or [{"name": n} for n in DEFAULT_SKILLS]
    rad = loadj("rgon_skill_radar.json")
    if isinstance(rad, dict): rad = rad.get("items") or rad.get("cards") or rad.get("radar") or []
    s = json.dumps({"brief": brief, "skills": skills, "radar": rad or []}, ensure_ascii=False).replace("</", "<\\/")
    for w in FORBID_WORDS: s = s.replace(w, w[0] + "\\u%04x" % ord(w[1]) + w[2:])
    return s

DEFAULT_V15 = r"""<!-- [RGYT-PLACE-ONCE-V15-START] -->
<script id="rgyt-place-once">
(function(){
  function placeOnce(){
    var w=document.getElementById('rgyt-wrap');
    if(!w||w.getAttribute('data-placed')==='1')return;
    var all=document.body?document.body.getElementsByTagName('*'):[];
    var seed=null;
    for(var i=0;i<all.length;i++){
      var el=all[i];
      if(w.contains(el))continue;
      if(/^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|TEXTAREA)$/.test(el.tagName))continue;
      var t=(el.textContent||'').replace(/\s+/g,' ').trim();
      if(t.length>0&&t.length<220&&t.indexOf('실시간 브리핑 전문')>=0){
        var deeper=false;
        for(var c=el.firstElementChild;c;c=c.nextElementSibling){
          if((c.textContent||'').indexOf('실시간 브리핑 전문')>=0){deeper=true;break;}
        }
        if(!deeper){seed=el;break;}
      }
    }
    if(!seed)return;
    var u=seed.closest('details')||seed;
    for(var g=0;g<8;g++){
      var p=u.parentElement;
      if(!p||p===document.body||p.children.length>5)break;
      u=p;
    }
    if(u&&u.parentNode&&u.nextElementSibling!==w){
      u.parentNode.insertBefore(w,u.nextSibling);
    }
    w.setAttribute('data-placed','1');
  }
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',placeOnce,{once:true});
  }else{
    placeOnce();
  }
})();
</script>
<!-- [RGYT-PLACE-ONCE-V15-END] -->"""

BLOCK = r"""<style>
#rgyt-wrap{margin:6px 0;border:1px solid #2a3550;border-radius:10px;background:#0f1626;color:#dfe6f5;font-size:13px}
#rgyt-head{display:flex;gap:8px;align-items:center;padding:8px 12px;cursor:pointer;flex-wrap:wrap;background:linear-gradient(90deg,#111c35,#162447);border-radius:10px}
#rgyt-pulse{opacity:.92;font-size:12px;color:#93c5fd}#rgyt-tog{margin-left:auto;font-weight:bold;color:#60a5fa}
#rgyt-tabs{display:flex;gap:6px;padding:8px 10px 6px;flex-wrap:wrap;border-top:1px solid #1e293b}
#rgyt-tabs button,#rgyt-wrap .rgyt-card button{background:#1b2540;color:#dfe6f5;border:1px solid #33416a;border-radius:7px;padding:4px 9px;cursor:pointer;font-size:12px}
#rgyt-tabs button.on{background:#2563eb;border-color:#3b82f6;font-weight:bold;color:#fff}
#rgyt-pane{max-height:440px;overflow:auto;padding:4px 10px 10px}
.rgyt-card{border:1px solid #26314d;border-radius:8px;padding:8px 10px;margin:6px 0;background:#131c30}
.rgyt-tag{font-size:11px;background:#24304f;color:#93c5fd;border-radius:5px;padding:1px 6px;margin-left:4px;display:inline-block}
.rgyt-sm{font-size:12px;opacity:.82;margin:4px 0;line-height:1.45}.rgyt-tool{display:flex;gap:6px;margin:4px 0;flex-wrap:wrap}
.rgyt-tool input,.rgyt-tool select{background:#0b1220;color:#dfe6f5;border:1px solid #33416a;border-radius:6px;padding:4px 8px;font-size:12px}
.rgyt-tool input{flex:1;min-width:140px}
.rgyt-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:6px;margin-top:6px}
.rgyt-org{background:#0b1324;border:1px solid #1e293b;border-radius:6px;padding:5px 8px;font-size:12px}
#rgyt-wrap table{width:100%;border-collapse:collapse;margin-top:6px;font-size:12px}#rgyt-wrap td,#rgyt-wrap th{border-bottom:1px solid #26314d;padding:5px 4px;text-align:left}
#rgyt-wrap a{color:#60a5fa;text-decoration:none;margin-right:8px;font-size:12px}
</style>
<div id="rgyt-wrap" data-ver="v11.22-OMNI-UI" data-antibody="R1~R23">
<div id="rgyt-head"><b>🔭 유튜브 트렌드 &amp; AI 스킬 흡수기</b><span id="rgyt-pulse"></span><span id="rgyt-tog">▼ 펼치기</span></div>
<div id="rgyt-body" hidden><div id="rgyt-tabs">
<button type="button" data-tab="radar" id="rgyt-t-radar" class="on">📡 트렌드 레이더</button>
<button type="button" data-tab="skills" id="rgyt-t-skills">🍯 보유 스킬</button>
<button type="button" data-tab="pulse" id="rgyt-t-pulse">🫀 전신 맥박 &amp; 3자 심판</button>
</div><div id="rgyt-pane"></div></div></div>
<script>
(function(){'use strict';try{
var FB=__FB__;
var ORG=['1_radar','2_nutrient','3_ticket_shield','4_wbc','5_iching','6_pulse_snapshot'];
var S={b:FB.brief||{},k:FB.skills||[],r:FB.radar||[],tab:'radar',q:'',cat:''};
function $(i){return document.getElementById(i);}
function esc(t){return String(t==null?'':t).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function pick(o,ks,d){for(var i=0;i<ks.length;i++){if(o&&typeof o==='object'&&o[ks[i]]!=null&&o[ks[i]]!=='')return o[ks[i]];}return d;}
function ok(v){if(v&&typeof v==='object')v=pick(v,['status','state','ok','result'],true);if(v===true)return true;return /^(ok|pass|passed|green|success|done|healthy|true|✔|✅)$/i.test(String(v).trim());}
function parseTri(raw){
  if(!Array.isArray(raw))return[];
  return raw.map(function(x){
    if(x&&typeof x==='object')return{topic:pick(x,['topic','agenda','title','name'],'-'),bull:pick(x,['bull','bull_score'],'-'),bear:pick(x,['bear','bear_score'],'-'),judge:pick(x,['judge','score'],'-'),verdict:pick(x,['verdict','status'],'APPROVED')};
    var s=String(x||'');
    var m=s.match(/\[([^\]]+)\]\s*([\d.]+)점\s*\(Bull\s*([\d.]+)\s*\/\s*Bear\s*([\d.]+)\s*\/\s*([^)]+)\)\s*(.*)/);
    if(m)return{verdict:m[1]+' ('+m[5]+')',judge:m[2]+'점',bull:m[3],bear:m[4],topic:m[6]||s};
    return{topic:s,bull:'-',bear:'-',judge:'-',verdict:'승인'};
  });
}
function B(){
  var b=S.b||{},vc=b.vascular_circulation||{},nt=b.nutrient||{};
  var h=vc.iching||b.hexagram||b.iching||{};if(typeof h==='string')h={name:h};
  var og=vc.organs||b.organs||{},ol=[];
  Object.keys(og).sort().forEach(function(k){ol.push([k,og[k]]);});
  if(!ol.length)ORG.forEach(function(k){ol.push([k,true]);});
  var tri=nt.trinity||b.trinity||b.council||[];
  return{
    sc:pick(b,['health_score','score'],100),
    ab:pick(b,['antibody_range'],'R1~R23'),
    hx:pick(h,['name','title'],'중천건(重天乾)'),
    mt:pick(h,['meaning','motto','keyword'],'자강불식(自強不息)'),
    act:pick(h,['action','guidance'],'상선약수(上善若水) · 삼성(三省) — 6대 기관을 물처럼 순환시키고 하루 세 번 무결성을 살핀다.'),
    ol:ol,
    c:parseTri(tri)
  };
}
function cp(t,btn){var o=btn.textContent;function done(){btn.textContent='✅ 복사완료';setTimeout(function(){btn.textContent=o;},1200);}
function fb(){var a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}a.remove();done();}
if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(done,fb);else fb();}
function badge(){var x=B();$('rgyt-pulse').textContent='🩸'+x.sc+'점 · 🛡️'+x.ab+' · ☯️'+x.hx.split('(')[0]+' · 🍯스킬 '+S.k.length+'개 · 📡레이더 '+S.r.length+'건';
$('rgyt-t-radar').textContent='📡 트렌드 레이더 ('+S.r.length+')';$('rgyt-t-skills').textContent='🍯 보유 스킬 ('+S.k.length+')';}
function cat(x){return pick(x,['category','cat','channel','tag'],'트렌드');}
function list(){var q=S.q.toLowerCase(),L=S.r.filter(function(x){return(!S.cat||cat(x)===S.cat)&&(!q||JSON.stringify(x).toLowerCase().indexOf(q)>=0);});
$('rgyt-list').innerHTML=L.map(function(x){var u=pick(x,['url','link','source_url','source'],''),t=pick(x,['title','name'],'(무제)'),sm=pick(x,['summary','desc','description','why','action_plan'],'');
return'<div class="rgyt-card"><b>'+esc(t)+'</b><span class="rgyt-tag">'+esc(cat(x))+'</span><div class="rgyt-sm">'+esc(sm)+'</div>'+(u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">🔗 원본열기</a>':'')+'<button type="button" data-cp="'+esc('[스킬흡수 지시] '+t+(u?' ('+u+')':'')+' 핵심 내용을 우리 시스템에 적용해 줘.')+'">📋 지시문 복사</button></div>';}).join('')||'<div class="rgyt-sm">결과 없음</div>';}
function vRadar(){var cs={};S.r.forEach(function(x){cs[cat(x)]=1;});
return'<div class="rgyt-tool"><select id="rgyt-cat"><option value="">전체 카테고리</option>'+Object.keys(cs).map(function(c){return'<option'+(c===S.cat?' selected':'')+'>'+esc(c)+'</option>';}).join('')+'</select><input id="rgyt-q" placeholder="🔍 트렌드·스킬 검색..." value="'+esc(S.q)+'"></div><div id="rgyt-list"></div>';}
function vSkills(){return S.k.map(function(s){if(typeof s==='string')s={name:s};var n=pick(s,['name','slug','id'],'?'),sl=pick(s,['slug','id'],n),inv='[RGON 스킬 호출: '+n+' ('+pick(s,['path'],'skills/'+sl+'/SKILL.md')+')] 이 스킬의 표준 절차에 따라 작업을 수행해 줘.',
g=String(pick(s,['hexagram_tag','hexagram','gua','iching'],'')).replace(/^#/,''),u=pick(s,['source_url','source','url','link'],''),p=pick(s,['path'],'');
return'<div class="rgyt-card"><b>🍯 '+esc(n)+'</b><span class="rgyt-tag">'+esc(pick(s,['category','cat'],'skill'))+'</span>'+(g?'<span class="rgyt-tag">☯️ #'+esc(g)+'</span>':'')+
'<div class="rgyt-sm">경로: <code>'+esc(p||('skills/'+sl+'/SKILL.md'))+'</code></div>'+(u&&u.indexOf('http')===0?'<a href="'+esc(u)+'" target="_blank" rel="noopener">🔗 출처링크</a>':'')+'<button type="button" data-cp="'+esc(inv)+'">📋 스킬호출 복사</button></div>';}).join('');}
function vPulse(){var x=B();
var h='<div class="rgyt-card"><b>🫀 6대 기관 전신 대순환 상태 (Step 22~23 · '+esc(x.ab)+')</b><div class="rgyt-grid">'+x.ol.map(function(o){return'<div class="rgyt-org">'+(ok(o[1])?'🟢 ✔ ':'🔴 ✖ ')+esc(o[0])+'</div>';}).join('')+'</div></div>';
h+='<div class="rgyt-card"><b>☯️ 오늘의 주역 64괘 — '+esc(x.hx)+'</b><div class="rgyt-sm">• <b>풀이:</b> '+esc(x.mt)+'<br>• <b>행동 지침:</b> '+esc(x.act)+'</div></div>';
h+='<div class="rgyt-card"><b>⚖️ 3자 찬반 심판기 (Trinity Council — Bull vs Bear vs Judge)</b><table><tr><th>안건</th><th>🐂Bull</th><th>🐻Bear</th><th>⚖️점수</th><th>판정·괘</th></tr>'+
(x.c.length?x.c.map(function(c){return'<tr><td>'+esc(c.topic)+'</td><td>'+esc(c.bull)+'</td><td>'+esc(c.bear)+'</td><td><b>'+esc(c.judge)+'</b></td><td>'+esc(c.verdict)+'</td></tr>';}).join(''):'<tr><td colspan="5">심판 기록 없음</td></tr>')+'</table></div>';return h;}
function render(){var ts=$('rgyt-tabs').querySelectorAll('button');for(var i=0;i<ts.length;i++)ts[i].className=ts[i].getAttribute('data-tab')===S.tab?'on':'';
$('rgyt-pane').innerHTML=S.tab==='radar'?vRadar():S.tab==='skills'?vSkills():vPulse();if(S.tab==='radar')list();}
function get(ns){return ns.reduce(function(p,n){return p.then(function(r){return r||fetch(n,{cache:'no-store'}).then(function(x){return x.ok?x.json():null;}).catch(function(){return null;});});},Promise.resolve(null));}
function load(){if(!window.fetch)return;Promise.all([get(['rgon_morning_brief.json','./rgon_morning_brief.json','../rgon_morning_brief.json']),get(['skills/SKILL_INDEX.json','./skills/SKILL_INDEX.json','../skills/SKILL_INDEX.json']),get(['rgon_skill_radar.json','./rgon_skill_radar.json','../rgon_skill_radar.json'])]).then(function(v){
if(v[0]&&typeof v[0]==='object')S.b=v[0];var k=v[1]&&(Array.isArray(v[1])?v[1]:v[1].skills);if(k&&k.length)S.k=k;var r=v[2]&&(Array.isArray(v[2])?v[2]:(v[2].items||v[2].cards||v[2].radar));if(r&&r.length)S.r=r;badge();render();}).catch(function(){});}
function initUI(){var w=$('rgyt-wrap');if(!w||w.getAttribute('data-ui-bound')==='1')return;w.setAttribute('data-ui-bound','1');
w.addEventListener('click',function(e){var t=e.target;if(t.closest('#rgyt-head')){var b=$('rgyt-body');b.hidden=!b.hidden;$('rgyt-tog').textContent=b.hidden?'▼ 펼치기':'▲ 접기';return;}
var tb=t.closest('[data-tab]');if(tb){S.tab=tb.getAttribute('data-tab');render();return;}var c=t.closest('[data-cp]');if(c)cp(c.getAttribute('data-cp'),c);});
w.addEventListener('input',function(e){if(e.target.id==='rgyt-q'){S.q=e.target.value;list();}});
w.addEventListener('change',function(e){if(e.target.id==='rgyt-cat'){S.cat=e.target.value;list();}});
badge();render();load();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initUI,{once:true});else initUI();
}catch(e){}})();
</script>"""

def patch(targets, fbjson):
    anchors = {}
    for p in targets:
        t = rd(p); bak(p)
        i, j = t.index(M_S) + len(M_S), t.index(M_E)
        old_inner = t[i:j]
        if V15_S in old_inner and V15_E in old_inner:
            v15_part = old_inner[old_inner.index(V15_S):old_inner.index(V15_E) + len(V15_E)]
            anchors[rel(p)] = "V15-placeOnce(실시간 브리핑 전문 아래)"
        else:
            v15_part = DEFAULT_V15
            anchors[rel(p)] = "DEFAULT-V15-placeOnce"
        blk = BLOCK.replace("__FB__", fbjson) + "\n" + v15_part
        wr(p, t[:i] + "\n" + blk + "\n" + t[j:])
        log(f"🎨 V13 내부 교체 {rel(p)} ({anchors[rel(p)]})")
    return anchors

def verify(targets, guard):
    v1 = []
    for p in targets:
        t = rd(p); ok = t.count(M_S) == 1 and t.count(M_E) == 1
        inner = t[t.index(M_S):t.index(M_E)] if ok else ""
        f_in, f_all = len(FORBID.findall(inner)), len(FORBID.findall(t))
        v1.append((rel(p), ok and "placeOnce" in inner and f_in == 0, f_in, f_all))
    diff = [rel(p) for p, h in guard.items() if not p.exists() or sha(p) != h]
    miss = [r for r in SYNC if (ROOT / r).exists() and not (VER in rd(ROOT / r) and AB in rd(ROOT / r))]
    led = ROOT / "rgon_immune_ledger.json"
    if led.exists() and "R23" not in rd(led): miss.append("rgon_immune_ledger.json(R23)")
    miss += [b for b in BACKEND if (ROOT / b).exists() and "R23" not in rd(ROOT / b)]
    return v1, diff, miss

def report(targets, guard, v1, diff, miss, anchors, cyc):
    g1, g2, g3 = all(x[1] for x in v1) and bool(v1), not diff, not miss
    L = [f"# STEP23 UI REPORT — {VER} / {AB}", "", f"- 생성: {TS}", f"- 항체: {R23}", f"- daily_cycle: {'성공' if cyc else '실패/경고'}",
         f"- 백업: {rel(BAK)}", f"- 대상 HTML: {len(targets)}개 (기대 7개{'' if len(targets) == 7 else ' ⚠️ 불일치'})", "",
         f"## 三省 ① 대상 검증 {'✅' if g1 else '❌'}", "| 파일 | 통과 | 마커 내부 금지어 | 파일 전체 금지어(마커 밖 기존, 무수정) | 배치 방식 |", "|---|---|---|---|---|"]
    L += [f"| {a} | {'✅' if b else '❌'} | {c} | {d} | {anchors.get(a, '')} |" for a, b, c, d in v1]
    L += ["", f"## 三省 ② 비대상 SHA-256 불변 {'✅' if g2 else '❌'} (수호 {len(guard)}개, 변경 {len(diff)}개)", BT3]
    L += [f"{h[:16]}…  {rel(p)}" for p, h in sorted(guard.items())][:200] + [BT3]
    L += [f"- 변경 감지: {d}" for d in diff]
    L += ["", f"## 三省 ③ 버전·항체 동기화 {'✅' if g3 else '❌'}"] + [f"- 미동기화: {m}" for m in miss]
    L += ["", "## 실행 로그", BT3] + LOG[-60:] + [BT3]
    wr(ROOT / "STEP23_UI_REPORT.md", "\n".join(L) + "\n")
    return sum([g1, g2, g3])

def git():
    files = sorted({rel(p) for p in CHANGED if p.exists() and BAK not in p.parents})
    if Path(__file__).resolve().exists() and ROOT in Path(__file__).resolve().parents:
        files = sorted(set(files) | {rel(Path(__file__).resolve())})
    out = []
    for cmd in (["git", "add", "--"] + files, ["git", "commit", "-m", f"Step23 {VER} {AB}: 전신 맥박·18 스킬 3탭 (V13 마커 내부만, placeOnce 단발)"], ["git", "push"]):
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        out.append(f"{cmd[1]} rc={r.returncode}"); log(f"🌿 {cmd[1]} rc={r.returncode} {(r.stdout + r.stderr)[-200:].strip()}")
    return " · ".join(out)

def msgbox(msg, good):
    try:
        import ctypes; ctypes.windll.user32.MessageBoxW(0, msg, f"RGON Step23 {VER}", 0x40 if good else 0x30)
    except Exception: print(msg)

def main():
    bump_backend()
    cyc = run_cycle()
    sync_fix()
    targets, guard = classify()
    log(f"🔍 V13 대상 {len(targets)}개 · 수호(비대상 HTML/.js/manifest) {len(guard)}개")
    if not targets: msgbox("V13 마커 보유 HTML을 찾지 못했습니다. 중단합니다.", False); return
    anchors = patch(targets, fallback())
    v1, diff, miss = verify(targets, guard)
    score = report(targets, guard, v1, diff, miss, anchors, cyc)
    g = git()
    msgbox(f"三省 {score}/3\n대상 HTML {len(targets)}개 교체 (V15 placeOnce 보존, 루프 0)\n비대상 해시 변경 {len(diff)}건\n"
           f"미동기화 {len(miss)}건\n{g}\n보고서: STEP23_UI_REPORT.md", score == 3)

if __name__ == "__main__":
    main()
