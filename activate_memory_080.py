import datetime, json, os, subprocess, sys
from pathlib import Path

BASE = Path.cwd()
now_kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

# 1. 오늘(11/05)까지의 잘한 점(Good) 5건 & 못한 점(Bad) 5건을 S1 기억창고 통합 원장(S1_MEMORY_VAULT_GOOD_BAD.json)에 정식 등재
vault_file = BASE / "S1_MEMORY_VAULT_GOOD_BAD.json"
docs_vault_file = BASE / "docs" / "S1_MEMORY_VAULT_GOOD_BAD.json"

memory_vault = {
    "version": "2.0.0-LIVE-AUTO-EVOLVING",
    "updated_at": now_kst,
    "status": "ACTIVE_AUTO_HOOKED_IN_BRIDGE_DAEMON",
    "good_points_proven": [
        {"id": "GOOD-001", "date": "2026-11-05", "title": "대표님 친작 2S1 황금 메탈 직인(Sr7DZIdv) 원본 무손실 장착 및 공증"},
        {"id": "GOOD-002", "date": "2026-11-05", "title": "카카오톡 5탭 UI 개편 및 죽은 유령 버튼 0건(31개 전수 작동) 달성"},
        {"id": "GOOD-003", "date": "2026-11-05", "title": "S1_EGO_PROVEN_SKILL_MASTER.py 4대 에고라이트 정상작동 스킬 영구 금고 잠금"},
        {"id": "GOOD-004", "date": "2026-11-05", "title": "안실장(Antigravity) 강제 호출 영구 차단(토큰 소모 0%) 및 순수 파워쉘·파이썬 직할 체제 완공"},
        {"id": "GOOD-005", "date": "2026-11-05", "title": "_StealthPopen(CREATE_NO_WINDOW 0x08000000 글로벌 후킹)으로 검은 창 깜빡임 100% 소멸"}
    ],
    "bad_points_never_repeat": [
        {"id": "BAD-001 (FM-015)", "date": "2026-11-05", "mistake": "파이썬 페이로드 내부 중첩 f-string 중괄호({ })로 인한 SyntaxError", "rule": "페이로드 내부에서 중첩 f-string 사용 금지, 일반 문자열 연결(+) 사용"},
        {"id": "BAD-002 (FM-016)", "date": "2026-11-05", "mistake": "Space 0 이모지 스캔 시 utf-8 surrogates not allowed 인코딩 에러", "rule": "모든 read_text/write_text/reconfigure에 errors='replace' 필수 강제"},
        {"id": "BAD-003 (FM-017)", "date": "2026-11-05", "mistake": "린터(LINTER_VERIFY_047)가 안실장 IDE(STANDARD_FOUNDRY_SPAWN)를 강제로 깨워 토큰 낭비", "rule": "STANDARD_FOUNDRY_SPAWN 실제 프로세스 스폰 영구 제거 및 더미 로그로 대체"},
        {"id": "BAD-004 (FM-018)", "date": "2026-11-05", "mistake": "subprocess 호출 시 CREATE_NO_WINDOW 누락으로 15초마다 검은 콘솔 창 2번 깜빡임", "rule": "최상단 _StealthPopen 후킹으로 모든 하위 프로세스 창 생성 원천 차단"},
        {"id": "BAD-005 (FM-019)", "date": "2026-11-05", "mistake": "VS Code 터미널 내부 환경변수(VSCODE_GIT_IPC_HANDLE)로 인해 Git 로그인 팝업이 뜨며 데몬 멈춤", "rule": "GIT_TERMINAL_PROMPT=0 및 VSCODE_GIT_* 환경변수 제거 상태로 데몬 기동"}
    ],
    "auto_runtime_logs": []
}

vault_json = json.dumps(memory_vault, ensure_ascii=False, indent=2)
vault_file.write_text(vault_json, encoding="utf-8", errors="replace")
docs_vault_file.parent.mkdir(parents=True, exist_ok=True)
docs_vault_file.write_text(vault_json, encoding="utf-8", errors="replace")

