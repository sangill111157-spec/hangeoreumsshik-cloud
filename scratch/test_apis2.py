import urllib.request
import json

base = "http://127.0.0.1:8501"

def test_api(url, payload=None, timeout=25):
    req = urllib.request.Request(
        f"{base}{url}",
        data=json.dumps(payload).encode("utf-8") if payload else None,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

print("3. /api/copyright-register 테스트:")
res3 = test_api("/api/copyright-register", {"work_title": "Omni-Nexus v2.0"})
print("  dossier_id:", res3.get("dossier_id"))
print("  author:", res3.get("author"))
print("  co_creators:", res3.get("co_creators"))
print("  sha256:", res3.get("sha256")[:16])

print("\n4. /api/github-scout-super-presets 테스트:")
res4 = test_api("/api/github-scout-super-presets", {"preset_id": "artcraft"})
print("  preset title:", res4.get("preset", {}).get("title"))
print("  badge:", res4.get("preset", {}).get("badge"))

print("\n2. /api/analyze-youtube-url 테스트 (timeout 30s):")
try:
    res2 = test_api("/api/analyze-youtube-url", {"url": "https://youtube.com/shorts/_zuysTgqoF0"}, timeout=30)
    print("  video_id:", res2.get("video_id"))
    print("  metadata title:", res2.get("metadata", {}).get("title"))
    print("  report len:", len(res2.get("fusion_report", "")))
except Exception as e:
    print("  youtube url test error:", e)

print("\nDONE!")
