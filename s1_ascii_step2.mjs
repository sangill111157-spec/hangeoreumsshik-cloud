const sleep = ms => new Promise(r => setTimeout(r, ms));
const fs = await import('node:fs');
const DIR = 'C:/Users/sangi/Downloads/shin-agent/';
const msg = fs.readFileSync(DIR + 's1_msg.txt', 'utf8').trim();
const t0 = await takeOverTaskSpace(0);
const tabs = await t0.tabs();
for (const tb of tabs) {
  const pg = await t0.userPage(tb.label);
  if (!pg) continue;
  try {
    await sleep(500);
    await pg.click('textarea');
    await pg.fill('textarea', msg);
    await sleep(500);
    await pg.press('textarea', 'Enter');
    console.log('REPORT_ENTER_100_OK_ON_' + tb.label);
    break;
  } catch (e) {}
}
