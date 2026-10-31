
const t = await taskSpace(0);
const tbs = await t.tabs();
const out = [];
for (const b of tbs) {
  if (String(b.url).includes('genspark.ai/agents')) {
    const p = await t.userPage(b.label);
    const txt = await p.evaluate(() => document.body ? document.body.innerText : '');
    out.push({space:0, label:b.label, url:b.url, title:b.title, text:txt});
  }
}
console.log('__S1_JSON__' + JSON.stringify(out));
