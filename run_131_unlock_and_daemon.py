# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_131
import json, datetime, os, sys, time, hashlib, re, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/4] 6개 스페이스(Space 0~5)의 'Done Space' 잠금 딱지 일괄 해제(clear_all_spaces_lock) 중...")
try:
    ego.clear_all_spaces_lock()
except Exception as e:
    print("lock clear ref:", e)

print("[2/4] Done Space 자동 해제 기능이 내장된 파워셸 무인 복붙 데몬(s1_zero_paste_daemon.py v2) 기동 중...")
daemon_code = '''# -*- coding: utf-8 -*-
import json, os, sys, time, hashlib, re, subprocess, datetime
from pathlib import Path

BASE = Path(r"C:\\Users\\sangi\\Downloads\\shin-agent")
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

import S1_EGO_PROVEN_SKILL_MASTER as ego

STATE_FILE = BASE / "S1_ZERO_PASTE_DAEMON_STATE.json"
PID_FILE = BASE / "s1_zero_paste_daemon.pid"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"executed_ids": ["RGON_DIR_NEW_FOUNDATION_130", "RGON_DIR_NEW_FOUNDATION_131"], "executed_hashes": [], "runs": []}

def save_state(st):
    st["updated_at"] = datetime.datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")

def extract_python_payload(raw_block: str) -> str:
    txt = raw_block.strip()
    m = re.search(r"@'\\s*\\r?\\n(.*?)\\r?\\n'@", txt, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = []
    for ln in txt.splitlines():
        if ln.strip().startswith("@'") or ln.strip().startswith("'@"):
            continue
        if "Set-Content -Path" in ln:
            continue
        lines.append(ln)
    return "\\n".join(lines).strip()

def main():
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    st = load_state()
    try:
        ego.clear_all_spaces_lock()
        init_scan = ego.scan_and_auto_copy_space0()
        if isinstance(init_scan, dict):
            for b in init_scan.get("blocks", []):
                bh = hashlib.sha256(b.encode("utf-8")).hexdigest()[:16]
                if bh not in st["executed_hashes"]:
                    st["executed_hashes"].append(bh)
                m_id = re.search(r"DIRECTIVE_ID:\\s*(RGON_DIR_[A-Z0-9_]+)", b)
                if m_id and m_id.group(1) not in st["executed_ids"]:
                    st["executed_ids"].append(m_id.group(1))
        save_state(st)
    except Exception:
        pass

    while True:
        try:
            res = ego.scan_and_auto_copy_space0()
            if isinstance(res, dict) and res.get("ok") and not res.get("generating"):
                blocks = res.get("blocks", [])
                if blocks:
                    latest = blocks[-1]
                    bh = hashlib.sha256(latest.encode("utf-8")).hexdigest()[:16]
                    m_id = re.search(r"DIRECTIVE_ID:\\s*(RGON_DIR_[A-Z0-9_]+)", latest)
                    dir_id = m_id.group(1) if m_id else f"HASH_{bh}"

                    if bh not in st["executed_hashes"] and dir_id not in st["executed_ids"]:
                        st["executed_hashes"].append(bh)
                        st["executed_ids"].append(dir_id)
                        save_state(st)

                        ego.clear_all_spaces_lock()
                        py_code = extract_python_payload(latest)
                        if "import " in py_code and "[S1_AUTO_DISPATCH_TO_ANCHONGRI]" in py_code:
                            run_file = BASE / f"auto_exec_{dir_id.lower()}.py"
                            run_file.write_text(py_code, encoding="utf-8")
                            proc = subprocess.run(
                                [sys.executable, str(run_file)],
                                cwd=str(BASE), env=env, capture_output=True, text=True, timeout=240, creationflags=no_win
                            )
                            st["runs"].append({
                                "directive_id": dir_id,
                                "executed_at": datetime.datetime.now().isoformat(),
                                "returncode": proc.returncode,
                                "stderr_tail": (proc.stderr or "")[-200:]
                            })
                            st["runs"] = st["runs"][-50:]
                            save_state(st)
        except Exception:
            pass
        time.sleep(3.5)

if __name__ == "__main__":
    main()
'''

daemon_path = BASE / "s1_zero_paste_daemon.py"
daemon_path.write_text(daemon_code, encoding="utf-8")

pid_file = BASE / "s1_zero_paste_daemon.pid"
if pid_file.exists():
    try:
        old_pid = int(pid_file.read_text(encoding="utf-8").strip())
        subprocess.run(["taskkill", "/F", "/PID", str(old_pid)], capture_output=True, creationflags=no_win)
    except Exception:
        pass

daemon_proc = subprocess.Popen(
    [sys.executable, str(daemon_path)],
    cwd=str(BASE), env=env, creationflags=no_win, close_fds=True
)
time.sleep(1.2)
daemon_alive = (daemon_proc.poll() is None)

print("[3/4] 6번째 창(Space 5: Credit discount on Seedance 2.0 Mini) 입력창·모델 옵션만 단독 스캔 중 (Space 4 디스트로키드는 이미 복구완료되어 보존!)...")
js_s5_only = """
let task = null;
try {
  try { task = await takeOverTaskSpace(5); } catch (_) { try { task = await claimTaskSpace(5); } catch (__) { task = await taskSpace(5); } }
  const up = task.userPage ? task.userPage() : null;
  let page = up ? await task.adopt(up).catch(() => up) : null;
  if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
  const info = await page.evaluate(() => {
    const txt = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
    const placeholders = Array.from(document.querySelectorAll('textarea, input, [contenteditable="true"]'))
      .map(el => el.placeholder || el.getAttribute('placeholder') || (el.innerText || '').trim())
      .filter(Boolean);
    return { url: location.href, text: txt.slice(0, 900), inputs: placeholders.slice(0, 10) };
  });
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, s5: info }));
} catch (err) {
  process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: false, error: String(err) }));
} finally {
  try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
}
"""
s5_res = s1_ego.run_ego_js(js_s5_only, timeout=25)

print("[4/4] Space 1(솔)과 Space 2(오푸스)에 이미 떠 있는 최신 답변 수거 후 Space 0 자동 보고 전송 중...")
sol_last = ego.ask_and_harvest_side_room(1, "", wait_ms=800)
opus_last = ego.ask_and_harvest_side_room(2, "", wait_ms=800)

ego.clear_all_spaces_lock()

s5_info = s5_res.get("s5", {}) if isinstance(s5_res, dict) else {}
sol_t = str(sol_last.get("harvested", {}).get("latest_texts", [""])[-1]).replace("\n", " ")[:220] if isinstance(sol_last, dict) else ""
opus_t = str(opus_last.get("harvested", {}).get("latest_texts", [""])[-1]).replace("\n", " ")[:220] if isinstance(opus_last, dict) else ""

ego.send_auto_confirm_enter_space0(
    f"확인 (131호 Done잠금해제 & 무인데몬v2기동:{daemon_alive}[PID:{daemon_proc.pid}] | Space4디스트로키드복구완료 | Space5캡컷:[URL:{s5_info.get('url')} / 입력창:{s5_info.get('inputs')} / 본문:{str(s5_info.get('text',''))[:180]}] | 솔:{sol_t} | 오푸스:{opus_t})"
)
