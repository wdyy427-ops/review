from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "rq_review_20261024" / "supplement_enhanced_v2" / "06_RQ3"
OUT = ROOT / "figures"
TABLES = ROOT / "figure_data"
OUT.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 8.3,
        "axes.labelsize": 8.3,
        "axes.titlesize": 9.4,
        "axes.linewidth": 0.65,
        "xtick.labelsize": 7.7,
        "ytick.labelsize": 7.7,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "text.color": "#222222",
        "axes.labelcolor": "#222222",
        "axes.edgecolor": "#555555",
        "xtick.color": "#444444",
        "ytick.color": "#444444",
    }
)

MODEL_FILE = DATA / "rq3_model_comparison_g1_g7.csv"
WEIGHT_FILE = DATA / "rq3_label_group_weights_stable.csv"

models = pd.read_csv(MODEL_FILE, keep_default_na=False)
weights = pd.read_csv(WEIGHT_FILE, keep_default_na=False)

models = models[models["analysis_tier"] == "扩展规范集"].copy()

target_order = ["评价维度", "主观指标", "测量工具类别"]
target_titles = {
    "评价维度": "Evaluation dimensions",
    "主观指标": "Subjective indicators",
    "测量工具类别": "Tool classes",
}
panel_letters = {"评价维度": "a", "主观指标": "b", "测量工具类别": "c"}
model_order = ["频率基线", "L2多项逻辑回归", "随机森林", "直方图梯度提升"]
model_labels = {
    "频率基线": "Frequency baseline",
    "L2多项逻辑回归": "L2 logistic regression",
    "随机森林": "Random forest",
    "直方图梯度提升": "Histogram gradient boosting",
}
model_colors = {
    "频率基线": "#A7ADB2",
    "L2多项逻辑回归": "#4477AA",
    "随机森林": "#228833",
    "直方图梯度提升": "#D99A32",
}


def clean_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E9E9E9", linewidth=0.55)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=3, width=0.6)


# Figure A: algorithm comparison and model selection.
fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.45), sharey=True)
fig.subplots_adjust(left=0.075, right=0.99, top=0.80, bottom=0.32, wspace=0.30)

best_rows = []
for ax, target in zip(axes, target_order):
    sub = models[models["target"] == target].set_index("model").reindex(model_order).reset_index()
    x = np.arange(len(sub))
    values = sub["macro_f1_mean"].astype(float).to_numpy()
    errors = sub["macro_f1_sd"].astype(float).to_numpy()
    bars = ax.bar(
        x,
        values,
        yerr=errors,
        capsize=2.4,
        width=0.66,
        color=[model_colors[m] for m in sub["model"]],
        edgecolor="white",
        linewidth=0.5,
        error_kw={"elinewidth": 0.75, "ecolor": "#555555", "capthick": 0.75},
    )
    nonbaseline = sub[sub["model"] != "频率基线"]
    best_idx = nonbaseline["macro_f1_mean"].astype(float).idxmax()
    best = sub.loc[best_idx]
    best_rows.append(best)
    bars[best_idx].set_edgecolor("#111111")
    bars[best_idx].set_linewidth(1.25)
    for i, (bar, value) in enumerate(zip(bars, values)):
        marker = "*" if i == best_idx else ""
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + errors[i] + 0.018,
            f"{value:.3f}{marker}",
            ha="center",
            va="bottom",
            fontsize=7.2,
            weight="bold" if i == best_idx else "normal",
        )
    ax.set_xticks(x, ["Baseline", "L2", "RF", "HGB"])
    ax.set_ylim(0, 0.76)
    ax.set_yticks([0, 0.2, 0.4, 0.6])
    ax.set_xlabel("Model")
    clean_axis(ax)
    ax.text(-0.10, 1.20, panel_letters[target], transform=ax.transAxes, fontsize=11, weight="bold", va="bottom")
    ax.text(0.00, 1.20, target_titles[target], transform=ax.transAxes, fontsize=9.4, va="bottom")
    meta = sub.iloc[0]
    unit = "instances" if target == "测量工具类别" else "records"
    ax.text(
        0.00,
        1.055,
        f"{int(meta['n'])} {unit}; {int(meta['papers'])} papers\n{int(meta['classes'])} classes; {int(meta['folds'])}-fold CV",
        transform=ax.transAxes,
        fontsize=7.1,
        va="bottom",
        linespacing=1.25,
        color="#555555",
    )

axes[0].set_ylabel("Macro-F1 (mean ± SD)")
fig.text(
    0.075,
    0.13,
    "Baseline = frequency baseline; RF = random forest; HGB = histogram gradient boosting.",
    fontsize=7.2,
    color="#555555",
)
fig.text(
    0.075,
    0.075,
    "Black outline and * identify the highest-Macro-F1 non-baseline model for each target.",
    fontsize=7.2,
    color="#555555",
)

stem = OUT / "figXX_rq3_model_selection"
for ext in ("png", "pdf", "svg"):
    fig.savefig(stem.with_suffix(f".{ext}"), dpi=400, bbox_inches="tight", pad_inches=0.04)
plt.close(fig)