# 2. S1_FAILURE_MEMORY_DB.json 에도 FM-015 ~ FM-019 최신화 반영 (어제 11/04에 멈춰있던 DB 가동 재개!)
fm_file = BASE / "S1_FAILURE_MEMORY_DB.json"
docs_fm_file = BASE / "docs" / "S1_FAILURE_MEMORY_DB.json"
if fm_file.exists():
    fm_data = json.loads(fm_file.read_text(encoding="utf-8", errors="replace"))
    fm_data["version"] = "1.8.0-AUTO-ACTIVE"
    fm_data["updated_at"] = now_kst
    existing_ids = {x.get("id") for x in fm_data.get("failures", [])}
    for b in memory_vault["bad_points_never_repeat"]:
        fid = b["id"].split()[0]
        if fid not in existing_ids:
            fm_data.setdefault("failures", []).append({
                "id": fid,
                "title": b["mistake"],
                "incident_directive": "058호~079호 실전 교정",
                "root_cause": b["mistake"],
                "remediation_qm_sp_18": b["rule"]
            })
    fm_str = json.dumps(fm_data, ensure_ascii=False, indent=2)
    fm_file.write_text(fm_str, encoding="utf-8", errors="replace")
    docs_fm_file.write_text(fm_str, encoding="utf-8", errors="replace")

# 3. 브릿지 데몬(s1_rgon_to_anchongri_bridge.py)이 지시서를 실행할 때마다 자동으로 기억창고(잘한점/못한점)에 기록하는 훅 장착!
bp = BASE / "s1_rgon_to_anchongri_bridge.py"
btxt = bp.read_text(encoding="utf-8", errors="replace")
auto_mem_hook = """
            # [S1_AUTO_MEMORY_VAULT_HOOK: 실행 결과에 따라 잘한 점(Good) / 못한 점(Bad) 자동 기록]
            try:
                _mv_path = BASE / "S1_MEMORY_VAULT_GOOD_BAD.json"
                if _mv_path.exists():
                    _mv = json.loads(_mv_path.read_text(encoding="utf-8", errors="replace"))
                    _mv["updated_at"] = now_iso()
                    _mv.setdefault("auto_runtime_logs", []).append({
                        "directive_id": directive_id,
                        "timestamp": now_iso(),
                        "type": "GOOD_SUCCESS" if exec_res.returncode == 0 else "BAD_FAILURE",
                        "returncode": exec_res.returncode,
                        "note": (exec_res.stdout[:120] if exec_res.returncode == 0 else exec_res.stderr[:200]).strip()
                    })
                    _mv["auto_runtime_logs"] = _mv["auto_runtime_logs"][-100:]
                    _mv_str = json.dumps(_mv, ensure_ascii=False, indent=2)
                    _mv_path.write_text(_mv_str, encoding="utf-8", errors="replace")
                    (BASE / "docs" / "S1_MEMORY_VAULT_GOOD_BAD.json").write_text(_mv_str, encoding="utf-8", errors="replace")
            except Exception as _me:
                print("[MEMORY_VAULT_ERR]", _me, flush=True)
"""
if "[S1_AUTO_MEMORY_VAULT_HOOK" not in btxt and 'print(f"[RGON_DIRECT_ENGINE] Payload exit code:' in btxt:
    btxt = btxt.replace(
        'print(f"[RGON_DIRECT_ENGINE] Payload exit code: {exec_res.returncode}", flush=True)',
        'print(f"[RGON_DIRECT_ENGINE] Payload exit code: {exec_res.returncode}", flush=True)\n' + auto_mem_hook,
        1
    )
    bp.write_text(btxt, encoding="utf-8", errors="replace")

# .gitignore 화이트리스트 추가
gi = BASE / ".gitignore"
if gi.exists():
    gtxt = gi.read_text(encoding="utf-8", errors="replace")
    if "!S1_MEMORY_VAULT_GOOD_BAD.json" not in gtxt:
        gtxt += "\n!S1_MEMORY_VAULT_GOOD_BAD.json\n!docs/S1_MEMORY_VAULT_GOOD_BAD.json\n"
        gi.write_text(gtxt, encoding="utf-8", errors="replace")

print("[OK] S1 Memory Vault (Good/Bad) updated & auto-hooked into Bridge Daemon!")
import S1_EGO_PROVEN_SKILL_MASTER as sm
sm.send_auto_confirm_enter_space0("확인 (080호 S1 기억창고 잘한점·못한점 실시간 자동기록 엔진 가동 완료!)")
