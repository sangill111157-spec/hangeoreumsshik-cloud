import sys
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')
import asyncio
from app.services.pod_manager import GrowthPod

p = GrowthPod()
try:
    asyncio.run(p.analyze({'stock_info': {'week_52_high': 0, 'current_price': 100}}))
except Exception as e:
    import traceback
    traceback.print_exc()
