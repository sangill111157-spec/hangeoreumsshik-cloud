import os
import json
import librosa
import soundfile as sf
import numpy as np

def run_fast_track_a():
    audio_path = "00_audio/master.wav"
    y, sr = librosa.load(audio_path, sr=None)
    duration = float(librosa.get_duration(y=y, sr=sr))
    
    os.makedirs("00_audio/verify", exist_ok=True)
    
    # 1. Verification WAVs
    v_files = {
        "00_audio/verify/v1_intro_0-20.wav": (0.0, 20.0),
        "00_audio/verify/v2_verse1_28-46.wav": (28.0, 46.0),
        "00_audio/verify/v3_prechorus_45-64.wav": (45.0, 64.0),
        "00_audio/verify/v4_chorus1_74-90.wav": (74.0, 90.0),
        "00_audio/verify/v5_bridge_125-140.wav": (125.0, 140.0),
        "00_audio/verify/v6_outro_170-186.wav": (170.0, 185.48)
    }
    
    for fpath, (t_start, t_end) in v_files.items():
        s_idx = int(t_start * sr)
        e_idx = min(len(y), int(t_end * sr))
        sf.write(fpath, y[s_idx:e_idx], sr)
        print(f"Saved verification file: {fpath}")

    # 2. Extract Templates
    whistle_y = y[0 : int(7.0 * sr)]
    sf.write("00_audio/verify/tpl_whistle.wav", whistle_y, sr)
    
    clap_y = y[int(32.0 * sr) : int(33.5 * sr)]
    sf.write("00_audio/verify/tpl_clap.wav", clap_y, sr)
    
    riff_y = y[int(51.0 * sr) : int(52.5 * sr)]
    sf.write("00_audio/verify/tpl_riff.wav", riff_y, sr)

    # Audio Characteristics Measurement
    def measure_char(signal, sr):
        cent = float(np.mean(librosa.feature.spectral_centroid(y=signal, sr=sr)))
        flatness = float(np.mean(librosa.feature.spectral_flatness(y=signal)))
        
        y_harm, y_perc = librosa.effects.hpss(signal)
        e_harm = float(np.sum(y_harm**2))
        e_perc = float(np.sum(y_perc**2)) + 1e-8
        hnr_db = 10 * np.log10(e_harm / e_perc)
        
        return {
            "spectral_centroid_hz": round(cent, 1),
            "spectral_flatness": round(flatness, 4),
            "hnr_db": round(hnr_db, 2),
            "harmonic_ratio": round(e_harm / (e_harm + e_perc), 4)
        }

    tpl_stats = {
        "tpl_whistle": measure_char(whistle_y, sr),
        "tpl_clap": measure_char(clap_y, sr),
        "tpl_riff": measure_char(riff_y, sr)
    }

    # 3. Whistle Phrases
    whistle_phrases = [
        {"phrase": 1, "text": "휘이", "start": 0.523, "end": 1.045},
        {"phrase": 2, "text": "휘휘", "start": 1.568, "end": 2.091},
        {"phrase": 3, "text": "휘휘", "start": 2.613, "end": 3.136},
        {"phrase": 4, "text": "휘휘휘", "start": 4.181, "end": 4.704},
        {"phrase": 5, "text": "휘휘", "start": 5.227, "end": 5.749},
        {"phrase": 6, "text": "휘", "start": 6.272, "end": 6.794}
    ]
    with open("00_audio/whistle_phrases.json", "w", encoding="utf-8") as f:
        json.dump(whistle_phrases, f, indent=2, ensure_ascii=False)

    # 4. Accents
    accents_data = {
        "clap_5hits_32_33": [32.395, 32.656, 32.918, 33.179, 33.440],
        "riff1_4hits_51_52": [51.220, 51.742, 52.265, 52.788],
        "riff2_4hits_131_132": [131.704, 132.227, 132.749, 133.272]
    }
    with open("00_audio/accents.json", "w", encoding="utf-8") as f:
        json.dump(accents_data, f, indent=2, ensure_ascii=False)

    print("=== Template Characteristics ===")
    print(json.dumps(tpl_stats, indent=2))
    return tpl_stats, accents_data

if __name__ == '__main__':
    run_fast_track_a()
