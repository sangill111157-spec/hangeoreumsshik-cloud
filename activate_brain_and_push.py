#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
activate_brain_and_push.py
위치: C:\Users\sangi\Downloads\shin-agent\activate_brain_and_push.py
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import hashlib
import importlib
import io
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
BASKET = BASE_DIR / "ingredients_basket"
SAMPLE = BASKET / "sample_paper_cup.jpg"
SAMPLE_META = BASKET / "sample_paper_cup.r1.json"
BACKUP_MUG = BASKET / "backup_old_ceramic_mug.jpg"
GROK_JSON = BASKET / "grok_5_viral_recipes.json"
TARGET_MP4 = BASKET / "trimmed_ad_paper_cup_10s.mp4"
OUT_DIR = BASE_DIR / "external_kitchen_outputs"
ALT_OUT_DIRS = [OUT_DIR, BASE_DIR / "kitchen_output"]
WORKER = BASE_DIR / "external_kitchen_worker.py"
V5_SCRIPT = BASE_DIR / "upgrade_all_in_one_ad_v5.py"
BRAIN_DIR = BASE_DIR / "brain_basket"
ACTIVE_RECIPE = BRAIN_DIR / "active_grok_recipe.json"
SELF_LOG = BRAIN_DIR / "self_correction_log.json"
BACKUPS = BASE_DIR / ".rgon_ad_backups"

TOPIC = "종이컵"
STYLE = "반전형"
VOICE = "ko-KR-InJoonNeural"
W, H, FPS, DUR = 540, 960, 30, 10.0
SLOTS = [(0.0, 3.0), (3.0, 7.0), (7.0, 10.0)]
SCENE_NAMES = ["scene_0_hook.jpg", "scene_1_body.jpg", "scene_2_cta.jpg"]
SCENE_KEYS = ["hook", "body", "cta"]
SCENE_LABELS = ["HOOK · 반전 예고", "BODY · 반전 공개", "CTA · 지금 행동"]
SCENE_SUBS = ["끝까지 보면 반전!", "손잡이 없는 진짜 일회용 종이컵", "친환경 일회용 종이컵 · 대량 할인"]
ACCENTS = [(255, 77, 109), (255, 176, 59), (0, 196, 140)]
DEFAULT_LINES = ["이거, 그냥 종이컵 아닙니다.", "손잡이 없는 일회용 종이컵, 그런데 손은 안 뜨겁죠.", "지금 바로 주문하세요!"]
LINE_LIMITS = [26, 36, 24]

POLLI_URL = ("https://image.pollinations.ai/prompt/Photorealistic%20vertical%209:16%20commercial%20product%20"
             "photograph%20of%20a%20single%20disposable%20white%20paper%20takeaway%20cup%20on%20warm%20wooden%20"
             "table%20no%20handle%20no%20ceramic%20mug%20no%20saucer%20clean%20upper%20negative%20space"
             "?width=540&height=960&nologo=true&seed=42")
R1_PROMPT = ("Photorealistic vertical 9:16 commercial product photograph of a single disposable white paper cup, "
             "single-use takeaway paper cup, rolled rim, no handle, no ceramic mug, no saucer, on a warm wooden table, "
             "soft studio lighting, clean upper negative space")
R1_NEGATIVE = "ceramic mug, coffee mug, cup handle, saucer, porcelain, glass cup"

BGM_EXPR = ("0.05*(sin(2*PI*220*t)+sin(2*PI*277.18*t)+sin(2*PI*329.63*t))*(0.75+0.25*sin(2*PI*t*62/240))"
            "+0.32*sin(2*PI*58*t)*exp(-9*(t-floor(t*62/60)*60/62))")

COMMIT_MSG = "feat(brain-v5): activate external brain kitchen & self-corrected paper cup MP4"
GITIGNORE_BLOCK = [
    "*.pickle", "*.pickle*", "config/token*", "**/config/token*", "token.json", "token.pickle",
    "credentials*.json", "client_secret*.json", "service_account*.json",
    "*.db", "*.sqlite", "*.sqlite3", ".env", ".env.*", "*.pem", "*.p12",
    "external_kitchen_outputs/", "kitchen_output/", ".rgon_ad_backups/",
    "*.bak_v5_*", "v5_server_*.log", "__pycache__/",
    "ingredients_basket/backup_old_ceramic_mug*.jpg",
]
ADD_PATHS = [
    ".gitignore", ".github/workflows/rgon_external_brain_kitchen.yml",
    "external_kitchen_worker.py", "setup_external_brain_kitchen.py", "upgrade_all_in_one_ad_v5.py",
    "activate_brain_and_push.py", "prep_and_trim_ingredients.py",
    "brain_basket", "ingredients_basket", "dashboard/ingredients_basket", "docs/ingredients_basket",
    "rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html",
    "sw.js", "dashboard/sw.js", "docs/sw.js",
    "top1_ingredients_basket.json", "evolution_memory.json",
]
SENSITIVE_NAME = re.compile(
    r"(\.pickle|(^|/)config/token|(^|/)token\.(json|pickle|txt)$|\.db$|\.sqlite3?$|client_secret|"
    r"credentials[^/]*\.json$|service_account[^/]*\.json$|(^|/)\.env(\.|$)|\.pem$|\.p12$)", re.I)
SECRET_CONTENT = [re.compile(p) for p in (
    r"ya29\.[0-9A-Za-z_\-]{20,}",
    r"1//0[0-9A-Za-z_\-]{30,}",
    r"GOCSPX-[0-9A-Za-z_\-]{10,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"AIza[0-9A-Za-z_\-]{35}",
    r"ghp_[0-9A-Za-z]{36}",
    r"github_pat_[0-9A-Za-z_]{40,}",
)]
TEXT_EXT = {".py", ".js", ".json", ".yml", ".yaml", ".md", ".html", ".htm", ".css", ".txt", ".cfg", ".ini", ".toml", ""}
MAX_FILE_BYTES = 95 * 1024 * 1024


def log(m=""):
    print(f"   {m}", flush=True)


def step(m):
    print(f"\n▶ {m}", flush=True)


def ok(m):
    print(f"   ✅ {m}", flush=True)


def warn(m):
    print(f"   ⚠️  {m}", flush=True)


def fail(m):
    print(f"   ❌ {m}", flush=True)


def now_kst():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")


def stamp():
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(p):
    try:
        return Path(p).resolve().relative_to(BASE_DIR).as_posix()
    except Exception:
        return str(p)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(p: Path):
    if not p.is_file():
        return None
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            with open(p, "r", encoding=enc) as f:
                return json.load(f)
        except Exception:
            continue
    return None


def write_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_cap(cmd, timeout=300, env=None):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, cwd=str(BASE_DIR), env=env)


