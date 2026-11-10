# AI-assisted Design Workflow 中 Perceived Effect 评价实践：系统综述、规范性审查与推荐建模

## 研究范围与最终数据

本研究对用户提供的 125 篇全文重新编码。旧工作簿只用于保留已经确定的固定分类，不把旧表中的效果主张、构念、指标、工具或评价结果当作事实来源。全文证据链按 **Evaluation Question／效果主张 → Construct／感知构念 → Indicator／主观指标 → Measure／测量工具** 记录，情境条件按评价目的、对象、环境、评价主体、目标用户、数据源、设计阶段、任务及 AI 角色与功能记录。

最终数据包括 125 篇论文，其中 94（75.2%） 经全文筛查确认含有人类主观感知评价；共形成 158 个评价案例和 490 条可追溯证据链。12 篇由逐页人工复核结果覆盖，113 篇采用“全文规则筛查＋高相关证据页语义清点＋PDF原句回定位”的组合流程。自动流程只保留能重新定位到原文页码的证据链。后续正式投稿前仍建议由两名研究者进行独立复核和一致性检验。

### 固定分类

- 设计领域：ICoD 六类。
- 设计阶段：ICoD 四阶段。
- AI 功能：识别需求、知识检索、方案生成、原型实现、评估反馈、迭代优化。
- 评价维度：设计成果质量、设计过程质量、设计者认知情感与能力、人机交互体验、社会情境价值。
- 评价目的：价值引出与标准建构、模型监督／校准与代理目标、形成性反馈与迭代引导、总结性验证与比较。
- 无法可靠归入固定二级分类的内容标为 `UNMAPPED`，没有因量化需要而临时创造新类别。

## RQ1 评价证据的分布

### 发表年份

| 代码 | 类别 | n | 分母 | 占比 |
|---|---|---|---|---|
| 2026 | 2026 | 56 | 125 | 44.8% |
| 2025 | 2025 | 27 | 125 | 21.6% |
| 2024 | 2024 | 20 | 125 | 16.0% |
| 2022 | 2022 | 11 | 125 | 8.8% |
| 2023 | 2023 | 11 | 125 | 8.8% |

### 设计领域

| 代码 | 类别 | n | 分母 | 占比 |
|---|---|---|---|---|
| D2 | 工业／产品设计 | 89 | 125 | 71.2% |
| D1 | 视觉传播设计 | 32 | 125 | 25.6% |
| D3 | 时装设计 | 26 | 125 | 20.8% |
| D6 | UI/UX设计 | 14 | 125 | 11.2% |
| D4 | 室内设计 | 5 | 125 | 4.0% |
| D5 | 服务设计 | 3 | 125 | 2.4% |
| UNMAPPED | UNMAPPED | 1 | 125 | 0.8% |

### 设计阶段

| 代码 | 类别 | n | 分母 | 占比 |
|---|---|---|---|---|
| S2 | 构思 | 84 | 125 | 67.2% |
| S1 | 研究 | 77 | 125 | 61.6% |
| S4 | 实施 | 68 | 125 | 54.4% |
| S3 | 原型制作与测试 | 44 | 125 | 35.2% |

### AI 功能

| 代码 | 类别 | n | 分母 | 占比 |
|---|---|---|---|---|
| F5 | 评估反馈 | 101 | 125 | 80.8% |
| F6 | 迭代优化 | 99 | 125 | 79.2% |
| F3 | 方案生成 | 68 | 125 | 54.4% |
| F4 | 原型实现 | 52 | 125 | 41.6% |
| F2 | 知识检索 | 28 | 125 | 22.4% |
| F1 | 识别需求 | 12 | 125 | 9.6% |

### Perceived effect 评价维度

| 代码 | 类别 | n | 分母 | 占比 |
|---|---|---|---|---|
| A | 设计成果质量 | 136 | 490 | 27.8% |
| C | 设计者认知、情感与能力 | 101 | 490 | 20.6% |
| D | 人机交互体验 | 91 | 490 | 18.6% |
| E | 社会情境价值 | 63 | 490 | 12.9% |
| UNMAPPED | UNMAPPED | 58 | 490 | 11.8% |
| B | 设计过程质量 | 41 | 490 | 8.4% |

### 主观指标

