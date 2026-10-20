import urllib.request
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Test compliance-audit
print("--- 1. Testing /api/compliance-audit ---")
try:
    with urllib.request.urlopen("http://127.0.0.1:8501/api/compliance-audit", timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Status:", data.get("overall_status"))
        print("Signals:", list(data.get("signals", {}).keys()))
        print("Briefing:", data.get("briefing")[:80])
except Exception as e:
    print("Error on compliance-audit:", e)

# 2. Test empire-council
print("\n--- 2. Testing /api/empire-council ---")
try:
    req = urllib.request.Request("http://127.0.0.1:8501/api/empire-council", data=b"{}", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Success:", data.get("success"))
        print("Model:", data.get("model"))
        print("Council Text:\n", data.get("text")[:250], "...")
except Exception as e:
    print("Error on empire-council:", e)
