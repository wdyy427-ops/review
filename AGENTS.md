# AGENTS.md

本文件适用于整个仓库，供后续 Codex 或其他编码代理理解项目、选择正确数据源并安全修改文件。

## Project summary

This repository supports the systematic literature review **Subjective Evaluation of Perceived Effects in AI-Assisted Design Workflows**. The study maps evaluation dimensions, subjective indicators, and tools; appraises reported evaluation practices; analyzes their relationships with seven contextual factors; and translates the findings into an evidence-based evaluation operationalization recommender.

## Source-of-truth hierarchy

1. Use `outputs/rq_review_20261024/supplement_enhanced_v2/03_revised_results/` for the current analytical data.
2. Use `outputs/manuscript_20261029/audit_data.md` for verified denominators, known discrepancies, methodological limitations, and manuscript decisions.
3. Use `outputs/rq_review_20261024/protocol.md` for the coding taxonomy, field definitions, audit anchors, and planned modeling logic.
4. Treat `outputs/最终整合文档_20261027/`, `baseline_v1_snapshot/`, and reports based on 158 cases or 490 records as historical versions unless the user explicitly requests a historical comparison.
5. When two files disagree, do not silently choose or overwrite a value. Trace the value to the machine-readable data and record the discrepancy.

The current headline counts are 125 papers, 159 evaluation cases, 514 candidate evidence records, 460 dimension-mapped records, 454 indicator-mapped records, 624 tool instances, and 3,598 criterion-level audit rows.

## Terminology to preserve

- Preserve the title terms **Subjective Evaluation**, **Perceived Effects**, and **AI-Assisted Design Workflows** when editing manuscript text.
- Use **evaluation dimensions**, **subjective indicators**, and **tools** for the three progressive levels of evaluation operationalization.
- Use the contextual labels G1–G7 consistently: evaluation purpose, design domain, design stage, evaluation object, evaluators, target users, and AI function.
- Distinguish papers, evaluation cases, candidate evidence records, mapped records, and tool instances. Never interchange their denominators.
- Distinguish reported support from demonstrated methodological quality. JCSEE-inspired statuses are researcher-defined operational classifications, not official JCSEE certification.
- Describe model results as predictive or associational, not causal. Describe the recommender as a research prototype unless new validation supports a stronger claim.

## Safe working rules

- Inspect `git status` before editing and preserve unrelated user changes.
- Prefer text sources and machine-readable CSV/JSON files over manually copying values from DOCX, PDF, screenshots, or rendered tables.
- Do not modify original screening workbooks, full-text PDFs, or frozen baseline files in place. Write corrected or derived outputs to a clearly named new location.
- Do not regenerate all outputs merely to change one document. Run the smallest relevant script and verify its affected artifacts.
- Do not delete, rename, or bulk-move research data without explicit user authorization.
- Do not claim that automated or AI-assisted coding was independently human validated unless an actual validation record supports that statement.
- Never fabricate citations, DOI values, search logs, reliability statistics, or missing methodological details.
- Keep literal status values such as `NA` from being parsed as missing data when loading CSV files; for pandas, use `keep_default_na=False` where applicable.
- Group train/test splits by paper ID for modeling. Do not allow rows from the same paper to cross training and test partitions.
- Check for target leakage before interpreting contextual-factor contribution, especially any feature derived from dimension or indicator labels.

## File and artifact policy

The following content is intentionally excluded from ordinary Git synchronization and must remain excluded:

- full-text article corpora and publisher PDFs;
- local LLM weights, CUDA libraries, and downloaded runtimes;
- `_deps/`, `node_modules/`, `.vite-service/`, virtual environments, caches, and build products;
- temporary files, QA page renders, logs, PID files, and duplicate archives.

Do not force-add ignored files unless the user explicitly requests it and the licensing, privacy, and GitHub size implications have been checked.

## Validation expectations

For data or analysis changes:

1. Verify row counts, unique identifiers, foreign-key links, allowed codes, and missing-value handling.
2. Report the exact analysis unit and denominator for every table or figure.
3. Compare changed results against the prior output and explain material differences.
4. Preserve scripts, parameters, seeds, and source paths needed for reproduction.

For manuscript changes:

1. Check every numerical statement against the current machine-readable result.
2. Keep claims within the limits documented in `audit_data.md`.
3. Rebuild the DOCX/PDF only when requested or when source changes must be delivered as rendered artifacts.
4. Visually inspect affected figures, tables, pagination, and references after rebuilding.

For recommender changes:

1. Keep recommendations traceable to supporting papers and context configurations.
2. Separate literature frequency, model score, and evidence quality in the interface and documentation.
3. Do not present normalized feature contributions as causal weights or probabilities of appropriateness.
4. Verify that the deployed data and displayed methodology match the current analysis rather than an older snapshot.

## Git collaboration

- Pull with `git pull --rebase origin main` before starting work on another machine.
- Make focused commits using prefixes such as `screening:`, `coding:`, `analysis:`, `figures:`, `manuscript:`, or `recommender:`.
- Avoid simultaneous edits to the same DOCX/XLSX file on two hosts because Git cannot merge binary Office files reliably.
- Before pushing, confirm that no full-text PDFs, model files, dependency trees, secrets, or unrelated generated artifacts are staged.

