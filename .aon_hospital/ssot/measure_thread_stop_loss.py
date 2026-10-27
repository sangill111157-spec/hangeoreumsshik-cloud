import time
import asyncio
import os
import sys
import threading

sys.path.insert(0, r"C:\trading\package\nvda_trading_system\backend")

from app.services.account_state import fetch_account_state
from app.services.scheduler import get_scheduler

def test_in_worker_thread():
    print("=== MEASURING job_stop_loss_monitor in ThreadPool (like APScheduler) ===")
    sched = get_scheduler()
    t0 = time.perf_counter()
    sched.job_stop_loss_monitor()
    dt = time.perf_counter() - t0
    print(f"job_stop_loss_monitor worker thread time: {dt:.4f}s")

if __name__ == "__main__":
    t = threading.Thread(target=test_in_worker_thread)
    t.start()
    t.join()
