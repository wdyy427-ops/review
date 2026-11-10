"""Paper-level 2x2 associations on first-pass codes; descriptive/exploratory only."""
import json,sys,csv,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'_deps'))
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests
from config import ROOT,LABELS
r=ROOT/'results';papers=json.loads((r/'legacy_papers.json').read_text(encoding='utf8'));cases=json.loads((r/'legacy_cases.json').read_text(encoding='utf8'))
pc=collections.defaultdict(lambda:collections.defaultdict(set))
for c in cases:
 for f in ['purpose','dimension','indicator']:
  pc[c['paper_id']][f].update(x for x in c[f+'_codes'] if x in LABELS[f])
out=[]
for feature in ['domain','stage','ai_function','purpose']:
 for fc,fl in LABELS[feature].items():
  x=[fc in (p[feature+'_codes'] if feature!='purpose' else pc[p['paper_id']]['purpose']) for p in papers]
  for dc,dl in LABELS['dimension'].items():
   y=[dc in pc[p['paper_id']]['dimension'] for p in papers]
   a=sum(i and j for i,j in zip(x,y));b=sum(i and not j for i,j in zip(x,y));c=sum(not i and j for i,j in zip(x,y));d=sum(not i and not j for i,j in zip(x,y))
   odds,pval=fisher_exact([[a,b],[c,d]])
   rd=a/(a+b)-c/(c+d) if (a+b)*(c+d) else None
   out.append({'feature':feature,'context_code':fc,'context':fl,'dimension_code':dc,'dimension':dl,'both_papers':a,'context_only':b,'dimension_only':c,'neither':d,'risk_difference':rd,'odds_ratio':None if odds==float('inf') else odds,'p_fisher':pval})
_,q,_,_=multipletests([x['p_fisher'] for x in out],method='fdr_bh')
for item,val in zip(out,q):item['q_BH_all_100_tests']=float(val)
(r/'legacy_exploratory_associations.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
with (r/'legacy_exploratory_associations.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
print(json.dumps({'tests':len(out),'q_under_0.05':[x for x in out if x['q_BH_all_100_tests']<.05]},ensure_ascii=False,indent=2))
