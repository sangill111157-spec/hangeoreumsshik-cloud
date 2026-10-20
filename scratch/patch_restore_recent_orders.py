import re

kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"
test_orders_path = r"C:\trading\package\nvda_trading_system\backend\tests\test_broker_reconcile_and_orders.py"

# 1. Update kis_broker.py get_recent_orders_sync implementation
with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

new_recent_orders_code = '''    def get_recent_orders_sync(self, exchange: str = "NASD") -> List[Dict[str, Any]]:
        """
        [P2-2] 최근 주문/체결 전체 목록 동기 조회 (ORDER_UNKNOWN 확정 및 원장 체결 상세용)
        - 체결 완료(ccld_qty > 0, nccs_qty == 0) 및 미체결 주문 전체를 포함 조회 (CCLD_DVSN="00" / CCLD_NCCS_DVSN="00")
        - 국내: VTTC8001R (모의) / TTTC8001R (실전) inquire-daily-ccld
        - 해외: VTTS3035R (모의) inquire-ccnl / TTTS3035R (실전, 미검증 주석)
        - 기간: KST 기준 전일~당일
        - 실패 시 OpenOrdersInquiryError 예외 발생 (빈 목록 반환 금지, msg_cd="70070000"만 성공 0건 빈 목록)
        - 반환 키: odno, ticker, side, quantity, ccld_qty, ccld_prc, raw (HEAD 규격 100% 보존)
        """
        token = self.get_access_token_sync()
        if not token:
            raise OpenOrdersInquiryError("Token missing for get_recent_orders_sync")

        now_kst = datetime.now(timezone(timedelta(hours=9)))
        today_str = now_kst.strftime("%Y%m%d")
        yesterday_str = (now_kst - timedelta(days=1)).strftime("%Y%m%d")

        excg_upper = exchange.upper()
        parsed: List[Dict[str, Any]] = []

        if excg_upper in ("KRX", "KR", "DOMESTIC"):
            # 국내 주문/체결 전체 조회 (CCLD_DVSN="00")
            tr_id = "VTTC8001R" if self.is_paper else "TTTC8001R"
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
            headers = {
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": tr_id,
                "Content-Type": "application/json; charset=utf-8",
            }
            params = {
                "CANO": self.account_no,
                "ACNT_PRDT_CD": "01",
                "INQR_STRT_DT": yesterday_str,
                "INQR_END_DT": today_str,
                "SLL_BUY_DVSN_CD": "00",
                "INQR_DVSN": "00",
                "PDNO": "",
                "CCLD_DVSN": "00",  # 00: 전체 (체결+미체결)
                "ORD_GNO_BRNO": "",
                "ODNO": "",
                "INQR_DVSN_3": "00",
                "INQR_DVSN_1": "",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            }
            get_kis_rate_limiter().acquire_sync(1.0)
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=10)
            except Exception as e:
                raise OpenOrdersInquiryError(f"Domestic recent orders HTTP request failed: {e}") from e

            if resp.status_code != 200:
                raise OpenOrdersInquiryError(f"Domestic recent orders inquiry HTTP {resp.status_code}: {resp.text}")

            try:
                data = resp.json()
            except Exception as e:
                raise OpenOrdersInquiryError(f"Invalid JSON in domestic recent orders: {e}") from e

            rt_cd = data.get("rt_cd")
            if rt_cd != "0":
                if data.get("msg_cd") == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Domestic recent orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")

            raw_orders = data.get("output1", [])
            for o in raw_orders:
                side_code = o.get("sll_buy_dvsn_cd", "")
                tot_qty = int(float(o.get("ord_qty", 0) or 0))
                ccld_qty = int(float(o.get("tot_ccld_qty", 0) or o.get("ccld_qty", 0) or 0))
                ccld_prc = float(o.get("avg_prvs", 0.0) or o.get("ccld_unpr", 0.0) or 0.0)
                parsed.append({
                    "odno": str(o.get("odno", "")),
                    "ticker": str(o.get("pdno", "")).strip().upper(),
                    "side": "BUY" if side_code == "02" else ("SELL" if side_code == "01" else side_code),
                    "quantity": tot_qty,
                    "ccld_qty": ccld_qty,
                    "ccld_prc": ccld_prc,
                    "raw": o,
                })
            return parsed

        elif excg_upper in ("NASD", "NAS", "NYSE", "AMEX"):
            # 해외 주문/체결 전체 조회 (CCLD_NCCS_DVSN="00")
            if self.is_paper:
                tr_id = "VTTS3035R"
                url = f"{self.base_url}/uapi/overseas-stock/v1/trading/inquire-ccnl"
                ovrs_excg = "NASD" if excg_upper in ("NASD", "NAS") else excg_upper
                params = {
                    "CANO": self.account_no,
                    "ACNT_PRDT_CD": "01",
                    "PDNO": "",
                    "ORD_STRT_DT": yesterday_str,
                    "ORD_END_DT": today_str,
                    "SLL_BUY_DVSN": "00",
                    "CCLD_NCCS_DVSN": "00",  # 00: 전체 (체결+미체결)
                    "OVRS_EXCG_CD": ovrs_excg,
                    "SORT_SQN": "DS",
                    "ORD_DT": "",
                    "ORD_GNO_BRNO": "",
                    "ODNO": "",
                    "CTX_AREA_NK200": "",
                    "CTX_AREA_FK200": "",
                }
            else:
                # 실전 매핑 (실전 미검증 주석: TTTS3035R 해외체결조회 전용)
                tr_id = "TTTS3035R"
                url = f"{self.base_url}/uapi/overseas-stock/v1/trading/inquire-ccnl"
                ovrs_excg = "NASD" if excg_upper in ("NASD", "NAS") else excg_upper
                params = {
                    "CANO": self.account_no,
                    "ACNT_PRDT_CD": "01",
                    "PDNO": "",
                    "ORD_STRT_DT": yesterday_str,
                    "ORD_END_DT": today_str,
                    "SLL_BUY_DVSN": "00",
                    "CCLD_NCCS_DVSN": "00",  # 00: 전체 (체결+미체결)
                    "OVRS_EXCG_CD": ovrs_excg,
                    "SORT_SQN": "DS",
                    "ORD_DT": "",
                    "ORD_GNO_BRNO": "",
                    "ODNO": "",
                    "CTX_AREA_NK200": "",
                    "CTX_AREA_FK200": "",
                }

            headers = {
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": tr_id,
                "Content-Type": "application/json; charset=utf-8",
            }
            get_kis_rate_limiter().acquire_sync(1.0)
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=10)
            except Exception as e:
                raise OpenOrdersInquiryError(f"Overseas recent orders HTTP request failed: {e}") from e

            if resp.status_code != 200:
                raise OpenOrdersInquiryError(f"Overseas recent orders inquiry HTTP {resp.status_code}: {resp.text}")

            try:
                data = resp.json()
            except Exception as e:
                raise OpenOrdersInquiryError(f"Invalid JSON in overseas recent orders: {e}") from e

            rt_cd = data.get("rt_cd")
            if rt_cd != "0":
                if data.get("msg_cd") == "70070000":
                    return []
                raise OpenOrdersInquiryError(f"Overseas recent orders inquiry failed: rt_cd={rt_cd}, msg={data.get('msg1')}")

            raw_orders = data.get("output", []) if "output" in data and isinstance(data["output"], list) else data.get("output1", [])
            for o in raw_orders:
                side_code = o.get("sll_buy_dvsn_cd") or o.get("sll_buy_dvsn", "")
                tot_qty = int(float(o.get("ft_ord_qty", 0) or o.get("ord_qty", 0) or 0))
                ccld_qty = int(float(o.get("ft_ccld_qty", 0) or o.get("ccld_qty", 0) or 0))
                ccld_prc = float(o.get("ft_ccld_unpr3", 0.0) or o.get("ccld_unpr", 0.0) or 0.0)
                parsed.append({
                    "odno": str(o.get("odno", "")),
                    "ticker": str(o.get("pdno", "")).strip().upper(),
                    "side": "BUY" if side_code == "02" else ("SELL" if side_code == "01" else side_code),
                    "quantity": tot_qty,
                    "ccld_qty": ccld_qty,
                    "ccld_prc": ccld_prc,
                    "raw": o,
                })
            return parsed
        else:
            raise OpenOrdersInquiryError(f"Unsupported exchange code for recent orders inquiry: {exchange}")
'''

