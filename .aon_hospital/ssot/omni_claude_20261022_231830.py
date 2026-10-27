#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rgon_local_cleanup.py  (Python 3 표준 라이브러리 전용 / 네트워크 전송 없음)

1) 클립보드 자동 덮어쓰기 코드 진단 + 안전 비활성화 (.js 주석 처리, rgon_bridge_8765.py 의 clip.exe 호출 제거)
2) HTML 대시보드 탐색·복원, 바탕화면 바로가기 갱신, 브라우저 오픈
3) RGON_EVOLUTION_LOG.md 일일 마감 기록 추가 (사전 .bak 백업)
4) 기억 저장소 파일 상태 + 로그 마지막 15줄 출력, daily_wrapup_summary.txt 저장

수정되는 모든 파일은 <파일명>.bak_YYYYmmdd_HHMMSS 로 먼저 백업됩니다.
"""
import ast
import os
import re
import shutil
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\sangi\Downloads\shin-agent")
DESKTOP = Path(r"C:\Users\sangi\Desktop")
GITHUB_PAGES = "https://sangill111157-spec.github.io/hangeoreumsshik-cloud/"
DASH_NAME = "rgon_alpha_audience.html"
DASH = ROOT / DASH_NAME
LOG_MD = ROOT / "RGON_EVOLUTION_LOG.md"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
MAX_SCAN_BYTES = 2_000_000
BAT_ENC = "mbcs" if os.name == "nt" else "utf-8"

REPORT = []


def say(msg=""):
    print(msg, flush=True)
    REPORT.append(str(msg))


def section(title):
    say("")
    say("=" * 78)
    say(title)
    say("=" * 78)


def human(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{int(n)}B" if u == "B" else f"{n:.1f}{u}"
        n /= 1024


def fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def backup(path):
    b = path.with_name(path.name + f".bak_{STAMP}")
    shutil.copy2(path, b)
    return b


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(text)


def walk_files(base, suffixes):
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if Path(fn).suffix.lower() in suffixes:
                yield Path(dp) / fn


def rel(p):
    try:
        return str(Path(p).relative_to(ROOT))
    except ValueError:
        return str(p)


# ───────────────────────── 1. 클립보드 덮어쓰기 진단/차단 ─────────────────────────
CORE_RE = re.compile(
    r"""["']shared["']|\bentries\b|clipboard\s*\.\s*writeText|execCommand\(\s*["']copy["']"""
    r"""|clip\.exe|Set-Clipboard|pyperclip""", re.I)
TIMER_LINE_RE = re.compile(r"setInterval|\bpoll\w*", re.I)
CLIP_JS_RE = re.compile(r"""navigator\s*\.\s*clipboard\s*\.\s*writeText\s*\(|execCommand\(\s*["']copy["']\s*\)""")
SHARED_RE = re.compile(r"""["']shared["']|\bshared\s*:|\bentries\b""")
TIMER_RE = re.compile(r"setInterval|setTimeout|\bpoll\w*|alarms\.|onAlarm|MutationObserver|\bsync\w*", re.I)
USER_EVENT_RE = re.compile(
    r"""addEventListener\(\s*["'](click|keydown|keyup|contextmenu|mousedown|copy)["']|\bonclick\b|\.click\(\)"""
    r"""|commands\.onCommand|contextMenus\.onClicked|action\.onClicked""")
CLIP_PY_RE = re.compile(r"clip\.exe|Set-Clipboard|pyperclip", re.I)


def scan_clipboard_hits():
    section("[1-A] 클립보드/\"shared\"/\"entries\" 관련 코드 스캔 (.js, .py)")
    files = []
    for p in walk_files(ROOT, {".js", ".py"}):
        try:
            if p.stat().st_size <= MAX_SCAN_BYTES:
                files.append(p)
        except OSError:
            pass
    shown = 0
    for p in sorted(files):
        try:
            lines = read_text(p).splitlines()
        except OSError:
            continue
        core = [(i, l) for i, l in enumerate(lines, 1) if CORE_RE.search(l)]
        if not core:
            continue
        timers = [(i, l) for i, l in enumerate(lines, 1) if TIMER_LINE_RE.search(l)]
        shown += 1
        say(f"\n  ■ {rel(p)}")
        merged = sorted(set(core[:40]) | set(timers[:10]))
        for i, l in merged:
            tag = "타이머" if (i, l) in timers and (i, l) not in core else "핵심"
            say(f"     L{i:<5} [{tag}] {l.strip()[:150]}")
    if not shown:
        say("  해당 패턴을 포함한 .js/.py 파일이 없습니다.")


