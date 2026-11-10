"""Leakage-reduced exploratory analysis; original research files remain read-only.

Fixed before inspecting this analysis's results: L2 logistic regression C=1,
class_weight=balanced; 10 shuffled paper-grouped CV repetitions. No model or
feature subset is selected from these results. Group ablations are descriptive.
"""
from pathlib import Path
import json
import platform
import warnings
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import f1_score, accuracy_score

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'outputs/rq_review_20261024/supplement_enhanced_v2/03_revised_results'
OUT = Path(__file__).resolve().parent
GROUPS = {'G1': 'purposes', 'G2': 'domains', 'G3': 'stages',
          'G5_raw': 'evaluators', 'G6': 'target_users', 'G7': 'ai_functions'}
REPEATS = 10
SEED = 20261029

def tokens(v):
    return [x.strip() for x in str(v).split(';') if x.strip() not in {'', 'NR', 'NA', 'UNMAPPED', 'nan'}]

def feature_dicts(df, groups, fixed):
    rows = []
    for r in df.to_dict('records'):
        features = {}
        for group in groups:
            vals = tokens(r.get(GROUPS[group], ''))
            if group == 'G6':
                vals = [v for v in vals if v in {'U1', 'U2', 'U3'}]
            for value in vals:
                features[group + ':' + value] = 1.0
        for field in fixed:
            for value in tokens(r.get(field, '')):
                features['FIXED:' + field + ':' + value] = 1.0
        # A constant keeps the fit defined even if every categorical field is missing.
        features['intercept_feature'] = 1.0
        rows.append(features)
    return rows

def metrics(y, pred, probs, classes, paper_ids):
    y = np.asarray(y)
    order = np.argsort(-probs, axis=1, kind='stable')[:, :2]
    top2 = np.any(np.asarray(classes)[order] == y[:, None], axis=1)
    counts = pd.Series(paper_ids).value_counts()
    pw = np.asarray([1.0 / counts[p] for p in paper_ids])
    return {'macro_f1': float(f1_score(y, pred, labels=classes, average='macro', zero_division=0)),
            'accuracy': float(accuracy_score(y, pred)),
            'top2_accuracy': float(np.mean(top2)),
            'paper_balanced_macro_f1': float(f1_score(y, pred, labels=classes, average='macro', zero_division=0, sample_weight=pw)),
            'paper_balanced_accuracy': float(accuracy_score(y, pred, sample_weight=pw)),
            'paper_balanced_top2_accuracy': float(np.average(top2, weights=pw))}

