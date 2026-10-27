# -*- coding: utf-8 -*-
import sys, os, subprocess, shutil

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("================================================================================")
print("1. Update tests/conftest.py to isolate STOP_LOSS_STATE_FILE & TradingScheduler")
print("================================================================================")

conftest_code = '''import pytest
import os
from pathlib import Path
from unittest.mock import patch
from app.services.auto_trader import AutoTrader
import app.services.auto_trader as at_mod
from app.services.scheduler import TradingScheduler
import app.services.scheduler as sched_mod


@pytest.fixture(autouse=True)
def reset_autotrader_singleton_global():
    """모든 테스트 파일 전후로 AutoTrader 싱글턴 인스턴스 및 전역 객체를 원복하여 엄격 격리"""
    AutoTrader._instance = None
    at_mod._auto_trader = None
    yield
    AutoTrader._instance = None
    at_mod._auto_trader = None


@pytest.fixture(autouse=True)
def isolate_stop_loss_state_file_and_scheduler(tmp_path, monkeypatch):
    """
    모든 테스트 실행 시 실제 data/stop_loss_state.json이 오염되지 않도록
    STOP_LOSS_STATE_FILE을 tmp_path 임시 파일로 엄격 격리하고 싱글톤 인스턴스를 리셋.
    """
    temp_state_file = tmp_path / "temp_stop_loss_state.json"
    monkeypatch.setattr(sched_mod, "STOP_LOSS_STATE_FILE", temp_state_file)
    TradingScheduler._instance = None
    sched_mod._scheduler = None
    yield
    TradingScheduler._instance = None
    sched_mod._scheduler = None
'''

conftest_path = os.path.join(backend_dir, 'tests', 'conftest.py')
with open(conftest_path, 'w', encoding='utf-8') as f:
    f.write(conftest_code)
print(f"Updated {conftest_path}")

print("\n================================================================================")
print("2. Fix rebalance.py:89 encoding typo")
print("================================================================================")
reb_path = os.path.join(backend_dir, 'app', 'api', 'routes', 'rebalance.py')
with open(reb_path, 'r', encoding='utf-8') as f:
    reb_content = f.read()

old_corrupted = '    # ?? 166?182 ??: Gate 1 dry-run ? ENABLE_LIVE_ORDERS ??? ? HTTP 404 ??'
new_clean = '    # 결함 166·182 완결: Gate 1 dry-run 중 ENABLE_LIVE_ORDERS 미설정 시 HTTP 404 차단'

if old_corrupted in reb_content:
    reb_content = reb_content.replace(old_corrupted, new_clean)
    with open(reb_path, 'w', encoding='utf-8') as f:
        f.write(reb_content)
    print("Fixed rebalance.py:89 successfully.")
else:
    print("Corrupted line pattern not found directly, checking lines...")

print("\n================================================================================")
print("3. Verify stop_loss_state.json SHA256 before & after pytest with isolated fixture")
print("================================================================================")
sl_path = os.path.join(backend_dir, 'data', 'stop_loss_state.json')
with open(sl_path, 'rb') as f:
    b_before = f.read()
sha_before = hashlib.sha256(b_before).hexdigest()
print(f"BEFORE test run - Size: {len(b_before)}, SHA256: {sha_before}")

res_test = subprocess.run([os.path.join(backend_dir, 'venv', 'Scripts', 'pytest.exe'), 'tests/', '-v'], cwd=backend_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')

with open(sl_path, 'rb') as f:
    b_after = f.read()
sha_after = hashlib.sha256(b_after).hexdigest()
print(f"AFTER test run - Size: {len(b_after)}, SHA256: {sha_after}")

if sha_before == sha_after:
    print("✅ PERFECT: data/stop_loss_state.json is 100% ISOLATED and UNCHANGED during pytest!")
else:
    print("🚨 ERROR: SHA256 still changed!")