def disable_js_clipboard(path):
    """타이머/자동 동기화 문맥에서 'shared' JSON 을 클립보드에 쓰는 한 줄짜리 문장만 주석 처리."""
    try:
        text = read_text(path)
    except OSError as e:
        return [], [f"읽기 실패: {e}"]
    lines = text.splitlines(keepends=True)
    changed, notes = [], []
    for idx, raw in enumerate(lines):
        m = CLIP_JS_RE.search(raw)
        if not m or raw.strip().startswith(("//", "*", "/*")):
            continue
        win = "".join(lines[max(0, idx - 40): idx + 15])
        lineno = idx + 1
        if USER_EVENT_RE.search(win):
            notes.append(f"L{lineno}: 사용자 이벤트(클릭/단축키 등)와 연관 → 유지")
            continue
        if not (TIMER_RE.search(win) and SHARED_RE.search(win)):
            notes.append(f"L{lineno}: 타이머+shared 문맥 아님(수동 확인 권장) → 유지")
            continue
        s = raw.strip()
        prefix = s[:m.start() - (len(raw) - len(raw.lstrip()))] if False else s[:s.find(m.group(0))]
        safe = (s.endswith(";") and s.count("(") == s.count(")") and s.count("{") == s.count("}")
                and re.fullmatch(r"\s*(await\s+|void\s+)?", prefix) is not None)
        if not safe:
            notes.append(f"L{lineno}: 자동 쓰기 의심이나 한 줄 단독 문장이 아님 → 자동 수정 불가, 수동 확인 필요")
            continue
        indent = raw[:len(raw) - len(raw.lstrip())]
        eol = "\r\n" if raw.endswith("\r\n") else "\n"
        lines[idx] = f"{indent}// [RGON_DISABLED_AUTO_CLIPBOARD] {s}{eol}{indent}void 0;{eol}"
        changed.append(lineno)
    if changed:
        b = backup(path)
        write_text(path, "".join(lines))
        notes.append(f"백업: {b.name}")
    return changed, notes


def neutralize_python_clip(path):
    """rgon_bridge_8765.py 의 clip.exe 호출 문장을 주석 처리하고 pass 로 대체 (ast 로 문장 범위 확인)."""
    try:
        src = read_text(path)
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError) as e:
        return [], [f"파싱 실패로 건너뜀: {e}"]
    lines = src.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines, 1) if CLIP_PY_RE.search(l) and not l.strip().startswith("#")]
    if not hits:
        return [], []
    simple = [n for n in ast.walk(tree) if isinstance(n, ast.stmt) and not hasattr(n, "body")]
    targets, notes = {}, []
    for h in hits:
        cover = [n for n in simple if n.lineno <= h <= n.end_lineno]
        if not cover:
            notes.append(f"L{h}: 단독 문장이 아님(조건식/헤더 등) → 수동 확인 필요")
            continue
        n = min(cover, key=lambda x: x.end_lineno - x.lineno)
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            continue  # docstring / 문자열 상수
        first = lines[n.lineno - 1]
        if n.col_offset != len(first) - len(first.lstrip()):
            notes.append(f"L{h}: 한 줄에 여러 구문 → 수동 확인 필요")
            continue
        targets[(n.lineno, n.end_lineno)] = n
    removed = []
    new_lines = lines[:]
    for (a, b), n in sorted(targets.items(), reverse=True):
        first = new_lines[a - 1]
        indent = first[:len(first) - len(first.lstrip())]
        eol = "\r\n" if first.endswith("\r\n") else "\n"
        block = [f"{indent}# [RGON_DISABLED_CLIPBOARD] {l.strip()}{eol}" for l in new_lines[a - 1:b]]
        block.append(f"{indent}pass{eol}")
        new_lines[a - 1:b] = block
        removed.append(a)
    if not removed:
        return [], notes
    new_src = "".join(new_lines)
    try:
        ast.parse(new_src)
    except SyntaxError as e:
        return [], notes + [f"수정 결과 문법 검증 실패 → 원본 유지: {e}"]
    bk = backup(path)
    write_text(path, new_src)
    notes.append(f"백업: {bk.name} / 수정 후 ast.parse 통과")
    return sorted(removed), notes


