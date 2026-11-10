const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  await page.goto('https://idvxlab.com/ai4design/', { waitUntil: 'networkidle', timeout: 90000 });
  await page.screenshot({ path: path.resolve(__dirname, 'ai4design_reference.png'), fullPage: true });
  const details = await page.evaluate(() => ({
    title: document.title,
    bodyText: document.body.innerText.slice(0, 6000),
    colors: [...new Set([...document.querySelectorAll('*')].slice(0, 500).map(el => getComputedStyle(el).color))].slice(0, 30),
    backgrounds: [...new Set([...document.querySelectorAll('*')].slice(0, 500).map(el => getComputedStyle(el).backgroundColor))].slice(0, 30),
    fonts: [...new Set([...document.querySelectorAll('*')].slice(0, 500).map(el => getComputedStyle(el).fontFamily))].slice(0, 20)
  }));
  console.log(JSON.stringify(details, null, 2));
  await browser.close();
})();
