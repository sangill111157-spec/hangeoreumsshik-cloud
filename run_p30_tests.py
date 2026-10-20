# -*- coding: utf-8 -*-
import sys, os, subprocess, json, inspect, asyncio, time
from typing import Dict, Any, Optional

# 테스트용 기본 환경변수 주입 (Settings 검증 통과용)
os.environ.setdefault("KIS_APP_KEY", "test_mock_app_key")
os.environ.setdefault("KIS_APP_SECRET", "test_mock_app_secret")
os.environ.setdefault("SECRET_KEY", "test_mock_secret_key_32_characters_long_min")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_bot_token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "test_chat_id")

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("==================================================")
print("TEST 1: Loop-Binding Fake Notifier (Consecutive 2-Calls)")
print("==================================================")

class LoopBoundFakeNotifier:
    """
    첫 호출 시 이벤트 루프를 기록하고, 다른 루프(또는 새 루프)에서 호출되면 예외를 던지는 Fake Notifier.
    만약 __init__ 시점의 루프와 다른 루프에서 실행되면 RuntimeError 발생.
    """
    def __init__(self, bound_loop: Optional[asyncio.AbstractEventLoop] = None):
        self.bound_loop = bound_loop
        self.call_count = 0
        self.chat_id = "test_chat_id"
        self.enabled = True
        self.calls = []

    async def send_message(self, message):
        current_loop = asyncio.get_running_loop()
        self.call_count += 1
        self.calls.append((self.call_count, current_loop, message.text))
        
        if self.bound_loop is not None and current_loop != self.bound_loop:
            raise RuntimeError(
                f"[LOOP_MISMATCH_ERROR] FakeNotifier bound to loop {id(self.bound_loop)}, "
                f"but called from loop {id(current_loop)} on call #{self.call_count}"
            )
        return True

from app.services.scheduler import TradingScheduler

def test_fake_notifier_execution():
    print("\n--- Case A: BackgroundScheduler Worker Thread without _loop (asyncio.run fallback) ---")
    sched = TradingScheduler(notifier_enabled=True)
    
    # 가상의 메인 루프 생성
    main_loop = asyncio.new_event_loop()
    
    # Fake notifier bound to main_loop
    fake_notifier_bound = LoopBoundFakeNotifier(bound_loop=main_loop)
    sched.notifier = fake_notifier_bound
    sched._loop = None  # _loop 없음 (P29 상태)

    print("Executing _send_telegram Call 1 with loop-bound fake notifier...")
    sched._send_telegram("Message 1 (Test)")
    print("Executing _send_telegram Call 2 with loop-bound fake notifier...")
    sched._send_telegram("Message 2 (Test)")
    print(f"Fake Notifier call_count: {fake_notifier_bound.call_count}")

    print("\n--- Case B: Unbound Fake Notifier (Per-call independent loop simulation) ---")
    fake_notifier_unbound = LoopBoundFakeNotifier(bound_loop=None)
    sched.notifier = fake_notifier_unbound
    sched._send_telegram("Message 1 (Unbound)")
    sched._send_telegram("Message 2 (Unbound)")
    print(f"Unbound Fake Notifier call_count: {fake_notifier_unbound.call_count}")
    for idx, loop_obj, txt in fake_notifier_unbound.calls:
        print(f"  Call {idx}: Loop ID = {id(loop_obj)}, Text = {txt}")

test_fake_notifier_execution()

print("\n==================================================")
print("TEST 2: calculate_master_signal Call & Signature Inspection")
print("==================================================")
from app.services.master_signal import calculate_master_signal, MasterSignalResult

sig_cms = inspect.signature(calculate_master_signal)
print(f"inspect.signature(calculate_master_signal): {sig_cms}")

print("\nCalling calculate_master_signal('NVDA') without modules:")
res_no_mod = calculate_master_signal("NVDA")
print(f"Result type: {type(res_no_mod)}")
print(f"Result score: {getattr(res_no_mod, 'score', None)}, signal: {getattr(res_no_mod, 'signal', None)}, confidence: {getattr(res_no_mod, 'confidence', None)}")
print(f"Result blocked_by_gate: {getattr(res_no_mod, 'blocked_by_gate', None)}")
print(f"Result action: {getattr(res_no_mod, 'action', None)}")

print("\nCalling calculate_master_signal('NVDA', modules={...8 modules...}):")
sample_modules = {
    'technical': {'score': 70.0, 'confidence': 80, 'signal': 'BUY', 'available': True},
    'options_flow': {'score': 65.0, 'confidence': 75, 'signal': 'BUY', 'available': True},
    'news_sentiment': {'score': 60.0, 'confidence': 70, 'signal': 'BUY', 'available': True},
    'market_trend': {'score': 65.0, 'confidence': 70, 'signal': 'BUY', 'available': True},
    'social': {'score': 55.0, 'confidence': 60, 'signal': 'BUY', 'available': True},
    'insider': {'score': 50.0, 'confidence': 50, 'signal': 'HOLD', 'available': True},
    'macro': {'score': 60.0, 'confidence': 65, 'signal': 'BUY', 'available': True},
    'ai_inference': {'score': 70.0, 'confidence': 80, 'signal': 'BUY', 'available': True},
}
res_with_mod = calculate_master_signal("NVDA", modules=sample_modules)
print(f"Result score: {getattr(res_with_mod, 'score', None)}, signal: {getattr(res_with_mod, 'signal', None)}, confidence: {getattr(res_with_mod, 'confidence', None)}")
print(f"Result blocked_by_gate: {getattr(res_with_mod, 'blocked_by_gate', None)}")
