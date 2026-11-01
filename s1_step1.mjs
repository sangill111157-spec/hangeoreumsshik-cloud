const sleep = ms => new Promise(r => setTimeout(r, ms));
const fs = await import('node:fs');
const all = await spaces();
const omni = all.find(s => s.name === 'S1_OmniChat');
if (omni) {
  const t = await takeOverTaskSpace(omni.id);
  const pg = await t.userPage('p1');
  await pg.goto('http://127.0.0.1:8504/index.html?v=' + Date.now());
  await sleep(1500);
  await pg.evaluate(() => { const b = document.querySelector('.chip'); if (b) b.click(); });
  await sleep(2000);
  const snap = await pg.snapshot();
  fs.writeFileSync('S1_FINAL_CHIP_PROOF.md', '# S1 BROWSER CHIP CLICK BUBBLE PROOF\n\n```\n' + snap + '\n```\n', 'utf8');
}
