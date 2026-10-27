import os
import json

p_dir = r'C:\Users\sangi\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\0801'
draft_content_path = os.path.join(p_dir, 'draft_content.json')

with open(draft_content_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== CapCut 0801 Project Overview ===")
print("Canvas config:", data.get("canvas_config"))
print("Duration (us):", data.get("duration"))
print("Tracks:")
for idx, trk in enumerate(data.get("tracks", [])):
    t_type = trk.get("type")
    segs = trk.get("segments", [])
    print(f" Track {idx} [{t_type}]: {len(segs)} segments")

materials = data.get("materials", {})
print("\nMaterials:")
for k, v in materials.items():
    if isinstance(v, list):
        print(f" - {k}: {len(v)} items")
