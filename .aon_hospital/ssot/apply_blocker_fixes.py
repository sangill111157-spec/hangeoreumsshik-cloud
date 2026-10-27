import json
import re

# 1. app/services/scheduler.py 수정: _save_stop_loss_state에서 if exists else rename 제거하고 os.replace 단일화
sched_path = r'C:\trading\package\nvda_trading_system\backend\app\services\scheduler.py'
with open(sched_path, 'r', encoding='utf-8') as f:
    sched_text = f.read()

old_replace = """            if os.path.exists(state_file):
                os.replace(temp_file, state_file)
            else:
                os.rename(temp_file, state_file)"""

new_replace = """            os.replace(temp_file, state_file)"""

if old_replace in sched_text:
    sched_text = sched_text.replace(old_replace, new_replace, 1)
    print("Successfully simplified _save_stop_loss_state to single os.replace!")
else:
    old_replace_crlf = old_replace.replace('\n', '\r\n')
    new_replace_crlf = new_replace.replace('\n', '\r\n')
    if old_replace_crlf in sched_text:
        sched_text = sched_text.replace(old_replace_crlf, new_replace_crlf, 1)
        print("Successfully simplified _save_stop_loss_state (CRLF) to single os.replace!")
    else:
        print("Warning: old_replace pattern not found in scheduler.py")

with open(sched_path, 'w', encoding='utf-8') as f:
    f.write(sched_text)

# 2. tests/test_scheduler_sizing.py 수정
test_path = r'C:\trading\package\nvda_trading_system\backend\tests\test_scheduler_sizing.py'
with open(test_path, 'r', encoding='utf-8') as f:
    test_text = f.read()

# 2-1: test_stop_loss_dry_run_does_not_block_subsequent_live_run 시각 고정 + 리터럴 단정
old_test1 = '''def test_stop_loss_dry_run_does_not_block_subsequent_live_run():
    """dry-run 모드에서는 stop_loss_fired에 세션 마커를 남기지 않아 이후 LIVE 실행이 차단되지 않는다."""
    sched = get_scheduler()
    sched._stop_loss_fired = {}

    mock_trader = MagicMock()
    mock_trader._get_current_price.return_value = 85.0
    mock_trader.execute_trade.return_value = {"success": True}

    mock_state = make_test_account_state("NVDA", shares=10, avg_price=100.0, current_price=85.0)

    with patch("app.services.scheduler.fetch_account_state", return_value=mock_state), \\
         patch("app.services.scheduler.get_auto_trader", return_value=mock_trader), \\
         patch.object(sched, "_send_telegram"), \\
         patch("app.services.scheduler.is_market_open_for_ticker", return_value=True):

        # 1차: dry-run 실행
        mock_trader.get_status.return_value = {"dry_run": True}
        sched.job_stop_loss_monitor()
        assert "NVDA" not in sched._stop_loss_fired  # dry-run은 마커를 남기지 않음!

        # 2차: LIVE 모드로 전환 후 실행 -> 정상 발사되어야 함
        mock_trader.get_status.return_value = {"dry_run": False}
        sched.job_stop_loss_monitor()
        assert "NVDA" in sched._stop_loss_fired
        assert mock_trader.execute_trade.call_count == 2'''

new_test1 = '''def test_stop_loss_dry_run_does_not_block_subsequent_live_run():
    """dry-run 모드에서는 stop_loss_fired에 세션 마커를 남기지 않아 이후 LIVE 실행이 차단되지 않는다."""
    sched = get_scheduler()
    sched._stop_loss_fired = {}

    mock_trader = MagicMock()
    mock_trader._get_current_price.return_value = 85.0
    mock_trader.execute_trade.return_value = {"success": True}

    mock_state = make_test_account_state("NVDA", shares=10, avg_price=100.0, current_price=85.0)

    fixed_t = datetime(2026, 8, 28, 14, 0, 0, tzinfo=timezone.utc)
    with patch("app.services.scheduler.fetch_account_state", return_value=mock_state), \\
         patch("app.services.scheduler.get_auto_trader", return_value=mock_trader), \\
         patch.object(sched, "_send_telegram"), \\
         patch("app.services.scheduler.is_market_open_for_ticker", return_value=True), \\
         patch("app.services.scheduler.datetime") as mock_dt:

        mock_dt.now.side_effect = lambda tz=None: fixed_t.astimezone(tz) if tz else fixed_t

        # 1차: dry-run 실행
        mock_trader.get_status.return_value = {"dry_run": True}
        sched.job_stop_loss_monitor()
        assert "NVDA" not in sched._stop_loss_fired  # dry-run은 마커를 남기지 않음!

        # 2차: LIVE 모드로 전환 후 실행 -> 정상 발사되어야 함 (고정 시각 대비 리터럴 일자 단정)
        mock_trader.get_status.return_value = {"dry_run": False}
        sched.job_stop_loss_monitor()
        assert sched._stop_loss_fired.get("NVDA") == "2026-08-28"
        assert mock_trader.execute_trade.call_count == 2'''

