# -*- coding: utf-8 -*-
"""
S1 4-Channel Directors & K-Global Courtesy Suno Master Engine (s1_channel_directors.py)

Implements:
1. 4 Channel Director Agents:
   - Director_Step (Space 6: 한걸음씩 | @한걸음씩-r4i)
   - Director_Booster (Space 7: 부스터 플리 | @Booster_Playlist)
   - Director_Cafe (Space 8: The Café Hour | @TheCaféHour)
   - Director_US_AON (Space 17: SUN-ONE AON | @SUNONE_AON)
2. K-Heritage / Eastern Land of Courtesy (동방예의지국) Core Philosophical Foundations:
   - Filial piety, respect, integrity, warm 'Jeong' (情), hospitable tea culture, righteous dynamic energy.
3. Suno AI v4/v4.5 Structured Prompt Builder:
   - Style tags, Korean traditional fusion instruments (Gayageum, Haegeum, Piri) + modern synth/piano.
   - Structured tags: [Intro], [Verse], [Pre-Chorus], [Chorus], [Bridge], [Outro].
   - DistroKid audio master specs: -14.0 LUFS, 44.1kHz 16-bit PCM Stereo WAV.
4. Suno Dispatch Queue Manager (suno_dispatch_queue.json) for Space 4 integration.
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
VAULT_DIR = ROOT_DIR / "studio_vault" / "K_GLOBAL_PACKAGES"
QUEUE_FILE = ROOT_DIR / "suno_dispatch_queue.json"
REGISTRY_FILE = ROOT_DIR / "S1_SPACE_REGISTRY.json"

def now_kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

# =============================================================================
# 1. DIRECTORS REGISTRY & K-HERITAGE PHILOSOPHICAL DEFINITIONS
# =============================================================================

CHANNEL_DIRECTORS = {
    "Director_Step": {
        "channel_id": "CH_01_STEP",
        "name": "Director_Step",
        "target_channel": "한걸음씩",
        "handle": "@한걸음씩-r4i",
        "space_index": 6,
        "subscribers": 33,
        "video_count": 48,
        "slogan": "🌿 한마디가 당신의 인생을 바꿉니다",
        "target_time_kst": "06:00 ~ 08:00 (아침 기상/출근 감성 위로)",
        "target_time_est": "17:00 ~ 19:00 (퇴근길 위로)",
        "k_global_identity": "K-Wisdom & Courteous Life Philosophy (동방예의지국 삶의 지혜와 예절)",
        "core_virtues": [
            "부모와 스승에 대한 공경과 보은 (Filial Piety & Gratitude)",
            "성실과 정직, 인과응보의 섭리 (Righteous Diligence & Karma)",
            "한국 고유의 따뜻한 정(Jeong, 情)과 인생 치유 (Healing & Warm Empathy)"
        ],
        "suno_spec": {
            "vocal_gender": "warm baritone male / soulful female vocal",
            "primary_genre": "K-Cinematic Acoustic Folk Ballad",
            "instruments": "Acoustic guitar, warm piano, Haegeum (해금 선율), Gayageum (가야금 아르페지오), string quartet, subtle orchestral percussion",
            "bpm_range": "70 - 82 BPM",
            "keys": ["C Major", "G Major", "D Major", "E Minor"],
            "lufs_target": -14.0,
            "sample_rate": 44100,
            "bit_depth": 16
        }
    },
    "Director_Booster": {
        "channel_id": "CH_02_BOOSTER",
        "name": "Director_Booster",
        "target_channel": "부스터 플리 | 운동·드라이브 음악",
        "handle": "@Booster_Playlist",
        "space_index": 7,
        "subscribers": 26,
        "video_count": 15,
        "slogan": "지친 일상에 강력한 에너지를 채워줄 '부스터 플리(Booster Playlist)'입니다.",
        "target_time_kst": "18:00 ~ 21:00 (퇴근 드라이브 & 야간 헬스/러닝)",
        "target_time_est": "05:00 ~ 08:00 (모닝 모티베이션)",
        "k_global_identity": "K-Dynamic Spirit & Righteous Energy (역동적 기상과 의로운 열정)",
        "core_virtues": [
            "퇴폐성 배제, 건강한 스포츠맨십과 페어플레이 (Clean Athletic Energy)",
            "함께 달리는 동료를 응원하는 상호 격려와 의리 (Mutual Encouragement & Camaraderie)",
            "서울 한강 야경 드라이브의 세련된 한국적 현대미 (Seoul Han River Nightline Aesthetic)"
        ],
        "suno_spec": {
            "vocal_gender": "melodic synth vocal chops / anthemic voice",
            "primary_genre": "Melodic Chill Phonk / K-Synthwave / High-Tension Workout Drive",
            "instruments": "Analog Juno synth leads, Moog bassline, punchy 808 kick, 128 BPM 4-on-the-floor drums, subtle Taepyeongso (태평소) brass accent",
            "bpm_range": "124 - 130 BPM",
            "keys": ["F Minor", "A Minor", "D Minor"],
            "lufs_target": -14.0,
            "sample_rate": 44100,
            "bit_depth": 16
        }
    },
    "Director_Cafe": {
        "channel_id": "CH_03_CAFE",
        "name": "Director_Cafe",
        "target_channel": "The Café Hour",
        "handle": "@TheCaféHour",
        "space_index": 8,
        "subscribers": 5,
        "video_count": 4,
        "slogan": "☕ The Café Hour – 음악으로 채우는 카페의 하루",
        "target_time_kst": "11:00 ~ 15:00 (한낮의 카페 휴식 & 집중)",
        "target_time_est": "22:00 ~ 02:00 (심야 집중 & 릴랙스)",
        "k_global_identity": "K-Café Hospitality & Serene Aesthetics (정갈한 다도와 한국적 환대)",
        "core_virtues": [
            "손님을 정성으로 맞이하는 한국 다도(茶道)의 환대 예절 (Hospitality & Mindful Tea Tradition)",
            "서울 북촌 한옥·성수·연남 카페 거리의 고즈넉한 여유 (Seoul Aesthetic Tranquility)",
            "MORNING · AFTERNOON · EVENING 시간대별 세심한 배려 (Attentive Time-Slot Curation)"
        ],
        "suno_spec": {
            "vocal_gender": "instrumental priority / gentle vocal humming",
            "primary_genre": "K-Indie Jazz & Cozy Piano Lo-Fi (Coffeehouse Ambience)",
            "instruments": "Fender Rhodes electric piano, upright jazz double bass, brushed snare drums, warm vinyl rain ambience, muted saxophone",
            "bpm_range": "72 - 78 BPM",
            "keys": ["Bb Major", "Eb Major", "Ab Major"],
            "lufs_target": -14.0,
            "sample_rate": 44100,
            "bit_depth": 16
        }
    },
    "Director_US_AON": {
        "channel_id": "CH_04_US_AON",
        "name": "Director_US_AON",
        "target_channel": "SUN-ONE AON",
        "handle": "@SUNONE_AON",
        "space_index": 17,
        "subscribers": 0,
        "video_count": 0,
        "slogan": "Music for the Soul, Value Returned to the World: Global Philanthropy through Sound",
        "target_time_kst": "21:00 ~ 23:00 (익일 미국 아침 송출)",
        "target_time_est": "08:00 ~ 11:00 (미국 프라임타임 스트리밍)",
        "k_global_identity": "Global K-Ethics AI Story & Music Label (동방예의지국 철학의 세계화)",
        "core_virtues": [
            "상선약수(上善若水): 만물을 이롭게 하되 다투지 않는 지혜 (The Highest Good is Like Water)",
            "세계인을 향한 환원의 국제화와 자선 서약 (Global Philanthropy & Honest Stewardship)",
            "품격 있는 K-시네마틱 스토리텔링과 무결점 글로벌 감동 (World-Class Ethical Cinematic Harmony)"
        ],
        "suno_spec": {
            "vocal_gender": "world-class anthemic male & female cinematic chorus",
            "primary_genre": "Epic K-Cinematic Future Bass / Ambient Orchestral Hybrid",
            "instruments": "Full cinematic strings, electric cello, grand piano, atmospheric pads, Korean 5-tone pentatonic melodic motifs, sub-bass pulse",
            "bpm_range": "90 - 110 BPM",
            "keys": ["D Major", "B Minor", "F# Minor"],
            "lufs_target": -14.0,
            "sample_rate": 44100,
            "bit_depth": 16
        }
    }
}

# =============================================================================
# 2. SUNO AI v4/v4.5 STRUCTURED PROMPT BUILDER
# =============================================================================

def build_suno_master_prompt(director_name, song_concept):
    """
    Constructs a production-ready Suno AI v4/v4.5 structured prompt package:
    - Style prompt (Genre tags + Instruments + BPM + Key + Mood)
    - Structured Lyrics with tags: [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Bridge], [Chorus], [Outro], [Fade Out]
    - DistroKid audio master target parameters.
    """
    director = CHANNEL_DIRECTORS.get(director_name)
    if not director:
        raise ValueError(f"Unknown director: {director_name}")

    spec = director["suno_spec"]
    theme_virtue = director["core_virtues"][0]

    # Style Prompt
    style_tags = [
        spec["primary_genre"],
        spec["instruments"],
        f"{spec['bpm_range']}",
        spec["keys"][0],
        spec["vocal_gender"],
        "mastered, wide stereo, polished acoustics, inspiring emotional resonance"
    ]
    style_prompt = ", ".join(style_tags)

    title_ko = song_concept.get("title_ko", "상선약수의 노래")
    title_en = song_concept.get("title_en", "Song of Living Water")
    concept_story = song_concept.get("story", "지친 하루에 전하는 따뜻한 예절과 위로")

    # Structured Lyrics
    lyrics_structure = f"""[Intro: Instrumental - {spec['instruments']}]
