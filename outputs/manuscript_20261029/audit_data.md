# Independent audit of manuscript inputs

Audit date: 29 October 2026. All original workbooks, PDFs, coding tables, and analysis scripts were treated as read-only. New audit and corrective-analysis files are in `outputs/manuscript_20261029/`. This audit checks computational provenance and retained evidence, not every full text. It does not supply independent human validation of the coding.

## 1. Which data are current, and what do the denominators mean?

Use `outputs/rq_review_20261024/supplement_enhanced_v2/03_revised_results/`, not the older 490-record analysis. The current CSVs contain 125 papers,159 evaluation cases,514 candidate records,624 measurement-tool instances, and 3,598 standard-level audit rows. Of 514 records,460 map to a perceived-effect dimension and 454 to a subjective indicator. Of 624 tool instances,608 map to M1–M5 and 16 remain unmapped.

**Corpus and mapped evidence are not the same set.** There are 125 corpus papers;95 contribute at least one of the 514 candidate records;71 contribute at least one of the 460 dimension-mapped records. Twenty-fourpapers contribute candidate records but none mapped to a dimension, and 30 papers contribute no candidate records. The 54 dimension-unmapped records occur in 34 papers:24 with only unmapped records and 10 with both mapped and unmapped records. The paper-level `has_human_subjective_evaluation` flag is 95 yes/30 no. Thus a manuscript must not claim that all 125 papers contributed mapped Subjective Evaluation evidence or that all 514 candidate records are confirmed complete evidence chains.

The five dimension counts, denominator 460, are A144(31.30%),B43(9.35%),C110(23.91%),D97(21.09%),E66(14.35%). The classified tool-instance counts, denominator 608, are M1(named standardized scales)97(15.95%),M2(ad hoc structured ratings)193(31.74%),M3(qualitative verbal elicitation)138(22.70%),M4(non-scale structured questionnaires)115(18.91%),M5(existing perceptual-data analysis)65(10.69%). These are record/instance frequencies, not proportions of papers or evaluations. Multiple records within papers are dependent. Domains, stages, and contextual categories are multi-label where recorded.

All 36 predefined subjective indicators appear. The 6 records with a mapped dimension but unmapped indicator and the 54 dimension-unmapped records must remain distinguishable. The older-to-current change is 28 replacement/additional records minus 4 removed records, net+24. RQ1 distribution differences are small (maximum absolute change 0.9215 percentage points for tool classes), but model feature rankings and selected subsets are not stable under this update.

Machine-readable counts are in `audit_facts.json`; the complete catalogue is `reviewed_corpus_catalogue.csv`.

## 2. Search and screening provenance

`text.docx` documents a 25September 2026 retrieval, initially covering 2016–2026. It describes OpenAlex-based proxies for ACM and selected design-journal sources, rather than a fully executed native ACM Digital Library or multidisciplinary bibliographic-database search. Native database queries must not be claimed without their actual export logs. Exact original Boolean strings, per-query counts, and deduplication implementation should be reported from the retained narrative/logs where available, with missing details acknowledged.

The workbooks independently establish the following counts:

| Stage | Count | Evidence |
|---|---:|---|
| Raw retrieved records |5,299|`text.docx` narrative only|
| Repeated identical IDs across retrievals |164|`text.docx` narrative only|
| Unique IDs before metadata screening |5,135|4,993 candidates+142 excluded in round 1|
| Duplicate titles |54|`check/round1_corrected.xlsx`,Excluded|
| Duplicate DOI |1|Same worksheet|
| Metadata-identifiable non-full/non-peer-reviewed records |87|Same worksheet|
| Title/abstract-screened candidates |4,993|Candidates worksheet|
| Provisional includes / unclear / excludes |82/503/4,408|`check/round2_corrected.xlsx`|
| Advanced assessment candidates |585|82+503|
| Unclear retained / rejected |80/423|`check/round3.xlsx`|
| Provisional includes retained / rejected |60/22|Same workbook|
| Retained before date refinement |140|`check/Final included_corrected.xlsx`|
| Pre 2022 removed by later scope refinement |15|Numbered records 126–140|
| Final contemporary corpus |125|Numbered records 1–125|

