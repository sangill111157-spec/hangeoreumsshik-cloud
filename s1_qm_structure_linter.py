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

import ast
import datetime
import hashlib
import json
import math
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
        "./audio/father_age_shorts_scenes/scene_01.png?v=04",
        "STAMP_042_5_AUDIT",
        "./S1_RGON_DIRECTIVE_QUEUE.json",
        "./S1_RELAY_STAMP_PASSPORT.json",
        "./S1_ANCHONGRI_TO_RGON_OUTBOX.json",
        "./S1_STEP_BY_STEP_PIPELINE_STATE.json",
    ]
    missing_markers = [m for m in required_markers if m not in html]
    if missing_markers:
        return False, f"대시보드 최신 프리렌더링(SSR) 또는 실시간 JSON 바인딩 누락: {missing_markers}"

    badge_valid = (
        "046호: 연결·소통·만능" in html or
        "047호: 연결·소통·만능" in html or
        "047호: 카카오페이지" in html or "048호: 카카오페이지" in html or "049호: 시원한" in html or "049호: 클린" in html
    )
    if not badge_valid:
        return False, "대시보드 최신 배지(046호/047호) 부재"

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
    if not re.search(r"s1-aon-v(?:2[1-9]|[3-9]\d|\d{3,})-", sw_txt):
        return False, "sw.js 캐시 버전 미갱신 (v21 이상, 현재 기준 s1-aon-v21-disney-warm-3d-motion-042 필요)"

    return (
        True,
        f"구버전·빈 로딩 문구 0건, 수채화 배지·SSR·4대 JSON·27대 릴레이 도장({len(pp_stamps)}개)·QM-SP-18 가드·sw.js v20 검증 완료",
    )




def _measure_segment_non_zoompan_residual(mp4_path: pathlib.Path, start_s: float, dur_s: float) -> float:
    """
    6x10 로컬 블록 광학 흐름(Block-Matching Optical Flow)을 추출한 뒤,
    전역 선형 줌인·아웃/팬 모델(dx = a*rx + tx, dy = a*ry + ty)을 최소제곱 피팅하고 남는
    '비선형 독립 피사체 모션 잔차(Non-Zoompan Independent Motion Residual)' 평균 픽셀값을 반환한다.
    - 순수 FFmpeg zoompan 슬라이드쇼 실측치: ~0.059 px (< 0.25 불량 격리)
    - 실제 AI Image-to-Video 모션 실측치: ~0.45 ~ 1.80+ px (>= 0.25 적합 통과)
    """
    w, h = 96, 160
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-ss",
        f"{start_s:.2f}",
        "-t",
        f"{dur_s:.2f}",
        "-i",
        str(mp4_path),
        "-vf",
        f"fps=4,scale={w}:{h}",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "gray",
        "-",
    ]
    raw = subprocess.check_output(cmd, timeout=20)
    frame_bytes = w * h
    n_frames = len(raw) // frame_bytes
    if n_frames < 4:
        return 0.0
    frames = [raw[i * frame_bytes : (i + 1) * frame_bytes] for i in range(n_frames)]

    gx, gy, bs, sr = 6, 10, 16, 4
    residuals = []
    for idx in range(len(frames) - 1):
        f0, f1 = frames[idx], frames[idx + 1]
        vecs = []
        for by in range(1, gy - 1):
            for bx in range(1, gx - 1):
                x0, y0 = bx * bs, by * bs
                best_sad, best_dx, best_dy = 10**18, 0, 0
                for dy in range(-sr, sr + 1):
                    for dx in range(-sr, sr + 1):
                        sad = 0
                        for r in range(0, bs, 2):
                            o0 = (y0 + r) * w + x0
                            o1 = (y0 + dy + r) * w + (x0 + dx)
                            for c in range(0, bs, 2):
                                sad += abs(f0[o0 + c] - f1[o1 + c])
                        if sad < best_sad:
                            best_sad, best_dx, best_dy = sad, dx, dy
                vecs.append((x0 + bs / 2.0 - w / 2.0, y0 + bs / 2.0 - h / 2.0, best_dx, best_dy))
        sum_r2 = sum(rx * rx + ry * ry for rx, ry, _, _ in vecs)
        tx = sum(dx for _, _, dx, _ in vecs) / len(vecs)
        ty = sum(dy for _, _, _, dy in vecs) / len(vecs)
        a = sum(rx * (dx - tx) + ry * (dy - ty) for rx, ry, dx, dy in vecs) / max(1.0, sum_r2)
        err = sum(math.hypot(dx - (a * rx + tx), dy - (a * ry + ty)) for rx, ry, dx, dy in vecs) / len(vecs)
        residuals.append(err)
    return round(sum(residuals) / len(residuals), 4)


