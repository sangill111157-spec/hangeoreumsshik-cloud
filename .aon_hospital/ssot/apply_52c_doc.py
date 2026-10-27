# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')
target_file = r'C:\trading\package\nvda_trading_system\backend\docs\testing_runtime_protocol.md'

with open(target_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Locate line 71
idx_71 = -1
for i, l in enumerate(lines):
    if '| 71 | 16.59 s | 329 |' in l:
        idx_71 = i
        break
assert idx_71 != -1, 'Line 71 not found'

line_72 = '| 72 | 13.90 s | 329 | 백로그 52-A 커밋 A(b7e2bbb) 지표 검증 실행 (n=1, 중위값 비산입) | `C:\\Users\\sangi\\.gemini\\antigravity-ide\\brain\\430e5f30-e823-40e4-a50a-d4d49e59e185\\.system_generated\\tasks\\task-2822.log` |\n'
lines.insert(idx_71 + 1, line_72)

# 2. Locate header line with ab90c5f
idx_hdr = -1
for i, l in enumerate(lines):
    if '`ab90c5f`' in l and i > idx_71 + 1:
        idx_hdr = i
        break
assert idx_hdr != -1, 'Header line with ab90c5f not found'

lines[idx_hdr] = lines[idx_hdr].replace('`ab90c5f`', '`b7e2bbb`')

with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(lines)

print('52-C edit applied successfully!')
