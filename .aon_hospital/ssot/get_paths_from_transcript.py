# -*- coding: utf-8 -*-
import json, re

t_path = r'C:\Users\sangi\.gemini\antigravity-ide\brain\593500b5-1844-4ea0-bbeb-7ab36bfba970\.system_generated\logs\transcript.jsonl'
seen = set()
with open(t_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        matches = re.findall(r'[A-Za-z]:\\[^"\'\n\r\t<>]+', line)
        for m in matches:
            if any(k in m.lower() for k in ['nvda', 'trading', 'app.tsx', 'master.py']):
                clean = m.strip()
                if clean not in seen:
                    seen.add(clean)
                    print('Found path:', clean)