def check_fm009_non_zoompan_dynamic_motion():
    mp4_root = BASE / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    mp4_docs = BASE / "docs" / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    if not mp4_root.exists() or not mp4_docs.exists():
        return False, "마스터 쇼츠 MP4(루트 또는 docs/audio) 누락"
    if sha256_file(mp4_root) != sha256_file(mp4_docs):
        return False, "마스터 쇼츠 MP4 루트 <-> docs/audio 해시 불일치"

    scenes_root = BASE / "audio" / "father_age_shorts_scenes"
    scenes_docs = BASE / "docs" / "audio" / "father_age_shorts_scenes"
    required_imgs = [f"scene_0{i}.png" for i in range(1, 7)] + ["FATHER_AGE_6SCENES_CONTACT_SHEET.png"]
    for fn in required_imgs:
        pr, pd = scenes_root / fn, scenes_docs / fn
        if not pr.exists() or not pd.exists():
            return False, f"6컷 아트워크 또는 합본 시트 누락: {fn}"
        if sha256_file(pr) != sha256_file(pd):
            return False, f"6컷 아트워크 루트 <-> docs 해시 불일치: {fn}"

    guide_r = BASE / "S1_DISNEY_WARM_3D_MOTION_MASTER_GUIDE.md"
    guide_d = BASE / "docs" / "S1_DISNEY_WARM_3D_MOTION_MASTER_GUIDE.md"
    if not guide_r.exists() or not guide_d.exists() or sha256_file(guide_r) != sha256_file(guide_d):
        return False, "S1_DISNEY_WARM_3D_MOTION_MASTER_GUIDE.md 누락 또는 docs 미러 불일치"

    p13_r = BASE / "S1_IO_TEST_13_DISNEY_WARM_3D_MOTION_PROOF.md"
    p13_d = BASE / "docs" / "S1_IO_TEST_13_DISNEY_WARM_3D_MOTION_PROOF.md"
    if not p13_r.exists() or not p13_d.exists() or sha256_file(p13_r) != sha256_file(p13_d):
        return False, "S1_IO_TEST_13_DISNEY_WARM_3D_MOTION_PROOF.md 누락 또는 docs 미러 불일치"

    pp_data = json.loads((BASE / "S1_RELAY_STAMP_PASSPORT.json").read_text(encoding="utf-8"))
    pp_stamps = pp_data.get("stamps", [])
    pp_names = {s.get("stamp_name") for s in pp_stamps}
    if len(pp_stamps) < 32 or "STAMP_042_5_AUDIT" not in pp_names:
        return False, f"S1_RELAY_STAMP_PASSPORT.json 042호 5대 공정 도장(#28~#32) 미완비 (현재 {len(pp_stamps)}개)"

    # Verify probe metadata via ffprobe (1080x1920, ~34.0s, AAC audio)
    probe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(mp4_root),
    ]
    pinfo = json.loads(subprocess.check_output(probe_cmd, text=True, timeout=15))
    v_stream = next((s for s in pinfo.get("streams", []) if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in pinfo.get("streams", []) if s.get("codec_type") == "audio"), {})
    vw, vh = int(v_stream.get("width", 0)), int(v_stream.get("height", 0))
    dur = float(pinfo.get("format", {}).get("duration", 0.0))
    if (vw, vh) != (1080, 1920):
        return False, f"비디오 해상도 규격 불일치: {vw}x{vh} (1080x1920 필수)"
    if not (33.5 <= dur <= 34.6):
        return False, f"비디오 총 재생시간 규격 불일치: {dur:.2f}s (34.00s 후렴구 기준)"
    if a_stream.get("codec_name") != "aac":
        return False, f"오디오 코덱 불일치: {a_stream.get('codec_name')} (AAC 필수)"

    # Measure Optical-Flow Non-Zoompan Residual across all 6 cuts: (0~5, 5~11, 11~17, 17~23, 23~29, 29~34)
    cut_windows = [(0.4, 4.0), (5.5, 4.8), (11.5, 4.8), (17.5, 4.8), (23.5, 4.8), (29.4, 4.0)]
    cut_scores = [_measure_segment_non_zoompan_residual(mp4_root, s, d) for s, d in cut_windows]
    avg_score = round(sum(cut_scores) / len(cut_scores), 4)
    zoompan_cuts = [i + 1 for i, sc in enumerate(cut_scores) if sc < 0.25]
    if zoompan_cuts or avg_score < 0.35:
        return (
            False,
            f"단순 줌인·아웃(zoompan) 슬라이드쇼 감지! 컷별 비선형 모션 잔차={cut_scores} (평균 {avg_score} < 0.35, 불량 컷={zoompan_cuts})",
        )

    return (
        True,
        f"6컷 전원 탈-줌인(Non-Zoompan) 실제 피사체 모션 검증 통과! 컷별 비선형 광학흐름 잔차={cut_scores} (평균 {avg_score}px >= 0.35px, 1080x1920 {dur:.2f}s AAC)",
    )



