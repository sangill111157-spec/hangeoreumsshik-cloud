conftest_path = r"C:\trading\package\nvda_trading_system\backend\tests\conftest.py"

with open(conftest_path, "r", encoding="utf-8") as f:
    content = f.read()

new_fixture = '''

@pytest.fixture(autouse=True)
def mock_open_orders_for_order_execution(request, monkeypatch):
    """[단위 테스트 격리] test_scheduler_sizing 등 주문 발주 테스트에서
    get_open_orders_sync가 conftest의 Session.send 네트워크 차단으로 인해
    Fail-Closed 차단되는 것을 방지하기 위해 미체결 0건([])을 기본 반환하도록 설정.
    단, test_broker_reconcile_and_orders 및 test_kis_broker_exchange_codes 등
    미체결 조회 자체를 테스트하는 모듈은 제외.
    """
    node_name = str(getattr(request.node, "fspath", ""))
    if "test_scheduler_sizing" in node_name:
        from app.services.kis_broker import KisBroker
        monkeypatch.setattr(KisBroker, "get_open_orders_sync", lambda self, *args, **kwargs: [])
'''

if "def mock_open_orders_for_order_execution" not in content:
    content += new_fixture
    with open(conftest_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added mock_open_orders_for_order_execution fixture to conftest.py")
else:
    print("Fixture already in conftest.py")
