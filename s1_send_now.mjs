const sleep = ms => new Promise(r => setTimeout(r, ms));
const fs = await import('node:fs');
const msg = fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/s1_msg.txt', 'utf8').trim();
const t0 = await takeOverTaskSpace(0);
for (const pid of ['p1', 'p2', 'p3', 'p4']) {
  try {
    const pg = await t0.userPage(pid);
    if (!pg) continue;
    await pg.click('textarea', { timeout: 2000 });
    await pg.fill('textarea', msg);
    await sleep(400);
    await pg.press('textarea', 'Enter');
    console.log('SENT_OK_ON_' + pid);
    break;
  } catch (e) {}
}
