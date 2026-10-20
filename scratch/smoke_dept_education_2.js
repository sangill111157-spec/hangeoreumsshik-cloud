
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
    vm.runInContext("\n    function selectAnswer(ans) {\n      const fb = document.getElementById('quiz-feedback');\n      if (ans === 'A') {\n        fb.textContent = '\ud83d\udc96 [MQ \uacf5\uac10\ub825 +15 \ub2ec\uc131!] \uce5c\uad6c\uc758 \ub9c8\uc74c\uc5d0 \ub530\ub73b\ud55c \uc628\uae30\ub97c \uc120\ubb3c\ud588\uc2b5\ub2c8\ub2e4.';\n      } else {\n        fb.textContent = '\ud83c\udf1f [EQ \uacbd\uccad\ub825 +20 \ub2ec\uc131!] \ud568\uaed8 \uc788\uc5b4 \uc8fc\ub294 \uac83\ub9cc\uc73c\ub85c\ub3c4 \ud070 \ud798\uc774 \ub429\ub2c8\ub2e4.';\n      }\n    }\n\n    function recordAffirmation() {\n      const btn = document.getElementById('btn-speech');\n      const res = document.getElementById('speech-result');\n      btn.textContent = '\ud83d\udd34 \ub4e3\ub294 \uc911... (\ub9d0\uc500\ud558\uc138\uc694)';\n      setTimeout(() => {\n        btn.textContent = '\ud83c\udf99\ufe0f \ud655\uc5b8 \ub9d0\ud558\uae30 \uc2dc\uc791';\n        res.innerHTML = '<span class=\"text-emerald-400 font-bold\">\u2705 \uc778\uc2dd \uc644\ub8cc:</span> \"\ub098\ub294 \uc138\uc0c1\uc5d0\uc11c \uac00\uc7a5 \uc18c\uc911\ud55c \uc0ac\ub78c\uc774\ub2e4.\" (\uc790\uc2e0\uac10 \uc9c0\uc218: 100/100)';\n      }, 1500);\n    }\n\n    function issueCertificate() {\n      alert('\ud83c\udf93 [HGS-CERT] \uc815\uc2dd \ub514\uc9c0\ud138 \uc778\uc131 \uc778\uc99d\uc11c\uac00 \ubc1c\uae09\ub418\uc5b4 \ube14\ub85d\uccb4\uc778 \uae08\uace0\uc5d0 \uc601\uad6c \ub4f1\uc7ac\ub418\uc5c8\uc2b5\ub2c8\ub2e4!');\n    }\n\n    // \ud83d\udee1\ufe0f [v11.5] \uc11c\ube0c \uc5d0\uc774\uc804\ud2b8 \uc0c1\ud5a5 \ubcf4\uace0 \ud568\uc218\n    async function dispatchDeptSubAgent(agentId) {\n      const btn = document.getElementById('btn-dispatch-sub-agent');\n      const oldText = btn ? btn.innerHTML : '';\n      if (btn) {\n        btn.disabled = true;\n        btn.innerHTML = '<span>\u23f3</span><span>\uc810\uac80 \ubc0f \ub974\uace4-\uc54c\ud30c \uc0c1\ud5a5 \uc9c1\ubcf4 \uc911...</span>';\n      }\n      try {\n        const res = await fetch('/api/dept-sub-agent-dispatch', {\n          method: 'POST',\n          headers: { 'Content-Type': 'application/json' },\n          body: JSON.stringify({ agent_id: agentId, send_telegram: true })\n        });\n        const result = await res.json();\n        const data = result.data || result;\n        if (result.success || data.success) {\n          const repBox = document.getElementById('sub-agent-report-text');\n          const stampBox = document.getElementById('sub-agent-approval-stamp');\n          if (repBox && data.report) repBox.innerText = data.report;\n          if (stampBox && data.approval_stamp) stampBox.innerText = `\uacb0\uc7ac: ${data.approval_stamp} (${data.receipt_id || 'OK'})`;\n          alert(`\ud83d\udee1\ufe0f [${agentId} \uc0c1\ud5a5 \ubcf4\uace0 \uc644\ub8cc!]\\n\\n\u2022 \uc601\uc218\uc99d: ${data.receipt_id}\\n\u2022 \ubcf8\uad00 \ub974\uace4-\uc54c\ud30c(RGON-ALPHA) \uc218\uc2e0 \uacb0\uc7ac \uc644\ub8cc!\\n\u2022 \ub300\ud45c\ub2d8 \uc2a4\ub9c8\ud2b8\ud3f0 \ud154\ub808\uadf8\ub7a8 \ubc1c\uc1a1 \uc644\ub8cc!`);\n        } else {\n          alert('\uc0c1\ud5a5 \ubcf4\uace0 \uc751\ub2f5: ' + (result.message || '\uc644\ub8cc'));\n        }\n      } catch (err) {\n        alert('\uc11c\ube0c \uc5d0\uc774\uc804\ud2b8 \ud638\ucd9c \uc624\ub958: ' + err.message);\n      } finally {\n        if (btn) {\n          btn.disabled = false;\n          btn.innerHTML = oldText;\n        }\n      }\n    }\n    window.dispatchDeptSubAgent = dispatchDeptSubAgent;\n\n    async function loadDeptSubAgentStatus(agentId) {\n      try {\n        const res = await fetch('/api/dept-sub-agents?dept=' + encodeURIComponent(agentId) + '&t=' + Date.now());\n        if (!res.ok) return;\n        const result = await res.json();\n        const ag = result.agent || (result.sub_agents && result.sub_agents[agentId]);\n        if (ag) {\n          const repBox = document.getElementById('sub-agent-report-text');\n          const stampBox = document.getElementById('sub-agent-approval-stamp');\n          if (repBox && ag.last_report) repBox.innerText = ag.last_report;\n          if (stampBox && ag.approval_stamp) stampBox.innerText = `\uacb0\uc7ac: ${ag.approval_stamp} (${ag.last_receipt_id || 'OK'})`;\n        }\n      } catch (e) {\n        console.warn('Sub agent status load failed:', e);\n      }\n    }\n    window.loadDeptSubAgentStatus = loadDeptSubAgentStatus;\n\n    document.addEventListener('DOMContentLoaded', () => {\n      loadDeptSubAgentStatus('ALPHA-D4');\n    });\n  ", mockDOM, { timeout: 1000 });
} catch (err) {
    console.error('RUNTIME_ERR:' + err.message);
    process.exit(1);
}
