#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as _dt
import functools
import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
BASKET_NAME = "ingredients_basket"
SRC_BASKET = BASE_DIR / BASKET_NAME
MP4_NAME = "trimmed_ad_paper_cup_10s.mp4"
MANIFEST_NAME = "v5_manifest.json"
DEFAULT_PORT = 8501
HTML_NAME = "rgon_alpha_chat.html"

HTML_TARGETS = [
    BASE_DIR / "dashboard" / HTML_NAME,
    BASE_DIR / HTML_NAME,
    BASE_DIR / "docs" / HTML_NAME,
]
SW_TARGETS = [
    BASE_DIR / "sw.js",
    BASE_DIR / "dashboard" / "sw.js",
    BASE_DIR / "docs" / "sw.js",
]
BASKET_TARGETS = [
    SRC_BASKET,
    BASE_DIR / "dashboard" / BASKET_NAME,
    BASE_DIR / "docs" / BASKET_NAME,
]

MARK_START = "<!-- SHIN_AD_V5_START -->"
MARK_END = "<!-- SHIN_AD_V5_END -->"
SCENE_RE = re.compile(r"^scene_([0-2])_[\w\-]+\.(?:jpe?g|png|webp)$", re.I)
SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "env", ".idea", ".vscode", "dist", "build"}

DEFAULT_FIREFLY_PROMPT = (
    "Photorealistic commercial product photo of a premium double-wall white paper coffee cup "
    "with steam rising, held in a hand on a sunny morning commute, shallow depth of field, "
    "soft golden-hour light, clean minimal background, vertical 9:16, 8k, advertising quality"
)
DEFAULT_EXPRESS_KEYWORDS = "YouTube Shorts 광고, 커피 컵 프로모션, 미니멀 제품 광고, 세로 9:16 릴스 템플릿"
DEFAULT_SUNO_PROMPT = (
    "62 BPM warm lo-fi acoustic cafe groove, soft piano and brushed drums, "
    "uplifting morning mood, instrumental, ducking-friendly under Korean voice-over"
)
DEFAULT_PODCAST_TIP = "성우 녹음 파일(WAV/MP3)을 Adobe Podcast Enhance에 올리면 잡음 제거 + 스튜디오 음질로 무료 보정됩니다."

DEFAULT_PAPER_SCENES = [
    {"index": 0, "key": "hook", "title": "평범한 한 잔, 다르게.", "sub": "매일의 한 잔에, 새로운 분위기", "start": 0.0, "end": 3.0},
    {"index": 1, "key": "benefit", "title": "한 잔의 순간을 더 근사하게.", "sub": "종이컵으로 연출하는 작은 순간", "start": 3.0, "end": 7.0},
    {"index": 2, "key": "cta", "title": "당신의 한 잔을 골라보세요.", "sub": "마음에 드는 한 잔을 만나보세요", "start": 7.0, "end": 10.0},
]


def log(msg: str) -> None:
    print(f"   {msg}", flush=True)


def step(msg: str) -> None:
    print(f"\n▶ {msg}", flush=True)


def ok(msg: str) -> None:
    print(f"   ✅ {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"   ⚠️  {msg}", flush=True)


def fail(msg: str) -> None:
    print(f"   ❌ {msg}", flush=True)


def validate_mp4(path: Path) -> dict:
    info = {"exists": path.is_file(), "bytes": 0, "ftyp": False, "probe": None}
    if not info["exists"]:
        return info
    info["bytes"] = path.stat().st_size
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        info["ftyp"] = head[4:8] == b"ftyp"
    except Exception:
        pass
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        try:
            out = subprocess.run(
                [ffprobe, "-v", "error", "-show_entries",
                 "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
                 "-of", "json", str(path)],
                capture_output=True, text=True, timeout=20,
            )
            if out.returncode == 0:
                info["probe"] = json.loads(out.stdout or "{}")
        except Exception:
            pass
    return info


def describe_probe(probe: dict | None) -> str:
    if not probe:
        return "ffprobe 정보 없음"
    parts = []
    dur = (probe.get("format") or {}).get("duration")
    if dur:
        parts.append(f"{float(dur):.2f}s")
    for s in probe.get("streams") or []:
        if s.get("codec_type") == "video":
            parts.append(f"video={s.get('codec_name')} {s.get('width')}x{s.get('height')} @{s.get('r_frame_rate')}")
        elif s.get("codec_type") == "audio":
            parts.append(f"audio={s.get('codec_name')}")
    return ", ".join(parts) if parts else "스트림 정보 없음"


def load_recipes() -> list[Path]:
    if not SRC_BASKET.is_dir():
        return []
    files = list(SRC_BASKET.glob("trimmed_recipe_*.json"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def read_json(path: Path) -> dict:
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            with open(path, "r", encoding=enc) as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {"data": data}
        except Exception:
            continue
    return {}


def as_text(v) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, (list, tuple)):
        return ", ".join(as_text(x) for x in v if as_text(x))
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def find_key(obj, names: set[str]):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in names and as_text(v):
                return v
        for v in obj.values():
            r = find_key(v, names)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, names)
            if r is not None:
                return r
    return None


def extract_recipe_fields(recipe: dict) -> dict:
    firefly = ""
    af = recipe.get("adobe_firefly")
    if isinstance(af, dict):
        firefly = as_text(af.get("image_prompt_en"))
    if not firefly:
        firefly = as_text(find_key(recipe, {"image_prompt_en", "firefly_prompt", "firefly_prompt_en"}))

    express_names = {"template_keywords", "template_search", "template_search_keywords", "template_search_keywords_ko",
                     "search_keywords", "template_query", "keywords", "search_query", "template_keyword"}
    ex = recipe.get("adobe_express") if isinstance(recipe.get("adobe_express"), (dict, list)) else {}
    express = as_text(find_key(ex, express_names)) or as_text(find_key(recipe, express_names - {"keywords"}))

    pod = recipe.get("adobe_podcast") or recipe.get("adobe_podcast_enhance") or {}
    podcast = as_text(find_key(pod, {"tip", "guide", "instructions", "note", "steps", "how_to", "purpose"}))

    suno_obj = recipe.get("suno") or recipe.get("suno_ai") or recipe.get("suno_bgm") or recipe.get("suno_recipe") or {}
    suno = as_text(find_key(suno_obj, {"prompt", "prompt_en", "style", "style_prompt", "description", "style_of_music"}))
    if not suno:
        suno = as_text(find_key(recipe, {"suno_prompt", "suno_style"}))

    scenes = []
    raw = recipe.get("scenes") or recipe.get("scene_plan") or recipe.get("storyboard")
    if isinstance(raw, list):
        for i, s in enumerate(raw[:3]):
            if not isinstance(s, dict):
                continue
            title = as_text(s.get("headline") or s.get("title") or s.get("text") or s.get("caption") or s.get("copy")).replace("\n", " ")
            sub = as_text(s.get("sub") or s.get("subtitle") or s.get("narration") or s.get("voice") or s.get("vo"))
            if title:
                scenes.append({"index": i, "title": title[:60], "sub": sub[:80]})

    return {
        "topic": as_text(recipe.get("topic")) or "종이컵",
        "firefly_prompt": firefly or DEFAULT_FIREFLY_PROMPT,
        "express_keywords": express or DEFAULT_EXPRESS_KEYWORDS,
        "podcast_tip": podcast or DEFAULT_PODCAST_TIP,
        "suno_prompt": suno or DEFAULT_SUNO_PROMPT,
        "scenes": scenes,
    }


def discover_scenes(max_depth: int = 4) -> dict[int, Path]:
    found: dict[int, list[Path]] = {0: [], 1: [], 2: []}
    excluded = {(BASE_DIR / "dashboard" / BASKET_NAME).resolve(), (BASE_DIR / "docs" / BASKET_NAME).resolve()}

    def consider(p: Path):
        m = SCENE_RE.match(p.name)
        if m:
            found[int(m.group(1))].append(p)

    if SRC_BASKET.is_dir():
        for p in SRC_BASKET.iterdir():
            if p.is_file():
                consider(p)

    base_depth = len(BASE_DIR.parts)
    for root, dirs, files in os.walk(BASE_DIR):
        rp = Path(root)
        if len(rp.parts) - base_depth >= max_depth:
            dirs[:] = []
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and (rp / d).resolve() not in excluded]
        if rp.resolve() == SRC_BASKET.resolve():
            continue
        for fn in files:
            consider(rp / fn)

    result: dict[int, Path] = {}
    preferred = {0: "hook", 2: "cta"}
    for idx, lst in found.items():
        if not lst:
            continue
        in_basket = [p for p in lst if p.parent.resolve() == SRC_BASKET.resolve()]
        pool = in_basket or lst
        pref = [p for p in pool if idx in preferred and preferred[idx] in p.stem.lower()]
        pool = pref or pool
        pool.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        result[idx] = pool[0]
    return result


