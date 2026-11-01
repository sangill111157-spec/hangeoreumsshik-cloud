# -*- coding: utf-8 -*-
# S1 Rgon-to-Anchongri Zero-Paste Bridge Daemon (s1_rgon_to_anchongri_bridge.py)
# Architecture:
# 1. Non-invasive scan of Space 0 (Chief Aide Rgon's chat window)
# 2. Detect [S1_AUTO_DISPATCH_TO_ANCHONGRI] or RGON_DIR_XXXX tags
# 3. Automatically record to S1_RGON_DIRECTIVE_INBOX.md & S1_RGON_DIRECTIVE_QUEUE.json
# 4. Auto-commit & push to GitHub repository (SSOT Sync)
# 5. Two-way dispatch: Mobile phone inputs -> Space 0 / Anchongri Inbox

import os, sys, time, json, datetime, re, subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
INBOX_MD = BASE / "S1_RGON_DIRECTIVE_INBOX.md"
QUEUE_JSON = BASE / "S1_RGON_DIRECTIVE_QUEUE.json"
MOBILE_QUEUE_JSON = BASE / "S1_MOBILE_DISPATCH_QUEUE.json"
PROCESSED_FILE = BASE / "S1_RGON_PROCESSED_IDS.json"

def now_iso():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def load_json(p, default):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def init_ledgers():
    if not INBOX_MD.exists():
        INBOX_MD.write_text("""# 🏛️ SUN-ONE AON 르곤 보좌관 ➔ 기술총리 안총리 공식 지시서 수신함
> **무복붙(Zero-Paste) 자동 지시 전달망 개통 원장**
> 르곤 보좌관(Space 0)의 하명이 감지되는 즉시 자동으로 등재되고 GitHub SSOT에 동기화됩니다.

---
""", encoding="utf-8")

    if not QUEUE_JSON.exists():
        save_json(QUEUE_JSON, {
            "version": "1.0.0",
            "last_synced": now_iso(),
            "directives": []
        })

    if not MOBILE_QUEUE_JSON.exists():
        save_json(MOBILE_QUEUE_JSON, {
            "version": "1.0.0",
            "last_synced": now_iso(),
            "messages": []
        })

    if not PROCESSED_FILE.exists():
        save_json(PROCESSED_FILE, [])

