# -*- coding: utf-8 -*-
"""
SUN-ONE AON 2026 Futuristic YouTube Studio Branding Suite Generator
===================================================================
Produces ultra-futuristic, high-trend branding assets for @SUN-ONEAON:
1. banner_2560x1440.png (YouTube Master Banner, Strict 1546x423 Safe Area, 3-Logo Synergy)
2. avatar_800x800.png (YouTube Master Avatar, Strict 400px Circular Safe Radius)
3. watermark_800x800.png & watermark_150x150.png (Transparent Video Watermark)
4. thumbnail_template_1920x1080.png & EP01~EP04 Master Thumbnails
"""

import os
import sys
import math
import random
import pathlib
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent

# Cleaned logo paths
LOGO1_PATH = ROOT / "s1_logo_1_clean.png"
LOGO2_PATH = ROOT / "s1_logo_2_clean.png"
LOGO3_PATH = ROOT / "s1_logo_3_clean.png"

# Target output directories
BRANDING_DIR_1 = ROOT / "studio_vault" / "CHANNELS" / "04_US_SUNONE_AON" / "BRANDING_KIT"
BRANDING_DIR_2 = ROOT / "studio_vault" / "US_AON_VAULT" / "BRANDING_KIT"
BRANDING_DIR_3 = ROOT / "assets" / "channel_branding_2026"
EASY_ACCESS_DIR = pathlib.Path("C:/Users/sangi/Downloads/SUNONE_AON_YOUTUBE_BRANDING")

for d in [BRANDING_DIR_1, BRANDING_DIR_2, BRANDING_DIR_3, EASY_ACCESS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Fonts
FONT_MALGUN_BD = "C:/WINDOWS/Fonts/malgunbd.ttf"
FONT_MALGUN = "C:/WINDOWS/Fonts/malgun.ttf"
FONT_ARIAL_BD = "C:/WINDOWS/Fonts/arialbd.ttf"
FONT_ARIAL = "C:/WINDOWS/Fonts/arial.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_cyber_grid(draw, w, h, horizon_y, grid_color=(15, 30, 60, 100)):
    # Horizontal grid lines with increasing spacing towards bottom
    for i in range(12):
        y = int(horizon_y + (h - horizon_y) * (i / 12.0) ** 1.6)
        alpha = int(40 + 80 * (i / 12.0))
        draw.line([(0, y), (w, y)], fill=(grid_color[0], grid_color[1], grid_color[2], alpha), width=1)
    
    # Perspective vanishing lines converging to center horizon
    center_x = w // 2
    for x in range(0, w + 100, 120):
        alpha = 60
        draw.line([(center_x, horizon_y), (x, h)], fill=(grid_color[0], grid_color[1], grid_color[2], alpha), width=1)

def draw_stars(draw, w, h, count=180, seed=42):
    random.seed(seed)
    for _ in range(count):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.choice([1, 1, 1, 2, 2, 3])
        tint = random.choice([
            (245, 158, 11, random.randint(80, 200)), # Gold
            (34, 211, 238, random.randint(80, 220)), # Cyan
            (255, 255, 255, random.randint(100, 255)), # White
        ])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=tint)

def draw_concentric_telemetry(draw, cx, cy, radius, primary_color=(34, 211, 238), secondary_color=(245, 158, 11)):
    # Outer circle with ticks
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(*primary_color[:3], 90), width=2)
    # Ticks
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        length = 8 if deg % 30 == 0 else 4
        x1 = cx + (radius - length) * math.cos(rad)
        y1 = cy + (radius - length) * math.sin(rad)
        x2 = cx + radius * math.cos(rad)
        y2 = cy + radius * math.sin(rad)
        col = (*secondary_color[:3], 180) if deg % 90 == 0 else (*primary_color[:3], 120)
        draw.line([(x1, y1), (x2, y2)], fill=col, width=2 if deg % 30 == 0 else 1)
    
    # Inner ring
    r_inner = radius - 20
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], outline=(*secondary_color[:3], 80), width=1)


