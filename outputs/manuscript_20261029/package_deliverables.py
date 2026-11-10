from pathlib import Path
import shutil, json, hashlib, zipfile, importlib.metadata

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'Submission_Reference_Package';DEST.mkdir(exist_ok=True)
SOURCE=ROOT.parent/'rq_review_20261024'/'supplement_enhanced_v2'
files=['Subjective_Evaluation_Manuscript.docx','Subjective_Evaluation_Manuscript.pdf','manuscript_full_text.txt','00_abstract.txt','01_introduction.txt','02_methods.txt','03_results.txt','04_guidelines_discussion.txt','build_manuscript.py','export_docx.ps1','references.bib','references_verified.json','manuscript_tables.json','figure_manifest.json','manuscript_build_report.json','reviewed_corpus_catalogue.csv','publication_year_sensitivity.csv','Author_Verification_Notes.txt']
for name in files:shutil.copy2(ROOT/name,DEST/name)
for folder in ['figure_data','corrective_analysis']:
 for src in (ROOT/folder).rglob('*'):
  if src.is_file() and '__pycache__' not in src.parts:
   dst=DEST/src.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for src in (ROOT/'figures').glob('*'):
 if src.is_file() and not src.name.startswith('figS04_'):
  dst=DEST/'figures'/src.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(src,dst)
for folder in ['03_revised_results','04_RQ1','05_RQ2','06_RQ3','07_robustness_comparison','08_QC','reports']:
 for src in (SOURCE/folder).glob('*'):
  if src.is_file() and src.suffix in ['.csv','.json','.md','.txt']:
   dst=DEST/'source_data'/folder/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
audit_names=['audit_data.md','audit_facts.json','a2_a3_retained_evidence_triage.csv','search_screening_audit.csv','consensus_recalculated.csv','consensus_paired_decisions.csv','consensus_disagreements.csv','crossref_corpus_metadata.json','literature_notes.md','figure_qa.json']
for name in audit_names:
 if (ROOT/name).exists():
  dst=DEST/'verification'/name;dst.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/name,dst)
plot=(ROOT/'build_figures.py').read_text(encoding='utf-8').replace("BASE=ROOT.parent/'rq_review_20261024'/'supplement_enhanced_v2'","BASE=ROOT/'source_data'")
(DEST/'build_figures.py').write_text(plot,encoding='utf-8')
model_path=DEST/'corrective_analysis/run_corrective_analysis.py'
s=model_path.read_text(encoding='utf-8').replace("ROOT = Path(__file__).resolve().parents[3]","ROOT = Path(__file__).resolve().parents[1]").replace("DATA = ROOT / 'outputs/rq_review_20261024/supplement_enhanced_v2/03_revised_results'","DATA = ROOT / 'source_data/03_revised_results'")
model_path.write_text(s,encoding='utf-8')
readme='''论文范本与研究材料包

Subjective Evaluation of Perceived Effects in AI-Assisted Design Workflows: A Systematic Literature Review

主要文件
Subjective_Evaluation_Manuscript.docx：可编辑的完整英文论文范本。
Subjective_Evaluation_Manuscript.pdf：已核对版式的阅读版本。
Author_Verification_Notes.txt：独立于论文正文的作者核查说明。本文是依据现有材料完成的写作参考，并不代表其中所有研究判断已获得重新人工验证。

论文内容
摘要；Introduction；Conceptual Background and Related Work；Review Method；RQ1评价证据分布；RQ2报告支持；RQ3情境关联与预测分析；RQ4评价建议与渐进式推荐器；Discussion；Limitations and Future Work；Conclusion；Data and Materials Availability；28篇引用文献；3个附录。共7幅主图和7张表（含附录A1）。

图件
figures/包含7幅主图与3幅补充图，均提供SVG、矢量PDF和320dpi PNG。figS01为完整指标分布，figS02为补充材料扩充敏感性，figS03为条件预测贡献。figure_data/保留绘图源数据。图形使用一致的色彩、字体、面板标记和白色背景。

证据与分析
reviewed_corpus_catalogue.csv：125篇文献与DOI、原编码年份、筛选年份、Crossref日期对照。
source_data/：保留原始研究结果的副本，不应把旧模型输出与正文新增模型结果混用。
corrective_analysis/：正文使用的固定模型、按论文分组的重复验证结果及可复现脚本。
verification/：筛选、一致性、文献元数据及评价标签核查资料；不属于论文正文。

重新生成
Python环境依赖记录在requirements.txt。运行python build_figures.py重建全部图件（脚本另外输出一个明确标注为历史诊断的S04图）；运行python corrective_analysis/run_corrective_analysis.py重算模型；运行python build_manuscript.py重建Word文件。图形脚本已改用本包source_data相对路径，模型脚本亦使用包内数据。
在安装Microsoft Word的Windows上，可运行export_docx.ps1并指定InputPath与OutputPath导出PDF。正文来源为00至04的txt文件，采用清晰的章节标记，便于全文修改；references.bib供文献管理或LaTeX转稿使用。

使用边界
推荐器章节呈现研究原型及设计建议，未虚构新的用户实验、专家验证或部署效果。作者、机构、经费和未提供的声明信息没有被编造。数据解释与正式投稿前需完成的核查见独立作者说明。包内不重新分发被综述论文的完整PDF。
'''
(DEST/'README.txt').write_text(readme,encoding='utf-8-sig')
req=[]
for pkg in ['numpy','pandas','scikit-learn','matplotlib','Pillow','python-docx','pypdfium2','pdfplumber']:
 req.append(pkg+'=='+importlib.metadata.version(pkg))
(DEST/'requirements.txt').write_text('\n'.join(req)+'\n',encoding='utf-8')
manifest=[]
for p in sorted(DEST.rglob('*')):
 if p.is_file() and p.name!='package_manifest.json':
  manifest.append({'path':p.relative_to(DEST).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(DEST/'package_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
zpath=ROOT/'Subjective_Evaluation_Research_Package.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for p in DEST.rglob('*'):
  if p.is_file():z.write(p,arcname='Submission_Reference_Package/'+p.relative_to(DEST).as_posix())
print(json.dumps({'files':len(manifest)+1,'zip':str(zpath),'size_MB':round(zpath.stat().st_size/1048576,2)},ensure_ascii=False))