def same_file(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except Exception:
        return False


def copy_if_needed(src: Path, dst: Path) -> str:
    if same_file(src, dst):
        return "source"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        s, d = src.stat(), dst.stat()
        if s.st_size == d.st_size and int(d.st_mtime) >= int(s.st_mtime):
            return "up-to-date"
    shutil.copy2(src, dst)
    return "copied"


def build_manifest(build_id: str, mp4: Path, mp4_info: dict, recipes: list[Path], scenes: dict[int, Path]) -> dict:
    fields = extract_recipe_fields(read_json(recipes[0])) if recipes else extract_recipe_fields({})
    scene_list = []
    for base in DEFAULT_PAPER_SCENES:
        s = dict(base)
        override = next((x for x in fields["scenes"] if x["index"] == s["index"]), None)
        if override:
            s["title"] = override["title"] or s["title"]
            s["sub"] = override["sub"] or s["sub"]
        s["file"] = scenes[s["index"]].name if s["index"] in scenes else None
        scene_list.append(s)

    grok_recipes = []
    grok_file = SRC_BASKET / "grok_5_viral_recipes.json"
    if grok_file.is_file():
        try:
            grok_recipes = json.loads(grok_file.read_text(encoding="utf-8"))
        except Exception:
            grok_recipes = []

    return {
        "version": "v5",
        "build": build_id,
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "topic": fields["topic"],
        "video": MP4_NAME,
        "video_bytes": mp4_info.get("bytes", 0),
        "video_spec": "540x960 · 30fps · 10.0s · H.264/AAC",
        "voice": "InJoon (Korean voice actor)",
        "bgm": "62 BPM ducking BGM",
        "recipe_file": recipes[0].name if recipes else None,
        "recipes": [p.name for p in recipes],
        "scenes": scene_list,
        "grok_viral_styles": grok_recipes,
        "adobe": {
            "firefly_prompt": fields["firefly_prompt"],
            "firefly_url": "https://firefly.adobe.com",
            "express_keywords": fields["express_keywords"],
            "express_url": "https://new.express.adobe.com",
            "podcast_tip": fields["podcast_tip"],
            "podcast_url": "https://podcast.adobe.com/enhance",
        },
        "suno": {"prompt": fields["suno_prompt"]},
    }


def sync_basket(mp4: Path, recipes: list[Path], scenes: dict[int, Path], manifest: dict) -> None:
    grok_file = SRC_BASKET / "grok_5_viral_recipes.json"
    for target in BASKET_TARGETS:
        target.mkdir(parents=True, exist_ok=True)
        rel = target.relative_to(BASE_DIR).as_posix()
        results = [f"{MP4_NAME}:{copy_if_needed(mp4, target / MP4_NAME)}"]
        for r in recipes:
            results.append(f"{r.name}:{copy_if_needed(r, target / r.name)}")
        if grok_file.is_file():
            results.append(f"{grok_file.name}:{copy_if_needed(grok_file, target / grok_file.name)}")
        for idx in sorted(scenes):
            p = scenes[idx]
            results.append(f"{p.name}:{copy_if_needed(p, target / p.name)}")
        with open(target / MANIFEST_NAME, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        results.append(f"{MANIFEST_NAME}:written")
        ok(f"{rel}/  →  " + " | ".join(results))


V5_BLOCK_TEMPLATE = r"""<!-- SHIN_AD_V5_START -->
<style id="shin-ad-v5-style">
#shinAdV5Modal{position:fixed;inset:0;z-index:2147483640;display:flex;align-items:center;justify-content:center;background:rgba(5,7,18,.84);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);font-family:'Pretendard','Noto Sans KR','Malgun Gothic',system-ui,sans-serif;color:#e9ecff}
#shinAdV5Modal *{box-sizing:border-box}
#shinAdV5Modal .v5-card{position:relative;width:min(1200px,96vw);max-height:94vh;overflow:auto;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:18px;padding:22px;border-radius:20px;background:linear-gradient(155deg,#151b36 0%,#0b0f20 100%);border:1px solid #2e3a70;box-shadow:0 30px 90px rgba(0,0,0,.65)}
@media (max-width:880px){#shinAdV5Modal .v5-card{grid-template-columns:1fr}}
#shinAdV5Modal .v5-close{position:absolute;top:12px;right:14px;width:36px;height:36px;border-radius:50%;border:1px solid #3a4680;background:#1b2347;color:#fff;font-size:18px;cursor:pointer;z-index:2}
#shinAdV5Modal .v5-h{margin:6px 0 4px;font-size:20px;font-weight:800;line-height:1.35}
#shinAdV5Modal .v5-badge{display:inline-block;padding:3px 9px;border-radius:999px;background:#253067;color:#9fb4ff;font-size:11px;margin-right:6px}
#shinAdV5Modal .v5-sec{background:rgba(255,255,255,.035);border:1px solid #27315f;border-radius:14px;padding:12px 14px;margin-top:12px}
#shinAdV5Modal .v5-sec h4{margin:0 0 8px;font-size:13px;color:#a9b8ff}
#shinAdV5Modal .v5-scene{display:flex;gap:10px;align-items:center;padding:6px 0;border-bottom:1px dashed #2a3463}
#shinAdV5Modal .v5-scene:last-child{border-bottom:0}
#shinAdV5Modal .v5-scene img,#shinAdV5Modal .v5-scene .ph{width:54px;height:96px;object-fit:cover;border-radius:8px;background:#222a52;flex:0 0 auto}
#shinAdV5Modal .v5-scene .t{font-weight:700;font-size:13px}
#shinAdV5Modal .v5-scene .s{font-size:12px;color:#aab3d9}
#shinAdV5Modal .v5-scene .tm{font-size:11px;color:#7f8bc0}
#shinAdV5Modal .v5-pre{white-space:pre-wrap;word-break:break-word;font-size:12px;line-height:1.5;background:#0a0e1c;border:1px solid #232c57;border-radius:10px;padding:8px 10px;color:#cfd7ff;max-height:120px;overflow:auto;margin:0;font-family:inherit}
.v5-btn{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;padding:11px 14px;margin-top:8px;border:0;border-radius:12px;font-weight:700;font-size:14px;cursor:pointer;color:#fff !important;text-decoration:none !important;transition:transform .08s,filter .15s;font-family:inherit;line-height:1.3;text-align:center}
.v5-btn:hover{filter:brightness(1.12)}
.v5-btn:active{transform:scale(.98)}
.v5-btn[disabled]{opacity:.6;cursor:wait}
.v5-dl{background:linear-gradient(90deg,#00a862,#00d4a0);font-size:15px;padding:14px;margin-top:0}
.v5-dl.missing{background:#4a4f66}
.v5-play{background:linear-gradient(90deg,#ff3d6e,#ff8a3d)}
.v5-firefly{background:linear-gradient(90deg,#e8341c,#ff6a3d)}
.v5-express{background:linear-gradient(90deg,#5c2bd8,#c23ee0)}
.v5-podcast{background:linear-gradient(90deg,#1473e6,#2fa8ff)}
.v5-sub{background:#27315f}
#shinAdV5Modal .v5-tabs{display:flex;gap:6px;margin-top:10px}
#shinAdV5Modal .v5-tab{flex:1;padding:9px;border-radius:10px;border:1px solid #33407a;background:#151c3b;color:#c5cdf5;font-weight:700;font-size:13px;cursor:pointer;font-family:inherit}
#shinAdV5Modal .v5-tab.on{background:#3346a8;color:#fff;border-color:#4d62d6}
#shinAdV5Modal .v5-stage{margin-top:10px;display:flex;justify-content:center;background:#000;border-radius:14px;overflow:hidden}
#shinAdV5Modal .v5-stage video,#shinAdV5Modal .v5-stage canvas{display:block;height:min(60vh,620px);width:auto;aspect-ratio:9/16;max-width:100%;background:#000}
#shinAdV5Modal .v5-row{display:flex;gap:8px}
#shinAdV5Modal .v5-row .v5-btn{flex:1}
#shinAdV5Modal .v5-note{display:block;font-size:11.5px;color:#8f9ad0;margin-top:6px;line-height:1.5}
#shinAdV5Toast{position:fixed;left:50%;bottom:36px;transform:translateX(-50%);z-index:2147483647;background:#111833;color:#fff;border:1px solid #4357c9;padding:11px 18px;border-radius:12px;font-size:13.5px;box-shadow:0 10px 30px rgba(0,0,0,.5);opacity:0;transition:opacity .25s;pointer-events:none;max-width:90vw;font-family:'Pretendard','Noto Sans KR','Malgun Gothic',system-ui,sans-serif}
#shinAdV5Toast.on{opacity:1}
.v5-panel-adobe{margin-top:10px;padding:10px;border:1px solid #2e3a70;border-radius:12px;background:rgba(20,26,54,.6)}
.v5-panel-adobe .v5-btn{font-size:13px;padding:9px 12px}
</style>
<script id="shin-ad-v5-script">
(function(){
'use strict';
if(window.__SHIN_AD_V5__)return;
window.__SHIN_AD_V5__=true;

var BUILD='__BUILD_ID__';
var MANIFEST=__MANIFEST_JSON__;
var MP4=MANIFEST.video||'trimmed_ad_paper_cup_10s.mp4';
var CANDS=['/ingredients_basket/','ingredients_basket/','../ingredients_basket/'];
var basePromise=null;
var lastTopic='종이컵';
var lastOpen=0;
var timers=[];
var engine=null;
var previewAC=null;

(function(){
 try{
  var k='shin_ad_v5_build';
  if(localStorage.getItem(k)!==BUILD){
   localStorage.setItem(k,BUILD);
   if(window.caches&&caches.keys){caches.keys().then(function(ks){ks.forEach(function(x){caches.delete(x);});});}
  }
  if('serviceWorker' in navigator){
   navigator.serviceWorker.getRegistrations().then(function(rs){rs.forEach(function(r){try{r.update();}catch(e){}});});
   navigator.serviceWorker.addEventListener('message',function(e){if(e.data&&e.data.type==='SHIN_SW_RESET'){console.log('[SHIN v5] SW cache reset',e.data.build);}});
  }
 }catch(e){}
})();

function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function safeName(s){return String(s||'ad').replace(/[\\\/:*?"<>|\s]+/g,'_').slice(0,40)||'ad';}
function isPaperCup(t){return /종이컵|종이\s*컵|paper\s*cup/i.test(String(t||''));}

function resolveBase(){
 if(basePromise)return basePromise;
 basePromise=(async function(){
  for(var i=0;i<CANDS.length;i++){
   try{
    var r=await fetch(CANDS[i]+'v5_manifest.json?v='+BUILD,{cache:'no-store'});
    if(r.ok){
     try{var j=await r.json();if(j&&j.video){MANIFEST=Object.assign({},MANIFEST,j);MP4=MANIFEST.video||MP4;}}catch(e){}
     return CANDS[i];
    }
   }catch(e){}
  }
  return CANDS[0];
 })();
 return basePromise;
}

function toast(msg,ms){
 var t=document.getElementById('shinAdV5Toast');
 if(!t){t=document.createElement('div');t.id='shinAdV5Toast';document.body.appendChild(t);}
 t.textContent=msg;t.classList.add('on');
 clearTimeout(t._h);t._h=setTimeout(function(){t.classList.remove('on');},ms||2600);
}

function copyText(text){
 var ok=false;
 try{
  var ta=document.createElement('textarea');
  ta.value=text;ta.setAttribute('readonly','');
  ta.style.cssText='position:fixed;top:-1000px;left:-1000px;opacity:0;';
  document.body.appendChild(ta);ta.select();
  ok=document.execCommand('copy');ta.remove();
 }catch(e){}
 try{
  if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(text).catch(function(){});ok=true;}
 }catch(e){}
 return ok;
}

var ADOBE={
 firefly:function(){
  var a=MANIFEST.adobe||{};
  var ok=copyText(a.firefly_prompt||'');
  toast(ok?'✅ Firefly 실사 프롬프트 복사 완료! 새 탭 프롬프트 창에 Ctrl+V 하세요.':'⚠️ 자동 복사 실패: 모달의 프롬프트를 직접 복사해 주세요.',4000);
  window.open(a.firefly_url||'https://firefly.adobe.com','_blank','noopener');
 },
 express:function(){
  var a=MANIFEST.adobe||{};
  var ok=copyText(a.express_keywords||'');
  toast(ok?'✅ Express 쇼츠 템플릿 검색어 복사 완료! 템플릿 검색창에 Ctrl+V 하세요.':'⚠️ 자동 복사 실패: 검색어를 직접 복사해 주세요.',4000);
  window.open(a.express_url||'https://new.express.adobe.com','_blank','noopener');
 },
 podcast:function(){
  var a=MANIFEST.adobe||{};
  toast('🎙️ Adobe Podcast Enhance: '+(a.podcast_tip||'성우 음성을 올리면 무료로 음질이 보정됩니다.'),4200);
  window.open(a.podcast_url||'https://podcast.adobe.com/enhance','_blank','noopener');
 }
};
function adobeButtons(){
 return '<button type="button" class="v5-btn v5-firefly" data-v5-adobe="firefly">🎨 Adobe Firefly 열기 + 실사 프롬프트 자동복사</button>'+
        '<button type="button" class="v5-btn v5-express" data-v5-adobe="express">✨ Adobe Express 열기 + 쇼츠 템플릿 검색어 복사</button>'+
        '<button type="button" class="v5-btn v5-podcast" data-v5-adobe="podcast">🎙️ Adobe Podcast 열기 (무료 성우 음질 보정)</button>';
}
document.addEventListener('click',function(e){
 var t=e.target;if(!t||!t.closest)return;
 var b=t.closest('[data-v5-adobe]');
 if(b){e.preventDefault();e.stopPropagation();var k=b.getAttribute('data-v5-adobe');if(ADOBE[k])ADOBE[k]();return;}
 var o=t.closest('[data-v5-open-studio]');
 if(o){e.preventDefault();e.stopPropagation();openModal(lastTopic||'종이컵');}
},true);

function scenesFor(topic){
 if(isPaperCup(topic)&&MANIFEST.scenes&&MANIFEST.scenes.length)return MANIFEST.scenes;
 return [
  {index:0,key:'hook',title:topic+', 아직도 고민 중이세요?',sub:'10초면 충분합니다',start:0,end:3,file:null},
  {index:1,key:'benefit',title:'차원이 다른 '+topic,sub:'한 번 써보면 바로 알게 됩니다',start:3,end:7,file:null},
  {index:2,key:'cta',title:'지금 바로 만나보세요',sub:topic+' · 오늘 주문하면 내일 도착',start:7,end:10,file:null}
 ];
}

function makeBgm(ac,dest,dur){
 var beat=60/62,t0=ac.currentTime+0.05,barDur=beat*4;
 var master=ac.createGain();master.gain.value=0.5;master.connect(dest);
 var chords=[[220,277.18,329.63],[196,246.94,293.66],[174.61,220,261.63],[196,246.94,293.66]];
 for(var b=0;b*barDur<dur;b++){
  (function(b){
   var st=t0+b*barDur,en=t0+Math.min(dur,(b+1)*barDur);
   chords[b%4].forEach(function(f){
    var o=ac.createOscillator(),g=ac.createGain();
    o.type='triangle';o.frequency.value=f;
    g.gain.setValueAtTime(0,st);g.gain.linearRampToValueAtTime(0.06,st+0.3);g.gain.linearRampToValueAtTime(0,en);
    o.connect(g);g.connect(master);o.start(st);o.stop(en+0.05);
   });
  })(b);
 }
 for(var k=0;k*beat<dur;k++){
  var o=ac.createOscillator(),g=ac.createGain(),st=t0+k*beat;
  o.frequency.setValueAtTime(120,st);o.frequency.exponentialRampToValueAtTime(40,st+0.18);
  g.gain.setValueAtTime(0.45,st);g.gain.exponentialRampToValueAtTime(0.001,st+0.22);
  o.connect(g);g.connect(master);o.start(st);o.stop(st+0.25);
 }
 master.gain.setValueAtTime(0.5,t0+Math.max(0,dur-0.8));
 master.gain.linearRampToValueAtTime(0,t0+dur);
 return master;
}

function wrapText(ctx,text,maxW){
 var out=[];
 String(text||'').split('\n').forEach(function(para){
  var line='';
  para.split('').forEach(function(ch){
   var test=line+ch;
   if(ctx.measureText(test).width>maxW&&line){out.push(line);line=ch.trim()?ch:'';}
   else line=test;
  });
  if(line)out.push(line);
 });
 return out.slice(0,3);
}
function makeEngine(canvas,scenes,topic,base){
 var ctx=canvas.getContext('2d'),W=540,H=960,DUR=10,raf=0,running=false;
 var FONT='"Pretendard","Noto Sans KR","Malgun Gothic",sans-serif';
 var pal=[['#1b1f3b','#ff5f6d'],['#0f2027','#2c5364'],['#232526','#f7971e']];
 var imgs=scenes.map(function(s){
  if(!s.file)return null;
  var im=new Image();im.onload=function(){if(!running)draw(0);};
  im.src=base+encodeURIComponent(s.file);return im;
 });
 function sceneAt(t){for(var i=0;i<scenes.length;i++){if(t<scenes[i].end)return i;}return scenes.length-1;}
 function draw(t){
  var i=sceneAt(t),s=scenes[i],local=(t-s.start)/Math.max(0.001,s.end-s.start);
  ctx.save();ctx.clearRect(0,0,W,H);
  var im=imgs[i];
  if(im&&im.complete&&im.naturalWidth){
   var sc=Math.max(W/im.naturalWidth,H/im.naturalHeight)*(1.04+0.06*local);
   var dw=im.naturalWidth*sc,dh=im.naturalHeight*sc;
   ctx.drawImage(im,(W-dw)/2,(H-dh)/2,dw,dh);
  }else{
   var p=pal[i%3],g=ctx.createLinearGradient(0,0,W,H);
   g.addColorStop(0,p[0]);g.addColorStop(1,p[1]);ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
   ctx.globalAlpha=0.15;ctx.fillStyle='#fff';
   ctx.beginPath();ctx.arc(W*0.78,H*0.22+40*Math.sin(t*2),120,0,Math.PI*2);ctx.fill();
   ctx.beginPath();ctx.arc(W*0.18,H*0.42+30*Math.cos(t*1.6),70,0,Math.PI*2);ctx.fill();
   ctx.globalAlpha=1;
  }
  var sh=ctx.createLinearGradient(0,H*0.45,0,H);
  sh.addColorStop(0,'rgba(0,0,0,0)');sh.addColorStop(1,'rgba(0,0,0,.8)');
  ctx.fillStyle=sh;ctx.fillRect(0,0,W,H);
  var a=Math.min(1,local*4),y=H*0.68+(1-a)*40;
  ctx.globalAlpha=a;ctx.textAlign='center';ctx.shadowColor='rgba(0,0,0,.6)';ctx.shadowBlur=12;
  ctx.font='900 46px '+FONT;ctx.fillStyle='#fff';
  var lines=wrapText(ctx,s.title,W-70);
  lines.forEach(function(ln,k){ctx.fillText(ln,W/2,y+k*56);});
  ctx.font='600 26px '+FONT;ctx.fillStyle='#ffe08a';
  wrapText(ctx,s.sub,W-80).forEach(function(ln,k){ctx.fillText(ln,W/2,y+lines.length*56+14+k*34);});
  ctx.globalAlpha=1;ctx.shadowBlur=0;
  ctx.font='700 18px '+FONT;ctx.fillStyle='rgba(255,255,255,.88)';ctx.textAlign='left';
  ctx.fillText('#'+topic+'  ·  10s AD',24,44);
  ctx.fillStyle='rgba(255,255,255,.25)';ctx.fillRect(0,H-8,W,8);
  ctx.fillStyle='#ff4d6d';ctx.fillRect(0,H-8,W*Math.min(1,t/DUR),8);
  ctx.restore();
 }
 function run(onEnd){
  cancelAnimationFrame(raf);running=true;var t0=performance.now();
  (function loop(){
   var t=(performance.now()-t0)/1000;
   if(t>=DUR){draw(DUR-0.001);running=false;if(onEnd)onEnd();return;}
   draw(t);raf=requestAnimationFrame(loop);
  })();
 }
 function stop(){cancelAnimationFrame(raf);running=false;}
 draw(0);
 return {canvas:canvas,draw:draw,run:run,stop:stop,DUR:DUR};
}

function clearTimers(){timers.forEach(function(h){clearTimeout(h);});timers=[];}

function previewCanvas(scenes,useTts){
 if(!engine)return;
 clearTimers();
 try{speechSynthesis.cancel();}catch(e){}
 try{if(previewAC)previewAC.close();}catch(e){}
 try{var AC=window.AudioContext||window.webkitAudioContext;previewAC=new AC();makeBgm(previewAC,previewAC.destination,engine.DUR);}catch(e){previewAC=null;}
 engine.run(function(){try{if(previewAC)previewAC.close();}catch(e){}previewAC=null;});
 if(!useTts||!window.speechSynthesis)return;
 scenes.forEach(function(s){
  timers.push(setTimeout(function(){
   var u=new SpeechSynthesisUtterance(s.title+'. '+(s.sub||''));
   u.lang='ko-KR';u.rate=1.15;
   var vs=speechSynthesis.getVoices().filter(function(v){return /ko/i.test(v.lang);});
   if(vs.length)u.voice=vs[0];
   speechSynthesis.speak(u);
  },s.start*1000));
 });
}

function recordWebm(topic,btn){
 if(!engine)return;
 if(!window.MediaRecorder||!HTMLCanvasElement.prototype.captureStream){toast('⚠️ 이 브라우저는 Canvas 녹화를 지원하지 않습니다.');return;}
 var orig=btn.textContent;
 var vs=engine.canvas.captureStream(30);
 var ac=null,dest=null;
 try{
  var AC=window.AudioContext||window.webkitAudioContext;ac=new AC();
  dest=ac.createMediaStreamDestination();
  var mix=ac.createGain();mix.connect(dest);mix.connect(ac.destination);
  makeBgm(ac,mix,engine.DUR);
 }catch(e){ac=null;dest=null;}
 var tracks=vs.getVideoTracks().slice();
 if(dest)tracks=tracks.concat(dest.stream.getAudioTracks());
 var stream=new MediaStream(tracks);
 var types=['video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus','video/webm'],mime='';
 for(var i=0;i<types.length;i++){if(MediaRecorder.isTypeSupported(types[i])){mime=types[i];break;}}
 var rec;
 try{rec=new MediaRecorder(stream,mime?{mimeType:mime,videoBitsPerSecond:4000000}:{});}
 catch(e){toast('⚠️ MediaRecorder 생성 실패: '+e.message);return;}
 var chunks=[];
 rec.ondataavailable=function(e){if(e.data&&e.data.size)chunks.push(e.data);};
 rec.onstop=function(){
  var blob=new Blob(chunks,{type:'video/webm'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download='ad_'+safeName(topic)+'_10s.webm';
  document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},5000);
  try{if(ac)ac.close();}catch(e){}
  btn.disabled=false;btn.textContent=orig;
  toast('✅ 10초 WebM 저장 완료 ('+Math.round(blob.size/1024)+' KB)');
 };
 btn.disabled=true;btn.textContent='⏺ 녹화 중... (10초)';
 rec.start(250);
 engine.run(function(){setTimeout(function(){if(rec.state!=='inactive')rec.stop();},150);});
}

var suppressObs=null;
function hideForeign(el){
 if(!el||el.nodeType!==1||el.id==='shinAdV5Modal'||el.id==='shinAdV5Toast')return;
 try{
  var cs=getComputedStyle(el),z=parseInt(cs.zIndex,10);
  if(cs.position==='fixed'&&z>=2147483000){el.setAttribute('data-v5-hidden','1');el.style.setProperty('display','none','important');}
 }catch(e){}
}
function suppressOthers(on){
 if(on){
  Array.prototype.forEach.call(document.body.children,hideForeign);
  if(!suppressObs)suppressObs=new MutationObserver(function(ms){ms.forEach(function(m){m.addedNodes.forEach(hideForeign);});});
  suppressObs.observe(document.body,{childList:true});
 }else{
  if(suppressObs)suppressObs.disconnect();
  document.querySelectorAll('[data-v5-hidden]').forEach(function(el){
   if(/광고|스튜디오|studio/i.test(el.textContent||''))el.remove();
   else{el.removeAttribute('data-v5-hidden');el.style.removeProperty('display');}
  });
 }
}

function closeModal(){
 var m=document.getElementById('shinAdV5Modal');
 clearTimers();
 try{speechSynthesis.cancel();}catch(e){}
 try{if(previewAC)previewAC.close();}catch(e){}
 previewAC=null;
 if(engine){engine.stop();engine=null;}
 if(m){var v=m.querySelector('video');if(v){try{v.pause();}catch(e){}}m.remove();}
 suppressOthers(false);
 document.removeEventListener('keydown',escHandler,true);
}
function escHandler(e){if(e.key==='Escape'){e.stopPropagation();closeModal();}}

async function openModal(topic){
 var now=Date.now();if(now-lastOpen<800)return;lastOpen=now;
 topic=String(topic||'종이컵').trim()||'종이컵';lastTopic=topic;
 var base=await resolveBase();
 closeModal();suppressOthers(true);
 var paper=isPaperCup(topic),scenes=scenesFor(topic),a=MANIFEST.adobe||{},suno=MANIFEST.suno||{};
 var mp4Src=base+encodeURIComponent(MP4)+'?v='+BUILD;
 var mp4Dl=base+encodeURIComponent(MP4);
 var s0=(MANIFEST.scenes||[])[0];
 var poster=(s0&&s0.file)?base+encodeURIComponent(s0.file):'';
 var sceneHtml=scenes.map(function(s){
  var img=s.file?'<img src="'+esc(base+encodeURIComponent(s.file))+'" alt="">':'<div class="ph"></div>';
  return '<div class="v5-scene">'+img+'<div><div class="tm">'+esc(s.start)+'s ~ '+esc(s.end)+'s · '+esc((s.key||'scene').toUpperCase())+'</div><div class="t">'+esc(s.title)+'</div><div class="s">'+esc(s.sub)+'</div></div></div>';
 }).join('');
 var m=document.createElement('div');
 m.id='shinAdV5Modal';
 m.innerHTML=
 '<div class="v5-card" role="dialog" aria-modal="true">'+
  '<button type="button" class="v5-close" data-v5-close title="닫기 (Esc)">✕</button>'+
  '<div class="v5-left">'+
   '<div><span class="v5-badge">STUDIO v5</span><span class="v5-badge">'+esc(BUILD)+'</span></div>'+
   '<h3 class="v5-h">🎬 10초 광고 스튜디오: 「'+esc(topic)+'」</h3>'+
   '<span class="v5-note">'+esc(MANIFEST.voice||'InJoon')+' 실제 성우 · '+esc(MANIFEST.bgm||'62 BPM ducking BGM')+' · 실사 타이포그래피 · '+esc(MANIFEST.video_spec||'540x960 · 30fps · 10.0s')+'</span>'+
   '<div class="v5-sec"><h4>🎞️ 3씬 구성 (Hook → Benefit → CTA)</h4>'+sceneHtml+'</div>'+
   '<div class="v5-sec"><h4>🎨 Adobe Firefly 실사 프롬프트 (EN)</h4><pre class="v5-pre">'+esc(a.firefly_prompt)+'</pre></div>'+
   '<div class="v5-sec"><h4>✨ Adobe Express 쇼츠 템플릿 검색어</h4><pre class="v5-pre">'+esc(a.express_keywords)+'</pre></div>'+
   '<div class="v5-sec"><h4>🎵 Suno BGM 레시피</h4><pre class="v5-pre">'+esc(suno.prompt)+'</pre>'+
    (MANIFEST.recipe_file?'<span class="v5-note">📄 레시피: '+esc(MANIFEST.recipe_file)+'</span>':'')+'</div>'+
   '<div class="v5-sec"><h4>🅰️ Adobe 무료 3대장 직통</h4>'+adobeButtons()+'</div>'+
  '</div>'+
  '<div class="v5-right">'+
   '<a class="v5-btn v5-dl" data-v5-dl href="'+esc(mp4Dl)+'" download="'+esc(MP4)+'">💾 성우 음성 포함 10초 광고 MP4 즉시 다운로드 ('+esc(MP4)+')</a>'+
   (paper?'':'<span class="v5-note">※ 완성본 MP4는 「종이컵」 주제로 제작된 결과물입니다. 「'+esc(topic)+'」 주제는 아래 [실시간 Canvas 3씬 + WebM] 탭에서 바로 생성할 수 있습니다.</span>')+
   '<button type="button" class="v5-btn v5-play" data-v5-playmp4>🎬 실제 성우+BGM+실사 합체 완성본 MP4 바로 재생</button>'+
   '<div class="v5-tabs"><button type="button" class="v5-tab" data-v5-tab="mp4">🎬 완성본 MP4</button><button type="button" class="v5-tab" data-v5-tab="canvas">🖼️ 실시간 Canvas 3씬 + WebM</button></div>'+
   '<div data-v5-pane="mp4">'+
    '<div class="v5-stage"><video id="shinAdV5Video" controls playsinline preload="auto"'+(poster?' poster="'+esc(poster)+'"':'')+' src="'+esc(mp4Src)+'"></video></div>'+
    '<span class="v5-note" data-v5-vnote>▶ 재생하면 브라우저 TTS가 아닌 실제 녹음된 InJoon 성우 목소리와 62BPM 덕킹 BGM이 소리와 함께 재생됩니다.</span>'+
   '</div>'+
   '<div data-v5-pane="canvas" style="display:none">'+
    '<div class="v5-stage"><canvas id="shinAdV5Canvas" width="540" height="960"></canvas></div>'+
    '<div class="v5-row"><button type="button" class="v5-btn v5-sub" data-v5-cv-preview>▶ 3씬 미리보기 (+BGM/TTS)</button><button type="button" class="v5-btn v5-sub" data-v5-cv-record>⏺ 10초 WebM 녹화·다운로드</button></div>'+
    '<label class="v5-note"><input type="checkbox" id="shinAdV5Tts" checked> 미리보기 때 브라우저 TTS 내레이션 사용 (녹화 파일에는 62BPM BGM만 들어갑니다)</label>'+
   '</div>'+
  '</div>'+
 '</div>';
 document.body.appendChild(m);
 document.addEventListener('keydown',escHandler,true);

 var video=m.querySelector('#shinAdV5Video');
 var canvas=m.querySelector('#shinAdV5Canvas');
 var dl=m.querySelector('[data-v5-dl]');

 function showTab(name){
  m.querySelectorAll('[data-v5-tab]').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-v5-tab')===name);});
  m.querySelectorAll('[data-v5-pane]').forEach(function(p){p.style.display=p.getAttribute('data-v5-pane')===name?'':'none';});
  if(name==='canvas'){if(!engine)engine=makeEngine(canvas,scenes,topic,base);try{video.pause();}catch(e){}}
  else if(engine){engine.stop();try{speechSynthesis.cancel();}catch(e){}}
 }

 m.addEventListener('click',function(e){
  var t=e.target;
  if(t===m||(t.closest&&t.closest('[data-v5-close]'))){closeModal();return;}
  var tab=t.closest&&t.closest('[data-v5-tab]');
  if(tab){showTab(tab.getAttribute('data-v5-tab'));return;}
  if(t.closest&&t.closest('[data-v5-playmp4]')){
   showTab('mp4');
   try{video.currentTime=0;}catch(err){}
   video.muted=false;video.volume=1;
   var p=video.play();
   if(p&&p.then){p.then(function(){toast('🔊 InJoon 성우 + 62BPM BGM 완성본 재생 중');}).catch(function(){toast('▶ 플레이어의 재생 버튼을 한 번 눌러 주세요.');});}
   return;
  }
  if(t.closest&&t.closest('[data-v5-cv-preview]')){previewCanvas(scenes,m.querySelector('#shinAdV5Tts').checked);return;}
  var rb=t.closest&&t.closest('[data-v5-cv-record]');
  if(rb){recordWebm(topic,rb);return;}
  if(t.closest&&t.closest('[data-v5-dl]')){
   if(dl.classList.contains('missing')){e.preventDefault();toast('⚠️ MP4 파일을 찾을 수 없습니다.',4200);return;}
   toast('💾 '+MP4+' 다운로드 시작!');
  }
 });

 video.addEventListener('error',function(){
  var n=m.querySelector('[data-v5-vnote]');
  if(n)n.textContent='⚠️ MP4 로드 실패: '+mp4Src+' 경로를 확인해 주세요.';
 });

 fetch(mp4Dl,{method:'HEAD',cache:'no-store'}).then(function(r){
  if(!r.ok){dl.classList.add('missing');dl.textContent='⚠️ 완성본 MP4 없음';}
 }).catch(function(){});

 showTab(paper?'mp4':'canvas');
 if(paper){video.muted=false;var pp=video.play();if(pp&&pp.catch)pp.catch(function(){});}
}

/* ── v4 RGON_AD_STUDIO 연동: 전송 시 v5 모달도 즉시 오픈 ── */
window.addEventListener('rgon:ad-generated',function(e){
 var tp=(e&&e.detail&&e.detail.topic)||'종이컵';
 setTimeout(function(){openModal(tp);},80);
});

function isAdRequest(t){
 t=String(t||'');
 return (/광고/.test(t)&&/(만들|제작|생성|뽑아|짜\s*줘|해\s*줘|부탁|주제)/.test(t))||/\d+\s*초\s*(짜리\s*)?광고/.test(t)||/광고\s*(영상|쇼츠|만들기)/.test(t);
}
function extractTopic(t){
 t=String(t||'');
 var m=t.match(/주제\s*(?:는|은|:|=)?\s*["'「『]?([^"'」』,.!?\n]+?)["'」』]?\s*(?:$|[,.!?\n]|으로|로\s|입니다|이야|야$|요$)/);
 if(m&&m[1].trim())return m[1].trim().slice(0,30);
 m=t.match(/([가-힣A-Za-z0-9 ]{1,24}?)\s*(?:의\s*)?(?:10\s*초\s*)?광고/);
 if(m){
  var c=m[1].replace(/간단한|간단하게|짧은|\d+\s*초|짜리|영상|만들기/g,' ').trim();
  if(c)return c.split(/\s+/).pop();
 }
 return '종이컵';
}
var lastTyped='';
function trigger(text){
 if(!isAdRequest(text))return false;
 var tp=extractTopic(text);
 setTimeout(function(){openModal(tp);},120);
 return true;
}
document.addEventListener('input',function(e){
 var el=e.target;if(!el||(el.closest&&el.closest('#shinAdV5Modal')))return;
 if(el.tagName==='TEXTAREA'||(el.tagName==='INPUT'&&/^(text|search)$/i.test(el.type||'text'))){lastTyped=el.value;}
 else if(el.isContentEditable){lastTyped=el.innerText;}
},true);
document.addEventListener('keydown',function(e){
 if(e.key!=='Enter'||e.shiftKey)return;
 var el=e.target;if(!el||(el.closest&&el.closest('#shinAdV5Modal')))return;
 if(el.tagName==='TEXTAREA'||el.tagName==='INPUT'||el.isContentEditable){
  if(trigger(el.value!=null?el.value:el.innerText))lastTyped='';
 }
},true);
document.addEventListener('click',function(e){
 var t=e.target;if(!t||!t.closest)return;
 var b=t.closest('button,[role="button"],input[type="submit"]');
 if(!b||b.closest('#shinAdV5Modal')||b.hasAttribute('data-v5-adobe')||b.hasAttribute('data-v5-open-studio'))return;
 var cls=typeof b.className==='string'?b.className:'';
 var label=(b.id+' '+cls+' '+(b.getAttribute('aria-label')||'')+' '+(b.title||'')+' '+(b.textContent||'')).toLowerCase();
 if((/send|submit|전송|보내|실행/.test(label)||b.type==='submit')&&lastTyped){if(trigger(lastTyped))lastTyped='';}
},true);

function injectPanel(){
 try{
  var xp=document.evaluate("//*[contains(normalize-space(text()),'한마디 올인원') or contains(normalize-space(text()),'실전 지휘 패널')]",document.body,null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);
  for(var i=0;i<xp.snapshotLength;i++){
   var el=xp.snapshotItem(i);
   if(!el||!el.closest||el.closest('#shinAdV5Modal')||el.closest('[data-v5-panel-adobe]'))continue;
   if(/^(SCRIPT|STYLE|TEXTAREA|TITLE|OPTION|BUTTON|A|INPUT|LABEL)$/.test(el.tagName))continue;
   var host=el.closest('#rgon-clean-aside-modal,[class*="panel"],[id*="panel"],section,aside,details,.card,[role="dialog"]')||el.parentElement;
   if(!host||host===document.body||host.querySelector('[data-v5-panel-adobe]'))continue;
   var box=document.createElement('div');
   box.className='v5-panel-adobe';box.setAttribute('data-v5-panel-adobe','1');
   box.innerHTML='<div style="font-size:12px;font-weight:800;color:#a9b8ff;margin-bottom:2px">🅰️ Adobe 무료 3대장 직통 (v5)</div>'+adobeButtons()+
    '<button type="button" class="v5-btn v5-play" data-v5-open-studio>🎬 10초 광고 스튜디오 v5 열기 (완성본 MP4)</button>';
   host.appendChild(box);
  }
 }catch(e){}
}
var injT=0;
function scheduleInject(){clearTimeout(injT);injT=setTimeout(injectPanel,400);}
function init(){
 resolveBase();
 injectPanel();
 try{new MutationObserver(scheduleInject).observe(document.body,{childList:true,subtree:true});}catch(e){}
 console.log('[SHIN v5] 10초 광고 스튜디오 v5 준비 완료 · build',BUILD);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();

window.openShinAdStudioV5=openModal;
window.openAdStudioModal=openModal;
window.shinAdV5={open:openModal,close:closeModal,manifest:function(){return MANIFEST;},build:BUILD,adobe:ADOBE};
})();
</script>
<!-- SHIN_AD_V5_END -->"""


SW_TEMPLATE = r"""// SHIN service worker: v5 cache reset worker (build __BUILD_ID__)
const BUILD = '__BUILD_ID__';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((k) => caches.delete(k)));
    await self.clients.claim();
    const clients = await self.clients.matchAll({ type: 'window' });
    clients.forEach((c) => c.postMessage({ type: 'SHIN_SW_RESET', build: BUILD }));
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.headers.has('range')) return;
  if (url.pathname.includes('/ingredients_basket/')) return;
  if (/\.(mp4|webm|mp3|wav|m4a|ogg|jpg|jpeg|png|webp|gif|json)$/i.test(url.pathname)) return;
  if (req.mode === 'navigate' || /\.html?$/i.test(url.pathname)) {
    event.respondWith(fetch(req, { cache: 'no-store' }).catch(() => caches.match(req)));
  }
});
"""


def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return raw.decode(enc), ("utf-8" if enc.startswith("utf-8") else enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8"


def render_block(build_id: str, manifest: dict) -> str:
    mjson = (json.dumps(manifest, ensure_ascii=False)
             .replace("</", "<\\/")
             .replace("\u2028", "\\u2028")
             .replace("\u2029", "\\u2029"))
    return V5_BLOCK_TEMPLATE.replace("__BUILD_ID__", build_id).replace("__MANIFEST_JSON__", mjson)


def ensure_html_targets() -> None:
    existing = [p for p in HTML_TARGETS if p.is_file()]
    if not existing:
        raise SystemExit("❌ rgon_alpha_chat.html을 하나도 찾지 못했습니다.")
    src = existing[0]
    for p in HTML_TARGETS:
        if not p.is_file():
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, p)


def patch_html(path: Path, block: str, build_id: str, ts: str) -> None:
    text, enc = read_text(path)
    backup = path.with_name(f"{path.name}.bak_v5_{ts}")
    shutil.copy2(path, backup)

    text = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END) + r"\s*", "", text, flags=re.S)
    text = re.sub(
        r"""(register\(\s*['"])([^'"]*?sw\.js)(\?[^'"]*)?(['"])""",
        lambda m: f"{m.group(1)}{m.group(2)}?v={build_id}{m.group(4)}",
        text,
    )
    idx = text.lower().rfind("</body>")
    if idx == -1:
        text = text.rstrip() + "\n" + block + "\n"
    else:
        text = text[:idx] + block + "\n" + text[idx:]

    with open(path, "w", encoding=enc, newline="") as f:
        f.write(text)
    ok(f"{path.relative_to(BASE_DIR).as_posix()} 패치 완료")


