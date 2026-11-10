from __future__ import annotations

import json

import pandas as pd

from config import ROOT
from revised_pipeline import TOOL_LABELS
from rq3_rebuild_g1_g7 import FINAL_LABELS


ENHANCED = ROOT / "supplement_enhanced_v2"
DATA = ENHANCED / "03_revised_results"
RQ3DATA = ENHANCED / "06_RQ3"
OUT = ROOT / "site_g1_g7" / "dist"
OUT.mkdir(parents=True, exist_ok=True)


def records(name: str):
    return pd.read_csv(DATA / name, keep_default_na=False).to_dict("records")


def main():
    chains = pd.read_csv(RQ3DATA / "evidence_chains_context_g1_g7.csv", keep_default_na=False)
    keep = [
        "paper_id", "eval_id", "chain_id", "title", "year", "domains", "stages",
        "ai_functions", "purposes", "objects_g4", "evaluators_g5", "target_users_g6", "claim_quote",
        "claim_summary", "construct_raw", "dimension_code", "indicator_code", "pages",
        "result_quote", "revised_quality_tier", "revised_quality_index",
        "model_eligible_main", "model_eligible_sensitivity",
    ]
    payload = {
        "summary": json.loads((ENHANCED / "analysis_summary.json").read_text(encoding="utf-8"))["revised"],
        "labels": FINAL_LABELS,
        "toolLabels": TOOL_LABELS,
        "chains": chains[keep].to_dict("records"),
        "instances": records("measure_instances.csv"),
        "weights": pd.read_csv(RQ3DATA / "rq3_label_group_weights_stable.csv", keep_default_na=False).to_dict("records"),
        "specific": [],
    }
    (OUT / "data_thresholded.js").write_text(
        "window.REVIEW_DATA=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8",
    )

    html = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI辅助设计感知评价证据导航</title>
