from pathlib import Path
import csv
import json
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / 'outputs/rq_review_20261024/supplement_enhanced_v2/03_revised_results'

def table(caption, headers, rows, widths, **kw):
    assert len(headers) == len(widths)
    assert all(len(r) == len(headers) for r in rows)
    assert abs(sum(widths) - 6.5) < .001
    return {'caption': caption, 'headers': headers, 'rows': rows, 'widths': widths, 'width_unit': 'inches', **kw}

tables = {}
tables['screening'] = table(
    'Search and selection flow. Advanced assessment does not imply that full texts were available for every record. The 2022–2026 focus was adopted after the initial search.',
    ['Selection stage', 'Records'],
    [['Raw retrieval results', '5,299'], ['Repeated record IDs across retrievals removed', '164'],
     ['Unique retrieved IDs', '5,135'], ['Duplicate titles or DOIs removed', '55'],
     ['Metadata-identifiable non-full/non-peer-reviewed records removed', '87'],
     ['Records screened by title and abstract', '4,993'], ['Records excluded at title/abstract screening', '4,408'],
     ['Records advanced for further assessment', '585'], ['Records excluded during further assessment', '445'],
     ['Records retained before date refinement', '140'], ['Pre-2022 records excluded by scope refinement', '15'],
     ['Papers in the final corpus', '125']], [5.6, .9],
    note='Raw retrieval and repeated-ID counts derive from the retained retrieval narrative; subsequent counts are independently recoverable from the screening workbooks. The 585 advanced records comprise 82 provisional includes and 503 unclear records. The 55 duplicates comprise 54 title duplicates and one DOI duplicate.')

tables['context'] = table(
    'Contextual factors used to describe Subjective Evaluation of Perceived Effects. The prediction analysis uses the recorded contextual fields described below; derived object and evaluator-role fields are excluded.',
    ['Factor', 'Operational meaning and categories', 'Analytic role'],
    [
      ['G1 Evaluation purpose', 'Value elicitation and criteria construction; model supervision and calibration; formative feedback and iteration; summative verification and comparison.', 'Contextual predictor.'],
      ['G2 Design domain', 'Visual communication; industrial/product; fashion; interior; service; UI/UX design.', 'Contextual predictor; multiple domains may apply.'],
      ['G3 Design stage', 'Research; ideation; prototyping and testing; implementation.', 'Contextual predictor; describes the supported design activity.'],
      ['G4 Evaluation object', 'Design output; task or workflow; AI system/interface; human state or capability; human–AI relationship.', 'Descriptive category; excluded from prediction because its recoding used the target dimension or indicator.'],
      ['G5 Evaluator', 'Original identity categories: professional designer/domain expert; student/novice; target end user; public/crowdworker; client/organizational stakeholder; researcher.', 'Original identity coding is a predictor; derived role coding is excluded.'],
      ['G6 Target user', 'Direct workflow users: professional designer; design student/novice; nonprofessional creator.', 'Contextual predictor; distinguished from the actual evaluator.'],
      ['G7 AI function', 'Needs identification; knowledge retrieval; solution generation; prototype implementation; evaluation feedback; iterative optimization.', 'Contextual predictor; multiple functions may apply.'],
    ], [1.25, 3.15, 2.1],
    note='The coding schema permits multiple labels. G4 remains relevant to study description and evidence browsing, but the available derived coding is unsuitable as an independent predictor. G5 in the predictive sensitivity analysis refers to the original identity taxonomy, not the subsequent five-category evaluator-role taxonomy.')

tables['standards'] = table(
    'Selected JCSEE standards and review-specific operational questions. These questions adapt the standards to published evaluation evidence; they do not constitute an official certification instrument.',
    ['Code and official standard name', 'Operational question'],
    [
      ['U5 Relevant Information', 'Does the reported information address the stated evaluation purpose and the Perceived Effects under investigation?'],
      ['A2 Valid Information', 'Is the interpretation of the subjective indicator supported by a defensible connection among the Perceived Effects, operationalization, and measure?'],
      ['A3 Reliable Information', 'Is the dependability or credibility of the information supported by evidence appropriate to the measurement and analysis?'],
      ['A4 Explicit Program and Context Descriptions', 'Are the evaluation object, participants, task, and setting described sufficiently to interpret the findings?'],
      ['A6 Sound Designs and Analyses', 'Are the evaluation design and analysis appropriate for the question and the strength of the reported claim?'],
      ['A7 Explicit Evaluation Reasoning', 'Can the reasoning from collected information through analysis to the reported conclusion be traced?'],
      ['E1 Evaluation Documentation', 'Are the measures, procedures, scoring, results, and source locations documented sufficiently for scrutiny?'],
    ], [2.55, 3.95])

facts = json.loads((HERE / 'audit_facts.json').read_text(encoding='utf-8'))
tables['audit'] = table(
    'Provisional operational classifications of reported support across 514 candidate records. Counts describe the recorded screening outputs and are not verified assessments of study quality or JCSEE certification.',
    ['Criterion', 'S', 'P', 'C', 'NR', 'NA'],
    [[s] + [str(facts['audit_statuses'][s].get(status, 0)) for status in ['S', 'P', 'C', 'NR', 'NA']]
    for s in ['U5', 'A2', 'A3', 'A4', 'A6', 'A7', 'E1']], [1.5, 1., 1., 1., 1., 1.],
    note='S: sufficient support according to the operational screen; P: partial support; C: explicit concern; NR: not reported or indeterminate; NA: deemed inapplicable. Source-specific validation is outstanding. Inspection of retained support statements identified substantive mismatches in some A2 and A3 classifications. Every row totals 514; A3 contains 40 NA records.')

