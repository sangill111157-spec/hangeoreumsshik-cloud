#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
record_evolution_and_sync.py
오늘자(2026-10-20) RGON Omni-Link Hub v6.0.3 진화 기록을
1) evolution_memory.json
2) RGON_EVOLUTION_LOG.md
3) Google Sheets 2곳 ('RGON_진화일지' 탭)
에 기록하고,
4) Git Commit & Push 수행
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

NEW_ROWS = [
    {
        "일시": NOW,
        "구분": "잘한 점 (Well Done)",
        "핵심항목": "커스텀 신경망 직접 쓰기(Custom Role) 탑재",
        "상세내용": "사령관님 맞춤형 AI/신경망 탭 명칭을 직접 입력·등록하여 유연하게 감지·라우팅하는 만능 소통창 v6.0.3 완성",
        "적용_및_조치": "rgon_aside_extension / omni_link_ext에 직접 쓰기 UI 및 상태 머신 반영",
        "상태": "완료"
    },
    {
        "일시": NOW,
        "구분": "잘한 점 (Well Done)",
        "핵심항목": "개별 체크/단독/전체 다중 디스패치 완성",
        "상세내용": "체크박스 선택 발사, 단독 발사, 3종 전체 동시 발사 인터페이스를 구축하여 지시 대상 탭을 정밀 제어",
        "적용_및_조치": "독대실 상단 및 확장 프로그램 팝업/사이드바에 멀티 타겟 디스패처 탑재",
        "상태": "완료"
    },
    {
        "일시": NOW,
        "구분": "잘한 점 (Well Done)",
        "핵심항목": "아레나 자동 흡수 및 자동 청소(Auto-Clean) 엔진",
        "상세내용": "이전 라운드 잔여 코드 자동 정리 기능(#autoCleanAbs)과 'Copy' 접두어 3중 필터링을 통해 Best-of-Breed 아레나 분석 정밀도 극대화",
        "적용_및_조치": "브리지 /api/shared/replace 및 클라이언트 샌드박스 정화 엔진 적용",
        "상태": "완료"
    }
]

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
    data.extend(NEW_ROWS)
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ evolution_memory.json 업데이트 완료 (총 {len(data)}개 항목)")

def update_evolution_md():
    md_path = ROOT / "RGON_EVOLUTION_LOG.md"
    new_md_lines = []
    for r in NEW_ROWS:
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
        r"C:\Users\sangi\Downloads\shin-agent\config\token.pickle"
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
        for r in NEW_ROWS
    ]
    results = {}
    for sid, name in [(SHEET_1_SHIN, "SHIN FAMILY COMMAND CENTER"), (SHEET_3_BLOG, "BLOG AUTOMATION COMMAND CENTER")]:
        body = {
            "values": rows_values
        }
        res = service.spreadsheets().values().append(
            spreadsheetId=sid,
            range=f"'{TAB_NAME}'!A:F",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        updated_range = res.get("updates", {}).get("updatedRange", "N/A")
        results[name] = updated_range
        print(f"✅ {name} ({sid}) '{TAB_NAME}' 추가 완료: {updated_range}")
    return results

def git_commit_and_push():
    # .gitignore 확인
    # 민감 파일들은 이미 .gitignore에 보호되어 있음
    files_to_add = [
        "omni_link_ext",
        "rgon_aside_extension",
        "omni_bridge.py",
        "start_omni_bridge.bat",
        "build_omni_link_communicator.py",
        "upgrade_omni_link_v601.py",
        "upgrade_omni_link_v602.py",
        "upgrade_omni_link_v603.py",
        "rgon_alpha_chat.html",
        "dashboard/rgon_alpha_chat.html",
        "docs/rgon_alpha_chat.html",
        "evolution_memory.json",
        "RGON_EVOLUTION_LOG.md"
    ]
    
    existing_files = [f for f in files_to_add if (ROOT / f).exists()]
    for f in existing_files:
        subprocess.run(["git", "add", f], cwd=str(ROOT), check=True)
    
    commit_msg = "feat(omni-link-v6.0.3): custom neural role & solo/check dispatch + evolution sync"
    commit_res = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8"
    )
    if commit_res.returncode == 0:
        print("✅ git commit 완료:", commit_msg)
    else:
        print("ℹ️ git commit 결과 (이미 최신이거나 반영됨):", commit_res.stdout.strip())
        
    push_res = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8"
    )
    if push_res.returncode == 0:
        print("✅ git push origin main 성공!")
    else:
        print("⚠️ git push 실패 또는 추가 조치 필요:", push_res.stderr)
        
    head_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8"
    ).stdout.strip()
    return head_hash

def main():
    print("=" * 64)
    print("📋 2단계: 오늘자 진화 장부 기록 및 GitHub 원격 봉인 시작")
    print("=" * 64)
    update_evolution_json()
    update_evolution_md()
    sheet_ranges = sync_sheets()
    commit_hash = git_commit_and_push()
    
    print("\n" + "=" * 64)
    print(f"🧾 Commit 해시: {commit_hash}")
    for name, rng in sheet_ranges.items():
        print(f"📊 {name} 추가 범위: {rng}")
    print("=" * 64)

if __name__ == "__main__":
    main()
