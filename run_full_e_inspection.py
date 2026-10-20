# -*- coding: utf-8 -*-
import sys, os, subprocess, json, time, asyncio, urllib.request
backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.path.insert(0, backend_dir)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=backend_dir):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return res.stdout, res.stderr

print("==================================================")
print("1. [1cdbedf RAW -U0 DIFF] git diff 1cdbedf~1..1cdbedf -U0")
print("==================================================")
h_file = os.path.join(backend_dir, "h.txt")
run_cmd(f"git diff 1cdbedf~1..1cdbedf -U0 -- app/services/master_signal.py > {h_file}")
with open(h_file, "r", encoding="utf-8", errors="replace") as f:
    print(f.read())

print("\n==================================================")
print("2. [MasterSignalResult DEFINITION] master_signal.py")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\master_signal.py'), 'r', encoding='utf-8', errors='replace') as f:
    ms_lines = f.readlines()
for i, l in enumerate(ms_lines):
    if 'class MasterSignalResult' in l:
        for j in range(i, min(len(ms_lines), i + 35)):
            print(f"{j+1:4d}: {ms_lines[j].rstrip()}")
        break

print("\n==================================================")
print("3. [kis_broker.py AS-IS GREP]")
print("==================================================")
out, _ = run_cmd('git grep -n -E "rt_code|rt_msg|\"success\"" app/services/kis_broker.py')
print(out)

print("\n==================================================")
print("4. [llm_analyzer.py & Institutional (master_signal.py) BRANCHES]")
print("==================================================")
with open(os.path.join(backend_dir, r'app\services\llm_analyzer.py'), 'r', encoding='utf-8', errors='replace') as f:
    llm_lines = f.readlines()
for i, l in enumerate(llm_lines):
    if 'def _analyze_sentiment' in l or 'sentiment_label' in l or 'def analyze(' in l:
        for j in range(i, min(len(llm_lines), i + 25)):
            print(f"llm_analyzer:{j+1:4d}: {llm_lines[j].rstrip()}")
        break

for i, l in enumerate(ms_lines):
    if 'inst_score' in l or 'institutional' in l:
        if 'signal=' in l or 'ComponentScore' in l:
            for j in range(max(0, i-5), min(len(ms_lines), i+15)):
                print(f"master_signal:{j+1:4d}: {ms_lines[j].rstrip()}")
            break

print("\n==================================================")
print("5. [gather DETAILED CALL SITE & 8 TASKS IN stock.py]")
print("==================================================")
with open(os.path.join(backend_dir, r'app\api\routes\stock.py'), 'r', encoding='utf-8', errors='replace') as f:
    stock_lines = f.readlines()
for i in range(580, 640):
    print(f"stock.py:{i+1:4d}: {stock_lines[i].rstrip()}")

print("\n==================================================")
print("6. [LIVE /signal PAYLOAD & MULTI-STRATEGY SCORE]")
print("==================================================")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/stock/NVDA/signal", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        live_json = json.loads(resp.read().decode('utf-8'))
        print("Live /signal response summary:")
        print("  master_score:", live_json.get("master_score"))
        print("  raw_score   :", live_json.get("raw_score"))
        print("  coverage    :", live_json.get("coverage"))
        print("  signal      :", live_json.get("signal"))
        print("  components  :")
        for c in live_json.get("components", []):
            print(f"    - {c.get('name'):12s}: score={c.get('score')}, signal={c.get('signal')}, conf={c.get('confidence')}")
except Exception as e:
    print("Live signal fetch error:", e)

