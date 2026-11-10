import json
import math
from pathlib import Path

import pandas as pd

from config import ROOT, LABELS, FIELD_NAMES, STANDARDS, SOURCE_URLS


DATA = ROOT / "final_results"


def safe(v):
    if pd.isna(v) if not isinstance(v, (list, dict)) else False:
        return None
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and not math.isfinite(v):
        return "∞" if v > 0 else ("-∞" if v < 0 else None)
    return v


def df_rows(df):
    return [list(map(str, df.columns))] + [[safe(v) for v in row] for row in df.itertuples(index=False, name=None)]


def main():
    summary = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    sheets = {}
    sheets["研究概览"] = [
        ["项目", "结果", "口径／说明"],
        ["全文论文", summary["papers"], "用户提供的125篇PDF；旧表仅保留固定分类"],
        ["含人类主观评价的论文", summary["papers_with_human_subjective_evaluation"], "全文确认实际收集人的主观感知、判断、态度或体验"],
        ["评价案例", summary["evaluations"], "独立样本或独立研究为一个案例"],
        ["评价证据链", summary["chains"], "效果主张→构念→指标→测量工具"],
        ["严格高规范案例", summary["strict_evaluations"], "A2/A3/A6/A7充分；U5/A4/E1至少部分；无明确问题"],
        ["关联分析案例", summary["association_eligible_evaluations"], "A3未报告可保留；其他关键环节至少部分；无明确问题"],
        ["关联分析证据链", summary["association_analysis_chains"], "用于RQ3的实际分析单位"],
        ["逐页人工复核论文", summary["manual_reviewed_papers"], "覆盖三个编号区间的校准样本"],
        ["规则筛查＋语义清点论文", summary["hybrid_reviewed_papers"], "证据链只保留可回定位PDF原句；正式投稿前建议双人复核"],
    ]
    sheets["RQ1分布"] = df_rows(pd.read_csv(DATA / "rq1_distributions.csv"))
    sheets["RQ2规范性"] = df_rows(pd.read_csv(DATA / "rq2_audit_status.csv"))
    sheets["RQ2案例层级"] = df_rows(pd.read_csv(DATA / "rq2_quality_tiers.csv"))
    sheets["RQ3关联"] = df_rows(pd.read_csv(DATA / "rq3_associations.csv"))
    sheets["模型比较"] = df_rows(pd.read_csv(DATA / "rq3_model_comparison.csv"))
    sheets["推荐证据"] = df_rows(pd.read_csv(DATA / "recommendations.csv"))
    sheets["论文125"] = df_rows(pd.read_csv(DATA / "papers.csv"))
    sheets["评价案例"] = df_rows(pd.read_csv(DATA / "evaluations.csv"))
    sheets["证据链"] = df_rows(pd.read_csv(DATA / "chains.csv"))
    sheets["JCSEE审查"] = df_rows(pd.read_csv(DATA / "audits.csv"))
    code_rows = [["字段", "代码", "分类", "固定／研究操作化"]]
    fixed = {"domain", "stage", "ai_function", "dimension", "indicator", "purpose"}
    for field, mapping in LABELS.items():
        if field == "audit_status":
            continue
        for code, label in mapping.items():
            code_rows.append([FIELD_NAMES.get(field, field), code, label, "用户要求保留的固定分类" if field in fixed else "依据研究问题操作化"])
    for code, label in STANDARDS.items():
        code_rows.append(["JCSEE对照标准", code, label, "由论文可观察信息操作化"])
    sheets["代码本"] = code_rows
    sheets["方法与限制"] = [
        ["主题", "说明", "来源"],
        ["评价证据链", "Evaluation Question／效果主张→Construct／构念→Indicator／指标→Measure／测量工具", SOURCE_URLS["CDC"]],
        ["规范性审查", "保留U5、A2、A3、A4、A6、A7、E1逐项状态、事实、理由、页码和短引文；不制造JCSEE官方总分", SOURCE_URLS["JCSEE"]],
        ["关联检验", "Fisher精确检验＋条件概率＋lift＋有向Cramér’s V；同族BH多重比较校正", "研究操作化"],
        ["预测验证", "按论文分组交叉验证；比较频率基线、逻辑回归、随机森林、极端随机树、直方图梯度提升", SOURCE_URLS["GroupedCV"]],
        ["不采用SEM作为主模型", "数据是论文内嵌套的多标签类别选择，缺少潜变量测量模型及连续观测结构", "模型适用性判断"],
        ["自动抽取边界", "12篇逐页人工复核；其他论文采用全文规则筛查、语义清点与PDF原句回定位。正式投稿前需要双人独立复核与一致性检验", "质量控制说明"],
        ["多标签分母", "论文层和证据链层分别统计；同一记录可进入多个类别，百分比之和可超过100%", "统计口径"],
        ["UNMAPPED", "固定二级分类无法可靠容纳时标记，不为方便建模临时新建类别", "代码本规则"],
    ]
    (ROOT / "workbook_data_final.json").write_text(json.dumps(sheets, ensure_ascii=False), encoding="utf-8")
    print(ROOT / "workbook_data_final.json")


if __name__ == "__main__":
    main()