def run():
    chains = pd.read_csv(DATA / 'evidence_chains_supplement_enhanced.csv', encoding='utf-8-sig', keep_default_na=False)
    measures = pd.read_csv(DATA / 'measure_instances_supplement_enhanced.csv', encoding='utf-8-sig', keep_default_na=False)
    measures = measures.merge(chains[['chain_id'] + list(GROUPS.values())], on='chain_id', how='left', validate='many_to_one')
    meta, repeat_rows, predictions, split_checks, class_counts = [], [], [], [], []
    metrics_names = ['macro_f1', 'accuracy', 'top2_accuracy', 'paper_balanced_macro_f1', 'paper_balanced_accuracy', 'paper_balanced_top2_accuracy']
    for tier, eligibility in [('main', 'model_eligible_main'), ('expanded', 'model_eligible_sensitivity')]:
        for target, field, source, fixed, valid in [
            ('perceived_effect_dimension', 'dimension_code', chains, [], list('ABCDE')),
            ('subjective_indicator', 'indicator_code', chains, ['dimension_code'], None),
            ('tool_class', 'tool_code', measures, ['dimension_code', 'indicator_code'], ['M1', 'M2', 'M3', 'M4', 'M5'])]:
            df = source[source[eligibility] == 1].copy()
            df = df[df[field].isin(valid)] if valid else df[~df[field].isin(['', 'UNMAPPED', 'NA', 'NR'])]
            c = df.groupby(field).agg(records=(field, 'size'), papers=('paper_id', 'nunique'))
            c['eligible'] = (c.records >= 5) & (c.papers >= 3)
            for code, row in c.iterrows():
                class_counts.append({'tier': tier, 'target': target, 'class': code, **row.to_dict()})
            df = df[df[field].isin(c.index[c.eligible])].reset_index(drop=True)
            nclasses, npapers = df[field].nunique(), df.paper_id.nunique()
            eligible = len(df) >= 30 and nclasses >= 2
            nfolds = int(min(5, df.groupby(field).paper_id.nunique().min(), npapers)) if eligible else 0
            meta.append({'tier': tier, 'target': target, 'n': len(df), 'papers': npapers, 'classes': nclasses, 'folds': nfolds, 'status': 'estimated' if eligible else 'insufficient_support'})
            if not eligible or nfolds < 3:
                continue
            y, pids = df[field].to_numpy(), df.paper_id.to_numpy()
            classes = sorted(df[field].unique())
            designs = {'frequency_baseline': ([], [], True), 'context_only': (list(GROUPS), [], False)}
            if fixed:
                designs['known_evidence_only'] = ([], fixed, False)
                designs['context_plus_known_evidence'] = (list(GROUPS), fixed, False)
            fullname = 'context_plus_known_evidence' if fixed else 'context_only'
            if tier == 'expanded':
                for group in GROUPS:
                    designs['without_' + group] = ([g for g in GROUPS if g != group], fixed, False)
            prepared = {name: feature_dicts(df, gs, fs) for name, (gs, fs, dummy) in designs.items()}
            for repeat in range(REPEATS):
                splits = list(StratifiedGroupKFold(n_splits=nfolds, shuffle=True, random_state=SEED + repeat).split(np.zeros(len(y)), y, pids))
                for fold, (tr, te) in enumerate(splits):
                    overlap = len(set(pids[tr]) & set(pids[te]))
                    assert overlap == 0
                    split_checks.append({'tier': tier, 'target': target, 'repeat': repeat, 'fold': fold, 'train_papers': len(set(pids[tr])), 'test_papers': len(set(pids[te])), 'paper_overlap': overlap, 'missing_train_classes': ';'.join(sorted(set(classes) - set(y[tr])))})
                for name, (gs, fs, dummy) in designs.items():
                    pred = np.empty(len(df), dtype=object)
                    probs = np.zeros((len(df), len(classes)))
                    for fold, (tr, te) in enumerate(splits):
                        vec = DictVectorizer(sparse=True)
                        xtr = vec.fit_transform([prepared[name][i] for i in tr])
                        xte = vec.transform([prepared[name][i] for i in te])
                        model = DummyClassifier(strategy='prior') if dummy else LogisticRegression(C=1.0, solver='lbfgs', max_iter=5000, class_weight='balanced', random_state=SEED)
                        model.fit(xtr, y[tr])
                        pred[te] = model.predict(xte)
                        fold_probs = model.predict_proba(xte)
                        for j, cls in enumerate(model.classes_):
                            probs[te, classes.index(cls)] = fold_probs[:, j]
                    row = {'tier': tier, 'target': target, 'model': name, 'repeat': repeat, 'seed': SEED + repeat, 'n': len(df), 'papers': npapers, 'classes': nclasses, 'folds': nfolds, **metrics(y, pred, probs, classes, pids)}
                    repeat_rows.append(row)
                    if repeat == 0:
                        for i, r in df.iterrows():
                            predictions.append({'tier': tier, 'target': target, 'model': name, 'paper_id': r.paper_id, 'chain_id': r.chain_id, 'instance_id': r.get('measure_instance_id', r.chain_id), 'truth': y[i], 'prediction': pred[i], 'probabilities': json.dumps(dict(zip(classes, probs[i].tolist())))})
            print(tier, target, len(df), npapers, nclasses, flush=True)
    raw = pd.DataFrame(repeat_rows)
    summary = []
    for (tier, target, model), g in raw.groupby(['tier', 'target', 'model'], sort=False):
        row = {'tier': tier, 'target': target, 'model': model, 'n': int(g.n.iloc[0]), 'papers': int(g.papers.iloc[0]), 'classes': int(g.classes.iloc[0]), 'folds': int(g.folds.iloc[0]), 'repeats': len(g)}
        for name in metrics_names:
            row.update({name + '_mean': g[name].mean(), name + '_split_sd': g[name].std(ddof=1), name + '_split_min': g[name].min(), name + '_split_max': g[name].max()})
        summary.append(row)
    ablations = []
    for target, g in raw[raw.tier == 'expanded'].groupby('target', sort=False):
        full = g[g.model == ('context_only' if target == 'perceived_effect_dimension' else 'context_plus_known_evidence')].set_index('repeat')
        for group in GROUPS:
            reduced = g[g.model == 'without_' + group].set_index('repeat')
            if reduced.empty:
                continue
            delta = full.macro_f1 - reduced.macro_f1
            ablations.append({'tier': 'expanded', 'target': target, 'group': group, 'mean_delta_macro_f1': delta.mean(), 'split_sd_delta': delta.std(ddof=1), 'split_min_delta': delta.min(), 'split_max_delta': delta.max(), 'positive_repeats': int((delta > 0).sum()), 'repeats': len(delta)})
    pd.DataFrame(meta).to_csv(OUT / 'task_metadata.csv', index=False)
    pd.DataFrame(class_counts).to_csv(OUT / 'class_support.csv', index=False)
    raw.to_csv(OUT / 'repeat_metrics.csv', index=False)
    pd.DataFrame(summary).to_csv(OUT / 'model_summary.csv', index=False)
    pd.DataFrame(ablations).to_csv(OUT / 'group_ablations.csv', index=False)
    pd.DataFrame(predictions).to_csv(OUT / 'primary_split_predictions.csv', index=False)
    pd.DataFrame(split_checks).to_csv(OUT / 'group_split_checks.csv', index=False)
    protocol = {'source': str(DATA), 'python': platform.python_version(), 'sklearn': sklearn.__version__, 'feature_groups': GROUPS, 'excluded': ['G4 target-derived object code', 'G5 target-derived recoded evaluator role'], 'estimator': 'L2 logistic regression C=1 class_weight=balanced lbfgs max_iter=5000, fixed without model comparison', 'baseline': 'training-fold class frequency prior; additional known-evidence-only baseline for indicator and tool tasks', 'encoding': 'binary multihot DictVectorizer, fit on training fold only; unknown test category ignored', 'validation': '10 repeated StratifiedGroupKFold, seed20261029+repeat, at most5 folds, all rows of paper stay together', 'support': 'at least5 records from3 papers per target class; task requires30 records and2 classes; support filter applied to full corpus to define estimand', 'scoring': 'pooled out-of-fold predictions per repeat; macroF1 explicitly includes all retained target labels; no averaging over variable class sets across folds', 'weighting': 'primary metrics record-weighted; sensitivity metrics weight each paper equally by inverse record count; training not paper weighted', 'uncertainty': 'split SD/range only; no confidence intervals, p values, or normalized importance weights', 'limitations': ['retrospective coding is not independently blinded', 'G5 uses earlier identity-based taxonomy rather than latest role taxonomy', 'small selected quality subset', 'grouped CV does not eliminate publication or missing reporting bias', 'known dimension/indicator assumes these are supplied by the user and is not an end-to-end prediction result', 'tool instances can include multiple classes per chain; estimates are instance-level, not joint multitool recommendations', 'no prospective user evaluation or calibration guarantee']}
    (OUT / 'analysis_protocol.json').write_text(json.dumps(protocol, indent=2, ensure_ascii=False), encoding='utf-8')
    print(pd.DataFrame(summary)[lambda x: ~x.model.str.startswith('without_')][['tier', 'target', 'model', 'n', 'papers', 'classes', 'macro_f1_mean', 'macro_f1_split_sd', 'top2_accuracy_mean']].to_string(index=False), flush=True)

if __name__ == '__main__':
    warnings.filterwarnings('ignore', category=UserWarning)
    run()