The 54 title+1DOI+87 metadata exclusions resolve the conflicting narrative 54+88 versus 55+87:55 duplicates in total, not 55 duplicate titles. The later exclusion of 15 pre 2022 papers is a post-search refinement, not a prespecified search limit. The user's stated rationale is the small earlier corpus and focus on the rapidly expanding contemporary AI era. It does not establish a universal technological break in 2022. Do not label all 585 advanced candidates “retrieved full texts”: the later screening pilot includes decisions based only on abstracts or publication metadata. Report actual retrieval failures only if independently documented.

`search_screening_audit.csv` supplies these counts and their evidence status.

## 3. Screening agreement is not coding reliability

The actual paired workbooks were read without editing. Rows were paired only after checking exact record-ID equality. “Included” was normalized to “include”; “unclear” remained its own class. These are unweighted Cohen kappas, not weighted or chance-corrected percentage agreements.

| Comparison | Paired rows | Agreements | Agreement | Kappa |
|---|---:|---:|---:|---:|
| Title/abstract model–model |999|965|96.60%|0.746751|
| Title/abstract model–human |21|20|95.24%|0.644068|
| Later screening model–human, all paired rows |115|86|74.78%|0.501495|
| Same later sample, duplicate IDs removed |109|82|75.23%|0.515795|

The later sample has 6 duplicate records with identical paired decisions. Of 115 paired decisions,77 were labelled full-text-based,37 abstract-based, and 1 publication-metadata-based by the model output. The full-text-based 77 alone yield kappa 0.365276. Removing the 5 model “unclear” rows from the 115 does not reproduce the narrative 0.742 either (kappa 0.545611). Accordingly, **the existing narrative claim of 0.742 cannot be substantiated by these paired files**.

Source files: `1_consensus test/model consensus/{5.6 sol,6.1 sol} consensus test screened.xlsx`; `1_consensus test/model-human consensus/{6.1 sol test,artificial test}.xlsx`; `2_consensus test/{6.1 sol consensus test2 screened,artificial experiment}.xlsx`. Later decisions use column 21 of both first worksheets; the 21-record pair uses modelcolumn 18 and humancolumn 14. Preserved paired rows and disagreements are in `consensus_paired_decisions.csv` and `consensus_disagreements.csv`. None of these pilots establishes reliability of the 125-paper extraction, perceived-effect mapping, or JCSEE-inspired ratings. The 24Octoberprotocol explicitly describes AI-assisted full-text coding and disclaims independent dual-human coding.

## 4. Metadata and temporal sensitivity

The numbered original workbook identifies the same 125 papers. Two DOI fields in the analytical CSV required correction in the new catalogue only:

- Paper 34, “Large language model agent as a mechanical designer”: `10.1080/09544828.2026.2624356`. The analytical CSV's `10.1109/TASE.2025.123456` is incorrect. Crossref confirms the corrected title, online 11February 2026, print 3August 2026.
- Paper 125, “Identification of similar design principles of passenger cars using deep neural networks”: `10.1504/jdr.2022.127571`. The analytical CSV's `10.1504/JDR.2022.10051661` does not match the original record. Crossref confirms the corrected DOI/title/year 2022.

Thirty-two of 125 coded years differ from the original screening years. This is partly online-first versus issue-year assignment, but not uniformly so. Do not equate either field automatically with first publication. For 2022,2023,2024,2025,2026 respectively, coding-year counts are 11,11,20,27,56; screening-year counts are 11,13,27,35,39. Examples verified by Crossref:paper 40 online 2025/print 2026;paper 41 online 2025/print 2026;paper 34 really 2026 rather than coded 2025;paper 47 screening 2025 but Crossref online 2026. Hence the magnitude of recent growth depends on the date convention.

`reviewed_corpus_catalogue.csv` preserves original screening title/year/date and coded title/year/DOI, plus Crossref online/print/published/issued dates. `publication_year_sensitivity.csv` recomputes paper, dimension-record, and tool-instance distributions under the coding-year, screening-year, and Crossref-published conventions. `crossref_corpus_metadata.json` preserves successful official metadata responses for all 125 papers. Neither original source dataset was silently repaired.

