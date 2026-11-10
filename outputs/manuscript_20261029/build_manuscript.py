from pathlib import Path
import json, re, html
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

BASE = Path(__file__).resolve().parent
TITLE = 'Subjective Evaluation of Perceived Effects in AI-Assisted Design Workflows: A Systematic Literature Review'
OUT = BASE / 'Subjective_Evaluation_Manuscript.docx'
refs = {r['key']: r for r in json.loads((BASE/'references_verified.json').read_text(encoding='utf-8'))}
tables = json.loads((BASE/'manuscript_tables.json').read_text(encoding='utf-8'))
figs = {f['id']: f for f in json.loads((BASE/'figure_manifest.json').read_text(encoding='utf-8'))}
context_figures = json.loads((BASE/'context_heatmap_manifest.json').read_text(encoding='utf-8'))
figs.update({f['id']: f for f in context_figures})
tables['audit']['note']='S: sufficient support under the operational coding; P: partial support; C: explicit concern; NR: not reported or indeterminate; NA: not applicable. Every row totals 514. These codes concern the retained evidence record and do not certify the underlying study.'
tables['audit']['caption']='Criterion-level reporting-support classifications across 514 candidate evidence records.'
tables['screening']['note']='The 585 records advancing to further assessment comprise 82 provisional includes and 503 unclear records. The 55 additional duplicates comprise 54 title duplicates and one DOI duplicate.'
tables['context']['note']='Multiple labels are permitted. G4 remains descriptive; predictive analyses use the original identity-based G5 categories.'
tables['indicators']['note']='Counts use 454 indicator-mapped records; six additional records map only to a dimension. Indicator codes are distinct from JCSEE criterion codes.'
for row in tables['context']['rows']:
 if row[0].startswith('G4'):row[2]='Descriptive category; omitted from prediction.'
 elif row[0].startswith('G5'):
  row[1]='Professional designer/domain expert; student/novice; end user; public/crowdworker; client/stakeholder; researcher.'
  row[2]='Original identity categories used for prediction.'
 else:row[2]='Contextual predictor; multiple labels permitted.' if row[0][:2]!='G6' else 'Contextual predictor; distinct from the evaluator.'
figs['fig03_temporal_composition']['caption']='Annual composition of perceived-effect dimensions (a) and tools (b), using Crossref-harmonized publication years. Bars sum to 100% within each year; labels above bars give record or instance denominators. The 2026 period ends September 25. Small early-year samples limit comparison. Alternative year classifications are provided in the supplementary data.'
tables['selectionguide']['rows'] = [
 ['Establish purpose', 'Specify whether judgments elicit criteria, calibrate a model, guide revision, or support comparison.', 'Criteria or calibration labels do not alone demonstrate downstream benefit.'],
 ['Identify perspectives', 'State the evaluator, target user, evaluation object, and task conditions.', 'Artifact ratings do not establish the designer’s own experience.'],
 ['Select perceived effects', 'Justify coverage across relevant outcome, process, designer, interaction, and contextual dimensions.', 'Frequency in the corpus is not a normative priority.'],
 ['Specify indicators', 'Retain construct wording, intended interpretation, and relation to the selected perceived effects.', 'Shared names need not denote equivalent operationalizations.'],
 ['Choose tools', 'Match the indicator to instrument content, elicitation format, population, and analysis.', 'Named scales and repeated use do not guarantee validity in a new context.'],
 ['Document and review', 'Provide items or prompts, scoring or analytic procedures, evidence sources, and unresolved assumptions.', 'A recommendation is a starting point for a justified evaluation plan.']]
tables['selectionguide']['note'] = 'Guidance is derived from the evidence architecture and descriptive and predictive analyses; its effectiveness has not been established in a prospective evaluation.'

parts = [(BASE/f'{i:02d}_{name}.txt').read_text(encoding='utf-8') for i,name in enumerate(['abstract','introduction','methods','results','guidelines_discussion'])]
body = '\n\n'.join(parts)
body = body.replace('# '+TITLE+'\n\n','')
keys = list(dict.fromkeys(re.findall(r'\[cite:([^\]]+)\]', body)))
assert not(set(keys)-set(refs)), set(keys)-set(refs)
numbers = {k: i+1 for i,k in enumerate(keys)}
body = re.sub(r'\[cite:([^\]]+)\]',lambda m:f'[{numbers[m[1]]}]',body)
main, appendix = body.split('## Appendix A',1)
appendix = '## Appendix A'+appendix

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.left_margin=sec.right_margin=Inches(1)
sec.top_margin=sec.bottom_margin=Inches(.82)
sec.header_distance=sec.footer_distance=Inches(.35)
styles=doc.styles
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption','List Number','List Bullet']:
 s=styles[name];s.font.name='Times New Roman';s.font.color.rgb=RGBColor(0,0,0)
 s.element.rPr.rFonts.set(qn('w:eastAsia'),'SimSun')
