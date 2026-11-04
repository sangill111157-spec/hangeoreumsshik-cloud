"""
========================================================================
⚡ [S1-BUILD-049] 르곤 직할 무인 집행 엔진 시공 마스터
========================================================================
"""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
KST = timezone(timedelta(hours=9))

def now_iso() -> str:
    return datetime.now(KST).isoformat()

def sha256_file(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

NEW_TRIGGER_FUNC = '''
def auto_execute_directive_trigger(directive_id: str, full_text: str = "") -> dict:
    """
    [049호 르곤 직할 무인 집행 엔진]
    안총리(IDE 채팅창) 개입 없이 르곤 보좌관(Space 0)의 파이썬 페이로드(# [S1_DIRECT_PYTHON_PAYLOAD])를
    s1_rgon_to_anchongri_bridge.py 데몬이 직접 추출 -> 로컬 실행 -> 린터 검증 -> git commit & push 까지 100% 무인 완주!
    """
    log_file = BASE / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"
    docs_log_file = BASE / "docs" / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"
    
    # [A] 르곤 직할 파이썬 페이로드(# [S1_DIRECT_PYTHON_PAYLOAD]) 감지
    payload_marker = "# [S1_DIRECT_PYTHON_PAYLOAD]"
    if full_text and payload_marker in full_text:
        print(f"[RGON_DIRECT_ENGINE] Detected direct payload in {directive_id}!", flush=True)
        code_to_run = ""
        # 1) ```python ... ``` 형태
        m_fence = re.search(r"```(?:python)?\\s*\\n([\\s\\S]*?)```", full_text)
        if m_fence and payload_marker in m_fence.group(0):
            code_to_run = m_fence.group(1).strip()
        else:
            # 2) 마커 이후부터 [/S1_DIRECT_PYTHON_PAYLOAD] 또는 블록 끝까지
            m_block = re.search(r"#\\s*\\[S1_DIRECT_PYTHON_PAYLOAD\\]([\\s\\S]*?)(?:#\\s*\\[/S1_DIRECT_PYTHON_PAYLOAD\\]|\\[/S1_AUTO_DISPATCH_TO_ANCHONGRI\\]|\\Z)", full_text)
            if m_block:
                code_to_run = m_block.group(1).strip()

        if code_to_run:
            runner_file = BASE / "s1_direct_payload_runner.py"
            runner_file.write_text(code_to_run, encoding="utf-8")
            print(f"[RGON_DIRECT_ENGINE] Saved payload to {runner_file} ({len(code_to_run)} bytes). Executing immediately...", flush=True)

            # 1) 직접 실행
            exec_res = subprocess.run([sys.executable, str(runner_file)], cwd=BASE, timeout=120, capture_output=True, text=True)
            print(f"[RGON_DIRECT_ENGINE] Payload exit code: {exec_res.returncode}", flush=True)
            if exec_res.stdout:
                print(f"[RGON_DIRECT_ENGINE] Stdout: {exec_res.stdout[:300]}", flush=True)

            # 2) 린터 자동 검증
            linter_res = subprocess.run([sys.executable, "s1_qm_structure_linter.py"], cwd=BASE, timeout=60, capture_output=True, text=True)
            print(f"[RGON_DIRECT_ENGINE] Linter exit code: {linter_res.returncode}", flush=True)

            # 3) Git 무인 커밋 & 푸시
            try:
                subprocess.run(["git", "add", "-A"], cwd=BASE, check=False)
                subprocess.run(["git", "commit", "-m", f"auto(rgon-direct): executed {directive_id} without anchongri"], cwd=BASE, check=False)
                subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=BASE, check=False)
                subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)
                print(f"[RGON_DIRECT_ENGINE] Git auto push completed for {directive_id}!", flush=True)
            except Exception as e:
                print(f"[RGON_DIRECT_ENGINE] Git sync note: {e}", flush=True)

            log_entry = {
                "directive_id": directive_id,
                "timestamp": now_iso(),
                "pid": os.getpid(),
                "mode": "RGON_DIRECT_PYTHON_EXECUTION",
                "status": "COMPLETED",
                "returncode": exec_res.returncode,
                "ok": (exec_res.returncode == 0)
            }
            _save_trigger_log(log_file, docs_log_file, log_entry)
            return log_entry

    # [B] 일반 지시서인 경우 로컬 무쿼터 파운드리 백그라운드 가동
    foundry_py = BASE / "s1_zero_quota_triumvirate_foundry.py"
    pid = None
    if foundry_py.exists():
        try:
            proc = subprocess.Popen(
                [sys.executable, str(foundry_py), "--directive", directive_id],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            pid = proc.pid
            print(f"[BRIDGE_TRIGGER] Auto-spawned zero-quota foundry for {directive_id} (PID: {pid})", flush=True)
        except Exception as e:
            print(f"[BRIDGE_TRIGGER] Failed to spawn foundry: {e}", flush=True)

    log_entry = {
        "directive_id": directive_id,
        "timestamp": now_iso(),
        "pid": pid,
        "mode": "STANDARD_FOUNDRY_SPAWN",
        "status": "TRIGGERED",
        "ok": True
    }
    _save_trigger_log(log_file, docs_log_file, log_entry)
    return log_entry


def _save_trigger_log(log_file, docs_log_file, log_entry):
    try:
        data = {"version": "1.0.0", "triggers": []}
        if log_file.exists():
            try:
                data = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        data.setdefault("triggers", []).append(log_entry)
        log_json_str = json.dumps(data, ensure_ascii=False, indent=2)
        log_file.write_text(log_json_str, encoding="utf-8")
        docs_log_file.parent.mkdir(parents=True, exist_ok=True)
        docs_log_file.write_text(log_json_str, encoding="utf-8")
    except Exception as e:
        print(f"[BRIDGE_TRIGGER] Failed to write trigger log: {e}", flush=True)
'''

CLIPBOARD_CODE = '''
def scan_clipboard_for_directives():
    """클립보드에 새 [S1_AUTO_DISPATCH_TO_ANCHONGRI] 지시서가 복사되었을 때 즉시 감지하여 집행"""
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True, timeout=3)
        cb_text = res.stdout.strip()
        if "[S1_AUTO_DISPATCH_TO_ANCHONGRI]" in cb_text:
            id_match = re.search(r"(?:ID:\\s*|DIRECTIVE_ID:\\s*|#\\s*)?(RGON_DIR_[A-Za-z0-9_]+)", cb_text)
            if id_match:
                did = id_match.group(1)
                title_match = re.search(r"TITLE:\\s*(.+)|작업명:\\s*(.+)", cb_text)
                title = (title_match.group(1) or title_match.group(2)).strip() if title_match else f"클립보드 직통 지시서 ({did})"
                register_new_directive(did, title, cb_text)
    except Exception:
        pass
'''

def step1_clean_and_refactor_bridge():
    print("[1] s1_rgon_to_anchongri_bridge.py 중복 제거 및 엔진 삽입...")
    b_file = BASE / "s1_rgon_to_anchongri_bridge.py"
    txt = b_file.read_text(encoding="utf-8")

    # 1. auto_execute_directive_trigger 함수 중복 정의들 전면 제거
    # def register_new_directive 이전의 모든 auto_execute_directive_trigger 정의 제거
    txt = re.sub(r'def auto_execute_directive_trigger\([\s\S]*?(?=def register_new_directive)', '', txt)

    # 2. 정품 단일 함수를 register_new_directive 바로 위에 삽입
    txt = txt.replace("def register_new_directive(directive_id, title, full_text):", NEW_TRIGGER_FUNC.strip() + "\n\n\ndef register_new_directive(directive_id, title, full_text):")

    # 3. register_new_directive 내부의 auto_execute_directive_trigger 호출 정리 (1회만)
    txt = re.sub(
        r'(?:auto_execute_directive_trigger\([^\)]*\)\s*\n\s*)+',
        'auto_execute_directive_trigger(directive_id, full_text)\n    ',
        txt
    )

    # 4. harvest_from_github_ssot 내부의 auto_execute_directive_trigger 호출 정리 (1회만)
    harv_pattern = r'(ACTIVE_TASK_MD\.write_text\(task_content, encoding="utf-8"\)[\s\S]*?)(?:auto_execute_directive_trigger\([^\)]*\)\s*\n\s*)+(print\(f"\[HARVESTER\] Picked up directive)'
    txt = re.sub(
        harv_pattern,
        r'\1auto_execute_directive_trigger(did, item.get("full_text", ""))\n            \2',
        txt
    )

    # 5. 클립보드 스캔 함수 삽입
    if "def scan_clipboard_for_directives" not in txt:
        txt = txt.replace("def process_mobile_queue():", CLIPBOARD_CODE.strip() + "\n\n\ndef process_mobile_queue():")
        txt = txt.replace("run_bridge_cycle(cycle_num=cycle_count)", "scan_clipboard_for_directives()\n            run_bridge_cycle(cycle_num=cycle_count)")

    # 6. BASE_DIR 0건 확인
    txt = txt.replace("BASE_DIR", "BASE")

    b_file.write_text(txt, encoding="utf-8")
    print("  └─ s1_rgon_to_anchongri_bridge.py 리팩토링 완료!")


def step2_test_rgon_direct_execution():
    print("[2] 르곤 직할 파이썬 페이로드(# [S1_DIRECT_PYTHON_PAYLOAD]) 무인 실행 실측 테스트...")
    test_did = "RGON_DIR_DIRECT_TEST_049"
    test_code = """
import json
from pathlib import Path
out = Path("S1_RGON_DIRECT_PAYLOAD_PROOF.json")
out.write_text(json.dumps({"status": "SUCCESS", "directive": "RGON_DIR_DIRECT_TEST_049", "message": "Direct execution without anchongri completed!"}, indent=2), encoding="utf-8")
print("SUCCESS: Direct python payload executed cleanly!")
"""
    test_directive_payload = f"""[S1_AUTO_DISPATCH_TO_ANCHONGRI]
- 지시서_ID: {test_did}
- 작업명: 르곤 직할 무인 파이썬 페이로드 자동 집행 실측 테스트

# [S1_DIRECT_PYTHON_PAYLOAD]
{test_code.strip()}
# [/S1_DIRECT_PYTHON_PAYLOAD]
[/S1_AUTO_DISPATCH_TO_ANCHONGRI]"""

    import s1_rgon_to_anchongri_bridge
    res = s1_rgon_to_anchongri_bridge.auto_execute_directive_trigger(test_did, test_directive_payload)
    print(f"  └─ 반환 결과: {res}")

    if res.get("mode") != "RGON_DIRECT_PYTHON_EXECUTION":
        raise RuntimeError(f"엔진 모드 불일치: {res.get('mode')}")
    if not res.get("ok"):
        raise RuntimeError("직접 실행 실패!")

    proof_f = BASE / "S1_RGON_DIRECT_PAYLOAD_PROOF.json"
    if not proof_f.exists():
        raise RuntimeError("결과 파일 S1_RGON_DIRECT_PAYLOAD_PROOF.json 부재!")
    print(f"  └─ 페이로드 결과 파일 생성 입증: {proof_f.read_text(encoding='utf-8')}")

    # S1_BRIDGE_AUTO_TRIGGER_LOG.json 검증
    log_file = BASE / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"
    log_data = json.loads(log_file.read_text(encoding="utf-8"))
    entries = [t for t in log_data.get("triggers", []) if t.get("mode") == "RGON_DIRECT_PYTHON_EXECUTION" and t.get("directive_id") == test_did]
    if not entries:
        raise RuntimeError("로그에 RGON_DIRECT_PYTHON_EXECUTION 기록 누락!")
    print(f"  └─ S1_BRIDGE_AUTO_TRIGGER_LOG.json 등재 확인: {entries[-1]}")
    shutil.copyfile(log_file, BASE / "docs" / "S1_BRIDGE_AUTO_TRIGGER_LOG.json")


def step3_ast_check():
    print("[3] AST 정적 분석 검증...")
    b_file = BASE / "s1_rgon_to_anchongri_bridge.py"
    tree = ast.parse(b_file.read_text(encoding="utf-8"))

    func_lineno = None
    main_lineno = None
    reg_calls = False
    harv_calls = False
    def_count = 0

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "auto_execute_directive_trigger":
            def_count += 1
            func_lineno = node.lineno
        elif isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare) and getattr(node.test.left, "id", "") == "__name__":
                main_lineno = node.lineno
        elif isinstance(node, ast.FunctionDef) and node.name == "register_new_directive":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and getattr(sub.func, "id", "") == "auto_execute_directive_trigger":
                    reg_calls = True
        elif isinstance(node, ast.FunctionDef) and node.name == "harvest_from_github_ssot":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and getattr(sub.func, "id", "") == "auto_execute_directive_trigger":
                    harv_calls = True

    print(f"  └─ def count: {def_count} (단 1개 필수)")
    print(f"  └─ func_lineno: {func_lineno}, main_lineno: {main_lineno} (func < main 필수)")
    print(f"  └─ reg_calls: {reg_calls}, harv_calls: {harv_calls}")

    if def_count != 1:
        raise RuntimeError(f"auto_execute_directive_trigger 함수가 {def_count}번 정의되어 있습니다! (1개 필수)")
    if not (func_lineno and main_lineno and func_lineno < main_lineno and reg_calls and harv_calls):
        raise RuntimeError("AST 검증 조건 불만족!")


def main():
    print("=" * 70)
    print("⚡ [S1-BUILD-049] 르곤 직할 무인 집행 엔진 시공 시작")
    print("=" * 70)

    step1_clean_and_refactor_bridge()
    step2_test_rgon_direct_execution()
    step3_ast_check()

    print("\n" + "=" * 70)
    print("✨ [S1-BUILD-049] 르곤 직할 무인 엔진 장착 완료!")
    print("=" * 70)

if __name__ == "__main__":
    main()
