import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'rq2_jcsee30'

def rows(name):
    df=pd.read_csv(SRC/name,dtype=str,encoding='utf-8-sig').fillna('')
    return {"columns":df.columns.tolist(),"rows":df.values.tolist()}

def summary_rows(name):
    df=pd.read_csv(SRC/name,dtype=str,encoding='utf-8-sig').fillna('')
    order=[f'U{i}' for i in range(1,9)]+[f'F{i}' for i in range(1,5)]+[f'P{i}' for i in range(1,8)]+[f'A{i}' for i in range(1,9)]+[f'E{i}' for i in range(1,4)]
    df['_order']=df.standard.map({c:i for i,c in enumerate(order)})
    df=df.sort_values('_order').drop(columns='_order')
    return {"columns":df.columns.tolist(),"rows":df.values.tolist()}

summaries={k:pd.read_csv(SRC/f'standard_summary_{k}.csv') for k in ['practice','case','paper']}
fam=[]
labels={'U':'效用 U','F':'可行性 F','P':'适切性 P','A':'准确性 A','E':'评价责任 E'}
for code,label in labels.items():
    row={'family':label}
    for k,cn in [('practice','实践加权'),('case','案例等权'),('paper','论文等权')]:
        row[cn]=float(pd.to_numeric(summaries[k][summaries[k].standard.str.startswith(code)].support_pct,errors='coerce').mean())/100
    fam.append(row)

data={
    'metrics':{'source_papers':125,'candidate_records':490,'audited_practices':426,'audited_cases':108,'audited_papers':66,'excluded_records':64},
    'cluster_summary':[
        ['实践加权',426,float(summaries['practice'].support_pct.mean())/100],
        ['案例等权',108,float(summaries['case'].support_pct.mean())/100],
        ['论文等权',66,float(summaries['paper'].support_pct.mean())/100],
    ],
    'family_summary':fam,
    'standard_practice':summary_rows('standard_summary_practice.csv'),
    'standard_case':summary_rows('standard_summary_case.csv'),
    'standard_paper':summary_rows('standard_summary_paper.csv'),
    'codebook':rows('standard_codebook.csv'),
    'audit_wide':rows('practice_jcsee30_audit_wide.csv'),
    'audit_long':rows('practice_jcsee30_audit_long.csv'),
    'profiles':rows('practice_quality_profiles.csv'),
    'excluded':rows('excluded_incomplete_candidate_records.csv'),
}
(SRC/'rq2_workbook_data.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
print(SRC/'rq2_workbook_data.json')

if __name__=='__main__':
    pass
