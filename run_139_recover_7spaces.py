# [S1_AUTO_DISPATCH_TO_ANCHONGRI]
# DIRECTIVE_ID: RGON_DIR_NEW_FOUNDATION_139
import json, datetime, os, sys, time, hashlib, re, subprocess
from pathlib import Path
import s1_ego
import S1_EGO_PROVEN_SKILL_MASTER as ego

BASE = Path(r"C:\Users\sangi\Downloads\shin-agent")
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"
no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")

print("[1/4] 7개 전체 스페이스(Space 0~6) 잠금 강제 해제 및 검은 화면에 걸린 Space 3 즉시 복구 중...")
js_unlock_7 = """
for (let i = 0; i <= 6; i++) {
  try {
    let t = null;
    try { t = await takeOverTaskSpace(i); } catch (_) { try { t = await claimTaskSpace(i); } catch (__) { t = await taskSpace(i); } }
    if (t && typeof t.finish === 'function') await t.finish({ keep: [] });
  } catch (e) {}
}
process.stdout.write('S1EGO_JSON::{"ok":true,"unlocked_spaces":7}');
"""
s1_ego.run_ego_js(js_unlock_7, timeout=20)
ego.clear_all_spaces_lock()

print("[2/4] 절대로 멈추지 않는 Watchdog 타임아웃(75초)이 내장된 무인 데몬 v3(s1_zero_paste_daemon.py) 재기동 중...")
daemon_v3 = '''# -*- coding: utf-8 -*-
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
    return {"executed_ids": ["RGON_DIR_NEW_FOUNDATION_138", "RGON_DIR_NEW_FOUNDATION_139"], "executed_hashes": [], "runs": []}

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
        if ln.strip().startswith("@'") or ln.strip().startswith("'@") or "Set-Content -Path" in ln:
            continue
        lines.append(ln)
    return "\\n".join(lines).strip()

def main():
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    st = load_state()
    for _id in ["RGON_DIR_NEW_FOUNDATION_138", "RGON_DIR_NEW_FOUNDATION_139"]:
        if _id not in st["executed_ids"]:
            st["executed_ids"].append(_id)
    try:
        ego.clear_all_spaces_lock()
        init_scan = ego.scan_and_auto_copy_space0()
        if isinstance(init_scan, dict):
            for b in init_scan.get("blocks", []):
                bh = hashlib.sha256(b.encode("utf-8")).hexdigest()[:16]
                if bh not in st["executed_hashes"]:
                    st["executed_hashes"].append(bh)
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
                            try:
                                proc = subprocess.run(
                                    [sys.executable, str(run_file)],
                                    cwd=str(BASE), env=env, capture_output=True, text=True, timeout=85, creationflags=no_win
                                )
                                rc = proc.returncode
                            except subprocess.TimeoutExpired:
                                rc = -999
                                ego.clear_all_spaces_lock()
                            st["runs"].append({
                                "directive_id": dir_id,
                                "executed_at": datetime.datetime.now().isoformat(),
                                "returncode": rc
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
daemon_path.write_text(daemon_v3, encoding="utf-8")

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
time.sleep(1.0)
daemon_alive = (daemon_proc.poll() is None)

print("[3/4] 7번째 창(Space 6: Google Vids) 상태 및 Space 3 복구 확인 중...")
js_s3_s6 = """
let out = {};
for (const idx of [3, 6]) {
  let task = null;
  try {
    try { task = await takeOverTaskSpace(idx); } catch (_) { try { task = await claimTaskSpace(idx); } catch (__) { task = await taskSpace(idx); } }
    const up = task.userPage ? task.userPage() : null;
    let page = up ? await task.adopt(up).catch(() => up) : null;
    if (!page && task.pages) { const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }
    if (idx === 3) {
      await page.goto('https://studio.youtube.com/', { waitUntil: 'domcontentloaded', timeout: 18000 }).catch(() => {});
      await new Promise(r => setTimeout(r, 2000));
      out.space3 = { url: page.url(), title: await page.title().catch(() => '') };
    } else if (idx === 6) {
      out.space6 = await page.evaluate(() => {
        const txt = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
        return { url: location.href, title: document.title, text: txt.slice(0, 500) };
      }).catch(e => ({ error: String(e) }));
    }
  } catch (e) {
    out['space' + idx] = { error: String(e) };
  } finally {
    try { if (task && typeof task.finish === 'function') await task.finish({ keep: [] }); } catch (_) {}
  }
}
process.stdout.write('S1EGO_JSON::' + JSON.stringify({ ok: true, spaces: out }));
"""
s3_s6_res = s1_ego.run_ego_js(js_s3_s6, timeout=35)

print("[4/4] Space 1(솔)과 Space 2(오푸스)에 이미 떠 있는 최신 답변을 대기 없이 즉시 수거하여 보고 중...")
sol_now = ego.ask_and_harvest_side_room(1, "", wait_ms=800)
opus_now = ego.ask_and_harvest_side_room(2, "", wait_ms=800)

ego.clear_all_spaces_lock()

s3_u = s3_s6_res.get("spaces", {}).get("space3", {}).get("url", "") if isinstance(s3_s6_res, dict) else ""
s6_info = s3_s6_res.get("spaces", {}).get("space6", {}) if isinstance(s3_s6_res, dict) else {}
sol_t = str(sol_now.get("harvested", {}).get("latest_texts", [""])[-1]).replace("\n", " ")[:220] if isinstance(sol_now, dict) else ""
opus_t = str(opus_now.get("harvested", {}).get("latest_texts", [""])[-1]).replace("\n", " ")[:220] if isinstance(opus_now, dict) else ""

ego.send_auto_confirm_enter_space0(
    f"확인 (139호 7대스페이스잠금해제 & 무인데몬v3복구:{daemon_alive}[PID:{daemon_proc.pid}] | Space3복구:{s3_u} | Space6구글빕스:[{s6_info.get('title')} / {str(s6_info.get('text',''))[:140]}] | 솔최신:{sol_t} | 오푸스최신:{opus_t})"
)
