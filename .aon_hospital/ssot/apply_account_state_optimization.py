import re

target_file = r"C:\trading\package\nvda_trading_system\backend\app\services\account_state.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

target = '''                try:
                    # 1. 주문가능 USD 및 환율 조회 (TR: 3007R)
                    # 2. 해외주식 종목별 잔고 조회 (TR: inquire-balance)
                    cash_res = await broker.get_orderable_cash_usd(ticker=probe_ticker, price=probe_price)
                    balance_res = await broker._get_us_balance()

                    orderable_cash = float(cash_res.get("orderable_cash_usd", 0.0))
                    exchange_rate = float(cash_res.get("exchange_rate", 0.0))
                    balance_source = str(cash_res.get("balance_source", "KIS_VTTS3007R"))

                    if orderable_cash <= 0:
                        logger.critical(f"[ACCOUNT_STATE] Broker orderable cash is non-positive: {orderable_cash}")

                    raw_holdings = balance_res.get("holdings", [])
                    positions: Dict[str, int] = {}
                    for h in raw_holdings:
                        sym = str(h.get("symbol", "")).upper()
                        qty = int(float(h.get("quantity", 0) or 0))
                        if sym:
                            positions[sym] = qty'''

replacement = '''                try:
                    # 1. 해외주식 종목별 잔고 조회 (TR: inquire-balance) 먼저 수행
                    balance_res = await broker._get_us_balance()
                    raw_holdings = balance_res.get("holdings", [])
                    positions: Dict[str, int] = {}
                    for h in raw_holdings:
                        sym = str(h.get("symbol", "")).upper()
                        qty = int(float(h.get("quantity", 0) or 0))
                        if sym and qty > 0:
                            positions[sym] = qty

                    # 2. 보유 종목이 0개이고 require_positive_cash=False인 경우(손절 감시), 불필요한 3007R 호출 건너뜀
                    if len(positions) == 0 and not require_positive_cash:
                        orderable_cash = self._cache.orderable_cash_usd if self._cache else 0.0
                        exchange_rate = self._cache.exchange_rate if self._cache else 1360.0
                        balance_source = "KIS_HOLDINGS_EMPTY_FAST"
                        logger.info("[ACCOUNT_STATE_FAST] Holdings is 0 & require_positive_cash=False: skipping 3007R orderable cash check")
                    else:
                        cash_res = await broker.get_orderable_cash_usd(ticker=probe_ticker, price=probe_price)
                        orderable_cash = float(cash_res.get("orderable_cash_usd", 0.0))
                        exchange_rate = float(cash_res.get("exchange_rate", 0.0))
                        balance_source = str(cash_res.get("balance_source", "KIS_VTTS3007R"))
                        if orderable_cash <= 0:
                            logger.critical(f"[ACCOUNT_STATE] Broker orderable cash is non-positive: {orderable_cash}")'''

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: account_state.py optimized")
else:
    print("TARGET NOT FOUND in account_state.py")
