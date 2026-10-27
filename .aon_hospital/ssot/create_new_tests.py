# 1. tests/test_scheduler_hourly_scan.py
test_scan_content = '''from unittest.mock import MagicMock, patch
from app.services.stock_scanner import StockScanner, ScanResult
from app.services.scheduler import TradingScheduler

def test_stock_scanner_scan_watchlist_method_exists():
    scanner = StockScanner()
    with patch.object(scanner, "run_scan") as mock_run:
        mock_result = MagicMock(spec=ScanResult)
        mock_result.final_candidates = [{"ticker": "NVDA"}]
        mock_result.total_scanned = 10
        mock_result.primary_passed = 3
        
        async def fake_scan(market=None):
            return mock_result
            
        mock_run.side_effect = fake_scan
        
        res = scanner.scan_watchlist(market="US")
        assert "candidates" in res
        assert len(res["candidates"]) == 1
        assert res["total_scanned"] == 10

def test_job_hourly_scan_execution():
    scheduler = TradingScheduler()
    with patch("app.services.scheduler.get_stock_scanner") as mock_get_scanner, \
         patch.object(scheduler, "_send_telegram") as mock_send:
        mock_scanner = MagicMock()
        mock_scanner.scan_watchlist.return_value = {"candidates": [{"ticker": "NVDA"}]}
        mock_get_scanner.return_value = mock_scanner
        
        scheduler.job_hourly_scan()
        assert mock_scanner.scan_watchlist.called
        assert mock_send.called
'''

# 2. tests/test_telegram_html_formatting.py
test_telegram_content = '''from app.services.telegram_notifier import (
    TelegramMessage,
    format_telegram_alert,
    TelegramNotifier,
)

def test_telegram_message_default_html_parse_mode():
    msg = TelegramMessage(chat_id="12345", text="<b>test</b>")
    assert msg.parse_mode == "HTML"

def test_format_telegram_alert_escapes_special_chars():
    alert = format_telegram_alert(
        level="긴급",
        is_paper=True,
        title="계좌 조회 실패 <test> & [error]",
        impact="손절 감시가 3분째 멈춤 *critical*",
        action="HTS 확인 필요_manual",
        tech_info="ACCOUNT_STATE_FAIL: 'NoneType' & <Error>"
    )
    assert "[긴급][모의]" in alert
    assert "&lt;test&gt;" in alert
    assert "&amp;" in alert
    assert "<b>영향:</b>" in alert
    assert "<code>" in alert

def test_telegram_notifier_tracks_failure():
    notifier = TelegramNotifier(bot_token="fake", chat_id="fake")
    assert notifier.failed_send_count == 0
    assert notifier.last_send_error is None
'''

# 3. tests/test_broker_event_loop_resilience.py
test_broker_content = '''import pytest
import asyncio
from app.services.kis_broker import KisBroker

@pytest.mark.asyncio
async def test_kis_broker_client_recreated_on_different_loop():
    broker = KisBroker()
    
    # Loop 1
    client1 = await broker._get_http_client()
    assert client1 is not None
    assert broker._client_loop is asyncio.get_running_loop()
    
    # Run in a separate thread with a new closed loop
    def run_in_separate_loop():
        new_loop = asyncio.new_event_loop()
        try:
            client2 = new_loop.run_until_complete(broker._get_http_client())
            assert client2 is not None
        finally:
            new_loop.close()
            
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        pool.submit(run_in_separate_loop).result()
        
    # Back to Loop 1: client should be refreshed because previous loop was closed
    client3 = await broker._get_http_client()
    assert client3 is not None
    assert broker._client_loop is asyncio.get_running_loop()
'''

with open(r"C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_hourly_scan.py", "w", encoding="utf-8") as f:
    f.write(test_scan_content)

with open(r"C:\trading\package\nvda_trading_system\backend\tests\test_telegram_html_formatting.py", "w", encoding="utf-8") as f:
    f.write(test_telegram_content)

with open(r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_event_loop_resilience.py", "w", encoding="utf-8") as f:
    f.write(test_broker_content)

print("Created 3 new test files successfully")
