#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
night_seal_v607.py
사령관님 취침 전 최종 봉인 스크립트:
1) evolution_memory.json & brain_basket/master_schedule.json 에 R7 항체 및 내일 아침 1순위 스케줄 등록
2) RGON_EVOLUTION_LOG.md 동기화
3) Google Sheets 2곳 ('RGON_진화일지' 탭)에 오늘 밤 최종 요약 2행 append
4) Git commit & push
"""

from __future__ import annotations

import json
import os
import pickle
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

SHEET_1_SHIN = "1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY"  # SHIN FAMILY COMMAND CENTER
SHEET_3_BLOG = "1gYDrCuqM2hKQbYyE3cYEZhJZEhrH_Is6tdUhsw-cgaw"  # BLOG AUTOMATION COMMAND CENTER
TAB_NAME = "RGON_진화일지"

R7_ANTIBODY = {
    "id": "R7_TARGET_ROW_BADGE_ONLY_SCAN",
    "name": "발사 대상 행 영구 보존 및 배지 전용 스캔",
    "rule": "3.5초 주기 스캔(refreshScan) 시 체크박스 DOM(innerHTML)을 재생성하면 체크 상태가 초기화되므로, 행(Row)은 최초 1회만 빌드하고 주기적 스캔은 오직 연결 배지(textContent)만 갱신한다 (v6.0.7 완치)",
    "version": "6.0.7",
    "registered_at": NOW
}

NEXT_MORNING_TOP1 = {
    "priority": 1,
    "task_id": "GEN1_AUTONOMOUS_EVOLUTION_CLOSED_LOOP",
    "title": "GEN-1 완전 무인 자가 진화 폐쇄 루프 개통",
    "description": "사령관 한 줄 지시 -> 멀티 AI 발사 -> 완료 감지 -> 자동 수거 -> 문법/실행 자동 검증 -> 실패 시 자동 재발사 -> 승리 코드 자동 적용",
    "target_date": "2026-10-21 (내일 아침)",
    "status": "SCHEDULED_TOP1",
    "engine": "rgon_auto_evolve_brain.py + omni_bridge.py /reflect",
    "registered_at": NOW
}

NIGHT_SUMMARY_ROWS = [
    {
        "일시": NOW,
        "구분": "잘한 점 (Well Done)",
        "핵심항목": "Omni-Link v6.0.7 발사 대상 행 영구 보존 & 배지 전용 스캔 완치",
        "상세내용": "Claude 마스터 패치 적용: 3.5초 주기 스캔 시 DOM 덮어쓰기 원천 차단 + 3중 체크 저장소(메모리/localStorage/chrome.storage) 연동 + R7 항체 수립",
        "적용_및_조치": "rgon_aside_extension v6.0.7 반영, node --check 통과, Git 봉인",
        "상태": "완료"
    },
    {
        "일시": NOW,
        "구분": "내일 진화 과제 (Next Step)",
        "핵심항목": "GEN-1 완전 무인 자가 진화 폐쇄 루프 개통",
        "상세내용": "사령관 한 줄 지시 -> 멀티 AI 발사 -> 완료 감지 -> 자동 수거 -> 문법/실행 자동 검증 -> 실패 시 교정 재발사 -> 승리 코드 자동 로컬 디스크 적용 파이프라인 완성",
        "적용_및_조치": "자가 진화 두뇌(rgon_auto_evolve_brain.py) 연동 고도화",
        "상태": "예정"
    }
]

def update_master_schedule():
    sched_path = ROOT / "brain_basket" / "master_schedule.json"
    sched_path.parent.mkdir(exist_ok=True)
    data = {}
    if sched_path.exists():
        try:
            with open(sched_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["R7_ANTIBODY"] = R7_ANTIBODY
    data["NEXT_MORNING_TOP1"] = NEXT_MORNING_TOP1
    
    # schedules 리스트 갱신
    schedules = data.get("schedules", [])
    # 기존 NEXT_MORNING_TOP1 과 유사한 항목 있으면 교체, 없으면 맨 앞에 삽입
    schedules = [s for s in schedules if s.get("task_id") != "GEN1_AUTONOMOUS_EVOLUTION_CLOSED_LOOP"]
    schedules.insert(0, NEXT_MORNING_TOP1)
    data["schedules"] = schedules

    with open(sched_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ brain_basket/master_schedule.json 업데이트 완료 (R7 항체 및 내일 아침 1순위 스케줄 등재)")

def update_evolution_json():
    json_path = ROOT / "evolution_memory.json"
    data = []
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    if not isinstance(data, list):
        data = [data]

    # R7 항체와 내일 1순위 과제 메타데이터 삽입
    data.append({
        "type": "ANTIBODY_REGISTRATION",
        "antibody": R7_ANTIBODY,
        "ts": NOW
    })
    data.extend(NIGHT_SUMMARY_ROWS)

    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ evolution_memory.json 업데이트 완료 (총 {len(data)}개 항목)")

def update_evolution_md():
    md_path = ROOT / "RGON_EVOLUTION_LOG.md"
    new_md_lines = []
    for r in NIGHT_SUMMARY_ROWS:
        line = f"| {r['일시']} | **{r['구분']}** | {r['핵심항목']} | {r['상세내용']} | {r['적용_및_조치']} | {r['상태']} |\n"
        new_md_lines.append(line)

    if md_path.exists():
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.rstrip() + "\n" + "".join(new_md_lines)
    else:
        header = "# 🏛️ RGON 진화일지 (Evolution Log)\n\n| 일시 | 구분 | 핵심항목 | 상세내용 | 적용 및 조치 | 상태 |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        content = header + "".join(new_md_lines)

    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("✅ RGON_EVOLUTION_LOG.md 업데이트 완료")

def find_token() -> str:
    candidates = [
        r"C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation\config\token.pickle",
        r"C:\Users\sangi\Desktop\hangeoreumsshik\automation\config\token.pickle",
        str(ROOT / "config" / "token.pickle"),
        str(ROOT / "token.pickle")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Google OAuth token.pickle을 찾지 못했습니다.")

def get_sheets_service():
    token_path = find_token()
    with open(token_path, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
    return build("sheets", "v4", credentials=creds)

def sync_sheets():
    service = get_sheets_service()
    rows_values = [
        [r["일시"], r["구분"], r["핵심항목"], r["상세내용"], r["적용_및_조치"], r["상태"]]
        for r in NIGHT_SUMMARY_ROWS
    ]
    results = {}
    for sid, name in [(SHEET_1_SHIN, "SHIN FAMILY COMMAND CENTER"), (SHEET_3_BLOG, "BLOG AUTOMATION COMMAND CENTER")]:
        body = { "values": rows_values }
        res = service.spreadsheets().values().append(
            spreadsheetId=sid,
            range=f"'{TAB_NAME}'!A:F",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        updated_range = res.get("updates", {}).get("updatedRange", "N/A")
        results[name] = updated_range
        print(f"✅ {name} '{TAB_NAME}' 2행 추가 완료: {updated_range}")
    return results

def git_commit_and_push():
    files_to_add = [
        "evolution_memory.json",
        "brain_basket/master_schedule.json",
        "RGON_EVOLUTION_LOG.md",
        "night_seal_v607.py"
    ]
    for f in files_to_add:
        if (ROOT / f).exists():
            subprocess.run(["git", "add", "-f", f], cwd=str(ROOT), check=True)

    commit_msg = "chore(night-seal-v6.0.7): record R7 antibody & GEN-1 autonomous evolution roadmap to sheets and github"
    res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    if res.returncode == 0:
        print("✅ git commit 완료:", commit_msg)
    else:
        print("ℹ️ git commit:", res.stdout.strip() or res.stderr.strip())

    push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    if push_res.returncode == 0:
        print("✅ git push origin main 성공!")
    else:
        print("⚠️ git push 실패:", push_res.stderr)

    head_hash = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8").stdout.strip()
    return head_hash

def main():
    print("=" * 64)
    print("🌙 사령관님 취침 전 최종 봉인: R7 항체 & GEN-1 진화 로드맵 영구 기록")
    print("=" * 64)
    update_master_schedule()
    update_evolution_json()
    update_evolution_md()
    sheet_ranges = sync_sheets()
    commit_hash = git_commit_and_push()

    print("\n" + "=" * 64)
    print("🧾 [취침 전 최종 영수증]")
    print(f"  * Commit 해시: {commit_hash}")
    for name, rng in sheet_ranges.items():
        print(f"  * {name}: {rng}")
    print("  * R7 항체: R7_TARGET_ROW_BADGE_ONLY_SCAN (등록 완료)")
    print("  * 내일 아침 1순위: GEN-1 완전 무인 자가 진화 폐쇄 루프 (등재 완료)")
    print("=" * 64)

if __name__ == "__main__":
    main()
