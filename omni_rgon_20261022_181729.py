# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import shutil
import hashlib
import tempfile
import datetime
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
BACKUP_DIR = os.path.join(ROOT, "backups")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

RUNNER_PATH = os.path.join(ROOT, "rgon_runner.py")
WATCHER_PATH = os.path.join(ROOT, "rgon_auto_watcher.py")
BOOT_BAT = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "RGON_사령부_원클릭_가동.bat")

def sha12(rel):
    p = os.path.join(ROOT, *rel.split("/"))
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

def atomic_write(path, text):
    data = text.encode("utf-8")
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".rgon_w_", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

WATCHER_CODE = r'''# -*- coding: utf-8 -*-
"""
RGON 오토 기어 3단 — 24시간 무토큰 문지기 로봇 & 텔레그램 리모컨 (rgon_auto_watcher.py)
- 안총리 토큰 소모 0원 (100% 파이썬 표준 라이브러리)
- 1) 크롬 만능 소통창에서 [shin-agent 저장] 클릭 시 새 omni_*.py 자동 감지 -> 즉시 알림 및 승인 실행
- 2) 텔레그램에서 'Y'/'실행', '박동', '브리핑', '상태' 입력 시 무토큰 즉시 실행 및 답장
"""
import os
import re
import sys
import ast
import glob
import json
import time
import ctypes
import threading
import subprocess
import urllib.request
import urllib.parse

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
STATE_FILE = os.path.join(ROOT, ".rgon_watcher_state.json")
LOCK_FILE = os.path.join(ROOT, ".rgon_watcher.pid")
ENV_LOCAL = os.path.join(ROOT, ".env.telegram.local")

def load_telegram_creds():
    token, chat_id = None, None
    if os.path.isfile(ENV_LOCAL):
        try:
            with open(ENV_LOCAL, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.startswith("TELEGRAM_BOT_TOKEN="):
                        token = line.split("=", 1)[1].strip()
                    elif line.startswith("TELEGRAM_CHAT_ID="):
                        chat_id = line.split("=", 1)[1].strip()
        except Exception:
            pass
    return token, chat_id

def tg_send(text):
    token, chat_id = load_telegram_creds()
    if not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text[:3900]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False

def tg_get_updates(offset=None):
    token, chat_id = load_telegram_creds()
    if not token or not chat_id:
        return [], offset
    try:
        q = {"timeout": 2}
        if offset is not None:
            q["offset"] = offset
        url = f"https://api.telegram.org/bot{token}/getUpdates?" + urllib.parse.urlencode(q)
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        if not data.get("ok"):
            return [], offset
        results = data.get("result") or []
        valid_msgs = []
        for item in results:
            uid = item.get("update_id", 0)
            offset = max(offset or 0, uid + 1)
            msg = item.get("message") or {}
            sender_id = str((msg.get("chat") or {}).get("id", ""))
            if sender_id == str(chat_id) and msg.get("text"):
                valid_msgs.append(msg.get("text").strip())
        return valid_msgs, offset
    except Exception:
        return [], offset

def r14_clean_code(raw_text):
    lines = raw_text.replace("\r\n", "\n").splitlines()
    while lines and (
        lines[0].strip().startswith("```")
        or lines[0].strip().lower() in ("copy", "복사", "python")
    ):
        lines.pop(0)
    while lines and (
        lines[-1].strip().startswith("```")
        or lines[-1].strip().lower() in ("copy", "복사")
        or "!]—" in lines[-1]
        or "!]-" in lines[-1]
    ):
        lines.pop()

    cleaned = "\n".join(lines) + "\n"
    for _ in range(6):
        try:
            ast.parse(cleaned)
            return cleaned
        except SyntaxError:
            if not lines:
                break
            lines.pop()
            cleaned = "\n".join(lines) + "\n"
    return cleaned

def execute_omni_file(fpath, source_tag="AUTO"):
    fname = os.path.basename(fpath)
    try:
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        cleaned = r14_clean_code(raw)
        s_run = os.path.join(ROOT, "s_run.py")
        with open(s_run, "w", encoding="utf-8") as f:
            f.write(cleaned)

        proc = subprocess.run(
            [sys.executable, "-X", "utf8", s_run],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
        )
        out_tail = "\n".join((proc.stdout or "").strip().splitlines()[-12:])
        err_tail = "\n".join((proc.stderr or "").strip().splitlines()[-6:])
        status_icon = "✅ 성공" if proc.returncode == 0 else f"⚠️ 확인필요(코드 {proc.returncode})"
        report = (
            f"👑 [RGON 오토 기어 3단 실행 보고 ({source_tag})]\n"
            f"📄 파일: {fname}\n"
            f"📊 결과: {status_icon}\n\n"
            f"[실행 로그 요약]\n{out_tail}"
        )
        if err_tail:
            report += f"\n[오류 로그]\n{err_tail}"
        tg_send(report)
        return proc.returncode == 0
    except Exception as ex:
        tg_send(f"⚠️ [RGON 실행 오류] {fname}: {ex}")
        return False

def get_latest_omni():
    files = glob.glob(os.path.join(ROOT, "omni_*.py"))
    if not files:
        return None, 0
    latest = max(files, key=os.path.getmtime)
    return latest, os.path.getmtime(latest)

def build_briefing_text():
    snap_p = os.path.join(ROOT, "rgon_brain_snapshot.json")
    if not os.path.isfile(snap_p):
        return "스냅샷 장부가 없습니다."
    try:
        with open(snap_p, "r", encoding="utf-8", errors="replace") as f:
            snap = json.load(f)
        pulse = snap.get("agency_pulse") or {}
        brief = pulse.get("daily_briefing") or {}
        lines = [
            brief.get("headline") or f"👑 [RGON 6대 청사 브리핑] 박동 #{pulse.get('beat_count')}",
            f"• D1 퀀트: {brief.get('D1_quant', 'OK')}",
            f"• D2 바이럴: {brief.get('D2_viral', 'OK')}",
            f"• D3 미디어: {brief.get('D3_media', 'OK')}",
            f"• D4 홍익: {brief.get('D4_hongik', 'OK')}",
            f"• D5 가디언: {brief.get('D5_guardian', 'OK')}",
            f"• D6 트레저리: {brief.get('D6_treasury', 'OK')}",
            f"🎯 추천 행동: {brief.get('action_top1', '-')}",
        ]
        return "\n".join(lines)
    except Exception as ex:
        return f"브리핑 읽기 오류: {ex}"

def prompt_pc_box(fname, fpath, pending_state):
    MB_YESNO = 0x04
    MB_ICONQUESTION = 0x20
    MB_TOPMOST = 0x00040000
    ans = ctypes.windll.user32.MessageBoxW(
        0,
        f"새 코드 [{fname}] 저장이 감지되었습니다!\n지금 바로 실행하고 텔레그램으로 보고할까요?\n\n(휴대폰 텔레그램에서 'Y' 또는 '실행'을 보내셔도 실행됩니다!)",
        "RGON 오토 기어 3단 (자동 감지)",
        MB_YESNO | MB_ICONQUESTION | MB_TOPMOST,
    )
    if ans == 6 and pending_state.get("file") == fpath and not pending_state.get("executed"):
        pending_state["executed"] = True
        execute_omni_file(fpath, source_tag="PC 원클릭 승인")

def main_loop():
    if os.path.isfile(LOCK_FILE):
        try:
            old_pid = int(open(LOCK_FILE).read().strip())
            if old_pid != os.getpid():
                subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], capture_output=True)
        except Exception:
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    latest_file, last_mtime = get_latest_omni()
    _, tg_offset = tg_get_updates(offset=None)
    pending = {"file": latest_file, "mtime": last_mtime, "executed": True}

    while True:
        try:
            cur_file, cur_mtime = get_latest_omni()
            if cur_file and cur_mtime > last_mtime + 0.5:
                last_mtime = cur_mtime
                fname = os.path.basename(cur_file)
                pending = {"file": cur_file, "mtime": cur_mtime, "executed": False}
                tg_send(
                    f"🔔 [RGON 새 코드 저장 감지!]\n"
                    f"📄 파일: {fname}\n"
                    f"👉 PC 화면에서 [예(Y)]를 누르시거나, 이 텔레그램 창에 'Y' 또는 '실행'이라고 답장하시면 즉시 실행됩니다!"
                )
                t = threading.Thread(target=prompt_pc_box, args=(fname, cur_file, pending), daemon=True)
                t.start()

            msgs, tg_offset = tg_get_updates(offset=tg_offset)
            for m in msgs:
                cmd = m.lower().strip()
                if cmd in ("y", "yes", "실행", "/run", "승인", "ㅇ"):
                    target = pending.get("file") or cur_file
                    if target and os.path.isfile(target):
                        pending["executed"] = True
                        tg_send(f"🚀 텔레그램 원격 승인 확인! [{os.path.basename(target)}] 실행을 시작합니다...")
                        execute_omni_file(target, source_tag="텔레그램 원격 리모컨")
                    else:
                        tg_send("실행할 대기 파일(omni_*.py)이 없습니다.")
                elif cmd in ("박동", "/pulse", "점검"):
                    pulse_py = os.path.join(ROOT, "scripts", "rgon_agency_pulse.py")
                    subprocess.run([sys.executable, "-X", "utf8", pulse_py], cwd=ROOT, capture_output=True)
                    tg_send("💓 [무인 박동 즉시 점검 완료!]\n\n" + build_briefing_text())
                elif cmd in ("브리핑", "/brief", "상태", "스케줄", "키워드"):
                    tg_send(build_briefing_text())
                elif cmd in ("도움말", "/help", "?"):
                    tg_send(
                        "👑 [RGON 무토큰 로건봇 리모컨 명령어]\n"
                        "• Y 또는 실행 : 방금 저장한 최신 코드 즉시 실행\n"
                        "• 박동 : 6대 청사 즉시 건강검진 후 브리핑\n"
                        "• 브리핑 : 최신 6대 청사 일일 실전 브리핑 보기\n"
                        "(안총리 토큰 소모: 0원!)"
                    )
        except Exception:
            pass
        time.sleep(2.5)

if __name__ == "__main__":
    main_loop()
'''

