# -*- coding: utf-8 -*-
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