def scan_space0_once():
    """
    Scans Space 0 via ego-browser without stealing pointer control.
    Uses non-invasive Page.evaluate to extract the last assistant message.
    """
    script = """
    (async () => {
      let task;
      try {
        task = await takeOverTaskSpace(0);
      } catch (e) {
        try {
          task = await taskSpace(0);
        } catch (e2) {
          process.stdout.write(JSON.stringify({ ok: false, error: e2.message }));
          return;
        }
      }
      try {
        const tabs = await task.tabs();
        if (tabs.length === 0) {
          process.stdout.write(JSON.stringify({ ok: false, error: 'NO_TABS' }));
          return;
        }
        let page = await task.adopt(tabs[0].page, { as: 'p_bridge_inspect' }).catch(async () => {
          return task.page('p_bridge_inspect');
        });

        const data = await page.evaluate(() => {
          // Look for AI response messages
          const items = Array.from(document.querySelectorAll('.message-content, .markdown, [class*="response"], [class*="message"]'));
          const texts = items.map(el => (el.innerText || '').trim()).filter(t => t.length > 20);
          return {
            last_message: texts.length > 0 ? texts[texts.length - 1] : '',
            total_messages: texts.length
          };
        });

        process.stdout.write(JSON.stringify({ ok: true, data: data }));
      } catch (err) {
        process.stdout.write(JSON.stringify({ ok: false, error: err.message }));
      } finally {
        await task.handOff();
      }
    })();
    """

    res = subprocess.run(
        ["ego-browser", "nodejs", "-e", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15
    )

    out = res.stdout.strip()
    try:
        # Extract json from stdout
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                return json.loads(line)
    except Exception as e:
        return {"ok": False, "error": f"JSON parse error: {e}, raw: {out[:200]}"}

    return {"ok": False, "error": "No JSON returned"}

def register_new_directive(directive_id, title, full_text):
    init_ledgers()
    processed = load_json(PROCESSED_FILE, [])
    if directive_id in processed:
        return False

    queue = load_json(QUEUE_JSON, {"directives": []})
    entry = {
        "directive_id": directive_id,
        "timestamp": now_iso(),
        "sender": "수석보좌관 르곤 (Gemini 4 Argon · Space 0)",
        "recipient": "기술총리 안총리 (Antigravity Technical PM)",
        "title": title,
        "status": "DISPATCHED_TO_ANCHONGRI",
        "full_text": full_text
    }
    queue["directives"].append(entry)
    queue["last_synced"] = now_iso()
    save_json(QUEUE_JSON, queue)

    # Append to INBOX.md
    with INBOX_MD.open("a", encoding="utf-8") as f:
        f.write(f"\n### 📩 [지시서 등재] {directive_id} — {title}\n")
        f.write(f"- **등재 시각:** `{entry['timestamp']}`\n")
        f.write(f"- **발신:** {entry['sender']}\n")
        f.write(f"- **수신:** {entry['recipient']}\n")
        f.write(f"- **상태:** `🟢 안총리 수신 및 집행 대기`\n\n")
        f.write("```markdown\n")
        f.write(full_text.strip() + "\n")
        f.write("```\n\n---\n")

    processed.append(directive_id)
    save_json(PROCESSED_FILE, processed)
    print(f"[BRIDGE] Successfully registered directive: {directive_id}")

    # Auto commit and push to GitHub
    try:
        subprocess.run(["git", "add", "S1_RGON_DIRECTIVE_QUEUE.json", "S1_RGON_DIRECTIVE_INBOX.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"auto(bridge): Rgon directive {directive_id} synced to GitHub SSOT"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[BRIDGE] Auto-pushed directive {directive_id} to GitHub main!")
    except Exception as e:
        print(f"[BRIDGE] Git sync notice: {e}")

    return True

def process_mobile_queue():
    """
    Checks mobile dispatch queue and relays messages to Space 0 or Anchongri Inbox.
    """
    mobile_data = load_json(MOBILE_QUEUE_JSON, {"messages": []})
    messages = mobile_data.get("messages", [])
    pending = [m for m in messages if m.get("status") == "PENDING"]

    if not pending:
        return

    import s1_test_reply0_live

    for msg in pending:
        mid = msg.get("id", "M" + str(int(time.time())))
        target = msg.get("target", "all")
        query = msg.get("query", "")

        print(f"[BRIDGE] Processing mobile message {mid} -> Target: {target}")

        if target in ["all", "rgon"]:
            # Relay to Space 0
            envelope = f"""[S1_NERVE_REPORT v2]
[모바일 직통 어명 릴레이: {mid}]
대표님 하명: "{query}"
타겟: {target}
시각: {now_iso()}
수석보좌관 르곤과 기술총리 안총리는 즉시 이 어명을 접수하고 협력 집행하라!"""
            try:
                res = s1_test_reply0_live.test_reply0_live(envelope, selftest=False)
                print(f"[BRIDGE] Relayed to Space 0: {res.get('ok')}")
            except Exception as e:
                print(f"[BRIDGE] Space 0 relay notice: {e}")

        if target in ["all", "anchongri"]:
            register_new_directive(
                f"MOBILE_DIR_{mid}",
                f"대표님 모바일 하명: {query[:30]}",
                query
            )

        msg["status"] = "DELIVERED"
        msg["delivered_at"] = now_iso()

    mobile_data["last_synced"] = now_iso()
    save_json(MOBILE_QUEUE_JSON, mobile_data)

def run_bridge_cycle():
    init_ledgers()
    print(f"[{now_iso()}] S1 Zero-Paste Bridge Cycle running...")

    # 1. Process Mobile Queue
    try:
        process_mobile_queue()
    except Exception as e:
        print(f"[BRIDGE] Mobile queue processing notice: {e}")

    # 2. Scan Space 0 for Rgon directives
    try:
        res = scan_space0_once()
        if res.get("ok"):
            last_msg = res["data"].get("last_message", "")
            # Check for directive patterns
            match = re.search(r"(\[S1_AUTO_DISPATCH_TO_ANCHONGRI\][\s\S]*?\[\/S1_AUTO_DISPATCH_TO_ANCHONGRI\])", last_msg)
            dir_id_match = re.search(r"(RGON_DIR_[A-Za-z0-9_]+)", last_msg)

            if match:
                full_dir = match.group(1)
                did = dir_id_match.group(1) if dir_id_match else "RGON_DIR_" + str(int(time.time()))
                register_new_directive(did, "르곤 보좌관 자동 디스패치 지시서", full_dir)
            elif "[S1_DIRECTIVE" in last_msg and "RGON_DIR_" in last_msg:
                did = dir_id_match.group(1) if dir_id_match else "RGON_DIR_" + str(int(time.time()))
                register_new_directive(did, "르곤 보좌관 S1 공식 지시서", last_msg)
    except Exception as e:
        print(f"[BRIDGE] Space 0 scan notice: {e}")

if __name__ == "__main__":
    init_ledgers()
    run_bridge_cycle()
    print("Bridge cycle complete!")