# ==============================================================================
# 1. RENDER BANNER (2560 x 1440) - Strict Safe Area 1546x423
# ==============================================================================
def render_banner():
    print(">>> [1/4] Rendering 2560x1440 YouTube Master Banner...")
    W, H = 2560, 1440
    banner = Image.new("RGBA", (W, H), (2, 4, 10, 255))
    draw = ImageDraw.Draw(banner, "RGBA")

    # 1. Background radial & linear gradient (Cosmic void to deep cyan nebula)
    for y in range(H):
        dist_y = abs(y - 720) / 720.0
        r = int(2 + 8 * (1.0 - dist_y))
        g = int(5 + 16 * (1.0 - dist_y))
        b = int(12 + 28 * (1.0 - dist_y))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Top & Bottom soft nebula haze
    draw_stars(draw, W, H, count=220, seed=101)
    draw_cyber_grid(draw, W, H, horizon_y=950, grid_color=(34, 211, 238, 50))

    # Safe Area definitions
    # Mobile/Universal Safe Area: 1546 x 423 (x: 507 to 2053, y: 508 to 931)
    SX0, SY0 = 507, 508
    SX1, SY1 = 2053, 931
    SAFE_W, SAFE_H = SX1 - SX0, SY1 - SY0
    CENTER_Y = (SY0 + SY1) // 2 # 719

    # Ambient Background Accents outside safe area (Visible on TV/4K)
    # Subtle ambient glow behind safe area
    for r in range(80, 0, -10):
        alpha = int(15 * (1.0 - r / 80.0))
        draw.rounded_rectangle([SX0 - r, SY0 - r, SX1 + r, SY1 + r], radius=24, fill=(10, 30, 60, alpha))

    # Safe Area Glassmorphic Panel (Translucent Cyber HUD Container)
    panel = Image.new("RGBA", (SAFE_W, SAFE_H), (8, 16, 32, 210))
    pdraw = ImageDraw.Draw(panel, "RGBA")
    # Border
    pdraw.rounded_rectangle([0, 0, SAFE_W - 1, SAFE_H - 1], radius=16, outline=(34, 211, 238, 90), width=1)
    # Subtle inner gold border
    pdraw.rounded_rectangle([3, 3, SAFE_W - 4, SAFE_H - 4], radius=14, outline=(245, 158, 11, 40), width=1)
    
    # Corner HUD brackets on panel
    bracket_len = 28
    # Top-Left
    pdraw.line([(0, 0), (bracket_len, 0)], fill=(245, 158, 11, 255), width=3)
    pdraw.line([(0, 0), (0, bracket_len)], fill=(245, 158, 11, 255), width=3)
    # Top-Right
    pdraw.line([(SAFE_W - bracket_len, 0), (SAFE_W, 0)], fill=(245, 158, 11, 255), width=3)
    pdraw.line([(SAFE_W, 0), (SAFE_W, bracket_len)], fill=(245, 158, 11, 255), width=3)
    # Bottom-Left
    pdraw.line([(0, SAFE_H), (bracket_len, SAFE_H)], fill=(245, 158, 11, 255), width=3)
    pdraw.line([(0, SAFE_H - bracket_len), (0, SAFE_H)], fill=(245, 158, 11, 255), width=3)
    # Bottom-Right
    pdraw.line([(SAFE_W - bracket_len, SAFE_H), (SAFE_W, SAFE_H)], fill=(245, 158, 11, 255), width=3)
    pdraw.line([(SAFE_W, SAFE_H - bracket_len), (SAFE_W, SAFE_H)], fill=(245, 158, 11, 255), width=3)

    banner.paste(panel, (SX0, SY0), panel)

    # -------------------------------------------------------------
    # SECTION A: LEFT WING - LOGO 2 (Aqua-Solar Core / 상선약수)
    # -------------------------------------------------------------
    core_cx = SX0 + 200
    core_cy = CENTER_Y - 20
    draw_concentric_telemetry(draw, core_cx, core_cy, radius=130, primary_color=(34, 211, 238), secondary_color=(245, 158, 11))

    # Paste Logo 2
    logo2 = Image.open(LOGO2_PATH).convert("RGBA")
    # Scaled to ~240x143
    l2_w, l2_h = logo2.size
    target_l2_w = 230
    target_l2_h = int(l2_h * (target_l2_w / l2_w))
    logo2_resized = logo2.resize((target_l2_w, target_l2_h), Image.Resampling.LANCZOS)
    banner.paste(logo2_resized, (core_cx - target_l2_w // 2, core_cy - target_l2_h // 2), logo2_resized)

    # Left Wing HUD Micro-Labels
    f_hud_sm = get_font(FONT_ARIAL_BD, 13)
    f_hud_kr = get_font(FONT_MALGUN_BD, 15)
    f_hud_mini = get_font(FONT_ARIAL, 11)

    label_l1 = "◈ AQUA-SOLAR CORE ◈"
    label_l2 = "상선약수 (上善若水)"
    label_l3 = "FREQ: 48kHz / 24-BIT HI-RES"

    # Centered under core
    draw.text((core_cx - 85, core_cy + 120), label_l1, font=f_hud_sm, fill=(34, 211, 238, 230))
    draw.text((core_cx - 72, core_cy + 140), label_l2, font=f_hud_kr, fill=(245, 158, 11, 255))
    draw.text((core_cx - 80, core_cy + 165), label_l3, font=f_hud_mini, fill=(148, 163, 184, 190))

    # -------------------------------------------------------------
    # SECTION B: RIGHT WING - LOGO 3 (Sovereign Imperial Crest / 33% Pledge)
    # -------------------------------------------------------------
    crest_cx = SX1 - 200
    crest_cy = CENTER_Y - 20
    draw_concentric_telemetry(draw, crest_cx, crest_cy, radius=130, primary_color=(245, 158, 11), secondary_color=(34, 211, 238))

    # Paste Logo 3
    logo3 = Image.open(LOGO3_PATH).convert("RGBA")
    l3_w, l3_h = logo3.size
    target_l3_h = 195
    target_l3_w = int(l3_w * (target_l3_h / l3_h))
    logo3_resized = logo3.resize((target_l3_w, target_l3_h), Image.Resampling.LANCZOS)
    banner.paste(logo3_resized, (crest_cx - target_l3_w // 2, crest_cy - target_l3_h // 2), logo3_resized)

    label_r1 = "★ SOVEREIGN IMPERIAL SEAL ★"
    label_r2 = "글로벌 환원의 국제화 (33%)"
    label_r3 = "ETHICAL ARTIFICIAL INTELLIGENCE"

    draw.text((crest_cx - 105, crest_cy + 120), label_r1, font=f_hud_sm, fill=(245, 158, 11, 240))
    draw.text((crest_cx - 95, crest_cy + 140), label_r2, font=f_hud_kr, fill=(34, 211, 238, 240))
    draw.text((crest_cx - 98, crest_cy + 165), label_r3, font=f_hud_mini, fill=(148, 163, 184, 190))

    # -------------------------------------------------------------
    # SECTION C: CENTER WING - LOGO 1 + 2026 CYBER TYPOGRAPHY
    # -------------------------------------------------------------
    center_cx = SX0 + SAFE_W // 2 # 1280
    
    # 1. Logo 1 (Typographic Wordmark)
    logo1 = Image.open(LOGO1_PATH).convert("RGBA")
    l1_w, l1_h = logo1.size
    target_l1_w = 480
    target_l1_h = int(l1_h * (target_l1_w / l1_w))
    logo1_resized = logo1.resize((target_l1_w, target_l1_h), Image.Resampling.LANCZOS)
    l1_x = center_cx - target_l1_w // 2
    l1_y = SY0 + 28
    banner.paste(logo1_resized, (l1_x, l1_y), logo1_resized)

    # 2. Main Slogans & Mission Statement
    f_slogan_main = get_font(FONT_ARIAL_BD, 26)
    f_slogan_kr = get_font(FONT_MALGUN_BD, 21)
    f_pledge = get_font(FONT_ARIAL_BD, 17)
    f_credits = get_font(FONT_ARIAL, 14)

    slogan_1 = "GLOBAL K-TREND AI CULTURAL SOVEREIGNTY"
    slogan_2 = "東方禮義之國의 품격과 상선약수(上善若水)의 감성"
    slogan_3 = "★ 33% Global Philanthropy Pledge for Humanity & Earth ★"
    credit_line = "Executive Producer: Sangill Lee | AI Chief Architect: AON"

    # Centered text positions
    def draw_centered_text(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((center_cx - tw // 2, y), text, font=font, fill=fill)

    base_y = l1_y + target_l1_h + 10
    draw_centered_text(base_y, slogan_1, f_slogan_main, (255, 235, 175, 255)) # Cyber Warm Gold
    draw_centered_text(base_y + 34, slogan_2, f_slogan_kr, (205, 240, 255, 240)) # Ice Cyan White
    draw_centered_text(base_y + 68, slogan_3, f_pledge, (245, 158, 11, 255)) # Glowing Gold
    draw_centered_text(base_y + 98, credit_line, f_credits, (148, 163, 184, 210)) # Muted Ice

    # 3. Bottom Tech Badges Pill
    badge_y = base_y + 124
    badges = ["48kHz / 24-BIT MASTER", "DISTROKID 2-SLOT", "SUNO V6 MAESTRO", "OFFICIAL ARTIST"]
    f_badge = get_font(FONT_ARIAL_BD, 11)
    
    total_badge_w = len(badges) * 165
    cur_x = center_cx - total_badge_w // 2
    for b_text in badges:
        bw, bh = 150, 22
        draw.rounded_rectangle([cur_x, badge_y, cur_x + bw, badge_y + bh], radius=6, fill=(15, 30, 55, 180), outline=(34, 211, 238, 80))
        tb = draw.textbbox((0, 0), b_text, font=f_badge)
        draw.text((cur_x + (bw - (tb[2] - tb[0])) // 2, badge_y + 4), b_text, font=f_badge, fill=(34, 211, 238, 220))
        cur_x += 165

    # 4. TV Ambient Markings outside safe area (Top & Bottom)
    f_tv = get_font(FONT_ARIAL_BD, 14)
    draw.text((80, 60), "SUN-ONE AON // K-GLOBAL CULTURAL HEADQUARTERS", font=f_tv, fill=(34, 211, 238, 90))
    draw.text((W - 460, 60), "LAT 37.5665° N / LON 126.9780° E // SEOUL-GLOBAL", font=f_tv, fill=(245, 158, 11, 90))
    draw.text((80, H - 80), "TRANSMISSION: 4K UHD HDR // MASTER AUDIO 48kHz", font=f_tv, fill=(148, 163, 184, 80))
    draw.text((W - 460, H - 80), "COPYRIGHT © 2026 SUN-ONE AON. ALL RIGHTS RESERVED.", font=f_tv, fill=(148, 163, 184, 80))

    # Save to all target paths
    out_paths = [
        BRANDING_DIR_1 / "banner_2560x1440.png",
        BRANDING_DIR_2 / "banner_2560x1440.png",
        BRANDING_DIR_3 / "banner_2560x1440.png",
        EASY_ACCESS_DIR / "banner_2560x1440.png",
        ROOT / "banner_2560x1440.png"
    ]
    for p in out_paths:
        banner.save(p, format="PNG", optimize=True)
        print(f"  -> Saved Banner: {p} ({p.stat().st_size:,} bytes)")


# ==============================================================================
# 2. RENDER AVATAR (800 x 800) - Strict 400px Circular Safe Radius
# ==============================================================================
def render_avatar():
    print(">>> [2/4] Rendering 800x800 YouTube Master Profile Avatar...")
    S = 800
    avatar = Image.new("RGBA", (S, S), (2, 4, 10, 255))
    draw = ImageDraw.Draw(avatar, "RGBA")

    cx, cy = S // 2, S // 2

    # Radial gradient background
    for r in range(400, 0, -5):
        factor = 1.0 - (r / 400.0)
        cr = int(3 + 18 * factor)
        cg = int(6 + 28 * factor)
        cb = int(14 + 50 * factor)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, 255))

    # Subtle particle sparkles
    draw_stars(draw, S, S, count=70, seed=77)

    # Concentric Cyber Rings (within radius 380px to safely avoid 400px circle cut)
    # Ring 1: Outer dashed telemetry ring (r=375)
    for deg in range(0, 360, 6):
        if (deg % 30) < 18:
            rad1 = math.radians(deg)
            rad2 = math.radians(deg + 5)
            x1 = cx + 372 * math.cos(rad1)
            y1 = cy + 372 * math.sin(rad1)
            x2 = cx + 372 * math.cos(rad2)
            y2 = cy + 372 * math.sin(rad2)
            draw.line([(x1, y1), (x2, y2)], fill=(34, 211, 238, 140), width=2)

    # Ring 2: Golden energy glow ring (r=345)
    for w_off in [-1, 0, 1]:
        draw.ellipse([cx - 345 - w_off, cy - 345 - w_off, cx + 345 + w_off, cy + 345 + w_off], outline=(245, 158, 11, 100), width=1)

    # Ring 3: Cardinal HUD brackets (r=320)
    for deg in [0, 90, 180, 270]:
        rad = math.radians(deg)
        bx = cx + 345 * math.cos(rad)
        by = cy + 345 * math.sin(rad)
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(34, 211, 238, 255))

    # Center Logo 2 (Aqua-Solar Core)
    logo2 = Image.open(LOGO2_PATH).convert("RGBA")
    l2_w, l2_h = logo2.size
    target_w = 420
    target_h = int(l2_h * (target_w / l2_w))
    logo2_resized = logo2.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Place center at (cx, cy - 35)
    avatar.paste(logo2_resized, (cx - target_w // 2, cy - 35 - target_h // 2), logo2_resized)

    # Bottom Branding Pill within circular safe area
    pill_w, pill_h = 320, 52
    pill_x = cx - pill_w // 2
    pill_y = cy + 185
    
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=16, fill=(10, 20, 38, 230), outline=(245, 158, 11, 220), width=2)
    
    f_avatar_title = get_font(FONT_ARIAL_BD, 22)
    f_avatar_kr = get_font(FONT_MALGUN_BD, 15)

    tb1 = draw.textbbox((0, 0), "SUN-ONE AON", font=f_avatar_title)
    draw.text((cx - (tb1[2] - tb1[0]) // 2, pill_y + 6), "SUN-ONE AON", font=f_avatar_title, fill=(245, 158, 11, 255))
    
    tb2 = draw.textbbox((0, 0), "上善若水 · 33% PLEDGE", font=f_avatar_kr)
    draw.text((cx - (tb2[2] - tb2[0]) // 2, pill_y + 30), "上善若水 · 33% PLEDGE", font=f_avatar_kr, fill=(34, 211, 238, 230))

    # Save to all target paths
    out_paths = [
        BRANDING_DIR_1 / "avatar_800x800.png",
        BRANDING_DIR_2 / "avatar_800x800.png",
        BRANDING_DIR_3 / "avatar_800x800.png",
        EASY_ACCESS_DIR / "avatar_800x800.png",
        ROOT / "avatar_800x800.png"
    ]
    for p in out_paths:
        avatar.save(p, format="PNG", optimize=True)
        print(f"  -> Saved Avatar: {p} ({p.stat().st_size:,} bytes)")


# ==============================================================================
# 3. RENDER VIDEO WATERMARK (150x150 & 800x800 Transparent PNG)
# ==============================================================================
def render_watermark():
    print(">>> [3/4] Rendering Transparent Video Watermark (800x800 & 150x150)...")
    S = 800
    wm = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(wm, "RGBA")
    cx, cy = S // 2, S // 2

    # Outer subtle cyber circle
    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline=(34, 211, 238, 180), width=6)
    draw.ellipse([cx - 335, cy - 335, cx + 335, cy + 335], outline=(245, 158, 11, 150), width=4)

    # Logo 2
    logo2 = Image.open(LOGO2_PATH).convert("RGBA")
    l2_w, l2_h = logo2.size
    target_w = 460
    target_h = int(l2_h * (target_w / l2_w))
    logo2_resized = logo2.resize((target_w, target_h), Image.Resampling.LANCZOS)
    wm.paste(logo2_resized, (cx - target_w // 2, cy - 40 - target_h // 2), logo2_resized)

    # Micro branding text
    f_wm = get_font(FONT_ARIAL_BD, 34)
    tb = draw.textbbox((0, 0), "SUN-ONE AON", font=f_wm)
    draw.text((cx - (tb[2] - tb[0]) // 2, cy + 200), "SUN-ONE AON", font=f_wm, fill=(255, 235, 175, 255))

    # Resize to 150x150 for YouTube Studio specification
    wm_150 = wm.resize((150, 150), Image.Resampling.LANCZOS)

    # Save 800x800 & 150x150
    for p800, p150 in [
        (BRANDING_DIR_1 / "watermark_800x800.png", BRANDING_DIR_1 / "watermark_150x150.png"),
        (BRANDING_DIR_2 / "watermark_800x800.png", BRANDING_DIR_2 / "watermark_150x150.png"),
        (BRANDING_DIR_3 / "watermark_800x800.png", BRANDING_DIR_3 / "watermark_150x150.png"),
        (EASY_ACCESS_DIR / "watermark_800x800.png", EASY_ACCESS_DIR / "watermark_150x150.png"),
        (ROOT / "watermark_800x800.png", ROOT / "watermark_150x150.png"),
    ]:
        wm.save(p800, format="PNG", optimize=True)
        wm_150.save(p150, format="PNG", optimize=True)
        print(f"  -> Saved Watermark: {p800} & {p150}")


# ==============================================================================
# 4. RENDER 1080p MASTER THUMBNAILS (1920 x 1080) for Suno V6 Tracks
# ==============================================================================
def render_thumbnails():
    print(">>> [4/4] Rendering 1920x1080 Full HD Video Thumbnails (EP01~EP04)...")
    tracks = [
        {
            "id": "EP01",
            "title_kr": "희망의 등불",
            "title_en": "BEACON OF HOPE",
            "genre": "K-POP ANTHEM BALLAD · 110 BPM",
            "cover": ROOT / "studio_vault" / "CEO_SUNO_V6_ORIGINALS" / "01_BEACON_OF_HOPE_cover.jpeg"
        },
        {
            "id": "EP02",
            "title_kr": "희망의 바다",
            "title_en": "OCEAN OF HOPE",
            "genre": "BROADCAST-QUALITY ANTHEM · 110 BPM",
            "cover": ROOT / "studio_vault" / "CEO_SUNO_V6_ORIGINALS" / "02_OCEAN_OF_HOPE_cover.jpeg"
        },
        {
            "id": "EP03",
            "title_kr": "공식 테마 인스트 #1",
            "title_en": "OFFICIAL THEME INST 1",
            "genre": "FUTURISTIC SYNTHWAVE · 128 BPM",
            "cover": ROOT / "studio_vault" / "CEO_SUNO_V6_ORIGINALS" / "03_OFFICIAL_THEME_INST_1_cover.jpeg"
        },
        {
            "id": "EP04",
            "title_kr": "공식 테마 인스트 #2",
            "title_en": "OFFICIAL THEME INST 2",
            "genre": "COSMIC CHILLWAVE / AMBIENT · 100 BPM",
            "cover": ROOT / "studio_vault" / "CEO_SUNO_V6_ORIGINALS" / "04_OFFICIAL_THEME_INST_2_cover.jpeg"
        }
    ]

    W, H = 1920, 1080

    for trk in tracks:
        thumb = Image.new("RGBA", (W, H), (4, 7, 15, 255))
        draw = ImageDraw.Draw(thumb, "RGBA")

        # 1. Background gradient
        for y in range(H):
            fact = 1.0 - abs(y - H // 2) / (H // 2)
            draw.line([(0, y), (W, y)], fill=(int(6 + 12 * fact), int(10 + 20 * fact), int(22 + 40 * fact), 255))

        draw_stars(draw, W, H, count=90, seed=int(trk["id"][-1]) * 100)

        # 2. Left side: Album Cover Card (800x800)
        card_size = 780
        card_x, card_y = 100, (H - card_size) // 2
        
        # Cover card glow
        draw.rounded_rectangle([card_x - 10, card_y - 10, card_x + card_size + 10, card_y + card_size + 10], radius=24, fill=(34, 211, 238, 40))

        if trk["cover"].is_file():
            cov = Image.open(trk["cover"]).convert("RGBA").resize((card_size, card_size), Image.Resampling.LANCZOS)
            thumb.paste(cov, (card_x, card_y))
        else:
            draw.rounded_rectangle([card_x, card_y, card_x + card_size, card_y + card_size], radius=16, fill=(15, 25, 45, 255))

        # Cover border
        draw.rounded_rectangle([card_x, card_y, card_x + card_size, card_y + card_size], radius=16, outline=(245, 158, 11, 220), width=4)

        # 3. Right side: Title & Metadata Card
        rx = card_x + card_size + 80
        
        # Badges Row (Top)
        badge_y = card_y + 40
        f_badge = get_font(FONT_ARIAL_BD, 18)
        
        badges = [f"SUN-ONE AON {trk['id']}", "OFFICIAL 4K MV", "HI-RES 48kHz / 24-BIT", "SUNO V6 MASTER"]
        bx = rx
        for b in badges:
            tb = draw.textbbox((0, 0), b, font=f_badge)
            bw = tb[2] - tb[0] + 28
            draw.rounded_rectangle([bx, badge_y, bx + bw, badge_y + 36], radius=8, fill=(15, 30, 60, 220), outline=(34, 211, 238, 140), width=2)
            draw.text((bx + 14, badge_y + 7), b, font=f_badge, fill=(34, 211, 238, 255))
            bx += bw + 15

        # Korean Title (Massive Bold)
        f_title_kr = get_font(FONT_MALGUN_BD, 68)
        draw.text((rx, badge_y + 80), trk["title_kr"], font=f_title_kr, fill=(255, 255, 255, 255))

        # English Title
        f_title_en = get_font(FONT_ARIAL_BD, 48)
        draw.text((rx, badge_y + 175), trk["title_en"], font=f_title_en, fill=(245, 158, 11, 255))

        # Genre & Style
        f_genre = get_font(FONT_ARIAL_BD, 26)
        draw.text((rx, badge_y + 250), trk["genre"], font=f_genre, fill=(180, 220, 255, 230))

        # Philosophy & Pledge
        f_phil = get_font(FONT_MALGUN_BD, 24)
        draw.text((rx, badge_y + 310), "상선약수(上善若水) · 東方禮義之國 K-글로벌 문화 주권", font=f_phil, fill=(200, 230, 255, 210))
        
        # Golden Pledge Banner
        p_box_y = badge_y + 380
        draw.rounded_rectangle([rx, p_box_y, W - 100, p_box_y + 70], radius=12, fill=(25, 20, 10, 220), outline=(245, 158, 11, 240), width=2)
        f_pledge = get_font(FONT_ARIAL_BD, 22)
        draw.text((rx + 30, p_box_y + 20), "★ 33% Global Philanthropy Pledge for Humanity & Earth ★", font=f_pledge, fill=(245, 158, 11, 255))

        # Credits
        f_cred = get_font(FONT_ARIAL, 18)
        draw.text((rx, p_box_y + 95), "Executive Producer: Sangill Lee | AI Chief Architect: AON", font=f_cred, fill=(148, 163, 184, 200))

        # Save thumbnail
        thumb_name = f"thumbnail_{trk['id']}_1920x1080.png"
        for out_dir in [BRANDING_DIR_1, BRANDING_DIR_3, EASY_ACCESS_DIR]:
            p = out_dir / thumb_name
            thumb.save(p, format="PNG", optimize=True)
            print(f"  -> Saved Thumbnail: {p}")

if __name__ == "__main__":
    print("======================================================================")
    print(" S1 SUN-ONE AON 2026 YouTube Studio Futuristic Branding Suite Builder ")
    print("======================================================================")
    render_banner()
    render_avatar()
    render_watermark()
    render_thumbnails()
    print(">>> ALL 2026 BRANDING ASSETS SUCCESSFULLY GENERATED & VERIFIED!")

