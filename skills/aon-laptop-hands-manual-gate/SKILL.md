# aon-laptop-hands-manual-gate (31번째 정식 스킬)

- 버전: v11.34-AON-LAPTOP-HANDS · 항체: R1~R35
- 기관: 제11기관 노트북 만능 제어 수족 & 중요 결재 수동 ON/OFF 마스터 스위치 (`rgon_laptop_hands.py`)
- 철학: 주역 #60 수택절(節, 마디의 절제) · #62 뇌산소과(小過, 작은 일은 열고 큰 일은 잠근다) · #14 화천대유(大有, 크게 가진 자의 겸손)

## 1. 수동 스위치
- `master_approval_on` 기본값은 False(🔒 철통잠금)입니다.
- `gates`: finance_payment(OFF) · laptop_app_browser(ON) · file_modify_delete(OFF) · external_dispatch(OFF)
- API: `set_master_gate(on)`, `set_category_gate(cat, on)`, `lock_all_gates()`
- 상태 파일: `rgon_manual_gate_state.json`, `docs/rgon_manual_gate_state.json`

## 2. 검증 게이트 `can_execute_critical(category, tier=3)`
- Tier 3 또는 중요 카테고리는 마스터 ON과 카테고리 ON이 모두 충족돼야 `allowed: True`입니다. 하나라도 OFF면 승인을 눌러도 집행 0건입니다.
- 카테고리가 여러 개 섞였거나 분류되지 않으면 `unknown`으로 보고, 마스터와 중요 3종이 모두 ON이어야 합니다.

## 3. 노트북 4대 작업 `execute_laptop_action(action_type, target, dry_run=True, approved=False)`
- system_check(T1): OS · 디스크 여유 · 사령부 파일 수 · 파이썬
- open_app_or_url(T2): 허용 목록 앱(메모장·계산기·탐색기·그림판), 사이트(유튜브·구글·네이버), http(s) 주소만 엽니다. 임의 명령은 거부합니다.
- draft_file(T2): `aon_drafts/` 아래에 초안을 생성합니다.
- critical_order_or_delete(T3): 스위치와 승인 3중 확인을 거칩니다. 실제 주문·삭제 API는 연결하지 않고, 집행 기록(`rgon_laptop_hands_ledger.jsonl`)만 남깁니다.

## 4. 대화·UI 연동
- 제10기관 분별기: `gate_control`(켜기는 마스터만, 끄기는 즉시 전체 잠금) · `laptop_check` · `laptop_open`
- 뮤즈: `approve` 계열 함수를 R35 게이트로 감쌉니다.
- HTML: `[RGON-GATE-V1]`. 상단 `🔒 결재수동 OFF ⇄ 🔓 결재수동 ON` 토글과 📋 보드의 🎛️ 제어판으로 구성되며, `[✅ 승인 집행]`은 캡처 단계에서 차단합니다.

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
