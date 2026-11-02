import json

with open("studio_dom_snapshot.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print("URL:", d.get("url"))
print("Desc length:", d.get("descLength"))
print("=== FILE INPUTS ===")
for fi in d.get("fileInputs", []):
    print(fi)
print("=== BUTTONS ===")
for b in d.get("btns", []):
    print(f"[{b['index']}] id='{b['id']}', tag='{b['tag']}', text='{b['text']}', disabled={b['disabled']}, parent='{b['parentText'][:40]}'")

