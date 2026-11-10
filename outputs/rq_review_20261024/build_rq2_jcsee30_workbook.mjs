import fs from "node:fs/promises";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = "C:/Users/Administrator/Desktop/review/outputs/rq_review_20261024/rq2_jcsee30";
const data = JSON.parse(await fs.readFile(`${root}/rq2_workbook_data.json`, "utf8"));
const wb = Workbook.create();

const navy = "#17365D", blue = "#2F75B5", pale = "#D9EAF7", light = "#F3F6F8", grid = "#D9E1E8", text = "#1F2933";
const statusFills = { S:"#E2F0D9", P:"#DDEBF7", NR:"#E7E6E6", C:"#F4CCCC", NA:"#FFF2CC", UJ:"#E4DFEC" };

function colName(n) {
  let s=""; n++;
  while(n){ const r=(n-1)%26; s=String.fromCharCode(65+r)+s; n=Math.floor((n-1)/26); }
  return s;
}
function styleTitle(sheet, title, subtitle="") {
  sheet.showGridLines = false;
  sheet.getRange("A2").values=[[title]];
  sheet.getRange("A2").format.font={name:"Arial",size:15,bold:true,color:navy};
  sheet.getRange("A3").values=[[subtitle]];
  sheet.getRange("A3").format.font={name:"Arial",size:10,italic:true,color:"#52606D"};
  sheet.getRange("A4:R4").format.borders={bottom:{style:"thin",color:blue}};
}
function styleHeader(rng) {
  rng.format.fill = navy;
  rng.format.font = {name:"Arial",size:10,bold:true,color:"#FFFFFF"};
  rng.format.horizontalAlignment="center";
  rng.format.verticalAlignment="center";
  rng.format.wrapText=true;
  rng.format.borders={insideVertical:{style:"thin",color:"#FFFFFF"},bottom:{style:"thin",color:navy}};
}
let tableSeq=1;
function addDataSheet(name, title, obj, opts={}) {
  const sh=wb.worksheets.add(name); styleTitle(sh,title,opts.subtitle||"");
  const matrix=[obj.columns,...obj.rows];
  const endCol=colName(obj.columns.length-1), endRow=5+obj.rows.length;
  sh.getRange(`A5:${endCol}${endRow}`).values=matrix;
  styleHeader(sh.getRange(`A5:${endCol}5`));
  sh.getRange(`A6:${endCol}${endRow}`).format.font={name:"Arial",size:9,color:text};
  sh.getRange(`A6:${endCol}${endRow}`).format.verticalAlignment="top";
  sh.getRange(`A6:${endCol}${endRow}`).format.borders={bottom:{style:"hair",color:grid}};
  if(opts.wrap!==false) sh.getRange(`A6:${endCol}${endRow}`).format.wrapText=true;
  sh.freezePanes.freezeRows(5);
  sh.freezePanes.freezeColumns(opts.freezeCols||1);
  const table=sh.tables.add(`A5:${endCol}${endRow}`,true,`DataTable${tableSeq++}`);
  table.style="TableStyleMedium2";
  table.showBandedRows=true;
  for(let i=0;i<obj.columns.length;i++) sh.getRange(`${colName(i)}:${colName(i)}`).format.columnWidth = (opts.widths&&opts.widths[i]) || 16;
  if(opts.statusStart!==undefined){
    for(let i=opts.statusStart;i<obj.columns.length;i++){
      const r=sh.getRange(`${colName(i)}6:${colName(i)}${endRow}`);
      for(const [s,c] of Object.entries(statusFills)) r.conditionalFormats.add("cellIs",{operator:"equal",formula:`\"${s}\"`,format:{fill:c,font:{bold:true,color:"#202020"}}});
      r.format.horizontalAlignment="center";
    }
  }
  return sh;
}

