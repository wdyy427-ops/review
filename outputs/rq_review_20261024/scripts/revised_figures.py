from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import ROOT, LABELS, INDICATORS
from revised_pipeline import TOOL_LABELS, AUDIT_LABELS, STATUS_LABELS


DATA = ROOT / "revised_results"
OUT = ROOT / "revised_figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "Microsoft YaHei",
    "axes.unicode_minus": False,
    "figure.dpi": 180,
    "savefig.dpi": 320,
    "axes.titleweight": "bold",
    "axes.titlesize": 15,
    "axes.labelsize": 11,
})
sns.set_theme(style="whitegrid", font="Microsoft YaHei")
COLORS = {"A":"#214761", "B":"#3F7C85", "C":"#6A9F74", "D":"#D8A247", "E":"#B75D69"}
TOOL_COLORS = {"M1":"#214761", "M2":"#3F7C85", "M3":"#6A9F74", "M4":"#D8A247", "M5":"#B75D69"}


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def line_panel(df, labels, colors, title, name, unit_note):
    years = sorted(df.year.unique())
    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    for code, label in labels.items():
        sub = df[df.code == code].sort_values("year")
        axes[0].plot(sub.year, sub.n, marker="o", lw=2.2, color=colors[code], label=f"{code} {label}")
        axes[1].plot(sub.year, sub.percent * 100, marker="o", lw=2.2, color=colors[code], label=f"{code} {label}")
    axes[0].set_ylabel("数量")
    axes[1].set_ylabel("当年占比（%）")
    axes[1].set_xlabel("发表年份")
    axes[1].set_xticks(years)
    axes[0].set_title(title, loc="left")
    axes[0].legend(ncol=2, frameon=False, loc="upper left")
    axes[1].text(0, -0.25, unit_note, transform=axes[1].transAxes, fontsize=9, color="#555")
    for ax in axes:
        ax.grid(axis="x", visible=False)
        ax.spines[["top", "right"]].set_visible(False)
    save(fig, name)


def dimension_trend():
    df = pd.read_csv(DATA / "rq1_dimension_by_year.csv")
    line_panel(df, LABELS["dimension"], COLORS,
               "RQ1：五类感知评价维度的年度变化",
               "图01_评价维度年度趋势",
               "单位：已映射评价维度的证据链；上图为数量，下图为当年构成比。")


def indicator_trends():
    df = pd.read_csv(DATA / "rq1_indicator_by_year.csv")
    for dim in "ABCDE":
        codes = [f"{dim}{i}" for i in range(1, len(INDICATORS[dim]) + 1)]
        sub = df[df.code.isin(codes)].copy()
        fig, axes = plt.subplots(2, 1, figsize=(11.5, 9), sharex=True)
        palette = sns.color_palette("husl", len(codes))
        for code, color in zip(codes, palette):
            s = sub[sub.code == code].sort_values("year")
            label = f"{code} {LABELS['indicator'][code]}"
            axes[0].plot(s.year, s.n, marker="o", lw=1.9, color=color, label=label)
            axes[1].plot(s.year, s.percent * 100, marker="o", lw=1.9, color=color, label=label)
        axes[0].set_title(f"RQ1：{dim}类“{LABELS['dimension'][dim]}”指标的年度变化", loc="left")
        axes[0].set_ylabel("数量")
        axes[1].set_ylabel("当年全部已映射指标中的占比（%）")
        axes[1].set_xlabel("发表年份")
        axes[1].set_xticks(sorted(sub.year.unique()))
        axes[0].legend(ncol=2, frameon=False, loc="upper left", fontsize=9)
        axes[1].text(0, -0.25, "单位：已映射主观指标的证据链；零值保留，以显示新出现或暂未使用的指标。", transform=axes[1].transAxes, fontsize=9, color="#555")
        for ax in axes:
            ax.grid(axis="x", visible=False)
            ax.spines[["top", "right"]].set_visible(False)
        save(fig, f"图02{dim}_{dim}类指标年度趋势")


def tool_trend():
    df = pd.read_csv(DATA / "rq1_tool_by_year.csv")
    line_panel(df, TOOL_LABELS, TOOL_COLORS,
               "RQ1：五类测量工具的年度变化",
               "图03_测量工具年度趋势",
               "单位：可判定类别的测量工具实例；一条证据链可包含多个工具实例。")


def context_heatmap(kind, title, name):
    df = pd.read_csv(DATA / f"rq1_{kind}_dimension_cells.csv")
    index_codes = list(LABELS[kind])
    mat = df.pivot(index="context_code", columns="dimension_code", values="row_percent").reindex(index=index_codes, columns=list("ABCDE")) * 100
    counts = df.pivot(index="context_code", columns="dimension_code", values="n").reindex(index=index_codes, columns=list("ABCDE"))
    annot = counts.fillna(0).astype(int).astype(str) + "\n" + mat.fillna(0).map(lambda x: f"{x:.1f}%")
    fig, ax = plt.subplots(figsize=(11, 1.0 + .72 * len(index_codes)))
    sns.heatmap(mat, annot=annot, fmt="", cmap="YlGnBu", vmin=0, vmax=max(55, np.nanmax(mat.values)), cbar_kws={"label":"该情境内的维度占比（%）"}, linewidths=.6, linecolor="white", ax=ax)
    ax.set_yticklabels([f"{c} {LABELS[kind][c]}" for c in index_codes], rotation=0)
    ax.set_xticklabels([f"{c}\n{LABELS['dimension'][c]}" for c in "ABCDE"], rotation=0)
    ax.set_xlabel("评价维度")
    ax.set_ylabel("")
    ax.set_title(title, loc="left")
    save(fig, name)


