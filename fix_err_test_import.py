test_path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(test_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = 'def test_stop_loss_job_error_event_alerts_with_exception_details_and_independent_throttle():\n    """EVENT_JOB_ERROR'
replacement = 'def test_stop_loss_job_error_event_alerts_with_exception_details_and_independent_throttle():\n    from apscheduler.events import JobExecutionEvent, EVENT_JOB_ERROR, EVENT_JOB_MAX_INSTANCES\n    """EVENT_JOB_ERROR'

text = text.replace(target, replacement, 1)

with open(test_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Added local import in test_stop_loss_job_error_event_alerts_with_exception_details_and_independent_throttle")
