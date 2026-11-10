from __future__ import annotations

import json
import math

import pandas as pd

from config import ROOT, LABELS, FIELD_NAMES, SOURCE_URLS
from revised_pipeline import TOOL_LABELS, AUDIT_LABELS, STATUS_LABELS


DATA = ROOT / "revised_results"


def safe(v):
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and not math.isfinite(v):
        return "∞" if v > 0 else ("-∞" if v < 0 else None)
    return v


def read(name):
    return pd.read_csv(DATA / name, keep_default_na=False)


def rows(df):
    return [list(map(str, df.columns))] + [[safe(v) for v in row] for row in df.itertuples(index=False, name=None)]


def main():
    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    chains = read("evidence_chains_revised.csv")
    instances = read("measure_instances.csv")
    audits = read("jcsee_chain_audit.csv")

    sheets = {}
    sheets["00_研究概览"] = [
        ["项目", "结果", "统计口径与解释"],
        ["全文论文", summary["papers"], "用户提供的125篇论文；固定二级分类按既定代码本保留"],
        ["评价案例", summary["evaluation_cases"], "独立样本或独立研究为一个评价案例"],
        ["评价证据链", summary["evidence_chains"], "效果主张→构念→指标→测量工具；RQ2的规范性审查单位"],
        ["测量工具实例", summary["measure_instances"], "一条证据链可包含多个工具；每个实例仅属于M1–M5之一"],
        ["工具类别已判定", int(instances.tool_code.isin(TOOL_LABELS).sum()), "其余实例保留UNMAPPED，未为建模方便强行归类"],
        ["已映射评价维度的证据链", summary["mapped_dimension_chains"], "用于RQ1评价维度分布"],
        ["已映射主观指标的证据链", summary["mapped_indicator_chains"], "用于RQ1指标分布"],
        ["Q1高置信证据链", summary["Q1_high_confidence"], "核心标准充分或适用时满足，且无明确问题"],
        ["Q2可用证据链", summary["Q2_usable"], "核心标准至少部分支持，且无明确问题"],
        ["主要规范集", summary["main_model_chains"], "Q1+Q2；用于主分析与严格推荐依据"],
        ["扩展规范集", summary["sensitivity_model_chains"], "允许A3未报告，其他关键标准至少部分支持；用于敏感性分析与网页回退"],
        ["排除证据链", summary["excluded"], "发现明确问题"],
    ]
    sheets["01_论文"] = rows(read("papers.csv"))
    sheets["02_评价案例"] = rows(read("evaluation_cases.csv"))
    sheets["03_评价证据链"] = rows(chains)
    sheets["04_测量工具实例"] = rows(instances)
    sheets["05_JCSEE链级审查"] = rows(audits)

    temporal = pd.concat([
        read("rq1_dimension_by_year.csv").assign(analysis="评价维度年度分布"),
        read("rq1_indicator_by_year.csv").assign(analysis="主观指标年度分布"),
        read("rq1_tool_by_year.csv").assign(analysis="测量工具年度分布"),
        read("rq1_temporal_trend_tests.csv").assign(analysis="年度趋势检验"),
    ], ignore_index=True, sort=False)
    sheets["06_RQ1年代趋势"] = rows(temporal)
    context = pd.concat([
        read("rq1_domain_dimension_cells.csv").assign(analysis="设计领域×评价维度"),
        read("rq1_stage_dimension_cells.csv").assign(analysis="设计阶段×评价维度"),
    ], ignore_index=True, sort=False)
    tests = read("rq1_context_dimension_tests.csv").assign(analysis="总体独立性检验")
    context = pd.concat([context, tests], ignore_index=True, sort=False)
    sheets["07_RQ1领域阶段"] = rows(context)

    rq2 = pd.concat([
        read("rq2_chain_audit_summary.csv").assign(result_type="标准状态分布"),
        read("rq2_chain_quality_tiers.csv").assign(result_type="证据链质量层级"),
    ], ignore_index=True, sort=False)
    sheets["08_RQ2质量结果"] = rows(rq2)
    analysis_set_cols = ["paper_id", "eval_id", "chain_id", "title", "year", "dimension_code", "indicator_code", "revised_quality_tier", "revised_quality_index", "model_eligible_main", "model_eligible_sensitivity"]
    sheets["09_RQ3分析集"] = rows(chains[analysis_set_cols])

    rq3 = pd.concat([
        read("rq3_model_comparison.csv").assign(result_type="模型比较"),
        read("rq3_label_group_weights.csv").assign(result_type="标签组消融权重"),
        read("rq3_context_associations.csv").assign(result_type="情境与推荐目标关联"),
    ], ignore_index=True, sort=False)
    sheets["10_RQ3关联与权重"] = rows(rq3)
    sheets["11_推荐证据库"] = rows(read("rq3_specific_tool_evidence.csv"))

    code_rows = [["字段", "代码", "分类", "来源／状态"]]
    fixed = {"domain", "stage", "ai_function", "dimension", "indicator", "purpose"}
    for field, mapping in LABELS.items():
        if field in {"audit_status", "tool_family"}:
            continue
        for code, label in mapping.items():
            code_rows.append([FIELD_NAMES.get(field, field), code, label, "既定分类" if field in fixed else "研究操作化"])
    for code, label in TOOL_LABELS.items():
        code_rows.append(["测量工具类别", code, label, "本研究互斥操作化"])
    for code, label in AUDIT_LABELS.items():
        code_rows.append(["JCSEE对照标准", code, label, "由论文可观察报告信息操作化"])
    for code, label in STATUS_LABELS.items():
        code_rows.append(["规范性状态", code, label, "链级状态"])
    code_rows.append(["测量工具类别", "UNMAPPED", "现有证据不足以判定", "保留缺失，不强行归类"])
    sheets["12_代码本"] = code_rows
    sheets["13_方法与限制"] = [
        ["主题", "说明", "来源"],
        ["评价证据链", "Evaluation Question／效果主张→Construct／构念→Indicator／指标→Measure／测量工具。", SOURCE_URLS["CDC"]],
        ["工具实例", "490条父证据链拆出600个测量工具实例。工具实例是M1–M5互斥分类的统计单位。", "研究操作化"],
        ["M1", "标准化具名量表：有正式名称、来源和相对固定题项或计分程序。", "研究操作化"],
        ["M2", "自编结构化评分工具：研究者自编Likert、语义差异、等级或专家评分。", "研究操作化"],
        ["M3", "定性言语引出工具：访谈、焦点小组、开放回答或思维口述并做质性分析。", "研究操作化"],
        ["M4", "非量表型结构化问卷：选择、排序、偏好或事实题，不形成标准化构念得分。", "研究操作化"],
        ["M5", "既有感知资料分析：分析研究实施前已存在的评论、论坛、社交文本或其他二手感知材料。", "研究操作化"],
        ["JCSEE审查", "对490条证据链逐项保留U5、A2、A3、A4、A6、A7、E1的状态、事实、理由和页码。未制造JCSEE官方总分。", SOURCE_URLS["JCSEE"]],
        ["层级规则", "Q1高置信、Q2可用、Q3描述／敏感性、EXCLUDE明确问题。主要规范集为Q1+Q2；扩展规范集允许A3未报告。", "预先声明的研究规则"],
        ["RQ1趋势", "同时报告年度数量与当年构成比；二项GLM估计每年优势比变化，BH校正多重比较。稀疏指标只作描述。", "研究分析方案"],
        ["RQ1领域／阶段", "多标签证据链展开后做卡方独立性检验、Cramér’s V与单元标准化残差。", "研究分析方案"],
        ["RQ3验证", "按论文分组交叉验证，比较频率基线、L2多项逻辑回归、随机森林、直方图梯度提升。", SOURCE_URLS["GroupedCV"]],
        ["标签权重", "对标签组逐组消融，以Macro-F1下降表示增量贡献并归一化。负下降截为0。该权重不作因果解释。", "研究分析方案"],
        ["推荐层级", "先推荐评价维度，再在已确定维度下推荐主观指标，最后在已确定维度与指标下推荐工具类别和具体工具。", "研究应用规则"],
        ["数据泄漏控制", "预测维度时不输入维度；预测指标时仅把维度作为已知上一级条件；预测工具时仅把维度和指标作为已知上级条件。", "研究分析方案"],
        ["人工复核边界", "12篇逐页人工复核，113篇为全文规则筛查、语义清点与原句回定位。正式投稿前仍需第二编码者独立复核并报告一致性。", "质量控制说明"],
        ["解释边界", "关联和模型表现说明现有文献中的共同出现与可预测性，不能解释因果，也不能证明推荐对新任务的外部有效性。", "研究限制"],
    ]
    (ROOT / "workbook_data_revised.json").write_text(json.dumps(sheets, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
