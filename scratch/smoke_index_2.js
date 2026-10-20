
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
    vm.runInContext("\n    tailwind.config = {\n      darkMode: 'class',\n      theme: {\n        extend: {\n          colors: {\n            space: {\n              950: '#030712',\n              900: '#060913',\n              850: '#0b1120',\n              800: '#0f172a',\n            }\n          },\n          fontFamily: {\n            sans: ['Pretendard', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],\n          }\n        }\n      }\n    };\n  ", mockDOM, { timeout: 1000 });
} catch (err) {
    console.error('RUNTIME_ERR:' + err.message);
    process.exit(1);
}
