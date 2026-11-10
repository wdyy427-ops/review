"""Transparent descriptive baseline from the supplied first-pass workbook.

These rows are NOT a substitute for the separately audited PDF reviews.
"""
import json,csv,collections
from pathlib import Path
from config import ROOT,LABELS

SRC=ROOT/'extracted'; OUT=ROOT/'results'
data=[json.loads((SRC/f'{i:03d}.json').read_text(encoding='utf-8')) for i in range(1,126)]
def codes(field,value):
    rev={v:k for k,v in LABELS[field].items()}
    return [rev.get(v.strip(),'UNMAPPED') for v in str(value or '').split('；') if v.strip()] or ['NR']
rows=[];papers=[];cases={}
for p in data:
    pid=p['paper_id'];m=p['metadata'];ctx=p['previous_context']
    pr={'paper_id':pid,'year':m.get('1.年份'),'title':m.get('1.论文题目'),'doi':m.get('1.DOI'),
        'domain_codes':codes('domain',ctx.get('2.设计领域（ICoD）')),
        'stage_codes':codes('stage',ctx.get('3.设计阶段／任务（ICoD）')),
        'ai_function_codes':codes('ai_function',ctx.get('6.AI功能')),
        'review_status':'PDF全文复核完成' if (ROOT/'agents'/f'paper_{pid:03d}.json').exists() else '仅旧表首轮编码；待全文复核',
        'pdf_pages':len(p['pages'])}
    papers.append(pr)
    for c in p['previous_chains']:
        eid=c.get('评价记录编号') or f'{pid}-未编号'
        key=(pid,eid)
        if key not in cases:cases[key]={'paper_id':pid,'legacy_eval_id':eid,'year':pr['year'],'domain_codes':pr['domain_codes'],'stage_codes':pr['stage_codes'],'ai_function_codes':pr['ai_function_codes'],'purpose_codes':codes('purpose',c.get('18.评价作用')),'dimension_codes':[],'indicator_codes':[],'row_count':0,'review_status':pr['review_status']}
        dim=codes('dimension',c.get('13.评价维度（一级）'))[0]
        ind=codes('indicator',c.get('14.主观指标类型（二级）'))[0]
        z={'paper_id':pid,'legacy_row':c['_legacy_row'],'legacy_eval_id':eid,'year':pr['year'],
          'claim_summary_previous':c.get('12.效果主张（中文归纳）'),'dimension_code_previous':dim,'indicator_code_previous':ind,
          'indicator_raw_previous':c.get('15.原文指标名称（三级；中文译述）'),'instrument_previous':c.get('16.测量工具（方法及实际形式）'),
          'result_direction_previous':c.get('17.效果方向'),'source_locator_previous':c.get('原文定位'),
          'source_excerpt_previous':c.get('原文证据摘录（供复核）'),
          'review_status':pr['review_status'],'coding_status_previous':c.get('编码状态'),
          'notice':'旧表为检索索引；未经全文复核的行不能进入规范性审查或推荐训练。'}
        rows.append(z)
        ca=cases[key];ca['row_count']+=1
        for f,val in [('dimension_codes',dim),('indicator_codes',ind)]:
            if val not in ca[f]:ca[f].append(val)

def write(name,rs):
    (OUT/f'{name}.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2),encoding='utf-8')
    if not rs:return
    ks=list(dict.fromkeys(k for r in rs for k in r))
    with (OUT/f'{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=ks);w.writeheader()
        for r in rs:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in r.items()})
write('legacy_papers',papers);write('legacy_cases',list(cases.values()));write('legacy_rows',rows)
print(json.dumps({'papers':len(papers),'cases':len(cases),'rows':len(rows),'reviewed_papers':sum(p['review_status']=='PDF全文复核完成' for p in papers)},ensure_ascii=False))
