from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "rq3_g1_g7_rebuilt"
FIG = DATA / "figures"

TARGETS = {
    "dimension": ("评价维度", "随机森林"),
    "indicator": ("主观指标", "随机森林"),
    "tool": ("测量工具类别", "直方图梯度提升"),
}
GROUPS = [
    "G1_评价目的",
    "G2_设计领域",
    "G3_设计阶段",
    "G4_评价对象",
    "G5_评价主体",
    "G6_目标用户",
    "G7_AI功能",
]


def load_results() -> pd.DataFrame:
    rows = []
    for key, (target, model) in TARGETS.items():
        d = pd.read_csv(DATA / f"rq3_{key}_weight_stability.csv", encoding="utf-8-sig")
        d["target_key"] = key
        d["target"] = target
        d["selected_model"] = model
        rows.append(d)
    out = pd.concat(rows, ignore_index=True)

    # The two importance estimators have different scales.  Build a transparent
    # recommendation-priority score by normalising positive effects within each
    # method and target, then averaging the two shares.  This score is only for
    # ordering website questions; inference remains based on raw deltas and CIs.
    scored = []
    for _, d in out.groupby("target_key", sort=False):
        d = d.copy()
        drop = d["drop_mean"].clip(lower=0)
        perm = d["permutation_mean"].clip(lower=0)
        d["drop_positive_share"] = drop / drop.sum() if drop.sum() else 0.0
        d["permutation_positive_share"] = perm / perm.sum() if perm.sum() else 0.0
        d["consensus_priority"] = (
            d["drop_positive_share"] + d["permutation_positive_share"]
        ) / 2
        scored.append(d)
    out = pd.concat(scored, ignore_index=True)
    return out


