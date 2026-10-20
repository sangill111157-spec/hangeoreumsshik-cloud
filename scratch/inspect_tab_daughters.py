with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

start_idx = c.find('id="tab-daughters"')
end_idx = c.find('id="tab-vault"')
print(f"tab-daughters range: {start_idx} ~ {end_idx} (len: {end_idx - start_idx})")

# find sub-sections
sub_markers = [
    '한걸음씩 상생나눔 제1호 무료 앱',
    '5대 하이엔드 성우 & 트렌디 보이스 스튜디오',
    '4방향 캔버스 피팅 룸',
    '인성 시네마 퀴즈',
    '전담 초격차 관리팀',
    '3대 직통 배포 센터',
    '글로벌 4Q 균형 인재 레이더',
    '사랑의 인성 밸런스 게임'
]

for m in sub_markers:
    idx = c.find(m, start_idx)
    if idx != -1 and idx < end_idx:
        print(f"Found marker: {m} at {idx}")
    else:
        print(f"Marker not found: {m}")
