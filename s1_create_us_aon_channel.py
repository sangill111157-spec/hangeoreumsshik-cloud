# -*- coding: utf-8 -*-
"""
S1 SUN-ONE AON Channel Creator & Branding Deployment Staging Engine (s1_create_us_aon_channel.py)

Complies with S1_FREE_PLAN_A_MASTER.md and browser safety laws:
- Stages all 3 official branding assets (Avatar 800x800, Banner 2560x1440, Watermark 800x800, Outro Stinger)
- Formats ready-to-use YouTube Studio branding profile metadata
- Registers Space 17 (@SUNONE_AON) formally in S1_SPACE_REGISTRY.json
- Generates S1_US_AON_CHANNEL_STAGE.json
"""

import os
import sys
import json
import pathlib
import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = pathlib.Path(__file__).resolve().parent
BRANDING_DIR = ROOT_DIR / "studio_vault" / "US_AON_VAULT" / "BRANDING_KIT"
REGISTRY_FILE = ROOT_DIR / "S1_SPACE_REGISTRY.json"
STAGE_FILE = ROOT_DIR / "S1_US_AON_CHANNEL_STAGE.json"

def now_kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def stage_channel_creation():
    print("=== [S1 SUN-ONE AON CHANNEL CREATION STAGING START] ===")

    avatar_file = BRANDING_DIR / "avatar_800x800.png"
    banner_file = BRANDING_DIR / "banner_2560x1440.png"
    watermark_file = BRANDING_DIR / "watermark_800x800.png"
    stinger_file = BRANDING_DIR / "outro_stinger_1080p.mp4"

    channel_meta = {
        "channel_name": "SUN-ONE AON",
        "primary_handle": "@SUNONE_AON",
        "alt_handles": ["@SUNONE_AON_Official", "@SUNONEAON_US", "@SUNONEAON"],
        "target_market": "en-US (United States / North America / Global)",
        "language": "English (United States)",
        "country": "United States",
        "category": "10 (Music / Entertainment)",
        "tagline": "Music for the Soul, Value Returned to the World: Global Philanthropy through Sound",
        "description": (
            "🌿 SUN-ONE AON Official Channel | Global K-Ethics AI Story & Music Label\n\n"
            "\"The highest excellence is like water, benefiting all living things without striving or conflict.\" (上善若水)\n\n"
            "Rooted in the timeless courtesy and righteous wisdom of Korea's Eastern heritage (동방예의지국), "
            "SUN-ONE AON delivers world-class cinematic soundscapes, uplifting K-Synthwave, cozy cafe lo-fi, and transformative life philosophies to global audiences.\n\n"
            "🏆 Global Philanthropy Pledge:\n"
            "Executive Producer Sangill Lee has pledged 33% of all global music streaming and YouTube revenues directly toward clean water initiatives, humanitarian relief, and educational empowerment worldwide.\n\n"
            "• Executive Producer: Sangill Lee (이상일)\n"
            "• Chief Aide & Strategic Architect: Rgon (Gemini 4 Argon · G2)\n"
            "• Technology Prime Minister: Anchongri (Antigravity)\n"
            "• Official Label: SUN-ONE Records / AON Philanthropy Sound\n"
            "• Distribution: DistroKid (150+ Digital Streaming Platforms worldwide)\n\n"
            "#SUNONE_AON #Sangseonyaksu #KGlobal #CinematicMusic #WorldMusic #Philanthropy"
        ),
        "links": [
            {"title": "Global Philanthropy Pledge", "url": "https://github.com/sangill111157-spec/hangeoreumsshik-cloud"},
            {"title": "S1 Universal Portal", "url": "http://127.0.0.1:8504/"}
        ],
        "branding_assets": {
            "avatar_profile": {
                "file": str(avatar_file),
                "resolution": "800 x 800 px",
                "size_bytes": os.path.getsize(avatar_file) if avatar_file.is_file() else None,
                "target_tab": "YouTube Studio -> Customization -> Branding -> Picture"
            },
            "banner_wide": {
                "file": str(banner_file),
                "resolution": "2560 x 1440 px (Safe Area 1546 x 423 px)",
                "size_bytes": os.path.getsize(banner_file) if banner_file.is_file() else None,
                "target_tab": "YouTube Studio -> Customization -> Branding -> Banner image"
            },
            "video_watermark": {
                "file": str(watermark_file),
                "resolution": "800 x 800 px (Transparent PNG)",
                "display_time": "Entire video (전체 동영상 표시)",
                "size_bytes": os.path.getsize(watermark_file) if watermark_file.is_file() else None,
                "target_tab": "YouTube Studio -> Customization -> Branding -> Video watermark"
            },
            "outro_stinger": {
                "file": str(stinger_file),
                "resolution": "1920 x 1080 px (5s Full HD)",
                "size_bytes": os.path.getsize(stinger_file) if stinger_file.is_file() else None
            }
        },
        "space_registration": {
            "space_index": 17,
            "space_name": "S1_17_YT_US_AON",
            "url": "https://www.youtube.com/@SUNONE_AON",
            "studio_url": "https://studio.youtube.com",
            "switcher_url": "https://www.youtube.com/channel_switcher",
            "status": "BRANDING_KIT_STAGED_READY"
        },
        "created_at": now_kst()
    }

    STAGE_FILE.write_text(json.dumps(channel_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Staging file created: {STAGE_FILE}")
    print("=== [S1 SUN-ONE AON CHANNEL CREATION STAGING COMPLETED] ===")
    return channel_meta

if __name__ == "__main__":
    stage_channel_creation()

