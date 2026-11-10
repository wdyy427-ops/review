from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import f1_score, top_k_accuracy_score
from sklearn.model_selection import StratifiedGroupKFold


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import revised_pipeline as rp  # noqa: E402
import rq3_rebuild_g1_g7 as rr  # noqa: E402
import rq3_indicator_weight_stability as stability  # noqa: E402


warnings.filterwarnings(
    "ignore",
    message="`sklearn.utils.parallel.delayed` should be used.*",
    category=UserWarning,
)

ROOT = SCRIPT_DIR.parent
DATA = ROOT / "rq3_g1_g7_rebuilt"
N_REPEATS = 20
BOOTSTRAPS = 5000
SEED = 20261027

TARGET_NAMES = {
    "dimension": "评价维度",
    "indicator": "主观指标",
    "tool": "测量工具类别",
}


def model_for(kind: str):
    if kind in {"dimension", "indicator"}:
        return rp.candidate_models()["随机森林"].set_params(n_estimators=400, n_jobs=1)
    return rp.candidate_models()["直方图梯度提升"]


def score_macro(y_true, pred, labels):
    return f1_score(y_true, pred, labels=labels, average="macro", zero_division=0)


def bootstrap_ci(values, rng):
    v = np.asarray(values, dtype=float)
    boot = np.asarray([rng.choice(v, len(v), replace=True).mean() for _ in range(BOOTSTRAPS)])
    return float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def evaluate_layer(kind: str, priority: pd.DataFrame):
    data, x, groups, y, target_col = stability.prepare(kind)
    target = TARGET_NAMES[kind]
    p = priority[(priority.target == target) & (priority.robust_positive == 1)].copy()
    p = p.sort_values("consensus_priority", ascending=False)
    order = p.feature_group.tolist()
    weights = p.set_index("feature_group").consensus_priority.to_dict()
    if not order:
        raise RuntimeError(f"{target}没有双重稳健标签，无法选择阈值")

    labels = sorted(y.unique())
    paper_ids = data.paper_id.to_numpy()
    model = model_for(kind)
    repeat_rows = []
    fold_rows = []

    for repeat in range(N_REPEATS):
        class_papers = data[[target_col, "paper_id"]].drop_duplicates().groupby(target_col).paper_id.nunique()
        n_splits = int(min(5, class_papers.min(), data.paper_id.nunique()))
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=SEED + repeat)
        splits = list(cv.split(x, y, paper_ids))
        scores = {k: [] for k in range(1, len(order) + 1)}
        top2 = {k: [] for k in range(1, len(order) + 1)}
        for fold, (tr, te) in enumerate(splits, 1):
            for k in range(1, len(order) + 1):
                selected = order[:k]
                cols = list(groups.get("FIXED", []))
                for g in selected:
                    cols.extend(groups.get(g, []))
                cols = list(dict.fromkeys(cols))
                fitted = clone(model).fit(x.iloc[tr][cols], y.iloc[tr])
                pred = fitted.predict(x.iloc[te][cols])
                macro = score_macro(y.iloc[te], pred, labels)
                if hasattr(fitted, "predict_proba"):
                    prob = fitted.predict_proba(x.iloc[te][cols])
                    t2 = top_k_accuracy_score(
                        y.iloc[te], prob, k=min(2, len(fitted.classes_)), labels=fitted.classes_
                    )
                else:
                    t2 = np.nan
                scores[k].append(macro)
                top2[k].append(t2)
                fold_rows.append(
                    {
                        "target": target,
                        "repeat": repeat + 1,
                        "fold": fold,
                        "k": k,
                        "included_groups": ";".join(selected),
                        "threshold_candidate": weights[selected[-1]],
                        "macro_f1": macro,
                        "top2_accuracy": t2,
                        "test_n": len(te),
                        "test_papers": int(data.iloc[te].paper_id.nunique()),
                    }
                )
        for k in scores:
            repeat_rows.append(
                {
                    "target": target,
                    "repeat": repeat + 1,
                    "k": k,
                    "included_groups": ";".join(order[:k]),
                    "threshold_candidate": weights[order[k - 1]],
                    "macro_f1": float(np.mean(scores[k])),
                    "top2_accuracy": float(np.nanmean(top2[k])),
                }
            )

    rep = pd.DataFrame(repeat_rows)
    rng = np.random.default_rng(SEED + {"dimension": 1, "indicator": 2, "tool": 3}[kind])
    summary = []
    for k, z in rep.groupby("k", sort=True):
        ci_low, ci_high = bootstrap_ci(z.macro_f1.to_numpy(), rng)
        summary.append(
            {
                "target": target,
                "k": int(k),
                "included_groups": z.included_groups.iloc[0],
                "threshold_candidate": float(z.threshold_candidate.iloc[0]),
                "macro_f1_mean": float(z.macro_f1.mean()),
                "macro_f1_sd": float(z.macro_f1.std(ddof=1)) if len(z) > 1 else 0.0,
                "macro_f1_se": float(z.macro_f1.std(ddof=1) / np.sqrt(len(z))) if len(z) > 1 else 0.0,
                "macro_f1_ci_low": ci_low,
                "macro_f1_ci_high": ci_high,
                "top2_accuracy_mean": float(z.top2_accuracy.mean()),
                "repeats": int(len(z)),
                "folds_per_repeat": int(n_splits),
            }
        )
    curve = pd.DataFrame(summary)
    best = curve.loc[curve.macro_f1_mean.idxmax()]
    cutoff = float(best.macro_f1_mean - best.macro_f1_se)
    eligible = curve[curve.macro_f1_mean >= cutoff]
    selected = eligible.sort_values("k").iloc[0]
    curve["best_mean_minus_one_se"] = cutoff
    curve["selected_by_one_se"] = (curve.k == int(selected.k)).astype(int)
    curve["delta_from_best"] = curve.macro_f1_mean - float(best.macro_f1_mean)
    result = {
        "target": target,
        "n": int(len(data)),
        "papers": int(data.paper_id.nunique()),
        "classes": int(y.nunique()),
        "robust_order": order,
        "best_k": int(best.k),
        "best_macro_f1": float(best.macro_f1_mean),
        "best_standard_error": float(best.macro_f1_se),
        "one_se_cutoff": cutoff,
        "selected_k": int(selected.k),
        "selected_groups": order[: int(selected.k)],
        "selected_threshold": float(weights[order[int(selected.k) - 1]]),
        "selected_macro_f1": float(selected.macro_f1_mean),
        "selected_top2_accuracy": float(selected.top2_accuracy_mean),
    }
    return curve, pd.DataFrame(fold_rows), rep, result