def audit_figure():
    df = pd.read_csv(DATA / "rq2_chain_audit_summary.csv", keep_default_na=False)
    piv = df.pivot(index="standard", columns="status", values="percent").fillna(0).reindex(list(AUDIT_LABELS))
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    left = np.zeros(len(piv))
    colors = {"S":"#26765D", "P":"#8DC3AC", "C":"#C94B50", "NR":"#A9AFB8", "NA":"#E7E9EC"}
    for status in ["S", "P", "C", "NR", "NA"]:
        vals = piv[status].to_numpy() if status in piv else np.zeros(len(piv))
        ax.barh(np.arange(len(piv)), vals * 100, left=left * 100, color=colors[status], edgecolor="white", label=f"{status} {STATUS_LABELS[status]}")
        for i, (v, l) in enumerate(zip(vals, left)):
            if v >= .045:
                ax.text((l + v/2)*100, i, f"{v:.1%}", ha="center", va="center", fontsize=8, color="#1F2933")
        left += vals
    ax.set_yticks(np.arange(len(piv)), [f"{s}  {AUDIT_LABELS[s]}" for s in piv.index])
    ax.set_xlim(0, 100)
    ax.set_xlabel("490条评价证据链中的比例（%）")
    ax.set_title("RQ2：以证据链为单位的JCSEE对照审查", loc="left")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(.5, -0.29), frameon=False)
    ax.grid(axis="y", visible=False)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "图05_JCSEE证据链规范性审查")


def weights_figure():
    df = pd.read_csv(DATA / "rq3_label_group_weights.csv")
    df = df[df.analysis_tier == "扩展规范集"].copy()
    targets = ["评价维度", "主观指标", "测量工具类别"]
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 6), sharey=True)
    order = ["G1_评价目的", "G2_效果主张形式", "G3_评价对象", "G4_设计情境", "G5_相关人的价值", "G6_可信证据可行条件", "G7_AI活动特征"]
    short = {"G1_评价目的":"评价目的", "G2_效果主张形式":"效果主张形式", "G3_评价对象":"评价对象", "G4_设计情境":"设计情境", "G5_相关人的价值":"评价主体与用户", "G6_可信证据可行条件":"数据源与可行条件", "G7_AI活动特征":"AI角色、功能与任务"}
    for ax, target in zip(axes, targets):
        s = df[df.target == target].set_index("feature_group").reindex(order)
        vals = s.normalized_weight.fillna(0) * 100
        colors = ["#2B6F92" if v > 0 else "#D7DBE0" for v in vals]
        ax.barh(np.arange(len(order)), vals, color=colors)
        ax.set_title(target)
        ax.set_xlabel("归一化消融权重（%）")
        ax.set_xlim(0, max(50, vals.max() * 1.15))
        for i, v in enumerate(vals):
            if v > 0:
                ax.text(v + .7, i, f"{v:.1f}%", va="center", fontsize=8)
        ax.grid(axis="y", visible=False)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_yticks(np.arange(len(order)), [short[x] for x in order])
    fig.suptitle("RQ3：设计师标签组对三级推荐目标的增量贡献", fontsize=16, fontweight="bold", x=.5, y=1.02)
    fig.text(.5, -.02, "扩展规范集；按论文分组交叉验证。权重仅表示本数据中移除标签组后Macro-F1的相对下降，不解释因果。", ha="center", fontsize=9, color="#555")
    save(fig, "图06_RQ3标签组权重")


def model_figure():
    df = pd.read_csv(DATA / "rq3_model_comparison.csv")
    df = df[df.analysis_tier == "扩展规范集"].copy()
    fig, axes = plt.subplots(1, 3, figsize=(15.2, 5.2), sharey=True)
    target_order = ["评价维度", "主观指标", "测量工具类别"]
    model_order = ["频率基线", "L2多项逻辑回归", "随机森林", "直方图梯度提升"]
    palette = ["#A9AFB8", "#2B6F92", "#4D9D8C", "#D8A247"]
    for ax, target in zip(axes, target_order):
        s = df[df.target == target].set_index("model").reindex(model_order)
        vals = s.macro_f1_mean.fillna(0)
        ax.bar(np.arange(len(model_order)), vals, color=palette)
        ax.set_xticks(np.arange(len(model_order)), ["基线", "L2逻辑回归", "随机森林", "梯度提升"], rotation=22, ha="right")
        ax.set_title(target)
        ax.set_ylim(0, .65)
        ax.set_ylabel("Macro-F1" if ax is axes[0] else "")
        for i, v in enumerate(vals):
            ax.text(i, v + .012, f"{v:.2f}", ha="center", fontsize=9)
        ax.grid(axis="x", visible=False)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("RQ3：候选模型的论文分组交叉验证表现", fontsize=16, fontweight="bold", y=1.02)
    save(fig, "图07_RQ3模型交叉验证")


def main():
    dimension_trend()
    indicator_trends()
    tool_trend()
    context_heatmap("domain", "RQ1：评价维度在六类设计领域中的构成", "图04A_设计领域与评价维度")
    context_heatmap("stage", "RQ1：评价维度在四个设计阶段中的构成", "图04B_设计阶段与评价维度")
    audit_figure()
    weights_figure()
    model_figure()


if __name__ == "__main__":
    main()