## 5. RQ2: exact implemented screen and limitations

Use the actual 514×7 audit rows, not the current narrative report's A3 row. Correct counts are:

| Criterion | S | P | NR | C | NA |
|---|---:|---:|---:|---:|---:|
| U5 |446|6|62|0|0|
| A2 |44|405|65|0|0|
| A3 |205|7|262|0|40|
| A4 |60|407|47|0|0|
| A6 |191|25|292|6|0|
| A7 |214|2|292|6|0|
| E1 |152|345|17|0|0|

**The current RQ2 narrative incorrectly gives A3NA=0; the correct value is 40.** Its printed row sums to 474 rather than 514. Use `keep_default_na=False` when reading these CSVs: pandas otherwise interprets the literal “NA” as missing.

The implemented algorithm is `outputs/rq_review_20261024/scripts/revised_pipeline.py::chain_audit`, called by `tmp/run_supplement_enhanced_analysis.py`. Its statuses are reproducible automated operational screens of retained fields:

- U5: presence of claim, construct, mapped indicator, and instrument (S); weaker dimension-level mapping(P).
- A2: a validity keyword with limited negation detection, mapped indicator, and instrument(S); dimension/instrument plus item or named scale(P).
- A3: a reliability/credibility keyword with limited negation detection(S); exclusivelyM4 and no scoring(NA); named scale plus nonempty validity field(P); otherwiseNR.
- A4: inherited evaluation-level status; it is not re-estimated independently for every chain.
- A6: result plus recognizable analysis keyword or comparator(S), result alone(P); explicit causal claim lacking comparator/recognized analysis(C).
- A7: claim plus result with algorithmically permitted claim strength(S/P); the same causal overreach condition(C).
- E1: completeness count across pages, instrument, scoring, item, and result:all 5(S);at least 3 including pages/instrument(P).

The seven codes are researcher operationalizations inspired by selected JCSEE standards, not an official validated seven-item instrument or certification. A keyword match is not adequate source-specific validity/reliability appraisal, a comparator is not sufficient design/analysis adequacy, and completeness is not correctness. NR denotes insufficient reporting/information in retained fields, not demonstrated poor research.

Exact tiers:

- **Q1=19:** no C;U5/A2/A6/A7 allS;A3S orNA;A4/E1S orP.
- **Q2=44:** no C;U5/A2/A4/A6/A7/E1 allS orP;A3S/P/NA;not Q1.
- **Main operational screen=63 records from 22 papers:** Q1+Q2. Includes 69 classified tool instances before tool-class support filtering.
- **Expanded operational screen=183 records from 43 papers:** sameS/Prequirements on U5/A2/A4/A6/A7/E1, no C, but A3 may also beNR. Includes 210 classified tool instances.
- Q3=445 includes both the additional 120 expanded-eligible records and 325 records failing that screen. EXCLUDE=6.

This differs from the 24Octoberprotocol's stricter stated main criterion(A2/A3/A6/A7Swith justifiedNA;U5/A4/E1≥P). It must not be described as unchanged prespecified quality eligibility or as a set of “high-quality” studies. The implemented quality-index arithmetic is also not an official JCSEE total score.

### Retained-evidence triage

All 32 unique strings underlying 205A3Sassignments and all 8 unique strings underlying 44A2Sassignments were inspected semantically. Original statuses were not changed. In A3,74 records from 11 papers contain an explicit topic mismatch, negation, or future-only statement;57 others have generic or insufficient quoted support;74 contain apparently pertinent material that still needs source and construct correspondence checks. Seven of the 74 clear-concern records enter both main and expanded screens. Examples include entity-annotation Kappa expressly said not to support emotion measurement(paper 3), t-test assumption checks(paper 12), reliable LLM JSON output(paper 54), futurework(paper 25), and participants' distrust of AI content(paper 82). These cannot establish measurement reliability merely because the word appears.

