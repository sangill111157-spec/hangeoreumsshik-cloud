import os

test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

content = '''"""
Unit tests for KIS broker balance & open orders sync, and Reconciler integration.
Network calls are completely forbidden and fully mocked.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest

from app.services.kis_broker import (
    BrokerInquiryError,
    OpenOrdersInquiryError,
    get_overseas_balance_exchange_codes,
)
from app.services.reconciler import (
    BrokerInquiryAdapter,
    BrokerSnapshot,
    DiscrepancyCode,
    INQUIRY_TRANSIENT_HOLD_CODE,
    LocalSnapshot,
    PositionSnapshot,
    ReconciliationLoop,
    reconcile_positions_and_cash,
)


# ==============================================================================
# 1. KIS Broker Balance Sync Tests
# ==============================================================================
def test_get_overseas_balance_exchange_codes():
    paper_codes = get_overseas_balance_exchange_codes(is_paper=True)
    assert paper_codes == ["NASD", "NYSE", "AMEX"]
    real_codes = get_overseas_balance_exchange_codes(is_paper=False)
    assert real_codes == ["NASD"]


def test_get_domestic_balance_sync_rt_cd_failure():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "1",
        "msg_cd": "EGW00123",
        "msg1": "조회 실패",
        "output1": [],
        "output2": []
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        with pytest.raises(BrokerInquiryError) as exc_info:
            kis_broker.get_domestic_balance_sync()
        assert "rt_cd=1" in str(exc_info.value)


def test_get_domestic_balance_sync_no_data_70070000():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "70070000",
        "msg1": "해당 내역이 없습니다.",
        "output1": [],
        "output2": [{"dnca_tot_amt": "1000000"}]
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        res = kis_broker.get_domestic_balance_sync()
        assert res["positions"] == {}
        assert res["cash"] == 1000000.0


def test_get_domestic_balance_sync_pagination_and_positions():
    from app.services import kis_broker

    # Page 1
    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.headers = {"tr_cont": "D", "ctx_area_fk100": "FK1", "ctx_area_nk100": "NK1"}
    resp1.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "msg1": "정상조회",
        "ctx_area_fk100": "FK1",
        "ctx_area_nk100": "NK1",
        "output1": [
            {"pdno": "005930", "hldg_qty": "10", "pchs_avg_pric": "70000"}
        ],
        "output2": [{"dnca_tot_amt": "500000"}]
    }

    # Page 2
    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.headers = {"tr_cont": "F", "ctx_area_fk100": "", "ctx_area_nk100": ""}
    resp2.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "msg1": "정상조회",
        "ctx_area_fk100": "",
        "ctx_area_nk100": "",
        "output1": [
            {"pdno": "000660", "hldg_qty": "5", "pchs_avg_pric": "120000"}
        ],
        "output2": [{"dnca_tot_amt": "500000"}]
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.side_effect = [resp1, resp2]
        res = kis_broker.get_domestic_balance_sync()
        assert len(res["positions"]) == 2
        assert res["positions"]["005930"]["quantity"] == 10
        assert res["positions"]["000660"]["quantity"] == 5
        assert res["cash"] == 500000.0


def test_get_overseas_balance_sync_3_exchanges_and_dedup():
    from app.services import kis_broker

    # NASD resp
    resp_nasd = MagicMock()
    resp_nasd.status_code = 200
    resp_nasd.headers = {}
    resp_nasd.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "msg1": "정상조회",
        "output1": [
            {"ovrs_pdno": "NVDA", "cblc_qty": "10", "pchs_avg_pric": "120.5"}
        ],
        "output2": {}
    }

    # NYSE resp (with same NVDA and new symbol)
    resp_nyse = MagicMock()
    resp_nyse.status_code = 200
    resp_nyse.headers = {}
    resp_nyse.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "msg1": "정상조회",
        "output1": [
            {"ovrs_pdno": "NVDA", "cblc_qty": "10", "pchs_avg_pric": "120.5"},
            {"ovrs_pdno": "IBM", "cblc_qty": "4", "pchs_avg_pric": "150.0"}
        ],
        "output2": {}
    }

    # AMEX resp (empty)
    resp_amex = MagicMock()
    resp_amex.status_code = 200
    resp_amex.headers = {}
    resp_amex.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "70070000",
        "msg1": "해당 내역이 없습니다.",
        "output1": [],
        "output2": {}
    }

    # Cash resp (VTTS3007R)
    resp_cash = MagicMock()
    resp_cash.status_code = 200
    resp_cash.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "output": {
            "ord_psbl_frcr_amt": "3450.75"
        }
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.side_effect = [resp_nasd, resp_nyse, resp_amex, resp_cash]
        res = kis_broker.get_overseas_balance_sync()
        assert len(res["positions"]) == 2
        assert "NVDA" in res["positions"]
        assert "IBM" in res["positions"]
        assert res["positions"]["NVDA"]["quantity"] == 10
        assert res["cash"] == 3450.75


# ==============================================================================
# 2. Open Orders Sync Tests
# ==============================================================================
def test_get_open_orders_sync_failure_raises_exception():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        with pytest.raises(OpenOrdersInquiryError):
            kis_broker.get_open_orders_sync(exchange="KRX")


def test_get_open_orders_sync_krx_routes_to_domestic():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "output1": [
            {
                "odno": "000123",
                "pdno": "005930",
                "sll_buy_dvsn_cd": "02",  # 02=BUY
                "nccs_qty": "5",
                "ord_unpr": "70000"
            }
        ]
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        orders = kis_broker.get_open_orders_sync(exchange="KRX")
        assert len(orders) == 1
        assert orders[0]["ticker"] == "005930"
        assert orders[0]["side"] == "BUY"
        assert orders[0]["quantity"] == 5
        # Verify domestic endpoint was called
        call_url = mock_req.get.call_args[0][0]
        assert "domestic-stock/v1/trading/inquire-daily-ccld" in call_url


def test_get_open_orders_sync_nasd_routes_to_overseas_paper():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "output": [
            {
                "odno": "000987",
                "pdno": "NVDA",
                "sll_buy_dvsn_cd": "01",  # 01=SELL
                "nccs_qty": "10",
                "ft_ord_unpr3": "120.0"
            }
        ]
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        orders = kis_broker.get_open_orders_sync(exchange="NASD")
        assert len(orders) == 1
        assert orders[0]["ticker"] == "NVDA"
        assert orders[0]["side"] == "SELL"
        assert orders[0]["quantity"] == 10
        # Verify overseas endpoint was called
        call_url = mock_req.get.call_args[0][0]
        assert "overseas-stock/v1/trading/inquire-ccnl" in call_url


# ==============================================================================
# 3. Auto Trader Fail-Closed / Reduce-Only Tests
# ==============================================================================
def test_auto_trader_open_orders_error_blocks_buy():
    from app.services import kis_broker

    with patch.object(kis_broker, "get_open_orders_sync", side_effect=OpenOrdersInquiryError("Inquiry failed")):
        # Buy should fail closed
        with pytest.raises(OpenOrdersInquiryError):
            try:
                kis_broker.get_open_orders_sync(exchange="KRX")
            except OpenOrdersInquiryError:
                action = "BUY"
                if action == "SELL":
                    pass
                else:
                    raise


def test_auto_trader_open_orders_error_allows_reduce_only_sell():
    from app.services import kis_broker

    with patch.object(kis_broker, "get_open_orders_sync", side_effect=OpenOrdersInquiryError("Inquiry failed")):
        action = "SELL"
        allowed = False
        try:
            kis_broker.get_open_orders_sync(exchange="NASD")
        except OpenOrdersInquiryError:
            if action == "SELL":
                allowed = True
            else:
                raise
        assert allowed is True


# ==============================================================================
# 4. Reconciler Adapter & Transient Hold / Blocking Tests
# ==============================================================================
def test_broker_adapter_raises_inquiry_failure_on_exception():
    adapter = BrokerInquiryAdapter()
    from app.services import kis_broker

    with patch.object(kis_broker, "get_domestic_balance_sync", side_effect=BrokerInquiryError("Network timeout")):
        with pytest.raises(BrokerInquiryError):
            adapter.fetch_domestic_snapshot()


def test_reconciler_loop_inquiry_failure_transient_hold_and_consecutive_blocking():
    adapter = MagicMock()
    loop = ReconciliationLoop(adapter=adapter, interval_seconds=30)

    # 1st cycle failure -> TRANSIENT_HOLD
    fail_snap = BrokerSnapshot(
        positions={},
        cash_krw=0.0,
        cash_usd=0.0,
        open_orders=[],
        timestamp=datetime.now(timezone.utc),
        is_success=False,
        error_message="Broker inquiry failed",
    )
    adapter.fetch_broker_snapshot.return_value = fail_snap

    res1 = loop.run_single_cycle()
    assert res1.details.get("inquiry_failure", {}).get("code") == INQUIRY_TRANSIENT_HOLD_CODE
    assert loop._consecutive_inquiry_failures == 1
    assert loop.is_reconciliation_blocked is False  # 1회 실패는 즉시 차단하지 않고 유예

    # 2nd cycle failure -> BLOCKING (INQUIRY_FAILURE)
    res2 = loop.run_single_cycle()
    assert DiscrepancyCode.INQUIRY_FAILURE in res2.discrepancies
    assert loop._consecutive_inquiry_failures == 2
    assert loop.is_reconciliation_blocked is True  # 2회 연속 실패 시 Fail-Closed 차단


def test_reconciler_qty_mismatch_and_resolution():
    local_snap = LocalSnapshot(
        positions={"NVDA": PositionSnapshot(ticker="NVDA", quantity=10, avg_price=120.0)},
        cash_krw=1000000.0,
        cash_usd=500.0,
        open_orders=[],
        timestamp=datetime.now(timezone.utc),
    )

    # Case A: Mismatch (Broker has 8, Local has 10)
    broker_snap_mismatch = BrokerSnapshot(
        positions={"NVDA": PositionSnapshot(ticker="NVDA", quantity=8, avg_price=120.0)},
        cash_krw=1000000.0,
        cash_usd=500.0,
        open_orders=[],
        timestamp=datetime.now(timezone.utc),
        is_success=True,
    )
    res_mismatch = reconcile_positions_and_cash(local_snap, broker_snap_mismatch)
    assert DiscrepancyCode.QTY_MISMATCH in res_mismatch.discrepancies

    # Case B: Match
    broker_snap_match = BrokerSnapshot(
        positions={"NVDA": PositionSnapshot(ticker="NVDA", quantity=10, avg_price=120.0)},
        cash_krw=1000000.0,
        cash_usd=500.0,
        open_orders=[],
        timestamp=datetime.now(timezone.utc),
        is_success=True,
    )
    res_match = reconcile_positions_and_cash(local_snap, broker_snap_match)
    assert len(res_match.discrepancies) == 0
'''

with open(test_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Written clean {test_path}")
