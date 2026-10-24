#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""step25_omni_skill_dispatcher.py — Step 25 「연결·소통·만능」 v11.24-OMNI-DISPATCH / R1~R25
카파시 4원칙(먼저 생각·단순함·외과적 변경·검증 목표) + 무위자연·과유불급·삼성(三省 3/3) 준수.
V13 마커 내부의 V15 앞부분만 업그레이드하고, V15 placeOnce 블록은 바이트 단위로 그대로 보존한다(R15·R23·R25)."""
import datetime, hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VER, RNG, BT3 = "v11.24-OMNI-DISPATCH", "R1~R25", chr(96) * 3
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
R25 = "R25: 연결·소통·만능 원터치 스킬 디스패처 — 보유 스킬·트렌드·3자 심판 결과를 독대실 질문창에 무간섭 단발 장전"
M13S, M13E = "<!-- [RGON-YT-SCOUT-V13-START] -->", "<!-- [RGON-YT-SCOUT-V13-END] -->"
M15S, M15E = "<!-- [RGYT-PLACE-ONCE-V15-START] -->", "<!-- [RGYT-PLACE-ONCE-V15-END] -->"
FORBID = ("Mutation" + "Observer", "set" + "Interval", "request" + "AnimationFrame")
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "backups", ".rgon_ad_backups"}
RX_R, RX_V = re.compile(r"R1\s*[~\-–]\s*R2[0-4]\b"), re.compile(r"v1\d\.\d+[A-Za-z0-9_\-]*")
CHANGED, LOG = set(), []
SKILL = {"slug": "omni-skill-dispatcher", "id": "omni-skill-dispatcher",
         "name": "Omni Skill Dispatcher (만능 원터치 디스패처)",
         "category": "omni-dispatch", "hexagram_tag": "#14-大有", "origin": "core",
         "version": VER, "antibody": "R25",
         "path": "skills/omni-skill-dispatcher/SKILL.md",
         "source_url": "local://step25_omni_skill_dispatcher.py",
         "description": "독대실 3탭(트렌드·보유 스킬·3자 심판) 항목을 [⚡ 질문창 장전] 원터치로 질문창에 단발 장전하고 클립보드에도 복사"}
IDX = [ROOT / "skills/SKILL_INDEX.json", ROOT / "dashboard/skills/SKILL_INDEX.json", ROOT / "docs/skills/SKILL_INDEX.json"]
BRIEF = [ROOT / "rgon_morning_brief.json", ROOT / "dashboard/rgon_morning_brief.json", ROOT / "docs/rgon_morning_brief.json"]
SNAP = [ROOT / "rgon_brain_snapshot.json", ROOT / "dashboard/rgon_brain_snapshot.json", ROOT / "docs/rgon_brain_snapshot.json"]
LEDGER, MDS = ROOT / "rgon_immune_ledger.json", ["CLAUDE.md", "CODE_MAP.md", "MORNING_BRIEF.md", "RGON_EVOLUTION_LOG.md"]

def rd(p): return p.read_bytes().decode("utf-8", errors="replace")
def wr(p, s): p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(s.encode("utf-8")); CHANGED.add(p)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def jsave(p, o): wr(p, json.dumps(o, ensure_ascii=False, indent=2) + "\n")
def jload(p):
    try: return json.loads(rd(p).lstrip("\ufeff"))
    except Exception: return None
def walk():
    for dp, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if d not in SKIP]
        for f in fs: yield Path(dp) / f
def rel(p): return p.relative_to(ROOT).as_posix()
def v15(s):
    a = s.find(M15S); b = s.find(M15E, a)
    return s[a:b + len(M15E)] if a >= 0 and b > a else ""
def v13_inner(s):
    a = s.find(M13S); b = s.find(M13E, a)
    return s[a + len(M13S):b] if a >= 0 and b > a else ""
def arr(o, keys):
    if isinstance(o, list): return o
    if isinstance(o, dict):
        for k in keys:
            if isinstance(o.get(k), list): return o[k]
        for v in o.values():
            if isinstance(v, list): return v
    return []

def forge_skill():
    md = ("---\nname: omni-skill-dispatcher\ndescription: " + SKILL["description"] + "\n---\n\n"
          f"# ⚡ Omni Skill Dispatcher — 20번째 정식 스킬 (#14-大有 · omni-dispatch · {VER})\n\n> {R25}\n\n"
          "## 언제 쓰나\n독대실 3탭(📡 트렌드 레이더 / 🍯 보유 스킬 / 🫀 전신 맥박 & 3자 심판)의 항목을 질문창에 바로 장전할 때.\n\n"
          "## 동작 (단발 · 루프 없음)\n1. `[⚡ 질문창 장전]`(data-load)을 누르면 `#rgyt-wrap` 바깥의 보이는 textarea 또는 text input을 찾는다(`#rgyt-q` 제외).\n"
          "2. 네이티브 value setter로 값을 넣고 `input`/`change` 이벤트를 보낸다(React 제어형 입력창 호환).\n"
          "3. 클립보드에도 복사하고, 버튼에 1.2초 동안 `⚡ 장전+복사 완료!`를 띄운 뒤 입력창에 포커스한다.\n\n"
          "## 금기 (R15·R23·R25)\nV15 placeOnce 블록 보존. 감시 루프·반복 타이머·프레임 루프 API는 쓰지 않는다. .js/manifest.json은 수정하지 않는다.\n\n"
          f"## 호출 예\n{BT3}text\n[⚡ 스킬 호출] omni-skill-dispatcher\n→ skills/omni-skill-dispatcher/SKILL.md 지침에 따라 실행해 줘.\n{BT3}\n")
    for base in ("skills", "dashboard/skills", "docs/skills"):
        if base == "skills" or (ROOT / base).is_dir(): wr(ROOT / base / "omni-skill-dispatcher/SKILL.md", md)
    base_obj = None
    for p in IDX:
        o = jload(p) if p.exists() else None
        if o is None: o = json.loads(json.dumps(base_obj)) if base_obj is not None else {"skills": []}
        lst = o if isinstance(o, list) else o.setdefault("skills", [])
        lst[:] = [x for x in lst if not (isinstance(x, dict) and SKILL["slug"] in (x.get("slug"), x.get("id")))] + [dict(SKILL)]
        if isinstance(o, dict): o.update(version=VER, count=len(lst), antibody_range=RNG, updated=NOW)
        jsave(p, o); base_obj = base_obj if base_obj is not None else o
    LOG.append(f"스킬 주조 및 인덱스 3곳 등재 완료 ({len(arr(jload(IDX[0]), ['skills']))}개)")

def bump(o, d=0):
    if d > 3: return o
    if isinstance(o, dict):
        for k, v in list(o.items()):
            kl = k.lower()
            if isinstance(v, str) and "version" in kl and RX_V.match(v): o[k] = VER
            elif isinstance(v, str) and "antibody_range" in kl: o[k] = RNG
            elif type(v) is int and "skill" in kl and ("count" in kl or "total" in kl): o[k] = 20
            else: o[k] = bump(v, d + 1)
        return o
    if isinstance(o, list): return [bump(x, d + 1) for x in o]
    return RX_R.sub(RNG, o) if isinstance(o, str) else o

def ledger_add(o):
    rule = {"id": "R25", "name": "원터치 만능 스킬 디스패처", "rule": R25, "version": VER, "status": "활성", "added": NOW}
    o["antibody_count"] = 25
    for k in ("antibodies", "rules", "immune_rules", "ledger", "entries"):
        v = o.get(k)
        if isinstance(v, list):
            if "R25" not in json.dumps(v, ensure_ascii=False): v.append(R25 if v and isinstance(v[0], str) else rule)
            return
        if isinstance(v, dict): v.setdefault("R25", R25 if any(isinstance(x, str) for x in v.values()) else rule); return
    o.setdefault("antibodies", [rule])

def sync_json(p, ledger=False):
    o = jload(p) if p.exists() else ({} if ledger else None)
    if not isinstance(o, dict): LOG.append(f"⚠️ 건너뜀(없음/비객체): {rel(p)}"); return
    bump(o)
    if ledger: ledger_add(o)
    o.update(version=VER, antibody_range=RNG, skill_count=20, skills_count=20, last_sync=f"Step25 {NOW}")
    jsave(p, o)

def sync_md():
    blk = (f"<!-- [RGON-STATUS-V25-START] -->\n> **현재 버전**: `{VER}` · 항체 `{RNG}` · 정식 스킬 **20개** "
           f"(20번째: `omni-skill-dispatcher` · #14-大有 · omni-dispatch)\n> **{R25}**\n<!-- [RGON-STATUS-V25-END] -->")
    pat = re.compile(r"<!-- \[RGON-STATUS-V25-START\] -->.*?<!-- \[RGON-STATUS-V25-END\] -->", re.S)
    for n in MDS:
        p = ROOT / n; s = rd(p) if p.exists() else f"# {n[:-3]}\n"
        s = RX_R.sub(RNG, RX_V.sub(VER, s))
        if pat.search(s): s = pat.sub(lambda m: blk, s)
        else: h, _, t = s.partition("\n"); s = h + "\n\n" + blk + "\n" + t
        if n == "RGON_EVOLUTION_LOG.md" and f"Step 25 — {VER}" not in s:
            s = s.rstrip() + (f"\n\n## Step 25 — {VER} ({NOW})\n- 20번째 스킬 `omni-skill-dispatcher` (#14-大有) 주조\n"
                              "- 독대실 3탭 `[⚡ 질문창 장전]`(data-load) 원터치 디스패처 장착 (V13 내부, V15 placeOnce 보존)\n"
                              f"- 항체 {RNG} 승격 — {R25}\n")
        wr(p, s)

TC_PATCH = '''
# [RGON-OMNI-DISPATCH-R25-START] — Step25: 20번째 스킬 omni-skill-dispatcher 보존
_OMNI_SKILL = __SKILL__
try:
    _omni_orig_ensure = ensure_skill_index
    def ensure_skill_index(*a, **k):
        r = _omni_orig_ensure(*a, **k)
        import json as _j, pathlib as _pl
        _b = _pl.Path(__file__).resolve().parent
        for _rel in ("skills", "dashboard/skills", "docs/skills"):
            _p = _b / _rel / "SKILL_INDEX.json"
            try:
                _o = _j.loads(_p.read_text(encoding="utf-8"))
                _l = _o if isinstance(_o, list) else _o.setdefault("skills", [])
                if not any(isinstance(x, dict) and x.get("slug") == _OMNI_SKILL["slug"] for x in _l):
                    _l.append(dict(_OMNI_SKILL))
                if isinstance(_o, dict):
                    _o["count"] = len(_l)
                    _o["version"] = "v11.24-OMNI-DISPATCH"
                    _o["antibody_range"] = "R1~R25"
                _p.write_text(_j.dumps(_o, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
            except Exception:
                pass
        return 20
except NameError:
    pass
# [RGON-OMNI-DISPATCH-R25-END]
'''

def sync_backend():
    rx_a = re.compile(r"""^(\s*[A-Z_]*(?:VERSION|VER)[A-Z_]*\s*=\s*)(["'])v1\d\.\d+[^"'\n]*\2""", re.M)
    rx_k = re.compile(r"""(["']version["']\s*:\s*)(["'])v1\d\.\d+[^"'\n]*\2""")
    rx_tc = re.compile(r"\n# \[RGON-OMNI-DISPATCH-R25-START\].*?# \[RGON-OMNI-DISPATCH-R25-END\]\n", re.S)
    for p in [q for q in walk() if q.name.startswith("rgon_") and q.suffix == ".py"]:
        old = rd(p); s = RX_R.sub(RNG, rx_k.sub(lambda m: f"{m[1]}{m[2]}{VER}{m[2]}", rx_a.sub(lambda m: f"{m[1]}{m[2]}{VER}{m[2]}", old)))
        if p.name == "rgon_trading_council.py" and "def ensure_skill_index" in s:
            blk = TC_PATCH.replace("__SKILL__", repr(SKILL)); s = rx_tc.sub("", s)
            m = re.search(r'^if __name__\s*==\s*["\']__main__["\']', s, re.M)
            s = s[:m.start()] + blk.lstrip("\n") + "\n" + s[m.start():] if m else s.rstrip() + "\n" + blk
        if s == old: continue
        try: compile(s, str(p), "exec"); wr(p, s); LOG.append(f"백엔드 동기화: {rel(p)}")
        except SyntaxError as e: LOG.append(f"⚠️ 롤백(문법 오류): {rel(p)} — {e}")

BLOCK_UI = r"""<style>
#rgyt-wrap{margin:6px 0;border:1px solid #2a3550;border-radius:10px;background:#0f1626;color:#dfe6f5;font-size:13px}
#rgyt-head{display:flex;gap:8px;align-items:center;padding:8px 12px;cursor:pointer;flex-wrap:wrap;background:linear-gradient(90deg,#111c35,#162447);border-radius:10px}
#rgyt-pulse{opacity:.92;font-size:12px;color:#93c5fd}#rgyt-tog{margin-left:auto;font-weight:bold;color:#60a5fa}
#rgyt-tabs{display:flex;gap:6px;padding:8px 10px 6px;flex-wrap:wrap;border-top:1px solid #1e293b}
#rgyt-tabs button,#rgyt-wrap .rgyt-card button,#rgyt-wrap td button{background:#1b2540;color:#dfe6f5;border:1px solid #33416a;border-radius:7px;padding:4px 9px;cursor:pointer;font-size:12px;margin-right:4px}
#rgyt-tabs button.on{background:#2563eb;border-color:#3b82f6;font-weight:bold;color:#fff}
#rgyt-wrap button[data-load]{background:#5b3df5;border-color:#7b61ff;color:#fff;font-weight:600}
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
<div id="rgyt-wrap" data-ver="v11.24-OMNI-DISPATCH" data-antibody="R1~R25">
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
    ab:pick(b,['antibody_range'],'R1~R25'),
    hx:pick(h,['name','title'],'중천건(重天乾)'),
    mt:pick(h,['meaning','motto','keyword'],'자강불식(自強不息)'),
    act:pick(h,['action','guidance'],'상선약수(上善若水) · 삼성(三省) — 6대 기관을 물처럼 순환시키고 하루 세 번 무결성을 살핀다.'),
    ol:ol,
    c:parseTri(tri)
  };
}
function cpText(t){
  function fb(){var a=document.createElement('textarea');a.value=t;a.style.cssText='position:fixed;left:-9999px;opacity:0';document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}a.remove();}
  if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).catch(fb);else fb();
}
function findInput(){
  var w=$('rgyt-wrap');
  var c=[].slice.call(document.querySelectorAll('textarea,input[type=text],input:not([type])')).filter(function(e){
    return e.id!=='rgyt-q'&&(!w||!w.contains(e))&&!e.disabled&&!e.readOnly&&e.offsetParent!==null;
  });
  c.sort(function(a,b){return(b.tagName==='TEXTAREA')-(a.tagName==='TEXTAREA');});
  return c[0]||null;
}
function setInputVal(el,val){
  var proto=el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
  var d=Object.getOwnPropertyDescriptor(proto,'value');
  if(d&&d.set)d.set.call(el,val);else el.value=val;
  el.dispatchEvent(new Event('input',{bubbles:true}));
  el.dispatchEvent(new Event('change',{bubbles:true}));
}
function flashBtn(btn,msg){
  var o=btn.textContent;btn.textContent=msg;
  setTimeout(function(){btn.textContent=o;},1200);
}
function badge(){var x=B();$('rgyt-pulse').textContent='🩸'+x.sc+'점 · 🛡️'+x.ab+' · ☯️'+x.hx.split('(')[0]+' · 🍯스킬 '+S.k.length+'개 · 📡레이더 '+S.r.length+'건';
$('rgyt-t-radar').textContent='📡 트렌드 레이더 ('+S.r.length+')';$('rgyt-t-skills').textContent='🍯 보유 스킬 ('+S.k.length+')';$('rgyt-t-pulse').textContent='🫀 전신 맥박 & 3자 심판 ('+x.c.length+')';}
function cat(x){return pick(x,['category','cat','channel','tag'],'트렌드');}
function list(){var q=S.q.toLowerCase(),L=S.r.filter(function(x){return(!S.cat||cat(x)===S.cat)&&(!q||JSON.stringify(x).toLowerCase().indexOf(q)>=0);});
$('rgyt-list').innerHTML=L.map(function(x){var u=pick(x,['url','link','source_url','source'],''),t=pick(x,['title','name'],'(무제)'),sm=pick(x,['summary','desc','description','why','action_plan'],'');
var prompt='[📡 트렌드 흡수 지시] '+t+(u?' ('+u+')':'')+'\n'+sm+'\n→ 이 트렌드를 RGON(카파시 4원칙·무위자연·R1~R25)에 맞게 흡수하는 방안을 제시해 줘.';
return'<div class="rgyt-card"><b>'+esc(t)+'</b><span class="rgyt-tag">'+esc(cat(x))+'</span><div class="rgyt-sm">'+esc(sm)+'</div>'+(u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">🔗 원본열기</a>':'')+'<button type="button" data-cp="'+esc(prompt)+'">📋 복사</button><button type="button" data-load="'+esc(prompt)+'">⚡ 질문창 장전</button></div>';}).join('')||'<div class="rgyt-sm">결과 없음</div>';}
function vRadar(){var cs={};S.r.forEach(function(x){cs[cat(x)]=1;});
return'<div class="rgyt-tool"><select id="rgyt-cat"><option value="">전체 카테고리</option>'+Object.keys(cs).map(function(c){return'<option'+(c===S.cat?' selected':'')+'>'+esc(c)+'</option>';}).join('')+'</select><input id="rgyt-q" placeholder="🔍 트렌드·스킬 검색..." value="'+esc(S.q)+'"></div><div id="rgyt-list"></div>';}
function vSkills(){return S.k.map(function(s){if(typeof s==='string')s={name:s};var n=pick(s,['name','slug','id'],'?'),sl=pick(s,['slug','id'],n),p=pick(s,['path'],'skills/'+sl+'/SKILL.md'),
inv='[⚡ RGON 스킬 호출: '+n+' ('+p+')] 이 스킬의 표준 절차(카파시 4원칙·R1~R25)에 따라 지금 작업을 수행해 줘.',
g=String(pick(s,['hexagram_tag','hexagram','gua','iching'],'')).replace(/^#/,''),u=pick(s,['source_url','source','url','link'],'');
return'<div class="rgyt-card"><b>🍯 '+esc(n)+'</b><span class="rgyt-tag">'+esc(pick(s,['category','cat'],'skill'))+'</span>'+(g?'<span class="rgyt-tag">☯️ #'+esc(g)+'</span>':'')+
'<div class="rgyt-sm">경로: <code>'+esc(p)+'</code></div>'+(u&&u.indexOf('http')===0?'<a href="'+esc(u)+'" target="_blank" rel="noopener">🔗 출처링크</a>':'')+'<button type="button" data-cp="'+esc(inv)+'">📋 복사</button><button type="button" data-load="'+esc(inv)+'">⚡ 질문창 장전</button></div>';}).join('');}
function vPulse(){var x=B();
var h='<div class="rgyt-card"><b>🫀 6대 기관 전신 대순환 상태 ('+esc(x.ab)+')</b><div class="rgyt-grid">'+x.ol.map(function(o){return'<div class="rgyt-org">'+(ok(o[1])?'🟢 ✔ ':'🔴 ✖ ')+esc(o[0])+'</div>';}).join('')+'</div></div>';
h+='<div class="rgyt-card"><b>☯️ 오늘의 주역 64괘 — '+esc(x.hx)+'</b><div class="rgyt-sm">• <b>풀이:</b> '+esc(x.mt)+'<br>• <b>행동 지침:</b> '+esc(x.act)+'</div></div>';
h+='<div class="rgyt-card"><b>⚖️ 3자 찬반 심판기 (Trinity Council — 시스템 3건 + 실전 트레이딩 4건)</b><table><tr><th>안건</th><th>🐂Bull</th><th>🐻Bear</th><th>⚖️점수</th><th>판정·괘</th><th>원터치</th></tr>'+
(x.c.length?x.c.map(function(c){var pr='[⚖️ 3자 심판 점검] '+c.topic+' (판정: '+c.verdict+', 점수: '+c.judge+', Bull '+c.bull+' / Bear '+c.bear+') → 이 안건의 현재 리스크와 실행 지침을 점검해 줘.';return'<tr><td>'+esc(c.topic)+'</td><td>'+esc(c.bull)+'</td><td>'+esc(c.bear)+'</td><td><b>'+esc(c.judge)+'</b></td><td>'+esc(c.verdict)+'</td><td><button type="button" data-load="'+esc(pr)+'">⚡ 질문창 장전</button></td></tr>';}).join(''):'<tr><td colspan="6">심판 기록 없음</td></tr>')+'</table></div>';return h;}
function render(){var ts=$('rgyt-tabs').querySelectorAll('button');for(var i=0;i<ts.length;i++)ts[i].className=ts[i].getAttribute('data-tab')===S.tab?'on':'';
$('rgyt-pane').innerHTML=S.tab==='radar'?vRadar():S.tab==='skills'?vSkills():vPulse();if(S.tab==='radar')list();}
function get(ns){return ns.reduce(function(p,n){return p.then(function(r){return r||fetch(n,{cache:'no-store'}).then(function(x){return x.ok?x.json():null;}).catch(function(){return null;});});},Promise.resolve(null));}
function load(){if(!window.fetch)return;Promise.all([get(['rgon_morning_brief.json','./rgon_morning_brief.json','../rgon_morning_brief.json']),get(['skills/SKILL_INDEX.json','./skills/SKILL_INDEX.json','../skills/SKILL_INDEX.json']),get(['rgon_skill_radar.json','./rgon_skill_radar.json','../rgon_skill_radar.json'])]).then(function(v){
if(v[0]&&typeof v[0]==='object')S.b=v[0];var k=v[1]&&(Array.isArray(v[1])?v[1]:v[1].skills);if(k&&k.length)S.k=k;var r=v[2]&&(Array.isArray(v[2])?v[2]:(v[2].items||v[2].cards||v[2].radar));if(r&&r.length)S.r=r;badge();render();}).catch(function(){});}
function initUI(){var w=$('rgyt-wrap');if(!w||w.getAttribute('data-ui-bound')==='1')return;w.setAttribute('data-ui-bound','1');
w.addEventListener('click',function(e){var t=e.target;if(t.closest('#rgyt-head')){var b=$('rgyt-body');b.hidden=!b.hidden;$('rgyt-tog').textContent=b.hidden?'▼ 펼치기':'▲ 접기';return;}
var tb=t.closest('[data-tab]');if(tb){S.tab=tb.getAttribute('data-tab');render();return;}
var cpBtn=t.closest('[data-cp]');if(cpBtn){cpText(cpBtn.getAttribute('data-cp'));flashBtn(cpBtn,'✅ 복사완료');return;}
var ldBtn=t.closest('[data-load]');if(ldBtn){var txt=ldBtn.getAttribute('data-load');cpText(txt);var inp=findInput();if(inp){setInputVal(inp,txt);try{inp.scrollIntoView({behavior:'smooth',block:'center'});}catch(_){}inp.focus({preventScroll:true});flashBtn(ldBtn,'⚡ 장전+복사 완료!');}else{flashBtn(ldBtn,'📋 복사완료(입력창 없음)');}}});
w.addEventListener('input',function(e){if(e.target.id==='rgyt-q'){S.q=e.target.value;list();}});
w.addEventListener('change',function(e){if(e.target.id==='rgyt-cat'){S.cat=e.target.value;list();}});
badge();render();load();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initUI,{once:true});else initUI();
}catch(e){}})();
</script>"""

def build_panel():
    brief = jload(ROOT / "rgon_morning_brief.json") or {}
    tri_list = ((brief.get("nutrient") or {}).get("trinity")) or []
    skills = arr(jload(IDX[0]), ["skills"])
    radar = arr(jload(ROOT / "rgon_skill_radar.json"), ["items", "cards", "radar", "trends", "entries"])
    fb = {"brief": brief, "skills": skills, "radar": radar}
    s = json.dumps(fb, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    for w in FORBID: s = s.replace(w, w[0] + "\\u%04x" % ord(w[1]) + w[2:])
    n = {"brief": len(tri_list), "skills": len(skills), "radar": len(radar)}
    return f"\n<!-- [RGON-OMNI-DISPATCH-V25] {VER} · {RNG} · 단발 렌더(무루프) -->\n" + BLOCK_UI.replace("__FB__", s) + "\n", n

def patch_html(p, panel):
    s = rd(p); a = s.find(M13S); b = s.find(M13E, a); inner = s[a + len(M13S):b]; i = inner.find(M15S)
    if i < 0 and "placeOnce" in inner: LOG.append(f"⚠️ 보류(V15 밖에 placeOnce 있음): {rel(p)}"); return
    new = s[:a + len(M13S)] + panel + (inner[i:] if i >= 0 else "\n") + s[b:]
    if new != s: wr(p, new)

def git(*a):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()

def msgbox(title, msg, ok):
    try: import ctypes; ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40 if ok else 0x10)
    except Exception: print(f"[{title}]\n{msg}")

def main():
    os.chdir(ROOT); files = list(walk())
    targets = sorted([p for p in files if p.suffix.lower() in (".html", ".htm") and M13S.encode() in p.read_bytes() and M13E.encode() in p.read_bytes()])
    tset = set(targets)
    prot = [p for p in files if p.suffix.lower() == ".js" or p.name == "manifest.json" or (p.suffix.lower() in (".html", ".htm") and p not in tset)]
    before, v15b = {p: sha(p) for p in prot}, {p: v15(rd(p)) for p in targets}
    forge_skill()
    for p in BRIEF + SNAP: sync_json(p)
    sync_json(LEDGER, ledger=True); sync_md(); sync_backend()
    panel, n = build_panel()
    for p in targets: patch_html(p, panel)
    e1 = [] if len(targets) == 7 else [f"대상 HTML {len(targets)}개 (7개여야 함)"]
    for p in targets:
        s = rd(p); inner = v13_inner(s)
        if s.count(M13S) != 1 or s.count(M13E) != 1: e1.append(f"{rel(p)}: V13 마커 쌍 이상")
        if v15(s) != v15b[p] or "placeOnce" not in s: e1.append(f"{rel(p)}: V15 placeOnce 보존 실패")
        if 'data-load' not in inner: e1.append(f"{rel(p)}: data-load 장착 없음")
        bad = [w for w in FORBID if w in inner]
        if bad: e1.append(f"{rel(p)}: 마커 내부 금지어 {bad}")
    e2 = [rel(p) for p in prot if not p.exists() or sha(p) != before[p]]
    e3 = []
    for p in IDX:
        lst = arr(jload(p), ["skills"]); hit = [x for x in lst if isinstance(x, dict) and x.get("slug") == SKILL["slug"]]
        if len(lst) != 20 or not hit or hit[0].get("hexagram_tag") != "#14-大有": e3.append(f"{rel(p)}: 스킬 {len(lst)}개 / 등재 이상")
    for p in [x for x in BRIEF + SNAP if x.exists()] + [LEDGER] + [ROOT / m for m in MDS]:
        t = rd(p)
        if VER not in t or RNG not in t: e3.append(f"{rel(p)}: {VER}/{RNG} 미동기화")
    if "R25" not in rd(LEDGER): e3.append("rgon_immune_ledger.json: R25 없음")
    ok = not (e1 or e2 or e3); passed = sum(not e for e in (e1, e2, e3))
    warn = [f"브리핑 {n['brief']}건(기대 7)" if n["brief"] != 7 else "", f"레이더 {n['radar']}건(기대 13)" if n["radar"] != 13 else ""]
    def sec(t, e): return f"### {t} — {'✅ 통과' if not e else '❌ 실패'}\n" + "".join(f"- {x}\n" for x in e[:50])
    rep = (f"# STEP25 OMNI DISPATCH REPORT — {VER}\n\n- 시각: {NOW}\n- 항체: {RNG} — {R25}\n- 삼성: **{passed}/3**\n"
           f"- V13 대상 HTML: {len(targets)}개 · 보호 해시 대상: {len(prot)}개 · 변경 0건 여부: {'예' if not e2 else '아니오'}\n"
           f"- 내장 폴백(__FB__): 3자심판 {n['brief']}건 · 스킬 {n['skills']}개 · 레이더 {n['radar']}건\n"
           + "".join(f"- ⚠️ {w}\n" for w in warn if w) + "\n" + sec("一省 V13 HTML·placeOnce·data-load·금지어", e1)
           + sec("二省 비대상 HTML·.js·manifest.json SHA-256 불변", e2) + sec("三省 버전·R1~R25·스킬 20개 3곳 동기화", e3)
           + f"\n## 대상 HTML\n" + "".join(f"- {rel(p)}\n" for p in targets) + f"\n## 작업 로그\n{BT3}text\n" + "\n".join(LOG) + f"\n{BT3}\n")
    wr(ROOT / "STEP25_OMNI_DISPATCH_REPORT.md", rep)
    gmsg = "Git 생략(검증 실패)"
    if ok and (ROOT / ".git").exists():
        me = Path(__file__).resolve()
        add = sorted({rel(p) for p in CHANGED} | ({rel(me)} if me.exists() and ROOT in me.parents else set()))
        git("add", "--", *add); c, o = git("commit", "-m", f"Step25 {VER}: omni-skill-dispatcher(20번째 스킬)·R25·⚡ 질문창 장전")
        pc, po = git("push"); gmsg = f"commit={'OK' if c == 0 else o[:120]} / push={'OK' if pc == 0 else po[:160]}"
    elif ok: gmsg = "Git 저장소 없음 — 생략"
    print(rep); print(gmsg)
    msgbox("RGON Step25 " + ("완료 ✅" if ok else "검증 실패 ❌"),
           f"{VER} / {RNG}\n삼성 {passed}/3\nV13 HTML {len(targets)}개 · 보호 해시 변경 {len(e2)}건\n스킬 {n['skills']}개 · 3자심판 {n['brief']}건 · 레이더 {n['radar']}건\n{gmsg}", ok)
    sys.exit(0 if ok else 1)

if __name__ == "__main__": main()
