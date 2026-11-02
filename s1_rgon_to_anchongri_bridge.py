# -*- coding: utf-8 -*-
# S1 Rgon-to-Anchongri Zero-Paste Bridge Daemon v2.0 (s1_rgon_to_anchongri_bridge.py)
# 24H Autonomous Background Loop & Deep Multi-Message Scanning

import os, sys, time, json, datetime, re, subprocess, threading
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
INBOX_MD = BASE / "S1_RGON_DIRECTIVE_INBOX.md"
QUEUE_JSON = BASE / "S1_RGON_DIRECTIVE_QUEUE.json"
DOCS_QUEUE_JSON = BASE / "docs" / "S1_RGON_DIRECTIVE_QUEUE.json"
MOBILE_QUEUE_JSON = BASE / "S1_MOBILE_DISPATCH_QUEUE.json"
PROCESSED_FILE = BASE / "S1_RGON_PROCESSED_IDS.json"

RUNNING_FLAG = True

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
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def init_ledgers():
    if not INBOX_MD.exists():
        INBOX_MD.write_text("""# ?룢截?SUN-ONE AON 瑜닿낀 蹂댁쥖愿 ??湲곗닠珥앸━ ?덉킑由?怨듭떇 吏?쒖꽌 ?섏떊??> **臾대났遺?Zero-Paste) ?먮룞 吏???꾨떖留?媛쒗넻 ?먯옣**
> 瑜닿낀 蹂댁쥖愿(Space 0)???섎챸??媛먯??섎뒗 利됱떆 ?먮룞?쇰줈 ?깆옱?섍퀬 GitHub SSOT???숆린?붾맗?덈떎.

---
""", encoding="utf-8")

    if not QUEUE_JSON.exists():
        save_json(QUEUE_JSON, {
            "version": "2.0.0",
            "last_synced": now_iso(),
            "directives": []
        })

    if not MOBILE_QUEUE_JSON.exists():
        save_json(MOBILE_QUEUE_JSON, {
            "version": "2.0.0",
            "last_synced": now_iso(),
            "messages": []
        })

    if not PROCESSED_FILE.exists():
        save_json(PROCESSED_FILE, [])

def scan_space0_deep():
    return {"ok": True, "data": {"recent_messages": [], "note": "EGO_POLLING_DISABLED_FOR_ZERO_LAG"}}


