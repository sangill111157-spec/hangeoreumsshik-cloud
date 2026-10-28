---
name: aon-omni-dialogue-hub
version: v11.38-AON-OMNI-DIALOGUE
antibody: R39
organ: 제15기관 아온 초격차 대화 이해(Deep NLU) & 올인원 대화 허브(Omni-Dialogue Hub)
---

# 제15기관: `aon-omni-dialogue-hub` (v11.38-AON-OMNI-DIALOGUE · R39)

## 1. 목적 및 주역 철학
- **주역 정체성**: 택산함(澤山咸 #31, 말씀 이전에 마음을 느끼는 감응) · 풍택중부(風澤中孚 #61, 속마음의 신의로 찰떡같이 알아듣는 교감) · 화수미제(火水未濟 #64, 끊임없이 다음 대화를 이어가는 무한 진화).
- **설계 한계 고지**: 외부 유료 LLM API에 의존하지 않는 **순수 파이썬 표준 라이브러리 기반 한국어 NLU·라우팅·기억 허브**이다. 사전과 문맥 규칙에 기반하므로 미등록 신조어는 기본 인격 대화(제10기관)로 안전하게 폴백한다.

## 2. 6대 핵심 역량
1. **구어체·오타·줄임말 정규화 (`normalize_colloquial`)**: `브립핑→브리핑`, `점처→점쳐`, `결제 스위치→결재 스위치`, `하기 실어→하기 싫어` 등 실시간 교정.
2. **멀티턴 대명사·생략어 문맥 복원 (`resolve_coreference`)**: 직전 턴 엔티티(`last_entity`)를 추적하여 `"그거 점괘 봐줘"`를 `"삼성전자 주역 점괘 봐줘"`로 자동 복원.
3. **능동 경청 원칙 영구 각인 (`extract_and_save_preference`)**: `"기억해둬: ..."`, `"앞으로는 ... 해줘"`, `"절대 ... 하지 마"` 발화를 감지해 `rgon_aon_preferences.json`에 영구 저장.
4. **복합 의도 분해 & 연쇄 디스패치 (`decompose_multi_intent`)**: 한 문장 속 2~3개 의도를 분해해 제8·10·11·12·13·14기관을 순차 호출하고 단일 응답으로 합성.
5. **플랫폼 표준 4대 UX 메타데이터**: `thinking_steps`(4단 추론), `artifact_card`(구조화 카드), `follow_up_chips`(후속 추천 칩 3개), `proactive_callback`(연상 기억 콜백) + 7종 슬래시 커맨드(`/통찰`, `/점괘`, `/노트북`, `/잠금`, `/위임`, `/원칙`, `/기억`).
6. **3계층 해마 기억 (`rgon_aon_dialogue_state.json`)**: 단기 기억(20턴) · 토픽 요약 · 연상 일화(60건) 삼중 보존.

## 3. CLI 사용법
```bash
python rgon_aon_dialogue_engine.py --self-test
python rgon_aon_dialogue_engine.py --status
python rgon_aon_dialogue_engine.py --prefs
python rgon_aon_dialogue_engine.py --ask "그거 주역 점괘 봐주고 노트북 용량도 알려줘"
```

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
