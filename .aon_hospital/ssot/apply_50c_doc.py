# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\docs\testing_runtime_protocol.md'

with open(target_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Locate line 72
idx_72 = -1
for i, l in enumerate(lines):
    if '| 72 | 13.90 s | 329 |' in l:
        idx_72 = i
        break
assert idx_72 != -1, 'Line 72 not found'

line_73 = '| 73 | 14.54 s | 329 | 백로그 50 커밋 A(ec6913b) 지표 검증 실행 (n=1, 중위값 비산입) | `C:\\Users\\sangi\\.gemini\\antigravity-ide\\brain\\12531781-a500-4dda-9423-9d53b71046e4\\.system_generated\\tasks\\task-151.log` |\n'
lines.insert(idx_72 + 1, line_73)

# 2. Locate header line with b7e2bbb
idx_hdr = -1
for i, l in enumerate(lines):
    if '`b7e2bbb`' in l and i > idx_72 + 1:
        idx_hdr = i
        break
assert idx_hdr != -1, 'Header line with b7e2bbb not found'

lines[idx_hdr] = lines[idx_hdr].replace('`b7e2bbb`', '`ec6913b`')

with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(lines)

print('50-C edit applied successfully!')
