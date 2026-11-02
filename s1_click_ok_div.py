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
    const okDiv = document.querySelector('.session-limit-dialog .button.ok') || document.querySelector('.session-limit-dialog .button');
    if (okDiv) {
      okDiv.click();
      return { clicked: true, text: okDiv.innerText };
    }
    return { clicked: false };
  });
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify(res) + '\\n');
} catch(e) {
  process.stdout.write('\\nS1EGO_JSON::' + JSON.stringify({ error: String(e) }) + '\\n');
} finally {
  try { if (task && typeof task.handOff === 'function') await task.handOff(); } catch (_) {}
}
"""

print(json.dumps(s1_ego.run_ego_js(js), indent=2, ensure_ascii=False))

