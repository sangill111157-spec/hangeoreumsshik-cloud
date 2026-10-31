# -*- coding: utf-8 -*-
# S1 Ego-Lite Universal Nerve CLI v1.0 (s1_ego.py)
# Principles:
# 1. No claimTaskSpace() -> never lock out the user's mouse without explicit need.
# 2. stdin=subprocess.DEVNULL + file loader -> zero pipe hang on Windows.
# 3. Promise.race timeout on page.evaluate() + page.snapshot() fallback -> zero 15s hang.
# 4. Native page.fill() + page.keyboard.press("Enter") -> reliable chat interaction.
# 5. Strictly scoped to trusted Space/Tab inspection and Triumvirate consultation.

import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
EGO_BIN = os.environ.get("EGO_REAL", "") or shutil.which("ego-browser") or r"C:\Users\sangi\.local\share\ego\active_version_dir\ego-browser.exe"

KNOWN_CHATS = {
    0: "c1647638-2531-43db-a059-c153d8da14d9", # Space 0: Gemini 4 Argon (수석 보좌관)
    2: "212e5993-72c0-4a3c-9a6e-586aa09a9f31", # Space 2: GPT-6.1 Sol (제2성)
    3: "a481ead5-a237-432c-abfb-0396b8a34d16", # Space 3: Claude Opus 5.5 (제3성)
}

