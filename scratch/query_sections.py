with open('dashboard/index.html', encoding='utf-8') as f:
    text = f.read()

import re

queries = [
    ('어전회의 모달 복사/텔레그램', r'id="council-[^"]+"|copyCouncil|sendCouncil'),
    ('헤더 보안설정', r'vault|setting|보안'),
    ('제1원 법무 감사', r'compliance|audit|legal'),
    ('제2원 scout', r'scout|오픈소스|답사'),
    ('제3원 나눔 온도계', r'donation|charity|나눔|온도'),
    ('클라우드 발사대', r'workflow|dispatch|발사|trigger'),
    ('채팅 프리셋', r'preset|quick|안실장|질문'),
    ('인증원 세 딸 프리셋', r'daughter|인증서|첫째|둘째|셋째'),
]

out = []
for label, pat in queries:
    m = re.findall(pat, text, re.IGNORECASE)
    out.append(f"=== {label} === ({len(m)} matches)")
    found_lines = []
    for line in text.splitlines():
        if re.search(pat, line, re.IGNORECASE):
            found_lines.append(line.strip()[:120])
    for l in found_lines[:8]:
        out.append(f"  {l}")

with open('scratch/query_sections_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Wrote to scratch/query_sections_out.txt")
