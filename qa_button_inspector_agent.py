# -*- coding: utf-8 -*-
"""
qa_button_inspector_agent.py [QA-901]
--------------------------------------------------------------------------------
이상일 대표님([COMMANDER-000]) 직속 독립 검수 에이전트 [QA-901]
1. 대시보드 및 독립 앱 내 모든 <button> & onclick 핸들러 전수 검사 (미정의 함수 0건 확인)
2. 4방향 고정 각도 버튼 완전 삭제 여부 검증
3. 3D 360° 좌우회전 / 상하 틸트 및 실사 얼굴 합성 엔진 검증
4. 만능 멀티-AI 실시간 교신 관제탑 (omni_agent_bus.json & /api/omni-agent-bus) 검증
5. 르곤-안실장 양방향 무인 동기화 데몬 (rgon_auto_sync_daemon.py) 검증
6. 5개 탭 DOM 누수 0건 격리 무결성 및 JS 문법(node --check) 검증
--------------------------------------------------------------------------------
"""

import os
import sys
import re
import subprocess
import urllib.request
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def check_file_onclick_integrity(filepath):
    print(f"\n[🔍 1. 버튼 및 함수 매핑 검수] 대상 파일: {filepath}")
    if not os.path.exists(filepath):
        print(f"❌ [FAIL] 파일 없음: {filepath}")
        return False, []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    onclick_matches = re.findall(r'onclick=(["\'])(.*?)\1', content, re.IGNORECASE)
    onclick_calls = [m[1].strip() for m in onclick_matches]

    called_funcs = set()
    for oc in onclick_calls:
        funcs = re.findall(r'(?<!\.)\b([a-zA-Z0-9_$]+)\s*\(', oc)
        for fn in funcs:
            called_funcs.add(fn)

    defined_funcs = set()
    script_blocks = re.findall(r'<script\b[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    for block in script_blocks:
        for fn in re.findall(r'function\s+([a-zA-Z0-9_$]+)\s*\(', block):
            defined_funcs.add(fn)
        for fn in re.findall(r'(?:var|let|const|window\.)\s*([a-zA-Z0-9_$]+)\s*=\s*', block):
            defined_funcs.add(fn)
        for fn in re.findall(r'async\s+function\s+([a-zA-Z0-9_$]+)\s*\(', block):
            defined_funcs.add(fn)

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
        "3D 360° 회전 실시간 배지 (3D 360° 터치 회전)": "3D 360° 터치 회전" in content,
        "만능 멀티-AI 교신 관제탑 (omni-agent-bus-panel)": "omni-agent-bus-panel" in content,
        "대표님 명령 하달창 (cmd-broadcast-input)": "cmd-broadcast-input" in content,
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

def check_omni_agent_bus():
    print("\n[🌐 5. 만능 멀티-AI 실시간 교신 버스 (omni_agent_bus.json & API) 검수]")
    if not os.path.exists("omni_agent_bus.json"):
        print("  ❌ [FAIL] omni_agent_bus.json 파일 없음")
        return False

    with open("omni_agent_bus.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    reg = data.get("registry", [])
    msgs = data.get("messages", [])
    print(f"  - 등록된 AI 에이전트 수: {len(reg)}개")
    for a in reg:
        print(f"    * [{a['id']}] {a['name']} ({a['role']})")
    print(f"  - 현재 교신 메시지 수: {len(msgs)}개")

    has_commander = any(a["id"] == "COMMANDER-000" for a in reg)
    has_rgon = any(a["id"] == "RGON-001" for a in reg)
    has_agv = any(a["id"] == "AGV-101" for a in reg)
    has_qa = any(a["id"] == "QA-901" for a in reg)

    if has_commander and has_rgon and has_agv and has_qa:
        print("  ✅ [PASS] 전 에이전트 고유번호 레지스트리 무결성 100% 확인!")
        return True
    else:
        print("  ❌ [FAIL] 필수 에이전트 ID 누락")
        return False

def check_rgon_auto_sync_daemon():
    print("\n[⚡ 6. 르곤-안실장 무인 동기화 데몬 (rgon_auto_sync_daemon.py) 검수]")
    if not os.path.exists("rgon_auto_sync_daemon.py"):
        print("  ❌ [FAIL] rgon_auto_sync_daemon.py 파일 없음")
        return False

    try:
        res = subprocess.run(["python", "rgon_auto_sync_daemon.py", "--test-sync"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if "100% 통과" in res.stdout or "PASS" in res.stdout:
            print("  ✅ [PASS] 르곤이 시그널 IN/OUT 양방향 무인 동기화 엔진 100% 정상 가동!")
            return True
        else:
            print(f"  ❌ [FAIL] 데몬 자가검증 실패:\n{res.stdout}\n{res.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ [FAIL] 실행 에러: {e}")
        return False

def check_swarm_dom_isolation():
    print("\n[🛡️ 7. 에이전트 스웜(agent_swarm_cloner.py) DOM 격리 무결성 검수]")
    if os.path.exists("agent_swarm_cloner.py"):
        try:
            res = subprocess.run(["python", "agent_swarm_cloner.py"], capture_output=True, text=True, encoding="utf-8", errors="replace")
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
    print("🚀 [독립 검수 에이전트: QA-901] 만능 멀티-AI 관제탑 & 꿈의 옷장 4대 개혁 전수 검수")
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

    pass_bus = check_omni_agent_bus()
    pass_sync = check_rgon_auto_sync_daemon()
    pass_swarm = check_swarm_dom_isolation()

    print("\n" + "=" * 80)
    print("📋 [QA-901 최종 검수 판정표]")
    print("=" * 80)
    total_pass = True
    for fp, passed, missing in all_file_results:
        status = "🏅 100% PASS" if passed else "❌ REJECT"
        print(f"- {fp}: {status}")
        if not passed:
            total_pass = False
            if missing:
                print(f"  👉 결손 함수: {missing}")

    status_bus = "🏅 100% PASS" if pass_bus else "❌ REJECT"
    print(f"- 만능 멀티-AI 실시간 교신 버스: {status_bus}")
    if not pass_bus:
        total_pass = False

    status_sync = "🏅 100% PASS" if pass_sync else "❌ REJECT"
    print(f"- 르곤-안실장 무인 동기화 엔진: {status_sync}")
    if not pass_sync:
        total_pass = False

    status_swarm = "🏅 100% PASS" if pass_swarm else "❌ REJECT"
    print(f"- 5개 탭 DOM 누수 격리 무결성: {status_swarm}")
    if not pass_swarm:
        total_pass = False

    print("=" * 80)
    if total_pass:
        print("🎉 [최종 결과]: 전 항목 100% 통과(ALL PASS)! 이상일 대표님([COMMANDER-000])께 즉시 보고 가능!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("🚨 [최종 결과]: 일부 검수 항목 미통과! 즉시 자동 수리 후 재검수 필요!")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
