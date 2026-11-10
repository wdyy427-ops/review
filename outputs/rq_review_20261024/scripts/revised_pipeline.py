from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, norm
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss, top_k_accuracy_score
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold

from config import ROOT, LABELS, INDICATORS


SRC = ROOT / "final_results"
OUT = ROOT / "revised_results"
OUT.mkdir(exist_ok=True)

TOOL_LABELS = {
    "M1": "标准化具名量表",
    "M2": "自编结构化评分工具",
    "M3": "定性言语引出工具",
    "M4": "非量表型结构化问卷",
    "M5": "既有感知资料分析",
}

AUDIT_LABELS = {
    "U5": "信息与评价目的相关",
    "A2": "测量解释的效度依据",
    "A3": "信息的可靠性／可信性依据",
    "A4": "对象、样本、任务与情境描述",
    "A6": "研究设计与分析适切性",
    "A7": "评价推理可追溯性",
    "E1": "评价记录充分性",
}

STATUS_LABELS = {"S": "充分支持", "P": "部分支持", "NR": "未报告／无法判断", "C": "明确问题", "NA": "不适用"}

NAMED_SCALES = [
    (r"\bNASA[- ]?TLX\b|NASA Task Load Index", "NASA-TLX"),
    (r"\bSystem Usability Scale\b|\bSUS\b", "System Usability Scale (SUS)"),
    (r"\bCreativity Support Index\b|\bCSI\b", "Creativity Support Index (CSI)"),
    (r"\bUser Experience Questionnaire\b|\bUEQ(?:-S)?\b", "User Experience Questionnaire (UEQ)"),
    (r"\bAttrakDiff\b", "AttrakDiff"),
    (r"\bPANAS\b|Positive and Negative Affect Schedule", "PANAS"),
    (r"\bSAM\b|Self[- ]Assessment Manikin", "Self-Assessment Manikin (SAM)"),
    (r"\bPSSUQ\b|Post[- ]Study System Usability Questionnaire", "PSSUQ"),
    (r"\bASQ\b|After[- ]Scenario Questionnaire", "After-Scenario Questionnaire (ASQ)"),
    (r"\bTechnology Acceptance Model\b|\bTAM\b", "Technology Acceptance Model questionnaire (TAM)"),
    (r"\bGodspeed\b", "Godspeed Questionnaire"),
    (r"\bTrust in Automation\b|Jian.*trust", "Trust in Automation Scale"),
    (r"\bRaw NASA[- ]?TLX\b|\bRTLX\b", "Raw NASA-TLX"),
    (r"\bNet Promoter Score\b|\bNPS\b", "Net Promoter Score (NPS)"),
    (r"\bFlow State Scale\b", "Flow State Scale"),
    (r"\bIntrinsic Motivation Inventory\b|\bIMI\b", "Intrinsic Motivation Inventory (IMI)"),
]


def split_codes(value):
    return [x for x in str(value or "").split(";") if x and x not in {"NR", "NA", "UNMAPPED", "nan"}]


def present(value):
    s = str(value or "").strip()
    return bool(s and s.lower() != "nan" and s not in {"NR", "NA", "UNMAPPED", "未报告"})