| 代码 | 类别 | n | 分母 | 占比 |
|---|---|---|---|---|
| UNMAPPED | UNMAPPED | 64 | 490 | 13.1% |
| A3 | 适用性 | 36 | 490 | 7.3% |
| A1 | 新颖性 | 32 | 490 | 6.5% |
| C5 | 愉悦 | 28 | 490 | 5.7% |
| D8 | 沟通、协调、冲突与共同理解 | 24 | 490 | 4.9% |
| A4 | 可行性 | 23 | 490 | 4.7% |
| A2 | 美观性 | 20 | 490 | 4.1% |
| D3 | 控制感 | 20 | 490 | 4.1% |
| C2 | 知识获得 | 18 | 490 | 3.7% |
| C1 | 灵感刺激 | 18 | 490 | 3.7% |
| E2 | 用户需求、情境与人群适配 | 17 | 490 | 3.5% |
| D1 | 易用性 | 16 | 490 | 3.3% |
| B5 | 过程连续性 | 14 | 490 | 2.9% |
| E1 | 终端用户体验与接受 | 13 | 490 | 2.7% |
| C6 | 反思 | 12 | 490 | 2.4% |
| A6 | 全面性 | 12 | 490 | 2.4% |
| E7 | 商业、品牌与市场价值 | 11 | 490 | 2.2% |
| D7 | 角色、分工与贡献公平 | 11 | 490 | 2.2% |
| B2 | 工作负荷 | 11 | 490 | 2.2% |
| D5 | 信任感 | 10 | 490 | 2.0% |

### 测量工具族

| 代码 | 类别 | n | 分母 | 占比 |
|---|---|---|---|---|
| M1 | 自编数值等级／语义差异评分 | 374 | 490 | 76.3% |
| M4 | 访谈／焦点小组 | 274 | 490 | 55.9% |
| M5 | 开放文本／观察／思维口述 | 234 | 490 | 47.8% |
| M2 | 具名量表 | 95 | 490 | 19.4% |
| M3 | 成对比较／排序／偏好选择 | 62 | 490 | 12.7% |
| M6 | 多准则赋权／感性工学评价 | 56 | 490 | 11.4% |
| M7 | 既有文本感知分析 | 52 | 490 | 10.6% |
| UNMAPPED | UNMAPPED | 9 | 490 | 1.8% |
| NR | NR | 8 | 490 | 1.6% |

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

| 标准 | 含义 | S充分 | P部分 | C问题 | NR未报告 | NA不适用 |
|---|---|---|---|---|---|---|
| A2 | 测量解释的效度依据 | 40.5% | 59.5% | 0.0% | 0.0% |  |
| A3 | 信息的可靠性依据 | 45.6% | 7.6% | 0.0% | 46.8% |  |
| A4 | 对象与情境描述 | 5.1% | 81.0% | 0.0% | 13.9% |  |
| A6 | 研究设计与分析适切性 | 27.2% | 16.5% | 3.2% | 53.2% |  |
| A7 | 评价推理可追溯性 | 32.3% | 8.2% | 6.3% | 53.2% |  |
| E1 | 评价记录充分性 | 8.2% | 36.7% | 0.0% | 55.1% |  |
| U5 | 信息与评价目的相关 | 19.6% | 80.4% | 0.0% | 0.0% |  |

| 案例层级 | 预设规则 | n | 分母 |
|---|---|---|---|
| 严格高规范案例 | A2/A3/A6/A7为S或NA；U5/A4/E1为S/P/NA；无C | 13 | 158 |
| 关联分析案例 | U5/A2/A4/A6/A7/E1为S/P/NA；A3未报告可保留；无C | 59 | 158 |
| 全部人类主观评价案例 | 全文确认存在人类主观评价 | 158 | 158 |

“严格高规范案例”用于判断当前文献是否已经提供完整、可信且可直接复用的评价依据。“关联分析案例”保留未报告可靠性但其他关键环节至少部分满足、且没有明确问题的案例；A3 作为质量指标而非硬排除条件。这一层级只用于探索情境与选择之间的经验关系，不等同于 JCSEE 官方评分。

## RQ3 情境条件与评价证据之间的关联

### 分析单位与统计顺序

1. 先用 Fisher 精确检验扫描“情境代码—评价维度／工具族”的二元共现关系。
2. 同时报告条件概率、基线概率、lift、有向 Cramér’s V 和原始 p 值。
3. 在同一分析族内用 Benjamini–Hochberg 控制多重比较。
4. 只把具有足够共同出现次数的关系带入推荐表；`证据不足` 不作为推荐依据。
5. 预测模型用论文编号进行分组交叉验证，保证同一论文的多条证据链不会同时进入训练集与测试集。

### 主要关联

