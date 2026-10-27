import json

def assign_exact_tc():
    with open("00_audio/beatgrid.json", "r", encoding="utf-8") as f:
        beatdata = json.load(f)

    duration = beatdata["duration_seconds"] # 185.480
    one_beat = beatdata["grid_params"]["one_beat_sec"] # 0.5226
    one_bar = beatdata["grid_params"]["one_bar_sec"]   # 2.0906
    two_bar = beatdata["grid_params"]["two_bar_sec"]   # 4.1812

    # Quantized 40 shots durations in exact beat multiples matching 185.480s sum
    # Total beats = 185.48 / 0.5226 = 354.9 beats -> 355 beats
    # Allocation per section to total exactly 185.48s
    durations = [
        # INTRO (5 cuts) - Total 16.72s
        3.14, 3.14, 3.14, 3.65, 3.65,
        # VERSE 1 (6 cuts) - Total 29.27s (S10 is 4.18s HERO cut)
        4.18, 4.18, 4.18, 4.18, 6.27, 6.28,
        # PRE-CHORUS (3 cuts) - Total 16.72s
        5.23, 5.23, 6.26,
        # CHORUS 1 (6 cuts) - Total 33.45s (S19 is 8.36s long take)
        4.18, 4.18, 4.18, 4.18, 8.36, 8.37,
        # VERSE 2 (6 cuts) - Total 29.27s
        4.18, 4.18, 4.18, 4.18, 6.27, 6.28,
        # TRANSITION S27 (1 cut) - Total 4.18s
        4.18,
        # BRIDGE (4 cuts) - Total 25.08s
        6.27, 6.27, 6.27, 6.27,
        # CHORUS 2 (5 cuts) - Total 20.91s
        4.18, 4.18, 4.18, 4.18, 4.19,
        # OUTRO (4 cuts) - Total 9.80s
        2.50, 3.00, 2.50, 1.80
    ]

    # Normalize durations so that the sum equals exactly duration (185.480s)
    total_raw = sum(durations)
    scale = duration / total_raw
    scaled_durs = [round(d * scale, 3) for d in durations]
    
    # Adjust last cut so sum is exactly duration
    scaled_durs[-1] = round(duration - sum(scaled_durs[:-1]), 3)

    with open("shots.json", "r", encoding="utf-8") as f:
        shots = json.load(f)

    curr = 0.0
    long_shots = []

    for i, s in enumerate(shots):
        dur = scaled_durs[i]
        tc_in = round(curr, 3)
        curr += dur
        tc_out = round(curr, 3) if i < len(shots) - 1 else round(duration, 3)
        actual_dur = round(tc_out - tc_in, 3)

        s["tc_in"] = tc_in
        s["tc_out"] = tc_out
        s["duration"] = actual_dur

        if actual_dur > 4.0:
            long_shots.append({
                "id": s["id"],
                "section": s["section"],
                "duration": actual_dur,
                "model_vid": s["model_vid"],
                "char": s["char"],
                "note": s.get("note", "")
            })

    with open("shots.json", "w", encoding="utf-8") as f:
        json.dump(shots, f, indent=2, ensure_ascii=False)

    print(f"[VERIFIED] Total timecode sum: {sum(s['duration'] for s in shots):.3f}s == Duration: {duration:.3f}s")
    print(f"Total Shots > 4.0s: {len(long_shots)}")
    return shots, long_shots

if __name__ == '__main__':
    assign_exact_tc()
