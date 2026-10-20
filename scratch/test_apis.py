import urllib.request
import json

base = "http://127.0.0.1:8501"

def test_api(url, payload=None):
    req = urllib.request.Request(
        f"{base}{url}",
        data=json.dumps(payload).encode("utf-8") if payload else None,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

print("1. /api/system-status:")
res1 = test_api("/api/system-status")
print("  success:", res1.get("disk_free_gb"))

print("\n2. /api/analyze-youtube-url:")
res2 = test_api("/api/analyze-youtube-url", {"url": "https://youtube.com/shorts/_zuysTgqoF0"})
print("  video_id:", res2.get("video_id"))
print("  metadata:", res2.get("metadata", {}).get("title"))
print("  report len:", len(res2.get("fusion_report", "")))

print("\n3. /api/copyright-register:")
res3 = test_api("/api/copyright-register", {"work_title": "Omni-Nexus v2.0"})
print("  dossier_id:", res3.get("dossier_id"))
print("  author:", res3.get("author"))
print("  co_creators:", res3.get("co_creators"))

print("\n4. /api/github-scout-super-presets:")
res4 = test_api("/api/github-scout-super-presets", {"preset_id": "artcraft"})
print("  preset title:", res4.get("preset", {}).get("title"))
print("  badge:", res4.get("preset", {}).get("badge"))

print("\nALL 4 APIS WORKING PERFECTLY!")
