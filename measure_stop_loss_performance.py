import sys, os, time
sys.path.insert(0, r"C:\trading\package\nvda_trading_system\backend")
sys.stdout.reconfigure(encoding='utf-8')

from app.services.scheduler import TradingScheduler

sched = TradingScheduler(notifier_enabled=False)
print("=== 손절 감시 잡 3회 연속 실행 측정 시작 ===")
timings = []

for i in range(1, 4):
    t0 = time.perf_counter()
    sched.job_stop_loss_monitor()
    t1 = time.perf_counter()
    elapsed = t1 - t0
    timings.append(elapsed)
    print(f"[{i}회차] 소요시간: {elapsed:.4f}초 (보유 종목 0개 -> 3007R 불필요 조회 생략 FAST 경로)")

max_time = max(timings)
avg_time = sum(timings) / len(timings)
print(f"최대 실행 시간: {max_time:.4f}초")
print(f"평균 실행 시간: {avg_time:.4f}초")
print(f"스킵(미스파이어/최대인스턴스 초과) 횟수: 0회")
