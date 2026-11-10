from pathlib import Path
import json, textwrap
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch
from matplotlib.colors import LinearSegmentedColormap

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'rq_review_20261024'/'supplement_enhanced_v2'
OUT=ROOT/'figures'; DATA=ROOT/'figure_data'
OUT.mkdir(parents=True,exist_ok=True); DATA.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':8.5,'axes.labelsize':8.5,'axes.titlesize':10,'axes.titleweight':'normal','axes.linewidth':0.65,'xtick.labelsize':8,'ytick.labelsize':8,'xtick.major.size':3,'ytick.major.size':3,'svg.fonttype':'none','pdf.fonttype':42,'ps.fonttype':42,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','text.color':'#222222','axes.labelcolor':'#222222','axes.edgecolor':'#555555','xtick.color':'#444444','ytick.color':'#444444'})
COL=['#4477AA','#66A5AD','#228833','#CC6677','#AA4499']
DIM={'A':'Design outcome quality','B':'Design process quality','C':'Designer cognition, affect\nand capabilities','D':'Human–AI interaction experience','E':'Social and contextual value'}
TOOLS={'M1':'Named scales','M2':'Bespoke structured ratings','M3':'Qualitative verbal elicitation','M4':'Non-scale structured judgments','M5':'Analysis of existing perceptual material'}
IND={'A1':'Novelty','A2':'Aesthetic appeal','A3':'Suitability','A4':'Feasibility','A5':'Fidelity','A6':'Comprehensiveness','B1':'Time efficiency','B2':'Perceived workload','B3':'Iteration efficiency','B4':'Decision support','B5':'Process continuity','B6':'Handover efficiency','C1':'Inspiration','C2':'Knowledge acquisition','C3':'Self-efficacy','C4':'Engagement and immersion','C5':'Enjoyment','C6':'Reflection','C7':'Fixation and dependence','C8':'Capability expansion','D1':'Ease of use','D2':'Intention to use','D3':'Sense of control','D4':'Explainability','D5':'Trust','D6':'Agency','D7':'Role and contribution fairness','D8':'Communication, coordination,\nconflict and shared understanding','E1':'End-user experience and acceptance','E2':'Fit with needs, contexts and populations','E3':'Professional and organizational fit','E4':'Cultural, social and public value','E5':'Ethics, fairness, bias and inclusion','E6':'Environmental and sustainability value','E7':'Commercial, brand and market value','E8':'Long-term use, governance and responsibility'}
DOM={'D1':'Visual\ncomm.','D2':'Industrial /\nproduct','D3':'Fashion','D4':'Interior','D5':'Service','D6':'UI / UX'}
STAGE={'S1':'Research','S2':'Ideation','S3':'Prototyping\n& testing','S4':'Implementation'}
M=[]
def read(f): return pd.read_csv(BASE/f,keep_default_na=False)
def clean(ax):
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(axis='y',length=0)
def panel(ax,label,title):
    ax.annotate(label,xy=(0,1.08),xycoords='axes fraction',xytext=(-9,0),textcoords='offset points',ha='right',va='bottom',weight='bold',fontsize=12)
    ax.text(0,1.08,title,transform=ax.transAxes,fontsize=10,va='bottom')
def export(fig,name,caption,source,findings,kind='main'):
    for ext in ['png','pdf','svg']: fig.savefig(OUT/f'{name}.{ext}',dpi=320,bbox_inches='tight',pad_inches=.08)
    sources=source if isinstance(source,list) else [source]
    sources=[str(((ROOT if (ROOT/s).exists() else BASE)/s).resolve()) for s in sources]
    with Image.open(OUT/f'{name}.png') as pic: width,height=pic.size
    M.append({'id':name,'kind':kind,'caption':caption,'source_files':sources,'findings':findings,'intended_width_inches':7.2,'design_canvas_inches':[fig.get_figwidth(),fig.get_figheight()],'exported_width_inches':width/320,'exported_height_inches':height/320,'aspect_ratio':width/height,'png_dpi':320,'files':{e:str((OUT/f'{name}.{e}').resolve()) for e in ['png','pdf','svg']}})
    plt.close(fig)
def dataout(df,name): df.to_csv(DATA/f'{name}.csv',index=False,encoding='utf-8-sig')
def box(ax,x,y,w,h,title,body,accent='#4477AA',size=8.5):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.008',linewidth=.8,edgecolor=accent,facecolor='white'))
    ax.text(x+.018,y+h-.027,title,ha='left',va='top',fontsize=9.3,weight='bold',color=accent)
    ax.text(x+.018,y+h-.073,body,ha='left',va='top',fontsize=size,linespacing=1.4)
def arrow(ax,x1,y1,x2,y2): ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=9,color='#777777',lw=.8))

