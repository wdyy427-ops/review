from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config import ROOT, LABELS, SOURCE_URLS
from revised_pipeline import TOOL_LABELS, AUDIT_LABELS, STATUS_LABELS


DATA = ROOT / "revised_results"
OUT = ROOT / "AI辅助设计感知效应_RQ1-RQ3修订后研究报告.md"


def pct(x):
    return f"{100*x:.1f}%"


def main():
    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    dim = pd.read_csv(DATA / "rq1_dimension_by_year.csv")
    ind = pd.read_csv(DATA / "rq1_indicator_by_year.csv")
    tools = pd.read_csv(DATA / "rq1_tool_by_year.csv")
    trends = pd.read_csv(DATA / "rq1_temporal_trend_tests.csv")
    context = pd.read_csv(DATA / "rq1_context_dimension_tests.csv")
    audit = pd.read_csv(DATA / "rq2_chain_audit_summary.csv", keep_default_na=False)
    tiers = pd.read_csv(DATA / "rq2_chain_quality_tiers.csv")
    models = pd.read_csv(DATA / "rq3_model_comparison.csv")
    weights = pd.read_csv(DATA / "rq3_label_group_weights.csv")
    assoc = pd.read_csv(DATA / "rq3_context_associations.csv")
    inst = pd.read_csv(DATA / "measure_instances.csv", keep_default_na=False)

    dim_tot = dim.groupby(["code", "label"]).n.sum().reset_index()
    dim_tot["percent"] = dim_tot.n / dim_tot.n.sum()
    tool_tot = tools.groupby(["code", "label"]).n.sum().reset_index()
    tool_tot["percent"] = tool_tot.n / tool_tot.n.sum()
    ind_top = ind.groupby(["code", "label"]).n.sum().sort_values(ascending=False).head(12).reset_index()

    audit_table = audit.pivot_table(index=["standard", "standard_label"], columns="status", values="n", fill_value=0).reset_index()
    for c in ["S", "P", "NR", "C", "NA"]:
        if c not in audit_table:
            audit_table[c] = 0

    main_models = models[models.analysis_tier == "主要规范集"]
    exp_models = models[models.analysis_tier == "扩展规范集"]
    exp_w = weights[weights.analysis_tier == "扩展规范集"]

    lines = []
    add = lines.append
    add("# AI-assisted Design workflow 中 Perceived Effect 评价实践：RQ1–RQ3 修订后研究报告")
    add("")
    add("## 1. 研究对象、分析单位与数据结构")
    add("")
    add(f"本研究纳入 **{summary['papers']} 篇全文论文**，识别 **{summary['evaluation_cases']} 个评价案例**，拆解为 **{summary['evidence_chains']} 条评价证据链**。评价证据链以“效果主张／评价问题→感知构念→主观指标→测量工具”为结构。规范性审查、RQ1的维度与指标统计以及RQ3的链级建模均以证据链为基本单位。")
    add("")
    add(f"490条证据链进一步拆出 **{summary['measure_instances']} 个测量工具实例**。原因是一条证据链可能同时使用量表、访谈或问卷等多个工具。每个工具实例只归入一个互斥类别：M1标准化具名量表、M2自编结构化评分工具、M3定性言语引出工具、M4非量表型结构化问卷、M5既有感知资料分析。共{int(inst.tool_code.isin(TOOL_LABELS).sum())}个实例可判定类别，{int((inst.tool_code=='UNMAPPED').sum())}个因原文信息不足保留为UNMAPPED。")
    add("")
    add("该划分借用CDC“Gather Credible Evidence”中从评价问题、概念到指标和测量的证据形成逻辑；JCSEE标准用于构造可观察的报告质量检查项。这里的质量层级和M1–M5均为本研究操作化，不是CDC或JCSEE发布的官方分类或总分。")
    add("")
    add(f"- CDC证据形成框架：{SOURCE_URLS['CDC']}")
    add(f"- JCSEE项目评价标准：{SOURCE_URLS['JCSEE']}")
    add("")
    add("## 2. RQ1：评价证据的分布")
    add("")
    add("### 2.1 评价维度的总体分布与年代趋势")
    add("")
    add("| 维度 | 证据链数 | 占已映射维度证据链 |")
    add("|---|---:|---:|")
    for r in dim_tot.sort_values("code").itertuples():
        add(f"| {r.code} {r.label} | {int(r.n)} | {pct(r.percent)} |")
    add("")
    add("设计成果质量是现有研究最常评价的维度，其后依次为设计者认知、情感与能力、人机交互体验、社会情境价值和设计过程质量。年度数量在2024年后明显上升，反映的是本语料库的发表结构；因此趋势判断同时查看数量和当年构成比。二项GLM的年度构成检验显示，C类和D类占比出现统计下降，但效应较小：C类每年优势比0.949（BH校正q=.050），D类0.983（q=.025）。A、B、E的校正后趋势没有达到.05。")
    add("")
    add("![评价维度年度趋势](revised_figures/图01_评价维度年度趋势.png)")
    add("")
    add("### 2.2 主观指标的分布与年代趋势")
    add("")
    add("| 排名 | 指标 | 证据链数 |")
    add("|---:|---|---:|")
    for i, r in enumerate(ind_top.itertuples(), 1):
        add(f"| {i} | {r.code} {r.label} | {int(r.n)} |")
    add("")
    add("高频指标集中在适用性、新颖性、愉悦、沟通协作、可行性、美观性和控制感。指标级趋势比维度级趋势更具体，但部分指标总量很少，容易产生完全分离或极端年度比值。因而报告只把总量不少于10且优势比有限的结果作为稳定描述。增长较明确的指标包括能力扩展（每年OR=1.290）、知识获得（1.276）、商业／品牌／市场价值（1.231）、美观性（1.143）、工作负荷（1.105）与角色／贡献公平（1.105）；下降较明确的包括灵感刺激（0.618）、控制感（0.843）、愉悦（0.868）、沟通协作（0.909）和全面性（0.912）。这些结果描述文献选择的变化，不表示真实设计效应随年代发生同样变化。")
    add("")
    for dim_code in "ABCDE":
        add(f"![{dim_code}类指标年度趋势](revised_figures/图02{dim_code}_{dim_code}类指标年度趋势.png)")
        add("")
    add("### 2.3 测量工具的总体分布与年代趋势")
    add("")
    add("| 工具类别 | 工具实例数 | 占可判定工具实例 |")
    add("|---|---:|---:|")
    for r in tool_tot.sort_values("code").itertuples():
        add(f"| {r.code} {r.label} | {int(r.n)} | {pct(r.percent)} |")
    add("")
    add("M2自编结构化评分是最常见工具，2026年达到当年可判定实例的37.3%。年度构成检验显示M2上升（每年OR=1.336），M1、M3和M5下降（分别为0.854、0.861和0.914）；M4没有稳定单调趋势。该结果说明研究正在更多依赖面向具体系统或设计任务的自编评分，也提示跨研究可比性可能继续下降。")
    add("")
    add("![测量工具年度趋势](revised_figures/图03_测量工具年度趋势.png)")
    add("")
    add("### 2.4 评价维度在设计领域和设计阶段中的分布")
    add("")
    domain = context[context.field == "domains"].iloc[0]
    stage = context[context.field == "stages"].iloc[0]
    add(f"设计领域×评价维度的总体独立性检验为χ²({int(domain.df)})={domain.chi_square:.2f}, p={domain.p_value:.3f}, Cramér’s V={domain.cramers_v:.3f}；设计阶段×评价维度为χ²({int(stage.df)})={stage.chi_square:.2f}, p={stage.p_value:.3f}, V={stage.cramers_v:.3f}。两者均未达到统计显著，效应量也小。因此不能把设计领域或阶段单独当作决定评价维度的充分依据。领域和阶段仍适合作为推荐系统的情境筛选标签，但需要与评价对象、数据源、目的和主体联合使用。")
    add("")
    add("![设计领域与评价维度](revised_figures/图04A_设计领域与评价维度.png)")
    add("")
    add("![设计阶段与评价维度](revised_figures/图04B_设计阶段与评价维度.png)")
    add("")
    add("## 3. RQ2：评价实践的规范性审查")
    add("")
    add("### 3.1 审查步骤")
    add("")
    add("1. **确定审查单位。** 每条效果主张—构念—指标—测量工具链视为一次评价实践；同一案例中的不同感知效应分别审查。")
    add("2. **选择可由论文文本判断的JCSEE条目。** 使用U5、A2、A3、A4、A6、A7和E1，覆盖用途相关性、效度、可靠性、情境描述、设计分析、推理可追溯和记录充分性。")
    add("3. **把标准转为可观察规则。** 例如A2查找量表来源、题项、理论依据、预测试或效度证据；A3查找内部一致性、评分者一致性、编码一致性、三角互证等；A6与A7把主张类型、比较条件、分析方法和结果引文连起来判断。")
    add("4. **逐链记录状态与依据。** 每一条链保留S充分支持、P部分支持、NR未报告／无法判断、C明确问题或NA不适用，同时记录事实、理由、页码和短引文。共形成3,430条标准—证据链审查记录。")
    add("5. **形成研究用途层级。** Q1要求核心条目充分；Q2允许部分支持；Q3保留为描述或敏感性分析；发现明确问题者进入EXCLUDE。层级用于透明选样，不被解释为JCSEE官方总分。")
    add("6. **建立建模输入。** 主要规范集为Q1+Q2共48条链；扩展规范集在没有明确问题且其他关键标准至少部分支持的前提下允许A3未报告，共155条链。")
    add("")
    add("### 3.2 各标准结果")
    add("")
    add("| 标准 | 充分S | 部分P | 未报告NR | 明确问题C | 不适用NA |")
    add("|---|---:|---:|---:|---:|---:|")
    for r in audit_table.itertuples():
        add(f"| {r.standard} {r.standard_label} | {int(r.S)} ({pct(r.S/490)}) | {int(r.P)} ({pct(r.P/490)}) | {int(r.NR)} ({pct(r.NR/490)}) | {int(r.C)} ({pct(r.C/490)}) | {int(r.NA)} ({pct(r.NA/490)}) |")
    add("")
    add("主要缺口集中在A6研究设计与分析适切性、A7推理可追溯性和A3可靠性／可信性。A6和A7各有60.4%的证据链无法从论文报告判断，A3有51.0%未报告。相对较好的是U5用途相关性，85.3%的链达到充分支持；E1记录充分性多数为部分支持，说明论文通常能看出使用了什么，但不足以完整复现题项、计分和推理。")
    add("")
    add("![JCSEE链级审查](revised_figures/图05_JCSEE证据链规范性审查.png)")
    add("")
    add("### 3.3 质量层级结果")
    add("")
    add("| 层级 | 证据链数 | 比例 | 用途 |")
    add("|---|---:|---:|---|")
    use = {"Q1":"高置信实例与严格推荐", "Q2":"主要关联分析与严格推荐", "Q3":"描述统计、敏感性分析和网页回退", "EXCLUDE":"不进入建模"}
    for r in tiers.itertuples():
        add(f"| {r.tier} | {int(r.n)} | {pct(r.percent)} | {use[r.tier]} |")
    add("")
    add("Q1仅6条，Q2为42条，说明如果只使用严格规范案例，指标模型无法覆盖足够类别。本文因此把主要规范集作为最严格的验证结果，把扩展规范集作为推荐系统的开发证据，并在界面中清楚标注证据层级和支持论文数。")
    add("")
    add("## 4. RQ3：情境标签如何影响维度、指标和工具选择")
    add("")
    add("### 4.1 建模设计")
    add("")
    add("输入按七组组织：G1评价目的、G2效果主张形式、G3评价对象、G4设计领域与阶段、G5评价主体与目标用户、G6数据源／评价环境／可行约束、G7 AI功能／角色／设计任务。输出采用三级顺序：评价维度→主观指标→测量工具类别及具体工具。预测指标时把已确定维度作为条件；预测工具时把已确定维度和指标作为条件。人工编码的目标变量不会作为同级输入。")
    add("")
    add("模型比较包括频率基线、L2多项逻辑回归、随机森林和直方图梯度提升。所有交叉验证按论文分组，避免同一论文的多条证据链同时进入训练和测试。主指标为Macro-F1，并同时保留加权F1、平衡准确率、准确率、对数损失和Top-2准确率。")
    add("")
    add("### 4.2 模型结果")
    add("")
    add("| 分析集 | 推荐目标 | n | 论文数 | 类别数 | 最优模型 | Macro-F1 | 频率基线 | Top-2准确率 |")
    add("|---|---|---:|---:|---:|---|---:|---:|---:|")
    for tier, d in [("主要规范集", main_models), ("扩展规范集", exp_models)]:
        for target in ["评价维度", "主观指标", "测量工具类别"]:
            s = d[d.target == target]
            if s.empty:
                continue
            nonbase = s[s.model != "频率基线"]
            if nonbase.empty:
                continue
            best = nonbase.sort_values("macro_f1_mean", ascending=False).iloc[0]
            base = s[s.model == "频率基线"].iloc[0]
            add(f"| {tier} | {target} | {int(best.n)} | {int(best.papers)} | {int(best.classes)} | {best.model} | {best.macro_f1_mean:.3f} | {base.macro_f1_mean:.3f} | {best.top2_accuracy_mean:.3f} |")
    add("")
    add("主要规范集中的主观指标只有6条、1个满足最小支持阈值的类别，因此不建模。扩展规范集的指标模型表现最好：随机森林Macro-F1=.548，Top-2准确率=.786。维度和工具模型虽优于频率基线，但Macro-F1分别只有.190和.234，说明现有语料更适合做带证据强度的候选排序，不适合自动给出唯一答案。")
    add("")
    add("![模型交叉验证](revised_figures/图07_RQ3模型交叉验证.png)")
    add("")
    add("### 4.3 标签组权重")
    add("")
    add("权重由扩展规范集中逐组消融得到：去掉一个标签组后Macro-F1下降越多，该组对当前推荐目标的增量贡献越大；只把正下降归一化为100%。")
    add("")
    add("| 推荐目标 | 标签组及归一化权重 |")
    add("|---|---|")
    for target in ["评价维度", "主观指标", "测量工具类别"]:
        s = exp_w[exp_w.target == target].sort_values("normalized_weight", ascending=False)
        vals = [f"{r.feature_group.split('_',1)[1]} {r.normalized_weight:.1%}" for r in s.itertuples() if r.normalized_weight > 0]
        add(f"| {target} | {'；'.join(vals)} |")
    add("")
    add("这给网站的标签交互一个清晰顺序：推荐维度时优先询问数据源与可行条件、设计情境、评价对象；推荐指标时优先询问评价目的、评价主体与用户、AI活动特征和主张形式；推荐工具时优先使用效果主张形式、评价对象、AI活动特征和评价目的。权重不是稳定的理论常数；只有维度模型中G6和G4、指标模型中G1和G5的消融置信区间明确高于0，其余标签应视作探索性排序依据。")
    add("")
    add("![标签组权重](revised_figures/图06_RQ3标签组权重.png)")
    add("")
    add("### 4.4 可解释的关联证据")
    add("")
    add("Fisher精确检验、条件概率、lift和有向Cramér’s V用于展示具体标签与输出类别的共同出现关系，并对同批比较做BH校正。主要规范集中，设计学生／新手作为目标用户与M1标准化具名量表明显共同出现（8/9，基线11/48，lift=3.88，q=.001）；第三方人工评价与M2自编结构化评分共同出现（12/22，基线14/48，lift=1.87，q=.021）。扩展规范集中，访谈／开放回答数据源与M3为结构上相符的强关联；设计成果对象更常连接M2，设计过程／工作流对象更常连接M3。前两类结果适合作为推荐解释，后者中包含由定义带来的近确定性关系，应避免把它们误解为独立发现。")
    add("")
    add("## 5. 推荐网页的最终逻辑")
    add("")
    add("1. 设计师先描述拟评价的效果主张，再选择评价目的、评价对象、设计领域、设计阶段、评价主体、目标用户、可用数据源、评价环境与约束，以及AI功能、角色和任务。")
    add("2. 系统先给出评价维度候选，显示条件概率、相对基线、支持链数、支持论文数和证据层级。设计师确认或调整维度。")
    add("3. 系统在已确认维度下推荐主观指标，仍显示证据支持与不确定性；不把低支持指标隐藏成确定答案。")
    add("4. 系统在已确认维度和指标下推荐M1–M5工具类别，再列出可追溯的具名量表或通用工具方案。具体工具至少需要两个独立论文支持才进入默认推荐；单论文工具只在“探索性证据”中显示。")
    add("5. 默认先检索主要规范集；样本不足时回退到扩展规范集并明确标注。没有足够证据时返回“证据不足”，同时提示需要补充的报告要素。")
    add("6. 网页不能宣称替代研究者判断。它提供的是基于现有文献的可解释候选排序和证据追踪。")
    add("")
    add("## 6. 结论")
    add("")
    add("本研究最重要的发现不是某个设计领域固定对应某种感知维度，而是**评价证据的选择由不同层级的情境标签共同约束，并且约束重点会随推荐目标改变**。设计领域和阶段对维度的总体关联较弱，不能独立承担推荐入口；数据源、评价对象、目的、相关人和AI活动特征提供了更有用的组合信息。现有论文最大的规范性短板是可靠性依据、研究设计／分析说明和从结果到结论的可追溯性。推荐系统因此应同时输出候选、证据量、规范性层级和不确定性。")
    add("")
    add("## 7. 研究限制与下一步")
    add("")
    add("- 12篇论文完成逐页人工复核，113篇依赖全文规则筛查、语义清点和原句回定位。正式投稿前应由第二编码者独立复核，并报告一致性。")
    add("- 2026年的文献数量较多，年度趋势可能同时反映检索窗口和语料构成。")
    add("- 多条证据链来自同一论文。建模已按论文分组，但描述统计和卡方表仍是证据链展开结果，应同时报告论文数。")
    add("- 主要规范集只有48条链，主观指标模型无法建立；扩展规范集结果只用于敏感性和网页回退。")
    add("- 工具实例中仍有16个UNMAPPED。它们保留为缺失，避免将含糊文本强行放入M1–M5。")
    add("- 当前模型验证的是对现有文献编码的预测，尚未验证网站建议能否提高新研究的测量效度。下一步需要前瞻性用户研究和外部语料验证。")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
