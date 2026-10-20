with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = re.findall(r'id=["\'](tab-[a-zA-Z0-9_\-]+)["\']', c)
print('All tab IDs found:', set(matches))

panes = re.findall(r'<div[^>]*class=["\'][^"\']*tab-pane[^"\']*["\'][^>]*>', c)
for p in panes:
    print('Found pane:', p)
