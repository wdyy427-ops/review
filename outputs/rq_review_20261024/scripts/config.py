from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LABELS={
'domain':dict(zip(['D1','D2','D3','D4','D5','D6'],['视觉传播设计','工业／产品设计','时装设计','室内设计','服务设计','UI/UX设计'])),
'stage':dict(zip(['S1','S2','S3','S4'],['研究','构思','原型制作与测试','实施'])),
'ai_function':dict(zip(['F1','F2','F3','F4','F5','F6'],['识别需求','知识检索','方案生成','原型实现','评估反馈','迭代优化'])),
'ai_role':dict(zip(['R1','R2','R3'],['跟随式生成AI','顾问式AI','即兴式AI'])),
'dimension':dict(zip('ABCDE',['设计成果质量','设计过程质量','设计者认知、情感与能力','人机交互体验','社会情境价值'])),
'purpose':dict(zip(['P1','P2','P3','P4'],['价值引出与标准建构','模型监督、校准与代理目标','形成性反馈与迭代引导','总结性验证与比较'])),
'object':dict(zip(['O1','O2','O3','O4','O5','O6','O7'],['设计成果','设计过程／工作流','AI系统及界面','人机协作关系','设计者状态与能力','设计成果使用／社会后果','需求偏好与价值标准'])),
'evaluator':dict(zip(['V1','V2','V3','V4','V5','V6'],['专业设计师／领域专家','设计学生／新手','目标终端用户','一般公众／众包','客户／组织利益相关者','研究者自评'])),
'target_user':dict(zip(['U1','U2','U3','U4','U5','U6'],['专业设计师','设计学生／新手','非专业创作者','组织／团队','其他专业人员','设计成果终端用户'])),
'source':dict(zip(['H1','H2','H3','H4','H5','H6'],['参与者自陈','第三方人工评价','访谈／开放回答／思维口述','既有评论／社交文本','行为／任务日志','自动计算代理'])),
'setting':dict(zip(['L1','L2','L3','L4','L5'],['控制环境／实验室','线上远程研究','实际工作／现场','混合','档案／二手资料'])),
'design':dict(zip(['G1','G2','G3','G4','G5','G6','G7','G8'],['单条件描述性评价','被试内比较','被试间比较','混合比较','质性探索','档案观察','偏好／权重引出','监督标签／模型验证'])),
'tool_family':dict(zip(['M1','M2','M3','M4','M5','M6','M7'],['自编数值等级／语义差异评分','具名量表','成对比较／排序／偏好选择','访谈／焦点小组','开放文本／观察／思维口述','多准则赋权／感性工学评价','既有文本感知分析'])),
'tool_origin':dict(zip(['T1','T2','T3','T4','T5'],['原量表直接使用','改编／翻译既有工具','自编工具','质性研究方案','二手感知数据'])),
'claim_type':dict(zip(['C1','C2','C3','C4'],['描述性状态','组间／条件比较','明确因果主张','探索／需求引出'])),
'task':dict(zip(['K1','K2','K3','K4','K5','K6','K7'],['需求提取／研究分析','概念创意／探索','方案表达／内容制作','方案比较／选择','修改／优化','实现／测试','协作沟通／反馈'])),
'constraint':dict(zip(['Q1','Q2','Q3','Q4','Q5','Q6'],['评价者可及性限制','时间／答题负担限制','语言／文化适配要求','原型／真实场景可及性限制','既有数据可及性','隐私／组织访问限制'])),
'audit_status':{'S':'报告提供充分支持','P':'提供部分支持','C':'发现明确问题','NR':'未报告／无法判断','NA':'不适用'},
}
INDICATORS={
'A':['新颖性','美观性','适用性','可行性','保真度','全面性'],
'B':['时间效率','工作负荷','迭代效率','决策支持','过程连续性','交接效率'],
'C':['灵感刺激','知识获得','自我效能','参与沉浸','愉悦','反思','固着依赖','能力扩展'],
'D':['易用性','使用意愿','控制感','可解释性','信任感','主体性','角色、分工与贡献公平','沟通、协调、冲突与共同理解'],
'E':['终端用户体验与接受','用户需求、情境与人群适配','专业与组织工作适配','文化、社会与公共价值','伦理、公平、偏见与包容','环境与可持续价值','商业、品牌与市场价值','长期使用、治理与责任']}
LABELS['indicator']={f'{k}{i}':v for k,vals in INDICATORS.items() for i,v in enumerate(vals,1)}
FIELD_NAMES={'domain':'设计领域','stage':'设计活动阶段','ai_function':'AI功能','ai_role':'AI介入角色','dimension':'评价维度','purpose':'评价目的','object':'评价对象','evaluator':'评价主体','target_user':'AI辅助目标用户','source':'实际证据来源','setting':'评价环境','design':'研究设计','tool_family':'测量工具族','tool_origin':'工具来源','claim_type':'效果主张类型','indicator':'主观指标类型','audit_status':'审查状态'}
FIELD_NAMES.update({'task':'设计任务类型','constraint':'明确报告的证据获取约束'})
STANDARDS={'U5':'信息与评价目的相关','A2':'测量解释的效度依据','A3':'信息的可靠性依据','A4':'对象与情境描述','A6':'研究设计与分析适切性','A7':'评价推理可追溯性','E1':'评价记录充分性'}
SOURCE_URLS={
'JCSEE':'https://evaluationstandards.org/program/',
'JCSEE_checklist':'https://wmich.edu/sites/default/files/attachments/u350/2021/program-eval-standards-jc.pdf',
'ICoD_domain':'https://www.theicod.org/en/professional-design/what-is-a-designer/design-disciplines',
'ICoD_stage':'https://www.theicod.org/en/professional-design/design-ing/design-ing',
'CDC':'https://www.cdc.gov/evaluation/php/evaluation-framework-action-guide/step-4-gather-credible-evidence.html',
'GroupedCV':'https://scikit-learn.org/stable/modules/cross_validation.html',
'NestedCV':'https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html',
'TabPFN':'https://www.nature.com/articles/s41586-024-08328-6',
'Model_selection_bias':'https://jmlr.org/papers/v11/cawley10a.html',
}
def code_labels(field,codes):
    if isinstance(codes,str): codes=[codes]
    return '；'.join(LABELS.get(field,{}).get(c,c) for c in (codes or []))
def as_codes(x):
    if x is None:return []
    return x if isinstance(x,list) else [x]
def quality_gate(audit):
    # All statuses remain available; this is a declared research-specific selection rule.
    a={s:audit.get(s,'NR') for s in STANDARDS}
    strict=all(a[s] in ('S','NA') for s in ['A2','A3','A6','A7']) and all(a[s] in ('S','P','NA') for s in ['U5','A4','E1']) and 'C' not in a.values()
    sensitivity=all(a[s] in ('S','P','NA') for s in ['A2','A6','A7','A4']) and 'C' not in a.values()
    return int(strict),int(sensitivity)
