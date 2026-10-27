# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
sched_file = os.path.join(backend_dir, 'app', 'services', 'scheduler.py')

with open(sched_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix __init__ and _load_stop_loss_state clean layout
bad_block = """        self._stop_loss_locked_tickers: Dict[str, str] = {}
        self._stop_loss_last_re_alert: Dict[str, float] = {}
        self._stop_loss_disabled: bool = False

        self._load_stop_loss_state()
        self._check_pipeline_health_on_startup()
        self._initialized = True
        logger.info("TradingScheduler initialized")

    def _load_stop_loss_state(self):
        \"\"\"stop_loss_state.json에서 손절 발사 및 실패 상태 로드 (손상 시 fail-closed)\"\"\"
        state_file = STOP_LOSS_STATE_FILE
        try:
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._stop_loss_fired = data.get('stop_loss_fired', {})
                    self._price_fail_count = data.get('price_fail_count', {})
                    self._gate_blocked_alert_fired = data.get('gate_blocked_alert_fired', {})
                    self._stop_loss_reject_count = data.get('reject_count', {})
                    self._stop_loss_next_retry = data.get('next_retry', {})
                    self._stop_loss_locked_tickers = data.get('locked_tickers', {})
                    self._stop_loss_last_re_alert = data.get('last_re_alert', {})
            else:
                self._stop_loss_fired = {}
                self._price_fail_count = {}
                self._gate_blocked_alert_fired = {}
                self._stop_loss_reject_count = {}
                self._stop_loss_next_retry = {}
                self._stop_loss_locked_tickers = {}
                self._stop_loss_last_re_alert = {}
            self._stop_loss_disabled = False
            self._stop_loss_disabled_last_alert: float = 0.0
        self._telegram_fail_count: int = 0 

            # 재기동 시 잠금 종목이 존재하면 CRITICAL 보고"""

good_block = """        self._stop_loss_locked_tickers: Dict[str, str] = {}
        self._stop_loss_last_re_alert: Dict[str, float] = {}
        self._stop_loss_disabled: bool = False
        self._stop_loss_disabled_last_alert: float = 0.0
        self._telegram_fail_count: int = 0

        self._load_stop_loss_state()
        self._check_pipeline_health_on_startup()
        self._initialized = True
        logger.info("TradingScheduler initialized")

    def _load_stop_loss_state(self):
        \"\"\"stop_loss_state.json에서 손절 발사 및 실패 상태 로드 (손상 시 fail-closed)\"\"\"
        state_file = STOP_LOSS_STATE_FILE
        try:
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._stop_loss_fired = data.get('stop_loss_fired', {})
                    self._price_fail_count = data.get('price_fail_count', {})
                    self._gate_blocked_alert_fired = data.get('gate_blocked_alert_fired', {})
                    self._stop_loss_reject_count = data.get('reject_count', {})
                    self._stop_loss_next_retry = data.get('next_retry', {})
                    self._stop_loss_locked_tickers = data.get('locked_tickers', {})
                    self._stop_loss_last_re_alert = data.get('last_re_alert', {})
            else:
                self._stop_loss_fired = {}
                self._price_fail_count = {}
                self._gate_blocked_alert_fired = {}
                self._stop_loss_reject_count = {}
                self._stop_loss_next_retry = {}
                self._stop_loss_locked_tickers = {}
                self._stop_loss_last_re_alert = {}
            self._stop_loss_disabled = False

            # 재기동 시 잠금 종목이 존재하면 CRITICAL 보고"""

if bad_block in content:
    content = content.replace(bad_block, good_block)
    with open(sched_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully cleaned up scheduler.py init & load block")
else:
    print("Warning: bad_block not found directly, performing line-based fix")
