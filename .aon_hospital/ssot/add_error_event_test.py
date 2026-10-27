test_path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(test_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. EVENT_JOB_ERROR import 추가
if 'from apscheduler.events import JobExecutionEvent, EVENT_JOB_MAX_INSTANCES' in text:
    text = text.replace(
        'from apscheduler.events import JobExecutionEvent, EVENT_JOB_MAX_INSTANCES',
        'from apscheduler.events import JobExecutionEvent, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR'
    )

# 2. 신규 테스트 추가
new_err_test = '''

def test_stop_loss_job_error_event_alerts_with_exception_details_and_independent_throttle():
    """EVENT_JOB_ERROR 발생 시 exception/traceback 포함 경보가 발송되고, 스킵 이벤트와 스로틀이 상호 간섭하지 않는다."""
    sched = get_scheduler()
    sched._stop_loss_error_last_alert = 0.0
    sched._stop_loss_skip_last_alert = 0.0

    mock_trader = MagicMock()
    with patch.object(sched, "_send_telegram") as mock_tg, \\
         patch("app.services.scheduler.get_auto_trader", return_value=mock_trader):

        # 1. ERROR 이벤트 발생 -> 예외 세부정보 포함 경보 발송
        err_event = JobExecutionEvent(
            code=EVENT_JOB_ERROR,
            job_id=STOP_LOSS_JOB_ID,
            jobstore="default",
            scheduled_run_time=datetime.now(),
            exception=RuntimeError("Unhandled worker crash"),
            traceback="Fake traceback line 1\\nFake traceback line 2"
        )
        sched._on_scheduler_job_event(err_event)

        assert mock_tg.call_count == 1
        calls = [c[0][0] for c in mock_tg.call_args_list]
        assert any("손절 감시 잡 실행 중 예외 발생" in msg and "Unhandled worker crash" in msg for msg in calls)

        # 2. 직후 스킵 이벤트 발생 -> 독립 스로틀이므로 조용히 억제되지 않고 정상 발송! (call_count == 2)
        skip_event = JobExecutionEvent(
            code=EVENT_JOB_MAX_INSTANCES,
            job_id=STOP_LOSS_JOB_ID,
            jobstore="default",
            scheduled_run_time=datetime.now()
        )
        sched._on_scheduler_job_event(skip_event)
        assert mock_tg.call_count == 2
        calls2 = [c[0][0] for c in mock_tg.call_args_list]
        assert any("손절 감시 틱 스킵/미스파이어 발생" in msg for msg in calls2)
'''

if 'def test_stop_loss_job_error_event_alerts_with_exception_details_and_independent_throttle' not in text:
    text += new_err_test
    print("Added test_stop_loss_job_error_event_alerts_with_exception_details_and_independent_throttle!")

with open(test_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished updating tests!")