def save_tables(d: pd.DataFrame) -> None:
    d.to_csv(DATA / "rq3_label_group_priority_stable.csv", index=False, encoding="utf-8-sig")
    site = d.copy()
    site.insert(0, "analysis_tier", "扩展规范集")
    site["normalized_weight"] = site["consensus_priority"]
    site["weight_method"] = "20次论文分组CV；正向删组与置换贡献分别归一化后等权平均"
    site[
        [
            "analysis_tier",
            "target",
            "selected_model",
            "feature_group",
            "drop_mean",
            "drop_ci_low",
            "drop_ci_high",
            "permutation_mean",
            "permutation_ci_low",
            "permutation_ci_high",
            "robust_positive",
            "normalized_weight",
            "weight_method",
        ]
    ].to_csv(DATA / "rq3_label_group_weights_stable.csv", index=False, encoding="utf-8-sig")

    threshold = 0.01
    policy = {
        "method": "20次论文级分组交叉验证；删组与测试集置换正向贡献分别归一化后等权平均",
        "default_rule": "两种方法的95%置信区间均高于0，且综合排序权重不低于阈值",
        "supplemental_rule": "综合排序权重不低于阈值，但未通过双重稳健判定",
        "display_threshold": threshold,
        "layers": {},
    }
    for target in ["评价维度", "主观指标", "测量工具类别"]:
        x = d[d.target == target].sort_values("consensus_priority", ascending=False)
        policy["layers"][target] = {
            "core": x[(x.robust_positive == 1) & (x.consensus_priority >= threshold)]["feature_group"].tolist(),
            "supplemental": x[(x.robust_positive != 1) & (x.consensus_priority >= threshold)]["feature_group"].tolist(),
            "excluded_below_threshold": x[x.consensus_priority < threshold]["feature_group"].tolist(),
        }
    (DATA / "rq3_recommender_policy.json").write_text(
        json.dumps(policy, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def setup_font() -> None:
    yahei = Path("C:/Windows/Fonts/msyh.ttc")
    if yahei.exists():
        font_manager.fontManager.addfont(str(yahei))
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False


def priority_heatmap(d: pd.DataFrame) -> None:
    matrix = (
        d.pivot(index="target", columns="feature_group", values="consensus_priority")
        .reindex(["评价维度", "主观指标", "测量工具类别"])
        .reindex(columns=GROUPS)
    )
    robust = (
        d.pivot(index="target", columns="feature_group", values="robust_positive")
        .reindex(index=matrix.index, columns=matrix.columns)
        .fillna(0)
    )
    ann = matrix.copy().astype(object)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix.iloc[i, j] * 100
            star = " ★" if robust.iloc[i, j] == 1 else ""
            ann.iloc[i, j] = f"{v:.1f}%{star}"

    sns.set_theme(style="white")
    setup_font()
    fig, ax = plt.subplots(figsize=(13.4, 5.5), dpi=180)
    sns.heatmap(
        matrix * 100,
        annot=ann,
        fmt="",
        cmap=sns.color_palette("YlGnBu", as_cmap=True),
        vmin=0,
        vmax=100,
        linewidths=0.8,
        linecolor="#f1f2ec",
        cbar_kws={"label": "综合排序权重（%）"},
        annot_kws={"fontsize": 10, "fontweight": "semibold"},
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels([x.replace("_", "\n") for x in matrix.columns], rotation=0, fontsize=10)
    ax.set_yticklabels(["评价维度", "主观指标", "测量工具"], rotation=0, fontsize=11)
    ax.set_title(
        "扩展规范集：重复论文分组验证后的标签综合排序权重",
        loc="left",
        fontsize=16,
        fontweight="bold",
        pad=28,
    )
    ax.text(
        0,
        1.045,
        "20次重复分组交叉验证；删组与测试集置换的正向贡献分别归一化后等权平均。★ 表示两种方法的95%置信区间均高于0。",
        transform=ax.transAxes,
        fontsize=9.5,
        color="#52616b",
        va="bottom",
    )
    fig.tight_layout()
    fig.savefig(FIG / "图_RQ3_G1-G7_标签组权重.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def stability_forest(d: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    setup_font()
    labels = [g.split("_", 1)[1] for g in GROUPS]
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 6.1), dpi=180, sharey=True)
    colors = {"drop": "#235d78", "perm": "#d07a32"}
    for ax, (key, (target, _)) in zip(axes, TARGETS.items()):
        x = d[d.target_key == key].set_index("feature_group").reindex(GROUPS)
        y = np.arange(len(GROUPS))[::-1]
        offsets = {"drop": 0.12, "perm": -0.12}
        for method, mean_col, lo_col, hi_col, label in [
            ("drop", "drop_mean", "drop_ci_low", "drop_ci_high", "删组重训"),
            ("perm", "permutation_mean", "permutation_ci_low", "permutation_ci_high", "测试集置换"),
        ]:
            m = x[mean_col].to_numpy() * 100
            lo = x[lo_col].to_numpy() * 100
            hi = x[hi_col].to_numpy() * 100
            ax.errorbar(
                m,
                y + offsets[method],
                xerr=np.vstack([m - lo, hi - m]),
                fmt="o",
                ms=5,
                capsize=2.5,
                color=colors[method],
                ecolor=colors[method],
                lw=1.3,
                label=label,
                zorder=3,
            )
        ax.axvline(0, color="#27343b", lw=1)
        ax.set_title(target.replace("类别", ""), fontsize=13, fontweight="bold")
        ax.set_xlabel("Δ Macro-F1（百分点）", fontsize=10)
        ax.grid(axis="x", color="#dfe5e8", lw=0.7)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(np.arange(len(GROUPS))[::-1], labels)
    axes[0].legend(loc="lower right", frameon=True, fontsize=9)
    fig.suptitle(
        "G1–G7标签贡献的重复验证与不确定性",
        x=0.06,
        y=0.985,
        ha="left",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.06,
        0.925,
        "点为20次论文级分组交叉验证的平均性能变化，横线为95% bootstrap置信区间；正值表示该标签对预测有帮助。",
        fontsize=9.5,
        color="#52616b",
    )
    fig.tight_layout(rect=[0.03, 0.03, 1, 0.87])
    fig.savefig(FIG / "图_RQ3_G1-G7_权重稳健性核验.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_audit_note(d: pd.DataFrame) -> None:
    table_lines = []
    for target in ["评价维度", "主观指标", "测量工具类别"]:
        x = d[d.target == target].sort_values("consensus_priority", ascending=False)
        parts = [f"{r.feature_group.replace('_', ' ')} {r.consensus_priority*100:.1f}%" for r in x.itertuples()]
        robust = [r.feature_group.replace("_", " ") for r in x.itertuples() if r.robust_positive == 1]
        table_lines.append(
            f"| {target.replace('类别','')} | {'；'.join(parts)} | {'、'.join(robust) if robust else '无'} |"
        )
    note = f"""# RQ3标签权重热力图核验与更正

## 核验结论

原图中的“主观指标—G6目标用户100%”不是数据中存在100%的决定关系，而是旧计算方式产生的归一化假象。旧图只使用一次论文分组交叉验证；将负的删组贡献截为0后，该行只剩G6一个很小的正值（ΔMacro-F1 = 0.019），于是归一化为100%。该值原95%区间为[-0.008, 0.065]，已经跨越0，不能视为稳定贡献。

重新计算使用20次不同随机种子的论文级分组交叉验证，并同时检验：①删去整个标签组后重新训练的性能变化；②在测试集置换该标签组后的性能变化。只有两种方法的95% bootstrap置信区间均高于0，才标记为稳健正向信号。

## 更正后的主要结果

| 推荐层 | 综合排序权重 | 两种检验均稳健的标签组 |
|---|---|---|
{chr(10).join(table_lines)}

主观指标层中，G6目标用户的重复删组均值为{d[(d.target=='主观指标') & (d.feature_group=='G6_目标用户')].drop_mean.iloc[0]:.3f}，95%区间跨0；因此撤回“G6占100%”的结论。该层稳定信号是G1评价目的和G2设计领域。

评价维度层的G4评价对象在两种检验中均保持很高的正向贡献，说明它的集中度有数据依据；但G4与A–E评价维度在定义上相邻，因此该结果应解释为强预测路由信号，不能解释为因果权重。

测量工具层的稳定信号分布在G1评价目的、G2设计领域、G3设计阶段、G6目标用户和G7 AI功能。G4评价对象与G5评价主体只有置换检验区间高于0，删组检验区间跨0，属于探索性信号。

## 图表口径

新的热力图不再把单次删组结果直接称为理论贡献。图中的“综合排序权重”仅用于网页中安排标签提问顺序：对每一推荐层，将两种方法的正向平均贡献分别归一化，再等权平均。置信区间判断仍基于未经归一化的原始ΔMacro-F1。配套的稳健性图直接报告两种原始效应及区间。

## 可复核文件

- `rq3_dimension_weight_stability.csv`、`rq3_indicator_weight_stability.csv`、`rq3_tool_weight_stability.csv`：每种方法的均值、区间和重复为正比例；
- `rq3_label_group_priority_stable.csv`：三层合并结果与综合排序分数；
- `rq3_label_group_weights_stable.csv`：供推荐网页读取的权重表；
- `figures/图_RQ3_G1-G7_标签组权重.png`：更正后的综合排序热力图；
- `figures/图_RQ3_G1-G7_权重稳健性核验.png`：原始效应及95%区间。
"""
    (DATA / "RQ3标签权重热力图核验与更正.md").write_text(note, encoding="utf-8")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    d = load_results()
    save_tables(d)
    priority_heatmap(d)
    stability_forest(d)
    save_audit_note(d)
    summary = {
        t: {
            r.feature_group: round(float(r.consensus_priority), 6)
            for r in d[d.target == t].itertuples()
        }
        for t in d.target.unique()
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
