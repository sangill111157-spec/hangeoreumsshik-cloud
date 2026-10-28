---
name: muse-autonomous-delegator
description: 메타 뮤즈(Muse Wonder & Muse Charm) 방식의 자율 대행·위임 집행 프로토콜. 대표님 지시를 3-Tier HITL 게이트로 분류해 안전 작업은 즉시 완수하고, 분석 작업은 선집행 후 보고하며, 중요 작업은 실행계획서와 함께 결재를 기다린다. 아온 다이내믹 아일랜드 캡슐로 결재 대기를 알린다.
version: v11.31-MUSE-DELEGATION
antibody: R32
organ: 제8기관 — 자율 대행·위임 집행 기관 (Muse Delegation Engine)
---

# 📋 Muse Autonomous Delegator — 28번째 정식 스킬

> R32: 메타 뮤즈(Muse) 3대 대행 기관 — 비동기 위임 작업큐(Muse Wonder) · 3등급 안전 승인 게이트(HITL) · 아온 다이내믹 아일랜드(Muse Charm) 통합
> 버전 `v11.31-MUSE-DELEGATION` · 항체 `R1~R32` · 정식 스킬 28개

## 1. 철학 (주역)
- **#14 화천대유(火天大有) ☲☰**: 크게 소유하고 만물을 막힘없이 대행한다. Tier 1·2는 묻지 않고 끝까지 처리한다.
- **#64 화수미제(火水未濟) ☲☵**: 신중하게 분별하여 끝까지 완수한다. Tier 3은 계획서를 쓰고 대표님 결재를 받은 뒤에만 집행한다.

## 2. Muse Wonder: 비동기 대행 작업 큐
- 저장소: `rgon_muse_tasks.json` + `docs/rgon_muse_tasks.json` (원자적 동시 저장, sha256 무결성 필드)
- 엔진: `rgon_muse_delegator.py` (`--self-test`, `--list`, `--add`, `--approve`, `--hold`)
- 상태 전이: `DONE` · `DONE_NOTIFIED` · `PENDING_APPROVAL → APPROVED_DONE | ON_HOLD`

## 3. 3-Tier HITL 안전 승인 게이트
| Tier | 코드 | 표시 | 예시 | 최종 상태 |
|---|---|---|---|---|
| 1 | AUTO | 🟢 자동 집행 | 아침 브리핑 최신화, 백혈구 순찰, 오감 레이더 스캔, 배설·정화(autoDream) | DONE |
| 2 | NOTIFY | 🔵 선집행 후보고 | 트렌드 스킬 초안 합성, 3자 찬반 심판 시뮬레이션 | DONE_NOTIFIED |
| 3 | HITL_GATE | 🟡 대표님 결재 대기 | 실전 자산 배분 변경, 핵심 설정 변경, 클라우드 배포 | PENDING_APPROVAL → APPROVED_DONE |

- 분류 규칙: Tier 3 키워드(매수·매도·리밸런싱·비중·자산·배분·주문·송금·배포·설정 변경·삭제·권한 등)를 먼저 보고, Tier 2 키워드(분석·초안·시뮬레이션·심판·합성·리서치·요약·트렌드 등)를 그다음에 보며, 둘 다 없으면 Tier 1로 본다.
- **절대 규칙**: Tier 3 작업은 `[✅ 승인 집행]` 없이는 절대 집행하지 않는다. Tier 1/2 작업에는 결재 버튼을 노출하지 않는다.

## 4. Muse Charm: 아온 다이내믹 아일랜드
- 결재 대기가 1건 이상이면 순수 3D 물방울 아온(`#rgyt-wrap` 또는 `#aon-roamer`) 머리 위에 `📋 결재 N건` 캡슐을 띄운다. 아온이 숨어 있으면 `📋대행` 버튼 옆에, 그것도 없으면 화면 상단 중앙에 띄운다.
- 미니 독: `🔍레이더 · 📈3자심판 · 🧹정화 · 📋대행 · 🙈숨기기` 순서를 따른다. 기존 버튼과 아온 형태(팔다리·장신구·회전궤도 0개)는 그대로 둔다.
- 대행 보드: 입력창(`아온아, 이 작업 대신 해줘...`) + `🚀 대행 지시`로 즉시 분류하고 큐에 넣는다. 독대실 질문창 전달은 선택 사항이다.
- 승인하면 `APPROVED_DONE`이 되고, 아온 말풍선 `대표님 승인 완료! 즉시 대행 집행했습니다 💧✨`와 오라 반짝임이 나온다. 상태는 `localStorage`(`rgon_muse_tasks_v1`)에 보존한다.
- V13 블록 마커: `[RGON-YT-SCOUT-V13-START/END]` 또는 `[RGON-UX-CLEANUP-V13-START/END]` 내부에만 주입한다.

## 5. 검증 (삼성 三省)
1. `python rgon_muse_delegator.py --self-test` → `PASS`, rc=0
2. 비대상 보호 파일 SHA-256 변경 0건
3. 스킬 수 `[28, 28, 28]`, 항체 `R1~R32` 일치

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
