
import fs from 'node:fs';
const prompt = fs.readFileSync('state/triumvirate_prompt.txt', 'utf8');
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function askSpace(spaceId) {
  const t = await taskSpace(spaceId);
  const tbs = await t.tabs();
  const target = tbs.find(b => String(b.url).includes('genspark.ai/agents')) || tbs[0];
  const p = await t.userPage(target.label);
  await p.evaluate((msg) => {
    const ta = document.querySelector('textarea');
    if (!ta) return 'NO_TA';
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(ta, msg);
    ta.dispatchEvent(new Event('input', { bubbles: true }));
    ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
    const btns = Array.from(document.querySelectorAll('button'));
    const sendBtn = btns.find(b => b.querySelector('svg') && !b.disabled && (b.getAttribute('type') === 'submit' || b.className.includes('send') || b.parentElement === ta.parentElement));
    if (sendBtn) sendBtn.click();
    return 'SENT';
  }, prompt);
}

await askSpace(3);
await askSpace(2);
await sleep(32000);

async function readSpace(spaceId) {
  const t = await taskSpace(spaceId);
  const tbs = await t.tabs();
  const target = tbs.find(b => String(b.url).includes('genspark.ai/agents')) || tbs[0];
  const p = await t.userPage(target.label);
  const txt = await p.evaluate(() => document.body ? document.body.innerText : '');
  return txt.slice(-3500);
}

const gptAns = await readSpace(2);
const claudeAns = await readSpace(3);
console.log('__ANS_JSON__' + JSON.stringify({ gpt: gptAns, claude: claudeAns }));
