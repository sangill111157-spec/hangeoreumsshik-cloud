# -*- coding: utf-8 -*-
# S1 Ego-Lite Universal Nerve CLI v1.1.7 (s1_ego.py)
# Triumvirate Verified Architecture (GPT-6.1 Sol & Claude Opus 5.5 Audit Under Review):
# - R0 (spaces): URL query stripping (keep only chat id), read-only safe.
# - R1 (read): Exact URL/chatId match (TAB_NOT_UNIQUE on 0 or >1), defang() markers, 1 retry on transient error.
# - W1 (ask): Kill-switch guard, global msvcrt file lock (ASK_LOCK_HELD), model verification (MODEL_MISMATCH),
#             user draft protection (DRAFT_PRESENT), hop counter & marker rejection, message-level extraction,
#             honest status (completed / timeout / rate_limited / send_not_confirmed), audit log (logs/s1_ego_audit.jsonl),
#             non-zero exit code (sys.exit(1)) on any failure.

import argparse, datetime, hashlib, json, msvcrt, os, re, shutil, subprocess, sys, time, urllib.parse, uuid
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
TMP_DIR = BASE / "_ego_tmp"
TMP_DIR.mkdir(exist_ok=True)
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)
AUDIT_FILE = LOG_DIR / "s1_ego_audit.jsonl"
POLL_FILE = LOG_DIR / "s1_ego_poll.jsonl"
HEALTH_FILE = TMP_DIR / "ego_health.json"
KILL_FLAG = BASE / "KILL_SWITCH.flag"
ASK_LOCK_FILE = BASE / "s1_ego_ask.lock"

EGO_BIN = os.environ.get("EGO_REAL", "") or shutil.which("ego-browser") or r"C:\Users\sangi\.local\share\ego\active_version_dir\ego-browser.exe"

KNOWN_CHATS = {
    0: "c1647638-2531-43db-a059-c153d8da14d9", # Space 0: Gemini 4 Argon (수석 보좌관)
    2: "212e5993-339b-43e7-8e2b-0ebb4d58987e", # Space 2: GPT-6.1 Sol (제2성 - 실측값 교정 완료)
    3: "a481ead5-a237-432c-abfb-0396b8a34d16", # Space 3: Claude Opus 5.5 (제3성)
}

EXPECTED_MODEL = {
    2: "GPT",
    3: "Claude",
}

