# -*- coding: utf-8 -*-
import sys
import json
import pathlib

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

json_path = pathlib.Path("studio_vault/CEO_SUNO_V6_ORIGINALS/suno_clips_raw.json")
data = json.loads(json_path.read_text(encoding="utf-8"))
clips = data.get("clips", [])

print(f"Total clips loaded: {len(clips)}")

keywords = ["희망", "등불", "바다", "Theme", "SUN-ONE", "썬원", "Official Theme"]

matches = []
for c in clips:
    title = c.get("title") or ""
    metadata = c.get("metadata") or {}
    prompt = metadata.get("prompt") or ""
    tags = metadata.get("tags") or ""
    full_text = f"{title} {prompt} {tags}"
    if any(k.lower() in full_text.lower() for k in keywords):
        matches.append(c)

print(f"\nTotal matches found: {len(matches)}")
for idx, m in enumerate(matches, 1):
    meta = m.get("metadata") or {}
    print(f"\n--- MATCH {idx} ---")
    print(f"ID: {m.get('id')}")
    print(f"Title: {m.get('title')}")
    print(f"Model: {m.get('model_name')}")
    print(f"Duration: {meta.get('duration')}s")
    print(f"Audio URL: {m.get('audio_url')}")
    print(f"Image URL: {m.get('image_large_url') or m.get('image_url')}")
    print(f"Tags: {meta.get('tags')}")
    print(f"Prompt snippet: {meta.get('prompt')[:150]}")

