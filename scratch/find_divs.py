with open('dashboard/dream_closet_future_master_app.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = re.findall(r'<div class="[^"]*rounded-2xl[^"]*"', c)
for m in matches[:10]:
    print(m)
