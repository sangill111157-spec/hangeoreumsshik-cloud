# -*- coding: utf-8 -*-
import os, sys

# Target backend directory
backend_dir = r"C:\trading\package\nvda_trading_system\backend"
os.chdir(backend_dir)

# 1. Patch app/services/scheduler.py
with open("app/services/scheduler.py", "r", encoding="utf-8-sig") as f:
    sched_text = f.read()

# Remove duplicate item["_normalized_symbol"] = sym
dup_str = '        item["_normalized_symbol"] = sym\n        item["_normalized_symbol"] = sym'
assert dup_str in sched_text, "Duplicate not found"
sched_text = sched_text.replace(dup_str, '        item["_normalized_symbol"] = sym', 1)

# Fix contract fail count in line 904 - downgrade to local log, no dynamic instance attr creation
old_contract = '''                ticker = item.get("_normalized_symbol")
                if not ticker:
                    # Contract violation: item missing _normalized_symbol after filter (should never happen)
                    self._stop_loss_scan_contract_fail_count = getattr(self, "_stop_loss_scan_contract_fail_count", 0) + 1
                    logger.critical(f"🔴 [STOP_LOSS_CONTRACT_FAIL] item missing _normalized_symbol after filter (count={self._stop_loss_scan_contract_fail_count}), skipping")
                    continue'''

new_contract = '''                ticker = item.get("_normalized_symbol")
                if not ticker:
                    # Contract violation: item missing _normalized_symbol after filter (should never happen)
                    logger.critical(f"🔴 [STOP_LOSS_CONTRACT_FAIL] item missing _normalized_symbol after filter, skipping: {item}")
                    continue'''

assert old_contract in sched_text, "Old contract block not found"
sched_text = sched_text.replace(old_contract, new_contract, 1)

# Add T model 6-term table in docstring
old_t_comment = '''# [BACKLOG_6] 손절 모니터링 대상 종목 수 Cold 틱 안전 한도 상수
# 도출식: 정본 T 모델 (T_pre=3.0s, p99 t_y=0.5381s, 페이싱 1.0s, 백오프 6.0s 기준 59.27s < 60s)
# [BACKLOG_12 정본 T 모델 및 버킷 만충/동적 결손 방어]
# T = T_pre(3.0s) + N*t_y + T_rate_limit(1.0s~3.5s) + 3.0*K_order + 3.5*K_tg + B_backoff(3.5s~6.0s) <= 59.27s < 60.0s'''

new_t_comment = '''# [BACKLOG_6] 손절 모니터링 대상 종목 수 Cold 틱 안전 한도 상수
# 도출식: 정본 T 모델 (T_pre=3.0s, p99 t_y=0.5381s, 페이싱 1.0s, 백오프 6.0s 기준 59.27s < 60s)
# [BACKLOG_12 / BACKLOG_13 정본 T 모델 6항 표 및 버킷 만충/동적 결손 방어]
# | 항           | 값 (초) | 출처 / 비고                                         |
# |-------------|---------|-----------------------------------------------------|
# | T_pre       | 3.0     | KIS 토큰 갱신 최악 (kis_broker.py:967, :1145)        |
# | T_p99       | 3.767   | 7 * 0.5381s (N=7 p99)                               |
# | T_pacing    | 1.0     | 공식 확정 페이싱 항                                   |
# | T_scan      | 45.5    | N=7 스캔 (429 백오프 및 직렬 대기 한도)               |
# | 기저 소계   | 53.267  | 정상 최악 기저 소계                                  |
# | T_deficit   | 2.5     | capacity/rate = 5/2.0 완충 시간                      |
# | T_budget_eff| 3.5     | max(0.0, 6.0 - 2.5) 실효 백오프 예산                  |
# | 합계        | 59.267  | < 60.0s (1분 모니터링 주기 엄격 보장)                 |
# T = T_pre(3.0s) + N*t_y + T_rate_limit(1.0s~3.5s) + 3.0*K_order + 3.5*K_tg + B_backoff(3.5s~6.0s) <= 59.27s < 60.0s'''

assert old_t_comment in sched_text, "Old T comment not found"
sched_text = sched_text.replace(old_t_comment, new_t_comment, 1)

# Save without BOM (UTF-8 no BOM)
with open("app/services/scheduler.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(sched_text)

print("app/services/scheduler.py patched successfully (no BOM)!")

# 2. Patch tests/test_stop_loss_ticker_missing.py
with open("tests/test_stop_loss_ticker_missing.py", "r", encoding="utf-8-sig") as f:
    test_text = f.read()

old_doc1 = '''def test_whitespace_symbol_falls_back_to_valid_ticker():
    """[BACKLOG_13 / Blocking B] symbol이 공백('   ')이어도 유효한 ticker('NVDA')가 존재하면'''

new_doc1 = '''def test_whitespace_symbol_falls_back_to_valid_ticker():
    """[역할 1: 필터 회귀 검증 / BACKLOG_13 Blocking B] symbol이 공백('   ')이어도 유효한 ticker('NVDA')가 존재하면'''

assert old_doc1 in test_text, "old_doc1 not found"
test_text = test_text.replace(old_doc1, new_doc1, 1)

old_doc2 = '''def test_whitespace_symbol_falls_back_to_valid_ticker_in_filter():
    """[BACKLOG_13 / Blocking B] symbol='   ', ticker='NVDA'
    -> filter: anomaly=0, valid=1, _normalized_symbol='NVDA'
    """'''

new_doc2 = '''def test_whitespace_symbol_falls_back_to_valid_ticker_in_filter():
    """[역할 2: 계약 캐시 검증 / BACKLOG_13 Blocking B] symbol='   ', ticker='NVDA'
    -> filter 통과 후 _normalized_symbol='NVDA' 캐시 주입 및 정규화 값 일치 단정.
    """'''

assert old_doc2 in test_text, "old_doc2 not found"
test_text = test_text.replace(old_doc2, new_doc2, 1)

# Save without BOM (UTF-8 no BOM)
with open("tests/test_stop_loss_ticker_missing.py", "w", encoding="utf-8", newline="\n") as f:
    f.write(test_text)

print("tests/test_stop_loss_ticker_missing.py patched successfully (no BOM)!")