def run_stream(cmd, env=None, prefix="      │ "):
    p = subprocess.Popen(cmd, cwd=str(BASE_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace", env=env)
    lines = []
    for line in p.stdout:
        line = line.rstrip("\r\n")
        print(prefix + line, flush=True)
        lines.append(line)
    return p.wait(), "\n".join(lines)


def ensure_pkg(mod, pip_name):
    try:
        importlib.import_module(mod)
        return True
    except ImportError:
        pass
    warn(f"{pip_name} 미설치 → pip install {pip_name} (경량 패키지)")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", pip_name], capture_output=True, text=True)
    importlib.invalidate_caches()
    try:
        importlib.import_module(mod)
        ok(f"{pip_name} 설치 완료")
        return True
    except ImportError:
        fail(f"{pip_name} 설치 실패")
        return False


def find_ffmpeg():
    ff, fp = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ff:
        cand = BASE_DIR / "ffmpeg-8.0.1-full_build" / "bin" / "ffmpeg.exe"
        if cand.is_file():
            ff = str(cand)
    if not fp and ff:
        cand_p = Path(ff).with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
        if cand_p.is_file():
            fp = str(cand_p)
    if not ff:
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ff = None
    return ff, fp


def _lerp(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def _font(size):
    from PIL import ImageFont
    for c in ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf",
              "C:/Windows/Fonts/NotoSansKR-Bold.otf", "C:/Windows/Fonts/NanumGothicBold.ttf",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
              "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
              "/System/Library/Fonts/AppleSDGothicNeo.ttc"]:
        if os.path.isfile(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def cover(im, w, h):
    from PIL import Image
    s = max(w / im.width, h / im.height)
    nw, nh = max(w, round(im.width * s)), max(h, round(im.height * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - w) // 2, (nh - h) // 2
    return im.crop((l, t, l + w, t + h))


def _overlay(base, draw_fn, blur=0, clip=None):
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    if clip is not None:
        lay.putalpha(ImageChops.multiply(lay.getchannel("A"), clip))
    return Image.alpha_composite(base, lay)


def fetch_pollinations(dst: Path, deadline=12.0):
    box = {}

    def _go():
        try:
            req = urllib.request.Request(POLLI_URL, headers={"User-Agent": "Mozilla/5.0 (RGON-Brain R1)"})
            with urllib.request.urlopen(req, timeout=deadline) as r:
                box["ctype"] = r.headers.get("Content-Type", "")
                box["data"] = r.read(10_000_000)
        except Exception as e:
            box["err"] = f"{type(e).__name__}: {e}"

    t0 = time.perf_counter()
    th = threading.Thread(target=_go, daemon=True)
    th.start()
    th.join(deadline)
    el = time.perf_counter() - t0
    if th.is_alive():
        return False, f"{deadline:.0f}초 타임아웃"
    if "err" in box:
        return False, box["err"]
    data, ctype = box.get("data", b""), box.get("ctype", "")
    if "image" not in ctype.lower() or len(data) < 8000:
        return False, f"이미지 아님 (Content-Type={ctype}, {len(data)}B)"
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("RGB")
        cover(im, W, H).save(dst, "JPEG", quality=93)
    except Exception as e:
        return False, f"이미지 디코드 실패: {e}"
    return True, f"{len(data) / 1024:.0f} KB · {el:.1f}s"


def draw_paper_cup(dst: Path):
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    S = 2
    w, h = W * S, H * S
    rnd = random.Random(42)
    table_y = int(h * 0.655)

    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(table_y):
        d.line([(0, y), (w, y)], fill=_lerp((244, 236, 224), (212, 194, 170), y / table_y))
    for y in range(table_y, h):
        d.line([(0, y), (w, y)], fill=_lerp((182, 122, 74), (112, 68, 38), ((y - table_y) / (h - table_y)) ** 0.8))
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((int(-w * 0.1), int(h * 0.04), int(w * 0.78), int(h * 0.60)), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(180)).point(lambda v: int(v * 0.6))
    img = Image.composite(Image.new("RGB", (w, h), (255, 249, 238)), img, glow).convert("RGBA")

    def grain(dr):
        n = 160
        for i in range(n):
            t = (i + rnd.random() * 0.7) / n
            y0 = table_y + 6 + (t ** 1.5) * (h - table_y)
            amp, fq, ph = 1.5 + t * 9, rnd.uniform(0.0018, 0.005), rnd.uniform(0, 6.283)
            col = (72, 40, 18, rnd.randint(30, 80)) if rnd.random() < 0.62 else (222, 168, 115, rnd.randint(22, 60))
            wd = 1 + int(t * 3 * rnd.random())
            pts = [(x, y0 + amp * math.sin(x * fq + ph) + 2.5 * math.sin(x * fq * 3.3 + ph * 1.7))
                   for x in range(-24, w + 25, 12)]
            dr.line(pts, fill=col, width=wd)

    img = _overlay(img, grain, blur=1.1)
    img = _overlay(img, lambda dr: dr.ellipse((int(w * 0.05), table_y + 40, int(w * 0.70), table_y + 260),
                                              fill=(255, 230, 200, 45)), blur=60)

    def ao(dr):
        for k in range(46):
            dr.line([(0, table_y + k), (w, table_y + k)], fill=(40, 22, 10, int(90 * (1 - k / 46) ** 2)))

    img = _overlay(img, ao, blur=2)
    img = _overlay(img, lambda dr: dr.line([(0, table_y - 1), (w, table_y - 1)], fill=(255, 240, 220, 110), width=2))

    cx = w // 2
    yt, yb = int(h * 0.40), int(h * 0.705)
    tw, bw, ryt, ryb = 232, 162, 40, 27

    img = _overlay(img, lambda dr: dr.ellipse((cx - bw + 30, yb - 34, cx + bw + 360, yb + 64), fill=(45, 25, 10, 120)), blur=42)
    img = _overlay(img, lambda dr: dr.ellipse((cx - bw - 22, yb - ryb - 4, cx + bw + 26, yb + ryb + 16), fill=(30, 16, 6, 175)), blur=14)

    body = Image.new("L", (w, h), 0)
    bd = ImageDraw.Draw(body)
    bd.polygon([(cx - tw, yt), (cx + tw, yt), (cx + bw, yb), (cx - bw, yb)], fill=255)
    bd.ellipse((cx - bw, yb - ryb, cx + bw, yb + ryb), fill=255)
    bd.ellipse((cx - tw, yt - ryt, cx + tw, yt + ryt), fill=255)

    strip = Image.new("RGB", (512, 1))
    px = strip.load()
    lx, ly, lz = -0.55, 0.25, 0.80
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / ln, ly / ln, lz / ln
    hx, hz = lx, lz + 1.0
    hn = math.sqrt(hx * hx + hz * hz)
    hx, hz = hx / hn, hz / hn
    for i in range(512):
        u = (i + 0.5) / 512 * 2 - 1
        nz = math.sqrt(max(0.0, 1 - u * u))
        diff = max(0.0, u * lx + nz * lz)
        spec = max(0.0, u * hx + nz * hz) ** 30
        rim = max(0.0, u - 0.82) / 0.18 * 0.10
        v = 0.58 + 0.40 * diff + 0.08 * spec + rim
        px[i, 0] = tuple(min(255, int(c * v)) for c in (250, 249, 246))

    shade = Image.new("RGB", (w, h), (0, 0, 0))
    for y in range(yt - ryt, yb + ryb + 1):
        if y < yt:
            hw = tw
        elif y > yb:
            hw = bw
        else:
            hw = tw + (bw - tw) * (y - yt) / (yb - yt)
        width = int(2 * hw) + 4
        row = strip.resize((width, 1), Image.BILINEAR)
        f = 1 - 0.12 * max(0.0, min(1.0, (y - yt) / (yb - yt))) ** 2.2
        if f < 0.999:
            row = row.point(lambda v, f=f: int(v * f))
        shade.paste(row, (int(cx - hw) - 2, y))
    cup = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cup.paste(shade.convert("RGBA"), (0, 0), body)
    img = Image.alpha_composite(img, cup)

    img = _overlay(img, lambda dr: dr.line([(cx + tw * 0.58, yt + ryt * 0.8), (cx + bw * 0.58, yb + ryb * 0.8)],
                                           fill=(190, 188, 183, 200), width=3), blur=0.8, clip=body)
    img = _overlay(img, lambda dr: dr.line([(cx + tw * 0.58 - 4, yt + ryt * 0.8), (cx + bw * 0.58 - 4, yb + ryb * 0.8)],
                                           fill=(255, 255, 255, 120), width=2), blur=0.8, clip=body)
    img = _overlay(img, lambda dr: dr.arc((cx - bw, yb - ryb, cx + bw, yb + ryb), 0, 180, fill=(170, 166, 160, 220), width=4), blur=1)
    img = _overlay(img, lambda dr: dr.arc((cx - tw + 6, yt - ryt + 14, cx + tw - 6, yt + ryt + 14), 0, 180,
                                          fill=(0, 0, 0, 70), width=14), blur=6, clip=body)

    e_in = (cx - tw + 16, yt - ryt + 7, cx + tw - 16, yt + ryt - 7)
    inner = Image.new("L", (w, h), 0)
    ImageDraw.Draw(inner).ellipse(e_in, fill=255)

    def interior(dr):
        dr.ellipse(e_in, fill=(232, 228, 220, 255))
        dr.ellipse((cx - (tw - 30), yt - ryt + 22, cx + (tw - 30), yt + ryt + 14), fill=(150, 96, 58, 255))
        dr.ellipse((cx - (tw - 38), yt - ryt + 25, cx + (tw - 38), yt + ryt + 12), fill=(86, 50, 28, 255))

    img = _overlay(img, interior, clip=inner)
    img = _overlay(img, lambda dr: dr.ellipse((cx - tw * 0.55, yt - 14, cx - tw * 0.05, yt + 6), fill=(255, 236, 214, 70)),
                   blur=6, clip=inner)
    img = _overlay(img, lambda dr: dr.arc(e_in, 180, 360, fill=(170, 164, 154, 140), width=10), blur=5, clip=inner)

    img = _overlay(img, lambda dr: dr.ellipse((cx - tw - 5, yt - ryt - 4, cx + tw + 5, yt + ryt + 4),
                                              outline=(244, 243, 239, 255), width=17))
    img = _overlay(img, lambda dr: dr.arc((cx - tw - 1, yt - ryt - 1, cx + tw + 1, yt + ryt + 1), 150, 320,
                                          fill=(255, 255, 255, 235), width=5), blur=1.2)
    img = _overlay(img, lambda dr: dr.arc((cx - tw - 3, yt - ryt + 3, cx + tw + 3, yt + ryt + 7), 10, 170,
                                          fill=(176, 172, 165, 170), width=4), blur=1.5)

    def steam(dr):
        for j, off in enumerate((-70, 10, 85)):
            pts = [(cx + off + 18 * math.sin(yy / 38 + j * 1.9), yy) for yy in range(yt - 50, yt - 360, -8)]
            dr.line(pts, fill=(255, 255, 255, 70), width=12)

    img = _overlay(img, steam, blur=12)

    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse((int(-w * 0.25), int(-h * 0.12), int(w * 1.25), int(h * 1.12)), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(200))
    mask = ImageChops.invert(vig).point(lambda v: int(v * 0.45))
    img = Image.composite(Image.new("RGBA", (w, h), (20, 10, 4, 255)), img, mask)

    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
    out.save(dst, "JPEG", quality=94, subsampling=0)


def r1_replace_sample(regen=False, offline=False):
    BASKET.mkdir(parents=True, exist_ok=True)
    meta = read_json(SAMPLE_META) or {}
    already = SAMPLE.is_file() and meta.get("sha256") == sha256(SAMPLE)
    if already and not regen:
        ok(f"sample_paper_cup.jpg가 이미 R1 교정본입니다 ({meta.get('source')}) → 유지")
        return meta

    if SAMPLE.is_file():
        if already:
            BACKUPS.mkdir(parents=True, exist_ok=True)
            dst = BACKUPS / f"sample_paper_cup_r1_prev_{stamp()}.jpg"
            shutil.copy2(SAMPLE, dst)
            ok(f"이전 R1 교정본 → {rel(dst)} 보관")
        else:
            dst = BACKUP_MUG
            if BACKUP_MUG.is_file() and sha256(BACKUP_MUG) != sha256(SAMPLE):
                dst = BASKET / f"backup_old_ceramic_mug_{stamp()}.jpg"
            if not dst.is_file():
                shutil.copy2(SAMPLE, dst)
            ok(f"🧠 R1 복기: 기존 '손잡이+받침대 도자기 머그컵' → {rel(dst)} 백업")
        SAMPLE.unlink()
        ok("기존 sample_paper_cup.jpg 삭제 (워커가 머그컵을 재사용하지 못하도록 차단)")
    else:
        log("기존 sample_paper_cup.jpg 없음 → 새로 생성")

    source = None
    if not offline:
        log("🌐 Pollinations 실사 API 시도 (데드라인 12초, R1 프롬프트: no handle / no ceramic mug / no saucer)")
        good, msg = fetch_pollinations(SAMPLE, 12.0)
        if good:
            source = "pollinations.ai (R1 prompt, seed=42)"
            ok(f"Pollinations 실사 이미지 수신: {msg}")
        else:
            warn(f"Pollinations 실패: {msg} → Pillow 스튜디오 렌더로 즉시 전환")
    if not source:
        t0 = time.perf_counter()
        draw_paper_cup(SAMPLE)
        source = "Pillow studio render (rolled rim + trapezoid body + wooden table, no handle/no saucer)"
        ok(f"Pillow로 손잡이 없는 일회용 종이컵 렌더 완료 ({time.perf_counter() - t0:.1f}s, {W}x{H})")

    meta = {"rule": "R1_PAPER_CUP_NOT_MUG", "source": source, "prompt": R1_PROMPT, "negative": R1_NEGATIVE,
            "size": f"{W}x{H}", "sha256": sha256(SAMPLE), "created_at": now_kst()}
    write_json(SAMPLE_META, meta)
    ok(f"{rel(SAMPLE)} 저장 ({SAMPLE.stat().st_size / 1024:.0f} KB) + {SAMPLE_META.name}")
    return meta


def _walk_dicts(o, depth=0):
    if depth > 8:
        return
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk_dicts(v, depth + 1)
    elif isinstance(o, list):
        for v in o:
            yield from _walk_dicts(v, depth + 1)


TEXT_KEYS = ("line", "text", "narration", "voice", "vo", "copy", "headline", "caption", "title", "대사", "자막", "script")


def _first(d, keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _texts(v):
    out = []
    if isinstance(v, str) and v.strip():
        out.append(v.strip())
    elif isinstance(v, list):
        for x in v:
            if isinstance(x, str) and x.strip():
                out.append(x.strip())
            elif isinstance(x, dict):
                t = _first(x, TEXT_KEYS)
                if t:
                    out.append(t)
    return out


def find_reversal_recipe(data):
    if data is None:
        return None
    for dct in _walk_dicts(data):
        for k in ("style", "style_name", "name", "title", "type", "스타일", "유형", "id"):
            v = dct.get(k)
            if isinstance(v, str) and "반전" in v:
                return dct
    for dct in _walk_dicts(data):
        for k, v in dct.items():
            if "반전" in str(k):
                if isinstance(v, dict):
                    return v
                if isinstance(v, (str, list)):
                    return {"script": v}
    return None


def _clean_line(s, limit, default):
    s = str(s or "").strip()
    s = re.sub(r"^\s*(?:\[[^\]]{1,12}\]|\(?\d+[.)]|(?:HOOK|BODY|CTA|후크|본문|반전|마무리|씬\s*\d)\s*[:：])\s*", "", s, flags=re.I)
    s = s.strip(" \"'“”‘’`")
    s = s.replace("{topic}", TOPIC).replace("{t}", TOPIC).replace("{주제}", TOPIC)
    s = re.sub(r"머그\s*(컵|잔)", "종이컵", s)
    s = re.sub(r"\s+", " ", s)
    if not s:
        return default
    if len(s) > limit:
        cut = max(s.rfind(" ", 0, limit), s.rfind(",", 0, limit))
        if cut >= int(limit * 0.5):
            s = s[:cut].rstrip(" ,")
        else:
            return default
    return s


def extract_lines(rec):
    lines = [None, None, None]
    if rec:
        for key in ("scenes", "script", "lines", "beats", "storyboard", "대본", "씬"):
            v = rec.get(key)
            t = _texts(v) if isinstance(v, list) else []
            if len(t) >= 3:
                lines = [t[0], t[1], t[-1]]
                break
            if isinstance(v, str) and v.strip():
                parts = [p.strip() for p in re.split(r"[\n/|]+|(?<=[.!?])\s+", v) if p.strip()]
                if len(parts) >= 3:
                    lines = [parts[0], parts[1], parts[-1]]
                    break
        if not lines[0]:
            lines[0] = _first(rec, ("hook_0_3s", "hook", "hook_line", "opening", "후크", "첫문장", "headline"))
        if not lines[1]:
            lines[1] = _first(rec, ("body_3_7s", "body", "twist", "reveal", "benefit", "반전", "본문", "middle", "main"))
        if not lines[2]:
            lines[2] = _first(rec, ("cta_7_10s", "cta", "call_to_action", "closing", "마무리", "행동유도"))
    return [_clean_line(lines[i], LINE_LIMITS[i], DEFAULT_LINES[i]) for i in range(3)]


def prepare_recipe():
    data = read_json(GROK_JSON)
    rec = find_reversal_recipe(data)
    if data is None:
        warn(f"{rel(GROK_JSON)} 없음 → 기본 반전형 대본 사용")
    elif rec is None:
        warn("grok_5_viral_recipes.json에서 '반전형'을 찾지 못함 → 기본 반전형 대본 사용")
    else:
        ok("Grok 4.7 '반전형' 레시피 로드 완료")
    lines = extract_lines(rec)
    for i, ln in enumerate(lines):
        log(f"· {SLOTS[i][0]:.0f}~{SLOTS[i][1]:.0f}s [{SCENE_KEYS[i].upper()}] {ln}")
    active = {"topic": TOPIC, "style": STYLE, "source": rel(GROK_JSON) if rec else "default",
              "scenes": [{"index": i, "key": SCENE_KEYS[i], "line": lines[i], "sub": SCENE_SUBS[i],
                          "start": SLOTS[i][0], "end": SLOTS[i][1]} for i in range(3)],
              "image_prompt_en": R1_PROMPT, "negative_prompt": R1_NEGATIVE,
              "pipeline": {"voice": f"edge-tts:{VOICE}", "bgm_bpm": 62, "ducking": True,
                           "video_codec": "h264", "audio_codec": "aac", "duration_s": 10.0, "frames": 300},
              "raw_recipe": rec, "updated_at": now_kst()}
    write_json(ACTIVE_RECIPE, active)
    ok(f"워커 연동용 레시피 저장: {rel(ACTIVE_RECIPE)} (env RGON_ACTIVE_RECIPE)")
    return lines


def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(" "), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
            continue
        if cur:
            lines.append(cur)
        cur = ""
        for ch in wd:
            if draw.textlength(cur + ch, font=font) > maxw and cur:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
    if cur:
        lines.append(cur)
    return lines[:3]


def render_text_scene(bg: Path, idx: int, line: str, dst: Path):
    from PIL import Image, ImageDraw
    im = cover(Image.open(bg).convert("RGB"), W, H).convert("RGBA")

    def grad(dr):
        for y in range(600):
            dr.line([(0, y), (W, y)], fill=(12, 10, 20, int(175 * (1 - y / 600) ** 1.4)))
        for y in range(840, H):
            dr.line([(0, y), (W, y)], fill=(12, 10, 20, int(130 * ((y - 840) / (H - 840)))))

    im = _overlay(im, grad)
    d = ImageDraw.Draw(im)
    acc = ACCENTS[idx]
    lf, tf, sf, bf = _font(20), _font(52), _font(26), _font(30)
    lab = SCENE_LABELS[idx]
    lw = d.textlength(lab, font=lf)
    d.rounded_rectangle((34, 60, 34 + lw + 28, 98), radius=19, fill=acc + (255,))
    d.text((48, 79), lab, font=lf, fill=(255, 255, 255), anchor="lm")
    lines = _wrap(d, line, tf, W - 72)
    y = 170
    for ln in lines:
        d.text((W // 2 + 3, y + 3), ln, font=tf, fill=(0, 0, 0, 170), anchor="mm")
        d.text((W // 2, y), ln, font=tf, fill=(255, 255, 255), anchor="mm")
        y += 66
    if idx in (0, 1):
        d.text((W // 2, y + 6), SCENE_SUBS[idx], font=sf, fill=(255, 224, 138), anchor="mm")
    else:
        txt = "지금 주문하기 →"
        bw_ = d.textlength(txt, font=bf) + 70
        d.rounded_rectangle((W // 2 - bw_ / 2, y + 8, W // 2 + bw_ / 2, y + 78), radius=35, fill=acc + (255,))
        d.text((W // 2, y + 43), txt, font=bf, fill=(255, 255, 255), anchor="mm")
        d.text((W // 2, y + 112), SCENE_SUBS[2], font=sf, fill=(255, 224, 138), anchor="mm")
    d.text((28, H - 52), f"#{TOPIC} · 10s AD · InJoon 성우", font=lf, fill=(255, 255, 255), anchor="lm")
    d.rectangle((0, H - 8, W, H), fill=(80, 80, 90))
    d.rectangle((0, H - 8, int(W * SLOTS[idx][1] / DUR), H), fill=acc)
    im.convert("RGB").save(dst, "JPEG", quality=93)


def tts(text, path: Path) -> bool:
    try:
        import edge_tts

        async def _go():
            await edge_tts.Communicate(text, VOICE, rate="+6%").save(str(path))

        asyncio.run(_go())
        if path.is_file() and path.stat().st_size > 1000:
            return True
    except Exception as e:
        warn(f"edge-tts 모듈 실패: {e}")
    try:
        run_cap([sys.executable, "-m", "edge_tts", "--voice", VOICE, "--rate=+6%", "--text", text,
                 "--write-media", str(path)], timeout=90)
    except Exception:
        pass
    return path.is_file() and path.stat().st_size > 1000


def media_duration(p: Path, ff, fp) -> float:
    try:
        if fp:
            r = run_cap([fp, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], 60)
            return float((r.stdout or "0").strip().splitlines()[0])
        r = run_cap([ff, "-hide_banner", "-i", str(p)], 60)
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    except Exception:
        pass
    return 0.0


def build_ffmpeg(ff, scenes, voices, tempos, out: Path, normalize=True):
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error"]
    for p, (s, e) in zip(scenes, SLOTS):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{e - s:.3f}", "-i", str(p)]
    for v in voices:
        cmd += ["-i", str(v)] if v else ["-f", "lavfi", "-t", "3", "-i", "anullsrc=r=44100:cl=stereo"]
    cmd += ["-f", "lavfi", "-t", "10", "-i", f"aevalsrc='{BGM_EXPR}|{BGM_EXPR}':s=44100:d=10"]
    nm = ":normalize=0" if normalize else ""
    fc = []
    for i in range(3):
        fc.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},format=yuv420p[v{i}]")
    fc.append("[v0][v1][v2]concat=n=3:v=1:a=0,fade=t=in:st=0:d=0.25,fade=t=out:st=9.6:d=0.4[v]")
    for i, (s, _) in enumerate(SLOTS):
        ms = int(s * 1000) + 150
        tp = f",atempo={tempos[i]:.3f}" if tempos[i] > 1.001 else ""
        fc.append(f"[{3 + i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo{tp},adelay={ms}|{ms}[l{i}]")
    fc.append(f"[l0][l1][l2]amix=inputs=3:duration=longest{nm}{'' if normalize else ',volume=3'},apad,atrim=0:10,asplit=2[vo1][vo2]")
    fc.append("[6:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.8,"
              "afade=t=in:st=0:d=0.5,afade=t=out:st=9.2:d=0.8[bg]")
    fc.append("[bg][vo1]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350[duck]")
    fc.append(f"[duck][vo2]amix=inputs=2:duration=first{nm}{'' if normalize else ',volume=2'},atrim=0:10,alimiter=limit=0.95[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-frames:v", "300", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-t", "10.000",
            "-movflags", "+faststart", str(out)]
    return cmd


def builtin_cook(lines, ff, fp):
    run = OUT_DIR / f"run_{stamp()}_builtin"
    run.mkdir(parents=True, exist_ok=True)
    log(f"🍳 내장 파이프라인 → {rel(run)}")
    scenes = []
    for i, name in enumerate(SCENE_NAMES):
        p = run / name
        render_text_scene(SAMPLE, i, lines[i], p)
        scenes.append(p)
        ok(f"씬 {name} (R1 종이컵 배경 + 한글 타이포)")
    ensure_pkg("edge_tts", "edge-tts")
    voices, tempos = [], []
    for i, ln in enumerate(lines):
        p = run / f"voice_{i}_{SCENE_KEYS[i]}.mp3"
        good = tts(ln, p)
        dur = media_duration(p, ff, fp) if good else 0.0
        slot = SLOTS[i][1] - SLOTS[i][0] - 0.3
        tempo = min(1.6, max(1.0, dur / slot)) if dur else 1.0
        voices.append(p if good else None)
        tempos.append(tempo)
        (ok if good else warn)(f"성우 {p.name}: {'OK' if good else '실패(무음 대체)'} · {dur:.2f}s · atempo {tempo:.2f} 「{ln}」")
    out = run / "trimmed_ad_10s.mp4"
    r = run_cap(build_ffmpeg(ff, scenes, voices, tempos, out, True), 600)
    if r.returncode != 0 or not out.is_file():
        warn("amix normalize 옵션 미지원 가능성 → 호환 모드로 재합성")
        r = run_cap(build_ffmpeg(ff, scenes, voices, tempos, out, False), 600)
    if r.returncode != 0 or not out.is_file():
        fail("FFmpeg 합성 실패:\n" + (r.stderr or "")[-2500:])
        return None, run
    write_json(run / "recipe.json", read_json(ACTIVE_RECIPE) or {})
    return out, run


def probe(path: Path, ff, fp):
    info = {"bytes": path.stat().st_size if path.is_file() else 0, "duration": 0.0, "vcodec": None, "acodec": None,
            "width": None, "height": None, "frames": None, "mean_db": None, "max_db": None}
    if fp:
        try:
            r = run_cap([fp, "-v", "error", "-show_entries",
                         "format=duration:stream=codec_type,codec_name,width,height", "-of", "json", str(path)], 60)
            j = json.loads(r.stdout or "{}")
            info["duration"] = float((j.get("format") or {}).get("duration") or 0)
            for s in j.get("streams", []):
                if s.get("codec_type") == "video" and not info["vcodec"]:
                    info.update(vcodec=s.get("codec_name"), width=s.get("width"), height=s.get("height"))
                elif s.get("codec_type") == "audio" and not info["acodec"]:
                    info["acodec"] = s.get("codec_name")
            r = run_cap([fp, "-v", "error", "-select_streams", "v:0", "-count_packets",
                         "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)], 120)
            m = re.search(r"\d+", r.stdout or "")
            if m:
                info["frames"] = int(m.group(0))
        except Exception:
            pass
    if ff and (info["frames"] is None or not info["vcodec"] or not info["duration"]):
        r = run_cap([ff, "-hide_banner", "-i", str(path), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"], 120)
        err = r.stderr or ""
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
        if m and not info["duration"]:
            info["duration"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        m = re.search(r"Video:\s*(\w+).*?\b(\d{2,5})x(\d{2,5})\b", err)
        if m and not info["vcodec"]:
            info.update(vcodec=m.group(1), width=int(m.group(2)), height=int(m.group(3)))
        m = re.search(r"Audio:\s*(\w+)", err)
        if m and not info["acodec"]:
            info["acodec"] = m.group(1)
        fr = re.findall(r"frame=\s*(\d+)", err)
        if fr and info["frames"] is None:
            info["frames"] = int(fr[-1])
    if ff:
        r = run_cap([ff, "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a:0",
                     "-af", "volumedetect", "-f", "null", "-"], 120)
        m1 = re.search(r"mean_volume:\s*(-?[\d.]+|-inf)", r.stderr or "")
        m2 = re.search(r"max_volume:\s*(-?[\d.]+|-inf)", r.stderr or "")
        info["mean_db"] = -999.0 if (m1 and m1.group(1) == "-inf") else (float(m1.group(1)) if m1 else None)
        info["max_db"] = -999.0 if (m2 and m2.group(1) == "-inf") else (float(m2.group(1)) if m2 else None)
    return info


def validate(path: Path, ff, fp, title="MP4"):
    if not path or not path.is_file():
        fail(f"{title}: 파일 없음")
        return False, {}
    i = probe(path, ff, fp)
    checks = {
        "10.000s": abs(i["duration"] - 10.0) <= 0.06,
        "300프레임": i["frames"] is not None and abs(i["frames"] - 300) <= 1,
        "H.264": (i["vcodec"] or "").lower() == "h264",
        "AAC": (i["acodec"] or "").lower() == "aac",
        "540x960": i["width"] == W and i["height"] == H,
        "무음아님": i["max_db"] is not None and i["max_db"] > -30 and (i["mean_db"] is None or i["mean_db"] > -55),
    }
    allp = all(checks.values())
    log(f"🔬 {title}: {rel(path)} · {i['bytes'] / 1024:.0f} KB · {i['duration']:.3f}s · frames={i['frames']} · "
        f"{i['vcodec']}/{i['acodec']} · {i['width']}x{i['height']} · mean {i['mean_db']} dB / max {i['max_db']} dB")
    log("   " + " | ".join(f"{k} {'O' if v else 'X'}" for k, v in checks.items()))
    (ok if allp else fail)(f"{title} 검증 {'PASS' if allp else 'FAIL'}")
    i["checks"] = checks
    i["passed"] = allp
    return allp, i


def find_new_mp4(since):
    cands = []
    for d in ALT_OUT_DIRS:
        if d.is_dir():
            cands += [p for p in d.rglob("*.mp4") if p.stat().st_mtime >= since - 1]
    if not cands:
        return None
    pref = [p for p in cands if p.name == "trimmed_ad_10s.mp4"]
    return max(pref or cands, key=lambda p: p.stat().st_mtime)


def find_scenes(folder: Path):
    res = {}
    for i in range(3):
        c = [p for p in folder.glob(f"scene_{i}_*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
        if not c:
            continue
        pref = [p for p in c if SCENE_KEYS[i] in p.stem.lower()]
        res[i] = max(pref or c, key=lambda p: p.stat().st_mtime)
    return res


def normalize_run(mp4: Path, lines):
    from PIL import Image
    src = mp4.parent
    if src.name.startswith("run_") and OUT_DIR.resolve() in src.resolve().parents:
        run = src
    else:
        run = OUT_DIR / f"run_{stamp()}_worker"
        run.mkdir(parents=True, exist_ok=True)
    target = run / "trimmed_ad_10s.mp4"
    if mp4.resolve() != target.resolve():
        shutil.copy2(mp4, target)
    found = find_scenes(src)
    for i, name in enumerate(SCENE_NAMES):
        dst = run / name
        if i in found:
            if found[i].resolve() != dst.resolve():
                if found[i].suffix.lower() in (".jpg", ".jpeg"):
                    shutil.copy2(found[i], dst)
                else:
                    Image.open(found[i]).convert("RGB").save(dst, "JPEG", quality=93)
        else:
            render_text_scene(SAMPLE, i, lines[i], dst)
            log(f"· {name}: 워커 산출물에 없어 R1 종이컵 배경으로 렌더")
    return run, target


def run_worker(lines):
    if not WORKER.is_file():
        warn("external_kitchen_worker.py 없음")
        return None
    try:
        help_txt = run_cap([sys.executable, "-X", "utf8", str(WORKER), "--help"], 60).stdout or ""
    except Exception:
        help_txt = ""
    cmd = [sys.executable, "-X", "utf8", str(WORKER), "--topic", TOPIC, "--style", STYLE]
    if re.search(r"--approved\b", help_txt):
        cmd.append("--approved")
    elif re.search(r"--approve\b", help_txt):
        cmd.append("--approve")
    if re.search(r"--output\b", help_txt):
        cmd += ["--output", OUT_DIR.name]
    elif re.search(r"--out\b", help_txt):
        cmd += ["--out", OUT_DIR.name]
    if re.search(r"--mode\b", help_txt) and "cook" in help_txt:
        cmd += ["--mode", "cook"]
    ff_bin = BASE_DIR / "ffmpeg-8.0.1-full_build" / "bin"
    path_env = (str(ff_bin) + os.pathsep + os.environ.get("PATH", "")) if ff_bin.is_dir() else os.environ.get("PATH", "")
    env = dict(os.environ, PATH=path_env, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", RGON_APPROVED="1",
               RGON_SAMPLE_IMAGE=str(SAMPLE), RGON_ACTIVE_RECIPE=str(ACTIVE_RECIPE), RGON_GROK_STYLE=STYLE,
               RGON_SCRIPT_LINES=json.dumps(lines, ensure_ascii=False))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log("$ " + " ".join(cmd[1:]))
    t0 = time.time()
    try:
        rc, _ = run_stream(cmd, env=env)
    except Exception as e:
        fail(f"워커 실행 오류: {e}")
        return None
    mp4 = find_new_mp4(t0)
    (ok if rc == 0 else warn)(f"워커 종료 rc={rc} · 새 MP4: {rel(mp4) if mp4 else '없음'}")
    return mp4


def update_trimmed_recipe(lines):
    target = BASKET / f"trimmed_recipe_{TOPIC}.json"
    data = read_json(target) if target.is_file() else {}
    if not isinstance(data, dict):
        data = {"data": data}
    if target.is_file():
        BACKUPS.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, BACKUPS / f"{target.stem}_{stamp()}.json")
    af = data.get("adobe_firefly") if isinstance(data.get("adobe_firefly"), dict) else {}
    af.update(image_prompt_en=R1_PROMPT, negative_prompt=R1_NEGATIVE, r1_corrected=True)
    data["adobe_firefly"] = af
    data["topic"] = data.get("topic") or TOPIC
    data["grok_style"] = STYLE
    data["scenes"] = [{"index": i, "key": SCENE_KEYS[i], "headline": lines[i], "sub": SCENE_SUBS[i],
                       "start": SLOTS[i][0], "end": SLOTS[i][1], "file": SCENE_NAMES[i]} for i in range(3)]
    data["self_correction"] = {"rule": "R1_PAPER_CUP_NOT_MUG", "applied_at": now_kst(),
                               "note": "coffee cup → disposable white paper cup, no handle, no ceramic mug, no saucer"}
    write_json(target, data)
    ok(f"{rel(target)} 갱신 (R1 프롬프트 + 반전형 3씬)")


def sync_basket(run: Path, mp4: Path):
    BASKET.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(parents=True, exist_ok=True)
    if TARGET_MP4.is_file():
        shutil.copy2(TARGET_MP4, BACKUPS / f"trimmed_ad_paper_cup_10s_{stamp()}.mp4")
    shutil.copyfile(mp4, TARGET_MP4)
    os.utime(TARGET_MP4, None)
    ok(f"{rel(mp4)} → {rel(TARGET_MP4)}")
    for p in BASKET.glob("scene_[0-2]_*"):
        if p.name not in SCENE_NAMES and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            shutil.move(str(p), str(BACKUPS / f"{p.stem}_{stamp()}{p.suffix}"))
            log(f"· 구버전 씬 {p.name} → .rgon_ad_backups/ 이동")
    for name in SCENE_NAMES:
        shutil.copyfile(run / name, BASKET / name)
        os.utime(BASKET / name, None)
        ok(f"{rel(run / name)} → ingredients_basket/{name}")


def run_v5():
    if not V5_SCRIPT.is_file():
        fail("upgrade_all_in_one_ad_v5.py 없음")
        return False, None
    ff_bin = BASE_DIR / "ffmpeg-8.0.1-full_build" / "bin"
    path_env = (str(ff_bin) + os.pathsep + os.environ.get("PATH", "")) if ff_bin.is_dir() else os.environ.get("PATH", "")
    rc, out = run_stream([sys.executable, "-X", "utf8", str(V5_SCRIPT), "--no-open"],
                         env=dict(os.environ, PATH=path_env, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
    m = re.search(r"새 빌드 URL\s*:\s*(\S+)", out)
    url = m.group(1) if m else None
    if not url:
        man = read_json(BASKET / "v5_manifest.json") or {}
        if man.get("build"):
            url = f"http://127.0.0.1:8501/rgon_alpha_chat.html?build={man['build']}&v5=1"
    (ok if rc == 0 else warn)(f"STUDIO v5 리빌드 rc={rc}")
    return rc == 0, url


def git(*args, timeout=300):
    return run_cap(["git", *args], timeout)


def ensure_gitignore():
    gi = BASE_DIR / ".gitignore"
    cur = gi.read_text(encoding="utf-8", errors="ignore") if gi.is_file() else ""
    have = {x.strip() for x in cur.splitlines()}
    add = [x for x in GITIGNORE_BLOCK if x not in have]
    if add:
        with open(gi, "a", encoding="utf-8", newline="\n") as f:
            f.write(("\n" if cur and not cur.endswith("\n") else "")
                    + "# RGON brain-v5: 토큰·비밀키·임시 산출물 커밋 차단\n" + "\n".join(add) + "\n")
        ok(".gitignore 보강: " + ", ".join(add))
    else:
        ok(".gitignore 민감 패턴 이미 완비")


def untrack_ignored():
    r = git("ls-files", "-ci", "--exclude-standard", "-z")
    files = [f for f in (r.stdout or "").split("\0") if f]
    if not files:
        ok("추적 중인 민감/무시 대상 파일 없음")
        return []
    for i in range(0, len(files), 50):
        git("rm", "-r", "--cached", "-q", "--", *files[i:i + 50])
    warn(f"이미 추적되던 무시 대상 {len(files)}개를 인덱스에서 제거 (로컬 파일은 유지): " + ", ".join(files[:8])
         + (" ..." if len(files) > 8 else ""))
    return files


def staged_files():
    r = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    return [f for f in (r.stdout or "").split("\0") if f]


def secret_scan(files):
    hits = []
    for f in files:
        if SENSITIVE_NAME.search(f):
            hits.append((f, "민감 파일명"))
            continue
        p = BASE_DIR / f
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT or p.stat().st_size > 3 * 1024 * 1024:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for rx in SECRET_CONTENT:
            if rx.search(txt):
                hits.append((f, f"비밀키 패턴 {rx.pattern[:24]}…"))
                break
    return hits


def pages_urls(remote, build):
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", remote or "")
    if not m:
        return None, None
    owner, repo = m.group(1), m.group(2)
    q = f"?build={build}&v5=1" if build else ""
    return (f"https://{owner.lower()}.github.io/{repo}/rgon_alpha_chat.html{q}",
            f"https://github.com/{owner}/{repo}/actions/workflows/rgon_external_brain_kitchen.yml")


def git_commit_push(no_push=False, remote_url=None):
    res = {"committed": False, "pushed": False, "hash": None, "remote": None}
    if not shutil.which("git"):
        fail("git이 설치되어 있지 않습니다.")
        return res
    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        if not remote_url:
            fail("Git 저장소가 아닙니다. --remote-url https://github.com/<owner>/hangeoreumsshik-cloud.git 로 다시 실행하세요.")
            return res
        git("init")
        git("checkout", "-B", "main")
        git("remote", "add", "origin", remote_url)
        ok(f"git init + origin={remote_url}")
    elif remote_url:
        if git("remote", "get-url", "origin").returncode == 0:
            git("remote", "set-url", "origin", remote_url)
        else:
            git("remote", "add", "origin", remote_url)
    r = git("remote", "get-url", "origin")
    remote = (r.stdout or "").strip()
    res["remote"] = remote
    if not remote:
        fail("origin 원격이 없습니다. --remote-url 로 지정하세요.")
        return res
    (ok if "hangeoreumsshik-cloud" in remote else warn)(f"origin = {remote}")

    ensure_gitignore()
    untrack_ignored()
    paths = [p for p in ADD_PATHS if (BASE_DIR / p).exists()]
    r = git("add", "-A", "--", *paths)
    if r.returncode != 0:
        warn("git add 경고: " + (r.stderr or "").strip()[:300])
    files = staged_files()
    for f in files:
        p = BASE_DIR / f
        if p.is_file() and p.stat().st_size > MAX_FILE_BYTES:
            git("reset", "-q", "--", f)
            warn(f"GitHub 100MB 제한 → 스테이징 제외: {f}")
    files = staged_files()
    hits = secret_scan(files)
    if hits:
        git("reset", "-q")
        for f, why in hits:
            fail(f"🔐 커밋 차단: {f} ({why})")
        fail("민감 정보가 감지되어 스테이징을 전부 해제하고 Push를 중단했습니다.")
        return res
    ok(f"🔐 비밀키 스캔 통과 · 스테이징 {len(files)}개 파일")

    if git("diff", "--cached", "--quiet").returncode != 0:
        r = git("commit", "-m", COMMIT_MSG)
        if r.returncode != 0:
            fail("commit 실패: " + ((r.stderr or "") + (r.stdout or "")).strip()[:600])
            return res
        res["committed"] = True
        ok(f"commit: {COMMIT_MSG}")
    else:
        ok("새로 커밋할 변경 없음 (기존 HEAD 푸시)")
    res["hash"] = (git("rev-parse", "HEAD").stdout or "").strip() or None

    if no_push:
        warn("--no-push: push 생략")
        return res
    branch = (git("rev-parse", "--abbrev-ref", "HEAD").stdout or "").strip()
    refspec = "main" if branch == "main" else "HEAD:main"
    log(f"$ git push -u origin {refspec}")
    rc = subprocess.run(["git", "push", "-u", "origin", refspec], cwd=str(BASE_DIR)).returncode
    if rc != 0:
        warn("push 거부 → git pull --rebase --autostash origin main 후 재시도")
        rr = subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE_DIR)).returncode
        if rr != 0:
            git("rebase", "--abort")
            fail("rebase 충돌 → 자동 중단. 수동으로 충돌을 해결한 뒤 다시 실행하세요.")
            return res
        rc = subprocess.run(["git", "push", "-u", "origin", refspec], cwd=str(BASE_DIR)).returncode
    res["pushed"] = rc == 0
    res["hash"] = (git("rev-parse", "HEAD").stdout or "").strip() or res["hash"]
    (ok if res["pushed"] else fail)(f"git push origin main {'성공' if res['pushed'] else '실패'} · {res['hash']}")
    return res


def main():
    ap = argparse.ArgumentParser(description="RGON 두뇌 R1 자가교정 + 외부 주방 가동 + GitHub Push")
    ap.add_argument("--regen-sample", action="store_true")
    ap.add_argument("--offline-image", action="store_true")
    ap.add_argument("--builtin", action="store_true")
    ap.add_argument("--skip-v5", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--remote-url", default=None)
    a = ap.parse_args()

    print("=" * 74)
    print(" 🧠 RGON Brain Self-Correction (R1) → External Kitchen → STUDIO v5 → GitHub")
    print(f" 📁 {BASE_DIR} · {now_kst()}")
    print(" 📜 헌법 5조: 사령관 직접 실행 = 사전 승인으로 간주")
    print("=" * 74)
    receipt = {"started_at": now_kst()}

    if not ensure_pkg("PIL", "pillow"):
        return 1
    ff, fp = find_ffmpeg()
    if not ff:
        fail("ffmpeg를 찾을 수 없습니다 (PATH 또는 imageio-ffmpeg).")
        return 1
    ok(f"ffmpeg: {ff} · ffprobe: {fp or '없음(ffmpeg 폴백 검증)'}")

    step("[1/4] 🧠 R1 복기 실전 적용: 도자기 머그컵 → 손잡이 없는 일회용 종이컵")
    receipt["sample"] = r1_replace_sample(a.regen_sample, a.offline_image)

    step("[2/4] 🍳 Grok '반전형' 연동 + 외부 손질 워커 실전 가동")
    lines = prepare_recipe()
    mp4, run, info, passed = None, None, {}, False
    if not a.builtin:
        wmp4 = run_worker(lines)
        if wmp4:
            passed, info = validate(wmp4, ff, fp, "워커 MP4")
            if passed:
                run, mp4 = normalize_run(wmp4, lines)
                ok(f"정규화: {rel(mp4)} + 3씬")
    if not passed:
        if not a.builtin:
            warn("헌법 4조: 워커 결과가 Critic 미통과/부재 → 내장 파이프라인으로 자동 교정")
        mp4, run = builtin_cook(lines, ff, fp)
        passed, info = validate(mp4, ff, fp, "내장 MP4") if mp4 else (False, {})
    receipt["mp4"] = {"path": rel(mp4) if mp4 else None, "validation": info}
    if not passed:
        fail("⛔ 10초 MP4 검증 실패 → 장바구니 동기화와 Push를 중단합니다 (헌법 4조).")
        return 1

    step("[3/4] 🧺 STUDIO v5 장바구니 동기화 + 리빌드")
    sync_basket(run, mp4)
    update_trimmed_recipe(lines)
    validate(TARGET_MP4, ff, fp, "장바구니 MP4")
    build_url = None
    if not a.skip_v5:
        v5_ok, build_url = run_v5()
        receipt["v5_ok"] = v5_ok
    man = read_json(BASKET / "v5_manifest.json") or {}
    build_id = man.get("build")

    logdata = read_json(SELF_LOG) or []
    if not isinstance(logdata, list):
        logdata = [logdata]
    logdata.append({"at": now_kst(), "rule": "R1_PAPER_CUP_NOT_MUG",
                    "action": "ceramic mug sample backed up & replaced with handle-less disposable paper cup",
                    "sample_source": receipt["sample"].get("source"), "grok_style": STYLE, "lines": lines,
                    "mp4": rel(TARGET_MP4), "duration_s": round(info.get("duration", 0), 3),
                    "frames": info.get("frames"), "codecs": f"{info.get('vcodec')}/{info.get('acodec')}",
                    "build": build_id})
    write_json(SELF_LOG, logdata[-50:])
    write_json(BRAIN_DIR / "activation_receipt.json", {**receipt, "build": build_id, "build_url": build_url})
    ok(f"두뇌 복기 로그: {rel(SELF_LOG)}")

    step("[4/4] ☁️ GitHub 외부 클라우드 주방 안전 Commit & Push")
    g = git_commit_push(a.no_push, a.remote_url)
    pages, actions = pages_urls(g.get("remote"), build_id)

    BACKUPS.mkdir(parents=True, exist_ok=True)
    write_json(BACKUPS / f"activation_receipt_{stamp()}.json", {**receipt, "git": g, "build_url": build_url,
                                                                 "pages_url": pages, "finished_at": now_kst()})
    print("\n" + "=" * 74)
    print(f"   🧠 R1 교정 이미지 : {rel(SAMPLE)} ({receipt['sample'].get('source')})")
    print(f"   🎬 완성본 MP4     : {rel(TARGET_MP4)} · {info.get('duration', 0):.3f}s · {info.get('frames')}f · "
          f"{info.get('vcodec')}/{info.get('acodec')} · max {info.get('max_db')} dB")
    print(f"   🧾 커밋 해시      : {g.get('hash') or '-'} {'(pushed)' if g.get('pushed') else ''}")
    if actions:
        print(f"   ⚙️ Actions        : {actions}")
    if pages:
        print(f"   🌍 Pages(/docs)   : {pages}")
    print(f"   🌐 새 빌드 URL    : {build_url or '-'}")
    print("=" * 74)
    if a.no_push and g.get("hash"):
        print(f"BRAIN SELF-CORRECTION COMPLETE (PUSH SKIPPED) {build_url or ''}")
        return 0
    if not g.get("pushed"):
        print("⚠️ Push 미완료: 위 로그를 확인한 뒤 다시 실행해 주세요.")
        return 2
    print(f"BRAIN SELF-CORRECTION & GITHUB CLOUD KITCHEN PUSH COMPLETE! {build_url or pages or ''}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⛔ 사용자 중단")
        sys.exit(130)
