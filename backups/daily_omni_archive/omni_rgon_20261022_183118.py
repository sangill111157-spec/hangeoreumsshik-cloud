# -*- coding: utf-8 -*-
import os
import re
import sys
import glob
import json
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
TRADING_DIR = r"C:\trading"
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
DESKTOP_ALT = os.path.join(os.path.expanduser("~"), "Desktop")
ENV_LOCAL = os.path.join(ROOT, ".env.telegram.local")
REPORT_PATH = os.path.join(ROOT, "EXISTING_AUTOMATION_AND_SHEETS_REPORT.md")

def send_tg(text):
    if not os.path.isfile(ENV_LOCAL):
        return False
    tok, cid = None, None
    for ln in open(ENV_LOCAL, encoding="utf-8", errors="replace").read().splitlines():
        if ln.startswith("TELEGRAM_BOT_TOKEN="):
            tok = ln.split("=", 1)[1].strip()
        elif ln.startswith("TELEGRAM_CHAT_ID="):
            cid = ln.split("=", 1)[1].strip()
    if not tok or not cid:
        return False
    url = f"https://api.telegram.org/bot{tok}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": cid, "text": text[:3900]}).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=12) as r:
            return r.status == 200
    except Exception:
        return False

def scan_windows_tasks():
    tasks = []
    try:
        p = subprocess.run(
            ["schtasks", "/query", "/fo", "CSV", "/nh"],
            capture_output=True,
            text=True,
            encoding="cp949",
            errors="replace",
            timeout=15,
        )
        keywords = ("rgon", "shin", "trading", "nvda", "nvidia", "ahn", "안총리", "로건", "bot", "auto", "sheet", "brief", "pulse", "python")
        for line in (p.stdout or "").splitlines():
            low = line.lower()
            if any(k in low for k in keywords) and "microsoft\\" not in low:
                parts = [x.strip('"') for x in line.split('","')]
                if len(parts) >= 3:
                    tasks.append(f"{parts[0]} (다음실행: {parts[1]}, 상태: {parts[2]})")
    except Exception as ex:
        tasks.append(f"스케줄러 조회 참고: {ex}")
    return tasks[:25]

def scan_bat_and_startup():
    items = []
    startup_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup",
    )
    search_dirs = [
        ("바탕화면(OneDrive)", DESKTOP_DIR),
        ("바탕화면(기본)", DESKTOP_ALT),
        ("윈도우 시작프로그램", startup_dir),
        ("shin-agent 루트", ROOT),
        ("C:\\trading", TRADING_DIR),
    ]
    for label, d in search_dirs:
        if not os.path.isdir(d):
            continue
        for ext in ("*.bat", "*.cmd", "*.vbs", "*.ps1", "*.lnk"):
            for f in glob.glob(os.path.join(d, ext)):
                bname = os.path.basename(f)
                items.append(f"[{label}] {bname}")
    return items[:40]

def scan_google_sheets_and_automation():
    sheet_ids = {}
    sheet_scripts = []
    tg_bots = []
    auto_scripts = []

    sheet_id_re = re.compile(r"spreadsheets/d/([a-zA-Z0-9-_]{25,60})")
    sheet_var_re = re.compile(
        r'(?:SPREADSHEET_ID|SHEET_ID|DOC_ID|GOOGLE_SHEET|sheet_id|spreadsheet_id)\s*[=:]\s*["\']([a-zA-Z0-9-_]{25,60})["\']'
    )
    tab_name_re = re.compile(
        r'(?:worksheet|sheet_name|TAB_NAME|tab_name|gid)\s*[=:(]\s*["\']([^"\']{2,40})["\']'
    )

    scan_roots = [ROOT]
    if os.path.isdir(TRADING_DIR):
        scan_roots.append(TRADING_DIR)

    found_tabs = set()
    service_jsons = []

    for sroot in scan_roots:
        for dirpath, dirnames, filenames in os.walk(sroot):
            dirnames[:] = [
                d for d in dirnames
                if d not in (".git", "node_modules", "venv", ".venv", "__pycache__", "backups")
            ]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                rel = os.path.relpath(fp, sroot)
                prefix = "shin-agent" if sroot == ROOT else "C:\\trading"
                full_label = f"{prefix}/{rel}"

                low_fn = fn.lower()
                if any(k in low_fn for k in ("auto", "bot", "telegram", "sched", "daemon", "watch", "cron", "ahn", "runner", "pulse")) and low_fn.endswith((".py", ".js", ".bat", ".ps1")):
                    auto_scripts.append(full_label)

                if not low_fn.endswith((".py", ".json", ".md", ".env", ".txt", ".bat", ".html", ".yml")):
                    continue
                if os.path.getsize(fp) > 800000:
                    continue

                try:
                    text = open(fp, "r", encoding="utf-8", errors="replace").read()
                except Exception:
                    continue

                if low_fn.endswith(".json") and '"service_account"' in text and '"client_email"' in text:
                    m_email = re.search(r'"client_email"\s*:\s*"([^"]+)"', text)
                    service_jsons.append(f"{full_label} ({m_email.group(1) if m_email else 'service_account'})")

                for sid in sheet_id_re.findall(text) + sheet_var_re.findall(text):
                    if len(sid) >= 28:
                        sheet_ids.setdefault(sid, set()).add(full_label)

                if any(k in text for k in ("gspread", "googleapiclient", "spreadsheets", " Master_Schedule", "구글 시트", "구글시트")):
                    if low_fn.endswith(".py"):
                        sheet_scripts.append(full_label)
                    for tb in tab_name_re.findall(text):
                        if len(tb) < 35 and not tb.startswith("http"):
                            found_tabs.add(tb)

                if "api.telegram.org" in text or "TELEGRAM_BOT_TOKEN" in text or "telebot" in text or "aiogram" in text:
                    if low_fn.endswith(".py"):
                        tg_bots.append(full_label)

    return {
        "sheet_ids": {k: sorted(list(v))[:5] for k, v in sheet_ids.items()},
        "service_accounts": service_jsons[:15],
        "sheet_scripts": sorted(list(set(sheet_scripts)))[:25],
        "found_tabs": sorted(list(found_tabs))[:30],
        "tg_bots": sorted(list(set(tg_bots)))[:25],
        "auto_scripts": sorted(list(set(auto_scripts)))[:35],
    }

