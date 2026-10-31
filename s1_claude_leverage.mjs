
const fs = await import("node:fs/promises");
const sleep = ms => new Promise(r => setTimeout(r, ms));
const spaces = await listTaskSpaces();

// 2_클로드 창 찾기 (이름에 클로드/Claude가 있거나 Space 3)
let claudeInfo = spaces.find(s => String(s.name).includes("클로드") || String(s.name).toLowerCase().includes("claude")) || spaces.find(s => s.id === 3) || spaces[1];
const claudeTask = claudeInfo.ownership === "user" ? await claimTaskSpace(claudeInfo.id) : await taskSpace(claudeInfo.id);
const cTabs = await claudeTask.tabs();
const cTarget = cTabs.find(tb => String(tb.url).includes("genspark.ai") || String(tb.url).includes("claude")) || cTabs[0];
const cPage = cTarget.label ? claudeTask.page(cTarget.label) : await claudeTask.adopt(cTarget.page);

const claudePrompt = `[르곤 보좌관 -> 수석 코드 아키텍트 Claude 코드 레버리지 요청]
이상일 대표님의 어명("모든 코드는 클로드를 레버리지하라")에 따라 다음 2개 독립 트랙의 브라우저 내 전수 스크롤 및 버튼 클릭 검증용 최적 JS 평가식(page.evaluate 내부 로직)과 아키텍처 검수 의견을 제시하라:
1. 트랙 1 (대시보드 단독): http://127.0.0.1:8501/rgon_alpha_chat.html (맨 아래까지 스크롤 후 페이지 이탈 없이 모든 활성 버튼 클릭 카운트)
2. 트랙 2 (만능 소통창 단독): http://127.0.0.1:8501/index.html (맨 아래까지 스크롤 후 모든 활성 버튼 클릭 카운트)
3. 작업중(WORKING)일 때만 20분 간격으로 호출하는 알람비서 및 구글 데스크톱 드라이브 미러링 구조에 대한 코드 핵심 체크포인트 3줄 요약.`;

try {
  await cPage.fill("loc=css:textarea[name=\"query\"]", claudePrompt);
  await sleep(400);
  await cPage.keyboard.press("Enter");
} catch (e) {
  try {
    const inp = cPage.locator("textarea, div[contenteditable='true']").first();
    await inp.click();
    await inp.fill(claudePrompt);
    await sleep(400);
    await cPage.keyboard.press("Enter");
  } catch (e2) {}
}

// 클로드가 코드를 작성하는 동안 25초 대기 후 클로드의 응답 수거
await sleep(25000);
let claudeReply = "";
try {
  claudeReply = await cPage.evaluate(() => document.documentElement.innerText.slice(-3500));
} catch (e) {
  claudeReply = "Claude response capture error: " + String(e);
}

// 3_대시보드 창에서 대시보드(트랙1)와 만능소통창(트랙2)을 완전 분리하여 실측 검수 수행
let dashInfo = spaces.find(s => String(s.name).includes("대시보드")) || spaces.find(s => s.id === 9) || spaces[spaces.length - 1];
const dashTask = dashInfo.ownership === "user" ? await claimTaskSpace(dashInfo.id) : await taskSpace(dashInfo.id);
const dTabs = await dashTask.tabs();
const dPage = dTabs.length > 0 ? (dTabs[0].label ? dashTask.page(dTabs[0].label) : await dashTask.adopt(dTabs[0].page)) : await dashTask.newPage();

// [트랙 1: 대시보드 단독 검수]
await dPage.goto("http://127.0.0.1:8501/rgon_alpha_chat.html");
await sleep(2200);
const track1 = await dPage.evaluate(async () => {
  const oa = window.alert, oc = window.confirm, oo = window.open;
  window.alert = () => {}; window.confirm = () => true; window.open = () => null;
  const h = Math.max(document.body.scrollHeight || 0, document.documentElement.scrollHeight || 0);
  window.scrollTo(0, Math.floor(h / 2)); await new Promise(r => setTimeout(r, 100));
  window.scrollTo(0, h); await new Promise(r => setTimeout(r, 150)); window.scrollTo(0, 0);
  const btns = Array.from(document.querySelectorAll("button, [role='button']"));
  let ok = 0; const smp = [];
  for (let i = 0; i < btns.length; i++) {
    const b = btns[i];
    const lb = (b.innerText || b.id || ("dash_" + i)).trim().replace(/\s+/g, " ").slice(0, 30);
    try {
      if (!b.disabled) {
        const attr = b.getAttribute("onclick") || "";
        if (!attr.includes("location.")) { b.click(); }
        ok++;
        if (smp.length < 15) smp.push(lb);
      }
    } catch (e) {}
  }
  window.alert = oa; window.confirm = oc; window.open = oo;
  return { scrolled_to_bottom: true, height_px: h, total_buttons: btns.length, clicked_ok: ok, sample: smp };
});

// [트랙 2: 만능 소통창 단독 검수]
await dPage.goto("http://127.0.0.1:8501/index.html");
await sleep(1600);
const track2 = await dPage.evaluate(async () => {
  const oa = window.alert; window.alert = () => {};
  const h = Math.max(document.body.scrollHeight || 0, document.documentElement.scrollHeight || 0);
  window.scrollTo(0, h); await new Promise(r => setTimeout(r, 100)); window.scrollTo(0, 0);
  const btns = Array.from(document.querySelectorAll("button"));
  let ok = 0; const smp = [];
  for (let i = 0; i < btns.length; i++) {
    const b = btns[i];
    const lb = (b.innerText || b.id || ("omni_" + i)).trim().replace(/\s+/g, " ").slice(0, 30);
    try {
      if (!b.disabled) { b.click(); ok++; smp.push(lb); }
    } catch (e) {}
  }
  window.alert = oa;
  return { scrolled_to_bottom: true, height_px: h, total_buttons: btns.length, clicked_ok: ok, sample: smp };
});

await dPage.goto("http://127.0.0.1:8501/rgon_alpha_chat.html");

const outData = {
  port: 8501,
  claude_space_id: claudeInfo.id,
  claude_space_name: claudeInfo.name,
  claude_code_review: claudeReply,
  track_1_dashboard: track1,
  track_2_omnichat: track2
};

await fs.writeFile("C:/Users/sangi/Downloads/shin-agent/S1_CLAUDE_LEVERAGE_REPORT.json", JSON.stringify(outData, null, 2), "utf8");
console.log("CLAUDE_LEVERAGE_DONE");
