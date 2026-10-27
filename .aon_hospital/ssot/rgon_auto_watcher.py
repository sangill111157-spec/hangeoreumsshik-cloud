# -*- coding: utf-8 -*-
"""
RGON 오토 기어 3단 — 24시간 무토큰 문지기 로봇 & 텔레그램 리모컨 (rgon_auto_watcher.py)
- 1) 크롬 만능 소통창에서 [shin-agent 저장] 클릭 시 새 omni_*.py 자동 감지 -> 즉시 알림 및 승인 실행
- 2) C:\\Users\\sangi\\Downloads 및 하위 경로에 저장된 omni_*.py 즉시 shin-agent로 자동 이동 (os.replace)
- 3) 0.5초 감지 주기 및 수정시각(mtime) 갱신 즉시 감지
- 4) 백그라운드에서도 윈도우 화면 최상단(TopMost) MessageBox 팝업 보장
- 5) rgon_watcher.log 상세 로깅 기록
"""
# ---- RGON_NOWINDOW_SHIM_BEGIN (모든 subprocess 호출을 콘솔 창 없이 실행) ----
import subprocess as _rg_sp, sys as _rg_sys
if _rg_sys.platform == "win32" and not getattr(_rg_sp, "_rgon_patched", False):
    _rg_orig_init = _rg_sp.Popen.__init__
    def _rg_init(self, *a, **kw):
        kw["creationflags"] = kw.get("creationflags", 0) | 0x08000000
        si = kw.get("startupinfo")
        if si is None:
            si = _rg_sp.STARTUPINFO()
        si.dwFlags |= _rg_sp.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        kw["startupinfo"] = si
        _rg_orig_init(self, *a, **kw)
    _rg_sp.Popen.__init__ = _rg_init
    _rg_sp._rgon_patched = True
# ---- RGON_NOWINDOW_SHIM_END ----
import os
import re
import sys
import ast
import glob
import json
import time
import shutil
import ctypes
import threading
import subprocess
import urllib.request
import urllib.parse

ROOT = r"C:\Users\sangi\Downloads\shin-agent"
DOWNLOADS_DIR = r"C:\Users\sangi\Downloads"
LOG_FILE = os.path.join(ROOT, "rgon_watcher.log")
LOCK_FILE = os.path.join(ROOT, ".rgon_watcher.pid")
ENV_LOCAL = os.path.join(ROOT, ".env.telegram.local")
ENV_TRADING = r"C:\trading\package\nvda_trading_system\backend\.env"

