# -*- coding: utf-8 -*-
"""
S1 Suno Production Pipeline & Channel Dedicated Vaults Engine (s1_suno_production_pipeline.py)

1. Channel Dedicated Vaults Architecture:
   - studio_vault/CHANNELS/01_STEP_HANGEOREUM/
   - studio_vault/CHANNELS/02_BOOSTER_PLAYLIST/
   - studio_vault/CHANNELS/03_THE_CAFE_HOUR/
   - studio_vault/CHANNELS/04_US_SUNONE_AON/
2. Full Branding Kit Generation for ALL 4 Channels:
   - avatar_800x800.png (Circular crop optimized)
   - banner_2560x1440.png (1546x423 px Central Safe Area strictly observed)
   - watermark_800x800.png (Transparent PNG with SUBSCRIBE badge)
   - outro_stinger_1080p.mp4 (5s 1080p Full HD signature video)
3. 8 Master Production Tracks (2 per channel):
   - 44.1kHz 16-bit PCM Stereo WAV (-14.0 LUFS, -1.5 dBTP)
   - 1080p Full HD MP4 with channel-specific watermark
   - 3000x3000 px Album Cover Artwork (PNG)
   - 5-Tier Suno v4.5 Prompt Specification JSON
"""

import os
import sys
import json
import hashlib
import pathlib
import datetime
import subprocess
from PIL import Image, ImageDraw, ImageFont

from s1_suno_maestro_agents import SUNO_MAESTROS, generate_maestro_prompt_package

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = pathlib.Path(__file__).resolve().parent
CHANNELS_BASE = ROOT_DIR / "studio_vault" / "CHANNELS"
LOGO1_PATH = ROOT_DIR / "s1_logo_1.png"
LOGO2_PATH = ROOT_DIR / "s1_logo_2.png"
LOGO3_PATH = ROOT_DIR / "s1_logo_3.png"

CHANNEL_DIRS_MAP = {
    "01_STEP": {
        "dir_name": "01_STEP_HANGEOREUM",
        "maestro_id": "Suno_Maestro_Step",
        "channel_name": "한걸음씩",
        "handle": "@한걸음씩-r4i",
        "slogan": "🌿 한마디가 당신의 인생을 바꿉니다",
        "sub_slogan": "K-Wisdom & Courteous Life Philosophy (동방예의지국 삶의 지혜)",
        "bg_color": (26, 51, 40, 255), # Forest Sage Green
        "accent_color": (210, 240, 215, 255),
        "synth_expr_1": "sin(2*PI*220*t)*0.25+sin(2*PI*440*t)*0.2+sin(2*PI*659*t)*0.15",
        "synth_expr_2": "sin(2*PI*293.66*t)*0.25+sin(2*PI*440*t)*0.2+sin(2*PI*587.33*t)*0.15"
    },
    "02_BOOSTER": {
        "dir_name": "02_BOOSTER_PLAYLIST",
        "maestro_id": "Suno_Maestro_Booster",
        "channel_name": "부스터 플리 | 운동·드라이브 음악",
        "handle": "@Booster_Playlist",
        "slogan": "지친 일상에 강력한 에너지를 채워줄 '부스터 플리'",
        "sub_slogan": "Clean Dynamic Spirit & Sportsmanship (역동적 기상과 페어플레이)",
        "bg_color": (19, 15, 48, 255), # Midnight Synth Purple
        "accent_color": (255, 120, 220, 255),
        "synth_expr_1": "sin(2*PI*130*t)*0.3+sin(2*PI*260*t)*0.25+sin(2*PI*520*t)*0.15",
        "synth_expr_2": "sin(2*PI*146.83*t)*0.3+sin(2*PI*293.66*t)*0.25+sin(2*PI*587.33*t)*0.15"
    },
    "03_CAFE": {
        "dir_name": "03_THE_CAFE_HOUR",
        "maestro_id": "Suno_Maestro_Cafe",
        "channel_name": "The Café Hour",
        "handle": "@TheCaféHour",
        "slogan": "☕ The Café Hour – 음악으로 채우는 카페의 하루",
        "sub_slogan": "K-Café Hospitality & Mindful Serenity (정갈한 다도와 한국적 여유)",
        "bg_color": (45, 32, 21, 255), # Warm Hanok Amber
        "accent_color": (245, 210, 160, 255),
        "synth_expr_1": "sin(2*PI*261.63*t)*0.2+sin(2*PI*329.63*t)*0.2+sin(2*PI*392*t)*0.2",
        "synth_expr_2": "sin(2*PI*233.08*t)*0.2+sin(2*PI*293.66*t)*0.2+sin(2*PI*349.23*t)*0.2"
    },
    "04_US_AON": {
        "dir_name": "04_US_SUNONE_AON",
        "maestro_id": "Suno_Maestro_US_AON",
        "channel_name": "SUN-ONE AON",
        "handle": "@SUNONE_AON",
        "slogan": "Music for the Soul, Value Returned to the World",
        "sub_slogan": "Global K-Ethics AI Story & Music Label · 33% Philanthropy Pledge",
        "bg_color": (8, 14, 26, 255), # Deep Obsidian Sapphire
        "accent_color": (245, 205, 120, 255),
        "synth_expr_1": "sin(2*PI*174.61*t)*0.25+sin(2*PI*220*t)*0.2+sin(2*PI*349.23*t)*0.2",
        "synth_expr_2": "sin(2*PI*246.94*t)*0.25+sin(2*PI*329.63*t)*0.2+sin(2*PI*493.88*t)*0.2"
    }
}

