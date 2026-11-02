import s1_ego
import json

js = """
try {
  let task;
  try { task = await taskSpace(0); await task.tabs(); }
  catch (e) { task = await takeOverTaskSpace(0); }
  const tabs = await task.tabs();
  let page = tabs[0].label ? task.page(tabs[0].label) : await task.adopt(tabs[0].page);

  const res = await page.evaluate(() => {
    // Check if generating
    const stopBtn = Array.from(document.querySelectorAll("button, [role='button']")).some(b => {
      const t = (b.innerText || b.getAttribute("aria-label") || "").toLowerCase();
      return t === "stop" || t === "중지" || t.includes("생성 중지");
    });

    // Get all assistant messages
    const msgs = Array.from(document.querySelectorAll('.answer-markdown, .markdown-viewer, [class*="agent-message"], [class*="assistant-message"]'));
    let latestAssistant = "";
    if (msgs.length > 0) {
      latestAssistant = msgs[msgs.length - 1].innerText.trim();
    } else {
      // fallback: find all message containers
      const allMsgs = Array.from(document.querySelectorAll('div[data-message-id], div[class*="message"]'));
      if (allMsgs.length > 0) {
        latestAssistant = allMsgs[allMsgs.length - 1].innerText.trim();
      }
    }

    // Also get the last user message to see what was sent
    const userMsgs = Array.from(document.querySelectorAll('div, article, p')).filter(el => {
      return el.innerText && el.innerText.startsWith('[S1_NERVE_REPORT v2]');
    });
    let lastUser = "";
    if (userMsgs.length > 0) {
      lastUser = userMsgs[userMsgs.length - 1].innerText.trim().slice(0, 300);
    }

    return {
      generating: stopBtn,
      total_assistant_elements: msgs.length,
      latest_assistant_text: latestAssistant,
      last_user_snippet: lastUser
    };
  });
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify(res) + '\\n');
} catch(e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ error: String(e) }) + '\\n');
} finally {
  try { if (task && typeof task.handOff === 'function') await task.handOff(); } catch (_) {}
}
"""

print(json.dumps(s1_ego.run_ego_js(js), indent=2, ensure_ascii=False))

