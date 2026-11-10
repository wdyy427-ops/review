from __future__ import annotations

import json

import pandas as pd

from config import ROOT, LABELS
from revised_pipeline import TOOL_LABELS, AUDIT_LABELS


DATA = ROOT / "revised_results"


def main():
    papers = pd.read_csv(DATA / "papers.csv", keep_default_na=False)
    evals = pd.read_csv(DATA / "evaluation_cases.csv", keep_default_na=False)
    chains = pd.read_csv(DATA / "evidence_chains_revised.csv", keep_default_na=False)
    inst = pd.read_csv(DATA / "measure_instances.csv", keep_default_na=False)
    audits = pd.read_csv(DATA / "jcsee_chain_audit.csv", keep_default_na=False)
    checks = {
        "papers_125": papers.paper_id.nunique() == 125,
        "evaluation_cases_158": evals.eval_id.nunique() == 158,
        "evidence_chains_490": chains.chain_id.nunique() == 490 and len(chains) == 490,
        "measure_instance_ids_unique": inst.measure_instance_id.is_unique,
        "measure_instances_have_parent": set(inst.chain_id) <= set(chains.chain_id),
        "each_chain_has_measure_instance": set(chains.chain_id) == set(inst.chain_id),
        "tool_code_single_and_valid": inst.tool_code.isin(list(TOOL_LABELS) + ["UNMAPPED"]).all(),
        "audit_rows_3430": len(audits) == 490 * 7,
        "seven_audits_per_chain": audits.groupby("chain_id").standard.nunique().eq(7).all(),
        "audit_standard_codes_valid": set(audits.standard) == set(AUDIT_LABELS),
        "audit_status_valid": audits.status.isin(["S", "P", "NR", "C", "NA"]).all(),
        "quality_tiers_exhaustive": chains.revised_quality_tier.isin(["Q1", "Q2", "Q3", "EXCLUDE"]).all(),
        "dimension_codes_valid_or_missing": chains.dimension_code.isin(list(LABELS["dimension"]) + ["NR", "NA", "UNMAPPED", ""]).all(),
        "indicator_codes_valid_or_missing": chains.indicator_code.isin(list(LABELS["indicator"]) + ["NR", "NA", "UNMAPPED", ""]).all(),
    }
    checks = {k: bool(v) for k, v in checks.items()}
    out = {
        "all_checks_pass": bool(all(checks.values())),
        "checks": checks,
        "counts": {
            "papers": int(papers.paper_id.nunique()),
            "evaluation_cases": int(evals.eval_id.nunique()),
            "evidence_chains": int(chains.chain_id.nunique()),
            "measure_instances": int(inst.measure_instance_id.nunique()),
            "audit_rows": int(len(audits)),
            "unmapped_measure_instances": int((inst.tool_code == "UNMAPPED").sum()),
            "mapped_dimension_chains": int(chains.dimension_code.isin(LABELS["dimension"]).sum()),
            "mapped_indicator_chains": int(chains.indicator_code.isin(LABELS["indicator"]).sum()),
        },
    }
    (DATA / "qc_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if not out["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
