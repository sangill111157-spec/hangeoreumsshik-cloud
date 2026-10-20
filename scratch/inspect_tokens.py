import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

start_pos = c.find('id="tab-command"')
end_pos = c.find('id="tab-suno"')
segment = c[start_pos:end_pos]

tokens = re.finditer(r'<div[^>]*>|</div>', segment)
depth = 0
for i, m in enumerate(tokens):
    tok = m.group(0)
    old_depth = depth
    if tok == '</div>':
        depth -= 1
    else:
        depth += 1
    
    if depth <= 1 or old_depth <= 1 or i < 35:
        # print snippet around this token
        pos = m.start()
        line_start = segment.rfind('\n', 0, pos)
        line_end = segment.find('\n', pos)
        line_text = segment[line_start:line_end].strip()
        print(f"Token {i:3d} (depth {old_depth:2d}->{depth:2d}): {tok:20s} | {line_text[:80]}")