def compact(value, n=180):
    s = re.sub(r"\s+", " ", str(value or "")).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def bh_adjust(values):
    p = np.asarray(values, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.minimum.accumulate((ranked * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    out = np.empty_like(adjusted)
    out[order] = np.minimum(1, adjusted)
    return out


def positive_evidence(text, patterns):
    s = str(text or "")
    if not present(s):
        return False
    for pat in patterns:
        for m in re.finditer(pat, s, re.I):
            window = s[max(0, m.start() - 28) : m.end() + 20]
            if not re.search(r"未报告|没有报告|not report|no evidence|without", window, re.I):
                return True
    return False


def extract_named_scales(text):
    found = []
    for pat, name in NAMED_SCALES:
        if re.search(pat, text, re.I):
            found.append(name)
    return list(dict.fromkeys(found))


def recode_tool_instances(chains):
    rows = []
    for _, r in chains.iterrows():
        text = " | ".join(
            str(r.get(c, "") or "")
            for c in ["instrument_raw", "item_quote", "response_scoring", "validity_evidence", "reliability_evidence"]
        )
        old = set(split_codes(r.get("tool_families")))
        sources = set(split_codes(r.get("sources")))
        instances = []

        secondary = bool(re.search(r"existing (?:reviews?|comments?|posts?|dataset)|social media|online reviews?|archival|secondary data|论坛|社交媒体|既有评论|用户评论", text, re.I)) or "H4" in sources
        qualitative = bool(re.search(r"semi[- ]?structured interview|in[- ]depth interview|focus group|open[- ]?ended|thematic analysis|qualitative coding|think[- ]?aloud|访谈|焦点小组|开放式|主题分析|思维口述", text, re.I))
        numeric = bool(re.search(r"likert|semantic differential|visual analog|\bVAS\b|\d+[- ]?point|rating scale|rated on|expert score|专家.*评分|[五七十]\s*点|数值评分|等级评分", text, re.I))
        choice = bool(re.search(r"pairwise|ranking|rank order|forced choice|preference choice|multiple choice|select(?:ed)? the|排序|成对比较|偏好选择|单选|多选", text, re.I))
        questionnaire = bool(re.search(r"questionnaire|survey|问卷|调查", text, re.I)) or "H1" in sources
        names = extract_named_scales(text)

        if secondary:
            instances.append(("M5", "既有评论／社交文本／二手感知资料"))
        if qualitative and not secondary:
            qname = "定性言语引出方案"
            if re.search(r"focus group|焦点小组", text, re.I):
                qname = "焦点小组"
            elif re.search(r"think[- ]?aloud|思维口述", text, re.I):
                qname = "思维口述"
            elif re.search(r"interview|访谈", text, re.I):
                qname = "访谈"
            elif re.search(r"open[- ]?ended|开放式", text, re.I):
                qname = "开放式回答"
            instances.append(("M3", qname))
        for name in names:
            instances.append(("M1", name))
        if numeric and not names:
            if re.search(r"semantic differential|语义差异", text, re.I):
                m2_name = "自编语义差异量表"
            elif re.search(r"expert score|expert rating|专家.*评分", text, re.I):
                m2_name = "自编专家结构化评分"
            elif re.search(r"likert|[五七十]\s*点", text, re.I):
                m2_name = "自编Likert评分"
            else:
                m2_name = "自编数值／等级评分"
            instances.append(("M2", m2_name))
        if (choice or questionnaire) and not numeric and not names and not qualitative and not secondary:
            if re.search(r"pairwise|ranking|rank order|preference choice|排序|成对比较|偏好选择", text, re.I):
                m4_name = "结构化偏好／排序问卷"
            else:
                m4_name = "非量表型结构化问卷"
            instances.append(("M4", m4_name))

        if not instances:
            if "M2" in old:
                instances.append(("M1", "具名量表（名称待人工核验）"))
            elif "M1" in old or "M6" in old:
                instances.append(("M2", "自编结构化评分"))
            elif old.intersection({"M4", "M5"}) or "H3" in sources:
                instances.append(("M3", "定性言语引出方案"))
            elif "M3" in old:
                instances.append(("M4", "非量表型结构化问卷"))
            elif "M7" in old or "H4" in sources:
                instances.append(("M5", "既有评论／社交文本／二手感知资料"))

        if not instances:
            instances.append(("UNMAPPED", compact(r.get("instrument_raw") or "未能判定工具", 110)))

        unique = []
        seen = set()
        for code, name in instances:
            key = (code, re.sub(r"\W+", "", name).lower()[:100])
            if key not in seen:
                seen.add(key)
                unique.append((code, name))
        for i, (code, name) in enumerate(unique, 1):
            rows.append(
                {
                    "paper_id": int(r.paper_id),
                    "eval_id": r.eval_id,
                    "chain_id": r.chain_id,
                    "measure_instance_id": f"{r.chain_id}-M{i}",
                    "year": int(r.year) if pd.notna(r.year) else np.nan,
                    "dimension_code": r.dimension_code,
                    "indicator_code": r.indicator_code,
                    "tool_code": code,
                    "tool_label": TOOL_LABELS.get(code, "未映射"),
                    "instrument_name": name,
                    "instrument_raw": r.get("instrument_raw", ""),
                    "response_scoring": r.get("response_scoring", ""),
                    "pages": r.get("pages", ""),
                }
            )
    return pd.DataFrame(rows)


def chain_audit(chains, evals, instances):
    eval_lookup = evals.set_index("eval_id").to_dict("index")
    tool_lookup = instances.groupby("chain_id")["tool_code"].apply(list).to_dict()
    audit_rows = []
    chain_rows = []

    for _, r in chains.iterrows():
        ev = eval_lookup.get(r.eval_id, {})
        tools = [x for x in tool_lookup.get(r.chain_id, []) if x in TOOL_LABELS]
        mapped_dim = r.dimension_code in LABELS["dimension"]
        mapped_ind = r.indicator_code in LABELS["indicator"]
        claim = present(r.claim_quote) or present(r.claim_summary)
        construct = present(r.construct_raw)
        result = present(r.result_quote)
        item = present(r.item_quote)
        instrument = present(r.instrument_raw) and bool(tools)
        scoring = present(r.response_scoring)
        pages = present(r.pages)
        analysis_text = " | ".join(str(ev.get(c, "") or "") for c in ["analysis", "procedure", "comparator", "actual_results"])
        comparator = present(ev.get("comparator")) and str(ev.get("comparator")) not in {"无", "none", "NR"}
        analysis = positive_evidence(analysis_text, [r"anova", r"t[- ]?test", r"regression", r"mixed[- ]?effects?", r"wilcoxon", r"mann[- ]?whitney", r"chi[- ]?square", r"thematic analysis", r"content analysis", r"confidence interval", r"\bp\s*[<=>]"])
        causal_or_comparative = r.claim_type in {"C2", "C3"}
        overreach = r.claim_type == "C3" and not comparator and not analysis

        u5 = "S" if claim and construct and mapped_ind and instrument else ("P" if claim and mapped_dim and instrument else "NR")

        valid_positive = positive_evidence(
            r.validity_evidence,
            [r"content validity", r"construct validity", r"factor analysis", r"validated", r"pilot", r"pretest", r"expert review", r"理论依据", r"效度", r"预测试"],
        )
        if valid_positive and mapped_ind and instrument:
            a2 = "S"
        elif mapped_dim and instrument and (item or any(t == "M1" for t in tools)):
            a2 = "P"
        else:
            a2 = "NR"

        reliable_positive = positive_evidence(
            r.reliability_evidence,
            [r"cronbach", r"\bICC\b", r"kappa", r"kendall", r"inter[- ]?rater", r"test[- ]?retest", r"reliab", r"double cod", r"two coders", r"saturation", r"triangulat", r"member check", r"信度", r"一致性", r"饱和", r"三角"],
        )
        if reliable_positive:
            a3 = "S"
        elif tools and all(t == "M4" for t in tools) and not scoring:
            a3 = "NA"
        elif any(t == "M1" for t in tools) and present(r.validity_evidence):
            a3 = "P"
        else:
            a3 = "NR"

        inherited_a4 = str(ev.get("A4", "NR"))
        a4 = inherited_a4 if inherited_a4 in STATUS_LABELS else "NR"

        if overreach:
            a6 = "C"
        elif result and (analysis or comparator):
            a6 = "S"
        elif result:
            a6 = "P"
        else:
            a6 = "NR"

        if overreach:
            a7 = "C"
        elif claim and result and (not causal_or_comparative or analysis or comparator):
            a7 = "S"
        elif claim and result:
            a7 = "P"
        else:
            a7 = "NR"

        complete = sum([pages, instrument, scoring, item, result])
        e1 = "S" if complete >= 5 else ("P" if complete >= 3 and pages and instrument else "NR")

        statuses = {"U5": u5, "A2": a2, "A3": a3, "A4": a4, "A6": a6, "A7": a7, "E1": e1}
        core_no_c = not any(v == "C" for v in statuses.values())
        q1 = core_no_c and all(statuses[x] == "S" for x in ["U5", "A2", "A6", "A7"]) and statuses["A3"] in {"S", "NA"} and statuses["A4"] in {"S", "P"} and statuses["E1"] in {"S", "P"}
        q2 = core_no_c and all(statuses[x] in {"S", "P"} for x in ["U5", "A2", "A4", "A6", "A7", "E1"]) and statuses["A3"] in {"S", "P", "NA"}
        sensitivity = core_no_c and all(statuses[x] in {"S", "P"} for x in ["U5", "A2", "A4", "A6", "A7", "E1"]) and statuses["A3"] in {"S", "P", "NA", "NR"}
        if q1:
            tier = "Q1"
        elif q2:
            tier = "Q2"
        elif sensitivity:
            tier = "Q3"
        elif any(v == "C" for v in statuses.values()):
            tier = "EXCLUDE"
        else:
            tier = "Q3"
        score_map = {"S": 1.0, "P": 0.5, "NR": 0.0, "C": -1.0, "NA": np.nan}
        vals = [score_map[v] for v in statuses.values() if not pd.isna(score_map[v])]
        quality = float(np.mean(vals)) if vals else 0.0

        evidence = {
            "U5": compact(f"主张={r.claim_summary or r.claim_quote}; 构念={r.construct_raw}; 指标={r.indicator_raw}; 工具={r.instrument_raw}"),
            "A2": compact(f"{r.validity_evidence}; 题项={r.item_quote}"),
            "A3": compact(r.reliability_evidence),
            "A4": compact(f"样本={ev.get('sample_description','')}; 任务={ev.get('task','')}; 情境={ev.get('setting','')}"),
            "A6": compact(f"设计={ev.get('design','')}; 比较={ev.get('comparator','')}; 分析={ev.get('analysis','')}"),
            "A7": compact(f"结果={r.result_quote}; 主张={r.claim_summary or r.claim_quote}"),
            "E1": compact(f"工具={r.instrument_raw}; 计分={r.response_scoring}; 页码={r.pages}"),
        }
        for standard, status in statuses.items():
            audit_rows.append(
                {
                    "paper_id": int(r.paper_id),
                    "eval_id": r.eval_id,
                    "chain_id": r.chain_id,
                    "standard": standard,
                    "standard_label": AUDIT_LABELS[standard],
                    "status": status,
                    "status_label": STATUS_LABELS[status],
                    "evidence": evidence[standard],
                    "pages": r.pages,
                }
            )
        row = r.to_dict()
        row.update({f"audit_{k}": v for k, v in statuses.items()})
        row.update(
            {
                "revised_quality_tier": tier,
                "revised_quality_index": quality,
                "model_eligible_main": int(q1 or q2),
                "model_eligible_sensitivity": int(sensitivity),
                "revised_tool_classes": ";".join(dict.fromkeys(tools)) if tools else "UNMAPPED",
            }
        )
        chain_rows.append(row)
    return pd.DataFrame(chain_rows), pd.DataFrame(audit_rows)


def yearly_distribution(df, code_col, labels, unit_name):
    data = df[pd.notna(df.year)].copy()
    data["year"] = data.year.astype(int)
    data = data[data[code_col].isin(labels)]
    years = sorted(data.year.unique())
    rows = []
    totals = data.groupby("year").size().to_dict()
    for year in years:
        counts = data.loc[data.year == year, code_col].value_counts()
        for code, label in labels.items():
            n = int(counts.get(code, 0))
            rows.append({"unit": unit_name, "year": year, "code": code, "label": label, "n": n, "denominator": totals[year], "percent": n / totals[year] if totals[year] else 0})
    return pd.DataFrame(rows)


def trend_tests(yearly):
    rows = []
    try:
        import statsmodels.api as sm
    except Exception:
        sm = None
    for code, sub in yearly.groupby("code"):
        sub = sub.sort_values("year")
        if len(sub) < 3 or sub.n.sum() < 3:
            rows.append({"code": code, "label": sub.label.iloc[0], "slope_log_odds": np.nan, "se": np.nan, "p_value": np.nan, "status": "样本不足"})
            continue
        if sm is None:
            rows.append({"code": code, "label": sub.label.iloc[0], "slope_log_odds": np.nan, "se": np.nan, "p_value": np.nan, "status": "statsmodels不可用"})
            continue
        x = sm.add_constant(sub.year - sub.year.mean())
        prop = np.clip(sub.percent.astype(float), 1e-6, 1 - 1e-6)
        try:
            model = sm.GLM(prop, x, family=sm.families.Binomial(), freq_weights=sub.denominator).fit(cov_type="HC0")
            rows.append({"code": code, "label": sub.label.iloc[0], "slope_log_odds": float(model.params.iloc[1]), "se": float(model.bse.iloc[1]), "p_value": float(model.pvalues.iloc[1]), "status": "完成"})
        except Exception as exc:
            rows.append({"code": code, "label": sub.label.iloc[0], "slope_log_odds": np.nan, "se": np.nan, "p_value": np.nan, "status": f"失败:{type(exc).__name__}"})
    out = pd.DataFrame(rows)
    mask = out.p_value.notna()
    out.loc[mask, "q_value_bh"] = bh_adjust(out.loc[mask, "p_value"].values)
    out["odds_ratio_per_year"] = np.exp(out.slope_log_odds)
    return out


def context_dimension_table(chains, field, labels):
    rows = []
    for _, r in chains[chains.dimension_code.isin(LABELS["dimension"])].iterrows():
        for code in split_codes(r.get(field)):
            if code in labels:
                rows.append({"chain_id": r.chain_id, "eval_id": r.eval_id, "context_code": code, "dimension_code": r.dimension_code})
    long = pd.DataFrame(rows)
    table = pd.crosstab(long.context_code, long.dimension_code).reindex(index=list(labels), columns=list(LABELS["dimension"]), fill_value=0)
    chi2, p, dof, expected = chi2_contingency(table.values)
    n = table.values.sum()
    v = math.sqrt(chi2 / (n * min(table.shape[0] - 1, table.shape[1] - 1))) if n else np.nan
    residual = (table.values - expected) / np.sqrt(expected)
    cell_p = 2 * norm.sf(np.abs(residual))
    cell_q = bh_adjust(cell_p.ravel()).reshape(cell_p.shape)
    detail = []
    for i, rc in enumerate(table.index):
        for j, dc in enumerate(table.columns):
            detail.append(
                {
                    "context_field": field,
                    "context_code": rc,
                    "context_label": labels[rc],
                    "dimension_code": dc,
                    "dimension_label": LABELS["dimension"][dc],
                    "n": int(table.loc[rc, dc]),
                    "row_percent": table.loc[rc, dc] / table.loc[rc].sum() if table.loc[rc].sum() else 0,
                    "expected": expected[i, j],
                    "standardized_residual": residual[i, j],
                    "cell_p": cell_p[i, j],
                    "cell_q_bh": cell_q[i, j],
                }
            )
    stats = {"field": field, "n": int(n), "chi_square": float(chi2), "df": int(dof), "p_value": float(p), "cramers_v": float(v)}
    return long, table, pd.DataFrame(detail), stats


FEATURE_GROUPS = {
    "G1_评价目的": ["purposes"],
    "G2_效果主张形式": ["claim_type"],
    "G3_评价对象": ["objects"],
    "G4_设计情境": ["domains", "stages"],
    "G5_相关人的价值": ["evaluators", "target_users"],
    "G6_可信证据可行条件": ["sources", "constraints", "setting"],
    "G7_AI活动特征": ["ai_functions", "ai_roles", "tasks"],
}


def encode_features(df, fixed_cols=None):
    fixed_cols = fixed_cols or []
    pieces, groups = [], {}
    for group, cols in FEATURE_GROUPS.items():
        gp = []
        for col in cols:
            if col not in df:
                continue
            values = sorted({v for x in df[col].fillna("") for v in split_codes(x)})
            if col in {"claim_type", "setting"}:
                values = sorted({str(x) for x in df[col].fillna("") if present(x)})
            for value in values:
                name = f"{col}={value}"
                if col in {"claim_type", "setting"}:
                    series = (df[col].astype(str) == value).astype(int)
                else:
                    series = df[col].fillna("").map(lambda x: int(value in split_codes(x)))
                pieces.append(series.rename(name)); gp.append(name)
        groups[group] = gp
    fixed_names = []
    for col in fixed_cols:
        if col not in df:
            continue
        for value in sorted({str(x) for x in df[col].fillna("") if present(x)}):
            name = f"FIXED:{col}={value}"
            pieces.append((df[col].astype(str) == value).astype(int).rename(name)); fixed_names.append(name)
    x = pd.concat(pieces, axis=1).astype(float) if pieces else pd.DataFrame(index=df.index)
    groups["FIXED"] = fixed_names
    return x, groups


def make_splits(y, paper_ids):
    class_papers = pd.DataFrame({"y": y, "paper": paper_ids}).drop_duplicates().groupby("y").paper.nunique()
    n_splits = int(min(5, class_papers.min(), pd.Series(paper_ids).nunique()))
    if n_splits < 3:
        return []
    try:
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=20261025)
        return list(cv.split(np.zeros(len(y)), y, paper_ids))
    except Exception:
        cv = GroupKFold(n_splits=n_splits)
        return list(cv.split(np.zeros(len(y)), y, paper_ids))


def candidate_models():
    return {
        "L2多项逻辑回归": LogisticRegression(max_iter=3000, class_weight="balanced", solver="lbfgs"),
        "随机森林": RandomForestClassifier(n_estimators=400, min_samples_leaf=2, class_weight="balanced_subsample", random_state=20261025, n_jobs=-1),
        "直方图梯度提升": HistGradientBoostingClassifier(max_iter=180, learning_rate=0.05, max_leaf_nodes=15, random_state=20261025),
    }


def evaluate_model(model, x, y, splits):
    rows = []
    for fold, (tr, te) in enumerate(splits, 1):
        m = clone(model)
        m.fit(x.iloc[tr], y.iloc[tr])
        pred = m.predict(x.iloc[te])
        prob = m.predict_proba(x.iloc[te]) if hasattr(m, "predict_proba") else None
        row = {
            "fold": fold,
            "macro_f1": f1_score(y.iloc[te], pred, average="macro", zero_division=0),
            "weighted_f1": f1_score(y.iloc[te], pred, average="weighted", zero_division=0),
            "balanced_accuracy": balanced_accuracy_score(y.iloc[te], pred),
            "accuracy": accuracy_score(y.iloc[te], pred),
        }
        if prob is not None:
            try:
                row["log_loss"] = log_loss(y.iloc[te], prob, labels=m.classes_)
                row["top2_accuracy"] = top_k_accuracy_score(y.iloc[te], prob, k=min(2, len(m.classes_)), labels=m.classes_)
            except Exception:
                row["log_loss"] = np.nan; row["top2_accuracy"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def model_and_weights(df, target_col, target_name, fixed_cols=None):
    data = df.copy()
    data = data[data[target_col].notna() & ~data[target_col].isin(["", "NR", "NA", "UNMAPPED"])].copy()
    counts = data[target_col].value_counts()
    paper_counts = data[[target_col, "paper_id"]].drop_duplicates()[target_col].value_counts()
    keep = [c for c in counts.index if counts[c] >= 5 and paper_counts.get(c, 0) >= 3]
    data = data[data[target_col].isin(keep)].reset_index(drop=True)
    if len(data) < 30 or data[target_col].nunique() < 2:
        return pd.DataFrame(), pd.DataFrame(), {"target": target_name, "n": len(data), "classes": len(keep), "status": "样本不足"}
    x, groups = encode_features(data, fixed_cols)
    y = data[target_col].astype(str)
    splits = make_splits(y, data.paper_id)
    if not splits:
        return pd.DataFrame(), pd.DataFrame(), {"target": target_name, "n": len(data), "classes": len(keep), "status": "分组不足"}

    comparisons, fold_cache = [], {}
    # Frequency baseline learned independently inside each fold.
    base_rows = []
    for fold, (tr, te) in enumerate(splits, 1):
        mode = y.iloc[tr].value_counts().idxmax()
        pred = np.repeat(mode, len(te))
        base_rows.append({"fold": fold, "macro_f1": f1_score(y.iloc[te], pred, average="macro", zero_division=0), "weighted_f1": f1_score(y.iloc[te], pred, average="weighted", zero_division=0), "balanced_accuracy": balanced_accuracy_score(y.iloc[te], pred), "accuracy": accuracy_score(y.iloc[te], pred), "log_loss": np.nan, "top2_accuracy": np.nan})
    bdf = pd.DataFrame(base_rows)
    comparisons.append({"target": target_name, "model": "频率基线", "n": len(data), "papers": data.paper_id.nunique(), "classes": y.nunique(), "folds": len(splits), **{f"{c}_mean": bdf[c].mean() for c in ["macro_f1", "weighted_f1", "balanced_accuracy", "accuracy", "log_loss", "top2_accuracy"]}, "macro_f1_sd": bdf.macro_f1.std(ddof=1)})

    for name, model in candidate_models().items():
        fdf = evaluate_model(model, x, y, splits)
        fold_cache[name] = (model, fdf)
        comparisons.append({"target": target_name, "model": name, "n": len(data), "papers": data.paper_id.nunique(), "classes": y.nunique(), "folds": len(splits), **{f"{c}_mean": fdf[c].mean() for c in ["macro_f1", "weighted_f1", "balanced_accuracy", "accuracy", "log_loss", "top2_accuracy"]}, "macro_f1_sd": fdf.macro_f1.std(ddof=1)})
    comp = pd.DataFrame(comparisons)
    best_name = comp[comp.model != "频率基线"].sort_values("macro_f1_mean", ascending=False).iloc[0].model
    best_model, full_folds = fold_cache[best_name]

    importance_rows = []
    for group, cols in groups.items():
        if group == "FIXED" or not cols:
            continue
        keep_cols = [c for c in x.columns if c not in cols]
        if not keep_cols:
            continue
        reduced = evaluate_model(best_model, x[keep_cols], y, splits)
        drops = full_folds.macro_f1.values - reduced.macro_f1.values
        rng = np.random.default_rng(20261025)
        boot = np.array([rng.choice(drops, size=len(drops), replace=True).mean() for _ in range(2000)])
        importance_rows.append({"target": target_name, "selected_model": best_name, "feature_group": group, "full_macro_f1": full_folds.macro_f1.mean(), "ablated_macro_f1": reduced.macro_f1.mean(), "delta_macro_f1": drops.mean(), "ci_low": np.quantile(boot, 0.025), "ci_high": np.quantile(boot, 0.975), "n": len(data), "papers": data.paper_id.nunique()})
    imp = pd.DataFrame(importance_rows)
    if len(imp):
        positive = imp.delta_macro_f1.clip(lower=0)
        if positive.sum() > 0:
            imp["normalized_weight"] = positive / positive.sum()
        else:
            imp["normalized_weight"] = 0.0
        imp = imp.sort_values("normalized_weight", ascending=False)
    meta = {"target": target_name, "n": len(data), "papers": int(data.paper_id.nunique()), "classes": int(y.nunique()), "best_model": best_name, "status": "完成"}
    return comp, imp, meta


def binary_associations(chains, instances, eligible_col="model_eligible_main", analysis_tier="main"):
    rows = []
    base = chains[chains[eligible_col] == 1].copy()
    if not len(base):
        return pd.DataFrame()
    outcomes = [("dimension", code, label) for code, label in LABELS["dimension"].items()]
    inst_map = instances.merge(base[["chain_id"]], on="chain_id", how="inner")
    for code, label in TOOL_LABELS.items():
        outcomes.append(("tool", code, label))
    context_fields = {
        "purpose": ("purposes", LABELS["purpose"]), "object": ("objects", LABELS["object"]),
        "domain": ("domains", LABELS["domain"]), "stage": ("stages", LABELS["stage"]),
        "evaluator": ("evaluators", LABELS["evaluator"]), "target_user": ("target_users", LABELS["target_user"]),
        "source": ("sources", LABELS["source"]), "ai_function": ("ai_functions", LABELS["ai_function"]),
        "ai_role": ("ai_roles", LABELS["ai_role"]), "task": ("tasks", LABELS["task"]),
    }
    for field_name, (col, labels) in context_fields.items():
        for ccode, clabel in labels.items():
            x = base[col].fillna("").map(lambda z: ccode in split_codes(z))
            if x.sum() < 3 or (~x).sum() < 3:
                continue
            for ofield, ocode, olabel in outcomes:
                if ofield == "dimension":
                    y = base.dimension_code == ocode
                else:
                    valid_ids = set(inst_map.loc[inst_map.tool_code == ocode, "chain_id"])
                    y = base.chain_id.isin(valid_ids)
                if y.sum() < 3 or (~y).sum() < 3:
                    continue
                a = int((x & y).sum()); b = int((x & ~y).sum()); c = int((~x & y).sum()); d = int((~x & ~y).sum())
                odds, p = fisher_exact([[a, b], [c, d]])
                n = a + b + c + d
                phi = (a * d - b * c) / math.sqrt((a + b) * (c + d) * (a + c) * (b + d)) if min((a + b), (c + d), (a + c), (b + d)) > 0 else 0
                cond = a / (a + b) if a + b else 0; baseline = (a + c) / n if n else 0
                rows.append({"context_field": field_name, "context_code": ccode, "context_label": clabel, "target_field": ofield, "target_code": ocode, "target_label": olabel, "a_both": a, "context_n": a + b, "target_n": a + c, "n": n, "conditional_probability": cond, "baseline_probability": baseline, "lift": cond / baseline if baseline else np.nan, "odds_ratio": odds, "cramers_v_signed": phi, "p_value": p})
    out = pd.DataFrame(rows)
    if len(out):
        out["q_value_bh"] = bh_adjust(out.p_value.values)
        out["evidence_grade"] = np.select([(out.q_value_bh <= .05) & (out.a_both >= 5), (out.q_value_bh <= .10) & (out.a_both >= 3)], ["较强", "探索性"], default="有限")
        out["analysis_tier"] = analysis_tier
        out = out.sort_values(["q_value_bh", "cramers_v_signed"], ascending=[True, False])
    return out


def main():
    chains = pd.read_csv(SRC / "chains.csv")
    evals = pd.read_csv(SRC / "evaluations.csv")
    papers = pd.read_csv(SRC / "papers.csv")
    instances = recode_tool_instances(chains)
    revised, audits = chain_audit(chains, evals, instances)
    instances = instances.merge(revised[["chain_id", "revised_quality_tier", "revised_quality_index", "model_eligible_main", "model_eligible_sensitivity"]], on="chain_id", how="left")

    revised.to_csv(OUT / "evidence_chains_revised.csv", index=False, encoding="utf-8-sig")
    instances.to_csv(OUT / "measure_instances.csv", index=False, encoding="utf-8-sig")
    audits.to_csv(OUT / "jcsee_chain_audit.csv", index=False, encoding="utf-8-sig")
    evals.to_csv(OUT / "evaluation_cases.csv", index=False, encoding="utf-8-sig")
    papers.to_csv(OUT / "papers.csv", index=False, encoding="utf-8-sig")

    # RQ1 annual trends.
    dim_year = yearly_distribution(revised, "dimension_code", LABELS["dimension"], "evidence_chain")
    ind_year = yearly_distribution(revised, "indicator_code", LABELS["indicator"], "evidence_chain")
    tool_year = yearly_distribution(instances, "tool_code", TOOL_LABELS, "measure_instance")
    dim_year.to_csv(OUT / "rq1_dimension_by_year.csv", index=False, encoding="utf-8-sig")
    ind_year.to_csv(OUT / "rq1_indicator_by_year.csv", index=False, encoding="utf-8-sig")
    tool_year.to_csv(OUT / "rq1_tool_by_year.csv", index=False, encoding="utf-8-sig")
    trend = pd.concat([trend_tests(dim_year).assign(level="dimension"), trend_tests(ind_year).assign(level="indicator"), trend_tests(tool_year).assign(level="tool")], ignore_index=True)
    trend.to_csv(OUT / "rq1_temporal_trend_tests.csv", index=False, encoding="utf-8-sig")

    # RQ1 context distributions.
    context_stats = []
    for field, labels, stem in [("domains", LABELS["domain"], "domain"), ("stages", LABELS["stage"], "stage")]:
        long, table, detail, stats = context_dimension_table(revised, field, labels)
        long.to_csv(OUT / f"rq1_{stem}_dimension_long.csv", index=False, encoding="utf-8-sig")
        table.to_csv(OUT / f"rq1_{stem}_dimension_table.csv", encoding="utf-8-sig")
        detail.to_csv(OUT / f"rq1_{stem}_dimension_cells.csv", index=False, encoding="utf-8-sig")
        context_stats.append(stats)
    pd.DataFrame(context_stats).to_csv(OUT / "rq1_context_dimension_tests.csv", index=False, encoding="utf-8-sig")

    # RQ2 summaries.
    audit_summary = audits.groupby(["standard", "standard_label", "status", "status_label"]).size().rename("n").reset_index()
    audit_summary["denominator"] = revised.chain_id.nunique(); audit_summary["percent"] = audit_summary.n / audit_summary.denominator
    audit_summary.to_csv(OUT / "rq2_chain_audit_summary.csv", index=False, encoding="utf-8-sig")
    tiers = revised.revised_quality_tier.value_counts().rename_axis("tier").reset_index(name="n")
    tiers["denominator"] = len(revised); tiers["percent"] = tiers.n / len(revised)
    tiers.to_csv(OUT / "rq2_chain_quality_tiers.csv", index=False, encoding="utf-8-sig")

    # RQ3 main model set.
    main_chains = revised[(revised.model_eligible_main == 1) & revised.dimension_code.isin(LABELS["dimension"])].copy()
    main_instances = instances[(instances.model_eligible_main == 1) & instances.tool_code.isin(TOOL_LABELS)].merge(
        revised.drop(columns=["revised_quality_tier", "revised_quality_index", "model_eligible_main", "model_eligible_sensitivity"], errors="ignore"), on=["paper_id", "eval_id", "chain_id", "year", "dimension_code", "indicator_code"], how="left", suffixes=("", "_chain")
    )
    comparisons, weights, metas = [], [], []
    sensitivity_chains = revised[(revised.model_eligible_sensitivity == 1) & revised.dimension_code.isin(LABELS["dimension"])].copy()
    sensitivity_instances = instances[(instances.model_eligible_sensitivity == 1) & instances.tool_code.isin(TOOL_LABELS)].merge(
        revised.drop(columns=["revised_quality_tier", "revised_quality_index", "model_eligible_main", "model_eligible_sensitivity"], errors="ignore"), on=["paper_id", "eval_id", "chain_id", "year", "dimension_code", "indicator_code"], how="left", suffixes=("", "_chain")
    )
    analysis_sets = [
        ("主要规范集", main_chains, main_instances),
        ("扩展规范集", sensitivity_chains, sensitivity_instances),
    ]
    for tier_name, tier_chains, tier_instances in analysis_sets:
        for df, target_col, name, fixed in [
            (tier_chains, "dimension_code", "评价维度", []),
            (tier_chains[tier_chains.indicator_code.isin(LABELS["indicator"])], "indicator_code", "主观指标", ["dimension_code"]),
            (tier_instances, "tool_code", "测量工具类别", ["dimension_code", "indicator_code"]),
        ]:
            comp, imp, meta = model_and_weights(df, target_col, name, fixed)
            if len(comp):
                comp.insert(0, "analysis_tier", tier_name)
                comparisons.append(comp)
            if len(imp):
                imp.insert(0, "analysis_tier", tier_name)
                weights.append(imp)
            meta["analysis_tier"] = tier_name
            metas.append(meta)
    model_comp = pd.concat(comparisons, ignore_index=True) if comparisons else pd.DataFrame()
    label_weights = pd.concat(weights, ignore_index=True) if weights else pd.DataFrame()
    model_comp.to_csv(OUT / "rq3_model_comparison.csv", index=False, encoding="utf-8-sig")
    label_weights.to_csv(OUT / "rq3_label_group_weights.csv", index=False, encoding="utf-8-sig")
    associations = pd.concat([
        binary_associations(revised, instances, "model_eligible_main", "主要规范集"),
        binary_associations(revised, instances, "model_eligible_sensitivity", "扩展规范集"),
    ], ignore_index=True)
    associations.to_csv(OUT / "rq3_context_associations.csv", index=False, encoding="utf-8-sig")

    # Specific tool evidence retrieval table.
    rec_parts = []
    for tier_name, eligible_instances in [("主要规范集", main_instances), ("扩展规范集", sensitivity_instances)]:
        eligible_instances = eligible_instances[eligible_instances.indicator_code.isin(LABELS["indicator"])].copy()
        if len(eligible_instances):
            part = eligible_instances.groupby(["dimension_code", "indicator_code", "tool_code", "tool_label", "instrument_name"], dropna=False).agg(
                support_instances=("measure_instance_id", "nunique"), support_chains=("chain_id", "nunique"), support_papers=("paper_id", "nunique"), mean_quality=("revised_quality_index", "mean")
            ).reset_index()
            part.insert(0, "analysis_tier", tier_name)
            rec_parts.append(part)
    rec = pd.concat(rec_parts, ignore_index=True).sort_values(["analysis_tier", "indicator_code", "support_papers", "mean_quality"], ascending=[True, True, False, False]) if rec_parts else pd.DataFrame()
    rec.to_csv(OUT / "rq3_specific_tool_evidence.csv", index=False, encoding="utf-8-sig")

    summary = {
        "papers": int(papers.paper_id.nunique()),
        "evaluation_cases": int(evals.eval_id.nunique()),
        "evidence_chains": int(revised.chain_id.nunique()),
        "measure_instances": int(instances.measure_instance_id.nunique()),
        "mapped_dimension_chains": int(revised.dimension_code.isin(LABELS["dimension"]).sum()),
        "mapped_indicator_chains": int(revised.indicator_code.isin(LABELS["indicator"]).sum()),
        "Q1_high_confidence": int((revised.revised_quality_tier == "Q1").sum()),
        "Q2_usable": int((revised.revised_quality_tier == "Q2").sum()),
        "Q3_descriptive_or_sensitivity": int((revised.revised_quality_tier == "Q3").sum()),
        "excluded": int((revised.revised_quality_tier == "EXCLUDE").sum()),
        "main_model_chains": int(revised.model_eligible_main.sum()),
        "sensitivity_model_chains": int(revised.model_eligible_sensitivity.sum()),
        "model_metadata": metas,
        "tool_distribution": instances[instances.tool_code.isin(TOOL_LABELS)].tool_code.value_counts().to_dict(),
        "context_tests": context_stats,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
