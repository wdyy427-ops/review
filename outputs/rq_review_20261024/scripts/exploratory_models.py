"""Exploratory prediction on legacy first-pass codes only; NOT RQ3 validation."""
import json,sys,collections
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'_deps'))
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier,HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score,f1_score,brier_score_loss
from config import ROOT,LABELS

cases=json.loads((ROOT/'results'/'legacy_cases.json').read_text(encoding='utf8'))
features=[(f,c) for f in ['domain','stage','ai_function','purpose'] for c in LABELS[f]]
labels=list(LABELS['dimension'])
X=np.array([[int(code in r.get(f+'_codes',[])) for f,code in features] for r in cases],dtype=float)
Y=np.array([[int(code in r['dimension_codes']) for code in labels] for r in cases],dtype=int)
groups=np.array([r['paper_id'] for r in cases])
assert len(set(groups))==125 and X.shape==(198,len(features))
cv=GroupKFold(n_splits=5)
models={
 'fold_prevalence':None,
 'L2_logistic':lambda:LogisticRegression(C=.5,max_iter=2000,class_weight=None),
 'random_forest':lambda:RandomForestClassifier(n_estimators=300,min_samples_leaf=3,max_features='sqrt',random_state=9,n_jobs=-1),
 'extra_trees':lambda:ExtraTreesClassifier(n_estimators=300,min_samples_leaf=3,max_features='sqrt',random_state=9,n_jobs=-1),
 'hist_gradient_boosting':lambda:HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=7,min_samples_leaf=15,l2_regularization=5,random_state=9),
}
out=[];predictions=[]
for name,make in models.items():
    P=np.zeros_like(Y,dtype=float)
    for fold,(train,test) in enumerate(cv.split(X,Y,groups),1):
        for j in range(Y.shape[1]):
            y=Y[train,j];prev=(y.sum()+1)/(len(y)+2)
            if make is None or len(np.unique(y))<2:p=np.full(len(test),prev)
            else:
                model=make();model.fit(X[train],y)
                p=model.predict_proba(X[test])[:,1]
            P[test,j]=p
    ap=[average_precision_score(Y[:,j],P[:,j]) if Y[:,j].sum() else None for j in range(Y.shape[1])]
    pred=(P>=.5).astype(int)
    out.append({'model':name,'cases_n':len(cases),'papers_n':len(set(groups)),
       'micro_ap':float(average_precision_score(Y.ravel(),P.ravel())),
       'macro_ap':float(np.mean([v for v in ap if v is not None])),
       'micro_f1_at_0_5':float(f1_score(Y.ravel(),pred.ravel(),zero_division=0)),
       'macro_f1_at_0_5':float(f1_score(Y,pred,average='macro',zero_division=0)),
       'brier':float(brier_score_loss(Y.ravel(),P.ravel())),
       'per_dimension_ap':dict(zip(labels,ap)),
       'use_limit':'仅旧表首轮编码；不满足规范性子集，不可用作正式指标/工具推荐效能。'})
    for i,r in enumerate(cases):predictions.append({'model':name,'paper_id':r['paper_id'],'legacy_eval_id':r['legacy_eval_id'],
         'true_dimensions':r['dimension_codes'],'predicted_probabilities':dict(zip(labels,np.round(P[i],4).tolist()))})
(ROOT/'results'/'legacy_exploratory_model_comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'results'/'legacy_exploratory_predictions.json').write_text(json.dumps(predictions,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
