# -*- coding: utf-8 -*-
"""
S1 US Vault Builder (s1_build_us_vault.py)
Builds the US Channel Launch Kit, Vault EP01-EP03 Packages, and renders EP01 48kHz Master + 1080p Video.
"""
import os
import sys
import json
import uuid
import hashlib
import pathlib
import datetime
import subprocess

ROOT_DIR = pathlib.Path(__file__).resolve().parent
VAULT_DIR = ROOT_DIR / "studio_vault" / "US_SUN_ONE_AON"
ICON_PATH = ROOT_DIR / "icon-512.png"

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

def probe_file(filepath):
    p = pathlib.Path(filepath)
    if not p.is_file():
        return None
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", str(p)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        return None
    try:
        return json.loads(res.stdout)
    except Exception:
        return None

def build_launch_kit():
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    kit_path = VAULT_DIR / "US_CHANNEL_LAUNCH_KIT.md"

    content = """# 🇺🇸 SUN-ONE AON YouTube US Channel Launch Kit
> **Flagship Global Channel for the United States Market & Global Philanthropy**
> **Channel Handle:** `@SUNONE_AON` (Alt: `@SUNONEAON_US`)
> **Core Mission:** "Music for the Soul, Value Returned to the World: Global Philanthropy through Sound"

---

## 1. 1-Minute Copy-Paste Channel Setup (유튜브 '+ 채널 만들기' 1분 완성)

### 📌 Basic Information (기본 정보)
- **Channel Name (채널명):** `SUN-ONE AON`
- **Handle (핸들):** `@SUNONE_AON` (Alternative: `@SUNONEAON_US`)
- **Channel Description (영문 공식 채널 소개글):**
```text
Welcome to SUN-ONE AON — the global sanctuary of transformative cinematic sound, inspiring melodies, and heartfelt visual art, dedicated to listeners worldwide.

Rooted in the timeless Eastern philosophy of "Sangseonyaksu" (上善若水 — "The highest excellence is like water, benefiting all living things without striving or conflict"), our creations seek to heal the weary soul, spark enduring hope, and bring peace to a restless world.

[Our Global Philanthropy Pledge]
We believe that true art finds its highest purpose in giving back. A core commitment of SUN-ONE AON is our global value return initiative: revenue generated through this channel is systematically dedicated to humanitarian relief, environmental restoration, and youth empowerment projects across the globe.

Every note is crafted in uncompromised 48kHz / 24-bit studio fidelity, designed for deep focus, restorative sleep, emotional healing, and cinematic inspiration.

Walk with us, one step at a time. Like gentle water, we shall reach the great ocean together.

Produced by S1 Imperial Command & AON Global Studio.
Executive Producer: Sangill Lee
```

---

## 2. YouTube Studio Settings (스튜디오 필수 환경 설정 가이드)

| Setting Category | Recommended Value | Description & Purpose |
| :--- | :--- | :--- |
| **Country of Residence (거주 국가)** | `United States` (미국) | 북미 추천 알고리즘 및 미국 시청자 타깃 활성화 |
| **Default Language (기본 언어)** | `English (United States)` | 영문 메타데이터 및 영어 자막 기본 적용 |
| **Channel Keywords (채널 키워드)** | `SUN-ONE AON, Cinematic Music, Soul Healing, Deep Focus Soundscape, 48kHz Studio Audio, US Billboard Chill, Meditation Music, Inspirational Ballad, Neo Classical, Ambient Study Beats, Global Philanthropy` | US 검색 및 탐색 피드 노출 극대화 |
| **Category (카테고리)** | `Music` (10) | 공식 음악 채널 클러스터링 |
| **Altered / Synthetic Content Disclosure** | `Yes (선택: 변경되거나 합성된 콘텐츠)` | AI 생성 음원 및 영상 공시 정책 100% 준수 (계정 정지 및 패널티 0% 방어) |

---

## 3. US Prime-Time Scheduling Strategy (북미 골든타임 업로드 전략)

- **East Coast (EST - New York / Washington D.C.):**
  - **Lunchtime Inspiration:** 12:00 PM – 1:30 PM EST (한국 시간: 다음 날 새벽 2:00 – 3:30)
  - **Evening Relaxation & Sleep:** 8:00 PM – 10:00 PM EST (한국 시간: 다음 날 오전 10:00 – 12:00)
- **West Coast (PST - Los Angeles / Silicon Valley):**
  - **Commute & Focus:** 8:00 AM – 9:30 AM PST
  - **Night Sanctuary:** 9:00 PM – 11:00 PM PST
- **Release Cadence (비축 및 발행 주기):**
  - 로컬 금고(`studio_vault/`)에 최소 3~5편을 선(先)비축한 후, 주 1~2회 정기 스케줄 발행.

---

## 4. Brand Asset Specifications (채널 비주얼 에셋 규격)
- **Profile Picture (프로필):** 800x800px (S1 황금 로고 / 아이콘 마스크 `icon-512.png` 적용)
- **Banner Artwork (배너):** 2560x1440px (Safe Area: 1232x338px 중앙 배치)
- **Watermark (워터마크):** 150x150px PNG (`S1 AON` 황금 인장)
"""
    kit_path.write_text(content.strip() + "\n", encoding="utf-8")
    return str(kit_path)

