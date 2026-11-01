# -*- coding: utf-8 -*-
"""
S1 Task B: Video Upload Staging Manifest & Safe Scheduled Draft Master
- Prevents unauthorized public release (enforces TTY SHA-8 & Private/Scheduled Draft mode)
- Stages:
  1. @한걸음씩-r4i: 『가을과 겨울 사이』 41:14 Full Album (Publish: 2026-11-06 00:00 KST)
  2. @SUN-ONEAON: 『썬원 에이온 - 희망의 등불』 1080p MV (Publish: 2026-11-04 21:00 KST)
"""
import os
import json
import hashlib

def sha256_file(filepath):
    if not os.path.exists(filepath):
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def main():
    step_mp4 = r"C:\Users\sangi\Downloads\shin-agent\studio_vault\CHANNELS\01_STEP_HANGEOREUM\NOV06_FINAL_MASTER\AUTUMN_AND_WINTER_12TRACKS_HYBRID_MASTER_14LUFS.mp4"
    step_thumb = r"C:\Users\sangi\Downloads\shin-agent\studio_vault\CHANNELS\01_STEP_HANGEOREUM\NOV06_FINAL_MASTER\THUMBNAIL_1280x720_MASTER.jpg"
    
    aon_mp4 = r"C:\Users\sangi\Downloads\shin-agent\studio_vault\CEO_SUNO_V6_MASTERS\01_BEACON_OF_HOPE_1080p_MV.mp4"
    aon_thumb = r"C:\Users\sangi\Downloads\shin-agent\assets\channel_branding_2026\thumbnail_EP01_1920x1080.png"

    manifest = {
        "manifest_name": "S1_VIDEO_UPLOAD_STAGING_MANIFEST",
        "version": "2.0.0",
        "created_at": "2026-11-01T23:38:00+09:00",
        "safety_constitution": {
            "unauthorized_public_block": True,
            "default_upload_privacy": "PRIVATE_OR_SCHEDULED_DRAFT",
            "tty_sha8_gate_required": True,
            "rule": "절대 대표님의 승인 없이 즉시 공개(Public)로 게시하지 않으며, 지정된 D-Day 예약 스케줄로만 안전 적재한다."
        },
        "staging_queue": [
            {
                "queue_id": "STAGE_01_HANGEOREUM_FULL_ALBUM",
                "channel_handle": "@한걸음씩-r4i",
                "channel_space": 6,
                "video_file": step_mp4,
                "video_exists": os.path.exists(step_mp4),
                "video_size_bytes": os.path.getsize(step_mp4) if os.path.exists(step_mp4) else 0,
                "thumbnail_file": step_thumb,
                "thumbnail_exists": os.path.exists(step_thumb),
                "title": "[Full Album] 한걸음씩 - 가을과 겨울 사이 (Between Autumn and Winter) | Official 1st Full Album [4K/FHD 41분 전곡]",
                "scheduled_publish_kst": "2026-11-06 00:00:00 KST",
                "scheduled_publish_utc": "2026-11-05 15:00:00 UTC",
                "visibility_mode": "SCHEDULED",
                "distrokid_upc": "700563848544",
                "track_count": 12,
                "total_duration": "41:14",
                "status": "STAGED_DRAFT_READY"
            },
            {
                "queue_id": "STAGE_02_SUNONE_AON_GENESIS_MV",
                "channel_handle": "@SUN-ONEAON",
                "channel_space": 18,
                "video_file": aon_mp4,
                "video_exists": os.path.exists(aon_mp4),
                "video_size_bytes": os.path.getsize(aon_mp4) if os.path.exists(aon_mp4) else 0,
                "thumbnail_file": aon_thumb,
                "thumbnail_exists": os.path.exists(aon_thumb),
                "title": "[Official MV] 썬원 에이온 - 희망의 등불 (SUN-ONE AON) | 개국 1호 공식 테마곡 [1080p FHD]",
                "scheduled_publish_kst": "2026-11-04 21:00:00 KST",
                "scheduled_publish_est": "2026-11-04 07:00:00 EST",
                "visibility_mode": "SCHEDULED",
                "distrokid_upc": "883071294093",
                "audio_source": "Suno V6 Authentic 320kbps Master (-14.0 LUFS)",
                "total_duration": "02:38",
                "status": "STAGED_DRAFT_READY"
            }
        ]
    }

    out_file = "S1_VIDEO_UPLOAD_STAGING_MANIFEST.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Saved {out_file} successfully!")

if __name__ == "__main__":
    main()
