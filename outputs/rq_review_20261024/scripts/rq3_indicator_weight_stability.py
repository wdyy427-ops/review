from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import revised_pipeline as rp  # noqa: E402
import rq3_rebuild_g1_g7 as rr  # noqa: E402
from config import LABELS  # noqa: E402


# scikit-learn 1.7 emits one joblib configuration warning for every RF tree
# when an estimator created by the legacy pipeline uses n_jobs != 1.  The
# warning is unrelated to model validity and can generate gigabytes of logs.
warnings.filterwarnings(
    "ignore",
    message="`sklearn.utils.parallel.delayed` should be used.*",
    category=UserWarning,
)


ROOT = SCRIPT_DIR.parent
DATA = ROOT / "rq3_g1_g7_rebuilt"
N_REPEATS = 20
N_PERMUTATIONS = 10


def prepare(kind):
    d = pd.read_csv(DATA / "evidence_chains_context_g1_g7.csv", encoding="utf-8-sig")
    d = d[(d.model_eligible_sensitivity == 1) & d.dimension_code.isin(LABELS["dimension"])].copy()
    if kind == "dimension":
        target_col = "dimension_code"
        fixed = []
    elif kind == "indicator":
        d = d[d.indicator_code.isin(LABELS["indicator"])].copy()
        target_col = "indicator_code"
        fixed = ["dimension_code"]
    elif kind == "tool":
        inst = pd.read_csv(ROOT / "revised_results" / "measure_instances.csv", encoding="utf-8-sig")
        inst = inst[(inst.model_eligible_sensitivity == 1) & inst.tool_code.isin(rp.TOOL_LABELS)].copy()
        context_cols = ["chain_id"] + sorted({c for cols in rr.FEATURE_GROUPS.values() for c in cols})
        inst = inst.drop(columns=[c for c in context_cols if c != "chain_id" and c in inst.columns], errors="ignore")
        d = inst.merge(d[context_cols], on="chain_id", how="inner")
        target_col = "tool_code"
        fixed = ["dimension_code", "indicator_code"]
    else:
        raise ValueError(kind)
    counts = d[target_col].value_counts()
    paper_counts = d[[target_col, "paper_id"]].drop_duplicates()[target_col].value_counts()
    keep = [c for c in counts.index if counts[c] >= 5 and paper_counts.get(c, 0) >= 3]
    d = d[d[target_col].isin(keep)].reset_index(drop=True)
    rp.FEATURE_GROUPS = rr.FEATURE_GROUPS
    x, groups = rp.encode_features(d, fixed)
    return d, x, groups, d[target_col].astype(str), target_col


def score(y_true, pred, labels):
    return f1_score(y_true, pred, labels=labels, average="macro", zero_division=0)


