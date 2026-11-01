# -*- coding: utf-8 -*-
"""
S1 Suno Maestro Agents Engine (s1_suno_maestro_agents.py)

Implements:
1. 2026 Latest Suno AI v4.5 / v5.5 5-Tier Custom Mode Prompt Formula:
   - Tier 1: Genre & Era
   - Tier 2: Mood & Ethos (동방예의지국 & 상선약수)
   - Tier 3: Detailed Instrumentation (국악 퓨전 + 현대 오케스트라/신스)
   - Tier 4: Vocal & Dynamic Profile
   - Tier 5: Production & Mastering Specs (-14.0 LUFS Broadcast Standard)
2. 4 Dedicated Channel Suno Maestros:
   - Suno_Maestro_Step (한걸음씩 @한걸음씩-r4i)
   - Suno_Maestro_Booster (부스터 플리 @Booster_Playlist)
   - Suno_Maestro_Cafe (The Café Hour @TheCaféHour)
   - Suno_Maestro_US_AON (SUN-ONE AON @SUNONE_AON)
3. 2 Track concepts per channel (Total 8 tracks) ready for production and channel-dedicated vaulting.
"""

import os
import sys
import json
import uuid
import pathlib
import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = pathlib.Path(__file__).resolve().parent

def now_kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

# =============================================================================
# 1. 2026 5-TIER PROMPT FORMULA BUILDER
# =============================================================================

def build_5tier_style_prompt(tier1_genre, tier2_mood, tier3_instruments, tier4_vocal, tier5_mastering):
    """
    Constructs a 2026 Suno v4.5/v5.5 compliant 5-tier style prompt up to 1000 characters.
    """
    tiers = [
        f"[GENRE]: {tier1_genre}",
        f"[MOOD & ETHOS]: {tier2_mood}",
        f"[INSTRUMENTATION]: {tier3_instruments}",
        f"[VOCALS & DYNAMICS]: {tier4_vocal}",
        f"[PRODUCTION & MASTERING]: {tier5_mastering}"
    ]
    prompt_str = " | ".join(tiers)
    return prompt_str[:1000]

# =============================================================================
# 2. 4 DEDICATED SUNO MAESTROS SPECIFICATION
# =============================================================================