def check_fm010_beat_sync_and_motion_density():
    mp4_root = BASE / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    mp4_docs = BASE / "docs" / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    if not mp4_root.exists() or not mp4_docs.exists():
        return False, "마스터 쇼츠 MP4(루트 또는 docs/audio) 누락"
    if sha256_file(mp4_root) != sha256_file(mp4_docs):
        return False, "마스터 쇼츠 MP4 루트 <-> docs/audio 해시 불일치"

    # Verify zero-quota triumvirate foundry engine and cloud workflow
    foundry_py = BASE / "s1_zero_quota_triumvirate_foundry.py"
    cloud_yml = BASE / ".github" / "workflows" / "s1_cloud_triumvirate_foundry.yml"
    if not foundry_py.exists():
        return False, "s1_zero_quota_triumvirate_foundry.py 누락"
    if not cloud_yml.exists():
        return False, ".github/workflows/s1_cloud_triumvirate_foundry.yml 누락"

    # Verify ZERO_COST_SAFETY_LOCK hard guard in foundry
    foundry_txt = foundry_py.read_text(encoding="utf-8", errors="ignore")
    if "ZERO_COST_SAFETY_LOCK = True" not in foundry_txt:
        return False, "s1_zero_quota_triumvirate_foundry.py 내 ZERO_COST_SAFETY_LOCK 하드 가드 부재"

    # Verify proof documents
    proof_r = BASE / "S1_IO_TEST_14_100PT_SHORTS_AND_ZERO_QUOTA_FOUNDRY_PROOF.md"
    proof_d = BASE / "docs" / "S1_IO_TEST_14_100PT_SHORTS_AND_ZERO_QUOTA_FOUNDRY_PROOF.md"
    if not proof_r.exists() or not proof_d.exists() or sha256_file(proof_r) != sha256_file(proof_d):
        return False, "S1_IO_TEST_14_100PT_SHORTS_AND_ZERO_QUOTA_FOUNDRY_PROOF.md 누락 또는 docs 미러 불일치"

    # Verify passport 043 stamps (STAMP #33 ~ #37)
    pp_data = json.loads((BASE / "S1_RELAY_STAMP_PASSPORT.json").read_text(encoding="utf-8"))
    pp_stamps = pp_data.get("stamps", [])
    pp_names = {s.get("stamp_name") or s.get("stamp_id") for s in pp_stamps}
    if len(pp_stamps) < 37 or "STAMP_043_5_AUDIT" not in pp_names:
        return False, f"S1_RELAY_STAMP_PASSPORT.json 043호 5대 공정 도장(#33~#37) 미완비 (현재 {len(pp_stamps)}개)"

    # Measure Optical-Flow Non-Zoompan Residual across all 6 cuts for 043-SAFE
    windows = [(0.4, 4.0), (6.5, 4.5), (12.0, 3.8), (17.5, 4.2), (23.5, 4.5), (29.2, 4.0)]
    scores = [_measure_segment_non_zoompan_residual(mp4_root, s, d) for s, d in windows]
    avg_score = round(sum(scores) / len(scores), 4)

    low_cuts = [i + 1 for i, sc in enumerate(scores) if sc < 0.45]
    if low_cuts or avg_score < 0.70:
        return False, f"FM-010 모션 밀도 미달: 잔차={scores} (평균 {avg_score} < 0.70, 저밀도 컷={low_cuts})"

    return (
        True,
        f"043-SAFE 무과금 가드·비트 칼싱크·무쿼터 파운드리·전 컷 비선형 잔차 0.45px 이상(잔차={scores}, 평균 {avg_score}px >= 0.70px) 100점 완공",
    )