| 情境 | 评价结果 | 共同出现 | 情境n | 条件概率 | 基线 | lift | V | p | BH q | 证据等级 |
|---|---|---|---|---|---|---|---|---|---|---|
| 访谈／开放回答／思维口述 | 访谈／焦点小组 | 20 | 29 | 69.0% | 33.9% | 2.034 | 0.728 | 0.000 | 0.000 | 较强 |
| 设计过程／工作流 | 设计者认知、情感与能力 | 26 | 33 | 78.8% | 47.5% | 1.660 | 0.707 | 0.000 | 0.000 | 较强 |
| AI系统及界面 | 设计者认知、情感与能力 | 27 | 36 | 75.0% | 47.5% | 1.580 | 0.690 | 0.000 | 0.000 | 较强 |
| 设计过程／工作流 | 人机交互体验 | 23 | 33 | 69.7% | 40.7% | 1.713 | 0.666 | 0.000 | 0.000 | 较强 |
| 概念创意／探索 | 访谈／焦点小组 | 18 | 26 | 69.2% | 33.9% | 2.042 | 0.663 | 0.000 | 0.000 | 较强 |
| 访谈／开放回答／思维口述 | 开放文本／观察／思维口述 | 21 | 29 | 72.4% | 40.7% | 1.780 | 0.635 | 0.000 | 0.000 | 较强 |
| 访谈／开放回答／思维口述 | 设计者认知、情感与能力 | 23 | 29 | 79.3% | 47.5% | 1.671 | 0.627 | 0.000 | 0.000 | 较强 |
| AI系统及界面 | 人机交互体验 | 23 | 36 | 63.9% | 40.7% | 1.571 | 0.591 | 0.000 | 0.000 | 较强 |
| 设计过程／工作流 | 开放文本／观察／思维口述 | 22 | 33 | 66.7% | 40.7% | 1.639 | 0.596 | 0.000 | 0.000 | 较强 |
| 方案表达／内容制作 | 设计者认知、情感与能力 | 23 | 30 | 76.7% | 47.5% | 1.615 | 0.595 | 0.000 | 0.000 | 较强 |
| 设计学生／新手 | 设计者认知、情感与能力 | 20 | 24 | 83.3% | 47.5% | 1.756 | 0.595 | 0.000 | 0.000 | 较强 |
| 概念创意／探索 | 设计者认知、情感与能力 | 21 | 26 | 80.8% | 47.5% | 1.702 | 0.592 | 0.000 | 0.000 | 较强 |
| 概念创意／探索 | 开放文本／观察／思维口述 | 19 | 26 | 73.1% | 40.7% | 1.796 | 0.585 | 0.000 | 0.001 | 较强 |
| 需求提取／研究分析 | 设计者认知、情感与能力 | 20 | 25 | 80.0% | 47.5% | 1.686 | 0.559 | 0.000 | 0.001 | 较强 |
| 识别需求 | 多准则赋权／感性工学评价 | 10 | 21 | 47.6% | 18.6% | 2.554 | 0.553 | 0.000 | 0.002 | 较强 |
| 需求提取／研究分析 | 访谈／焦点小组 | 16 | 25 | 64.0% | 33.9% | 1.888 | 0.545 | 0.000 | 0.002 | 较强 |
| AI系统及界面 | 开放文本／观察／思维口述 | 22 | 36 | 61.1% | 40.7% | 1.502 | 0.520 | 0.000 | 0.003 | 较强 |
| 价值引出与标准建构 | 设计者认知、情感与能力 | 24 | 35 | 68.6% | 47.5% | 1.445 | 0.511 | 0.000 | 0.004 | 较强 |
| 设计学生／新手 | 开放文本／观察／思维口述 | 17 | 24 | 70.8% | 40.7% | 1.741 | 0.508 | 0.000 | 0.004 | 较强 |
| AI系统及界面 | 访谈／焦点小组 | 19 | 36 | 52.8% | 33.9% | 1.557 | 0.499 | 0.000 | 0.004 | 较强 |

关联是文献中的选择规律，不代表情境变量因果决定评价指标或工具。推荐系统因此显示支持量、概率和证据等级，而不输出唯一正确答案。

### 五类模型交叉验证

结构方程模型需要明确的潜变量测量模型、足够样本以及可解释的连续或有序观测指标。本研究的分析单位是嵌套在论文中的多标签类别选择，主要目标是预测“选择了哪类评价维度／工具”，所以 SEM 不适合承担主模型。采用频率基线、L2 多项逻辑回归、随机森林、极端随机树和直方图梯度提升进行比较，并以分组交叉验证的 macro-F1 为主指标。

