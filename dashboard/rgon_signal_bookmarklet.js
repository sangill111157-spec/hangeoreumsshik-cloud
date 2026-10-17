// javascript: 북마클릿 (Genspark 탭 주소창 또는 북마크바에서 클릭 시 르곤이 시그널 감시 센서 즉시 작동)
javascript:(function(){
    const sig = "⟪⚡RGON_SIGNAL_READY⚡⟫";
    const text = document.body.innerText || "";
    if (!text.includes(sig)) {
        alert("🔍 현재 페이지에서 르곤이의 '" + sig + "' 시그널을 찾지 못했습니다. 르곤이 답변 완료 후 다시 눌러주세요!");
        return;
    }
    const idx = text.lastIndexOf(sig);
    const promptSnippet = text.substring(Math.max(0, idx - 4500), idx + sig.length);
    fetch("http://127.0.0.1:8501/api/signal-sync-in", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            signal: sig,
            prompt: promptSnippet,
            sender: "Gemini-4-Argon (Bookmarklet)",
            timestamp: new Date().toISOString()
        })
    })
    .then(r => r.json())
    .then(res => {
        alert("⚡ [성공] 르곤이 명령서가 안실장에게 0.01초 만에 무인 전송되었습니다!\n" + res.message);
    })
    .catch(e => {
        // 서버 연결 실패 시 클립보드에 바로 복사
        navigator.clipboard.writeText(promptSnippet).then(() => {
            alert("📋 로컬 서버 오프라인으로 인해 르곤이 명령서가 클립보드에 즉시 복사되었습니다!\n안실장 채팅창에 붙여넣어주세요.");
        });
    });
})();
