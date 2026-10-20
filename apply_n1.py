import json

target_path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(target_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. 파일 상단에 import re 추가
if 'import re' not in text:
    text = 'import re\n' + text
    print("Added import re to top of file")

# 2. test_stop_loss_dry_run_3_ticks_alerts_only_once_and_keeps_fired_empty 단정 확인
# sched._stop_loss_alerted.get("NVDA")의 세션 날짜 계산:
# 테스트 실행 시점이 2026-09-07이므로 실제 날짜가 "2026-09-07"입니다.
# 정규식과 리터럴 일치 검증:
old_assert = 'assert re.match(r"^\\d{4}-\\d{2}-\\d{2}$", today_session)'
if old_assert not in text:
    print("re.match already in text or needs update")

with open(target_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated tests/test_scheduler_sizing.py with import re!")
