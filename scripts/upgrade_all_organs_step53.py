import glob, re, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))

PROTECTED = {'rgon_Numeric_Organ.py', 'rgon_work_loop.py', 'rgon_self_Reflection.py', 'index_20260405_backup.html'}
TARGET_VER = 'v11.52-AON-PAGE-BUTTON-BOT'
TARGET_AB = 'R1~R53'

count = 0
for f in glob.glob('rgon_*.py'):
    if f in PROTECTED:
        continue
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        new_content = re.sub(r'VERSION\s*=\s*"v11\.\d+-[A-Z0-9-]+"', f'VERSION = "{TARGET_VER}"', content)
        new_content = re.sub(r'ANTIBODY_RANGE\s*=\s*"R1~R\d+"', f'ANTIBODY_RANGE = "{TARGET_AB}"', new_content)
        new_content = re.sub(r'ANTIBODIES\s*=\s*"R1~R\d+"', f'ANTIBODIES = "{TARGET_AB}"', new_content)
        
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(new_content)
            count += 1
            print(f'Updated {f}')
    except Exception as e:
        print(f'Error updating {f}: {e}')

print(f'Total {count} files upgraded to {TARGET_VER}')
