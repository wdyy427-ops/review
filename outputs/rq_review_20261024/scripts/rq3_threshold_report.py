from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "rq3_g1_g7_rebuilt"
FIG = DATA / "figures"


def setup_font():
    p = Path("C:/Windows/Fonts/msyh.ttc")
    if p.exists():
        font_manager.fontManager.addfont(str(p))
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False


def make_figure(curve: pd.DataFrame):
    setup_font()
    targets = ["评价维度", "主观指标", "测量工具类别"]
    fig, axes = plt.subplots(1, 3, figsize=(14.8, 4.9), dpi=180)
    for ax, target in zip(axes, targets):
        d = curve[curve.target == target].sort_values("k")
        x = d.k.to_numpy()
        y = d.macro_f1_mean.to_numpy()
        lo = d.macro_f1_ci_low.to_numpy()
        hi = d.macro_f1_ci_high.to_numpy()
        ax.errorbar(
            x, y, yerr=np.vstack([y - lo, hi - y]), fmt="o-", lw=1.8,
            capsize=3, color="#24647b", markerfacecolor="#fff", markeredgewidth=1.8,
        )
        selected = d[d.selected_by_one_se == 1].iloc[0]
        ax.scatter([selected.k], [selected.macro_f1_mean], s=82, color="#d1782c", zorder=5)
        ax.axhline(selected.best_mean_minus_one_se, color="#8999a2", ls="--", lw=1.1)
        ax.annotate(
            f"选定阈值 {selected.threshold_candidate*100:.1f}%",
            (selected.k, selected.macro_f1_mean), xytext=(0, 13),
            textcoords="offset points", ha="center", fontsize=9, color="#9a551f",
        )
        ax.set_title(target.replace("类别", ""), fontweight="bold", fontsize=13)
        ax.set_xlabel("纳入的稳健标签数（Top-k）")
        ax.set_ylabel("Macro-F1" if ax is axes[0] else "")
        ax.set_xticks(x)
        ax.grid(axis="y", color="#dfe5e8", lw=0.7)
        ax.grid(axis="x", visible=False)
        if len(d) == 1:
            ax.set_xlim(0.55, 1.45)
    fig.suptitle("三层推荐器的权重阈值选择", x=0.055, y=0.985, ha="left", fontsize=16, fontweight="bold")
    fig.text(
        0.055, 0.895,
        "20次论文级分组交叉验证；橙点为一个标准误规则选中的最简组合，虚线为最佳均值减去一个标准误。",
        fontsize=9.5, color="#52616b",
    )
    fig.tight_layout(rect=[0.025, 0.02, 1, 0.82])
    fig.savefig(FIG / "图_RQ3_推荐层阈值选择.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_report(curve: pd.DataFrame, selected: dict):
    layers = selected["layers"]
    rows = []
    for target in ["评价维度", "主观指标", "测量工具类别"]:
        x = layers[target]
        rows.append(
            f"| {target.replace('类别','')} | {x['selected_threshold']*100:.1f}% | "
            f"{'、'.join(g.replace('_',' ') for g in x['selected_groups'])} | "
            f"{x['selected_macro_f1']:.3f} | {x['selected_top2_accuracy']:.3f} |"
        )
    tool = curve[curve.target == "测量工具类别"].sort_values("k")
    indicator = curve[curve.target == "主观指标"].sort_values("k")
    text = f"""# RQ3三层推荐器最佳权重阈值

## 方法

阈值选择只在已经通过删组重训与测试集置换双重稳健性检验的标签中进行。每层按综合排序权重从高到低构造Top-1至Top-k组合，使用20次论文级分组交叉验证比较Macro-F1。最终选择标签数量最少、同时满足下式的组合：

`平均Macro-F1 ≥ 最佳平均Macro-F1 − 最佳组合标准误`

该组合中最低的综合排序权重就是该层核心标签阈值。三个推荐层分别确定阈值，不使用统一的15%。

## 最终阈值

| 推荐层 | 最佳阈值 | 默认核心标签 | Macro-F1 | Top-2准确率 |
|---|---:|---|---:|---:|
{chr(10).join(rows)}

## 结果解释

- **评价维度层：96.7%**。该层只有G4评价对象通过双重稳健检验，因此只有一个候选组合；96.7%是当前数据下的结构性阈值，而不是经过多个候选点竞争产生的通用分界值。
- **主观指标层：27.7%**。只使用G1时Macro-F1为{indicator.iloc[0].macro_f1_mean:.3f}；加入G2后上升至{indicator.iloc[1].macro_f1_mean:.3f}，所以G1和G2都应保留。
- **测量工具层：15.1%**。Top-4组合达到最高Macro-F1 {tool[tool.k==4].iloc[0].macro_f1_mean:.3f}；继续加入权重10.4%的G2后下降至{tool[tool.k==5].iloc[0].macro_f1_mean:.3f}，并低于一个标准误界线{tool.iloc[0].best_mean_minus_one_se:.3f}，所以核心标签止于G6目标用户。

这些阈值直接决定推荐器的运行输入。未达到本层阈值或未通过双重稳健检验的标签不在条件定义界面显示，也不在后台参与匹配与排序；它们只保留在研究结果中用于敏感性分析。

## 可复核文件

- `rq3_threshold_one_se_curves.csv`：每个Top-k组合的均值、标准误、置信区间和选定状态；
- `rq3_threshold_one_se_repeats.csv`：20次重复交叉验证的组合级结果；
- `rq3_threshold_one_se_folds.csv`：每个测试折的原始结果；
- `rq3_threshold_one_se_selected.json`：最终阈值和核心标签；
- `rq3_recommender_policy.json`：推荐器实际读取的分层政策；
- `figures/图_RQ3_推荐层阈值选择.png`：阈值选择曲线。
"""
    (DATA / "RQ3三层推荐器最佳权重阈值.md").write_text(text, encoding="utf-8")


def main():
    FIG.mkdir(exist_ok=True)
    curve = pd.read_csv(DATA / "rq3_threshold_one_se_curves.csv", encoding="utf-8-sig")
    selected = json.loads((DATA / "rq3_threshold_one_se_selected.json").read_text(encoding="utf-8"))
    make_figure(curve)
    make_report(curve, selected)


if __name__ == "__main__":
    main()
