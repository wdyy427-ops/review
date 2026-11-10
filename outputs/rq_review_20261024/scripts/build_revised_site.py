from __future__ import annotations

import json

import pandas as pd

from config import ROOT, LABELS
from revised_pipeline import TOOL_LABELS


DATA = ROOT / "revised_results"
OUT = ROOT / "site" / "dist"
OUT.mkdir(parents=True, exist_ok=True)


def records(name):
    return pd.read_csv(DATA / name, keep_default_na=False).to_dict("records")


def main():
    chains = pd.read_csv(DATA / "evidence_chains_revised.csv", keep_default_na=False)
    keep = ["paper_id","eval_id","chain_id","title","year","domains","stages","ai_functions","ai_roles","target_users","purposes","objects","evaluators","sources","setting","tasks","constraints","claim_type","claim_quote","claim_summary","construct_raw","dimension_code","indicator_code","pages","result_quote","revised_quality_tier","revised_quality_index","model_eligible_main","model_eligible_sensitivity"]
    payload = {
        "summary": json.loads((DATA / "summary.json").read_text(encoding="utf-8")),
        "labels": LABELS,
        "toolLabels": TOOL_LABELS,
        "chains": chains[keep].to_dict("records"),
        "instances": records("measure_instances.csv"),
        "weights": records("rq3_label_group_weights.csv"),
        "specific": records("rq3_specific_tool_evidence.csv"),
    }
    (OUT / "data.js").write_text("window.REVIEW_DATA=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
    html = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI辅助设计感知评价证据导航</title>
<style>
:root{--ink:#19384d;--ink2:#2b6078;--text:#263640;--muted:#657682;--line:#dce5e9;--paper:#f4f7f8;--white:#fff;--teal:#3f8377;--gold:#d29a3d;--rose:#b85f69;--soft:#eef4f5}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--text);font-family:"Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;line-height:1.55}
header{background:linear-gradient(125deg,#112f45 0%,#245b73 62%,#377f72 100%);color:white;padding:46px max(24px,calc((100vw - 1220px)/2)) 76px}header h1{margin:0 0 10px;font-size:clamp(29px,4vw,46px);letter-spacing:.02em}header p{max-width:850px;margin:0;color:#e4eef1;font-size:16px}
.wrap{max-width:1220px;margin:-48px auto 80px;padding:0 20px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.stat{background:white;border-radius:15px;padding:18px 20px;box-shadow:0 10px 25px #17324d17;border:1px solid #edf2f4}.stat b{display:block;font-size:29px;color:var(--ink)}.stat span{font-size:13px;color:var(--muted)}
.panel{background:white;border:1px solid var(--line);border-radius:18px;padding:24px;margin-top:20px;box-shadow:0 5px 18px #17324d0a}.panel h2{margin:0 0 5px;color:var(--ink);font-size:23px}.note{margin:0 0 17px;color:var(--muted);font-size:14px}
.weights{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.weight-card{background:linear-gradient(180deg,#fbfcfd,#f5f8f9);border:1px solid var(--line);border-radius:13px;padding:15px}.weight-card h3{margin:0 0 8px;color:var(--ink);font-size:16px}.barline{display:grid;grid-template-columns:128px 1fr 44px;gap:8px;align-items:center;font-size:12px;margin:6px 0}.bar{height:7px;background:#e4eaed;border-radius:20px;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--ink2),var(--teal))}
.group-title{grid-column:1/-1;margin:12px 0 -3px;font-weight:800;color:var(--ink);font-size:14px;border-bottom:1px solid var(--line);padding-bottom:6px}.filters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.field label{display:block;font-size:12px;font-weight:800;color:#465d6b;margin-bottom:5px}.field select,.field input{width:100%;border:1px solid #cdd9df;border-radius:10px;background:white;padding:10px 11px;font:inherit;color:var(--text)}.field input:focus,.field select:focus{outline:2px solid #63a69a55;border-color:#4f9185}.wide{grid-column:1/-1}.actions{display:flex;align-items:center;gap:10px;margin-top:16px;flex-wrap:wrap}.btn{border:0;border-radius:10px;padding:11px 17px;background:var(--ink);color:white;font-weight:800;cursor:pointer}.btn.secondary{background:#e8eef1;color:var(--ink)}.toggle{margin-left:auto;font-size:13px;color:var(--muted)}.toggle select{margin-left:6px;padding:8px;border-radius:8px;border:1px solid #cdd9df}
.flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:10px;align-items:center}.step{background:#f8fafb;border:1px solid var(--line);border-radius:12px;padding:14px;min-height:75px}.step b{color:var(--ink)}.arrow{color:#7e909b;font-size:20px}.results-block{margin-top:21px}.results-head{display:flex;align-items:end;justify-content:space-between;gap:10px;border-bottom:1px solid var(--line);padding-bottom:8px}.results-head h3{margin:0;color:var(--ink);font-size:19px}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:12px}.card{border:1px solid var(--line);border-radius:14px;padding:16px;background:white;position:relative}.card.selected{border:2px solid var(--teal);padding:15px;box-shadow:0 4px 16px #3f83771c}.card h4{margin:0 0 7px;color:var(--ink);font-size:17px}.card button{border:0;background:none;padding:0;text-align:left;width:100%;font:inherit;cursor:pointer}.chips{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}.chip,.badge{display:inline-block;border-radius:999px;padding:3px 8px;font-size:11px}.chip{background:#e9f2f0;color:#2c6b60}.chip.gold{background:#fff1d8;color:#8a5d19}.badge{font-weight:800}.q12{background:#dbeee8;color:#245e52}.q3{background:#fff0d5;color:#855a16}.weak{background:#edf0f2;color:#65717a}.meter{height:8px;background:#edf1f3;border-radius:20px;overflow:hidden;margin:9px 0}.meter i{display:block;height:100%;background:linear-gradient(90deg,var(--ink2),var(--teal))}.meta{font-size:12px;color:var(--muted);margin:6px 0}.evidence{font-size:12px;color:#445966;background:#f6f8f9;border-left:3px solid #9db2bd;padding:9px 10px;margin-top:9px;max-height:150px;overflow:auto}.empty{grid-column:1/-1;padding:28px;text-align:center;color:var(--muted);border:1px dashed #b8c8d0;border-radius:13px}.warning{background:#fff8e8;border:1px solid #ecd39d;border-radius:10px;padding:10px 12px;color:#76541e;font-size:13px}.screen-reader{position:absolute;left:-9999px}footer{text-align:center;color:#71818b;font-size:12px;margin-top:28px}
@media(max-width:950px){.weights,.cards{grid-template-columns:1fr 1fr}.filters{grid-template-columns:1fr 1fr}}@media(max-width:650px){.stats,.weights,.cards,.filters,.flow{grid-template-columns:1fr}.arrow{text-align:center;transform:rotate(90deg)}.toggle{margin-left:0}.wide{grid-column:1}}
</style></head><body>
<header><h1>AI辅助设计感知评价证据导航</h1><p>把设计师的评价目的、效果主张、对象、情境、相关人和可用数据转化为可追溯的“评价维度→主观指标→测量工具”候选。每项建议同时显示证据层级和支持量。</p></header>
<main class="wrap"><section class="stats" id="stats"></section>
<section class="panel"><h2>标签对不同推荐目标的作用不同</h2><p class="note">下列权重来自扩展规范集的论文分组交叉验证消融。它们用于安排提问顺序和排序，不解释因果。</p><div class="weights" id="weights"></div></section>
<section class="panel"><h2>1. 描述你的评价任务</h2><p class="note">可以只选你确定的标签。系统会按标签组权重计算相似证据，并在严格证据不足时明确回退到扩展规范集。</p><div class="filters" id="filters"></div><div class="actions"><button class="btn" id="run">更新推荐</button><button class="btn secondary" id="reset">清空条件</button><label class="toggle">证据范围<select id="tier"><option value="auto">自动：先严格后扩展</option><option value="main">只看主要规范集</option><option value="expanded">查看扩展规范集</option></select></label></div></section>
<section class="panel"><h2>2. 按层级确认</h2><div class="flow"><div class="step"><b>评价维度</b><br><span class="meta">先确定要解释哪类感知效应</span></div><div class="arrow">→</div><div class="step"><b>主观指标</b><br><span class="meta">在维度内选择可操作的指标</span></div><div class="arrow">→</div><div class="step"><b>测量工具</b><br><span class="meta">再选择工具类别和具体方案</span></div></div><div id="resultNote" class="warning" style="margin-top:15px"></div><div id="results"></div></section>
<footer>依据125篇论文、158个评价案例、490条评价证据链构建。建议用于研究设计支持，不能替代构念界定、效度论证和预测试。</footer></main>
<script src="data.js"></script><script>
const D=window.REVIEW_DATA,L=D.labels,T=D.toolLabels;
const split=s=>String(s||'').split(';').filter(x=>x&&!['NR','NA','UNMAPPED'].includes(x));
const esc=s=>String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const short=(s,n=260)=>{s=String(s||'').replace(/\s+/g,' ').trim();return s.length>n?s.slice(0,n-1)+'…':s};
const groups={G1:['purposes'],G2:['claim_type'],G3:['objects'],G4:['domains','stages'],G5:['evaluators','target_users'],G6:['sources','constraints','setting'],G7:['ai_functions','ai_roles','tasks']};
const fields=[
 ['评价核心','claimText','text','拟评价的效果主张（可输入关键词）'],
 ['评价核心','purposes','purpose','评价目的'],['评价核心','claim_type','claim_type','效果主张形式'],['评价核心','objects','object','评价对象'],
 ['设计情境','domains','domain','设计领域'],['设计情境','stages','stage','设计阶段'],
 ['相关人','evaluators','evaluator','评价主体'],['相关人','target_users','target_user','AI辅助目标用户'],
 ['证据条件','sources','source','可用数据源'],['证据条件','setting','setting','评价环境'],['证据条件','constraints','constraint','可行性约束'],
 ['AI活动','ai_functions','ai_function','AI功能'],['AI活动','ai_roles','ai_role','AI角色'],['AI活动','tasks','task','设计任务']
];
const targetMap={dimension:'评价维度',indicator:'主观指标',tool:'测量工具类别'};
function weightMap(target){const rows=D.weights.filter(x=>x.analysis_tier==='扩展规范集'&&x.target===targetMap[target]);const o={};rows.forEach(x=>o[x.feature_group.split('_')[0]]=+x.normalized_weight||0);return o}
function renderWeights(){const label={G1:'评价目的',G2:'效果主张形式',G3:'评价对象',G4:'设计情境',G5:'评价主体与用户',G6:'数据源与可行条件',G7:'AI活动特征'};document.querySelector('#weights').innerHTML=['dimension','indicator','tool'].map(t=>{const w=weightMap(t);return `<div class="weight-card"><h3>${targetMap[t]}</h3>${Object.keys(label).sort((a,b)=>(w[b]||0)-(w[a]||0)).map(g=>`<div class="barline"><span>${label[g]}</span><span class="bar"><i style="width:${Math.round((w[g]||0)*100)}%"></i></span><b>${Math.round((w[g]||0)*100)}%</b></div>`).join('')}</div>`}).join('')}
function renderFilters(){let last='';document.querySelector('#filters').innerHTML=fields.map(([section,col,f,label])=>{let h='';if(section!==last){last=section;h=`<div class="group-title">${section}</div>`}if(f==='text')return h+`<div class="field wide"><label>${label}</label><input id="claimText" placeholder="例如：AI辅助构思是否提高设计方案的新颖性？"></div>`;return h+`<div class="field"><label>${label}</label><select data-col="${col}"><option value="">不限</option>${Object.entries(L[f]||{}).map(([k,v])=>`<option value="${k}">${k} ${v}</option>`).join('')}</select></div>`}).join('')}
function selections(){const s={};document.querySelectorAll('[data-col]').forEach(e=>{if(e.value)s[e.dataset.col]=e.value});const q=document.querySelector('#claimText').value.trim().toLowerCase();if(q)s.claimText=q;return s}
function groupOf(col){for(const [g,cols] of Object.entries(groups))if(cols.includes(col))return g;return 'G2'}
function rowScore(c,target,sel){const w=weightMap(target);let got=0,den=0;for(const [col,val] of Object.entries(sel)){if(col==='claimText')continue;const g=groupOf(col),ww=(w[g]||.02);den+=ww;const yes=['claim_type','setting'].includes(col)?String(c[col])===val:split(c[col]).includes(val);if(yes)got+=ww}if(sel.claimText){den+=.15;const txt=[c.claim_quote,c.claim_summary,c.construct_raw].join(' ').toLowerCase();if(sel.claimText.split(/\s+/).some(k=>k&&txt.includes(k)))got+=.15}return den?got/den:1}
function sourceRows(mode){if(mode==='main')return D.chains.filter(c=>+c.model_eligible_main===1);return D.chains.filter(c=>+c.model_eligible_sensitivity===1)}
function summarize(rows,target,sel,filterFn){const map={};rows.filter(filterFn||(()=>true)).forEach(c=>{const code=target==='dimension'?c.dimension_code:c.indicator_code;if(!(target==='dimension'?L.dimension[code]:L.indicator[code]))return;const s=rowScore(c,target,sel);if(s<=0)return;const x=map[code]??={code,label:target==='dimension'?L.dimension[code]:L.indicator[code],score:0,chains:new Set(),papers:new Set(),rows:[]};x.score+=s;x.chains.add(c.chain_id);x.papers.add(c.paper_id);x.rows.push({...c,_score:s});map[code]=x});return Object.values(map).map(x=>({...x,n:x.chains.size,p:x.papers.size})).sort((a,b)=>b.score-a.score||b.p-a.p||b.n-a.n)}
function chooseTier(target,sel,filterFn){const requested=document.querySelector('#tier').value;if(requested!=='auto')return {tier:requested,rows:sourceRows(requested),fallback:false};const m=summarize(sourceRows('main'),target,sel,filterFn);const enough=m.some(x=>x.p>=2&&x.n>=3);return enough?{tier:'main',rows:sourceRows('main'),fallback:false}:{tier:'expanded',rows:sourceRows('expanded'),fallback:true}}
let selectedDimension='',selectedIndicator='';
function evidenceCard(x,target,tier,maxScore){const cls=tier==='main'?'q12':'q3';const badge=tier==='main'?'主要规范集':'扩展规范集';const samples=x.rows.sort((a,b)=>b._score-a._score).slice(0,3).map(c=>`论文${c.paper_id}（${esc(c.pages||'页码未报告')}）：${esc(short(c.result_quote||c.claim_quote||c.claim_summary))}`).join('<br><br>');const chosen=(target==='dimension'&&x.code===selectedDimension)||(target==='indicator'&&x.code===selectedIndicator);return `<article class="card ${chosen?'selected':''}"><button data-pick="${target}" data-code="${x.code}" aria-label="选择${esc(x.label)}"><h4>${x.code} ${esc(x.label)}</h4></button><div class="chips"><span class="badge ${cls}">${badge}</span><span class="chip">${x.p}篇论文</span><span class="chip">${x.n}条链</span></div><div class="meter"><i style="width:${Math.max(4,Math.round(100*x.score/Math.max(.001,maxScore)))}%"></i></div><p class="meta">加权相似支持 ${x.score.toFixed(1)}</p><details><summary>查看证据</summary><div class="evidence">${samples||'暂无可显示引文'}</div></details></article>`}
function toolSummary(rows,sel,tier){const valid=new Set(rows.map(c=>c.chain_id));const map={};D.instances.filter(i=>valid.has(i.chain_id)&&T[i.tool_code]).forEach(i=>{const c=rows.find(x=>x.chain_id===i.chain_id);if(!c)return;const s=rowScore(c,'tool',sel);const x=map[i.tool_code]??={code:i.tool_code,label:T[i.tool_code],score:0,chains:new Set(),papers:new Set(),names:{},rows:[]};x.score+=s;x.chains.add(i.chain_id);x.papers.add(i.paper_id);x.names[i.instrument_name]=(x.names[i.instrument_name]||0)+1;x.rows.push({...c,_score:s});map[i.tool_code]=x});return Object.values(map).map(x=>({...x,n:x.chains.size,p:x.papers.size,topNames:Object.entries(x.names).sort((a,b)=>b[1]-a[1]).slice(0,4)})).sort((a,b)=>b.score-a.score||b.p-a.p)}
function render(){const sel=selections();const dimPick=chooseTier('dimension',sel);const dims=summarize(dimPick.rows,'dimension',sel).slice(0,5);if(selectedDimension&&!dims.some(x=>x.code===selectedDimension))selectedDimension='';const dim=selectedDimension||dims[0]?.code||'';const indFilter=c=>!dim||c.dimension_code===dim;const indPick=chooseTier('indicator',sel,indFilter);const inds=summarize(indPick.rows,'indicator',sel,indFilter).slice(0,8);if(selectedIndicator&&!inds.some(x=>x.code===selectedIndicator))selectedIndicator='';const ind=selectedIndicator||inds[0]?.code||'';const toolFilter=c=>(!dim||c.dimension_code===dim)&&(!ind||c.indicator_code===ind);const toolPick=chooseTier('tool',sel,toolFilter);const toolRows=toolPick.rows.filter(toolFilter);const tool=toolSummary(toolRows,sel,toolPick.tier).slice(0,5);
const selectedCount=Object.keys(sel).length;document.querySelector('#resultNote').textContent=selectedCount?`已使用${selectedCount}个标签／关键词。维度、指标和工具分别按对应的标签组权重排序。点击候选可确认上一级。`:`未选择标签时显示语料中的基础分布。点击维度和指标可继续下钻。`;
const section=(title,sub,cards,html)=>`<div class="results-block"><div class="results-head"><h3>${title}</h3><span class="meta">${sub}</span></div><div class="cards">${cards.length?html:`<div class="empty">当前条件没有足够证据。减少筛选条件或把它记录为研究空白。</div>`}</div></div>`;
const dimHtml=dims.map(x=>evidenceCard(x,'dimension',dimPick.tier,dims[0]?.score||1)).join('');
const indHtml=inds.map(x=>evidenceCard(x,'indicator',indPick.tier,inds[0]?.score||1)).join('');
const toolHtml=tool.map(x=>{const cls=toolPick.tier==='main'?'q12':'q3';const names=x.topNames.map(([n,k])=>`${esc(n)}（${k}）`).join('；');return `<article class="card"><h4>${x.code} ${esc(x.label)}</h4><div class="chips"><span class="badge ${cls}">${toolPick.tier==='main'?'主要规范集':'扩展规范集'}</span><span class="chip gold">${x.p}篇论文</span><span class="chip">${x.n}条链</span></div><div class="meter"><i style="width:${Math.max(4,Math.round(100*x.score/Math.max(.001,tool[0]?.score||1)))}%"></i></div><p class="meta">常见具体方案：${names||'未形成可复核名称'}</p></article>`}).join('');
document.querySelector('#results').innerHTML=section('A. 评价维度',`${dimPick.fallback?'严格证据不足，已回退；':''}${dimPick.rows.length}条候选证据链`,dims,dimHtml)+section(`B. 主观指标${dim?'：'+dim+' '+L.dimension[dim]:''}`,`${indPick.fallback?'严格证据不足，已回退；':''}${indPick.rows.filter(indFilter).length}条候选证据链`,inds,indHtml)+section(`C. 测量工具${ind?'：'+ind+' '+L.indicator[ind]:''}`,`${toolPick.fallback?'严格证据不足，已回退；':''}${toolRows.length}条候选证据链`,tool,toolHtml);
document.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>{if(b.dataset.pick==='dimension'){selectedDimension=b.dataset.code;selectedIndicator=''}else selectedIndicator=b.dataset.code;render()})}
document.querySelector('#stats').innerHTML=[['全文论文',D.summary.papers],['评价案例',D.summary.evaluation_cases],['评价证据链',D.summary.evidence_chains],['工具实例',D.summary.measure_instances]].map(x=>`<div class="stat"><b>${x[1]}</b><span>${x[0]}</span></div>`).join('');
renderWeights();renderFilters();document.querySelector('#run').onclick=()=>{selectedDimension='';selectedIndicator='';render()};document.querySelector('#tier').onchange=render;document.querySelector('#reset').onclick=()=>{document.querySelectorAll('select').forEach(x=>x.value=x.id==='tier'?'auto':'');document.querySelector('#claimText').value='';selectedDimension='';selectedIndicator='';render()};render();
</script></body></html>'''
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(OUT / "index.html")


if __name__ == "__main__":
    main()
