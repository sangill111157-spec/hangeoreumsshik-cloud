import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

with open('turn41_verification_log.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

for line in text.splitlines():
    if 'current_price' in line:
        d = json.loads(line)
        print("Raw JSON parsed:")
        print(json.dumps(d, indent=2, ensure_ascii=False))
        break
