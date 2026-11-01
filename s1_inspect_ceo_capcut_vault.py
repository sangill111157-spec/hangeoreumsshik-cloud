# -*- coding: utf-8 -*-
"""
S1 CEO CapCut Vault Inspector & FFprobe Analyzer
- Targets: C:\\Users\\sangi\\OneDrive\\Videos\\켑컷 재작 영상\\가을과 겨울사이 앨범
- Measures: Video/Audio codecs, resolution, bitrate, duration, LUFS, timestamps
"""
import os
import sys
import json
import subprocess

def run_ffprobe(filepath):
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", filepath
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0:
        return json.loads(res.stdout)
    return {}

def measure_lufs(filepath):
    # run ffmpeg ebur128 filter
    cmd = [
        "ffmpeg", "-i", filepath, "-af", "ebur128=framelog=verbose",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    # Parse integrated loudness
    lufs = -14.0 # default fallback
    for line in res.stderr.splitlines():
        if "I:" in line and "LUFS" in line:
            parts = line.split("I:")
            if len(parts) > 1:
                val = parts[1].split("LUFS")[0].strip()
                try:
                    lufs = float(val)
                except:
                    pass
    return lufs

def main():
    capcut_base = r"C:\Users\sangi\OneDrive\Videos\켑컷 재작 영상\가을과 겨울사이 앨범"
    mp4_path = os.path.join(capcut_base, "1009.mp4")
    thumb_path = os.path.join(capcut_base, "thumbnail.jpg")

    print(f"Checking CapCut Master: {mp4_path}")
    print(f"Exists: {os.path.exists(mp4_path)}")
    if not os.path.exists(mp4_path):
        print("ERROR: 1009.mp4 not found!")
        return

    size_bytes = os.path.getsize(mp4_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"File Size: {size_bytes:,} bytes ({size_mb:.2f} MB)")

    info = run_ffprobe(mp4_path)
    fmt = info.get("format", {})
    streams = info.get("streams", [])

    duration_sec = float(fmt.get("duration", 0))
    bitrate = int(fmt.get("bit_rate", 0))

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

    width = video_stream.get("width")
    height = video_stream.get("height")
    v_codec = video_stream.get("codec_name")
    fps_eval = video_stream.get("r_frame_rate", "30/1")
    try:
        num, den = fps_eval.split("/")
        fps = float(num) / float(den)
    except:
        fps = 30.0

    a_codec = audio_stream.get("codec_name")
    sample_rate = audio_stream.get("sample_rate")
    channels = audio_stream.get("channels")
    a_bitrate = audio_stream.get("bit_rate")

    mins = int(duration_sec // 60)
    secs = int(duration_sec % 60)
    time_str = f"{mins:02d}:{secs:02d}"

    print(f"Duration: {duration_sec:.2f}s ({time_str})")
    print(f"Video: {width}x{height} @ {fps:.2f}fps ({v_codec}), Bitrate: {bitrate//1000} kbps")
    print(f"Audio: {a_codec} {sample_rate}Hz, {channels}ch, Bitrate: {int(a_bitrate)//1000 if a_bitrate else 'N/A'} kbps")

    print("Measuring LUFS loudness (first 120s sample for speed)...")
    cmd_lufs = [
        "ffmpeg", "-t", "120", "-i", mp4_path, "-af", "ebur128", "-f", "null", "-"
    ]
    res_lufs = subprocess.run(cmd_lufs, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    lufs = -14.0
    for line in res_lufs.stderr.splitlines():
        if "I:" in line and "LUFS" in line:
            parts = line.split("I:")
            if len(parts) > 1:
                val = parts[1].split("LUFS")[0].strip()
                try:
                    lufs = float(val)
                except:
                    pass
    print(f"Sample Integrated Loudness: {lufs} LUFS")

    # Analyze 12 individual tracks in studio_vault to calculate timeline offsets
    album_dir = r"C:\Users\sangi\Downloads\shin-agent\studio_vault\CHANNELS\01_STEP_HANGEOREUM\DISTROKID_ALBUMS\01_AUTUMN_AND_WINTER_BETWEEN_12TRACKS"
    track_meta_path = os.path.join(album_dir, "ALBUM_METADATA.json")
    
    track_timeline = []
    if os.path.exists(track_meta_path):
        with open(track_meta_path, "r", encoding="utf-8") as f:
            tmeta = json.load(f)
        
        current_time = 0.0
        for t in tmeta.get("tracks", []):
            t_num = t.get("track", 1)
            t_title = t.get("title", "")
            wav_file = t.get("wav_file", "")
            t_dur = 0.0
            if wav_file and os.path.exists(wav_file):
                winfo = run_ffprobe(wav_file)
                t_dur = float(winfo.get("format", {}).get("duration", 0))
            else:
                # Parse duration string "MM:SS"
                d_str = t.get("duration", "03:30")
                if ":" in d_str:
                    dm, ds = d_str.split(":")
                    t_dur = float(dm) * 60 + float(ds)
            
            m = int(current_time // 60)
            s = int(current_time % 60)
            ts_str = f"{m:02d}:{s:02d}"
            track_timeline.append({
                "track": t_num,
                "title": t_title,
                "title_en": t.get("title_en", ""),
                "start_time_sec": round(current_time, 2),
                "timestamp": ts_str,
                "duration_sec": round(t_dur, 2)
            })
            current_time += t_dur

    result = {
        "source": "OneDrive/켑컷 재작 영상/가을과 겨울사이 앨범",
        "mp4_file": mp4_path,
        "thumbnail_file": thumb_path,
        "file_size_bytes": size_bytes,
        "file_size_mb": round(size_mb, 2),
        "duration_seconds": duration_sec,
        "duration_formatted": time_str,
        "resolution": f"{width}x{height}",
        "width": width,
        "height": height,
        "fps": round(fps, 2),
        "video_codec": v_codec,
        "audio_codec": a_codec,
        "sample_rate": sample_rate,
        "channels": channels,
        "integrated_lufs": lufs,
        "track_timeline": track_timeline
    }

    out_path = r"C:\Users\sangi\Downloads\shin-agent\s1_capcut_vault_specs.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nSaved specs to {out_path}")

if __name__ == "__main__":
    main()
