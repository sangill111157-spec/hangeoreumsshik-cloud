import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[:1000], 1):
    if 'id="tab-' in l:
        print(f'{i}: {l.strip()[:100]}')

for i, l in enumerate(lines[1550:1620], 1551):
    if 'id="tab-' in l or '꿈의 옷장' in l or '드림 클로젯' in l or '하이브리드 패션' in l:
        print(f'{i}: {l.strip()[:100]}')
