import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1710, 1735):
    if i < len(lines):
        print(f"{i+1}: {repr(lines[i])}")
