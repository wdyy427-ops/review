"""Build a local, evidence-labelled research prototype from audited cases."""
import json,html
from pathlib import Path
from config import ROOT,LABELS
catalog=json.loads((ROOT/'results'/'rq4_catalog.json').read_text(encoding='utf8'))
chains=json.loads((ROOT/'results'/'chains.json').read_text(encoding='utf8'))
papers={p['paper_id']:p for p in json.loads((ROOT/'results'/'papers.json').read_text(encoding='utf8'))}
site=ROOT/'site'/'dist';site.mkdir(parents=True,exist_ok=True)
out=[]
for x in catalog:
    examples=[]
    for c in chains:
        if c['chain_id'] not in x['chain_ids']:continue
        p=papers[c['paper_id']]
        examples.append({'paper_id':c['paper_id'],'title':p['title'],'year':p['year'],'doi':p['doi'],
           'pages':c.get('pages',[]),'indicator_raw':c.get('indicator_raw',''),'instrument_raw':c.get('instrument_raw',''),
           'response_scoring':c.get('response_scoring',''),'result_quote':c.get('result_quote',''),
           'audit':c.get('audit_statuses',{}),'sensitivity':c.get('sensitivity_eligible',0)})
    out.append({**x,'examples':examples})
data={'catalog':out,'labels':{k:LABELS[k] for k in ['domain','stage','ai_function','dimension','indicator','tool_family']},
      'coverage':{'papers_total':125,'fulltext_reviewed':len(papers),'strict_chains':sum(c.get('strict_eligible',0) for c in chains)}}
(site/'data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
(site/'data.js').write_text('window.EVIDENCE_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';',encoding='utf8')
page_file=site/'index.html'
page=page_file.read_text(encoding='utf8')
page=page.replace('<script>\nlet db;', '<script src="data.js"></script><script>\nlet db;')
page=page.replace("fetch('data.json').then(r=>r.json()).then(d=>{", 'Promise.resolve(window.EVIDENCE_DATA).then(d=>{')
page_file.write_text(page,encoding='utf8')
print(json.dumps({'groups':len(catalog),'examples':sum(len(x['examples']) for x in out),'site':str(site)},ensure_ascii=False))
