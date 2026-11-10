import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const ROOT = "C:/Users/Administrator/Desktop/review/outputs/rq_review_20261024/supplement_enhanced_v2";
const OUT = path.join(ROOT, "deliverables");
await fs.mkdir(OUT, { recursive: true });

function parseCsv(text) {
  const rows=[]; let row=[], field="", quoted=false;
  for(let i=0;i<text.length;i++){
    const ch=text[i];
    if(quoted){ if(ch==='"' && text[i+1]==='"'){field+='"';i++;} else if(ch==='"') quoted=false; else field+=ch; }
    else { if(ch==='"') quoted=true; else if(ch===','){row.push(field);field="";} else if(ch==='\n'){row.push(field.replace(/\r$/,""));rows.push(row);row=[];field="";} else field+=ch; }
  }
  if(field.length||row.length){row.push(field.replace(/\r$/,""));rows.push(row);}
  return rows;
}

async function csv(rel){
  const txt=(await fs.readFile(path.join(ROOT,rel),"utf8")).replace(/^\uFEFF/,"");
  const m=parseCsv(txt); const h=m.shift()||[];
  return m.filter(r=>r.some(v=>v!=="")).map(r=>Object.fromEntries(h.map((x,i)=>[x,r[i]??""])));
}
async function json(rel){return JSON.parse(await fs.readFile(path.join(ROOT,rel),"utf8"));}
function numeric(v){return typeof v==="string" && /^-?\d+(\.\d+)?([eE][+-]?\d+)?$/.test(v.trim());}
function normalize(v,h){
  if(v===null||v===undefined)return "";
  const s=String(v); if(s.length>32000)return s.slice(0,31920)+"…[截断]";
  if(numeric(s) && (/^(paper_id|year|n|denominator|http_status|sample_n|classes|folds|papers|repeats|k)$/.test(h) || /(_n|_count|_instances|_chains|_papers)$/.test(h))) return Number(s);
  if(numeric(s) && /(percent|proportion|weight|macro_f1|accuracy|delta|ci_|p_value|q_value|cramers|lift|odds|index|threshold|rate|mean|sd|se)$/.test(h)) return Number(s);
  return s;
}
function colName(n){let s="";for(let x=n+1;x;x=Math.floor((x-1)/26))s=String.fromCharCode(65+(x-1)%26)+s;return s;}
function matrix(rows){if(!rows.length)return [["无数据"]];const h=Object.keys(rows[0]);return [h,...rows.map(r=>h.map(x=>normalize(r[x],x)))];}

const FONT="Microsoft YaHei", NAVY="#24425C", PALE="#DCE6EF", GREEN="#2F6B5F", RED="#8A4A44";
let TABLE_COUNTER=0;
function addDataSheet(wb,name,rows,tabColor=null){
  const sh=wb.worksheets.add(name); sh.showGridLines=false; if(tabColor)sh.tabColor=tabColor;
  const m=matrix(rows), nr=m.length,nc=m[0].length;
  sh.getRangeByIndexes(0,0,nr,nc).values=m;
  const used=sh.getRangeByIndexes(0,0,nr,nc); used.format.font={name:FONT,size:9,color:"#1F2933"};used.format.wrapText=true;used.format.verticalAlignment="top";
  const hdr=sh.getRangeByIndexes(0,0,1,nc);hdr.format.fill=NAVY;hdr.format.font={name:FONT,size:9,bold:true,color:"#FFFFFF"};hdr.format.horizontalAlignment="center";hdr.format.rowHeight=30;
  for(let j=0;j<nc;j++){
    const h=String(m[0][j]);let w=14;
    if(/title|quote|summary|description|evidence|procedure|analysis|result|note|reason|rule|source|url|context|说明|依据/.test(h))w=36;
    else if(/id|code|year|status|tier|paper_id|standard|unit|level/.test(h))w=15;
    else if(/percent|weight|macro|accuracy|delta|ci|p_value|n$/.test(h))w=13;
    else w=22;
    sh.getRange(`${colName(j)}:${colName(j)}`).format.columnWidth=w;
  }
  sh.freezePanes.freezeRows(1); sh.freezePanes.freezeColumns(Math.min(3,nc));
  if(nr>1){const t=sh.tables.add(`A1:${colName(nc-1)}${nr}`,true,`tbl_${++TABLE_COUNTER}`);t.style="TableStyleMedium2";}
  return sh;
}
function addTitle(sh,range,text){sh.getRange(range).merge();sh.getRange(range.split(":")[0]).values=[[text]];sh.getRange(range).format.font={name:FONT,size:16,bold:true,color:"#17324D"};}

