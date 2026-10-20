import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.scheduler import TradingScheduler


@pytest.mark.asyncio
async def test_scheduler_all_jobs_execution_with_mocks():
    """
    스케줄러에 등록된 모든 작업(잡)을 모의 객체로 감싸 1회씩 직접 실행하여,
    존재하지 않는 메서드 호출이나 속성 오류(AttributeError)가 없는지 검증한다.
    """
    sched = TradingScheduler(notifier_enabled=False)

    # 1. job_hourly_scan 모의 실행 (get_stock_scanner 및 run_scan)
    with patch("app.services.scheduler.get_stock_scanner") as mock_get_scanner, \
         patch("app.services.scheduler.get_auto_trader") as mock_trader_func:
        mock_scanner = MagicMock()
        mock_scan_res = MagicMock()
        mock_scan_res.final_candidates = []
        mock_scanner.run_scan = AsyncMock(return_value=mock_scan_res)
        mock_get_scanner.return_value = mock_scanner

        mock_trader = MagicMock()
        mock_trader.get_status = MagicMock(return_value={"dry_run": True})
        mock_trader_func.return_value = mock_trader

        assert sched.run_job_manually("hourly_scan") is True

    # 2. job_daily_analysis 모의 실행
    with patch("app.services.scheduler.get_auto_trader") as mock_trader_func:
        mock_trader = MagicMock()
        mock_trader.run_daily_analysis = MagicMock(return_value={"status": "completed"})
        mock_trader.get_status = MagicMock(return_value={"dry_run": True})
        mock_trader_func.return_value = mock_trader

        assert sched.run_job_manually("daily_analysis") is True

    # 3. job_stop_loss_monitor 모의 실행
    with patch("app.services.scheduler.get_auto_trader") as mock_trader_func, \
         patch("app.services.scheduler.fetch_account_state") as mock_fetch_acc:
        mock_trader = MagicMock()
        mock_trader.get_status = MagicMock(return_value={"dry_run": True})
        mock_trader_func.return_value = mock_trader

        mock_acc = MagicMock()
        mock_acc.positions_detail = []
        mock_fetch_acc.return_value = mock_acc

        assert sched.run_job_manually("stop_loss_monitor") is True

    # 4. job_weekly_report 모의 실행
    with patch("app.services.scheduler.get_auto_trader") as mock_trader_func:
        mock_trader = MagicMock()
        mock_trader.generate_weekly_summary = MagicMock(return_value={"report": "summary"})
        mock_trader.get_status = MagicMock(return_value={"dry_run": True})
        mock_trader_func.return_value = mock_trader

        assert sched.run_job_manually("weekly_report") is True

    # 5. job_us_market_heartbeat 모의 실행
    with patch.object(sched, "_send_telegram"):
        assert sched.run_job_manually("us_market_heartbeat") is True
