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

href_hash = []
for f in files:
    p = Path(f)
    if not p.exists():
        continue
    txt = p.read_text(encoding='utf-8', errors='ignore')
    for idx, line in enumerate(txt.splitlines()):
        if 'href="#"' in line or "href='#'" in line:
            href_hash.append((f, idx+1, line.strip()))

print(f'Dead links (href="#"): {len(href_hash)}')
for f, idx, line in href_hash:
    print(f' - [{f}:{idx}] {line[:100]}')
