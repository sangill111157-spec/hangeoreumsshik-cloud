# -*- coding: utf-8 -*-
"""
S1 DistroKid Release Manager & Reverse Schedule Planner (s1_distrokid_release_manager.py)

Manages:
1. Reverse schedule calculation based on Release Date (D-Day):
   - D-14 to D-7: Suno production, 44.1kHz 16-bit WAV mastering, 3000x3000 album cover, DistroKid metadata package
   - D-3: 15-30s Preview Shorts & YouTube Community Tab teaser
   - D-Day: Full 1080p MV / 55-60m Compilation Playlist & YouTube Scheduled Upload package
2. DistroKid Submission Specification (ISRC/UPC, Songwriter, Producer, Clean Rating, 150+ Stores).
3. 5 Master Google Sheets Ledgers synchronization.
"""

import os
import sys
import csv
import json
import uuid
import pathlib
import datetime
from s1_channel_directors import CHANNEL_DIRECTORS, build_suno_master_prompt
from s1_playlist_compiler import compile_playlist_manifest

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = pathlib.Path(__file__).resolve().parent
VAULT_DIR = ROOT_DIR / "studio_vault" / "K_GLOBAL_PACKAGES"
LEDGERS_DIR = ROOT_DIR / "master_ledgers"

def now_kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def calculate_schedule_milestones(d_day_dt):
    """
    Computes D-14, D-7, D-3, and D-Day milestone timestamps.
    """
    d14 = d_day_dt - datetime.timedelta(days=14)
    d7 = d_day_dt - datetime.timedelta(days=7)
    d3 = d_day_dt - datetime.timedelta(days=3)
    return {
        "d_minus_14": d14.strftime("%Y-%m-%d %H:%M:%S KST"),
        "d_minus_7": d7.strftime("%Y-%m-%d %H:%M:%S KST"),
        "d_minus_3": d3.strftime("%Y-%m-%d %H:%M:%S KST"),
        "d_day": d_day_dt.strftime("%Y-%m-%d %H:%M:%S KST")
    }