model_rows = list(csv.DictReader((HERE / 'corrective_analysis/model_summary.csv').open(encoding='utf-8-sig')))
target_names = {'perceived_effect_dimension': 'Perceived Effects dimension', 'subjective_indicator': 'Subjective indicator', 'tool_class': 'Tool class'}
model_names = {'frequency_baseline': 'Frequency baseline', 'context_only': 'Context only', 'known_evidence_only': 'Known evidence only', 'context_plus_known_evidence': 'Context + known evidence'}
out = []
for r in model_rows:
    if r['tier'] != 'expanded' or r['model'] not in model_names:
        continue
    out.append([target_names[r['target']], model_names[r['model']], r['n'], r['papers'], r['classes'],
                f"{float(r['macro_f1_mean']):.3f} ± {float(r['macro_f1_split_sd']):.3f}", f"{float(r['top2_accuracy_mean']):.3f}"])
assert len(out) == 10
tables['models'] = table(
    'Expanded-screen conditional prediction results over ten repetitions of cross-validation grouped by paper. Macro-F1 is reported as mean ± SD across data splits; SD is not a population confidence interval.',
    ['Prediction target', 'Information supplied', 'Records', 'Papers', 'Classes', 'Macro-F1', 'Top-2 accuracy'],
    out, [1.25, 1.55, .55, .5, .5, 1.25, .9],
    note='All non-baseline rows use the same fixed regularized logistic-regression specification. Known evidence is the selected Perceived Effects dimension for indicator prediction and the selected dimension plus indicator for tool prediction. G4 and derived G5 are excluded. Tool records are individual tool instances. Metrics are pooled over out-of-fold predictions within each repetition. Equal-paper-weighted scoring reverses the indicator ordering between known-evidence-only and context-plus-known-evidence (macro-F1 .321 versus .305), limiting claims of incremental contextual benefit.')

names = {
 'A1':'Novelty', 'A2':'Aesthetics', 'A3':'Suitability', 'A4':'Feasibility', 'A5':'Fidelity', 'A6':'Comprehensiveness',
 'B1':'Time efficiency', 'B2':'Workload', 'B3':'Iteration efficiency', 'B4':'Decision support', 'B5':'Process continuity', 'B6':'Handover efficiency',
 'C1':'Inspiration', 'C2':'Knowledge acquisition', 'C3':'Self-efficacy', 'C4':'Engagement and immersion', 'C5':'Enjoyment', 'C6':'Reflection', 'C7':'Fixation and dependence', 'C8':'Capability expansion',
 'D1':'Ease of use', 'D2':'Intention to use', 'D3':'Sense of control', 'D4':'Explainability', 'D5':'Trust', 'D6':'Agency', 'D7':'Roles, division of labor, and contribution fairness', 'D8':'Communication, coordination, conflict, and shared understanding',
 'E1':'End-user experience and acceptance', 'E2':'Fit with user needs, contexts, and populations', 'E3':'Fit with professional and organizational work', 'E4':'Cultural, social, and public value', 'E5':'Ethics, fairness, bias, and inclusion', 'E6':'Environmental and sustainability value', 'E7':'Business, brand, and market value', 'E8':'Long-term use, governance, and responsibility'}
chains = list(csv.DictReader((DATA / 'evidence_chains_supplement_enhanced.csv').open(encoding='utf-8-sig')))
counts = Counter(r['indicator_code'] for r in chains if r['indicator_code'] in names)
assert len(names) == 36 and sum(counts.values()) == 454
tables['indicators'] = table(
    'Distribution of the 36 subjective indicators across 454 indicator-mapped records. Counts reflect records, not independent papers or participants.',
    ['Code', 'Subjective indicator', 'Records', '%'],
    [[c, name, str(counts[c]), f'{100 * counts[c] / 454:.2f}'] for c, name in names.items()], [.55, 4.45, .75, .75],
    note='Indicator codes belong to the review taxonomy and should not be confused with similarly named JCSEE standard codes. Five Perceived Effects dimensions contain these indicators: A design outcome quality; B design process quality; C designer cognition, affect, and capability; D human–AI interaction experience; E social and contextual value. Six additional records map to a dimension but not to a specific indicator.')

tables['selectionguide'] = table(
    'Practical guidance for selecting evidence in Subjective Evaluation of Perceived Effects.',
    ['Decision', 'Evidence to establish', 'Interpretive limitation'], [], [1.4, 3.0, 2.1],
    note='Reserved for authoring by the lead manuscript agent; no empirical validation of recommendation effectiveness is implied.')

(HERE / 'manuscript_tables.json').write_text(json.dumps(tables, ensure_ascii=False, indent=2), encoding='utf-8')
print({k: len(v['rows']) for k, v in tables.items()})
