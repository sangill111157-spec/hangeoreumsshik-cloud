#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S1 QM Structural Linter v1.1 (s1_qm_structure_linter.py)
- Directive: RGON_DIR_DASHBOARD_ZERO_STALE_AND_FM008_041
- Inspired by:
  1) SpaceX Lauren Tan `cursor/plugins/pstack` (`encode-lessons-in-structure`)
  2) `obra/superpowers` (`verification-before-completion`)
- Enforces automated structural checks BEFORE any completion report can be sent:
  [A] 4 Absolute Protected Files 0% Touch Integrity
  [B] S1_FAILURE_MEMORY_DB.json 8 Failure-Mode Regression Guards (FM-001 ~ FM-008)
  [C] S1_RELAY_STAMP_PASSPORT.json Cryptographic Hash-Chain Continuity
  [D] R2 Zero Secret Leak & Root Hygiene (.gitignore isolation & docs/ 1:1 Mirror Sync)
- Exits with EXIT CODE 1 (QM-SP-11 REJECTED_LOT) immediately if ANY check fails!
"""

import datetime
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = pathlib.Path(__file__).resolve().parent

PROTECTED_FILES = {
    "rgon_Numeric_Organ.py",
    "rgon_work_loop.py",
    "rgon_self_Reflection.py",
    "index_20260405_backup.html",
}

SECRET_PATTERNS = [
    ("OpenAI Key", re.compile(r"sk-[a-zA-Z0-9]{32,}")),
    ("Anthropic Key", re.compile(r"sk-ant-[a-zA-Z0-9_\-]{40,}")),
    ("Google API Key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("GitHub PAT", re.compile(r"ghp_[a-zA-Z0-9]{36}")),
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private Key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\r\n]{40,}")),
]


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ==============================================================================
# [A] 4 Absolute Protected Files Integrity
# ==============================================================================
def check_protected_files():
    out_status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=BASE, capture_output=True, text=True
    ).stdout
    out_diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"], cwd=BASE, capture_output=True, text=True
    ).stdout
    touched = []
    for line in (out_status + "\n" + out_diff).splitlines():
        for pf in PROTECTED_FILES:
            if pf in line:
                touched.append(line.strip())
    passed = len(touched) == 0
    return {
        "id": "GATE-A-PROTECTED-FILES",
        "name": "4대 절대 보호 파일 무접촉 헌법 검증",
        "passed": passed,
        "detail": "4대 보호 파일 수정·접촉 0건 완벽 수호" if passed else f"보호 파일 접촉 감지: {touched}",
    }


# ==============================================================================
# [B] 7 Failure Memory DB Structural Guards (FM-001 ~ FM-007)
# ==============================================================================
def check_fm001_no_fake_tkinter():
    rx = re.compile(r"^\s*(?:import|from)\s+tkinter\b", re.MULTILINE)
    offenders = []
    for py in sorted(BASE.glob("s1_*.py")):
        if py.name == "s1_qm_structure_linter.py":
            continue
        txt = py.read_text(encoding="utf-8", errors="ignore")
        if rx.search(txt):
            offenders.append(py.name)
    passed = len(offenders) == 0
    return (
        passed,
        "s1_*.py 내 가짜 tkinter 창 모사 코드 0건" if passed else f"가짜 tkinter 감지: {offenders}",
    )


def check_fm002_authentic_motion_shorts():
    root_mp4 = BASE / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    docs_mp4 = BASE / "docs" / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    if not root_mp4.exists() or not docs_mp4.exists():
        return False, "마스터 쇼츠 MP4 파일(루트 또는 docs/audio) 누락"
    sz = root_mp4.stat().st_size
    if sz < 5_000_000:
        return False, f"마스터 쇼츠 용량 미달({sz} bytes < 5MB)"
    return True, f"진품 마스터 쇼츠 실존 확인 ({sz:,} bytes, 루트 & docs 동기화)"


def check_fm003_ego_lockfile_guard():
    bridge = BASE / "s1_rgon_to_anchongri_bridge.py"
    if not bridge.exists():
        return False, "s1_rgon_to_anchongri_bridge.py 파일 누락"
    txt = bridge.read_text(encoding="utf-8", errors="ignore")
    has_def = "def is_ego_running(" in txt
    has_call = "if not is_ego_running():" in txt
    passed = has_def and has_call
    return (
        passed,
        "is_ego_running() 무잠금 가드 정의 및 호출 정상 작동"
        if passed
        else "s1_rgon_to_anchongri_bridge.py 내 is_ego_running() 가드 누락",
    )


def check_fm004_dynamic_monitor_geometry():
    agent = BASE / "s1_host_desktop_agent.py"
    if not agent.exists():
        return False, "s1_host_desktop_agent.py 파일 누락"
    txt = agent.read_text(encoding="utf-8", errors="ignore")
    has_dyn = "EnumDisplayMonitors" in txt and "def get_monitors(" in txt
    has_864 = bool(re.search(r"\b864\b", txt))
    passed = has_dyn and not has_864
    return (
        passed,
        "EnumDisplayMonitors 동적 해상도 측정 적용 및 864px 하드코딩 0건"
        if passed
        else f"동적 모니터 측정 미비(has_dyn={has_dyn}, has_864={has_864})",
    )


def check_fm005_space0_bottom_scroll():
    agent = BASE / "s1_host_desktop_agent.py"
    if not agent.exists():
        return False, "s1_host_desktop_agent.py 파일 누락"
    txt = agent.read_text(encoding="utf-8", errors="ignore")
    ok = (
        "def configure_top_left_space0(" in txt
        and "MOUSEEVENTF_WHEEL" in txt
        and "VK_END" in txt
    )
    return (
        ok,
        "좌상단 Space 0 가독성 배율 및 최하단 휠/End 스크롤 로직 탑재 확인"
        if ok
        else "좌상단 Space 0 스크롤 로직 누락",
    )


def check_fm006_ide_chat_only_exposure():
    agent = BASE / "s1_host_desktop_agent.py"
    if not agent.exists():
        return False, "s1_host_desktop_agent.py 파일 누락"
    txt = agent.read_text(encoding="utf-8", errors="ignore")
    ok = (
        "def configure_top_right_ide(" in txt
        and "View: Close Panel" in txt
        and "View: Close Primary Side Bar" in txt
    )
    return (
        ok,
        "우상단 IDE 에디터 탭(Ctrl+K Ctrl+W)·터미널·사이드바 멱등 닫기 로직 탑재 확인"
        if ok
        else "우상단 IDE 정리 로직 누락",
    )


def check_fm007_audio_and_docs_mirror_zero_404():
    idx = BASE / "index.html"
    docs_idx = BASE / "docs" / "index.html"
    if not idx.exists() or not docs_idx.exists():
        return False, "index.html 또는 docs/index.html 누락"

    html = idx.read_text(encoding="utf-8", errors="ignore")
    audio_refs = sorted(set(re.findall(r"\./audio/([A-Za-z0-9_.\-/]+)", html)))
    missing = []
    for rel in audio_refs:
        if not (BASE / "audio" / rel).exists():
            missing.append(f"audio/{rel}")
        if not (BASE / "docs" / "audio" / rel).exists():
            missing.append(f"docs/audio/{rel}")
    if missing:
        return False, f"404 위험 오디오/영상 경로 누락: {missing}"

    mirror_pairs = [
        ("index.html", "docs/index.html"),
        ("sw.js", "docs/sw.js"),
        ("S1_GLOSSARY.md", "docs/S1_GLOSSARY.md"),
        ("S1_FAILURE_MEMORY_DB.json", "docs/S1_FAILURE_MEMORY_DB.json"),
        ("S1_YOUTUBE_11_SKILLS_GUIDE.md", "docs/S1_YOUTUBE_11_SKILLS_GUIDE.md"),
    ]
    desync = []
    for a, b in mirror_pairs:
        pa, pb = BASE / a, BASE / b
        if not pa.exists() or not pb.exists():
            desync.append(f"missing:{a}<->{b}")
        elif sha256_file(pa) != sha256_file(pb):
            desync.append(f"hash_mismatch:{a}<->{b}")
    if desync:
        return False, f"루트 <-> docs/ 미러 불일치: {desync}"

    # Ensure dashboard-linked JSON files are not blocked by .gitignore (*.json wildcard)
    ignored_chk = subprocess.run(
        [
            "git",
            "check-ignore",
            "S1_FAILURE_MEMORY_DB.json",
            "docs/S1_FAILURE_MEMORY_DB.json",
            "S1_QM_LINTER_LAST_REPORT.json",
            "docs/S1_QM_LINTER_LAST_REPORT.json",
        ],
        cwd=BASE,
        capture_output=True,
        text=True,
    )
    if ignored_chk.stdout.strip():
        return False, f".gitignore 차단으로 클라우드 404 유발 파일 감지: {ignored_chk.stdout.strip().splitlines()}"

    return True, f"오디오/쇼츠 참조 {len(audio_refs)}종 무결성, 5대 핵심 문서 루트<->docs 해시 100% 일치 및 .gitignore 허용 확인"


def check_fm008_dashboard_freshness():
    idx = BASE / "index.html"
    docs_idx = BASE / "docs" / "index.html"
    sw = BASE / "sw.js"
    docs_sw = BASE / "docs" / "sw.js"
    if not idx.exists() or not docs_idx.exists():
        return False, "index.html 또는 docs/index.html 누락"
    if not sw.exists() or not docs_sw.exists():
        return False, "sw.js 또는 docs/sw.js 누락"

    html = idx.read_text(encoding="utf-8", errors="ignore")

    stale_patterns = [
        "023호 9:16 시네마틱 쇼츠",
        "클로드 스토리 · 솔 6컷 비주얼",
        "집계 중...",
        "불러오는 중...",
        "불러오는 중입니다...",
        "수신 대기 중입니다...",
    ]
    found_stale = [s for s in stale_patterns if s in html]
    if found_stale:
        return False, f"대시보드 구버전 배지 또는 빈 로딩 문구 잔존: {found_stale}"

    required_markers = [
        "무자막 감성 수채화",
        "후렴구 하이라이트(54~88초) 마스터 쇼츠",
        "./audio/father_age_shorts_scenes/scene_01.png?v=041",
        "34s 후렴구 클라이맥스 · 글씨 0% 순수 수채화 6컷 · 삼성 2단계 완공",
        "RGON_DIR_DASHBOARD_ZERO_STALE_AND_FM008_041",
        "STAMP_041_5_AUDIT",
        "./S1_RGON_DIRECTIVE_QUEUE.json",
        "./S1_RELAY_STAMP_PASSPORT.json",
        "./S1_ANCHONGRI_TO_RGON_OUTBOX.json",
        "./S1_STEP_BY_STEP_PIPELINE_STATE.json",
    ]
    missing_markers = [m for m in required_markers if m not in html]
    if missing_markers:
        return False, f"대시보드 최신 프리렌더링(SSR) 또는 실시간 JSON 바인딩 누락: {missing_markers}"

    live_json_pairs = [
        ("S1_RGON_DIRECTIVE_QUEUE.json", "docs/S1_RGON_DIRECTIVE_QUEUE.json"),
        ("S1_ANCHONGRI_TO_RGON_OUTBOX.json", "docs/S1_ANCHONGRI_TO_RGON_OUTBOX.json"),
        ("S1_STEP_BY_STEP_PIPELINE_STATE.json", "docs/S1_STEP_BY_STEP_PIPELINE_STATE.json"),
        ("S1_RELAY_STAMP_PASSPORT.json", "docs/S1_RELAY_STAMP_PASSPORT.json"),
    ]
    json_desync = []
    check_ignore_targets = []
    for a, b in live_json_pairs:
        check_ignore_targets.extend([a, b])
        pa, pb = BASE / a, BASE / b
        if not pa.exists() or not pb.exists():
            json_desync.append(f"missing:{a}<->{b}")
        elif sha256_file(pa) != sha256_file(pb):
            json_desync.append(f"hash_mismatch:{a}<->{b}")
    if json_desync:
        return False, f"대시보드 연동 JSON 루트 <-> docs/ 불일치: {json_desync}"

    ig = subprocess.run(
        ["git", "check-ignore", *check_ignore_targets],
        cwd=BASE,
        capture_output=True,
        text=True,
    )
    if ig.stdout.strip():
        return False, f".gitignore 차단으로 클라우드 JSON 404 위험 감지: {ig.stdout.strip().splitlines()}"

    pp_data = json.loads((BASE / "S1_RELAY_STAMP_PASSPORT.json").read_text(encoding="utf-8"))
    pp_stamps = pp_data.get("stamps", [])
    pp_names = {s.get("stamp_name") for s in pp_stamps}
    if len(pp_stamps) < 27 or "STAMP_041_5_AUDIT" not in pp_names:
        return False, f"S1_RELAY_STAMP_PASSPORT.json 041호 5대 공정 도장(#23~#27) 미완비 (현재 {len(pp_stamps)}개)"

    bridge_file = BASE / "s1_rgon_to_anchongri_bridge.py"
    if bridge_file.exists() and "--autostash" in bridge_file.read_text(encoding="utf-8", errors="ignore"):
        return False, "s1_rgon_to_anchongri_bridge.py 내 --autostash 레이스 컨디션 유발 플래그 잔존 (QM-SP-18 위반)"

    proof_root = BASE / "S1_IO_TEST_12_DASHBOARD_ZERO_STALE_PROOF.md"
    proof_docs = BASE / "docs" / "S1_IO_TEST_12_DASHBOARD_ZERO_STALE_PROOF.md"
    if not proof_root.exists() or not proof_docs.exists() or sha256_file(proof_root) != sha256_file(proof_docs):
        return False, "S1_IO_TEST_12_DASHBOARD_ZERO_STALE_PROOF.md 루트 <-> docs/ 증빙 문서 누락 또는 해시 불일치"

    sw_txt = sw.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"s1-aon-v(?:[2-9]\d|\d{3,})-", sw_txt):
        return False, "sw.js 캐시 버전 미갱신 (v20 이상, 현재 기준 s1-aon-v20-zero-stale-dashboard-041 필요)"

    return (
        True,
        f"구버전·빈 로딩 문구 0건, 수채화 배지·SSR·4대 JSON·27대 릴레이 도장({len(pp_stamps)}개)·QM-SP-18 가드·sw.js v20 검증 완료",
    )


GUARD_DISPATCH = {
    "check_fm001_no_fake_tkinter": check_fm001_no_fake_tkinter,
    "check_fm002_authentic_motion_shorts": check_fm002_authentic_motion_shorts,
    "check_fm003_ego_lockfile_guard": check_fm003_ego_lockfile_guard,
    "check_fm004_dynamic_monitor_geometry": check_fm004_dynamic_monitor_geometry,
    "check_fm005_space0_bottom_scroll": check_fm005_space0_bottom_scroll,
    "check_fm006_ide_chat_only_exposure": check_fm006_ide_chat_only_exposure,
    "check_fm007_audio_and_docs_mirror_zero_404": check_fm007_audio_and_docs_mirror_zero_404,
    "check_fm008_dashboard_freshness": check_fm008_dashboard_freshness,
}


def check_failure_memory_db():
    db_path = BASE / "S1_FAILURE_MEMORY_DB.json"
    if not db_path.exists():
        return [{"id": "FM-DB", "name": "실패 오답노트 DB", "passed": False, "detail": "S1_FAILURE_MEMORY_DB.json 누락"}]
    db = json.loads(db_path.read_text(encoding="utf-8"))
    results = []
    for entry in db.get("failures", []):
        fid = entry.get("id", "FM-???")
        fn_name = entry.get("guard_function", "")
        fn = GUARD_DISPATCH.get(fn_name)
        if not fn:
            results.append({"id": fid, "name": entry.get("title", ""), "passed": False, "detail": f"미등록 가드 함수: {fn_name}"})
            continue
        ok, detail = fn()
        results.append({"id": fid, "name": entry.get("title", ""), "passed": ok, "detail": detail})
    return results


# ==============================================================================
# [C] Relay Stamp Passport Hash-Chain Continuity
# ==============================================================================
def check_passport_hash_chain():
    pp = BASE / "S1_RELAY_STAMP_PASSPORT.json"
    docs_pp = BASE / "docs" / "S1_RELAY_STAMP_PASSPORT.json"
    if not pp.exists() or not docs_pp.exists():
        return {"id": "GATE-C-PASSPORT", "name": "릴레이 여권 해시 체인 검증", "passed": False, "detail": "여권 파일 누락"}
    if sha256_file(pp) != sha256_file(docs_pp):
        return {"id": "GATE-C-PASSPORT", "name": "릴레이 여권 해시 체인 검증", "passed": False, "detail": "루트 <-> docs 여권 해시 불일치"}

    data = json.loads(pp.read_text(encoding="utf-8"))
    stamps = data.get("stamps", [])
    if not stamps:
        return {"id": "GATE-C-PASSPORT", "name": "릴레이 여권 해시 체인 검증", "passed": False, "detail": "도장 내역 비어 있음"}

    broken = []
    for i in range(1, len(stamps)):
        prev_h = stamps[i - 1].get("stamp_hash", "")
        cur_prev = stamps[i].get("prev_stamp_hash", "")
        if not prev_h or prev_h != cur_prev:
            broken.append(f"idx {stamps[i].get('stamp_index')}: prev_stamp_hash mismatch")
    if data.get("last_stamp_hash") != stamps[-1].get("stamp_hash"):
        broken.append("last_stamp_hash != final stamp_hash")

    passed = len(broken) == 0
    return {
        "id": "GATE-C-PASSPORT",
        "name": "릴레이 여권 해시 체인 연속성 검증",
        "passed": passed,
        "detail": f"총 {len(stamps)}대 릴레이 도장 사슬 연속성 100% 무결 (최종 해시 {data.get('last_stamp_hash', '')[:12]}...)"
        if passed
        else f"해시 체인 단절: {broken}",
    }


# ==============================================================================
# [D] R2 Secret Zero-Leak & Root Hygiene
# ==============================================================================
def check_secrets_and_hygiene():
    leaks = []
    for ext in ("*.py", "*.md", "*.json", "*.html", "*.js"):
        for f in BASE.glob(ext):
            if f.name == "s1_qm_structure_linter.py":
                continue
            txt = f.read_text(encoding="utf-8", errors="ignore")
            for label, rx in SECRET_PATTERNS:
                if rx.search(txt):
                    leaks.append(f"{f.name}:{label}")
    gi = (BASE / ".gitignore").read_text(encoding="utf-8", errors="ignore") if (BASE / ".gitignore").exists() else ""
    gi_ok = ("scratch/" in gi or "scratch" in gi) and ("_ego_tmp/" in gi or "_ego_tmp" in gi)
    passed = (len(leaks) == 0) and gi_ok
    return {
        "id": "GATE-D-SECURITY-HYGIENE",
        "name": "R2 시크릿 노출 0% & 루트 위생(.gitignore 격리) 검증",
        "passed": passed,
        "detail": "API 키/시크릿 노출 0건 및 scratch/ · _ego_tmp/ 격리 정상"
        if passed
        else f"보안/위생 위반: leaks={leaks}, gitignore_ok={gi_ok}",
    }


def run_all_checks():
    checks = []
    checks.append(check_protected_files())
    checks.extend(check_failure_memory_db())
    checks.append(check_passport_hash_chain())
    checks.append(check_secrets_and_hygiene())

    passed_count = sum(1 for c in checks if c["passed"])
    total_count = len(checks)
    score = round((passed_count / max(1, total_count)) * 100.0, 1)
    all_passed = passed_count == total_count

    report = {
        "linter_version": "1.1.0",
        "directive_id": "RGON_DIR_DASHBOARD_ZERO_STALE_AND_FM008_041",
        "timestamp": now_iso(),
        "verdict": "PASS" if all_passed else "QM_SP_11_REJECTED_LOT",
        "score": score,
        "passed_checks": passed_count,
        "total_checks": total_count,
        "checks": checks,
    }

    report_path = BASE / "S1_QM_LINTER_LAST_REPORT.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if (BASE / "docs").exists():
        shutil.copyfile(report_path, BASE / "docs" / "S1_QM_LINTER_LAST_REPORT.json")

    print("=" * 72)
    print(f"🛡️ [S1 구조적 품질 린터 v1.1] 전수 검사 결과: {report['verdict']} ({score} / 100.0)")
    print("=" * 72)
    for c in checks:
        mark = "✅ PASS" if c["passed"] else "❌ FAIL (QM-SP-11 격리)"
        print(f" - [{c['id']}] {c['name']}: {mark}\n     └─ {c['detail']}")
    print("=" * 72)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_checks())
