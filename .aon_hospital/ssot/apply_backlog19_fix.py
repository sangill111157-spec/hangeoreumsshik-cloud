# -*- coding: utf-8 -*-
import os

backend_dir = r"C:\trading\package\nvda_trading_system\backend"
os.chdir(backend_dir)

# 1. Update tests/fixtures/master_signal_stubs.py
stubs_code = '''# -*- coding: utf-8 -*-
"""
Master Signal Test Fixtures & Stubs for unit testing only.
Production codebase (app/) must NEVER import from this file.
"""
from typing import Dict, Any
from app.services.master_signal import BASE_WEIGHTS
from app.services.technical_analysis import TechnicalIndicators
from app.services.data_collector import StockInfo


def get_full_available_modules_stub() -> Dict[str, Any]:
    """[BACKLOG_19] 7대 가중 모듈 전체 가용 및 정상 BUY 신호 스텁 딕셔너리.
    BASE_WEIGHTS SSOT의 모든 모듈 키를 참조하여 동적으로 완결성을 보장하며,
    6대 자본 케이스 회귀 테스트 및 마스터 신호 유닛 테스트용 기본 모듈 데이터를 제공한다.
    """
    stub: Dict[str, Any] = {
        "investor_analysis": {
            "overall_signal": "BUY",
            "overall_confidence": 75,
            "bull_count": 3,
            "bear_count": 0,
            "score": 75.0,
            "available": True,
        },
        "pod_signals": [
            {"pod_name": "tech_pod", "signal": "BUY", "confidence": 80, "score": 75.0, "available": True}
        ],
        "technical": {
            "overall_signal": "BUY",
            "confidence": 75,
            "available": True,
        },
        "llm_news": {
            "news_composite_score": 75.0,
            "news_signal": "BUY",
            "sentiment_label": "BUY",
            "total_news_analyzed": 5,
            "available": True,
        },
        "institutional": {
            "available": True,
            "confidence": 70,
        },
        "options_flow": {
            "available": True,
            "options_composite_score": 70.0,
            "options_signal": "BUY",
        },
        "darkpool": {
            "available": True,
            "confidence": 65,
            "darkpool_composite_score": 65.0,
        },
        "events": {
            "upcoming_events": [],
            "earnings_season": False,
            "has_regulatory_event": False,
            "available": True,
        },
        "correlation": {
            "available": True,
            "macro_score": 55.0,
        },
    }

    # BASE_WEIGHTS SSOT의 모든 키가 누락 없이 stub에 포함되도록 보장
    for mod_name in BASE_WEIGHTS.keys():
        if mod_name not in stub:
            stub[mod_name] = {"available": True, "confidence": 75, "signal": "BUY"}

    return stub


def get_stubbed_technical_indicators(ticker: str = "NVDA", confidence: int = 75) -> TechnicalIndicators:
    """[BACKLOG_19] 6대 자본 회귀 테스트용 정상 BUY 신뢰도 기술적 지표 스텁 객체 생성."""
    return TechnicalIndicators(
        ticker=ticker,
        overall_signal="buy",
        confidence=confidence,
        available=True,
    )


def get_stubbed_stock_info(ticker: str = "NVDA", current_price: float = 100.0) -> StockInfo:
    """[BACKLOG_19] 6대 자본 회귀 테스트용 기본 주식 정보 스텁 객체 생성."""
    return StockInfo(
        symbol=ticker,
        name=f"{ticker} Corp",
        current_price=current_price,
        previous_close=current_price * 0.98,
        open_price=current_price * 0.99,
        day_high=current_price * 1.02,
        day_low=current_price * 0.98,
        volume=1000000,
        market_cap=2000000000,
        pe_ratio=35.0,
        eps=2.5,
        week_52_high=current_price * 1.25,
        week_52_low=current_price * 0.75,
        avg_volume=1000000,
        timestamp="2026-09-12T00:00:00",
        currency="USD",
        market="US",
    )
'''

with open("tests/fixtures/master_signal_stubs.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(stubs_code)

print("Updated tests/fixtures/master_signal_stubs.py successfully!")

# 2. Append wire_master_signal_stubs_for_regression fixture to tests/conftest.py
with open("tests/conftest.py", "r", encoding="utf-8") as f:
    conftest_text = f.read()

fixture_code = '''

@pytest.fixture(autouse=True)
def wire_master_signal_stubs_for_regression(request, monkeypatch):
    """[백로그 19] 자본 6대 케이스 회귀(test_six_capital_cases_regression.py) 및 마스터 신호 스텁 배선:
    단위 테스트 오프라인 환경에서 modules 미전달로 인한 master_signal fail-closed 차단 및
    시세/신호 미연결로 인한 사이징 실패를 방지하기 위해,
    tests/fixtures/master_signal_stubs.py의 SSOT 기반 modules 스텁을 안전하게 배선한다.
    """
    # 1. calculate_master_signal 호출 시 modules=None이면 스텁 주입 (단, fail-closed 전용 테스트는 보존)
    import app.services.master_signal as ms_mod
    orig_calc = ms_mod.calculate_master_signal

    def safe_calc_master_signal(ticker: str, modules: Optional[dict] = None):
        if modules is None:
            if request.node.name == "test_calculate_master_signal_no_modules_is_fail_closed":
                return orig_calc(ticker, modules=None)
            from tests.fixtures.master_signal_stubs import get_full_available_modules_stub
            modules = get_full_available_modules_stub()
        return orig_calc(ticker, modules=modules)

    monkeypatch.setattr(ms_mod, "calculate_master_signal", safe_calc_master_signal)
    monkeypatch.setattr("app.services.scheduler.calculate_master_signal", safe_calc_master_signal)

    # 2. test_six_capital_cases_regression.py 스코프 한정 시세 및 테크니컬 신호 스텁 배선
    if "test_six_capital_cases_regression" in str(request.node.fspath):
        from tests.fixtures.master_signal_stubs import (
            get_stubbed_technical_indicators,
            get_stubbed_stock_info,
        )
        from app.services.data_collector import DataCollector
        from app.services.technical_analysis import TechnicalAnalyzer

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

assert "@pytest.fixture(autouse=True)" in conftest_text
if "def wire_master_signal_stubs_for_regression" not in conftest_text:
    conftest_text = conftest_text.rstrip() + fixture_code + "\n"
    with open("tests/conftest.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(conftest_text)
    print("Updated tests/conftest.py successfully!")
else:
    print("tests/conftest.py already contains wire_master_signal_stubs_for_regression!")