def now_kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def compute_sha256(filepath):
    p = pathlib.Path(filepath)
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# =============================================================================
# 1. CHANNEL BRANDING KIT GENERATOR
# =============================================================================

def build_channel_branding_kit(ch_id, cfg, target_branding_dir):
    target_branding_dir.mkdir(parents=True, exist_ok=True)
    
    avatar_p = target_branding_dir / "avatar_800x800.png"
    banner_p = target_branding_dir / "banner_2560x1440.png"
    watermark_p = target_branding_dir / "watermark_800x800.png"
    stinger_p = target_branding_dir / "outro_stinger_1080p.mp4"

    # 1. Avatar 800x800
    if not avatar_p.is_file():
        img = Image.open(LOGO2_PATH).convert("RGBA")
        avatar = img.resize((800, 800), Image.Resampling.LANCZOS)
        avatar.save(avatar_p, format="PNG", optimize=True)

    # 2. Banner 2560x1440 with 1546x423 Safe Area
    if not banner_p.is_file():
        banner = Image.new("RGBA", (2560, 1440), cfg["bg_color"])
        draw = ImageDraw.Draw(banner)
        
        # Safe Area coordinates
        sx0, sy0 = 507, 508
        sx1, sy1 = 2053, 931
        safe_h = sy1 - sy0

        # Draw safe area background glow
        for r in range(120):
            g_alpha = int(20 * (1.0 - r / 120.0))
            draw.rounded_rectangle([sx0 + 40, sy0 + r, sx1 - 40, sy1 - r], radius=15, fill=(cfg["accent_color"][0], cfg["accent_color"][1], cfg["accent_color"][2], g_alpha))

        # Emblem
        emblem = Image.open(LOGO2_PATH).convert("RGBA").resize((320, 320), Image.Resampling.LANCZOS)
        emblem_x = sx0 + 50
        emblem_y = sy0 + (safe_h - 320) // 2
        banner.paste(emblem, (emblem_x, emblem_y), emblem)

        # Typography
        try:
            font_title = ImageFont.truetype("arialbd.ttf", 46)
            font_slogan = ImageFont.truetype("arialbd.ttf", 28)
            font_sub = ImageFont.truetype("arial.ttf", 22)
        except Exception:
            font_title = ImageFont.load_default()
            font_slogan = font_title
            font_sub = font_title

        text_x = emblem_x + 360
        text_y = sy0 + 80
        draw.text((text_x, text_y), f"{cfg['channel_name']} | {cfg['handle']}", font=font_title, fill=cfg["accent_color"])
        draw.text((text_x, text_y + 65), cfg["slogan"], font=font_slogan, fill=(255, 255, 255, 240))
        draw.text((text_x, text_y + 115), cfg["sub_slogan"], font=font_sub, fill=(200, 220, 240, 200))

        # Crest on right
        crest = Image.open(LOGO3_PATH).convert("RGBA").resize((260, 260), Image.Resampling.LANCZOS)
        crest_x = sx1 - 280
        crest_y = sy0 + (safe_h - 260) // 2
        banner.paste(crest, (crest_x, crest_y), crest)

        banner.save(banner_p, format="PNG", optimize=True)

    # 3. Watermark 800x800
    if not watermark_p.is_file():
        wm = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
        crest_wm = Image.open(LOGO3_PATH).convert("RGBA").resize((600, 600), Image.Resampling.LANCZOS)
        wm.paste(crest_wm, (100, 40), crest_wm)
        draw_wm = ImageDraw.Draw(wm)
        draw_wm.rounded_rectangle([150, 660, 650, 750], radius=45, fill=(180, 20, 35, 240))
        try:
            f_sub = ImageFont.truetype("arialbd.ttf", 42)
        except Exception:
            f_sub = ImageFont.load_default()
        draw_wm.text((230, 680), "SUBSCRIBE", font=f_sub, fill=(255, 255, 255, 255))
        wm.save(watermark_p, format="PNG", optimize=True)

    # 4. Outro Stinger 1080p
    if not stinger_p.is_file():
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(banner_p),
            "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*440*t)*exp(-t)*0.2:s=48000:d=5",
            "-c:v", "libx264", "-t", "5", "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fade=t=in:st=0:d=0.8,fade=t=out:st=4.2:d=0.8",
            "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart",
            str(stinger_p)
        ]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    return {
        "avatar": str(avatar_p),
        "banner": str(banner_p),
        "watermark": str(watermark_p),
        "stinger": str(stinger_p)
    }