recent_orders_pattern = re.compile(
    r"    def get_recent_orders_sync\(self, exchange: str = \"NASD\"\) -> List\[Dict\[str, Any\]\]:[\s\S]*?return parsed\n",
    re.MULTILINE
)
match_recent = recent_orders_pattern.search(content)
if match_recent:
    content = content[:match_recent.start()] + new_recent_orders_code + content[match_recent.end():]
    print("Successfully restored full order inquiry in get_recent_orders_sync!")
else:
    print("Warning: get_recent_orders_sync pattern not matched!")

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)


# 2. Add comprehensive tests to tests/test_broker_reconcile_and_orders.py
with open(test_orders_path, "r", encoding="utf-8") as f:
    test_orders_content = f.read()

# Replace or append the section 6 tests
new_tests_section = '''

# ==============================================================================
# 6. Legacy endpoint elimination and get_recent_orders_sync full verification
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
                "ft_ord_qty": "10",
                "ft_ccld_qty": "5",
                "ft_ccld_unpr3": "125.5",
            }
        ]
    }

    with patch("requests.get", return_value=mock_resp) as mock_get, \\
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

    with patch("requests.get", return_value=mock_resp), \\
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
    with patch("requests.get", return_value=mock_resp_err), \\
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        with pytest.raises(OpenOrdersInquiryError):
            broker.get_recent_orders_sync(exchange="NASD")


def test_get_recent_orders_sync_request_params_full_orders_00():
    """get_recent_orders_sync 요청 파라미터에 CCLD_NCCS_DVSN=00(해외) / CCLD_DVSN=00(국내)이 들어가는지 검증."""
    from app.services.kis_broker import KisBroker

    broker = KisBroker()
    broker.get_access_token_sync = MagicMock(return_value="mock_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"rt_cd": "0", "msg_cd": "MCA00000", "output": []}

    with patch("requests.get", return_value=mock_resp) as mock_get, \\
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        # 1. 해외 (NASD) -> CCLD_NCCS_DVSN = "00"
        broker.get_recent_orders_sync(exchange="NASD")
        _, kwargs_ovrs = mock_get.call_args
        assert kwargs_ovrs["params"]["CCLD_NCCS_DVSN"] == "00"

    mock_resp_dom = MagicMock()
    mock_resp_dom.status_code = 200
    mock_resp_dom.json.return_value = {"rt_cd": "0", "msg_cd": "MCA00000", "output1": []}

    with patch("requests.get", return_value=mock_resp_dom) as mock_get_dom, \\
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        # 2. 국내 (KRX) -> CCLD_DVSN = "00"
        broker.get_recent_orders_sync(exchange="KRX")
        _, kwargs_dom = mock_get_dom.call_args
        assert kwargs_dom["params"]["CCLD_DVSN"] == "00"


def test_get_recent_orders_sync_includes_filled_orders():
    """체결 완료 주문(nccs_qty=0, ccld_qty>0) mock 응답이 결과에 포함되고 ccld_qty·ccld_prc가 채워지는지 검증."""
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
                "odno": "77701",
                "pdno": "NVDA",
                "sll_buy_dvsn": "02",
                "ft_ord_qty": "20",
                "nccs_qty": "0",      # 미체결 0건 (완전 체결 상태)
                "ft_ccld_qty": "20",   # 체결 완료 20주
                "ft_ccld_unpr3": "122.5",
            }
        ]
    }

    with patch("requests.get", return_value=mock_resp), \\
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        orders = broker.get_recent_orders_sync(exchange="NASD")

        assert len(orders) == 1
        assert orders[0]["odno"] == "77701"
        assert orders[0]["quantity"] == 20
        assert orders[0]["ccld_qty"] == 20
        assert orders[0]["ccld_prc"] == 122.5


def test_get_execution_detail_sync_finds_filled_price_from_recent_orders():
    """get_execution_detail_sync가 체결 주문 mock에서 체결가를 찾는지 검증."""
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
                "odno": "88801",
                "pdno": "NVDA",
                "sll_buy_dvsn": "02",
                "ft_ord_qty": "15",
                "ft_ccld_qty": "15",
                "ft_ccld_unpr3": "130.0",
            }
        ]
    }

    with patch("requests.get", return_value=mock_resp), \\
         patch("app.services.kis_broker.get_kis_rate_limiter"):
        detail = broker.get_execution_detail_sync(order_no="88801", exchange="NASD")

        assert detail["success"] is True
        assert detail["odno"] == "88801"
        assert detail["ccld_qty"] == 15
        assert detail["ccld_prc"] == 130.0
        assert detail["is_filled"] is True
        assert detail["is_partial"] is False


def test_resolve_unknown_order_no_reorder_on_inquiry_exception(mock_autotrader):
    """_resolve_unknown_order: 최근 주문 조회 중 예외가 발생해도 재주문(requests.post)하지 않고 UNKNOWN을 유지함을 검증."""
    mock_broker = MagicMock()
    mock_broker.get_access_token_sync.return_value = "VALID_TOKEN"
    mock_broker.get_open_orders_sync.return_value = []
    # get_recent_orders_sync가 예외 발생 (Fail-Closed 원칙)
    mock_broker.get_recent_orders_sync.side_effect = OpenOrdersInquiryError("Broker inquiry network failed")

    with patch("app.services.kis_broker.get_kis_broker", return_value=mock_broker):
        with patch("requests.post", side_effect=requests.exceptions.Timeout("Connection timed out")) as mock_post:
            with patch("time.sleep"):
                result = mock_autotrader._execute_kis_order(
                    ticker="NVDA",
                    action="BUY",
                    shares=10,
                    price=120.0,
                    exchange_override="NASD"
                )

                # 검증:
                # 1. 1회차 post 타임아웃 이후 재발주(post 추가 호출)를 절대 하지 않음! (post 호출 1회)
                assert mock_post.call_count == 1
                # 2. 결과는 UNKNOWN 유지 (재주문 금지 및 수동 개입 대기)
                assert result.get("success") is False
                assert result.get("order_state") == "ORDER_UNKNOWN"
'''

# Replace section 6 in test_broker_reconcile_and_orders.py
sec6_marker = "# 6. Legacy endpoint elimination and get_recent_orders_sync verification"
if sec6_marker in test_orders_content:
    idx = test_orders_content.index(sec6_marker)
    # find comment line right before sec6_marker
    line_start = test_orders_content.rfind("# ===", 0, idx)
    test_orders_content = test_orders_content[:line_start] + new_tests_section
else:
    test_orders_content += new_tests_section

with open(test_orders_path, "w", encoding="utf-8") as f:
    f.write(test_orders_content)
print("Successfully updated test_broker_reconcile_and_orders.py with all required tests!")
