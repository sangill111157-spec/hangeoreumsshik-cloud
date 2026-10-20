import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

start_pos = c.find('id="tab-daughters"')
end_pos = c.find('id="tab-vault"')
segment = c[start_pos:end_pos]

tokens = list(re.finditer(r'<div[^>]*>|</div>', segment))
depth = 0
for i, m in enumerate(tokens):
    tok = m.group(0)
    old_depth = depth
    if tok == '</div>':
        depth -= 1
    else:
        depth += 1
    
    pos = m.start()
    line_start = segment.rfind('\n', 0, pos)
    line_end = segment.find('\n', pos)
    line_text = segment[line_start:line_end].strip()
    if depth <= 2 or i >= len(tokens) - 10:
        print(f"Token {i:2d} (depth {old_depth:2d}->{depth:2d}): {tok[:25]:25s} | {line_text[:70]}")

print(f"\nTotal tokens: {len(tokens)}, Final depth: {depth}")