def write_sw(build_id: str, ts: str) -> None:
    content = SW_TEMPLATE.replace("__BUILD_ID__", build_id)
    for p in SW_TARGETS:
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.is_file():
            shutil.copy2(p, p.with_name(f"sw.js.bak_v5_{ts}"))
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        ok(f"{p.relative_to(BASE_DIR).as_posix()} 캐시 리셋 워커 갱신 (build {build_id})")


class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".json": "application/json; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".html": "text/html; charset=utf-8",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
    })

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def run_server(port: int) -> None:
    handler = functools.partial(RangeRequestHandler, directory=str(BASE_DIR))
    httpd = http.server.ThreadingHTTPServer(("", port), handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.8):
            return True
    except OSError:
        return False


def http_get(url: str, headers: dict | None = None, limit: int = 2_000_000, method: str = "GET"):
    req = urllib.request.Request(url, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            body = r.read(limit) if method != "HEAD" else b""
            return r.status, dict(r.headers), body
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), b""
    except Exception as e:
        return 0, {"error": str(e)}, b""


def quote_path(rel: str) -> str:
    return "/".join(urllib.parse.quote(part) for part in rel.split("/"))


def verify(port: int, build_id: str, manifest: dict) -> dict:
    base = f"http://127.0.0.1:{port}"
    results = {"pages": {}, "assets": {}}

    for rel in (HTML_NAME, f"dashboard/{HTML_NAME}", f"docs/{HTML_NAME}"):
        st, _, body = http_get(f"{base}/{rel}?v={build_id}")
        text = body.decode("utf-8", errors="ignore")
        good = st == 200 and MARK_START in text and build_id in text
        results["pages"][rel] = good
        (ok if good else warn)(f"[HTML] /{rel} → {st} · v5 블록 {'O' if MARK_START in text else 'X'}")

    rel_mp4 = f"{BASKET_NAME}/{MP4_NAME}"
    st, hd, body = http_get(f"{base}/{rel_mp4}", limit=2048)
    good = st in (200, 206) and body[4:8] == b"ftyp"
    results["assets"][rel_mp4] = good
    (ok if good else fail)(f"[MP4 ] /{rel_mp4} → {st} · ftyp {'O' if body[4:8] == b'ftyp' else 'X'}")

    rel_man = f"{BASKET_NAME}/{MANIFEST_NAME}"
    st, _, body = http_get(f"{base}/{rel_man}?v={build_id}")
    try:
        good = st == 200 and json.loads(body.decode("utf-8")).get("build") == build_id
    except Exception:
        good = False
    results["assets"][rel_man] = good
    (ok if good else fail)(f"[JSON] /{rel_man} → {st} · build 일치 {'O' if good else 'X'}")

    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="SHIN 10초 광고 스튜디오 v5 업그레이드")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    if args.serve:
        run_server(args.port)
        return 0

    ts = _dt.datetime.now().strftime("%Y%m%d%H%M%S")
    build_id = f"v5-{ts}"
    print("=" * 72)
    print(f" 🎬 SHIN 올인원 광고 스튜디오 v5 업그레이드  ·  build {build_id}")
    print("=" * 72)

    step("1) 손질된 완성본 MP4 검증")
    mp4 = SRC_BASKET / MP4_NAME
    info = validate_mp4(mp4)
    if not info["exists"]:
        fail(f"{mp4} 파일이 없습니다.")
        return 1
    ok(f"{MP4_NAME} · {info['bytes'] / 1024:.1f} KB · ftyp O · {describe_probe(info['probe'])}")

    step("2) 레시피 / 씬 이미지 수집")
    recipes = load_recipes()
    scenes = discover_scenes()

    step("3) ingredients_basket 동기화 (루트 / dashboard / docs) + v5_manifest.json 생성")
    manifest = build_manifest(build_id, mp4, info, recipes, scenes)
    sync_basket(mp4, recipes, scenes, manifest)

    step("4) rgon_alpha_chat.html 3곳 v5 모달 패치")
    ensure_html_targets()
    block = render_block(build_id, manifest)
    for p in HTML_TARGETS:
        patch_html(p, block, build_id, ts)

    step("5) sw.js 캐시 리셋 워커 갱신")
    write_sw(build_id, ts)

    step("6) HTTP 검증")
    results = verify(args.port, build_id, manifest)

    url = f"http://127.0.0.1:{args.port}/{HTML_NAME}?build={build_id}&v5=1"
    print()
    log(f"🌐 새 빌드 URL : {url}")
    log(f"🎞️ 완성본 MP4  : http://127.0.0.1:{args.port}/{BASKET_NAME}/{MP4_NAME}")

    if not args.no_open:
        try:
            webbrowser.open(url, new=2)
        except Exception:
            pass

    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