In A2,11 records from 3 papers expressly acknowledge absent/unverified validity justification yet are assignedS;9 enter the main screen and all 11 the expanded screen. Another 12 use a general multi-level validity assertion requiring further verification. These are flags on retained evidence, not definitive re-ratings of the papers. The exact fields, IDs, page locators, reasons, and screen membership are preserved in `a2_a3_retained_evidence_triage.csv`; summary counts are in `retained_evidence_triage_summary.json`.

Consequently, publish the counts only as **provisional automated reporting-support classifications requiring human criterion validation**. Their computational reproducibility does not establish the accuracy of the classifications. The source-specific status of allsevencriteria remains unvalidated.

## 6. RQ3: original analysis and leakage

The current RQ3 pipeline groups train/test splits bypaper, which prevents same-paper row overlap. It retains target classes with≥5 records from≥3 papers, excludes unsupported classes, and models a single categorical target at record/instance level. Tool predictions operate on instances, not joint multi-tool sets. Models use binary encodings; indicator prediction fixes known dimension, and tool prediction fixes known dimension+indicator. Those are conditional prediction tasks, not end-to-end recommendation accuracy.

**Critical target leakage:** `scripts/rq3_rebuild_g1_g7.py::recode_object` directly reads `dimension_code` and `indicator_code` to construct G4. For example, dimensionBassigns processO2,Cassigns human stateO4,Aassigns outputO1; particularDindicators assign interface/relationship objects. G4's 96.3%dimension importance therefore partly restates the target. G5 recoding also reads dimensionB/C/Dwhen disambiguating oldV1 with sourceH1. It additionally reads claim/instrument text. Grouped cross-validation does not cure target-dependent feature construction. G1/G2/G3/G7 are inherited context codes;G6 is a direct code filter. No programmatic target dependency was found in their transformation, but retrospective coding was not blinded.

Other important differences from the written protocol:

- Candidate model selection, feature-group ranking, and one-standard-error subset selection reuse the evaluation corpus; no implemented nested outer validation was found.
- Full data provide the encoding vocabulary and class-support filters in the original code.
- Stability analysis repeats groupedCV20 times. Its bootstrap resamples repeat-mean scores, not independent papers. These intervals are split-resampling summaries, not paper-population confidence intervals.
- Held-out permutation occurs at row level, potentially disrupting contextual configurations within papers. Drop-group changes and permutations are not causal effects.
- Positive contributions are normalized into weights; zero/negative changes are truncated. Large weights can arise when all other contributions are small. Weight magnitudes are not proportions of causal influence.
- Context association tables apply Fisher tests to dependent chain/instance rows, thenBHadjustment. BHdoes not repair clustered-observation dependence. Treat conditional proportions/lifts as descriptive, not confirmatory inferential evidence.

Existing noG4 sensitivity already weakens dimension prediction: expandedLRmacroF1=.1326,RF=.1118,frequencybaseline=.1026(single groupedCV). That version still uses target-influenced G5. Original selected-feature recommendations and 95%interval labels should not be carried into a claim of validated recommendation effectiveness.

## 7. Leakage-reduced supplementary analysis

New results reside in `corrective_analysis/`, with runnable `run_corrective_analysis.py`, `analysis_protocol.json`, task/class support tables, individual repeat metrics, primary out-of-fold predictions, and per-split overlap checks. Original outputs are preserved.

A fixed L2 logistic regression(C=1,balanced class weights,lbfgs,max_iter 5000) was chosen before inspecting the new results. G4 and recodedG5 are excluded; G5 uses the original identity-based codes, which is a different taxonomy and explicitly a sensitivity specification. G1/G2/G3/G6/G7 remain as recorded. Encoding is fitted within each training fold. Ten shuffled StratifiedGroupKFold repetitions keep all paper rows together;seeds 20261029–20261038. Classes require≥5 records/≥3 papers; tasksrequire≥30 recordsand≥2 classes. No feature subset or model is selected from these results. Metrics pool out-of-fold predictions across each entire repeat and include all retained target labels in macroF1, avoiding variable-label fold averaging. SDand ranges describe split variation only. Equal-paper-weighted score sensitivities are also exported; training remains record-based.

