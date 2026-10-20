auto_trader_path = r"C:\trading\package\nvda_trading_system\backend\app\services\auto_trader.py"
test_orders_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

# 1. Modify auto_trader.py line ~802
with open(auto_trader_path, "r", encoding="utf-8") as f:
    content = f.read()

target = 'recent_orders = broker.get_recent_orders_sync(exchange=(excg_cd if not is_kr else "NASD"))'
replacement = '''target_exchange = "KRX" if is_kr else (excg_cd or "NASD")
                        recent_orders = broker.get_recent_orders_sync(exchange=target_exchange)'''

if target in content:
    content = content.replace(target, replacement)
    with open(auto_trader_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated auto_trader.py line 802 domestic exchange branching!")
else:
    print("Warning: target string not found in auto_trader.py!")


# 2. Add test for domestic unknown order resolution to test_broker_reconcile_and_orders.py
with open(test_orders_path, "r", encoding="utf-8") as f:
    test_content = f.read()

new_domestic_test = '''
def test_resolve_unknown_order_domestic_does_not_call_overseas_tr(monkeypatch):
    """국내 주문 불확정 시 get_recent_orders_sync가 해외 TR(VTTS3035R)을 부르지 않고 국내 TR(VTTC8001R)을 호출하는지 검증."""
    from app.services.auto_trader import AutoTrader
    from app.services.kis_broker import KisBroker

    monkeypatch.setenv("KIS_IS_PAPER", "True")
    monkeypatch.setenv("ENABLE_TEST_ENDPOINTS", "true")

    trader = AutoTrader()
    trader.dry_run = True
    trader.kis_app_key = "MOCK_KEY"
    trader.kis_app_secret = "MOCK_SECRET"
    trader.kis_account_no = "12345678"
    trader.tr_id_buy = "VTTC0802U"
    trader.tr_id_sell = "VTTC0801U"

    broker = KisBroker()
    broker.get_access_token_sync = MagicMock(return_value="MOCK_TOKEN")
    broker.get_open_orders_sync = MagicMock(return_value=[])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "output1": [
            {
                "odno": "11101",
                "pdno": "005930",
                "sll_buy_dvsn_cd": "02",
                "ord_qty": "10",
                "tot_ccld_qty": "10",
                "avg_prvs": "70000",
            }
        ]
    }

    with patch("app.services.kis_broker.get_kis_broker", return_value=broker), \\
         patch("app.services.auto_trader.get_kis_broker", return_value=broker), \\
         patch("requests.post", side_effect=requests.exceptions.Timeout("Connection timed out")), \\
         patch("requests.get", return_value=mock_resp) as mock_get, \\
         patch("app.services.kis_broker.get_kis_rate_limiter"), \\
         patch("time.sleep"):

        result = trader._execute_kis_order(
            ticker="005930",
            action="BUY",
            shares=10,
            price=70000.0,
            is_kr=True,
        )

        # 1. 국내 체결 주문으로 정상 복구 확정
        assert result.get("success") is True
        assert result.get("order_no") == "11101"
        assert result.get("order_state") == "ORDER_FILLED"

        # 2. 해외 TR(VTTS3035R)이나 inquire-ccnl이 절대 불리지 않고, 국내 TR(VTTC8001R)과 inquire-daily-ccld가 호출되었음을 검증
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        called_headers = mock_get.call_args[1]["headers"]
        assert "inquire-ccnl" not in called_url
        assert "inquire-daily-ccld" in called_url
        assert called_headers["tr_id"] == "VTTC8001R"
        assert called_headers["tr_id"] != "VTTS3035R"
'''

if "test_resolve_unknown_order_domestic_does_not_call_overseas_tr" not in test_content:
    test_content += new_domestic_test
    with open(test_orders_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    print("Successfully added test_resolve_unknown_order_domestic_does_not_call_overseas_tr!")
else:
    print("Test already present.")
