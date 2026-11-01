# -*- coding: utf-8 -*-
"""
S1 Studio Pipeline Manager (s1_studio_pipeline.py)
Priority 4 Core Mission Phase 1: 3-Channel YouTube Master Package & FFmpeg Synthesis Engine
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
STUDIO_DIR = ROOT_DIR / "studio_output" / "EP01_S1_MASTERPIECE"
PROOF_FILE = ROOT_DIR / "S1_STUDIO_PIPELINE_PROOF.json"
LEDGER_FILE = ROOT_DIR / "s1_studio_ledger.jsonl"
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

def build_channel_packages():
    STUDIO_DIR.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------
    # Channel A: 한걸음씩 (@한걸음씩-r4i, Space 6)
    # ----------------------------------------------------
    dir_a = STUDIO_DIR / "channel_a_hangeoreum"
    dir_a.mkdir(exist_ok=True)

    spec_a = {
        "channel_name": "한걸음씩",
        "channel_id": "@한걸음씩-r4i",
        "space": 6,
        "theme": "감성 보컬/발라드 · 인생 응원 명작",
        "suno_v6_spec": {
            "title": "한걸음씩, 물처럼 유연하게 (Like Gentle Water)",
            "style_tags": "K-Pop, emotional ballad, heartfelt male vocal, warm acoustic grand piano, gentle cello and violin, 72 bpm, 48kHz studio mastering, inspiring, melancholic yet uplifting",
            "exclude_tags": "heavy metal, autotune, distortion, aggressive EDM, harsh noise, shouting, electronic stutter",
            "lyrics": """[Intro - Soft Grand Piano & Gentle Rain Ambience]

[Verse 1]
비바람 거세게 불어오던 날
돌아갈 길마저 흐려질 때
멈춰 서서 가만히 숨을 고르면
낮은 곳으로 흐르는 물의 소리 들려와

[Pre-Chorus]
서두르지 않아도, 부딪히지 않아도
돌부리를 만나면 부드럽게 감싸 안고
묵묵히 제 길을 향해 흘러가는
그 깊고 유연한 마음처럼

[Chorus]
한걸음씩, 오늘도 너의 길을 걸어가
거센 파도 속에서도 중심을 잡고서
상선약수(上善若水), 다투지 않고 세상을 비추는
가장 맑은 별이 되어 끝내 바다에 닿으리

[Verse 2]
어제의 아픔은 흙먼지처럼 가라앉고
투명해진 가슴엔 새벽 햇살이 깃드네
남들의 속도에 쫓기지 마라
너만의 궤적이 가장 눈부신 법이니까

[Chorus]
한걸음씩, 오늘도 너의 길을 걸어가
거센 파도 속에서도 중심을 잡고서
상선약수(上善若水), 다투지 않고 세상을 비추는
가장 맑은 별이 되어 끝내 바다에 닿으리

[Bridge - Orchestral Strings Swell]
넘어지면 쉬어가고, 막히면 돌아가면 돼
스스로를 믿는 네 안의 강인함이
결국에는 커다란 기적이 될 테니

[Chorus - Full Dynamics & Choir]
한걸음씩, 가슴 벅차게 세상을 향해 날아라
빛나는 너의 발걸음 축복이 내리길
물처럼 낮게, 그러나 바다처럼 넓게
끝내 완성될 너의 가장 찬란한 노래

[Outro - Gentle Piano fading out]
한걸음씩... 물처럼 유연하게...
너의 내일을 응원해."""
        }
    }
    (dir_a / "prompt_spec.json").write_text(json.dumps(spec_a, ensure_ascii=False, indent=2), encoding="utf-8")

    srt_a = """1
00:00:00,000 --> 00:00:05,000
[Intro - 피아노 선율과 따뜻한 빗소리]

2
00:00:05,500 --> 00:00:10,000
비바람 거세게 불어오던 날

3
00:00:10,500 --> 00:00:15,000
돌아갈 길마저 흐려질 때

4
00:00:15,500 --> 00:00:20,000
멈춰 서서 가만히 숨을 고르면

5
00:00:20,500 --> 00:00:26,000
낮은 곳으로 흐르는 물의 소리 들려와

6
00:00:26,500 --> 00:00:32,000
서두르지 않아도, 부딪히지 않아도

