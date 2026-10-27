# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')
target_file = r"C:\trading\package\nvda_trading_system\backend\tests\test_stop_loss_priority_slot.py"

content = '''# -*- coding: utf-8 -*-
"""
[BACKLOG_21 / BACKLOG_39] 손절 주문 알림의 잠금 종목 일일 리마인더 인라인 슬롯 선점 단위 테스트:
- 동일 사이클 내에서 잠금 종목 리마인더와 손절 매도 주문 알림이 동시 발생할 경우,
  손절 주문 알림이 인라인 슬롯(CAP=1)을 최우선 선점하고, 리마인더는 요약 알림으로 안전 편입됨을 단정.
"""
import time
from unittest.mock import MagicMock, patch
from app.services.scheduler import (
    get_scheduler,
    ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER,
)


def _wait_for_threads(timeout: float = 2.0):
    """비블로킹 백그라운드 요약 발송 스레드가 완료될 때까지 확실히 대기"""
    import threading
    for t in list(threading.enumerate()):
        if t.name == "stop_loss_summary_flush":
            t.join(timeout=timeout)
    time.sleep(0.05)


def test_order_alert_preempts_locked_reminder_inline_slot(monkeypatch):
    """[BACKLOG_21 / BACKLOG_39] 동일 사이클 리마인더·주문 알림 동시 발생 시 인라인 슬롯 선점 순위 검증:
    1. 잠금 종목 리마인더(NVDA)와 손절 매도 주문(TSLA)을 단일 사이클에 동시 유발.
    2. 인라인 개별 알림 1건(first_call_msg)은 반드시 긴급 손절 주문 알림이어야 함.
    3. 잠금 종목 리마인더는 인라인 슬롯을 주문에 양보하고 사이클 요약 알림 내부로 편입되어야 함.
    """
    sched = get_scheduler()
    mock_send = MagicMock(return_value=True)
    monkeypatch.setattr(sched, '_send_telegram', mock_send)

    # 1. 잠금 종목 설정 (리마인더 1건 유발)
    monkeypatch.setattr(sched, '_stop_loss_locked_tickers', {
        "NVDA": "3-Strike test lock",
    })
    monkeypatch.setattr(sched, '_stop_loss_lock_daily_alert', {})

    # 2. 보유 종목 설정 (손절 주문 1건 유발)
    holdings = [
        {"_normalized_symbol": "TSLA", "symbol": "TSLA", "quantity": 10, "avg_price": 200.0}
    ]

    class DummyAccountState:
        positions_detail = holdings

    mock_trader = MagicMock()
    mock_trader.get_status.return_value = {"dry_run": False}
    mock_trader._get_current_price.return_value = 180.0  # -10% 하락 -> 손절선(-3%) 미달로 주문 트리거
    mock_trader.execute_trade.return_value = {
        "success": True,
        "order_state": "ORDER_ACCEPTED",
        "order_id": "ORD_TEST_999",
    }

    with patch("app.services.scheduler.get_auto_trader", return_value=mock_trader), \
         patch("app.services.scheduler.fetch_account_state", return_value=DummyAccountState()), \
         patch("app.services.scheduler.order_holdings_for_scan", return_value=(holdings, 0)), \
         patch.object(sched, "_save_stop_loss_state"), \
         patch("app.services.scheduler.is_market_open_for_ticker", return_value=True), \
         patch("app.services.scheduler.get_session_date_for_ticker", return_value="2026-09-12"):

        sched.job_stop_loss_monitor()

    _wait_for_threads()

    # 인라인 주문 알림 1건 + 리마인더 포함 요약 알림 1건 = 총 2건 호출 단정
    assert mock_send.call_count == 2, f"Expected 2 telegram calls (1 inline order + 1 summary), got {mock_send.call_count}"

    first_call_msg = mock_send.call_args_list[0][0][0]
    second_call_msg = mock_send.call_args_list[1][0][0]

    # [선점 검증] 인라인 개별 알림 1건은 손절 주문 접수 알림이어야 하고 리마인더 태그가 없어야 함
    assert "긴급 손절 주문 접수 완료" in first_call_msg, f"First call should be order alert, got: {first_call_msg}"
    assert "TSLA" in first_call_msg
    assert ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER not in first_call_msg

    # [편입 검증] 리마인더는 요약 알림 내부로 편입되어 발송되어야 함
    assert "손절 감시 사이클 요약 알림" in second_call_msg, f"Second call should be summary alert, got: {second_call_msg}"
    assert ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER in second_call_msg
    assert "NVDA" in second_call_msg


def test_startup_unsuppressed_reminder_with_concurrent_order_yields_inline_to_order(monkeypatch):
    """[BACKLOG_21 / 차단 10] 기동 억제 창 내부·억제 미발생·ORDER 동시 조건에서 ORDER 인라인 슬롯 확보 단정:
    1. 기동 억제 창 내에서 잠금 리마인더가 발생했으나 억제 카운터가 증가하지 않는 조건(억제 미발생) 모의.
    2. 리마인더는 인라인 슬롯(CAP=1)을 소비하지 않고 지연 큐로 양보.
    3. 동일 사이클의 긴급 손절 주문(ORDER) 알림이 인라인 개별 알림으로 즉시 발송됨을 검증.
    """
    sched = get_scheduler()
    sched._startup_ts = time.time()
    sched._startup_window_sec = 60.0
    sched._startup_suppressed_count = 0
    monkeypatch.setattr(sched, "_is_restart_suppressed_message", lambda msg: False)

    mock_send = MagicMock(return_value=True)
    monkeypatch.setattr(sched, "_send_telegram", mock_send)

    # 1. 잠금 종목 설정 (리마인더 유발)
    monkeypatch.setattr(sched, "_stop_loss_locked_tickers", {
        "NVDA": "3-Strike test lock",
    })
    monkeypatch.setattr(sched, "_stop_loss_lock_daily_alert", {})

    # 2. 보유 종목 손절 주문 설정
    holdings = [
        {"_normalized_symbol": "TSLA", "symbol": "TSLA", "quantity": 10, "avg_price": 200.0}
    ]

    class DummyAccountState:
        positions_detail = holdings

    mock_trader = MagicMock()
    mock_trader.get_status.return_value = {"dry_run": False}
    mock_trader._get_current_price.return_value = 180.0
    mock_trader.execute_trade.return_value = {
        "success": True,
        "order_state": "ORDER_ACCEPTED",
        "order_id": "ORD_STARTUP_UNSUPP_1",
    }

    with patch("app.services.scheduler.get_auto_trader", return_value=mock_trader), \
         patch("app.services.scheduler.fetch_account_state", return_value=DummyAccountState()), \
         patch("app.services.scheduler.order_holdings_for_scan", return_value=(holdings, 0)), \
         patch.object(sched, "_save_stop_loss_state"), \
         patch("app.services.scheduler.is_market_open_for_ticker", return_value=True), \
         patch("app.services.scheduler.get_session_date_for_ticker", return_value="2026-09-12"):

        sched.job_stop_loss_monitor()

    _wait_for_threads()

    # 인라인 주문 알림 1건 + 지연 요약 알림 1건 = 총 2건 호출
    assert mock_send.call_count == 2, f"Expected 2 telegram calls, got {mock_send.call_count}"
    first_call_msg = mock_send.call_args_list[0][0][0]
    second_call_msg = mock_send.call_args_list[1][0][0]

    # ORDER 알림이 인라인을 확보하였음을 단정
    assert "긴급 손절 주문 접수 완료" in first_call_msg
    assert "TSLA" in first_call_msg
    assert ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER not in first_call_msg

    # 리마인더는 요약 알림으로 편입되었음을 단정
    assert "손절 감시 사이클 요약 알림" in second_call_msg
    assert ALERT_TAG_LOCKED_TICKER_DAILY_REMINDER in second_call_msg
    assert "NVDA" in second_call_msg
'''

with open(target_file, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("test_stop_loss_priority_slot.py rewritten successfully!")
