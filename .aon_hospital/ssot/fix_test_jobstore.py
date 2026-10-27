path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old = 'event1 = JobExecutionEvent(code=EVENT_JOB_MAX_INSTANCES, job_id="stop_loss_monitor", scheduled_run_time=datetime.now())'
new = 'event1 = JobExecutionEvent(code=EVENT_JOB_MAX_INSTANCES, job_id="stop_loss_monitor", jobstore="default", scheduled_run_time=datetime.now())'

if old in text:
    text = text.replace(old, new, 1)
    print("Replaced old pattern successfully!")
else:
    print("Warning: old pattern not found directly!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished fixing test jobstore!")
