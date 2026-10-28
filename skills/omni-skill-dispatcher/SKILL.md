---
name: omni-skill-dispatcher
description: 독대실 3탭(트렌드·보유 스킬·3자 심판) 항목을 [⚡ 질문창 장전] 원터치로 질문창에 단발 장전하고 클립보드에도 복사
---

# ⚡ Omni Skill Dispatcher — 20번째 정식 스킬 (#14-大有 · omni-dispatch · v11.24-OMNI-DISPATCH)

> R25: 연결·소통·만능 원터치 스킬 디스패처 — 보유 스킬·트렌드·3자 심판 결과를 독대실 질문창에 무간섭 단발 장전

## 언제 쓰나
독대실 3탭(📡 트렌드 레이더 / 🍯 보유 스킬 / 🫀 전신 맥박 & 3자 심판)의 항목을 질문창에 바로 장전할 때.

## 동작 (단발 · 루프 없음)
1. `[⚡ 질문창 장전]`(data-load)을 누르면 `#rgyt-wrap` 바깥의 보이는 textarea 또는 text input을 찾는다(`#rgyt-q` 제외).
2. 네이티브 value setter로 값을 넣고 `input`/`change` 이벤트를 보낸다(React 제어형 입력창 호환).
3. 클립보드에도 복사하고, 버튼에 1.2초 동안 `⚡ 장전+복사 완료!`를 띄운 뒤 입력창에 포커스한다.

## 금기 (R15·R23·R25)
V15 placeOnce 블록 보존. 감시 루프·반복 타이머·프레임 루프 API는 쓰지 않는다. .js/manifest.json은 수정하지 않는다.

## 호출 예
```text
[⚡ 스킬 호출] omni-skill-dispatcher
→ skills/omni-skill-dispatcher/SKILL.md 지침에 따라 실행해 줘.
```

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
