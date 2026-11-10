const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const target = 'file:///' + path.resolve(__dirname, 'dist', 'index.html').replace(/\\/g, '/');
  await page.goto(target, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.resolve(__dirname, 'recommender_english.png'), fullPage: true });
  await page.selectOption('[data-answer="objects_g4"]', { index: 1 });
  await page.selectOption('[data-answer="purposes"]', { index: 1 });
  await page.click('#recommend');
  const dimensionCandidates = await page.locator('[data-pick="dimension"]').count();
  if (!dimensionCandidates) throw new Error('No dimension recommendations were generated.');
  await page.locator('[data-pick="dimension"]').first().click();
  const indicatorFactors = await page.locator('.input-head h3').allTextContents();
  await page.selectOption('[data-answer="domains"]', { index: 1 });
  await page.selectOption('[data-answer="target_users_g6"]', { index: 1 });
  await page.click('#recommend');
  const indicatorCandidates = await page.locator('[data-pick="indicator"]').count();
  if (!indicatorCandidates) throw new Error('No indicator recommendations were generated.');
  await page.locator('[data-pick="indicator"]').first().click();
  const toolFactors = await page.locator('.input-head h3').allTextContents();
  await page.click('#recommend');
  const toolCandidates = await page.locator('[data-pick="tool"]').count();
  if (!toolCandidates) throw new Error('No tool recommendations were generated.');
  const firstEvidence = page.locator('.card details').first();
  if (await firstEvidence.count()) await firstEvidence.locator('summary').click();
  const visibleHanText = (await page.locator('body').innerText()).match(/[\u4e00-\u9fff]+/g) || [];
  await page.screenshot({ path: path.resolve(__dirname, 'recommender_english_stage3.png'), fullPage: true });
  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await mobile.goto(target, { waitUntil: 'networkidle' });
  await mobile.screenshot({ path: path.resolve(__dirname, 'recommender_english_mobile.png'), fullPage: true });
  console.log(JSON.stringify({ dimensionCandidates, indicatorFactors, indicatorCandidates, toolFactors, toolCandidates, visibleHanText }, null, 2));
  await browser.close();
})();
