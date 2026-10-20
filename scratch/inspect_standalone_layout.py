with open('dashboard/dream_closet_future_master_app.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = re.findall(r'<div class="[^"]*max-w-[^"]*"', c)
for m in matches:
    print(m)
