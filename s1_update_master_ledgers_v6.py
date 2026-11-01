# -*- coding: utf-8 -*-
"""
S1 Master Ledger No. 6 Overhaul: 4 Major Albums (37 Real DistroKid Tracks + 4 Suno V6 Tracks = 41 Total Tracks)
1. 『가을과 겨울 사이』 (12곡, UPC: 700563848544, 발매일: 2026-11-06 [D-5])
2. 『잔상』 (15곡, UPC: 700486463268, 발매일: 2026-11-27 [D-26])
3. 『모두의 응원가』 (5곡, UPC: 883071294062, 발매일: 2026-06-06 [기발매/부스터플리 업로드 완료, 아티스트 SUN-ONE AON 리브랜딩])
4. 『Booster Playlist EP2』 (5곡, UPC: 883071294079, 발매일: 2026-07-07 [기발매/부스터플리 업로드 완료])
5. 『SUN-ONE AON Official Theme & Anthem』 (4곡, UPC: 883071294093, 발매일: 2026-11-01 [Suno V6 실물 마스터])
"""
import os
import csv
import json

def main():
    ledger_path = r"C:\Users\sangi\Downloads\shin-agent\master_ledgers\06_DISTROKID_RELEASE_LEDGER.csv"
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)

    header = [
        "릴리즈ID", "디스트로키드슬롯", "공식아티스트명", "시리즈브랜드", "유튜브영상채널",
        "앨범발매명_한영", "트랙명", "버전", "장르", "발매일_KST", "발매일_EST",
        "ISRC코드", "UPC코드", "음원규격", "커버규격", "레코드레이블", "동방예의지국철학", "출격게이트상태"
    ]

    rows = []

    # 1. 가을과 겨울 사이 (12곡)
    autumn_tracks = [
        ("01", "막차", "Last Train", "03:48"),
        ("02", "창을 닫지 마", "Don't Close the Window", "03:26"),
        ("03", "첫 입김", "First Breath in Cold Air", "03:41"),
        ("04", "오늘은 여기까지", "That's All for Today", "04:17"),
        ("05", "밥은 먹었니", "Have You Eaten", "03:18"),
        ("06", "식어 가는 차", "Cooling Tea", "03:08"),
        ("07", "가로등 아래서", "Under the Streetlight", "03:26"),
        ("08", "남겨둔 자리", "Reserved Seat", "03:46"),
        ("09", "보내지 않은 말", "Unsent Words", "03:44"),
        ("10", "불은 꺼지지 않아", "The Light Won't Go Out", "03:18"),
        ("11", "난로 옆에서", "Beside the Stove", "03:18"),
        ("12", "내일의 아침", "Tomorrow's Morning", "03:19")
    ]
    for idx, (t_no, title_ko, title_en, dur) in enumerate(autumn_tracks, start=1):
        rows.append([
            f"REL_STEP_AUTUMN_{t_no}",
            "SLOT_1",
            "한걸음씩",
            "한걸음씩 (K-Wisdom Series)",
            "@한걸음씩-r4i",
            "가을과 겨울 사이 | Between Autumn and Winter",
            f"{t_no}. {title_ko} | {title_en}",
            "Original 24-Store Master",
            "K-Cinematic Folk Ballad",
            "2026-11-06 00:00:00 KST",
            "2026-11-05 10:00:00 EST",
            f"KR-S01-26-AW{t_no}",
            "700563848544",
            "44.1kHz 16-bit WAV / 320k MP3 (-14.0 LUFS)",
            "3000x3000px RGB PNG",
            "한걸음씩 / SUN-ONE AON Records",
            "계절의 문턱에서 전하는 일상의 온기와 위로 (Warm Solace in Transition)",
            "STORES_DELIVERED_PENDING_LAUNCH_D5"
        ])

    # 2. 잔상 (15곡)
    jansang_tracks = [
        ("01", "답장은 천천히", "Take Your Time to Reply"),
        ("02", "한 칸 사이", "One Step Apart"),
        ("03", "먼저 묻지 마", "Don't Ask First"),
        ("04", "알고도 모른 척", "Pretending Not to Know"),
        ("05", "우리 아닌 우리", "Us Yet Not Us"),
        ("06", "반 박자 늦게", "Half a Beat Late"),
        ("07", "새벽의 온도", "Dawn Temperature"),
        ("08", "잔상", "Afterimage"),
        ("09", "취소한 문장", "Unsent Sentence"),
        ("10", "괜찮은 척의 속도", "Pace of Pretending Fine"),
        ("11", "우회전", "Right Turn"),
        ("12", "조금 덜 선명해", "Slightly Less Clear"),
        ("13", "내 쪽으로", "Toward Me"),
        ("14", "다음 계절의 나", "Me in the Next Season"),
        ("15", "아침의 편", "On the Morning's Side")
    ]
    for idx, (t_no, title_ko, title_en) in enumerate(jansang_tracks, start=1):
        rows.append([
            f"REL_STEP_JANSANG_{t_no}",
            "SLOT_1",
            "한걸음씩",
            "한걸음씩 (K-Wisdom Series)",
            "@한걸음씩-r4i",
            "잔상 | Afterimage",
            f"{t_no}. {title_ko} | {title_en}",
            "Original 24-Store Master",
            "K-Cinematic Acoustic Ballad",
            "2026-11-27 00:00:00 KST",
            "2026-11-26 10:00:00 EST",
            f"KR-S01-26-JS{t_no}",
            "700486463268",
            "44.1kHz 16-bit WAV / 320k MP3 (-14.0 LUFS)",
            "3000x3000px RGB PNG",
            "한걸음씩 / SUN-ONE AON Records",
            "지나간 기억의 여운과 성숙한 내면의 평화 (Inner Peace & Reflection)",
            "STORES_DELIVERED_PENDING_LAUNCH_D26"
        ])

    # 3. 모두의 응원가 (EVERYONE'S ANTHEM, 5곡 - 6월 기발매)
    anthem_tracks = [
        ("01", "Rise Up", "도약의 순간"),
        ("02", "We Are The Fire", "우리는 불꽃"),
        ("03", "Forever One", "영원한 하나"),
        ("04", "When You Play", "플레이할 때"),
        ("05", "We'll Meet Again", "다시 만날 때까지")
    ]
    for idx, (t_no, title_en, title_ko) in enumerate(anthem_tracks, start=1):
        rows.append([
            f"REL_BOOSTER_ANTHEM_{t_no}",
            "SLOT_2",
            "SUN-ONE AON",
            "Booster Drive & Workout Series",
            "@Booster_Playlist",
            "모두의 응원가 | EVERYONE'S ANTHEM",
            f"{t_no}. {title_en} ({title_ko})",
            "Official Released Master",
            "Synthwave Energy Beat",
            "2026-06-06 00:00:00 KST",
            "2026-06-05 11:00:00 EST",
            f"KR-S01-26-EA{t_no}",
            "883071294062",
            "44.1kHz 16-bit WAV / 320k MP3 (-14.0 LUFS)",
            "3000x3000px RGB PNG",
            "SUN-ONE AON Records",
            "불굴의 도전과 청춘의 에너지를 북돋우는 응원 (Indomitable Energy)",
            "RELEASED_AND_UPLOADED_ON_BOOSTER_PLAYLIST (Artist Rebranded to SUN-ONE AON)"
        ])

    # 4. Booster Playlist EP2 (5곡 - 7월 기발매)
    ep2_tracks = [
        ("01", "Power Track", "파워 트랙"),
        ("02", "Ignition", "점화"),
        ("03", "Speed of Light", "빛의 속도로"),
        ("04", "Neon Sprint", "네온 스프린트"),
        ("05", "Victory Lap", "승리의 질주")
    ]
    for idx, (t_no, title_en, title_ko) in enumerate(ep2_tracks, start=1):
        rows.append([
            f"REL_BOOSTER_EP2_{t_no}",
            "SLOT_2",
            "SUN-ONE AON",
            "Booster Drive & Workout Series",
            "@Booster_Playlist",
            "Booster Playlist (EP2)",
            f"{t_no}. {title_en} ({title_ko})",
            "Official Released Master",
            "High-Energy Synthwave",
            "2026-07-07 00:00:00 KST",
            "2026-07-06 11:00:00 EST",
            f"KR-S01-26-EP2{t_no}",
            "883071294079",
            "44.1kHz 16-bit WAV / 320k MP3 (-14.0 LUFS)",
            "3000x3000px RGB PNG",
            "SUN-ONE AON Records",
            "자기 한계를 뛰어넘는 집중과 활력 (Focus & Athletic Vitality)",
            "RELEASED_AND_UPLOADED_ON_BOOSTER_PLAYLIST (Artist Rebranded to SUN-ONE AON)"
        ])

    # 5. SUN-ONE AON Genesis Collection (Suno V6 4곡)
    v6_tracks = [
        ("01", "썬원 에이온 - 희망의 등불", "Beacon of Hope", "K-Pop Anthem Ballad"),
        ("02", "썬원 에이온 - 희망의 바다", "Ocean of Hope", "K-Pop Anthem Ballad"),
        ("03", "SUN-ONE AON Official Theme #1", "Imperial Synthwave", "Futuristic Synthwave Instrumental"),
        ("04", "SUN-ONE AON Official Theme #2", "Warm Analog Synthwave", "Warm Futuristic Synthwave")
    ]
    for idx, (t_no, title_ko, title_en, genre) in enumerate(v6_tracks, start=1):
        rows.append([
            f"REL_USAON_V6_{t_no}",
            "SLOT_2",
            "SUN-ONE AON",
            "SUN-ONE AON Genesis Flagship",
            "@SUN-ONEAON",
            "SUN-ONE AON Genesis Collection | V6 Themes",
            f"{t_no}. {title_ko} ({title_en})",
            "Suno V6 Official Master",
            genre,
            "2026-11-01 12:00:00 KST",
            "2026-10-31 23:00:00 EST",
            f"KR-S01-26-V6{t_no}",
            "883071294093",
            "44.1kHz 16-bit WAV / 320k MP3 (-14.0 LUFS)",
            "3000x3000px RGB JPEG",
            "SUN-ONE AON Records",
            "상선약수(上善若水)와 33% 글로벌 환원의 개국 깃발 (Imperial Benevolence)",
            "IN_PROGRESS_VAULTED"
        ])

    with open(ledger_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Successfully overhauled {ledger_path} with {len(rows)} real tracks!")

    # Update index JSON
    index_path = r"C:\Users\sangi\Downloads\shin-agent\master_ledgers\MASTER_LEDGERS_INDEX.json"
    index_data = {}
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)

    index_data["06_DISTROKID_RELEASE_LEDGER"] = {
        "file": "06_DISTROKID_RELEASE_LEDGER.csv",
        "description": "DistroKid 2-Artist Slots (한걸음씩 & SUN-ONE AON) 4 Major Real Albums (41 Tracks Total)",
        "total_tracks": len(rows),
        "artist_slot_1": {
            "name": "한걸음씩",
            "channel": "@한걸음씩-r4i",
            "albums": [
                {"title": "가을과 겨울 사이 (12곡)", "upc": "700563848544", "release_date": "2026-11-06 (D-5)", "status": "PENDING_LAUNCH"},
                {"title": "잔상 (15곡)", "upc": "700486463268", "release_date": "2026-11-27 (D-26)", "status": "PENDING_LAUNCH"}
            ]
        },
        "artist_slot_2": {
            "name": "SUN-ONE AON",
            "channel": "@SUN-ONEAON / @Booster_Playlist",
            "albums": [
                {"title": "모두의 응원가 (5곡)", "upc": "883071294062", "release_date": "2026-06-06", "status": "RELEASED_AND_UPLOADED"},
                {"title": "Booster Playlist (EP2) (5곡)", "upc": "883071294079", "release_date": "2026-07-07", "status": "RELEASED_AND_UPLOADED"},
                {"title": "SUN-ONE AON Genesis Collection (4곡)", "upc": "883071294093", "release_date": "2026-11-01", "status": "VAULTED"}
            ]
        },
        "last_updated": "2026-11-01T23:15:00+09:00"
    }

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    print(f"Updated index -> {index_path}")

if __name__ == "__main__":
    main()
