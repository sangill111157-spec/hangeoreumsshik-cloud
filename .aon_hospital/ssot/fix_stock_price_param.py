# -*- coding: utf-8 -*-
ms_file = r'C:\trading\package\nvda_trading_system\backend\app\services\master_signal.py'
with open(ms_file, 'r', encoding='utf-8') as f:
    content = f.read()

t = """        events: dict,
        correlation: dict,
        symbol: str = "NVDA",
        pod_composite_signal: Optional[str] = None"""

r = """        events: dict,
        correlation: dict,
        symbol: str = "NVDA",
        stock_price: float = 100.0,
        account_balance: float = 100000.0,
        pod_composite_signal: Optional[str] = None"""

content = content.replace(t, r, 1)

with open(ms_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("ADDED stock_price & account_balance parameters to calculate_final_master_signal")
