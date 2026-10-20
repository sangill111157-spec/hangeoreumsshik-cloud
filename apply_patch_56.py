# -*- coding: utf-8 -*-
import os

target = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_fixture_drift_guard.py'

with open(target, 'r', encoding='utf-8') as f:
    text = f.read()

old_comment = '    # 스냅샷 키 개수 검증 (36개 확정값)\n    assert len(snapshot_keys) == 39'
new_comment = '    # 스냅샷 키 개수 검증 (39개 확정값)\n    assert len(snapshot_keys) == 39'

assert old_comment in text, 'Old comment block not found'
text = text.replace(old_comment, new_comment, 1)

with open(target, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print('Backlog 56 patch applied successfully!')
