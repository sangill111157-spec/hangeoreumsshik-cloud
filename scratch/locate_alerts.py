# -*- coding: utf-8 -*-
from pathlib import Path
for f in ['dashboard/departments/dept_connect_ai.html', 'dashboard/departments/dept_media.html', 'dashboard/departments/dept_vault.html']:
    txt = Path(f).read_text(encoding='utf-8')
    for idx, line in enumerate(txt.splitlines()):
        if 'onclick=' in line and 'alert(' in line:
            print(f'{f}:{idx+1} -> {line.strip()[:140]}')
