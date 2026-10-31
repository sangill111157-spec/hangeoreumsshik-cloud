
try {
  const t0 = await taskSpace(0);
  for (const x of await t0.tabs()) {
    if (String(x.url).includes('genspark')) {
      const p0 = x.label ? t0.page(x.label) : await t0.adopt(x.page);
      await p0.bringToFront();
      const s0 = await p0.snapshot();
      const m0 = s0.match(/textbox\s+\[ref=(\d+)/);
      if (m0) {
        await p0.fill(m0[1], '[S1 전담비서 자동보고] 시공·실측·삼성 최종 감리 및 GitHub 커밋(08894b4)까지 모두 완료했습니다. 르곤 보좌관님, 검수 후 대표님께 최종 보고하십시오.');
        await p0.keyboard.press('Enter');
      }
      break;
    }
  }
} catch(e) {}
