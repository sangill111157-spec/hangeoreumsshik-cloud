---
name: aon-general-hospital
description: "제40기관 아온 초일류 종합병원 — 119 소방서(Fast-Path <2s 바이탈·포렌식 보존·3초 자동수혈) × 무인 AS센터(8단계 RCA·완치영수증) × 정밀 영상의학과(전신 혈관·모바일 엣지 안과·시냅스 뇌파) × 카파시 외과수술실(핀셋수술) × 백혈구 자가치료(3중 동기화 봉합) 마스터 센터"
version: v11.66-AON-GENERAL-HOSPITAL
organ: 40
skill_no: 60
antibody: R64_GENERAL_HOSPITAL_119_AS_WBC_AUTO_HEAL_GUARD
hexagram: "#14 화천대유(火天大有)"
created_at: 2026-10-28T03:15:00+09:00
---

# 🏥 [스킬 #60] 제40기관 아온 초일류 종합병원 마스터 센터

## 1. 개요 및 헌법적 위상
- **주관 기관:** 제40기관 『아온 초일류 종합병원』 (`step65_aon_general_hospital_self_healing.py`)
- **버전:** `v11.66-AON-GENERAL-HOSPITAL` · **항체:** `R64_GENERAL_HOSPITAL_119_AS_WBC_AUTO_HEAL_GUARD` (`R1~R64`)
- **승인:** 이상일 대표님 | **설계:** RGON 사령부 G1 · 르곤(G2) 교차검증

## 2. 5대 진료과 진료 체계
1. **🚒 D01 119 소방서 & 권역응급의료센터:**
   - 4대 절대 보호 파일 MD5 바이탈 실시간 감시
   - Python AST 구문 화재 및 JSON 골절 0건 유지
   - 손상 파일 발생 시 `.corrupt-<timestamp>` 포렌식 보존 후 3초 내 정상 백업 자동 수혈(롤백)
2. **🛠️ D02 무인 AS센터 & 원스톱 외래 진료소:**
   - 8단계 RCA: 관찰(Observe) ➔ 재현(Reproduce) ➔ 추적(Trace/GRAPH_REPORT.md) ➔ 가설(Hypothesize) ➔ 입증(Prove) ➔ 처방(Fix) ➔ 항체등록(Prevent) ➔ 완치영수증(Receipt)
   - 모바일 버튼 겹침, 깡통 대답 등 접수 즉시 `#AS-2026-XXXX` 영수증 발급
3. **🔬 D03 정밀 영상의학과 & 종합건강검진센터:**
   - 전신 세포(파일) 혈관 스캔
   - 모바일 375x812 우측 엣지 잘림(edge_clipped) 안과 검진
   - 신경망 시냅스 100.0점 뇌파 검사
4. **🩺 D04 카파시 외과수술실 & 포니테일 성형외과:**
   - Karpathy 4원칙: 아픈 부위만 핀셋 수술 (주변 멀쩡한 장기 접촉 0%)
   - Ponytail 7단 사다리: 기존 코드 재사용 우선 (비대 코드 53% 다이어트)
5. **🧬 D05 백혈구 자가치료 & 백신 면역연구소:**
   - 본관/dashboard/docs 3중 동기화 DRIFT_DETECTED 감지 즉시 SSOT 세포 복제 ➔ AUTO_HEALED 봉합
   - `hospital_health.jsonl` 최대 500줄 원자적 회전 캡핑 보존

## 3. 종합검진표 및 CLI 가동
- 종합검진표: `HOSPITAL_MEDICAL_CHART.md`
- 진단 로그: `hospital_health.jsonl`
- CLI:
  ```bash
  python -X utf8 step65_aon_general_hospital_self_healing.py --self-test
  python -X utf8 step65_aon_general_hospital_self_healing.py --root .
  python -X utf8 step65_aon_general_hospital_self_healing.py --root . --as "모바일 우측 버튼 겹침"
  ```

<!-- RGON_IMMUTABLE_WORK_DNA_V1176 -->
> **[RGON 불변의 일처리 8대 법칙 (Immutable Work DNA v11.76 · 항체 R69) 이식 완료]**
> 1. Global Top-1 Benchmark | 2. Karpathy 4-Rules & LLM Council | 3. Master KeyVault Leverage (0% Leak) | 4. Chronometer Runtime Proof | 5. Maestro Synergy DAG Relay | 6. Ponytail Zero-Bloat Diet | 7. Water Self-Healing & Samseong(三省) | 8. Commander Approval Gate
<!-- /RGON_IMMUTABLE_WORK_DNA_V1176 -->
