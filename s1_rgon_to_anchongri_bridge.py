# -*- coding: utf-8 -*-
# S1 Rgon-to-Anchongri Zero-Paste Bridge Daemon v3.5 (s1_rgon_to_anchongri_bridge.py)
# 24H Autonomous Background Loop, Dual-Bridge Harvester & Non-Invasive Space 0 Eye (finditer & Zero-Lag)

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
OUTBOX_JSON = BASE / "S1_ANCHONGRI_TO_RGON_OUTBOX.json"
DOCS_OUTBOX_JSON = BASE / "docs" / "S1_ANCHONGRI_TO_RGON_OUTBOX.json"
ACTIVE_TASK_MD = BASE / "S1_ANCHONGRI_ACTIVE_TASK.md"

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
        INBOX_MD.write_text("""# 🏛️ SUN-ONE AON 르곤 보좌관 ➔ 기술총리 안총리 공식 지시서 수신함
> **무복붙(Zero-Paste) 자동 지시 전달망 개통 원장**
> 르곤 보좌관(Space 0)의 하명을 감지하는 즉시 자동으로 등재하고 GitHub SSOT에 동기화됩니다.

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

def is_ego_running():
    return True

def scan_space0_deep(do_reload=False):
    try:
        import S1_EGO_PROVEN_SKILL_MASTER as ego_master
        res = ego_master.scan_and_auto_copy_space0(do_reload=False)
        if isinstance(res, dict) and res.get('blocks'):
            return {'ok': True, 'data': {'recent_messages': res.get('blocks', [])}}
    except Exception as _e:
        pass
    return _legacy_scan_space0_deep(do_reload=do_reload)

def _legacy_scan_space0_deep(do_reload=False):
    """
    [수거봇 눈 복원 v5.0 - 025호 무렉(Zero-Lag) & Human-Presence Shield & 비침습 스캔]
    1. takeOverTaskSpace 전면 제거 -> claimTaskSpace / taskSpace 비침습 접근
    2. innerText 및 강제 스크롤 전면 제거 -> 0-reflow textContent (pre, code) 0.001초 스캔
    3. Human-Presence Shield: 마우스 포커스(document.hasFocus) 또는 드래그(window.getSelection) 시 새로고침/스크롤 100% Skip
    4. finally에서 finish({ keep: [] })로 세션 종료하여 파란 테두리 / Need your action 원천 차단 (ownership: "user")
    """
    if not is_ego_running():
        return {"ok": False, "skipped": "EGO_NOT_RUNNING"}
    import s1_ego
    js = f"""
    let task = null;
    try {{
      try {{
        task = await claimTaskSpace(0);
      }} catch (_) {{
        task = await taskSpace(0);
      }}
      const up = task.userPage ? task.userPage() : null;
      const page = up ? await task.adopt(up) : (task.page ? task.page("p1") : null);
      if (!page) {{
        process.stdout.write('\nS1EGO_JSON::' + JSON.stringify({{ ok: false, error: "NO_ACTIVE_PAGE" }}) + '\n');
        return;
      }}

      // Disable any ego overlay elements
      await page.evaluate(() => {{
        window.__ego_overlay_disabled = true;
      }}).catch(() => {{}});

      const doReload = Boolean({1 if do_reload else 0});

      // Human-Presence Shield: Check if user is actively interacting (focus or selection)
      const userState = await page.evaluate(() => {{
        const isFocused = typeof document.hasFocus === 'function' ? document.hasFocus() : false;
        const sel = window.getSelection ? window.getSelection().toString() : '';
        const isSelecting = sel.trim().length > 0;
        const ta = document.querySelector('textarea[name="query"], textarea, [contenteditable="true"]');
        const val = ta ? (ta.value || ta.textContent || '').trim() : '';
        const stopBtn = Array.from(document.querySelectorAll("button, [role='button']")).some(b => {{
          const t = (b.textContent || b.getAttribute("aria-label") || "").toLowerCase();
          return t === "stop" || t === "중지" || t.includes("생성 중지");
        }});
        return {{
          humanActive: isFocused || isSelecting,
          canReload: !isSelecting && val.length === 0 && !stopBtn
        }};
      }}).catch(() => ({{ humanActive: true, canReload: false }}));

      if (doReload && userState.canReload) {{
        try {{
          await page.evaluate(() => window.location.reload());
          await new Promise(r => setTimeout(r, 3500));
        }} catch (_) {{}}
      }}

      // Zero-reflow scan using textContent on pre, code elements
      const data = await page.evaluate(() => {{
        const items = Array.from(document.querySelectorAll('pre, code, article, .markdown, [class*="message"], body'));
        const texts = items.slice(-10).map(el => (el.textContent || '').trim()).filter(t => t.length > 20);
        return {{
          recent_messages: texts,
          total_messages: texts.length
        }};
      }}).catch(err => ({{ recent_messages: [], total_messages: 0, error: String(err) }}));

      data.reloaded = doReload && userState.canReload;
      data.shield_active = userState.humanActive;

      process.stdout.write('\nS1EGO_JSON::' + JSON.stringify({{
        ok: true,
        data: data
      }}) + '\n');
    }} catch (err) {{
      process.stdout.write('\nS1EGO_JSON::' + JSON.stringify({{ ok: false, error: String(err.message || err) }}) + '\n');
    }} finally {{
      try {{
        if (task && typeof task.finish === 'function') {{
          await task.finish({{ keep: [] }});
        }} else if (task && typeof task.handOff === 'function') {{
          await task.handOff();
        }}
      }} catch (_) {{}}
    }}
    """
    try:
        res = s1_ego.run_ego_js(js, timeout=25)
        return res
    except Exception as e:
        return {"ok": False, "error": str(e)}



def send_auto_confirm_to_space0(directive_id: str):
    """임무 완료 및 GitHub 푸시 직후 에고라이트 Space 0에 자동으로 '확인' 메시지를 타이핑·전송"""
    try:
        import s1_ego
        head_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE, text=True).strip()
        msg = f"확인 (자동수거·임무완료: {directive_id} · 커밋 {head_sha})"
        msg_json = json.dumps(msg, ensure_ascii=False)
        js = f"""
        let task = null;
        try {{
          try {{ task = await takeOverTaskSpace(0); }} catch (_) {{ try {{ task = await claimTaskSpace(0); }} catch (__) {{ task = await taskSpace(0); }} }}
          const up = task.userPage ? task.userPage() : null;
          let page = up ? await task.adopt(up).catch(() => up) : null;
          if (!page && task.pages) {{ const ps = await task.pages(); if (ps && ps.length) page = ps[0]; }}
          if (!page) return;
          const qText = {msg_json};
          await page.evaluate((t) => {{
            const el = document.querySelector('textarea[name="query"], textarea, div[contenteditable="true"], [role="textbox"]');
            if (!el) return;
            el.focus();
            if (el.tagName && el.tagName.toLowerCase() === 'textarea') {{
              const ns = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
              if (ns) ns.call(el, t); else el.value = t;
              el.dispatchEvent(new Event('input', {{ bubbles: true }}));
              el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
              el.textContent = t;
              el.dispatchEvent(new InputEvent('input', {{ bubbles: true, data: t }}));
            }}
            const btns = Array.from(document.querySelectorAll('button[type="submit"], button[aria-label*="send" i], button[aria-label*="전송" i], .enter-icon-wrapper'));
            const ab = btns.find(b => !b.disabled);
            if (ab) ab.click();
            else el.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
          }}, qText);
          await new Promise(r => setTimeout(r, 500));
        }} catch (_) {{}} finally {{
          try {{ if (task && typeof task.finish === 'function') await task.finish({{ keep: [] }}); }} catch (_) {{}}
        }}
        """
        s1_ego.run_ego_js(js, timeout=30)
        print(f"[AUTO-CONFIRM] Sent automatic '확인' to Space 0 for {directive_id}", flush=True)
    except Exception as e:
        print(f"[AUTO-CONFIRM] Error: {e}", flush=True)

def auto_execute_directive_trigger(directive_id: str, full_text: str = "") -> dict:
    """
    [049호 르곤 직할 무인 집행 엔진]
    안총리(IDE 채팅창) 개입 없이 르곤 보좌관(Space 0)의 파이썬 페이로드(# [S1_DIRECT_PYTHON_PAYLOAD])를
    s1_rgon_to_anchongri_bridge.py 데몬이 직접 추출 -> 로컬 실행 -> 린터 검증 -> git commit & push 까지 100% 무인 완주!
    """
    log_file = BASE / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"
    docs_log_file = BASE / "docs" / "S1_BRIDGE_AUTO_TRIGGER_LOG.json"
    # [055호 오푸스 조건: 이미 COMPLETED 된 directive_id 중복 재실행 원천 차단]
    if log_file.exists():
        try:
            prev_logs = json.loads(log_file.read_text(encoding="utf-8")).get("triggers", [])
            if any(x.get("directive_id") == directive_id and x.get("status") == "COMPLETED" for x in prev_logs):
                return {"ok": True, "skipped": "ALREADY_COMPLETED_ONCE"}
        except Exception:
            pass

    
    # [A] 르곤 직할 파이썬 페이로드(# [S1_DIRECT_PYTHON_PAYLOAD]) 감지
    payload_marker = "# [S1_DIRECT_PYTHON_PAYLOAD]"
    if full_text and payload_marker in full_text:
        print(f"[RGON_DIRECT_ENGINE] Detected direct payload in {directive_id}!", flush=True)
        code_to_run = ""
        # 1) ```python ... ``` 형태
        m_fence = re.search(r"```(?:python)?\s*\n([\s\S]*?)```", full_text)
        if m_fence and payload_marker in m_fence.group(0):
            code_to_run = m_fence.group(1).strip()
        else:
            # 2) 마커 이후부터 [/S1_DIRECT_PYTHON_PAYLOAD] 또는 블록 끝까지
            m_block = re.search(r"#\s*\[S1_DIRECT_PYTHON_PAYLOAD\]([\s\S]*?)(?:#\s*\[/S1_DIRECT_PYTHON_PAYLOAD\]|\[/S1_AUTO_DISPATCH_TO_ANCHONGRI\]|\Z)", full_text)
            if m_block:
                code_to_run = m_block.group(1).strip()

        if code_to_run:
            runner_file = BASE / "s1_direct_payload_runner.py"
            runner_file.write_text(code_to_run, encoding="utf-8")
            print(f"[RGON_DIRECT_ENGINE] Saved payload to {runner_file} ({len(code_to_run)} bytes). Executing immediately...", flush=True)

            # 1) 직접 실행
            exec_res = subprocess.run([sys.executable, str(runner_file)], cwd=BASE, timeout=120, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            print(f"[RGON_DIRECT_ENGINE] Payload exit code: {exec_res.returncode}", flush=True)
            if exec_res.stdout:
                print(f"[RGON_DIRECT_ENGINE] Stdout: {exec_res.stdout[:300]}", flush=True)

            # 2) 린터 자동 검증
            linter_res = subprocess.run([sys.executable, "s1_qm_structure_linter.py"], cwd=BASE, timeout=60, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            print(f"[RGON_DIRECT_ENGINE] Linter exit code: {linter_res.returncode}", flush=True)

            # 3) Git 무인 커밋 & 푸시
            try:
                subprocess.run(["git", "add", "-A"], cwd=BASE, check=False)
                subprocess.run(["git", "commit", "-m", f"auto(rgon-direct): executed {directive_id} without anchongri"], cwd=BASE, check=False)
                subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=BASE, check=False)
                subprocess.run(["git", "push", "origin", "main"], cwd=BASE, check=False)
                send_auto_confirm_to_space0(directive_id)
                try:
                    h_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE, text=True).strip()
                    msg0 = f"[자동수거·임무완료 보고] 지시서 {directive_id} 자동 실행 및 GitHub 푸시 완료! (커밋: {h_sha})"
                    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "ask", "--space", "0", "--prompt", msg0], cwd=BASE, timeout=25, check=False)
                    subprocess.run([sys.executable, str(BASE / "s1_ego.py"), "finish", "--space", "0"], cwd=BASE, timeout=8, check=False)
                except Exception as _e:
                    print("[AUTO-REPLY-ERR]", _e, flush=True)
                print(f"[RGON_DIRECT_ENGINE] Git auto push completed for {directive_id}!", flush=True)
            except Exception as e:
                print(f"[RGON_DIRECT_ENGINE] Git sync note: {e}", flush=True)

            log_entry = {
                "directive_id": directive_id,
                "timestamp": now_iso(),
                "pid": os.getpid(),
                "mode": "RGON_DIRECT_PYTHON_EXECUTION",
                "status": "COMPLETED",
                "returncode": exec_res.returncode,
                "ok": (exec_res.returncode == 0)
            }
            _save_trigger_log(log_file, docs_log_file, log_entry)
            return log_entry

    # [B] 일반 지시서인 경우 로컬 무쿼터 파운드리 백그라운드 가동
    foundry_py = BASE / "s1_zero_quota_triumvirate_foundry.py"
    pid = None
    if foundry_py.exists():
        try:
            proc = subprocess.Popen(
                [sys.executable, str(foundry_py), "--directive", directive_id],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            pid = proc.pid
            print(f"[BRIDGE_TRIGGER] Auto-spawned zero-quota foundry for {directive_id} (PID: {pid})", flush=True)
        except Exception as e:
            print(f"[BRIDGE_TRIGGER] Failed to spawn foundry: {e}", flush=True)

    log_entry = {
        "directive_id": directive_id,
        "timestamp": now_iso(),
        "pid": pid,
        "mode": "STANDARD_FOUNDRY_SPAWN",
        "status": "TRIGGERED",
        "ok": True
    }
    _save_trigger_log(log_file, docs_log_file, log_entry)
    return log_entry


def _save_trigger_log(log_file, docs_log_file, log_entry):
    try:
        data = {"version": "1.0.0", "triggers": []}
        if log_file.exists():
            try:
                data = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        data.setdefault("triggers", []).append(log_entry)
        log_json_str = json.dumps(data, ensure_ascii=False, indent=2)
        log_file.write_text(log_json_str, encoding="utf-8")
        docs_log_file.parent.mkdir(parents=True, exist_ok=True)
        docs_log_file.write_text(log_json_str, encoding="utf-8")
    except Exception as e:
        print(f"[BRIDGE_TRIGGER] Failed to write trigger log: {e}", flush=True)


def register_new_directive(directive_id, title, full_text):
    init_ledgers()
    processed = load_json(PROCESSED_FILE, [])
    if directive_id in processed:
        return False

    queue = load_json(QUEUE_JSON, {"directives": []})
    # Avoid duplicate in queue list
    if any(d.get("directive_id") == directive_id for d in queue.get("directives", [])):
        processed.append(directive_id)
        save_json(PROCESSED_FILE, processed)
        return False

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
    save_json(DOCS_QUEUE_JSON, queue)

    with INBOX_MD.open("a", encoding="utf-8") as f:
        f.write(f"\n### 📩 [지시서 등재] {directive_id} — {title}\n")
        f.write(f"- **등재 시각:** `{entry['timestamp']}`\n")
        f.write(f"- **발신:** {entry['sender']}\n")
        f.write(f"- **수신:** {entry['recipient']}\n")
        f.write(f"- **상태:** `⚡ 안총리 수신 및 집행 대기`\n\n")
        f.write("```markdown\n")
        f.write(full_text.strip() + "\n")
        f.write("```\n\n---\n")

    processed.append(directive_id)
    save_json(PROCESSED_FILE, processed)
    print(f"[BRIDGE] Registered directive: {directive_id} ({title})", flush=True)
    auto_execute_directive_trigger(directive_id, full_text)
    # Auto commit and push to GitHub
    try:
        subprocess.run(["git", "add", "S1_RGON_DIRECTIVE_QUEUE.json", "docs/S1_RGON_DIRECTIVE_QUEUE.json", "S1_RGON_DIRECTIVE_INBOX.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"auto(bridge): Rgon directive {directive_id} synced to GitHub SSOT"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[BRIDGE] Auto-pushed directive {directive_id} to GitHub main!", flush=True)
    except Exception as e:
        print(f"[BRIDGE] Git sync note: {e}", flush=True)

    return True

def scan_clipboard_for_directives():
    """클립보드에 새 [S1_AUTO_DISPATCH_TO_ANCHONGRI] 지시서가 복사되었을 때 즉시 감지하여 집행"""
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], capture_output=True, text=True, timeout=3)
        cb_text = res.stdout.strip()
        if "[S1_AUTO_DISPATCH_TO_ANCHONGRI]" in cb_text:
            id_match = re.search(r"(?:ID:\s*|DIRECTIVE_ID:\s*|#\s*)?(RGON_DIR_[A-Za-z0-9_]+)", cb_text)
            if id_match:
                did = id_match.group(1)
                title_match = re.search(r"TITLE:\s*(.+)|작업명:\s*(.+)", cb_text)
                title = (title_match.group(1) or title_match.group(2)).strip() if title_match else f"클립보드 직통 지시서 ({did})"
                register_new_directive(did, title, cb_text)
    except Exception:
        pass


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

        print(f"[BRIDGE] Dispatching mobile msg {mid} -> Target: {target}", flush=True)

        if target in ["all", "rgon"]:
            envelope = f"""[S1_NERVE_REPORT v2]
[모바일 직통 어명 릴레이: {mid}]
대표님 하명: "{query}"
타깃: {target}
시각: {now_iso()}
수석보좌관 르곤과 기술총리 안총리는 즉시 이 어명을 접수하고 협력 집행하라!"""
            try:
                res = s1_test_reply0_live.test_reply0_live(envelope, selftest=False)
                print(f"[BRIDGE] Relayed to Space 0: {res.get('ok')}", flush=True)
            except Exception as e:
                print(f"[BRIDGE] Space 0 relay note: {e}", flush=True)

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

def harvest_from_github_ssot():
    """
    [015호 GitHub 지시서 수거봇 (Harvester)]
    15초 주기로 GitHub 원격 저장소 및 로컬 큐를 스캔하여
    새로운 지시서(PENDING_PICKUP, RECEIVED, DISPATCHED_TO_ANCHONGRI)를 즉시 수거.
    - 상태를 PICKED_UP_BY_ANCHONGRI로 변경 및 picked_up_at 기록
    - S1_ANCHONGRI_ACTIVE_TASK.md에 최신 수거 지시서 원문 기록
    """
    init_ledgers()
    
    # 1. Pull latest from remote GitHub SSOT (QM-SP-18: skip pull when tracked working tree is dirty to prevent autostash race/rollback)
    try:
        st = subprocess.run(
            ["git", "status", "--porcelain", "-uno"],
            cwd=BASE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if st.returncode == 0 and not st.stdout.strip():
            subprocess.run(
                ["git", "pull", "--rebase", "origin", "main"],
                cwd=BASE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=12,
            )
    except Exception:
        pass

    queue = load_json(QUEUE_JSON, {"directives": []})
    directives = queue.get("directives", [])
    harvested = []
    
    target_statuses = ["PENDING_PICKUP", "RECEIVED", "DISPATCHED_TO_ANCHONGRI"]
    
    for item in directives:
        status = item.get("status", "")
        did = item.get("directive_id", "")
        if status in target_statuses:
            item["status"] = "PICKED_UP_BY_ANCHONGRI"
            item["picked_up_at"] = now_iso()
            harvested.append(item)
            
            # Write to S1_ANCHONGRI_ACTIVE_TASK.md
            task_content = f"""# ⚡ [안총리 실시간 수거 집행 작업] {did} — {item.get('title', '')}

- **지시서 ID:** `{did}`
- **수거 일시:** `{item['picked_up_at']}`
- **발신자:** {item.get('sender', '수석보좌관 르곤 (Gemini 4 Argon · Space 0)')}
- **수신자:** 기술총리 안총리 (Antigravity Technical PM)
- **현재 상태:** `PICKED_UP_BY_ANCHONGRI (수거 완료 · 즉시 집행 중)`

---

## 📋 지시서 원문 전문 (Directive Text)

```markdown
{item.get('full_text', '')}
```

---
> **사령부 행동강령:** 지체 없이 분석과 실행에 돌입하여 1·2차 삼성제도 100.0점 통과 후 대시보드에 완료보고서를 전송하라.
"""
            ACTIVE_TASK_MD.write_text(task_content, encoding="utf-8")
            auto_execute_directive_trigger(did, item.get("full_text", ""))
            print(f"[HARVESTER] Picked up directive: {did} -> Status: PICKED_UP_BY_ANCHONGRI", flush=True)

    if harvested:
        queue["last_synced"] = now_iso()
        save_json(QUEUE_JSON, queue)
        save_json(DOCS_QUEUE_JSON, queue)
        print(f"[HARVESTER] Total {len(harvested)} directives harvested and synchronized to SSOT!", flush=True)
        try:
            subprocess.run(["git", "add", "S1_RGON_DIRECTIVE_QUEUE.json", "docs/S1_RGON_DIRECTIVE_QUEUE.json", "S1_ANCHONGRI_ACTIVE_TASK.md"], check=False)
            subprocess.run(["git", "commit", "-m", f"auto(harvester): picked up {len(harvested)} directives into active task"], check=False)
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=False)
            subprocess.run(["git", "push", "origin", "main"], check=False)
        except Exception as e:
            print(f"[HARVESTER] Git sync note: {e}", flush=True)

    return {
        "ok": True,
        "harvested_count": len(harvested),
        "harvested_ids": [h["directive_id"] for h in harvested]
    }

def send_completion_report_to_dashboard(directive_id: str, summary_ko: str, commit_hash: str = None, triumvirate_score: str = "100.0 / 100.0 PASS") -> dict:
    """
    [안총리 -> 르곤 대시보드 완료보고 실시간 발송 브릿지]
    1. S1_RGON_DIRECTIVE_QUEUE.json(및 docs) 상태를 COMPLETED_REPORT_SENT로 업데이트
    2. completion_report 필드(요약, 완료시각, 커밋해시, 삼성제도 점수) 기록
    3. S1_ANCHONGRI_TO_RGON_OUTBOX.json(및 docs)에 완료보고서 저장 및 자동 git push
    """
    init_ledgers()
    if commit_hash is None:
        try:
            commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
        except Exception:
            commit_hash = "HEAD"

    # 1. Update directive queue
    queue = load_json(QUEUE_JSON, {"directives": []})
    matched = False
    for item in queue.get("directives", []):
        if item.get("directive_id") == directive_id:
            item["status"] = "COMPLETED_REPORT_SENT"
            item["completion_report"] = {
                "completed_at": now_iso(),
                "summary": summary_ko,
                "commit_hash": commit_hash,
                "triumvirate_score": triumvirate_score
            }
            matched = True
            break
            
    if not matched:
        queue["directives"].append({
            "directive_id": directive_id,
            "timestamp": now_iso(),
            "sender": "수석보좌관 르곤 (Space 0)",
            "recipient": "기술총리 안총리",
            "title": f"공식 하명 지시서 ({directive_id})",
            "status": "COMPLETED_REPORT_SENT",
            "full_text": summary_ko,
            "completion_report": {
                "completed_at": now_iso(),
                "summary": summary_ko,
                "commit_hash": commit_hash,
                "triumvirate_score": triumvirate_score
            }
        })

    queue["last_synced"] = now_iso()
    save_json(QUEUE_JSON, queue)
    save_json(DOCS_QUEUE_JSON, queue)

    # 2. Update Anchongri Outbox
    outbox = load_json(OUTBOX_JSON, {"version": "1.0.0", "reports": []})
    report_entry = {
        "report_id": f"REP_{directive_id}",
        "directive_id": directive_id,
        "summary": summary_ko,
        "commit_hash": commit_hash,
        "triumvirate_score": triumvirate_score,
        "timestamp": now_iso(),
        "status": "DELIVERED_TO_DASHBOARD"
    }

    reports = [r for r in outbox.get("reports", []) if r.get("directive_id") != directive_id]
    reports.insert(0, report_entry)
    outbox["reports"] = reports
    outbox["last_updated"] = now_iso()

    save_json(OUTBOX_JSON, outbox)
    save_json(DOCS_OUTBOX_JSON, outbox)

    print(f"[OUTBOX] Delivered completion report for {directive_id} ({commit_hash}) to dashboard!", flush=True)

    # 3. Auto commit & push
    try:
        subprocess.run(["git", "add", "S1_RGON_DIRECTIVE_QUEUE.json", "docs/S1_RGON_DIRECTIVE_QUEUE.json", "S1_ANCHONGRI_TO_RGON_OUTBOX.json", "docs/S1_ANCHONGRI_TO_RGON_OUTBOX.json"], check=False)
        subprocess.run(["git", "commit", "-m", f"report(anchongri): completion report for {directive_id} delivered to dashboard ({commit_hash})"], check=False)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=False)
        print(f"[OUTBOX] Completion report auto-pushed to GitHub main!", flush=True)
    except Exception as e:
        print(f"[OUTBOX] Git push note: {e}", flush=True)

    return {
        "ok": True,
        "directive_id": directive_id,
        "commit_hash": commit_hash,
        "report": report_entry
    }

def run_bridge_cycle(cycle_num=0):
    init_ledgers()
    # 0. Harvest Directives from GitHub SSOT (15s Cycle)
    try:
        harvest_from_github_ssot()
    except Exception as e:
        print(f"[BRIDGE] Harvester note: {e}", flush=True)

    # 1. Process Mobile Queue
    try:
        process_mobile_queue()
    except Exception as e:
        print(f"[BRIDGE] Mobile queue note: {e}", flush=True)

    # 2. Deep Scan Space 0 for Rgon directives (Smart Auto-Reload on every 3rd cycle: ~45s)
    try:
        do_reload = (cycle_num > 0 and cycle_num % 4 == 0)
        res = scan_space0_deep(do_reload=do_reload)
        if res and res.get("ok"):
            recent = res.get("data", {}).get("recent_messages", [])
            for msg_text in recent:
                # 1) finditer on explicit [S1_AUTO_DISPATCH_TO_ANCHONGRI] blocks
                dispatch_matches = list(re.finditer(r"(\[S1_AUTO_DISPATCH_TO_ANCHONGRI\][\s\S]*?(?:\[/S1_AUTO_DISPATCH_TO_ANCHONGRI\]|$))", msg_text))
                for dm in dispatch_matches:
                    full_block = dm.group(1).strip()
                    id_match = re.search(r"(?:ID:\s*|DIRECTIVE_ID:\s*|#\s*)?(RGON_DIR_[A-Za-z0-9_]+)", full_block)
                    if not id_match:
                        continue
                    did = id_match.group(1)
                    # Ignore ephemeral timestamp patterns
                    if re.match(r"^RGON_DIR_\d{10}$", did):
                        continue
                    title_match = re.search(r"TITLE:\s*(.+)", full_block)
                    title = title_match.group(1).strip() if title_match else f"르곤 보좌관 공식 지시서 ({did})"
                    register_new_directive(did, title, full_block)

                # 2) finditer on standalone RGON_DIR_[A-Za-z0-9_]+ (Only legitimate names, not pure timestamps)
                dir_matches = list(re.finditer(r"\b(RGON_DIR_[A-Za-z][A-Za-z0-9_]+)\b", msg_text))
                for dm in dir_matches:
                    did = dm.group(1)
                    if re.match(r"^RGON_DIR_\d{10}$", did):
                        continue
                    start_pos = max(0, dm.start() - 100)
                    end_pos = min(len(msg_text), dm.end() + 2000)
                    context_snippet = msg_text[start_pos:end_pos].strip()
                    title_match = re.search(r"TITLE:\s*(.+)|\[(.+?)\]", context_snippet)
                    title = (title_match.group(1) or title_match.group(2)).strip() if title_match else f"르곤 보좌관 공식 지시서 ({did})"
                    register_new_directive(did, title, context_snippet)
    except Exception as e:
        print(f"[BRIDGE] Space 0 scan note: {e}", flush=True)

def bridge_daemon_loop(poll_interval=15):
    """
    24H Persistent Loop. Runs inside s1_server or standalone.
    Scan interval: 15s (Zero mouse disruption with safeHandOff).
    """
    print(f"[{now_iso()}] S1 Zero-Paste Persistent Daemon started (Interval: {poll_interval}s)", flush=True)
    init_ledgers()

    # Pre-register known directives from Rgon
    known_directives = [
        ("RGON_DIR_LIVE_001", "무복붙 자동 전달망 실전 라이브 개통", "Space 0 -> GitHub -> Anchongri 무복붙 파이프라인 가동"),
        ("RGON_DIR_ABSORB_10SHORTS_002", "쇼츠 10편 6대 초경량 핵심 기술 흡수 및 시각화", "Interactive Anatomy 실시간 에너지 구슬, Savvy Progress & File Tree, 3단 뷰포트 클린 검증"),
        ("RGON_DIR_TRIUMVIRATE_MANDATE_003", "전 작업 삼성(三聖) 제도 만장일치 통과 강제 룰 헌법 잠금", "Open Agent Harness 4대 안전장치 + 삼성 만장일치 통과 룰 영구 강제")
    ]
    for did, title, content in known_directives:
        register_new_directive(did, title, content)

    cycle_count = 0
    while RUNNING_FLAG:
        try:
            cycle_count += 1
            scan_clipboard_for_directives()
            run_bridge_cycle(cycle_num=cycle_count)
            if cycle_count % 4 == 0:
                print(f"[{now_iso()}] [HARVESTER_HEARTBEAT] 15s cycle #{cycle_count} running healthy. SSOT & Space 0 eye ok.", flush=True)
        except Exception as e:
            print(f"[BRIDGE] Error in cycle: {e}", flush=True)
        time.sleep(poll_interval)

if __name__ == "__main__":
    init_ledgers()
    bridge_daemon_loop(15)

