from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import ROOT, LABELS, STANDARDS


DATA = ROOT / "final_results"
OUT = ROOT / "final_figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "Microsoft YaHei",
    "axes.unicode_minus": False,
    "figure.dpi": 180,
    "savefig.dpi": 320,
    "axes.titleweight": "bold",
})
sns.set_theme(style="whitegrid", font="Microsoft YaHei")
PALETTE = ["#16324F", "#2B6F92", "#4D9D8C", "#E0A458", "#C1666B"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def audit_figure():
    df = pd.read_csv(DATA / "rq2_audit_status.csv")
    piv = df.pivot(index="standard", columns="status", values="percent").fillna(0).reindex(list(STANDARDS))
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    left = np.zeros(len(piv))
    colors = {"S": "#2F7D6D", "P": "#8FC1A9", "C": "#C95D63", "NR": "#B8BDC5", "NA": "#E8EAED"}
    for status in ["S", "P", "C", "NR", "NA"]:
        vals = piv.get(status, pd.Series(0, index=piv.index)).to_numpy()
        ax.barh(range(len(piv)), vals, left=left, label=f"{status} {LABELS['audit_status'][status]}", color=colors[status], edgecolor="white")
        left += vals
    ax.set_yticks(range(len(piv)), [f"{s}  {STANDARDS[s]}" for s in piv.index])
    ax.set_xlim(0, 1)
    ax.set_xticks(np.linspace(0, 1, 6), [f"{x:.0%}" for x in np.linspace(0, 1, 6)])
    ax.set_xlabel("评价案例占比")
    ax.set_title("AI辅助设计中感知评价实践的JCSEE对照审查")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(.5, -0.3), frameon=False)
    save(fig, "图1_JCSEE规范性审查")


def evidence_distribution():
    c = pd.read_csv(DATA / "chains.csv")
    p = pd.read_csv(DATA / "papers.csv")[["paper_id", "year"]]
    c = c.merge(p, on="paper_id", suffixes=("", "_paper"))
    c["year_final"] = pd.to_numeric(c.year_paper.fillna(c.year), errors="coerce")
    c = c[c.dimension_code.isin(LABELS["dimension"])]
    if c.empty:
        return
    bins = pd.cut(c.year_final, bins=[2000, 2018, 2020, 2022, 2024, 2027], labels=["≤2018", "2019–2020", "2021–2022", "2023–2024", "2025–2026"])
    tab = pd.crosstab(bins, c.dimension_code, normalize="index").reindex(columns=list("ABCDE"), fill_value=0)
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    sns.heatmap(tab.T, annot=True, fmt=".0%", cmap=sns.light_palette("#2B6F92", as_cmap=True), cbar_kws={"label": "时期内证据链占比"}, ax=ax)
    ax.set_yticklabels([f"{d} {LABELS['dimension'][d]}" for d in tab.columns], rotation=0)
    ax.set_xlabel("发表时期")
    ax.set_ylabel("评价维度")
    ax.set_title("感知评价证据的时间结构")
    save(fig, "图2_评价证据时间结构")


def association_figure():
    path = DATA / "rq3_associations.csv"
    df = pd.read_csv(path)
    if df.empty:
        return
    d = df[(df.target_field == "dimension") & (df.a_both >= 3)].copy()
    d["strength"] = d.cramers_v_signed.abs()
    d = d.sort_values(["evidence_grade", "strength"], ascending=[True, False]).head(25)
    if d.empty:
        return
    d["pair"] = d.context_label + " → " + d.target_label
    d = d.sort_values("cramers_v_signed")
    fig, ax = plt.subplots(figsize=(10.5, max(5.5, .32 * len(d) + 1.5)))
    colors = d.evidence_grade.map({"较强": "#2F7D6D", "探索性": "#E0A458", "证据不足": "#B8BDC5"})
    ax.scatter(d.cramers_v_signed, range(len(d)), s=40 + 8 * d.a_both, c=colors, alpha=.9, edgecolor="white")
    ax.axvline(0, color="#666", lw=.8)
    ax.set_yticks(range(len(d)), d.pair)
    ax.set_xlabel("有向 Cramér's V（正值表示共同出现）")
    ax.set_title("情境条件与评价维度的关联强度")
    ax.grid(axis="y", visible=False)
    save(fig, "图3_情境与评价维度关联")


def tool_heatmap():
    rec = pd.read_csv(DATA / "recommendations.csv")
    if rec.empty:
        return
    top_ind = rec.groupby("indicator_code").support_chains.sum().nlargest(20).index
    tab = rec[rec.indicator_code.isin(top_ind)].pivot_table(index="indicator_code", columns="tool_code", values="support_chains", aggfunc="sum", fill_value=0)
    tab = tab.reindex(top_ind)
    fig, ax = plt.subplots(figsize=(10.5, max(6, .34*len(tab)+2)))
    sns.heatmap(tab, annot=True, fmt="g", cmap=sns.light_palette("#4D9D8C", as_cmap=True), cbar_kws={"label": "证据链数量"}, ax=ax)
    ax.set_yticklabels([f"{i} {LABELS['indicator'].get(i,i)}" for i in tab.index], rotation=0)
    ax.set_xticklabels([f"{i}\n{LABELS['tool_family'].get(i,i)}" for i in tab.columns], rotation=25, ha="right")
    ax.set_xlabel("测量工具族")
    ax.set_ylabel("主观指标")
    ax.set_title("规范性筛选后指标与工具的经验对应")
    save(fig, "图4_指标与工具对应")


def main():
    audit_figure()
    evidence_distribution()
    association_figure()
    tool_heatmap()


if __name__ == "__main__":
    main()
