
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
    vm.runInContext("\n    function fmt(num) {\n      return Math.round(num).toLocaleString('ko-KR') + ' \uc6d0';\n    }\n\n    function calculateSalaryAndSavings() {\n      const gross = parseFloat(document.getElementById('monthly-salary').value) || 0;\n      const meal = parseFloat(document.getElementById('tax-free-meal').value) || 0;\n      const years = parseFloat(document.getElementById('work-years').value) || 1;\n\n      const taxable = Math.max(0, gross - meal);\n\n      // 2026\ub144 \uae30\uc900 \uacf5\uc81c \uc694\uc728\n      const pension = Math.min(taxable * 0.045, 265500); // \uad6d\ubbfc\uc5f0\uae08 \uc0c1\ud55c \uc801\uc6a9\n      const health = taxable * 0.03545;\n      const care = health * 0.1295;\n      const employ = taxable * 0.009;\n\n      // \uac04\uc774\uc138\uc561 \ucd94\uc815 (\uc18c\ub4dd \uad6c\uac04\ubcc4 \uadfc\uc0ac\uce58)\n      let incomeTax = 0;\n      if (taxable > 5000000) incomeTax = taxable * 0.06;\n      else if (taxable > 3000000) incomeTax = taxable * 0.03;\n      else if (taxable > 1500000) incomeTax = taxable * 0.015;\n      else incomeTax = taxable * 0.005;\n\n      const localTax = incomeTax * 0.1;\n      const totalDeduction = pension + health + care + employ + incomeTax + localTax;\n      const net = Math.max(0, gross - totalDeduction);\n\n      // \ud1f4\uc9c1\uae08 \uacc4\uc0b0 (1\ub144 \uc774\uc0c1 \uadfc\ubb34 \uc2dc 1\ub144\ub2f9 1\uac1c\uc6d4\ubd84 \uae09\uc5ec)\n      const severance = gross * years;\n\n      document.getElementById('net-salary').innerText = fmt(net);\n      document.getElementById('total-deduction').innerText = fmt(totalDeduction);\n      document.getElementById('deduct-pension').innerText = fmt(pension);\n      document.getElementById('deduct-health').innerText = fmt(health);\n      document.getElementById('deduct-care').innerText = fmt(care);\n      document.getElementById('deduct-employ').innerText = fmt(employ);\n\n      document.getElementById('label-years').innerText = years;\n      document.getElementById('severance-pay').innerText = fmt(severance);\n\n      // 50:25:15:10 \uac00\uacc4 \ubc30\ubd84\n      document.getElementById('ratio-50').innerText = fmt(net * 0.50);\n      document.getElementById('ratio-25').innerText = fmt(net * 0.25);\n      document.getElementById('ratio-15').innerText = fmt(net * 0.15);\n      document.getElementById('ratio-10').innerText = fmt(net * 0.10);\n    }\n\n    function copySalarySummary() {\n      const net = document.getElementById('net-salary').innerText;\n      const sev = document.getElementById('severance-pay').innerText;\n      const text = `[2026 \ud55c\uac78\uc74c\uc529 \uae09\uc5ec\u00b7\ud1f4\uc9c1\uae08 \uacc4\uc0b0 \uc694\uc57d]\\n\u2022 \uc608\uc0c1 \uc6d4 \uc2e4\uc218\ub839\uc561: ${net}\\n\u2022 \uc608\uc0c1 \ubc95\uc815 \ud1f4\uc9c1\uae08: ${sev}\\n\u2022 \uc800\ucd95 \ud669\uae08\ube44\uc728: \uc0dd\ud65c 50% / \ud22c\uc790 25% / \ube44\uc0c1\uae08 15% / \ub098\ub214 10%\\n\u203b \uc77c\uc0c1 \ucc38\uace0\uc6a9 \ubb34\ub8cc \uacc4\uc0b0\uae30: ${window.location.href}`;\n      \n      if (navigator.clipboard) {\n        navigator.clipboard.writeText(text).then(() => {\n          alert('\ud83d\udccb \uacc4\uc0b0 \uc694\uc57d\uc774 \ubcf5\uc0ac\ub418\uc5c8\uc2b5\ub2c8\ub2e4! \uac00\uacc4\ubd80\ub098 \uba54\ubaa8\uc7a5\uc5d0 \ubd99\uc5ec\ub123\uc5b4 \ud65c\uc6a9\ud558\uc138\uc694.');\n        });\n      } else {\n        alert(text);\n      }\n    }\n\n    document.addEventListener('DOMContentLoaded', calculateSalaryAndSavings);\n  ", mockDOM, { timeout: 1000 });
} catch (err) {
    console.error('RUNTIME_ERR:' + err.message);
    process.exit(1);
}
