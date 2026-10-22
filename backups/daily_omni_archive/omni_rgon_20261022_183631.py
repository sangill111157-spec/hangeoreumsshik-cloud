# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import subprocess
import urllib.request
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
ENV_LOCAL = os.path.join(ROOT, ".env.telegram.local")

KEY_FILES = [
    "auto_write_to_5_google_sheets.py",
    "sync_all_command_centers.py",
    "agency_stage_gate_scheduler.py",
    "cheongwadae_comm_engine.py",
    "cross_dept_synergy_engine.py",
    os.path.join("brain_basket", "external_kitchen_setup_receipt.json"),
    "CONNECT_AI_WORKFLOW.md",
]

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

def get_task_detail(task_name):
    try:
        p = subprocess.run(
            ["schtasks", "/query", "/tn", task_name, "/v", "/fo", "LIST"],
            capture_output=True,
            text=True,
            encoding="cp949",
            errors="replace",
            timeout=10,
        )
        out = []
        for ln in (p.stdout or "").splitlines():
            if any(k in ln for k in ("작업 이름", "실행할 작업", "시작 위치", "상태", "다음 실행", "TaskName", "Task To Run", "Start In")):
                out.append(ln.strip())
        return "\n  ".join(out[:8])
    except Exception as ex:
        return str(ex)

def summarize_file(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        return f"❌ {rel}: 파일 없음"
    txt = open(p, "r", encoding="utf-8", errors="replace").read()
    lines = txt.splitlines()

    if rel.endswith(".json"):
        return f"📄 {rel} ({len(lines)}줄):\n  " + txt[:500].replace("\n", "\n  ")

    funcs = re.findall(r"^def\s+([a-zA-Z0-9_]+)\s*\(", txt, re.M)
    sheets = re.findall(r"[a-zA-Z0-9-_]{35,50}", txt)
    urls = re.findall(r"https?://[^\s\"'>)]+", txt)
    head_comments = [l.strip() for l in lines[:25] if l.strip().startswith(("#", '"""', "'''")) or "시트" in l or "청사" in l]

    summary = [f"🐍 {rel} (총 {len(lines)}줄)"]
    if head_comments:
        summary.append("  • 설명: " + " / ".join(head_comments[:3])[:180])
    if funcs:
        summary.append("  • 주요 기능(함수): " + ", ".join(funcs[:10]))
    if sheets:
        summary.append("  • 연결 시트ID: " + ", ".join(sorted(list(set(sheets)))[:5]))
    if urls:
        summary.append("  • 연결 주소( 웹훅/API ): " + ", ".join(sorted(list(set(urls)))[:3]))
    return "\n".join(summary)

def main():
    report_lines = ["🔬 [보물 파일 2차 정밀 해부 보고서 (R0 읽기 전용)]\n"]

    report_lines.append("1️⃣ [윈도우 아침 7시 알람 상세]")
    for tname in (r"\ConnectAI_Daily_Briefing", r"\SHIN Family Daily Agent"):
        report_lines.append(f"• {tname}:\n  " + get_task_detail(tname))

    report_lines.append("\n2️⃣ [기존 핵심 자동화 & 5대 구글 시트 파일 해부]")
    for rel in KEY_FILES:
        report_lines.append(summarize_file(rel))

    full_text = "\n\n".join(report_lines)
    print(full_text)

    out_file = os.path.join(ROOT, "DEEP_DIVE_SHEETS_AND_TASKS.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(full_text)

    send_tg(full_text)
    print("[OK] 2차 정밀 해부 보고서 텔레그램 발송 완료!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
Copy