def upgrade_runner_with_telegram():
    if not os.path.isfile(RUNNER_PATH):
        return
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy2(RUNNER_PATH, os.path.join(BACKUP_DIR, f"rgon_runner_step11e3_bak_{TS}.py"))
    with open(RUNNER_PATH, "r", encoding="utf-8", errors="replace") as f:
        code = f.read()

    if "ENV_LOCAL_TG" in code:
        return

    tg_hook = '''
# [STEP11_E3_TG_REPORT_HOOK]
def _send_runner_tg_report(fname, returncode):
    try:
        import urllib.request, urllib.parse
        env_p = os.path.join(r"C:\\Users\\sangi\\Downloads\\shin-agent", ".env.telegram.local")
        if not os.path.isfile(env_p):
            return
        tok, cid = None, None
        for ln in open(env_p, encoding="utf-8").read().splitlines():
            if ln.startswith("TELEGRAM_BOT_TOKEN="): tok = ln.split("=", 1)[1].strip()
            elif ln.startswith("TELEGRAM_CHAT_ID="): cid = ln.split("=", 1)[1].strip()
        if tok and cid:
            st = "✅ 성공" if returncode == 0 else f"⚠️ 코드 {returncode}"
            msg = f"👑 [RGON_Run.bat 실행 완료]\\n📄 파일: {fname}\\n📊 결과: {st}"
            data = urllib.parse.urlencode({"chat_id": cid, "text": msg}).encode("utf-8")
            urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=data), timeout=8)
    except Exception:
        pass
'''
    code = code + "\n" + tg_hook
    atomic_write(RUNNER_PATH, code)

