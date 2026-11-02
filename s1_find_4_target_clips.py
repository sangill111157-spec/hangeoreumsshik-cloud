# -*- coding: utf-8 -*-
import sys
import json
import pathlib

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

output_path = pathlib.Path(r"C:\Users\sangi\.gemini\antigravity\brain\ba7b50e7-5ae2-436d-b5b0-4494fabe4343\.system_generated\steps\2515\output.txt")
data = json.loads(output_path.read_text(encoding="utf-8"))
clips = data.get("clips", [])

print(f"Total clips loaded: {len(clips)}")

keywords = ["희망", "등불", "바다", "Theme", "SUN-ONE", "썬원"]
matches = []
for c in clips:
    title = c.get("title") or ""
    prompt = c.get("prompt") or ""
    tags = c.get("tags") or ""
    full_text = f"{title} {prompt} {tags}"
    if any(k in full_text for k in keywords):
        matches.append(c)

print(f"Matches found: {len(matches)}")
for idx, m in enumerate(matches, 1):
    print(f"\n--- MATCH {idx} ---")
    print(f"ID: {m.get('id')}")
    print(f"Title: {m.get('title')}")
    print(f"Model: {m.get('model_name')}")
    print(f"Duration: {m.get('duration')}s")
    print(f"Tags: {m.get('tags')}")
    print(f"Image: {m.get('image_large_url') or m.get('image_url')}")
    print(f"Audio: {m.get('audio_url')}")
    print(f"Prompt snippet: {m.get('prompt')[:150]}")

