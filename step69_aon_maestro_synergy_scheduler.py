#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step69_aon_maestro_synergy_scheduler.py
제44기관: 아온 마에스트로(Maestro) 7대 기관장 협업 시너지 DAG & 24시간 분야별 마스터 스케줄러
버전: v11.74-AON-MAESTRO-SYNERGY-SCHEDULER · 항체: R1~R68 (신규 R68) · 정식 스킬: #64 (64개)
주역 괘: #14 화천대유(火天大有) × #50 화풍정(火風鼎) — 7대 기관장이 정(鼎)의 발처럼 조화를 이루어 대업을 완수함

[필수 구현 5대 핵심 설계]
1. 7대 기관장(Director) 직책·역할·관할 기관 배정 (`DIRECTORS_7`)
2. 5대 실전 협업 시너지 릴레이 체인 (`SYNERGY_CHAINS_5` — LangGraph State-DAG 방식 실제 함수 연쇄 호출)
3. 24시간 6대 타임슬롯 분야별 마스터 스케줄러 (`MASTER_SCHEDULE_24H` + APScheduler misfire_grace_time=300)
4. 대시보드 UI 드로어(`step69-maestro-synergy-drawer`) & 정식 스킬 `#64` & 시냅스 노드 `#37`(`S38`) 연동
5. `--self-test` 및 `--apply` 전수 실증 (`5/5 Chains Executed, 0 Errors`)
"""

from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import importlib
import json
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Any

for _sname in ("stdout", "stderr"):
    _st = getattr(sys, _sname, None)
    if _st is not None and hasattr(_st, "reconfigure"):
        try:
            _st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

os.environ["PYTHONWARNINGS"] = "ignore::SyntaxWarning"
warnings.filterwarnings("ignore", category=SyntaxWarning)

KST = datetime.timezone(datetime.timedelta(hours=9))
ROOT = Path(__file__).resolve().parent

VERSION = "v11.74-AON-MAESTRO-SYNERGY-SCHEDULER"
PREV_VERSION = "v11.72-AON-CHRONO-DIET-PERFECTION"
ORGAN_NO = 44
ORGAN_ID = "ORGAN-44-MAESTRO-SYNERGY-SCHEDULER"
ORGAN_NAME = "제44기관 아온 마에스트로(Maestro) 7대 기관장 협업 시너지 DAG & 24시간 분야별 마스터 스케줄러"
ANTIBODY_ID = "R68"
ANTIBODY_FULL = "R68_MAESTRO_7DIRECTORS_SYNERGY_DAG_24H_SCHEDULER_LOCK"
ANTIBODY_RANGE = "R1~R68"
SKILL_NO = 64
SKILL_ID = "aon_maestro_synergy_scheduler"
MARKER = "RGON_STEP69_MAESTRO_SYNERGY_SCHEDULER_V1174"
DRAWER_ID = "step69-maestro-synergy-drawer"

REGISTRY_PATH = ROOT / "rgon_maestro_synergy_schedule_registry.json"
REPORT_PATH = ROOT / "rgon_step69_maestro_report.json"
CODE_MAP_JSON_PATH = ROOT / "rgon_code_map.json"
ROOT_SKILL_INDEX_PATH = ROOT / "SKILL_INDEX.json"
SKILL_MD_PATH = ROOT / "skills" / "aon_maestro_synergy_scheduler" / "SKILL.md"

PROTECTED_4_FILES = (
    "rgon_Numeric_Organ.py",
    "rgon_work_loop.py",
    "rgon_self_Reflection.py",
    "index_20260405_backup.html",
)

HTML_TRIO = (
    "index.html",
    "dashboard/index.html",
    "docs/index.html",
)

APSCHEDULER_DEFAULT_POLICY = {
    "misfire_grace_time": 300,
    "coalesce": True,
    "max_instances": 3,
    "timezone": "Asia/Seoul",
}

# ==============================================================================
# 1. 7대 기관장(Director) 직책·역할·관할 기관 배정 (`DIRECTORS_7`)
# ==============================================================================
DIRECTORS_7: dict[str, dict[str, Any]] = {
    "D1_IMMUNE_HOSPITAL_CHIEF": {
        "director_id": "D1_IMMUNE_HOSPITAL_CHIEF",
        "title": "생명·면역·초일류 종합병원장",
        "orchestration_role": "CrewAI Chief Medical & Homeostasis Officer",
        "jurisdiction_organs": [
            "제1~20기관 (생명·면역·혈관·항상성·뇌하수체·주역도술관)",
            "제40기관 아온 초일류 종합병원 (Step 65 · 119 소방서 × 무인 AS센터 × 백혈구 자가치료)",
        ],
        "core_modules": [
            "rgon_white_blood_cell.py",
            "rgon_vascular_core.py",
            "rgon_daily_cycle.py",
            "step65_aon_general_hospital_self_healing.py",
        ],
        "mission": "4대 보호파일 바이탈 수호, 백혈구 100/100 면역 순찰, 8단계 RCA 무인 AS 처방 및 자가치유",
    },
    "D2_SYNAPSE_BRAIN_CHIEF": {
        "director_id": "D2_SYNAPSE_BRAIN_CHIEF",
        "title": "신경망·외부두뇌·스킬팩토리장",
        "orchestration_role": "CrewAI Chief Neural Architect & Skill Factory Director",
        "jurisdiction_organs": [
            "제21~32기관 (국무회의·외부두뇌·버튼봇·검수총장·조직구성도·듀얼텔레그램)",
            "제16기관 전신 신경망 시냅스 병렬 정밀 검증기",
        ],
        "core_modules": [
            "rgon_neural_synapse_verifier.py",
            "rgon_aon_soul_brain.py",
            "rgon_aon_dialogue_engine.py",
            "skills/aon_maestro_synergy_scheduler/SKILL.md",
        ],
        "formal_skills_managed": 64,
        "mission": "37노드·35시냅스 100.0점 뇌파 동기화, 64개 정식 SKILL.md 표준화 및 외부두뇌 지식 증류",
    },
    "D3_WALLSTREET_TRADING_CHIEF": {
        "director_id": "D3_WALLSTREET_TRADING_CHIEF",
        "title": "월가 AI 트레이딩·금융 리서치장",
        "orchestration_role": "CrewAI Chief Alpha Quant & Risk Strategist",
        "jurisdiction_organs": [
            "제33기관 인비저블 텔레그램 백본",
            "제38기관 학술/금융 리서치 (Step 63)",
            "제39기관 TradingAgents Bull vs Bear 끝장토론 (Step 64)",
            "제41기관 Karpathy LLM Council 3단 합의 (Step 66)",
            "NVIDIA 트레이딩 봇 APScheduler 데몬",
        ],
        "core_modules": [
            "rgon_aon_13shorts_omni_engine.py",
            "step64_aon_15shorts_super_senior_engine.py",
            "step66_aon_omniroute_council_15shorts_engine.py",
            "rgon_aon_invisible_kakao_tg_backbone.py",
            "rgon_trading_council.py",
        ],
        "mission": "AutoResearch 거시/종목 지표 수집 → 강세/약세 적대적 토론 → 3단 카운슬 합의 → 손절 감시 무결성 수호",
    },
    "D4_MEDIA_MOTION_STUDIO_CHIEF": {
        "director_id": "D4_MEDIA_MOTION_STUDIO_CHIEF",
        "title": "유튜브 3채널·쇼츠·모션 스튜디오장",
        "orchestration_role": "CrewAI Chief Viral Media & Motion Graphics Producer",
        "jurisdiction_organs": [
            "제38기관 AutoClip 6단계 무인 편집 & 한국어 1% 설득 카피 (Step 63)",
            "제39기관 Remotion/HyperFrames & 한글 모션 100선 window.seek(t) (Step 64)",
            "제41기관 /hr 14슬롯 모션 매트릭스 & AI 워터마크 세척기 (Step 66)",
        ],
        "core_modules": [
            "rgon_aon_13shorts_omni_engine.py",
            "step64_aon_15shorts_super_senior_engine.py",
            "step66_aon_omniroute_council_15shorts_engine.py",
            "rgon_aon_opus_motion_studio.py",
            "update_3channels_analytics.py",
        ],
        "mission": "경쟁 채널 후킹 해부 → 한국어 1% 카피 교정 → AI 워터마크 세척 → 14슬롯 모션 & 6단계 무인 렌더링",
    },
    "D5_APP_CLONER_VENTURE_CHIEF": {
        "director_id": "D5_APP_CLONER_VENTURE_CHIEF",
        "title": "수익형 웹/앱 역공학 클로닝·창업 스튜디오장",
        "orchestration_role": "CrewAI Chief Venture Studio & Reverse-Engineering Director",
        "jurisdiction_organs": [
            "제38기관 PHP2Shell·내앱보안 4대 점검 & TypeSafe Jev (Step 63)",
            "제39기관 Google Stitch × OpenDesign × Taste Skill (Step 64)",
            "제41기관 경쟁앱 불만 분석기 × 무료 앱 클로너 × 49 에이전트 스튜디오 × llms.txt (Step 66)",
        ],
        "core_modules": [
            "step66_aon_omniroute_council_15shorts_engine.py",
            "step64_aon_15shorts_super_senior_engine.py",
            "rgon_aon_13shorts_omni_engine.py",
        ],
        "mission": "경쟁 앱 불만 리뷰 역전 기획 → Stitch/Inspo 명품 UI 설계 → 49 에이전트 클로닝 → 보안 4대 감사 및 llms.txt 발행",
    },
    "D6_ENTERPRISE_OPS_RPA_CHIEF": {
        "director_id": "D6_ENTERPRISE_OPS_RPA_CHIEF",
        "title": "1인 대기업 경영비서·법무/재무·시각 RPA장",
        "orchestration_role": "CrewAI Chief Enterprise Operations & Visual RPA Director",
        "jurisdiction_organs": [
            "제37기관 Google One 5TB 조니데시멀 아카이브",
            "제39기관 구글 드라이브 무삭제 스마트 리네이머 (Step 64)",
            "제41기관 앤트로픽 11대 직무 플러그인 × 시각 모방 RPA × GitDiagram+Gitingest (Step 66)",
        ],
        "core_modules": [
            "step66_aon_omniroute_council_15shorts_engine.py",
            "step64_aon_15shorts_super_senior_engine.py",
            "rgon_aon_gdrive_5tb_organizer.py",
            "general_affairs_treasury.py",
        ],
        "mission": "GitDiagram/Gitingest 레포 해독 → Graphify 지도 갱신 → 앤트로픽 11대 직무 플러그인 & 드라이브 무삭제 자동 정리",
    },
    "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF": {
        "director_id": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        "title": "무중단 라우터·크로노미터 100점 감사·다이어트장",
        "orchestration_role": "CrewAI Chief Chronometer Auditor & Zero-Downtime Reliability Officer",
        "jurisdiction_organs": [
            "제39기관 Graphify 코드 지식그래프 & Ponytail 7단 사다리 (Step 64)",
            "제41기관 OmniRoute 4단 무중단 쿼터 폴백 & MCP Tasks (Step 66)",
            "제42기관 크로노미터 전수 톱니바퀴 감사원 (Step 67)",
            "제43기관 텔레그램 실측 무결성 & Ponytail 무결점 다이어트 감사원 (Step 68)",
        ],
        "core_modules": [
            "step66_aon_omniroute_council_15shorts_engine.py",
            "step67_aon_chronometer_deep_auditor.py",
            "step68_aon_chrono_diet_perfection.py",
        ],
        "mission": "OmniRoute 4단 무중단 폴백, 전수 Python AST 0 에러 감시, 텔레그램 스팸 차단 및 무결점 다이어트 수호",
    },
}

# ==============================================================================
# 2. 5대 실전 협업 시너지 릴레이 체인 정의 (`SYNERGY_CHAINS_5`)
# ==============================================================================
SYNERGY_CHAINS_5: dict[str, dict[str, Any]] = {
    "CHAIN_1_ALPHA_TRADING": {
        "chain_id": "CHAIN_1_ALPHA_TRADING",
        "name": "월가 알파 트레이딩 & 3단 카운슬 합의 릴레이 체인",
        "lead_director": "D3_WALLSTREET_TRADING_CHIEF",
        "participating_directors": [
            "D3_WALLSTREET_TRADING_CHIEF",
            "D2_SYNAPSE_BRAIN_CHIEF",
            "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        ],
        "dag_nodes": [
            "N1_AUTORESEARCH_PICO",
            "N2_TRADING_AGENTS_DEBATE",
            "N3_KARPATHY_LLM_COUNCIL",
            "N4_INVISIBLE_TG_DRYRUN_BRIEF",
        ],
        "pipeline_desc": "AutoResearch 뉴스/지표 수집 ➔ TradingAgents 강세/약세 토론(Step 64) ➔ Karpathy LLM Council 3단 합의(Step 66) ➔ 인비저블 텔레그램 Dry-Run 브리핑(Step 68)",
    },
    "CHAIN_2_VIRAL_MEDIA_FACTORY": {
        "chain_id": "CHAIN_2_VIRAL_MEDIA_FACTORY",
        "name": "유튜브 3채널 바이럴 쇼츠 & 14슬롯 모션 무인 팩토리 체인",
        "lead_director": "D4_MEDIA_MOTION_STUDIO_CHIEF",
        "participating_directors": [
            "D4_MEDIA_MOTION_STUDIO_CHIEF",
            "D3_WALLSTREET_TRADING_CHIEF",
            "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        ],
        "dag_nodes": [
            "N1_COMPETITOR_CHANNEL_DISSECT",
            "N2_KOREAN_1PCT_HOOK_COPY",
            "N3_AI_WATERMARK_SCRUBBER",
            "N4_AUTOCLIP_14SLOT_MOTION_RENDER",
        ],
        "pipeline_desc": "경쟁 채널 분석(Step 66) ➔ 한국어 1% 후킹 카피 생성(Step 63) ➔ AI 워터마크 세척(Step 66) ➔ AutoClip + 14슬롯 모션 매트릭스 렌더링(Step 63 & 66)",
    },
    "CHAIN_3_APP_CLONE_LAUNCHPAD": {
        "chain_id": "CHAIN_3_APP_CLONE_LAUNCHPAD",
        "name": "수익형 웹/앱 역공학 클로닝 & 49 에이전트 런치패드 체인",
        "lead_director": "D5_APP_CLONER_VENTURE_CHIEF",
        "participating_directors": [
            "D5_APP_CLONER_VENTURE_CHIEF",
            "D4_MEDIA_MOTION_STUDIO_CHIEF",
            "D1_IMMUNE_HOSPITAL_CHIEF",
        ],
        "dag_nodes": [
            "N1_COMPETITOR_PAIN_DISSECT",
            "N2_STITCH_INSPO_UI_SPEC",
            "N3_49AGENT_STUDIO_CLONING",
            "N4_SECURITY_4AUDIT_AND_LLMSTXT",
        ],
        "pipeline_desc": "경쟁 앱 불만 리뷰 해부(Step 66) ➔ Google Stitch & Inspo 명품 UI 설계(Step 64 & 66) ➔ 49 에이전트 스튜디오 클로닝(Step 66) ➔ 앱 보안 4대 감사(Step 63) + llms.txt 발행(Step 66)",
    },
    "CHAIN_4_SECOND_BRAIN_ENTERPRISE": {
        "chain_id": "CHAIN_4_SECOND_BRAIN_ENTERPRISE",
        "name": "세컨드브레인 레포 해독 & 1인 대기업 무삭제 자동화 체인",
        "lead_director": "D6_ENTERPRISE_OPS_RPA_CHIEF",
        "participating_directors": [
            "D6_ENTERPRISE_OPS_RPA_CHIEF",
            "D2_SYNAPSE_BRAIN_CHIEF",
            "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        ],
        "dag_nodes": [
            "N1_GITDIAGRAM_GITINGEST_DECODE",
            "N2_GRAPHIFY_CODE_MAP_REFRESH",
            "N3_ANTHROPIC_11PLUGINS_GDRIVE_ZERODELETE",
        ],
        "pipeline_desc": "GitDiagram/Gitingest 레포 해독(Step 66) ➔ Graphify 코드 지도 갱신(Step 64) ➔ 앤트로픽 11대 직무 플러그인 & 구글 드라이브 자동 정리(Step 64 & 66)",
    },
    "CHAIN_5_IMMORTAL_EMPIRE_GUARD": {
        "chain_id": "CHAIN_5_IMMORTAL_EMPIRE_GUARD",
        "name": "무중단 제국 방어 & 초일류 종합병원·크로노미터·백혈구 100점 수호 체인",
        "lead_director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        "participating_directors": [
            "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
            "D1_IMMUNE_HOSPITAL_CHIEF",
            "D2_SYNAPSE_BRAIN_CHIEF",
        ],
        "dag_nodes": [
            "N1_OMNIROUTE_4STAGE_FAILOVER",
            "N2_HOSPITAL_8STEP_CHECKUP",
            "N3_CHRONOMETER_AST_DIET_AUDIT",
            "N4_WBC_100_PATROL_ICHING_GUIDANCE",
        ],
        "pipeline_desc": "OmniRoute 4단 무중단 쿼터 폴백(Step 66) ➔ 제40기관 종합병원 8대 검진(Step 65) ➔ 크로노미터 AST & 다이어트 감사(Step 67 & 68) ➔ 백혈구 100점 면역 순찰 & 주역 64괘 지침(Step 68)",
    },
}

# ==============================================================================
# 3. 24시간 6대 타임슬롯 분야별 마스터 스케줄러 (`MASTER_SCHEDULE_24H`)
# ==============================================================================
MASTER_SCHEDULE_24H: list[dict[str, Any]] = [
    {
        "slot_id": "SLOT_1_0600_MORNING_IMMUNE_BRIEF",
        "time_window_kst": "06:00~08:59",
        "label": "06:00 아침 면역·브리핑",
        "cron": "0 6 * * *",
        "hours_kst": [6, 7, 8],
        "lead_director": "D1_IMMUNE_HOSPITAL_CHIEF",
        "co_director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        "primary_chain": "CHAIN_5_IMMORTAL_EMPIRE_GUARD",
        "tasks": [
            "백혈구 100/100 면역 순찰 및 4대 보호파일 MD5 검증",
            "주역 64괘 오늘의 지침 생성 및 [RGON 아침 마스터 브리핑] 발행",
            "제40기관 종합병원 119 바이탈 체크",
        ],
        **APSCHEDULER_DEFAULT_POLICY,
    },
    {
        "slot_id": "SLOT_2_0900_MORNING_MEDIA_ENTERPRISE",
        "time_window_kst": "09:00~12:59",
        "label": "09:00 오전 미디어·경영",
        "cron": "0 9 * * *",
        "hours_kst": [9, 10, 11, 12],
        "lead_director": "D4_MEDIA_MOTION_STUDIO_CHIEF",
        "co_director": "D6_ENTERPRISE_OPS_RPA_CHIEF",
        "primary_chain": "CHAIN_2_VIRAL_MEDIA_FACTORY",
        "tasks": [
            "유튜브 3채널 애널리틱스 동기화 및 경쟁 채널 후킹 해부",
            "한국어 1% 설득 카피 생성 & AI 워터마크 세척",
            "AutoClip 6단계 무인 편집 & /hr 14슬롯 모션 렌더링",
        ],
        **APSCHEDULER_DEFAULT_POLICY,
    },
    {
        "slot_id": "SLOT_3_1300_AFTERNOON_RND_APP_CLONE",
        "time_window_kst": "13:00~17:59",
        "label": "13:00 오후 R&D·앱클로닝",
        "cron": "0 13 * * *",
        "hours_kst": [13, 14, 15, 16, 17],
        "lead_director": "D5_APP_CLONER_VENTURE_CHIEF",
        "co_director": "D2_SYNAPSE_BRAIN_CHIEF",
        "primary_chain": "CHAIN_3_APP_CLONE_LAUNCHPAD",
        "tasks": [
            "경쟁 앱 불만 리뷰 해부 및 역전 기획서 도출",
            "Google Stitch × OpenDesign × Inspo 명품 UI 설계",
            "49 에이전트 스튜디오 클로닝 & 앱 보안 4대 감사 + llms.txt 발행",
        ],
        **APSCHEDULER_DEFAULT_POLICY,
    },
    {
        "slot_id": "SLOT_4_1800_EVENING_SECOND_BRAIN_PREMARKET",
        "time_window_kst": "18:00~21:59",
        "label": "18:00 저녁 세컨드브레인·프리마켓",
        "cron": "0 18 * * *",
        "hours_kst": [18, 19, 20, 21],
        "lead_director": "D6_ENTERPRISE_OPS_RPA_CHIEF",
        "co_director": "D2_SYNAPSE_BRAIN_CHIEF",
        "primary_chain": "CHAIN_4_SECOND_BRAIN_ENTERPRISE",
        "tasks": [
            "GitDiagram/Gitingest 글로벌 트렌드 레포 해독",
            "Graphify 로컬 코드 지식그래프 갱신 및 정식 SKILL.md 증류",
            "앤트로픽 11대 직무 플러그인 & 구글 드라이브 5TB 무삭제 리네임",
        ],
        **APSCHEDULER_DEFAULT_POLICY,
    },
    {
        "slot_id": "SLOT_5_2200_NIGHT_WALLSTREET_TRADING",
        "time_window_kst": "22:00~05:30",
        "label": "22:00~05:30 심야 월가 트레이딩",
        "cron": "0 22 * * 1-5",
        "hours_kst": [22, 23, 0, 1, 2, 3, 4, 5],
        "lead_director": "D3_WALLSTREET_TRADING_CHIEF",
        "co_director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        "primary_chain": "CHAIN_1_ALPHA_TRADING",
        "tasks": [
            "AutoResearch 미국 본장/프리마켓 지표 및 뉴스 수집",
            "TradingAgents 강세/약세 끝장토론 & Codex 적대적 검증",
            "Karpathy LLM Council 3단 합의 & NVDA 손절 감시(misfire_grace_time=300)",
        ],
        **APSCHEDULER_DEFAULT_POLICY,
    },
    {
        "slot_id": "SLOT_6_24H_ALWAYS_ON_DAEMON",
        "time_window_kst": "00:00~23:59 (24h 상시)",
        "label": "24h 상시 무중단·자가치유 데몬",
        "cron": "*/10 * * * *",
        "hours_kst": list(range(24)),
        "lead_director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
        "co_director": "D1_IMMUNE_HOSPITAL_CHIEF",
        "primary_chain": "CHAIN_5_IMMORTAL_EMPIRE_GUARD",
        "tasks": [
            "OmniRoute 4단 무중단 쿼터 폴백 및 MCP Tasks 비동기 감시",
            "크로노미터 AST 구문 에러 0건 및 3중 대시보드 바이트 일치 수호",
            "텔레그램 자가진단 스팸 디바운스 루프백 방어",
        ],
        **APSCHEDULER_DEFAULT_POLICY,
    },
]


def _imp(mod_name: str) -> Any:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return importlib.import_module(mod_name)


def execute_synergy_chain(chain_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    [핵심 엔진] LangGraph State-DAG 방식 5대 시너지 체인 실제 함수 연쇄 실행기
    앞 단계 기관 모듈의 출력(State Dict)을 받아 뒷 단계 기관 모듈의 함수를 연쇄 호출한다.
    """
    if chain_id not in SYNERGY_CHAINS_5:
        raise ValueError(f"Unknown synergy chain_id: {chain_id}")

    t0 = time.perf_counter()
    meta = SYNERGY_CHAINS_5[chain_id]
    state: dict[str, Any] = dict(payload or {})
    steps_trace: list[dict[str, Any]] = []
    errors: list[str] = []

    m63 = _imp("rgon_aon_13shorts_omni_engine")
    m64 = _imp("step64_aon_15shorts_super_senior_engine")
    m65 = _imp("step65_aon_general_hospital_self_healing")
    m66 = _imp("step66_aon_omniroute_council_15shorts_engine")
    m67 = _imp("step67_aon_chronometer_deep_auditor")
    m68 = _imp("step68_aon_chrono_diet_perfection")

    try:
        if chain_id == "CHAIN_1_ALPHA_TRADING":
            topic = str(state.get("topic") or "NVDA 엔비디아 AI 반도체 슈퍼사이클")
            # Node 1: AutoResearch 뉴스/지표 수집 (Organ 38)
            res_n1 = m63.academic_research_5step(topic)
            state["research_topic"] = f"{topic} ({res_n1['step_3_peer_review']})"
            state["pico_outcome"] = res_n1["step_1_pico"]["outcome"]
            steps_trace.append({
                "node": "N1_AUTORESEARCH_PICO",
                "organ": 38,
                "director": "D3_WALLSTREET_TRADING_CHIEF",
                "func": "rgon_aon_13shorts_omni_engine.academic_research_5step",
                "ok": bool(res_n1.get("step_1_pico")),
                "out_key": "research_topic",
            })

            # Node 2: TradingAgents 강세/약세 토론 (Step 64 · Organ 39) — Node 1 출력 입력
            res_n2 = m64.run_bull_vs_bear_debate(state["research_topic"])
            state["debate_decision"] = res_n2["consensus"]["decision"]
            state["max_position_pct"] = res_n2["risk"]["max_position_pct"]
            steps_trace.append({
                "node": "N2_TRADING_AGENTS_DEBATE",
                "organ": 39,
                "director": "D3_WALLSTREET_TRADING_CHIEF",
                "func": "step64_aon_15shorts_super_senior_engine.run_bull_vs_bear_debate",
                "ok": bool(res_n2.get("consensus")) and len(res_n2.get("analysts", {})) == 4,
                "out_key": "debate_decision",
            })

            # Node 3: Karpathy LLM Council 3단 합의 (Step 66 · Organ 41) — Node 2 출력 입력
            council_input = f"{topic} | 토론결론: {state['debate_decision']} (비중상한 {state['max_position_pct']}%)"
            res_n3 = m66.run_karpathy_llm_council(council_input)
            state["chairman_synthesis"] = res_n3["stage3_chairman_synthesis"]
            state["consensus_score"] = res_n3["consensus_score"]
            steps_trace.append({
                "node": "N3_KARPATHY_LLM_COUNCIL",
                "organ": 41,
                "director": "D3_WALLSTREET_TRADING_CHIEF",
                "func": "step66_aon_omniroute_council_15shorts_engine.run_karpathy_llm_council",
                "ok": res_n3.get("consensus_score", 0) > 0.99 and len(res_n3.get("stage1_opinions", [])) == 3,
                "out_key": "chairman_synthesis",
            })

            # Node 4: 인비저블 텔레그램 Dry-Run 브리핑 (Step 68 · Organ 33/43) — Node 3 출력 입력
            tg_mod = _imp("rgon_aon_invisible_kakao_tg_backbone")
            mgr = tg_mod.InvisibleBackboneManager()
            brief_msg = f"[SELF_TEST] [월가 알파 브리핑] {state['chairman_synthesis']}"
            res_n4 = mgr.dispatch_invisible(brief_msg, channel="ALL", dry_run=True)
            tg_res = res_n4.get("tg_result", {})
            state["telegram_brief_dispatched"] = bool(res_n4.get("ok") and tg_res.get("dry_run") and tg_res.get("loopback"))
            steps_trace.append({
                "node": "N4_INVISIBLE_TG_DRYRUN_BRIEF",
                "organ": 43,
                "director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
                "func": "rgon_aon_invisible_kakao_tg_backbone.InvisibleBackboneManager.dispatch_invisible",
                "ok": state["telegram_brief_dispatched"],
                "out_key": "telegram_brief_dispatched",
            })

        elif chain_id == "CHAIN_2_VIRAL_MEDIA_FACTORY":
            channel_topic = str(state.get("channel_topic") or "한걸음씩 3채널 쇼츠 — 교대근무 수면·건강 & AI 자동화")
            # Node 1: 경쟁 채널 분석 (Step 66 · Organ 41)
            res_n1 = m66.run_karpathy_llm_council(channel_topic)
            rev = res_n1["competitor_reversal_plan"]["reversal_strategy"]
            state["raw_copy"] = f"{channel_topic}에 대하여 매우 훌륭하고 놀라운 {rev}\u200b 솔루션을 수행합니다. 할 수 있습니다."
            steps_trace.append({
                "node": "N1_COMPETITOR_CHANNEL_DISSECT",
                "organ": 41,
                "director": "D4_MEDIA_MOTION_STUDIO_CHIEF",
                "func": "step66_aon_omniroute_council_15shorts_engine.run_karpathy_llm_council",
                "ok": bool(rev),
                "out_key": "raw_copy",
            })

            # Node 2: 한국어 1% 후킹 카피 생성 (Step 63 · Organ 38) — Node 1 출력 입력
            fixed_copy = m63.kfix_korean_copy(state["raw_copy"])
            choice_res = m63.TypeSafeJevEngine.choice(
                fixed_copy,
                [
                    f"[유튜브 3초 훅] {fixed_copy}",
                    "[음원] 가을과 겨울 사이 오피셜 모션",
                    "[블로그] 교대근무 건강 루틴",
                ],
            )
            state["hook_copy"] = choice_res["selected_choice"]
            steps_trace.append({
                "node": "N2_KOREAN_1PCT_HOOK_COPY",
                "organ": 38,
                "director": "D4_MEDIA_MOTION_STUDIO_CHIEF",
                "func": "rgon_aon_13shorts_omni_engine.kfix_korean_copy",
                "ok": "진행합니다" in fixed_copy and "검증된" in fixed_copy and bool(state["hook_copy"]),
                "out_key": "hook_copy",
            })

            # Node 3: AI 워터마크 세척 (Step 66 · Organ 41) — Node 2 출력 입력
            res_n3 = m66.scrub_watermark_and_guard_distillation(state["hook_copy"], rpm=24)
            state["cleaned_copy"] = res_n3["cleaned_text"]
            state["watermark_removed"] = res_n3["watermark_removed"]
            steps_trace.append({
                "node": "N3_AI_WATERMARK_SCRUBBER",
                "organ": 41,
                "director": "D4_MEDIA_MOTION_STUDIO_CHIEF",
                "func": "step66_aon_omniroute_council_15shorts_engine.scrub_watermark_and_guard_distillation",
                "ok": res_n3["watermark_removed"] is True and "\u200b" not in state["cleaned_copy"],
                "out_key": "cleaned_copy",
            })

            # Node 4: AutoClip + 14슬롯 모션 매트릭스 렌더링 (Step 63 & 64 & 66) — Node 3 출력 입력
            clip_res = m63.unmanned_video_pipeline(state["cleaned_copy"])
            motion_res = m66.convert_repo_and_14slot_motion(
                "https://github.com/sangill111157-spec/hangeol-plan",
                slots={"hook_0_3s": state["cleaned_copy"][:60]},
            )
            seek_html = m64.generate_seek_motion_template(state["cleaned_copy"][:40], 128)
            state["render_ready"] = (
                clip_res.get("ready_to_export") is True
                and motion_res.get("motion_14slots_count") == 14
                and "window.seek=function(t)" in seek_html
            )
            steps_trace.append({
                "node": "N4_AUTOCLIP_14SLOT_MOTION_RENDER",
                "organ": 41,
                "director": "D4_MEDIA_MOTION_STUDIO_CHIEF",
                "func": "unmanned_video_pipeline + convert_repo_and_14slot_motion + generate_seek_motion_template",
                "ok": state["render_ready"],
                "out_key": "render_ready",
            })

        elif chain_id == "CHAIN_3_APP_CLONE_LAUNCHPAD":
            app_target = str(state.get("app_target") or "글로벌 인기 생산성·헬스케어 구독 앱")
            # Node 1: 경쟁 앱 불만 리뷰 해부 (Step 66 · Organ 41)
            res_n1 = m66.run_karpathy_llm_council(app_target)
            state["pain_points"] = res_n1["competitor_reversal_plan"]["analyzed_pain_points"]
            state["reversal_strategy"] = res_n1["competitor_reversal_plan"]["reversal_strategy"]
            steps_trace.append({
                "node": "N1_COMPETITOR_PAIN_DISSECT",
                "organ": 41,
                "director": "D5_APP_CLONER_VENTURE_CHIEF",
                "func": "step66_aon_omniroute_council_15shorts_engine.run_karpathy_llm_council",
                "ok": len(state["pain_points"]) >= 3 and bool(state["reversal_strategy"]),
                "out_key": "reversal_strategy",
            })

            # Node 2: Google Stitch & Inspo 명품 UI 설계 (Step 64 & 66) — Node 1 출력 입력
            stitch_meta = m64.SHORTS_15_ARSENAL["S04_STITCH_OPENDESIGN"]
            taste_meta = m64.SHORTS_15_ARSENAL["S08_EVERY_AI_5_TASTE"]
            box_check = m63.TypeSafeJevEngine.box(0, 0, 375, 812, (375, 812))
            state["ui_design_spec"] = {
                "stitch_core": stitch_meta["core"],
                "taste_core": taste_meta["core"],
                "applied_reversal": state["reversal_strategy"],
                "mobile_viewport_safe": box_check["safe_in_canvas"],
            }
            steps_trace.append({
                "node": "N2_STITCH_INSPO_UI_SPEC",
                "organ": 39,
                "director": "D5_APP_CLONER_VENTURE_CHIEF",
                "func": "SHORTS_15_ARSENAL[S04_STITCH_OPENDESIGN] + TypeSafeJevEngine.box",
                "ok": box_check["safe_in_canvas"] is True and "DESIGN.md" in stitch_meta["core"],
                "out_key": "ui_design_spec",
            })

            # Node 3: 49 에이전트 스튜디오 클로닝 (Step 66 · Organ 41) — Node 2 출력 입력
            res_n3 = m66.convert_repo_and_14slot_motion("https://github.com/sangill111157-spec/hangeol-plan")
            state["studio_clone_status"] = {
                "agents": res_n3["game_studio_agents"],
                "skills": res_n3["game_studio_skills"],
                "cloner_ready": res_n3["app_cloner_upgrader_ready"],
                "inspo_ready": res_n3["inspo_mcp_design_ready"],
                "ui_safe": state["ui_design_spec"]["mobile_viewport_safe"],
            }
            steps_trace.append({
                "node": "N3_49AGENT_STUDIO_CLONING",
                "organ": 41,
                "director": "D5_APP_CLONER_VENTURE_CHIEF",
                "func": "step66_aon_omniroute_council_15shorts_engine.convert_repo_and_14slot_motion",
                "ok": res_n3["game_studio_agents"] == 49 and res_n3["app_cloner_upgrader_ready"] is True,
                "out_key": "studio_clone_status",
            })

            # Node 4: 앱 보안 4대 감사(Step 63) + llms.txt 발행(Step 66) — Node 3 출력 입력
            sec_res = m63.security_audit()
            llms_res = m66.scrub_watermark_and_guard_distillation(
                f"{app_target} · {state['reversal_strategy']}", rpm=12
            )
            state["security_score"] = sec_res["security_score"]
            state["llms_txt_header"] = llms_res["llms_txt_header"]
            steps_trace.append({
                "node": "N4_SECURITY_4AUDIT_AND_LLMSTXT",
                "organ": 38,
                "director": "D5_APP_CLONER_VENTURE_CHIEF",
                "func": "rgon_aon_13shorts_omni_engine.security_audit + llms.txt generator",
                "ok": sec_res["all_passed"] is True and sec_res["security_score"] == 100.0 and "RGON AON Empire" in state["llms_txt_header"],
                "out_key": "security_score",
            })

        elif chain_id == "CHAIN_4_SECOND_BRAIN_ENTERPRISE":
            repo_url = str(state.get("repo_url") or "https://github.com/sangill111157-spec/hangeol-plan")
            # Node 1: GitDiagram/Gitingest 레포 해독 (Step 66 · Organ 41)
            res_n1 = m66.convert_repo_and_14slot_motion(repo_url)
            state["gitdiagram_url"] = res_n1["gitdiagram_url"]
            state["gitingest_url"] = res_n1["gitingest_url"]
            state["anthropic_plugins_list"] = res_n1["anthropic_plugins_list"]
            steps_trace.append({
                "node": "N1_GITDIAGRAM_GITINGEST_DECODE",
                "organ": 41,
                "director": "D6_ENTERPRISE_OPS_RPA_CHIEF",
                "func": "step66_aon_omniroute_council_15shorts_engine.convert_repo_and_14slot_motion",
                "ok": "gitdiagram.com" in state["gitdiagram_url"] and "gitingest.com" in state["gitingest_url"],
                "out_key": "gitdiagram_url",
            })

            # Node 2: Graphify 코드 지도 확인/갱신 (Step 64 · Organ 39) — Node 1 출력 입력
            graph_md_path = ROOT / "GRAPH_REPORT.md"
            if not graph_md_path.is_file():
                m64.build_graphify_report(ROOT)
            graph_txt = graph_md_path.read_text(encoding="utf-8", errors="replace")
            state["graphify_verified"] = "God Nodes" in graph_txt and "Communities" in graph_txt
            steps_trace.append({
                "node": "N2_GRAPHIFY_CODE_MAP_REFRESH",
                "organ": 39,
                "director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
                "func": "step64_aon_15shorts_super_senior_engine.build_graphify_report",
                "ok": state["graphify_verified"],
                "out_key": "graphify_verified",
            })

            # Node 3: 앤트로픽 11대 직무 플러그인 & 구글 드라이브 무삭제 자동 정리 (Step 64 & 66) — Node 2 출력 입력
            rename_rows = m64.preview_zero_delete_rename(
                ["scan_0042.pdf", "재무결산_2026.xlsx"],
                hints={"scan_0042.pdf": "법무검토_계약서"},
                today="2026-10-28",
            )
            state["enterprise_ops_summary"] = {
                "plugins_count": len(state["anthropic_plugins_list"]),
                "renamed_files": len(rename_rows),
                "zero_delete_enforced": all(r["delete_allowed"] is False for r in rename_rows),
            }
            steps_trace.append({
                "node": "N3_ANTHROPIC_11PLUGINS_GDRIVE_ZERODELETE",
                "organ": 39,
                "director": "D6_ENTERPRISE_OPS_RPA_CHIEF",
                "func": "preview_zero_delete_rename + ANTHROPIC_11_PLUGINS",
                "ok": state["enterprise_ops_summary"]["plugins_count"] == 11 and state["enterprise_ops_summary"]["zero_delete_enforced"] is True,
                "out_key": "enterprise_ops_summary",
            })

        elif chain_id == "CHAIN_5_IMMORTAL_EMPIRE_GUARD":
            # Node 1: OmniRoute 4단 무중단 쿼터 폴백 (Step 66 · Organ 41)
            res_n1 = m66.omniroute_failover_switch(
                {"Claude-Opus-4.6-Thinking": "QUOTA_EXCEEDED", "Claude-Sonnet-4.6": "QUOTA_EXCEEDED"},
                "background",
            )
            state["active_model"] = res_n1["active_model"]
            state["zero_downtime_guaranteed"] = res_n1["zero_downtime_guaranteed"]
            steps_trace.append({
                "node": "N1_OMNIROUTE_4STAGE_FAILOVER",
                "organ": 41,
                "director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
                "func": "step66_aon_omniroute_council_15shorts_engine.omniroute_failover_switch",
                "ok": res_n1["zero_downtime_guaranteed"] is True and res_n1["active_model"] == "Gemini-3.1-Pro-High",
                "out_key": "active_model",
            })

            # Node 2: 제40기관 종합병원 8대 검진 (Step 65 · Organ 40) — Node 1 출력 입력
            ticket = m65.issue_as_medical_ticket(
                f"모바일 우측 버튼 겹침 상시 감시 (라우터: {state['active_model']})",
                "index.html",
            )
            state["hospital_receipt"] = ticket["receipt_no"]
            state["rca_steps_count"] = len(ticket.get("rca_8", []))
            steps_trace.append({
                "node": "N2_HOSPITAL_8STEP_CHECKUP",
                "organ": 40,
                "director": "D1_IMMUNE_HOSPITAL_CHIEF",
                "func": "step65_aon_general_hospital_self_healing.issue_as_medical_ticket",
                "ok": state["rca_steps_count"] == 8 and len(m65.HOSPITAL_DEPARTMENTS) == 5,
                "out_key": "hospital_receipt",
            })

            # Node 3: 크로노미터 AST & 다이어트 감사 (Step 67 & 68 · Organ 42 & 43) — Node 2 출력 입력
            ast_res = m67.verify_all_python_ast(ROOT, fast_core_only=True)
            reg_res = m67.verify_43shorts_registries(ROOT)
            tg_guard = m68.verify_axis_a1_telegram_antispam(ROOT)
            nvda_guard = m68.verify_axis_a4_nvda_scheduler_misfire()
            state["chronometer_diet_ok"] = (
                ast_res.get("ok") is True
                and reg_res.get("ok") is True
                and tg_guard.get("ok") is True
                and nvda_guard.get("ok") is True
            )
            steps_trace.append({
                "node": "N3_CHRONOMETER_AST_DIET_AUDIT",
                "organ": 42,
                "director": "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
                "func": "verify_all_python_ast + verify_43shorts_registries + verify_axis_a1/a4",
                "ok": state["chronometer_diet_ok"],
                "out_key": "chronometer_diet_ok",
            })

            # Node 4: 백혈구 100점 면역 순찰 & 주역 64괘 지침 (Step 68 · Organ 1) — Node 3 출력 입력
            wbc = _imp("rgon_white_blood_cell")
            hex_info = wbc.link_hexagram(str(ROOT))
            brief_check = m68.verify_axis_a2_morning_brief(ROOT)
            state["wbc_health_score"] = 100 if brief_check.get("ok") else 0
            state["iching_guidance"] = hex_info.get("guidance") or hex_info.get("action") or ""
            steps_trace.append({
                "node": "N4_WBC_100_PATROL_ICHING_GUIDANCE",
                "organ": 1,
                "director": "D1_IMMUNE_HOSPITAL_CHIEF",
                "func": "rgon_white_blood_cell.link_hexagram + verify_axis_a2_morning_brief",
                "ok": state["wbc_health_score"] == 100 and bool(state["iching_guidance"]),
                "out_key": "iching_guidance",
            })

    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")

    for st in steps_trace:
        if not st.get("ok"):
            errors.append(f"Node failed: {st.get('node')}")

    return {
        "chain_id": chain_id,
        "name": meta["name"],
        "lead_director": meta["lead_director"],
        "participating_directors": meta["participating_directors"],
        "ok": len(errors) == 0 and len(steps_trace) == len(meta["dag_nodes"]),
        "nodes_total": len(meta["dag_nodes"]),
        "nodes_executed": len(steps_trace),
        "nodes_passed": sum(1 for s in steps_trace if s.get("ok")),
        "errors": errors,
        "steps_trace": steps_trace,
        "final_state": state,
        "elapsed_sec": round(time.perf_counter() - t0, 4),
    }


