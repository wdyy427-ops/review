import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const base = new URL('.', import.meta.url).pathname.replace(/^\/(?=[A-Za-z]:)/, '');
const sheets = JSON.parse(await fs.readFile(`${base}/workbook_data_revised.json`, 'utf8'));
const wb = Workbook.create();
const longPattern = /题名|摘要|概要|事实|理由|原文|引文|程序|分析|结果|限制|说明|内容|效果主张|构念|题项|招募|任务|情境|证据|instrument|quote|rationale|description/i;

for (const [name, rows] of Object.entries(sheets)) {
  const sh = wb.worksheets.add(name);
  sh.showGridLines = false;
  const nrow = rows.length, ncol = rows[0].length;
  const range = sh.getRangeByIndexes(0, 0, nrow, ncol);
  range.values = rows.map(r => r.map(v => v === undefined ? null : v));
  range.format.font = {name: 'Microsoft YaHei', size: 9, color: '#20313E'};
  range.format.verticalAlignment = 'top';
  range.format.wrapText = true;
  sh.getRangeByIndexes(0, 0, 1, ncol).format = {
    fill: '#17364D', font: {name: 'Microsoft YaHei', size: 10, bold: true, color: '#FFFFFF'},
    rowHeight: 36, verticalAlignment: 'center', horizontalAlignment: 'center', wrapText: true,
    borders: {bottom: {style: 'medium', color: '#17364D'}}
  };
  sh.freezePanes.freezeRows(1);
  if (['03_评价证据链','04_测量工具实例','05_JCSEE链级审查','09_RQ3分析集'].includes(name)) sh.freezePanes.freezeColumns(3);
  for (let j = 0; j < ncol; j++) {
    const h = String(rows[0][j] ?? '');
    let w = 17;
    if (longPattern.test(h)) w = 42;
    else if (/title|论文题目|标准|label|名称|工具|评价|领域|阶段|目的|主体|对象|来源|feature_group/i.test(h)) w = 25;
    else if (/percent|probability|weight|macro|accuracy|lift|odds|score|index|value|p_value|q_value/i.test(h)) w = 15;
    else if (/^n$|year|年份|代码|code|id$/i.test(h)) w = 13;
    sh.getRangeByIndexes(0, j, nrow, 1).format.columnWidth = w;
    if (nrow > 1 && /percent|probability|normalized_weight/i.test(h)) sh.getRangeByIndexes(1, j, nrow - 1, 1).format.numberFormat = '0.0%';
    else if (nrow > 1 && /p_value|q_value|cramers|macro_f1|accuracy|delta|ci_|lift|odds|score|index/i.test(h)) sh.getRangeByIndexes(1, j, nrow - 1, 1).format.numberFormat = '0.000';
  }
  if (nrow > 1) sh.getRangeByIndexes(1, 0, nrow - 1, ncol).format.rowHeight = 30;
  for (let r = 2; r < nrow; r += 2) sh.getRangeByIndexes(r, 0, 1, ncol).format.fill = '#F4F7F8';
  sh.tabColor = name.startsWith('06_') || name.startsWith('07_') ? '#2B6F92'
    : name.startsWith('08_') || name.startsWith('05_') ? '#B75D69'
    : name.startsWith('09_') || name.startsWith('10_') || name.startsWith('11_') ? '#D8A247'
    : name === '00_研究概览' ? '#17364D' : name === '12_代码本' || name === '13_方法与限制' ? '#6E7D8B' : '#4D9D8C';

  if (name === '00_研究概览') {
    sh.getRange('A:A').format.columnWidth = 29;
    sh.getRange('B:B').format.columnWidth = 18;
    sh.getRange('C:C').format.columnWidth = 78;
    sh.getRangeByIndexes(1, 1, nrow - 1, 1).format.font = {name:'Microsoft YaHei', size:13, bold:true, color:'#17364D'};
    sh.getRangeByIndexes(1, 0, nrow - 1, ncol).format.rowHeight = 39;
  }
  if (name === '05_JCSEE链级审查') {
    const statusCol = rows[0].indexOf('status');
    if (statusCol >= 0) {
      for (let r = 1; r < nrow; r++) {
        const v = String(rows[r][statusCol] ?? '');
        const fill = {S:'#DCEFE9', P:'#FFF0D6', C:'#F7D9DC', NR:'#EDF0F2', NA:'#F5F5F5'}[v];
        if (fill) sh.getRangeByIndexes(r, statusCol, 1, 1).format.fill = fill;
      }
    }
  }
}

wb.recalculate();
await fs.mkdir(`${base}/previews`, {recursive:true});
const preview = await wb.render({sheetName:'00_研究概览', range:'A1:C14', scale:1.4, format:'png'});
await fs.writeFile(`${base}/previews/revised_workbook_overview.png`, new Uint8Array(await preview.arrayBuffer()));
const auditPreview = await wb.render({sheetName:'08_RQ2质量结果', range:'A1:J30', scale:1.1, format:'png'});
await fs.writeFile(`${base}/previews/revised_workbook_rq2.png`, new Uint8Array(await auditPreview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(`${base}/AI辅助设计感知效应_RQ修订后最终编码与分析.xlsx`);

const inspect = await wb.inspect({kind:'table', range:'00_研究概览!A1:C14', include:'values,formulas', tableMaxRows:14, tableMaxCols:3, maxChars:7000});
console.log(inspect.ndjson);
const errors = await wb.inspect({kind:'match', searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options:{useRegex:true,maxResults:100}, summary:'final formula error scan'});
console.log(errors.ndjson);
console.log('exported revised workbook');
