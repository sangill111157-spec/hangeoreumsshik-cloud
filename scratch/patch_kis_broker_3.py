kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update overseas balance parsing to support cblc_qty / ovrs_cblc_qty and deduplicate by ovrs_pdno
target_holdings_loop = '''                raw_holdings = data.get("output1", [])
                for item in raw_holdings:
                    ticker = (item.get("ovrs_pdno") or item.get("pdno", "")).strip().upper()
                    qty = int(float(item.get("ovrs_cblc_qty", 0) or item.get("ord_psbl_qty", 0) or 0))
                    avg_p = float(item.get("pchs_avg_pric", 0.0) or 0.0)
                    if ticker and qty > 0:
                        if ticker in positions_map:
                            prev = positions_map[ticker]
                            total_qty = prev["quantity"] + qty
                            total_cost = (prev["quantity"] * prev["avg_price"]) + (qty * avg_p)
                            positions_map[ticker]["quantity"] = total_qty
                            positions_map[ticker]["avg_price"] = total_cost / total_qty if total_qty > 0 else 0.0
                        else:
                            positions_map[ticker] = {
                                "ticker": ticker,
                                "quantity": qty,
                                "avg_price": avg_p,
                            }'''

replacement_holdings_loop = '''                raw_holdings = data.get("output1", [])
                for item in raw_holdings:
                    ticker = (item.get("ovrs_pdno") or item.get("pdno", "")).strip().upper()
                    qty = int(float(item.get("ovrs_cblc_qty") or item.get("cblc_qty") or item.get("ord_psbl_qty") or 0))
                    avg_p = float(item.get("pchs_avg_pric", 0.0) or 0.0)
                    if ticker and qty > 0:
                        # ovrs_pdno 기준 중복 제거 (첫 조회된 거래소 우선)
                        if ticker not in positions_map:
                            positions_map[ticker] = {
                                "ticker": ticker,
                                "quantity": qty,
                                "avg_price": avg_p,
                            }'''

assert target_holdings_loop in content, "target_holdings_loop not found"
content = content.replace(target_holdings_loop, replacement_holdings_loop)

# 2. Update KisBroker.get_open_orders_sync signature to accept exchange_codes: Optional[List[str]] = None
target_open_orders_sig = 'def get_open_orders_sync(self, exchange: str = "NASD") -> List[Dict[str, Any]]:'
replacement_open_orders_sig = 'def get_open_orders_sync(self, exchange: str = "NASD", exchange_codes: Optional[List[str]] = None) -> List[Dict[str, Any]]:'

assert target_open_orders_sig in content, "target_open_orders_sig not found"
content = content.replace(target_open_orders_sig, replacement_open_orders_sig)

# 3. Update module-level wrapper get_open_orders_sync
target_wrapper = '''def get_open_orders_sync(
    exchange: Optional[str] = None,
    exchange_codes: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    return get_kis_broker().get_open_orders_sync(exchange=exchange or "NASD", exchange_codes=exchange_codes)'''

replacement_wrapper = '''def get_open_orders_sync(
    exchange: Optional[str] = None,
    exchange_codes: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    return get_kis_broker().get_open_orders_sync(exchange=exchange or "NASD", exchange_codes=exchange_codes)'''

# Target and replacement are already matching if signature updated

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated kis_broker.py with deduplication, cblc_qty, and exchange_codes!")
