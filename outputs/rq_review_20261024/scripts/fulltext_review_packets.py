"""Build paper review packets from PDF text only.

No fields from the previous workbook are read. The packets preserve page provenance and
are an aid to full-text review, not final coding.
"""
import json,re
from pathlib import Path
from config import ROOT

SRC=ROOT/'extracted'; OUT=ROOT/'review_packets';OUT.mkdir(exist_ok=True)
terms={
 'study':r'\b(user stud(?:y|ies)|evaluation|experiment|survey|questionnaire|interview|focus group|participant|rater|judge|expert review|usability test)\b',
 'measure':r'\b(likert|scale|instrument|measure(?:d|ment)?|item|rating|score|semantic differential|nasa.?tlx|sus\b|creativity support index|attrakdiff|ueq\b)\b',
 'quality':r'\b(cronbach|reliab|validit|inter.?rater|kappa|kendall|icc\b|test.?retest|triangulat|member check|thematic analysis)\b',
 'result':r'\b(results?|findings?|p\s*[<=>]|significant|mean\b|standard deviation|effect size|confidence interval|anova|t.?test|wilcoxon|mann.?whitney)\b',
 'ethics':r'\b(ethic|consent|institutional review|irb\b|compensation|recruited)\b',
}
def clean(t):return re.sub(r'\s+',' ',t or '').strip()
stats=[]
for i in range(1,126):
 d=json.loads((SRC/f'{i:03d}.json').read_text(encoding='utf8'))
 scored=[]
 for p in d['pages']:
  t=p['text'];hits={k:len(re.findall(rx,t,re.I)) for k,rx in terms.items()}
  score=4*hits['study']+3*hits['measure']+2*hits['quality']+2*hits['result']+hits['ethics']
  if score:scored.append((score,p['page'],hits,t))
 seed={pg for _,pg,_,_ in sorted(scored,reverse=True)[:10]}
 # Include adjacent pages so method/result sections remain coherent.
 keep=sorted({q for pg in seed for q in range(max(1,pg-1),min(len(d['pages']),pg+1)+1)})
 packet={'paper_id':i,'pdf_path':d['pdf_path'],'metadata':d['metadata'],'total_pages':len(d['pages']),
         'candidate_pages':keep,'page_scores':[{'page':pg,'score':s,'hits':h} for s,pg,h,_ in sorted(scored,reverse=True)],
         'pages':[p for p in d['pages'] if p['page'] in keep],
         'notice':'全文复核辅助包；候选页由关键词定位，最终编码必须回看完整PDF与必要的非候选页。'}
 (OUT/f'{i:03d}.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf8')
 stats.append({'paper_id':i,'total_pages':len(d['pages']),'candidate_pages':len(keep),'top_score':max([x[0] for x in scored],default=0),'likely_human_evaluation':any(x[2]['study'] and x[2]['measure'] for x in scored)})
(OUT/'manifest.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'papers':len(stats),'total_pages':sum(x['total_pages'] for x in stats),'candidate_pages':sum(x['candidate_pages'] for x in stats),'likely_human_evaluation':sum(x['likely_human_evaluation'] for x in stats)},ensure_ascii=False))
