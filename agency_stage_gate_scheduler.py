# -*- coding: utf-8 -*-
"""
agency_stage_gate_scheduler.py
[v12.3-AGENCY-STAGE-GATE-SCHEDULER]
================================================================================
👑 COMMANDER-000 이상일 대표님 & RGON-001 제1수석보좌관 르곤 직속
- 6대 현존 확실한 기관 24시간 일일 기본 루틴 및 STEP 1 ➔ 4 하드-게이트 통제 엔진
- 현재 단계 목표(KPI) 100% 달성 시에만 다음 단계(🔒 LOCKED) 해금
- 폐기된 옛 명칭('꿈의 옷장') 100% 완전 소각 / 확정 명칭만 사용
  • 제1청사: 미국주식 퀀트 & 리스크 본부 (알파-퀀트)
  • 제2청사: 커넥트 AI 바이럴 & 트래픽 본부 (알파-바이럴)
  • 제3청사: 미디어 홀 — 유튜브 3채널 & Suno 432Hz 본부 (알파-미디어)
  • 제4청사: 홍익 교육원 — 5대 클린룸 안전 웹앱 본부 (알파-홍익)
  • 제5청사: 비밀 금고 — 31개 보안키 & 구글 시트 85탭 본부 (알파-가디언)
  • 제6청사: 국고 관리소 — 실전 금고 0원 & 복식부기 본부 (알파-트레저리)
================================================================================
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
MASTER_FILE = BASE_DIR / "agency_stage_gate_master.json"
TREASURY_FILE = BASE_DIR / "treasury_ledger.json"

def load_stage_gate_master() -> Dict[str, Any]:
    if not MASTER_FILE.exists():
        return {"error": "agency_stage_gate_master.json file not found", "agencies": {}}
    try:
        return json.loads(MASTER_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e), "agencies": {}}

def save_stage_gate_master(data: Dict[str, Any]) -> bool:
    try:
        MASTER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False

def get_stage_gate_schedule() -> Dict[str, Any]:
    """6대 기관 24시간 기본 스케줄 및 STEP 1~4 잠금/해금 현황 반환"""
    data = load_stage_gate_master()
    agencies = data.get("agencies", {})
    
    # 금고 0원 점검
    is_treasury_0krw = True
    if TREASURY_FILE.exists():
        try:
            t = json.loads(TREASURY_FILE.read_text(encoding="utf-8"))
            if t.get("balance_krw", 0) != 0 or t.get("total_spent_krw", 0) != 0:
                is_treasury_0krw = False
        except Exception:
            pass

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary_list = []
    for k, ag in agencies.items():
        # stage_gates 및 별칭 필드 자동 보강 (호환성 100%)
        if "steps" in ag and "stage_gates" not in ag:
            ag["stage_gates"] = {
                f"step_{s_num}": s_val for s_num, s_val in ag["steps"].items()
            }
        if "agency_code" not in ag:
            ag["agency_code"] = ag.get("agency_id", k)
        if "name" not in ag:
            ag["name"] = ag.get("agency_name", k)

        curr_step = ag.get("current_step", 1)
        step_data = ag.get("steps", {}).get(str(curr_step), {})
        summary_list.append({
            "agency_id": ag.get("agency_id"),
            "agency_name": ag.get("agency_name"),
            "current_step": curr_step,
            "step_title": step_data.get("title", ""),
            "progress_pct": step_data.get("progress_pct", 0.0),
            "kpi_targets": step_data.get("kpi_targets", ""),
            "routine_count": len(ag.get("daily_routine", []))
        })

    return {
        "status": "OK",
        "success": True,
        "engine_version": "v12.3-STAGE-GATE-SCHEDULER",
        "timestamp": now_str,
        "agencies_count": len(agencies),
        "agencies": agencies,
        "summary": summary_list,
        "treasury_0krw_verified": is_treasury_0krw,
        "policy": "LOCKED_UNTIL_PREVIOUS_STEP_100_PERCENT"
    }

def evaluate_stage_gate_status(agency_id: Optional[str] = None) -> Dict[str, Any]:
    """일일 기본 스케줄 수행 체크 및 승급 조건 충족 여부 실시간 판정"""
    data = load_stage_gate_master()
    agencies = data.get("agencies", {})
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    eval_results = []
    for k, ag in agencies.items():
        if agency_id and ag.get("agency_id") != agency_id and k != agency_id:
            continue
            
        curr_step = ag.get("current_step", 1)
        step_dict = ag.get("steps", {}).get(str(curr_step), {})
        prog = step_dict.get("progress_pct", 0.0)
        can_advance = (prog >= 100.0 and curr_step < 4)

        eval_results.append({
            "agency_id": ag.get("agency_id"),
            "agency_name": ag.get("agency_name"),
            "current_step": curr_step,
            "current_step_title": step_dict.get("title", ""),
            "progress_pct": prog,
            "can_advance_to_next_step": can_advance,
            "next_step_locked": True if curr_step < 4 and not can_advance else False,
            "next_unlock_condition": ag.get("steps", {}).get(str(curr_step + 1), {}).get("unlock_condition", "최종 단계 달성")
        })

    return {
        "status": "OK",
        "success": True,
        "timestamp": now_str,
        "evaluations": eval_results,
        "receipt_id": f"#STAGE-GATE-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

if __name__ == "__main__":
    print("=" * 70)
    print("🎯 [v12.3] 6대 기관 단계별 목표 해금 스케줄러 로컬 테스트")
    st = get_stage_gate_schedule()
    print("• 기관 수:", st["agencies_count"])
    for s in st["summary"]:
        print(f"• [{s['agency_name']}] STEP {s['current_step']} ({s['progress_pct']}%) - {s['step_title']}")
    print("=" * 70)
