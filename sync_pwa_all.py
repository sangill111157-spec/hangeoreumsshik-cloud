# -*- coding: utf-8 -*-
import os
import shutil
from pathlib import Path

pwa_tags = '  <link rel="manifest" href="/manifest.webmanifest">\n  <script src="/pwa_bootstrap.js" defer></script>'

def inject_pwa_to_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'manifest.webmanifest' not in content:
        if '</head>' in content:
            new_content = content.replace('</head>', f'{pwa_tags}\n</head>')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Injected PWA to: {file_path}')
        else:
            print(f'No </head> in {file_path}')
    else:
        print(f'Already has PWA: {file_path}')

# 1. dashboard 내부 HTML 검사
dash_dir = Path('dashboard')
for html_file in dash_dir.glob('**/*.html'):
    if html_file.name == 'offline.html':
        continue
    inject_pwa_to_html(html_file)

# 2. 루트 HTML 검사
for html_file in Path('.').glob('*.html'):
    if html_file.name == 'offline.html':
        continue
    inject_pwa_to_html(html_file)

# 3. docs 내부 HTML 검사
for html_file in Path('docs').glob('**/*.html'):
    if html_file.name == 'offline.html':
        continue
    inject_pwa_to_html(html_file)

# 4. dashboard에서 루트 및 docs 동기화
for f in ['index.html', 'rgon_alpha_chat.html', 'offline.html']:
    src = dash_dir / f
    if src.exists():
        shutil.copy2(src, Path(f))
        shutil.copy2(src, Path('docs') / f)
        print(f'Synced {f} from dashboard to root and docs')

docs_dept = Path('docs/departments')
docs_dept.mkdir(parents=True, exist_ok=True)
root_dept = Path('departments')
root_dept.mkdir(parents=True, exist_ok=True)

for dept_file in (dash_dir / 'departments').glob('*.html'):
    shutil.copy2(dept_file, docs_dept / dept_file.name)
    shutil.copy2(dept_file, root_dept / dept_file.name)
    print(f'Synced {dept_file.name} to docs/departments and departments/')

for f in ['manifest.webmanifest', 'sw.js', 'pwa_bootstrap.js', 'offline.html', 'tunnel_bridge.json', 'grok_viral_master_plan.json']:
    src = Path(f)
    if src.exists():
        shutil.copy2(src, dash_dir / f)
        shutil.copy2(src, Path('docs') / f)
        print(f'Synced asset {f} to dashboard and docs')

print('ALL HTML & PWA ASSETS FULLY SYNCED!')
