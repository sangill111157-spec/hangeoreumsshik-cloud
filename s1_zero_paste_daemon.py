# -*- coding: utf-8 -*-
import os, sys, time, re, json, subprocess
from playwright.sync_api import sync_playwright

BASE = r"C:\Users\sangi\Downloads\shin-agent"
STATE_FILE = os.path.join(BASE, "s1_zero_paste_state.json")
LOG_FILE = os.path.join(BASE, "s1_zero_paste_daemon.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_executed_num": 157}

def save_state(num):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_executed_num": num, "updated_at": time.strftime('%Y-%m-%d %H:%M:%S')}, f)
    except Exception:
        pass

def scan_once():
    state = load_state()
    last_num = int(state.get("last_executed_num", 157))
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=8000)
        for ctx in browser.contexts:
            for page in ctx.pages:
                if "genspark.ai" in (page.url or ""):
                    try:
                        # 자동 스크롤 및 전체 pre/code 텍스트 추출
                        blocks = page.evaluate("""() => {
                            try {
                                const scrollers = document.querySelectorAll('div, main');
                                scrollers.forEach(el => {
                                    if (el.scrollHeight > el.clientHeight + 200) {
                                        el.scrollTop = el.scrollHeight;
                                    }
                                });
                            } catch(e) {}
                            const els = Array.from(document.querySelectorAll('pre, code'));
                            return els.map(el => el.innerText || '');
                        }""")
                        best_num = last_num
                        best_code = None
                        for txt in blocks:
                            if "Set-Content" in txt and "run_" in txt:
                                m_num = re.search(r'run_(\d+)\.py', txt)
                                if m_num:
                                    num = int(m_num.group(1))
                                    if num > best_num:
                                        m_py = re.search(r"@'\s*\r?\n([\s\S]*?)\r?\n'@\s*\|\s*Set-Content", txt)
                                        if m_py:
                                            best_num = num
                                            best_code = m_py.group(1)
                        if best_code and best_num > last_num:
                            save_state(best_num)
                            py_path = os.path.join(BASE, f"run_{best_num}.py")
                            with open(py_path, "w", encoding="utf-8") as f:
                                f.write(best_code)
                            log(f"Executing run_{best_num}.py automatically...")
                            out_log = os.path.join(BASE, f"run_{best_num}_out.log")
                            with open(out_log, "w", encoding="utf-8") as lf:
                                subprocess.run([sys.executable, py_path], cwd=BASE, stdout=lf, stderr=lf, timeout=240)
                            log(f"Finished run_{best_num}.py")
                    except Exception as e:
                        log(f"Page eval error: {e}")

if __name__ == "__main__":
    log("Zero-Paste Daemon v5 started.")
    while True:
        try:
            scan_once()
        except Exception as e:
            log(f"Loop error: {e}")
        time.sleep(3.5)