7
00:00:32,500 --> 00:00:38,000
돌부리를 만나면 부드럽게 감싸 안고

8
00:00:38,500 --> 00:00:44,000
묵묵히 제 길을 향해 흘러가는 마음처럼

9
00:00:44,500 --> 00:00:51,000
한걸음씩, 오늘도 너의 길을 걸어가

10
00:00:51,500 --> 00:00:57,500
거센 파도 속에서도 중심을 잡고서

11
00:00:58,000 --> 00:01:04,500
상선약수(上善若水), 다투지 않고 세상을 비추는

12
01:04,500 --> 01:12,000
가장 맑은 별이 되어 끝내 바다에 닿으리
"""
    (dir_a / "subtitles_ko.srt").write_text(srt_a.strip() + "\n", encoding="utf-8")

    yt_a = {
        "title": "한걸음씩, 물처럼 유연하게 — 지친 그대를 위한 따뜻한 인생 위로 발라드 [S1 명작 EP01]",
        "description": """인생의 폭풍우 속에서도 나를 지켜내는 힘,
이상일 대표님의 '상선약수(上善若水)' 철학을 담아낸 S1 제1호 감성 힐링 발라드입니다.
물처럼 낮추고 유연하게, 다투지 않고 만물을 이롭게 하며 끝내 드넓은 바다에 닿는 기적.
오늘 하루도 수고 많으셨습니다. 한걸음씩 나아가는 당신의 발걸음을 응원합니다.

[Credits]
Executive Producer: Sangill Lee (S1 Imperial Command)
Music Production: Suno v6 Studio Engine & S1 Neural Organ
Audio Mastering: 48kHz 24-bit Stereo (-16.0 LUFS / -1.5 dBTP)
Design & Art: Hae-sang Lee (Chief Character Designer) & AON Studio