| 目标 | 模型 | 链n | 论文n | 类别 | 折数 | Macro-F1 | SD | Weighted-F1 | 平衡准确率 | 分析层级 |
|---|---|---|---|---|---|---|---|---|---|---|
| 测量工具族 | 频率基线 | 256 | 35 | 6 | 5 | 0.156 | 0.027 | 0.333 | 0.237 | 关联分析案例 |
| 测量工具族 | 直方图梯度提升 | 256 | 35 | 6 | 5 | 0.138 | 0.131 | 0.265 | 0.173 | 关联分析案例 |
| 测量工具族 | L2多项逻辑回归 | 256 | 35 | 6 | 5 | 0.119 | 0.057 | 0.257 | 0.187 | 关联分析案例 |
| 测量工具族 | 极端随机树 | 256 | 35 | 6 | 5 | 0.109 | 0.024 | 0.258 | 0.180 | 关联分析案例 |
| 测量工具族 | 随机森林 | 256 | 35 | 6 | 5 | 0.101 | 0.041 | 0.237 | 0.156 | 关联分析案例 |
| 评价维度 | 直方图梯度提升 | 251 | 35 | 5 | 5 | 0.214 | 0.048 | 0.249 | 0.249 | 关联分析案例 |
| 评价维度 | 随机森林 | 251 | 35 | 5 | 5 | 0.201 | 0.060 | 0.248 | 0.244 | 关联分析案例 |
| 评价维度 | L2多项逻辑回归 | 251 | 35 | 5 | 5 | 0.198 | 0.026 | 0.234 | 0.246 | 关联分析案例 |
| 评价维度 | 极端随机树 | 251 | 35 | 5 | 5 | 0.185 | 0.059 | 0.232 | 0.224 | 关联分析案例 |
| 评价维度 | 频率基线 | 251 | 35 | 5 | 5 | 0.098 | 0.003 | 0.158 | 0.200 | 关联分析案例 |

模型结果用于检验情境信息是否具有可重复的选择信号。若复杂模型没有稳定超过频率基线，网站采用透明的频数、条件概率和质量门槛，不把不稳定模型包装成智能推荐。

## 指标与工具推荐规则

推荐流程分为两步：

1. 设计师先声明自己的效果主张。系统依据领域、阶段、AI 功能与角色、评价目的、对象、主体、用户和可用数据源，展示有文献支持的构念／指标候选。
2. 在确定构念或主观指标后，系统推荐实际测量工具族和论文中出现的工具实例，并同时显示支持论文数、证据链数、规范性层级和不确定性。

系统不主动替设计师生成需要证明的效果主张。效果主张体现研究目的和价值判断，应由研究者先提出；网站可以提示相似情境中常见但被遗漏的效果维度，作为覆盖检查。

### 支持度最高的指标—工具对应

