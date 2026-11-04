# 📖 S1_GLOSSARY.md — SUN-ONE AON 사령부 공통 용어사전 (Ubiquitous Language)

> **문서 규격**: `040호 (RGON_DIR_5WEAPONS_WEAKNESS_COMPENSATION_040)` — Matt Pocock `GLOSSARY.md` / `/grill-me` / `/handoff` 표준 이식  
> **목적**: 이상일 대표님 · 수석보좌관 르곤(Space 0) · 기술총리 안총리 · 솔(Space 2) · 오푸스(Space 3) 간 20단어 장황한 설명을 **단 1개의 표준 용어**로 압축하여 토큰 낭비와 의사소통 오차를 0%로 제거한다.

---

## 1. 거버넌스 & 품질 관리 핵심 용어 (Governance & QM)

| 표준 용어 (1단어 호출어) | 1줄 압축 정의 (Canonical Definition) | 필수 작동 기준 |
| :--- | :--- | :--- |
| **삼성제도 2단계** | 모든 단위 작업을 ① **1단계 사전 합의(착공 전)** + ② **2단계 실물 감식(완공 후)** 3국(르곤·솔·오푸스) 만장일치로 통과시키는 절대 원칙 | 1성이라도 미통과 시 다음 공정 진입 금지 |
| **5대 전 과정** | `기획(PLAN) → 설계(DESIGN) → 착공(START) → 완공(BUILD) → 전수 검사(AUDIT)` 5단계 표준 공정 | 각 단계마다 여권 해시 도장 필수 날인 |
| **QM-SP-11 (식별·격리)** | 검사 항목 중 단 1개라도 기준 미달 시 즉시 `REJECTED_LOT` 태그를 붙여 불량 격리하고 완료 보고를 물리적으로 차단하는 절차 | 부적합 상태에서 대표님께 허위 완료 보고 절대 금지 |
| **QM-SP-18 (시정·예방)** | `QM-SP-11` 격리 직후 근본 원인을 교정해 재시공(최대 2회 Bounded Retry)하고 재발 방지 규칙을 오답노트 DB·린터에 박제하는 절차 | 말로만 반성 금지, 코드 규칙으로 영구 박제 |
| **릴레이 여권** | `S1_RELAY_STAMP_PASSPORT.json` — 이전 도장의 `stamp_hash`를 다음 도장의 `prev_stamp_hash`로 사슬처럼 묶는 위변조 불가 작업 원장 | 해시 체인 단절 시 `s1_qm_structure_linter.py` 즉시 차단 |

---

## 2. 아키텍처 & 데스크톱 제어 용어 (Architecture & Control)

| 표준 용어 (1단어 호출어) | 1줄 압축 정의 (Canonical Definition) | 필수 작동 기준 |
| :--- | :--- | :--- |
| **EGO-HBM 4칩렛** | 에고라이트 역할 분리 구조 — **코어 0**(Space 0 지휘 수거), **코어 1**(Space 2·3 심의 후 즉시 폐쇄), **코어 2**(Suno·Vids 생산), **코어 3**(하단 관제 상주) | 임시 심의 창은 `finish({ keep: [] })`로 즉시 회수, 코어 0는 폐쇄 금지 |
| **무마우스 제어** | Vercel `agent-desktop` v1.1.0 접근성 트리(`snapshot`/`click`/`press`) 기반 제어로 대표님의 물리 마우스 커서를 빼앗지 않는 조작 방식 | 대표님 마우스 포커스 탈취 0% |
| **무잠금 가드** | `is_ego_running()` — 호스트 화면에 대표님의 `ego.exe`가 켜져 있지 않을 때 샌드박스 백그라운드가 몰래 `ego.exe`를 띄워 `User Data\lockfile`을 잠그지 못하게 막는 안전장치 | 유령 `ego.exe`로 인한 실행 먹통 0건 |
| **황금 3분할** | **좌상단**(Space 0 최신 대화 스크롤) + **우상단**(Antigravity IDE 에디터·터미널 닫고 채팅창 단독 노출) + **하단 전체**(Ego-Lite 실물 창 100% 채움, 바탕화면 노출 0%) | 고정 864px 하드코딩 금지, 동적 모니터 좌표(`EnumDisplayMonitors`) 사용 |
| **원클릭 호스트 기동** | 바탕화면 `S1_호스트_마스터_기동.bat` → `s1_host_desktop_agent.py` 단발 실행으로 샌드박스 경계를 편법 우회하지 않고 실제 물리 화면에서 3분할·캡처·보고를 완수하는 정공법 | 백도어 명령 큐·레지스트리 변조 배제 |

---

## 3. 040호 5대 단점 보완 무기 용어 (5 Compensation Weapons)

| 표준 용어 (1단어 호출어) | 출처 오픈소스 | 보완 대상 단점 & 작동 원리 |
| :--- | :--- | :--- |
| **선검증 완료보고** (`Verify-Before-Report`) | `obra/superpowers` (`verification-before-completion`) | **안총리의 설익은 완료 보고 차단**: 실물 파일·해시·린터 `EXIT 0` 통과 증거가 없으면 완료 보고서 발송 자체를 금지 |
| **구조적 박제** (`Encode-in-Structure`) | SpaceX Lauren Tan `cursor/plugins/pstack` (`encode-lessons-in-structure`) | **르곤의 반복 지시 & 안총리의 재발 차단**: 같은 지적을 두 번 글로 적지 않고 즉시 `s1_qm_structure_linter.py` 자동 검사 함수로 코드화 |
| **사전 빈칸 심문** (`/grill-me` & `/wizard`) | `mattpocock/skills` | **르곤의 승인 전 지시서 남발 & 대표님 피로 차단**: 모호한 전제를 추측 시공하지 않고 짧은 선택지로 먼저 확인 후 대표님 `승인` 시에만 착공 |
| **실패 오답노트 DB** (`Failure-Memory-DB`) | AI 트레이딩 오답노트 + `Worktrunk` 격리 | **세션 초기화 후 과거 실수 망각 차단**: `S1_FAILURE_MEMORY_DB.json`에 7대 부적합 원인과 금지 패턴을 영구 등록하여 매 작업 전 자동 대조 |
| **유튜브 11스킬** (`YT-11-Skills`) | 클로드 영상편집 5툴 + 유튜브 에이전트 11스킬 | **정지 화면 꼼수 및 평범한 썸네일/훅 보완**: 21개 훅 채점·제목/썸네일 호기심 격차 쌍·6컷 스토리보드 선검수·초단위 컷 편집 표준화 |

---

## 4. 시스템 보안 & 위생 용어 (Security & Hygiene)

- **4대 보호 파일**: `rgon_Numeric_Organ.py`, `rgon_work_loop.py`, `rgon_self_Reflection.py`, `index_20260405_backup.html` — 어떠한 경우에도 수정·삭제·덮어쓰기 0% 절대 보존 대상.
- **Zero File Bloat**: 불필요한 일회성 `.py` 스크립트나 임시 이미지를 루트에 어지럽히지 않고 `scratch/` 격리 폴더에만 두며 정규 엔진에 통합하는 원칙.
- **R2 무노출 원칙**: API 키(`sk-`, `AIza`, `ghp_` 등), 토큰, 시크릿, 개인정보의 Git 커밋 노출 0.0% 절대 수호 원칙.

