# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding='utf-8')
target_file = r"C:\trading\package\nvda_trading_system\backend\tests\test_stop_loss_priority_slot.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

new_test = '''

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

    mock_send = MagicMock(return_value=True)
    monkeypatch.setattr(sched, '_send_telegram', mock_send)

    # 1. 잠금 종목 설정 (리마인더 유발)
    monkeypatch.setattr(sched, '_stop_loss_locked_tickers', {
        "NVDA": "3-Strike test lock",
    })
    monkeypatch.setattr(sched, '_stop_loss_lock_daily_alert', {})

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

if 'test_startup_unsuppressed_reminder_with_concurrent_order_yields_inline_to_order' not in content:
    content += new_test
    with open(target_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("New test node added successfully!")
else:
    print("Already present")
