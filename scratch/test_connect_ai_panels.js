// scratch/test_connect_ai_panels.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const htmlPath = path.join(__dirname, '..', 'dashboard', 'departments', 'dept_connect_ai.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// HTML에서 각 ID 블록의 원본 마크업을 추출하는 헬퍼
function extractElementMarkup(id) {
  const regex = new RegExp(`<[^>]+id=["']${id}["'][^>]*>([\\s\\S]*?)<\\/[a-zA-Z0-9]+>`, 'i');
  const m = html.match(regex);
  return m ? m[0] : '';
}

class MockElement {
  constructor(id, tagName = 'div', initialHTML = '') {
    this.id = id;
    this.tagName = tagName;
    this.style = { display: 'none' };
    this.innerHTML = initialHTML;
    this.innerText = '';
    this.textContent = '';
    this.value = '29000';
    this.classList = {
      _classes: new Set(['hidden']),
      add: (c) => this.classList._classes.add(c),
      remove: (c) => this.classList._classes.delete(c),
      contains: (c) => this.classList._classes.has(c)
    };
  }
  querySelector(sel) { return new MockElement('sub'); }
  querySelectorAll() { return []; }
  scrollIntoView() {}
}

const elements = {};
function getEl(id) {
  if (!elements[id]) {
    const markup = extractElementMarkup(id);
    elements[id] = new MockElement(id, 'div', markup);
  }
  return elements[id];
}

// 사전 등록: 주요 패널들
['stitch-result-panel', 'script-result-panel', 'bm-result-panel', 'corps-result-panel',
 'stitch-palette-chips', 'stitch-code-output', 'script-result-content',
 'bm-unit-price', 'bm-sales-qty', 'bm-table-body', 'corps-cards-container'].forEach(id => {
  getEl(id);
});

const mockWindow = {
  document: {
    getElementById: (id) => getEl(id),
    querySelector: (sel) => getEl(sel.replace('#', '')),
    querySelectorAll: () => [],
    createElement: (tag) => new MockElement('created', tag),
    addEventListener: (evt, cb) => cb && cb()
  },
  navigator: {
    clipboard: {
      writeText: () => Promise.resolve()
    }
  },
  location: {
    origin: 'http://127.0.0.1:8501',
    href: 'http://127.0.0.1:8501'
  },
  addEventListener: (evt, cb) => cb && cb(),
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  alert: (msg) => {},
  console: console
};
mockWindow.window = mockWindow;

// dept_connect_ai.html 내 모든 script 추출
const scriptMatches = [...html.matchAll(/<script[\s\S]*?>([\s\S]*?)<\/script>/gi)];
const fullScript = scriptMatches.map(m => m[1]).join('\n;\n');

const context = vm.createContext(mockWindow);
vm.runInContext(fullScript, context);

// 4대 함수 실행 및 검증
const results = {};

// 1) Stitch 2.0
if (typeof context.toggleStitchPanel === 'function') {
  context.toggleStitchPanel(true);
  const el = getEl('stitch-result-panel');
  const chips = getEl('stitch-palette-chips');
  // 패널 내부 콘텐츠 합산
  const fullContent = el.innerHTML + (chips ? chips.innerHTML : '');
  results.stitch = {
    display: el.style.display,
    len: fullContent.length,
    ok: el.style.display !== 'none' && fullContent.length >= 200
  };
} else {
  results.stitch = { ok: false, error: 'toggleStitchPanel not found' };
}

// 2) Script Studio
if (typeof context.toggleScriptPanel === 'function') {
  context.toggleScriptPanel(true);
  const el = getEl('script-result-panel');
  const content = getEl('script-result-content');
  const fullContent = el.innerHTML + (content ? content.innerHTML : '');
  results.script = {
    display: el.style.display,
    len: fullContent.length,
    ok: el.style.display !== 'none' && fullContent.length >= 200
  };
} else {
  results.script = { ok: false, error: 'toggleScriptPanel not found' };
}

// 3) BM Simulator
if (typeof context.toggleBmPanel === 'function') {
  context.toggleBmPanel(true);
  const el = getEl('bm-result-panel');
  const tbody = getEl('bm-table-body');
  const fullContent = el.innerHTML + (tbody ? tbody.innerHTML : '');
  results.bm = {
    display: el.style.display,
    len: fullContent.length,
    ok: el.style.display !== 'none' && fullContent.length >= 200
  };
} else {
  results.bm = { ok: false, error: 'toggleBmPanel not found' };
}

// 4) Corps Dispatch
if (typeof context.toggleCorpsPanel === 'function') {
  context.toggleCorpsPanel(true);
  const el = getEl('corps-result-panel');
  const cards = getEl('corps-cards-container');
  const fullContent = el.innerHTML + (cards ? cards.innerHTML : '');
  results.corps = {
    display: el.style.display,
    len: fullContent.length,
    ok: el.style.display !== 'none' && fullContent.length >= 200
  };
} else {
  results.corps = { ok: false, error: 'toggleCorpsPanel not found' };
}

console.log(JSON.stringify(results));
const allOk = Object.values(results).every(r => r.ok);
process.exit(allOk ? 0 : 1);
