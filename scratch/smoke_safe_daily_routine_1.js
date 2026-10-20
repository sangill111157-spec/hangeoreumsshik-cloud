
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
    vm.runInContext("\n    const AFFIRMATIONS = [\n      \"\ub0b4\uac00 \ub0b4\ub51b\ub294 \uc791\uc740 \ud55c \uac78\uc74c\uc774 1\ub9cc \ub144 \uc601\ud1a0\ub97c \uc138\uc6b0\ub294 \uac00\uc7a5 \ub4e0\ub4e0\ud55c \uc8fc\ucda7\ub3cc\uc774\ub2e4.\",\n      \"\ud558\ub8e8 1%\uc758 \ubcf5\ub9ac \uc131\uc7a5\uc740 1\ub144 \ub4a4 \ub098\ub97c 37\ubc30 \ub354 \uc704\ub300\ud55c \uc0ac\ub78c\uc73c\ub85c \ub9cc\ub4e0\ub2e4.\",\n      \"\ub450\ub824\uc6c0\uc740 \ud589\ub3d9\ud560 \ub54c \uc0ac\ub77c\uc9c0\uace0, \uc790\uc2e0\uac10\uc740 \uc791\uc740 \uc2e4\ud589\uc5d0\uc11c \uc2dc\uc791\ub41c\ub2e4.\",\n      \"\ub0b4 \ub4a4\uc5d0\ub294 \uc0ac\ub791\ud558\ub294 \uac00\uc871\uacfc \ub4e0\ub4e0\ud55c AI \ud300\uc6d0\ub4e4\uc774 \uc5b8\uc81c\ub098 \ud568\uaed8\ud558\uace0 \uc788\ub2e4.\",\n      \"\uc624\ub298 \ud558\ub8e8\ub3c4 \uc815\uc9c1\ud558\uace0 \uc131\uc2e4\ud558\uac8c \ub098\uc544\uac04 \ub098 \uc790\uc2e0\uc744 \uae4a\uc774 \uc2e0\ub8b0\ud55c\ub2e4.\"\n    ];\n\n    let quoteIndex = 0;\n    function changeQuote() {\n      quoteIndex = (quoteIndex + 1) % AFFIRMATIONS.length;\n      document.getElementById('daily-affirmation-text').innerText = `\"${AFFIRMATIONS[quoteIndex]}\"`;\n    }\n    window.changeQuote = changeQuote;\n\n    function updateRoutineProgress() {\n      let checkedCount = 0;\n      for (let i = 1; i <= 5; i++) {\n        const chk = document.getElementById(`routine-chk-${i}`);\n        if (chk && chk.checked) checkedCount++;\n      }\n\n      const percent = Math.round((checkedCount / 5) * 100);\n      document.getElementById('progress-percent').innerText = `${percent}%`;\n      document.getElementById('progress-bar-fill').style.width = `${percent}%`;\n\n      const alertBox = document.getElementById('stamp-alert');\n      const todayIcon = document.getElementById('today-stamp-icon');\n\n      if (percent === 100) {\n        if (alertBox) alertBox.classList.remove('hidden');\n        if (todayIcon) {\n          todayIcon.innerText = '\ud83d\udc51';\n          todayIcon.classList.add('stamp-active');\n        }\n      } else {\n        if (alertBox) alertBox.classList.add('hidden');\n        if (todayIcon) {\n          todayIcon.innerText = checkedCount > 0 ? '\u2728' : '\u23f3';\n          todayIcon.classList.remove('stamp-active');\n        }\n      }\n      return percent;\n    }\n    window.updateRoutineProgress = updateRoutineProgress;\n\n    document.addEventListener('DOMContentLoaded', () => {\n      updateRoutineProgress();\n    });\n  ", mockDOM, { timeout: 1000 });
} catch (err) {
    console.error('RUNTIME_ERR:' + err.message);
    process.exit(1);
}