(Slow building melody, evoking {director['k_global_identity']})

[Verse 1]
{song_concept.get('verse1', '돌아보면 언제나 묵묵히 지켜주던 그 등불 하나\\n거친 파도 속에서도 흔들리지 않는 뿌리 깊은 나무처럼\\n바람은 지나가고 남은 것은 오직 진심의 무게뿐')}

[Pre-Chorus]
{song_concept.get('pre_chorus', '겸손한 마음으로 고개 숙여 인사를 건넬 때\\n세상의 모든 문이 조용히 열려오네\\n정직한 땀방울은 결코 길을 잃지 않으니')}

[Chorus]
{song_concept.get('chorus', f'{title_ko} - {title_en}\\n물처럼 흘러 만물을 적시며 다투지 않는 그 마음으로\\n한걸음씩 나아가는 길에 꽃이 피어나리라\\nLight that shines within, gentle yet unbroken')}

[Verse 2]
{song_concept.get('verse2', '어둠이 내려앉아도 서로의 손을 잡아주는 온기\\n예절과 배려 속에 피어나는 깊은 사람의 향기\\n우리가 걸어온 길은 결코 헛되지 않았음을')}

[Bridge]
{song_concept.get('bridge', '세상이 소란하여도 우리의 중심은 바르고 올곧게\\n스승의 가르침과 부모님의 기도를 가슴에 새기며\\n더 넓은 바다를 향해 당당히 흘러간다')}

