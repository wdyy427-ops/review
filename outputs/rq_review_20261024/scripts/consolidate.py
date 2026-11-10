import json,sys,re,csv,collections,argparse,unicodedata
from pathlib import Path
from config import ROOT,LABELS,STANDARDS,quality_gate,as_codes,code_labels

ap=argparse.ArgumentParser();ap.add_argument('--allow-partial',action='store_true');args=ap.parse_args()
def write_json(name,x): (ROOT/'results'/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def write_csv(name,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT/'results'/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
def norm(t):return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',str(t)).lower())
def verify_quote(q,pages,src):
    if not q or str(q).startswith(('NR','NA','未报告')):return 'not_quoted'
    pieces=[p for p in re.split(r'[…;；|]|\.\.\.',q) if len(norm(p))>=15]
    texts=' '.join(x['text'] for x in src['pages'] if x['page'] in pages)
    nt=norm(texts)
    if pieces and all(norm(p) in nt for p in pieces):return 'exact_normalized'
    if norm(q) in norm(' '.join(x['text'] for x in src['pages'])):return 'found_other_page'
    return 'needs_check'
papers=[];evaluations=[];chains=[];audits=[];changes=[];quotes=[];issues=[]
files=sorted((ROOT/'agents').glob('paper_*.json'))
ids={int(p.stem.split('_')[1]) for p in files}
if not args.allow_partial and ids!=set(range(1,126)):raise RuntimeError(f'Missing papers: {sorted(set(range(1,126))-ids)}')
for f in files:
    d=json.loads(f.read_text(encoding='utf-8'));pid=d['paper_id'];src=json.loads((ROOT/'extracted'/f'{pid:03d}.json').read_text(encoding='utf-8'))
    if not d.get('title_match'):issues.append({'paper_id':pid,'type':'title_mismatch','detail':d.get('scope_note','')})
    md=src['metadata']; mkeys=list(md)
    pp={'paper_id':pid,'title':md.get('1.论文题目'),'doi':md.get('1.DOI'),'source':md.get('1.来源'),'publication_date':md.get('1.发表时间'),'year':md.get('1.年份'),'venue':md.get('1.期刊／会议'),'keywords':md.get('1.关键词'),'abstract':md.get('1.摘要（中文概述）'),'pdf_path':src['pdf_path'],'pdf_pages':len(src['pages']),'reviewed_pages':d.get('reviewed_pages',[]),'scope_note':d.get('scope_note',''),'context_summary':d.get('context_summary',''),'context_evidence':d.get('context_evidence',[]),'metadata_corrections':d.get('metadata_corrections',{})}
    for field in ['domain','stage','ai_function','ai_role','target_user']:
        pp[field+'_codes']=as_codes(d.get(field+'_codes',[]))
        for c in pp[field+'_codes']:
            if c not in LABELS[field] and c not in ['NR','NA','UNMAPPED']:issues.append({'paper_id':pid,'type':'invalid_code','detail':field+':'+str(c)})
    papers.append(pp)
    handled=collections.Counter()
    for ei,e in enumerate(d.get('evaluations',[]),1):
        eid=e.get('eval_id',f'{pid}-R{ei}')
        ev={k:v for k,v in e.items() if k not in ['chains','audit']}
        ev.update({'paper_id':pid,'eval_id':eid,'year':pp['year']})
        for field in ['domain','stage','ai_function','ai_role','target_user']:ev[field+'_codes']=pp[field+'_codes']
        for field in ['purpose','object','evaluator','source','task','constraint']:
            ev[field+'_codes']=as_codes(ev.get(field+'_codes',[]))
            for c in ev[field+'_codes']:
                if c not in LABELS[field] and c not in ['NR','NA','UNMAPPED']:issues.append({'paper_id':pid,'eval_id':eid,'type':'invalid_code','detail':field+':'+str(c)})
        base={a['standard']:a for a in e.get('audit',[])}
        for s in STANDARDS:
            if s not in base:issues.append({'paper_id':pid,'eval_id':eid,'type':'missing_audit','detail':s})
        ev['audit_statuses']={s:base.get(s,{}).get('status','NR') for s in STANDARDS}
        for s,a in base.items():
            ar=dict(a,paper_id=pid,eval_id=eid,chain_id='',unit='评价案例',audit_id=f'{eid}-{s}')
            audits.append(ar)
            quotes.append({'paper_id':pid,'eval_id':eid,'chain_id':'','field':s,'pages':a.get('pages',[]),'quote':a.get('quote',''),'verification':verify_quote(a.get('quote',''),a.get('pages',[]),src)})
        ce=[]
        for ci,c in enumerate(e.get('chains',[]),1):
            cid=f'{eid}-C{ci:02d}'
            ch={k:v for k,v in c.items() if k!='audit_overrides'}
            ch.update({'paper_id':pid,'eval_id':eid,'chain_id':cid})
            for r in c.get('legacy_rows',[]):handled[r]+=1
            for field in ['dimension','indicator','claim_type','tool_origin']:
                code=ch.get(field+'_code' if field!='claim_type' else field,'NR')
                if code not in LABELS[field] and code not in ['NR','NA','UNMAPPED']:issues.append({'paper_id':pid,'chain_id':cid,'type':'invalid_code','detail':field+':'+str(code)})
            dc=ch.get('dimension_code','NR');ic=ch.get('indicator_code','NR')
            if ic in LABELS['indicator'] and dc!=ic[0]:issues.append({'paper_id':pid,'chain_id':cid,'type':'hierarchy_mismatch','detail':str(dc)+' '+str(ic)})
            statuses=dict(ev['audit_statuses'])
            for a in c.get('audit_overrides',[]):
                statuses[a['standard']]=a['status']
                ar=dict(a,paper_id=pid,eval_id=eid,chain_id=cid,unit='证据链',audit_id=f'{cid}-{a["standard"]}')
                audits.append(ar)
            ch['audit_statuses']=statuses;ch['strict_eligible'],ch['sensitivity_eligible']=quality_gate(statuses)
            chains.append(ch);ce.append(ch)
            for field in ['claim_quote','item_quote','result_quote']:
                q=c.get(field,'');quotes.append({'paper_id':pid,'eval_id':eid,'chain_id':cid,'field':field,'pages':c.get('pages',[]),'quote':q,'verification':verify_quote(q,c.get('pages',[]),src)})
            for r in c.get('legacy_rows',[]):changes.append({'paper_id':pid,'legacy_row':r,'eval_id':eid,'chain_id':cid,'action':'保留并复核／合并','reason':c.get('recoding_note',''),'pages':c.get('pages',[])})
            if not c.get('legacy_rows'):changes.append({'paper_id':pid,'legacy_row':None,'eval_id':eid,'chain_id':cid,'action':'全文新增','reason':c.get('recoding_note',''),'pages':c.get('pages',[])})
        ev['chain_ids']=[x['chain_id'] for x in ce]
        ev['dimension_codes']=sorted({x.get('dimension_code','NR') for x in ce})
        ev['indicator_codes']=sorted({x.get('indicator_code','NR') for x in ce})
        ev['tool_family_codes']=sorted({v for x in ce for v in as_codes(x.get('tool_family_codes',[]))})
        # Cases may contain chains at different quality levels. Actual model subsets rebuild outcomes only from selected chains.
        ev['strict_eligible_any_chain']=int(any(x['strict_eligible'] for x in ce));ev['sensitivity_eligible_any_chain']=int(any(x['sensitivity_eligible'] for x in ce))
        evaluations.append(ev)
    for x in d.get('excluded_legacy_rows',[]):
        r=x['legacy_row'];handled[r]+=1
        changes.append({'paper_id':pid,'legacy_row':r,'eval_id':'','chain_id':'','action':'排除旧编码','reason':x.get('reason',''),'pages':x.get('pages',[])})
    expected={r['_legacy_row'] for r in src['previous_chains']}
    missing=expected-set(handled);extra=set(handled)-expected
    if missing:issues.append({'paper_id':pid,'type':'legacy_unhandled','detail':sorted(missing)})
    if extra:issues.append({'paper_id':pid,'type':'unknown_legacy_row','detail':sorted(extra)})
    for k,v in handled.items():
        if v>1:issues.append({'paper_id':pid,'type':'legacy_split','detail':f'{k}: {v} chains; verify intentional'})
    for gap in d.get('category_gaps',[]):issues.append({'paper_id':pid,'type':'category_gap','detail':gap})
    pp['evaluation_count']=len(d.get('evaluations',[]));pp['chain_count']=sum(len(e.get('chains',[])) for e in d.get('evaluations',[]))

for name,data in [('papers',papers),('evaluations',evaluations),('chains',chains),('audits',audits),('changes',changes),('quote_checks',quotes),('validation_issues',issues)]:
    write_json(name+'.json',data);write_csv(name+'.csv',data)
write_json('consolidation_summary.json',{'papers':len(papers),'evaluations':len(evaluations),'chains':len(chains),'audit_records':len(audits),'strict_chains':sum(c['strict_eligible'] for c in chains),'sensitivity_chains':sum(c['sensitivity_eligible'] for c in chains),'issues':len(issues),'missing_papers':sorted(set(range(1,126))-ids)})
print(json.dumps({'papers':len(papers),'evaluations':len(evaluations),'chains':len(chains),'issues':len(issues)},ensure_ascii=False))
