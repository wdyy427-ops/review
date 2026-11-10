from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config import ROOT, LABELS, STANDARDS, SOURCE_URLS


DATA = ROOT / "final_results"
OUT = ROOT / "AI辅助设计感知效应_系统综述与推荐建模报告.md"


def pct(n, d):
    return f"{n}（{n/d:.1%}）" if d else f"{n}"


def md_table(df, cols, headers=None, digits=3):
    if df.empty:
        return "无可报告结果。"
    headers = headers or cols
    rows = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        vals = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, float):
                v = "" if pd.isna(v) else f"{v:.{digits}f}"
            vals.append(str(v).replace("|", "／").replace("\n", " "))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join(rows)


def main():
    s = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    rq1 = pd.read_csv(DATA / "rq1_distributions.csv")
    tiers = pd.read_csv(DATA / "rq2_quality_tiers.csv")
    status = pd.read_csv(DATA / "rq2_audit_status.csv")
    assoc = pd.read_csv(DATA / "rq3_associations.csv")
    models = pd.read_csv(DATA / "rq3_model_comparison.csv")
    recs = pd.read_csv(DATA / "recommendations.csv")
    papers = pd.read_csv(DATA / "papers.csv")
    chains = pd.read_csv(DATA / "chains.csv")

    def top_dist(field, k=10):
        d = rq1[rq1.variable == field].copy().sort_values("n", ascending=False).head(k)
        d["占比"] = d.percent.map(lambda x: f"{x:.1%}")
        return md_table(d, ["code", "label", "n", "denominator", "占比"], ["代码", "类别", "n", "分母", "占比"])

    st = status.copy()
    st["占比"] = st.percent.map(lambda x: f"{x:.1%}")
    st_wide = st.pivot(index=["standard", "standard_label"], columns="status", values="占比").reset_index().fillna("0.0%")

    top_assoc = assoc[(assoc.evidence_grade != "证据不足") & (assoc.a_both >= 3)].head(20).copy()
    if len(top_assoc):
        top_assoc["P(结果|情境)"] = top_assoc.conditional_probability.map(lambda x: f"{x:.1%}")
        top_assoc["基线"] = top_assoc.baseline_probability.map(lambda x: f"{x:.1%}")

    best_models = models.sort_values(["target", "macro_f1_mean"], ascending=[True, False]) if "macro_f1_mean" in models else models
    top_recs = recs.sort_values(["support_papers", "conditional_probability"], ascending=[False, False]).head(25).copy() if len(recs) else recs
    if len(top_recs):
        top_recs["经验概率"] = top_recs.conditional_probability.map(lambda x: f"{x:.1%}")
        def compact_examples(value):
            parts = [" ".join(x.split()) for x in str(value or "").split("；") if x and x not in {"NR", "UNMAPPED"}]
            parts = [(x[:89] + "…") if len(x) > 90 else x for x in parts[:2]]
            return "；".join(parts) or "—"
        top_recs["example_instruments"] = top_recs.example_instruments.fillna("").map(compact_examples)

    text = f"""# AI-assisted Design Workflow 中 Perceived Effect 评价实践：系统综述、规范性审查与推荐建模

## 研究范围与最终数据

本研究对用户提供的 125 篇全文重新编码。旧工作簿只用于保留已经确定的固定分类，不把旧表中的效果主张、构念、指标、工具或评价结果当作事实来源。全文证据链按 **Evaluation Question／效果主张 → Construct／感知构念 → Indicator／主观指标 → Measure／测量工具** 记录，情境条件按评价目的、对象、环境、评价主体、目标用户、数据源、设计阶段、任务及 AI 角色与功能记录。

最终数据包括 {s['papers']} 篇论文，其中 {pct(s['papers_with_human_subjective_evaluation'], s['papers'])} 经全文筛查确认含有人类主观感知评价；共形成 {s['evaluations']} 个评价案例和 {s['chains']} 条可追溯证据链。12 篇由逐页人工复核结果覆盖，113 篇采用“全文规则筛查＋高相关证据页语义清点＋PDF原句回定位”的组合流程。自动流程只保留能重新定位到原文页码的证据链。后续正式投稿前仍建议由两名研究者进行独立复核和一致性检验。

### 固定分类

- 设计领域：ICoD 六类。
- 设计阶段：ICoD 四阶段。
- AI 功能：识别需求、知识检索、方案生成、原型实现、评估反馈、迭代优化。
- 评价维度：设计成果质量、设计过程质量、设计者认知情感与能力、人机交互体验、社会情境价值。
- 评价目的：价值引出与标准建构、模型监督／校准与代理目标、形成性反馈与迭代引导、总结性验证与比较。
- 无法可靠归入固定二级分类的内容标为 `UNMAPPED`，没有因量化需要而临时创造新类别。

## RQ1 评价证据的分布

### 发表年份

{top_dist('year', 30)}

### 设计领域

{top_dist('domain')}

### 设计阶段

{top_dist('stage')}

### AI 功能

{top_dist('ai_function')}

### Perceived effect 评价维度

{top_dist('dimension')}

### 主观指标

{top_dist('indicator', 20)}

### 测量工具族

{top_dist('tool_family')}

RQ1 的分母分层处理：年份、领域、阶段与 AI 功能以论文为单位；评价维度、指标和工具以证据链为单位。多标签变量允许一篇论文或一条证据链进入多个类别，因此同一变量下的百分比之和可能超过 100%。

## RQ2 JCSEE 对照规范性审查

本研究没有把 JCSEE《项目评价标准》简化为一个未经验证的总分。审查按七项可从论文中观察的标准逐案例完成，并保留原文事实、判断理由、页码和短引文。

### 第一步：确认评价目的与感知证据是否相关（U5）

核对论文声明的问题、参与者实际完成的任务和作者使用主观数据回答的结论。自动性能指标不能替代人类感知证据。

### 第二步：审查测量解释的效度依据（A2）

核对构念定义、题项或评价准则、工具来源、翻译／改编过程、内容或构念效度依据，并判断测量材料是否支持作者给出的解释。

### 第三步：审查信息的可靠性依据（A3）

量表关注内部一致性、复测或其他可靠性信息；专家评分关注评分者训练、人数及一致性；质性资料关注编码程序、复核或一致性。单题不机械要求 Cronbach’s α，但仍需说明稳定性或一致性支持。

### 第四步：审查对象与情境描述（A4）

核对样本、招募、评价对象、AI 条件、任务、场景、比较条件和实施程序是否足以判断可迁移范围。

### 第五步：审查研究设计与分析适切性（A6）

把设计和分析与主张强度对照。描述性单条件研究可以支持限定的状态描述，但不能支持无对照的因果或优越性结论。

### 第六步：审查推理可追溯性（A7）

沿“问题／主张—构念—指标—工具—结果—结论”逐项回溯，检查结论是否超出实际结果及比较条件。

### 第七步：审查评价记录充分性（E1）

核对完整题项或准则、量尺与计分、工具来源、样本和程序、分析、数值／主题结果及必要附件是否足以复核。

### 审查结果

{md_table(st_wide, ['standard','standard_label','S','P','C','NR','NA'], ['标准','含义','S充分','P部分','C问题','NR未报告','NA不适用'])}

{md_table(tiers, ['tier','rule','n','denominator'], ['案例层级','预设规则','n','分母'])}

“严格高规范案例”用于判断当前文献是否已经提供完整、可信且可直接复用的评价依据。“关联分析案例”保留未报告可靠性但其他关键环节至少部分满足、且没有明确问题的案例；A3 作为质量指标而非硬排除条件。这一层级只用于探索情境与选择之间的经验关系，不等同于 JCSEE 官方评分。

## RQ3 情境条件与评价证据之间的关联

### 分析单位与统计顺序

1. 先用 Fisher 精确检验扫描“情境代码—评价维度／工具族”的二元共现关系。
2. 同时报告条件概率、基线概率、lift、有向 Cramér’s V 和原始 p 值。
3. 在同一分析族内用 Benjamini–Hochberg 控制多重比较。
4. 只把具有足够共同出现次数的关系带入推荐表；`证据不足` 不作为推荐依据。
5. 预测模型用论文编号进行分组交叉验证，保证同一论文的多条证据链不会同时进入训练集与测试集。

### 主要关联

{md_table(top_assoc, ['context_label','target_label','a_both','context_n','P(结果|情境)','基线','lift','cramers_v_signed','p_value','q_value_bh','evidence_grade'], ['情境','评价结果','共同出现','情境n','条件概率','基线','lift','V','p','BH q','证据等级'])}

关联是文献中的选择规律，不代表情境变量因果决定评价指标或工具。推荐系统因此显示支持量、概率和证据等级，而不输出唯一正确答案。

### 五类模型交叉验证

结构方程模型需要明确的潜变量测量模型、足够样本以及可解释的连续或有序观测指标。本研究的分析单位是嵌套在论文中的多标签类别选择，主要目标是预测“选择了哪类评价维度／工具”，所以 SEM 不适合承担主模型。采用频率基线、L2 多项逻辑回归、随机森林、极端随机树和直方图梯度提升进行比较，并以分组交叉验证的 macro-F1 为主指标。

{md_table(best_models, ['target','model','n','papers','classes','folds','macro_f1_mean','macro_f1_sd','weighted_f1_mean','balanced_accuracy_mean','analysis_tier'], ['目标','模型','链n','论文n','类别','折数','Macro-F1','SD','Weighted-F1','平衡准确率','分析层级'])}

模型结果用于检验情境信息是否具有可重复的选择信号。若复杂模型没有稳定超过频率基线，网站采用透明的频数、条件概率和质量门槛，不把不稳定模型包装成智能推荐。

## 指标与工具推荐规则

推荐流程分为两步：

1. 设计师先声明自己的效果主张。系统依据领域、阶段、AI 功能与角色、评价目的、对象、主体、用户和可用数据源，展示有文献支持的构念／指标候选。
2. 在确定构念或主观指标后，系统推荐实际测量工具族和论文中出现的工具实例，并同时显示支持论文数、证据链数、规范性层级和不确定性。

系统不主动替设计师生成需要证明的效果主张。效果主张体现研究目的和价值判断，应由研究者先提出；网站可以提示相似情境中常见但被遗漏的效果维度，作为覆盖检查。

### 支持度最高的指标—工具对应

{md_table(top_recs, ['indicator_code','indicator_label','tool_code','tool_label','support_chains','support_papers','经验概率','example_instruments'], ['指标代码','指标','工具代码','工具族','链n','论文n','经验概率','工具实例'])}

## 可执行产物

- 最终编码与分析工作簿：`AI辅助设计感知效应_最终编码与分析.xlsx`
- 完整研究报告：本文件。
- 推荐网页：`site/dist/index.html`，可按情境筛选并查看推荐及证据来源。
- 四幅图：JCSEE 审查、时间结构、情境关联、指标—工具对应。
- 可复核中间数据：`final_results/` 中的论文、评价案例、证据链、审查、关联、模型与推荐 CSV/JSON。

## 方法边界

1. 125 篇是用户提供的研究集合，结论适用于该语料，不自动代表所有 AI 辅助设计研究。
2. 多数论文的测量报告不完整；`NR` 表示无法从论文判断，不能等同于方法实际没有实施。
3. 12 篇逐页人工复核，其他论文采用规则筛查与本地语义清点组合流程；正式发表前需双人独立复核，报告 Cohen’s κ 或 Krippendorff’s α，并解决分歧。
4. 关联和预测反映文献中的选择习惯，也可能包含领域传统、发表偏差和可得工具偏好。
5. 固定二级分类保证可量化，但会压缩构念细节；所有 `UNMAPPED` 项应在下一轮代码本修订中复核。

## 理论与标准依据

- [CDC: Gather Credible Evidence]({SOURCE_URLS['CDC']})：用于组织评价问题、概念／构念、指标与测量之间的证据形成关系。
- [JCSEE Program Evaluation Standards]({SOURCE_URLS['JCSEE']}) 与 [标准清单]({SOURCE_URLS['JCSEE_checklist']})：用于建立规范性审查维度；本文只选取能从论文全文观察的条目进行操作化。
- [ICoD Design Disciplines]({SOURCE_URLS['ICoD_domain']}) 与 [Designing]({SOURCE_URLS['ICoD_stage']})：用于保留六类设计领域和四阶段分类。
- [Scikit-learn grouped cross-validation]({SOURCE_URLS['GroupedCV']}) 与 [nested model selection example]({SOURCE_URLS['NestedCV']})：用于避免同一论文的数据泄漏和说明模型选择偏差控制。
"""
    OUT.write_text(text, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