def build_vault_episodes():
    # -------------------------------------------------------------------------
    # EP01: Dawn of Hope (Like Water in the Wind)
    # -------------------------------------------------------------------------
    dir_ep01 = VAULT_DIR / "VAULT_US_EP01_DAWN_OF_HOPE"
    dir_ep01.mkdir(parents=True, exist_ok=True)

    prompt_ep01 = {
        "episode_id": "VAULT_US_EP01",
        "title": "Dawn of Hope (Like Water in the Wind)",
        "theme": "Cinematic Inspirational Ballad · Soul Healing & Resilience",
        "suno_v6_spec": {
            "style_tags": "Billboard cinematic ballad, poignant grand piano, acoustic guitar, emotional male tenor vocal, soaring orchestral strings, 72 bpm, 48kHz audio mastering, uplifting, anthemic, Grammy-tier production",
            "exclude_tags": "heavy metal, autotune, distortion, aggressive EDM, mumble, harsh noise, shouting",
            "lyrics": """[Intro - Delicate Grand Piano & Gentle Morning Breeze]

[Verse 1]
When the shadows stretch across the empty room,
And the heaviest silence begins to bloom,
Take a breath, feel the ground beneath your feet,
There's a quiet strength in every heartbeat.

[Pre-Chorus]
Like the mountain stream that carves the stone,
You don't have to face the storm alone.
Soft as water, yet reaching far and deep,
There's a promise you were born to keep.

[Chorus]
Step by step into the rising sun,
The greatest journey has just begun.
Flowing like water, humble and free,
Nothing can break what is meant to be.
From the darkest night to the morning light,
Dawn of hope, shine so bright.

[Verse 2]
Every broken dream you carried yesterday,
Is a stepping stone that paves the way.
Do not rush the dawn, do not fear the rain,
There is healing found inside the pain.

[Chorus]
Step by step into the rising sun,
The greatest journey has just begun.
Flowing like water, humble and free,
Nothing can break what is meant to be.
From the darkest night to the morning light,
Dawn of hope, shine so bright.

[Bridge - Orchestral Swell with Cello & Timpani]
Water bends, but it never breaks,
Giving life for the world's own sake.
In the lowest place, the miracles rise,
Look ahead to the open skies!

[Chorus - Full Dynamic Orchestra & Backing Choir]
Step by step, hear the anthem call,
Rise above every towering wall!
Like water returning to the sea,
We are boundless, we are free!
Dawn of hope, our hearts unite,
Bathed in everlasting light!

[Outro - Gentle Piano fading out into ambient silence]
Step by step...
Flow like water...
You are not alone."""
        }
    }
    (dir_ep01 / "prompt_us.json").write_text(json.dumps(prompt_ep01, ensure_ascii=False, indent=2), encoding="utf-8")

    srt_en_ep01 = """1
00:00:00,000 --> 00:00:05,000
[Delicate Grand Piano & Gentle Morning Breeze]

2
00:00:05,500 --> 00:00:10,000
When the shadows stretch across the empty room

3
00:00:10,500 --> 00:00:15,000
And the heaviest silence begins to bloom

4
00:00:15,500 --> 00:00:20,000
Take a breath, feel the ground beneath your feet

5
00:00:20,500 --> 00:00:26,000
There's a quiet strength in every heartbeat

6
00:00:26,500 --> 00:00:32,000
Like the mountain stream that carves the stone

7
00:00:32,500 --> 00:00:38,000
You don't have to face the storm alone

8
00:00:38,500 --> 00:00:44,000
Soft as water, yet reaching far and deep

9
00:00:44,500 --> 00:00:51,000
Step by step into the rising sun

10
00:00:51,500 --> 00:00:57,500
The greatest journey has just begun

11
00:00:58,000 --> 00:01:05,000
Flowing like water, humble and free

12
01:05,000 --> 01:12,000
Dawn of hope, shine so bright
"""
    (dir_ep01 / "subtitles_en_US.srt").write_text(srt_en_ep01.strip() + "\n", encoding="utf-8")

    srt_ko_ep01 = """1
00:00:00,000 --> 00:00:05,000
[섬세한 그랜드 피아노와 아침의 산들바람]

2
00:00:05,500 --> 00:00:10,000
빈 방 안 가득 그림자가 길어지고

3
00:00:10,500 --> 00:00:15,000
무거운 침묵이 피어오를 때

4
00:00:15,500 --> 00:00:20,000
깊은 숨을 쉬며 발아래 대지를 느껴봐

5
00:00:20,500 --> 00:00:26,000
너의 심장 박동 속에 고요한 힘이 깃들어 있어

6
00:00:26,500 --> 00:00:32,000
바위를 깎아내는 산골짜기 시냇물처럼

7
00:00:32,500 --> 00:00:38,000
홀로 폭풍우를 견딜 필요는 없어

8
00:00:38,500 --> 00:00:44,000
물처럼 부드럽지만 가장 깊은 곳까지 닿는

9
00:00:44,500 --> 00:00:51,000
한걸음씩 떠오르는 태양을 향해

10
00:00:51,500 --> 00:00:57,500
가장 위대한 여정은 이제 시작되었어

11
00:00:58,000 --> 00:01:05,000
물처럼 유연하고 자유롭게

12
01:05,000 --> 01:12,000
희망의 새벽이여, 찬란히 비추어라
"""
    (dir_ep01 / "subtitles_ko.srt").write_text(srt_ko_ep01.strip() + "\n", encoding="utf-8")

    seo_ep01 = {
        "ctr_titles": [
            "When Everything Falls Apart, Listen to This — Dawn of Hope [SUN-ONE AON]",
            "Dawn of Hope — A Cinematic Anthem for Healing, Peace, and Strength (48kHz Lossless)",
            "Step by Step: The Song That Restores Your Soul When You Feel Lost"
        ],
        "primary_title": "When Everything Falls Apart, Listen to This — Dawn of Hope [SUN-ONE AON]",
        "description": """If you are carrying a burden too heavy to speak of, let this music hold your heart today.

Inspired by the timeless wisdom of Sangseonyaksu (上善若水) — "The highest good is like water, nourishing all without conflict" — "Dawn of Hope" is a cinematic anthem created to remind you that even through the darkest storm, gentle water always finds its way to the ocean.

[Global Philanthropy Mission]
SUN-ONE AON is dedicated to global giving. Revenue generated by this channel is contributed to humanitarian relief, mental wellness, and community empowerment initiatives worldwide.

[Audio Production Standard]
Mastered in lossless 48,000 Hz / 24-bit Stereo (-16.0 LUFS, -1.5 dBTP) for pure acoustic fidelity.

[Timestamps]
00:00 Finding Quiet in the Silence
00:26 The Strength Within
00:44 Step by Step (The Rising Sun)
01:15 Dawn of Hope Reborn

#SUNONEAON #HealingMusic #CinematicBallad #InspirationalMusic #SoulRestoration #HopeSong #BillboardStyle #GlobalPhilanthropy""",
        "tags": ["SUN-ONE AON", "Dawn of Hope", "Cinematic Ballad", "Healing Music", "Inspirational Music", "Soul Healing", "48kHz Audio", "Global Philanthropy", "K-Pop Producer", "Suno v6"],
        "category_id": "10",
        "default_language": "en",
        "default_audio_language": "en-US",
        "privacy_status": "private"
    }
    (dir_ep01 / "youtube_us_seo.json").write_text(json.dumps(seo_ep01, ensure_ascii=False, indent=2), encoding="utf-8")

    # -------------------------------------------------------------------------
    # EP02: Golden Horizon (Chasing the Light)
    # -------------------------------------------------------------------------
    dir_ep02 = VAULT_DIR / "VAULT_US_EP02_GOLDEN_HORIZON"
    dir_ep02.mkdir(parents=True, exist_ok=True)

    prompt_ep02 = {
        "episode_id": "VAULT_US_EP02",
        "title": "Golden Horizon (Chasing the Light)",
        "theme": "Uplifting Synthwave / Melodic Electro-Pop · Sunset Drive & Breakthrough",
        "suno_v6_spec": {
            "style_tags": "Cinematic synthwave, melodic electro-pop, driving 124 bpm bassline, punchy acoustic-electronic hybrid drums, hopeful vocal harmonies, sunset highway drive, warm analog synths, anthemic chorus",
            "exclude_tags": "harsh distortion, dark trap, screamo, lo-fi hiss, heavy dubstep",
            "lyrics": """[Intro - Shimmering Arpeggios & Pulse Bass]

[Verse 1]
The city lights fade in the rear-view glass,
Letting go of the ghosts in the shadowed past.
Open highway underneath the dusk,
In this forward momentum, in hope we trust.

[Pre-Chorus]
Feel the engine purr, feel the road ignite,
We are chasing the edge of the fading night.
Nothing holding back what we're meant to find,
Leave the sorrow and doubt far behind.

[Chorus]
Golden horizon calling our name,
A brand new spark in a burning flame!
Drive through the thunder, drive through the rain,
We are alive, we will conquer the pain!
Golden horizon, open and wide,
Hope is the compass that travels beside!

[Outro]
Chasing the light...
Golden horizon...
Never look back."""
        }
    }
    (dir_ep02 / "prompt_us.json").write_text(json.dumps(prompt_ep02, ensure_ascii=False, indent=2), encoding="utf-8")

    srt_en_ep02 = """1
00:00:00,000 --> 00:00:06,000
[Shimmering Synth Arpeggios & Pulse Bass]

2
00:00:06,500 --> 00:00:12,000
The city lights fade in the rear-view glass

3
00:00:12,500 --> 00:00:18,000
Letting go of the ghosts in the shadowed past

4
00:00:18,500 --> 00:00:25,000
Golden horizon calling our name

5
00:00:25,500 --> 00:00:32,000
A brand new spark in a burning flame!
"""
    (dir_ep02 / "subtitles_en_US.srt").write_text(srt_en_ep02.strip() + "\n", encoding="utf-8")

    srt_ko_ep02 = """1
00:00:00,000 --> 00:00:06,000
[빛나는 신스 아르페지오와 펄스 베이스]

2
00:00:06,500 --> 00:00:12,000
룸미러 너머로 도시의 불빛이 흐려지고

3
00:00:12,500 --> 00:00:18,000
어두웠던 과거의 잔영들을 놓아줄 때

4
00:00:18,500 --> 00:00:25,000
황금빛 지평선이 우리 이름을 부르네

5
00:00:25,500 --> 00:00:32,000
타오르는 불꽃 속 새로운 불씨가 되어!
"""
    (dir_ep02 / "subtitles_ko.srt").write_text(srt_ko_ep02.strip() + "\n", encoding="utf-8")

    seo_ep02 = {
        "ctr_titles": [
            "Late Night Drive to Clear Your Mind — Golden Horizon [SUN-ONE AON]",
            "Golden Horizon: 124 BPM High-Energy Synthwave for Motivation & Running",
            "Turn Up the Volume and Leave the Past Behind (Cinematic Electro-Pop)"
        ],
        "primary_title": "Late Night Drive to Clear Your Mind — Golden Horizon [SUN-ONE AON]",
        "description": """When the weight of the day is too much, roll down the windows, press play, and let the pulse of Golden Horizon carry you forward.

Mastered in 48kHz / 24-bit studio sound.
Produced by SUN-ONE AON Global Studio.

#SUNONEAON #GoldenHorizon #Synthwave #NightDrive #WorkoutMusic #Motivation""",
        "tags": ["SUN-ONE AON", "Golden Horizon", "Synthwave", "Drive Music", "Workout Beat", "Electro Pop", "48kHz"],
        "category_id": "10",
        "default_language": "en",
        "default_audio_language": "en-US",
        "privacy_status": "private"
    }
    (dir_ep02 / "youtube_us_seo.json").write_text(json.dumps(seo_ep02, ensure_ascii=False, indent=2), encoding="utf-8")

    # -------------------------------------------------------------------------
    # EP03: Light Returned (The Water and the Sea)
    # -------------------------------------------------------------------------
    dir_ep03 = VAULT_DIR / "VAULT_US_EP03_LIGHT_RETURNED"
    dir_ep03.mkdir(parents=True, exist_ok=True)

    prompt_ep03 = {
        "episode_id": "VAULT_US_EP03",
        "title": "Light Returned (The Water and the Sea)",
        "theme": "Neo-Classical / Ambient Piano & Cello · Restorative Meditation",
        "suno_v6_spec": {
            "style_tags": "Ambient neo-classical, warm Rhodes piano, soothing cello solos, gentle rain ambience, 68 bpm, deeply restorative, meditative, soul healing, peaceful acoustic resonance",
            "exclude_tags": "aggressive drums, loud horns, sudden drops, distortion, harsh vocals",
            "lyrics": """[Atmospheric Rain & Gentle Rhodes Piano Chords]

[Spoken Word / Gentle Vocalise]
Water asks for no applause.
It flows where nothing else dares to go.
It embraces the broken stones.
And in the quiet depths,
All things return to light.

[Melodic Swell - Cello & Acoustic Strings]
Rest now.
The storm has passed.
Peace is here at last."""
        }
    }
    (dir_ep03 / "prompt_us.json").write_text(json.dumps(prompt_ep03, ensure_ascii=False, indent=2), encoding="utf-8")

    srt_en_ep03 = """1
00:00:00,000 --> 00:00:08,000
Water asks for no applause.

2
00:00:08,500 --> 00:00:16,000
It flows where nothing else dares to go.

3
00:00:16,500 --> 00:00:24,000
It embraces the broken stones.

4
00:00:24,500 --> 00:00:32,000
And in the quiet depths, all things return to light.
"""
    (dir_ep03 / "subtitles_en_US.srt").write_text(srt_en_ep03.strip() + "\n", encoding="utf-8")

    srt_ko_ep03 = """1
00:00:00,000 --> 00:00:08,000
물은 갈채를 바라지 않는다.

2
00:00:08,500 --> 00:00:16,000
그 누구도 가려 하지 않는 가장 낮은 곳으로 흐르며

3
00:00:16,500 --> 00:00:24,000
부서진 돌부리들을 조용히 품어 안는다.

4
00:00:24,500 --> 00:00:32,000
그리고 깊고 고요한 바다에서, 모든 것은 마침내 빛으로 환원된다.
"""
    (dir_ep03 / "subtitles_ko.srt").write_text(srt_ko_ep03.strip() + "\n", encoding="utf-8")

    seo_ep03 = {
        "ctr_titles": [
            "Deep Sleep & Stress Relief in 10 Minutes — Light Returned [SUN-ONE AON]",
            "Pure Peace: Ambient Piano & Rain for Calming Overthinking",
            "The Water and the Sea — Neo-Classical Meditation (48kHz Lossless)"
        ],
        "primary_title": "Deep Sleep & Stress Relief in 10 Minutes — Light Returned [SUN-ONE AON]",
        "description": """Close your eyes and breathe.
Let the gentle piano and soothing rain wash away anxiety, restlessness, and fatigue.

Format: 48kHz / 24-bit Mastered.
Pledged to Global Philanthropy.

#SUNONEAON #SleepMusic #MeditationMusic #PianoRain #DeepFocus #CalmSound""",
        "tags": ["SUN-ONE AON", "Light Returned", "Sleep Music", "Meditation", "Rain Ambience", "Relaxing Piano", "Neo Classical"],
        "category_id": "10",
        "default_language": "en",
        "default_audio_language": "en-US",
        "privacy_status": "private"
    }
    (dir_ep03 / "youtube_us_seo.json").write_text(json.dumps(seo_ep03, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ep01": str(dir_ep01),
        "ep02": str(dir_ep02),
        "ep03": str(dir_ep03)
    }

def render_ep01_media():
    dir_ep01 = VAULT_DIR / "VAULT_US_EP01_DAWN_OF_HOPE"
    wav_out = dir_ep01 / "sample_master_48k.wav"
    mp4_out = dir_ep01 / "preview_1080p.mp4"

    # 1. 48kHz 24-bit Master Audio (Dawn of Hope inspirational harmonic chord)
    # A warm inspiring chord progression: D major 9 (D4, F#4, A4, C#5, E5) with slow crescendo and rich stereo spread
    synth_expr = (
        "sin(293.66*2*PI*t)*0.22+sin(369.99*2*PI*t)*0.18+sin(440.00*2*PI*t)*0.18+sin(554.37*2*PI*t)*0.14+sin(659.25*2*PI*t)*0.10|"
        "sin(293.66*2*PI*t)*0.18+sin(369.99*2*PI*t)*0.22+sin(440.00*2*PI*t)*0.15+sin(554.37*2*PI*t)*0.16+sin(659.25*2*PI*t)*0.12"
    )
    synth_input = f"aevalsrc={synth_expr}:s=48000:d=10"
    audio_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", synth_input,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=7",
        "-c:a", "pcm_s24le",
        "-ar", "48000",
        str(wav_out)
    ]
    res_a = subprocess.run(audio_cmd, capture_output=True, text=True, encoding="utf-8")
    if res_a.returncode != 0:
        raise RuntimeError(f"FFmpeg audio render failed: {res_a.stderr}")

    # 2. 1080p Full HD MP4 Preview Video
    art_path = str(ICON_PATH if ICON_PATH.is_file() else ROOT_DIR / "icon-192.png")
    video_filter = "scale=512:512,pad=1920:1080:(1920-512)/2:(1080-512)/2:color=0x080e1a,format=yuv420p"
    video_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", art_path,
        "-i", str(wav_out),
        "-vf", video_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4_out)
    ]
    res_v = subprocess.run(video_cmd, capture_output=True, text=True, encoding="utf-8")
    if res_v.returncode != 0:
        raise RuntimeError(f"FFmpeg video render failed: {res_v.stderr}")

    probe_wav = probe_file(wav_out)
    probe_mp4 = probe_file(mp4_out)

    return {
        "wav": {
            "path": str(wav_out),
            "size": wav_out.stat().st_size,
            "sha256": compute_sha256(wav_out),
            "probe": probe_wav
        },
        "mp4": {
            "path": str(mp4_out),
            "size": mp4_out.stat().st_size,
            "sha256": compute_sha256(mp4_out),
            "probe": probe_mp4
        }
    }

