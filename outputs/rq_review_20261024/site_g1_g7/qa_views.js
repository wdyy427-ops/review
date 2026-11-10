const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const root = 'http://127.0.0.1:5173/';

  await page.goto(root + '#corpus', { waitUntil: 'networkidle' });
  const initialRows = await page.locator('#corpusRows tr').count();
  const initialCount = await page.locator('#corpusCount').innerText();
  await page.selectOption('#filterDomain', 'D1');
  const filteredCount = await page.locator('#corpusCount').innerText();
  await page.screenshot({ path: path.resolve(__dirname, 'corpus_english.png'), fullPage: true });

  await page.goto(root + '#method', { waitUntil: 'networkidle' });
  const methodRows = await page.locator('#methodRelationships tr').count();
  const methodText = await page.locator('#page-method').innerText();
  await page.screenshot({ path: path.resolve(__dirname, 'method_english.png'), fullPage: true });

  await page.goto(root + '#recommender', { waitUntil: 'networkidle' });
  await page.selectOption('[data-answer="objects_g4"]', { index: 1 });
  await page.selectOption('[data-answer="purposes"]', { index: 1 });
  await page.click('#recommend');
  const recommenderCandidates = await page.locator('[data-pick="dimension"]').count();

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mobile.goto(root + '#corpus', { waitUntil: 'networkidle' });
  const mobileNavLinks = await mobile.locator('[data-view]').count();
  await mobile.screenshot({ path: path.resolve(__dirname, 'corpus_english_mobile.png'), fullPage: true });

  console.log(JSON.stringify({
    initialRows,
    initialCount,
    filteredCount,
    methodRows,
    recommenderCandidates,
    visibleHanInMethod: /[\u4e00-\u9fff]/.test(methodText),
    mobileNavLinks
  }, null, 2));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