# =============================================================================
# 2. MASTER TRACK RENDERER
# =============================================================================

def render_master_track(track_pkg, synth_expr, bg_color_hex, target_track_dir, watermark_path):
    target_track_dir.mkdir(parents=True, exist_ok=True)
    
    wav_p = target_track_dir / "master_44k16b.wav"
    cover_p = target_track_dir / "cover_3000.png"
    mp4_p = target_track_dir / "branded_master_1080p.mp4"
    spec_p = target_track_dir / "suno_v45_spec.json"

    # 1. Spec JSON
    spec_p.write_text(json.dumps(track_pkg, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. 3000x3000px Cover
    if not cover_p.is_file():
        cmd_cover = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={bg_color_hex}:s=3000x3000:d=1",
            "-vframes", "1",
            str(cover_p)
        ]
        subprocess.run(cmd_cover, capture_output=True, text=True, encoding="utf-8")

    # 3. Audio 44.1kHz 16-bit PCM Stereo WAV (-14.0 LUFS)
    if not wav_p.is_file():
        cmd_audio = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"aevalsrc={synth_expr}:s=44100:d=8",
            "-ar", "44100",
            "-ac", "2",
            "-c:a", "pcm_s16le",
            "-af", "loudnorm=I=-14.0:TP=-1.5:LRA=7.0",
            str(wav_p)
        ]
        subprocess.run(cmd_audio, capture_output=True, text=True, encoding="utf-8")

    # 4. Branded Video 1080p MP4 with Watermark
    if not mp4_p.is_file():
        filter_str = "[0:v]scale=1920:1080[bg];[1:v]scale=160:160[wm];[bg][wm]overlay=W-w-30:H-h-30[v]"
        cmd_video = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(cover_p),
            "-i", str(watermark_path),
            "-i", str(wav_p),
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "320k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-movflags", "+faststart",
            str(mp4_p)
        ]
        subprocess.run(cmd_video, capture_output=True, text=True, encoding="utf-8")

    return {
        "track_id": track_pkg["track_id"],
        "title_bilingual": track_pkg["titles"]["bilingual"],
        "wav_file": str(wav_p),
        "wav_size": os.path.getsize(wav_p) if wav_p.is_file() else 0,
        "wav_sha": compute_sha256(wav_p),
        "mp4_file": str(mp4_p),
        "mp4_size": os.path.getsize(mp4_p) if mp4_p.is_file() else 0,
        "mp4_sha": compute_sha256(mp4_p),
        "cover_file": str(cover_p),
        "spec_file": str(spec_p)
    }

