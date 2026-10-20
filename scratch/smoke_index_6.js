
const vm = require('vm');
const mockDOM = {
    window: {
        location: { pathname: '/', search: '', hash: '', replace: () => {}, href: '' },
        localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
        document: {
            getElementById: () => ({ innerText: '', innerHTML: '', classList: { add: () => {}, remove: () => {}, contains: () => false } }),
            querySelectorAll: () => [],
            addEventListener: () => {}
        },
        AudioContext: class { resume() {} createOscillator() { return { type: '', frequency: { setValueAtTime: () => {} }, connect: () => {}, start: () => {}, stop: () => {} }; } createGain() { return { gain: { setValueAtTime: () => {}, linearRampToValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} }, connect: () => {} }; } },
        console: console,
        setTimeout: setTimeout,
        setInterval: setInterval,
        clearTimeout: clearTimeout,
        clearInterval: clearInterval,
        requestAnimationFrame: (cb) => cb(),
        alert: () => {}
    },
    document: null,
    localStorage: null,
    console: console,
    fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
};
mockDOM.document = mockDOM.window.document;
mockDOM.localStorage = mockDOM.window.localStorage;
try {
    vm.createContext(mockDOM);
    vm.runInContext("\nasync function fetchTreasuryQuickStatus() {\n  try {\n    const res = await fetch('/api/treasury-status');\n    if (!res.ok) return;\n    const data = await res.json();\n    const s = data.summary || {};\n    const elemIn = document.getElementById('main-total-in');\n    const elemOut = document.getElementById('main-total-out');\n    const elemNet = document.getElementById('main-net-profit');\n    if (elemIn) elemIn.innerText = Math.round(s.total_in || 0).toLocaleString('ko-KR') + '\uc6d0';\n    if (elemOut) elemOut.innerText = Math.round(s.total_out || 0).toLocaleString('ko-KR') + '\uc6d0';\n    if (elemNet) elemNet.innerText = Math.round(s.net_profit || 0).toLocaleString('ko-KR') + '\uc6d0';\n  } catch (e) {\n    console.warn('[Treasury] Quick status skip:', e);\n  }\n}\n", mockDOM, { timeout: 1000 });
} catch (err) {
    console.error('RUNTIME_ERR:' + err.message);
    process.exit(1);
}
