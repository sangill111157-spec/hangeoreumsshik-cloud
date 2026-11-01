
const CFG = {"roles": {"argon": ["c1647638", "\uc644\uacf5 \ud30c\uc774\ud504\ub77c\uc778", "\uc778\uc218\uc778\uacc4", "0\ubc88"], "gpt": ["c1c2", "GPT-6.1", "chatgpt.com"], "claude": ["b0c3", "Claude Opus", "claude.ai"]}, "switchFirst": false, "dumpAll": true};
const out = { tabs: [], errors: [] };
function roleOf(t, snapText) {
  const hay = (t.title || "") + " " + (t.url || "") + " " + (snapText || "").slice(0, 2000);
  for (const [role, keys] of Object.entries(CFG.roles)) {
    if (keys.some(k => hay.includes(k))) return role;
  }
  return null;
}
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
    let task;
    try { task = sp.ownership === "user" ? await claimTaskSpace(sp.id) : await taskSpace(sp.id); }
    catch (e) { out.errors.push("space " + sp.id + ": " + e.message); continue; }
    let tabs = [];
    try { tabs = await task.tabs(); }
    catch (e) { out.errors.push("tabs " + sp.id + ": " + e.message); continue; }
    for (const tb of tabs) {
      const base = { space: sp.id, label: tb.label || null, title: tb.title || "", url: tb.url || "", active: !!tb.active };
      try {
        const page = tb.label ? task.page(tb.label) : await task.adopt(tb.page);
        let text = "";
        if (false) { try { text = toText(await page.snapshot()); } catch (e) { text = ""; } }
        if (!text) {
          try {  } catch (e) {}
          try { text = toText(await page.snapshot()); } catch (e) { text = ""; }
        }
        const role = roleOf(tb, text) || "none";
        if (role !== "none" || CFG.dumpAll) {
          out.tabs.push({ ...base, role, text });
        }
      } catch (e) { out.errors.push("tab " + base.title + ": " + e.message); }
    }
  }
} catch (e) { out.errors.push("fatal: " + e.message); }
process.stdout.write("\nS1JSON::" + JSON.stringify(out) + "\n");
