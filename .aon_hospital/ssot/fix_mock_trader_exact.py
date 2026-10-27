target = r"C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_all_jobs_mock.py"

with open(target, "r", encoding="utf-8") as f:
    c = f.read()

# test_job_stop_loss_monitor_mock 안의 get_auto_trader만 _mock_trader로
old_sl = """def test_job_stop_loss_monitor_mock(mock_scheduler):
    with patch('app.services.scheduler.fetch_account_state') as mock_fetch, \\
         patch('app.services.scheduler.get_auto_trader'):"""

new_sl = """def test_job_stop_loss_monitor_mock(mock_scheduler):
    with patch('app.services.scheduler.fetch_account_state') as mock_fetch, \\
         patch('app.services.scheduler.get_auto_trader'):"""

# test_job_us_market_heartbeat_mock은 mock_trader 복원
old_hb = """def test_job_us_market_heartbeat_mock(mock_scheduler):
    with patch('app.services.scheduler.get_auto_trader'):
        mock_trader.return_value.get_status.return_value = {'dry_run': True}"""

new_hb = """def test_job_us_market_heartbeat_mock(mock_scheduler):
    with patch('app.services.scheduler.get_auto_trader') as mock_trader:
        mock_trader.return_value.get_status.return_value = {'dry_run': True}"""

if old_hb in c:
    c = c.replace(old_hb, new_hb, 1)

with open(target, "w", encoding="utf-8") as f:
    f.write(c)

print("SUCCESS: adjusted heartbeat mock")