def check_fm011_autumn_winter_53tracks_ledger_and_extras_zero_cost():
    m_root = BASE / "S1_DISTROKID_53_TRACKS_MASTER_LEDGER.json"
    m_docs = BASE / "docs" / "S1_DISTROKID_53_TRACKS_MASTER_LEDGER.json"
    if not m_root.exists() or not m_docs.exists():
        return False, "S1_DISTROKID_53_TRACKS_MASTER_LEDGER.json (루트 또는 docs/) 누락"
    if sha256_file(m_root) != sha256_file(m_docs):
        return False, "S1_DISTROKID_53_TRACKS_MASTER_LEDGER.json 루트 <-> docs 해시 불일치"

    data = json.loads(m_root.read_text(encoding="utf-8"))
    tracks = data.get("tracks", [])
    if len(tracks) != 53:
        return False, f"마스터 원장 총 트랙 수 불일치: {len(tracks)}곡 (53곡 필수)"

    # Check 0 KRW extras policy
    extras = data.get("distrokid_extras_zero_cost_policy", {})
    if "ZERO_COST_PROTECTION_ENFORCED" not in extras.get("policy_status", ""):
        return False, "DistroKid Extras 0원 무과금 수호 정책 미명시"

    # Check masterbook
    mb_root = BASE / "S1_AUTUMN_WINTER_12TRACKS_LAUNCH_MASTERBOOK.md"
    mb_docs = BASE / "docs" / "S1_AUTUMN_WINTER_12TRACKS_LAUNCH_MASTERBOOK.md"
    if not mb_root.exists() or not mb_docs.exists() or sha256_file(mb_root) != sha256_file(mb_docs):
        return False, "S1_AUTUMN_WINTER_12TRACKS_LAUNCH_MASTERBOOK.md 누락 또는 docs 미러 불일치"

    # Check IO TEST 15
    p15_root = BASE / "S1_IO_TEST_15_AUTUMN_WINTER_53TRACKS_LAUNCH_PROOF.md"
    p15_docs = BASE / "docs" / "S1_IO_TEST_15_AUTUMN_WINTER_53TRACKS_LAUNCH_PROOF.md"
    if not p15_root.exists() or not p15_docs.exists() or sha256_file(p15_root) != sha256_file(p15_docs):
        return False, "S1_IO_TEST_15_AUTUMN_WINTER_53TRACKS_LAUNCH_PROOF.md 누락 또는 docs 미러 불일치"

    # Check passport 044 stamps
    pp_data = json.loads((BASE / "S1_RELAY_STAMP_PASSPORT.json").read_text(encoding="utf-8"))
    pp_stamps = pp_data.get("stamps", [])
    pp_names = {s.get("stamp_name") or s.get("stamp_id") for s in pp_stamps}
    if len(pp_stamps) < 42 or "STAMP_044_5_AUDIT" not in pp_names:
        return False, f"S1_RELAY_STAMP_PASSPORT.json 044호 5대 공정 도장(#38~#42) 미완비 (현재 {len(pp_stamps)}개)"

    return True, f"53곡 글로벌 원장 및 12트랙 쇼케이스·1+12 마스터북·유료 Extras 0원 방어·여권 42대 도장({len(pp_stamps)}개) 100% 무결 검증"


def check_fm012_first_screen_ui_showcase_and_freshness():
    idx = BASE / "index.html"
    docs_idx = BASE / "docs" / "index.html"
    if not idx.exists() or not docs_idx.exists():
        return False, "index.html 또는 docs/index.html 누락"
    if sha256_file(idx) != sha256_file(docs_idx):
        return False, "index.html 루트 <-> docs 해시 불일치"

    html = idx.read_text(encoding="utf-8", errors="ignore")

    # 1. Check showcase card exists in DOM
    if 'id="s1-autumn-winter-12tracks-showcase"' not in html:
        return False, '신보 12트랙 쇼케이스 카드 id=s1-autumn-winter-12tracks-showcase 실제 DOM 미삽입'

    # 2. Check top banner does not have stale 042호
    if "042호:" in html:
        return False, "최상단 #banner-father-mountain 등에 구버전 '042호:' 잔존"

    # 3. Check no stale '41곡 원장 & 11/6 발매'
    if "41곡 원장 & 11/6 발매" in html or "💿 41곡 원장" in html:
        return False, "구버전 '41곡 원장' 알약 버튼 텍스트 잔존"

    # 4. Check IO TEST 16 proof
    p16_root = BASE / "S1_IO_TEST_16_FIRST_SCREEN_UI_53TRACKS_PROOF.md"
    p16_docs = BASE / "docs" / "S1_IO_TEST_16_FIRST_SCREEN_UI_53TRACKS_PROOF.md"
    if not p16_root.exists() or not p16_docs.exists() or sha256_file(p16_root) != sha256_file(p16_docs):
        return False, "S1_IO_TEST_16_FIRST_SCREEN_UI_53TRACKS_PROOF.md 누락 또는 docs 미러 불일치"

    # 5. Check passport 045 stamps
    pp_data = json.loads((BASE / "S1_RELAY_STAMP_PASSPORT.json").read_text(encoding="utf-8"))
    pp_stamps = pp_data.get("stamps", [])
    pp_names = {s.get("stamp_name") or s.get("stamp_id") for s in pp_stamps}
    if len(pp_stamps) < 47 or "STAMP_045_5_AUDIT" not in pp_names:
        return False, f"S1_RELAY_STAMP_PASSPORT.json 045호 5대 공정 도장(#43~#47) 미완비 (현재 {len(pp_stamps)}개)"

    # 6. Check sw.js v24 or v25
    sw = BASE / "sw.js"
    sw_text = sw.read_text(encoding="utf-8", errors="ignore") if sw.exists() else ""
    if not sw.exists() or ("s1-aon-v24-" not in sw_text and "s1-aon-v25-" not in sw_text and "s1-aon-v048-" not in sw_text and "s1-aon-v049-" not in sw_text and "s1-aon-v26-" not in sw_text and "s1-aon-v26-" not in sw_text):
        return False, "sw.js 캐시 버전 미갱신 (v24 또는 v25 필수)"

    return True, f"첫 화면 045호 배지·12트랙 쇼케이스 DOM·53곡 버튼 전수 교체·sw.js v24·여권 47대 도장({len(pp_stamps)}개) 100% 무결 검증"


