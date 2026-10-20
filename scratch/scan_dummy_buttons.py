# -*- coding: utf-8 -*-
from pathlib import Path
import re

files = [
    'dashboard/index.html',
    'dashboard/departments/dept_closet.html',
    'dashboard/departments/dept_connect_ai.html',
    'dashboard/departments/dept_media.html',
    'dashboard/departments/dept_education.html',
    'dashboard/departments/dept_vault.html',
    'dashboard/departments/dept_treasury.html',
    'dashboard/safe_daily_lucky_app.html',
    'dashboard/safe_salary_planner_app.html',
    'dashboard/safe_healing_sound_app.html',
    'dashboard/safe_rich_dna_test_app.html',
    'dashboard/safe_daily_routine_app.html',
    'dashboard/aside_drawer.js'
]

onclick_pat = re.compile(r'onclick=["\']([^"\']+)["\']', re.IGNORECASE)

total_buttons = 0
dummy_candidates = []

for f in files:
    p = Path(f)
    if not p.exists():
        continue
    txt = p.read_text(encoding='utf-8', errors='ignore')
    for m in onclick_pat.finditer(txt):
        handler = m.group(1).strip()
        total_buttons += 1
        if handler.startswith('alert(') or handler == 'void(0)' or handler == '#' or handler == '':
            dummy_candidates.append((f, handler))

print(f'Total buttons found by onclick: {total_buttons}')
print(f'Dummy button candidates (alert only or void): {len(dummy_candidates)}')
for f, h in dummy_candidates:
    print(f' - [{f}] {h}')
