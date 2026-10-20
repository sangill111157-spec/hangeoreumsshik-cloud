import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

start_pos = c.find('id="tab-command"')
end_pos = c.find('id="tab-suno"')
segment = c[start_pos:end_pos]

lines = segment.splitlines()
depth = 0
for i, line in enumerate(lines):
    open_count = len(re.findall(r'<div[^>]*>', line))
    close_count = len(re.findall(r'</div>', line))
    old_depth = depth
    depth += (open_count - close_count)
    if depth <= 1 or old_depth <= 1:
        text = line.strip()[:100]
        if text:
            print(f"Line {i+1} (depth {old_depth}->{depth}): {text}")
