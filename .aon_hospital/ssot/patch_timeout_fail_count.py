# -*- coding: utf-8 -*-
import os, sys

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update scheduler.py: remove fail_count increment from TimeoutError branches
sched_p = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')
with open(sched_p, 'r', encoding='utf-8') as f:
    c = f.read()

# Replace async timeout block
old_async_to = '''                    except (TimeoutError, concurrent.futures.TimeoutError):
                        self._telegram_fail_count += 1
                        logger.critical(f"🚨 [TELEGRAM_ASYNC_TIMEOUT] Message delivery timed out after {timeout}s (consecutive: {self._telegram_fail_count})")
                        return False'''

new_async_to = '''                    except (TimeoutError, concurrent.futures.TimeoutError):
                        # [BACKLOG_1] 타임아웃은 미확정 상태이므로 전송 실패 카운터(_telegram_fail_count) 증가 제외 (3-strike 오작동 방지)
                        logger.critical(f"🚨 [TELEGRAM_ASYNC_TIMEOUT] Message delivery timed out after {timeout}s; unconfirmed, fail count unchanged ({self._telegram_fail_count})")
                        return False'''

assert old_async_to in c, "old_async_to not found in scheduler.py"
c = c.replace(old_async_to, new_async_to)

# Replace sync timeout block
old_sync_to = '''                except (TimeoutError, asyncio.TimeoutError):
                    self._telegram_fail_count += 1
                    logger.critical(f"🚨 [TELEGRAM_SYNC_TIMEOUT] Message delivery timed out after {timeout}s (consecutive: {self._telegram_fail_count})")
                    return False'''

new_sync_to = '''                except (TimeoutError, asyncio.TimeoutError):
                    # [BACKLOG_1] 타임아웃은 미확정 상태이므로 전송 실패 카운터(_telegram_fail_count) 증가 제외 (3-strike 오작동 방지)
                    logger.critical(f"🚨 [TELEGRAM_SYNC_TIMEOUT] Message delivery timed out after {timeout}s; unconfirmed, fail count unchanged ({self._telegram_fail_count})")
                    return False'''

assert old_sync_to in c, "old_sync_to not found in scheduler.py"
c = c.replace(old_sync_to, new_sync_to)

with open(sched_p, 'w', encoding='utf-8') as f:
    f.write(c)
print("Updated scheduler.py cleanly!")

# 2. Update test_telegram_delivery_confirmation.py: assert fail_count == 0 on timeout
test_p = os.path.join(backend_dir, 'tests', 'test_telegram_delivery_confirmation.py')
with open(test_p, 'r', encoding='utf-8') as f:
    tc = f.read()

old_test_to = '''        # 타임아웃으로 전송 미확인이므로 마커 미설정
        assert "NVDA" not in sched._stop_loss_lock_daily_alert
        assert sched._telegram_fail_count == 1'''

new_test_to = '''        # 타임아웃으로 전송 미확인이므로 마커 미설정, 단 미확정 상태이므로 실패 카운터는 증가하지 않고 0 유지 (3-strike 오작동 방지)
        assert "NVDA" not in sched._stop_loss_lock_daily_alert
        assert sched._telegram_fail_count == 0'''

assert old_test_to in tc, "old_test_to not found in test file"
tc = tc.replace(old_test_to, new_test_to)

with open(test_p, 'w', encoding='utf-8') as f:
    f.write(tc)
print("Updated test_telegram_delivery_confirmation.py cleanly!")
