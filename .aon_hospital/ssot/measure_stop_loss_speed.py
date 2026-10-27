import time
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, r"C:\trading\package\nvda_trading_system\backend")

from app.services.account_state import fetch_account_state
from app.services.scheduler import get_scheduler

async def measure():
    times = []
    print("=== MEASURING fetch_account_state(require_positive_cash=False) ===")
    for i in range(5):
        t0 = time.perf_counter()
        st = await fetch_account_state(require_positive_cash=False)
        dt = time.perf_counter() - t0
        times.append(dt)
        print(f"Run {i+1}: {dt:.4f}s | holdings={len(st.positions)} | source={st.balance_source}")
    print(f"Stats: Min={min(times):.4f}s, Max={max(times):.4f}s, Avg={sum(times)/len(times):.4f}s\n")

    print("=== MEASURING job_stop_loss_monitor 1 RUN ===")
    sched = get_scheduler()
    t0 = time.perf_counter()
    sched.job_stop_loss_monitor()
    dt = time.perf_counter() - t0
    print(f"job_stop_loss_monitor total time: {dt:.4f}s")

if __name__ == "__main__":
    asyncio.run(measure())