def register_new_directive(directive_id, title, full_text):
    init_ledgers()
    processed = load_json(PROCESSED_FILE, [])
    if directive_id in processed:
        return False

    queue = load_json(QUEUE_JSON, {"directives": []})
    entry = {
        "directive_id": directive_id,
        "timestamp": now_iso(),
        "sender": "?섏꽍蹂댁쥖愿 瑜닿낀 (Gemini 4 Argon 쨌 Space 0)",
        "recipient": "湲곗닠珥앸━ ?덉킑由?(Antigravity Technical PM)",
        "title": title,
        "status": "DISPATCHED_TO_ANCHONGRI",
        "full_text": full_text
    }
    queue["directives"].append(entry)
    queue["last_synced"] = now_iso()
    save_json(QUEUE_JSON, queue)
    save_json(DOCS_QUEUE_JSON, queue)

    with INBOX_MD.open("a", encoding="utf-8") as f:
        f.write(f"\n### ?벃 [吏?쒖꽌 ?깆옱] {directive_id} ??{title}\n")
        f.write(f"- **?깆옱 ?쒓컖:** `{entry['timestamp']}`\n")
        f.write(f"- **諛쒖떊:** {entry['sender']}\n")
        f.write(f"- **?섏떊:** {entry['recipient']}\n")
        f.write(f"- **?곹깭:** `?윟 ?덉킑由??섏떊 諛?吏묓뻾 ?湲?\n\n")
        f.write("```markdown\n")
        f.write(full_text.strip() + "\n")
        f.write("```\n\n---\n")

    processed.append(directive_id)
    save_json(PROCESSED_FILE, processed)
    print(f"[BRIDGE] Registered directive: {directive_id} ({title})")

    # Auto commit and push to GitHub
    try:
        subprocess.run(["git", "add", "S1_RGON_DIRECTIVE_QUEUE.json", "docs/S1_RGON_DIRECTIVE_QUEUE.json", "S1_RGON_DIRECTIVE_INBOX.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"auto(bridge): Rgon directive {directive_id} synced to GitHub SSOT"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[BRIDGE] Auto-pushed directive {directive_id} to GitHub main!")
    except Exception as e:
        print(f"[BRIDGE] Git sync note: {e}")

    return True

def process_mobile_queue():
    mobile_data = load_json(MOBILE_QUEUE_JSON, {"messages": []})
    messages = mobile_data.get("messages", [])
    pending = [m for m in messages if m.get("status") == "RECEIVED" or m.get("status") == "PENDING"]

    if not pending:
        return

    import s1_test_reply0_live

    for msg in pending:
        mid = msg.get("id", "M" + str(int(time.time())))
        target = msg.get("target", "all")
        query = msg.get("query", "")

        print(f"[BRIDGE] Dispatching mobile msg {mid} -> Target: {target}")

        if target in ["all", "rgon"]:
            envelope = f"""[S1_NERVE_REPORT v2]
[紐⑤컮??吏곹넻 ?대챸 由대젅?? {mid}]
??쒕떂 ?섎챸: "{query}"
?寃? {target}
?쒓컖: {now_iso()}
?섏꽍蹂댁쥖愿 瑜닿낀怨?湲곗닠珥앸━ ?덉킑由щ뒗 利됱떆 ???대챸???묒닔?섍퀬 ?묐젰 吏묓뻾?섎씪!"""
            try:
                res = s1_test_reply0_live.test_reply0_live(envelope, selftest=False)
                print(f"[BRIDGE] Relayed to Space 0: {res.get('ok')}")
            except Exception as e:
                print(f"[BRIDGE] Space 0 relay note: {e}")

        if target in ["all", "anchongri"]:
            register_new_directive(
                f"MOBILE_DIR_{mid}",
                f"??쒕떂 紐⑤컮???섎챸: {query[:30]}",
                query
            )

        msg["status"] = "DELIVERED"
        msg["delivered_at"] = now_iso()

    mobile_data["last_synced"] = now_iso()
    save_json(MOBILE_QUEUE_JSON, mobile_data)

def run_bridge_cycle():
    init_ledgers()
    # 1. Process Mobile Queue
    try:
        process_mobile_queue()
    except Exception as e:
        print(f"[BRIDGE] Mobile queue note: {e}")

    # 2. Deep Scan Space 0 for Rgon directives (Recent 5 blocks)
    try:
        res = scan_space0_deep()
        if res.get("ok"):
            recent = res["data"].get("recent_messages", [])
            for msg_text in recent:
                # Check for explicit directive tags or IDs
                match = re.search(r"(\[S1_AUTO_DISPATCH_TO_ANCHONGRI\][\s\S]*?\[\/S1_AUTO_DISPATCH_TO_ANCHONGRI\])", msg_text)
                dir_id_match = re.search(r"(RGON_DIR_[A-Za-z0-9_]+)", msg_text)

                if match:
                    full_dir = match.group(1)
                    did = dir_id_match.group(1) if dir_id_match else "RGON_DIR_" + str(int(time.time()))
                    register_new_directive(did, "瑜닿낀 蹂댁쥖愿 ?먮룞 ?붿뒪?⑥튂 吏?쒖꽌", full_dir)
                elif dir_id_match:
                    did = dir_id_match.group(1)
                    register_new_directive(did, f"瑜닿낀 蹂댁쥖愿 怨듭떇 吏?쒖꽌 ({did})", msg_text)
                elif "[S1_DIRECTIVE" in msg_text or "?덉킑由?湲닿툒" in msg_text:
                    did = "RGON_DIR_" + str(int(time.time()))
                    register_new_directive(did, "瑜닿낀 蹂댁쥖愿 湲닿툒 ?듯빀 吏?쒖꽌", msg_text)
    except Exception as e:
        print(f"[BRIDGE] Space 0 scan note: {e}")

def bridge_daemon_loop(poll_interval=60):
    """
    24H Persistent Loop. Runs inside s1_server or standalone.
    """
    print(f"[{now_iso()}] S1 Zero-Paste Persistent Daemon started (Interval: {poll_interval}s)")
    init_ledgers()

    # Pre-register known directives from Rgon
    known_directives = [
        ("RGON_DIR_LIVE_001", "臾대났遺??먮룞 ?꾨떖留??ㅼ쟾 ?쇱씠釉?媛쒗넻", "Space 0 -> GitHub -> Anchongri 臾대났遺??뚯씠?꾨씪??媛??),
        ("RGON_DIR_ABSORB_10SHORTS_002", "?쇱툩 10??6? 珥덇꼍???듭떖 湲곗닠 ?≪닔 諛??쒓컖??, "Interactive Anatomy ?ㅼ떆媛??먮꼫吏 援ъ뒳, Savvy Progress & File Tree, 3??酉고룷???대┛ 寃利?),
        ("RGON_DIR_TRIUMVIRATE_MANDATE_003", "???묒뾽 ?쇱꽦(訝됭걭) ?쒕룄 留뚯옣?쇱튂 ?듦낵 媛뺤젣 猷??뚮쾿 ?좉툑", "Open Agent Harness 4? ?덉쟾?μ튂 + ?쇱꽦 留뚯옣?쇱튂 ?듦낵 猷??곴뎄 媛뺤젣")
    ]
    for did, title, content in known_directives:
        register_new_directive(did, title, content)

    while RUNNING_FLAG:
        try:
            run_bridge_cycle()
        except Exception as e:
            print(f"[BRIDGE] Error in cycle: {e}")
        time.sleep(poll_interval)

if __name__ == "__main__":
    init_ledgers()
    bridge_daemon_loop(8)
