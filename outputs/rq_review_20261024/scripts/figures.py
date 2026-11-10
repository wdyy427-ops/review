import json,sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'_deps'))
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from config import ROOT,LABELS,STANDARDS
res=ROOT/'results';out=ROOT/'figures';out.mkdir(exist_ok=True)
def load(n):return json.loads((res/f'{n}.json').read_text(encoding='utf8'))
plt.rcParams['font.sans-serif']=['Microsoft YaHei'];plt.rcParams['axes.unicode_minus']=False
papers=load('legacy_papers');cases=load('legacy_cases');review=load('evaluations')
dom=list(LABELS['domain']);dims=list(LABELS['dimension'])
presence={p['paper_id']:set() for p in papers}
for c in cases:presence[c['paper_id']].update(c['dimension_codes'])
counts=np.array([[sum(d in p['domain_codes'] and k in presence[p['paper_id']] for p in papers) for k in dims] for d in dom])
den=np.array([sum(d in p['domain_codes'] for p in papers) for d in dom])
fig,ax=plt.subplots(figsize=(11.6,5.8),layout='constrained');fig.patch.set_facecolor('#F7F9F6');ax.set_facecolor('#F7F9F6')
color=LinearSegmentedColormap.from_list('green',['#EFF4EF','#B6D5C4','#267E63','#14503F'])
percent=np.divide(counts,den[:,None],out=np.zeros_like(counts,dtype=float),where=den[:,None]>0)
im=ax.imshow(percent,cmap=color,vmin=0,vmax=1,aspect='auto')
short={'A':'成果质量','B':'过程质量','C':'设计者感知','D':'交互体验','E':'社会情境价值'}
ax.set_xticks(range(5),[f'{k} {short[k]}' for k in dims],fontsize=11)
ax.set_yticks(range(6),[f'{LABELS["domain"][d]}  (n={n})' for d,n in zip(dom,den)],fontsize=10)
for i in range(6):
 for j in range(5):ax.text(j,i,f'{counts[i,j]}\n{percent[i,j]:.0%}',ha='center',va='center',fontsize=10,color='white' if percent[i,j]>.55 else '#193D31',fontweight='bold')
ax.set_title('设计领域 × 感知维度：论文层面覆盖',loc='left',fontsize=16,fontweight='bold',pad=20,color='#173D31')
fig.text(.11,.012,'说明：125篇旧表首轮编码的描述性图；可多领域、多维度，不代表已完成125篇全文复核。格内为论文数及该领域内比例。',fontsize=9,color='#63736A')
for s in ax.spines.values():s.set_visible(False)
ax.tick_params(length=0)
fig.savefig(out/'RQ1_首轮领域与感知维度.png',dpi=220,bbox_inches='tight');fig.savefig(out/'RQ1_首轮领域与感知维度.svg',bbox_inches='tight');plt.close(fig)

statuses=['S','P','C','NR','NA'];colors=['#2B8064','#8FC2A5','#BD654C','#B5BEC0','#E0E5DD']
fig,ax=plt.subplots(figsize=(11.6,5.2),layout='constrained');fig.patch.set_facecolor('#F7F9F6');ax.set_facecolor('#F7F9F6')
for i,(std,label) in enumerate(STANDARDS.items()):
 c=collections.Counter(e['audit_statuses'][std] for e in review);left=0
 for status,color in zip(statuses,colors):
  n=c[status]
  if not n:continue
  w=n/len(review);ax.barh(i,w,left=left,color=color,height=.64)
  if w>.08:ax.text(left+w/2,i,str(n),ha='center',va='center',color='white' if status in ['S','C'] else '#1B3F32',fontweight='bold',fontsize=10)
  left+=w
ax.set_yticks(range(len(STANDARDS)),[f'{k} {v}' for k,v in STANDARDS.items()],fontsize=10)
ax.invert_yaxis();ax.set_xlim(0,1);ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
ax.set_xlabel('已复核评价案例占比（n=31）',fontsize=10)
ax.set_title('JCSEE适用条款：逐案例报告状态',loc='left',fontsize=16,fontweight='bold',pad=17,color='#173D31')
ax.legend([matplotlib.patches.Patch(color=c) for c in colors],['充分支持 S','部分支持 P','明确问题 C','未报告 NR','不适用 NA'],ncol=5,loc='upper center',bbox_to_anchor=(.5,-.12),frameon=False,fontsize=9)
ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
for s in ax.spines.values():s.set_visible(False)
fig.text(.11,-.04,'仅12/125篇已完成全文复核；状态是本综述对JCSEE条款的操作化审查，不是JCSEE官方评分。',fontsize=9,color='#63736A')
fig.savefig(out/'RQ2_已复核案例规范性状态.png',dpi=220,bbox_inches='tight');fig.savefig(out/'RQ2_已复核案例规范性状态.svg',bbox_inches='tight');plt.close(fig)
print('figures ready')
