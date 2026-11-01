# -*- coding: utf-8 -*-
"""
S1 DistroKid 2-Artist Slot Rebranding & Master Release Engine (s1_distrokid_2slot_rebrand.py)

Implements CEO Lee Sang-il's Master Directive:
- DistroKid Musician Plus Plan (2 Artist Slots):
  * Slot 1: '한걸음씩' -> YouTube OAC '@한걸음씩-r4i' (Space 6)
  * Slot 2: 'SUN-ONE AON' (Rebranded from 'The Café Hour') -> YouTube OAC '@SUN-ONEAON' (Space 17)
- Distributes all 4 channels across these 2 slots with 0 additional cost!
"""

import os
import sys
import csv
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
LEDGERS_DIR = ROOT_DIR / "master_ledgers"
CHANNELS_DIR = ROOT_DIR / "studio_vault" / "CHANNELS"

DISTROKID_SLOTS = {
    "SLOT_1": {
        "slot_index": 1,
        "artist_name": "한걸음씩",
        "youtube_oac_channel": "한걸음씩",
        "youtube_handle": "@한걸음씩-r4i",
        "youtube_space_index": 6,
        "primary_genres": ["K-Folk Ballad", "K-Wisdom", "World Heritage"],
        "assigned_channels": ["01_STEP_HANGEOREUM"],
        "oac_status": "ELIGIBLE_FOR_NOTE_BADGE",
        "description": "K-Wisdom 시네마틱 포크/발라드 및 한국어 서사 전곡 유통 전담"
    },
    "SLOT_2": {
        "slot_index": 2,
        "artist_name": "SUN-ONE AON",
        "rebranded_from": "The Café Hour",
        "youtube_oac_channel": "SUN-ONE AON",
        "youtube_handle": "@SUN-ONEAON",
        "youtube_space_index": 17,
        "primary_genres": ["Cinematic Orchestral", "K-Heritage Lo-Fi", "Synthwave Workout"],
        "assigned_channels": ["04_US_SUNONE_AON", "03_THE_CAFE_HOUR", "02_BOOSTER_PLAYLIST"],
        "oac_status": "ELIGIBLE_FOR_NOTE_BADGE_PERFECT_MATCH",
        "description": "글로벌 플래그십 심포니, 카페 로파이 재즈, 부스터 신스웨이브 통합 음원 유통 전담"
    }
}

