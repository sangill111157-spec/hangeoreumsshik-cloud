# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

test_content = """# -*- coding: utf-8 -*-
import sys, os, time, json, pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

os.environ.setdefault("KIS_APP_KEY", "test_app_key")
os.environ.setdefault("KIS_APP_SECRET", "test_app_secret")
os.environ.setdefault("SECRET_KEY", "test_secret_key_32_characters_minimum_len")

from app.services.scheduler import TradingScheduler, STOP_LOSS_STATE_FILE

def test_stop_loss_disabled_periodic_alert_and_persistence(tmp_path):
    state_file = Path(STOP_LOSS_STATE_FILE)
    backup_file = None
    if state_file.exists():
        backup_data = state_file.read_bytes()
        backup_file = True

    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w', encoding='utf-8') as f:
            f.write("{invalid_json_corrupted_content: 123,")

        sched = TradingScheduler(notifier_enabled=True)
        mock_send = MagicMock()
        sched._send_telegram = mock_send

        assert sched._stop_loss_disabled is True
        initial_alert_time = sched._stop_loss_disabled_last_alert
        assert initial_alert_time > 0

        # 10분 경과 -> 재알림 없음
        sched._stop_loss_disabled_last_alert = time.time() - 600.0
        sched.job_stop_loss_monitor()
        assert mock_send.call_count == 0

        # 3601초 경과 -> 1시간 재알림 전송
        sched._stop_loss_disabled_last_alert = time.time() - 3601.0
        sched.job_stop_loss_monitor()
        assert mock_send.call_count == 1
        assert "1시간 재알림" in mock_send.call_args[0][0]

    finally:
        if backup_file:
            state_file.write_bytes(backup_data)
        elif state_file.exists():
            state_file.unlink()

def test_health_check_reflects_stop_loss_disabled():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.services.scheduler import get_scheduler

    c = TestClient(app)
    sched = get_scheduler()
    sched._stop_loss_disabled = True

    res = c.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["stop_loss_disabled"] is True
    assert data["status"] == "degraded"

    sched._stop_loss_disabled = False
    sched._stop_loss_locked_tickers = {}
    res_ok = c.get("/health")
    assert res_ok.status_code == 200
    assert res_ok.json()["stop_loss_disabled"] is False
"""

test_path = os.path.join(backend_dir, 'tests', 'test_stop_loss_disabled_alert.py')
with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_content)
print(f"Created {test_path}")
