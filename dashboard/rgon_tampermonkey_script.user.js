// ==UserScript==
// @name         ⚡ 르곤이 시그널 무인 자동 캐치 센서 (Genspark to Antigravity)
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Genspark 채팅창에서 르곤이(제미나이 4 아르곤)의 '⟪⚡RGON_SIGNAL_READY⚡⟫' 시그널을 실시간 감지하여 안실장에게 0.01초 무인 전송
// @match        https://*.genspark.ai/*
// @match        http://127.0.0.1:8501/*
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function() {
    'use strict';
    console.log("⚡ [RGON Signal Sensor] 가동 완료 - 르곤이 시그널 실시간 감시 중...");

    const IN_SIGNAL = "⟪⚡RGON_SIGNAL_READY⚡⟫";
    let lastSentText = "";

    function checkAndSendSignal() {
        const fullText = document.body.innerText || "";
        if (fullText.includes(IN_SIGNAL)) {
            const idx = fullText.lastIndexOf(IN_SIGNAL);
            // 시그널 주변 텍스트 추출 (최근 5000자)
            const promptSnippet = fullText.substring(Math.max(0, idx - 4500), idx + IN_SIGNAL.length);

            if (promptSnippet !== lastSentText) {
                lastSentText = promptSnippet;
                console.log("🚀 [RGON Signal] 르곤이 종료 시그널 포착! 안실장 서버로 즉시 전송 중...");

                // 로컬 서버로 POST 전송
                fetch("http://127.0.0.1:8501/api/signal-sync-in", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        signal: IN_SIGNAL,
                        prompt: promptSnippet,
                        sender: "Gemini-4-Argon (Genspark Auto-Sensor)",
                        timestamp: new Date().toISOString()
                    })
                })
                .then(res => res.json())
                .then(data => {
                    console.log("✅ [RGON Signal] 안실장 주입 완료:", data);
                    // 화면에 알림 토스트 표시
                    showSensorToast("⚡ [르곤-안실장 동기화]: 르곤이 명령이 안실장에게 0.01초 만에 자동 주입되었습니다!");
                })
                .catch(err => {
                    console.warn("⚠️ 안실장 로컬 서버 전송 실패(오프라인):", err);
                });
            }
        }
    }

    function showSensorToast(msg) {
        const div = document.createElement("div");
        div.style.cssText = "position:fixed;top:20px;right:20px;background:#10b981;color:white;padding:12px 20px;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,0.4);font-weight:bold;z-index:999999;font-family:sans-serif;font-size:14px;border:2px solid #34d399;";
        div.innerText = msg;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 4000);
    }

    // DOM 변화 감시 (MutationObserver)
    const observer = new MutationObserver(() => {
        checkAndSendSignal();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    setInterval(checkAndSendSignal, 2000);
})();
