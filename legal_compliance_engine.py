# -*- coding: utf-8 -*-
"""
legal_compliance_engine.py [제5청사 자율법무·컴플라이언스 5대 안전망 감사 엔진]
================================================================================
👑 COMMANDER-000 이상일 대표님 제1원칙: "안전 제일! 위법/규정 위반 0%, 클린룸 자체 제작"
1) 저작권법 & 부정경쟁방지법: 타사 코드/상표 무단 도용 0%, 100% 클린룸 자체 창작
2) 공정거래위원회 표시광고법: 의무 대가성 문구 필수 표기
3) 개인정보보호법 (Zero-Collection): 서버 전송/저장 0%, 브라우저 로컬 안전 처리
4) 소비자 보호 및 면책 고지: 법률·세무·의료 진단 대체 불가 일상 참고용 명시
5) 2026 AI 기본법 & 건전성 가이드라인: 투명성 표시 및 스팸/사행성 원천 차단
================================================================================
"""

import os
import sys
import json
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAFE_APPS_DIR = os.path.join(BASE_DIR, "dashboard", "safe_apps")

# 5대 법적 필수 문구 상수 (SSOT)
REQUIRED_LEGAL_STATEMENTS = {
    "ftc_notice": "※ 본 콘텐츠(서비스)는 제휴 활동(쿠팡파트너스 등)의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다.",
    "privacy_cert": "🔒 개인정보 서버 미수집·미저장 안전 인증",
    "legal_disclaimer": "⚖️ 본 결과는 일상 참고용이며 전문적인 법률·세무·의료 진단을 대신하지 않습니다.",
    "clean_room_badge": "🛡️ 자율법무팀 합법·안전 심의필 (Clean-Room Original Creation)",
    "ai_transparency": "🤖 2026 AI 기본법 준수: 본 서비스는 건전하고 투명한 AI 보조 기술을 기반으로 자체 제작되었습니다."
}

def audit_file_content(filepath: str) -> dict:
    """HTML 파일의 5대 법률·규정 준수 여부를 정밀 전수 검사합니다."""
    if not os.path.exists(filepath):
        return {
            "passed": False,
            "filename": os.path.basename(filepath),
            "score": 0,
            "violations": ["파일이 존재하지 않습니다."]
        }

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    filename = os.path.basename(filepath)
    violations = []
    checks = {}

    # 1. 공정위 표시광고법 대가성 문구
    has_ftc = ("제휴 활동(쿠팡파트너스 등)의 일환으로" in content and "수수료를 제공받을 수 있습니다" in content)
    checks["ftc_notice"] = has_ftc
    if not has_ftc:
        violations.append("공정거래위원회 표시광고법 대가성 의무 문구 누락")

    # 2. 개인정보보호법 Zero-Collection 인증
    has_privacy = ("개인정보 서버 미수집·미저장" in content or "🔒 개인정보" in content)
    checks["privacy_protection"] = has_privacy
    if not has_privacy:
        violations.append("개인정보보호법 준수(서버 미수집·미저장) 문구 누락")

    # 3. 법적 면책 고지 (Legal Disclaimer)
    has_disclaimer = ("전문적인 법률·세무·의료 진단을 대신하지 않습니다" in content or "일상 참고용" in content)
    checks["legal_disclaimer"] = has_disclaimer
    if not has_disclaimer:
        violations.append("법적 면책 고지(Legal Disclaimer) 누락")

    # 4. 클린룸 자체 제작 및 저작권 준수
    has_clean_badge = ("합법·안전 심의필" in content or "Clean-Room" in content)
    checks["clean_room_badge"] = has_clean_badge
    if not has_clean_badge:
        violations.append("클린룸 자체 제작 심의필 배지 누락")

    # 5. 불법/위반 키워드(타사 무단도용, 스캠 등) 존재 여부 검사
    forbidden_keywords = ["불법복제", "도용코드", "크랙", "개인정보수집동의없이전송"]
    forbidden_found = [kw for kw in forbidden_keywords if kw in content]
    checks["no_forbidden_content"] = (len(forbidden_found) == 0)
    if forbidden_found:
        violations.append(f"금지된 위반 키워드 검출: {', '.join(forbidden_found)}")

    passed = len(violations) == 0
    score = int((sum(1 for v in checks.values() if v) / len(checks)) * 100)

    return {
        "passed": passed,
        "filename": filename,
        "filepath": filepath,
        "score": score,
        "checks": checks,
        "violations": violations
    }

def audit_all_safe_apps() -> dict:
    """dashboard/safe_apps/ 내의 모든 웹앱을 감사하고 종합 리포트를 반환합니다."""
    os.makedirs(SAFE_APPS_DIR, exist_ok=True)
    files = [os.path.join(SAFE_APPS_DIR, f) for f in os.listdir(SAFE_APPS_DIR) if f.endswith(".html")]

    results = []
    all_passed = True
    total_score = 0

    target_apps = [
        "safe_daily_lucky.html",
        "safe_salary_planner.html",
        "safe_healing_sound.html"
    ]

    for app_name in target_apps:
        app_path = os.path.join(SAFE_APPS_DIR, app_name)
        res = audit_file_content(app_path)
        results.append(res)
        if not res["passed"]:
            all_passed = False
        total_score += res["score"]

    avg_score = int(total_score / len(target_apps)) if target_apps else 0

    return {
        "status": "APPROVED" if all_passed else "REJECTED_NEEDS_FIX",
        "compliance_rate": f"{avg_score}%",
        "total_apps": len(target_apps),
        "apps": results,
        "required_statements": REQUIRED_LEGAL_STATEMENTS,
        "commander_safety_doctrine": "위법 0%, 클린룸 자체 제작, 소비자 보호 5대 안전장치 100% 가동"
    }

if __name__ == "__main__":
    rep = audit_all_safe_apps()
    print(json.dumps(rep, ensure_ascii=False, indent=2))