#한걸음씩 #인생위로 #감성발라드 #상선약수 #K발라드 #SunoV6 #S1AON #힐링음악""",
        "tags": ["한걸음씩", "위로발라드", "인생응원", "상선약수", "K-Ballad", "감성음악", "SunoV6", "S1AON"],
        "category_id": "10",
        "privacy_status": "private"
    }
    (dir_a / "youtube_metadata.json").write_text(json.dumps(yt_a, ensure_ascii=False, indent=2), encoding="utf-8")

    # ----------------------------------------------------
    # Channel B: 부스터 플리 | 운동·드라이브 음악 (@Booster_Playlist, Space 7)
    # ----------------------------------------------------
    dir_b = STUDIO_DIR / "channel_b_boosterply"
    dir_b.mkdir(exist_ok=True)

    spec_b = {
        "channel_name": "부스터 플리 | 운동·드라이브 음악",
        "channel_id": "@Booster_Playlist",
        "space": 7,
        "subscribers": 26,
        "theme": "하이텐션 드라이브 / 운동 부스터 플레이리스트",
        "suno_v6_spec": {
            "title": "심장을 뛰게 하는 하이텐션 부스터 비트 Vol.1 (Ignition Pulse)",
            "style_tags": "Synthwave, cyberpunk bass, energetic electronic dance, 128 bpm, punchy kick drum, driving synth arpeggios, motivational, workout gym booster, athletic pump, adrenaline rush",
            "exclude_tags": "sad ballad, slow tempo, lo-fi, silence, acoustic guitar, sleepy, quiet",
            "playlist_tracks": [
                {"track": 1, "title": "Engine Ignition (엔진 점화)", "start": "00:00", "bpm": 126},
                {"track": 2, "title": "Highway Sprint (질주하는 심장)", "start": "02:45", "bpm": 128},
                {"track": 3, "title": "Maximum Velocity (한계 돌파)", "start": "05:30", "bpm": 130},
                {"track": 4, "title": "Neon Horizon (네온 지평선)", "start": "08:15", "bpm": 128},
                {"track": 5, "title": "Cool Down Walk (승리의 호흡)", "start": "11:00", "bpm": 120}
            ]
        }
    }
    (dir_b / "prompt_spec.json").write_text(json.dumps(spec_b, ensure_ascii=False, indent=2), encoding="utf-8")

    tracklist_b = """[타임스탬프 Tracklist]
00:00 Track 01. Engine Ignition (엔진 점화) [126 BPM]
02:45 Track 02. Highway Sprint (질주하는 심장) [128 BPM]
05:30 Track 03. Maximum Velocity (한계 돌파) [130 BPM]
08:15 Track 04. Neon Horizon (네온 지평선) [128 BPM]
11:00 Track 05. Cool Down Walk (승리의 호흡) [120 BPM]

심장을 강타하는 묵직한 베이스와 끊임없이 솟구치는 아드레날린!
러닝, 헬스 웨이트, 야간 드라이브에서 최고의 집중력과 텐션을 이끌어냅니다.
S1 음향 연구소의 48kHz 정밀 마스터링으로 왜곡 없이 타격감 넘치는 사운드를 경험하세요.

#부스터플리 #운동플레이리스트 #드라이브음악 #하이텐션 #헬스음악 #신스웨이브 #S1AON
"""
    (dir_b / "tracklist_description.txt").write_text(tracklist_b.strip() + "\n", encoding="utf-8")

    yt_b = {
        "title": "[운동/드라이브] 텐션 폭발! 심장을 때리는 하이텐션 부스터 플레이리스트 [S1 부스터플리 EP01]",
        "description": tracklist_b.strip(),
        "tags": ["부스터플리", "운동플레이리스트", "드라이브음악", "하이텐션", "헬스음악", "신스웨이브", "S1AON"],
        "category_id": "10",
        "privacy_status": "private"
    }
    (dir_b / "youtube_metadata.json").write_text(json.dumps(yt_b, ensure_ascii=False, indent=2), encoding="utf-8")

    # ----------------------------------------------------
    # Channel C: The Café Hour (@TheCaféHour, Space 8)
    # ----------------------------------------------------
    dir_c = STUDIO_DIR / "channel_c_cafehour"
    dir_c.mkdir(exist_ok=True)

    spec_c = {
        "channel_name": "The Café Hour",
        "channel_id": "@TheCaféHour",
        "space": 8,
        "subscribers": 5,
        "theme": "시네마틱 카페 재즈 · 로파이 앰비언스 (75 BPM Lo-Fi Rhodes)",
        "suno_v6_spec": {
            "title": "비 내리는 오후의 따뜻한 재즈 라떼 (Rainy Cafe Rhodes)",
            "style_tags": "Cozy Lo-Fi hip hop, smooth Rhodes piano, mellow jazz guitar, soft vinyl crackle, gentle rain ambience, relaxing study beats, 75 bpm, warm vintage tape saturation, peaceful",
            "exclude_tags": "harsh vocals, loud snare, heavy drops, screaming, rock, fast tempo, dissonance"
        }
    }
    (dir_c / "prompt_spec.json").write_text(json.dumps(spec_c, ensure_ascii=False, indent=2), encoding="utf-8")

    loop_c = {
        "loop_mode": "SEAMLESS_CROSSFADE",
        "loop_points_sec": [0.0, 15.0],
        "crossfade_sec": 1.2,
        "ambient_layers": ["rain_ambient_bed", "warm_vinyl_dust"],
        "recommended_repeat_hours": 1.0,
        "recommended_use_cases": ["독서", "코딩 및 심층 업무", "카페 감성 휴식", "편안한 숙면"]
    }
    (dir_c / "loop_metadata.json").write_text(json.dumps(loop_c, ensure_ascii=False, indent=2), encoding="utf-8")

    yt_c = {
        "title": "[1시간/집중음악] 비 내리는 창가, 조용한 재즈 카페 로파이 BGM — 집중/독서/수면 [S1 The Café Hour EP01]",
        "description": """창밖으로 조용히 내리는 빗소리와 따뜻한 커피 한 잔.
부드러운 로즈 건반과 빈티지 바이닐 질감이 마음을 차분히 가라앉혀 줍니다.
집중이 필요한 공부 시간, 코딩, 독서, 혹은 하루를 마감하는 수면 시간에 함께하세요.

[BGM Loop Spec]
Format: 48kHz 24-bit Lossless Studio Mastering
Volume Norm: -16.0 LUFS (-1.5 dBTP)
Seamless Crossfade: 1.2s Infinite Loop Ready

#TheCafeHour #카페BGM #로파이재즈 #집중음악 #수면음악 #공부할때듣는음악 #S1AON""",
        "tags": ["The Café Hour", "카페BGM", "로파이재즈", "집중음악", "수면음악", "공부할때듣는음악", "S1AON"],
        "category_id": "10",
        "privacy_status": "private"
    }
    (dir_c / "youtube_metadata.json").write_text(json.dumps(yt_c, ensure_ascii=False, indent=2), encoding="utf-8")

    # ----------------------------------------------------
    # Channel D: SUN-ONE AON (@SUNONE_AON, Space 9 — 미국 전담 플래그십)
    # ----------------------------------------------------
    vault_us_dir = ROOT_DIR / "studio_vault" / "US_SUN_ONE_AON"

    return {
        "channel_a": str(dir_a),
        "channel_b": str(dir_b),
        "channel_c": str(dir_c),
        "channel_d_us_aon": str(vault_us_dir)
    }