def run_ego_js(js_code, timeout=60):
    tmp_js = BASE / "_s1_ego_cmd_tmp.js"
    tmp_js.write_text(js_code, encoding="utf-8")
    js_path_posix = str(tmp_js).replace("\\", "/")
    loader = (
        f"const fs=await import('node:fs'); "
        f"const c=fs.readFileSync('{js_path_posix}','utf8'); "
        f"const AF=Object.getPrototypeOf(async function(){{}}).constructor; "
        f"await (new AF(c))();"
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
        out = (r.stdout or "") + "\n" + (r.stderr or "")
        for line in reversed(out.splitlines()):
            if line.startswith("S1EGO_JSON::"):
                return json.loads(line[len("S1EGO_JSON::"):])
        return {"ok": False, "rc": r.returncode, "raw": out[-1500:]}
    finally:
        if tmp_js.exists():
            try:
                tmp_js.unlink()
            except OSError:
                pass

def cmd_spaces():
    js = r"""
    const spaces = await listTaskSpaces();
    const result = [];
    for (const sp of spaces) {
      let tabsInfo = [];
      try {
        const task = await taskSpace(sp.id);
        const tbs = await task.tabs();
        tabsInfo = tbs.map(t => ({ label: t.label || "", title: t.title || "", url: t.url || "" }));
      } catch (e) {
        tabsInfo = [{ error: e.message }];
      }
      result.push({ id: sp.id, name: sp.name || "", ownership: sp.ownership || "", tabs: tabsInfo });
    }
    process.stdout.write("\nS1EGO_JSON::" + JSON.stringify({ ok: true, spaces: result }) + "\n");
    """
    return run_ego_js(js, timeout=30)

def cmd_read(space_id, tail_chars=4000):
    expected_id = KNOWN_CHATS.get(space_id, "")
    js = f"""
    const task = await taskSpace({space_id});
    const tabs = await task.tabs();
    const expected = {json.dumps(expected_id)};
    const tb = (expected && tabs.find(t => String(t.url).includes(expected))) || tabs.find(t => String(t.url).includes('genspark.ai/agents')) || tabs[0];
    if (!tb) {{
      process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{ ok: false, error: "No tab in space " + {space_id} }}) + "\\n");
      return;
    }}
    const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
    let source = "innerText";
    let text = await Promise.race([
      page.evaluate(() => document.body ? document.body.innerText : ""),
      new Promise(r => setTimeout(() => r(""), 6000))
    ]);
    if (!text) {{
      source = "snapshot";
      const snap = await page.snapshot();
      text = typeof snap === "string" ? snap : (snap?.text || snap?.content || JSON.stringify(snap));
    }}
    const fullStr = String(text || "");
    process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
      ok: true,
      space: {space_id},
      label: tb.label || "",
      url: tb.url || "",
      source,
      total_len: fullStr.length,
      tail: fullStr.slice(-{tail_chars})
    }}) + "\\n");
    """
    return run_ego_js(js, timeout=30)

def cmd_ask(space_id, prompt_text, wait_sec=35, tail_chars=4500):
    if space_id == 0:
        raise ValueError("Safety guard: cmd_ask is not allowed on Space 0 (Argon primary chat).")
    expected_id = KNOWN_CHATS.get(space_id, "")
    prompt_file = BASE / f"_s1_ego_prompt_{space_id}.txt"
    prompt_file.write_text(prompt_text, encoding="utf-8")
    prompt_posix = str(prompt_file).replace("\\", "/")
    js = f"""
    const fs = await import('node:fs');
    const prompt = fs.readFileSync('{prompt_posix}', 'utf8');
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const task = await taskSpace({space_id});
    const tabs = await task.tabs();
    const expected = {json.dumps(expected_id)};
    const tb = (expected && tabs.find(t => String(t.url).includes(expected))) || tabs.find(t => String(t.url).includes('genspark.ai/agents'));
    if (!tb) throw new Error("Target agent tab not found in Space " + {space_id});
    const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);

    const beforeTxt = await Promise.race([
      page.evaluate(() => document.body ? document.body.innerText : ""),
      new Promise(r => setTimeout(() => r(""), 5000))
    ]);
    const beforeLen = String(beforeTxt || "").length;

    await page.fill('loc=css:textarea', prompt);
    await sleep(400);
    await page.keyboard.press('Enter');

    const maxWaitMs = {int(wait_sec * 1000)};
    const start = Date.now();
    let lastLen = beforeLen;
    let stableCount = 0;
    await sleep(4000);
    while (Date.now() - start < maxWaitMs) {{
      await sleep(2500);
      const cur = await Promise.race([
        page.evaluate(() => document.body ? document.body.innerText : ""),
        new Promise(r => setTimeout(() => r(""), 4000))
      ]);
      const curStr = String(cur || "");
      const isThinking = curStr.slice(-400).includes("Thinking...");
      if (curStr.length > beforeLen + 100 && !isThinking && curStr.length === lastLen) {{
        stableCount += 1;
        if (stableCount >= 2) break;
      }} else {{
        stableCount = 0;
      }}
      lastLen = curStr.length;
    }}

    let source = "innerText";
    let finalTxt = await Promise.race([
      page.evaluate(() => document.body ? document.body.innerText : ""),
      new Promise(r => setTimeout(() => r(""), 6000))
    ]);
    if (!finalTxt) {{
      source = "snapshot";
      const snap = await page.snapshot();
      finalTxt = typeof snap === "string" ? snap : (snap?.text || snap?.content || JSON.stringify(snap));
    }}
    const s = String(finalTxt || "");
    process.stdout.write("\\nS1EGO_JSON::" + JSON.stringify({{
      ok: true,
      space: {space_id},
      url: tb.url || "",
      source,
      elapsed_ms: Date.now() - start,
      total_len: s.length,
      tail: s.slice(-{tail_chars})
    }}) + "\\n");
    """
    try:
        return run_ego_js(js, timeout=wait_sec + 35)
    finally:
        if prompt_file.exists():
            try:
                prompt_file.unlink()
            except OSError:
                pass

def main():
    ap = argparse.ArgumentParser(description="S1 Ego-Lite Universal Nerve CLI v1.0")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("spaces")
    p_read = sub.add_parser("read")
    p_read.add_argument("space", type=int)
    p_read.add_argument("--tail", type=int, default=4000)
    p_ask = sub.add_parser("ask")
    p_ask.add_argument("space", type=int)
    p_ask.add_argument("--prompt-file", type=str, default="")
    p_ask.add_argument("--prompt", type=str, default="")
    p_ask.add_argument("--wait", type=int, default=40)
    args = ap.parse_args()

    if args.cmd == "spaces":
        res = cmd_spaces()
    elif args.cmd == "read":
        res = cmd_read(args.space, args.tail)
    elif args.cmd == "ask":
        txt = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else args.prompt
        res = cmd_ask(args.space, txt, wait_sec=args.wait)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