// Summary
const s=wb.worksheets.add("RQ2摘要"); styleTitle(s,"RQ2：JCSEE 30项全文规范性重审","完整评价实践链为审查单位；论文级、案例级和链级信息合并判断");
s.getRange("A6:F6").values=[["原始全文","候选记录","完整实践","评价案例","涉及论文","排除记录"]]; styleHeader(s.getRange("A6:F6"));
s.getRange("A7:F7").values=[[data.metrics.source_papers,data.metrics.candidate_records,data.metrics.audited_practices,data.metrics.audited_cases,data.metrics.audited_papers,data.metrics.excluded_records]];
s.getRange("A7:F7").format.font={name:"Arial",size:14,bold:true,color:navy}; s.getRange("A7:F7").format.horizontalAlignment="center"; s.getRange("A7:F7").setNumberFormat("#,##0");
s.getRange("A10:C10").values=[["计权口径","单位数","可判断标准平均支持指数"]]; styleHeader(s.getRange("A10:C10"));
s.getRange("A11:C13").values=data.cluster_summary; s.getRange("C11:C13").setNumberFormat("0.0%");
s.getRange("E10:H10").values=[["标准家族","实践加权","案例等权","论文等权"]]; styleHeader(s.getRange("E10:H10"));
s.getRange("E11:H15").values=data.family_summary.map(r=>[r.family,r["实践加权"],r["案例等权"],r["论文等权"]]); s.getRange("F11:H15").setNumberFormat("0.0%");
s.getRange("A17:J17").values=[["标准","英文名称","单位数","S","P","NR","C","NA","UJ","可观察支持指数"]]; styleHeader(s.getRange("A17:J17"));
const sp=data.standard_practice;
const spRows=sp.rows.map(r=>r.map((v,i)=> i>=2&&i<=8 ? Number(v||0) : v));
s.getRange(`A18:I${17+spRows.length}`).values=spRows.map(r=>r.slice(0,9));
for(let i=18;i<18+spRows.length;i++) s.getRange(`J${i}`).formulas=[[`=IFERROR((D${i}+0.5*E${i})/(D${i}+E${i}+F${i}+G${i}),\"\")`]];
s.getRange(`J18:J${17+spRows.length}`).setNumberFormat("0.0%");
s.getRange(`A18:J${17+spRows.length}`).format.font={name:"Arial",size:9,color:text};
s.getRange(`A18:J${17+spRows.length}`).format.borders={bottom:{style:"hair",color:grid}};
s.getRange("A51:J51").format.borders={bottom:{style:"thin",color:navy}};
s.getRange("A54").values=[["状态定义"]]; s.getRange("B54").values=[["S充分支持；P部分支持；NR未报告；C明确冲突；NA不适用；UJ仅凭论文无法判断。NR和UJ均不表示现实中未实施。"]];
s.getRange("A55").values=[["计算说明"]]; s.getRange("B55").values=[["可观察支持指数=(S+0.5×P)/(S+P+NR+C)。该指数描述公开报告覆盖度，不是JCSEE官方合规总分。"]];
s.getRange("A56").values=[["官方来源"]]; s.getRange("B56").values=[["JCSEE Program Evaluation Standards (2010): https://evaluationstandards.org/program/"]];
s.getRange("A54:A56").format.font={bold:true,color:navy}; s.getRange("B54:B56").format.font={italic:true,color:"#52606D"};
s.getRange("A:A").format.columnWidth=14; s.getRange("B:B").format.columnWidth=44; s.getRange("C:J").format.columnWidth=13; s.getRange("E:E").format.columnWidth=20;
s.freezePanes.freezeRows(4);
addDataSheet("30项规则","JCSEE 30项操作化规则",data.codebook,{widths:[10,8,32,18,42,44,38,36,38,32,42],freezeCols:2});
addDataSheet("逐实践审查","426条完整评价实践的30项判定",data.audit_wide,{widths:[10,16,18,11,11,...Array(30).fill(10)],statusStart:5,freezeCols:3,wrap:false});
addDataSheet("逐项证据","每条实践×每项标准的证据与理由",data.audit_long,{widths:[10,16,18,11,11,10,30,10,18,14,58,46],freezeCols:3});
addDataSheet("实践概况","逐实践公开报告覆盖度概况",data.profiles,{widths:[10,16,18,11,11,10,10,10,10,10,10,20,20],freezeCols:3,wrap:false});
addDataSheet("排除登记","64条不完整候选记录的排除登记",data.excluded,{widths:[10,16,20,42,30,30,50],freezeCols:3});
addDataSheet("案例等权","案例聚类稳健性汇总",data.standard_case,{widths:[10,34,12,12,12,12,12,12,12,18],freezeCols:2,wrap:false});
addDataSheet("论文等权","论文聚类稳健性汇总",data.standard_paper,{widths:[10,34,12,12,12,12,12,12,12,18],freezeCols:2,wrap:false});

await wb.recalculate();
const check=await wb.inspect({kind:"table",sheetId:s.sheetId,range:"A2:J25",include:"values,formulas",tableMaxRows:25,tableMaxCols:10,maxChars:6000});
await fs.writeFile(`${root}/workbook_inspect.ndjson`,check.ndjson,"utf8");
const err=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:300},summary:"final formula error scan"});
await fs.writeFile(`${root}/workbook_errors.ndjson`,err.ndjson,"utf8");
const preview=await wb.render({sheetName:"RQ2摘要",range:"A1:T56",scale:1.2,format:"png"});
await fs.writeFile(`${root}/workbook_preview.png`,new Uint8Array(await preview.arrayBuffer()));
const out=await SpreadsheetFile.exportXlsx(wb); await out.save(`${root}/AI辅助设计感知效应_RQ2_JCSEE30全文规范性审查.xlsx`);
console.log(`${root}/AI辅助设计感知效应_RQ2_JCSEE30全文规范性审查.xlsx`);
