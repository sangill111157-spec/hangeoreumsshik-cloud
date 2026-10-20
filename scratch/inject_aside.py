# -*- coding: utf-8 -*-
from pathlib import Path

names = [
    'dept_closet.html',
    'dept_connect_ai.html',
    'dept_media.html',
    'dept_education.html',
    'dept_vault.html',
    'dept_treasury.html'
]

tag = '<script src="/aside_drawer.js"></script>'

for name in names:
    p = Path('dashboard/departments') / name
    if not p.exists():
        print(f"File not found: {p}")
        continue
    content = p.read_text(encoding='utf-8')
    if tag not in content:
        idx = content.rfind('</body>')
        if idx != -1:
            new_content = content[:idx] + '  ' + tag + '\n' + content[idx:]
            p.write_text(new_content, encoding='utf-8')
            print(f"Successfully injected to {name}")
        else:
            print(f"No </body> tag in {name}")
    else:
        print(f"Already injected in {name}")
