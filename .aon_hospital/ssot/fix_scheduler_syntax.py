with open('app/services/scheduler.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def _on_scheduler_job_event')
# find beginning of that line
start_line = text.rfind('\n', 0, idx) + 1
end_idx = text.find('def _load_stop_loss_state', idx)

method_str = """    def _on_scheduler_job_event(self, event):
        \"\"\"손절 모니터 잡의 스킵(max_instances 초과) 또는 미스파이어 감지 시 CRITICAL 경보 발송 (5분 스로틀)\"\"\"
        if getattr(event, 'job_id', '') == "stop_loss_monitor":
            now_ts = time.time()
            if now_ts - getattr(self, '_stop_loss_skip_last_alert', 0.0) > 300.0:
                self._stop_loss_skip_last_alert = now_ts
                msg = (
                    f"🚨🚨 *[손절 감시 틱 스킵/미스파이어 발생]* 손절 모니터링 잡이 시스템 지연/유량 대기로 건너뛰어졌습니다!\\n"
                    f"이벤트 코드: {event.code} (max_instances 초과 또는 misfire 발생)"
                )
                logger.critical(msg)
                self._send_telegram(msg)

"""

text = text[:start_line] + method_str + text[end_idx:]

with open('app/services/scheduler.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Indentation fixed accurately!")
