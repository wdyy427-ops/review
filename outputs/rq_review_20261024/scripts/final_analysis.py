from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from config import ROOT, LABELS, STANDARDS, code_labels


LLM_DIR = ROOT / "llm_review"
HYBRID_DIR = ROOT / "hybrid_review"
MANUAL_DIR = ROOT / "agents"
FINAL_DIR = ROOT / "final_results"
FIG_DIR = ROOT / "final_figures"
SITE_DIR = ROOT / "site" / "dist"
for p in [FINAL_DIR, FIG_DIR, SITE_DIR]:
    p.mkdir(parents=True, exist_ok=True)

MANUAL_IDS = {1, 2, 3, 4, 43, 44, 45, 46, 47, 85, 86, 87}


def as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def clean_codes(field, values):
    allowed = set(LABELS[field])
    out = []
    for value in as_list(values):
        if value in allowed or value in {"UNMAPPED", "NR", "NA"}:
            out.append(value)
    return list(dict.fromkeys(out))


def normalize_paper(p):
    pid = int(p["paper_id"])
    p["paper_id"] = pid
    for field in ["domain", "stage", "ai_function", "ai_role", "target_user"]:
        p[field + "_codes"] = clean_codes(field, p.get(field + "_codes", []))
    p["evaluations"] = as_list(p.get("evaluations"))
    for ei, ev in enumerate(p["evaluations"], 1):
        ev["eval_id"] = ev.get("eval_id") or f"{pid:03d}-E{ei}"
        for field in ["purpose", "object", "evaluator", "source", "task", "constraint"]:
            ev[field + "_codes"] = clean_codes(field, ev.get(field + "_codes", []))
        for field in ["setting", "design"]:
            val = ev.get(field + "_code", "NR")
            ev[field + "_code"] = val if val in LABELS[field] or val in {"NR", "NA", "UNMAPPED"} else "NR"
        ev["evaluation_stage_codes"] = clean_codes("stage", ev.get("evaluation_stage_codes", []))
        audits = {a.get("standard"): a for a in as_list(ev.get("audit")) if isinstance(a, dict)}
        ev["audit"] = []
        for standard in STANDARDS:
            a = audits.get(standard, {})
            status = a.get("status", "NR")
            if status not in LABELS["audit_status"]:
                status = "NR"
            ev["audit"].append({
                "standard": standard,
                "status": status,
                "facts": a.get("facts", ""),
                "reason": a.get("reason", ""),
                "pages": as_list(a.get("pages")),
                "quote": a.get("quote", ""),
            })
        ev["chains"] = as_list(ev.get("chains"))
        for c in ev["chains"]:
            dc = c.get("dimension_code", "UNMAPPED")
            c["dimension_code"] = dc if dc in LABELS["dimension"] else "UNMAPPED"
            ic = c.get("indicator_code", "UNMAPPED")
            c["indicator_code"] = ic if ic in LABELS["indicator"] else "UNMAPPED"
            ct = c.get("claim_type", "NR")
            c["claim_type"] = ct if ct in LABELS["claim_type"] else "NR"
            c["tool_family_codes"] = clean_codes("tool_family", c.get("tool_family_codes", []))
            to = c.get("tool_origin_code", "NR")
            c["tool_origin_code"] = to if to in LABELS["tool_origin"] else "NR"
    return p


def load_final_papers():
    papers = []
    missing = []
    for pid in range(1, 126):
        source = MANUAL_DIR / f"paper_{pid:03d}.json" if pid in MANUAL_IDS else HYBRID_DIR / f"paper_{pid:03d}.json"
        if not source.exists():
            missing.append(pid)
            continue
        p = json.loads(source.read_text(encoding="utf-8"))
        if pid in MANUAL_IDS:
            meta_path = ROOT / "autocode" / f"paper_{pid:03d}.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                for key in ["title", "doi", "year", "pdf_path"]:
                    if not p.get(key):
                        p[key] = meta.get(key)
            extracted_path = ROOT / "extracted" / f"{pid:03d}.json"
            if extracted_path.exists():
                raw_doc = json.loads(extracted_path.read_text(encoding="utf-8"))
                first_text = raw_doc.get("pages", [{}])[0].get("text", "")
                first_years = [int(x) for x in re.findall(r"\b(20[0-2]\d)\b", first_text)]
                if first_years:
                    p["year"] = max(y for y in first_years if y <= 2026)
        p["coding_source"] = "manual_fulltext_review" if pid in MANUAL_IDS else "hybrid_fulltext_rules_plus_semantic_inventory"
        papers.append(normalize_paper(p))
    if missing:
        raise RuntimeError(f"Missing final paper files: {missing}")
    (FINAL_DIR / "papers.json").write_text(json.dumps(papers, ensure_ascii=False, indent=2), encoding="utf-8")
    return papers


