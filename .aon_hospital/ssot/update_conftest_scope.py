# -*- coding: utf-8 -*-
import os

backend_dir = r"C:\trading\package\nvda_trading_system\backend"
os.chdir(backend_dir)

with open("tests/conftest.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find def wire_master_signal_stubs_for_regression
idx = -1
for i, line in enumerate(lines):
    if "def wire_master_signal_stubs_for_regression" in line:
        idx = i
        break

assert idx != -1, "fixture not found"

# Remove from @pytest.fixture(autouse=True) before idx
start_idx = idx - 1
while start_idx > 0 and "@pytest.fixture" not in lines[start_idx]:
    start_idx -= 1

conftest_prefix = "".join(lines[:start_idx])

fixture_code = '''@pytest.fixture(autouse=True)
def wire_master_signal_stubs_for_regression(request, monkeypatch):
    """[백로그 19] 자본 6대 케이스 회귀(test_six_capital_cases_regression.py) 스텁 배선:
    오프라인 테스트 환경에서 시세/신호 미연결로 인한 사이징 실패를 방지하기 위해,
    tests/fixtures/master_signal_stubs.py의 SSOT 기반 modules 스텁 및 시세를 안전하게 배선한다.
    (자본 6대 케이스 테스트 파일 외에는 프로덕션 fail-closed 및 헬스체크 동작을 엄격히 보존함)
    """
    if "test_six_capital_cases_regression" not in str(request.node.fspath):
        yield
        return

    from tests.fixtures.master_signal_stubs import (
        get_full_available_modules_stub,
        get_stubbed_technical_indicators,
        get_stubbed_stock_info,
    )
    from app.services.data_collector import DataCollector
    from app.services.technical_analysis import TechnicalAnalyzer
    import app.services.master_signal as ms_mod

    # 1. calculate_master_signal 호출 시 modules=None이면 SSOT modules 스텁 주입
    orig_calc = ms_mod.calculate_master_signal

    def safe_calc_master_signal(ticker: str, modules=None):
        if modules is None:
            modules = get_full_available_modules_stub()
        return orig_calc(ticker, modules=modules)

    monkeypatch.setattr(ms_mod, "calculate_master_signal", safe_calc_master_signal)
    monkeypatch.setattr("app.services.scheduler.calculate_master_signal", safe_calc_master_signal)

    # 2. 시세 및 테크니컬 신호 스텁 배선 (오프라인 환경 보장)
    monkeypatch.setattr(
        DataCollector, "get_stock_info",
        lambda self, ticker: get_stubbed_stock_info(ticker, current_price=100.0)
    )
    monkeypatch.setattr(
        DataCollector, "get_historical_data",
        lambda self, ticker, period="1y", interval="1d": []
    )
    monkeypatch.setattr(
        TechnicalAnalyzer, "analyze",
        lambda self, ticker, historical_data=None, current_price=100.0: get_stubbed_technical_indicators(ticker, confidence=75)
    )

    yield
'''

with open("tests/conftest.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(conftest_prefix + fixture_code)

print("Updated conftest.py with scope-limited fixture successfully!")
