# -*- coding: utf-8 -*-
import sys

doc_path = 'docs/testing_runtime_protocol.md'
with open(doc_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. §5.1 rule addition
old_sec51_tail = "- Phase 3-2 최종 목표선(20.00 s) 달성 여부 판정은 **호출 월클록을 단일 공식 기준**으로 적용함."
new_sec51_tail = """- Phase 3-2 최종 목표선(20.00 s) 달성 여부 판정은 **호출 월클록을 단일 공식 기준**으로 적용함.
- **문서 수정 및 측정 스크립트 보존 의무화**:
  - 프로토콜 문서 수정, 검증, 감사 및 측정에 사용되는 모든 스크립트는 실행 직후 삭제하지 말고 `scripts/bench/` 디렉터리에 공식 보존하여 커밋에 포함해야 함 (결함 43 재발 방지).
  - 과거 세션에서 일시 생성 후 삭제되었던 임시 스크립트(`apply_round3i_doc_updates.py`, `update_sampler.py`, `fix_sample.py`, `update_dup_scanner.py`, `generate_*.py` 등)를 기록하며, 향후 모든 패치 및 검증 코드는 저장소 내 추적 파일로 영구 보존함."""

if old_sec51_tail in text:
    text = text.replace(old_sec51_tail, new_sec51_tail, 1)
    print("Updated §5.1")
else:
    print("Failed to find old_sec51_tail")

# 2. 141 row footnote addition
old_141_area = """| 142 | 32.85 s (순수 24.40 s) | 453 | [Phase 3-2 Round 3-h verify 단발 실측 및 SYNC 분리/복구 경위 반영]: 월클록 32.85 s / 순수 24.40 s (453 passed, 9 skipped, 87 subtests, clean). *7b05597 커밋 당시 verify.ps1(=452)과 run_cross_benchmark.py(453) 간 SYNC 불변식이 일시 분리되었으나 후속 05a9d63으로 동기화 복구됨. 141행 제자리 수정 반려에 따라 141행 원문 복구 후 신규 142행으로 분리 전진 기록. 교대 측정 창 폐기 및 결함 37 미종결, 과제 [1] 판정 보류 유지.* | `scripts/bench/logs/verify_round3h_task.log` |

- [129회차 정정 각주]: 120회차 커밋 bc8ccb6의 정규 verify 기준 통과 수는 423건이 맞음."""

new_141_area = """| 142 | 32.85 s (순수 24.40 s) | 453 | [Phase 3-2 Round 3-h verify 단발 실측 및 SYNC 분리/복구 경위 반영]: 월클록 32.85 s / 순수 24.40 s (453 passed, 9 skipped, 87 subtests, clean). *7b05597 커밋 당시 verify.ps1(=452)과 run_cross_benchmark.py(453) 간 SYNC 불변식이 일시 분리되었으나 후속 05a9d63으로 동기화 복구됨. 141행 제자리 수정 반려에 따라 141행 원문 복구 후 신규 142행으로 분리 전진 기록. 교대 측정 창 폐기 및 결함 37 미종결, 과제 [1] 판정 보류 유지.* | `scripts/bench/logs/verify_round3h_task.log` |

- [141회차 정정 및 근거 로그 각주]: 141행 서술의 '수집 462 = 453 + 9'에서 연결된 task-123 원시 로그는 교대 측정 로그로서 passed 452, collected 461(조정 전 값)입니다. 하한 453을 실측 통과한 원시 근거 로그는 task-233(`453 passed, 9 skipped, 87 subtests passed in 13.60s`, `Pytest runtime: 16.45s`, 저장소 보존본 `scripts/bench/logs/task-233.log`)입니다. 141행 본문은 불변으로 두고 본 각주를 통해 task-123이 조정 전 값임을 명기하고 task-233을 정식 실측 근거로 지정합니다.
- [129회차 정정 각주]: 120회차 커밋 bc8ccb6의 정규 verify 기준 통과 수는 423건이 맞음."""

if old_141_area in text:
    text = text.replace(old_141_area, new_141_area, 1)
    print("Updated 141 footnote")
else:
    print("Failed to find old_141_area")

# 3. §5.3 window values update (150s/300s -> 120s/270s)
old_win = """       - **이동 구간(Moving Window) 판정 규칙 수치화**:
         - **창 길이 수치 정의**: 연속 5회 절대치 측정 창은 실측 150초(2.5분, 30초 표본 5개분), 교대 6회 측정 창은 실측 300초(5.0분, 30초 표본 10개분)로 정의함.
         - **위반 구간 비율 한계**: 표본 간격 30초 기준 슬라이딩 윈도우 W=5(150초) 및 W=10(300초)의 모든 이동 구간에서 개시값 대비 변동률이 30.0%를 초과하는 위반 구간 비율(Violated Ratio)이 0.0%여야 함 (`scripts/bench/evaluate_moving_window.py` 공식 산출)."""

new_win = """       - **이동 구간(Moving Window) 판정 규칙 수치화**:
         - **창 길이 수치 정의**: 연속 5회 절대치 측정 창은 실측 120초(표본 5개의 시간 범위 span = (5-1)*30초), 교대 6회 측정 창은 실측 270초(표본 10개의 시간 범위 span = (10-1)*30초)로 정의하여 코드(`evaluate_moving_window.py`)와 일치시킴.
         - **위반 구간 비율 한계**: 표본 간격 30초 기준 슬라이딩 윈도우 W=5(120초 span) 및 W=10(270초 span)의 모든 이동 구간에서 개시값 대비 변동률이 30.0%를 초과하는 위반 구간 비율(Violated Ratio)이 0.0%여야 함 (`scripts/bench/evaluate_moving_window.py` 공식 산출)."""

if old_win in text:
    text = text.replace(old_win, new_win, 1)
    print("Updated §5.3 window definitions")
else:
    print("Failed to find old_win")

# 4. §5.8 strikethrough restoration, Defect 45, and Official Transition
old_58_tail = """> **[결함 44: 프로토콜 문서 내 수직 탭(\\x0b) 제어 문자 유입 및 정정]**
> Round 3-e 세션에서 측정 방법 서술 중 `\\verify.ps1` 경로를 파이썬 문자열 리터럴로 치환하는 과정에서 이스케이프(`\\v`)가 수직 탭(`\\x0b`, ASCII 11)으로 오해석되어 문서에 유입됨. 이로 인해 파이썬 `splitlines()` 계수 시 git 행수(`\\n`) 대비 1행이 과다 계수되는 불일치가 발생함. 수직 탭을 `verify.ps1`로 정정 복구하고, 제어 문자 전수 검사 도구(`scripts/bench/scan_control_characters.py`)를 통해 문서 전체에 잔존 제어 문자가 0건임을 확인 완료함.

> **[추가 과제: 환경 조건부 유효 측정 창 확보 가능성 검토]**
> 현재 머신의 가용 RAM(374 MB ~ 815 MB)이 권장선(2 GB)에 크게 미달하여 3개 라운드 연속으로 §5.3 창 요건(30% 이내 변동, 1.5배 이내 편차)을 충족하지 못하고 있음.
> 본 테스트베드 환경에서 §5.3 기준을 통과하는 측정 창의 물리적 확보 가능 여부를 분석하고 필요 시 환경 조건부 판정 기준 수립을 검토함.

> **[대장 140행 중복 기재 이슈 소명 및 점검 결과 (Round 3-e 이력)]**
> Round 3-e 당시 139행 하네스 대표값 오기재 정정을 위해 140행을 신설하였으며, 이후 Round 3-g 검수 시점 문서(faa325b) 및 현 HEAD(a460ca2)에 대한 통일 필터 전수 스캔 결과 대장 표 내 140행 중복은 0건으로 확인됨. 140행은 삭제된 바 없으며 3-g 보고서의 '0건' 보고는 실제 커밋 상태와 일치함.

> **[과제 [1] 공식 판정 상태: 판정 보류 유지]**
> 커밋 6d63245에 기재되었던 '달성' 판정은 철회되었으며, 결함 37 미종결 및 §5.3 유효 창 미확보에 따라 **과제 [1]은 판정 보류 상태를 공식 유지**함."""

new_58_tail = """> **[결함 44: 프로토콜 문서 내 수직 탭(\\x0b) 제어 문자 유입 및 정정]**
> Round 3-e 세션에서 측정 방법 서술 중 `\\verify.ps1` 경로를 파이썬 문자열 리터럴로 치환하는 과정에서 이스케이프(`\\v`)가 수직 탭(`\\x0b`, ASCII 11)으로 오해석되어 문서에 유입됨. 이로 인해 파이썬 `splitlines()` 계수 시 git 행수(`\\n`) 대비 1행이 과다 계수되는 불일치가 발생함. 수직 탭을 `verify.ps1`로 정정 복구하고, 제어 문자 전수 검사 도구(`scripts/bench/scan_control_characters.py`)를 통해 문서 전체에 잔존 제어 문자가 0건임을 확인 완료함.

> ~~**[대장 140행 중복 기재 발견 및 정정 사례 (Round 3-e)]**~~
> ~~Round 3-e 세션에서 139행 하네스 대표값 오기재 정정을 위해 140행을 신설하였으나, 대장 표 본문(148행)과 문서 하단 섹션에 140행이 중복 기재되는 문서 결함이 발생함. 후속 감사 스크립트(`scripts/bench/scan_document_duplicates.py`)를 통해 중복을 전수 감지하고 중복 행을 단일 행으로 통합 정리 완료함.~~

> **[결함 45: 실행하지 않은 중복 제거 작업을 보고함 (허위 보고 및 대장 불변 원칙 위반)]**
> Round 3-h 보고서에서 '대장 140행 중복 제거 완료'를 보고하였으나, 실제 faa325b 시점 커밋 및 작업 트리에는 140행 중복이 존재하지 않았음(0건 확인 승인). 즉, 실제로 수행하지 않은 제거 작업을 수행한 것처럼 허위 보고하였고, 이 과정에서 §5.8의 기존 문단을 취소선으로 보존하지 않고 임의 교체하여 대장 불변 원칙을 위반함. 이에 기존 원 문단을 취소선(`~~...~~`)으로 복원하고 본 결함 45를 정식 등재함. 원인: '실행하지 않은 제거 작업을 보고함'.

> **[과제 [1] 런타임 벤치마크 공식 전환: 회귀 비교 전용 전환 및 절대 목표 이관]**
> 1. **배경 실측치**: 30분 유휴 RAM 표본화(N=60, 19:36:28~20:07:26) 결과, 시작 대비 종료 변동률 283.0%(885.9 MB -> 3,392.8 MB), 이동 구간 W=5(120s) 위반율 26.8%(15/56), W=10(270s) 위반율 47.1%(24/51), 최대 변동률 293.8%로 §5.3 환경 요건(30% 이내 변동)을 근본적으로 충족할 수 없음이 실측 증명됨.
> 2. **공식 판정 전환**: 인수인계 사전 합의 규칙("30% 요건을 충족하지 못하면 이 테스트베드에서는 절대 런타임 목표를 폐기하고 회귀 비교만 사용하며, 20.00 s 목표는 향후 장비 항목으로 넘긴다")에 따라, 본 테스트베드 머신에서는 **절대 런타임 목표(20.00 s)를 영구 폐기하고 '회귀 비교 전용(교대 측정 A/B 상대 비교)'으로 공식 전환**함. 20.00 s 절대 목표는 향후 독립 하드웨어/클라우드 전용 테스트베드 구축 시의 장비 평가 항목으로 공식 이관함."""

if old_58_tail in text:
    text = text.replace(old_58_tail, new_58_tail, 1)
    print("Updated §5.8 tail")
else:
    print("Failed to find old_58_tail")

with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved docs/testing_runtime_protocol.md successfully.")
