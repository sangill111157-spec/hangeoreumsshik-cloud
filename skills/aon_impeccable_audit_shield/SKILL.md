---
name: aon_impeccable_audit_shield
version: v11.50-AON-TOKEN-EGOLITE-MASTER
antibody: R50
organ: 제26기관 · rgon_aon_impeccable_audit_shield
description: "아온 임페커블 UI 폴리시(62규칙) & 오픈셸·클라우드플레어 적대적 교차감사 기관 (Cloudflare 2단계 적대적 감사 + NVIDIA OpenShell 정책 동결 + Impeccable 62규칙 UI 무결점 + Hallmark 48 테마)"
hexagrams: ["#61 풍택중부 ☴☱", "#15 지산겸 ☷☶"]
---

# 🛡️ 아온 임페커블 UI 폴리시 & 오픈셸·클라우드플레어 적대적 교차감사 방패 (aon_impeccable_audit_shield)

## 📌 개요
제26기관 `rgon_aon_impeccable_audit_shield.py`에서 제공하는 적대적 반박 교차감사 및 UI 무결점 탐지 스킬.

## 🛠️ 핵심 기능
1. **Cloudflare `security-audit-skill` 기반 2단계 적대적 반박·교차감사 (`adversarial_two_phase_audit`)**:
   - Phase 1 (Finder Agent): 의심 후보군 탐색.
   - Phase 2 (Challenger Agent): 가혹한 반박 테스트를 통한 오탐(False Positive) 100% 제거.
2. **NVIDIA `OpenShell` 기반 샌드박스 & 정책 동결 가드 (`openshell_policy_guard`)**:
   - 워크스페이스 경계 준수, 보호 파일 무결성 및 데몬 0개 강제, SHA-256 정책 해시 동결.
3. **`pbakaus/impeccable` 62규칙 UI 결함 탐지 & `Nutlope/hallmark` 48개 테마 카탈로그 (`impeccable_ui_detector`)**:
   - 24개 Impeccable 디자인 커맨드 및 62개 결정론적 UI 결함 규칙 스캔, UI 무결점 100.0점 산출.
4. **Claude How-To Hook & AWS Agent Toolkit 연쇄 실행기 (`run_post_edit_hook`)**:
   - 코드/UI 수정 시 3대 엔진을 연쇄 교차감사하여 런타임 결함 사전 방어.