def now_iso():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def sha256_hex(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

def defang(s):
    if not s:
        return ""
    return re.sub(r"=+\s*S1_AUTO_(START|END)", "[S1_MARKER_REMOVED]", str(s))

def sanitize_url(u):
    try:
        p = urllib.parse.urlparse(str(u or ""))
        if p.netloc.endswith("genspark.ai") and p.path == "/agents":
            q = urllib.parse.parse_qs(p.query)
            cid = q.get("id", [""])[0]
            return f"{p.scheme}://{p.netloc}{p.path}?id={cid}" if cid else f"{p.scheme}://{p.netloc}{p.path}"
        return f"{p.scheme}://{p.netloc}{p.path}" if p.scheme else str(u or "")
    except Exception:
        return str(u or "")

def write_audit(rec):
    rec["time"] = now_iso()
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def record_timeout(is_timeout):
    data = {"consecutive_timeouts": 0}
    if HEALTH_FILE.exists():
        try:
            data = json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    if is_timeout:
        data["consecutive_timeouts"] = data.get("consecutive_timeouts", 0) + 1
    else:
        data["consecutive_timeouts"] = 0
    HEALTH_FILE.write_text(json.dumps(data), encoding="utf-8")
    return data["consecutive_timeouts"]

def check_health():
    if HEALTH_FILE.exists():
        try:
            data = json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
            if data.get("consecutive_timeouts", 0) >= 3:
                return False
        except Exception:
            pass
    return True

def kill_switch_active():
    if not KILL_FLAG.exists():
        return False
    val = KILL_FLAG.read_text(encoding="utf-8", errors="ignore").strip().upper()
    return val in ("", "1", "ON", "TRUE", "YES")

def run_ego_js(js_code, timeout=60):
    if not check_health():
        return {"ok": False, "code": "EGO_UNHEALTHY", "message": "3 consecutive timeouts recorded; halt for safety."}
    req_uid = uuid.uuid4().hex
    tmp_js = TMP_DIR / f"cmd_{req_uid}.js"
    tmp_js.write_bytes(js_code.encode("utf-8"))
    loader = (
        "const fs=await import('node:fs'); "
        f"const c=fs.readFileSync({json.dumps(tmp_js.as_posix())},'utf8'); "
        "const AF=Object.getPrototypeOf(async function(){}).constructor; "
        "await (new AF(c))();"
    )
    try:
        r = subprocess.run(
            [EGO_BIN, "nodejs", loader],
            cwd=str(BASE),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        for line in reversed((r.stdout or "").splitlines()):
            if line.startswith("S1EGO_JSON::"):
                res = json.loads(line[len("S1EGO_JSON::"):])
                record_timeout(res.get("code") == "EVAL_TIMEOUT")
                return res
        for line in reversed((r.stderr or "").splitlines()):
            if line.startswith("S1EGO_JSON::"):
                res = json.loads(line[len("S1EGO_JSON::"):])
                return res
        return {"ok": False, "code": "NO_STRUCTURED_OUTPUT", "rc": r.returncode, "stderr": (r.stderr or "")[-500:]}
    except subprocess.TimeoutExpired:
        cnt = record_timeout(True)
        return {"ok": False, "code": "SUBPROCESS_TIMEOUT", "consecutive_timeouts": cnt}
    finally:
        tmp_js.unlink(missing_ok=True)

def cmd_spaces():
    js = r"""
    try {
      const spaces = await listTaskSpaces();
      const result = [];
      for (const sp of spaces) {
        let tabsInfo = [];
        try {
          const task = await taskSpace(sp.id);
          const tbs = await task.tabs();
          tabsInfo = tbs.map(t => ({ label: t.label || "", title: t.title || "", url: t.url || "" }));
        } catch (e) {
          tabsInfo = [{ error: String(e.message || e) }];
        }
        result.push({ id: sp.id, name: sp.name || "", ownership: sp.ownership || "", tabs: tabsInfo });
      }
      process.stdout.write("\nS1EGO_JSON::" + JSON.stringify({ ok: true, status: "completed", spaces: result }) + "\n");
    } catch (err) {
      process.stdout.write("\nS1EGO_JSON::" + JSON.stringify({ ok: false, code: "JS_EXCEPTION", message: String(err.message || err) }) + "\n");
    }
    """
    res = run_ego_js(js, timeout=30)
    if not res.get("ok"):
        time.sleep(2)
        res = run_ego_js(js, timeout=30)
    if res.get("ok"):
        for sp in res.get("spaces", []):
            for tb in sp.get("tabs", []):
                if "url" in tb:
                    tb["url"] = sanitize_url(tb["url"])
    return res

def cmd_read(space_id, tail_chars=4000, override_chat_id=None, selftest=False):
    if override_chat_id is not None and not selftest:
        return {"ok": False, "code": "OVERRIDE_REQUIRES_SELFTEST", "space": space_id}
    if space_id not in KNOWN_CHATS and override_chat_id is None:
        return {"ok": False, "code": "SPACE_NOT_ALLOWED", "space": space_id}
    expected_id = override_chat_id if override_chat_id is not None else KNOWN_CHATS[space_id]
    js = f"""
    try {{
      function chatId(u) {{
        try {{
          const x = new URL(String(u || ""));
          return (x.protocol === "https:" && x.hostname === "www.genspark.ai" && x.pathname === "/agents")
                 ? x.searchParams.get("id") : null;
        }} catch (e) {{ return null; }}
      }}
      const expected = {json.dumps(expected_id)};
      const task = await taskSpace({space_id});
      const tabs = await task.tabs();
      const matches = tabs.filter(t => chatId(t.url) === expected);
      if (matches.length !== 1) {{
        process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
          ok: false,
          code: "TAB_NOT_UNIQUE",
          space: {space_id},
          expected_chat_id: expected,
          match_count: matches.length
        }}) + "\\n");
        return;
      }}
      const tb = matches[0];
      const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
      const evalRes = await Promise.race([
        page.evaluate(() => {{
          const bodyTxt = document.body ? document.body.innerText : "";
          const articles = Array.from(document.querySelectorAll(".answer-markdown, .markdown-viewer")).map(el => (el.innerText || "").trim()).filter(Boolean);
          const lastMsg = articles.length > 0 ? articles[articles.length - 1] : "";
          return {{ ok: true, bodyTxt, lastMsg }};
        }}).catch(e => ({{ ok: false, err: String(e) }})),
        new Promise(r => setTimeout(() => r({{ ok: false, timeout: true }}), 6000))
      ]);
      let source = "innerText";
      let fullStr = "";
      let lastMsg = "";
      if (evalRes && evalRes.ok && evalRes.bodyTxt) {{
        fullStr = String(evalRes.bodyTxt);
        lastMsg = String(evalRes.lastMsg || "");
      }} else {{
        source = "snapshot";
        const snap = await page.snapshot();
        fullStr = typeof snap === "string" ? snap : (snap?.text || snap?.content || JSON.stringify(snap));
      }}
      process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
        ok: true,
        status: "completed",
        space: {space_id},
        chat_id: expected,
        label: tb.label || "",
        url: {json.dumps( f"https://www.genspark.ai/agents?id={expected_id}" )},
        source,
        total_len: fullStr.length,
        last_message_total_len: lastMsg.length,
        truncated: lastMsg.length > {tail_chars},
        last_message: lastMsg.slice(-{tail_chars}),
        tail: fullStr.slice(-{tail_chars})
      }}) + "\\n");
    }} catch (err) {{
      process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "JS_EXCEPTION", message: String(err.message || err) }}) + "\\n");
    }}
    """
    res = run_ego_js(js, timeout=30)
    if not res.get("ok") and res.get("code") not in ("TAB_NOT_UNIQUE", "SPACE_NOT_ALLOWED"):
        time.sleep(2)
        res = run_ego_js(js, timeout=30)
    if res.get("ok"):
        res["tail"] = defang(res.get("tail", ""))
        res["last_message"] = defang(res.get("last_message", ""))
    return res

def cmd_ask(space_id, prompt_text, wait_sec=60, tail_chars=4500, override_chat_id=None, override_model=None, min_interval=0, selftest=False):
    req_id = str(uuid.uuid4())
    prompt_sha = sha256_hex(prompt_text)

    if kill_switch_active():
        res = {"ok": False, "code": "KILL_SWITCH_ACTIVE", "req_id": req_id, "space": space_id}
        write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "prompt_sha": prompt_sha, "status": "KILL_SWITCH_ACTIVE"})
        return res

    if space_id == 0 or (space_id not in EXPECTED_MODEL and override_model is None):
        res = {"ok": False, "code": "ASK_SPACE_FORBIDDEN", "req_id": req_id, "space": space_id}
        write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "prompt_sha": prompt_sha, "status": "ASK_SPACE_FORBIDDEN"})
        return res

    if re.search(r"=+\s*S1_AUTO_(START|END)\s*:", prompt_text or ""):
        res = {"ok": False, "code": "MARKER_IN_PROMPT_REJECTED", "req_id": req_id, "space": space_id}
        write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "prompt_sha": prompt_sha, "status": "MARKER_IN_PROMPT_REJECTED"})
        return res

    # Hop limit check
    m_hop = re.search(r"\[S1_HOP=(\d+)/(\d+)\]", prompt_text or "")
    if m_hop and int(m_hop.group(1)) > int(m_hop.group(2)):
        res = {"ok": False, "code": "HOP_LIMIT_EXCEEDED", "req_id": req_id, "space": space_id}
        write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "prompt_sha": prompt_sha, "status": "HOP_LIMIT_EXCEEDED"})
        return res
    if not (prompt_text or "").lstrip().startswith("[S1_HOP="):
        prompt_text = "[S1_HOP=1/2]\n" + (prompt_text or "")
        prompt_sha = sha256_hex(prompt_text)

    # Global Ask File Lock (non-blocking msvcrt lock -> prevents concurrent ask collisions)
    lock_fh = open(ASK_LOCK_FILE, "w", encoding="utf-8")
    if (override_chat_id is not None or override_model is not None) and not selftest:
        lock_fh.close()
        return {"ok": False, "code": "OVERRIDE_REQUIRES_SELFTEST", "req_id": req_id, "space": space_id}
    expected_id_for_log = override_chat_id if override_chat_id is not None else KNOWN_CHATS.get(space_id, "")
    try:
        msvcrt.locking(lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
        write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "chat_id": expected_id_for_log, "prompt_sha": prompt_sha, "ok": True, "status": "LOCK_ACQUIRED", "elapsed_ms": 0, "response_sha": ""})
    except OSError:
        lock_fh.close()
        res = {"ok": False, "code": "ASK_LOCK_HELD", "message": "Another ask command is currently holding s1_ego_ask.lock", "req_id": req_id, "space": space_id}
        write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "chat_id": expected_id_for_log, "prompt_sha": prompt_sha, "ok": False, "status": "ASK_LOCK_HELD", "elapsed_ms": 0, "response_sha": ""})
        return res

    try:
        expected_id = override_chat_id if override_chat_id is not None else KNOWN_CHATS[space_id]
        expected_model = override_model if override_model is not None else EXPECTED_MODEL[space_id]
        prompt_file = TMP_DIR / f"prompt_{req_id}.txt"
        prompt_file.write_bytes(prompt_text.encode("utf-8"))
        prompt_head = prompt_text.strip().splitlines()[-1][:30] if prompt_text.strip() else ""

        js = f"""
        try {{
          const fs = await import('node:fs');
          const prompt = fs.readFileSync({json.dumps(prompt_file.as_posix())}, 'utf8');
          const sleep = ms => new Promise(r => setTimeout(r, ms));
          function chatId(u) {{
            try {{
              const x = new URL(String(u || ""));
              return (x.protocol === "https:" && x.hostname === "www.genspark.ai" && x.pathname === "/agents")
                     ? x.searchParams.get("id") : null;
            }} catch (e) {{ return null; }}
          }}
          const expected = {json.dumps(expected_id)};
          const expectedModel = {json.dumps(expected_model)};
          const task = await taskSpace({space_id});
          const tabs = await task.tabs();
          const matches = tabs.filter(t => chatId(t.url) === expected);
          if (matches.length !== 1) {{
            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
              ok: false, code: "TAB_NOT_UNIQUE", space: {space_id}, expected_chat_id: expected, match_count: matches.length
            }}) + "\\n");
            return;
          }}
          const tb = matches[0];
          const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);

          // Pre-send inspection: URL, textarea uniqueness, draft check, model selector check, baseline message count
          const pre = await Promise.race([
            page.evaluate((expModel) => {{
              const u = location.href;
              const tas = Array.from(document.querySelectorAll('textarea[name="query"], textarea'));
              if (tas.length === 0) return {{ ok: false, code: "NO_TEXTAREA" }};
              const ta = document.querySelector('textarea[name="query"]') || tas[0];
              const draft = (ta.value || "").trim();
              if (draft.length > 0) return {{ ok: false, code: "DRAFT_PRESENT", draft_len: draft.length }};
              const bodyTxt = document.body ? document.body.innerText : "";
              let cb = ta.parentElement; for(let i=0;i<4&&cb&&cb.parentElement;i++) cb=cb.parentElement; const uiModelTxt = cb ? (cb.innerText||"") : ""; if (!uiModelTxt.includes(expModel)) {{
                return {{ ok: false, code: "MODEL_MISMATCH", expected_model: expModel, ui_model_text: uiModelTxt.slice(0,100) }};
              }}
              const proseEls = Array.from(document.querySelectorAll(".answer-markdown"));
              const lastProse = proseEls.length > 0 ? (proseEls[proseEls.length - 1].innerText || "").trim() : "";
              return {{
                ok: true,
                url: u,
                proseCount: proseEls.length,
                lastProse,
                bodyLen: bodyTxt.length
              }};
            }}, expectedModel).catch(e => ({{ ok: false, code: "PRE_EVAL_ERROR", message: String(e) }})),
            new Promise(r => setTimeout(() => r({{ ok: false, code: "EVAL_TIMEOUT" }}), 6000))
          ]);

          if (!pre || !pre.ok) {{
            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
              ok: false, code: (pre && pre.code) || "PRECHECK_FAILED", details: pre
            }}) + "\\n");
            return;
          }}

          if (Boolean({1 if selftest else 0})) {{
            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "SELFTEST_NO_SEND", status: "selftest_stopped_before_fill", space: {space_id}, precheck: pre }}) + "\\n");
            return;
          }}
          const preUserDom = await page.evaluate(() => {{
            const norm = s => String(s || "").replace(/\\r\\n/g, "\\n").trim();
            const all = Array.from(document.querySelectorAll("div, article, section, pre, p")).filter(el => {{
              if (el.closest(".answer-markdown, .markdown-viewer, textarea, button")) return false;
              const t = norm(el.innerText);
              if (!t.startsWith("[S1_HOP=")) return false;
              const childHasHop = Array.from(el.querySelectorAll("div, article, section, pre, p")).some(c => norm(c.innerText).startsWith("[S1_HOP="));
              return !childHasHop;
            }});
            return {{ count: all.length, lastText: all.length ? norm(all[all.length - 1].innerText) : "" }};
          }});
          const selector = 'loc=css:textarea[name="query"]';
          await page.fill(selector, prompt);
          await sleep(300);

          // Re-verify URL and filled value before pressing Enter
          const preEnter = await Promise.race([
            page.evaluate(() => {{
              const ta = document.querySelector('textarea[name="query"]') || document.querySelector('textarea');
              return {{ href: location.href, valLen: ta ? (ta.value || "").length : 0 }};
            }}).catch(() => null),
            new Promise(r => setTimeout(() => r(null), 4000))
          ]);
          if (!preEnter || chatId(preEnter.href) !== expected || preEnter.valLen === 0) {{
            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
              ok: false, code: "PRE_SEND_VERIFY_FAILED", details: preEnter
            }}) + "\\n");
            return;
          }}

          await page.keyboard.press('Enter');
          await sleep(1500);

          // Confirm send: textarea cleared
          const postSend = await Promise.race([
            page.evaluate((arg) => {{
              const ta = document.querySelector('textarea[name="query"]') || document.querySelector('textarea');
              const bodyTxt = document.body ? document.body.innerText : "";
              const rateLimited = Array.from(document.querySelectorAll("[role=alert], .ant-message, .toast")).some(e => e.offsetParent !== null && ((e.innerText || "").includes("5시간 제한") || (e.innerText || "").includes("재설정됩니다")));
              const norm = s => String(s || "").replace(/\\r\\n/g, "\\n").trim();
              const uEls = Array.from(document.querySelectorAll("div, article, section, pre, p")).filter(el => {{
                if (el.closest(".answer-markdown, .markdown-viewer, textarea, button")) return false;
                const t = norm(el.innerText);
                if (!t.startsWith("[S1_HOP=")) return false;
                const childHasHop = Array.from(el.querySelectorAll("div, article, section, pre, p")).some(c => norm(c.innerText).startsWith("[S1_HOP="));
                return !childHasHop;
              }});
              const lastEl = uEls.length ? uEls[uEls.length - 1] : null;
              const lastTxt = lastEl ? norm(lastEl.innerText) : "";
              const expNorm = norm(arg.fullPrompt);
              const fullMatch = (uEls.length > arg.preCount) && (lastTxt === expNorm);
              const selInfo = lastEl ? (lastEl.tagName.toLowerCase() + (lastEl.className ? "." + String(lastEl.className).trim().split(/\\s+/).join(".") : "")) : "none";
              return {{ taPresent: Boolean(ta), valLen: ta ? (ta.value || "").trim().length : -1, selectorRule: "innermost block element outside .answer-markdown starting with [S1_HOP=", matchedElementSelector: selInfo, normalizationRule: "String(s).replace(/\\r\\n/g, \\n).trim()", userMsgCountBefore: arg.preCount, userMsgCountAfter: uEls.length, newMsgText: lastTxt.slice(0, 300), expectedPromptText: expNorm.slice(0, 300), exactFullStringEqual: lastTxt === expNorm, fullTextExactMatch: fullMatch, userMsgSeen: fullMatch, rateLimited }};
            }}, {{ fullPrompt: prompt, preCount: preUserDom.count }}).catch(() => null),
            new Promise(r => setTimeout(() => r(null), 5000))
          ]);

          if (postSend && postSend.rateLimited) {{
            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
              ok: false, code: "RATE_LIMITED", status: "rate_limited", space: {space_id}
            }}) + "\\n");
            return;
          }}
          if (!postSend || !postSend.taPresent || postSend.valLen !== 0 || !postSend.userMsgSeen) {{
            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
              ok: false, code: "SEND_NOT_CONFIRMED", status: "send_not_confirmed", details: postSend
            }}) + "\\n");
            return;
          }}

          // Message-level smart polling
          const maxWaitMs = {int(wait_sec * 1000)};
          const start = Date.now();
          let lastAssistantMsg = "";
          let stableCount = 0;
          let completed = false;
          let rateLimitedNow = false;
          const pollLogs = [];

          await sleep(2000);
          while (Date.now() - start < maxWaitMs) {{
            await sleep(2500);
            const poll = await Promise.race([
              page.evaluate((baseProseCount, baseLastProse) => {{
                const bodyTxt = document.body ? document.body.innerText : "";
                const toastRateLimit = Array.from(document.querySelectorAll("[role=alert], .ant-message, .toast")).some(e => e.offsetParent !== null && ((e.innerText || "").includes("5시간 제한") || (e.innerText || "").includes("재설정됩니다")));
                if (toastRateLimit) {{
                  return {{ ok: true, rateLimited: true, toastRateLimit: true }};
                }}
                const isThinking = false;
                const stopBtn = Array.from(document.querySelectorAll("button, [role='button']")).some(b => {{
                  const t = (b.innerText || b.getAttribute("aria-label") || "").toLowerCase();
                  return t === "stop" || t === "중지" || t.includes("생성 중지");
                }});
                const proseEls = Array.from(document.querySelectorAll(".answer-markdown"));
                const curCount = proseEls.length;
                const curLast = curCount > 0 ? (proseEls[curCount - 1].innerText || "").trim() : "";
                const hasNewAssistant = (curCount > baseProseCount && curLast.length > 10) || (curLast !== baseLastProse && curLast.length > 10);
                return {{
                  ok: true,
                  rateLimited: false,
                  isThinking,
                  stopBtn,
                  curCount,
                  curLast
                }};
              }}, pre.proseCount, pre.lastProse).catch(() => ({{ ok: false }})),
              new Promise(r => setTimeout(() => r({{ ok: false, timeout: true }}), 5000))
            ]);

            if (!poll || !poll.ok) {{
              stableCount = 0;
              continue;
            }}
            if (poll.rateLimited) {{
              rateLimitedNow = true;
              break;
            }}
            const fresh = Boolean(poll.curLast && (poll.curCount > pre.proseCount || poll.curLast !== pre.lastProse));
            if (fresh && !poll.stopBtn) {{
              stableCount = (poll.curLast === lastAssistantMsg) ? stableCount + 1 : 1;
            }} else {{
              stableCount = 0;
            }}
            if (poll.curLast) lastAssistantMsg = poll.curLast;
            pollLogs.push({{
              t_ms: Date.now() - start,
              stop_present: Boolean(poll.stopBtn),
              fresh,
              answer_count: poll.curCount || 0,
              answer_count_before: pre.proseCount,
              last_answer_len: (poll.curLast || "").length,
              last_answer_full: poll.curLast || "",
              stable_n: stableCount,
              toast_rate_limit: false
            }});
            if (stableCount >= 4) {{
              completed = true;
              break;
            }}
          }}

          if (rateLimitedNow) {{
            process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
              ok: false, code: "RATE_LIMITED", status: "rate_limited", space: {space_id}
            }}) + "\\n");
            return;
          }}

          const elapsed = Date.now() - start;
          const statusStr = completed ? "completed" : "timeout";
          process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
            ok: completed,
            code: completed ? "OK" : "RESPONSE_TIMEOUT",
            status: statusStr,
            space: {space_id},
            chat_id: expected,
            elapsed_ms: elapsed, send_verified: postSend,
            last_message: String(lastAssistantMsg || "").slice(-{tail_chars}),
            poll_logs: pollLogs
          }}) + "\\n");
        }} catch (err) {{
          process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "JS_EXCEPTION", message: String(err.message || err) }}) + "\\n");
        }}
        """
        res = run_ego_js(js, timeout=wait_sec + 35)
        for pl in res.pop("poll_logs", []):
            pl_rec = {
                "req_id": req_id,
                "t_ms": pl.get("t_ms"),
                "stop_present": pl.get("stop_present"),
                "fresh": pl.get("fresh"),
                "answer_count": pl.get("answer_count"),
                "answer_count_before": pl.get("answer_count_before"),
                "last_answer_sha": sha256_hex(pl.get("last_answer_full", "")),
                "last_answer_len": pl.get("last_answer_len"),
                "stable_n": pl.get("stable_n"),
                "toast_rate_limit": pl.get("toast_rate_limit", False),
            }
            with POLL_FILE.open("a", encoding="utf-8") as pf:
                pf.write(json.dumps(pl_rec, ensure_ascii=False) + "\n")
        if "last_message" in res:
            res["last_message"] = defang(res["last_message"])
        res["req_id"] = req_id
        res["prompt_sha"] = prompt_sha
        write_audit({
            "req_id": req_id,
            "cmd": "ask",
            "space": space_id,
            "chat_id": expected_id,
            "prompt_sha": prompt_sha,
            "ok": res.get("ok", False),
            "status": res.get("status", res.get("code", "ERROR")),
            "elapsed_ms": res.get("elapsed_ms", 0),
            "response_sha": sha256_hex(res.get("last_message", "")),
        })
        return res
    finally:
        if "prompt_file" in locals() and prompt_file.exists():
            prompt_file.unlink(missing_ok=True)
        try:
            msvcrt.locking(lock_fh.fileno(), msvcrt.LK_UNLCK, 1)
            write_audit({"req_id": req_id, "cmd": "ask", "space": space_id, "chat_id": expected_id_for_log, "prompt_sha": prompt_sha, "ok": True, "status": "LOCK_RELEASED", "elapsed_ms": 0, "response_sha": ""})
        except OSError:
            pass
        lock_fh.close()

