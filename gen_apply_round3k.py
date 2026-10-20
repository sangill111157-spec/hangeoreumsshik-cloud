# -*- coding: utf-8 -*-
import sys

doc_path = 'docs/testing_runtime_protocol.md'
with open(doc_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Section 5.1 preservation note with script details
old_sec51_note = """- **문서 수정 및 측정 스크립트 보존 의무화**:
  - 프로토콜 문서 수정, 검증, 감사 및 측정에 사용되는 모든 스크립트는 실행 직후 삭제하지 말고 `scripts/bench/` 디렉터리에 공식 보존하여 커밋에 포함해야 함 (결함 43 재발 방지).
  - 과거 세션에서 일시 생성 후 삭제되었던 임시 스크립트(`apply_round3i_doc_updates.py`, `update_sampler.py`, `fix_sample.py`, `update_dup_scanner.py`, `generate_*.py` 등)를 기록하며, 향후 모든 패치 및 검증 코드는 저장소 내 추적 파일로 영구 보존함."""

new_sec51_note = """- **문서 수정 및 측정 스크립트 보존 의무화**:
  - 프로토콜 문서 수정, 검증, 감사 및 측정에 사용되는 모든 스크립트는 실행 직후 삭제하지 말고 `scripts/bench/` 디렉터리에 공식 보존하여 커밋에 포함해야 함 (결함 43 재발 방지).
  - 과거 세션에서 일시 생성 후 삭제되었던 임시 스크립트(`apply_round3i_doc_updates.py`, `update_sampler.py`, `fix_sample.py`, `update_dup_scanner.py`, `generate_*.py` 등)와 함께, 파일 미존재/파싱 에러로 실행 실패한 가상 파워쉘 명령(`compare_ram_metrics.ps1`, `verify_line_history.ps1`, `run_verify_gate.ps1`), 그리고 인라인 재생성 코드 및 외부 `Downloads/shin-agent` 작업 디렉터리에서 생성되어 복사된 원본 스크립트(`gen_*.py`) 이력을 대장에 명시하고 모든 파이썬 공식 스크립트를 저장소 내 추적 파일로 영구 보존함."""

if old_sec51_note in text:
    text = text.replace(old_sec51_note, new_sec51_note, 1)
    print("Updated Section 5.1 note")
else:
    print("Failed to find old_sec51_note")

# 2. Update Section 5.8 "영구 폐기" -> "이 테스트베드에서 적용 중단, 향후 장비 항목으로 이관" (원문 취소선 보존)
old_sec58_trans = """> **[과제 [1] 런타임 벤치마크 공식 전환: 회귀 비교 전용 전환 및 절대 목표 이관]**
> 1. **배경 실측치**: 30분 유휴 RAM 표본화(N=60, 19:36:28~20:07:26) 결과, 시작 대비 종료 변동률 283.0%(885.9 MB -> 3,392.8 MB), 이동 구간 W=5(120s) 위반율 26.8%(15/56), W=10(270s) 위반율 47.1%(24/51), 최대 변동률 293.8%로 §5.3 환경 요건(30% 이내 변동)을 근본적으로 충족할 수 없음이 실측 증명됨.
> 2. **공식 판정 전환**: 인수인계 사전 합의 규칙("30% 요건을 충족하지 못하면 이 테스트베드에서는 절대 런타임 목표를 폐기하고 회귀 비교만 사용하며, 20.00 s 목표는 향후 장비 항목으로 넘긴다")에 따라, 본 테스트베드 머신에서는 **절대 런타임 목표(20.00 s)를 영구 폐기하고 '회귀 비교 전용(교대 측정 A/B 상대 비교)'으로 공식 전환**함. 20.00 s 절대 목표는 향후 독립 하드웨어/클라우드 전용 테스트베드 구축 시의 장비 평가 항목으로 공식 이관함."""

new_sec58_trans = """> **[과제 [1] 런타임 벤치마크 공식 전환: 회귀 비교 전용 전환 및 절대 목표 이관]**
> 1. **배경 실측치**: 30분 유휴 RAM 표본화(N=60, 19:36:28~20:07:26) 결과, 시작 대비 종료 변동률 283.0%(885.9 MB -> 3,392.8 MB), 이동 구간 W=5(120s) 위반율 26.8%(15/56), W=10(270s) 위반율 47.1%(24/51), 최대 변동률 293.8%로 §5.3 환경 요건(30% 이내 변동)을 충족하지 못함이 실측 증명됨. (동시 명령 구간 제외 후 19:37:13 이후 N=58 재계산 시에도 W=5 위반율 24.1%, W=10 위반율 44.9%, max/min 4.78배로 불충족 동일 확정).
> 2. **공식 판정 전환**: 인수인계 사전 합의 규칙("30% 요건을 충족하지 못하면 이 테스트베드에서는 절대 런타임 목표를 폐기하고 회귀 비교만 사용하며, 20.00 s 목표는 향후 장비 항목으로 넘긴다")에 따라, 본 테스트베드 머신에서는 ~~절대 런타임 목표(20.00 s)를 영구 폐기하고~~ **절대 런타임 목표(20.00 s)를 이 테스트베드에서 적용 중단하고 '회귀 비교 전용(교대 측정 A/B 상대 비교)'으로 공식 전환**함. 20.00 s 절대 목표는 향후 독립 하드웨어/클라우드 전용 테스트베드 구축 시의 장비 평가 항목으로 이관함."""

if old_sec58_trans in text:
    text = text.replace(old_sec58_trans, new_sec58_trans, 1)
    print("Updated Section 5.8 transition text")
else:
    print("Failed to find old_sec58_trans")

# 3. Add Defect for R038 timer log and R139 log absence to the footnotes
old_fn = """- [141회차 정정 및 근거 로그 각주]: 141행 서술의 '수집 462 = 453 + 9'에서 연결된 task-123 원시 로그는 교대 측정 로그로서 passed 452, collected 461(조정 전 값)입니다. 하한 453을 실측 통과한 원시 근거 로그는 task-233(`453 passed, 9 skipped, 87 subtests passed in 13.60s`, `Pytest runtime: 16.45s`, 저장소 보존본 `scripts/bench/logs/task-233.log`)입니다. 141행 본문은 불변으로 두고 본 각주를 통해 task-123이 조정 전 값임을 명기하고 task-233을 정식 실측 근거로 지정합니다.
- [129회차 정정 각주]: 120회차 커밋 bc8ccb6의 정규 verify 기준 통과 수는 423건이 맞음."""

new_fn = """- [대장 출처 결함 등재 각주 (R038 및 R139)]:
  1. 38회차(R038) 대장에 기재된 `task-1099.log`는 원시 로그 확인 결과 테스트 실행 출력이 없는 타이머 스케줄링 로그(`Successfully scheduled one-shot timer`)로 판명되었으며, 이는 대장 출처 결함에 해당함.
  2. 139회차(R139) 대장에 기재된 순수 런타임 15.17 s의 출처 로그는 미보존 상태이며, 현재 연결된 `task-8675.log`는 verify 실행 로그(순수 32.96 s / 월클록 41.81 s)만을 담고 있어 15.17 s의 원시 근거 로그는 부재함.
- [141회차 정정 및 근거 로그 각주]: 141행 서술의 '수집 462 = 453 + 9'에서 연결된 task-123 원시 로그는 교대 측정 로그로서 passed 452, collected 461(조정 전 값)입니다. 하한 453을 실측 통과한 원시 근거 로그는 task-233(`453 passed, 9 skipped, 87 subtests passed in 13.60s`, `Pytest runtime: 16.45s`, 저장소 보존본 `scripts/bench/logs/task-233.log`)입니다. 141행 본문은 불변으로 두고 본 각주를 통해 task-123이 조정 전 값임을 명기하고 task-233을 정식 실측 근거로 지정합니다.
- [129회차 정정 각주]: 120회차 커밋 bc8ccb6의 정규 verify 기준 통과 수는 423건이 맞음."""

if old_fn in text:
    text = text.replace(old_fn, new_fn, 1)
    print("Updated footnotes with R038/R139 defects")
else:
    print("Failed to find old_fn")

with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved docs/testing_runtime_protocol.md successfully.")
