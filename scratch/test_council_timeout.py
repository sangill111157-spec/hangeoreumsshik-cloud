import urllib.request
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Testing /api/empire-council with 35s timeout...")
req = urllib.request.Request("http://127.0.0.1:8501/api/empire-council", data=b"{}", headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=35) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Success:", data.get("success"))
        print("Model:", data.get("model"))
        print("\n=== COUNCIL BRIEFING ===\n")
        print(data.get("text"))
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print("General Error:", e)
