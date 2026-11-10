import json
from collections import Counter
from pathlib import Path

from config import ROOT, LABELS, STANDARDS


FINAL = ROOT / "final_results"
HYBRID = ROOT / "hybrid_review"
MANUAL = ROOT / "agents"
MANUAL_IDS = {1, 2, 3, 4, 43, 44, 45, 46, 47, 85, 86, 87}


def main():
    issues = []
    totals = Counter()
    merged_path = FINAL / "papers.json"
    papers = json.loads(merged_path.read_text(encoding="utf-8")) if merged_path.exists() else []
    by_id = {int(p["paper_id"]): p for p in papers}
    for pid in range(1, 126):
        p = by_id.get(pid)
        if p is None:
            issues.append({"paper_id": pid, "issue": "missing_file"}); continue
        totals["papers"] += 1
        if int(p.get("paper_id", -1)) != pid: issues.append({"paper_id": pid, "issue": "id_mismatch"})
        y = p.get("year")
        try:
            if not (2000 <= int(y) <= 2026): issues.append({"paper_id": pid, "issue": f"year_out_of_range:{y}"})
        except Exception: issues.append({"paper_id": pid, "issue": f"year_missing:{y}"})
        for field in ["domain", "stage", "ai_function", "ai_role", "target_user"]:
            bad = [x for x in p.get(field+"_codes", []) if x not in LABELS[field] and x not in {"UNMAPPED","NR","NA"}]
            if bad: issues.append({"paper_id": pid, "issue": f"invalid_{field}:{bad}"})
        for ev in p.get("evaluations", []):
            totals["evaluations"] += 1
            audit = {a.get("standard"): a.get("status") for a in ev.get("audit", [])}
            if set(audit) != set(STANDARDS): issues.append({"paper_id": pid, "eval_id": ev.get("eval_id"), "issue": "audit_incomplete"})
            for s, v in audit.items():
                if v not in LABELS["audit_status"]: issues.append({"paper_id": pid, "eval_id": ev.get("eval_id"), "issue": f"audit_invalid:{s}:{v}"})
            for c in ev.get("chains", []):
                totals["chains"] += 1
                dc, ic = c.get("dimension_code"), c.get("indicator_code")
                if dc not in LABELS["dimension"] and dc != "UNMAPPED": issues.append({"paper_id": pid, "issue": f"invalid_dimension:{dc}"})
                if ic not in LABELS["indicator"] and ic != "UNMAPPED": issues.append({"paper_id": pid, "issue": f"invalid_indicator:{ic}"})
                if not c.get("pages"): issues.append({"paper_id": pid, "eval_id": ev.get("eval_id"), "issue": "chain_missing_page"})
    out = {"totals": dict(totals), "issue_count": len(issues), "issues": issues}
    (FINAL / "qc_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"totals": dict(totals), "issue_count": len(issues)}, ensure_ascii=False))
    if any(i["issue"] == "missing_file" for i in issues): raise SystemExit(2)


if __name__ == "__main__": main()