async function exportVerified(wb,file,previewSheet,previewRange){
  wb.recalculate();
  const check=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:100},summary:"formula error scan",maxChars:5000});
  await fs.writeFile(path.join(OUT,file.replace(/\.xlsx$/,"_inspect.txt")),check.ndjson,"utf8");
  const img=await wb.render({sheetName:previewSheet,range:previewRange,scale:1.1,format:"png"});
  await fs.writeFile(path.join(OUT,file.replace(/\.xlsx$/,"_preview.png")),new Uint8Array(await img.arrayBuffer()));
  const x=await SpreadsheetFile.exportXlsx(wb);await x.save(path.join(OUT,file));
}

const summary=await json("analysis_summary.json");
const auditSummary=await json("01_supplement_audit/supplement_audit_summary.json");

// Workbook 1: supplement audit and change log.
{
  const audit=await csv("01_supplement_audit/supplement_audit_125_papers.csv");
  const changes=await csv("02_evidence_chain_change_log.csv");
  const availCounts=Object.fromEntries(["AVAILABLE","INTEGRATED_IN_PDF","UNAVAILABLE","NOT_FOUND"].map(k=>[k,audit.filter(r=>r.supplement_availability_final===k).length]));
  const wb=Workbook.create();const sh=wb.worksheets.add("审查总览");sh.showGridLines=false;addTitle(sh,"A2:F2","125篇在线发表页面与补充材料全覆盖审查");
  sh.getRange("A4:C14").values=[
    ["检查项","数量","解释"],
    ["论文",auditSummary.papers,"每篇均检查DOI/Crossref、官方页面和PDF中的补充材料线索"],
    ["官方页面可直接访问",auditSummary.publication_page_accessible,"可自动读取页面内容"],
    ["官方页面受限",auditSummary.publication_page_blocked_or_restricted,"出版社反自动化或权限限制；未将不可访问内容推定为不存在"],
    ["发现/整合补充材料",auditSummary.supplement_discovered_or_integrated,"包括独立附件、数据档案或PDF内附录"],
    ["未发现独立补充材料",auditSummary.no_supplement_found,"在本次三路检查中没有可靠线索"],
    ["评价相关",auditSummary.evaluation_relevant,"可能含题项、计分、样本、信效度或分析信息"],
    ["技术/情境材料",auditSummary.technical_or_context_only,"未发现可新增主观评价链的信息"],
    ["可获取/整合附录",(availCounts.AVAILABLE||0)+(availCounts.INTEGRATED_IN_PDF||0),"AVAILABLE或INTEGRATED_IN_PDF"],
    ["发现但不可获取",availCounts.UNAVAILABLE||0,"明确记录为UNAVAILABLE，不推测附件内容"],
    ["DOI修正",auditSummary.doi_corrections,"第122篇占位DOI已更正"],
  ];
  sh.getRange("E4:F10").values=[
    ["数据层级","修订前→修订后"],
    ["评价案例",`${summary.baseline.evaluation_cases} → ${summary.revised.evaluation_cases}`],
    ["证据链",`${summary.baseline.evidence_chains} → ${summary.revised.evidence_chains}`],
    ["已映射维度",`${summary.baseline.mapped_dimension_chains} → ${summary.revised.mapped_dimension_chains}`],
    ["完整可建模链",`${summary.baseline.complete_modelable_chains} → ${summary.revised.complete_modelable_chains}`],
    ["工具实例",`${summary.baseline.measure_instances} → ${summary.revised.measure_instances}`],
    ["变更日志行",summary.change_log_rows],
  ];
  for(const r of ["A4:C4","E4:F4"]){sh.getRange(r).format.fill=NAVY;sh.getRange(r).format.font={name:FONT,size:10,bold:true,color:"#FFFFFF"};}
  sh.getRange("A4:F14").format.font={name:FONT,size:10};sh.getRange("A4:F14").format.wrapText=true;sh.getRange("A4:F14").format.borders={preset:"all",style:"thin",color:"#C9D3DC"};
  sh.getRange("A:A").format.columnWidth=24;sh.getRange("B:B").format.columnWidth=14;sh.getRange("C:C").format.columnWidth=48;sh.getRange("E:E").format.columnWidth=24;sh.getRange("F:F").format.columnWidth=22;
  addDataSheet(wb,"125篇补充材料审查",audit,GREEN);addDataSheet(wb,"证据链变更日志",changes,RED);
  await exportVerified(wb,"01_补充材料全覆盖审查与证据链变更.xlsx","审查总览","A1:F14");
}