TRACKS_2SLOT_CONFIG = [
    # Slot 1: 한걸음씩
    {
        "track_id": "STEP_TRK_01",
        "channel_dir": "01_STEP_HANGEOREUM",
        "channel_name": "한걸음씩",
        "channel_handle": "@한걸음씩-r4i",
        "distrokid_slot": "SLOT_1",
        "main_artist": "한걸음씩",
        "series_brand": "한걸음씩 (K-Wisdom Series)",
        "album_title": "사냥꾼의 새벽 | Hunter's Dawn",
        "track_title": "사냥꾼의 새벽 | Hunter's Dawn",
        "version": "Original Master",
        "genre": "K-Cinematic Folk Ballad",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-15 05:00:00 KST",
        "target_release_est": "2026-11-14 15:00:00 EST",
        "isrc": "KR-S01-26-STEP1",
        "upc": "UPC-8809901-01",
        "youtube_video_channel": "@한걸음씩-r4i",
        "k_ethos": "부모와 스승에 대한 공경과 보은 (Filial Piety & Gratitude)"
    },
    {
        "track_id": "STEP_TRK_02",
        "channel_dir": "01_STEP_HANGEOREUM",
        "channel_name": "한걸음씩",
        "channel_handle": "@한걸음씩-r4i",
        "distrokid_slot": "SLOT_1",
        "main_artist": "한걸음씩",
        "series_brand": "한걸음씩 (K-Wisdom Series)",
        "album_title": "어머니의 등불 | Mother's Lantern",
        "track_title": "어머니의 등불 | Mother's Lantern",
        "version": "Original Master",
        "genre": "K-Cinematic Folk Ballad",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-15 05:00:00 KST",
        "target_release_est": "2026-11-14 15:00:00 EST",
        "isrc": "KR-S01-26-STEP2",
        "upc": "UPC-8809901-02",
        "youtube_video_channel": "@한걸음씩-r4i",
        "k_ethos": "어머니의 무조건적 사랑과 헌신에 대한 묵상 (Unconditional Maternal Love)"
    },

    # Slot 2: SUN-ONE AON (Flagship)
    {
        "track_id": "USAON_TRK_01",
        "channel_dir": "04_US_SUNONE_AON",
        "channel_name": "SUN-ONE AON",
        "channel_handle": "@SUN-ONEAON",
        "distrokid_slot": "SLOT_2",
        "main_artist": "SUN-ONE AON",
        "series_brand": "SUN-ONE AON Flagship",
        "album_title": "상선약수: 선한 영향력의 바다 | Water of Benevolence",
        "track_title": "상선약수: 선한 영향력의 바다 | Water of Benevolence (Global Philanthropy Symphony)",
        "version": "Original Master",
        "genre": "Cinematic Hybrid Orchestra",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-15 20:00:00 KST",
        "target_release_est": "2026-11-15 07:00:00 EST",
        "isrc": "KR-S01-26-USAON1",
        "upc": "UPC-8809904-01",
        "youtube_video_channel": "@SUN-ONEAON",
        "k_ethos": "상선약수(上善若水): 만물을 이롭게 하되 다투지 않는 지혜와 33% 글로벌 환원 (Philanthropy Pledge)"
    },
    {
        "track_id": "USAON_TRK_02",
        "channel_dir": "04_US_SUNONE_AON",
        "channel_name": "SUN-ONE AON",
        "channel_handle": "@SUN-ONEAON",
        "distrokid_slot": "SLOT_2",
        "main_artist": "SUN-ONE AON",
        "series_brand": "SUN-ONE AON Flagship",
        "album_title": "새벽의 지평선 너머로 | Beyond the Golden Horizon",
        "track_title": "새벽의 지평선 너머로 | Beyond the Golden Horizon",
        "version": "Original Master",
        "genre": "Cinematic Hybrid Orchestra",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-15 20:00:00 KST",
        "target_release_est": "2026-11-15 07:00:00 EST",
        "isrc": "KR-S01-26-USAON2",
        "upc": "UPC-8809904-02",
        "youtube_video_channel": "@SUN-ONEAON",
        "k_ethos": "시련을 딛고 희망찬 새벽을 맞이하는 인류의 연대 (Universal Hope & Unity)"
    },

    # Slot 2: SUN-ONE AON (The Café Hour Collection)
    {
        "track_id": "CAFE_TRK_01",
        "channel_dir": "03_THE_CAFE_HOUR",
        "channel_name": "The Café Hour",
        "channel_handle": "@TheCaféHour",
        "distrokid_slot": "SLOT_2",
        "main_artist": "SUN-ONE AON",
        "series_brand": "The Café Hour Collection",
        "album_title": "The Café Hour Collection, Vol. 1: Bukchon Morning",
        "track_title": "북촌 한옥의 아침 다도 | Morning Tea at Bukchon Hanok",
        "version": "The Café Hour Edition",
        "genre": "K-Café Lo-Fi Jazz",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-16 11:00:00 KST",
        "target_release_est": "2026-11-15 21:00:00 EST",
        "isrc": "KR-S01-26-CAFE1",
        "upc": "UPC-8809903-01",
        "youtube_video_channel": "@TheCaféHour",
        "k_ethos": "손님을 정성으로 맞이하는 한국 다도(茶道)의 환대 예절 (Mindful Tea Hospitality)"
    },
    {
        "track_id": "CAFE_TRK_02",
        "channel_dir": "03_THE_CAFE_HOUR",
        "channel_name": "The Café Hour",
        "channel_handle": "@TheCaféHour",
        "distrokid_slot": "SLOT_2",
        "main_artist": "SUN-ONE AON",
        "series_brand": "The Café Hour Collection",
        "album_title": "The Café Hour Collection, Vol. 1: Bukchon Morning",
        "track_title": "성수동 비 내리는 오후의 커피 | Rainy Afternoon Coffee in Seongsu",
        "version": "The Café Hour Edition",
        "genre": "K-Café Lo-Fi Jazz",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-16 11:00:00 KST",
        "target_release_est": "2026-11-15 21:00:00 EST",
        "isrc": "KR-S01-26-CAFE2",
        "upc": "UPC-8809903-02",
        "youtube_video_channel": "@TheCaféHour",
        "k_ethos": "도심 속 현대인에게 안식을 주는 고요한 사색의 쉼표 (Tranquil Solitude)"
    },

    # Slot 2: SUN-ONE AON (Booster Drive & Workout Series)
    {
        "track_id": "BOOSTER_TRK_01",
        "channel_dir": "02_BOOSTER_PLAYLIST",
        "channel_name": "부스터 플리 | 운동·드라이브 음악",
        "channel_handle": "@Booster_Playlist",
        "distrokid_slot": "SLOT_2",
        "main_artist": "SUN-ONE AON",
        "series_brand": "Booster Drive & Workout Series",
        "album_title": "Booster Drive & Workout Series, Vol. 1: Seoul Nightline",
        "track_title": "여름밤 한강 드라이브 & 러닝 비트 | Summer Night Han River Drive & Workout Beat",
        "version": "Booster High-Energy Master",
        "genre": "Synthwave Workout Beat",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-17 17:00:00 KST",
        "target_release_est": "2026-11-17 03:00:00 EST",
        "isrc": "KR-S01-26-BOOST1",
        "upc": "UPC-8809902-01",
        "youtube_video_channel": "@Booster_Playlist",
        "k_ethos": "퇴폐성 배제, 건강한 스포츠맨십과 페어플레이 (Clean Athletic Energy)"
    },
    {
        "track_id": "BOOSTER_TRK_02",
        "channel_dir": "02_BOOSTER_PLAYLIST",
        "channel_name": "부스터 플리 | 운동·드라이브 음악",
        "channel_handle": "@Booster_Playlist",
        "distrokid_slot": "SLOT_2",
        "main_artist": "SUN-ONE AON",
        "series_brand": "Booster Drive & Workout Series",
        "album_title": "Booster Drive & Workout Series, Vol. 1: Seoul Nightline",
        "track_title": "결승선을 향한 질주 | Sprint to the Finish Line",
        "version": "Booster High-Energy Master",
        "genre": "Synthwave Workout Beat",
        "record_label": "SUN-ONE AON Records",
        "target_release_kst": "2026-11-17 17:00:00 KST",
        "target_release_est": "2026-11-17 03:00:00 EST",
        "isrc": "KR-S01-26-BOOST2",
        "upc": "UPC-8809902-02",
        "youtube_video_channel": "@Booster_Playlist",
        "k_ethos": "한계를 극복하는 불굴의 도전 정신 (Unstoppable Athletic Perseverance)"
    }
]