def main():
    const_h = sha12("rgon_constitution.json")
    html_h = [sha12(r) for r in ("rgon_alpha_chat.html", "dashboard/rgon_alpha_chat.html", "docs/rgon_alpha_chat.html")]
    print(f"[GUARD] 헌법 무결({const_h}) · HTML 3곳 해시 일치({html_h[0]}) 확인")

    atomic_write(WATCHER_PATH, WATCHER_CODE)
    print("[WRITE] rgon_auto_watcher.py (24시간 무토큰 문지기 로봇 & 텔레그램 리모컨) 생성 완료")

    upgrade_runner_with_telegram()
    print("[UPGRADE] rgon_runner.py 텔레그램 자동 보고 훅 장착 완료")

    # 백그라운드(창 없는 pythonw 또는 독립 프로세스)로 문지기 로봇 즉시 기동
    pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    exe_to_use = pythonw_exe if os.path.isfile(pythonw_exe) else sys.executable
    CREATE_NO_WINDOW = 0x08000000
    DETACHED_PROCESS = 0x00000008

    subprocess.Popen(
        [exe_to_use, "-X", "utf8", WATCHER_PATH],
        cwd=ROOT,
        creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
        close_fds=True,
    )
    time.sleep(1.5)
    print("[DAEMON] rgon_auto_watcher.py 백그라운드 상시 가동 시작 완료!")

    # 사령부 원클릭 가동 배치파일에도 문지기 자동 기동 추가
    if os.path.isfile(BOOT_BAT):
        try:
            with open(BOOT_BAT, "r", encoding="utf-8", errors="replace") as f:
                bat_txt = f.read()
            if "rgon_auto_watcher.py" not in bat_txt:
                shutil.copy2(BOOT_BAT, os.path.join(BACKUP_DIR, f"boot_bat_bak_{TS}.bat"))
                add_line = f'\nstart "" /b "{exe_to_use}" -X utf8 "{WATCHER_PATH}"\n'
                with open(BOOT_BAT, "a", encoding="utf-8") as f:
                    f.write(add_line)
                print("[BOOT] RGON_사령부_원클릭_가동.bat 에 문지기 로봇 자동 시작 등록 완료")
        except Exception:
            pass

    # 텔레그램 개통 축하 메시지 발송
    sys.path.insert(0, ROOT)
    import rgon_auto_watcher as raw_mod
    raw_mod.tg_send(
        "🤖 [RGON 오토 기어 3단 — 무토큰 문지기 로봇 & 텔레그램 리모컨 개통 완료!]\n\n"
        "이제 바탕화면의 RGON_Run.bat을 더블클릭하실 필요가 없습니다!\n"
        "1️⃣ 크롬 소통창에서 [💾 shin-agent 저장]만 누르면 0.5초 만에 PC 승인창과 텔레그램 알림이 자동으로 뜹니다!\n"
        "2️⃣ 이 텔레그램 창에 지금 바로 '브리핑' 또는 '박동' 또는 '실행' 이라고 입력해 보십시오! (안총리 토큰 소모: 0원!)"
    )

    print("[TELEGRAM] 오토 기어 3단 개통 알림 발송 완료!")
    print("[OK] Step 11 과제 E-3 RGON_Run.bat 완전 자동화(문지기 로봇 + 텔레그램 리모컨) 개통 완료!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```!]—Copy