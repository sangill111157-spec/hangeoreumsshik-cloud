# -*- coding: utf-8 -*-
import os

base_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. test_emergency_out_of_band.py
f1 = os.path.join(base_dir, 'tests', 'test_emergency_out_of_band.py')
with open(f1, 'r', encoding='utf-8') as f:
    text1 = f.read()

text1 = text1.replace(
    'def test_telegram_timeout_strike_triggers_emergency_alert():',
    'def test_telegram_timeout_strike_triggers_emergency_alert(monkeypatch):',
    1
)
text1 = text1.replace(
    '        sched.notifier = mock_notifier',
    '        monkeypatch.setattr(sched, "notifier", mock_notifier)',
    1
)

text1 = text1.replace(
    'def test_telegram_fail_strike_triggers_emergency_alert():',
    'def test_telegram_fail_strike_triggers_emergency_alert(monkeypatch):',
    1
)
text1 = text1.replace(
    '    sched.notifier = fake_bad_notifier',
    '    monkeypatch.setattr(sched, "notifier", fake_bad_notifier)',
    1
)

with open(f1, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text1)

# 2. test_stop_loss_telegram_inline_cap.py
f2 = os.path.join(base_dir, 'tests', 'test_stop_loss_telegram_inline_cap.py')
with open(f2, 'r', encoding='utf-8') as f:
    text2 = f.read()

text2 = text2.replace(
    'def test_startup_suppressed_alert_does_not_consume_slot_via_counter_delta():',
    'def test_startup_suppressed_alert_does_not_consume_slot_via_counter_delta(monkeypatch):',
    1
)
text2 = text2.replace(
    '    sched.notifier = MagicMock()',
    '    monkeypatch.setattr(sched, "notifier", MagicMock())',
    1
)

with open(f2, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text2)

print("57-C patch applied successfully!")