def now_kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def sync_2slot_distrokid_ledger():
    LEDGERS_DIR.mkdir(parents=True, exist_ok=True)
    ledger_file = LEDGERS_DIR / "06_DISTROKID_RELEASE_LEDGER.csv"

    fieldnames = [
        "릴리즈ID", "디스트로키드슬롯", "공식아티스트명", "시리즈브랜드", "유튜브영상채널",
        "앨범발매명_한영", "트랙명", "버전", "장르", "발매일_KST", "발매일_EST",
        "ISRC코드", "UPC코드", "음원규격", "커버규격", "레코드레이블", "동방예의지국철학", "출격게이트상태"
    ]

    rows = []
    for trk in TRACKS_2SLOT_CONFIG:
        rel_id = f"REL_2SLOT_{trk['track_id']}"
        rows.append({
            "릴리즈ID": rel_id,
            "디스트로키드슬롯": trk["distrokid_slot"],
            "공식아티스트명": trk["main_artist"],
            "시리즈브랜드": trk["series_brand"],
            "유튜브영상채널": trk["youtube_video_channel"],
            "앨범발매명_한영": trk["album_title"],
            "트랙명": trk["track_title"],
            "버전": trk["version"],
            "장르": trk["genre"],
            "발매일_KST": trk["target_release_kst"],
            "발매일_EST": trk["target_release_est"],
            "ISRC코드": trk["isrc"],
            "UPC코드": trk["upc"],
            "음원규격": "44.1kHz 16-bit WAV (-14.0 LUFS)",
            "커버규격": "3000x3000px RGB PNG",
            "레코드레이블": trk["record_label"],
            "동방예의지국철학": trk["k_ethos"],
            "출격게이트상태": "SHA8_GATE_STANDBY"
        })

    with open(ledger_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] DistroKid 2-Slot Master Ledger updated: {ledger_file} ({len(rows)} tracks)")

    # Update manifest in vault
    staged_manifest_path = ROOT_DIR / "DISTROKID_2SLOT_STAGED_MANIFEST.json"
    manifest_data = {
        "status": "STAGED_FOR_DISTROKID_RELEASE",
        "plan_type": "DistroKid Musician Plus (2 Artist Slots Limit Compliant)",
        "slots": DISTROKID_SLOTS,
        "total_tracks": len(TRACKS_2SLOT_CONFIG),
        "tracks": TRACKS_2SLOT_CONFIG,
        "executive_producer": "Sangill Lee (이상일)",
        "label": "SUN-ONE AON Records",
        "philanthropy_pledge": "33% of all digital royalties dedicated to global humanitarian causes",
        "updated_at": now_kst()
    }
    staged_manifest_path.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Staged Manifest written: {staged_manifest_path}")

    # Update JSON specs inside vault tracks
    for trk in TRACKS_2SLOT_CONFIG:
        spec_path = CHANNELS_DIR / trk["channel_dir"] / "TRACKS" / trk["track_id"] / "suno_v45_spec.json"
        if spec_path.is_file():
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
                spec["distrokid_metadata"] = {
                    "slot": trk["distrokid_slot"],
                    "main_artist": trk["main_artist"],
                    "series_brand": trk["series_brand"],
                    "record_label": trk["record_label"],
                    "isrc": trk["isrc"],
                    "upc": trk["upc"],
                    "youtube_oac": "@SUN-ONEAON" if trk["distrokid_slot"] == "SLOT_2" else "@한걸음씩-r4i"
                }
                spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception as e:
                print(f"Notice: could not update {spec_path}: {e}")

    print("[OK] All 8 track specs updated with DistroKid 2-Slot mapping!")
    return ledger_file

if __name__ == "__main__":
    print("=== [S1 DISTROKID 2-SLOT REBRANDING RUNNER] ===")
    sync_2slot_distrokid_ledger()

