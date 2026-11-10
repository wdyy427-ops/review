import sys,json,csv,collections,re
from pathlib import Path
from config import ROOT,LABELS,STANDARDS,FIELD_NAMES,as_codes,code_labels,SOURCE_URLS
def load(n):return json.loads((ROOT/'results'/f'{n}.json').read_text(encoding='utf-8'))
def save(n,x):(ROOT/'results'/f'{n}.json').write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def csvout(n,x):
    if not x:return
    with (ROOT/'results'/f'{n}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        keys=list(dict.fromkeys(k for r in x for k in r));w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        for r in x:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
papers=load('papers');evs=load('evaluations');chains=load('chains');audits=load('audits')
ep={e['eval_id']:e for e in evs};pp={p['paper_id']:p for p in papers};by_ev=collections.defaultdict(list)
for c in chains:by_ev[c['eval_id']].append(c)
measured_papers={c['paper_id'] for c in chains}
distributions=[]
def dist(unit,field,rows,value_fn,universe=None):
    count=collections.Counter(v for r in rows for v in set(value_fn(r)))
    for code in list(universe or [])+[k for k in count if not universe or k not in universe]:
        distributions.append({'unit':unit,'field':field,'code':str(code),'label':LABELS.get(field,{}).get(code,str(code)),'n':count.get(code,0),'denominator':len(rows),'proportion':count.get(code,0)/len(rows) if rows else None})
dist('论文','year',papers,lambda p:[p['year']])
for field in ['domain','stage','ai_role','ai_function','target_user']:
    dist('论文',field,papers,lambda p:as_codes(p.get(field+'_codes',[])),LABELS[field])
for field in ['dimension','indicator','tool_family']:
    getter=(lambda c,f=field:as_codes(c.get(f+'_codes',[]))) if field=='tool_family' else (lambda c,f=field:[c.get(f+'_code','NR')])
    dist('证据链',field,chains,getter,LABELS[field])
    dist('评价案例',field,evs,lambda e,f=field:as_codes(e.get(f+'_codes',[])),LABELS[field])
    papercodes={p['paper_id']:set() for p in papers}
    for c in chains:papercodes[c['paper_id']].update(getter(c))
    dist('论文',field,papers,lambda p:papercodes[p['paper_id']],LABELS[field])
for field in ['purpose','object','evaluator','source','task','constraint','setting','design']:
    getter=(lambda e,f=field:as_codes(e.get(f+'_codes',[]))) if field not in ['setting','design'] else (lambda e,f=field:[e.get(f+'_code','NR')])
    dist('评价案例',field,evs,getter,LABELS[field])
save('rq1_distributions',distributions);csvout('rq1_distributions',distributions)

cross=[]
for feature in ['domain','stage','ai_function','purpose','evaluator']:
    for code,label in LABELS[feature].items():
        subset=[e for e in evs if code in e.get(feature+'_codes',[])]
        for dim,dl in LABELS['dimension'].items():
            n=sum(dim in e.get('dimension_codes',[]) for e in subset)
            cross.append({'context_field':feature,'context_code':code,'context_label':label,'dimension':dim,'dimension_label':dl,'cases_n':n,'context_cases_n':len(subset),'proportion':n/len(subset) if subset else None,'papers_n':len({e['paper_id'] for e in subset if dim in e.get('dimension_codes',[])})})
save('rq1_cross',cross);csvout('rq1_cross',cross)

qdist=[]
for unit,rows in [('评价案例',evs),('证据链',chains)]:
    for std in STANDARDS:
        cnt=collections.Counter(r.get('audit_statuses',{}).get(std,'NR') for r in rows)
        for status in LABELS['audit_status']:
            qdist.append({'unit':unit,'standard':std,'standard_label':STANDARDS[std],'status':status,'status_label':LABELS['audit_status'][status],'n':cnt[status],'denominator':len(rows),'proportion':cnt[status]/len(rows) if rows else None})
save('rq2_distributions',qdist);csvout('rq2_distributions',qdist)

quality_sets=[]
for subset,label in [('all','全部实际感知证据'),('sensitivity','报告支持较充分（敏感性）'),('strict','主要规范性证据子集')]:
    selected=chains if subset=='all' else [c for c in chains if c.get(subset+'_eligible')]
    fullcases=[e for e in evs if by_ev[e['eval_id']] and (subset=='all' or all(c.get(subset+'_eligible') for c in by_ev[e['eval_id']]))]
    quality_sets.append({'subset':subset,'label':label,'chains_n':len(selected),'papers_with_eligible_chain':len({c['paper_id'] for c in selected}),'cases_with_eligible_chain':len({c['eval_id'] for c in selected}),'all_chains_eligible_cases':len(fullcases),'papers_with_whole_eligible_case':len({e['paper_id'] for e in fullcases})})
save('rq2_subsets',quality_sets);csvout('rq2_subsets',quality_sets)

fields_missing=[]
def absent(x):return x is None or x=='' or str(x).startswith(('NR','未报告','无法判断'))
for name in ['item_quote','construct_raw','instrument_raw','response_scoring','validity_evidence','reliability_evidence','result_quote']:
    nn=sum(absent(c.get(name)) for c in chains)
    fields_missing.append({'unit':'证据链','field':name,'missing_n':nn,'n':len(chains),'missing_proportion':nn/len(chains) if chains else None})
for name in ['sample_n','recruitment','procedure','analysis','actual_results','ethics','constraints_raw']:
    nn=sum(absent(e.get(name)) for e in evs)
    fields_missing.append({'unit':'评价案例','field':name,'missing_n':nn,'n':len(evs),'missing_proportion':nn/len(evs) if evs else None})
save('rq2_reporting',fields_missing);csvout('rq2_reporting',fields_missing)

# Observed applicability catalogue; not a claim that frequently used tools are validated.
catalog=[]
groups=collections.defaultdict(list)
for c in chains:
    for tool in as_codes(c.get('tool_family_codes',[])):
        groups[(c.get('dimension_code','NR'),c.get('indicator_code','NR'),tool)].append(c)
for (dim,ind,tool),rows in sorted(groups.items()):
    contexts={f:sorted({v for c in rows for v in as_codes(ep[c['eval_id']].get(f+'_codes',[]))}) for f in ['domain','stage','ai_function','purpose','evaluator','object']}
    names=sorted({c.get('instrument_raw','NR') for c in rows})
    catalog.append({'dimension_code':dim,'indicator_code':ind,'tool_family_code':tool,'dimension':LABELS['dimension'].get(dim,dim),'indicator':LABELS['indicator'].get(ind,ind),'tool_family':LABELS['tool_family'].get(tool,tool),'papers_n':len({c['paper_id'] for c in rows}),'cases_n':len({c['eval_id'] for c in rows}),'chains_n':len(rows),'strict_chains_n':sum(c['strict_eligible'] for c in rows),'sensitivity_chains_n':sum(c['sensitivity_eligible'] for c in rows),'contexts':contexts,'instruments':names,'chain_ids':[c['chain_id'] for c in rows],'paper_ids':sorted({c['paper_id'] for c in rows}),'recommendation_status':'可查询原研究；须核对目标情境与原工具，使用频次不代表适用性验证'})
save('rq4_catalog',catalog);csvout('rq4_catalog',catalog)

summary={'corpus_papers':len(papers),'papers_with_perceived_evidence':len(measured_papers),'papers_without_perceived_evidence':len(papers)-len(measured_papers),'evaluations':len(evs),'chains':len(chains),'pdf_pages':sum(p['pdf_pages'] for p in papers),'unmapped_indicator_chains':sum(c.get('indicator_code')=='UNMAPPED' for c in chains),'unmapped_domain_papers':sum('UNMAPPED' in p.get('domain_codes',[]) for p in papers),'quality_subsets':quality_sets,'sources':SOURCE_URLS}
save('research_summary',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
