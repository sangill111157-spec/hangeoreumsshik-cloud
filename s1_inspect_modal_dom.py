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
    const dialog = document.querySelector('.session-limit-dialog') || document.querySelector('[class*="session-limit"]');
    if (!dialog) return { found: false };
    const elements = Array.from(dialog.querySelectorAll('*')).map(el => ({
      tag: el.tagName,
      cls: el.className,
      text: el.innerText
    }));
    return { found: true, html: dialog.outerHTML.slice(0, 1000), elements };
  });
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify(res) + '\\n');
} catch(e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ error: String(e) }) + '\\n');
} finally {
  try { if (task && typeof task.handOff === 'function') await task.handOff(); } catch (_) {}
}
"""

print(json.dumps(s1_ego.run_ego_js(js), indent=2, ensure_ascii=False))