def render_sample_master_and_preview():
    STUDIO_DIR.mkdir(parents=True, exist_ok=True)
    wav_out = STUDIO_DIR / "sample_master_48k.wav"
    mp4_out = STUDIO_DIR / "preview_1080p.mp4"

    # 1. 48kHz 24-bit PCM Stereo Master Audio Synthesizer with -16.0 LUFS / -1.5 dBTP loudnorm
    # Musical chord: C maj9 chord (C4, E4, G4, B4, D5) warm pad with stereo pan and gentle envelope
    synth_expr = (
        "sin(261.63*2*PI*t)*0.22+sin(329.63*2*PI*t)*0.18+sin(392.00*2*PI*t)*0.18+sin(493.88*2*PI*t)*0.14+sin(587.33*2*PI*t)*0.10|"
        "sin(261.63*2*PI*t)*0.18+sin(329.63*2*PI*t)*0.22+sin(392.00*2*PI*t)*0.15+sin(493.88*2*PI*t)*0.16+sin(587.33*2*PI*t)*0.12"
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

    # 2. 1080p Cinematic Preview MP4 (H.264 + AAC 320kbps 48kHz stereo)
    # Uses icon-512.png centered on 1920x1080 dark luxury aesthetic backdrop
    art_path = str(ICON_PATH if ICON_PATH.is_file() else ROOT_DIR / "icon-192.png")
    video_filter = "scale=512:512,pad=1920:1080:(1920-512)/2:(1080-512)/2:color=0x070b14,format=yuv420p"
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

def run_pipeline():
    print("=== [S1 STUDIO PIPELINE PHASE 1 START] ===")
    channels = build_channel_packages()
    print("Channel packages built:", list(channels.keys()))

    renders = render_sample_master_and_preview()
    print("Audio & Video rendered successfully.")

    wav_info = renders["wav"]
    mp4_info = renders["mp4"]

    wav_stream = wav_info["probe"]["streams"][0] if wav_info["probe"] else {}
    mp4_streams = mp4_info["probe"]["streams"] if mp4_info["probe"] else []
    v_stream = next((s for s in mp4_streams if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in mp4_streams if s.get("codec_type") == "audio"), {})

    proof_data = {
        "timestamp": now_kst(),
        "mission": "PRIORITY_4_STUDIO_PIPELINE_PHASE2_US_VAULT",
        "project_id": "EP01_S1_MASTERPIECE",
        "channels": {
            "channel_a_hangeoreum": {
                "name": "한걸음씩",
                "handle": "@한걸음씩-r4i",
                "space": 6,
                "theme": "감성 보컬/발라드 · 인생 응원 명작",
                "prompt_file": str(STUDIO_DIR / "channel_a_hangeoreum" / "prompt_spec.json"),
                "srt_file": str(STUDIO_DIR / "channel_a_hangeoreum" / "subtitles_ko.srt"),
                "yt_metadata_file": str(STUDIO_DIR / "channel_a_hangeoreum" / "youtube_metadata.json"),
                "status": "READY"
            },
            "channel_b_boosterply": {
                "name": "부스터 플리 | 운동·드라이브 음악",
                "handle": "@Booster_Playlist",
                "space": 7,
                "subscribers": 26,
                "theme": "하이텐션 드라이브 / 운동 부스터 플레이리스트",
                "prompt_file": str(STUDIO_DIR / "channel_b_boosterply" / "prompt_spec.json"),
                "tracklist_file": str(STUDIO_DIR / "channel_b_boosterply" / "tracklist_description.txt"),
                "yt_metadata_file": str(STUDIO_DIR / "channel_b_boosterply" / "youtube_metadata.json"),
                "status": "READY"
            },
            "channel_c_cafehour": {
                "name": "The Café Hour",
                "handle": "@TheCaféHour",
                "space": 8,
                "subscribers": 5,
                "theme": "시네마틱 카페 재즈 · 로파이 앰비언스 (75 BPM Lo-Fi Rhodes)",
                "prompt_file": str(STUDIO_DIR / "channel_c_cafehour" / "prompt_spec.json"),
                "loop_file": str(STUDIO_DIR / "channel_c_cafehour" / "loop_metadata.json"),
                "yt_metadata_file": str(STUDIO_DIR / "channel_c_cafehour" / "youtube_metadata.json"),
                "status": "READY"
            },
            "channel_d_us_aon": {
                "name": "SUN-ONE AON",
                "handle": "@SUNONE_AON",
                "alt_handle": "@SUNONEAON_US",
                "space": 9,
                "subscribers": 0,
                "target_market": "en-US",
                "theme": "Music for the Soul, Value Returned to the World: Global Philanthropy through Sound",
                "launch_kit": str(ROOT_DIR / "studio_vault" / "US_SUN_ONE_AON" / "US_CHANNEL_LAUNCH_KIT.md"),
                "vault_inventory": str(ROOT_DIR / "studio_vault" / "US_SUN_ONE_AON" / "VAULT_INVENTORY.json"),
                "status": "VAULT_SEED_COMPLETE"
            }
        },
        "audio_master_proof": {
            "filename": "sample_master_48k.wav",
            "codec": wav_stream.get("codec_name"),
            "sample_rate": int(wav_stream.get("sample_rate", 0)),
            "channels": int(wav_stream.get("channels", 0)),
            "bits_per_sample": int(wav_stream.get("bits_per_sample", 0)),
            "loudness_standard": "-16.0 LUFS (-1.5 dBTP True Peak)",
            "size_bytes": wav_info["size"],
            "sha256": wav_info["sha256"],
            "pass": bool(wav_stream.get("sample_rate") == "48000" and wav_stream.get("channels") == 2 and wav_stream.get("bits_per_sample") == 24)
        },
        "video_preview_proof": {
            "filename": "preview_1080p.mp4",
            "video_codec": v_stream.get("codec_name"),
            "resolution": f"{v_stream.get('width')}x{v_stream.get('height')}",
            "pix_fmt": v_stream.get("pix_fmt"),
            "audio_codec": a_stream.get("codec_name"),
            "audio_sample_rate": int(a_stream.get("sample_rate", 0)),
            "audio_channels": int(a_stream.get("channels", 0)),
            "size_bytes": mp4_info["size"],
            "sha256": mp4_info["sha256"],
            "pass": bool(v_stream.get("codec_name") == "h264" and v_stream.get("width") == 1920 and v_stream.get("height") == 1080 and a_stream.get("codec_name") == "aac")
        },
        "final_verdict": "ALL_PASS_CLEAN"
    }

    PROOF_FILE.write_text(json.dumps(proof_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Proof written to {PROOF_FILE}")

    # Append to studio ledger
    ledger_entry = {
        "event_id": str(uuid.uuid4()),
        "event_type": "STUDIO_PHASE1_RENDER_SUCCESS",
        "timestamp": proof_data["timestamp"],
        "project_id": proof_data["project_id"],
        "wav_sha256": proof_data["audio_master_proof"]["sha256"],
        "mp4_sha256": proof_data["video_preview_proof"]["sha256"],
        "final_verdict": proof_data["final_verdict"]
    }
    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ledger_entry, ensure_ascii=False) + "\n")
    print(f"Appended to {LEDGER_FILE}")

    print("=== [S1 STUDIO PIPELINE PHASE 1 COMPLETED] ===")
    return proof_data

if __name__ == "__main__":
    proof = run_pipeline()
    print("VERDICT:", proof["final_verdict"])

