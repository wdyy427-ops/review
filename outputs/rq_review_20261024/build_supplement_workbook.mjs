import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const base = new URL('.', import.meta.url).pathname.replace(/^\/(?=[A-Za-z]:)/, '');
const sheets = JSON.parse(await fs.readFile(`${base}/supplement_workbook_data.json`, 'utf8'));
const wb = Workbook.create();
const longPattern = /说明|原因|内容|依据|规则|判定|distribution|observable|basis|结论|来源/i;

for (const [name, rows] of Object.entries(sheets)) {
  const sh = wb.worksheets.add(name);
  sh.showGridLines = false;
  const nrow = rows.length;
  const ncol = rows[0].length;
  const rg = sh.getRangeByIndexes(0, 0, nrow, ncol);
  rg.values = rows.map(row => row.map(v => v === undefined ? null : v));
  rg.format.font = {name:'Microsoft YaHei', size:9, color:'#263642'};
  rg.format.verticalAlignment = 'top';
  rg.format.wrapText = true;
  sh.getRangeByIndexes(0, 0, 1, ncol).format = {
    fill:'#17364D',
    font:{name:'Microsoft YaHei', size:10, bold:true, color:'#FFFFFF'},
    horizontalAlignment:'center', verticalAlignment:'center', wrapText:true,
    rowHeight:36,
    borders:{bottom:{style:'medium', color:'#17364D'}}
  };
  sh.freezePanes.freezeRows(1);
  if (['03_指标×领域','04_指标×阶段','10_规则代码本','11_规则分布'].includes(name)) sh.freezePanes.freezeColumns(3);
  if (nrow > 1) sh.getRangeByIndexes(1, 0, nrow - 1, ncol).format.rowHeight = 30;
  for (let r = 2; r < nrow; r += 2) sh.getRangeByIndexes(r, 0, 1, ncol).format.fill = '#F4F7F8';

  for (let c = 0; c < ncol; c++) {
    const h = String(rows[0][c] ?? '');
    let width = 16;
    if (longPattern.test(h)) width = 43;
    else if (/label|名称|标准|规则|工具|指标|领域|阶段|transition|validation|model|outcome/i.test(h)) width = 25;
    else if (/code|status|^n$|total|chains|papers|classes|folds|df/i.test(h)) width = 13;
    sh.getRangeByIndexes(0, c, nrow, 1).format.columnWidth = width;
    if (nrow > 1 && /percent_exact|context_percent|percent_all|percent_applicable|inflation/i.test(h)) {
      sh.getRangeByIndexes(1, c, nrow - 1, 1).format.numberFormat = '0.0%';
    } else if (nrow > 1 && /p_value|cramers|macro_f1|accuracy|chi_square|minimum_expected/i.test(h)) {
      sh.getRangeByIndexes(1, c, nrow - 1, 1).format.numberFormat = '0.000';
    }
  }

  sh.tabColor = name === '00_答复概览' ? '#17364D'
    : /^0[1-7]_/.test(name) ? '#2B7A78'
    : /^0[89]_/.test(name) || /^1[01]_/.test(name) ? '#B75D69'
    : /^1[23]_/.test(name) ? '#D8A247' : '#6E7D8B';

  if (name === '00_答复概览') {
    sh.getRange('A:A').format.columnWidth = 20;
    sh.getRange('B:B').format.columnWidth = 78;
    sh.getRange('C:C').format.columnWidth = 31;
    sh.getRangeByIndexes(1, 0, nrow - 1, 1).format.font = {name:'Microsoft YaHei', size:10, bold:true, color:'#17364D'};
    sh.getRangeByIndexes(1, 0, nrow - 1, ncol).format.rowHeight = 42;
  }

  if (name === '13_规范集指标支持') {
    const c = rows[0].indexOf('passes_min_support');
    if (c >= 0) {
      for (let r = 1; r < nrow; r++) {
        const yes = String(rows[r][c]).toLowerCase() === 'true';
        sh.getRangeByIndexes(r, c, 1, 1).format.fill = yes ? '#DCEFE9' : '#EDF0F2';
      }
    }
  }
}

wb.recalculate();
await fs.mkdir(`${base}/previews`, {recursive:true});
const p1 = await wb.render({sheetName:'00_答复概览', range:'A1:C8', scale:1.4, format:'png'});
await fs.writeFile(`${base}/previews/supplement_overview.png`, new Uint8Array(await p1.arrayBuffer()));
const p2 = await wb.render({sheetName:'11_规则分布', range:'A1:J30', scale:1.05, format:'png'});
await fs.writeFile(`${base}/previews/supplement_rules.png`, new Uint8Array(await p2.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(`${base}/AI辅助设计感知效应_问题答复与补充分析.xlsx`);

const inspect = await wb.inspect({kind:'table', range:'00_答复概览!A1:C8', include:'values,formulas', tableMaxRows:8, tableMaxCols:3, maxChars:6000});
console.log(inspect.ndjson);
const errors = await wb.inspect({kind:'match', searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options:{useRegex:true,maxResults:100}, summary:'supplement formula error scan'});
console.log(errors.ndjson);
console.log('exported supplement workbook');