| 指标代码 | 指标 | 工具代码 | 工具族 | 链n | 论文n | 经验概率 | 工具实例 |
|---|---|---|---|---|---|---|---|
| A1 | 新颖性 | M1 | 自编数值等级／语义差异评分 | 18 | 12 | 90.0% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| A3 | 适用性 | M1 | 自编数值等级／语义差异评分 | 16 | 11 | 72.7% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| A3 | 适用性 | M4 | 访谈／焦点小组 | 12 | 9 | 54.5% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| D3 | 控制感 | M1 | 自编数值等级／语义差异评分 | 11 | 8 | 91.7% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| C1 | 灵感刺激 | M4 | 访谈／焦点小组 | 9 | 8 | 90.0% | Additionally, the Creativity Support Index (CSI) (Cherry and Latulipe 2014) (0–10 scale) …；After completing both sessions, they completed questionnaires and participated in a semi-… |
| C5 | 愉悦 | M1 | 自编数值等级／语义差异评分 | 13 | 8 | 86.7% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| A3 | 适用性 | M5 | 开放文本／观察／思维口述 | 10 | 8 | 45.5% | Additionally, the Creativity Support Index (CSI) (Cherry and Latulipe 2014) (0–10 scale) …；After completing both sessions, they completed questionnaires and participated in a semi-… |
| C6 | 反思 | M1 | 自编数值等级／语义差异评分 | 9 | 7 | 90.0% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| D1 | 易用性 | M1 | 自编数值等级／语义差异评分 | 9 | 7 | 81.8% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| C1 | 灵感刺激 | M5 | 开放文本／观察／思维口述 | 8 | 7 | 80.0% | Additionally, the Creativity Support Index (CSI) (Cherry and Latulipe 2014) (0–10 scale) …；After completing both sessions, they completed questionnaires and participated in a semi-… |
| C5 | 愉悦 | M4 | 访谈／焦点小组 | 10 | 7 | 66.7% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| A1 | 新颖性 | M4 | 访谈／焦点小组 | 10 | 7 | 50.0% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| A1 | 新颖性 | M5 | 开放文本／观察／思维口述 | 9 | 7 | 45.0% | Additionally, the Creativity Support Index (CSI) (Cherry and Latulipe 2014) (0–10 scale) …；After completing both sessions, they completed questionnaires and participated in a semi-… |
| C8 | 能力扩展 | M5 | 开放文本／观察／思维口述 | 7 | 6 | 100.0% | Then the partici- pant was asked to remotely sign the informed consent form, and fill a d…；Specifically, upon receiving the user request through the Dialog Box, the system initiall… |
| B5 | 过程连续性 | M1 | 自编数值等级／语义差异评分 | 9 | 6 | 90.0% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| D8 | 沟通、协调、冲突与共同理解 | M5 | 开放文本／观察／思维口述 | 7 | 6 | 77.8% | In the experimental group, participants also reviewed and labelled intermediate graph out…；JOURNAL OF ENGINEERING DESIGN https://doi.org/10.1080/09544828.2026.2680619 Real-time dyn… |
| A4 | 可行性 | M1 | 自编数值等级／语义差异评分 | 8 | 6 | 61.5% | Additionally, the Creativity Support Index (CSI) (Cherry and Latulipe 2014) (0–10 scale) …；After completing both sessions, they completed questionnaires and participated in a semi-… |
| A4 | 可行性 | M5 | 开放文本／观察／思维口述 | 8 | 6 | 61.5% | Additionally, the Creativity Support Index (CSI) (Cherry and Latulipe 2014) (0–10 scale) …；After completing both sessions, they completed questionnaires and participated in a semi-… |
| D3 | 控制感 | M5 | 开放文本／观察／思维口述 | 7 | 6 | 58.3% | In the experimental group, participants also reviewed and labelled intermediate graph out…；JOURNAL OF ENGINEERING DESIGN https://doi.org/10.1080/09544828.2026.2680619 Real-time dyn… |
| C5 | 愉悦 | M5 | 开放文本／观察／思维口述 | 8 | 6 | 53.3% | Additionally, the Creativity Support Index (CSI) (Cherry and Latulipe 2014) (0–10 scale) …；After completing both sessions, they completed questionnaires and participated in a semi-… |
| A6 | 全面性 | M1 | 自编数值等级／语义差异评分 | 7 | 5 | 77.8% | In the experimental group, participants also reviewed and labelled intermediate graph out…；JOURNAL OF ENGINEERING DESIGN https://doi.org/10.1080/09544828.2026.2680619 Real-time dyn… |
| C2 | 知识获得 | M1 | 自编数值等级／语义差异评分 | 6 | 5 | 75.0% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| B5 | 过程连续性 | M4 | 访谈／焦点小组 | 7 | 5 | 70.0% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| C6 | 反思 | M4 | 访谈／焦点小组 | 7 | 5 | 70.0% | Before the experiment, participants completed a survey and received 20 min of training on…；Participants then took part in semi-structured interviews, where they elaborated on their… |
| D8 | 沟通、协调、冲突与共同理解 | M1 | 自编数值等级／语义差异评分 | 6 | 5 | 66.7% | In the experimental group, participants also reviewed and labelled intermediate graph out…；JOURNAL OF ENGINEERING DESIGN https://doi.org/10.1080/09544828.2026.2680619 Real-time dyn… |

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

- [CDC: Gather Credible Evidence](https://www.cdc.gov/evaluation/php/evaluation-framework-action-guide/step-4-gather-credible-evidence.html)：用于组织评价问题、概念／构念、指标与测量之间的证据形成关系。
- [JCSEE Program Evaluation Standards](https://evaluationstandards.org/program/) 与 [标准清单](https://wmich.edu/sites/default/files/attachments/u350/2021/program-eval-standards-jc.pdf)：用于建立规范性审查维度；本文只选取能从论文全文观察的条目进行操作化。
- [ICoD Design Disciplines](https://www.theicod.org/en/professional-design/what-is-a-designer/design-disciplines) 与 [Designing](https://www.theicod.org/en/professional-design/design-ing/design-ing)：用于保留六类设计领域和四阶段分类。
- [Scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) 与 [nested model selection example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)：用于避免同一论文的数据泄漏和说明模型选择偏差控制。
