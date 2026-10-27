# -*- coding: utf-8 -*-
import sys, os

backend_dir = r'C:\trading\package\nvda_trading_system\backend'

# 1. Update .gitignore
gi_path = os.path.join(backend_dir, '.gitignore')
with open(gi_path, 'r', encoding='utf-8') as f:
    gi_content = f.read()

# remove h.txt and h_full.txt lines
gi_lines = [l for l in gi_content.splitlines() if l.strip() not in ['h.txt', 'h_full.txt']]
with open(gi_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(gi_lines) + "\n")
print("Cleaned .gitignore")

# 2. Delete h.txt and h_full.txt if present
for h_file in ['h.txt', 'h_full.txt']:
    p = os.path.join(backend_dir, h_file)
    if os.path.exists(p):
        os.remove(p)
        print(f"Removed {p}")

# 3. Update docs/risk_and_exit_design.md if exists
docs_dir = os.path.join(backend_dir, 'docs')
os.makedirs(docs_dir, exist_ok=True)
risk_doc_path = os.path.join(docs_dir, 'risk_and_exit_design.md')

risk_note = """
## 📌 자동매수 파이프라인 및 DRY_RUN 관찰 범위 현황 (P30 기준)

1. **자동매수 전면 차단 (Fail-Closed) 상태**:
   - `scheduler.py:612`의 `calculate_master_signal(ticker)` 호출 시 하위 8개 분석 모듈(`modules`)이 주입되지 않아, Fail-Closed 원칙에 따라 `blocked_by_gate=True`, `signal=UNAVAILABLE`을 반환하며 매수 주문 경로가 전면 차단되어 있습니다.
   - 4축 TR-ID 라우팅, 해외 주문 payload, 8조합 테스트 등은 매수 경로에서 실행된 적이 없으며, `modules` 배선 작업은 향후 독립 사이클로 분리하여 진행합니다.

2. **DRY_RUN 관찰 범위**:
   - 현재 DRY_RUN 관찰 구간은 **실시간 현재가 및 포트폴리오 평단가 기반의 긴급 손절 매도 감시 경로**에 집중됩니다.
   - 손절 모니터링은 3-State(ACCEPTED/REJECTED/UNKNOWN), 3-Strike 지수 백오프, 1시간 주기 재알림 체계로 완전하게 가동됩니다.
"""

if os.path.exists(risk_doc_path):
    with open(risk_doc_path, 'r', encoding='utf-8') as f:
        existing_doc = f.read()
    if "자동매수 전면 차단" not in existing_doc:
        with open(risk_doc_path, 'w', encoding='utf-8') as f:
            f.write(existing_doc + "\n" + risk_note)
        print("Updated docs/risk_and_exit_design.md")
else:
    with open(risk_doc_path, 'w', encoding='utf-8') as f:
        f.write("# Risk and Exit Design\n" + risk_note)
    print("Created docs/risk_and_exit_design.md")