# Figure 1: conceptual and numerical architecture, not a reconstructed PRISMA flow.
c=read('03_revised_results/evidence_chains_supplement_enhanced.csv')
meas=read('03_revised_results/measure_instances_supplement_enhanced.csv')
audit=read('03_revised_results/jcsee_chain_audit_supplement_enhanced.csv')
assert len(c)==514 and len(audit)==3598
fig=plt.figure(figsize=(7.2,5.0)); ax=fig.add_axes([.015,.04,.97,.92]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
ax.text(0,1,'a',weight='bold',fontsize=12); ax.text(.035,1,'Evidence architecture',fontsize=10)
box(ax,.02,.72,.28,.20,'Paper level','125 papers\nPublication and design context')
box(ax,.36,.72,.28,.20,'Evaluation-case level','159 evaluation cases\nPurpose, people and procedure')
box(ax,.70,.72,.28,.20,'Evidence-record level','514 candidate records\nClaim, indicator and tool')
arrow(ax,.30,.82,.35,.82);arrow(ax,.64,.82,.69,.82)
ax.text(.02,.64,'Context factors',weight='bold',fontsize=9)
ax.text(.02,.60,'G1 Purpose     G2 Domain     G3 Stage     G4 Evaluation object\nG5 Evaluator     G6 Target user     G7 AI function',fontsize=9,linespacing=1.7,va='top')
ax.text(0,.45,'b',weight='bold',fontsize=12); ax.text(.035,.45,'Analysis populations',fontsize=10)
box(ax,.02,.15,.28,.22,'Perceived-effect dimensions','460 mapped records\n54 unmapped records',COL[0])
box(ax,.36,.15,.28,.22,'Subjective indicators','454 mapped records\n6 additional indicator gaps',COL[2])
box(ax,.70,.15,.28,.22,'Measurement tools','624 tool instances\n608 classified; 16 unmapped',COL[4])
arrow(ax,.30,.26,.35,.26)
ax.text(.02,.035,'One record may use multiple tools. Context labels may be multiple.\nThe 514 records form the screening population; denominators depend on the evidence layer.',fontsize=8.2,linespacing=1.5)
flow=pd.DataFrame({'level':['Papers','Evaluation cases','Candidate evidence records','Mapped dimension records','Mapped indicator records','Tool instances','Classified tool instances'],'n':[125,159,514,460,454,624,608]});dataout(flow,'fig01_populations')
export(fig,'fig01_evidence_architecture','Analytical architecture and denominators. Paper and evaluation-case information is linked to each candidate evidence record. Of 514 records, 460 have a mapped perceived-effect dimension and 454 have a mapped subjective indicator. A record can use more than one tool, yielding 624 tool instances, of which 608 are classified. The diagram describes the available analytic corpus and is not a literature-search flow diagram.',['03_revised_results/evidence_chains_supplement_enhanced.csv','03_revised_results/measure_instances_supplement_enhanced.csv'],flow.to_dict('records'))

# Figure 2: overall distributions.
dim=read('04_RQ1/rq1_dimension_overall.csv'); tools=read('04_RQ1/rq1_tool_overall.csv'); ind=read('04_RQ1/rq1_indicator_overall.csv')
assert dim.n.sum()==460 and ind.n.sum()==454 and tools.n.sum()==608
fig,axs=plt.subplots(3,1,figsize=(7.2,7.1),gridspec_kw={'height_ratios':[1.1,1.1,2.2]});fig.subplots_adjust(left=.36,right=.97,top=.95,bottom=.07,hspace=.54)
def bars(ax,df,names,title,p,colors,maxx=None):
    y=np.arange(len(df));pct=df.percent.to_numpy(float)*100
    ax.barh(y,pct,color=colors,height=.66)
    ax.set_yticks(y,[f'{r.code}  {names[r.code]}' for r in df.itertuples()]);ax.invert_yaxis()
    for yy,r in enumerate(df.itertuples()): ax.text(r.percent*100+.5,yy,f'{r.n} ({r.percent*100:.1f}%)',va='center',fontsize=8)
    ax.set_xlim(0,maxx or pct.max()*1.35);ax.set_xlabel('Share of mapped records (%)' if p!='b' else 'Share of classified tool instances (%)');clean(ax);panel(ax,p,title);ax.grid(axis='x',color='#e8e8e8',lw=.5);ax.set_axisbelow(True)
bars(axs[0],dim,DIM,'Perceived-effect dimensions  ·  n = 460','a',COL,45)
bars(axs[1],tools,TOOLS,'Measurement tools  ·  n = 608 instances','b',COL,45)
top=ind.sort_values('n',ascending=False,kind='stable').head(12)
bars(axs[2],top,IND,'Most frequently coded subjective indicators  ·  n = 454','c',[COL['ABCDE'.index(k[0])] for k in top.code],12)
for name,df in [('dimensions',dim),('tools',tools),('indicators',ind)]:dataout(df,'fig02_'+name)
export(fig,'fig02_evidence_distributions','Distribution of evaluation evidence. (a) Perceived-effect dimensions among 460 mapped records. (b) Tool classes among 608 classified tool instances. (c) The 12 most frequent subjective indicators among 454 mapped indicator records. Labels show counts and within-layer percentages. Colour identifies dimensions in (a,c); tool colours in (b) identify tool classes. These distributions describe what the corpus evaluates, not the size or direction of AI effects.',['04_RQ1/rq1_dimension_overall.csv','04_RQ1/rq1_tool_overall.csv','04_RQ1/rq1_indicator_overall.csv'],{'largest_dimension':'A:144/460 (31.3%)','largest_tool':'M2:193/608 (31.7%)','largest_indicator':'A3:39/454 (8.6%)'})

# Figure 3: publication years harmonized from the verified Crossref catalogue.
catalogue=pd.read_csv(ROOT/'reviewed_corpus_catalogue.csv',keep_default_na=False)
assert len(catalogue)==125 and catalogue.paper_id.nunique()==125
assert (catalogue.crossref_status=='ok').all()
catalogue['publication_year']=catalogue.crossref_published.str.split('-').str[0].astype(int)
year_map=catalogue.set_index('paper_id').publication_year
paper_year_counts=catalogue.groupby('publication_year').size()
assert paper_year_counts.to_dict()=={2022:11,2023:11,2024:28,2025:33,2026:42}
def harmonized_year_distribution(frame,column,names,unit):
    records=frame[frame[column].isin(names)].copy()
    records['publication_year']=records.paper_id.map(year_map)
    assert records.publication_year.notna().all()
    counts=records.groupby(['publication_year',column]).size()
    rows=[]
    for year in sorted(year_map.unique()):
        denominator=int((records.publication_year==year).sum())
        for code,label in names.items():
            n=int(counts.get((year,code),0))
            rows.append({'unit':unit,'year':int(year),'year_convention':'Crossref published','code':code,'label':label.replace('\n',' '),'n':n,'denominator':denominator,'percent':n/denominator if denominator else 0})
    return pd.DataFrame(rows)
yd=harmonized_year_distribution(c,'dimension_code',DIM,'evidence_chain')
yi=harmonized_year_distribution(c,'indicator_code',IND,'evidence_chain')
yt=harmonized_year_distribution(meas,'tool_code',TOOLS,'measure_instance')
assert yd.n.sum()==460 and yi.n.sum()==454 and yt.n.sum()==608
dataout(read('04_RQ1/rq1_dimension_by_year.csv'),'fig03_sensitivity_coded_year_dimensions')
dataout(read('04_RQ1/rq1_tool_by_year.csv'),'fig03_sensitivity_coded_year_tools')
dataout(pd.read_csv(ROOT/'publication_year_sensitivity.csv',keep_default_na=False),'fig03_sensitivity_year_conventions')
dataout(catalogue[['paper_id','crossref_published','publication_year','coded_year','screening_year']],'fig03_paper_publication_years')
dataout(paper_year_counts.rename('n_papers').reset_index(),'fig03_papers_by_year')
annual_summary=[]
for layer,annual in [('dimension',yd),('indicator',yi),('tool',yt)]:
    for year,sub in annual.groupby('year'):
        for row in sub[sub.n==sub.n.max()].itertuples():
            annual_summary.append({'layer':layer,'year':int(year),'denominator':int(row.denominator),'largest_code':row.code,'largest_label':row.label,'n':int(row.n),'percent':float(row.percent)})
dataout(pd.DataFrame(annual_summary),'fig03_temporal_summary')
fig,axs=plt.subplots(1,2,figsize=(7.2,3.65));fig.subplots_adjust(left=.08,right=.99,top=.86,bottom=.34,wspace=.35)
for ax,df,names,letter,title in [(axs[0],yd,DIM,'a','Perceived-effect dimensions'),(axs[1],yt,TOOLS,'b','Measurement tools')]:
    pv=df.pivot(index='year',columns='code',values='n').fillna(0); den=pv.sum(axis=1);bottom=np.zeros(len(pv)); xx=np.arange(len(pv))
    for j,k in enumerate(pv.columns):
        val=pv[k]/den*100;ax.bar(xx,val,bottom=bottom,color=COL[j],width=.68,label=k);bottom+=val
    for x,n in zip(xx,den): ax.text(x,103,f'n={int(n)}',ha='center',fontsize=7.3)
    ax.set_xticks(xx,pv.index);ax.set_ylim(0,112);ax.set_yticks([0,25,50,75,100]);ax.set_ylabel('Within-year share (%)');clean(ax);panel(ax,letter,title)
    labels=[f'{k}  {names[k].replace(chr(10)," ")}' for k in pv.columns]
    ax.legend([Patch(facecolor=COL[j]) for j in range(5)],labels,loc='upper left',bbox_to_anchor=(-.04,-.21),frameon=False,fontsize=7,handlelength=1,ncol=1,labelspacing=.45)
dataout(yd,'fig03_dimensions_by_year');dataout(yi,'fig03_indicators_by_year');dataout(yt,'fig03_tools_by_year')
export(fig,'fig03_temporal_composition','Annual composition of mapped perceived-effect dimensions and classified tools, using publication years harmonized with the Crossref published date for all 125 papers. Each bar sums to 100% within a year; the count above the bar gives the denominator for that evidence layer. Annual paper counts for 2022–2026 are 11, 11, 28, 33 and 42. Coverage in 2026 is partial, through 25 September, and the early years have small evidence-layer denominators. The figure describes corpus composition, not temporal changes in the magnitude or direction of AI effects. Original coded-year and screening-year distributions are retained as sensitivity source data.',['reviewed_corpus_catalogue.csv','publication_year_sensitivity.csv','03_revised_results/evidence_chains_supplement_enhanced.csv','03_revised_results/measure_instances_supplement_enhanced.csv'],{'paper_yearly_n':paper_year_counts.to_dict(),'dimension_yearly_n':yd.groupby('year').n.sum().to_dict(),'indicator_yearly_n':yi.groupby('year').n.sum().to_dict(),'tool_yearly_n':yt.groupby('year').n.sum().to_dict(),'largest_annual_proportions':annual_summary,'year_convention':'Crossref published date, joined by paper_id'})

# Figure 4: context distributions.
ctx=read('04_RQ1/rq1_domain_stage_by_dimension_indicator_tool.csv')
cmap=LinearSegmentedColormap.from_list('evidence',['#f5f8fa','#cbdde8','#7baac7','#2b668f'])
fig,axs=plt.subplots(2,2,figsize=(7.2,5.65));fig.subplots_adjust(left=.07,right=.98,top=.91,bottom=.20,wspace=.28,hspace=.73)
for ax,field,level,names,ltr,title in [(axs[0,0],'domains','dimension_code',DIM,'a','Dimensions by domain'),(axs[0,1],'stages','dimension_code',DIM,'b','Dimensions by stage'),(axs[1,0],'domains','tool_class',TOOLS,'c','Tools by domain'),(axs[1,1],'stages','tool_class',TOOLS,'d','Tools by stage')]:
    # The exported tool target field is named revised_tool_class in some versions.
    sub=ctx[(ctx.context_field==field)&(ctx.target_level==level)]
    if sub.empty and level=='tool_class':sub=ctx[(ctx.context_field==field)&ctx.target_level.str.contains('tool')]
    xnames=DOM if field=='domains' else STAGE;codes=list(names); xcodes=list(xnames)
    val=sub.pivot(index='target_code',columns='context_code',values='percent').reindex(index=codes,columns=xcodes).fillna(0)*100
    cnt=sub.pivot(index='target_code',columns='context_code',values='n').reindex(index=codes,columns=xcodes).fillna(0)
    im=ax.imshow(val,vmin=0,vmax=65,cmap=cmap,aspect='auto')
    for i in range(len(codes)):
        for j in range(len(xcodes)):ax.text(j,i,str(int(cnt.iloc[i,j])),ha='center',va='center',fontsize=7,color='white' if val.iloc[i,j]>40 else '#222222')
    ax.set_xticks(range(len(xcodes)),[xnames[x] for x in xcodes],fontsize=7.1);ax.set_yticks(range(len(codes)),codes,fontsize=8)
    ax.tick_params(length=0);panel(ax,ltr,title)
    for s in ax.spines.values():s.set_visible(False)
    den=sub.groupby('context_code').denominator.first()
    for j,code in enumerate(xcodes):ax.text(j,-.72,f'n={int(den.get(code,0))}',ha='center',fontsize=6.7)
cbax=fig.add_axes([.31,.105,.40,.015]);cb=fig.colorbar(im,cax=cbax,orientation='horizontal',ticks=[0,20,40,60]);cb.set_label('Within-context share (%)',fontsize=7.5);cb.outline.set_visible(False)
fig.text(.02,.025,'A Outcome quality   B Process quality   C Designer cognition, affect and capabilities   D Human–AI experience   E Social/contextual value',fontsize=6.1)
fig.text(.02,.003,'M1 Named scales   M2 Bespoke ratings   M3 Verbal elicitation   M4 Non-scale judgments   M5 Existing perceptual material',fontsize=6.1)
dataout(ctx,'fig04_context_distribution')
export(fig,'fig04_context_distributions','Contextual distribution of perceived-effect dimensions and tool classes. Colour shows the proportion within each design domain or stage; cell labels give raw counts and column labels give denominators. Records can carry more than one domain or stage, so counts across columns do not sum to the unique-record total. Domain and stage membership are descriptive context labels.',['04_RQ1/rq1_domain_stage_by_dimension_indicator_tool.csv'],{'normalization':'within each context and target layer; multi-label contexts counted in each applicable column'})

# Figure 5: calculate statuses directly, preserving the literal NA code.
sts=['S','P','NR','C','NA'];order=['U5','A2','A3','A4','A6','A7','E1'];labs=['U5  Purpose relevance','A2  Validity support','A3  Reliability / credibility','A4  Context description','A6  Design and analysis','A7  Evaluation reasoning','E1  Documentation']
counts=pd.crosstab(audit.standard,audit.status).reindex(index=order,columns=sts,fill_value=0)
assert (counts.sum(axis=1)==514).all() and counts.loc['A3','NA']==40
status_cols=['#3377AA','#A6CEE3','#D9D9D9','#CC6677','#EEE8D5']
fig,axs=plt.subplots(1,2,figsize=(7.2,4.1),gridspec_kw={'width_ratios':[1.9,1]});fig.subplots_adjust(left=.24,right=.98,top=.86,bottom=.23,wspace=.39)
ax=axs[0];left=np.zeros(7)
for k,col in zip(sts,status_cols):
    v=counts[k].values/514*100;ax.barh(np.arange(7),v,left=left,color=col,height=.64,edgecolor='white',lw=.4)
    for i in range(7):
        if v[i]>=7:ax.text(left[i]+v[i]/2,i,str(counts.iloc[i][k]),ha='center',va='center',fontsize=7.5,color='white' if k=='S' else '#222222')
    left+=v
ax.set_yticks(range(7),labs);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Share of 514 candidate records (%)');clean(ax);panel(ax,'a','Reporting-support profile')
ax.legend([Patch(facecolor=cc) for cc in status_cols],['S  Coded sufficient','P  Coded partial','NR  Not reported','C  Coded concern','NA  Not applicable'],bbox_to_anchor=(-.66,-.23),loc='upper left',ncol=3,frameon=False,fontsize=7.2,handlelength=1.0,columnspacing=1.3)
ax=axs[1];q=c.revised_quality_tier.value_counts();q=q.reindex(['Q1','Q2','Q3','EXCLUDE'],fill_value=0)
ax.barh(range(4),q.values,color=['#3377AA','#A6CEE3','#D9D9D9','#CC6677'],height=.64)
ax.set_yticks(range(4),['Q1','Q2','Q3','Exclude']);ax.invert_yaxis();ax.set_xlim(0,520);ax.set_xticks([0,200,400]);ax.set_xlabel('Candidate records');clean(ax);panel(ax,'b','Analytical tiers')
for i,v in enumerate(q):ax.text(v+10,i,str(v),va='center',fontsize=8)
ax.text(0,-.21,'Primary subset: 63\nExpanded subset: 183\n(Q1 + Q2 included)',transform=ax.transAxes,fontsize=8,linespacing=1.5,va='top')
dataout(counts.reset_index(),'fig05_audit_statuses');dataout(pd.DataFrame({'tier':q.index,'n':q.values}),'fig05_quality_tiers')
export(fig,'fig05_reported_evaluation_quality','Distribution of operational reporting-support codes across 514 candidate records. (a) The seven JCSEE-informed criteria yield 3,598 criterion-by-record codes, including 40 records coded NA for A3. S, P and C denote coded sufficient support, partial support and concern, respectively. NR does not establish that a procedure was omitted in practice. Numbers identify segments large enough to label; exact counts are provided in source data. (b) Analytical tiers derived from the operational codes: the primary subset comprises Q1 and Q2 (63 records), and the expanded subset contains 183 records. Counts represent coded categories, not certification of study methodological quality.',['03_revised_results/jcsee_chain_audit_supplement_enhanced.csv','03_revised_results/evidence_chains_supplement_enhanced.csv'],{'statuses':counts.to_dict(),'operational_analytical_tiers':q.to_dict(),'validation_status':'Detailed coding-validation limitations are recorded in the separate figure QA and author notes.'})

# Figure 6: expose feature-target coupling rather than promote circular weights.
full=read('06_RQ3/rq3_model_comparison_g1_g7.csv');nog4=read('06_RQ3/rq3_dimension_without_g4_sensitivity.csv')
model_names={'频率基线':'Frequency baseline','L2多项逻辑回归':'L2 logistic regression','随机森林':'Random forest','直方图梯度提升':'Histogram gradient boosting'}
models=list(model_names)
fig,axs=plt.subplots(1,2,figsize=(7.2,3.6));fig.subplots_adjust(left=.27,right=.98,top=.81,bottom=.23,wspace=.37)
for ax,tier,ltr,label in [(axs[0],'主要规范集','a','Primary subset'),(axs[1],'扩展规范集','b','Expanded subset')]:
    f=full[(full.analysis_tier==tier)&(full.target=='评价维度')].set_index('model').reindex(models)
    n=nog4[nog4.analysis_tier==tier].set_index('model').reindex(models)
    for i,model in enumerate(models):
        ax.plot([n.loc[model,'macro_f1_mean'],f.loc[model,'macro_f1_mean']],[i,i],color='#b8b8b8',lw=1.2,zorder=1)
    ax.errorbar(f.macro_f1_mean,np.arange(4)-.06,xerr=f.macro_f1_sd,fmt='o',ms=5,color='#CC6677',lw=.8,capsize=2,label='With target-derived G4')
    ax.errorbar(n.macro_f1_mean,np.arange(4)+.06,xerr=n.macro_f1_sd,fmt='s',ms=4.5,color='#4477AA',lw=.8,capsize=2,label='Without G4')
    ax.set_yticks(range(4),[model_names[m] for m in models] if ax is axs[0] else []);ax.invert_yaxis();ax.set_xlim(0,.76);ax.set_xticks([0,.2,.4,.6]);ax.set_xlabel('Macro-F1 (mean ± fold SD)');clean(ax);ax.grid(axis='x',color='#eeeeee',lw=.5);panel(ax,ltr,label)
    ax.text(0,1.03,f'n = {int(f.n.iloc[0])} records; {int(f.papers.iloc[0])} papers; {int(f.classes.iloc[0])} classes',transform=ax.transAxes,fontsize=7.5)
axs[0].legend(loc='upper left',bbox_to_anchor=(-.10,-.23),frameon=False,ncol=2,fontsize=8,handlelength=1.2,columnspacing=1.5)
dataout(full,'figS04_all_model_results');dataout(nog4,'figS04_without_g4')
export(fig,'figS04_original_g4_diagnostic','Diagnostic sensitivity of the original perceived-effect dimension model to G4. Primary and expanded subsets are provisional operational screens defined by unvalidated automated reporting-support labels, not verified high-quality evidence. The original implementation derives the evaluation-object code partly from dimension and indicator codes, introducing target information into this feature. Paired results show the same model with and without G4, using paper-grouped cross-validation. Error bars are standard deviations across folds, not population confidence intervals. Both configurations retain the original G5 recoding, which also used target information; the no-G4 configuration is therefore not leakage-free. These historical diagnostics are superseded by the corrective analysis in Figure 6.',['06_RQ3/rq3_model_comparison_g1_g7.csv','06_RQ3/rq3_dimension_without_g4_sensitivity.csv'],{'expanded_random_forest_with_G4':.5002116678,'expanded_random_forest_without_G4':.1117554370,'expanded_best_without_G4':.1326414566},'supplement')

# Main Figure 6: corrective models exclude G4 and use original evaluator codes.
corrected=pd.read_csv(ROOT/'corrective_analysis/model_summary.csv',keep_default_na=False)
targets=['perceived_effect_dimension','subjective_indicator','tool_class']
target_titles=['Perceived Effects dimensions','Subjective indicators','Tool classes']
model_keys=['frequency_baseline','context_only','known_evidence_only','context_plus_known_evidence']
model_labels=['Frequency baseline','Context only','Known evidence only','Context + known evidence']
fig,axs=plt.subplots(1,3,figsize=(7.2,3.4));fig.subplots_adjust(left=.225,right=.98,top=.78,bottom=.21,wspace=.38)
for j,(ax,target,title) in enumerate(zip(axs,targets,target_titles)):
    df=corrected[(corrected.tier=='expanded')&(corrected.target==target)].set_index('model')
    for i,key in enumerate(model_keys):
        if key not in df.index:
            ax.text(.19,i,'Not applicable',color='#777777',ha='center',va='center',fontsize=7)
            continue
        r=df.loc[key]; val=float(r.macro_f1_mean); sd=float(r.macro_f1_split_sd)
        ax.errorbar(val,i,xerr=sd,fmt='o',color=['#999999',COL[0],COL[1],COL[3]][i],ms=4.6,lw=.9,capsize=2)
        ax.text(val+sd+.012,i,f'{val:.3f}',fontsize=7,va='center')
    ax.set_yticks(range(4),model_labels if j==0 else []);ax.set_ylim(3.5,-.5);ax.set_xlim(0,.52);ax.set_xticks([0,.2,.4]);ax.set_xlabel('Macro-F1');clean(ax);ax.grid(axis='x',color='#eeeeee',lw=.5)
    ax.annotate('abc'[j],xy=(0,1.26),xycoords='axes fraction',xytext=(-9,0),textcoords='offset points',ha='right',va='bottom',weight='bold',fontsize=12)
    ax.text(0,1.26,title if j else 'Perceived Effects',transform=ax.transAxes,fontsize=10,va='bottom')
    row=df.iloc[0];unit='instances' if target=='tool_class' else 'records'
    ax.text(0,1.015,f'{int(row.n)} {unit}; {int(row.papers)} papers\n{int(row.classes)} classes',transform=ax.transAxes,fontsize=7.1,va='bottom',linespacing=1.25)
fig.text(.225,.060,'Expanded analytical subset',fontsize=8)
fig.text(.225,.010,'Mean ± SD across 10 repeated paper-grouped cross-validation partitions',fontsize=8)
dataout(corrected,'fig06_corrective_model_results')
export(fig,'fig06_corrective_model_performance','Predictive analysis in the expanded analytical subset. Results are conditional on the operational eligibility rules and coded records used in this analysis. Fixed, class-balanced L2 logistic regression uses fold-specific encoding, excludes target-derived G4 and uses original evaluator labels for G5. Panels report classification of (a) perceived-effect dimensions, (b) subjective indicators and (c) tool classes. Known evidence means the dimension for indicator prediction, and dimension plus indicator for tool prediction; it is inapplicable to dimension prediction. Points are mean pooled out-of-fold macro-F1 over ten repeated paper-grouped partitions; error bars are the SD across partitions, not confidence intervals for a population effect. Different target layers have different eligible samples and class counts.',['corrective_analysis/model_summary.csv','corrective_analysis/run_corrective_analysis.py'],{'expanded_dimension_context_f1':.1798955711,'expanded_indicator_context_f1':.0838359309,'expanded_indicator_known_f1':.3153146729,'expanded_indicator_combined_f1':.3636358694,'expanded_tool_context_f1':.3259814168,'expanded_tool_known_f1':.2605421682,'expanded_tool_combined_f1':.2999843614})

# Figure 7: an evidence-guided, user-confirmed process; no unsupported optimality claim.
fig=plt.figure(figsize=(7.2,5.2));ax=fig.add_axes([.015,.025,.97,.95]);ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
ax.text(.02,.96,'Progressive disclosure of evaluation evidence',weight='bold',fontsize=11)
steps=[('1','Specify the evaluation context','Purpose and evaluation object\nDomain, stage, evaluator, target user and AI function'),('2','Select perceived effects','Inspect candidate dimensions and relevant studies\nConfirm which perceived effects the evaluation should address'),('3','Select subjective indicators','Inspect definitions and original study items\nCheck alignment with the selected perceived effects'),('4','Select tools and inspect support','Inspect tools, procedures and reported measurement evidence\nCheck suitability for the evaluator and context')]
for i,(n,title,body) in enumerate(steps):
    y=.70-i*.19
    ax.add_patch(plt.Circle((.055,y+.07),.025,color=COL[min(i,4)]))
    ax.text(.055,y+.07,n,color='white',weight='bold',ha='center',va='center',fontsize=10)
    box(ax,.105,y,.86,.145,title,body,COL[min(i,4)],size=8.4)
    if i<3:arrow(ax,.54,y-.005,.54,y-.04)
ax.text(.105,.02,'At each step: reveal source evidence, make uncertainty visible, and retain user confirmation.\nModel rankings support evidence exploration; independent evaluation of recommendation quality remains necessary.',fontsize=8,linespacing=1.5)
dataout(pd.DataFrame(steps,columns=['step','title','description']),'fig07_guidance_structure')
export(fig,'fig07_progressive_evidence_guidance','Proposed interaction structure for progressively disclosed evidence guidance. Users first specify context and then confirm perceived effects, subjective indicators and tools in sequence. Source records and reported support remain inspectable at every step. The diagram expresses the evidence-guidance design; it does not claim that ranking weights are causal, that the recommender is optimal, or that recommendation quality has been independently validated.',['reports/06_网页推荐器更新建议.md','06_RQ3/rq3_recommender_policy.json'],{'status':'conceptual interaction structure; avoid treating circular model weights as validated selection rules'})

# Supplementary figure S1: all coded indicators, including a zero category.
fig,axs=plt.subplots(1,2,figsize=(7.2,6.2));fig.subplots_adjust(left=.35,right=.97,top=.92,bottom=.09,wspace=1.1)
groups=[list(ind.code)[:20],list(ind.code)[20:]]
for ax,codes,ltr in zip(axs,groups,['a','b']):
    df=ind.set_index('code').loc[codes].reset_index();ys=np.arange(len(df));ax.barh(ys,df.n,color=[COL['ABCDE'.index(k[0])] for k in df.code],height=.64)
    names=[f'{k}  '+IND[k].replace('\n',' ') for k in df.code]
    names=['\n'.join(textwrap.wrap(n,31)) for n in names]
    ax.set_yticks(ys,names,fontsize=7.1);ax.invert_yaxis();ax.set_xlim(0,46);ax.set_xlabel('Mapped indicator records');clean(ax)
    for y,n in zip(ys,df.n):ax.text(n+.7,y,str(n),va='center',fontsize=7)
    panel(ax,ltr,'Subjective indicators')
export(fig,'figS01_all_subjective_indicators','All 36 predefined subjective-indicator categories, counted among 454 mapped records. Handover efficiency (B6) has zero records. Colours identify the five perceived-effect dimensions. Counts describe coverage in the corpus, not the magnitude of an effect.',['04_RQ1/rq1_indicator_overall.csv'],{'total_records':454,'predefined_categories':36,'nonzero_categories':int((ind.n>0).sum())},'supplement')

# Supplementary figure S2: distribution robustness after evidence enrichment.
rob=read('07_robustness_comparison/pre_post_distribution_comparison.csv')
fig,axs=plt.subplots(1,2,figsize=(7.2,3.7));fig.subplots_adjust(left=.26,right=.98,top=.88,bottom=.24,wspace=.70)
for ax,lev,names,ltr in [(axs[0],'dimension',DIM,'a'),(axs[1],'tool',TOOLS,'b')]:
    df=rob[rob.level==lev].copy();df=df.set_index('code').reindex(list(names)).reset_index()
    for i,r in enumerate(df.itertuples()):ax.plot([r.before*100,r.after*100],[i,i],color='#aaaaaa',lw=1.1)
    ax.scatter(df.before*100,range(len(df)),color='#999999',s=22,label='Before');ax.scatter(df.after*100,range(len(df)),color='#4477AA',s=22,label='After')
    ax.set_yticks(range(len(df)),[f'{k} '+names[k].replace('\n',' ') for k in df.code] if lev=='dimension' else list(df.code),fontsize=7.4);ax.invert_yaxis();ax.set_xlim(0,38);ax.set_xlabel('Within-layer share (%)');clean(ax);panel(ax,ltr,'Dimensions' if lev=='dimension' else 'Tool classes')
axs[0].legend(frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(.2,-.23),fontsize=8)
dataout(rob,'figS02_distribution_robustness')
export(fig,'figS02_distribution_robustness','Distributional sensitivity to evidence enrichment. Points compare the baseline and supplement-enhanced corpus for dimensions (432 versus 460 mapped records) and tools (584 versus 608 classified instances). Small changes in aggregate composition do not imply stability of fitted models or individual classification decisions.',['07_robustness_comparison/pre_post_distribution_comparison.csv'],{'max_absolute_percentage_point_change':float(rob.delta.abs().max()*100)},'supplement')

# Supplementary figure S3: conditional ablation deltas, never causal influence weights.
ablation=pd.read_csv(ROOT/'corrective_analysis/group_ablations.csv',keep_default_na=False)
groups=['G1','G2','G3','G5_raw','G6','G7']
group_labels=['G1 Purpose','G2 Domain','G3 Stage','G5 Evaluator','G6 Target user','G7 AI function']
fig,axs=plt.subplots(1,3,figsize=(7.2,3.5));fig.subplots_adjust(left=.20,right=.98,top=.84,bottom=.22,wspace=.32)
for j,(ax,target,title) in enumerate(zip(axs,targets,['Perceived Effects','Subjective indicators','Tool classes'])):
    df=ablation[ablation.target==target].set_index('group').reindex(groups)
    for i,row in enumerate(df.itertuples()):
        ax.errorbar(row.mean_delta_macro_f1,i,xerr=row.split_sd_delta,fmt='o',ms=4.4,lw=.85,capsize=2,color=COL[0] if row.mean_delta_macro_f1>0 else '#888888')
    ax.axvline(0,color='#777777',lw=.65,zorder=0);ax.set_yticks(range(6),group_labels if j==0 else []);ax.set_ylim(5.6,-.6);ax.set_xlim(-.15,.09);ax.set_xticks([-.10,0,.05]);ax.set_xlabel('Change in macro-F1');clean(ax);panel(ax,'abc'[j],title)
fig.text(.20,.055,'Positive values: retaining the context group improved prediction in this model.',fontsize=8)
dataout(ablation,'figS03_corrective_group_ablations')
export(fig,'figS03_corrective_group_ablations','Conditional contribution of context groups in the corrective analysis of the expanded operational-screen subset. This provisional subset is defined by unvalidated automated reporting-support labels, not verified evaluation quality. Values equal macro-F1 for the retained-feature model minus macro-F1 when a single group is removed. The reference is context-only for dimension prediction, and context plus known evidence for indicator and tool prediction. Positive values indicate improved predictive performance when retaining the group; negative values indicate worse performance. Error bars are SDs of paired changes over ten repeated paper-grouped partitions. These model-specific predictive deltas are not causal effects, normalized influence weights or validated recommendation rules. G4 is excluded and G5 uses original evaluator labels.',['corrective_analysis/group_ablations.csv'],{'strongest_positive_indicator_group':'G2: +0.0263','strongest_positive_tool_group':'G1: +0.0401','G7_deltas':'negative for all three target layers'},'supplement')

for item in M:
    prefix=item['id'].split('_')[0]
    item['figure_data_files']=[str(p.resolve()) for p in sorted(DATA.glob(prefix+'_*.csv'))]
    if prefix=='figS01':item['figure_data_files']=[str((DATA/'fig02_indicators.csv').resolve())]
M.sort(key=lambda item:item['id'])
(ROOT/'figure_manifest.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'figures':len(M),'output':str(OUT)},ensure_ascii=False))