if old_test1 in test_text:
    test_text = test_text.replace(old_test1, new_test1, 1)
    print("Replaced test_stop_loss_dry_run_does_not_block_subsequent_live_run successfully!")
else:
    old_test1_crlf = old_test1.replace('\n', '\r\n')
    new_test1_crlf = new_test1.replace('\n', '\r\n')
    if old_test1_crlf in test_text:
        test_text = test_text.replace(old_test1_crlf, new_test1_crlf, 1)
        print("Replaced test_stop_loss_dry_run_does_not_block_subsequent_live_run (CRLF) successfully!")
    else:
        print("Warning: old_test1 pattern not found directly!")

# 2-2: test_stop_loss_dry_run_3_ticks_alerts_only_once_and_keeps_fired_empty 시각 고정 + 리터럴 단정 (정규식 삭제)
old_test2 = '''def test_stop_loss_dry_run_3_ticks_alerts_only_once_and_keeps_fired_empty():
    """dry-run 모드 3회 연속 tick: Tier 1 알림 1회만 발송, fired 마커는 항상 빈 상태 유지."""
    sched = get_scheduler()
    sched._stop_loss_fired = {}
    sched._stop_loss_alerted = {}

    mock_trader = MagicMock()
    mock_trader.get_status.return_value = {"dry_run": True}
    mock_trader._get_current_price.return_value = 85.0
    mock_trader.execute_trade.return_value = {"success": True, "dry_run": True}

    mock_state = make_test_account_state("NVDA", shares=10, avg_price=100.0, current_price=85.0)

    with patch("app.services.scheduler.fetch_account_state", return_value=mock_state), \\
         patch("app.services.scheduler.get_auto_trader", return_value=mock_trader), \\
         patch.object(sched, "_send_telegram") as mock_tg, \\
         patch("app.services.scheduler.is_market_open_for_ticker", return_value=True):

        # 3회 연속 실행
        for _ in range(3):
            sched.job_stop_loss_monitor()

        # Tier 1 경보는 첫 번째 tick에서 1회만 발송되어야 함
        # 고정 시각 대비 리터럴 일자 단정 (프로덕션 헬퍼 자기참조 단정 방지)
        today_session = sched._stop_loss_alerted.get("NVDA")
        assert today_session == "2026-09-07"
        assert re.match(r"^\\d{4}-\\d{2}-\\d{2}$", today_session)
        assert mock_tg.call_count == 1
        assert "NVDA" not in sched._stop_loss_fired'''

new_test2 = '''def test_stop_loss_dry_run_3_ticks_alerts_only_once_and_keeps_fired_empty():
    """dry-run 모드 3회 연속 tick: Tier 1 알림 1회만 발송, fired 마커는 항상 빈 상태 유지."""
    sched = get_scheduler()
    sched._stop_loss_fired = {}
    sched._stop_loss_alerted = {}

    mock_trader = MagicMock()
    mock_trader.get_status.return_value = {"dry_run": True}
    mock_trader._get_current_price.return_value = 85.0
    mock_trader.execute_trade.return_value = {"success": True, "dry_run": True}

    mock_state = make_test_account_state("NVDA", shares=10, avg_price=100.0, current_price=85.0)

    fixed_t = datetime(2026, 8, 28, 14, 0, 0, tzinfo=timezone.utc)
    with patch("app.services.scheduler.fetch_account_state", return_value=mock_state), \\
         patch("app.services.scheduler.get_auto_trader", return_value=mock_trader), \\
         patch.object(sched, "_send_telegram") as mock_tg, \\
         patch("app.services.scheduler.is_market_open_for_ticker", return_value=True), \\
         patch("app.services.scheduler.datetime") as mock_dt:

        mock_dt.now.side_effect = lambda tz=None: fixed_t.astimezone(tz) if tz else fixed_t

        # 3회 연속 실행
        for _ in range(3):
            sched.job_stop_loss_monitor()

        # Tier 1 경보는 첫 번째 tick에서 1회만 발송되어야 함 (고정 시각 대비 리터럴 일자 단정)
        # 프로덕션 헬퍼 자기참조 방지 및 자정 롤오버 내성 보장을 위한 2026-08-28 리터럴 일치 단정
        assert sched._stop_loss_alerted.get("NVDA") == "2026-08-28"
        assert mock_tg.call_count == 1
        assert "NVDA" not in sched._stop_loss_fired'''

if old_test2 in test_text:
    test_text = test_text.replace(old_test2, new_test2, 1)
    print("Replaced test_stop_loss_dry_run_3_ticks_alerts_only_once_and_keeps_fired_empty successfully!")
else:
    old_test2_crlf = old_test2.replace('\n', '\r\n')
    new_test2_crlf = new_test2.replace('\n', '\r\n')
    if old_test2_crlf in test_text:
        test_text = test_text.replace(old_test2_crlf, new_test2_crlf, 1)
        print("Replaced test_stop_loss_dry_run_3_ticks_alerts_only_once_and_keeps_fired_empty (CRLF) successfully!")
    else:
        print("Warning: old_test2 pattern not found directly!")

with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_text)

print("Finished applying blocker fixes!")
