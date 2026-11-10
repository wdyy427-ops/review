from pathlib import Path
import json, collections, re, sys, hashlib
import openpyxl
from pypdf import PdfReader

ROOT=Path(r'C:\Users\Administrator\Desktop\review')
OUT=ROOT/'outputs'/'rq_review_20261024'
for d in ['extracted','agents','results','figures','scripts','previews']:
    (OUT/d).mkdir(parents=True,exist_ok=True)
w=openpyxl.load_workbook(ROOT/'最终'/'125篇全文重新编码_18维度_三工作表.xlsx',read_only=True,data_only=True)
raw={s.title:[list(row) for row in s.iter_rows(values_only=True)] for s in w.worksheets}
(OUT/'extracted'/'previous_workbook.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
dist={}
for name,rows in raw.items():
    dist[name]={str(h):dict(collections.Counter(str(r[i]) for r in rows[1:] if r[i] is not None)) for i,h in enumerate(rows[0]) if name!='General background' and i not in [0,1,len(rows[0])-1,len(rows[0])-2]}
(OUT/'extracted'/'previous_categories.json').write_text(json.dumps(dist,ensure_ascii=False,indent=2),encoding='utf-8')
general={str(r[0]):dict(zip(raw['General background'][0],r)) for r in raw['General background'][1:]}
specific={str(r[0]):dict(zip(raw['Specific background'][0],r)) for r in raw['Specific background'][1:]}
chains=collections.defaultdict(list)
for i,r in enumerate(raw['Perceived effect'][1:],1):
    x=dict(zip(raw['Perceived effect'][0],r)); x['_legacy_row']=i+1
    chains[str(r[0])].append(x)
manifest=[]
pdfdir=ROOT/'最终'/'全文-重新排序 - 副本'
for i in range(1,126):
    p=pdfdir/f'{i}.pdf'
    cached=OUT/'extracted'/f'{i:03d}.json'
    try: pages=json.loads(cached.read_text(encoding='utf-8'))['pages']
    except Exception:
        reader=PdfReader(str(p))
        pages=[]
        for n,pg in enumerate(reader.pages,1):
            try: t=(pg.extract_text() or '').encode('utf-8',errors='replace').decode('utf-8')
            except Exception as e: t='[EXTRACTION ERROR] '+str(e)
            pages.append({'page':n,'text':t})
    data={'paper_id':i,'pdf_path':str(p),'metadata':general.get(str(i),{}),'previous_context':specific.get(str(i),{}),'previous_chains':chains.get(str(i),[]),'pages':pages}
    (OUT/'extracted'/f'{i:03d}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    text='\n\n'.join(f'=== PDF PAGE {x["page"]} ===\n{x["text"]}' for x in pages)
    (OUT/'extracted'/f'{i:03d}.txt').write_text(text,encoding='utf-8')
    manifest.append({'paper_id':i,'pages':len(pages),'chars':len(text),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'title':general.get(str(i),{}).get('1.论文题目'),'pdf':str(p)})
    print(i,len(pages),len(text),flush=True)
(OUT/'extracted'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',len(manifest),sum(x['pages'] for x in manifest))
