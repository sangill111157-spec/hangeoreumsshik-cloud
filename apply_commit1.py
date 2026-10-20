# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update app/services/scheduler.py
sched_file = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')
with open(sched_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add _stop_loss_disabled_last_alert in __init__
if "_stop_loss_disabled_last_alert" not in content:
    content = content.replace(
        "self._stop_loss_disabled = False",
        "self._stop_loss_disabled = False\n        self._stop_loss_disabled_last_alert: float = 0.0"
    )

# Update _load_stop_loss_state error handling
old_load_err = """        except Exception as e:
            logger.critical(f"🚨 [손절 상태 로드 실패 - Fail-Closed 차단] stop_loss_state.json 손상: {e}")
            self._stop_loss_disabled = True"""

new_load_err = """        except Exception as e:
            logger.critical(f"🚨 [손절 상태 로드 실패 - Fail-Closed 차단] stop_loss_state.json 손상: {e}")
            self._stop_loss_disabled = True
            self._stop_loss_disabled_last_alert = time.time()"""

if old_load_err in content:
    content = content.replace(old_load_err, new_load_err)

# Update job_stop_loss_monitor disabled check
old_monitor_check = """        if self._stop_loss_disabled:
            logger.critical("🚨 [STOP_LOSS_DISABLED] 상태 파일 손상으로 손절 모니터링이 중단된 상태입니다. (Fail-Closed)")
            return"""

new_monitor_check = """        if self._stop_loss_disabled:
            now_ts = time.time()
            if now_ts - getattr(self, "_stop_loss_disabled_last_alert", 0.0) >= 3600.0:
                alert_msg = (
                    "🚨🚨 *[긴급 손절 감시 중단 1시간 재알림]*\\n"
                    "stop_loss_state.json 상태 파일 손상으로 손절 모니터링이 중단(Fail-Closed)되어 있습니다!\\n"
                    "포지션이 무방비 상태이오니 HTS/MTS에서 수동으로 포지션을 확인하십시오."
                )
                logger.critical(alert_msg)
                self._send_telegram(alert_msg)
                self._stop_loss_disabled_last_alert = now_ts
            else:
                logger.critical("🚨 [STOP_LOSS_DISABLED] 상태 파일 손상으로 손절 모니터링이 중단된 상태입니다. (Fail-Closed)")
            return"""

if old_monitor_check in content:
    content = content.replace(old_monitor_check, new_monitor_check)

with open(sched_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app/services/scheduler.py")

# 2. Update app/schemas/nvda.py
schema_file = os.path.join(backend_dir, 'app', 'schemas', 'nvda.py')
with open(schema_file, 'r', encoding='utf-8') as f:
    s_content = f.read()

if "stop_loss_disabled: bool" not in s_content:
    s_content = s_content.replace(
        "    stop_loss_locked_tickers: Dict[str, str] = {}\n    live_order_gate_open: bool = False",
        "    stop_loss_locked_tickers: Dict[str, str] = {}\n    stop_loss_disabled: bool = False\n    live_order_gate_open: bool = False"
    )
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(s_content)
    print("Updated app/schemas/nvda.py")

# 3. Update app/main.py
main_file = os.path.join(backend_dir, 'app', 'main.py')
with open(main_file, 'r', encoding='utf-8') as f:
    m_content = f.read()

if "stop_loss_disabled=sl_disabled" not in m_content:
    m_content = m_content.replace(
        """    from app.services.scheduler import get_scheduler
    sched = get_scheduler()
    locked = getattr(sched, "_stop_loss_locked_tickers", {})
    gate_open = is_live_order_enabled()

    return HealthCheckResponse(
        status="ok" if all("unhealthy" not in s for s in services.values()) else "degraded",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services=services,
        auto_trade_effective=auto_trade_eff,
        stop_loss_locked_tickers=locked,
        live_order_gate_open=gate_open
    )""",
        """    from app.services.scheduler import get_scheduler
    sched = get_scheduler()
    locked = getattr(sched, "_stop_loss_locked_tickers", {})
    sl_disabled = getattr(sched, "_stop_loss_disabled", False)
    gate_open = is_live_order_enabled()

    is_degraded = (
        any("unhealthy" in s for s in services.values()) or
        sl_disabled or
        bool(locked)
    )

    return HealthCheckResponse(
        status="degraded" if is_degraded else "ok",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services=services,
        auto_trade_effective=auto_trade_eff,
        stop_loss_locked_tickers=locked,
        stop_loss_disabled=sl_disabled,
        live_order_gate_open=gate_open
    )"""
    )
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(m_content)
    print("Updated app/main.py")
