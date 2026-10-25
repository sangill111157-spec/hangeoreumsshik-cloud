---
name: aon-iching-strategic-planner
description: 주역 64괘(본괘·호괘·변괘·착괘·종괘)와 체용 생극·왕상휴수사를 WOOP·OODA·Stop Rule로 매핑하여 감사 가능한 reasoning_chain, 전략 추진 지수(0~100, 신뢰도 상한 85%), 3분기 MCTS 시나리오 트리, 3-Tier 실행 과제(Tier3 수동결재 게이트), 12시진 타임슬롯 스케줄을 생성하는 사령부 전략 기획관
version: v11.40-AON-ICHING-PLANNER
antibody: R41
skill_number: 37
---

# 제17기관 아온 주역 64괘 시운 전략 기획관 (WOOP·OODA·12시진·3분기 트리)

제17기관 `rgon_aon_iching_planner.py` 정식 스킬 #37.

## 사용법

```bash
python rgon_aon_iching_planner.py --self-test
python rgon_aon_iching_planner.py --plan 반도체 투자와 유튜브 성장 전략
python rgon_aon_iching_planner.py --daily
python rgon_aon_iching_planner.py --status
```

대화허브 슬래시 커맨드 `/계획`, `/plan`, `/전략`과 키워드(계획 짜·계획 세워·전략 짜·괘로 계획·로드맵)로 호출된다.

## 구조

본괘(관찰)·호괘(복병)·변괘(목표)·착괘(플랜B)·종괘(시장시선)·체용 통관(Stop Rule)을 WOOP+OODA로 매핑한다. reasoning_chain으로 점수 산출 근거를 남기고, 6대 시중처세, 3분기 MCTS 트리, 3-Tier 실행과제, 12시진 스케줄을 만든다.

## 안전 (헌법 제2항 · R35 · R41)

Tier3(금융·실매매·파일삭제·외부배포)은 항상 `requires_manual_gate: True`, `auto_executed: False`이다. 기획관은 계획만 세우고 실행하지 않는다.
