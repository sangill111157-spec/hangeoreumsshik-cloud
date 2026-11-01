
const sleep = ms => new Promise(r => setTimeout(r, ms));
const spaces = await listTaskSpaces();
const s0 = spaces.find(s => s.id === 0) || spaces[0];
const task = s0.ownership === "user" ? await claimTaskSpace(s0.id) : await taskSpace(s0.id);
const tabs = await task.tabs();
const target = tabs.find(tb => String(tb.url).includes("genspark.ai")) || tabs[0];
if (target) {
  const page = target.label ? task.page(target.label) : await task.adopt(target.page);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await sleep(500);
  await page.fill("loc=css:textarea[name=\"query\"]", "[에고 배달비서관 클로드 레버리지 완공 보고] 대표님 어명대로 ① 2_클로드(Claude)에 코드 설계를 먼저 레버리지하여 수거하고, ② 대시보드(rgon_alpha_chat.html) 단독 스크롤(740px) 및 12개 버튼 실클릭 완료, ③ 만능 소통창(index.html) 단독 8개 버튼 실클릭 완료, ④ 커밋(6a1bf5f)까지 모두 완료하여 보고합니다.");
  await sleep(400);
  await page.keyboard.press("Enter");
}