# Export the selected-model table used between the two figures.
best = pd.DataFrame(best_rows)
best["target_en"] = best["target"].map(target_titles)
best["model_en"] = best["model"].map(model_labels)
best_table = best[
    [
        "target_en",
        "model_en",
        "n",
        "papers",
        "classes",
        "folds",
        "macro_f1_mean",
        "macro_f1_sd",
        "balanced_accuracy_mean",
        "accuracy_mean",
        "top2_accuracy_mean",
    ]
].copy()
best_table.to_csv(TABLES / "tableXX_rq3_selected_models.csv", index=False, encoding="utf-8-sig")

# Figure B: group deletion and held-out test-set permutation for selected models.
group_order = [
    "G1_评价目的",
    "G2_设计领域",
    "G3_设计阶段",
    "G4_评价对象",
    "G5_评价主体",
    "G6_目标用户",
    "G7_AI功能",
]
group_labels = {
    "G1_评价目的": "G1  Evaluation purpose",
    "G2_设计领域": "G2  Design domain",
    "G3_设计阶段": "G3  Design stage",
    "G4_评价对象": "G4  Evaluation object",
    "G5_评价主体": "G5  Evaluators",
    "G6_目标用户": "G6  Target users",
    "G7_AI功能": "G7  AI function",
}
xlimits = {
    "评价维度": (-0.065, 0.395),
    "主观指标": (-0.04, 0.085),
    "测量工具类别": (-0.03, 0.095),
}
xticks = {
    "评价维度": [0.0, 0.1, 0.2, 0.3],
    "主观指标": [-0.025, 0.0, 0.025, 0.05, 0.075],
    "测量工具类别": [-0.025, 0.0, 0.025, 0.05, 0.075],
}

fig, axes = plt.subplots(1, 3, figsize=(7.2, 4.45))
fig.subplots_adjust(left=0.245, right=0.99, top=0.82, bottom=0.22, wspace=0.37)

for j, (ax, target) in enumerate(zip(axes, target_order)):
    sub = weights[weights["target"] == target].set_index("feature_group").reindex(group_order).reset_index()
    y = np.arange(len(sub))
    drop = sub["drop_mean"].astype(float).to_numpy()
    drop_low = sub["drop_ci_low"].astype(float).to_numpy()
    drop_high = sub["drop_ci_high"].astype(float).to_numpy()
    perm = sub["permutation_mean"].astype(float).to_numpy()
    perm_low = sub["permutation_ci_low"].astype(float).to_numpy()
    perm_high = sub["permutation_ci_high"].astype(float).to_numpy()
    robust = sub["robust_positive"].astype(int).to_numpy()

    ax.axvline(0, color="#777777", linewidth=0.8, linestyle="--", zorder=0)
    ax.errorbar(
        drop,
        y - 0.12,
        xerr=np.vstack([drop - drop_low, drop_high - drop]),
        fmt="o",
        markersize=4.2,
        color="#4477AA",
        ecolor="#4477AA",
        elinewidth=0.9,
        capsize=2,
        label="Group-deletion retraining",
        zorder=3,
    )
    ax.errorbar(
        perm,
        y + 0.12,
        xerr=np.vstack([perm - perm_low, perm_high - perm]),
        fmt="D",
        markersize=3.7,
        color="#D9772B",
        ecolor="#D9772B",
        elinewidth=0.9,
        capsize=2,
        label="Test-set permutation",
        zorder=3,
    )
    labels = [group_labels[g] + ("  *" if robust[i] else "") for i, g in enumerate(group_order)]
    ax.set_yticks(y, labels if j == 0 else [f"G{i+1}" + (" *" if robust[i] else "") for i in range(7)])
    ax.invert_yaxis()
    ax.set_xlim(*xlimits[target])
    ax.set_xticks(xticks[target])
    ax.set_xlabel("ΔMacro-F1")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#ECECEC", linewidth=0.55)
    ax.set_axisbelow(True)
    ax.text(-0.10, 1.20, panel_letters[target], transform=ax.transAxes, fontsize=11, weight="bold", va="bottom")
    ax.text(0.00, 1.20, target_titles[target], transform=ax.transAxes, fontsize=9.4, va="bottom")
    selected = sub.iloc[0]["selected_model"]
    ax.text(
        0.00,
        1.075,
        f"Selected model: {model_labels[selected]}",
        transform=ax.transAxes,
        fontsize=7.1,
        va="bottom",
        color="#555555",
    )

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.245, 0.075), frameon=False, ncol=2, fontsize=7.6)
fig.text(
    0.245,
    0.035,
    "Positive values indicate lower performance after disruption. * Both 95% bootstrap CIs are above zero.",
    fontsize=7.1,
    color="#555555",
)

stem = OUT / "figXX_rq3_group_contributions"
for ext in ("png", "pdf", "svg"):
    fig.savefig(stem.with_suffix(f".{ext}"), dpi=400, bbox_inches="tight", pad_inches=0.04)
plt.close(fig)

# Retain a compact source table for the contribution figure.
weights.to_csv(TABLES / "tableXX_rq3_group_contributions.csv", index=False, encoding="utf-8-sig")

