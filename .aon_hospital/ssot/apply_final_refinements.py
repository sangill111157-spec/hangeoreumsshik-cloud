import re

# 1. app/services/scheduler.py
sched_path = r'C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py'
with open(sched_path, 'r', encoding='utf-8') as f:
    sched_text = f.read()

# 1-1. STOP_LOSS_JOB_ID 상수 정의
if 'STOP_LOSS_JOB_ID' not in sched_text:
    target_imp = 'STOP_LOSS_PCT = 8.0'
    new_const = 'STOP_LOSS_JOB_ID: str = "stop_loss_monitor"\nSTOP_LOSS_PCT = 8.0'
    sched_text = sched_text.replace(target_imp, new_const, 1)
    print("Added STOP_LOSS_JOB_ID constant")

# 1-2. EVENT_JOB_ERROR import 및 리스너 등록에 추가
if 'EVENT_JOB_ERROR' not in sched_text:
    sched_text = sched_text.replace(
        'from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES',
        'from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR'
    )
    sched_text = sched_text.replace(
        'EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES',
        'EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES | EVENT_JOB_ERROR'
    )
    print("Added EVENT_JOB_ERROR to events and listener")

# 1-3. _on_scheduler_job_event에서 STOP_LOSS_JOB_ID 상수 참조
sched_text = sched_text.replace(
    'if getattr(event, \'job_id\', \'\') == "stop_loss_monitor":',
    'if getattr(event, \'job_id\', \'\') == STOP_LOSS_JOB_ID:'
)

# 1-4. add_job에서 STOP_LOSS_JOB_ID 상수 참조
sched_text = sched_text.replace(
    'id="stop_loss_monitor",',
    'id=STOP_LOSS_JOB_ID,'
)

# 1-5. 저장 실패 알림 폭주 방지: >= 3 -> == 3
sched_text = sched_text.replace(
    'if self._stop_loss_save_fail_count >= 3:',
    'if self._stop_loss_save_fail_count == 3:'
)
print("Updated stop_loss_save_fail_count condition to == 3")

with open(sched_path, 'w', encoding='utf-8') as f:
    f.write(sched_text)


# 2. tests/test_scheduler_sizing.py
test_path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(test_path, 'r', encoding='utf-8') as f:
    test_text = f.read()

# 2-1. 미사용 import 2건 제거 (timedelta, time as dtime)
old_dt_imp = 'from datetime import datetime, timezone, timedelta, time as dtime'
new_dt_imp = 'from datetime import datetime, timezone'
if old_dt_imp in test_text:
    test_text = test_text.replace(old_dt_imp, new_dt_imp, 1)
    print("Removed unused timedelta and dtime imports")

# 2-2. STOP_LOSS_JOB_ID import 및 test_stop_loss_job_skip_or_missed_triggers_critical_alert 수정
if 'from app.services.scheduler import get_scheduler, is_market_open_for_ticker, get_session_date_for_ticker, TradingScheduler' in test_text:
    test_text = test_text.replace(
        'from app.services.scheduler import get_scheduler, is_market_open_for_ticker, get_session_date_for_ticker, TradingScheduler',
        'from app.services.scheduler import get_scheduler, is_market_open_for_ticker, get_session_date_for_ticker, TradingScheduler, STOP_LOSS_JOB_ID'
    )
    print("Imported STOP_LOSS_JOB_ID in test file")

test_text = test_text.replace(
    'job_id="stop_loss_monitor"',
    'job_id=STOP_LOSS_JOB_ID'
)

# 2-3. == 3 저장 실패 단독 알림 검증 테스트 추가
save_3strike_test = '''

def test_stop_loss_state_save_failure_alerts_on_third_strike_only():
    """저장 실패 3회차에만 CRITICAL 경보 1회 발송되고 4회차 이후 폭주가 억제되며, 성공 시 카운터가 리셋된다."""
    sched = get_scheduler()
    sched._stop_loss_save_fail_count = 0

    with patch.object(sched, "_send_telegram") as mock_tg, \\
         patch("os.replace", side_effect=OSError("Disk full")):

        # 1회 실패: 카운터 1, 알림 0회
        sched._save_stop_loss_state()
        assert sched._stop_loss_save_fail_count == 1
        assert mock_tg.call_count == 0

        # 2회 실패: 카운터 2, 알림 0회
        sched._save_stop_loss_state()
        assert sched._stop_loss_save_fail_count == 2
        assert mock_tg.call_count == 0

        # 3회 실패: 카운터 3, CRITICAL 경보 정확히 1회 발송!
        sched._save_stop_loss_state()
        assert sched._stop_loss_save_fail_count == 3
        assert mock_tg.call_count == 1
        assert "저장이 3회 연속 실패했습니다" in mock_tg.call_args[0][0]

        # 4회 실패: 카운터 4, 경보 폭주 억제(추가 발송 0회, 총 1회 유지)!
        sched._save_stop_loss_state()
        assert sched._stop_loss_save_fail_count == 4
        assert mock_tg.call_count == 1

    # 5회차 정상 저장 성공: 카운터 0으로 완전 리셋!
    sched._save_stop_loss_state()
    assert sched._stop_loss_save_fail_count == 0
'''

if 'def test_stop_loss_state_save_failure_alerts_on_third_strike_only' not in test_text:
    test_text += save_3strike_test
    print("Added test_stop_loss_state_save_failure_alerts_on_third_strike_only")

with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_text)

print("Finished applying all final refinements!")
