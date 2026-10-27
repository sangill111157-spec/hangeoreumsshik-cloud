import os

test_tech_content = '''import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.stock import get_data_collector, get_technical_analyzer

client = TestClient(app)

def test_technical_endpoint_returns_null_when_unavailable():
    mock_collector = MagicMock()
    mock_stock_info = MagicMock()
    mock_stock_info.current_price = None
    mock_collector.get_stock_info.return_value = mock_stock_info
    mock_collector.get_historical_data.return_value = [{"date": "2026-01-01", "close": 100}]

    mock_analyzer = MagicMock()
    mock_tech = MagicMock()
    mock_tech.available = False
    mock_tech.trend = "bullish"
    mock_tech.overall_signal = "BUY"
    mock_tech.confidence = 80
    mock_tech.moving_averages = {"sma_20": 120}
    mock_tech.rsi = {"value": 51}
    mock_tech.macd = {"macd": 0.49}
    mock_tech.bollinger_bands = {"middle": 120}
    mock_tech.volume = {}
    mock_analyzer.analyze.return_value = mock_tech

    app.dependency_overrides[get_data_collector] = lambda: mock_collector
    app.dependency_overrides[get_technical_analyzer] = lambda: mock_analyzer

    try:
        response = client.get("/api/stock/NVDA/technical")
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is False
        assert data["current_price"] is None
        assert data["trend"] is None
        assert data["overall_signal"] == "UNAVAILABLE"
        assert data["confidence"] == 0
        assert data["rsi"] is None
        assert data["macd"] is None
        assert data["bollinger_bands"] is None
        assert data["moving_averages"] is None
        assert data["volume"] is None
    finally:
        app.dependency_overrides.clear()
'''

test_risk_content = '''import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.risk_monitor import RiskMonitor

client = TestClient(app)

def test_risk_score_returns_null_and_unavailable_when_no_data():
    monitor = RiskMonitor()
    with patch.object(monitor, "check_portfolio_risk", return_value={"success": False, "data": {}}), \
         patch.object(monitor, "check_market_risk", return_value={"success": False, "data": {}}):
        
        res = monitor.get_risk_score()
        assert res["success"] is True
        assert res["data"]["score"] is None
        assert res["data"]["level"] == "UNAVAILABLE"
        assert res["data"]["available"] is False

def test_risk_score_endpoint_returns_null_score():
    with patch("app.services.risk_monitor.get_risk_monitor") as mock_grm:
        mock_rm = MagicMock()
        mock_rm.get_risk_score.return_value = {
            "success": True,
            "data": {
                "score": None,
                "level": "UNAVAILABLE",
                "level_color": "⚪",
                "details": {},
                "available": False
            }
        }
        mock_grm.return_value = mock_rm
        response = client.get("/api/risk/score")
        assert response.status_code == 200
        data = response.json()
        assert data["score"] is None
        assert data["level"] == "UNAVAILABLE"
        assert data["available"] is False
'''

with open(r'C:\trading\package\nvda_trading_system\backend\tests\test_technical_null_when_unavailable.py', 'w', encoding='utf-8') as f:
    f.write(test_tech_content)

with open(r'C:\trading\package\nvda_trading_system\backend\tests\test_risk_score_null_when_no_data.py', 'w', encoding='utf-8') as f:
    f.write(test_risk_content)

print("Updated regression test files successfully")