def audit_metrics(ev):
    statuses = {a["standard"]: a["status"] for a in ev["audit"]}
    no_c = "C" not in statuses.values()
    strict = no_c and all(statuses[s] in {"S", "NA"} for s in ["A2", "A3", "A6", "A7"]) and all(statuses[s] in {"S", "P", "NA"} for s in ["U5", "A4", "E1"])
    association = no_c and all(statuses[s] in {"S", "P", "NA"} for s in ["U5", "A2", "A4", "A6", "A7", "E1"])
    scored = [s for s in statuses.values() if s != "NA"]
    score = sum({"S": 1.0, "P": 0.5, "NR": 0.0, "C": 0.0}.get(s, 0) for s in scored) / len(scored) if scored else np.nan
    return int(strict), int(association), score, statuses


def flatten(papers):
    paper_rows, eval_rows, audit_rows, chain_rows = [], [], [], []
    for p in papers:
        prow = {
            "paper_id": p["paper_id"], "title": p.get("title", ""), "doi": p.get("doi", ""), "year": p.get("year"),
            "domains": ";".join(p["domain_codes"]), "stages": ";".join(p["stage_codes"]),
            "ai_functions": ";".join(p["ai_function_codes"]), "ai_roles": ";".join(p["ai_role_codes"]),
            "target_users": ";".join(p["target_user_codes"]), "has_human_subjective_evaluation": int(bool(p["evaluations"])),
            "evaluation_count": len(p["evaluations"]), "coding_source": p.get("coding_source", ""),
            "scope_note": p.get("scope_note", ""), "context_summary": p.get("context_summary", ""),
        }
        paper_rows.append(prow)
        for ev in p["evaluations"]:
            strict, assoc, qscore, statuses = audit_metrics(ev)
            erow = {
                "paper_id": p["paper_id"], "eval_id": ev["eval_id"], "title": p.get("title", ""),
                "purposes": ";".join(ev["purpose_codes"]), "objects": ";".join(ev["object_codes"]),
                "evaluators": ";".join(ev["evaluator_codes"]), "sources": ";".join(ev["source_codes"]),
                "setting": ev["setting_code"], "design": ev["design_code"],
                "evaluation_stages": ";".join(ev["evaluation_stage_codes"]), "tasks": ";".join(ev["task_codes"]),
                "constraints": ";".join(ev["constraint_codes"]), "sample_n": ev.get("sample_n"),
                "sample_description": ev.get("sample_description", ""), "recruitment": ev.get("recruitment", ""),
                "task": ev.get("task", ""), "comparator": ev.get("comparator", ""), "procedure": ev.get("procedure", ""),
                "analysis": ev.get("analysis", ""), "actual_results": ev.get("actual_results", ""),
                "limitations": ev.get("limitations", ""), "ethics": ev.get("ethics", ""),
                "strict_eligible": strict, "association_eligible": assoc, "quality_index": qscore,
                "explicit_problem": int("C" in statuses.values()),
            }
            erow.update(statuses)
            eval_rows.append(erow)
            for a in ev["audit"]:
                audit_rows.append({"paper_id": p["paper_id"], "eval_id": ev["eval_id"], **a})
            for ci, c in enumerate(ev["chains"], 1):
                crow = {
                    "paper_id": p["paper_id"], "eval_id": ev["eval_id"], "chain_id": f"{ev['eval_id']}-C{ci}",
                    "title": p.get("title", ""), "year": p.get("year"), "domains": ";".join(p["domain_codes"]),
                    "stages": ";".join(p["stage_codes"]), "ai_functions": ";".join(p["ai_function_codes"]),
                    "ai_roles": ";".join(p["ai_role_codes"]), "target_users": ";".join(p["target_user_codes"]),
                    "purposes": erow["purposes"], "objects": erow["objects"], "evaluators": erow["evaluators"],
                    "sources": erow["sources"], "setting": erow["setting"], "design": erow["design"],
                    "evaluation_stages": erow["evaluation_stages"], "tasks": erow["tasks"], "constraints": erow["constraints"],
                    "strict_eligible": strict, "association_eligible": assoc, "quality_index": qscore,
                    "explicit_problem": erow["explicit_problem"],
                    "claim_quote": c.get("claim_quote", ""), "claim_summary": c.get("claim_summary", ""),
                    "claim_type": c.get("claim_type", "NR"), "construct_raw": c.get("construct_raw", ""),
                    "indicator_raw": c.get("indicator_raw", ""), "item_quote": c.get("item_quote", ""),
                    "dimension_code": c.get("dimension_code", "UNMAPPED"), "indicator_code": c.get("indicator_code", "UNMAPPED"),
                    "instrument_raw": c.get("instrument_raw", ""), "tool_families": ";".join(c.get("tool_family_codes", [])),
                    "tool_origin": c.get("tool_origin_code", "NR"), "adaptation": c.get("adaptation", ""),
                    "response_scoring": c.get("response_scoring", ""), "validity_evidence": c.get("validity_evidence", ""),
                    "reliability_evidence": c.get("reliability_evidence", ""), "result_quote": c.get("result_quote", ""),
                    "effect_direction": c.get("effect_direction", ""), "pages": ";".join(map(str, as_list(c.get("pages")))),
                }
                chain_rows.append(crow)
    dfs = {
        "papers": pd.DataFrame(paper_rows), "evaluations": pd.DataFrame(eval_rows),
        "audits": pd.DataFrame(audit_rows), "chains": pd.DataFrame(chain_rows),
    }
    for name, df in dfs.items():
        df.to_csv(FINAL_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
    return dfs


def explode_codes(df, column, field, level):
    counts = Counter()
    for text in df[column].fillna(""):
        for code in str(text).split(";"):
            if code:
                counts[code] += 1
    total = len(df)
    return pd.DataFrame([
        {"level": level, "variable": field, "code": code, "label": LABELS[field].get(code, code), "n": n, "denominator": total, "percent": n / total if total else np.nan}
        for code, n in counts.most_common()
    ])


def rq1_tables(dfs):
    p, c = dfs["papers"], dfs["chains"]
    rows = []
    years = pd.to_numeric(p["year"], errors="coerce").dropna().astype(int).value_counts().sort_index()
    rows.append(pd.DataFrame([{"level": "paper", "variable": "year", "code": str(y), "label": str(y), "n": int(n), "denominator": len(p), "percent": n / len(p)} for y, n in years.items()]))
    for col, field in [("domains", "domain"), ("stages", "stage"), ("ai_functions", "ai_function"), ("ai_roles", "ai_role"), ("target_users", "target_user")]:
        rows.append(explode_codes(p, col, field, "paper"))
    if len(c):
        for col, field in [("dimension_code", "dimension"), ("indicator_code", "indicator"), ("tool_families", "tool_family"), ("tool_origin", "tool_origin"), ("claim_type", "claim_type")]:
            rows.append(explode_codes(c, col, field, "chain"))
    out = pd.concat(rows, ignore_index=True)
    out.to_csv(FINAL_DIR / "rq1_distributions.csv", index=False, encoding="utf-8-sig")
    return out


def rq2_tables(dfs):
    a, e = dfs["audits"], dfs["evaluations"]
    status_order = ["S", "P", "C", "NR", "NA"]
    rows = []
    for standard in STANDARDS:
        sub = a[a.standard == standard]
        counts = sub.status.value_counts()
        for status in status_order:
            rows.append({
                "standard": standard, "standard_label": STANDARDS[standard], "status": status,
                "status_label": LABELS["audit_status"][status], "n": int(counts.get(status, 0)),
                "denominator": len(sub), "percent": counts.get(status, 0) / len(sub) if len(sub) else np.nan,
            })
    status = pd.DataFrame(rows)
    tiers = pd.DataFrame([
        {"tier": "严格高规范案例", "rule": "A2/A3/A6/A7为S或NA；U5/A4/E1为S/P/NA；无C", "n": int(e.strict_eligible.sum()), "denominator": len(e)},
        {"tier": "关联分析案例", "rule": "U5/A2/A4/A6/A7/E1为S/P/NA；A3未报告可保留；无C", "n": int(e.association_eligible.sum()), "denominator": len(e)},
        {"tier": "全部人类主观评价案例", "rule": "全文确认存在人类主观评价", "n": len(e), "denominator": len(e)},
    ])
    status.to_csv(FINAL_DIR / "rq2_audit_status.csv", index=False, encoding="utf-8-sig")
    tiers.to_csv(FINAL_DIR / "rq2_quality_tiers.csv", index=False, encoding="utf-8-sig")
    return status, tiers


def split_codes(text):
    return [x for x in str(text or "").split(";") if x and x not in {"NR", "NA", "UNMAPPED"}]


def bh_adjust(pvals):
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    q = np.minimum.accumulate((ranked * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    out = np.empty_like(q)
    out[order] = np.minimum(q, 1)
    return out


def association_table(chains):
    context_cols = {
        "domains": "domain", "stages": "stage", "ai_functions": "ai_function", "ai_roles": "ai_role",
        "target_users": "target_user", "purposes": "purpose", "objects": "object", "evaluators": "evaluator",
        "sources": "source", "evaluation_stages": "stage", "tasks": "task", "constraints": "constraint",
    }
    targets = [("dimension_code", "dimension"), ("tool_families", "tool_family")]
    records = []
    n = len(chains)
    for ccol, cfield in context_cols.items():
        for ccode in LABELS[cfield]:
            x = chains[ccol].fillna("").map(lambda s: ccode in split_codes(s)).to_numpy()
            if x.sum() < 3 or (~x).sum() < 3:
                continue
            for tcol, tfield in targets:
                for tcode in LABELS[tfield]:
                    y = chains[tcol].fillna("").map(lambda s: tcode in split_codes(s)).to_numpy()
                    if y.sum() < 3 or (~y).sum() < 3:
                        continue
                    a = int(np.sum(x & y)); b = int(np.sum(x & ~y)); c = int(np.sum(~x & y)); d = int(np.sum(~x & ~y))
                    odds, pval = fisher_exact([[a, b], [c, d]])
                    phi = (a*d-b*c) / math.sqrt((a+b)*(c+d)*(a+c)*(b+d)) if all(v > 0 for v in [(a+b),(c+d),(a+c),(b+d)]) else np.nan
                    px = a/(a+b) if a+b else np.nan
                    base = (a+c)/n if n else np.nan
                    records.append({
                        "context_field": cfield, "context_code": ccode, "context_label": LABELS[cfield][ccode],
                        "target_field": tfield, "target_code": tcode, "target_label": LABELS[tfield][tcode],
                        "a_both": a, "context_n": a+b, "target_n": a+c, "n": n,
                        "conditional_probability": px, "baseline_probability": base,
                        "lift": px/base if base else np.nan, "odds_ratio": odds, "cramers_v_signed": phi, "p_value": pval,
                    })
    out = pd.DataFrame(records)
    if len(out):
        out["q_value_bh"] = bh_adjust(out.p_value)
        out["evidence_grade"] = np.where((out.q_value_bh < .05) & (out.context_n >= 10) & (out.a_both >= 5), "较强", np.where((out.p_value < .05) & (out.a_both >= 3), "探索性", "证据不足"))
        out = out.sort_values(["q_value_bh", "cramers_v_signed"], ascending=[True, False])
    out.to_csv(FINAL_DIR / "rq3_associations.csv", index=False, encoding="utf-8-sig")
    return out


def aggregate_for_association(chains):
    if chains.empty:
        return chains.copy()
    context_cols = ["domains","stages","ai_functions","ai_roles","target_users","purposes","objects","evaluators","sources","setting","design","evaluation_stages","tasks","constraints"]
    rows = []
    for (pid, eid), sub in chains.groupby(["paper_id", "eval_id"], sort=False):
        row = {"paper_id": pid, "eval_id": eid}
        for col in context_cols:
            row[col] = sub.iloc[0][col]
        row["dimension_code"] = ";".join(sorted({x for s in sub.dimension_code for x in split_codes(s)}))
        row["tool_families"] = ";".join(sorted({x for s in sub.tool_families for x in split_codes(s)}))
        rows.append(row)
    return pd.DataFrame(rows)


def model_comparison(chains, target_col, target_name):
    data = chains.copy()
    if target_col == "tool_families":
        data["target"] = data[target_col].fillna("").map(lambda s: split_codes(s)[0] if split_codes(s) else "")
    else:
        data["target"] = data[target_col]
    data = data[~data.target.isin(["", "NR", "NA", "UNMAPPED"])].copy()
    counts = data.target.value_counts()
    keep = counts[counts >= 5].index
    data = data[data.target.isin(keep)].copy()
    if len(data) < 30 or data.target.nunique() < 2:
        return pd.DataFrame([{"target": target_name, "model": "样本不足", "n": len(data), "classes": data.target.nunique()}])
    n_splits = int(min(5, counts.loc[keep].min(), data.paper_id.nunique()))
    n_splits = max(2, n_splits)
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=20261025)
    feature_spec = {
        "domains":"domain", "stages":"stage", "ai_functions":"ai_function", "ai_roles":"ai_role",
        "target_users":"target_user", "purposes":"purpose", "objects":"object", "evaluators":"evaluator",
        "sources":"source", "evaluation_stages":"stage", "tasks":"task", "constraints":"constraint",
    }
    X = pd.DataFrame(index=data.index)
    for col, field in feature_spec.items():
        for code in LABELS[field]:
            X[f"{field}_{code}_{col}"] = data[col].fillna("").map(lambda s: int(code in split_codes(s)))
    for field in ["setting", "design"]:
        for code in LABELS[field]:
            X[f"{field}_{code}"] = (data[field] == code).astype(int)
    X["quality_index"] = pd.to_numeric(data.quality_index, errors="coerce").fillna(0)
    models = {
        "频率基线": DummyClassifier(strategy="prior"),
        "L2多项逻辑回归": LogisticRegression(max_iter=3000, class_weight="balanced", C=1.0),
        "随机森林": RandomForestClassifier(n_estimators=500, min_samples_leaf=2, class_weight="balanced_subsample", random_state=20261025),
        "极端随机树": ExtraTreesClassifier(n_estimators=500, min_samples_leaf=2, class_weight="balanced", random_state=20261025),
        "直方图梯度提升": HistGradientBoostingClassifier(max_iter=200, learning_rate=.05, max_leaf_nodes=15, random_state=20261025),
    }
    records = []
    y, groups = data.target, data.paper_id
    for name, clf in models.items():
        fold_scores = []
        for fold, (tr, te) in enumerate(cv.split(X, y, groups), 1):
            try:
                clf.fit(X.iloc[tr], y.iloc[tr])
                pred = clf.predict(X.iloc[te])
                fold_scores.append({
                    "macro_f1": f1_score(y.iloc[te], pred, average="macro", zero_division=0),
                    "weighted_f1": f1_score(y.iloc[te], pred, average="weighted", zero_division=0),
                    "balanced_accuracy": balanced_accuracy_score(y.iloc[te], pred),
                })
            except Exception as exc:
                fold_scores.append({"macro_f1": np.nan, "weighted_f1": np.nan, "balanced_accuracy": np.nan, "error": str(exc)})
        records.append({
            "target": target_name, "model": name, "n": len(data), "papers": data.paper_id.nunique(), "classes": data.target.nunique(), "folds": n_splits,
            "macro_f1_mean": np.nanmean([x["macro_f1"] for x in fold_scores]), "macro_f1_sd": np.nanstd([x["macro_f1"] for x in fold_scores]),
            "weighted_f1_mean": np.nanmean([x["weighted_f1"] for x in fold_scores]),
            "balanced_accuracy_mean": np.nanmean([x["balanced_accuracy"] for x in fold_scores]),
        })
    return pd.DataFrame(records)


def rq3_models(dfs):
    chains = dfs["chains"]
    eligible = chains[chains.association_eligible == 1].copy()
    if len(eligible) >= 30:
        analysis_set, used_tier = eligible, "关联分析案例"
    else:
        analysis_set = chains[(chains.explicit_problem == 0) & (pd.to_numeric(chains.quality_index, errors="coerce").fillna(0) >= .35)].copy()
        used_tier = "无明确问题且质量指数≥0.35的敏感性案例"
        if len(analysis_set) < 30:
            analysis_set = chains[chains.explicit_problem == 0].copy()
            used_tier = "无明确问题案例（关联分析案例不足30）"
    assoc = association_table(aggregate_for_association(analysis_set))
    models = pd.concat([
        model_comparison(analysis_set, "dimension_code", "评价维度"),
        model_comparison(analysis_set, "tool_families", "测量工具族"),
    ], ignore_index=True)
    models["analysis_tier"] = used_tier
    models.to_csv(FINAL_DIR / "rq3_model_comparison.csv", index=False, encoding="utf-8-sig")
    (FINAL_DIR / "rq3_analysis_set.json").write_text(json.dumps({"tier": used_tier, "chains": len(analysis_set), "papers": int(analysis_set.paper_id.nunique()) if len(analysis_set) else 0}, ensure_ascii=False, indent=2), encoding="utf-8")
    return analysis_set, assoc, models


def recommendation_tables(chains):
    # Empirical recommendation table: indicator -> tool family, stratified by major context codes when support exists.
    records = []
    for indicator, sub in chains[~chains.indicator_code.isin(["", "NR", "NA", "UNMAPPED"])].groupby("indicator_code"):
        tool_counts = Counter(t for s in sub.tool_families for t in split_codes(s))
        for tool, n in tool_counts.most_common():
            records.append({
                "indicator_code": indicator, "indicator_label": LABELS["indicator"].get(indicator, indicator),
                "dimension_code": indicator[0], "dimension_label": LABELS["dimension"].get(indicator[0], indicator[0]),
                "tool_code": tool, "tool_label": LABELS["tool_family"].get(tool, tool),
                "support_chains": n, "indicator_chains": len(sub), "conditional_probability": n / len(sub),
                "support_papers": sub[sub.tool_families.map(lambda s: tool in split_codes(s))].paper_id.nunique(),
                "example_instruments": "；".join(x for x, _ in Counter(sub[sub.tool_families.map(lambda s: tool in split_codes(s))].instrument_raw.dropna()).most_common(5) if x),
            })
    out = pd.DataFrame(records).sort_values(["indicator_code", "support_chains"], ascending=[True, False]) if records else pd.DataFrame()
    out.to_csv(FINAL_DIR / "recommendations.csv", index=False, encoding="utf-8-sig")
    return out


def main():
    papers = load_final_papers()
    dfs = flatten(papers)
    rq1 = rq1_tables(dfs)
    rq2_status, rq2_tiers = rq2_tables(dfs)
    analysis_set, assoc, models = rq3_models(dfs)
    recs = recommendation_tables(analysis_set)
    summary = {
        "papers": len(dfs["papers"]), "papers_with_human_subjective_evaluation": int(dfs["papers"].has_human_subjective_evaluation.sum()),
        "evaluations": len(dfs["evaluations"]), "chains": len(dfs["chains"]),
        "strict_evaluations": int(dfs["evaluations"].strict_eligible.sum()) if len(dfs["evaluations"]) else 0,
        "association_eligible_evaluations": int(dfs["evaluations"].association_eligible.sum()) if len(dfs["evaluations"]) else 0,
        "association_analysis_chains": len(analysis_set), "association_analysis_papers": int(analysis_set.paper_id.nunique()) if len(analysis_set) else 0,
        "manual_reviewed_papers": len(MANUAL_IDS), "hybrid_reviewed_papers": 125 - len(MANUAL_IDS),
    }
    (FINAL_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
