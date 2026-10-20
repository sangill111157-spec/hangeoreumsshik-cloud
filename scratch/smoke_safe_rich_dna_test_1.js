
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
    vm.runInContext("\n    const ARCHETYPES = {\n      A: {\n        badge: \"\ud83d\udc51\",\n        title: \"\ud669\uae08 \ubcf5\ub9ac \uc124\uacc4\uc790\ud615 (The Compound Master)\",\n        dna: \"DNA-COMPOUND-GOLD\",\n        desc: \"\uc2dc\uac04\uc758 \ub9c8\ubc95\uacfc \uc6d0\uce59\uc744 \uae4a\uc774 \uc2e0\ub8b0\ud558\ub294 \ud604\uc790\ud615 \uc790\uc0b0\uac00\uc785\ub2c8\ub2e4. \ub2e8\uae30 \uc720\ud589\uc774\ub098 \uc18c\uc74c\uc5d0 \ud754\ub4e4\ub9ac\uc9c0 \uc54a\uace0 \uc6b0\ub7c9\ud55c \uc790\uc0b0\uc744 \uafb8\uc900\ud788 \ubaa8\uc544\uac00\uba70, \ub9c8\uce68\ub0b4 \uac70\ub300\ud55c \ubcf5\ub9ac\uc758 \uae30\uc801\uc744 \ub9db\ubcf4\uac8c \ub429\ub2c8\ub2e4. 2026\ub144\uc740 \uadf8\ub3d9\uc548 \ub2e4\uc838\uc628 \uc8fc\ucda7\ub3cc \uc704\uc5d0\uc11c \uae30\ud558\uae09\uc218\uc801 \uc131\uc7a5\uc774 \uc2dc\uc791\ub418\ub294 \ud669\uae08\uae30\uc785\ub2c8\ub2e4!\"\n      },\n      B: {\n        badge: \"\ud83d\ude80\",\n        title: \"\ud601\uc2e0 \uc2dc\ub108\uc9c0 \uac1c\ucc99\uc790\ud615 (The Pioneer Builder)\",\n        dna: \"DNA-LEVERAGE-GROWTH\",\n        desc: \"\uc0c8\ub85c\uc6b4 \uae30\uc220\uacfc AI \uc790\ub3d9\ud654 \uc2dc\uc2a4\ud15c\uc758 \uc7a0\uc7ac\ub825\uc744 \ud55c\ubc1c \uc55e\uc11c \uaff0\ub6ab\uc5b4\ubcf4\ub294 \ubaa8\ud5d8\uac00\ud615 \uc790\uc0b0\uac00\uc785\ub2c8\ub2e4. \uc791\uc740 \uc790\ubcf8\uc774\ub77c\ub3c4 \uc9c0\ud61c\uc640 \ub808\ubc84\ub9ac\uc9c0\ub97c \uacb0\ud569\ud558\uc5ec 10\ubc30, 100\ubc30\uc758 \ubd80\uac00\uac00\uce58\ub97c \ucc3d\ucd9c\ud574\ub0b4\ub294 \ucc9c\uc7ac\uc801\uc778 \uc0ac\uc5c5\uac00 DNA\ub97c \uac00\uc9c0\uace0 \uc788\uc2b5\ub2c8\ub2e4!\"\n      },\n      C: {\n        badge: \"\ud83d\udee1\ufe0f\",\n        title: \"\ubb34\uacb0\uc810 \uae08\uace0 \uc218\ud638\uc790\ud615 (The Fortress Guardian)\",\n        dna: \"DNA-ZERO-RISK-SHIELD\",\n        desc: \"\uacf5\uaca9\ubcf4\ub2e4 \uc644\ubcbd\ud55c \ubc29\uc5b4\uac00 \uc704\ub300\ud55c \uc2b9\ub9ac\ub97c \ub9cc\ub4e0\ub2e4\ub294 \uc6cc\ub7f0 \ubc84\ud54f\uc758 \uc81c1\uc6d0\uce59\uc744 \uccb4\ud654\ud55c \uc218\ud638\uc790\ud615 \uc790\uc0b0\uac00\uc785\ub2c8\ub2e4. \ub4e4\uc5b4\uc624\ub294 \ub3c8\uacfc \ub098\uac00\ub294 \ub3c8\uc744 1\uc6d0 \ub2e8\uc704\uae4c\uc9c0 \uaf3c\uaf3c\ud788 \uc0b4\ud53c\uace0 \uc0c8\ub294 \uad6c\uba4d\uc744 \uc644\ubcbd\ud788 \ucc28\ub2e8\ud558\uc5ec \uc5b4\ub5a4 \uacbd\uc81c \uc704\uae30\uc5d0\ub3c4 \ud754\ub4e4\ub9ac\uc9c0 \uc54a\ub294 1\ub9cc \ub144 \ucca0\uc639\uc131\uc744 \uad6c\ucd95\ud569\ub2c8\ub2e4!\"\n      }\n    };\n\n    let latestResultText = \"\";\n\n    function runRichDnaAnalysis() {\n      const q1 = document.querySelector('input[name=\"q1\"]:checked')?.value || 'A';\n      const q2 = document.querySelector('input[name=\"q2\"]:checked')?.value || 'A';\n      const q3 = document.querySelector('input[name=\"q3\"]:checked')?.value || 'A';\n      const q4 = document.querySelector('input[name=\"q4\"]:checked')?.value || 'A';\n      const q5 = document.querySelector('input[name=\"q5\"]:checked')?.value || 'A';\n\n      const counts = { A: 0, B: 0, C: 0 };\n      [q1, q2, q3, q4, q5].forEach(v => counts[v] = (counts[v] || 0) + 1);\n\n      let primaryType = 'A';\n      if (counts.B > counts.A && counts.B >= counts.C) primaryType = 'B';\n      else if (counts.C > counts.A && counts.C > counts.B) primaryType = 'C';\n\n      const result = ARCHETYPES[primaryType] || ARCHETYPES.A;\n\n      document.getElementById('result-badge').innerText = result.badge;\n      document.getElementById('result-title').innerText = result.title;\n      document.getElementById('result-dna-code').innerText = result.dna;\n      document.getElementById('result-desc').innerText = result.desc;\n\n      document.getElementById('quiz-container').classList.add('hidden');\n      document.getElementById('result-card').classList.remove('hidden');\n\n      latestResultText = `[\ud83d\udc8e 2026 \ub098\uc758 \ubd80\uc790 DNA \uacb0\uacfc]\\n\uc720\ud615: ${result.badge} ${result.title}\\n\ucf54\ub4dc: ${result.dna}\\n\uc124\uba85: ${result.desc}\\n\u203b \ubb34\ub8cc \ud074\ub9b0\ub8f8 \ud14c\uc2a4\ud2b8: ${window.location.href}`;\n    }\n    window.runRichDnaAnalysis = runRichDnaAnalysis;\n\n    function copyResultToClipboard() {\n      if (!latestResultText) return;\n      if (navigator.clipboard) {\n        navigator.clipboard.writeText(latestResultText).then(() => {\n          alert('\ud83d\udccb \uacb0\uacfc \uce74\ub4dc\uac00 \ud074\ub9bd\ubcf4\ub4dc\uc5d0 \ubcf5\uc0ac\ub418\uc5c8\uc2b5\ub2c8\ub2e4! \uce74\uce74\uc624\ud1a1\uc774\ub098 SNS\uc5d0 \uacf5\uc720\ud574\ubcf4\uc138\uc694.');\n        }).catch(() => {\n          alert(latestResultText);\n        });\n      } else {\n        alert(latestResultText);\n      }\n    }\n    window.copyResultToClipboard = copyResultToClipboard;\n\n    function resetTest() {\n      document.getElementById('quiz-container').classList.remove('hidden');\n      document.getElementById('result-card').classList.add('hidden');\n    }\n    window.resetTest = resetTest;\n  ", mockDOM, { timeout: 1000 });
} catch (err) {
    console.error('RUNTIME_ERR:' + err.message);
    process.exit(1);
}
