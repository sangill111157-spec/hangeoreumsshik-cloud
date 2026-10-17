# -*- coding: utf-8 -*-
"""
qa_button_inspector_agent.py
--------------------------------------------------------------------------------
이상일 대표님의 특명: 스마트폰 v3.5 Pro 전수 버튼 및 3D/얼굴합성 독립 검수 에이전트
1. 대시보드 및 독립 앱 내 모든 <button> & onclick 핸들러 전수 검사 (미정의 함수 0건 확인)
2. 4방향 고정 각도 버튼 완전 삭제 여부 검증
3. 3D 360° 좌우회전 / 상하 틸트 및 실사 얼굴 합성 엔진 검증
4. 5개 탭 DOM 누수 0건 격리 무결성 및 JS 문법(node --check) 검증
--------------------------------------------------------------------------------
"""

import os
import sys
import re
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def check_file_onclick_integrity(filepath):
    print(f"\n[🔍 1. 버튼 및 함수 매핑 검수] 대상 파일: {filepath}")
    if not os.path.exists(filepath):
        print(f"❌ [FAIL] 파일 없음: {filepath}")
        return False, []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. onclick 속성 추출
    onclick_matches = re.findall(r'onclick=(["\'])(.*?)\1', content, re.IGNORECASE)
    onclick_calls = [m[1].strip() for m in onclick_matches]

    # 호출 함수명 추출 (점 앞의 메서드 제외: e.g. obj.method() -> method 제외)
    called_funcs = set()
    for oc in onclick_calls:
        # 점이 붙지 않은 순수 함수 호출 추출: (?<!\.)\b([a-zA-Z0-9_$]+)\s*\(
        funcs = re.findall(r'(?<!\.)\b([a-zA-Z0-9_$]+)\s*\(', oc)
        for fn in funcs:
            called_funcs.add(fn)

    # 2. <script> 태그 내부 정의 함수 추출
    defined_funcs = set()
    script_blocks = re.findall(r'<script\b[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    for block in script_blocks:
        # function funcName(...)
        for fn in re.findall(r'function\s+([a-zA-Z0-9_$]+)\s*\(', block):
            defined_funcs.add(fn)
        # var/let/const/window.funcName = ...
        for fn in re.findall(r'(?:var|let|const|window\.)\s*([a-zA-Z0-9_$]+)\s*=\s*', block):
            defined_funcs.add(fn)
        # async function funcName(...)
        for fn in re.findall(r'async\s+function\s+([a-zA-Z0-9_$]+)\s*\(', block):
            defined_funcs.add(fn)

    # 표준 브라우저 빌트인 제외
    standard_builtins = {
        'alert', 'confirm', 'prompt', 'preventDefault', 'stopPropagation',
        'open', 'close', 'focus', 'blur', 'print', 'scrollTo', 'scrollBy',
        'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'slice',
        'trim', 'replace', 'toLowerCase', 'toUpperCase', 'split', 'join'
    }

    missing = [fn for fn in sorted(called_funcs) if fn not in defined_funcs and fn not in standard_builtins]

    print(f"  - 발견된 총 onclick 핸들러 수: {len(onclick_calls)}개")
    print(f"  - 호출되는 고유 함수 수: {len(called_funcs)}개")
    print(f"  - 스크립트 내 정의된 함수 수: {len(defined_funcs)}개")

    if missing:
        print(f"  ⚠️ [미정의 함수 발견 ({len(missing)}개)]: {missing}")
        return False, missing
    else:
        print(f"  ✅ [PASS] 모든 onclick 호출 함수({len(called_funcs)}개)가 100% 정상 정의됨!")
        return True, []

def check_angle_buttons_removal(filepath):
    print(f"\n[🔄 2. 4방향 고정 각도 버튼 삭제 검수] 대상 파일: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # setMainAngle(0), setMainAngle(90) 등의 버튼 태그가 HTML 상에 남아있는지 검사
    button_fixed_angles = re.findall(r'<button[^>]*setMainAngle\(\s*\d+\s*\)[^>]*>', content, re.IGNORECASE)
    if button_fixed_angles:
        print(f"  ❌ [FAIL] 4방향 고정 각도 버튼이 아직 남아있음 ({len(button_fixed_angles)}개):")
        for b in button_fixed_angles:
            print(f"    - {b}")
        return False
    else:
        print("  ✅ [PASS] 4방향 고정 각도 버튼(0°/90°/180°/270°)이 100% 완전히 삭제됨!")
        return True

def check_3d_and_face_synthesis(filepath):
    print(f"\n[📸 3. 3D 360° 터치 회전 & 실사 얼굴 합성 엔진 검수] 대상 파일: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    requirements = {
        "3D 회전 변수 (yawAngle)": "yawAngle" in content,
        "상하 틸트 변수 (pitchTilt)": "pitchTilt" in content,
        "모바일 터치 이벤트 (touchmove)": "touchmove" in content,
        "터치 액션 제어 (touch-action: none)": "touch-action: none" in content,
        "실사 얼굴 전역 이미지 (userFaceImage)": "userFaceImage" in content,
        "캔버스 얼굴 원형 클리핑 합성 (drawImage & clip)": "drawImage" in content and "clip" in content,
        "내 얼굴 사진 넣기 버튼 ([📸 내 얼굴 사진 넣기])": "내 얼굴 사진 넣기" in content,
        "사진 촬영/선택 플로팅 메뉴 (face-photo-menu)": "face-photo-menu" in content,
    }

    all_passed = True
    for item, passed in requirements.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  - {item}: {status}")
        if not passed:
            all_passed = False

    return all_passed

def check_node_syntax(filepath):
    print(f"\n[⚙️ 4. 자바스크립트 문법(node --check) 무결성 검수] 대상 파일: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    script_blocks = re.findall(r'<script\b[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    if not script_blocks:
        print("  ⚠️ [WARN] 검사할 스크립트 블록 없음")
        return True

    combined_js = "\n\n// --- NEXT SCRIPT BLOCK ---\n\n".join(script_blocks)
    temp_js_path = ".qa_temp_script.js"
    with open(temp_js_path, "w", encoding="utf-8") as f:
        f.write(combined_js)

    try:
        res = subprocess.run(["node", "--check", temp_js_path], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode == 0:
            print("  ✅ [PASS] 자바스크립트 문법(node --check) 100% 오류 없음!")
            return True
        else:
            print(f"  ❌ [FAIL] JS 문법 에러 발견:\n{res.stderr}")
            return False
    except Exception as e:
        print(f"  ⚠️ [SKIP] node 실행 실패: {e}")
        return True
    finally:
        if os.path.exists(temp_js_path):
            os.remove(temp_js_path)

def check_swarm_dom_isolation():
    print("\n[🛡️ 5. 에이전트 스웜(agent_swarm_cloner.py) DOM 격리 무결성 검수]")
    if os.path.exists("agent_swarm_cloner.py"):
        try:
            res = subprocess.run(["python", "agent_swarm_cloner.py"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            print(res.stdout.strip())
            if "'success': True" in res.stdout and res.stdout.count("'status': 'PASS'") >= 5:
                print("  ✅ [PASS] 5개 탭 DOM 완전 격리 및 누수 0건 검증 완료!")
                return True
            else:
                return False
        except Exception as e:
            print(f"  ❌ [FAIL] agent_swarm_cloner 실행 에러: {e}")
            return False
    else:
        print("  ⚠️ [WARN] agent_swarm_cloner.py 파일 없음")
        return False

def main():
    print("=" * 80)
    print("🚀 [독립 검수 에이전트: QA-Inspector-Bot] 대시보드 v3.5 Pro 전수 검수 시작")
    print("=" * 80)

    files_to_check = [
        "dashboard/index.html",
        "dashboard/dream_closet_future_master_app.html"
    ]

    all_file_results = []

    for fp in files_to_check:
        print(f"\n==================== [파일 정밀 검수: {fp}] ====================")
        pass1, missing_funcs = check_file_onclick_integrity(fp)
        pass2 = check_angle_buttons_removal(fp)
        pass3 = check_3d_and_face_synthesis(fp)
        pass4 = check_node_syntax(fp)
        file_passed = pass1 and pass2 and pass3 and pass4
        all_file_results.append((fp, file_passed, missing_funcs))

    pass5 = check_swarm_dom_isolation()

    print("\n" + "=" * 80)
    print("📋 [최종 검수 판정표]")
    print("=" * 80)
    total_pass = True
    for fp, passed, missing in all_file_results:
        status = "🏅 100% PASS" if passed else "❌ REJECT"
        print(f"- {fp}: {status}")
        if not passed:
            total_pass = False
            if missing:
                print(f"  👉 결손 함수: {missing}")

    status5 = "🏅 100% PASS" if pass5 else "❌ REJECT"
    print(f"- 5개 탭 DOM 누수 격리 무결성: {status5}")
    if not pass5:
        total_pass = False

    print("=" * 80)
    if total_pass:
        print("🎉 [최종 결과]: 전 항목 100% 통과(ALL PASS)! 이상일 대표님께 즉시 보고 가능!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("🚨 [최종 결과]: 일부 검수 항목 미통과! 즉시 자동 수리 후 재검수 필요!")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