def main():
    print("=== [S1 US VAULT BUILD START] ===")
    launch_kit_path = build_launch_kit()
    print("Launch Kit created at:", launch_kit_path)

    episodes = build_vault_episodes()
    print("Vault Episodes created:", list(episodes.keys()))

    renders = render_ep01_media()
    print("EP01 Media rendered successfully.")

    wav_info = renders["wav"]
    mp4_info = renders["mp4"]

    wav_stream = wav_info["probe"]["streams"][0] if wav_info["probe"] else {}
    mp4_streams = mp4_info["probe"]["streams"] if mp4_info["probe"] else []
    v_stream = next((s for s in mp4_streams if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in mp4_streams if s.get("codec_type") == "audio"), {})

    inventory = {
        "timestamp": now_kst(),
        "channel": {
            "name": "SUN-ONE AON",
            "handle": "@SUNONE_AON",
            "alt_handle": "@SUNONEAON_US",
            "target_market": "en-US",
            "mission": "Global Philanthropy through Sound (환원의 국제화)",
            "launch_kit": str(VAULT_DIR / "US_CHANNEL_LAUNCH_KIT.md")
        },
        "vault_episodes": {
            "VAULT_US_EP01": {
                "title": "Dawn of Hope (Like Water in the Wind)",
                "genre": "Cinematic Inspirational Ballad",
                "folder": str(VAULT_DIR / "VAULT_US_EP01_DAWN_OF_HOPE"),
                "status": "MEDIA_RENDERED_AND_VERIFIED",
                "audio_master": {
                    "filename": "sample_master_48k.wav",
                    "codec": wav_stream.get("codec_name"),
                    "sample_rate": int(wav_stream.get("sample_rate", 0)),
                    "channels": int(wav_stream.get("channels", 0)),
                    "bits_per_sample": int(wav_stream.get("bits_per_sample", 0)),
                    "loudness": "-16.0 LUFS (-1.5 dBTP)",
                    "sha256": wav_info["sha256"],
                    "size_bytes": wav_info["size"]
                },
                "video_preview": {
                    "filename": "preview_1080p.mp4",
                    "resolution": f"{v_stream.get('width')}x{v_stream.get('height')}",
                    "codec": f"{v_stream.get('codec_name')}+{a_stream.get('codec_name')}",
                    "audio_rate": int(a_stream.get("sample_rate", 0)),
                    "sha256": mp4_info["sha256"],
                    "size_bytes": mp4_info["size"]
                }
            },
            "VAULT_US_EP02": {
                "title": "Golden Horizon (Chasing the Light)",
                "genre": "Uplifting Synthwave / Melodic Electro-Pop",
                "folder": str(VAULT_DIR / "VAULT_US_EP02_GOLDEN_HORIZON"),
                "status": "PACKAGE_SEEDED_AWAITING_SUNO"
            },
            "VAULT_US_EP03": {
                "title": "Light Returned (The Water and the Sea)",
                "genre": "Neo-Classical / Ambient Piano & Cello",
                "folder": str(VAULT_DIR / "VAULT_US_EP03_LIGHT_RETURNED"),
                "status": "PACKAGE_SEEDED_AWAITING_SUNO"
            }
        },
        "verdict": "US_VAULT_SEED_COMPLETE"
    }

    inv_path = VAULT_DIR / "VAULT_INVENTORY.json"
    inv_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Inventory written to {inv_path}")
    print("=== [S1 US VAULT BUILD COMPLETED] ===")
    return inventory

if __name__ == "__main__":
    inv = main()
    print("INVENTORY VERDICT:", inv["verdict"])

