test_orders_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_orders_path, "r", encoding="utf-8") as f:
    content = f.read()

target = 'def test_resolve_unknown_order_no_reorder_on_inquiry_exception(mock_autotrader):'
replacement = '''def test_resolve_unknown_order_no_reorder_on_inquiry_exception(monkeypatch):
    """_resolve_unknown_order: 최근 주문 조회 중 예외가 발생해도 재주문하지 않고 UNKNOWN을 유지함을 검증."""
    from app.services.auto_trader import AutoTrader
    monkeypatch.setenv("KIS_IS_PAPER", "True")
    monkeypatch.setenv("ENABLE_TEST_ENDPOINTS", "true")
    trader = AutoTrader()
    trader.dry_run = True
    trader.kis_app_key = "MOCK_KEY"
    trader.kis_app_secret = "MOCK_SECRET"
    trader.kis_account_no = "12345678"
    trader.tr_id_buy = "VTTT1002U"
    trader.tr_id_sell = "VTTT1001U"
    mock_autotrader = trader'''

if target in content:
    content = content.replace(target, replacement)
    with open(test_orders_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully fixed fixture in test_broker_reconcile_and_orders.py!")
else:
    print("Target already replaced or not found.")
