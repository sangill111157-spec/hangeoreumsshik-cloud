import fs from 'node:fs';

const task = await takeOverTaskSpace(17);
console.log("Took over task space 17");

const sunoPage = task.userPage();
console.log("User page URL:", sunoPage.url());

// Evaluate DOM elements related to download or audio
const info = await sunoPage.evaluate(() => {
  const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
    text: b.innerText ? b.innerText.trim() : '',
    ariaLabel: b.getAttribute('aria-label') || '',
    title: b.getAttribute('title') || '',
    className: b.className
  })).filter(b => b.text || b.ariaLabel || b.title);
  
  const audios = Array.from(document.querySelectorAll('audio')).map(a => ({
    src: a.src,
    currentSrc: a.currentSrc
  }));

  return {
    title: document.title,
    audios,
    buttonsCount: buttons.length,
    downloadButtons: buttons.filter(b => 
      b.text.toLowerCase().includes('download') || 
      b.ariaLabel.toLowerCase().includes('download') ||
      b.title.toLowerCase().includes('download') ||
      b.text.includes('다운로드')
    ),
    moreButtons: buttons.filter(b => 
      b.ariaLabel.toLowerCase().includes('more') || 
      b.title.toLowerCase().includes('more') ||
      b.text === '...' ||
      b.ariaLabel.includes('옵션') ||
      b.ariaLabel.includes('작업')
    )
  };
});

console.log("Page Info:", JSON.stringify(info, null, 2));

// Keep Space 17 open and hand off safely
await task.handOff();