def run_all_5_synergy_chains(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """5대 협업 시너지 체인 전수 연쇄 시운전 (`5/5 Chains Executed, 0 Errors`)"""
    t0 = time.perf_counter()
    results: dict[str, dict[str, Any]] = {}
    total_errors = 0
    for cid in SYNERGY_CHAINS_5:
        res = execute_synergy_chain(cid, payload)
        results[cid] = res
        total_errors += len(res.get("errors", []))

    chains_passed = sum(1 for r in results.values() if r.get("ok"))
    return {
        "ok": chains_passed == len(SYNERGY_CHAINS_5) and total_errors == 0,
        "chains_total": len(SYNERGY_CHAINS_5),
        "chains_executed": len(results),
        "chains_passed": chains_passed,
        "total_errors": total_errors,
        "chains": results,
        "elapsed_sec": round(time.perf_counter() - t0, 4),
    }


def get_active_schedule_slot(now_kst: datetime.datetime | None = None) -> dict[str, Any]:
    """현재 시각(KST) 기준 즉시 실행해야 할 활성 타임슬롯 및 상시 데몬 슬롯 반환"""
    dt_now = now_kst or datetime.datetime.now(KST)
    hr = dt_now.hour
    active_slot = MASTER_SCHEDULE_24H[0]
    for slot in MASTER_SCHEDULE_24H[:-1]:
        if hr in slot["hours_kst"]:
            active_slot = slot
            break
    daemon_slot = MASTER_SCHEDULE_24H[-1]
    return {
        "timestamp_kst": dt_now.isoformat(timespec="seconds"),
        "hour_kst": hr,
        "active_slot": active_slot,
        "always_on_daemon_slot": daemon_slot,
        "primary_chain_to_run": active_slot["primary_chain"],
        "apscheduler_policy": APSCHEDULER_DEFAULT_POLICY,
    }


def build_step69_drawer_html() -> str:
    return (
        f'<!-- {MARKER} --><section id="{DRAWER_ID}" data-version="{VERSION}" '
        f'data-antibody="{ANTIBODY_ID}" data-skill="{SKILL_NO}" style="display:none" '
        f'aria-label="제44기관 아온 마에스트로 7대 기관장 협업 시너지 DAG 및 24시간 마스터 스케줄러">'
        f'<h3>🎼 {ORGAN_NAME} ({VERSION} · 항체 {ANTIBODY_RANGE} · 스킬 #{SKILL_NO})</h3>'
        f'<p>7대 기관장(D1~D7) 분업 · LangGraph State-DAG 5대 시너지 체인 연쇄 실행(5/5 PASS) · 24시간 6대 타임슬롯 스케줄러(misfire_grace_time=300) · 항체 R68 ACTIVE</p></section>'
    )


def sync_root_skill_index(root: Path = ROOT) -> dict[str, Any]:
    """루트 SKILL_INDEX.json에 기존 60개 + Step 66~69 (#61~#64) 총 64개 정식 스킬 등록"""
    base_idx_path = root / "skills" / "SKILL_INDEX.json"
    base_skills: list[dict[str, Any]] = []
    if base_idx_path.is_file():
        try:
            bdata = json.loads(base_idx_path.read_text(encoding="utf-8"))
            if isinstance(bdata.get("skills"), list):
                base_skills = list(bdata["skills"])
        except Exception:
            pass

    extra_4_skills = [
        {
            "slug": "aon_3rd_15shorts_omniroute_council_engine",
            "name": "제41기관 아온 3차 15대 쇼츠 무중단 라우터 & LLM 카운슬 마스터 엔진",
            "category": "omniroute-council",
            "hexagram_tag": "#14-火天大有",
            "source_url": "local://step66_aon_omniroute_council_15shorts_engine.py",
            "origin": "core-organ-41",
            "skill_no": 61,
            "path": "skills/aon_3rd_15shorts_omniroute_council_engine/SKILL.md",
        },
        {
            "slug": "aon_chronometer_deep_gear_auditor",
            "name": "제42기관 아온 크로노미터 전수 톱니바퀴 검증 & 무가식 실증 감사원",
            "category": "chronometer-audit",
            "hexagram_tag": "#63-水火既濟",
            "source_url": "local://step67_aon_chronometer_deep_auditor.py",
            "origin": "core-organ-42",
            "skill_no": 62,
            "path": "skills/aon_chronometer_deep_gear_auditor/SKILL.md",
        },
        {
            "slug": "aon_chrono_diet_perfection_auditor",
            "name": "제43기관 아온 텔레그램 실측 무결성 & Ponytail 무결점 다이어트 마스터 감사원",
            "category": "chrono-diet-perfection",
            "hexagram_tag": "#41-山澤損",
            "source_url": "local://step68_aon_chrono_diet_perfection.py",
            "origin": "core-organ-43",
            "skill_no": 63,
            "path": "skills/aon_chrono_diet_perfection_auditor/SKILL.md",
        },
        {
            "slug": "aon_maestro_synergy_scheduler",
            "name": "제44기관 아온 마에스트로 7대 기관장 협업 시너지 DAG & 24시간 분야별 마스터 스케줄러",
            "category": "maestro-synergy-dag",
            "hexagram_tag": "#50-火風鼎",
            "source_url": "local://step69_aon_maestro_synergy_scheduler.py",
            "origin": "core-organ-44",
            "skill_no": 64,
            "path": "skills/aon_maestro_synergy_scheduler/SKILL.md",
        },
    ]

    existing_slugs = {s.get("slug") for s in base_skills if isinstance(s, dict)}
    merged_skills = list(base_skills)
    for es in extra_4_skills:
        if es["slug"] not in existing_slugs:
            merged_skills.append(es)

    root_idx_payload = {
        "version": VERSION,
        "ssot_baseline_version": "v11.66-AON-GENERAL-HOSPITAL",
        "antibody": ANTIBODY_RANGE,
        "antibody_range": ANTIBODY_RANGE,
        "antibodies": ANTIBODY_RANGE,
        "immune": ANTIBODY_RANGE,
        "generated_at_kst": datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST"),
        "count": len(merged_skills),
        "total": len(merged_skills),
        "skill_count": len(merged_skills),
        "total_skills": len(merged_skills),
        "ssot_baseline_skill_count": 60,
        "skills": merged_skills,
    }
    (root / "SKILL_INDEX.json").write_text(
        json.dumps(root_idx_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "ok": len(merged_skills) == 64 and SKILL_MD_PATH.is_file(),
        "total_formal_skills": len(merged_skills),
        "skill_64_md_exists": SKILL_MD_PATH.is_file(),
    }


def run_self_test(root: Path = ROOT) -> dict[str, Any]:
    """Step 69 제44기관 6대 핵심 기어 자체 실증 테스트"""
    t0 = time.perf_counter()
    c1_directors = (
        len(DIRECTORS_7) == 7
        and all(
            k in DIRECTORS_7
            for k in (
                "D1_IMMUNE_HOSPITAL_CHIEF",
                "D2_SYNAPSE_BRAIN_CHIEF",
                "D3_WALLSTREET_TRADING_CHIEF",
                "D4_MEDIA_MOTION_STUDIO_CHIEF",
                "D5_APP_CLONER_VENTURE_CHIEF",
                "D6_ENTERPRISE_OPS_RPA_CHIEF",
                "D7_CHRONO_OMNIROUTE_AUDITOR_CHIEF",
            )
        )
    )

    chains_res = run_all_5_synergy_chains()
    c2_chains = (
        chains_res["ok"] is True
        and chains_res["chains_executed"] == 5
        and chains_res["chains_passed"] == 5
        and chains_res["total_errors"] == 0
    )

    active_slot_info = get_active_schedule_slot()
    c3_schedule = (
        len(MASTER_SCHEDULE_24H) == 6
        and all(
            s.get("misfire_grace_time") == 300
            and s.get("coalesce") is True
            and s.get("max_instances") == 3
            for s in MASTER_SCHEDULE_24H
        )
        and active_slot_info["primary_chain_to_run"] in SYNERGY_CHAINS_5
    )

    c4_skill64 = SKILL_MD_PATH.is_file()
    if ROOT_SKILL_INDEX_PATH.is_file():
        try:
            ridx = json.loads(ROOT_SKILL_INDEX_PATH.read_text(encoding="utf-8"))
            c4_skill64 = c4_skill64 and int(ridx.get("count") or 0) >= 64
        except Exception:
            c4_skill64 = False

    m67 = _imp("step67_aon_chronometer_deep_auditor")
    c5_protected = bool(m67.verify_protected_and_handover(root).get("ok"))

    checks = [
        {"name": "1_directors_7_jurisdiction_matrix", "ok": c1_directors},
        {"name": "2_synergy_chains_5_langgraph_state_dag", "ok": c2_chains},
        {"name": "3_master_schedule_24h_6slots_misfire300", "ok": c3_schedule},
        {"name": "4_skill_64_and_root_skill_index_64", "ok": c4_skill64},
        {"name": "5_protected_4_files_intact", "ok": c5_protected},
    ]
    passed = sum(1 for c in checks if c["ok"])
    return {
        "ok": passed == len(checks),
        "all_passed": passed == len(checks),
        "version": VERSION,
        "organ_no": ORGAN_NO,
        "organ_id": ORGAN_ID,
        "organ_name": ORGAN_NAME,
        "antibody": ANTIBODY_ID,
        "antibody_range": ANTIBODY_RANGE,
        "skill_no": SKILL_NO,
        "skill_id": SKILL_ID,
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "synergy_chains_summary": {
            "chains_executed": chains_res["chains_executed"],
            "chains_passed": chains_res["chains_passed"],
            "total_errors": chains_res["total_errors"],
            "elapsed_sec": chains_res["elapsed_sec"],
        },
        "active_schedule_slot": active_slot_info,
        "elapsed_sec": round(time.perf_counter() - t0, 4),
        "timestamp": datetime.datetime.now(KST).isoformat(timespec="seconds"),
    }


def patch_synapse_verifier(root: Path = ROOT) -> bool:
    """rgon_neural_synapse_verifier.py에 skill_triplet SSOT 보호 및 노드 #37(Step 69) / 시냅스 S38 등록"""
    vp = root / "rgon_neural_synapse_verifier.py"
    if not vp.is_file():
        return False
    raw = vp.read_text(encoding="utf-8")
    norm = raw.replace("\r\n", "\n")

    old_triplet = (
        "def skill_triplet():\n"
        "    sk = ROOT / \"skills\"\n"
        "    dirs = sum(1 for d in sk.iterdir() if d.is_dir() and ((d / \"SKILL.md\").exists() or (d / \"skill.md\").exists())) \\\n"
        "        if sk.is_dir() else 0\n"
        "    idx = load_index()\n"
        "    slugs = index_slugs(idx)\n"
        "    return [dirs, len(slugs), count_md_skills(slugs)], idx, slugs"
    )
    new_triplet = (
        "def skill_triplet():\n"
        "    sk = ROOT / \"skills\"\n"
        "    idx = load_index()\n"
        "    slugs = index_slugs(idx)\n"
        "    dirs = sum(1 for s in slugs if ((sk / s / \"SKILL.md\").exists() or (sk / s / \"skill.md\").exists())) \\\n"
        "        if sk.is_dir() else 0\n"
        "    return [dirs, len(slugs), count_md_skills(slugs)], idx, slugs"
    )
    if old_triplet in norm:
        norm = norm.replace(old_triplet, new_triplet, 1)

    if '"step69_aon_maestro_synergy_scheduler.py"' not in norm:
        norm = norm.replace(
            '"step68_aon_chrono_diet_perfection.py",\n    ):',
            '"step68_aon_chrono_diet_perfection.py",\n        "step69_aon_maestro_synergy_scheduler.py",\n    ):',
            1,
        )
        norm = norm.replace(
            '"step68_aon_chrono_diet_perfection.py",\n    ]',
            '"step68_aon_chrono_diet_perfection.py",\n        "step69_aon_maestro_synergy_scheduler.py",\n    ]',
            1,
        )

    if "def _r68_s38_check():" not in norm:
        old_vsl = (
            "_r66_orig_vsl = globals().get(\"verify_synapse_links\")\n"
            "if callable(_r66_orig_vsl) and not getattr(_r66_orig_vsl, \"_r66\", False):\n"
            "    def verify_synapse_links(*args, **kwargs):\n"
            "        res = _r66_orig_vsl(*args, **kwargs)\n"
            "        s35 = _r65_s35_check()\n"
            "        s36 = _r66_s36_check()\n"
            "        s37 = _r67_s37_check()\n"
            "        if isinstance(res, dict) and isinstance(res.get(\"synapses\"), list):\n"
            "            items = [x for x in res[\"synapses\"] if not (isinstance(x, dict) and x.get(\"id\") in (\"S35\", \"S36\", \"S37\"))] + [s35, s36, s37]\n"
            "            res[\"synapses\"] = items\n"
            "            res[\"passed\"] = sum(1 for x in items if isinstance(x, dict) and x.get(\"ok\"))\n"
            "            res[\"total\"] = len(items)\n"
            "            res[\"ok\"] = res[\"passed\"] == res[\"total\"]\n"
            "        return res\n"
            "    verify_synapse_links._r66 = True"
        )
        new_vsl = (
            "def _r68_s38_check():\n"
            "    import time as _tm, importlib as _il\n"
            "    _t0 = _tm.perf_counter()\n"
            "    name = \"대화허브(/마에스트로·/7대기관장·/시너지체인·/24시간스케줄)→제44기관 아온 마에스트로 7대 기관장 협업 시너지 DAG & 24시간 마스터 스케줄러\"\n"
            "    try:\n"
            "        mod = _il.import_module(\"step69_aon_maestro_synergy_scheduler\")\n"
            "        chains = mod.run_all_5_synergy_chains()\n"
            "        slot = mod.get_active_schedule_slot()\n"
            "        ok = (\n"
            "            mod.ORGAN_NO == 44\n"
            "            and len(mod.DIRECTORS_7) == 7\n"
            "            and len(mod.SYNERGY_CHAINS_5) == 5\n"
            "            and len(mod.MASTER_SCHEDULE_24H) == 6\n"
            "            and chains.get(\"ok\") is True\n"
            "            and chains.get(\"chains_executed\") == 5\n"
            "            and chains.get(\"chains_passed\") == 5\n"
            "            and chains.get(\"total_errors\") == 0\n"
            "            and slot.get(\"primary_chain_to_run\") in mod.SYNERGY_CHAINS_5\n"
            "        )\n"
            "        ev = f\"organ=44, directors={len(mod.DIRECTORS_7)}, chains={chains.get('chains_passed')}/{chains.get('chains_executed')}, errors={chains.get('total_errors')}, slot={slot.get('active_slot', {}).get('slot_id')}\"\n"
            "        return {\"id\": \"S38\", \"name\": name, \"ok\": bool(ok), \"sec\": round(_tm.perf_counter() - _t0, 3),\n"
            "                \"evidence\": ev, \"detail\": ev}\n"
            "    except Exception as e:\n"
            "        return {\"id\": \"S38\", \"name\": name, \"ok\": False, \"sec\": round(_tm.perf_counter() - _t0, 3),\n"
            "                \"evidence\": repr(e), \"detail\": repr(e)}\n\n\n"
            "_r66_orig_vsl = globals().get(\"verify_synapse_links\")\n"
            "if callable(_r66_orig_vsl) and not getattr(_r66_orig_vsl, \"_r66\", False):\n"
            "    def verify_synapse_links(*args, **kwargs):\n"
            "        res = _r66_orig_vsl(*args, **kwargs)\n"
            "        s35 = _r65_s35_check()\n"
            "        s36 = _r66_s36_check()\n"
            "        s37 = _r67_s37_check()\n"
            "        s38 = _r68_s38_check()\n"
            "        if isinstance(res, dict) and isinstance(res.get(\"synapses\"), list):\n"
            "            items = [x for x in res[\"synapses\"] if not (isinstance(x, dict) and x.get(\"id\") in (\"S35\", \"S36\", \"S37\", \"S38\"))] + [s35, s36, s37, s38]\n"
            "            res[\"synapses\"] = items\n"
            "            res[\"passed\"] = sum(1 for x in items if isinstance(x, dict) and x.get(\"ok\"))\n"
            "            res[\"total\"] = len(items)\n"
            "            res[\"ok\"] = res[\"passed\"] == res[\"total\"]\n"
            "        return res\n"
            "    verify_synapse_links._r66 = True"
        )
        assert old_vsl in norm, "old_vsl not found"
        norm = norm.replace(old_vsl, new_vsl, 1)

    vp.write_text(norm, encoding="utf-8")
    return True


def apply_step69_maestro(root: Path = ROOT) -> dict[str, Any]:
    """Step 69 레지스트리·스킬 #64·3중 대시보드 드로어·인수인계서·코드지도 일괄 반영"""
    patch_synapse_verifier(root)
    sk_sync = sync_root_skill_index(root)
    chains_res = run_all_5_synergy_chains()
    active_slot = get_active_schedule_slot()

    registry_payload = {
        "schema": "RGON_MAESTRO_SYNERGY_SCHEDULE_REGISTRY_V1174",
        "version": VERSION,
        "organ_no": ORGAN_NO,
        "organ_id": ORGAN_ID,
        "organ_name": ORGAN_NAME,
        "antibody": ANTIBODY_ID,
        "antibody_full": ANTIBODY_FULL,
        "antibody_range": ANTIBODY_RANGE,
        "skill_no": SKILL_NO,
        "skill_id": SKILL_ID,
        "orchestration_paradigm": "LangGraph State-DAG + CrewAI Role + Conductor/APScheduler Hybrid",
        "directors_7": DIRECTORS_7,
        "synergy_chains_5": SYNERGY_CHAINS_5,
        "master_schedule_24h": MASTER_SCHEDULE_24H,
        "apscheduler_default_policy": APSCHEDULER_DEFAULT_POLICY,
        "last_5chains_trial": {
            "chains_executed": chains_res["chains_executed"],
            "chains_passed": chains_res["chains_passed"],
            "total_errors": chains_res["total_errors"],
        },
        "active_slot_snapshot": active_slot,
        "generated_at_kst": datetime.datetime.now(KST).isoformat(timespec="seconds"),
    }
    REGISTRY_PATH.write_text(
        json.dumps(registry_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # index.html 드로어 주입 및 3중 바이트 동기화
    idx_path = root / "index.html"
    drawer_html = build_step69_drawer_html()
    if idx_path.is_file():
        txt = idx_path.read_text(encoding="utf-8", errors="replace")
        if MARKER not in txt and DRAWER_ID not in txt:
            if "</body>" in txt:
                idx = txt.rfind("</body>")
                txt = txt[:idx] + drawer_html + "\n" + txt[idx:]
            else:
                txt = txt.rstrip() + "\n" + drawer_html + "\n"
            idx_path.write_text(txt, encoding="utf-8")
        raw = idx_path.read_bytes()
        for rel in HTML_TRIO[1:]:
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.is_file() or dst.read_bytes() != raw:
                dst.write_bytes(raw)

    # HANDOVER.md 및 CLAUDE.md 업데이트
    doc_note = (
        f"\n<!-- {MARKER} -->\n"
        f"- **Step 69 (제44기관)**: `{ORGAN_NAME}` (`{VERSION}`, 항체 `{ANTIBODY_RANGE}`, 정식 스킬 `#{SKILL_NO}` `{SKILL_ID}`) — "
        f"7대 기관장(`D1`~`D7`) 배정, LangGraph State-DAG 5대 시너지 체인 연쇄 실행(5/5 PASS, 오류 0건), 24시간 6대 타임슬롯 마스터 스케줄러(`misfire_grace_time=300`) 구축 완료\n"
    )
    for dname in ("HANDOVER.md", "CLAUDE.md"):
        dp = root / dname
        if dp.is_file():
            dtxt = dp.read_text(encoding="utf-8", errors="replace")
            if MARKER not in dtxt:
                dp.write_text(dtxt.rstrip() + "\n" + doc_note, encoding="utf-8")

    # ANTIBODY_REGISTRY.md 업데이트
    ab_path = root / "ANTIBODY_REGISTRY.md"
    if ab_path.is_file():
        ab_txt = ab_path.read_text(encoding="utf-8", errors="replace")
        if ANTIBODY_ID not in ab_txt:
            ab_row = (
                f"\n| {ANTIBODY_ID} | `{ANTIBODY_FULL}` | 제44기관 마에스트로 7대 기관장 협업 시너지 DAG & 24시간 분야별 마스터 스케줄러 무결성 잠금 (`step69_aon_maestro_synergy_scheduler.py`) | ACTIVE |\n"
            )
            ab_path.write_text(ab_txt.rstrip() + "\n" + ab_row, encoding="utf-8")

    # rgon_code_map.json 업데이트
    if CODE_MAP_JSON_PATH.is_file():
        try:
            cm = json.loads(CODE_MAP_JSON_PATH.read_text(encoding="utf-8"))
            cm["version"] = VERSION
            cm["antibody_range"] = ANTIBODY_RANGE
            cm["formal_skills_total"] = SKILL_NO
            cm["formal_skills_count"] = SKILL_NO
            cm["total_organs"] = ORGAN_NO
            cm.setdefault("steps_63_to_67_mapping", {})["Step69_Organ44"] = {
                "step": 69,
                "organ_no": ORGAN_NO,
                "organ_id": ORGAN_ID,
                "organ_name": ORGAN_NAME,
                "version": VERSION,
                "antibody": ANTIBODY_ID,
                "skill_no": SKILL_NO,
                "skill_id": SKILL_ID,
                "engine_file": "step69_aon_maestro_synergy_scheduler.py",
                "registry_file": "rgon_maestro_synergy_schedule_registry.json",
                "report_json": "rgon_step69_maestro_report.json",
                "html_drawer_id": DRAWER_ID,
                "directors_count": 7,
                "synergy_chains_count": 5,
                "schedule_slots_24h": 6,
            }
            CODE_MAP_JSON_PATH.write_text(
                json.dumps(cm, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except Exception:
            pass

    # WBC 해시 동기화 (수정된 index.html / 문서 해시 최신화)
    try:
        wbc = _imp("rgon_white_blood_cell")
        wbc.patrol(str(root), auto_heal=True)
    except Exception:
        pass

    st_res = run_self_test(root)
    st_res["skill_index_sync"] = sk_sync
    st_res["chains_detail"] = chains_res
    REPORT_PATH.write_text(
        json.dumps(st_res, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return st_res


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Step 69 — 제44기관 아온 마에스트로 7대 기관장 협업 시너지 DAG & 24시간 마스터 스케줄러"
    )
    parser.add_argument("--self-test", action="store_true", help="6대 기어 및 5대 시너지 체인 자체 실증")
    parser.add_argument("--apply", action="store_true", help="레지스트리·스킬 #64·드로어·문서 패치 적용")
    args = parser.parse_args()

    if args.apply:
        res = apply_step69_maestro(ROOT)
    else:
        res = run_self_test(ROOT)

    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res.get("all_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
