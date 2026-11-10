from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\Administrator\Desktop\review\outputs\rq_review_20261024")
EXT = ROOT / "extended_results"
OUT = ROOT / "AI辅助设计感知效应_问题答复与补充分析.md"


def read(name):
    return pd.read_csv(EXT / name, keep_default_na=False)


def md_table(headers, rows):
    def esc(x):
        return str(x).replace("|", "／").replace("\n", " ")
    out = ["| " + " | ".join(map(esc, headers)) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out += ["| " + " | ".join(esc(v) for v in row) + " |" for row in rows]
    return "\n".join(out)


hier = read("hierarchy_counts.csv")
dim = read("dimension_exact_percentages.csv")
tests = read("rq1_extended_context_tests.csv")
cv = read("grouped_vs_random_cv.csv")
main_ind = read("main_set_indicator_support.csv")
defs = read("jcsee_subrule_codebook.csv")
summ = read("jcsee_subrule_summary.csv")

status_rows = []
for keys, g in summ.groupby(["standard", "subrule", "subrule_name"]):
    d = {r.status: int(r.n) for r in g.itertuples()}
    app = int(g.applicable_chains.iloc[0])
    support = 100 * d.get("S", 0) / app if app else 0
    base = defs[defs.subrule == keys[1]].iloc[0]
    status_rows.append([
        keys[0], keys[1], keys[2], base.observable_rule, base.basis,
        f"{d.get('S',0)}/{app} ({support:.1f}%)", d.get("NR", 0), d.get("C", 0), d.get("NA", 0)
    ])

selected_rows = [
    ["U5", "Relevant Information／相关信息", "效果主张、构念、指标和工具是否形成与评价目的相关的链", "直接对应证据链的相关性和可操作性"],
    ["A2", "Valid Information／有效信息", "构念、指标、工具、题项、计分和效度依据", "判断测量能否支持预期解释"],
    ["A3", "Reliable Information／可靠信息", "量化信度、评分／编码一致性、质性可信性和重复实施细节", "判断信息是否足够稳定、一致"],
    ["A4", "Explicit Program and Context Descriptions／明确对象与情境", "对象、样本、招募、任务、环境、比较条件及AI设计情境", "判断证据适用边界"],
    ["A6", "Sound Designs and Analyses／健全设计与分析", "设计、分析、比较条件、结果及因果越界", "判断设计和分析是否支撑主张"],
    ["A7", "Explicit Evaluation Reasoning／明确评价推理", "主张、结果、位置、完整证据链和推理强度", "判断从信息到结论是否可追溯"],
    ["E1", "Evaluation Documentation／评价记录", "目的、设计、程序、工具、题项、计分、结果和位置", "判断读者能否复核评价过程"],
]

omitted_rows = [
    ["U1", "Evaluator Credibility／评价者可信度", "评价者资格和情境信誉通常无法由一条证据链判断"],
    ["U2", "Attention to Stakeholders／关注利益相关者", "论文可识别部分用户，但无法判断是否关注了完整利益相关者范围"],
    ["U3", "Negotiated Purposes／协商目的", "目的如何持续协商通常不报告"],
    ["U4", "Explicit Values／明确价值", "目标用户不等于支撑判断的个人与文化价值已被明确"],
    ["U6", "Meaningful Processes and Products／有意义的过程与成果", "参与者理解和行为改变多在评价实施之外"],
    ["U7", "Timely and Appropriate Communicating and Reporting／及时适当沟通", "受众、时机和传播过程无法从测量链判断"],
    ["U8", "Concern for Consequences and Influence／关注后果与影响", "评价被使用后的后果通常不在论文中"],
    ["F1–F4", "项目管理、程序实用性、情境可行性、资源使用", "需要预算、政治情境、实施管理和资源记录；论文正文通常不足"],
    ["P1–P7", "回应与包容、协议、人权、公平、披露、利益冲突、财务责任", "多为组织与伦理治理层面；伦理或利益冲突声明只能覆盖局部，不能等同整项标准"],
    ["A1", "Justified Conclusions and Decisions／有依据的结论与决定", "与A7和A4部分重叠，且需要结论产生后果的文化与情境证据；为避免重复计权而未单列"],
    ["A5", "Information Management／信息管理", "需要收集、复核、验证和存储流程，公开论文通常不完整"],
    ["A8", "Communication and Reporting／沟通与报告", "属于整篇报告的范围、偏差和误导风险，不适合链级计分；局部记录由A7和E1覆盖"],
    ["E2", "Internal Metaevaluation／内部元评价", "需要研究团队实际进行元评价的证据"],
    ["E3", "External Metaevaluation／外部元评价", "需要独立外部元评价的证据"],
]

domain_ind = read("rq1_indicator_by_domain.csv")
stage_ind = read("rq1_indicator_by_stage.csv")
domain_tool = read("rq1_tool_by_domain.csv")
stage_tool = read("rq1_tool_by_stage.csv")


def top_rows(df, k=5):
    rows = []
    for (code, label), g in df.groupby(["context_code", "context_label"], sort=False):
        z = g.sort_values(["n", "context_percent"], ascending=False).head(k)
        items = "；".join(f"{r.outcome_code} {r.outcome_label} {int(r.n)} ({100*r.context_percent:.1f}%)" for r in z.itertuples())
        rows.append([f"{code} {label}", items])
    return rows


content = f"""# AI-assisted Design workflow 感知效应研究：问题答复与补充分析

## 结论口径

本文件修正并补充主报告中的七个问题。JCSEE部分应表述为**“以JCSEE为依据的、基于公开论文文本的评价证据链报告充分性与方法适切性审查”**，不能表述为对一项完整项目评价是否全面符合JCSEE 30项标准的认证。下面A2.1等编号均为本研究为复核而设置的可观察检查项，并非JCSEE发布的官方子条款。

## 1. 125篇论文、158个案例、490条证据链和600个工具实例如何对应

这是四个嵌套但不同的分析单位：

1. **论文**是文献容器。
2. **评价案例**是论文内一个可独立识别的样本、实验、研究或评价协议。同一论文可包含多个研究或多组评价。
3. **评价证据链**是针对一个感知效应形成的“效果主张／评价问题→构念→指标→测量”。同一案例可评价多个感知效应，因此拆成多条链。
4. **测量工具实例**是某条链实际使用的一种具体工具。同一条链可同时使用量表、访谈或结构化问卷，因此工具实例数可以大于链数。

{md_table(["转换", "上级总数", "有下级", "无下级", "下级总数", "每个上级包含的下级数量分布"], [[r.transition, r.parent_total, r.parents_with_children, r.parents_without_children, r.children_total, r.distribution] for r in hier.itertuples()])}

具体算式为：54×1+27×2+12×3+1×14=158个案例；77×1+19×2+14×3+12×4+6×5+6×6+4×7+7×8+5×9+3×10+5×12=490条链；380×1+110×2=600个工具实例。125篇中94篇产生了纳入条件内的人类主观评价案例，31篇没有产生这类案例。

## 2. JCSEE如何被操作化

JCSEE第三版包含30项标准。官方说明明确指出，标准陈述本身不能传达每项标准的完整含义，实际应用还需要完整指南和具体情境。因此，本研究没有声称“完全按JCSEE判定合规”，而是：先选取可由公开论文文本观察、且与感知评价证据链直接相关的7项标准；再把它们转成可重复编码的文本规则；最后用S、P、NR、C和NA记录支持程度。

### 2.1 纳入的7项标准

{md_table(["标准", "官方标准名称", "本研究观察内容", "纳入理由"], selected_rows)}

### 2.2 没有进入链级质量层级的23项标准

{md_table(["代码", "标准", "未进入链级层级的原因"], omitted_rows)}

这些标准没有被判定为“不重要”。它们需要项目管理记录、利益相关者协商材料、伦理治理文件、资源信息或元评价材料，不能把论文“没有写”直接编码成研究“没有做”。其中伦理审批、利益冲突和局限披露可以另建论文级报告项，但不能替代P3、P5或P6的完整判断。

## 3. 评价维度百分比为何没有加到100%

已映射维度的分母是432条证据链，五类计数为136、41、101、91、63，合计正好432。此前表格分别四舍五入到1位小数，得到31.5%、9.5%、23.4%、21.1%和14.6%，显示合计为100.1%。这是独立四舍五入产生的0.1个百分点误差，不是重复编码。

{md_table(["维度", "证据链", "精确比例"], [[f"{r.dimension_code} {r.dimension_label}", int(r.chains), f"{100*r.percent_exact:.3f}%"] for r in dim.itertuples()])}

修订报告改用三位小数并注明分母，五项显示值合计100.000%。

## 4. 主观指标和测量工具在设计领域与设计阶段中的分布

### 4.1 呈现方法

指标有36类，适合使用两张分面热图：行是按A–E分组的指标，列分别为6个设计领域和4个设计阶段；颜色表示该领域／阶段内部的比例，格内数字表示原始计数。工具只有5类，使用两张5行热图即可放入正文。指标图适合作为正文概览加补充材料详表，避免用36组并列柱形图造成视觉拥挤。

一条链可对应多个领域或阶段，一条链也可有多个工具，所以这里统计的是“情境—链”或“情境—工具实例”展开后的分配次数。检验只作为探索性描述；尤其指标×领域有84.8%的期望频数小于5，不能根据普通卡方p值作强推断。

{md_table(["关系", "展开分配数", "χ²(df)", "p", "Cramér’s V", "期望频数<5比例"], [[("主观指标×设计领域" if r.context_field=='domains' and r.outcome=='indicator_code' else "测量工具×设计领域" if r.context_field=='domains' else "主观指标×设计阶段" if r.outcome=='indicator_code' else "测量工具×设计阶段"), int(r.n_assignments), f"{r.chi_square:.2f} ({int(r.df)})", f"{r.p_value:.3g}", f"{r.cramers_v:.3f}", f"{100*r.expected_below_5_percent:.1f}%"] for r in tests.itertuples()])}

结论是：指标构成在领域和阶段之间都没有稳定的总体差异；工具类别与设计领域的关联较明显（V=.300），与设计阶段的关联较弱（V=.110）。这些是语料中的选择模式，不表示领域或阶段对工具有因果作用。

### 4.2 各设计领域的高频主观指标

{md_table(["设计领域", "前5类指标：n（领域内比例）"], top_rows(domain_ind))}

![主观指标与设计领域](extended_figures/图08A_指标与设计领域.png)

### 4.3 各设计阶段的高频主观指标

{md_table(["设计阶段", "前5类指标：n（阶段内比例）"], top_rows(stage_ind))}

![主观指标与设计阶段](extended_figures/图08B_指标与设计阶段.png)

### 4.4 测量工具分布

{md_table(["设计领域", "工具：n（领域内比例）"], top_rows(domain_tool, 5))}

![测量工具与设计领域](extended_figures/图09A_工具与设计领域.png)

{md_table(["设计阶段", "工具：n（阶段内比例）"], top_rows(stage_tool, 5))}

![测量工具与设计阶段](extended_figures/图09B_工具与设计阶段.png)

## 5. JCSEE标准的选择依据、逐条可观察规则及分布

选择规则同时满足三点：第一，标准与评价信息、测量、情境、设计分析、推理或记录直接相关；第二，能从公开论文中的可定位文本判断；第三，能够落到单条评价证据链或其所属评价案例。S表示论文文本提供可观察支持，NR表示未报告或无法判断，C表示存在明确冲突，NA表示该规则对该链不适用。NR不能解释为研究实际没有实施该程序。

{md_table(["标准", "规则", "名称", "可观察判定", "依据", "支持S／适用数", "NR", "C", "NA"], status_rows)}

![JCSEE子规则分布](extended_figures/图10_JCSEE子规则分布.png)

最突出的报告缺口是：质性可信性程序0/130；效度依据35/490（7.1%）；评分／编码一致性41/366（11.2%）；完整证据链可追溯169/490（34.5%）；结果可定位188/490（38.4%）；量化可靠性依据119/277（43.0%）；计分／反应格式258/490（52.7%）。这些子规则用于诊断缺口，不重新计算原Q1/Q2/Q3层级，避免事后改变已定义的纳入阈值。

### 5.1 扩展规范集允许A3未报告的含义

扩展规范集要求U5、A2、A4、A6、A7和E1均至少达到S或P，所有标准均不得出现C；唯一放宽的是A3允许NR。它表示：论文提供了足以识别评价目的、证据链、情境、设计／分析和推理的文本，但没有报告可靠性或质性可信性依据，因此可靠性是**未知**，不是“已证明可靠”，也不是“已证明不可靠”。该集合只用于敏感性分析和网站证据不足时的回退，不应用于高置信规范结论。

## 6. 为什么按论文分组训练和测试

同一论文中的多条链通常共享参与者、任务、AI系统、实验条件、工具措辞和作者报告习惯。如果随机按链切分，同一论文的近似记录会同时进入训练集和测试集，模型可以识别论文特征而不是真正学习跨研究规律，形成数据泄漏。

{md_table(["目标", "模型", "验证方式", "n", "论文", "类别", "Macro-F1", "准确率", "Top-2准确率", "相对分组验证变化"], [[r.target, r.model, r.validation, int(r.n), int(r.papers), int(r.classes), f"{r.macro_f1:.3f}", f"{r.accuracy:.3f}", f"{r.top2_accuracy:.3f}", f"{100*r.inflation_vs_grouped:+.1f}%"] for r in cv.itertuples()])}

随机切分使维度模型Macro-F1虚高80.6%，使工具模型虚高153.9%。指标模型这一次随机切分没有提高Macro-F1，但不能消除同论文泄漏的结构性风险。因此最终报告按论文分组，衡量模型能否迁移到未见过的新论文。

## 7. 48条主要规范证据链为何只剩6条指标观测

48是“证据链数量”，不是“指标类别数量”。其中47条有可映射指标，分散在22个指标类别中；建模前还要求目标类别至少有5条证据链且来自至少3篇不同论文。只有A1新颖性达到6条链、5篇论文，其他21类都没有同时满足两个阈值，所以筛选后只有6条观测、1个类别，无法建立多分类模型。

{md_table(["指标", "证据链", "论文", "达到≥5条链且≥3篇论文"], [[f"{r.indicator_code} {r.indicator_label}", int(r.chains), int(r.papers), "是" if str(r.passes_min_support).lower()=='true' else "否"] for r in main_ind.itertuples()])}

这不是说其余42条规范链没有主观指标，而是它们分散到低频类别；另有1条指标未映射。为了避免用极少数论文训练出貌似精确的推荐，主要规范集不建立指标模型。扩展规范集有95条达到阈值的观测、10个类别，才进行探索性建模。

## 资料依据

- JCSEE Program Evaluation Standards：https://evaluationstandards.org/program/
- WMU Checklist of the Program Evaluation Standards Statements：https://files.wmich.edu/s3fs-public/attachments/u350/2021/program-eval-standards-jc.pdf

"""

OUT.write_text(content, encoding="utf-8")
print(OUT)
