import re

kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"
test_codes_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_kis_broker_exchange_codes.py"
test_orders_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

# 1. Modify app/services/kis_broker.py
with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1-a. Clean up comment at line ~39
content = content.replace(
    "# 해외 거래소 코드 매핑 SSOT (get_open_orders_sync, get_recent_orders_sync, get_order_list, cancel_order 등)",
    "# 해외 거래소 코드 매핑 SSOT (get_open_orders_sync, get_recent_orders_sync, cancel_order 등)"
)

# 1-b. Remove get_order_list
# We will match from `async def get_order_list(` up to `# [P2-1 & P2-2] SYNC ORDER / EXECUTION INQUIRY HELPERS`
order_list_pattern = re.compile(
    r"    async def get_order_list\([\s\S]*?raise KISApiError\(f\"Order list inquiry error: \{str\(e\)\}\"\)\n\n",
    re.MULTILINE
)
match = order_list_pattern.search(content)
if match:
    content = content[:match.start()] + content[match.end():]
    print("Successfully removed get_order_list!")
else:
    print("Warning: get_order_list pattern not found!")

# 1-c. Replace get_recent_orders_sync
new_recent_orders_code = '''    def get_recent_orders_sync(self, exchange: str = "NASD") -> List[Dict[str, Any]]:
        """
        [P2-2] 최근 주문/체결 목록 동기 조회 (새 조회 경로 get_open_orders_sync 기반 위임)
        - 실패 시 OpenOrdersInquiryError 예외 전파 (빈 리스트 [] 반환 금지)
        - 반환 형태: List[Dict[str, Any]] (odno, ticker, side, quantity, ccld_qty, ccld_prc, raw)
        """
        open_orders = self.get_open_orders_sync(exchange=exchange)
        parsed: List[Dict[str, Any]] = []
        for o in open_orders:
            raw = o.get("raw", {})
            ccld_qty = int(float(raw.get("ft_ccld_qty", 0) or raw.get("ccld_qty", 0) or 0))
            ccld_prc = float(raw.get("ft_ccld_unpr3", 0.0) or raw.get("ccld_unpr", 0.0) or 0.0)
            parsed.append({
                "odno": str(o.get("odno", "")),
                "ticker": str(o.get("ticker", "")),
                "side": str(o.get("side", "")),
                "quantity": int(o.get("quantity", 0)),
                "ccld_qty": ccld_qty,
                "ccld_prc": ccld_prc,
                "raw": raw,
            })
        return parsed
'''

recent_orders_pattern = re.compile(
    r"    def get_recent_orders_sync\(self, exchange: str = \"NASD\"\) -> List\[Dict\[str, Any\]\]:[\s\S]*?logger\.error\(f\"\[KIS_INQUIRY\] Failed to get recent orders sync: \{e\}\"\)\n            return \[\]\n",
    re.MULTILINE
)
match_recent = recent_orders_pattern.search(content)
if match_recent:
    content = content[:match_recent.start()] + new_recent_orders_code + content[match_recent.end():]
    print("Successfully replaced get_recent_orders_sync!")
else:
    print("Warning: get_recent_orders_sync pattern not found!")

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)


# 2. Modify tests/test_kis_broker_exchange_codes.py
with open(test_codes_path, "r", encoding="utf-8") as f:
    test_codes_content = f.read()

target_mock = 'mock_resp.json.return_value = {"output1": []}'
replacement_mock = '''mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "output1": [],
    }'''

if target_mock in test_codes_content:
    test_codes_content = test_codes_content.replace(target_mock, replacement_mock)
    with open(test_codes_path, "w", encoding="utf-8") as f:
        f.write(test_codes_content)
    print("Successfully updated test_kis_broker_exchange_codes.py mock response!")
else:
    print("Note: target_mock not found or already updated in test_kis_broker_exchange_codes.py")


# 3. Add tests to tests/test_broker_reconcile_and_orders.py
with open(test_orders_path, "r", encoding="utf-8") as f:
    test_orders_content = f.read()

new_tests = '''

# ==============================================================================
# 6. Legacy endpoint elimination and get_recent_orders_sync verification
# ==============================================================================
def test_get_recent_orders_sync_does_not_call_inquire_orders():
    """get_recent_orders_sync가 레거시 inquire-orders 대신 새 엔드포인트를 호출하는지 검증."""
    from app.services.kis_broker import KisBroker

    broker = KisBroker()
    broker.get_access_token_sync = MagicMock(return_value="mock_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MCA00000",
        "output": [
            {
                "odno": "99901",
                "pdno": "NVDA",
                "sll_buy_dvsn": "02",
                "nccs_qty": "10",
                "ft_ord_unpr3": "125.5",
                "ft_ccld_qty": "5",
                "ft_ccld_unpr3": "125.5",
            }
        ]
    }

    with patch("requests.get", return_value=mock_resp) as mock_get, \
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        orders = broker.get_recent_orders_sync(exchange="NASD")

        assert len(orders) == 1
        assert orders[0]["odno"] == "99901"
        assert orders[0]["ticker"] == "NVDA"
        assert orders[0]["ccld_qty"] == 5
        assert orders[0]["ccld_prc"] == 125.5

        # inquire-orders URL을 절대 호출하지 않았는지 검증
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "inquire-orders" not in called_url
        assert "inquire-ccnl" in called_url


def test_get_recent_orders_sync_failure_raises_exception_not_empty_list():
    """get_recent_orders_sync 조회 실패 시 빈 리스트 [] 대신 OpenOrdersInquiryError 예외가 발생하는지 검증."""
    from app.services.kis_broker import KisBroker

    broker = KisBroker()
    broker.get_access_token_sync = MagicMock(return_value="mock_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("requests.get", return_value=mock_resp), \
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        with pytest.raises(OpenOrdersInquiryError):
            broker.get_recent_orders_sync(exchange="NASD")

    # rt_cd != '0' 인 경우도 예외 발생 검증
    mock_resp_err = MagicMock()
    mock_resp_err.status_code = 200
    mock_resp_err.json.return_value = {
        "rt_cd": "1",
        "msg_cd": "ERR001",
        "msg1": "조회 실패",
    }
    with patch("requests.get", return_value=mock_resp_err), \
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        with pytest.raises(OpenOrdersInquiryError):
            broker.get_recent_orders_sync(exchange="NASD")
'''

if "test_get_recent_orders_sync_does_not_call_inquire_orders" not in test_orders_content:
    test_orders_content += new_tests
    with open(test_orders_path, "w", encoding="utf-8") as f:
        f.write(test_orders_content)
    print("Successfully added new tests to test_broker_reconcile_and_orders.py!")
else:
    print("Note: tests already present in test_broker_reconcile_and_orders.py")
