kis_broker_path = r"C:\trading\package\nvda_trading_system\backend\app\services\kis_broker.py"

with open(kis_broker_path, "r", encoding="utf-8") as f:
    content = f.read()

target = '''# ------------------------------------------------------------------------------
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
    return broker.get_open_orders_sync(exchange=exchange, exchange_codes=exchange_codes)'''

replacement = '''# ------------------------------------------------------------------------------
# Module-level convenience wrappers
# ------------------------------------------------------------------------------
broker = get_kis_broker()


def get_domestic_balance_sync() -> Dict[str, Any]:
    return get_kis_broker().get_domestic_balance_sync()


def get_overseas_balance_sync() -> Dict[str, Any]:
    return get_kis_broker().get_overseas_balance_sync()


def get_open_orders_sync(
    exchange: Optional[str] = None,
    exchange_codes: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    return get_kis_broker().get_open_orders_sync(exchange=exchange or "NASD", exchange_codes=exchange_codes)'''

assert target in content, "target not found"
content = content.replace(target, replacement)

with open(kis_broker_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated kis_broker.py with get_kis_broker() wrappers.")
