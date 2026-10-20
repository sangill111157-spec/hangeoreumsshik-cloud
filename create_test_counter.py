# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

test_content = """# -*- coding: utf-8 -*-
import sys, os, pytest, logging
from unittest.mock import MagicMock, patch

os.environ.setdefault("KIS_APP_KEY", "test_app_key")
os.environ.setdefault("KIS_APP_SECRET", "test_app_secret")
os.environ.setdefault("SECRET_KEY", "test_secret_key_32_characters_minimum_len")

from app.services.scheduler import TradingScheduler

def test_telegram_fallback_critical_logging_and_fail_counter(caplog):
    sched = TradingScheduler(notifier_enabled=True)
    assert sched._telegram_fail_count == 0

    # 1. Notifier send_message 실패 유도
    fake_bad_notifier = MagicMock()
    async def bad_send(msg):
        raise ConnectionError("Telegram server unreachable")
    fake_bad_notifier.send_message = bad_send
    fake_bad_notifier.chat_id = "12345"

    sched.notifier = fake_bad_notifier
    sched._loop = None  # fallback 경로 강제

    with caplog.at_level(logging.CRITICAL):
        sched._send_telegram("Test message 1")
        assert sched._telegram_fail_count == 1
        assert "TELEGRAM_SYNC_FALLBACK" in caplog.text

        sched._send_telegram("Test message 2")
        assert sched._telegram_fail_count == 2
        assert "consecutive fails: 2" in caplog.text

    # 2. 성공 시 카운터 리셋
    fake_good_notifier = MagicMock()
    async def good_send(msg):
        return True
    fake_good_notifier.send_message = good_send
    fake_good_notifier.chat_id = "12345"
    sched.notifier = fake_good_notifier

    sched._send_telegram("Test message success")
    assert sched._telegram_fail_count == 0
"""

test_path = os.path.join(backend_dir, 'tests', 'test_telegram_fail_counter.py')
with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_content)
print(f"Created {test_path}")
