import urllib.request
import urllib.parse
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

queries = {
    'audio': 'ambient audio OR sleep sound OR ffmpeg audio stars:>100',
    'education': 'kids learning OR canvas game OR educational game stars:>100',
    'quant': 'quant trading OR stock analysis stars:>200',
    'agent': 'ai agent OR autonomous agent stars:>200'
}

for cat, q in queries.items():
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&sort=stars&order=desc&per_page=3"
    req = urllib.request.Request(url, headers={'User-Agent': 'OmniNexus-Scout/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            print(f"=== {cat} (Total: {data.get('total_count', 0)}) ===")
            for item in data.get('items', []):
                lic = item['license']['spdx_id'] if item.get('license') else 'None'
                desc = (item.get('description') or '')[:70]
                print(f"  * {item['full_name']} (Stars: {item['stargazers_count']}, Lic: {lic}) - {desc}")
    except Exception as e:
        print(f"=== {cat} Error:", e)
