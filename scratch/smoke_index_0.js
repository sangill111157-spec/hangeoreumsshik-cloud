
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
    vm.runInContext("\n    (function() {\n      const REQUIRED_VER = 'v3.3';\n      const urlParams = new URLSearchParams(window.location.search);\n      const urlVer = urlParams.get('v');\n      const storedVer = localStorage.getItem('hgs_app_version');\n      \n      // \uad6c\ubc84\uc804(v3.1 \ub4f1) \ubb35\uc740 \uce90\uc2dc \uac10\uc9c0 \uc2dc \uc989\uc2dc v960 \uac15\uc81c \uac31\uc2e0\n      if (!urlVer || !urlVer.includes('96') || storedVer !== REQUIRED_VER) {\n        localStorage.setItem('hgs_app_version', REQUIRED_VER);\n        if (!urlVer || !urlVer.includes('96')) {\n          const tab = urlParams.get('tab') || 'command';\n          const newUrl = window.location.pathname + '?v=960_' + Date.now() + '&tab=' + tab + window.location.hash;\n          window.location.replace(newUrl);\n        }\n      }\n    })();\n  ", mockDOM, { timeout: 1000 });
} catch (err) {
    console.error('RUNTIME_ERR:' + err.message);
    process.exit(1);
}
