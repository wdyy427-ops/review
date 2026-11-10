from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\Administrator\Desktop\review\outputs\rq_review_20261024")
EXT = ROOT / "extended_results"


def rows_from_csv(name):
    d = pd.read_csv(EXT / name, keep_default_na=False)
    return [d.columns.tolist()] + d.astype(object).where(pd.notna(d), None).values.tolist()


overview = [
    ["问题", "结论", "证据位置"],
    ["1 层级数量", "125篇论文→158个评价案例→490条证据链→600个工具实例；单位间是一对多关系", "01_层级对应"],
    ["2 JCSEE操作化", "属于JCSEE启发的公开文本审查，不是完整30项标准合规认证", "08_JCSEE选择、09_JCSEE未纳入"],
    ["3 百分比", "432条已映射链；原100.1%来自一位小数独立四舍五入", "02_维度比例修正"],
    ["4 领域与阶段", "指标差异不稳定；工具与领域关联较明显、与阶段关联较弱", "03–07"],
    ["5 规则明细", "7项标准拆为41条本研究可观察规则；编码S/NR/C/NA", "10_规则代码本、11_规则分布"],
    ["6 分组验证", "同论文记录共享设计与工具；随机切分可明显虚高维度和工具模型", "12_分组CV验证"],
    ["7 48→6", "48条链中47条映射到22类指标；仅A1达到≥5链且≥3论文", "13_规范集指标支持"],
]

selected = [
    ["标准", "官方名称", "观察内容", "纳入理由"],
    ["U5", "Relevant Information／相关信息", "效果主张、构念、指标和工具是否形成与评价目的相关的链", "直接对应证据链的相关性和可操作性"],
    ["A2", "Valid Information／有效信息", "构念、指标、工具、题项、计分和效度依据", "判断测量能否支持预期解释"],
    ["A3", "Reliable Information／可靠信息", "量化信度、评分／编码一致性、质性可信性和重复实施细节", "判断信息是否足够稳定、一致"],
    ["A4", "Explicit Program and Context Descriptions／明确对象与情境", "对象、样本、招募、任务、环境、比较条件及AI设计情境", "判断证据适用边界"],
    ["A6", "Sound Designs and Analyses／健全设计与分析", "设计、分析、比较条件、结果及因果越界", "判断设计和分析是否支撑主张"],
    ["A7", "Explicit Evaluation Reasoning／明确评价推理", "主张、结果、位置、完整证据链和推理强度", "判断从信息到结论是否可追溯"],
    ["E1", "Evaluation Documentation／评价记录", "目的、设计、程序、工具、题项、计分、结果和位置", "判断读者能否复核评价过程"],
]

omitted = [
    ["代码", "标准", "未进入链级质量层级的原因"],
    ["U1", "Evaluator Credibility／评价者可信度", "评价者资格和情境信誉通常无法由一条证据链判断"],
    ["U2", "Attention to Stakeholders／关注利益相关者", "无法判断是否关注完整利益相关者范围"],
    ["U3", "Negotiated Purposes／协商目的", "目的如何持续协商通常不报告"],
    ["U4", "Explicit Values／明确价值", "目标用户不能替代个人与文化价值的明确说明"],
    ["U6", "Meaningful Processes and Products／有意义过程与成果", "参与者理解和行为改变多在测量链之外"],
    ["U7", "Timely and Appropriate Communicating and Reporting／及时适当沟通", "受众、时机和传播过程无法从链判断"],
    ["U8", "Concern for Consequences and Influence／关注后果与影响", "评价使用后的后果通常不在论文中"],
    ["F1–F4", "项目管理、实用程序、情境可行性、资源使用", "需要预算、政治情境、实施管理和资源记录"],
    ["P1–P7", "包容、协议、人权、公平、披露、利益冲突、财务责任", "属于组织和伦理治理层面；论文声明只能覆盖局部"],
    ["A1", "Justified Conclusions and Decisions／有依据的结论与决定", "与A7、A4重叠且需要结论后果情境；避免重复计权"],
    ["A5", "Information Management／信息管理", "需要收集、复核、验证和存储流程"],
    ["A8", "Communication and Reporting／沟通与报告", "整篇报告层面，不适合链级计分；局部由A7和E1覆盖"],
    ["E2", "Internal Metaevaluation／内部元评价", "需要团队实际进行元评价的证据"],
    ["E3", "External Metaevaluation／外部元评价", "需要独立外部元评价证据"],
]

notes = [
    ["主题", "说明"],
    ["JCSEE口径", "A2.1等是本研究为可复核编码设置的规则，不是JCSEE官方子条款。NR表示公开论文未报告或无法判断，不表示研究一定没有实施。"],
    ["交叉分布", "一条链可多领域、多阶段；一条链可有多个工具。n_assignments是展开后的分配次数。颜色建议使用情境内比例，格内显示n。"],
    ["卡方限制", "指标×领域84.8%、指标×阶段41.2%的期望频数小于5，且多标签展开违反完全独立假设，p值仅作探索性描述。"],
    ["扩展规范集", "U5、A2、A4、A6、A7、E1至少S/P，任何标准无C；A3可NR。表示可靠性未知，只用于敏感性和网页回退。"],
    ["模型阈值", "目标类别至少5条证据链且来自至少3篇论文；防止由单篇或极少样本支配模型。"],
    ["来源", "JCSEE: https://evaluationstandards.org/program/；WMU checklist: https://files.wmich.edu/s3fs-public/attachments/u350/2021/program-eval-standards-jc.pdf"],
]

sheets = {
    "00_答复概览": overview,
    "01_层级对应": rows_from_csv("hierarchy_counts.csv"),
    "02_维度比例修正": rows_from_csv("dimension_exact_percentages.csv"),
    "03_指标×领域": rows_from_csv("rq1_indicator_by_domain.csv"),
    "04_指标×阶段": rows_from_csv("rq1_indicator_by_stage.csv"),
    "05_工具×领域": rows_from_csv("rq1_tool_by_domain.csv"),
    "06_工具×阶段": rows_from_csv("rq1_tool_by_stage.csv"),
    "07_交叉检验": rows_from_csv("rq1_extended_context_tests.csv"),
    "08_JCSEE选择": selected,
    "09_JCSEE未纳入": omitted,
    "10_规则代码本": rows_from_csv("jcsee_subrule_codebook.csv"),
    "11_规则分布": rows_from_csv("jcsee_subrule_summary.csv"),
    "12_分组CV验证": rows_from_csv("grouped_vs_random_cv.csv"),
    "13_规范集指标支持": rows_from_csv("main_set_indicator_support.csv"),
    "14_方法说明": notes,
}

(ROOT / "supplement_workbook_data.json").write_text(json.dumps(sheets, ensure_ascii=False), encoding="utf-8")
print(ROOT / "supplement_workbook_data.json")