def log_msg(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_telegram_creds():
    token, chat_id = None, None
    for p in (ENV_LOCAL, ENV_TRADING):
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if line.startswith("TELEGRAM_BOT_TOKEN="):
                            token = line.split("=", 1)[1].strip()
                        elif line.startswith("TELEGRAM_CHAT_ID="):
                            chat_id = line.split("=", 1)[1].strip()
                if token and chat_id:
                    break
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
    except Exception as ex:
        log_msg(f"tg_send 실패: {ex}")
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
    log_msg(f"execute_omni_file 시작: {fname} (출처: {source_tag})")
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
        log_msg(f"execute_omni_file 완료: {status_icon}")
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
        log_msg(f"execute_omni_file 예외: {ex}")
        tg_send(f"⚠️ [RGON 실행 오류] {fname}: {ex}")
        return False

def set_clipboard(text):
    try:
        proc = subprocess.Popen(["clip.exe"], stdin=subprocess.PIPE, shell=True)
        proc.communicate(input=text.encode("utf-8", errors="replace"))
        return True
    except Exception as ex:
        log_msg(f"클립보드 적재 오류: {ex}")
        return False

def prompt_ahn_queue_box(fname, text_snippet):
    log_msg(f"안총리 텍스트 큐 안내 팝업 시도: {fname}")
    MB_OK = 0x00000000
    MB_ICONINFORMATION = 0x00000040
    MB_TOPMOST = 0x00040000
    MB_SETFOREGROUND = 0x00010000
    MB_SYSTEMMODAL = 0x00001000
    flags = MB_OK | MB_ICONINFORMATION | MB_TOPMOST | MB_SETFOREGROUND | MB_SYSTEMMODAL
    preview = (text_snippet[:250] + "...") if len(text_snippet) > 250 else text_snippet
    ctypes.windll.user32.MessageBoxW(
        0,
        f"📮 [안총리 실행 큐 접수 완료!]\n파일: {fname}\n\n내용이 클립보드 및 ahn_inbox_latest.txt 에 자동 복사되었습니다.\n안총리 대화창에서 바로 [Ctrl + V] 로 붙여넣으실 수 있습니다!\n\n[내용 미리보기]\n{preview}",
        "RGON 안총리 실행 큐 데스크",
        flags,
    )

def scan_and_relocate_downloads():
    """C:\\Users\\sangi\\Downloads 폴더의 omni_*.py, omni_queue_*.py, ahn_queue_* 파일을 shin-agent 폴더로 자동 이동"""
    moved = []
    patterns = [
        os.path.join(DOWNLOADS_DIR, "omni_*.py"),
        os.path.join(DOWNLOADS_DIR, "omni_queue_*.py"),
        os.path.join(DOWNLOADS_DIR, "ahn_queue_*.*"),
    ]
    try:
        cand_files = []
        for pat in patterns:
            cand_files.extend(glob.glob(pat))
        for p in cand_files:
            if os.path.abspath(os.path.dirname(p)) == os.path.abspath(ROOT):
                continue
            base = os.path.basename(p)
            dest = os.path.join(ROOT, base)
            try:
                os.replace(p, dest)
                log_msg(f"자동 이동 성공: {p} -> {dest}")
                moved.append(dest)
            except Exception as ex:
                try:
                    shutil.move(p, dest)
                    log_msg(f"shutil 이동 성공: {p} -> {dest}")
                    moved.append(dest)
                except Exception as ex2:
                    log_msg(f"파일 이동 실패 {p}: {ex2}")
    except Exception as ex:
        log_msg(f"scan_and_relocate 오류: {ex}")
    return moved

def check_and_process_ahn_text_queue():
    """shin-agent 내부의 ahn_queue_*.txt 또는 ahn_queue_*.* 파일 감지 및 안총리 인박스 처리"""
    txt_files = glob.glob(os.path.join(ROOT, "ahn_queue_*.*"))
    for tf in txt_files:
        try:
            base = os.path.basename(tf)
            if base.endswith(".processed"):
                continue
            with open(tf, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            # 1) ahn_inbox_latest.txt 갱신
            inbox_p = os.path.join(ROOT, "ahn_inbox_latest.txt")
            with open(inbox_p, "w", encoding="utf-8") as f:
                f.write(content)
            # 2) 클립보드 자동 적재
            set_clipboard(content)
            log_msg(f"📮 [안총리 지시서 큐 접수] {base} -> ahn_inbox_latest.txt 및 클립보드 복사 완료")
            # 3) 텔레그램 알림
            snippet = (content[:200] + "...") if len(content) > 200 else content
            tg_send(
                f"📮 [안총리 실행 큐: 지시서 접수]\n"
                f"📄 파일: {base}\n"
                f"📋 PC 클립보드 및 ahn_inbox_latest.txt 적재 완료!\n"
                f"안총리 창에서 바로 Ctrl+V 하시면 됩니다.\n\n"
                f"[요약]\n{snippet}"
            )
            # 4) 안내 팝업
            threading.Thread(target=prompt_ahn_queue_box, args=(base, content), daemon=True).start()
            # 5) 처리 완료 마킹
            os.rename(tf, tf + ".processed")
        except Exception as ex:
            log_msg(f"ahn_text_queue 처리 오류 {tf}: {ex}")

def get_latest_omni():
    # 먼저 Downloads 폴더 스캔 및 이동 수행
    scan_and_relocate_downloads()
    # 안총리 텍스트 큐 파일 처리
    check_and_process_ahn_text_queue()
    # omni_*.py 및 omni_queue_*.py 모두 포함
    files = glob.glob(os.path.join(ROOT, "omni_*.py"))
    if not files:
        return None, 0
    latest = max(files, key=os.path.getmtime)
    return latest, os.path.getmtime(latest)

def build_briefing_text():
    snap_p = os.path.join(ROOT, "rgon_brain_snapshot.json")
    if not os.path.isfile(snap_p):
        return "브리핑 파일이 없습니다."
    try:
        with open(snap_p, "r", encoding="utf-8", errors="replace") as f:
            snap = json.load(f)
        pulse = snap.get("agency_pulse") or {}
        brief = pulse.get("daily_briefing") or {}
        lines = [
            brief.get("headline") or f"👑 [RGON 6대 청사 브리핑] 박동 #{pulse.get('beat_count')}",
            f"🔹 D1 퀀트: {brief.get('D1_quant', 'OK')}",
            f"🔹 D2 바이럴: {brief.get('D2_viral', 'OK')}",
            f"🔹 D3 미디어: {brief.get('D3_media', 'OK')}",
            f"🔹 D4 홍익: {brief.get('D4_hongik', 'OK')}",
            f"🔹 D5 가디언: {brief.get('D5_guardian', 'OK')}",
            f"🔹 D6 트레저리: {brief.get('D6_treasury', 'OK')}",
            f"🎯 추천 행동: {brief.get('action_top1', '-')}",
        ]
        return "\n".join(lines)
    except Exception as ex:
        return f"브리핑 읽기 오류: {ex}"

def prompt_pc_box(fname, fpath, pending_state):
    log_msg(f"화면 최상단(TopMost) 승인창 팝업 시도: {fname}")
    MB_YESNO = 0x00000004
    MB_ICONQUESTION = 0x00000020
    MB_TOPMOST = 0x00040000
    MB_SETFOREGROUND = 0x00010000
    MB_SYSTEMMODAL = 0x00001000
    flags = MB_YESNO | MB_ICONQUESTION | MB_TOPMOST | MB_SETFOREGROUND | MB_SYSTEMMODAL
    ans = ctypes.windll.user32.MessageBoxW(
        0,
        f"새 코드 [{fname}] 가 감지되었습니다!\n지금 바로 실행하고 텔레그램 보고할까요?\n\n(모바일 텔레그램 'Y' 또는 '실행'으로도 승인됩니다!)",
        "RGON 오토 기어 3단 (자동 승인)",
        flags,
    )
    log_msg(f"MessageBox 응답 결과: ans={ans} (6=YES)")
    if ans == 6 and pending_state.get("file") == fpath and not pending_state.get("executed"):
        pending_state["executed"] = True
        execute_omni_file(fpath, source_tag="PC 원클릭 승인")

def main_loop():
    log_msg("=== rgon_auto_watcher 가동 시작 (감지주기: 0.5초) ===")
    if os.path.isfile(LOCK_FILE):
        try:
            old_pid = int(open(LOCK_FILE).read().strip())
            if old_pid != os.getpid():
                subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], capture_output=True)
                log_msg(f"이전 프로세스 정리: PID {old_pid}")
        except Exception:
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    latest_file, last_mtime = get_latest_omni()
    log_msg(f"초기 최신 파일: {latest_file} (mtime: {last_mtime})")
    _, tg_offset = tg_get_updates(offset=None)
    pending = {"file": latest_file, "mtime": last_mtime, "executed": True}

    while True:
        try:
            cur_file, cur_mtime = get_latest_omni()
            # 수정시각(mtime) 갱신 또는 새 파일 감지
            if cur_file and (cur_file != pending.get("file") or cur_mtime > last_mtime + 0.1):
                last_mtime = cur_mtime
                fname = os.path.basename(cur_file)
                log_msg(f"🎯 [새 코드 감지!] 파일: {fname}, mtime: {cur_mtime}")
                pending = {"file": cur_file, "mtime": cur_mtime, "executed": False}
                tg_send(
                    f"👑 [RGON 새 코드 자동 감지 성공!]\n"
                    f"📄 파일: {fname}\n"
                    f"🔔 PC 화면에서 [예(Y)]를 누르시거나, 이 텔레그램 대화창에 'Y' 또는 '실행'이라고 답장하시면 즉시 실행됩니다!"
                )
                t = threading.Thread(target=prompt_pc_box, args=(fname, cur_file, pending), daemon=True)
                t.start()

            # 텔레그램 명령 폴링
            msgs, tg_offset = tg_get_updates(offset=tg_offset)
            for m in msgs:
                cmd = m.lower().strip()
                log_msg(f"텔레그램 명령 수신: {cmd}")
                if cmd in ("y", "yes", "예", "/run", "실행", "승인"):
                    target = pending.get("file") or cur_file
                    if target and os.path.isfile(target):
                        pending["executed"] = True
                        tg_send(f"🚀 텔레그램 승인 확인! [{os.path.basename(target)}] 을 실행합니다...")
                        execute_omni_file(target, source_tag="텔레그램 원격 승인")
                    else:
                        tg_send("실행할 대상 파일(omni_*.py)이 없습니다.")
                elif cmd in ("박동", "/pulse", "펄스"):
                    pulse_py = os.path.join(ROOT, "scripts", "rgon_agency_pulse.py")
                    subprocess.run([sys.executable, "-X", "utf8", pulse_py], cwd=ROOT, capture_output=True)
                    tg_send("👑 [6대 청사 무인 박동 완료!]\n\n" + build_briefing_text())
                elif cmd in ("브리핑", "/brief", "보고", "요약", "키워드"):
                    tg_send(build_briefing_text())
                elif cmd in ("시트", "시트동기화", "구글시트", "/sheet", "/sheets"):
                    tg_send("📊 [4대 독대실 시트 무인 동기화] 시작합니다...")
                    s1 = os.path.join(ROOT, "auto_write_to_5_google_sheets.py")
                    s2 = os.path.join(ROOT, "sync_all_command_centers.py")
                    r1 = subprocess.run([sys.executable, "-X", "utf8", s1], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120) if os.path.isfile(s1) else None
                    r2 = subprocess.run([sys.executable, "-X", "utf8", s2], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120) if os.path.isfile(s2) else None
                    out1 = "\n".join((r1.stdout or "").strip().splitlines()[-5:]) if r1 else "없음"
                    out2 = "\n".join((r2.stdout or "").strip().splitlines()[-5:]) if r2 else "없음"
                    tg_send(f"✅ [구글 시트 동기화 완료!]\n\n[5대 시트 결과]\n{out1}\n\n[4대 커맨드센터 동기화]\n{out2}")
                elif cmd in ("시너지", "합동", "연계", "/synergy"):
                    tg_send("🔗 [1~6청사 이어달리기 시너지] 시작합니다...")
                    s3 = os.path.join(ROOT, "cross_dept_synergy_engine.py")
                    r3 = subprocess.run([sys.executable, "-X", "utf8", s3], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120) if os.path.isfile(s3) else None
                    out3 = "\n".join((r3.stdout or "").strip().splitlines()[-8:]) if r3 else "없음"
                    tg_send(f"✅ [1~6청사 시너지 완료!]\n{out3}")
                elif cmd in ("도움말", "/help", "?"):
                    tg_send(
                        "👑 [RGON 무토큰 인공지능 비서실 명령어]\n"
                        "👉 Y 또는 실행 : 방금 감지된 최신 코드 즉시 실행\n"
                        "👉 박동 : 6대 청사 펄스 즉시 가동 및 브리핑\n"
                        "👉 브리핑 : 최신 6대 청사 핵심 브리핑 출력\n"
                        "👉 시트 : 4대 구글 시트 즉시 동기화\n"
                        "👉 시너지 : 1~6청사 이어달리기 시너지 가동\n"
                        "(소모 토큰: 0원!)"
                    )
        except Exception as ex:
            log_msg(f"main_loop 예외: {ex}")
        time.sleep(0.5)


