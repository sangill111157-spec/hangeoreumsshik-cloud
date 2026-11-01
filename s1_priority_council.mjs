
const fs = await import('node:fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const promptText = fs.readFileSync('C:/Users/sangi/Downloads/shin-agent/s1_agenda.txt', 'utf-8');

for (const sid of [2, 3]) {
  try {
    const ts = await takeOverTaskSpace(sid, {leaseMs: 90000});
    const tabs = await ts.tabs();
    for (const tb of tabs) {
      const pg = tb.label ? ts.page(tb.label) : await ts.adopt(tb.page);
      if (String(tb.url).includes('genspark.ai/agents')) {
        await pg.bringToFront();
        const s = await pg.snapshot();
        const m = s.match(/textbox[^\n]*\[ref=(\d+)/);
        if (m) {
          await pg.fill(m[1], promptText);
          await pg.keyboard.press('Enter');
        }
        break;
      }
    }
    await ts.yieldToUser({message: '급선무 순위 선정 안건 상정 완료'});
  } catch(e) { console.log('SEND_ERR_' + sid, e.message); }
}

await sleep(75000);

let report = '# S1 TRIUMVIRATE NEXT PRIORITY COUNCIL REPORT\n\n';
for (const sid of [2, 3]) {
  try {
    const ts = await takeOverTaskSpace(sid, {leaseMs: 20000});
    const tabs = await ts.tabs();
    for (const tb of tabs) {
      const pg = tb.label ? ts.page(tb.label) : await ts.adopt(tb.page);
      if (String(tb.url).includes('genspark.ai/agents')) {
        await pg.bringToFront();
        let txt = '';
        try {
          txt = await pg.evaluate(() => document.body.innerText);
        } catch(e) {
          txt = await pg.snapshot();
        }
        report += '## SPACE ' + sid + ' (' + (sid===2?'GPT-6.1 Sol':'Claude Opus 5.5') + ')\n' + txt.slice(-6500) + '\n\n---\n\n';
        break;
      }
    }
    await ts.yieldToUser({message: '수거 완료'});
  } catch(e) { report += '## SPACE ' + sid + ' ERR: ' + e.message + '\n\n'; }
}

fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_NEXT_PRIORITY_COUNCIL.md', report, 'utf-8');
fs.writeFileSync('C:/Users/sangi/Downloads/shin-agent/S1_OUT.md', report, 'utf-8');
