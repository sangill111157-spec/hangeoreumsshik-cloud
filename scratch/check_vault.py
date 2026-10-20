import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = [m.start() for m in re.finditer(r'tab-vault|기억 금고|settings-modal', c)]
for idx in matches:
    print('--- match at', idx)
    print(c[max(0, idx-50):min(len(c), idx+150)])
