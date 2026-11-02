let task;
try {
  task = await takeOverTaskSpace(18);
} catch (e) {
  task = await claimTaskSpace(18);
}

try {
  const tabs = await task.tabs();
  let page;
  try {
    page = task.page("p1");
  } catch (e) {
    page = await task.adopt(tabs[0].page, { as: "p1" });
  }

  const info = await page.evaluate(() => {
    // 1. All file inputs
    const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map((fi, idx) => ({
      index: idx,
      id: fi.id,
      name: fi.name,
      accept: fi.accept,
      parentTag: fi.parentElement ? fi.parentElement.tagName : '',
      parentClass: fi.parentElement ? fi.parentElement.className : '',
      sectionText: (fi.closest('section, ytcp-entity-page-section, div[class*="section"], div[class*="row"]') || fi.parentElement)?.innerText?.slice(0, 100)?.replace(/\n/g, ' ') || ''
    }));

    // 2. All upload/change/publish buttons
    const allBtns = Array.from(document.querySelectorAll('button, tp-yt-paper-button, ytcp-button, [role="button"]'));
    const btns = allBtns.map((b, idx) => ({
      index: idx,
      id: b.id,
      tag: b.tagName,
      text: (b.innerText || b.getAttribute('aria-label') || '').trim().replace(/\n/g, ' '),
      disabled: b.disabled || b.hasAttribute('disabled'),
      parentText: (b.closest('section, ytcp-entity-page-section, div[class*="section"]') || b.parentElement)?.innerText?.slice(0, 80)?.replace(/\n/g, ' ') || ''
    })).filter(b => b.text && /업로드|변경|삭제|게시|취소|Upload|Change|Remove|Publish|Cancel/i.test(b.text));

    // 3. Description textbox
    const tb = document.querySelector('div#textbox');
    const descText = tb ? tb.innerText : 'NOT FOUND';

    return {
      url: location.href,
      fileInputs,
      btns,
      descLength: descText.length,
      descSnippet: descText.slice(0, 150)
    };
  });

  const fs = await import("fs");
  fs.writeFileSync("C:/Users/sangi/Downloads/shin-agent/studio_dom_snapshot.json", JSON.stringify(info, null, 2), "utf-8");
  process.stdout.write("SAVED_SNAPSHOT_OK\n");
} catch (e) {
  process.stdout.write("ERROR::" + e.message + "\n");
} finally {
  await task.handOff();
}
