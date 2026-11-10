"""Semantic triage of retained A2/A3 S evidence, not a new full-text rating."""
from pathlib import Path
from collections import defaultdict, Counter
import csv
import json
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
src = ROOT / 'outputs/rq_review_20261024/supplement_enhanced_v2/03_revised_results/evidence_chains_supplement_enhanced.csv'
rows = list(csv.DictReader(src.open(encoding='utf-8-sig')))

# Stable sequence of unique retained strings was inspected in full before triage.
A3 = {
 2: ('clear_concern', 'The retained statement expressly says entity-label Kappa does not test emotion-measure reliability.'),
 3: ('clear_concern', 'The retained statement expressly says no agreement for innovation ratings and Kappa belongs to entity annotation.'),
 4: ('insufficient_quote', 'Splitting idea sets to enable reliability checks does not report those checks or their outcomes.'),
 5: ('clear_concern', 'Reliability refers to technical geometry/design workflow output, not subjective measurement.'),
 6: ('insufficient_quote', 'Describes threats to pairwise-label reliability, without a reported reliability result.'),
 8: ('clear_concern', 'Normality/homogeneity assumptions for a t test do not establish reliability of questionnaire measurement.'),
 9: ('clear_concern', 'Reliable LLM control of a toy-car interface is system operation, not subjective measurement reliability.'),
 10: ('insufficient_quote', 'Researcher consensus concerns task logs and may not apply to each subjective indicator inheriting this statement.'),
 11: ('clear_concern', 'Future work to strengthen reliability is not present-study support.'),
 12: ('clear_concern', 'Configurational conditions reliably producing outcomes do not establish measurement reliability.'),
 18: ('clear_concern', 'JSON-format consistency of LLM output does not establish subjective measurement reliability.'),
 19: ('clear_concern', 'A generated delivery-system description discusses operational reliability, not reliability evidence for evaluation.'),
 20: ('clear_concern', 'Image-dataset deduplication, view filtering, and quality control do not establish subjective-rating reliability.'),
 23: ('clear_concern', 'The retained quote warns that small sample size may produce unreliable results; a negated word triggered support.'),
 24: ('insufficient_quote', 'Generic assertion of reliable data lacks a reported procedure, statistic, or identifiable credibility action in this quote.'),
 25: ('insufficient_quote', 'Generic reduction of researcher influence does not establish reliability for all inherited subjective measures.'),
 27: ('clear_concern', 'Participants skepticism about reliability of AI content is a perceived effect, not measurement reliability evidence.'),
 28: ('insufficient_quote', 'Recruiting50people to bolster conclusions is not a specific measurement-reliability assessment.'),
 31: ('insufficient_quote', 'Five labels per item may improve precision, but the quote does not itself report agreement or reliability.'),
 32: ('insufficient_quote', 'Calling human eyes the most reliable criterion is not reported reliability evidence for the study.'),
}
A2 = {
 2: ('insufficient_quote', 'A broad claim of internal/construct/external validity does not by itself document measurement-validity evidence for12chains.'),
 5: ('clear_concern', 'The retained summary explicitly notes missing instrument source and independent validity justification.'),
 6: ('clear_concern', 'The retained summary says the adapted response format lacks current construct-validity verification.'),
 8: ('clear_concern', 'The retained summary expressly states that validity of the modified instrument was not verified.'),
}
out = []
for standard, field, rules, expected in [('A3', 'reliability_evidence', A3, 32), ('A2', 'validity_evidence', A2, 8)]:
    groups = defaultdict(list)
    for row in rows:
        if row['audit_' + standard] == 'S':
            groups[row[field]].append(row)
    assert len(groups) == expected
    for i, (text, chains) in enumerate(groups.items(), 1):
        status, reason = rules.get(i, ('apparently_relevant_pending_source_check', 'Contains apparently relevant evidence; no conclusion about adequacy, target correspondence, or source fidelity is made without full-text verification.'))
        for row in chains:
            out.append({'standard': standard, 'retained_status': 'S', 'paper_id': row['paper_id'], 'eval_id': row['eval_id'], 'chain_id': row['chain_id'],
                        'indicator_code': row['indicator_code'], 'pages': row['pages'], 'retained_evidence': text, 'triage': status,
                        'reason': reason, 'main_screen_eligible': row['model_eligible_main'], 'expanded_screen_eligible': row['model_eligible_sensitivity'],
                        'scope': 'Semantic triage of retained evidence only; original status unchanged; not adjudication of source paper'})
pd.DataFrame(out).to_csv(HERE / 'a2_a3_retained_evidence_triage.csv', index=False, encoding='utf-8-sig')
summary = {s: dict(Counter(r['triage'] for r in out if r['standard'] == s)) for s in ['A2', 'A3']}
for s in ['A2', 'A3']:
    selected = [r for r in out if r['standard'] == s and r['triage'] == 'clear_concern']
    summary[s]['clear_concern_papers'] = len(set(r['paper_id'] for r in selected))
    summary[s]['clear_concern_main_records'] = sum(r['main_screen_eligible'] == '1' for r in selected)
    summary[s]['clear_concern_expanded_records'] = sum(r['expanded_screen_eligible'] == '1' for r in selected)
(HERE / 'retained_evidence_triage_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