def create_distrokid_release_package(director_name, song_concept, target_release_date_str=None):
    """
    Builds a complete DistroKid release and reverse schedule package for a given channel director.
    """
    director = CHANNEL_DIRECTORS.get(director_name)
    if not director:
        raise ValueError(f"Unknown director: {director_name}")

    if target_release_date_str:
        try:
            d_day_dt = datetime.datetime.fromisoformat(target_release_date_str)
        except Exception:
            d_day_dt = datetime.datetime.now() + datetime.timedelta(days=14)
    else:
        # Default release 14 days ahead
        d_day_dt = datetime.datetime.now() + datetime.timedelta(days=14)

    milestones = calculate_schedule_milestones(d_day_dt)
    release_id = f"REL_{director['channel_id']}_{uuid.uuid4().hex[:6].upper()}"

    title_ko = song_concept.get("title_ko", "동방예의지국의 선율")
    title_en = song_concept.get("title_en", "Melody of Courtesy")
    bilingual_title = f"{title_ko} | {title_en}"

    # 1. DistroKid Submission Metadata
    isrc_code = f"KR-S01-26-{uuid.uuid4().hex[:5].upper()}"
    distrokid_metadata = {
        "release_id": release_id,
        "director": director_name,
        "channel_id": director["channel_id"],
        "handle": director["handle"],
        "album_title": bilingual_title,
        "track_title": bilingual_title,
        "track_version": "Original Master (Clean)",
        "artist_name": f"{director['target_channel']} (SUN-ONE AON)",
        "featured_artist": "Sangill Lee",
        "songwriter": "Sangill Lee (이상일)",
        "composer": "Sangill Lee (이상일) & SUN-ONE AON Engine",
        "producer": "SUN-ONE Studio (Executive Producer: Sangill Lee)",
        "record_label": "SUN-ONE Records / AON Philanthropy Sound",
        "isrc": isrc_code,
        "upc": f"UPC-{uuid.uuid4().hex[:8].upper()}",
        "primary_genre": director["suno_spec"]["primary_genre"].split("/")[0].strip(),
        "secondary_genre": "K-Heritage / World Cinematic",
        "language": "Korean & English (Bilingual)",
        "explicit": "No (Clean, Safe for All Audiences)",
        "target_release_date": milestones["d_day"],
        "distribution_scope": "Worldwide (150+ Digital Streaming Platforms including Spotify, Apple Music, YouTube Music, Amazon, TikTok, Melon, Bugs, Flo, Genie)",
        "audio_format": {
            "format": "WAV",
            "sample_rate": 44100,
            "bit_depth": 16,
            "channels": 2,
            "integrated_lufs": -14.0,
            "true_peak_db": -1.5
        },
        "artwork_spec": {
            "resolution": "3000 x 3000 px",
            "aspect_ratio": "1:1 Square",
            "color_space": "RGB",
            "format": "PNG / TIFF (300 DPI)",
            "requirements": "Exact title matching, high resolution, no blurred edges, zero social links on cover"
        },
        "k_courtesy_bio": f"Rooted in Korea's timeless 'Eastern Land of Courtesy' (동방예의지국) heritage and Sangseonyaksu ('The highest excellence is like water'), this release embodies {director['core_virtues'][0]}."
    }

    # 2. D-3 Teaser Shorts & Community Package
    d3_teaser = {
        "shorts_title": f"[Shorts] {bilingual_title} - 3일 뒤 대공개! #Shorts",
        "duration_seconds": 25,
        "highlight_section": "Chorus (0:45 - 1:10)",
        "bilingual_caption": f"🌿 {director['slogan']}\n\n동방예의지국의 따뜻한 온기와 지혜를 전하는 '{title_ko}' 음원이 {milestones['d_day'][:10]} 전 세계 음원 사이트 및 유튜브에 정식 발매됩니다!\n\n#한걸음씩 #부스터플리 #TheCaféHour #SUNONE_AON #KGlobal #동방예의지국 #Shorts",
        "community_post": f"📢 [SUN-ONE Official Release Notice]\n\n사랑하는 구독자 여러분, 안녕하세요!\n{director['target_channel']} 전담 총감독 {director_name}입니다.\n\n동방예의지국의 깊은 정(Jeong)과 올바른 삶의 성실함을 담은 신곡 『{bilingual_title}』이 D-3일 앞으로 다가왔습니다.\n\n- 음원 스트리밍: Spotify, Apple Music, 멜론, 벅스 전 세계 동시 공개\n- 유튜브 본편 및 롱폼 플레이리스트: {milestones['d_day']} 공개\n\n많은 관심과 따뜻한 응원 부탁드립니다! 감사드립니다."
    }

    # 3. D-Day Full MV & Scheduled Upload Package
    d_day_package = {
        "youtube_title": f"{bilingual_title} - Official K-Global Audio & Video",
        "target_channel": director["target_channel"],
        "handle": director["handle"],
        "scheduled_time_kst": milestones["d_day"],
        "scheduled_time_est": (d_day_dt - datetime.timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S EST"),
        "category_id": "10 (Music)",
        "privacy_status": "private (Scheduled for Premiere)",
        "ai_disclosure_statement": "Altered or synthetic content: Sound and visuals generated with customized AI models and masterfully curated/produced by SUN-ONE Studio.",
        "tags": [
            "K-Global", "동방예의지국", "K-Wisdom", "K-Ballad", "K-LoFi", "K-Synthwave",
            director["target_channel"], director["handle"], "Sangill Lee", "SUN-ONE AON"
        ]
    }

    # 4. Longform Compilation Playlist (for Booster & Cafe)
    longform_manifest = None
    if director_name in ["Director_Booster", "Director_Cafe"]:
        sample_tracks = [
            {"title_ko": f"{title_ko} Part 1", "title_en": f"{title_en} Part 1", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 240},
            {"title_ko": f"{title_ko} Part 2", "title_en": f"{title_en} Part 2", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 250},
            {"title_ko": f"{title_ko} Part 3", "title_en": f"{title_en} Part 3", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 260},
            {"title_ko": f"{title_ko} Part 4", "title_en": f"{title_en} Part 4", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 240},
            {"title_ko": f"{title_ko} Part 5", "title_en": f"{title_en} Part 5", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 250},
            {"title_ko": f"{title_ko} Part 6", "title_en": f"{title_en} Part 6", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 240},
            {"title_ko": f"{title_ko} Part 7", "title_en": f"{title_en} Part 7", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 260},
            {"title_ko": f"{title_ko} Part 8", "title_en": f"{title_en} Part 8", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 250},
            {"title_ko": f"{title_ko} Part 9", "title_en": f"{title_en} Part 9", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 240},
            {"title_ko": f"{title_ko} Part 10", "title_en": f"{title_en} Part 10", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 250},
            {"title_ko": f"{title_ko} Part 11", "title_en": f"{title_en} Part 11", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 240},
            {"title_ko": f"{title_ko} Part 12", "title_en": f"{title_en} Part 12", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 260},
            {"title_ko": f"{title_ko} Part 13", "title_en": f"{title_en} Part 13", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 250},
            {"title_ko": f"{title_ko} Part 14", "title_en": f"{title_en} Part 14", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 240},
            {"title_ko": f"{title_ko} Part 15", "title_en": f"{title_en} Part 15", "bpm": 128 if "Booster" in director_name else 75, "duration_sec": 260}
        ]
        longform_manifest = compile_playlist_manifest(
            channel_handle=director["handle"],
            playlist_title=f"{bilingual_title} - 60 Min Full Compilation Playlist",
            tracks_data=sample_tracks,
            target_duration_minutes=60
        )

    full_package = {
        "release_id": release_id,
        "director": director_name,
        "milestones": milestones,
        "distrokid_metadata": distrokid_metadata,
        "d3_teaser": d3_teaser,
        "d_day_package": d_day_package,
        "longform_compilation": longform_manifest,
        "status": "PREPARED_FOR_RELEASE_GATE",
        "created_at": now_kst()
    }

    return full_package

def sync_distrokid_to_master_ledgers(release_packages):
    """
    Appends/updates release schedule data to master_ledgers/06_DISTROKID_RELEASE_LEDGER.csv
    and updates MASTER_LEDGERS_INDEX.json.
    """
    LEDGERS_DIR.mkdir(parents=True, exist_ok=True)
    ledger_file = LEDGERS_DIR / "06_DISTROKID_RELEASE_LEDGER.csv"

    fieldnames = [
        "릴리즈ID", "채널ID", "채널명", "담당에이전트", "발매곡명_한영", "발매일_KST",
        "발매일_EST", "ISRC코드", "UPC코드", "음원규격", "커버규격", "쇼츠티저일", "동방예의지국철학", "출격게이트상태"
    ]

    rows = []
    for pkg in release_packages:
        meta = pkg["distrokid_metadata"]
        rows.append({
            "릴리즈ID": pkg["release_id"],
            "채널ID": meta["channel_id"],
            "채널명": meta["artist_name"],
            "담당에이전트": pkg["director"],
            "발매곡명_한영": meta["album_title"],
            "발매일_KST": pkg["milestones"]["d_day"],
            "발매일_EST": pkg["d_day_package"]["scheduled_time_est"],
            "ISRC코드": meta["isrc"],
            "UPC코드": meta["upc"],
            "음원규격": "44.1kHz 16bit WAV (-14.0 LUFS)",
            "커버규격": "3000x3000px RGB PNG",
            "쇼츠티저일": pkg["milestones"]["d_minus_3"],
            "동방예의지국철학": meta["k_courtesy_bio"],
            "출격게이트상태": "SHA8_GATE_STANDBY"
        })

    with open(ledger_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"DistroKid Master Ledger updated: {ledger_file} ({len(rows)} releases)")

    # Update index
    index_file = LEDGERS_DIR / "MASTER_LEDGERS_INDEX.json"
    if index_file.is_file():
        try:
            idx_data = json.loads(index_file.read_text(encoding="utf-8"))
            idx_data["ledgers"]["06_distrokid_release_ledger"] = {
                "file": "06_DISTROKID_RELEASE_LEDGER.csv",
                "format": "UTF-8 with BOM CSV",
                "description": "4대 채널 DistroKid 글로벌 음원 등록 및 D-14 역산 릴리즈 스케줄 원장",
                "total_rows": len(rows),
                "updated_at": now_kst()
            }
            index_file.write_text(json.dumps(idx_data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print("Notice: could not update master ledgers index:", e)

    return ledger_file

if __name__ == "__main__":
    print("=== [S1 DISTROKID RELEASE MANAGER TEST] ===")
    test_pkg = create_distrokid_release_package(
        director_name="Director_Step",
        song_concept={
            "title_ko": "사냥꾼의 새벽",
            "title_en": "Hunter's Dawn"
        }
    )
    print("Release ID:", test_pkg["release_id"])
    print("Milestones:", test_pkg["milestones"])
    print("ISRC:", test_pkg["distrokid_metadata"]["isrc"])
    print("Shorts Title:", test_pkg["d3_teaser"]["shorts_title"])
    sync_distrokid_to_master_ledgers([test_pkg])

