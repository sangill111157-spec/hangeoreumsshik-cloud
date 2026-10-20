kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update get_overseas_balance_exchange_codes
target = '''def get_overseas_balance_exchange_codes(is_paper: bool = True) -> list[str]:
    """해외 잔고 조회 대상 거래소 코드 목록 SSOT
    - 모의투자: NASD, NYSE, AMEX 순회 합산 (1단계 실측 검증 완료)
    - 실전투자: NASD, NYSE, AMEX 순회 합산 (실전 미검증)
    """
    return ["NASD", "NYSE", "AMEX"]'''

replacement = '''def get_overseas_balance_exchange_codes(is_paper: bool = True) -> list[str]:
    """해외 잔고 조회 대상 거래소 코드 목록 SSOT
    - 모의투자: NASD, NYSE, AMEX 순회 합산 (1단계 실측 검증 완료)
    - 실전투자: NASD (실전 미검증 주석)
    """
    if is_paper:
        return ["NASD", "NYSE", "AMEX"]
    # [실전 미검증] 실전투자 API 경로는 향후 검증 필요
    return ["NASD"]'''

assert target in content, "target not found"
content = content.replace(target, replacement)

# 2. Add module-level wrappers at end of file if not present
wrapper_str = "def get_domestic_balance_sync() -> Dict[str, Any]:"
if wrapper_str not in content:
    content += '''

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

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated kis_broker.py!")
