---
name: trinity-trading-council
version: v11.23-TRADING-COUNCIL
antibody: R24
entry: rgon_trading_council.py
---
# ⚖️ Trinity Trading Council — 3자 찬반 심판기 + 주역 64괘 장세 필터

R24: 실전 트레이딩 3자 찬반 심판기(Bull/Bear/Judge) & 주역 64괘 리스크 필터 상시 가동 — 금고 보존(지족불욕·사환예방) 최우선 검증

## 실행
```bash
python rgon_trading_council.py --self-test     # 포맷·경계값 검증
python rgon_trading_council.py --run --merge   # 판정 후 morning brief(nutrient.trinity)에 병합
python rgon_trading_council.py --json          # 구조화 결과 출력
```

## 안건 & 괘
| # | 안건 | 괘 | 고전 지혜 |
|---|---|---|---|
| 1 | 💰 금고 보존 & 포지션 사이징 | #60 수택절(水澤節) | 지족불욕(知足不辱), 한도 수호 |
| 2 | 📈 추세 돌파 & 모멘텀 타점 | #01 중천건(重天乾) | 자강불식, 항룡유회 경계 |
| 3 | 🛡️ 변동성 방어 & 손절/익절 | #63 수화기제(水火既濟) | 사환예방(思患豫防) |
| 4 | 🔄 멀티에이전트 시그널 교차검증 | #64 화수미제(火水未濟) | 신변물거방(慎辨物居方) |

## 판정 규칙
- Judge = w·Bull + (1−w)·(100−Bear) → GO ≥ 65 / HOLD ≥ 50 / 그 외 DEFEND
- 금고(TREASURY) Bear ≥ 60이면 무조건 DEFEND (지족불욕 · R24)
- 모멘텀 Bull ≥ 85이면 Bear +15 (항룡유회)

## 출력 포맷 (Step 23 parseTri 호환)
`⚖️ [GO|HOLD|DEFEND] XX.X점 (Bull XX.X / Bear XX.X / #NN-괘명) 안건 — 판단`

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
