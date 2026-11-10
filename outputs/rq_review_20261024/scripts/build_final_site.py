from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config import ROOT, LABELS


DATA = ROOT / "final_results"
OUT = ROOT / "site" / "dist"
OUT.mkdir(parents=True, exist_ok=True)


def records(path):
    return pd.read_csv(path).fillna("").to_dict("records")


def main():
    payload = {
        "summary": json.loads((DATA / "summary.json").read_text(encoding="utf-8")),
        "labels": LABELS,
        "chains": records(DATA / "chains.csv"),
        "evaluations": records(DATA / "evaluations.csv"),
        "recommendations": records(DATA / "recommendations.csv"),
        "associations": records(DATA / "rq3_associations.csv"),
    }
    (OUT / "data.js").write_text("window.REVIEW_DATA=" + json.dumps(payload, ensure_ascii=False) + ";", encoding="utf-8")
    html = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI辅助设计感知评价推荐器</title>
<style>
:root{--ink:#17324d;--muted:#607080;--line:#dfe7ec;--paper:#f4f7f8;--white:#fff;--teal:#2f7d6d;--amber:#d39132;--red:#b94e55}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:#20313e;font-family:"Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;line-height:1.55}
header{background:linear-gradient(125deg,#102c46,#275d76 62%,#2f7d6d);color:white;padding:44px max(24px,calc((100vw - 1180px)/2));box-shadow:0 8px 28px #17324d2a}
header h1{margin:0 0 10px;font-size:clamp(28px,4vw,46px);letter-spacing:.02em}header p{max-width:820px;margin:0;color:#e4eef2;font-size:16px}
.wrap{max-width:1180px;margin:26px auto 80px;padding:0 20px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:-48px}.stat{background:white;border:1px solid #ffffff70;border-radius:16px;padding:20px;box-shadow:0 8px 24px #17324d18}.stat b{display:block;font-size:30px;color:var(--ink)}.stat span{color:var(--muted);font-size:13px}
.panel{background:white;border:1px solid var(--line);border-radius:18px;padding:24px;margin-top:22px;box-shadow:0 5px 18px #17324d0d}.panel h2{margin:0 0 6px;color:var(--ink)}.note{color:var(--muted);font-size:14px;margin:0 0 18px}
.filters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.field label{display:block;font-size:13px;font-weight:700;color:#405465;margin-bottom:6px}.field select,.field input{width:100%;border:1px solid #cfdbe2;border-radius:10px;background:white;padding:10px 11px;font:inherit;color:#20313e}.actions{display:flex;gap:10px;align-items:end}.btn{border:0;border-radius:10px;padding:11px 18px;background:var(--ink);color:white;font-weight:700;cursor:pointer}.btn.secondary{background:#e8eef1;color:var(--ink)}
.flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:10px;align-items:center;margin:18px 0}.step{border:1px solid var(--line);border-radius:12px;padding:14px;background:#f9fbfc;min-height:74px}.arrow{color:#80909d}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.card{border:1px solid var(--line);border-radius:14px;padding:18px;background:#fff}.card h3{margin:0 0 8px;color:var(--ink);font-size:18px}.chips{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}.chip{font-size:12px;background:#e8f2ef;color:#256656;border-radius:999px;padding:4px 9px}.chip.amber{background:#fff0d6;color:#915f17}.meter{height:8px;background:#edf1f3;border-radius:99px;overflow:hidden}.meter i{display:block;height:100%;background:linear-gradient(90deg,#2f7d6d,#65ac9c)}.meta{font-size:13px;color:var(--muted)}.empty{padding:36px;text-align:center;color:var(--muted);border:1px dashed #bdcbd3;border-radius:14px}.evidence{font-size:13px;color:#405465;background:#f7f9fa;border-left:3px solid #9db2bd;padding:9px 11px;margin-top:10px;max-height:140px;overflow:auto}.badge{display:inline-block;padding:3px 7px;border-radius:6px;font-size:11px;font-weight:700}.strong{background:#dcefe9;color:#216050}.explore{background:#fff0d6;color:#825718}.weak{background:#edf0f2;color:#68747c}
footer{color:#71808b;font-size:13px;text-align:center;margin-top:30px}@media(max-width:800px){.stats{grid-template-columns:repeat(2,1fr)}.filters,.cards{grid-template-columns:1fr}.flow{grid-template-columns:1fr}.arrow{transform:rotate(90deg);text-align:center}}
</style></head><body>
<header><h1>AI辅助设计感知评价推荐器</h1><p>根据125篇全文编码，先用研究情境缩小感知构念与指标范围，再依据规范性筛选后的证据推荐测量工具。所有建议同时显示支持度和不确定性。</p></header>
<main class="wrap"><section class="stats" id="stats"></section>
<section class="panel"><h2>1. 定义你的评价问题</h2><p class="note">效果主张由研究者提出。系统提供相似情境中常见的构念和指标，帮助检查遗漏。</p>
<div class="filters" id="filters"></div><div class="actions" style="margin-top:16px"><button class="btn" id="run">生成建议</button><button class="btn secondary" id="reset">清空条件</button></div></section>
<section class="panel"><h2>2. 从主张到测量</h2><div class="flow"><div class="step"><b>Evaluation Question</b><br><span class="meta">你拟提出的效果主张</span></div><div class="arrow">→</div><div class="step"><b>Construct / Indicator</b><br><span class="meta">本语料中可比较的感知维度与指标</span></div><div class="arrow">→</div><div class="step"><b>Measure</b><br><span class="meta">工具族、实例和可复核证据</span></div></div></section>
<section class="panel"><h2>推荐结果</h2><p class="note" id="resultNote"></p><div class="cards" id="results"></div></section>
<footer>本工具呈现文献中的经验选择规律，不替代构念定义、效度论证和具体研究设计。</footer></main>
<script src="data.js"></script><script>
const D=window.REVIEW_DATA,L=D.labels;
const fields=[['domains','domain','设计领域'],['stages','stage','设计阶段'],['ai_functions','ai_function','AI功能'],['ai_roles','ai_role','AI角色'],['purposes','purpose','评价目的'],['objects','object','评价对象'],['evaluators','evaluator','评价主体'],['sources','source','数据源']];
const split=s=>String(s||'').split(';').filter(Boolean);const esc=s=>String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));const short=(s,n=120)=>{s=String(s||'').replace(/\s+/g,' ').trim();return s.length>n?s.slice(0,n-1)+'…':s};
document.querySelector('#stats').innerHTML=[['论文',D.summary.papers],['人类主观评价论文',D.summary.papers_with_human_subjective_evaluation],['评价案例',D.summary.evaluations],['证据链',D.summary.chains]].map(x=>`<div class="stat"><b>${x[1]}</b><span>${x[0]}</span></div>`).join('');
document.querySelector('#filters').innerHTML=fields.map(([col,f,label])=>`<div class="field"><label>${label}</label><select data-col="${col}" data-field="${f}"><option value="">不限</option>${Object.entries(L[f]).map(([k,v])=>`<option value="${k}">${k} ${v}</option>`).join('')}</select></div>`).join('')+`<div class="field"><label>拟评价的主观指标</label><select id="indicator"><option value="">先由系统建议</option>${Object.entries(L.indicator).map(([k,v])=>`<option value="${k}">${k} ${v}</option>`).join('')}</select></div>`;
function selected(){const x={};document.querySelectorAll('[data-col]').forEach(e=>{if(e.value)x[e.dataset.col]=e.value});return x}
function grade(n,papers){return papers>=3&&n>=5?['较强','strong']:papers>=2&&n>=3?['探索性','explore']:['证据有限','weak']}
function render(){const sel=selected(),ind=document.querySelector('#indicator').value;let chains=D.chains.filter(c=>+c.association_eligible===1);const entries=Object.entries(sel);chains=chains.filter(c=>entries.every(([col,val])=>split(c[col]).includes(val)));let recs=[];
if(ind){recs=D.recommendations.filter(r=>r.indicator_code===ind).map(r=>({...r,dimension_code:ind[0],matched:chains.filter(c=>c.indicator_code===ind&&split(c.tool_families).includes(r.tool_code))}))}
else{const map={};chains.forEach(c=>{if(!L.indicator[c.indicator_code])return;split(c.tool_families).forEach(t=>{if(!L.tool_family[t])return;const k=c.indicator_code+'|'+t;(map[k]??={indicator_code:c.indicator_code,indicator_label:L.indicator[c.indicator_code],dimension_code:c.dimension_code,tool_code:t,tool_label:L.tool_family[t],matched:[]}).matched.push(c)})});recs=Object.values(map)}
recs.forEach(r=>{r.support_chains=r.matched.length;r.support_papers=new Set(r.matched.map(x=>x.paper_id)).size;r.prob=r.support_chains/Math.max(1,chains.filter(c=>c.indicator_code===r.indicator_code).length)});recs.sort((a,b)=>b.support_papers-a.support_papers||b.support_chains-a.support_chains);recs=recs.slice(0,24);
document.querySelector('#resultNote').textContent=`当前条件匹配 ${new Set(chains.map(c=>c.paper_id)).size} 篇论文、${chains.length} 条规范性筛选后证据链。`;
document.querySelector('#results').innerHTML=recs.length?recs.map(r=>{const [g,cl]=grade(r.support_chains,r.support_papers);const examples=[...new Set(r.matched.map(x=>x.instrument_raw).filter(x=>x&&!['NR','UNMAPPED'].includes(x)))].slice(0,3);const cites=r.matched.slice(0,5).map(x=>`论文 ${x.paper_id}，PDF页 ${esc(x.pages||'未报告')}：${esc(short(x.result_quote||x.claim_quote||x.claim_summary,360))}`);return `<article class="card"><h3>${r.indicator_code} ${esc(r.indicator_label||L.indicator[r.indicator_code])}</h3><div class="chips"><span class="chip">${r.dimension_code} ${L.dimension[r.dimension_code]||''}</span><span class="chip amber">${r.tool_code} ${esc(r.tool_label||L.tool_family[r.tool_code])}</span><span class="badge ${cl}">${g}</span></div><div class="meter"><i style="width:${Math.min(100,Math.round((r.prob||0)*100))}%"></i></div><p class="meta">${r.support_chains} 条证据链，${r.support_papers} 篇论文；在当前匹配中占 ${Math.round((r.prob||0)*100)}%</p>${examples.length?`<p><b>原文工具／方法表述</b><br>${examples.map(x=>esc(short(x))).join('；')}</p>`:''}<details><summary>查看原文证据</summary><div class="evidence">${cites.join('<br><br>')||'暂无可显示引文'}</div></details></article>`}).join(''):`<div class="empty">当前条件没有达到展示门槛的规范性证据。请减少筛选条件，或把它作为研究空白而不是强行推荐。</div>`}
document.querySelector('#run').onclick=render;document.querySelector('#reset').onclick=()=>{document.querySelectorAll('select').forEach(x=>x.value='');render()};render();
</script></body></html>'''
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(OUT / "index.html")


if __name__ == "__main__":
    main()
