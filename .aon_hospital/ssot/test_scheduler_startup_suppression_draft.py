# -*- coding: utf-8 -*-
import time
import asyncio
import threading
import logging
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.scheduler import get_scheduler

@pytest.fixture(autouse=True)
def isolate_test_env(monkeypatch):
    monkeypatch.setenv("KIS_APP_KEY", "test_app_key")
    monkeypatch.setenv("KIS_APP_SECRET", "test_app_secret")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key_32_characters_minimum_len")

class BackgroundLoop:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        self.thread.start()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=2.0)

def test_startup_burst_suppression_suppresses_blacklisted_alerts():
    """[백로그 2 테스트 1: 재기동 창 내 블랙리스트 알림 억제]
    기동 후 60초 창 내에서 블랙리스트에 해당하는 재기동성 알림(잠금 리마인더, KR 감시불가 등)이
    발생하면 전송을 억제(False 반환)하고 fail_count는 증가시키지 않으며 억제 카운터가 증가한다.
    """
    bg = BackgroundLoop()
    bg.start()
    try:
        sched = get_scheduler()
        sched._loop = bg.loop
        sched.notifier_enabled = True
        sched._startup_ts = time.time()
        sched._startup_window_sec = 60.0
        sched._startup_suppressed_count = 0
        sched._telegram_fail_count = 0

        mock_notifier = MagicMock()
        mock_notifier.send_message = AsyncMock(return_value=True)
        mock_notifier.chat_id = "12345"
        sched.notifier = mock_notifier

        # 1. 잠금 리마인더 알림 시도 (블랙리스트)
        msg1 = "🚨🚨 *[긴급 손절 잠금 일일 리마인더]* NVDA 종목이 시스템 오류로 손절 잠금 상태입니다!"
        res1 = sched._send_telegram(msg1)
        assert res1 is False
        assert sched._startup_suppressed_count == 1
        assert sched._telegram_fail_count == 0

        # 2. KR 종목 미지원 알림 시도 (블랙리스트)
        msg2 = "🚨 *[국내주식 손절 감시 불가]* 373220 종목은 해외주식 잔고 기반 손절 감시 대상이 아닙니다."
        res2 = sched._send_telegram(msg2)
        assert res2 is False
        assert sched._startup_suppressed_count == 2
        assert sched._telegram_fail_count == 0

        # 텔레그램 실제 전송은 0건이어야 함
        assert mock_notifier.send_message.call_count == 0
    finally:
        bg.stop()

def test_startup_window_expiry_restores_normal_alerts_and_logs_summary(caplog):
    """[백로그 2 테스트 2: 억제 창 만료 후 정상 발신 복귀 및 종료 요약 로그]
    기동 후 60초 창이 경과한 뒤에는 블랙리스트 알림도 정상적으로 전송(True 반환)되며,
    창 종료 시 억제된 건수에 대한 1회 요약 로그가 기록된다.
    """
    bg = BackgroundLoop()
    bg.start()
    try:
        sched = get_scheduler()
        sched._loop = bg.loop
        sched.notifier_enabled = True
        # 기동 창 만료 시뮬레이션 (현재 시각 기준 65초 전 기동)
        sched._startup_ts = time.time() - 65.0
        sched._startup_window_sec = 60.0
        sched._startup_suppressed_count = 5
        sched._startup_summary_logged = False

        mock_notifier = MagicMock()
        mock_notifier.send_message = AsyncMock(return_value=True)
        mock_notifier.chat_id = "12345"
        sched.notifier = mock_notifier

        with caplog.at_level(logging.INFO):
            msg = "🚨🚨 *[긴급 손절 잠금 일일 리마인더]* NVDA 종목이 시스템 오류로 손절 잠금 상태입니다!"
            res = sched._send_telegram(msg)

        assert res is True
        assert mock_notifier.send_message.call_count == 1
        assert sched._startup_summary_logged is True
        # 창 종료 요약 로그 검증
        assert any("STARTUP_SUPPRESSION_WINDOW_ENDED" in record.message for record in caplog.records)
    finally:
        bg.stop()

def test_startup_window_does_not_suppress_real_stop_loss_trigger():
    """[백로그 2 테스트 3: 억제 창 활성 중에도 실제 손절 트리거 즉시 발신]
    기동 후 60초 억제 창이 활성화되어 있는 동안에도, 실제 손절 주문/체결/트리거 CRITICAL 알림은
    블랙리스트에 해당하지 않으므로 억제되지 않고 즉시 발송된다.
    """
    bg = BackgroundLoop()
    bg.start()
    try:
        sched = get_scheduler()
        sched._loop = bg.loop
        sched.notifier_enabled = True
        # 억제 창 내부 (기동 직후)
        sched._startup_ts = time.time()
        sched._startup_window_sec = 60.0
        sched._startup_suppressed_count = 0

        mock_notifier = MagicMock()
        mock_notifier.send_message = AsyncMock(return_value=True)
        mock_notifier.chat_id = "12345"
        sched.notifier = mock_notifier

        # 실제 손절 주문 실행 알림 (블랙리스트 비대상)
        real_trigger_msg = "🚨🚨 *[긴급 손절 주문 실행]* NVDA 10주 시장가 매도 주문이 접수되었습니다! 현재가: $180.0, 평단: $200.0 (-10.0%)"
        res = sched._send_telegram(real_trigger_msg)

        assert res is True
        assert mock_notifier.send_message.call_count == 1
        assert sched._startup_suppressed_count == 0  # 억제 카운터 미증가
    finally:
        bg.stop()
