import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n): return json.loads((ROOT/'extracted'/f'{n:03}.json').read_text(encoding='utf-8-sig'))
def read(n,start=1,end=999):
 d=load(n)
 for p in d['pages']:
  if start<=p['page']<=end: print(f'\n[PAGE {p["page"]}]\n{p["text"]}')
def base(n,domains,stages,functions,roles,users,context,ev):
 d=load(n)
 return dict(paper_id=n,title_match=True,reviewed_pages=[],scope_note='全文人工式AI辅助审阅；不是独立人工双人编码。',domain_codes=domains,stage_codes=stages,ai_function_codes=functions,ai_role_codes=roles,target_user_codes=users,context_summary=context,context_evidence=ev,evaluations=[],excluded_legacy_rows=[],added_evidence_notes='',category_gaps=[])
def q(page,quote): return dict(page=page,quote=quote)
def e(field,page,quote): return dict(field=field,page=page,quote=quote)
def aud(s,status,facts,reason,pages,quote): return dict(standard=s,status=status,facts=facts,reason=reason,pages=pages,quote=quote)
def evaluation(id,legacy,purpose,objects,raters,sources,setting,design,stage,n,sample,recruit,task,comp,procedure,analysis,results,limits,ethics,evidence,audit):
 return dict(eval_id=id,legacy_eval_ids=legacy,purpose_codes=purpose,object_codes=objects,evaluator_codes=raters,source_codes=sources,setting_code=setting,design_code=design,evaluation_stage_codes=stage,sample_n=n,sample_description=sample,recruitment=recruit,task=task,comparator=comp,procedure=procedure,analysis=analysis,actual_results=results,limitations=limits,ethics=ethics,evidence=evidence,audit=audit,chains=[])
def chain(rows,claim,summary,ctype,construct,indicator,item,dim,code,instrument,tools,origin,adapt,scoring,validity,reliability,result,direction,pages,overrides=None):
 return dict(legacy_rows=rows,claim_quote=claim,claim_summary=summary,claim_type=ctype,construct_raw=construct,indicator_raw=indicator,item_quote=item,dimension_code=dim,indicator_code=code,instrument_raw=instrument,tool_family_codes=tools,tool_origin_code=origin,adaptation=adapt,response_scoring=scoring,validity_evidence=validity,reliability_evidence=reliability,result_quote=result,effect_direction=direction,pages=pages,audit_overrides=overrides or [])
def save(d):
 old={r['_legacy_row'] for r in load(d['paper_id'])['previous_chains']}
 used=[r for ev in d['evaluations'] for c in ev['chains'] for r in c['legacy_rows']]+[r['legacy_row'] for r in d['excluded_legacy_rows']]
 assert set(used)==old,(old-set(used),set(used)-old)
 assert len(used)==len(set(used)), 'duplicate legacy row'
 for ev in d['evaluations']:
  assert {a['standard'] for a in ev['audit']}=={'U5','A2','A3','A4','A6','A7','E1'}
 path=ROOT/'agents'/f'paper_{d["paper_id"]:03}.json'
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(path, 'evals',len(d['evaluations']),'chains',sum(len(e['chains']) for e in d['evaluations']))
if __name__=='__main__':
 import sys
 if len(sys.argv)>2 and sys.argv[2]=='meta':
  d=load(int(sys.argv[1])); print(json.dumps({k:v for k,v in d.items() if k!='pages'},ensure_ascii=False,indent=2)); print('PAGES',len(d['pages']))
 else: read(int(sys.argv[1]),int(sys.argv[2]) if len(sys.argv)>2 else 1,int(sys.argv[3]) if len(sys.argv)>3 else 999)
