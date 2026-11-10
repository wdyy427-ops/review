import json,collections
from pathlib import Path
from config import ROOT
auto=json.loads((ROOT/'autocode'/'all_papers.json').read_text(encoding='utf8'))
gold=[]
for f in sorted((ROOT/'agents').glob('paper_*.json')):
 d=json.loads(f.read_text(encoding='utf8'));inds={c['indicator_code'] for e in d.get('evaluations',[]) for c in e.get('chains',[]) if c.get('indicator_code') not in ['NR','NA','UNMAPPED']}
 gold.append({'paper_id':d['paper_id'],'domain':set(d.get('domain_codes',[])),'stage':set(d.get('stage_codes',[])),'ai_function':set(d.get('ai_function_codes',[])),'indicator':inds,'human':bool(d.get('evaluations'))})
def scores(field):
 tp=fp=fn=0;rows=[]
 for g in gold:
  a=next(x for x in auto if x['paper_id']==g['paper_id']);p=set(a[field+'_codes']) if field!='indicator' else {c['indicator_code'] for c in a['chains'] if c['indicator_code'] not in ['NR','NA','UNMAPPED']};q=g[field]
  tp+=len(p&q);fp+=len(p-q);fn+=len(q-p);rows.append((g['paper_id'],sorted(q),sorted(p)))
 return {'precision':tp/(tp+fp) if tp+fp else 0,'recall':tp/(tp+fn) if tp+fn else 0,'tp':tp,'fp':fp,'fn':fn,'rows':rows}
out={f:scores(f) for f in ['domain','stage','ai_function','indicator']}
print(json.dumps(out,ensure_ascii=False,indent=2))