SUNO_MAESTROS = {
    "Suno_Maestro_Step": {
        "channel_id": "01_STEP",
        "channel_name": "한걸음씩",
        "handle": "@한걸음씩-r4i",
        "space_index": 6,
        "specialty": "K-Wisdom 시네마틱 포크/발라드 마스터",
        "style_formula": {
            "tier1_genre": "2026 Modern K-Cinematic Acoustic Folk Ballad, Korean Traditional Heritage Fusion",
            "tier2_mood": "Deep Filial Piety (효), Wisdom of Sages, Warm Jeong (정), Hopeful Perseverance, Zero Cynicism",
            "tier3_instruments": "Haegeum (해금 감성 독주), Gayageum 12-string plucking, Fingerstyle Acoustic Guitar, Upright Warm Piano, Subtle Cello & Viola String Quartet",
            "tier4_vocal": "Soulful Baritone Male Vocal with Gentle Breathing Texture, Emotional Dynamic Swell in Chorus, Crystal Korean Articulation",
            "tier5_mastering": "44.1kHz 16-bit Master, -14.0 LUFS Broadcast Standard, Pristine Acoustic Separation, High Dynamic Warmth"
        },
        "sample_tracks": [
            {
                "track_id": "STEP_TRK_01",
                "title_ko": "사냥꾼의 새벽",
                "title_en": "Hunter's Dawn",
                "bpm": 74,
                "key": "G Major",
                "concept": "가족을 위해 새벽 눈길을 헤치는 가장의 효와 성실한 땀방울",
                "structure_tags": "[Intro: Warm Haegeum Solo] -> [Verse 1: Intimate Storytelling] -> [Pre-Chorus: Subtle Acoustic Strum] -> [Chorus: Emotional String Swell] -> [Verse 2: Reflective Memories] -> [Bridge: Traditional Daegum Solo] -> [Chorus: Grand Anthemic Harmony] -> [Outro: Lingering Acoustic Resonance] -> [Fade Out]"
            },
            {
                "track_id": "STEP_TRK_02",
                "title_ko": "어머니의 등불",
                "title_en": "Mother's Lantern",
                "bpm": 72,
                "key": "D Major",
                "concept": "비바람 치는 밤에도 자식을 위해 켜둔 등불의 무조건적 사랑과 보은",
                "structure_tags": "[Intro: Fingerstyle Acoustic Guitar & Gayageum Pluck] -> [Verse 1: Gentle Whisper] -> [Chorus: Touching Warm String Swell] -> [Verse 2: Nostalgic Journey] -> [Bridge: Cello Solo] -> [Chorus: Pure Emotional Climax] -> [Outro: Warm Piano Fading into Silence] -> [Fade Out]"
            }
        ]
    },
    "Suno_Maestro_Booster": {
        "channel_id": "02_BOOSTER",
        "channel_name": "부스터 플리 | 운동·드라이브 음악",
        "handle": "@Booster_Playlist",
        "space_index": 7,
        "specialty": "K-Dynamic Clean Synthwave & Melodic Workout Phonk 마스터",
        "style_formula": {
            "tier1_genre": "2026 Euphoric Melodic Synthwave, Clean Korean Workout Phonk, High-Tension Night Drive",
            "tier2_mood": "Righteous Dynamic Spirit, Fairplay Sportsmanship, Seoul Han River Nightline Passion, Zero Vulgarity",
            "tier3_instruments": "Juno-106 Analog Synth Arpeggios, Punchy 808 Sub-Bass, 128 BPM 4-on-the-Floor Kick, Subtle Taepyeongso Brass Accents",
            "tier4_vocal": "Anthemic Vocoder Chops, High-Energy Shouts, Motivational Vocal Echoes, Dynamic Filter Sweep",
            "tier5_mastering": "44.1kHz 16-bit Master, -14.0 LUFS Club & Gym Master, Wide Stereo Panning, Punchy Low-End Clarity"
        },
        "sample_tracks": [
            {
                "track_id": "BOOSTER_TRK_01",
                "title_ko": "여름밤 한강 드라이브 & 러닝 비트",
                "title_en": "Summer Night Han River Drive & Workout Beat",
                "bpm": 128,
                "key": "A Minor",
                "concept": "서울 올림픽대로의 야경과 한강 변을 함께 달리는 동료애와 스포츠맨십",
                "structure_tags": "[Intro: Atmospheric Analog Synth Lead] -> [Verse: Steady 128 BPM Pulse] -> [Build-Up: Rising Synth Filter & Snare Roll] -> [Drop: High-Energy Euphoric Seoul Night Drive Beat] -> [Verse 2: Punchy 808 Bassline] -> [Build-Up: Rising Intensity] -> [Drop: Climax Drive Anthem] -> [Outro: Ambient Synthwave Highway Trail] -> [Fade Out]"
            },
            {
                "track_id": "BOOSTER_TRK_02",
                "title_ko": "결승선을 향한 질주",
                "title_en": "Sprint to the Finish Line",
                "bpm": 130,
                "key": "F Minor",
                "concept": "자신의 한계를 돌파하며 정정당당하게 전력 질주하는 청춘의 건강한 에너지",
                "structure_tags": "[Intro: Fast Arpeggiator & Heartbeat Kick] -> [Build-Up: Rising Snare Riser] -> [Drop: Maximum Power Workout Beat] -> [Verse: Chiseled Bassline Groove] -> [Bridge: Euphoric Synth Pad Breakdown] -> [Drop 2: Ultimate Acceleration Climax] -> [Outro: Victorious Synth Chords] -> [Fade Out]"
            }
        ]
    },
    "Suno_Maestro_Cafe": {
        "channel_id": "03_CAFE",
        "channel_name": "The Café Hour",
        "handle": "@TheCaféHour",
        "space_index": 8,
        "specialty": "K-Café Hospitality Jazz & Hanok Lo-Fi 마스터",
        "style_formula": {
            "tier1_genre": "2026 Cozy K-Indie Jazz, Bukchon Hanok Coffeehouse Lo-Fi, Mindful Tea Ambience",
            "tier2_mood": "Warm Hospitality (다도 예절), Tranquil Aesthetics, Gentle Solitude, Healing Calmness",
            "tier3_instruments": "Vintage Fender Rhodes Mark I, Upright Double Bass, Brushed Jazz Snare Drums, Gayageum Harmonics, Soft Vinyl Ambience",
            "tier4_vocal": "Pure Instrumental Priority, Gentle Muted Vocal Humming, Breath Texture in Background",
            "tier5_mastering": "44.1kHz 16-bit Master, -14.0 LUFS Warm Velvet Master, Smooth Analog Rolloff, Relaxing Acoustic Space"
        },
        "sample_tracks": [
            {
                "track_id": "CAFE_TRK_01",
                "title_ko": "북촌 한옥의 아침 다도",
                "title_en": "Morning Tea at Bukchon Hanok",
                "bpm": 75,
                "key": "Eb Major",
                "concept": "정갈한 손길로 따뜻한 차를 올리는 한국 다도의 환대 예절과 고즈넉한 평안",
                "structure_tags": "[Morning Brew: Gentle Rhodes Chords] -> [Verse: Warm Brushed Snare Rhythm] -> [Chorus: Cozy Piano & Gayageum Harmonics] -> [Afternoon Sunlight: Soft Muted Trumpet Dialogue] -> [Bridge: Steaming Tea Ambience] -> [Chorus: Serene Café Harmony] -> [Evening Rain in Bukchon: Mellow Double Bass Outro] -> [Fade Out]"
            },
            {
                "track_id": "CAFE_TRK_02",
                "title_ko": "성수동 비 내리는 오후의 커피",
                "title_en": "Rainy Afternoon Coffee in Seongsu",
                "bpm": 76,
                "key": "Bb Major",
                "concept": "붉은 벽돌 카페 창가에 떨어지는 빗방울을 보며 사색에 잠기는 현대인의 쉼표",
                "structure_tags": "[Intro: Raindrops & Fender Rhodes Chime] -> [Verse 1: Cozy Double Bass Walk] -> [Chorus: Sweet Upright Piano Lead] -> [Bridge: Subtle Saxophone Whisper] -> [Chorus: Warm Cup of Latte Harmony] -> [Outro: Rain Sound & Soft Piano Chord] -> [Fade Out]"
            }
        ]
    },
    "Suno_Maestro_US_AON": {
        "channel_id": "04_US_AON",
        "channel_name": "SUN-ONE AON",
        "handle": "@SUN-ONEAON",
        "space_index": 17,
        "specialty": "Global K-Ethics Epic Orchestra & Philanthropy Anthem 마스터",
        "style_formula": {
            "tier1_genre": "2026 World-Class K-Cinematic Hybrid Orchestra, Global Philanthropy Symphony",
            "tier2_mood": "Sangseonyaksu (上善若水: The Highest Good is Like Water), Noble Dignity, Global Unity & Charity",
            "tier3_instruments": "Full 80-piece Symphony Orchestra, Electric Cello, Grand Steinway Piano, Korean Traditional Buk & Jing Drums, Piri Woodwind",
            "tier4_vocal": "Anthemic Native English Cinematic Choir & Solos, Majestic Emotional Crescendo, Inspiring Spoken Epilogue",
            "tier5_mastering": "44.1kHz 16-bit Master, -14.0 LUFS Hollywood Broadcast Master, Ultra-Wide Cinematic Stereo, Immersive Soundstage"
        },
        "sample_tracks": [
            {
                "track_id": "USAON_TRK_01",
                "title_ko": "상선약수: 선한 영향력의 바다",
                "title_en": "Water of Benevolence (Global Philanthropy Symphony)",
                "bpm": 92,
                "key": "D Major",
                "concept": "만물을 이롭게 하되 다투지 않는 상선약수의 정신으로 세계를 적시는 자선의 대서사",
                "structure_tags": "[Intro: Solemn Orchestral French Horn & Cello] -> [Verse 1: Cinematic English Narration & Soft Piano] -> [Pre-Chorus: Rising Taepyeongso & Timpani Swell] -> [Chorus: Grand Global Symphony of Benevolence] -> [Verse 2: Poignant World Strings] -> [Bridge: Powerful Korean Buk Drum Crescendo] -> [Chorus: Monumental Anthem of Peace & Charity] -> [Outro: Transcendent Piano & Living Water Resonance] -> [Fade Out]"
            },
            {
                "track_id": "USAON_TRK_02",
                "title_ko": "새벽의 지평선 너머로",
                "title_en": "Beyond the Golden Horizon",
                "bpm": 105,
                "key": "B Minor",
                "concept": "어둠을 뚫고 솟아오르는 태양(SUN)처럼 인류에게 희망과 용기를 전하는 장엄한 승리의 찬가",
                "structure_tags": "[Intro: Shimmering Cosmic Strings & Harp] -> [Verse: Deep Cinematic Pulse & English Tenor] -> [Chorus: Soaring Brass & Full Choir Explosion] -> [Bridge: Emotional Solo Cello Dialogue] -> [Build-Up: Massive Percussive Drive] -> [Final Chorus: World Anthem of Hope] -> [Outro: Pure Piano Chord Resolving into Light] -> [Fade Out]"
            }
        ]
    }
}