| Expanded task | Records / papers / classes | Frequency baseline F1 | Context only F1 | Known evidence only F1 | Context + known evidence F1 |
|---|---|---:|---:|---:|---:|
| Perceived-effect dimension |183/43/5|.1024|.1799|NA|NA|
| Subjective indicator |124/31/13|.0171|.0838|.3153|.3636|
| Tool class |210/43/5|.1302|.3260|.2605|.3000|

Dimension context-only splitSD=.0159;indicatorcombined=.0090;toolcombined=.0121. Corresponding top 2 accuracies are.4650,.7452,.5610. Main-screen indicator prediction remains unestimated:only 13 supported records from 8 papers in 2 classes. These results should not be directly subtracted from older model tables as a pure leakage effect: models, encoding, G5 definition, split seeds, and metric pooling differ.

Drop-group comparisons are exploratory. Expanded indicator prediction loses.0263 macroF1 on average when G2 is removed, positive in 10/10 splits;expandedtoolprediction loses.0401 whenG1 is removed, positive 10/10. RemovingG7 improves allthreefull specifications on average and in 10/10 splits. These results do not reproduce the prior claim thatG7 should be a learned tool-recommendation priority. No normalized “influence weights” or population confidence intervals were generated. The seven-standard input-screen uncertainty still applies; this analysis reduces a specific leakage mechanism, not all measurement bias.

Equal-paper-weighted scoring is a material sensitivity: for expanded indicator prediction, known-dimension-only macro-F1 is .3207 and context-plus-known-evidence is .3047, reversing their record-weighted order (.3153 versus .3636). Therefore the apparent incremental contextual benefit is not stable to the unit-weighting convention. Expanded dimension prediction has paper-balanced macro-F1 .1541 versus .1149 for the prior baseline, but paper-balanced accuracy .1964 versus .4032; improved macro-F1 is not across-the-board predictive superiority. All 230 corrective train/test splits have zero paper overlap and no absent training classes.

## 8. RQ4: implementation versus recommendation claims

The current supplemental policy file selects G4+G1 for dimensions,G4+G2+G6 for indicators,andG1+G7 for tools. The report explicitly says the existing website was not automatically overwritten. Do not describe that policy as deployed unless the actual website data/build are verified. The older and newer selected-label Jaccards are.50,.25,.50;their ranking correlations are below.80. RQ1 stability does not establish recommendation stability.

The existing weighted progressive-disclosure prototype can be discussed as a design translation or research demonstrator with traceable literature examples. Its scores are not established probabilities of appropriateness, evidence of measurement validity, or causal estimates of contextual influence. The corrected analysis does not validate its learned priorities. A defensible manuscript presents a transparency-first evidence browser/recommender architecture and makes the absence of prospective user evaluation, independent expert adjudication, calibration assessment, and external validation explicit. It should not claim demonstrated improvement in evaluation quality or an optimal tool-selection policy.

## Manuscript decisions supported by this audit

1. Preserve the 125-paper corpus and explicitly distinguish 95 candidate-evidence papers and 71 mapped-evidence papers.
2. Retain RQ1 descriptive maps with exact record/instance denominators and date-convention sensitivity.
3. Correct A3NAto 40;name allsevenratings provisional operational reporting-support screens.
4. Disclose automated extraction, screening pilot scope, recalculated kappas, and lack of independent coding validation.
5. Present original RQ3 weights only as diagnostic/superseded exploratory results;prefer the leakage-reduced conditional prediction analysis, without causal language.
6. Present RQ4 as a transparent prototype/design contribution, not a validated recommendation system.
7. Mark the manuscript as requiring source-specific human criterion validation and complete search-log reconciliation before submission. No further human audit was performed during this drafting task.

All 125 Crossref records were retrieved successfully. Under the Crossref published-date convention, the 2022-2026 counts are 11, 11, 28, 33, and 42. Six screening-year assignments differ from that convention; none of the Crossref published dates falls after 25 September 2026. The catalogue preserves all date fields to make this sensitivity reproducible.
