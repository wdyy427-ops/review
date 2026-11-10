import json,csv
from config import ROOT
src=ROOT/'extracted';dst=ROOT/'results'/'remaining_review_queue.csv'
rows=[]
for i in range(1,126):
 if (ROOT/'agents'/f'paper_{i:03d}.json').exists():continue
 d=json.loads((src/f'{i:03d}.json').read_text(encoding='utf8'))
 rows.append({'paper_id':i,'title':d['metadata'].get('1.论文题目'),'pages':len(d['pages']),'legacy_rows':len(d['previous_chains']),
 'pdf':d['pdf_path'],'status':'待全文复核','priority_hint':'先核查短论文与旧表无感知行论文；不代表可略过其余正文'})
rows.sort(key=lambda r:(r['pages'],r['paper_id']))
with dst.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(len(rows),sum(x['pages'] for x in rows),str(dst))
