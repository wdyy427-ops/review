# Literature verification and positioning notes

Verified on 29 October 2026. Bibliographic data and claim boundaries are stored in `references_verified.json`; citation keys below match that file. This is an editorial evidence memo, not a claim that all references belong to the screened review corpus.

## Requested TOCHI structural reference

Lee, Starner, Kunze, Kosch, Pospelova, and Woo (2026), *NASA-Task Load Index in CHI: A Comprehensive Review and Subscale Meta-Analysis with Implementation Guidelines*, TOCHI 33(5), Article 52, 38 pages, published 7 October 2026. [Publisher](https://doi.org/10.1145/3837858).

The article progresses from introduction and background through research approach, empirical investigations, implementation guidelines, toolkit, and conclusion. It differentiates a broad implementation review from a narrower quantitative analysis. Its toolkit translates observed problems into implementation support. The useful architectural precedent is therefore evidence synthesis → targeted analysis → practical guidance → accessible tool. Our review should retain separate RQ sections and describe its own association analysis, rather than borrowing the source's psychometric claims or calling coded practice frequencies a meta-analysis.

Recommended manuscript architecture, independently tailored to this project:

1. Introduction, ending with RQs and four contributions.
2. Background and Related Work: Perceived Effects and Subjective Evaluation; AI-assisted design and co-creativity; measurement and evaluation evidence; positioning against existing reviews.
3. Research Approach and Methodology: scope; search and screening; evidence model; coding and reliability; seven-standard appraisal; descriptive and association analyses; recommender derivation.
4. RQ1: Evidence Landscape, distinguishing paper, case and evidence-record denominators.
5. RQ2: Reported Evidence Quality, with the publication-based meaning of each judgment.
6. RQ3: Associations between Evaluation Context and Evidence Choices, with group-aware validation and sensitivity analyses.
7. RQ4: Progressive Disclosure Recommender, explaining the evidence trail, abstention and limits.
8. Discussion: conceptual contribution; practical recommendations; limitations and research agenda.
9. Conclusion; data/code availability; references; appendices.

## Novelty must acknowledge existing reviews

| Citation key | Relevant existing contribution | Appropriate positioning |
|---|---|---|
| frich2019 | Maps creativity support tools in HCI. | Builds on the broader CST landscape while concentrating on AI-assisted design workflows. |
| remy2020 | Reviews evaluation of creativity support tools and makes evaluation recommendations. | Extends evaluation synthesis through linked Perceived Effects, indicators, tools and reported evidence quality. |
| cox2025 | Reviews 173 CST evaluations and the distribution of outcome measures. | Goes beyond a list of outcome measures by preserving context and evidence linkages. |
| rezwana2023 | Models interaction in human–AI co-creative systems using COFI. | Uses AI-function and interaction context as explanatory descriptors, not as an alternative interaction framework. |
| zhang2025 | Synthesizes agency and collaboration strategies in human–AI co-creation. | Connects context to evidence choices; does not claim first mapping of agency or collaboration. |
| ahsan2026 | Reviews creativity measurement and evaluative methods in human–AI co-creativity. | Treats creativity as one part of a broader Perceived Effects space and appraises reported evaluation evidence. |

**Recommended gap wording:** Existing syntheses have mapped creativity-support tools, interaction patterns, and evaluation measures. A complementary need is to examine how Perceived Effects are connected to subjective indicators and tools within particular evaluation contexts, how well those connections are supported in published reports, and how this evidence can inform future evaluation planning. The manuscript investigates this need; it should not assert that subjective evaluation has never been systematically reviewed.

The Ahsan paper appeared on 1 October 2026 and belongs in contextual related work even if it postdates this review's search cutoff. Such a citation does not silently extend the screened corpus. The Zhang publisher record notes a June 2026 corrigendum; use the corrected article.

## Definition and inferential boundaries

- `okoso2025` provides a descriptive use of Perceived Effects in recommender explanations: people's interpretations and reactions, operationalized through several explanation goals. This is evidence of disciplinary usage, not a universal formal definition.
- A defensible introductory formulation is: **“Perceived Effects refer to the effects of a system, feature, or intervention as experienced, interpreted, and judged by people and elicited through Subjective Evaluation.”** Treat this as a literature-grounded synthesis. The phrase “elicited through” avoids implying that effects exist only during evaluation.
- If the user's preferred wording “during Subjective Evaluation” is retained, explain subsequently that evaluation elicits reports or judgments about effects that may occur before, during or after interaction.
- “Subjective” characterizes the evidential basis of the judgment; it does not mean unstructured, unquantifiable or scientifically inferior. A qualitative interview and a standardized numerical scale can both yield subjective evidence.
- Human involvement alone does not make a measure a Perceived Effect. Manual counting, factual coding, demographic description and task-completion logs remain conceptually different.
- A preference criterion, requirement or model calibration label can contribute to evaluating Perceived Effects, but the review must document the specific effect claim to which it connects. Process inclusion is not sufficient evidence of that connection.
- Human judgments about output properties, experiences of interaction, and inferred causal consequences should remain distinguishable. “Perceived effect” does not itself establish a causal effect of AI.

## Framework attribution and citation details

- `kidder2024`: CDC Table 7 explicitly aligns construct/concept, indicator and measure/metric, alongside an evaluation question, design, data source and expectation. The mapping Perceived Effects → subjective indicators → tools is this review's adaptation; a tool is a means of operationalization, not necessarily identical to a measure.
- `patton2008`: use the verified fourth edition of *Utilization-Focused Evaluation*. Intended users, intended uses and context inform questions and methods. G1–G7 are the review's contextual coding framework, not seven canonical UFE variables.
- `yarbrough2011`: the correct first author is **Donald B. Yarbrough**. JCSEE's website gives the release year as 2010; AEA and book copyright bibliographies use 2011. Use one convention consistently; the JSON uses 2011. The third edition is the relevant source.
- Selected seven standards: U5 (relevance), A2 (valid interpretation), A3 (dependability), A4 (context documentation), A6 (design/analysis adequacy), A7 (reasoning traceability), E1 (evaluation documentation). These short labels are paraphrases; use codes in tables. The review assesses reported evidence under an adaptation, not overall compliance with all thirty standards.
- `page2021`: PRISMA supports transparent review reporting. It neither supplies a quality score nor proves that screening was exhaustive or duplicated. Missing search/protocol details must remain explicit author-completion items.
- `flake2020` and `cronbach1955`: a recognizable scale name is not sufficient validity evidence. Conversely, an undocumented procedure in the paper cannot automatically be declared absent in the original research.
- `roberts2017`: paper-grouped validation is justified by nested observations. `saito2015` supports PR metrics under label imbalance. `benjamini1995` supports multiplicity correction. None turns predictive weights into causal influence.

## Sources and verified references

The JSON contains 33 records. DOI metadata was obtained from the registry and corrected against primary text where needed: the CDC registry's group-author affiliations were malformed, and the Hart–Staveland chapter lacked author fields. Publisher/author sources establish content claims. Direct ACM opens sometimes returned HTTP 403; indexed publisher full text and author-hosted copies were used for inspection. All final citations should point to the canonical publication URL, with optional accessible manuscript links.

No quoted prose from the target TOCHI article has been reproduced. The proposed section architecture is original to this review. The separate Related Work draft uses only the keys in the verified bibliography and should be integrated with the audited corpus, not read as empirical results.

## Additional terminology anchors and verified corpus exemplars

- `schleyer2012`: TOCHI 19(1), Article 2, 26 pages, DOI 10.1145/2147783.2147785. Section 3.4, Claim 12 distinguishes actual and perceived effects on collaboration practices and outcomes, and discusses user perceptions of system characteristics and impacts. This supports a distinction between perceived and objectively assessed consequences; it does not supply a universal formal definition. [Primary text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3872832/).
- `ma2025`: *EyeDraw*, PACMHCI 9(1), GROUP17, 24 pages, DOI 10.1145/3701196. A survey and study of 24 drawing pairs explicitly concentrate on collaborators' own perceptions of shared gaze and voice communication. This is relevant terminology beyond AI. Shared gaze itself should not be described as AI assistance. [Author manuscript](https://jeffhuang.com/papers/EyeDraw_GROUP25.pdf).

| Corpus paper | Key | Concrete evaluative distinction supported by primary text |
|---|---|---|
| 37 | krajcer2026 | Thirty-five UX-design students provide task-specific confidence and process-experience judgments, while experts judge artifacts. The authors explicitly delimit single-item confidence proxies and two-week observations. |
| 58 | hatfield2025 | Twenty-two textile, fashion and product designers examine AiLoupe's support for material sourcing, where sensory information and workflow experience matter. |
| 75 | wu2024 | A survey with 211 responses evaluates knitted-textile images using style, creativity, fashionability and purchase-intention judgments. These are distinct from manufacturing or purchase outcomes. |
| 85 | chen2024 | MemoVis evaluates fourteen feedback providers and eight participants with 3D-design experience separately; creating feedback and interpreting reference images involve different evaluation roles. |
| 103 | sun2024 | Haisor's scene rankings address rationality and human affordance, supplementing geometric metrics. Rendered-scene judgments do not demonstrate actual residential experience. |
| 120 | ashtari2022 | Two perceptual studies, with 100 participants each, use reference-style resemblance choices. The evaluation criterion is fidelity to a style, rather than unrestricted aesthetic preference. |

MemoVis has a bibliographic version discrepancy: the author preprint prints placeholder Article 1 and has 45 pages; the published record is TOCHI 31(5), Article 67, 41 pages. The JSON preserves final publication metadata and points to the accessible preprint as content evidence. This distinction should not be hidden.

Editorial implication: these cases make the G4–G6 distinction concrete. The person operating an AI tool, the person interpreting its output, and the person envisioned as a future beneficiary need not coincide. The review should preserve those roles instead of treating all human participants as equivalent end users.
