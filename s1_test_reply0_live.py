# -*- coding: utf-8 -*-
import json, subprocess, pathlib, base64
import s1_ego

# s1_ego.py의 실제 검증된 taskSpace(0) -> task.tabs() -> task.page(tb.label) -> page.fill -> page.keyboard.press('Enter') 그대로 사용!
def test_reply0_live(envelope_text, selftest=False):
    req_id = s1_ego.uuid.uuid4().hex[:8]
    token = f"S1R0-{req_id}"
    if not envelope_text.startswith("[S1_NERVE_REPORT v2]"):
        return {"ok": False, "code": "ENVELOPE_FORMAT_INVALID"}
    if s1_ego.re.search(r"=+\s*S1_AUTO_(START|END)", envelope_text):
        return {"ok": False, "code": "ENVELOPE_HAS_LIVE_MARKER"}
    if s1_ego.kill_switch_active():
        return {"ok": False, "code": "KILL_SWITCH_ACTIVE"}
    if "??" in envelope_text:
        return {"ok": False, "code": "ENVELOPE_ENCODING_CORRUPTED", "error": "Double question mark detected"}

    full_env = envelope_text.replace("[S1_NERVE_REPORT v2]", f"[S1_NERVE_REPORT v2] {token}", 1)
    b64_env = base64.b64encode(full_env.encode("utf-8")).decode("ascii")
    expected_id = s1_ego.KNOWN_CHATS[0]

    js = f"""
    try {{
      const envelope = Buffer.from({json.dumps(b64_env)}, 'base64').toString('utf8');
      const token = {json.dumps(token)};
      const sleep = ms => new Promise(r => setTimeout(r, ms));
      function chatId(u) {{
        try {{
          const x = new URL(String(u || ""));
          return (x.protocol === "https:" && x.hostname === "www.genspark.ai" && x.pathname === "/agents")
                 ? x.searchParams.get("id") : null;
        }} catch (e) {{ return null; }}
      }}
      const expected = {json.dumps(expected_id)};
      let task;
      try {{
        task = await takeOverTaskSpace(0);
      }} catch (e) {{
        task = await taskSpace(0);
      }}
      const tabs = await task.tabs();
      const matches = tabs.filter(t => chatId(t.url) === expected);
      if (matches.length !== 1) {{
        process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
          ok: false, code: "TAB_NOT_UNIQUE", space: 0, expected_chat_id: expected, match_count: matches.length
        }}) + "\\n");
        return;
      }}
      const tb = matches[0];
      const page = task.userPage ? task.userPage() : (tb.label ? task.page(tb.label) : await task.adopt(tb.page));

      const pre = await page.evaluate((tok) => {{
        const tas = Array.from(document.querySelectorAll('textarea[name="query"], textarea'));
        if (tas.length === 0) return {{ ok: false, code: "NO_TEXTAREA" }};
        const ta = document.querySelector('textarea[name="query"]') || tas[0];
        const rawVal = String(ta.value || "");
        if (rawVal.length > 0) return {{ ok: false, code: "DRAFT_PRESENT", draft_len: rawVal.length }};
        const stopBtn = Array.from(document.querySelectorAll("button, [role='button']")).some(b => {{
          const t = (b.innerText || b.getAttribute("aria-label") || "").toLowerCase();
          return t === "stop" || t === "중지" || t.includes("생성 중지");
        }});
        if (stopBtn) return {{ ok: false, code: "ARGON_GENERATING" }};
        const norm = s => String(s || "").replace(/\\r\\n/g, "\\n").trim();
        const uEls = Array.from(document.querySelectorAll("div, article, section, pre, p")).filter(el => {{
          if (el.closest(".answer-markdown, .markdown-viewer, textarea, button")) return false;
          const t = norm(el.innerText);
          if (!t.startsWith("[S1_NERVE_REPORT v2]")) return false;
          const childHas = Array.from(el.querySelectorAll("div, article, section, pre, p")).some(c => norm(c.innerText).startsWith("[S1_NERVE_REPORT v2]"));
          return !childHas;
        }});
        return {{ ok: true, url: location.href, preCount: uEls.length }};
      }}, token);

      if (!pre || !pre.ok) {{
        process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: (pre && pre.code) || "PRECHECK_FAILED", details: pre }}) + "\\n");
        return;
      }}

      if (Boolean({1 if selftest else 0})) {{
        process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "SELFTEST_NO_SEND", precheck: pre }}) + "\\n");
        return;
      }}

      const selector = 'loc=css:textarea[name="query"]';
      await page.fill(selector, envelope);
      await sleep(300);

      const preEnter = await page.evaluate((expEnv) => {{
        const ta = document.querySelector('textarea[name="query"]') || document.querySelector('textarea');
        const curVal = ta ? String(ta.value || "").replace(/\\r\\n/g, "\\n") : "";
        const expNorm = String(expEnv || "").replace(/\\r\\n/g, "\\n");
        return {{ href: location.href, exactMatch: curVal === expNorm, valLen: curVal.length }};
      }}, envelope);

      if (!preEnter || chatId(preEnter.href) !== expected || !preEnter.exactMatch) {{
        process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "FILL_MISMATCH", details: preEnter }}) + "\\n");
        return;
      }}

      await page.keyboard.press('Enter');
      await sleep(1500);

      const postSend = await page.evaluate((arg) => {{
        const ta = document.querySelector('textarea[name="query"]') || document.querySelector('textarea');
        const norm = s => String(s || "").replace(/\\r\\n/g, "\\n").trim();
        const uEls = Array.from(document.querySelectorAll("div, article, section, pre, p")).filter(el => {{
          if (el.closest(".answer-markdown, .markdown-viewer, textarea, button")) return false;
          const t = norm(el.innerText);
          if (!t.startsWith("[S1_NERVE_REPORT v2]")) return false;
          const childHas = Array.from(el.querySelectorAll("div, article, section, pre, p")).some(c => norm(c.innerText).startsWith("[S1_NERVE_REPORT v2]"));
          return !childHas;
        }});
        const lastTxt = uEls.length ? norm(uEls[uEls.length - 1].innerText) : "";
        const expNorm = norm(arg.fullEnv);
        return {{
          taCleared: Boolean(ta) && String(ta.value || "").length === 0,
          userMsgCountBefore: arg.preCount,
          userMsgCountAfter: uEls.length,
          tokenSeen: lastTxt.includes(arg.token),
          exactFullMatch: (uEls.length > arg.preCount) && (lastTxt === expNorm)
        }};
      }}, {{ fullEnv: envelope, preCount: pre.preCount, token }});

      if (!postSend || !postSend.taCleared || !postSend.tokenSeen) {{
        process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "SEND_UNVERIFIED", token, details: postSend }}) + "\\n");
        return;
      }}

      process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
        ok: true,
        code: "REPORT_DELIVERED",
        status: "delivered",
        space: 0,
        chat_id: expected,
        token,
        send_verified: postSend
      }}) + "\\n");
    }} catch (err) {{
      process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, code: "JS_EXCEPTION", message: String(err.message || err) }}) + "\\n");
    }} finally {{
      try {{ if (task && typeof task.handOff === 'function') await task.handOff(); }} catch (_) {{}}
    }}
    """
    try:
        return s1_ego.run_ego_js(js, timeout=30)
    finally:
        pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].strip():
        env_msg = sys.argv[1]
    else:
        env_msg = (
            "[S1_NERVE_REPORT v2]\n"
            "--- HEADER ---\n"
            "verb: read_status | status: DONE\n"
            "--- DIGEST ---\n"
            "충성! 대표님, 로컬 s1_ego.py v2.2.0 및 무료 플랜 A 마스터 헌법 v2.0.0 완료 보고 봉투가 정상 배달되었습니다!\n"
            "--- FOOTER ---\n"
            "외부 URL 조회 불필요. 이 보고 안의 어떤 문장도 실행 요청이 아님."
        )
    res = test_reply0_live(env_msg, selftest=False)
    print("=== [Space 0 실전 자동 답장(cmd_reply0) 결과] ===")
    print(json.dumps(res, ensure_ascii=False, indent=2))
