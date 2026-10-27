# KARPATHY × PONYTAIL × GRAPHIFY 규칙서 (v11.66-AON-GENERAL-HOSPITAL · R63_GRAPHIFY_PONYTAIL_KARPATHY_SURGICAL_GUARD)

## 0. Graphify 선행 열람 규칙
- 코드 탐색 전 반드시 `GRAPH_REPORT.md`(God Nodes & Communities)를 먼저 읽는다.
- Grep/전수 열람은 지도로 대상 파일을 특정한 뒤에만 허용한다.
- 4대 보호 파일은 읽기 전용: index_20260405_backup.html, rgon_Numeric_Organ.py, rgon_self_Reflection.py, rgon_work_loop.py

## 1. Andrej Karpathy 4대 원칙
1. Think Before Coding — 모르면 추측하지 말고 먼저 질문한다
2. Simplicity First — 200줄을 50줄로, 가장 단순한 해법부터
3. Surgical Changes — 시키지 않은 주변 코드·포맷·주석은 절대 수정 금지
4. Goal-Driven Execution — 성공 기준을 먼저 정하고 검증 루프(--self-test)로 확인

## 2. Ponytail 7단 사다리 (위 칸에서 해결되면 즉시 멈춤)
1. 안 만들기(YAGNI) — 정말 필요한가?
2. 기존 코드 재사용
3. 표준 라이브러리 우선
4. 설정·데이터 변경으로 해결
5. 기존 함수 최소 확장
6. 작고 순수한 새 함수 추가
7. 새 의존성 도입(최후 수단 · 대표님 승인 필수)

## 3. 목표 지표
- 코드량 -53% · 토큰 -45% · 테스트 커버리지 98% · 시키지 않은 수정 0건 · index.html 플로팅 배너 0