def main():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[SCAN] 기존 윈도우 자동화 및 구글 시트 전수 분해 시작 ({now_str})...")

    tasks = scan_windows_tasks()
    bats = scan_bat_and_startup()
    info = scan_google_sheets_and_automation()

    lines = [
        f"# 🔍 [RGON 기존 윈도우 자동화 & 구글 시트 완전 분해 보고서]",
        f"- 조사 시각: {now_str} (읽기 전용 R0 · 안총리 토큰 소모 0)",
        "",
        "## 1. ⏰ 윈도우 작업 스케줄러 (등록된 자동 실행 작업)",
    ]
    if tasks:
        for t in tasks:
            lines.append(f"- {t}")
    else:
        lines.append("- (탐지된 커스텀 파이썬/봇 스케줄러 없음)")

    lines.append("\n## 2. 🖥️ 바탕화면 · 시작프로그램 · 루트 배치파일(.bat/.ps1)")
    for b in bats[:20]:
        lines.append(f"- {b}")

    lines.append(f"\n## 3. 📊 발견된 구글 시트 ID ({len(info['sheet_ids'])}개) 및 서비스 계정")
    for sid, files in info["sheet_ids"].items():
        lines.append(f"- **시트 ID:** `{sid}`")
        lines.append(f"  - 연결 파일: {', '.join(files[:3])}")
    if info["service_accounts"]:
        lines.append("- **구글 서비스 계정(열쇠 JSON):**")
        for sa in info["service_accounts"]:
            lines.append(f"  - {sa}")
    if info["found_tabs"]:
        lines.append(f"- **코드 내 탐지된 시트 탭/키워드({len(info['found_tabs'])}종):** {', '.join(info['found_tabs'][:20])}")

    lines.append(f"\n## 4. 🐍 구글 시트 연동 파이썬 스크립트 ({len(info['sheet_scripts'])}개)")
    for s in info["sheet_scripts"]:
        lines.append(f"- `{s}`")

    lines.append(f"\n## 5. ✈️ 기존 텔레그램/로건봇/NVIDIA봇 관련 스크립트 ({len(info['tg_bots'])}개)")
    for tb in info["tg_bots"]:
        lines.append(f"- `{tb}`")

    lines.append(f"\n## 6. 🤖 안총리 & 윈도우 자동화/런처 스크립트 ({len(info['auto_scripts'])}개)")
    for a in info["auto_scripts"]:
        lines.append(f"- `{a}`")

    report_md = "\n".join(lines) + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(report_md)
    print(f"[REPORT] 상세 보고서 저장 완료: {REPORT_PATH}")

    tg_summary = (
        "🔍 [기존 자동화 & 구글 시트 완전 분해 보고서]\n\n"
        f"1️⃣ 윈도우 스케줄러({len(tasks)}건):\n"
        + ("\n".join("• " + x for x in tasks[:6]) if tasks else "• 등록된 작업 없음")
        + f"\n\n2️⃣ 바탕화면/시작 배치파일({len(bats)}건):\n"
        + "\n".join("• " + x for x in bats[:8])
        + f"\n\n3️⃣ 발견된 구글 시트 ID({len(info['sheet_ids'])}개):\n"
        + ("\n".join(f"• {k[:14]}... ({', '.join(v[:2])})" for k, v in list(info["sheet_ids"].items())[:6]) or "• 없음")
        + f"\n\n4️⃣ 구글 시트 연동 스크립트({len(info['sheet_scripts'])}개):\n"
        + ("\n".join("• " + x for x in info["sheet_scripts"][:8]) or "• 없음")
        + f"\n\n5️⃣ 기존 텔레그램/봇 스크립트({len(info['tg_bots'])}개):\n"
        + ("\n".join("• " + x for x in info["tg_bots"][:8]) or "• 없음")
        + "\n\n(전체 목록은 PC 화면 및 EXISTING_AUTOMATION_AND_SHEETS_REPORT.md 에 저장되었습니다!)"
    )
    ok = send_tg(tg_summary)
    print(f"[TELEGRAM] 보고서 텔레그램 발송 완료: ok={ok}")
    print("[OK] 기존 자동화 및 구글 시트 전수 분해 보고 완료 (파일 수정 0건)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```!]—Copy