# === RGON_HTTP_QUEUE_SERVER_V2 ===
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

QUEUE_PORTS = [1024, 1100, 1500, 2600, 3000, 3500, 4000, 4500, 5000, 5050, 5381, 7777, 8000, 8080, 8099, 8501, 8765, 8766, 8787, 9000, 9999, 10000, 11115, 11707, 15000, 20000, 21474, 40000, 50000, 60000, 65001, 65535]

class RGONQueueHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_cors(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self._send_cors(200)

    def do_GET(self):
        self._send_cors(200)
        self.wfile.write(b'{"ok": true, "status": "online", "job": null}')

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else ""
        text_payload = raw
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                text_payload = (
                    data.get("code") or data.get("text") or data.get("content")
                    or data.get("prompt") or data.get("payload") or raw
                )
        except Exception:
            pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        is_py = any(k in text_payload for k in ("import ", "def ", "if __name__", "# -*-"))
        if is_py:
            out_path = os.path.join(ROOT, f"omni_queue_{ts}.py")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text_payload)
        else:
            out_path = os.path.join(ROOT, f"ahn_queue_{ts}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text_payload)
            inbox = os.path.join(ROOT, "ahn_inbox_latest.txt")
            with open(inbox, "w", encoding="utf-8") as f:
                f.write(text_payload)
            try:
                subprocess.run(["clip.exe"], input=text_payload.encode("utf-16le"), timeout=5)
            except Exception:
                pass
            try:
                send_tg(f"📮 [안총리 실행 큐 접수 성공!]\n클립보드 및 ahn_inbox_latest.txt 적재 완료!\n\n{text_payload[:300]}")
            except Exception:
                pass

        self._send_cors(200)
        resp = json.dumps({"ok": True, "status": "queued", "file": os.path.basename(out_path)})
        self.wfile.write(resp.encode("utf-8"))


def _start_queue_servers():
    for port in QUEUE_PORTS:
        def _serve(p=port):
            try:
                srv = HTTPServer(("127.0.0.1", p), RGONQueueHandler)
                srv.serve_forever()
            except Exception:
                pass
        t = threading.Thread(target=_serve, daemon=True)
        t.start()

_start_queue_servers()


if __name__ == "__main__":
    main_loop()
