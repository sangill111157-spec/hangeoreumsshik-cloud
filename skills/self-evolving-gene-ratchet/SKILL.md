---
name: self-evolving-gene-ratchet
slug: self-evolving-gene-ratchet
category: self-evolution
hexagram_tag: "#49-革"
version: v11.25-SELF-EVOLVE
antibody: R26
description: EvoMap Gene Capsule 증류와 Amazon Ratchet 기여도 거버넌스와 AgentEvolver 자문자답 자가진화 엔진
---
# 🧬 Self-Evolving Gene Ratchet — 21번째 정식 스킬 (#49 澤火革)
> R26: 자가진화 유전자(Gene·Capsule) & 라쳇(Ratchet) 기여도 거버넌스 상시 가동 — 경험은 전략 유전자로 압축하고 검증 없는 진화(Library Drift)는 원천 차단
## 전략 (Strategy)
- Skill2Gene: skills/*/SKILL.md를 GEP 전략 유전자(rgon_genes.json)로 증류하고 실행 증거 캡슐(rgon_capsules.json)을 기록한다
- RatchetCurator: 스킬 기여도(-1.0~+1.0)를 채점하고 역회전 감지 시 최고 스냅샷으로 복구한다(rgon_ratchet_audit.json)
- SelfQuestioningLoop: Self-Questioning·Self-Navigating·Self-Attributing으로 [EVOLVE] 심판 줄을 nutrient.trinity에 병합한다
## 금지 (Avoid)
- AVOID: 검증(self-test) 없는 유전자 변경 — Library Drift 원천 차단
- AVOID: .html / .js / manifest.json 직접 수정 (삼성 ② 해시 불변)
- AVOID: 실행하지 않은 exit_code를 캡슐에 기록하는 위조
## 검증 (Validation)
```bash
python rgon_self_evolution_engine.py --run --merge --json
python rgon_self_evolution_engine.py --self-test --json
```

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
