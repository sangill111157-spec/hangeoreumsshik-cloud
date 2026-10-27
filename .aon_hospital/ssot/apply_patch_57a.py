# -*- coding: utf-8 -*-
import os

base_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. test_telegram_delivery_confirmation.py
f1 = os.path.join(base_dir, 'tests', 'test_telegram_delivery_confirmation.py')
with open(f1, 'r', encoding='utf-8') as f:
    text1 = f.read()

text1 = text1.replace('def test_telegram_async_delivery_success_confirms_marker():', 'def test_telegram_async_delivery_success_confirms_marker(monkeypatch):', 1)
text1 = text1.replace('        sched.notifier = mock_notifier', '        monkeypatch.setattr(sched, "notifier", mock_notifier)', 1)

text1 = text1.replace('def test_telegram_async_delivery_exception_leaves_marker_unconfirmed_and_increments_fail_count():', 'def test_telegram_async_delivery_exception_leaves_marker_unconfirmed_and_increments_fail_count(monkeypatch):', 1)
text1 = text1.replace('        sched.notifier = mock_notifier', '        monkeypatch.setattr(sched, "notifier", mock_notifier)', 1)

text1 = text1.replace('def test_telegram_async_delivery_timeout_leaves_marker_unconfirmed():', 'def test_telegram_async_delivery_timeout_leaves_marker_unconfirmed(monkeypatch):', 1)
text1 = text1.replace('        sched.notifier = mock_notifier', '        monkeypatch.setattr(sched, "notifier", mock_notifier)', 1)

text1 = text1.replace('def test_telegram_loop_unavailable_logs_critical_and_returns_false(caplog):', 'def test_telegram_loop_unavailable_logs_critical_and_returns_false(caplog, monkeypatch):', 1)
text1 = text1.replace('    sched.notifier = mock_notifier', '    monkeypatch.setattr(sched, "notifier", mock_notifier)', 1)

text1 = text1.replace('def test_telegram_same_thread_self_deadlock_prevented_and_increments_fail_count(caplog):', 'def test_telegram_same_thread_self_deadlock_prevented_and_increments_fail_count(caplog, monkeypatch):', 1)
text1 = text1.replace('    sched.notifier = mock_notifier', '    monkeypatch.setattr(sched, "notifier", mock_notifier)', 1)

with open(f1, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text1)

# 2. test_telegram_fail_counter.py
f2 = os.path.join(base_dir, 'tests', 'test_telegram_fail_counter.py')
with open(f2, 'r', encoding='utf-8') as f:
    text2 = f.read()

text2 = text2.replace('def test_telegram_fallback_critical_logging_and_fail_counter(caplog):', 'def test_telegram_fallback_critical_logging_and_fail_counter(caplog, monkeypatch):', 1)
text2 = text2.replace('    sched.notifier = fake_bad_notifier', '    monkeypatch.setattr(sched, "notifier", fake_bad_notifier)', 1)
text2 = text2.replace('    sched.notifier = fake_good_notifier', '    monkeypatch.setattr(sched, "notifier", fake_good_notifier)', 1)

with open(f2, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text2)

# 3. test_telegram_timeout_strike.py
f3 = os.path.join(base_dir, 'tests', 'test_telegram_timeout_strike.py')
with open(f3, 'r', encoding='utf-8') as f:
    text3 = f.read()

text3 = text3.replace('def test_telegram_timeout_counter_and_consecutive_3_strike_throttled_critical(caplog):', 'def test_telegram_timeout_counter_and_consecutive_3_strike_throttled_critical(caplog, monkeypatch):', 1)
text3 = text3.replace('        sched.notifier = mock_notifier', '        monkeypatch.setattr(sched, "notifier", mock_notifier)', 1)

text3 = text3.replace('def test_telegram_success_resets_timeout_counter():', 'def test_telegram_success_resets_timeout_counter(monkeypatch):', 1)
text3 = text3.replace('        sched.notifier = mock_notifier', '        monkeypatch.setattr(sched, "notifier", mock_notifier)', 1)

with open(f3, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text3)

print("57-A patch applied successfully!")
