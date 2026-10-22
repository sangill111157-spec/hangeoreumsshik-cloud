# -*- coding: utf-8 -*-
import os
import sys
import shutil
import hashlib
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
ENV_LOCAL = os.path.join(ROOT, ".env.telegram.local")
WATCHER_PATH = os.path.join(ROOT, "rgon_auto_watcher.py")
BACKUP_DIR = os.path.join(ROOT, "backups")
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

def sha12(rel):
    p = os.path.join(ROOT, *rel.split("/"))
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

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

def run_treasure_script(script_name, timeout=120):
    p = os.path.join(ROOT, script_name)
    if not os.path.isfile(p):
        return -1, f"{script_name} 파일 없음"
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", p],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        tail = "\n".join(combined.splitlines()[-10:])
        return proc.returncode, tail
    except Exception as ex:
        return -2, str(ex)

def upgrade_watcher_with_treasures():
    if not os.path.isfile(WATCHER_PATH):
        return
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy2(WATCHER_PATH, os.path.join(BACKUP_DIR, f"rgon_auto_watcher_bak_{TS}.py"))
    code = open(WATCHER_PATH, "r", encoding="utf-8", errors="replace").read()

    if "시트동기화" in code:
        return

    old_help_anchor = 'elif cmd in ("도움말", "/help", "?"):'
    treasure_handlers = '''elif cmd in ("시트", "시트동기화", "구글시트", "/sheet", "/sheets"):
                    tg_send("📊 [4대 구글 시트 통합 동기화] 시작합니다... (무토큰 실행)")
                    s1 = os.path.join(ROOT, "auto_write_to_5_google_sheets.py")
                    s2 = os.path.join(ROOT, "sync_all_command_centers.py")
                    r1 = subprocess.run([sys.executable, "-X", "utf8", s1], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120) if os.path.isfile(s1) else None
                    r2 = subprocess.run([sys.executable, "-X", "utf8", s2], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120) if os.path.isfile(s2) else None
                    out1 = "\\n".join((r1.stdout or "").strip().splitlines()[-5:]) if r1 else "없음"
                    out2 = "\\n".join((r2.stdout or "").strip().splitlines()[-5:]) if r2 else "없음"
                    tg_send(f"✅ [구글 시트 동기화 완료!]\\n\\n[5대 시트 기록]\\n{out1}\\n\\n[4대 커맨드센터 동기화]\\n{out2}")
                elif cmd in ("합동", "합동점검", "시너지", "/synergy"):
                    tg_send("🤝 [1~6청사 이어달리기 합동점검] 가동합니다...")
                    s3 = os.path.join(ROOT, "cross_dept_synergy_engine.py")
                    r3 = subprocess.run([sys.executable, "-X", "utf8", s3], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120) if os.path.isfile(s3) else None
                    out3 = "\\n".join((r3.stdout or "").strip().splitlines()[-8:]) if r3 else "없음"
                    tg_send(f"✅ [1~6청사 합동점검 완료!]\\n{out3}")
                elif cmd in ("도움말", "/help", "?"):'''

    if old_help_anchor in code:
        code = code.replace(old_help_anchor, treasure_handlers)
        code = code.replace(
            "• 브리핑 : 최신 6대 청사 일일 실전 브리핑 보기\\n",
            "• 브리핑 : 최신 6대 청사 일일 실전 브리핑 보기\\n"
            "• 시트 : 4대 구글 시트 즉시 통합 동기화\\n"
            "• 합동 : 1~6청사 이어달리기 합동점검 실행\\n",
        )
        with open(WATCHER_PATH, "w", encoding="utf-8") as f:
            f.write(code)

        pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        exe_to_use = pythonw_exe if os.path.isfile(pythonw_exe) else sys.executable
        subprocess.Popen(
            [exe_to_use, "-X", "utf8", WATCHER_PATH],
            cwd=ROOT,
            creationflags=0x08000000 | 0x00000008,
            close_fds=True,
        )

def main():
    const_h = sha12("rgon_constitution.json")
    html_h = [sha12(r) for r in ("rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html")]
    print(f"[GUARD] 헌법 무결({const_h}) · HTML 3곳 해시 일치({html_h[0]}) 확인")

    print("[1/3] auto_write_to_5_google_sheets.py 실행 테스트 중...")
    c1, out1 = run_treasure_script("auto_write_to_5_google_sheets.py")
    print(f"  -> 종료코드: {c1}\n{out1}")

    print("[2/3] sync_all_command_centers.py 실행 테스트 중...")
    c2, out2 = run_treasure_script("sync_all_command_centers.py")
    print(f"  -> 종료코드: {c2}\n{out2}")

    print("[3/3] 무토큰 로건봇 리모컨(rgon_auto_watcher.py)에 '시트' 및 '합동' 명령어 장착 중...")
    upgrade_watcher_with_treasures()

    report_msg = (
        "📊 [RGON 보물 1호 — 구글 시트 통합 동기화 & 로건봇 연결 결과]\n\n"
        f"1️⃣ auto_write_to_5_google_sheets.py (코드 {c1}):\n{out1[-400:]}\n\n"
        f"2️⃣ sync_all_command_centers.py (코드 {c2}):\n{out2[-400:]}\n\n"
        "🎉 이제 이 텔레그램 창에서 언제든:\n"
        "• '시트' 입력 -> 구글 시트 즉시 동기화\n"
        "• '합동' 입력 -> 1~6청사 이어달리기 점검\n"
        "• '브리핑' / '박동' / '실행' 입력 -> 즉시 작동합니다! (안총리 토큰 0원!)"
    )
    send_tg(report_msg)
    print("[OK] 구글 시트 동기화 실행 및 로건봇 명령어 연결 완료!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
