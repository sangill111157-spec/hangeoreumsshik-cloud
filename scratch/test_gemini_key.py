import urllib.request
import json
from pathlib import Path

# config/.env 읽기
env_vars = {}
for line in Path("config/.env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env_vars[k.strip()] = v.strip().strip('"').strip("'")

yt_key = env_vars.get("YOUTUBE_API_KEY")
print("Trying YOUTUBE_API_KEY:", yt_key[:8] if yt_key else "None")

payload = {
    "contents": [
        {
            "role": "user",
            "parts": [{"text": "안실장"}]
        }
    ]
}

for model in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={yt_key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"SUCCESS with {model}:")
            print(data["candidates"][0]["content"]["parts"][0]["text"][:150])
            break
    except urllib.error.HTTPError as e:
        print(f"FAILED {model}: {e.code}")
        print(e.read().decode("utf-8", errors="ignore")[:200])