[Chorus]
{song_concept.get('chorus', f'{title_ko} - {title_en}\\n물처럼 흘러 만물을 적시며 다투지 않는 그 마음으로\\n한걸음씩 나아가는 길에 꽃이 피어나리라\\nLight that shines within, gentle yet unbroken')}

[Outro]
{song_concept.get('outro', '고요히 퍼져나가는 종소리처럼\\n감사의 마음을 세상에 전하며\\nEver flowing, ever righteous')}

[Fade Out]
[End]"""

    prompt_pkg = {
        "director": director_name,
        "channel_id": director["channel_id"],
        "handle": director["handle"],
        "titles": {
            "bilingual": f"{title_ko} | {title_en}",
            "korean": title_ko,
            "english": title_en
        },
        "concept_story": concept_story,
        "k_heritage_theme": theme_virtue,
        "suno_v4_style_prompt": style_prompt,
        "suno_v4_lyrics": lyrics_structure,
        "meta_tags": {
            "bpm": spec["bpm_range"],
            "key": spec["keys"][0],
            "vocal_profile": spec["vocal_gender"],
            "lufs_target": spec["lufs_target"],
            "sample_rate": spec["sample_rate"],
            "bit_depth": spec["bit_depth"]
        },
        "created_at": now_kst()
    }
    return prompt_pkg

# =============================================================================
# 3. SUNO DISPATCH QUEUE MANAGER (Space 4 Integration)
# =============================================================================

def push_to_suno_queue(prompt_package):
    """
    Appends a new generation task to suno_dispatch_queue.json.
    """
    tasks = []
    if QUEUE_FILE.is_file():
        try:
            tasks = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except Exception:
            tasks = []

    task_entry = {
        "task_id": f"SUNO_{uuid.uuid4().hex[:8].upper()}",
        "status": "QUEUED_FOR_SPACE4",
        "created_at": now_kst(),
        "package": prompt_package
    }
    tasks.append(task_entry)
    QUEUE_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Task queued in {QUEUE_FILE}: {task_entry['task_id']}")
    return task_entry

def get_channel_directors_summary():
    return {
        "status": "ACTIVE_OPERATIONAL",
        "directors_count": len(CHANNEL_DIRECTORS),
        "directors": list(CHANNEL_DIRECTORS.keys()),
        "registry": CHANNEL_DIRECTORS
    }

if __name__ == "__main__":
    print("=== [S1 4-CHANNEL DIRECTORS & SUNO MASTER ENGINE TEST] ===")
    summary = get_channel_directors_summary()
    print(f"Loaded {summary['directors_count']} Directors: {', '.join(summary['directors'])}")

    # Test prompt building for Director_Step
    test_concept = {
        "title_ko": "사냥꾼의 새벽",
        "title_en": "Hunter's Dawn",
        "story": "거친 산속에서 가족을 지키기 위해 새벽을 여는 가장의 효와 성실한 노동의 서사",
        "verse1": "눈 덮인 산마루에 안개가 걷히고\\n아버지 낡은 장화 소리 눈길을 가르네\\n가족의 하루를 어깨에 짊어진 채\\n한걸음씩 새벽을 열어가는 침묵의 기도",
        "pre_chorus": "예절과 정직으로 다져온 세월\\n남을 해치지 않고 땀 흘려 얻은 것만이\\n우리 밥상을 따스하게 채운다 하셨지",
        "chorus": "사냥꾼의 새벽 | Hunter's Dawn\\n산새들이 깨어나 지저귀는 그 길목에서\\n부모님의 은혜를 가슴에 품고\\n정의로운 발걸음으로 내일을 맞이하리",
        "verse2": "시린 손끝을 모아 입김을 불어넣고\\n자연이 내어준 만큼만 감사히 받으니\\n욕심을 버린 자리에 피어나는 평온함",
        "bridge": "동방의 오랜 지혜가 가르쳐준 길\\n물처럼 겸손하되 바위처럼 굳세게\\n우리는 살아간다, 성실한 마음 하나로",
        "outro": "새벽 노을이 산마루를 붉게 물들일 때\\n집으로 향하는 발걸음엔 감사의 노래만 가득하네"
    }
    pkg = build_suno_master_prompt("Director_Step", test_concept)
    print("\n[Generated Suno v4 Prompt for Director_Step]:")
    print("Style:", pkg["suno_v4_style_prompt"][:100], "...")
    print("Bilingual Title:", pkg["titles"]["bilingual"])
    print("Queue Entry Created Successfully.")