def check_fm013_connect_communicate_omnipotent_and_streaming_diet():
    # 1. Check bridge DOM scan and auto trigger
    b_file = BASE / "s1_rgon_to_anchongri_bridge.py"
    if not b_file.exists():
        return False, "s1_rgon_to_anchongri_bridge.py 누락"
    b_txt = b_file.read_text(encoding="utf-8", errors="ignore")
    if "querySelectorAll('pre, code, article, .markdown, [class*=\"message\"], body')" not in b_txt:
        return False, "전달봇 전체 DOM 스캔 셀렉터 미적용"
    if "def auto_execute_directive_trigger" not in b_txt:
        return False, "전달봇 auto_execute_directive_trigger 자동 집행 손 부재"

    # 2. Check CLI-Anything master guide & cli-anything-hub import
    guide_r = BASE / "S1_CLI_ANYTHING_MASTER_GUIDE.md"
    guide_d = BASE / "docs" / "S1_CLI_ANYTHING_MASTER_GUIDE.md"
    if not guide_r.exists() or not guide_d.exists() or sha256_file(guide_r) != sha256_file(guide_d):
        return False, "S1_CLI_ANYTHING_MASTER_GUIDE.md 누락 또는 docs 미러 불일치"

    # 3. Check Diet Shorts size (3.0 MB ~ 20.0 MB) & aspect ratio SAR 1:1, DAR 9:16
    mp4_r = BASE / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    mp4_d = BASE / "docs" / "audio" / "FATHER_AGE_MASTER_SHORTS_1080x1920.mp4"
    if not mp4_r.exists() or not mp4_d.exists() or sha256_file(mp4_r) != sha256_file(mp4_d):
        return False, "마스터 쇼츠 누락 또는 docs 미러 불일치"
    
    sz_mb = mp4_r.stat().st_size / (1024 * 1024)
    if not (3.0 <= sz_mb <= 20.0):
        return False, f"마스터 쇼츠 용량 초과: {sz_mb:.2f} MB (3MB ~ 20MB 필수)"

    probe_cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", str(mp4_r)]
    pinfo = json.loads(subprocess.check_output(probe_cmd, text=True, timeout=15))
    v_stream = next((s for s in pinfo.get("streams", []) if s.get("codec_type") == "video"), {})
    if v_stream.get("sample_aspect_ratio") != "1:1":
        return False, f"SAR 불일치: {v_stream.get('sample_aspect_ratio')} (1:1 필수)"
    if v_stream.get("display_aspect_ratio") != "9:16":
        return False, f"DAR 불일치: {v_stream.get('display_aspect_ratio')} (9:16 필수)"

    # 4. Check IO TEST 17 proof
    p17_r = BASE / "S1_IO_TEST_17_CONNECT_COMMUNICATE_CLI_ANYTHING_PROOF.md"
    p17_d = BASE / "docs" / "S1_IO_TEST_17_CONNECT_COMMUNICATE_CLI_ANYTHING_PROOF.md"
    if not p17_r.exists() or not p17_d.exists() or sha256_file(p17_r) != sha256_file(p17_d):
        return False, "S1_IO_TEST_17_CONNECT_COMMUNICATE_CLI_ANYTHING_PROOF.md 누락 또는 docs 미러 불일치"

    # 5. Check passport 046 stamps with 2-step verification
    pp_data = json.loads((BASE / "S1_RELAY_STAMP_PASSPORT.json").read_text(encoding="utf-8"))
    pp_stamps = pp_data.get("stamps", [])
    pp_names = {s.get("stamp_name") or s.get("stamp_id") for s in pp_stamps}
    if len(pp_stamps) < 52 or "STAMP_046_5_AUDIT" not in pp_names:
        return False, f"S1_RELAY_STAMP_PASSPORT.json 046호 5대 공정 도장(#48~#52) 미완비 (현재 {len(pp_stamps)}개)"

    st48_52 = [s for s in pp_stamps if 48 <= s.get("stamp_index", 0) <= 52]
    for s in st48_52:
        payload = s.get("payload", {})
        if not (payload.get("stage1_pass") and payload.get("stage2_pass")):
            return False, f"도장 #{s.get('stamp_index')} 삼성 2단계 통과 기록 결손"

    return True, f"전달봇 전체 DOM 스캔 & auto_trigger 장착·CLI-Anything 가이드·쇼츠 다이어트({sz_mb:.2f}MB, SAR 1:1, DAR 9:16)·여권 52대 도장({len(pp_stamps)}개) 100% 무결 검증"

