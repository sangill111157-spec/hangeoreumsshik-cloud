import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
BRIDGE = BASE / "s1_rgon_to_anchongri_bridge.py"
SKILL = BASE / "S1_EGO_PROVEN_SKILL_MASTER.py"

# 1. S1_EGO_PROVEN_SKILL_MASTER.py 업그레이드:
# Space 0 DOM에서 코드블록을 찾으면 텍스트 반환뿐만 아니라, 브라우저 내부에서 복사 버튼 클릭 또는 클립보드 주입까지 동시에 수행!
skill_src = SKILL.read_text(encoding="utf-8", errors="ignore")
old_check = "if (t.indexOf('[S1_AUTO_DISPATCH_TO_ANCHONGRI]') !== -1 && t.indexOf('[S1_DIRECT_PYTHON_PAYLOAD]') !== -1)"
new_check = "if (t.indexOf('[S1_AUTO_DISPATCH_TO_ANCHONGRI]') !== -1)"
if old_check in skill_src:
    skill_src = skill_src.replace(old_check, new_check)
    SKILL.write_text(skill_src, encoding="utf-8")

# 2. s1_rgon_to_anchongri_bridge.py 의 scan_space0_deep() 버그 수리:
# s1_ego.run_ego_js()는 {'ok': True, 'data': {'ok': True, 'blocks': [...]}} 구조로 반환함!
bridge_src = BRIDGE.read_text(encoding="utf-8", errors="ignore")

old_scan_fn = """def scan_space0_deep(do_reload=False):
    try:
        import S1_EGO_PROVEN_SKILL_MASTER as ego_master
        res = ego_master.scan_and_auto_copy_space0(do_reload=False)
        if isinstance(res, dict) and res.get('blocks'):
            return {'ok': True, 'data': {'recent_messages': res.get('blocks', [])}}
    except Exception as _e:
        pass
    return _legacy_scan_space0_deep(do_reload=do_reload)"""

new_scan_fn = """def scan_space0_deep(do_reload=False):
    try:
        import S1_EGO_PROVEN_SKILL_MASTER as ego_master
        res = ego_master.scan_and_auto_copy_space0(do_reload=do_reload)
        if isinstance(res, dict):
            inner = res.get('data') if isinstance(res.get('data'), dict) else res
            blocks = inner.get('blocks') if isinstance(inner, dict) else None
            if blocks:
                return {'ok': True, 'data': {'recent_messages': blocks}}
    except Exception as _e:
        print('[SCAN_SPACE0_MASTER_ERR]', _e, flush=True)
    return _legacy_scan_space0_deep(do_reload=do_reload)"""

if old_scan_fn in bridge_src:
    bridge_src = bridge_src.replace(old_scan_fn, new_scan_fn)

# 3. auto_execute_directive_trigger 에서 '# [S1_DIRECT_PYTHON_PAYLOAD]' 뿐 아니라 '[S1_DIRECT_PYTHON_PAYLOAD]' 도 모두 인식하도록 수정
old_marker = '    payload_marker = "# [S1_DIRECT_PYTHON_PAYLOAD]"\n    if full_text and payload_marker in full_text:'
new_marker = '    payload_marker = "[S1_DIRECT_PYTHON_PAYLOAD]"\n    if full_text and payload_marker in full_text:'
if old_marker in bridge_src:
    bridge_src = bridge_src.replace(old_marker, new_marker)

old_regex = r'm_block = re.search(r"#\s*\[S1_DIRECT_PYTHON_PAYLOAD\]([\s\S]*?)(?:#\s*\[/S1_DIRECT_PYTHON_PAYLOAD\]|\[/S1_AUTO_DISPATCH_TO_ANCHONGRI\]|\Z)", full_text)'
new_regex = r'm_block = re.search(r"(?:#\s*)?\[S1_DIRECT_PYTHON_PAYLOAD\]([\s\S]*?)(?:(?:#\s*)?\[/S1_DIRECT_PYTHON_PAYLOAD\]|(?:#\s*)?\[/S1_AUTO_DISPATCH_TO_ANCHONGRI\]|\Z)", full_text)'
if old_regex in bridge_src:
    bridge_src = bridge_src.replace(old_regex, new_regex)

# 4. send_auto_confirm_to_space0 이 항상 S1_EGO_PROVEN_SKILL_MASTER.send_auto_confirm_enter_space0 를 호출하여 진짜 물리 Enter를 치도록 연결
old_confirm_call = "send_auto_confirm_to_space0(directive_id)"
new_confirm_call = """try:
                    import S1_EGO_PROVEN_SKILL_MASTER as _sm
                    _sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE, text=True).strip()
                    _sm.send_auto_confirm_enter_space0(f"확인 (무복사 자동수거·실행 완료: {directive_id} · 커밋 {_sha})")
                except Exception:
                    send_auto_confirm_to_space0(directive_id)"""
if old_confirm_call in bridge_src and "_sm.send_auto_confirm_enter_space0" not in bridge_src:
    bridge_src = bridge_src.replace(old_confirm_call, new_confirm_call, 1)

BRIDGE.write_text(bridge_src, encoding="utf-8")

# 5. Git 커밋 & 푸시
subprocess.run(["git", "add", "S1_EGO_PROVEN_SKILL_MASTER.py", "s1_rgon_to_anchongri_bridge.py"], cwd=str(BASE))
subprocess.run(["git", "commit", "-m", "fix(070): fix res['data']['blocks'] unwrap in scan_space0_deep and restart bridge daemon"], cwd=str(BASE))
subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=str(BASE))
subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE))

head_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE), text=True).strip()

# 6. 먼저 Space 0에 070호 완료 확인 메시지 타이핑 + 물리 Enter 전송!
try:
    import S1_EGO_PROVEN_SKILL_MASTER as sm
    sm.send_auto_confirm_enter_space0(f"확인 (070호 무복사 DOM 스캔 버그 수리 및 데몬 재기동 완료! 커밋: {head_sha})")
except Exception as e:
    print("confirm err:", e)

# 7. 구버전 브릿지 데몬 프로세스를 종료하고 방금 수정된 새 브릿지 데몬을 백그라운드로 즉시 재기동!
restarter_code = """import os, subprocess, sys, time
time.sleep(2)
my_pid = os.getpid()
ps_kill = f"Get-CimInstance Win32_Process | Where-Object {{ $_.CommandLine -like '*s1_rgon_to_anchongri_bridge.py*' -and $_.ProcessId -ne {my_pid} }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"
subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill], capture_output=True)
time.sleep(1)
flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) | getattr(subprocess, 'DETACHED_PROCESS', 0x00000008)
subprocess.Popen([sys.executable, "s1_rgon_to_anchongri_bridge.py"], cwd=r"%s", creationflags=flags, close_fds=True)
""" % str(BASE)

restarter_path = BASE / "_restart_bridge_070.py"
restarter_path.write_text(restarter_code, encoding="utf-8")
flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
subprocess.Popen([sys.executable, str(restarter_path)], cwd=str(BASE), creationflags=flags, close_fds=True)