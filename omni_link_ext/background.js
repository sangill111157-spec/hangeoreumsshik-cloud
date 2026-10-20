// RGON Omni-Link background v6.0.3
importScripts("core.js");

function boot() {
  chrome.alarms.create("omni_keepalive", { periodInMinutes: 0.5 });
  syncRolesToBridge();
}
chrome.runtime.onInstalled.addListener(boot);
chrome.runtime.onStartup.addListener(boot);
chrome.alarms.onAlarm.addListener(a => { if (a.name === "omni_keepalive") pollBridge(); });

let polling = false;
async function pollBridge() {
  if (polling) return;
  polling = true;
  try {
    const r = await fetch(BRIDGE + "/poll", { cache: "no-store" });
    if (r.ok) {
      const data = await r.json();
      for (const job of (data.jobs || [])) await handleJob(job);
    }
  } catch (e) {} finally { polling = false; }
}

async function handleJob(job) {
  let result = {};
  try {
    if (job.type === "dispatch") result = await omniDispatch(job.text || "", job.targets || ["claude", "gpt"]);
    else if (job.type === "absorb") result = (await omniAbsorb(job.targets || "__all__")).results;
    else if (job.type === "roles") { await syncRolesToBridge(); result = { ok: true }; }
  } catch (e) { result = { ok: false, err: String(e.message || e) }; }
  try {
    await fetch(BRIDGE + "/result", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: job.id, type: job.type, result }) });
  } catch (e) {}
}
setInterval(pollBridge, 1500);

chrome.runtime.onMessage.addListener((msg, sender, send) => {
  (async () => {
    try {
      switch (msg.cmd) {
        case "dispatch": send({ ok: true, results: await omniDispatch(msg.text, msg.targets) }); break;
        case "absorb":   { const r = await omniAbsorb(msg.targets); send({ ok: true, results: r.results }); break; }
        case "roles":    send({ ok: true, roles: await getRoleStatus() }); break;
        case "sync":     await syncRolesToBridge(); send({ ok: true }); break;
        default: send({ ok: false, err: "unknown cmd" });
      }
    } catch (e) { send({ ok: false, err: String(e.message || e) }); }
  })();
  return true;
});
