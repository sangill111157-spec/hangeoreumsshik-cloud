let task;
try {
  task = await takeOverTaskSpace(18);
} catch (e) {
  task = await claimTaskSpace(18);
}

try {
  console.log("Checking if DistroKid can be opened in Space 18...");
  const page = await task.newPage();
  await page.goto("https://distrokid.com/mymusic/", { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(4000);
  const url = await page.url();
  const title = await page.title();
  console.log("DistroKid Page URL:", url);
  console.log("DistroKid Page Title:", title);

  // Take screenshot of DistroKid
  await page.screenshot({ path: "C:/Users/sangi/Downloads/shin-agent/distrokid_mymusic_check.png" });

  const data = await page.evaluate(() => {
    return {
      bodySnippet: document.body.innerText.slice(0, 500).replace(/\n/g, ' '),
      links: Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText.trim(), href: a.href })).filter(a => a.href.includes('album') || a.href.includes('mymusic') || a.text)
    };
  });
  console.log("DistroKid Data:", JSON.stringify(data, null, 2));

  // Close the new tab so we don't leave clutter
  await page.close();

} catch (e) {
  console.error("DistroKid check error:", e);
} finally {
  await task.handOff();
}
