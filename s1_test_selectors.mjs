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

  const res = await page.evaluate(() => {
    const selBanner = 'ytcp-banner-upload-instructions input[type="file"], .ytcpBannerUploadInstructions input[type="file"], #banner-section input[type="file"]';
    const selAvatar = 'ytcp-profile-image-upload input[type="file"], #profile-image-section input[type="file"]';
    const selWatermark = 'ytcp-video-watermark-upload input[type="file"], #watermark-section input[type="file"]';

    const bEl = document.querySelector(selBanner) || document.querySelectorAll('input[type="file"]')[0];
    const aEl = document.querySelector(selAvatar) || document.querySelectorAll('input[type="file"]')[1];
    const wEl = document.querySelector(selWatermark) || document.querySelectorAll('input[type="file"]')[2];

    return {
      bannerSelector: !!document.querySelector(selBanner),
      avatarSelector: !!document.querySelector(selAvatar),
      watermarkSelector: !!document.querySelector(selWatermark),
      bTag: bEl ? bEl.parentElement.tagName + '.' + bEl.parentElement.className : 'null',
      aTag: aEl ? aEl.parentElement.tagName + '.' + aEl.parentElement.className : 'null',
      wTag: wEl ? wEl.parentElement.tagName + '.' + wEl.parentElement.className : 'null'
    };
  });

  process.stdout.write("SELECTORS_MATCH::" + JSON.stringify(res) + "\n");
} finally {
  await task.handOff();
}