// Workbook 2: full revised coding database.
{
  const papers=await csv("03_revised_results/papers_supplement_enhanced.csv");
  const cases=await csv("03_revised_results/evaluation_cases_supplement_enhanced.csv");
  const chains=await csv("03_revised_results/evidence_chains_supplement_enhanced.csv");
  const tools=await csv("03_revised_results/measure_instances_supplement_enhanced.csv");
  const audits=await csv("03_revised_results/jcsee_chain_audit_supplement_enhanced.csv");
  const subrules=await csv("05_RQ2/rq2_revised_subrule_audit.csv");
  const subruleBook=await csv("05_RQ2/rq2_revised_subrule_codebook.csv");
  const wb=Workbook.create();const sh=wb.worksheets.add("数据库总览");sh.showGridLines=false;addTitle(sh,"A2:F2","补充材料增强版完整编码数据库");
  sh.getRange("A4:D12").values=[
    ["层级","修订后数量","主键","用途"],
    ["论文",summary.revised.papers,"paper_id","发表信息与论文级情境"],
    ["评价案例",summary.revised.evaluation_cases,"eval_id","实施情境、样本、设计、分析"],
    ["评价证据链",summary.revised.evidence_chains,"chain_id","效果主张→构念→指标→测量"],
    ["已映射评价维度",summary.revised.mapped_dimension_chains,"chain_id","RQ1维度分布"],
    ["完整可建模链",summary.revised.complete_modelable_chains,"chain_id","RQ3维度/指标模型候选"],
    ["工具实例",summary.revised.measure_instances,"measure_instance_id","一条链可有多个工具"],
    ["主要规范集",summary.revised.main_normative_chains,"chain_id","严格建模/验证"],
    ["扩展规范集",summary.revised.extended_normative_chains,"chain_id","稳健性与推荐开发"],
  ];
  sh.getRange("A4:D4").format.fill=NAVY;sh.getRange("A4:D4").format.font={name:FONT,size:10,bold:true,color:"#FFFFFF"};sh.getRange("A4:D12").format.font={name:FONT,size:10};sh.getRange("A4:D12").format.wrapText=true;sh.getRange("A4:D12").format.borders={preset:"all",style:"thin",color:"#C9D3DC"};sh.getRange("A:D").format.columnWidth=26;
  addDataSheet(wb,"论文信息",papers);addDataSheet(wb,"评价案例",cases);addDataSheet(wb,"评价证据链",chains,GREEN);addDataSheet(wb,"测量工具实例",tools);addDataSheet(wb,"七项规范审查",audits,RED);addDataSheet(wb,"41条子规则词典",subruleBook);addDataSheet(wb,"41条子规则审查",subrules,RED);
  await exportVerified(wb,"02_补充材料增强版完整编码数据库.xlsx","数据库总览","A1:F13");
}