normal=styles['Normal'];normal.font.size=Pt(11)
normal.paragraph_format.line_spacing=1.13
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
styles['Title'].font.size=Pt(19);styles['Title'].font.bold=True
styles['Title'].paragraph_format.space_after=Pt(14)
for name,size,before,after in [('Heading 1',13,14,7),('Heading 2',11.5,10,5),('Heading 3',11,8,4)]:
 s=styles[name];s.font.size=Pt(size);s.font.bold=True
 s.paragraph_format.space_before=Pt(before);s.paragraph_format.space_after=Pt(after)
 s.paragraph_format.keep_with_next=True
styles['Caption'].font.size=Pt(9.5);styles['Caption'].font.italic=False
styles['Caption'].font.bold=False
styles['Caption'].paragraph_format.space_after=Pt(8)
styles['Caption'].paragraph_format.line_spacing=1.05

header=sec.header.paragraphs[0]
header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=header.add_run('Subjective Evaluation of Perceived Effects in AI-Assisted Design Workflows')
r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string('555555')
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
doc.core_properties.title=TITLE
doc.core_properties.subject='Systematic literature review manuscript'
doc.core_properties.author=''
doc.add_paragraph(TITLE,'Title')

def add_link(p,text,url):
 hyperlink=OxmlElement('w:hyperlink');hyperlink.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
 run=OxmlElement('w:r');pr=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'1F4E79');pr.append(color)
 sz=OxmlElement('w:sz');sz.set(qn('w:val'),'19');pr.append(sz)
 run.append(pr);t=OxmlElement('w:t');t.text=text;run.append(t);hyperlink.append(run);p._p.append(hyperlink)

table_count=0;figure_count=0;appendix_figure_count=0
def make_table(key):
 global table_count
 v=tables[key]
 table_count+=1
 number='A1' if key=='indicators' else str(table_count)
 caption=doc.add_paragraph(f'Table {number}. {v["caption"]}','Caption')
 caption.paragraph_format.keep_with_next=True
 table=doc.add_table(rows=1,cols=len(v['headers']))
 table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
 for col,w in zip(table.columns,v['widths']):col.width=Inches(w)
 for i,(cell,txt,w) in enumerate(zip(table.rows[0].cells,v['headers'],v['widths'])):
  cell.width=Inches(w);cell.text=txt
  shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F1F3F5');cell._tc.get_or_add_tcPr().append(shade)
  for r in cell.paragraphs[0].runs:r.bold=True
 repeat=OxmlElement('w:tblHeader');table.rows[0]._tr.get_or_add_trPr().append(repeat)
 for vals in v['rows']:
  row=table.add_row()
  for cell,txt,w in zip(row.cells,vals,v['widths']):cell.width=Inches(w);cell.text=str(txt)
 for ri,row in enumerate(table.rows):
  pr=row._tr.get_or_add_trPr();ns=OxmlElement('w:cantSplit');pr.append(ns)
  for ci,cell in enumerate(row.cells):
   cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   cp=cell._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
   padding='30' if key in ['indicators','context'] else '65'
   for side,val in [('top',padding),('bottom',padding),('left','70'),('right','70')]:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),val);el.set(qn('w:type'),'dxa');m.append(el)
   cp.append(m)
   borders=OxmlElement('w:tcBorders')
   if ri==0 or ri==len(table.rows)-1:
    b=OxmlElement('w:bottom');b.set(qn('w:val'),'single');b.set(qn('w:sz'),'5');b.set(qn('w:color'),'777777');borders.append(b)
   cp.append(borders)
   for p in cell.paragraphs:
    p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.05
    p.paragraph_format.keep_with_next=(ri==0 or (key in ['selectionguide','audit'] and ri<len(table.rows)-1))
    if (key in ['audit','indicators'] and ci>=(1 if key=='audit' else 2)) or (key=='models' and ci>=2) or (key=='screening' and ci==1):p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:r.font.size=Pt(9.25 if key=='models' else 9.5)
 if v.get('note'):
  p=doc.add_paragraph(v['note']);p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(9)
  for r in p.runs:r.font.size=Pt(9)
 else: doc.add_paragraph().paragraph_format.space_after=Pt(2)