# =============================================================================
# 2.5 TOOL MASTERY CONSTITUTION GATE (Article 0)
# =============================================================================

def verify_tool_mastery_before_start(tool_name: str = "Suno_Maestro_Agent", skill_book_path: str = None) -> bool:
    """
    S1 도구 마스터 헌법 제0조/제3조 준수 검증 게이트 (S1_TOOL_MASTERY_CONSTITUTION.md)
    """
    if skill_book_path is None:
        skill_book_path = str(ROOT_DIR / "skills" / "SKILL_EGO_SUNO_DIRECT_DOWNLOAD.md")
    p = pathlib.Path(skill_book_path)
    if not p.is_file():
        raise PermissionError(f"[헌법 위반] 도구 {tool_name}의 스킬북({skill_book_path})이 존재하지 않아 작업을 착수할 수 없습니다.")
    content = p.read_text(encoding="utf-8")
    for kw in ["dom", "api", "download", "verification"]:
        if kw not in content.lower():
            raise ValueError(f"[헌법 위반] 스킬북({skill_book_path})에 필수 실측 항목 '{kw}'이 결여되었습니다.")
    return True

# =============================================================================
# 3. COMPLETE PROMPT PACKAGE GENERATOR
# =============================================================================

def generate_maestro_prompt_package(maestro_id, track_index=0):
    verify_tool_mastery_before_start(maestro_id)
    maestro = SUNO_MAESTROS.get(maestro_id)
    if not maestro:
        raise ValueError(f"Unknown Maestro: {maestro_id}")

    track = maestro["sample_tracks"][track_index]
    formula = maestro["style_formula"]

    style_prompt = build_5tier_style_prompt(
        formula["tier1_genre"],
        formula["tier2_mood"],
        formula["tier3_instruments"],
        formula["tier4_vocal"],
        formula["tier5_mastering"]
    )

    lyrics_body = f"""{track['structure_tags']}

[Verse 1]
From the deepest mountain spring, pure and humble
No desire for glory, no desire for strife
Every drop a blessing, every stream a life

[Chorus]
{track['title_ko']} - {track['title_en']}
Like water in the wind, flowing wide and free
The highest excellence is here for all to see
Benevolence returned to humanity

[Bridge]
With honor to the past and courage for the dawn
Righteous in our spirit, forever marching on

[Chorus]
{track['title_ko']} - {track['title_en']}
Like water in the wind, flowing wide and free
The highest excellence is here for all to see
Benevolence returned to humanity

[Outro]
Grace upon the earth, peace upon the soul."""

    pkg = {
        "maestro_id": maestro_id,
        "channel_id": maestro["channel_id"],
        "channel_name": maestro["channel_name"],
        "handle": maestro["handle"],
        "space_index": maestro["space_index"],
        "specialty": maestro["specialty"],
        "track_id": track["track_id"],
        "titles": {
            "bilingual": f"{track['title_ko']} | {track['title_en']}",
            "korean": track["title_ko"],
            "english": track["title_en"]
        },
        "musical_parameters": {
            "bpm": track["bpm"],
            "key": track["key"],
            "target_lufs": -14.0,
            "sample_rate": 44100,
            "bit_depth": 16
        },
        "suno_custom_mode_fields": {
            "title_field": f"{track['title_ko']} | {track['title_en']}",
            "style_prompt_1000char": style_prompt,
            "lyrics_structure_meta": lyrics_body
        },
        "created_at": now_kst()
    }
    return pkg

if __name__ == "__main__":
    print("=== [S1 SUNO MAESTRO AGENTS TEST] ===")
    for m_id in SUNO_MAESTROS:
        pkg = generate_maestro_prompt_package(m_id, 0)
        print(f"\n[{m_id}] -> {pkg['channel_name']} ({pkg['handle']})")
        print(f"Title: {pkg['titles']['bilingual']}")
        print(f"5-Tier Style ({len(pkg['suno_custom_mode_fields']['style_prompt_1000char'])} chars):\n  {pkg['suno_custom_mode_fields']['style_prompt_1000char'][:140]}...")
    print("\nAll 4 Suno Maestro Agents operational.")