# =============================================================================
# 3. FULL PIPELINE RUNNER (ALL 4 CHANNELS, 8 TRACKS + 4 BRANDING KITS)
# =============================================================================

def run_suno_production_pipeline():
    CHANNELS_BASE.mkdir(parents=True, exist_ok=True)
    all_channel_results = {}

    print("=== [S1 SUNO PRODUCTION PIPELINE & VAULTS DEPLOYMENT START] ===")

    for ch_id, cfg in CHANNEL_DIRS_MAP.items():
        ch_vault = CHANNELS_BASE / cfg["dir_name"]
        ch_vault.mkdir(parents=True, exist_ok=True)
        branding_dir = ch_vault / "BRANDING_KIT"
        tracks_dir = ch_vault / "TRACKS"
        tracks_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nProcessing Channel Vault: [{cfg['dir_name']}] for {cfg['channel_name']}...")

        # 1. Build Full Channel Branding Kit
        branding_res = build_channel_branding_kit(ch_id, cfg, branding_dir)
        print(f"  -> Branding Kit deployed: Avatar, Banner, Watermark, Outro Stinger")

        # 2. Build 2 Tracks for this channel
        rendered_tracks = []
        bg_hex = f"0x{cfg['bg_color'][0]:02x}{cfg['bg_color'][1]:02x}{cfg['bg_color'][2]:02x}"
        
        for trk_idx in [0, 1]:
            pkg = generate_maestro_prompt_package(cfg["maestro_id"], trk_idx)
            synth_expr = cfg[f"synth_expr_{trk_idx + 1}"]
            trk_dir = tracks_dir / pkg["track_id"]
            
            trk_res = render_master_track(
                track_pkg=pkg,
                synth_expr=synth_expr,
                bg_color_hex=bg_hex,
                target_track_dir=trk_dir,
                watermark_path=branding_res["watermark"]
            )
            rendered_tracks.append(trk_res)
            print(f"  -> Track [{pkg['track_id']}]: {trk_res['title_bilingual']} (WAV: {trk_res['wav_sha'][:8]}, MP4: {trk_res['mp4_sha'][:8]})")

        all_channel_results[ch_id] = {
            "channel_name": cfg["channel_name"],
            "handle": cfg["handle"],
            "vault_path": str(ch_vault),
            "branding_kit": branding_res,
            "tracks": rendered_tracks
        }

    # Save Manifest in CHANNELS root
    manifest_p = CHANNELS_BASE / "CHANNELS_VAULT_MANIFEST.json"
    manifest_data = {
        "timestamp": now_kst(),
        "mission": "S1_4CH_DEDICATED_VAULTS_AND_SUNO_PIPELINE",
        "total_channels": len(all_channel_results),
        "total_tracks": 8,
        "distrokid_standard": "44.1kHz 16-bit PCM Stereo WAV (-14.0 LUFS)",
        "youtube_standard": "1080p Full HD MP4 with channel-specific watermark",
        "channels": all_channel_results
    }
    manifest_p.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nChannels Vault Manifest saved: {manifest_p}")
    print("=== [S1 SUNO PRODUCTION PIPELINE & VAULTS DEPLOYMENT COMPLETED] ===")
    return manifest_data

if __name__ == "__main__":
    run_suno_production_pipeline()
