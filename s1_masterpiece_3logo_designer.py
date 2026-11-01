# -*- coding: utf-8 -*-
"""
SUN-ONE AON 2026 Masterpiece 3-Logo Synergy Designer
(s1_masterpiece_3logo_designer.py)
==================================================
Physically synthesizes the 3 high-res original logos (s1_logo_1, 2, 3)
and Suno V6 artwork into world-class, 2026 futuristic YouTube Studio assets:
- avatar_800x800.png (Golden Rim + Aqua-Solar Core)
- banner_2560x1440.png (Suno V6 Cinematic Ocean Haze + Strict 1546x423 Safe Area + 3-Logo Trinity)
- watermark_800x800.png & watermark_150x150.png (Crest + Subscribe Pill)
"""

import os
import sys
import math
import random
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent

LOGO1_PATH = ROOT / "s1_logo_1_clean.png"
LOGO2_PATH = ROOT / "s1_logo_2_clean.png"
LOGO3_PATH = ROOT / "s1_logo_3_clean.png"
COVER_PATH = ROOT / "studio_vault" / "CEO_SUNO_V6_ORIGINALS" / "01_BEACON_OF_HOPE_cover.jpeg"

TARGET_DIRS = [
    ROOT / "studio_vault" / "CHANNELS" / "04_US_SUNONE_AON" / "BRANDING_KIT",
    ROOT / "studio_vault" / "US_AON_VAULT" / "BRANDING_KIT",
    ROOT / "assets" / "channel_branding_2026",
    pathlib.Path("C:/Users/sangi/Downloads/SUNONE_AON_YOUTUBE_BRANDING"),
    ROOT
]

for d in TARGET_DIRS:
    d.mkdir(parents=True, exist_ok=True)

FONT_MALGUN_BD = "C:/WINDOWS/Fonts/malgunbd.ttf"
FONT_ARIAL_BD = "C:/WINDOWS/Fonts/arialbd.ttf"
FONT_ARIAL = "C:/WINDOWS/Fonts/arial.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def save_to_all(img, filename, format="PNG"):
    for d in TARGET_DIRS:
        p = d / filename
        img.save(p, format=format, optimize=True)
        print(f"  -> Saved {filename}: {p} ({p.stat().st_size:,} bytes)")

