with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

markers = [
    'id="tab-command"',
    'GitHub Actions 최근 실행 기록',
    '신생국가 재정 헌법',
    'id="tab-suno"',
    'id="tab-brain"',
    'id="tab-daughters"',
    'id="tab-vault"'
]

for m in markers:
    idx = c.find(m)
    print(f'{m}: index {idx}')