// Workbook 3: RQ1-RQ3 and robustness results.
{
  const wb=Workbook.create();const sh=wb.worksheets.add("重分析总览");sh.showGridLines=false;addTitle(sh,"A2:H2","补充材料增强后的RQ1–RQ3重分析与稳健性比较");
  sh.getRange("A4:D12").values=[
    ["指标","修订前","修订后","变化"],
    ["评价案例",summary.baseline.evaluation_cases,summary.revised.evaluation_cases,"=C5-B5"],
    ["证据链",summary.baseline.evidence_chains,summary.revised.evidence_chains,"=C6-B6"],
    ["已映射维度",summary.baseline.mapped_dimension_chains,summary.revised.mapped_dimension_chains,"=C7-B7"],
    ["完整可建模链",summary.baseline.complete_modelable_chains,summary.revised.complete_modelable_chains,"=C8-B8"],
    ["工具实例",summary.baseline.measure_instances,summary.revised.measure_instances,"=C9-B9"],
    ["主要规范集",48,summary.revised.main_normative_chains,"=C10-B10"],
    ["扩展规范集",155,summary.revised.extended_normative_chains,"=C11-B11"],
    ["最大总体分布变化(pp)",0,summary.distribution_max_abs_delta_pp,"=C12-B12"],
  ];
  sh.getRange("D5:D12").formulas=[["=C5-B5"],["=C6-B6"],["=C7-B7"],["=C8-B8"],["=C9-B9"],["=C10-B10"],["=C11-B11"],["=C12-B12"]];
  sh.getRange("F4:H9").values=[
    ["阶段","数据口径","输出"],
    ["RQ1","不做质量筛选；全部可追溯记录","总体/年度/领域/阶段分布"],
    ["RQ2","每条链+所属案例+论文全文信息","7项JCSEE操作化规则及质量层级"],
    ["RQ3主要集",`${summary.revised.main_normative_chains}条链`,"保守验证"],
    ["RQ3扩展集",`${summary.revised.extended_normative_chains}条链`,"模型、权重、稳健性和推荐阈值"],
    ["稳健性","论文分组CV；删组重训+测试集置换","比较修订前后结论"],
  ];
  for(const r of ["A4:D4","F4:H4"]){sh.getRange(r).format.fill=NAVY;sh.getRange(r).format.font={name:FONT,size:10,bold:true,color:"#FFFFFF"};}
  sh.getRange("A4:H12").format.font={name:FONT,size:10};sh.getRange("A4:H12").format.wrapText=true;sh.getRange("A4:H12").format.borders={preset:"all",style:"thin",color:"#C9D3DC"};sh.getRange("A:D").format.columnWidth=20;sh.getRange("F:H").format.columnWidth=30;
  const sheets=[
    ["RQ1维度总体","04_RQ1/rq1_dimension_overall.csv"],["RQ1指标总体","04_RQ1/rq1_indicator_overall.csv"],["RQ1工具总体","04_RQ1/rq1_tool_overall.csv"],
    ["RQ1维度年度","04_RQ1/rq1_dimension_by_year.csv"],["RQ1指标年度","04_RQ1/rq1_indicator_by_year.csv"],["RQ1工具年度","04_RQ1/rq1_tool_by_year.csv"],
    ["RQ1领域阶段交叉","04_RQ1/rq1_domain_stage_by_dimension_indicator_tool.csv"],["RQ1趋势检验","04_RQ1/rq1_temporal_trend_tests.csv"],
    ["RQ1新增恢复链","04_RQ1/rq1_recovered_and_new_chains.csv"],["RQ1增量分布","04_RQ1/rq1_increment_distribution.csv"],["RQ1未映射原因","04_RQ1/rq1_unmapped_reason_distribution.csv"],
    ["RQ2七项分布","05_RQ2/rq2_7standard_distribution.csv"],["RQ2质量层级","05_RQ2/rq2_quality_tiers.csv"],["RQ2状态变更","05_RQ2/rq2_chain_status_changes.csv"],
    ["RQ2子规则汇总","05_RQ2/rq2_revised_subrule_summary.csv"],["RQ2层级转移","05_RQ2/rq2_quality_transition_matrix.csv"],
    ["RQ3模型比较","06_RQ3/rq3_model_comparison_g1_g7.csv"],["RQ3单次权重","06_RQ3/rq3_label_group_weights_g1_g7.csv"],["RQ3关联明细","06_RQ3/rq3_context_associations_g1_g7.csv"],
    ["RQ3稳健权重","06_RQ3/rq3_label_group_weights_stable.csv"],["RQ3阈值曲线","06_RQ3/rq3_threshold_one_se_curves.csv"],
    ["前后分布比较","07_robustness_comparison/pre_post_distribution_comparison.csv"],["前后模型比较","07_robustness_comparison/pre_post_model_performance_comparison.csv"],["前后权重比较","07_robustness_comparison/pre_post_stable_weight_comparison.csv"],
    ["质量检查","08_QC/qc_checks.csv"],
  ];
  for(const [name,rel] of sheets){try{addDataSheet(wb,name,await csv(rel));}catch(e){addDataSheet(wb,name,[{status:"文件尚未生成",path:rel,error:String(e)}]);}}
  await exportVerified(wb,"03_RQ1-RQ3重分析与稳健性比较.xlsx","重分析总览","A1:H13");
}

console.log(JSON.stringify({saved:3,output:OUT},null,2));