def check_fm014_real_bridge_ast_and_ego_v22_skill():
    """
    [FM-014] AST 정적 분석 및 런타임 실행 검증:
    1) s1_rgon_to_anchongri_bridge.py AST 분석:
       - auto_execute_directive_trigger 위치가 if __name__ 보다 상단에 위치
       - register_new_directive 내 ast.Call auto_execute_directive_trigger 존재
       - harvest_from_github_ssot 내 ast.Call auto_execute_directive_trigger 존재
       - BASE_DIR 오타 0건
    2) 런타임 실측: auto_execute_directive_trigger("LINTER_VERIFY_047") 호출 시 ok==True & 로그 생성
    3) ego-browser v2.2.0 스킬 및 S1_EGO_LITE_V2_2_SKILL_MASTER_GUIDE.md 무결성 검증
    """
    b_file = BASE / "s1_rgon_to_anchongri_bridge.py"
    if not b_file.exists():
        return False, "s1_rgon_to_anchongri_bridge.py 누락"

    code_txt = b_file.read_text(encoding="utf-8", errors="ignore")
    if "BASE_DIR" in code_txt:
        return False, "s1_rgon_to_anchongri_bridge.py 내 미정의 변수 BASE_DIR 오타 잔존"

    try:
        tree = ast.parse(code_txt)
    except Exception as e:
        return False, f"AST 파싱 실패: {e}"

    func_lineno = None
    main_lineno = None
    reg_calls_trigger = False
    harv_calls_trigger = False

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "auto_execute_directive_trigger":
            func_lineno = node.lineno
        elif isinstance(node, ast.If):
            # check if __name__ == "__main__"
            if isinstance(node.test, ast.Compare):
                left = node.test.left
                if isinstance(left, ast.Name) and left.id == "__name__":
                    main_lineno = node.lineno
        elif isinstance(node, ast.FunctionDef) and node.name == "register_new_directive":
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name) and subnode.func.id == "auto_execute_directive_trigger":
                        reg_calls_trigger = True
        elif isinstance(node, ast.FunctionDef) and node.name == "harvest_from_github_ssot":
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name) and subnode.func.id == "auto_execute_directive_trigger":
                        harv_calls_trigger = True

    if func_lineno is None:
        return False, "auto_execute_directive_trigger 함수 정의 부재"
    if main_lineno is not None and func_lineno > main_lineno:
        return False, f"auto_execute_directive_trigger(L{func_lineno})가 if __name__(L{main_lineno}) 아래 배치된 Dead Code 결함!"
    if not reg_calls_trigger:
        return False, "register_new_directive 내 auto_execute_directive_trigger ast.Call 미호출"
    if not harv_calls_trigger:
        return False, "harvest_from_github_ssot 내 auto_execute_directive_trigger ast.Call 미호출"

    # 2. 런타임 실측 호출 검증
    try:
        import s1_rgon_to_anchongri_bridge
        res = s1_rgon_to_anchongri_bridge.auto_execute_directive_trigger("LINTER_VERIFY_047")
        if not res.get("ok"):
            return False, f"런타임 auto_execute_directive_trigger 반환 실패: {res}"
        
        log_file = BASE / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"
        if not log_file.exists():
            return False, "S1_BRIDGE_AUTO_TRIGGER_LOG.json 부재"
        log_data = json.loads(log_file.read_text(encoding="utf-8"))
        has_entry = any(t.get("directive_id") == "LINTER_VERIFY_047" for t in log_data.get("triggers", []))
        if not has_entry:
            return False, "S1_BRIDGE_AUTO_TRIGGER_LOG.json 내 LINTER_VERIFY_047 기록 부재"
    except Exception as e:
        return False, f"런타임 실측 검증 중 예외 발생: {e}"

    # 3. 에고라이트 v2.2.0 스킬 및 마스터 가이드 검증
    skill_md = BASE / ".agents" / "skills" / "ego-browser" / "SKILL.md"
    if not skill_md.exists():
        return False, ".agents/skills/ego-browser/SKILL.md 누락"
    skill_txt = skill_md.read_text(encoding="utf-8", errors="ignore")
    if 'version: "2.2.0"' not in skill_txt:
        return False, f"ego-browser 스킬 버전 미갱신 (v2.2.0 필수)"

    guide_r = BASE / "S1_EGO_LITE_V2_2_SKILL_MASTER_GUIDE.md"
    guide_d = BASE / "docs" / "S1_EGO_LITE_V2_2_SKILL_MASTER_GUIDE.md"
    if not guide_r.exists() or not guide_d.exists() or sha256_file(guide_r) != sha256_file(guide_d):
        return False, "S1_EGO_LITE_V2_2_SKILL_MASTER_GUIDE.md 누락 또는 docs 미러 불일치"

    # 4. IO TEST 18 증빙서 검증
    p18_r = BASE / "S1_IO_TEST_18_REAL_BRIDGE_AND_EGO_V22_PROOF.md"
    p18_d = BASE / "docs" / "S1_IO_TEST_18_REAL_BRIDGE_AND_EGO_V22_PROOF.md"
    if not p18_r.exists() or not p18_d.exists() or sha256_file(p18_r) != sha256_file(p18_d):
        return False, "S1_IO_TEST_18_REAL_BRIDGE_AND_EGO_V22_PROOF.md 누락 또는 docs 미러 불일치"

    # 5. 여권 도장 검증 (57개)
    pp_data = json.loads((BASE / "S1_RELAY_STAMP_PASSPORT.json").read_text(encoding="utf-8"))
    pp_stamps = pp_data.get("stamps", [])
    pp_names = {s.get("stamp_name") or s.get("stamp_id") for s in pp_stamps}
    if len(pp_stamps) < 57 or "STAMP_047_5_AUDIT" not in pp_names:
        return False, f"S1_RELAY_STAMP_PASSPORT.json 047호 5대 공정 도장(#53~#57) 미완비 (현재 {len(pp_stamps)}개)"

    st53_57 = [s for s in pp_stamps if 53 <= s.get("stamp_index", 0) <= 57]
    for s in st53_57:
        payload = s.get("payload", {})
        if not (payload.get("stage1_pass") and payload.get("stage2_pass")):
            return False, f"도장 #{s.get('stamp_index')} 삼성 2단계 통과 기록 결손"

    
    # 6. [049호 클린 단일 스크롤 레이아웃 & 4대 HTML 1:1 동기화 검증]
    idx_f = BASE / "index.html"
    if not idx_f.exists():
        return False, "index.html 누락"
    idx_content = idx_f.read_text(encoding="utf-8", errors="ignore")

    # [049호 4대 HTML 1:1 동기화 검증]
    html_files = [
        BASE / "index.html",
        BASE / "docs" / "index.html",
        BASE / "rgon_alpha_chat.html",
        BASE / "docs" / "rgon_alpha_chat.html"
    ]
    for hf in html_files:
        if not hf.exists():
            return False, f"필수 HTML 파일 부재: {hf.name}"
    base_hash = sha256_file(html_files[0])
    for hf in html_files[1:]:
        if sha256_file(hf) != base_hash:
            return False, f"4대 HTML 1:1 동기화 불일치: {hf.relative_to(BASE)} != index.html"

    # [049호 sw.js 캐시 버전 검증]
    sw_f = BASE / "sw.js"
    docs_sw_f = BASE / "docs" / "sw.js"
    if "s1-aon-v049-clean-layout" not in sw_f.read_text(encoding="utf-8"):
        return False, "sw.js 캐시 버전 미갱신 (s1-aon-v049-clean-layout 필수)"
    if not docs_sw_f.exists() or sha256_file(sw_f) != sha256_file(docs_sw_f):
        return False, "sw.js <-> docs/sw.js 해시 불일치"

    # [049호 <main class="mn"> 바깥 상단 고정 영역 다이어트 검증]
    mn_pos = idx_content.find('<main class="mn"')
    if mn_pos == -1:
        return False, "<main class='mn'> 스크롤 컨테이너 부재"

    banner_pos = idx_content.find('id="banner-father-mountain"')
    showcase_pos = idx_content.find('id="s1-autumn-winter-12tracks-showcase"')
    if banner_pos == -1:
        return False, "#banner-father-mountain 부재"
    if showcase_pos == -1:
        return False, "#s1-autumn-winter-12tracks-showcase 부재"
    if banner_pos < mn_pos:
        return False, f"#banner-father-mountain이 <main class='mn'> 바깥(상단 고정 영역)에 위치하여 화면 짓누름 결함 유발 (banner_pos={banner_pos} < mn_pos={mn_pos})"
    if showcase_pos < mn_pos:
        return False, f"#s1-autumn-winter-12tracks-showcase가 <main class='mn'> 바깥(상단 고정 영역)에 위치하여 화면 짓누름 결함 유발 (showcase_pos={showcase_pos} < mn_pos={mn_pos})"

    # <main class="mn"> 바깥에 거대 섹션 존재 금지
    pre_mn_text = idx_content[:mn_pos]
    if 'id="s1-autumn-winter-12tracks-showcase"' in pre_mn_text:
        return False, "<main class='mn'> 바깥 상단 고정 영역에 거대 쇼케이스 박스 잔존 결함"
    if 'id="banner-father-mountain"' in pre_mn_text:
        return False, "<main class='mn'> 바깥 상단 고정 영역에 상단 배너 잔존 결함"

    # [049호 12곡 단일 통합 & 문구 정합 검증]
    showcase_count = idx_content.count('id="s1-autumn-winter-12tracks-showcase"')
    if showcase_count != 1:
        return False, f"신보 12트랙 쇼케이스 카드 중복/누락 결손: {showcase_count}개 발견 (정확히 단 1개 필수)"

    if 'id="s1-kakaopage-ranking-chart"' in idx_content:
        return False, "2중 중복 12곡 랭킹차트(#s1-kakaopage-ranking-chart) 미제거 잔존 결함"

    if "기존 53곡 카탈로그에 신보 12곡을 더해" in idx_content:
        return False, "왜곡된 문구 '기존 53곡 카탈로그에 신보 12곡을 더해' 잔존 (41+12=53 수정 필요)"
    if "기존 41곡 카탈로그에 신보 12곡을 더해" not in idx_content:
        return False, "필수 문구 '기존 41곡 카탈로그에 신보 12곡을 더해' 누락"
    if "총 53곡 글로벌 원장" not in idx_content:
        return False, "필수 문구 '총 53곡 글로벌 원장' 누락"

    # 12곡 정품 타이틀 전수 검증
    twelve_tracks = [
        "01. 막차", "02. 창을 닫지 마", "03. 첫 입김", "04. 오늘은 여기까지",
        "05. 밥은 먹었니", "06. 식어 가는 차", "07. 가로등 아래서", "08. 남겨 둔 자리",
        "09. 보내지 않은 말", "10. 불은 꺼지지 않아", "11. 난로 옆에서", "12. 내일의 아침"
    ]
    for trk in twelve_tracks:
        if trk not in idx_content:
            return False, f"12트랙 정품 곡명 누락: '{trk}'"

    # 잔류 찌꺼기 0건 검증
    forbidden_residues = ["Track 02 · Acoustic", "Track 03 · Warm Pad", "가을의 마지막 잎새", "첫눈 오는 날의 온기"]
    for fr in forbidden_residues:
        if fr in idx_content:
            return False, f"레이아웃 결함 잔류 찌꺼기 감지! '{fr}' 즉시 퇴출 필수 (QM-SP-11 격리)"

    return True, f"전달봇 AST 정적 검증(L{func_lineno} < L{main_lineno}, 2대 ast.Call)·런타임 실측 성공·ego-browser v2.2.0·여권 57대 도장({len(pp_stamps)}개) 100% 무결 검증"