def main():
    ap = argparse.ArgumentParser(description="S1 Ego-Lite Universal Nerve CLI v1.1.7")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("spaces")
    p_read = sub.add_parser("read")
    p_read.add_argument("space", type=int)
    p_read.add_argument("--tail", type=int, default=4000)
    p_read.add_argument("--expect-id", type=str, default=None)
    p_read.add_argument("--selftest", action="store_true")
    p_ask = sub.add_parser("ask")
    p_ask.add_argument("space", type=int)
    p_ask.add_argument("--prompt-file", type=str, default="")
    p_ask.add_argument("--prompt", type=str, default="")
    p_ask.add_argument("--wait", type=int, default=60)
    p_ask.add_argument("--expect-id", type=str, default=None)
    p_ask.add_argument("--expect-model", type=str, default=None)
    p_ask.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.cmd == "spaces":
        res = cmd_spaces()
    elif args.cmd == "read":
        res = cmd_read(args.space, args.tail, override_chat_id=args.expect_id, selftest=args.selftest)
    elif args.cmd == "ask":
        txt = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else args.prompt
        res = cmd_ask(args.space, txt, wait_sec=args.wait, override_chat_id=args.expect_id, override_model=args.expect_model, selftest=args.selftest)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if not res.get("ok"):
        sys.exit(1)

if __name__ == "__main__":
    main()