def step_clipboard():
    scan_clipboard_hits()
    section("[1-B] 자동 클립보드 쓰기 차단")
    js_total, py_total = 0, 0
    for p in sorted(walk_files(ROOT, {".js"})):
        try:
            if p.stat().st_size > MAX_SCAN_BYTES:
                continue
            if not CLIP_JS_RE.search(read_text(p)):
                continue
        except OSError:
            continue
        changed, notes = disable_js_clipboard(p)
        say(f"  ■ {rel(p)}")
        if changed:
            say(f"     자동 쓰기 비활성화(주석 처리) 줄: {changed}")
        for n in notes:
            say(f"     - {n}")
        js_total += len(changed)
    for p in sorted(ROOT.rglob("rgon_bridge_8765.py")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        removed, notes = neutralize_python_clip(p)
        say(f"  ■ {rel(p)}")
        say(f"     clip.exe 호출 제거(주석+pass) 줄: {removed if removed else '없음'}")
        for n in notes:
            say(f"     - {n}")
        py_total += len(removed)
    watcher = ROOT / "rgon_auto_watcher.py"
    if watcher.exists():
        hits = [i for i, l in enumerate(read_text(watcher).splitlines(), 1)
                if CLIP_PY_RE.search(l) and not l.strip().startswith("#")]
        say(f"  ■ rgon_auto_watcher.py 클립보드 관련 줄(수정 안 함, 참고용): {hits if hits else '없음'}")
    say("")
    say(f"  결과: JS {js_total}곳 / Python {py_total}곳 비활성화")
    if js_total:
        say("  ※ 확장프로그램은 chrome://extensions 에서 '새로고침'해야 변경이 적용됩니다.")
    return js_total, py_total


# ───────────────────────── 2. HTML 대시보드 ─────────────────────────
def step_html():
    section("[2-A] 프로젝트 내 .html 파일 목록")
    htmls = []
    for p in walk_files(ROOT, {".html", ".htm"}):
        try:
            st = p.stat()
            htmls.append((p, st.st_size, st.st_mtime))
        except OSError:
            pass
    htmls.sort(key=lambda r: r[2], reverse=True)
    if htmls:
        w = min(max(len(rel(r[0])) for r in htmls), 70)
        say(f"  {'경로':<{w}}  {'크기':>9}  최근 수정")
        say("  " + "-" * (w + 34))
        for p, s, m in htmls:
            say(f"  {rel(p)[:w]:<{w}}  {human(s):>9}  {fmt_time(m)}")
    else:
        say("  .html 파일이 없습니다.")

    restored = None
    if not DASH.exists():
        subs = [r for r in htmls
                if len(r[0].relative_to(ROOT).parts) > 1
                and r[0].relative_to(ROOT).parts[0].lower() in ("docs", "dashboard", "backups")]
        tiers = [
            [r for r in subs if r[0].name.lower() == DASH_NAME],
            [r for r in subs if re.search(r"dashboard|audience|rgon", r[0].name, re.I)],
            [r for r in subs if "extension" not in str(r[0]).lower()],
        ]
        for tier in tiers:
            if tier:
                src = max(tier, key=lambda r: r[2])[0]
                try:
                    shutil.copy2(src, DASH)
                    restored = src
                    say(f"\n  루트에 대시보드가 없어 복사했습니다: {rel(src)} → {DASH_NAME}")
                except OSError as e:
                    say(f"\n  복사 실패: {e}")
                break
        if not restored:
            say("\n  [참고] 루트에 대시보드가 없고 복원할 후보도 찾지 못했습니다 → GitHub Pages 주소를 사용합니다.")
    else:
        say(f"\n  루트 대시보드 존재: {DASH}")
    return htmls, restored


def step_shortcuts_and_open():
    section("[2-B] 바탕화면 바로가기 갱신 및 대시보드 오픈")
    target = DASH.as_uri() if DASH.exists() else GITHUB_PAGES
    say(f"  열 대상: {target}")
    try:
        DESKTOP.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        say(f"  바탕화면 폴더 접근 실패: {e}")
    url_file = DESKTOP / "RGON_Dashboard.url"
    bat_file = DESKTOP / "open_rgon_dashboard.bat"
    ok = 0
    try:
        write_text(url_file, f"[InternetShortcut]\r\nURL={target}\r\n")
        say(f"  갱신: {url_file}")
        ok += 1
    except OSError as e:
        say(f"  .url 갱신 실패: {e}")
    try:
        arg = str(DASH) if DASH.exists() else GITHUB_PAGES
        with open(bat_file, "w", encoding=BAT_ENC, errors="replace", newline="") as f:
            f.write(f'@echo off\r\nstart "" "{arg}"\r\nexit\r\n')
        say(f"  갱신: {bat_file}")
        ok += 1
    except OSError as e:
        say(f"  .bat 갱신 실패: {e}")
    opened = False
    try:
        opened = bool(webbrowser.open(target))
        say(f"  webbrowser.open: {'성공' if opened else '브라우저 호출 실패'}")
    except Exception as e:
        say(f"  오픈 실패: {e}")
    return target, ok, opened


# ───────────────────────── 3. 작업 일지 마감 기록 ─────────────────────────
def step_log(js_total, py_total):
    section("[3] RGON_EVOLUTION_LOG.md 일일 마감 기록 추가")
    now = datetime.now()
    entry = (
        f"\n\n## 🌙 일일 마감 (EOD) — {now:%Y-%m-%d %H:%M:%S}\n\n"
        f"- 클립보드(`{{\"shared\":...}}`) 자동 덮어쓰기 버그 진단 및 차단 조치 완료 "
        f"(JS {js_total}곳 / Python {py_total}곳 비활성화, 원본은 `.bak_{STAMP}` 로 백업)\n"
        "- 콘솔 깜빡임 방지(`CREATE_NO_WINDOW`) 정비 완료 및 `rgon_auto_watcher.py` 정상 가동 확인\n"
        "- 로컬 8765 큐 브리지(`rgon_bridge_8765.py`) 문법 검증(`ast.parse`) 필터 적용 완료\n"
        "- 아침 07:00 예약 작업(`RGON_Morning_Briefing_0700`, `\\ConnectAI_Daily_Briefing`) 활성화(`ENABLE`) 확인 완료\n"
        "- 구버전 임시 파일 `backups/daily_omni_archive` 폴더 정리 완료\n"
        "\n> 참고: 위 항목 중 클립보드 항목 외에는 이전 단계 결과를 기록한 것이며, 이 스크립트가 재검증하지는 않습니다.\n"
    )
    try:
        if LOG_MD.exists():
            b = backup(LOG_MD)
            say(f"  백업: {b.name}")
            existing = read_text(LOG_MD)
            sep = "" if existing.endswith("\n") else "\n"
            with open(LOG_MD, "a", encoding="utf-8", newline="") as f:
                f.write(sep + entry.replace("\n", "\r\n" if "\r\n" in existing else "\n"))
        else:
            say("  기존 파일이 없어 새로 생성합니다.")
            write_text(LOG_MD, "# RGON EVOLUTION LOG\n" + entry)
        say(f"  마감 기록 추가 완료: {LOG_MD}")
        return True
    except OSError as e:
        say(f"  기록 실패: {e}")
        return False


# ───────────────────────── 4. 기억 저장소 상태 ─────────────────────────
def find_memory_file(name):
    direct = ROOT / name
    if direct.exists():
        return direct
    found = [p for p in walk_files(ROOT, {Path(name).suffix.lower()}) if p.name.lower() == name.lower()]
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def step_memory_status():
    section("[4] 기억 저장소 파일 상태")
    names = ["evolution_memory.json", "memory_vault.json", "RGON_EVOLUTION_LOG.md"]
    say(f"  {'파일':<26} {'크기':>9}  {'최근 수정':<19}  경로")
    say("  " + "-" * 90)
    for n in names:
        p = find_memory_file(n)
        if p:
            st = p.stat()
            say(f"  {n:<26} {human(st.st_size):>9}  {fmt_time(st.st_mtime):<19}  {rel(p)}")
        else:
            say(f"  {n:<26} {'-':>9}  {'(파일 없음)':<19}")
    if LOG_MD.exists():
        say("")
        say("  ── RGON_EVOLUTION_LOG.md 마지막 15줄 ──")
        for l in read_text(LOG_MD).splitlines()[-15:]:
            say("  | " + l)


def save_summary():
    out = ROOT / "daily_wrapup_summary.txt"
    try:
        write_text(out, f"RGON daily wrap-up summary ({datetime.now():%Y-%m-%d %H:%M:%S})\n"
                        f"Root: {ROOT}\n\n" + "\n".join(REPORT) + "\n")
        print(f"\n  요약 저장: {out}", flush=True)
    except OSError as e:
        print(f"\n  요약 저장 실패: {e}", flush=True)


def main():
    if not ROOT.is_dir():
        sys.exit(f"작업 폴더가 없습니다: {ROOT}")
    say(f"RGON 로컬 정비 시작 {datetime.now():%Y-%m-%d %H:%M:%S} | {ROOT}")
    js_total = py_total = 0
    try:
        js_total, py_total = step_clipboard()
    except Exception as e:
        say(f"  [오류] 클립보드 진단: {type(e).__name__}: {e}")
    try:
        step_html()
        step_shortcuts_and_open()
    except Exception as e:
        say(f"  [오류] 대시보드: {type(e).__name__}: {e}")
    try:
        step_log(js_total, py_total)
    except Exception as e:
        say(f"  [오류] 일지 기록: {type(e).__name__}: {e}")
    try:
        step_memory_status()
    except Exception as e:
        say(f"  [오류] 기억 저장소 상태: {type(e).__name__}: {e}")
    save_summary()


if __name__ == "__main__":
    main()
Copy