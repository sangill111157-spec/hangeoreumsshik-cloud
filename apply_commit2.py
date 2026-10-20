# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sched_file = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')

with open(sched_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add _telegram_fail_count to __init__
if "self._telegram_fail_count" not in content:
    content = content.replace(
        "self._stop_loss_disabled_last_alert: float = 0.0",
        "self._stop_loss_disabled_last_alert: float = 0.0\n        self._telegram_fail_count: int = 0"
    )

# 2. Update _send_telegram
old_send_block = """            if loop and loop.is_running():
                try:
                    coro = asyncio.wait_for(self.notifier.send_message(msg), timeout=5.0)
                    future = asyncio.run_coroutine_threadsafe(coro, loop)
                    self._bg_tasks.add(future)
                    def _done(f):
                        self._bg_tasks.discard(f)
                    future.add_done_callback(_done)
                except Exception as e:
                    logger.error(f"[TELEGRAM_THREADSAFE] Failed: {e}")
            else:
                try:
                    asyncio.run(asyncio.wait_for(self.notifier.send_message(msg), timeout=5.0))
                except Exception as e:
                    logger.error(f"[TELEGRAM_SYNC_FALLBACK] Failed: {e}")
        except Exception as e:
            logger.error(f"Failed to send telegram message: {e}")"""

new_send_block = """            if loop and loop.is_running():
                try:
                    coro = asyncio.wait_for(self.notifier.send_message(msg), timeout=5.0)
                    future = asyncio.run_coroutine_threadsafe(coro, loop)
                    self._bg_tasks.add(future)
                    def _done(f):
                        self._bg_tasks.discard(f)
                    future.add_done_callback(_done)
                except Exception as e:
                    self._telegram_fail_count += 1
                    logger.critical(f"🚨 [TELEGRAM_THREADSAFE] Failed (consecutive fails: {self._telegram_fail_count}): {e}")
            else:
                try:
                    asyncio.run(asyncio.wait_for(self.notifier.send_message(msg), timeout=5.0))
                    self._telegram_fail_count = 0
                except Exception as e:
                    self._telegram_fail_count += 1
                    logger.critical(f"🚨 [TELEGRAM_SYNC_FALLBACK] Failed (consecutive fails: {self._telegram_fail_count}): {e}")
        except Exception as e:
            self._telegram_fail_count += 1
            logger.critical(f"🚨 [TELEGRAM_TOP_FAIL] Failed to send telegram message (consecutive fails: {self._telegram_fail_count}): {e}")"""

if old_send_block in content:
    content = content.replace(old_send_block, new_send_block)
    with open(sched_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated _send_telegram logging and consecutive fail counter in scheduler.py")
else:
    print("WARNING: old_send_block not matched exactly!")
