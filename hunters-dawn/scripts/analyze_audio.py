import os
import json
import librosa
import numpy as np

def analyze():
    audio_path = "00_audio/master.wav"
    print(f"Loading {audio_path}...")
    y, sr = librosa.load(audio_path, sr=None)

    duration = float(librosa.get_duration(y=y, sr=sr))
    print(f"Total Duration: {duration:.3f} seconds")

    # 1. BPM & Beat Tracking
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    
    bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
    print(f"Detected BPM: {bpm:.2f}")

    beat_duration = 60.0 / bpm
    bar_duration = beat_duration * 4
    two_bar_duration = bar_duration * 2

    # 2. Whistle Detection (2kHz ~ 4kHz band energy & harmonic simplicity)
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    
    idx_2k = np.argmin(np.abs(freqs - 2000))
    idx_4k = np.argmin(np.abs(freqs - 4000))
    
    whistle_band_energy = np.mean(S[idx_2k:idx_4k, :], axis=0)
    total_energy = np.mean(S, axis=0) + 1e-6
    whistle_ratio = whistle_band_energy / total_energy

    hop_length = 512
    frame_rate = sr / hop_length
    window_size = int(frame_rate * 0.5)
    kernel = np.ones(window_size) / window_size
    smoothed_ratio = np.convolve(whistle_ratio, kernel, mode='same')

    thresh = np.mean(smoothed_ratio) + 0.7 * np.std(smoothed_ratio)
    active_frames = np.where(smoothed_ratio > thresh)[0]
    times = librosa.frames_to_time(np.arange(len(smoothed_ratio)), sr=sr, hop_length=hop_length)

    whistle_ranges = []
    if len(active_frames) > 0:
        start_f = active_frames[0]
        prev_f = active_frames[0]
        for f in active_frames[1:]:
            if f - prev_f > int(frame_rate * 1.0):
                t_start = round(float(times[start_f]), 2)
                t_end = round(float(times[prev_f]), 2)
                if t_end - t_start >= 1.2:
                    whistle_ranges.append({"start": t_start, "end": t_end, "duration": round(t_end - t_start, 2)})
                start_f = f
            prev_f = f
        t_start = round(float(times[start_f]), 2)
        t_end = round(float(times[prev_f]), 2)
        if t_end - t_start >= 1.2:
            whistle_ranges.append({"start": t_start, "end": t_end, "duration": round(t_end - t_start, 2)})

    # Filter ranges
    intro_whistle = [r for r in whistle_ranges if r["start"] <= 18.0]
    mid_whistle = [r for r in whistle_ranges if 100.0 <= r["start"] <= 150.0]
    outro_whistle = [r for r in whistle_ranges if r["start"] >= 165.0]

    # Sections synced to beat grid (Total ~185.48s)
    # Intro: 0.0s ~ 16.72s (8 bars)
    # Verse1: 16.72s ~ 45.99s (14 bars)
    # PreChorus: 45.99s ~ 62.71s (8 bars)
    # Chorus1: 62.71s ~ 96.16s (16 bars)
    # Verse2: 96.16s ~ 125.43s (14 bars)
    # Bridge: 125.43s ~ 150.51s (12 bars)
    # Chorus2: 150.51s ~ 171.42s (10 bars)
    # Outro: 171.42s ~ 185.48s (7 bars / Fade out)
    sections = {
        "Intro": {"in": 0.0, "out": 16.724},
        "Verse1": {"in": 16.724, "out": 45.991},
        "PreChorus": {"in": 45.991, "out": 62.712},
        "Chorus1": {"in": 62.712, "out": 96.160},
        "Verse2": {"in": 96.160, "out": 125.432},
        "Bridge": {"in": 125.432, "out": 150.511},
        "Chorus2": {"in": 150.511, "out": 171.417},
        "Outro": {"in": 171.417, "out": round(duration, 3)}
    }

    beatgrid_data = {
        "bpm_measured": round(bpm, 2),
        "bpm_target": 115.0,
        "bpm_diff": round(abs(bpm - 115.0), 2),
        "duration_seconds": round(duration, 3),
        "grid_params": {
            "one_beat_sec": round(beat_duration, 4),
            "one_bar_sec": round(bar_duration, 4),
            "two_bar_sec": round(two_bar_duration, 4)
        },
        "whistle_ranges_all": whistle_ranges,
        "whistle_analysis": {
            "has_intro_whistle": len(intro_whistle) > 0,
            "has_mid_whistle": len(mid_whistle) > 0,
            "has_outro_whistle": len(outro_whistle) > 0,
            "intro_whistle_ranges": intro_whistle,
            "mid_whistle_ranges": mid_whistle,
            "outro_whistle_ranges": outro_whistle
        },
        "sections": sections,
        "beat_timestamps": [round(b, 4) for b in beat_times]
    }

    os.makedirs("00_audio", exist_ok=True)
    with open("00_audio/beatgrid.json", "w", encoding="utf-8") as f:
        json.dump(beatgrid_data, f, indent=2, ensure_ascii=False)

    print("[SUCCESS] Audio Analysis Completed. beatgrid.json generated.")

if __name__ == '__main__':
    analyze()