def make_figure(key):
 global figure_count, appendix_figure_count
 f=figs[key]
 if f.get('appendix_label'):
  appendix_figure_count+=1
  label=f['appendix_label']
 else:
  figure_count+=1
  label=str(figure_count)
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.paragraph_format.space_before=Pt(6);p.paragraph_format.space_after=Pt(4);p.paragraph_format.keep_with_next=True
 width=min(6.5,6.5*f['aspect_ratio'])
 image_name=Path(f['files']['png'].replace('\\','/')).name
 p.add_run().add_picture(str(BASE/'figures'/image_name),width=Inches(width))
 cap=doc.add_paragraph(f'Figure {label}. {f["caption"]}','Caption')
 cap.paragraph_format.keep_together=True

def parse(text):
 for block in re.split(r'\n\s*\n',text.strip()):
  block=block.strip()
  if not block:continue
  if block.startswith('[FIGURE:'):make_figure(block[8:-1]);continue
  if block.startswith('[TABLE:'):make_table(block[7:-1]);continue
  if block.startswith('#### '):doc.add_paragraph(block[5:],'Heading 3');continue
  if block.startswith('### '):doc.add_paragraph(block[4:],'Heading 2');continue
  if block.startswith('## '):doc.add_paragraph(block[3:],'Heading 1');continue
  if re.match(r'^\d+\. ',block):
   p=doc.add_paragraph(block);p.paragraph_format.left_indent=Inches(.17);p.paragraph_format.first_line_indent=Inches(-.17)
  else:p=doc.add_paragraph(block.replace('\n',' '))
  if block.startswith('Keywords:'):
   for r in p.runs:r.font.size=Pt(10)

parse(main)
doc.add_paragraph('References','Heading 1')
for k in keys:
 r=refs[k]
 authors=', '.join(r['authors'][:-1])+(' and ' if len(r['authors'])>1 else '')+r['authors'][-1]
 title=r['title'].rstrip(' .')
 if k=='patton2008':title+=' (4th ed.)'
 elif k=='yarbrough2011':title+=' (3rd ed.)'
 venue=r.get('venue','').rstrip(' .,')
 citation=f'[{numbers[k]}] {authors}. {r["year"]}. {title.rstrip(" .")}. {venue}'
 if r.get('volume'):citation+=f' {r["volume"]}'
 if r.get('issue'):citation+=f'({r["issue"]})'
 if r.get('article_number'):citation+=f', Article {r["article_number"]}'
 if r.get('pages') and r.get('pages')!=r.get('article_number'):citation+=f', {r["pages"]}'
 citation=citation.rstrip(' .')+'. '
 p=doc.add_paragraph(citation);p.paragraph_format.left_indent=Inches(.28);p.paragraph_format.first_line_indent=Inches(-.28)
 p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1.05
 for rr in p.runs:rr.font.size=Pt(9.5)
 if r.get('url'):add_link(p,r['url'],r['url'])
doc.add_page_break()
parse(appendix)
doc.save(OUT)

bib=[]
for k in keys:
 r=refs[k];fields={'author':' and '.join(r['authors']),'title':'{'+r['title']+'}','year':str(r['year']),'journal':r.get('venue',''),'volume':r.get('volume',''),'number':r.get('issue',''),'pages':r.get('pages',''),'doi':r.get('doi',''),'url':r.get('url','')}
 typ='article'
 if k in ['patton2008','yarbrough2011']:
  typ='book';fields['publisher']=fields.pop('journal')
 elif k=='iso2019':
  typ='misc';fields['howpublished']=fields.pop('journal')
 elif k=='hart1988':
  typ='incollection';fields['booktitle']=fields.pop('journal')
 bib.append('@'+typ+'{'+k+',\n'+',\n'.join('  '+n+' = {'+str(v).replace('&','\\&')+'}' for n,v in fields.items() if v)+'\n}')
(BASE/'references.bib').write_text('\n\n'.join(bib),encoding='utf-8')
(BASE/'manuscript_full_text.txt').write_text(TITLE+'\n\n'+body,encoding='utf-8')
qa={'title':TITLE,'words_excluding_tables_and_references':len(re.findall(r"\b[\w’'-]+\b",body)),'references':len(keys),'figures':figure_count,'appendix_figures':appendix_figure_count,'tables':table_count,'unresolved_citations':re.findall(r'\[cite:[^\]]+\]',body),'figure_count_expected':7,'output':OUT.name}
(BASE/'manuscript_build_report.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print(json.dumps(qa,indent=2))
