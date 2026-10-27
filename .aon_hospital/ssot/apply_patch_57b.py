# -*- coding: utf-8 -*-
import os

base_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. test_scheduler_startup_suppression.py
f1 = os.path.join(base_dir, 'tests', 'test_scheduler_startup_suppression.py')
with open(f1, 'r', encoding='utf-8') as f:
    text1 = f.read()

# Replace 4 signatures and 4 assignments
text1 = text1.replace(
    'def test_startup_burst_suppression_suppresses_blacklisted_alerts():',
    'def test_startup_burst_suppression_suppresses_blacklisted_alerts(monkeypatch):',
    1
)
text1 = text1.replace(
    '        sched.notifier = mock_notifier',
    '        monkeypatch.setattr(sched, "notifier", mock_notifier)',
    1
)

text1 = text1.replace(
    'def test_startup_window_expiry_restores_normal_alerts_and_logs_summary(caplog):',
    'def test_startup_window_expiry_restores_normal_alerts_and_logs_summary(caplog, monkeypatch):',
    1
)
text1 = text1.replace(
    '        sched.notifier = mock_notifier',
    '        monkeypatch.setattr(sched, "notifier", mock_notifier)',
    1
)

text1 = text1.replace(
    'def test_startup_window_does_not_suppress_real_stop_loss_trigger():',
    'def test_startup_window_does_not_suppress_real_stop_loss_trigger(monkeypatch):',
    1
)
text1 = text1.replace(
    '        sched.notifier = mock_notifier',
    '        monkeypatch.setattr(sched, "notifier", mock_notifier)',
    1
)

text1 = text1.replace(
    'def test_startup_window_does_not_suppress_unrecoverable_startup_failures():',
    'def test_startup_window_does_not_suppress_unrecoverable_startup_failures(monkeypatch):',
    1
)
text1 = text1.replace(
    '        sched.notifier = mock_notifier',
    '        monkeypatch.setattr(sched, "notifier", mock_notifier)',
    1
)

with open(f1, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text1)

# 2. test_scheduler_sizing.py
f2 = os.path.join(base_dir, 'tests', 'test_scheduler_sizing.py')
with open(f2, 'r', encoding='utf-8') as f:
    text2 = f.read()

text2 = text2.replace(
    'def test_apscheduler_worker_thread_telegram_alert_delivery():',
    'def test_apscheduler_worker_thread_telegram_alert_delivery(monkeypatch):',
    1
)
text2 = text2.replace(
    '    sched.notifier = mock_notifier',
    '    monkeypatch.setattr(sched, "notifier", mock_notifier)',
    1
)

with open(f2, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text2)

print("57-B patch applied successfully!")