def main():
    priority = pd.read_csv(DATA / "rq3_label_group_priority_stable.csv", encoding="utf-8-sig")
    curves, folds, repeats, results = [], [], [], []
    for kind in ["dimension", "indicator", "tool"]:
        c, f, r, result = evaluate_layer(kind, priority)
        curves.append(c); folds.append(f); repeats.append(r); results.append(result)

    curve = pd.concat(curves, ignore_index=True)
    curve.to_csv(DATA / "rq3_threshold_one_se_curves.csv", index=False, encoding="utf-8-sig")
    pd.concat(folds, ignore_index=True).to_csv(
        DATA / "rq3_threshold_one_se_folds.csv", index=False, encoding="utf-8-sig"
    )
    pd.concat(repeats, ignore_index=True).to_csv(
        DATA / "rq3_threshold_one_se_repeats.csv", index=False, encoding="utf-8-sig"
    )
    payload = {
        "selection_method": "20次论文级分组交叉验证；双重稳健标签按综合权重排序；一个标准误规则选择最小Top-k",
        "one_se_rule": "选择最小k，使其平均Macro-F1不低于最佳平均Macro-F1减去最佳模型的标准误",
        "layers": {x["target"]: x for x in results},
    }
    (DATA / "rq3_threshold_one_se_selected.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Persist the selected layer-specific thresholds into the table consumed by
    # the recommender, while retaining robustness as a separate property.
    weights_path = DATA / "rq3_label_group_weights_stable.csv"
    weights = pd.read_csv(weights_path, encoding="utf-8-sig")
    selected_lookup = {x["target"]: set(x["selected_groups"]) for x in results}
    threshold_lookup = {x["target"]: x["selected_threshold"] for x in results}
    weights["one_se_threshold"] = weights.target.map(threshold_lookup)
    weights["selected_core"] = [
        int(g in selected_lookup.get(t, set()))
        for t, g in zip(weights.target, weights.feature_group)
    ]
    weights["selection_state"] = [
        "核心标签" if core == 1 else (
            "稳健补充标签" if robust == 1 else (
                "探索性补充标签" if w >= 0.01 else "低于显示阈值"
            )
        )
        for core, robust, w in zip(
            weights.selected_core, weights.robust_positive, weights.normalized_weight
        )
    ]
    weights.to_csv(weights_path, index=False, encoding="utf-8-sig")

    policy = {
        "method": payload["selection_method"],
        "runtime_mode": "仅核心标签参与推荐；补充标签不显示且不计分",
        "core_rule": "双重稳健，且进入一个标准误规则选择的最简Top-k组合",
        "supplemental_rule": "仅保留作敏感性分析，不进入推荐器运行逻辑",
        "display_floor": 0.01,
        "layers": {},
    }
    for result in results:
        target = result["target"]
        z = weights[weights.target == target].sort_values("normalized_weight", ascending=False)
        policy["layers"][target] = {
            "one_se_threshold": result["selected_threshold"],
            "core": z[z.selected_core == 1].feature_group.tolist(),
            "stable_supplemental": z[
                (z.selected_core != 1) & (z.robust_positive == 1) & (z.normalized_weight >= 0.01)
            ].feature_group.tolist(),
            "exploratory_supplemental": z[
                (z.robust_positive != 1) & (z.normalized_weight >= 0.01)
            ].feature_group.tolist(),
            "excluded_below_display_floor": z[z.normalized_weight < 0.01].feature_group.tolist(),
            "selected_macro_f1": result["selected_macro_f1"],
            "best_macro_f1": result["best_macro_f1"],
            "one_se_cutoff": result["one_se_cutoff"],
        }
    (DATA / "rq3_recommender_policy.json").write_text(
        json.dumps(policy, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
