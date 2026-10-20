test_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

with open(test_path, "r", encoding="utf-8") as f:
    content = f.read()

new_tests = '''

# ==============================================================================
# 5. Missing rt_cd response tests (Strict validation: missing rt_cd -> Exception)
# ==============================================================================
def test_get_domestic_balance_sync_missing_rt_cd_raises_exception():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        # rt_cd omitted intentionally
        "msg_cd": "MCA00000",
        "output1": [{"pdno": "005930", "hldg_qty": "10"}],
        "output2": [{"dnca_tot_amt": "1000000"}]
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        with pytest.raises(BrokerInquiryError):
            kis_broker.get_domestic_balance_sync()


def test_get_overseas_balance_sync_missing_rt_cd_raises_exception():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        # rt_cd omitted intentionally
        "output1": [{"ovrs_pdno": "NVDA", "cblc_qty": "10"}],
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        with pytest.raises(BrokerInquiryError):
            kis_broker.get_overseas_balance_sync()


def test_get_open_orders_sync_missing_rt_cd_raises_exception_domestic():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        # rt_cd omitted intentionally
        "output1": [{"odno": "001", "pdno": "005930", "nccs_qty": "5"}]
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        with pytest.raises(OpenOrdersInquiryError):
            kis_broker.get_open_orders_sync(exchange="KRX")


def test_get_open_orders_sync_missing_rt_cd_raises_exception_overseas():
    from app.services import kis_broker

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        # rt_cd omitted intentionally
        "output": [{"odno": "002", "pdno": "NVDA", "nccs_qty": "10"}]
    }

    with patch.object(kis_broker, "requests") as mock_req, \
         patch.object(kis_broker, "get_kis_rate_limiter"):
        mock_req.get.return_value = mock_resp
        with pytest.raises(OpenOrdersInquiryError):
            kis_broker.get_open_orders_sync(exchange="NASD")
'''

if "test_get_domestic_balance_sync_missing_rt_cd_raises_exception" not in content:
    content += new_tests
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Added missing rt_cd tests to test_broker_reconcile_and_orders.py!")
else:
    print("Tests already present.")