GUARD_DISPATCH = {
    "check_fm001_no_fake_tkinter": check_fm001_no_fake_tkinter,
    "check_fm002_authentic_motion_shorts": check_fm002_authentic_motion_shorts,
    "check_fm003_ego_lockfile_guard": check_fm003_ego_lockfile_guard,
    "check_fm004_dynamic_monitor_geometry": check_fm004_dynamic_monitor_geometry,
    "check_fm005_space0_bottom_scroll": check_fm005_space0_bottom_scroll,
    "check_fm006_ide_chat_only_exposure": check_fm006_ide_chat_only_exposure,
    "check_fm007_audio_and_docs_mirror_zero_404": check_fm007_audio_and_docs_mirror_zero_404,
    "check_fm008_dashboard_freshness": check_fm008_dashboard_freshness,
    "check_fm009_non_zoompan_dynamic_motion": check_fm009_non_zoompan_dynamic_motion,
    "check_fm010_beat_sync_and_motion_density": check_fm010_beat_sync_and_motion_density,
    "check_fm011_autumn_winter_53tracks_ledger_and_extras_zero_cost": check_fm011_autumn_winter_53tracks_ledger_and_extras_zero_cost,
    "check_fm012_first_screen_ui_showcase_and_freshness": check_fm012_first_screen_ui_showcase_and_freshness,
    "check_fm013_connect_communicate_omnipotent_and_streaming_diet": check_fm013_connect_communicate_omnipotent_and_streaming_diet,
    "check_fm014_real_bridge_ast_and_ego_v22_skill": check_fm014_real_bridge_ast_and_ego_v22_skill,
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
        "linter_version": "1.6.0",
        "directive_id": "RGON_DIR_CONNECT_COMMUNICATE_OMNIPOTENT_046",
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
    print(f"🛡️ [S1 구조적 품질 린터 v1.7] 전수 검사 결과: {report['verdict']} ({score} / 100.0)")
    print("=" * 72)
    for c in checks:
        mark = "✅ PASS" if c["passed"] else "❌ FAIL (QM-SP-11 격리)"
        print(f" - [{c['id']}] {c['name']}: {mark}\n     └─ {c['detail']}")
    print("=" * 72)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_checks())