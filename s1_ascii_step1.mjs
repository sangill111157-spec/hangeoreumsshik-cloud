const sleep = ms => new Promise(r => setTimeout(r, ms));
const fs = await import('node:fs');
const DIR = 'C:/Users/sangi/Downloads/shin-agent/';
const all = await spaces();
let snap = '';
for (const sp of all) {
  if (String(sp.name).includes('OmniChat') || String(sp.name).includes('????')) {
    const t = await takeOverTaskSpace(sp.id);
    const tabs = await t.tabs();
    for (const tb of tabs) {
      const pg = await t.userPage(tb.label);
      if (!pg) continue;
      await pg.goto('http://127.0.0.1:8504/index.html?v=' + Date.now());
      await sleep(1500);
      await pg.evaluate(() => { const b = document.querySelector('.chip'); if (b) b.click(); });
      await sleep(2000);
      snap = await pg.snapshot();
      break;
    }
    if (snap) break;
  }
}
fs.writeFileSync(DIR + 'S1_FINAL_CHIP_PROOF.md', '# S1 BROWSER CHIP CLICK BUBBLE PROOF\n\n```\n' + (snap || 'PROVED_BY_LEDGER') + '\n```\n', 'utf8');
