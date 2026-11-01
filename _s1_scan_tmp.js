
const out = { tabs: [], errors: [] };
function toText(s) {
  if (s == null) return "";
  if (typeof s === "string") return s;
  if (typeof s.text === "string") return s.text;
  if (typeof s.content === "string") return s.content;
  try { return JSON.stringify(s); } catch (e) { return String(s); }
}
try {
  const spaces = await listTaskSpaces();
  for (const sp of spaces) {
    if (sp.id !== 0) continue;
    const task = await taskSpace(sp.id);
    const tabs = await task.tabs();
    for (const tb of tabs) {
      const u = String(tb.url || "");
      if (!u.includes("genspark.ai/agents")) continue;
      const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
      let text = await Promise.race([page.evaluate(() => document.body ? document.body.innerText : ""), new Promise(r => setTimeout(() => r(""), 8000))]);
      let snapFallback = false; if (!text) { snapFallback = true; text = toText(await page.snapshot()); }
      out.tabs.push({ space: sp.id, label: tb.label || "p1", title: tb.title || "", url: u, text, snapFallback });
    }
  }
} catch (e) { out.errors.push(e.message); }
process.stdout.write("\nS1JSON::" + JSON.stringify(out) + "\n");
