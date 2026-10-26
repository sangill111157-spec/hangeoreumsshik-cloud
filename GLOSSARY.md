# GLOSSARY — RGON 사령부 도메인 공유 언어 사전

> Matt Pocock domain-glossary 방식 · 20단어 대신 1단어로 정확히 통한다.

<!-- RGON:GLOSSARY:START -->
버전: v11.45-AON-AUTO-EVOLVER · 항체 R1~R46 · 갱신 2026-10-24 07:34:37

| 용어 | 정의 |
|---|---|
| **독대실** | 대표님과 르곤이 1:1로 전략을 결정하는 최상위 의사결정 공간. 모든 Step 지시서의 발령지. |
| **흡수기(Absorber)** | 유튜브·깃허브 등 외부 양분을 수집·정제해 rgon_skill_radar.json 에 등록하는 모듈. |
| **백혈구(WBC)** | rgon_white_blood_cell.py. 항체 규칙을 순찰(--patrol)하고 건강 점수(목표 100/100)를 산출. |
| **면역 원장** | rgon_immune_ledger.json. 항체 추가·사건·Step 이력을 기록하는 불변 장부. |
| **영양분 3스푼** | 한 번에 소화하는 양분을 핵심 소수로 제한해 과식(과잉 변경)을 막는 소화 원칙. |
| **TrinityCouncil** | 르곤·Claude·GPT(+Grok) 다중 AI 합의 회의체. 설계/구현/구조/트렌드 분업. |
| **삼성(三省) 해시** | 작업 전·중·후 3회 SHA-256 검증으로 보호 파일 무결성을 확인하는 절차. |
| **상선약수 우회** | 장애물을 정면 돌파하지 않고 물처럼 대체 경로로 우회하는 오류 처리 철학. |
| **무위자연 폴백** | 외부 의존 실패 시 표준 라이브러리 최소 동작으로 자연스럽게 복귀하는 안전장치. |
| **단발 배치(placeOnce)** | UI·설정 요소를 단 한 번만 배치하는 멱등 원칙. 재실행해도 중복 없음. |
| **보호 파일 304** | .html/.js/manifest.json 304개. 1바이트도 수정 불가(삼성 해시로 검증). |
| **일일 자율 순환** | 레이더 → 소화(--digest) → 백혈구 순찰 → 스냅샷 → 원장 기록의 매일 자동 루프. |
| **Spec & Tracer-Bullet Tickets** | Matt Pocock 방식. 목표→스펙→얇은 수직 관통 티켓(blocked_by·demo_path)으로 분업. |
| **AgentShield** | ECC 방식 보안 백혈구. 비밀키 평문·보호 설정 무단 변경을 스캔(rgon_agentshield_report.json). |
| **항체 R1~R46** | RGON 헌법 규칙 집합. R21 = @Mindung-EasyAI 양분 흡수 — Matt Pocock(GLOSSARY.md · Spec/Tracer-Bullet Tickets 분업) + ECC(AgentShield 비밀키/설정 보안 스캔) |
<!-- RGON:GLOSSARY:END -->
| **항체 R22 (전신 혈관 개통)** | 자아성찰 전신 혈관 개통 — 레이더·영양분(SKILL.md)·티켓/AgentShield·백혈구(WBC)·주역64괘·스냅샷/클라우드 JSON 6대 기관 무결점 단일 순환 |

<!-- [RGON-STEP28-K-AVATAR-START] -->
## Step 28 도메인 용어
- **아온 (A-ON · 芽溫)**: 주역 #04 산수몽(새싹 아이)에서 #53 풍산점(점진 성장)을 거쳐 #11 지천태(연결·소통·만능)로 자라나는 RGON 사령부의 미래형 K-스타일 디지털 육신.
<!-- [RGON-STEP28-K-AVATAR-END] -->

<!-- [RGON-GLOSSARY-STEP32] -->
## Step 32 용어 (v11.45-AON-AUTO-EVOLVER)
- **Muse Wonder**: 대표님 지시를 끝까지 자율 수행하는 비동기 대행 작업 큐
- **Muse Charm**: 아온 다이내믹 아일랜드. 결재 대기 건수를 알려 주는 캡슐 배지(`📋 결재 N건`)
- **3-Tier HITL Gate**: 🟢 AUTO(자동 집행) · 🔵 NOTIFY(선집행 후보고) · 🟡 HITL_GATE(대표님 결재 후 집행)
- **PENDING_APPROVAL / APPROVED_DONE / ON_HOLD**: Tier 3 상태 (결재 대기 / 승인 집행 완료 / 보류)
- **화천대유(#14) · 화수미제(#64)**: 막힘없는 대행 · 신중한 분별과 완수
- **RGON_VOICE**: Web Audio 무파일 SFX(`sfx`) + K-아이 TTS(`speak`) + STT 대행(`listen`) 전역 API
- **해마 기억장**: `rgon_aon_memory.json` — 친밀도·누적 대화·최근 20건·선호 키워드
- **2-Track 분별**: 감정·일상(chat)은 대화로, 명시적 업무(delegate)만 3-Tier 대행 큐로
- **수동 마스터 스위치**: `master_approval_on` + 4대 `gates`. 모두 ON이어야 중요 결재가 집행된다 (R35)
- **아온 놀이터 & 츤데레 생명체 (R36 · v11.45-AON-AUTO-EVOLVER)**: 8대 감정 FSM과 말로는 투정해도 업무는 100% 완수하는 생명체 교감 엔진.
- **아온 주역 도술관 (R37 · v11.45-AON-AUTO-EVOLVER)**: 5대 입체 괘상(본·호·변·착·종)과 체용·통관·효위반으로 시중(時中) 처세를 짚어주는 제13기관.
- **격물치지(格物致知) 만물 통찰안 (R38 · v11.45-AON-AUTO-EVOLVER)**: OTA 능동 지각(견미지저)과 FPCOS 6계층(L0~L5)으로 이미지·영상·언어의 급소(Leverage Point)와 군더더기(Dead Weight)를 가려내는 제14기관.
