const sleep = ms => new Promise(r => setTimeout(r, ms));
const fs = await import('node:fs');
const msg = fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/s1_msg.txt', 'utf8').trim();
const t0 = await taskSpace(0);
const tabs = await t0.tabs();
for (const x of tabs) {
  if (String(x.url).includes('genspark')) {
    const p0 = x.label ? t0.page(x.label) : await t0.adopt(x.page);
    const s0 = await p0.snapshot();
    const m0 = s0.match(/textbox[^\n]*\[ref=(\d+)/);
    if (m0) {
      await p0.fill(m0[1], msg);
      await sleep(500);
      await p0.keyboard.press('Enter');
      console.log('AUTO_ENTER_SUCCESS_REF_' + m0[1]);
    }
    break;
  }
}
