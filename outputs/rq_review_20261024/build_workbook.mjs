import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const base=new URL('.',import.meta.url).pathname.replace(/^\/(?=[A-Za-z]:)/,'');
const book=JSON.parse(await fs.readFile(`${base}/workbook_data.json`,'utf8'));
const wb=Workbook.create();
for(const [name,rows] of Object.entries(book)){
  const sh=wb.worksheets.add(name);sh.showGridLines=false;
  const ncol=rows[0].length,nrow=rows.length;
  sh.getRangeByIndexes(0,0,nrow,ncol).values=rows.map(row=>row.map(x=>x===undefined?null:x));
  sh.getRangeByIndexes(0,0,nrow,ncol).format.font={name:'Microsoft YaHei',size:10,color:'#18352D'};
  sh.getRangeByIndexes(0,0,1,ncol).format={fill:'#17493A',font:{name:'Microsoft YaHei',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,verticalAlignment:'center',wrapText:true};
  sh.getRangeByIndexes(0,0,nrow,ncol).format.columnWidth=20;
  if(nrow>1)sh.getRangeByIndexes(1,0,nrow-1,ncol).format.rowHeight=25;
  sh.getRangeByIndexes(0,0,nrow,1).format.columnWidth=10;
  if(name==='概览'){
    sh.getRange('A:A').format.columnWidth=25;sh.getRange('B:B').format.columnWidth=26;sh.getRange('C:C').format.columnWidth=90;
    sh.getRangeByIndexes(1,0,nrow-1,ncol).format.rowHeight=34;
  }else{
    for(let j=0;j<ncol;j++){
      const h=String(rows[0][j]);
      if(/题名|概要|事实|理由|原文|程序|分析|结果|边界|说明|内容/.test(h))sh.getRangeByIndexes(0,j,nrow,1).format.columnWidth=42;
      else if(/DOI|状态|代码|工具|评价/.test(h))sh.getRangeByIndexes(0,j,nrow,1).format.columnWidth=24;
    }
  }
  sh.freezePanes.freezeRows(1);
  sh.tabColor=name.startsWith('旧表')?'#B99B4C':name.startsWith('复核')||name==='JCSEE审查'?'#347C62':'#40667C';
  if(name==='概览')for(const i of [3,4,9,10])sh.getRangeByIndexes(i,0,1,ncol).format.fill='#FFF3D8';
  console.log(`${name}: ${nrow-1} rows`);
}
wb.recalculate();
const preview=await wb.render({sheetName:'概览',range:'A1:C11',scale:1.4,format:'png'});
await fs.writeFile(`${base}/previews/workbook_overview.png`,new Uint8Array(await preview.arrayBuffer()));
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(`${base}/AI辅助设计感知效应_综述编码与分析_阶段成果.xlsx`);
console.log('exported');
