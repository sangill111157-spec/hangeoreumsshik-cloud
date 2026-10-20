import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8501"

def test_api(method, path, payload=None, expected_status=200):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    else:
        data = None
    
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as res:
            elapsed = time.time() - t0
            status = res.status
            body = res.read().decode('utf-8')
            try:
                js = json.loads(body)
            except:
                js = body[:100]
            return {
                "path": path,
                "method": method,
                "status": status,
                "ok": status == expected_status,
                "elapsed": f"{elapsed:.3f}s",
                "preview": str(js)[:120]
            }
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        body = e.read().decode('utf-8', errors='ignore')
        return {
            "path": path,
            "method": method,
            "status": e.code,
            "ok": e.code == expected_status,
            "elapsed": f"{elapsed:.3f}s",
            "error": body[:120]
        }
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "path": path,
            "method": method,
            "status": "ERR",
            "ok": False,
            "elapsed": f"{elapsed:.3f}s",
            "error": str(e)
        }

tests = [
    ("GET", "/api/version", None, 200),
    ("GET", "/api/wisdom-ledger", None, 200),
    ("POST", "/api/wisdom-ledger", {"type": "good", "title": "전수 검증 E2E 테스트 자동화", "desc": "파이썬 및 브라우저 에이전트를 이용한 35개 전 버튼 전수 검증 체계"}, 200),
    ("GET", "/api/vault-keys", None, 200),
    ("GET", "/api/status", None, 200),
    ("POST", "/api/general-affairs-clean", {}, 200),
    ("POST", "/api/legal-audit", {}, 200),
    ("POST", "/api/github-scout", {"category": "healing_audio", "query": ""}, 200),
    ("POST", "/api/adopt-opensource", {"repo": "test/repo", "summary": "테스트 요약", "action": "테스트 실행"}, 200),
    ("GET", "/api/launch-status", None, 200),
    ("POST", "/api/launch", {"target": "daily_report"}, 200),
    ("POST", "/api/telegram-report", {"title": "테스트 보고", "message": "전수 검증 테스트"}, 200),
    ("GET", "/api/suno-files", None, 200),
    ("POST", "/api/chat", {"message": "안실장 안녕! 현재 상태 브리핑해줘"}, 200),
    ("POST", "/api/dispatch-to-agent", {"prompt": "테스트 태스크", "priority": "high"}, 200),
    ("POST", "/api/empire-council", {"topic": "전수 검증 및 제국 실록 연동"}, 200),
]

print("=== [E2E Backend API Verification] ===")
results = []
for method, path, payload, expected in tests:
    res = test_api(method, path, payload, expected)
    status_text = "[OK]" if res["ok"] else "[FAIL]"
    try:
        print(f"{status_text} [{res['method']} {res['path']}] Status: {res['status']} ({res['elapsed']})")
    except:
        pass
    results.append(res)

with open("scratch/api_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Saved to scratch/api_test_results.json")
