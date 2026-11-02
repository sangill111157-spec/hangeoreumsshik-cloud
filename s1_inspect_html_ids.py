# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print("HTML length:", len(text))
for m in re.finditer(r'id=["\']([^"\']+)["\']', text):
    i = m.group(1)
    if any(k in i.lower() for k in ['modal', 'btn', 'dr-', 'b-']):
        print('ID:', i)

