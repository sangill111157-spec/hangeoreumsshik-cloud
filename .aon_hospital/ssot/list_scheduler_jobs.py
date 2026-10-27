import sys
sys.path.insert(0, r'C:\trading\package\nvda_trading_system\backend')
from app.services.scheduler import TradingScheduler

sched = TradingScheduler()
print("All jobs in TradingScheduler:")
for method_name in dir(sched):
    if method_name.startswith("job_") or method_name.startswith("_job_"):
        print("-", method_name)