# ==============================================================================
# 1. PROFILE AVATAR (800 x 800)
# ==============================================================================
def create_masterpiece_avatar():
    print(">>> [1/3] Generating Masterpiece Profile Avatar (avatar_800x800.png)...")
    S = 800
    avatar = Image.new("RGBA", (S, S), (3, 6, 14, 255))
    draw = ImageDraw.Draw(avatar, "RGBA")
    cx, cy = S // 2, S // 2

    # Radial gradient background
    for r in range(400, 0, -4):
        factor = 1.0 - (r / 400.0)
        cr = int(3 + 22 * factor)
        cg = int(7 + 35 * factor)
        cb = int(16 + 65 * factor)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, 255))

    # Golden Rim & Cyber Neon Rings (Safe within radius 380px)
    # 1. Outer Golden Glow (r=365)
    for w_off in range(-2, 3):
        alpha = int(180 * (1.0 - abs(w_off) / 3.0))
        draw.ellipse([cx - 365 - w_off, cy - 365 - w_off, cx + 365 + w_off, cy + 365 + w_off], outline=(245, 158, 11, alpha), width=2)

    # 2. Cyan Orbit Dashes (r=345)
    for deg in range(0, 360, 8):
        if (deg % 30) < 18:
            rad1 = math.radians(deg)
            rad2 = math.radians(deg + 5)
            x1 = cx + 345 * math.cos(rad1)
            y1 = cy + 345 * math.sin(rad1)
            x2 = cx + 345 * math.cos(rad2)
            y2 = cy + 345 * math.sin(rad2)
            draw.line([(x1, y1), (x2, y2)], fill=(34, 211, 238, 180), width=2)

    # 3. Cardinal Gold Markers (r=345)
    for deg in [0, 90, 180, 270]:
        rad = math.radians(deg)
        bx = cx + 345 * math.cos(rad)
        by = cy + 345 * math.sin(rad)
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(245, 158, 11, 255))

    # Center Logo 2 (Aqua-Solar Core)
    logo2 = Image.open(LOGO2_PATH).convert("RGBA")
    l2_w, l2_h = logo2.size
    target_w = 460
    target_h = int(l2_h * (target_w / l2_w))
    logo2_resized = logo2.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Golden bloom glow behind Logo 2
    glow_mask = logo2_resized.split()[3].filter(ImageFilter.GaussianBlur(15))
    glow_layer = Image.new("RGBA", (target_w, target_h), (245, 158, 11, 160))
    avatar.paste(glow_layer, (cx - target_w // 2, cy - 40 - target_h // 2), glow_mask)
    avatar.paste(logo2_resized, (cx - target_w // 2, cy - 40 - target_h // 2), logo2_resized)

    # Bottom Branding Capsule within circular boundary
    pill_w, pill_h = 320, 56
    pill_x = cx - pill_w // 2
    pill_y = cy + 185
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=18, fill=(8, 16, 32, 230), outline=(245, 158, 11, 230), width=2)

    f_title = get_font(FONT_ARIAL_BD, 23)
    f_kr = get_font(FONT_MALGUN_BD, 15)

    tb1 = draw.textbbox((0, 0), "SUN-ONE AON", font=f_title)
    draw.text((cx - (tb1[2] - tb1[0]) // 2, pill_y + 7), "SUN-ONE AON", font=f_title, fill=(245, 158, 11, 255))
    
    tb2 = draw.textbbox((0, 0), "上善若水 · 33% PLEDGE", font=f_kr)
    draw.text((cx - (tb2[2] - tb2[0]) // 2, pill_y + 32), "上善若水 · 33% PLEDGE", font=f_kr, fill=(34, 211, 238, 230))

    save_to_all(avatar, "avatar_800x800.png")

# ==============================================================================
# 2. CHANNEL WIDE BANNER (2560 x 1440) - Strict 1546x423 Safe Area
# ==============================================================================
def create_masterpiece_banner():
    print(">>> [2/3] Generating Masterpiece Channel Wide Banner (banner_2560x1440.png)...")
    W, H = 2560, 1440
    banner = Image.new("RGBA", (W, H), (2, 4, 10, 255))

    # Base: Suno V6 Artwork with Cinematic Blur & Deep Navy Vignette
    if COVER_PATH.is_file():
        cov = Image.open(COVER_PATH).convert("RGBA")
        # Resize to cover whole canvas
        cov_scaled = cov.resize((W, H), Image.Resampling.LANCZOS)
        # Apply cinematic blur
        cov_blurred = cov_scaled.filter(ImageFilter.GaussianBlur(16))
        # Darken with deep cosmic overlay
        overlay = Image.new("RGBA", (W, H), (4, 10, 24, 195))
        cov_dark = Image.alpha_composite(cov_blurred, overlay)
        banner.paste(cov_dark, (0, 0))
    else:
        # Fallback dark gradient
        draw_b = ImageDraw.Draw(banner)
        for y in range(H):
            draw_b.line([(0, y), (W, y)], fill=(4, 10, 24, 255))

    draw = ImageDraw.Draw(banner, "RGBA")

    # Cosmic Dust & Stars
    random.seed(99)
    for _ in range(180):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.choice([1, 1, 2, 2, 3])
        tint = random.choice([
            (245, 158, 11, random.randint(100, 220)),
            (34, 211, 238, random.randint(100, 220)),
            (255, 255, 255, random.randint(150, 255))
        ])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=tint)

    # Safe Area Coordinates: 1546 x 423 (x: 507 to 2053, y: 508 to 931)
    SX0, SY0 = 507, 508
    SX1, SY1 = 2053, 931
    SAFE_W, SAFE_H = SX1 - SX0, SY1 - SY0
    CENTER_Y = (SY0 + SY1) // 2

    # Glassmorphism Safe Area Container
    panel = Image.new("RGBA", (SAFE_W, SAFE_H), (6, 14, 30, 205))
    pdraw = ImageDraw.Draw(panel, "RGBA")
    # Outer Cyan Rim
    pdraw.rounded_rectangle([0, 0, SAFE_W - 1, SAFE_H - 1], radius=20, outline=(34, 211, 238, 120), width=2)
    # Inner Gold Rim
    pdraw.rounded_rectangle([4, 4, SAFE_W - 5, SAFE_H - 5], radius=18, outline=(245, 158, 11, 60), width=1)

    # Corner brackets
    blen = 32
    # TL
    pdraw.line([(0, 0), (blen, 0)], fill=(245, 158, 11, 255), width=4)
    pdraw.line([(0, 0), (0, blen)], fill=(245, 158, 11, 255), width=4)
    # TR
    pdraw.line([(SAFE_W - blen, 0), (SAFE_W, 0)], fill=(245, 158, 11, 255), width=4)
    pdraw.line([(SAFE_W, 0), (SAFE_W, blen)], fill=(245, 158, 11, 255), width=4)
    # BL
    pdraw.line([(0, SAFE_H), (blen, SAFE_H)], fill=(245, 158, 11, 255), width=4)
    pdraw.line([(0, SAFE_H - blen), (0, SAFE_H)], fill=(245, 158, 11, 255), width=4)
    # BR
    pdraw.line([(SAFE_W - blen, SAFE_H), (SAFE_W, SAFE_H)], fill=(245, 158, 11, 255), width=4)
    pdraw.line([(SAFE_W, SAFE_H - blen), (SAFE_W, SAFE_H)], fill=(245, 158, 11, 255), width=4)

    banner.paste(panel, (SX0, SY0), panel)

    # -------------------------------------------------------------
    # LEFT: LOGO 2 (Aqua-Solar Core / 상선약수)
    # -------------------------------------------------------------
    core_cx = SX0 + 210
    core_cy = CENTER_Y - 18
    # Cyan/Gold concentric aura
    draw.ellipse([core_cx - 130, core_cy - 130, core_cx + 130, core_cy + 130], outline=(34, 211, 238, 140), width=2)
    draw.ellipse([core_cx - 110, core_cy - 110, core_cx + 110, core_cy + 110], outline=(245, 158, 11, 100), width=1)

    logo2 = Image.open(LOGO2_PATH).convert("RGBA")
    l2_w, l2_h = logo2.size
    target_l2_w = 240
    target_l2_h = int(l2_h * (target_l2_w / l2_w))
    logo2_res = logo2.resize((target_l2_w, target_l2_h), Image.Resampling.LANCZOS)
    banner.paste(logo2_res, (core_cx - target_l2_w // 2, core_cy - target_l2_h // 2), logo2_res)

    f_l_sm = get_font(FONT_ARIAL_BD, 13)
    f_l_kr = get_font(FONT_MALGUN_BD, 15)
    draw.text((core_cx - 88, core_cy + 120), "◈ AQUA-SOLAR CORE ◈", font=f_l_sm, fill=(34, 211, 238, 240))
    draw.text((core_cx - 75, core_cy + 142), "상선약수 (上善若水)", font=f_l_kr, fill=(245, 158, 11, 255))

    # -------------------------------------------------------------
    # RIGHT: LOGO 3 (Imperial Crest / 33% Global Philanthropy)
    # -------------------------------------------------------------
    crest_cx = SX1 - 210
    crest_cy = CENTER_Y - 18
    draw.ellipse([crest_cx - 130, crest_cy - 130, crest_cx + 130, crest_cy + 130], outline=(245, 158, 11, 150), width=2)
    draw.ellipse([crest_cx - 110, crest_cy - 110, crest_cx + 110, crest_cy + 110], outline=(34, 211, 238, 90), width=1)

    logo3 = Image.open(LOGO3_PATH).convert("RGBA")
    l3_w, l3_h = logo3.size
    target_l3_h = 205
    target_l3_w = int(l3_w * (target_l3_h / l3_h))
    logo3_res = logo3.resize((target_l3_w, target_l3_h), Image.Resampling.LANCZOS)
    banner.paste(logo3_res, (crest_cx - target_l3_w // 2, crest_cy - target_l3_h // 2), logo3_res)

    draw.text((crest_cx - 110, crest_cy + 120), "★ SOVEREIGN IMPERIAL SEAL ★", font=f_l_sm, fill=(245, 158, 11, 240))
    draw.text((crest_cx - 96, crest_cy + 142), "글로벌 환원의 국제화 (33%)", font=f_l_kr, fill=(34, 211, 238, 240))

    # -------------------------------------------------------------
    # CENTER: LOGO 1 + 2026 WORLD-CLASS TYPOGRAPHY
    # -------------------------------------------------------------
    center_cx = SX0 + SAFE_W // 2
    logo1 = Image.open(LOGO1_PATH).convert("RGBA")
    l1_w, l1_h = logo1.size
    target_l1_w = 510
    target_l1_h = int(l1_h * (target_l1_w / l1_w))
    logo1_res = logo1.resize((target_l1_w, target_l1_h), Image.Resampling.LANCZOS)
    l1_x = center_cx - target_l1_w // 2
    l1_y = SY0 + 25
    banner.paste(logo1_res, (l1_x, l1_y), logo1_res)

    f_s1 = get_font(FONT_ARIAL_BD, 25)
    f_s2 = get_font(FONT_MALGUN_BD, 21)
    f_s3 = get_font(FONT_ARIAL_BD, 17)
    f_s4 = get_font(FONT_ARIAL, 14)

    def draw_ctext(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((center_cx - tw // 2, y), text, font=font, fill=fill)

    base_y = l1_y + target_l1_h + 8
    draw_ctext(base_y, "GLOBAL K-ETHICS AI MUSIC & STORY STUDIO", f_s1, (255, 235, 175, 255))
    draw_ctext(base_y + 34, "東方禮義之國의 품격과 상선약수(上善若水)의 감성", f_s2, (210, 245, 255, 240))
    draw_ctext(base_y + 68, "★ 33% Global Philanthropy Pledge for Humanity & Earth ★", f_s3, (245, 158, 11, 255))
    draw_ctext(base_y + 98, "Executive Producer: Sangill Lee | AI Chief Architect: AON", f_s4, (148, 163, 184, 210))

    # Badges Row
    badge_y = base_y + 124
    badges = ["48kHz / 24-BIT MASTER", "DISTROKID 2-SLOT", "SUNO V6 MAESTRO", "@SUN-ONEAON"]
    f_b = get_font(FONT_ARIAL_BD, 11)
    tot_w = len(badges) * 165
    cur_x = center_cx - tot_w // 2
    for b in badges:
        bw, bh = 150, 22
        draw.rounded_rectangle([cur_x, badge_y, cur_x + bw, badge_y + bh], radius=6, fill=(15, 30, 55, 200), outline=(34, 211, 238, 90))
        tb = draw.textbbox((0, 0), b, font=f_b)
        draw.text((cur_x + (bw - (tb[2] - tb[0])) // 2, badge_y + 4), b, font=f_b, fill=(34, 211, 238, 230))
        cur_x += 165

    # TV Ambient Borders
    f_tv = get_font(FONT_ARIAL_BD, 14)
    draw.text((80, 60), "SUN-ONE AON // K-GLOBAL CULTURAL SOVEREIGNTY", font=f_tv, fill=(34, 211, 238, 100))
    draw.text((W - 460, 60), "LAT 37.5665° N / LON 126.9780° E // SEOUL-GLOBAL", font=f_tv, fill=(245, 158, 11, 100))
    draw.text((80, H - 80), "TRANSMISSION: 4K UHD HDR // MASTER AUDIO 48kHz", font=f_tv, fill=(148, 163, 184, 90))
    draw.text((W - 460, H - 80), "COPYRIGHT © 2026 SUN-ONE AON. ALL RIGHTS RESERVED.", font=f_tv, fill=(148, 163, 184, 90))

    save_to_all(banner, "banner_2560x1440.png")

# ==============================================================================
# 3. VIDEO WATERMARK (800 x 800 & 150 x 150)
# ==============================================================================
def create_masterpiece_watermark():
    print(">>> [3/3] Generating Masterpiece Video Watermark (watermark_800x800.png & 150x150.png)...")
    S = 800
    wm = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(wm, "RGBA")
    cx, cy = S // 2, S // 2

    # Circular Badge
    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], fill=(8, 16, 32, 220), outline=(245, 158, 11, 200), width=6)
    draw.ellipse([cx - 335, cy - 335, cx + 335, cy + 335], outline=(34, 211, 238, 160), width=3)

    # Logo 3 (Imperial Crest)
    logo3 = Image.open(LOGO3_PATH).convert("RGBA")
    l3_w, l3_h = logo3.size
    target_w = 420
    target_h = int(l3_h * (target_w / l3_w))
    logo3_res = logo3.resize((target_w, target_h), Image.Resampling.LANCZOS)
    wm.paste(logo3_res, (cx - target_w // 2, cy - 40 - target_h // 2), logo3_res)

    # Subscribe Pill
    pill_w, pill_h = 360, 68
    pill_x = cx - pill_w // 2
    pill_y = cy + 180
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=20, fill=(220, 38, 38, 255), outline=(245, 158, 11, 255), width=3)

    f_sub = get_font(FONT_ARIAL_BD, 34)
    tb = draw.textbbox((0, 0), "SUBSCRIBE", font=f_sub)
    draw.text((cx - (tb[2] - tb[0]) // 2, pill_y + 14), "SUBSCRIBE", font=f_sub, fill=(255, 255, 255, 255))

    save_to_all(wm, "watermark_800x800.png")

    wm_150 = wm.resize((150, 150), Image.Resampling.LANCZOS)
    save_to_all(wm_150, "watermark_150x150.png")

if __name__ == "__main__":
    print("======================================================================")
    print(" S1 2026 Masterpiece 3-Logo YouTube Studio Designer Running...         ")
    print("======================================================================")
    create_masterpiece_avatar()
    create_masterpiece_banner()
    create_masterpiece_watermark()
    print(">>> 3-LOGO MASTERPIECE ASSETS CREATED SUCCESSFULLY!")
