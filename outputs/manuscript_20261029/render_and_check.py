from pathlib import Path
import json, re
import pypdfium2 as pdfium
import pdfplumber
from PIL import Image, ImageOps, ImageDraw
BASE=Path(__file__).resolve().parent
OUT=BASE/'qa_render';OUT.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(BASE/'Subjective_Evaluation_Manuscript.pdf'))
for i,p in enumerate(pdf):
 im=p.render(scale=1.5).to_pil();im.save(OUT/f'page-{i+1:02d}.png');p.close()
pdf.close()
report=[]
with pdfplumber.open(BASE/'Subjective_Evaluation_Manuscript.pdf') as p:
 for i,page in enumerate(p.pages):
  txt=page.extract_text() or ''
  words=page.extract_words()
  report.append({'page':i+1,'words':len(words),'chars':len(txt),'images':len(page.images),'xmin':min([w['x0'] for w in words],default=None),'xmax':max([w['x1'] for w in words],default=None),'text':txt})
for start in range(0,len(report),10):
 canvas=Image.new('RGB',(5*310,2*430),'#e4e7eb');d=ImageDraw.Draw(canvas)
 for i in range(start,min(start+10,len(report))):
  im=Image.open(OUT/f'page-{i+1:02d}.png');im.thumbnail((300,400))
  x=(i-start)%5*310+5;y=(i-start)//5*430+22
  canvas.paste(im,(x,y));d.text((x,y-17),f'Page {i+1}',fill='black')
 canvas.save(OUT/f'contact-{start+1:02d}-{min(start+10,len(report)):02d}.png')
(OUT/'page_layout_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{k:v for k,v in x.items() if k!='text'} for x in report]))