<style>
:root{--ink:#173a50;--ink2:#28657c;--text:#263640;--muted:#667985;--line:#d9e4e9;--paper:#f3f7f8;--white:#fff;--teal:#3f877a;--gold:#d39a3d;--soft:#eef5f5;--shadow:#17324d12}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--text);font-family:"Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;line-height:1.55}
header{background:linear-gradient(125deg,#102f45 0%,#245c74 62%,#388276 100%);color:#fff;padding:42px max(24px,calc((100vw - 1180px)/2)) 72px}header h1{margin:0 0 9px;font-size:clamp(28px,4vw,44px)}header p{max-width:860px;margin:0;color:#e5f0f2}
.wrap{max-width:1180px;margin:-44px auto 72px;padding:0 20px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.stat,.panel{background:#fff;border:1px solid var(--line);box-shadow:0 7px 22px var(--shadow)}.stat{border-radius:14px;padding:16px 18px}.stat b{display:block;color:var(--ink);font-size:27px}.stat span,.meta,.note{color:var(--muted);font-size:12px}.panel{border-radius:18px;padding:23px;margin-top:18px}.panel h2{margin:0 0 6px;color:var(--ink);font-size:22px}.note{margin:0 0 16px;font-size:13px}
.progress{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.progress button{border:1px solid var(--line);border-radius:13px;background:#f7fafb;padding:14px;text-align:left;color:var(--muted);font:inherit;cursor:pointer}.progress button b{display:block;color:var(--ink);font-size:15px}.progress button.active{background:linear-gradient(135deg,#e7f3f1,#f5faf9);border-color:#71a99f;box-shadow:0 4px 14px #3f877a18}.progress button.locked{cursor:not-allowed;opacity:.58}.progress .num{display:inline-grid;place-items:center;width:25px;height:25px;border-radius:50%;margin-right:7px;background:#dfe9ed;color:var(--ink);font-weight:800}.progress button.active .num{background:var(--teal);color:#fff}
.chosen{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.chosen span{background:#edf4f5;border-radius:999px;padding:5px 10px;color:#335b68;font-size:12px}.chosen b{color:var(--ink)}
.group-list{display:grid;gap:12px}.group-card{border:1px solid var(--line);border-radius:14px;padding:15px;background:linear-gradient(180deg,#fbfcfd,#f6f9fa)}.group-card.supplemental{border-style:dashed;background:#fafbfb}.group-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}.group-head h3{display:flex;align-items:center;gap:7px;margin:0;color:var(--ink);font-size:16px}.status-tag{display:inline-block;border-radius:999px;padding:2px 7px;font-size:10px;font-weight:800}.status-tag.core{background:#dbeee8;color:#245e52}.status-tag.stable{background:#e8edf8;color:#425b89}.status-tag.supp{background:#edf0f2;color:#667985}.weight{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted)}.weight-bar{width:110px;height:7px;border-radius:10px;background:#e2eaed;overflow:hidden}.weight-bar i{display:block;height:100%;background:linear-gradient(90deg,var(--ink2),var(--teal))}.fields{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.field label{display:block;font-size:12px;font-weight:800;color:#49606d;margin-bottom:4px}.field select{width:100%;border:1px solid #cbd9df;border-radius:9px;background:#fff;padding:9px 10px;color:var(--text);font:inherit}.field select:focus{outline:2px solid #63a69a55;border-color:#4f9185}
.actions{display:flex;align-items:center;gap:9px;margin-top:15px;flex-wrap:wrap}.btn{border:0;border-radius:10px;padding:10px 16px;background:var(--ink);color:#fff;font-weight:800;cursor:pointer}.btn.secondary{background:#e8eef1;color:var(--ink)}.tier{margin-left:auto;font-size:12px;color:var(--muted)}.tier select{margin-left:5px;padding:7px;border:1px solid #cbd9df;border-radius:8px}
.warning{margin-top:14px;background:#fff8e8;border:1px solid #ead39e;border-radius:10px;padding:10px 12px;color:#76541e;font-size:13px}.results{margin-top:18px}.results-head{display:flex;justify-content:space-between;gap:10px;align-items:end;border-bottom:1px solid var(--line);padding-bottom:8px}.results-head h3{margin:0;color:var(--ink);font-size:19px}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;margin-top:11px}.card{border:1px solid var(--line);border-radius:14px;padding:15px;background:#fff}.card button{width:100%;padding:0;border:0;background:none;text-align:left;font:inherit;cursor:pointer}.card h4{margin:0 0 6px;color:var(--ink);font-size:16px}.chips{display:flex;gap:5px;flex-wrap:wrap;margin:7px 0}.chip,.badge{display:inline-block;border-radius:999px;padding:3px 8px;font-size:11px}.chip{background:#eaf2f2;color:#32685e}.chip.gold{background:#fff0d4;color:#865a16}.badge{font-weight:800}.q12{background:#dbeee8;color:#245e52}.q3{background:#fff0d5;color:#855a16}.meter{height:8px;background:#edf1f3;border-radius:20px;overflow:hidden;margin:8px 0}.meter i{display:block;height:100%;background:linear-gradient(90deg,var(--ink2),var(--teal))}.evidence{font-size:12px;color:#445966;background:#f6f8f9;border-left:3px solid #9db2bd;padding:8px 9px;margin-top:8px;max-height:145px;overflow:auto}.empty{padding:26px;text-align:center;color:var(--muted);border:1px dashed #b7c8d0;border-radius:12px}.next-hint{margin-top:12px;padding:11px 13px;border-radius:10px;background:#edf6f4;color:#2e675d;font-size:13px}footer{text-align:center;color:#71818b;font-size:12px;margin-top:26px}
@media(max-width:850px){.stats,.cards{grid-template-columns:1fr 1fr}.fields{grid-template-columns:1fr 1fr}}@media(max-width:600px){.stats,.cards,.fields,.progress{grid-template-columns:1fr}.tier{margin-left:0}.weight-bar{width:75px}}
</style></head><body>
<header><h1>AI辅助设计感知评价证据导航</h1><p>按“评价维度→主观指标→测量工具”逐层规划主观评价。每层仅使用同时通过删组重训与测试集置换检验的情境因素，并按综合排序权重安排提问顺序。</p></header>
<main class="wrap">
  <section class="stats" id="stats"></section>
  <section class="panel"><h2>三层渐进推荐</h2><p class="note">确认上一级后才披露下一层标签。已填写的信息会保留，并在后续层作为情境条件继续使用。</p><div class="progress" id="progress"></div></section>
  <section class="panel" id="workspace"><div id="stage"></div></section>
  <footer>依据125篇论文、159个评价案例、514条候选评价证据链和624个工具实例构建。情境关系来自20次论文分组交叉验证的删组重训与测试集置换检验，仅用于候选排序，不解释为因果效应。</footer>
</main>
<script src="data_thresholded.js"></script><script>
const D=window.REVIEW_DATA,L=D.labels,T=D.toolLabels;
const split=s=>String(s||'').split(';').filter(x=>x&&!['NR','NA','UNMAPPED'].includes(x));
const esc=s=>String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const short=(s,n=250)=>{s=String(s||'').replace(/\s+/g,' ').trim();return s.length>n?s.slice(0,n-1)+'…':s};
const groupLabels={G1:'评价目的',G2:'设计领域',G3:'设计阶段',G4:'评价对象',G5:'评价主体',G6:'目标用户',G7:'AI功能'};
const groupFields={
 G1:[['purposes','purpose','评价目的']],
 G2:[['domains','domain','设计领域']],
 G3:[['stages','stage','设计阶段']],
 G4:[['objects_g4','object','评价对象']],
 G5:[['evaluators_g5','evaluator','评价主体']],
 G6:[['target_users_g6','target_user','目标用户']],
 G7:[['ai_functions','ai_function','AI功能']]
};
const targetName={dimension:'评价维度',indicator:'主观指标',tool:'测量工具'};
const stageTarget={1:'dimension',2:'indicator',3:'tool'};
const state={stage:1,maxStage:1,answers:{},dimension:'',indicator:'',showResults:false,tier:'auto'};

function weightRows(target){return D.weights.filter(x=>x.analysis_tier==='扩展规范集'&&x.target===({dimension:'评价维度',indicator:'主观指标',tool:'测量工具类别'})[target])}
function weightMap(target){const out={};weightRows(target).forEach(x=>out[x.feature_group.split('_')[0]]=+x.normalized_weight||0);return out}
function robustMap(target){const out={};weightRows(target).forEach(x=>out[x.feature_group.split('_')[0]]=+x.robust_positive===1);return out}
function coreMap(target){return robustMap(target)}
function orderedGroups(target){const w=weightMap(target),r=robustMap(target);return Object.keys(groupFields).filter(g=>r[g]).sort((a,b)=>w[b]-w[a])}
function fieldMatch(c,col,val){return split(c[col]).includes(val)}
function rowScore(c,target){const w=weightMap(target);let numerator=0,denominator=0;for(const g of orderedGroups(target)){const answered=groupFields[g].filter(([col])=>state.answers[col]);if(!answered.length)continue;const matched=answered.filter(([col])=>fieldMatch(c,col,state.answers[col])).length;denominator+=w[g];numerator+=w[g]*(matched/answered.length)}return denominator?numerator/denominator:1}
function sourceRows(mode){if(mode==='main')return D.chains.filter(c=>+c.model_eligible_main===1);return D.chains.filter(c=>+c.model_eligible_sensitivity===1)}
function summarize(rows,target,filterFn=()=>true){const map={};for(const c of rows.filter(filterFn)){const code=target==='dimension'?c.dimension_code:c.indicator_code;const labels=target==='dimension'?L.dimension:L.indicator;if(!labels[code])continue;const s=rowScore(c,target);if(s<=0)continue;const x=map[code]??={code,label:labels[code],score:0,chains:new Set(),papers:new Set(),rows:[]};x.score+=s;x.chains.add(c.chain_id);x.papers.add(c.paper_id);x.rows.push({...c,_score:s})}return Object.values(map).map(x=>({...x,n:x.chains.size,p:x.papers.size})).sort((a,b)=>b.score-a.score||b.p-a.p||b.n-a.n)}
function chooseTier(target,filterFn=()=>true){if(state.tier!=='auto')return {tier:state.tier,rows:sourceRows(state.tier),fallback:false};const main=summarize(sourceRows('main'),target,filterFn);const enough=main.some(x=>x.p>=2&&x.n>=3);return enough?{tier:'main',rows:sourceRows('main'),fallback:false}:{tier:'expanded',rows:sourceRows('expanded'),fallback:true}}
function toolSummary(rows){const valid=new Set(rows.map(c=>c.chain_id)),byChain=new Map(rows.map(c=>[c.chain_id,c])),map={};for(const i of D.instances.filter(x=>valid.has(x.chain_id)&&T[x.tool_code])){const c=byChain.get(i.chain_id);if(!c)continue;const s=rowScore(c,'tool');if(s<=0)continue;const x=map[i.tool_code]??={code:i.tool_code,label:T[i.tool_code],score:0,instances:0,chains:new Set(),papers:new Set(),names:{},rows:[]};x.score+=s;x.instances+=1;x.chains.add(i.chain_id);x.papers.add(i.paper_id);if(i.instrument_name)x.names[i.instrument_name]=(x.names[i.instrument_name]||0)+1;x.rows.push({...c,_score:s})}return Object.values(map).map(x=>({...x,n:x.chains.size,p:x.papers.size,topNames:Object.entries(x.names).sort((a,b)=>b[1]-a[1]).slice(0,4)})).sort((a,b)=>b.score-a.score||b.p-a.p||b.instances-a.instances)}

function renderProgress(){document.querySelector('#progress').innerHTML=[1,2,3].map(n=>{const locked=n>state.maxStage,active=n===state.stage;const sub=n===1?'依据评价目的与评价对象推荐维度':n===2?'依据领域、评价对象与目标用户推荐指标':'依据目的、阶段、评价对象与AI功能推荐工具';return `<button data-stage="${n}" class="${active?'active ':''}${locked?'locked':''}" ${locked?'disabled':''}><b><span class="num">${n}</span>${targetName[stageTarget[n]]}</b><span class="meta">${sub}</span></button>`}).join('');document.querySelectorAll('[data-stage]').forEach(b=>b.onclick=()=>{state.stage=+b.dataset.stage;state.showResults=false;render()})}
function chosenSummary(){const bits=[];if(state.dimension)bits.push(`<span><b>评价维度：</b>${state.dimension} ${esc(L.dimension[state.dimension])}</span>`);if(state.indicator)bits.push(`<span><b>主观指标：</b>${state.indicator} ${esc(L.indicator[state.indicator])}</span>`);return bits.length?`<div class="chosen">${bits.join('')}</div>`:''}
function optionHtml(labelKey,current){return `<option value="">尚未定义／不限</option>${Object.entries(L[labelKey]||{}).map(([k,v])=>`<option value="${k}" ${current===k?'selected':''}>${k} ${esc(v)}</option>`).join('')}`}
function renderGroups(target){const w=weightMap(target);return `<div class="group-list">${orderedGroups(target).map(g=>`<div class="group-card"><div class="group-head"><h3>${groupLabels[g]}<span class="status-tag core">双重稳健</span></h3><div class="weight"><span>综合排序权重 ${(w[g]*100).toFixed(1)}%</span><span class="weight-bar"><i style="width:${Math.round(w[g]*100)}%"></i></span></div></div><div class="fields">${groupFields[g].map(([col,key,label])=>`<div class="field"><label>${label}${state.answers[col]?'（已继承）':''}</label><select data-answer="${col}">${optionHtml(key,state.answers[col]||'')}</select></div>`).join('')}</div></div>`).join('')}</div>`}
function evidenceCard(x,target,tier,maxScore){const badge=tier==='main'?'主要规范集':'扩展规范集',cls=tier==='main'?'q12':'q3';const samples=x.rows.sort((a,b)=>b._score-a._score).slice(0,3).map(c=>`论文${c.paper_id}（${esc(c.pages||'页码未报告')}）：${esc(short(c.result_quote||c.claim_quote||c.claim_summary))}`).join('<br><br>');return `<article class="card"><button data-pick="${target}" data-code="${x.code}"><h4>${x.code} ${esc(x.label)}</h4></button><div class="chips"><span class="badge ${cls}">${badge}</span><span class="chip">${x.p}篇论文</span><span class="chip">${x.n}条链</span>${x.instances?`<span class="chip gold">${x.instances}个工具实例</span>`:''}</div><div class="meter"><i style="width:${Math.max(4,Math.round(100*x.score/Math.max(.001,maxScore)))}%"></i></div><p class="meta">目标层权重下的匹配支持 ${x.score.toFixed(1)}</p><details><summary>查看证据</summary><div class="evidence">${samples||'暂无可显示引文'}</div></details></article>`}
function renderResults(target){let pick,items,filterFn=()=>true;if(target==='dimension'){pick=chooseTier(target);items=summarize(pick.rows,target).slice(0,5)}else if(target==='indicator'){filterFn=c=>c.dimension_code===state.dimension;pick=chooseTier(target,filterFn);items=summarize(pick.rows,target,filterFn).slice(0,8)}else{filterFn=c=>c.dimension_code===state.dimension&&c.indicator_code===state.indicator;pick=chooseTier('indicator',filterFn);const toolTier=state.tier==='auto'?(pick.fallback?'expanded':'main'):state.tier;pick={tier:toolTier,rows:sourceRows(toolTier),fallback:state.tier==='auto'&&toolTier==='expanded'};items=toolSummary(pick.rows.filter(filterFn)).slice(0,5)}const fallback=pick.fallback?'主要规范集支持不足，本层已回退到扩展规范集。':'';const title=target==='dimension'?'选择一个评价维度进入下一层':target==='indicator'?'选择一个主观指标进入下一层':'测量工具类别与具体方案';const cards=items.length?items.map(x=>evidenceCard(x,target,pick.tier,items[0]?.score||1)).join(''):`<div class="empty">当前条件下没有足够证据。可减少本层标签，或将其记录为研究空白。</div>`;return `<div class="results"><div class="results-head"><h3>${title}</h3><span class="meta">${fallback}</span></div><div class="cards">${cards}</div>${target!=='tool'&&items.length?`<div class="next-hint">点击候选后，系统才会披露下一层需要定义的标签。</div>`:''}</div>`}
function render(){renderProgress();const target=stageTarget[state.stage],rows=weightRows(target),model=rows[0]?.selected_model||'未建模';const intro=state.stage===1?'本层使用G4评价对象和G1评价目的推荐评价维度。':state.stage===2?'已确认维度作为固定条件，本层使用G4评价对象、G2设计领域和G6目标用户推荐主观指标。':'已确认维度和指标作为固定条件，本层使用G1评价目的、G7 AI功能、G4评价对象和G3设计阶段推荐测量工具。';document.querySelector('#stage').innerHTML=`<h2>${state.stage}. 定义${targetName[target]}推荐条件</h2><p class="note">${intro} 本层模型：${esc(model)}。仅显示删组重训与测试集置换的95%置信区间均高于0的情境因素。</p>${chosenSummary()}${renderGroups(target)}<div class="actions"><button class="btn" id="recommend">生成${targetName[target]}推荐</button><button class="btn secondary" id="resetStage">清空本层标签</button><label class="tier">证据范围<select id="tier"><option value="auto" ${state.tier==='auto'?'selected':''}>自动：先主要后扩展</option><option value="main" ${state.tier==='main'?'selected':''}>只看主要规范集</option><option value="expanded" ${state.tier==='expanded'?'selected':''}>查看扩展规范集</option></select></label></div><div class="warning">本层只使用上方双重稳健因素计算匹配分数；其他G组不显示且不参与后台计算。综合排序权重表示条件预测贡献，不代表因果效应。</div>${state.showResults?renderResults(target):''}`;document.querySelectorAll('[data-answer]').forEach(e=>e.onchange=()=>{if(e.value)state.answers[e.dataset.answer]=e.value;else delete state.answers[e.dataset.answer];state.showResults=false;render()});document.querySelector('#recommend').onclick=()=>{state.showResults=true;render()};document.querySelector('#tier').onchange=e=>{state.tier=e.target.value;state.showResults=false;render()};document.querySelector('#resetStage').onclick=()=>{for(const g of orderedGroups(target))for(const [col] of groupFields[g])delete state.answers[col];state.showResults=false;render()};document.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>{if(b.dataset.pick==='dimension'){state.dimension=b.dataset.code;state.indicator='';state.stage=2;state.maxStage=Math.max(state.maxStage,2)}else if(b.dataset.pick==='indicator'){state.indicator=b.dataset.code;state.stage=3;state.maxStage=3}state.showResults=false;render();window.scrollTo({top:document.querySelector('#workspace').offsetTop-20,behavior:'smooth'})})}
document.querySelector('#stats').innerHTML=[['全文论文',D.summary.papers],['评价案例',D.summary.evaluation_cases],['候选证据链',D.summary.evidence_chains],['工具实例',D.summary.measure_instances]].map(x=>`<div class="stat"><b>${x[1]}</b><span>${x[0]}</span></div>`).join('');
render();
</script></body></html>'''
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(OUT / "index.html")


if __name__ == "__main__":
    main()
