# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\docs\testing_runtime_protocol.md'

with open(target_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Locate line 73
idx_73 = -1
for i, l in enumerate(lines):
    if '| 73 | 14.54 s | 329 |' in l:
        idx_73 = i
        break
assert idx_73 != -1, 'Line 73 not found'

new_rows = [
    '| 74 | 29.82 s | 329 | 백로그 57-A 커밋 A(4909241) 지표 검증 실행 (n=1, 중위값 비산입) | `C:\\\\Users\\\\sangi\\\\.gemini\\\\antigravity-ide\\\\brain\\\\12531781-a500-4dda-9423-9d53b71046e4\\\\.system_generated\\\\tasks\\\\task-222.log` |\n',
    '| 75 | 42.73 s | 329 | 백로그 57-B 커밋 A(a7f52c1) 지표 검증 실행 (n=1 기록 전용, 신규 최댓값(직전 최댓값 39.48 s / 회차 40), 중위값 비산입) | `C:\\\\Users\\\\sangi\\\\.gemini\\\\antigravity-ide\\\\brain\\\\12531781-a500-4dda-9423-9d53b71046e4\\\\.system_generated\\\\tasks\\\\task-269.log` |\n',
    '| 76 | 35.66 s | 329 | 백로그 57-C 커밋 A(dc628c5) 지표 검증 실행 (n=1, 중위값 비산입) | `C:\\\\Users\\\\sangi\\\\.gemini\\\\antigravity-ide\\\\brain\\\\12531781-a500-4dda-9423-9d53b71046e4\\\\.system_generated\\\\tasks\\\\task-298.log` |\n',
    '| 77 | 34.16 s | 329 | 백로그 56 커밋 A(e926d76) 지표 검증 실행 (n=1, 중위값 비산입) | `C:\\\\Users\\\\sangi\\\\.gemini\\\\antigravity-ide\\\\brain\\\\12531781-a500-4dda-9423-9d53b71046e4\\\\.system_generated\\\\tasks\\\\task-329.log` |\n',
]

for offset, row in enumerate(new_rows):
    lines.insert(idx_73 + 1 + offset, row)

# 2. Locate header line with ec6913b
idx_hdr = -1
for i, l in enumerate(lines):
    if '`ec6913b`' in l and i > idx_73 + 4:
        idx_hdr = i
        break
assert idx_hdr != -1, 'Header line with ec6913b not found'

lines[idx_hdr] = lines[idx_hdr].replace('`ec6913b`', '`e926d76`')

with open(target_file, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(lines)

print('Combined docs edit applied successfully!')
