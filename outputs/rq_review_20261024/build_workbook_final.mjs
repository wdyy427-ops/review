import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const base=new URL('.',import.meta.url).pathname.replace(/^\/(?=[A-Za-z]:)/,'');
const sheets=JSON.parse(await fs.readFile(`${base}/workbook_data_final.json`,'utf8'));
const wb=Workbook.create();
const longPattern=/题名|概要|事实|理由|原文|引文|程序|分析|结果|限制|说明|内容|工具实例|效果主张|构念|题项|招募|任务|情境|证据/;
for(const [name,rows] of Object.entries(sheets)){
  const sh=wb.worksheets.add(name);sh.showGridLines=false;
  const nrow=rows.length,ncol=rows[0].length;
  const range=sh.getRangeByIndexes(0,0,nrow,ncol);
  range.values=rows.map(r=>r.map(v=>v===undefined?null:v));
  range.format.font={name:'Microsoft YaHei',size:9,color:'#20313E'};
  range.format.verticalAlignment='top';
  range.format.wrapText=true;
  sh.getRangeByIndexes(0,0,1,ncol).format={fill:'#16324F',font:{name:'Microsoft YaHei',size:10,bold:true,color:'#FFFFFF'},rowHeight:34,verticalAlignment:'center',wrapText:true};
  sh.freezePanes.freezeRows(1);
  sh.getRangeByIndexes(0,0,nrow,1).format.columnWidth=12;
  for(let j=0;j<ncol;j++){
    const h=String(rows[0][j]??'');
    let w=18;
    if(longPattern.test(h))w=42;
    else if(/DOI|代码|工具|评价|领域|阶段|目的|主体|对象|来源/.test(h))w=24;
    else if(/占比|percent|概率|lift|value|score|eligible|n$/.test(h))w=14;
    sh.getRangeByIndexes(0,j,nrow,1).format.columnWidth=w;
  }
  if(nrow>1)sh.getRangeByIndexes(1,0,nrow-1,ncol).format.rowHeight=31;
  const bandCount=Math.ceil((nrow-1)/2);
  for(let r=2;r<nrow;r+=2)sh.getRangeByIndexes(r,0,1,ncol).format.fill='#F4F7F8';
  sh.tabColor=name.startsWith('RQ1')?'#2B6F92':name.startsWith('RQ2')||name==='JCSEE审查'?'#C1666B':name.startsWith('RQ3')||name==='模型比较'?'#E0A458':name==='推荐证据'?'#4D9D8C':'#6E7D8B';
  if(name==='研究概览'){
    sh.getRange('A:A').format.columnWidth=28;sh.getRange('B:B').format.columnWidth=18;sh.getRange('C:C').format.columnWidth=76;
    sh.getRangeByIndexes(1,1,nrow-1,1).format.font={name:'Microsoft YaHei',size:13,bold:true,color:'#16324F'};
    sh.getRangeByIndexes(1,0,nrow-1,ncol).format.rowHeight=38;
  }
  if(name==='JCSEE审查'){
    const statusCol=rows[0].indexOf('status');
    if(statusCol>=0){
      for(let r=1;r<nrow;r++){
        const v=String(rows[r][statusCol]??'');
        const color={S:'#DCEFE9',P:'#FFF0D6',C:'#F7D9DC',NR:'#EDF0F2',NA:'#F5F5F5'}[v];
        if(color)sh.getRangeByIndexes(r,statusCol,1,1).format.fill=color;
      }
    }
  }
  console.log(`${name}: ${nrow-1} rows`);
}
wb.recalculate();
await fs.mkdir(`${base}/previews`,{recursive:true});
const preview=await wb.render({sheetName:'研究概览',range:'A1:C11',scale:1.35,format:'png'});
await fs.writeFile(`${base}/previews/final_workbook_overview.png`,new Uint8Array(await preview.arrayBuffer()));
const out=await SpreadsheetFile.exportXlsx(wb);
await out.save(`${base}/AI辅助设计感知效应_最终编码与分析.xlsx`);
console.log('exported final workbook');
