test_orders_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_orders_path, "r", encoding="utf-8") as f:
    content = f.read()

new_tests_code = '''

# ==============================================================================
# 7. Additional Verification Tests (Sell exception & all-filter)
# ==============================================================================
def test_open_orders_fail_sell_proceeds(monkeypatch):
    """미체결 조회가 예외를 내도, 보유 수량이 있는 매도는 주문 전송 함수가 정확히 1번 호출됨을 검증."""
    from app.services.auto_trader import AutoTrader
    from app.services.kis_broker import KisBroker, OpenOrdersInquiryError
    from app.services.account_state import AccountState

    monkeypatch.setenv("KIS_IS_PAPER", "True")
    monkeypatch.setenv("ENABLE_TEST_ENDPOINTS", "true")

    trader = AutoTrader()
    trader.dry_run = True
    trader.kis_app_key = "MOCK_KEY"
    trader.kis_app_secret = "MOCK_SECRET"
    trader.kis_account_no = "12345678"
    trader.tr_id_buy = "VTTT1002U"
    trader.tr_id_sell = "VTTT1001U"

    broker = KisBroker()
    broker.get_access_token_sync = MagicMock(return_value="MOCK_TOKEN")
    broker.get_open_orders_sync = MagicMock(side_effect=OpenOrdersInquiryError("Network timeout during open orders"))

    account_state = AccountState(
        cash_balance_usd=10000.0,
        positions={"NVDA": 10},
        holding_qty=10,
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "0",
        "output": {"ODNO": "99001", "odno": "99001"},
    }

    with patch("app.services.kis_broker.get_kis_broker", return_value=broker), \\
         patch("requests.post", return_value=mock_resp) as mock_post, \\
         patch("app.services.kis_broker.get_kis_rate_limiter"), \\
         patch("time.sleep"):

        result = trader._execute_kis_order(
            ticker="NVDA",
            action="SELL",
            shares=5,
            price=120.0,
            account_state=account_state,
        )

        assert mock_post.call_count == 1
        assert result.get("success") is True
        assert result.get("order_state") == "ORDER_ACCEPTED"


def test_open_orders_fail_buy_blocked(monkeypatch):
    """미체결 조회가 예외를 낼 때, 매수는 order_state=='ORDER_REJECTED', inquiry_failed==True, 주문 전송 0번임을 검증."""
    from app.services.auto_trader import AutoTrader
    from app.services.kis_broker import KisBroker, OpenOrdersInquiryError
    from app.services.account_state import AccountState

    monkeypatch.setenv("KIS_IS_PAPER", "True")
    monkeypatch.setenv("ENABLE_TEST_ENDPOINTS", "true")

    trader = AutoTrader()
    trader.dry_run = True
    trader.kis_app_key = "MOCK_KEY"
    trader.kis_app_secret = "MOCK_SECRET"
    trader.kis_account_no = "12345678"
    trader.tr_id_buy = "VTTT1002U"
    trader.tr_id_sell = "VTTT1001U"

    broker = KisBroker()
    broker.get_access_token_sync = MagicMock(return_value="MOCK_TOKEN")
    broker.get_open_orders_sync = MagicMock(side_effect=OpenOrdersInquiryError("Network timeout during open orders"))

    account_state = AccountState(
        cash_balance_usd=10000.0,
        positions={},
        holding_qty=0,
    )

    with patch("app.services.kis_broker.get_kis_broker", return_value=broker), \\
         patch("requests.post") as mock_post, \\
         patch("app.services.kis_broker.get_kis_rate_limiter"), \\
         patch("time.sleep"):

        result = trader._execute_kis_order(
            ticker="NVDA",
            action="BUY",
            shares=5,
            price=120.0,
            account_state=account_state,
        )

        assert mock_post.call_count == 0
        assert result.get("order_state") == "ORDER_REJECTED"
        assert result.get("inquiry_failed") is True


def test_recent_orders_uses_all_filter():
    """requests.get에 넘어간 params에서 국내 CCLD_DVSN=='00', 해외 CCLD_NCCS_DVSN=='00'을 검증."""
    from app.services.kis_broker import KisBroker

    broker = KisBroker()
    broker.get_access_token_sync = MagicMock(return_value="mock_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"rt_cd": "0", "msg_cd": "MCA00000", "output": []}

    with patch("requests.get", return_value=mock_resp) as mock_get, \\
         patch("app.services.kis_broker.get_kis_rate_limiter"):

        # 1. 해외 (NASD) -> CCLD_NCCS_DVSN == "00"
        broker.get_recent_orders_sync(exchange="NASD")
        mock_get.assert_called_once()
        _, kwargs_ovrs = mock_get.call_args
        assert kwargs_ovrs["params"]["CCLD_NCCS_DVSN"] == "00"

    mock_resp_dom = MagicMock()
    mock_resp_dom.status_code = 200
    mock_resp_dom.json.return_value = {"rt_cd": "0", "msg_cd": "MCA00000", "output1": []}

    with patch("requests.get", return_value=mock_resp_dom) as mock_get_dom, \\
         patch("app.services.kis_broker.get_kis_rate_limiter"):

        # 2. 국내 (KRX) -> CCLD_DVSN == "00"
        broker.get_recent_orders_sync(exchange="KRX")
        mock_get_dom.assert_called_once()
        _, kwargs_dom = mock_get_dom.call_args
        assert kwargs_dom["params"]["CCLD_DVSN"] == "00"
'''

if "def test_open_orders_fail_sell_proceeds" not in content:
    content += new_tests_code
    with open(test_orders_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully added 3 required tests to test_broker_reconcile_and_orders.py!")
else:
    print("Tests already present.")
