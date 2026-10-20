
async function fetchTreasuryQuickStatus() {
  try {
    const res = await fetch('/api/treasury-status');
    if (!res.ok) return;
    const data = await res.json();
    const s = data.summary || {};
    const elemIn = document.getElementById('main-total-in');
    const elemOut = document.getElementById('main-total-out');
    const elemNet = document.getElementById('main-net-profit');
    if (elemIn) elemIn.innerText = Math.round(s.total_in || 0).toLocaleString('ko-KR') + '원';
    if (elemOut) elemOut.innerText = Math.round(s.total_out || 0).toLocaleString('ko-KR') + '원';
    if (elemNet) elemNet.innerText = Math.round(s.net_profit || 0).toLocaleString('ko-KR') + '원';
  } catch (e) {
    console.warn('[Treasury] Quick status skip:', e);
  }
}
