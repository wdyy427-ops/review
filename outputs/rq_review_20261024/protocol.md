# 125篇AI辅助设计感知效应综述：编码与分析协议

日期：2026-10-24。这是研究者为本综述操作化的JCSEE适用标准，不是官方认证量表。所有结果为AI辅助全文编码，未声称独立人工双人编码。旧表仅作为待核查索引，不能当作原文。

## 来源与结构
全文目录：最终/全文-重新排序 - 副本/1.pdf至125.pdf。页码均为PDF物理页，从1起。
extracted/NNN.json包含metadata、previous_context、previous_chains和逐页全文；NNN.txt为逐页全文。
必须阅读全部正文（包括方法、结果、讨论和有用附录），不要只按关键词判定。若表格或提取异常，检查PDF页图。
逐篇核对题目与PDF是否匹配。逐项核查旧指标是否确实有人的主观感知数据；纯客观精度/时长、作者讨论、仅技术说明不能当作已测得感知效应。保留排除日志。

## 保留的类别
domain: D1视觉传播设计,D2工业／产品设计,D3时装设计,D4室内设计,D5服务设计,D6UI/UX设计。
stage: S1研究,S2构思,S3原型制作与测试,S4实施。按AI辅助的设计活动，而非把所有用户实验一概计为设计原型阶段。另记evaluation_stage。
ai_function: F1识别需求,F2知识检索,F3方案生成,F4原型实现,F5评估反馈,F6迭代优化。
ai_role: R1跟随式生成AI,R2顾问式AI,R3即兴式AI。
dimension: A设计成果质量,B设计过程质量（用户最近称效能，沿用旧表类别并记录别名）,C设计者认知、情感与能力,D人机交互体验,E社会情境价值。
indicator: A1新颖性,A2美观性,A3适用性,A4可行性,A5保真度,A6全面性; B1时间效率,B2工作负荷,B3迭代效率,B4决策支持,B5过程连续性,B6交接效率; C1灵感刺激,C2知识获得,C3自我效能,C4参与沉浸,C5愉悦,C6反思,C7固着依赖,C8能力扩展; D1易用性,D2使用意愿,D3控制感,D4可解释性,D5信任感,D6主体性,D7角色、分工与贡献公平,D8沟通、协调、冲突与共同理解; E1终端用户体验与接受,E2用户需求、情境与人群适配,E3专业与组织工作适配,E4文化、社会与公共价值,E5伦理、公平、偏见与包容,E6环境与可持续价值,E7商业、品牌与市场价值,E8长期使用、治理与责任。
purpose: P1价值引出与标准建构,P2模型监督、校准与代理目标,P3形成性反馈与迭代引导,P4总结性验证与比较。用户已确认保留四类。
预设类允许多选。NR=未报告，UNMAPPED=已报告但既定类别无法准确容纳（不能强塞，提供理由），NA=不适用。它们是缺失/适用性状态，不算新实质类别。

## 新增统一类别（阅读后可报告缺口，修改必须全库一致）
object: O1设计成果,O2设计过程/工作流,O3AI系统及界面,O4人机协作关系,O5设计者状态与能力,O6设计成果使用/社会后果,O7需求偏好与价值标准。
evaluator: V1专业设计师/领域专家,V2设计学生/新手,V3目标终端用户,V4一般公众/众包,V5客户/组织利益相关者,V6研究者自评；身份未明NR。目标用户与实际评价者分别记录。
target_user: U1专业设计师,U2设计学生/新手,U3非专业创作者,U4组织/团队,U5其他专业人员,U6设计成果终端用户。
source: H1参与者自陈,H2第三方人工评价,H3访谈/开放回答/思维口述,H4既有评论/社交文本,H5行为/任务日志,H6自动计算代理。只有H5/H6且无人的主观感知证据者不算感知评价证据链。
setting: L1控制环境/实验室,L2线上远程研究,L3实际工作/现场,L4混合,L5档案/二手资料,NR。
design: G1单条件描述性评价,G2被试内比较,G3被试间比较,G4混合比较,G5质性探索,G6档案观察,G7偏好/权重引出,G8监督标签/模型验证,NR。
tool_family: M1自编数值等级/语义差异评分,M2具名量表,M3成对比较/排序/偏好选择,M4访谈/焦点小组,M5开放文本/观察/思维口述,M6多准则赋权/感性工学评价,M7既有文本感知分析,NR。允许多选，不把Likert当成已验证具名工具。
tool_origin: T1原量表直接使用,T2改编/翻译既有工具,T3自编工具,T4质性研究方案,T5二手感知数据,NR。
claim_type: C1描述性状态,C2组间/条件比较,C3明确因果主张,C4探索/需求引出。
task: K1需求提取/研究分析,K2概念创意/探索,K3方案表达/内容制作,K4方案比较/选择,K5修改/优化,K6实现/测试,K7协作沟通/反馈。评价案例task_codes可多选，task仍保留具体任务原文概括。
constraint: Q1评价者可及性限制,Q2时间/答题负担限制,Q3语言/文化适配要求,Q4原型/真实使用场景可及性限制,Q5既有数据可及性,Q6隐私/组织访问限制。仅论文明确报告这些条件影响测量安排时编码，不能由小样本/线上招募自行推断；否则NR。constraints_raw保留原文及页码。实际source_codes是测量实现的一部分，默认不作工具选择模型的前置输入。

