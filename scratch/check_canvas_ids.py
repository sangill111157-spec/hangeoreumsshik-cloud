with open('dashboard/dream_closet_future_master_app.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = re.findall(r'id=["\']([a-zA-Z0-9_\-]+)["\']', c)
canvas_ids = [m for m in matches if 'canvas' in m.lower()]
print('Canvas IDs in standalone app:', canvas_ids)