def ci(values, rng):
    values = np.asarray(values, float)
    boot = np.array([rng.choice(values, len(values), replace=True).mean() for _ in range(5000)])
    return float(values.mean()), float(np.quantile(boot, .025)), float(np.quantile(boot, .975))


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "indicator"
    data, x, groups, y, target_col = prepare(kind)
    labels = sorted(y.unique())
    paper_ids = data.paper_id.to_numpy()
    # Fewer trees are sufficient for the RF stability audit and keep repeated
    # grouped refits tractable; final reported RF models retain 400 trees.
    if kind in {"dimension", "indicator"}:
        model_name = "随机森林"
        model = rp.candidate_models()[model_name].set_params(n_estimators=160, n_jobs=1)
    else:
        model_name = "直方图梯度提升"
        model = rp.candidate_models()[model_name]
    rng = np.random.default_rng(20261026)
    drop_by_repeat = {g: [] for g in rr.FEATURE_GROUPS}
    perm_by_repeat = {g: [] for g in rr.FEATURE_GROUPS}
    full_by_repeat = []
    fold_rows = []

    for repeat in range(N_REPEATS):
        class_papers = data[[target_col, "paper_id"]].drop_duplicates().groupby(target_col).paper_id.nunique()
        n_splits = int(min(5, class_papers.min(), data.paper_id.nunique()))
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=20261026 + repeat)
        splits = list(cv.split(x, y, paper_ids))
        full_fold = []
        drop_fold = {g: [] for g in rr.FEATURE_GROUPS}
        perm_fold = {g: [] for g in rr.FEATURE_GROUPS}
        for fold, (tr, te) in enumerate(splits, 1):
            fitted = clone(model).fit(x.iloc[tr], y.iloc[tr])
            base_pred = fitted.predict(x.iloc[te])
            base_score = score(y.iloc[te], base_pred, labels)
            full_fold.append(base_score)
            for g, cols in groups.items():
                if g == "FIXED" or not cols:
                    continue
                keep_cols = [c for c in x.columns if c not in cols]
                reduced = clone(model).fit(x.iloc[tr][keep_cols], y.iloc[tr])
                reduced_score = score(y.iloc[te], reduced.predict(x.iloc[te][keep_cols]), labels)
                drop_fold[g].append(base_score - reduced_score)

                perm_scores = []
                for _ in range(N_PERMUTATIONS):
                    xp = x.iloc[te].copy()
                    order = rng.permutation(len(xp))
                    xp.loc[:, cols] = xp[cols].to_numpy()[order]
                    perm_scores.append(score(y.iloc[te], fitted.predict(xp), labels))
                perm_fold[g].append(base_score - float(np.mean(perm_scores)))
                fold_rows.append(
                    {
                        "repeat": repeat + 1,
                        "fold": fold,
                        "feature_group": g,
                        "full_macro_f1": base_score,
                        "drop_column_delta": base_score - reduced_score,
                        "permutation_delta": base_score - float(np.mean(perm_scores)),
                        "test_n": len(te),
                        "test_papers": data.iloc[te].paper_id.nunique(),
                    }
                )
        full_by_repeat.append(float(np.mean(full_fold)))
        for g in rr.FEATURE_GROUPS:
            drop_by_repeat[g].append(float(np.mean(drop_fold[g])))
            perm_by_repeat[g].append(float(np.mean(perm_fold[g])))

    rows = []
    for g in rr.FEATURE_GROUPS:
        dm, dl, dh = ci(drop_by_repeat[g], rng)
        pm, pl, ph = ci(perm_by_repeat[g], rng)
        rows.append(
            {
                "feature_group": g,
                "drop_mean": dm,
                "drop_ci_low": dl,
                "drop_ci_high": dh,
                "drop_positive_repeat_rate": float(np.mean(np.asarray(drop_by_repeat[g]) > 0)),
                "permutation_mean": pm,
                "permutation_ci_low": pl,
                "permutation_ci_high": ph,
                "permutation_positive_repeat_rate": float(np.mean(np.asarray(perm_by_repeat[g]) > 0)),
            }
        )
    out = pd.DataFrame(rows)
    robust = (out.drop_ci_low > 0) & (out.permutation_ci_low > 0)
    out["robust_positive"] = robust.astype(int)
    raw = out.drop_mean.clip(lower=0).where(robust, 0)
    out["robust_normalized_weight"] = raw / raw.sum() if raw.sum() else 0.0
    out.to_csv(DATA / f"rq3_{kind}_weight_stability.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(fold_rows).to_csv(DATA / f"rq3_{kind}_weight_stability_folds.csv", index=False, encoding="utf-8-sig")
    summary = {
        "target": kind,
        "model": model_name,
        "n": len(data),
        "papers": int(data.paper_id.nunique()),
        "classes": int(y.nunique()),
        "repeats": N_REPEATS,
        "folds_per_repeat": n_splits,
        "permutations_per_group_fold": N_PERMUTATIONS,
        "full_macro_f1_mean": float(np.mean(full_by_repeat)),
        "full_macro_f1_ci": list(ci(full_by_repeat, rng)[1:]),
        "robust_positive_groups": out.loc[out.robust_positive == 1, "feature_group"].tolist(),
    }
    (DATA / f"rq3_{kind}_weight_stability_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(out.to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