## 每篇输出JSON schema
每篇单独保存 agents/paper_NNN.json。数组中的对象使用以下键。解释用中文，原文引文保持原语言。
{
 paper_id:int,title_match:bool,reviewed_pages:[int],scope_note:str,
 domain_codes:[],stage_codes:[],ai_function_codes:[],ai_role_codes:[],target_user_codes:[],
 context_summary:str,context_evidence:[{page:int,quote:str}],
 evaluations:[{
  eval_id:str,legacy_eval_ids:[],purpose_codes:[],object_codes:[],evaluator_codes:[],source_codes:[],setting_code:str,design_code:str,evaluation_stage_codes:[],
  sample_n:number|null,sample_description:str,recruitment:str,task:str,comparator:str,procedure:str,analysis:str,actual_results:str,limitations:str,ethics:str,
  evidence:[{field:str,page:int,quote:str}],
  audit:[{standard:'U5'|'A2'|'A3'|'A4'|'A6'|'A7'|'E1',status:'S'|'P'|'C'|'NR'|'NA',facts:str,reason:str,pages:[int],quote:str}],
  chains:[{
   legacy_rows:[int],claim_quote:str,claim_summary:str,claim_type:str,construct_raw:str,indicator_raw:str,item_quote:str,dimension_code:str,indicator_code:str,
   instrument_raw:str,tool_family_codes:[],tool_origin_code:str,adaptation:str,response_scoring:str,validity_evidence:str,reliability_evidence:str,result_quote:str,effect_direction:str,pages:[int],
   audit_overrides:[{standard:str,status:str,facts:str,reason:str,pages:[int],quote:str}]
  }]
 }],
 excluded_legacy_rows:[{legacy_row:int,reason:str,pages:[int]}],added_evidence_notes:str,category_gaps:[]
}
每条旧编码行（_legacy_row）必须出现在chain.legacy_rows或excluded_legacy_rows之一，可合并冗余条目，不能遗漏。新发现链legacy_rows为空。只保留实际感知证据。原题项未报告填NR，不把译写当原文。
一个评价案例可有多条证据链。不要给每条题项机械地创建重复链：同构念同工具同条件可以合并，保留所有原题项和legacy_rows。

## JCSEE适用条款的审查锚点
U5：明确目的/问题与所收集感知信息相符，能服务拟回答问题；明确匹配S，仅隐含P，明确错配C，无法识别NR。
A2：构念含义、题项/指标及测量解释有适切性依据。目标人群/评价对象一致。明确操作化且有内容/既有或当前效度依据S，表面匹配或依据不完整P，明确构念/对象错配C，无法判断NR。具名量表并不自动S。
A3：针对信息用途提供可靠/一致性支持（适当的量表信度、评分者一致性、复测、明确质性可信性措施等）；充分S，部分P，明确可靠性问题C，未报告NR。不强求单题Cronbach alpha，不把alpha当效度。
A4：任务、对象、参加者和研究条件足以理解结果S，部分缺失P，严重误述C，核心均缺NR。
A6：设计和分析足以支撑实际主张S，依据不完整P，明显错误或不支持所声称比较/因果C，无法判断NR。描述性主张不强制显著性检验；不因小样本自动C。
A7：信息/分析到结果及结论的推理可追溯且力度相称S，部分P，明显过度推断C，无法追溯NR。
E1：所用题项/程序/数据及结果有足够记录S，部分缺失P，NR不可复核。公开原始数据不是S的必要条件。
S=报告提供充分支持；P=提供部分支持；C=发现明确问题；NR=未报告/不足以判断；NA=不适用。不是量表分数，禁止直接求平均作官方规范性总分。每项有逐页证据和理由；NR列出查阅章节及缺何信息。

## 在关联分析前锁定的纳入规则
主要规范性证据子集：A2、A3、A6、A7均为S（或有明确理由NA），U5/A4/E1至少P，且没有C。不预设通过比例。若样本不足，报告不可估计，不放宽规则冒称规范。
敏感性子集：A2/A6/A7为S或P、A4为S或P、全项无C，单独标注报告支持较充分；所有实际感知案例为描述基线。
三个样本分层均报告。组间排除构成对比，NR不是实际质量差。

## 模型协议
主张/构念选择与测量选择分开。模型A：评价案例为单位预测感知维度/指标的多标签分布；模型B：案例-指标为单位，用情境+构念预测工具族。指标代码的首字母直接决定维度，不能把指标作为模型A特征或以此证明关联。
所有训练/调参/验证按论文ID分组；不把同篇的多条指标当独立样本。对照常数发生率基线，比较正则化逻辑回归、随机森林、ExtraTrees、梯度提升（必要时SVM替代），嵌套分组交叉验证，报告宏/微F1、AP、Brier或适当排名指标及论文级bootstrap不确定性。参数/缺失处理只在训练折拟合。样本/类别不足则只描述，不硬拟合SEM。
关联统计以论文/案例去重表为基础，采用分组置换或论文聚类bootstrap，BH多重比较校正。预测性能与因果解释分开。
网站为本地研究推荐原型，提供文献案例/工具使用证据，不把频繁使用自动称为经过验证最优。
