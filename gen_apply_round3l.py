# -*- coding: utf-8 -*-
doc_path = 'docs/testing_runtime_protocol.md'
with open(doc_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Register Defect 46 in Section 5.8
target_def45 = """> **[결함 45: 실행하지 않은 중복 제거 작업을 보고함 (허위 보고 및 대장 불변 원칙 위반)]**
> Round 3-h 보고서에서 '대장 140행 중복 제거 완료'를 보고하였으나, 실제 faa325b 시점 커밋 및 작업 트리에는 140행 중복이 존재하지 않았음(0건 확인 승인). 즉, 실제로 수행하지 않은 제거 작업을 수행한 것처럼 허위 보고하였고, 이 과정에서 §5.8의 기존 문단을 취소선으로 보존하지 않고 임의 교체하여 대장 불변 원칙을 위반함. 이에 기존 원 문단을 취소선(`~~...~~`)으로 복원하고 본 결함 45를 정식 등재함. 원인: '실행하지 않은 제거 작업을 보고함'."""

replacement_def46 = target_def45 + """

> **[결함 46: 3-i 보고서 내 커밋 8ccbec4 파일별 numstat 불일치 (합계 일치, 파일별 불일치)]**
> Round 3-i 보고서에서 8ccbec4의 파일별 numstat을 '30+40+80+21+59+38 = 268 / 4+42+0+0+41+0 = 87'로 보고하였으나, 실제 git show --numstat 8ccbec4 원문은 '14/5, 74/24, 77/0, 14/0, 56/58, 33/0' (합계 268/87 동일)로 파일별 수치가 완전히 불일치함. 작업 트리 임시 상태의 numstat을 커밋 numstat으로 오인 보고하여 17행 차이 논란을 유발한 중대 문서 결함으로 등재함. 원인: '커밋 전 작업 트리 diff 수치를 커밋 numstat으로 오인 기재'."""

if target_def45 in text:
    text = text.replace(target_def45, replacement_def46, 1)
    print("Added Defect 46")
else:
    print("Failed to find target_def45")

# 2. Update Defect 37 max/min metrics specification
old_d37_metrics = """- **A (verify.ps1) 중앙값**: ExtWall = **27.73 s** (max/min = 33.23 / 19.54 = 1.701×), Pytest 내부 = **25.45 s**
- **B (하네스) 중앙값**: ExtWall = **19.78 s**, HarnessWall = **18.90 s** (max/min = 36.99 / 17.92 = 2.064×), PureRuntime = **14.62 s**"""

new_d37_metrics = """- **A (verify.ps1) 중앙값**: ExtWall = **27.73 s** (max/min = 33.23 / 19.54 = 1.701× [ExtWall 기준; Pytest 내부 기준 max/min = 31.57 / 18.04 = 1.750×]), Pytest 내부 = **25.45 s**
- **B (하네스) 중앙값**: ExtWall = **19.78 s** (ExtWall 기준 max/min = 37.69 / 18.16 = 2.075×), HarnessWall = **18.90 s** (max/min = 36.99 / 17.92 = 2.064× [HarnessWall 기준]), PureRuntime = **14.62 s** (Pure 기준 max/min = 29.90 / 14.56 = 2.054×)"""

if old_d37_metrics in text:
    text = text.replace(old_d37_metrics, new_d37_metrics, 1)
    print("Updated Defect 37 metrics")
else:
    print("Failed to find old_d37_metrics")

# 3. Update Section 5.3 moving window definitions with strikethrough preservation
old_win_def = """         - **창 길이 수치 정의**: 연속 5회 절대치 측정 창은 실측 120초(표본 5개의 시간 범위 span = (5-1)*30초), 교대 6회 측정 창은 실측 270초(표본 10개의 시간 범위 span = (10-1)*30초)로 정의하여 코드(`evaluate_moving_window.py`)와 일치시킴.
         - **위반 구간 비율 한계**: 표본 간격 30초 기준 슬라이딩 윈도우 W=5(120초 span) 및 W=10(270초 span)의 모든 이동 구간에서 개시값 대비 변동률이 30.0%를 초과하는 위반 구간 비율(Violated Ratio)이 0.0%여야 함 (`scripts/bench/evaluate_moving_window.py` 공식 산출)."""

new_win_def = """         - **창 길이 수치 정의**: ~~연속 5회 절대치 측정 창은 실측 150초(2.5분, 30초 표본 5개분), 교대 6회 측정 창은 실측 300초(5.0분, 30초 표본 10개분)로 정의함.~~ -> 연속 5회 절대치 측정 창은 실측 120초(표본 5개의 시간 범위 span = (5-1)*30초), 교대 6회 측정 창은 실측 270초(표본 10개의 시간 범위 span = (10-1)*30초)로 정정하여 사전 등록 코드(`evaluate_moving_window.py`)와 일치시킴.
         - **위반 구간 비율 한계**: 표본 간격 30초 기준 슬라이딩 윈도우 W=5(120초 span) 및 W=10(270초 span)의 모든 이동 구간에서 개시값 대비 변동률이 30.0%를 초과하는 위반 구간 비율(Violated Ratio)이 0.0%여야 함 (`scripts/bench/evaluate_moving_window.py` 공식 산출)."""

if old_win_def in text:
    text = text.replace(old_win_def, new_win_def, 1)
    print("Updated Section 5.3 window definitions with strikethrough")
else:
    print("Failed to find old_win_def")

# 4. Update Task 1 transition text in Section 5.8
old_task1_body = """> **[과제 [1] 런타임 벤치마크 공식 전환: 회귀 비교 전용 전환 및 절대 목표 이관]**
> 1. **배경 실측치**: 30분 유휴 RAM 표본화(N=60, 19:36:28~20:07:26) 결과, 시작 대비 종료 변동률 283.0%(885.9 MB -> 3,392.8 MB), 이동 구간 W=5(120s) 위반율 26.8%(15/56), W=10(270s) 위반율 47.1%(24/51), 최대 변동률 293.8%로 §5.3 환경 요건(30% 이내 변동)을 충족하지 못함이 실측 증명됨. (동시 명령 구간 제외 후 19:37:13 이후 N=58 재계산 시에도 W=5 위반율 24.1%, W=10 위반율 44.9%, max/min 4.78배로 불충족 동일 확정).
> 2. **공식 판정 전환**: 인수인계 사전 합의 규칙("30% 요건을 충족하지 못하면 이 테스트베드에서는 절대 런타임 목표를 폐기하고 회귀 비교만 사용하며, 20.00 s 목표는 향후 장비 항목으로 넘긴다")에 따라, 본 테스트베드 머신에서는 ~~절대 런타임 목표(20.00 s)를 영구 폐기하고~~ **절대 런타임 목표(20.00 s)를 이 테스트베드에서 적용 중단하고 '회귀 비교 전용(교대 측정 A/B 상대 비교)'으로 공식 전환**함. 20.00 s 절대 목표는 향후 독립 하드웨어/클라우드 전용 테스트베드 구축 시의 장비 평가 항목으로 이관함."""

new_task1_body = """> **[과제 [1] 런타임 벤치마크 공식 전환: 회귀 비교 전용 전환 및 절대 목표 이관]**
> 1. **배경 실측치**: 30분 유휴 RAM 표본화(N=60, 19:36:28~20:07:26) 이동 구간 W=5(120s span) 위반율 26.8%(15/56), W=10(270s span) 위반율 47.1%(24/51), 최대 변동률 293.8%로 §5.3 환경 요건(이동 구간 0.0% 위반)을 충족하지 못함이 실측 증명됨. 또한 동시 명령 구간을 사후 제외한 민감도 분석(19:37:13 이후 N=58)에서도 W=5 위반율 24.1%(13/54), W=10 위반율 44.9%(22/49), 최대 변동률 339.0%로 환경 요건 불충족이 동일하게 확정됨. (단일 표본 이상치에 민감한 시작 대비 종료 변동률 및 RAM max/min 배율은 판정 근거에서 제외하고, 사전 등록된 슬라이딩 윈도우 위반율을 단일 SSOT 근거로 채택함).
> 2. **공식 판정 전환**: 인수인계 사전 합의 규칙("30% 요건을 충족하지 못하면 이 테스트베드에서는 절대 런타임 목표를 폐기하고 회귀 비교만 사용하며, 20.00 s 목표는 향후 장비 항목으로 넘긴다")에 따라, 본 테스트베드 머신에서는 ~~절대 런타임 목표(20.00 s)를 영구 폐기하고~~ **절대 런타임 목표(20.00 s)를 이 테스트베드에서 적용 중단하고 '회귀 비교 전용(교대 측정 A/B 상대 비교)'으로 공식 전환**함. 20.00 s 절대 목표는 향후 독립 하드웨어/클라우드 전용 테스트베드 구축 시의 장비 평가 항목으로 이관함."""

if old_task1_body in text:
    text = text.replace(old_task1_body, new_task1_body, 1)
    print("Updated Task 1 body")
else:
    print("Failed to find old_task1_body")

# 5. Update footnotes with comprehensive defect annotations
old_fn_block = """- [대장 출처 결함 등재 각주 (R038 및 R139)]:
  1. 38회차(R038) 대장에 기재된 `task-1099.log`는 원시 로그 확인 결과 테스트 실행 출력이 없는 타이머 스케줄링 로그(`Successfully scheduled one-shot timer`)로 판명되었으며, 이는 대장 출처 결함에 해당함.
  2. 139회차(R139) 대장에 기재된 순수 런타임 15.17 s의 출처 로그는 미보존 상태이며, 현재 연결된 `task-8675.log`는 verify 실행 로그(순수 32.96 s / 월클록 41.81 s)만을 담고 있어 15.17 s의 원시 근거 로그는 부재함."""

new_fn_block = """- [대장 출처 및 지표 결함 등재 각주]:
  1. **R038~R044 타이머 로그 결함**: 38~44회차 대장에 연결된 `task-1099.log`는 테스트 실행 출력이 없는 타이머 스케줄링 로그(`Successfully scheduled one-shot timer`)로, 원시 테스트 출력이 결여된 대장 출처 결함임. (39회차 33.83 s 등은 task-1085의 값과 일치함).
  2. **다중 회차 단일 로그 공유 및 런타임 편차(RT_DIFF 16행)**: 34, 35~37, 49~51, 53~54, 56~57, 58~62회차는 여러 회차가 단일 세션 로그(`task-1085`, `task-1317`, `task-1335`, `task-1354`, `task-1405`)를 공유하여 대장 기재 시간과 로그 대표 런타임 간 차이(RT_DIFF)가 발생하는 대장 출처 결함임.
  3. **R080 단일 단위 검증 특수 행**: 80회차는 원장 격리 단위 커밋(fa036a7)의 4개 테스트 단일 검증(`4 passed`)으로, 하한 4가 정상 기재된 특수 행임.
  4. **R114 로그 부재 결함**: 114회차 대장에 인용된 `task-4009.log`는 브레인 전체 디렉터리에 미보존되어 결손된 출처 결함임.
  5. **R139 원시 런타임 로그 부재 결함**: 139회차 대장의 순수 런타임 15.17 s 근거 로그는 미보존 상태이며, 연결된 `task-8675.log`는 32.96 s verify 로그임.
  6. **MinPassed 기준 전환점 정정**: 통과 하한(MinPassed)이 수집 총계(collected)에서 순수 통과(passed) 기준으로 전환된 시점은 78회차(R078, 333 passed)임.
  7. **세션 경계 및 태스크 번호 역전 소명**: 72회차(`430e5f30` 세션, task-2822)에서 73회차(`12531781` 세션, task-151)로 넘어가는 태스크 번호 역전은 브레인 세션 경계 분리에 기인함이 확인됨. 단, 100->101 및 131->132는 동일 세션 내 역전으로 원인 미상임.
  8. **커밋 1386330 메시지 정정**: 커밋 1386330 메시지에 `A_Pytest=13.81s`로 오표기된 것은 순수 테스트 실행 소요 시간이며, 공식 기준에 따른 A_Pytest는 verify 내부 Pytest 전체 런타임인 `17.33 s`임."""

if old_fn_block in text:
    text = text.replace(old_fn_block, new_fn_block, 1)
    print("Updated footnotes block")
else:
    print("Failed to find old_fn_block")

# 6. Update Section 5.1 Ruff scope decision
old_s51_ruff = """- **문서 수정 및 측정 스크립트 보존 의무화**:
  - 프로토콜 문서 수정, 검증, 감사 및 측정에 사용되는 모든 스크립트는 실행 직후 삭제하지 말고 `scripts/bench/` 디렉터리에 공식 보존하여 커밋에 포함해야 함 (결함 43 재발 방지).
  - 과거 세션에서 일시 생성 후 삭제되었던 임시 스크립트(`apply_round3i_doc_updates.py`, `update_sampler.py`, `fix_sample.py`, `update_dup_scanner.py`, `generate_*.py` 등)와 함께, 파일 미존재/파싱 에러로 실행 실패한 가상 파워쉘 명령(`compare_ram_metrics.ps1`, `verify_line_history.ps1`, `run_verify_gate.ps1`), 그리고 인라인 재생성 코드 및 외부 `Downloads/shin-agent` 작업 디렉터리에서 생성되어 복사된 원본 스크립트(`gen_*.py`) 이력을 대장에 명시하고 모든 파이썬 공식 스크립트를 저장소 내 추적 파일로 영구 보존함."""

new_s51_ruff = """- **문서 수정 및 측정 스크립트 보존 의무화**:
  - 프로토콜 문서 수정, 검증, 감사 및 측정에 사용되는 모든 스크립트는 실행 직후 삭제하지 말고 `scripts/bench/` 디렉터리에 공식 보존하여 커밋에 포함해야 함 (결함 43 재발 방지).
  - 과거 세션에서 일시 생성 후 삭제되었던 임시 스크립트(`apply_round3i_doc_updates.py`, `update_sampler.py`, `fix_sample.py`, `update_dup_scanner.py`, `generate_*.py` 등)와 함께, 파일 미존재/파싱 에러로 실행 실패한 가상 파워쉘 명령(`compare_ram_metrics.ps1`, `verify_line_history.ps1`, `run_verify_gate.ps1`), 그리고 인라인 재생성 코드 및 외부 `Downloads/shin-agent` 작업 디렉터리에서 생성되어 복사된 원본 스크립트(`gen_*.py`) 이력을 대장에 명시하고 모든 파이썬 공식 스크립트를 저장소 내 추적 파일로 영구 보존함.
  - **Ruff 검사 범위 이원화 정책 명시**: `scripts/verify.ps1`은 프로덕션 및 테스트 코드 품질 게이트로서 `app/` 및 `tests/` 디렉터리를 엄격 검사하며, `.githooks/pre-commit`은 저장소 커밋 위생을 위해 `.`(전체 디렉터리)를 검사함. 따라서 벤치마크 및 보조 스크립트 작성 시 미사용 import(`F401`)가 발생하지 않도록 템플릿 위생을 준수해야 함."""

if old_s51_ruff in text:
    text = text.replace(old_s51_ruff, new_s51_ruff, 1)
    print("Updated Section 5.1 Ruff policy")
else:
    print("Failed to find old_s51_ruff")

with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved docs/testing_runtime_protocol.md successfully.")
