kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update get_overseas_balance_exchange_codes
old_func = '''def get_overseas_balance_exchange_codes(is_paper: bool = True) -> list[str]:
    """해외 잔고 조회 대상 거래소 코드 목록 SSOT.
    모의투자는 KIS 버그로 인해 NASD/NYSE/AMEX 각 거래소별 개별 조회가 필요함.
    실전투자: 매핑만 정의하고 '실전 미검증' 주석 유지.
    """
    return ["NASD", "NYSE", "AMEX"]'''

new_func = '''def get_overseas_balance_exchange_codes(is_paper: bool = True) -> list[str]:
    """해외 잔고 조회 대상 거래소 코드 목록 SSOT.
    - 모의(is_paper=True): NASD, NYSE, AMEX 3개 거래소 개별 조회 후 합산.
    - 실전(is_paper=False): NASD (실전 미검증).
    """
    if is_paper:
        return ["NASD", "NYSE", "AMEX"]
    # [실전 미검증] 실전투자 API 경로는 향후 검증 필요
    return ["NASD"]'''

assert old_func in content, "old_func not found"
content = content.replace(old_func, new_func)

# 2. Add module-level wrappers at bottom of file
module_wrappers = '''

# ------------------------------------------------------------------------------
# Module-level convenience wrappers
# ------------------------------------------------------------------------------
def get_domestic_balance_sync() -> Dict[str, Any]:
    return broker.get_domestic_balance_sync()


def get_overseas_balance_sync() -> Dict[str, Any]:
    return broker.get_overseas_balance_sync()


def get_open_orders_sync(
    exchange: Optional[str] = None,
    exchange_codes: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    return broker.get_open_orders_sync(exchange=exchange, exchange_codes=exchange_codes)
'''

content += module_wrappers

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated kis_broker.py with updated exchange codes and module-level wrappers.")
