---
name: aon-neural-synapse-verifier
description: 제16기관 아온 전신 신경망 시냅스 병렬 정밀 검증기 (정식 스킬 #36, v11.39-AON-NEURAL-SYNAPSE, R1~R40)
---
# aon-neural-synapse-verifier

12개 기관 `--self-test` 병렬 실행(ThreadPoolExecutor 8), 10대 시냅스 E2E 실전 검증,
V13 HTML 브리지와 스킬 삼중 일치 [36, 36, 36] 확인을 수행합니다.

```bash
python rgon_neural_synapse_verifier.py --self-test
python rgon_neural_synapse_verifier.py --audit
python rgon_neural_synapse_verifier.py --status
```

결과물: `rgon_neural_synapse_map.json`, `docs/rgon_neural_synapse_map.json` (`synapse_health_score: 100.0`)

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
