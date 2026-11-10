from __future__ import annotations

import json

import pandas as pd

from config import ROOT


ENHANCED = ROOT / "supplement_enhanced_v2"
DATA = ENHANCED / "03_revised_results"
RQ3DATA = ENHANCED / "06_RQ3"
OUT = ROOT / "site_g1_g7" / "dist"
OUT.mkdir(parents=True, exist_ok=True)

LABELS = {
    "purpose": {
        "P1": "Value elicitation and criteria construction",
        "P2": "Model supervision, calibration, and proxy objectives",
        "P3": "Formative feedback and iterative guidance",
        "P4": "Summative validation and comparison",
    },
    "domain": {
        "D1": "Visual communication design",
        "D2": "Industrial and product design",
        "D3": "Fashion and textile design",
        "D4": "Interior and spatial design",
        "D5": "Service design",
        "D6": "UI/UX and interaction design",
    },
    "stage": {
        "S1": "Research",
        "S2": "Ideation",
        "S3": "Prototyping and testing",
        "S4": "Implementation",
    },
    "object": {
        "O1": "Design outcome or solution",
        "O2": "Design task or workflow",
        "O3": "AI-assisted design system or interface",
        "O4": "Human state or capability",
        "O5": "Human–AI collaborative relationship",
    },
    "evaluator": {
        "V1": "Design-task performer",
        "V2": "User of the design outcome",
        "V3": "External domain expert",
        "V4": "General public or non-target population",
        "V5": "Internal researcher or system developer",
    },
    "target_user": {
        "U1": "Professional design practitioners",
        "U2": "Design learners or novice designers",
        "U3": "Non-professional creators",
    },
    "ai_function": {
        "F1": "Need identification",
        "F2": "Knowledge retrieval",
        "F3": "Solution generation",
        "F4": "Prototype implementation",
        "F5": "Evaluation and feedback",
        "F6": "Iterative optimization",
    },
    "dimension": {
        "A": "Design outcome quality",
        "B": "Design process quality",
        "C": "Designer cognition, affect, and capabilities",
        "D": "Human–AI interaction experience",
        "E": "Social and contextual value",
    },
    "indicator": {
        "A1": "Novelty", "A2": "Aesthetic appeal", "A3": "Suitability",
        "A4": "Feasibility", "A5": "Fidelity", "A6": "Comprehensiveness",
        "B1": "Time efficiency", "B2": "Perceived workload", "B3": "Iteration efficiency",
        "B4": "Decision support", "B5": "Process continuity", "B6": "Handover efficiency",
        "C1": "Inspiration", "C2": "Knowledge acquisition", "C3": "Self-efficacy",
        "C4": "Engagement and immersion", "C5": "Enjoyment", "C6": "Reflection",
        "C7": "Fixation and dependence", "C8": "Capability expansion",
        "D1": "Ease of use", "D2": "Intention to use", "D3": "Sense of control",
        "D4": "Explainability", "D5": "Trust", "D6": "Agency",
        "D7": "Role and contribution fairness",
        "D8": "Communication, coordination, conflict, and shared understanding",
        "E1": "End-user experience and acceptance",
        "E2": "Fit with needs, contexts, and populations",
        "E3": "Professional and organizational fit",
        "E4": "Cultural, social, and public value",
        "E5": "Ethics, fairness, bias, and inclusion",
        "E6": "Environmental and sustainability value",
        "E7": "Commercial, brand, and market value",
        "E8": "Long-term use, governance, and responsibility",
    },
    "tool": {
        "M1": "Named standardized scales",
        "M2": "Bespoke structured rating tools",
        "M3": "Qualitative verbal elicitation",
        "M4": "Non-scale structured questionnaires",
        "M5": "Analysis of existing perceptual material",
    },
}


def records(path):
    return pd.read_csv(path, keep_default_na=False).to_dict("records")


def main():
    chains = pd.read_csv(RQ3DATA / "evidence_chains_context_g1_g7.csv", keep_default_na=False)
    keep = [
        "paper_id", "eval_id", "chain_id", "title", "year", "domains", "stages",
        "ai_functions", "purposes", "objects_g4", "evaluators_g5", "target_users_g6",
        "claim_quote", "claim_summary", "construct_raw", "dimension_code", "indicator_code",
        "pages", "result_quote", "revised_quality_tier", "revised_quality_index",
        "model_eligible_main", "model_eligible_sensitivity",
    ]
    summary = json.loads((ENHANCED / "analysis_summary.json").read_text(encoding="utf-8"))["revised"]
    payload = {
        "summary": summary,
        "labels": LABELS,
        "toolLabels": LABELS["tool"],
        "chains": chains[keep].to_dict("records"),
        "instances": records(DATA / "measure_instances.csv"),
        "weights": records(RQ3DATA / "rq3_label_group_weights_stable.csv"),
    }
    data_js = "window.REVIEW_DATA=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    (OUT / "data.js").write_text(data_js, encoding="utf-8")
    (OUT / "data_thresholded.js").write_text(data_js, encoding="utf-8")

    html = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evidence-Based Evaluation Operationalization Recommender</title>
<style>
:root{--ink:#172e35;--muted:#65767b;--line:#d9e2e4;--mist:#ddf4f4;--cyan:#45bdd0;--mint:#63c3a6;--blue:#849bd0;--pink:#df83b6;--paper:#fff;--wash:#f7faf9;--warn:#fff9ea}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:#fff;font-family:Aptos,Inter,"Segoe UI",Arial,sans-serif;line-height:1.48}
button,select,input{font:inherit}.topbar{height:72px;background:var(--mist);border-bottom:1px solid #c9e5e6;display:flex;align-items:center;padding:0 32px;position:sticky;top:0;z-index:10;overflow:hidden}.topbar:after{content:"";position:absolute;right:-20px;top:-55px;width:370px;height:180px;opacity:.42;background:repeating-radial-gradient(ellipse at 50% 100%,transparent 0 9px,#70cbd5 10px 11px,transparent 12px 17px);pointer-events:none}.brand{font-size:20px;font-weight:750;letter-spacing:-.02em;z-index:1}.nav{display:flex;align-items:center;gap:42px;margin-left:64px;height:100%;z-index:1}.nav a{height:100%;display:flex;align-items:center;color:var(--ink);text-decoration:none;font-size:14px;border-bottom:4px solid transparent;padding:4px 2px 0}.nav a.active{font-weight:700;border-color:var(--cyan)}.lang{margin-left:auto;font-size:13px;z-index:1}.app-view{display:none}.app-view.active{display:block}.shell.app-view.active{display:grid}.shell{grid-template-columns:296px minmax(0,1fr);min-height:calc(100vh - 72px)}
.sidebar{border-right:1px solid var(--line);padding:24px 24px 40px 30px;background:#fff;position:sticky;top:72px;height:calc(100vh - 72px);overflow:auto}.side-title{font-size:14px;margin:0 0 13px}.path{list-style:none;margin:0;padding:0}.path button{width:100%;border:0;background:none;text-align:left;padding:10px 10px 10px 30px;position:relative;color:var(--ink);cursor:pointer;border-left:1px solid #d9e1e3}.path button:before{content:"";position:absolute;left:10px;top:16px;width:10px;height:10px;border-radius:50%;background:var(--stage);box-shadow:0 0 0 3px #fff}.path button.active{background:#dff4f6;border-right:7px solid var(--cyan);font-weight:700}.path button.locked{opacity:.45;cursor:not-allowed}.path small{display:block;color:var(--muted);font-weight:400;margin-top:2px;line-height:1.35}.side-rule{border:0;border-top:1px solid var(--line);margin:22px 0}.scope label{display:block;font-size:12px;margin-bottom:6px;color:var(--muted)}.scope select{width:100%;padding:9px 10px;border:1px solid #cbd7da;background:#fff}.corpus{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px}.corpus b{display:block;font-size:20px}.corpus span{font-size:11px;color:var(--muted)}.method-note{font-size:12px;color:var(--muted);margin:10px 0 0}
.main{position:relative;min-width:0;background:linear-gradient(90deg,#fff 0,#fff 72%,#fbfefe 100%)}.intro{padding:35px 58px 27px;border-bottom:1px solid var(--line);position:relative;overflow:hidden}.intro:after{content:"";position:absolute;right:-80px;bottom:-130px;width:520px;height:260px;opacity:.17;background:repeating-radial-gradient(ellipse at 20% 50%,transparent 0 11px,#45bdd0 12px 13px,transparent 14px 22px);pointer-events:none}.intro h1{font-size:30px;letter-spacing:-.035em;margin:0 0 8px;max-width:760px}.intro p{margin:0;max-width:760px;color:var(--muted);font-size:14px}.workspace{padding:30px 58px 70px;max-width:1220px}.stage-head{display:flex;gap:14px;align-items:flex-start;border-bottom:1px solid var(--line);padding-bottom:18px}.stage-dot{width:14px;height:14px;border-radius:50%;background:var(--stage);margin-top:7px;flex:none}.stage-head h2{font-size:21px;margin:0 0 5px}.stage-head p{margin:0;color:var(--muted);font-size:13px;max-width:780px}.chosen{display:flex;flex-wrap:wrap;gap:7px;margin:15px 0 0}.chosen span{border:1px solid #bcdfe3;background:#effafb;padding:5px 9px;font-size:11px}.input-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 26px;margin-top:23px;border-top:1px solid var(--line)}.input-row{padding:18px 0;border-bottom:1px solid var(--line)}.input-row:nth-child(odd){padding-right:8px}.input-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:9px}.input-head h3{font-size:14px;margin:0}.robust{font-size:10px;background:#dff3ed;color:#267560;padding:3px 7px;border-radius:999px}.weight{font-size:11px;color:var(--muted)}.weight i{display:inline-block;width:65px;height:4px;background:#e4ecee;margin-left:6px;vertical-align:middle;position:relative}.weight i:after{content:"";display:block;width:var(--w);height:100%;background:var(--stage)}.field label{display:block;font-size:11px;color:var(--muted);margin-bottom:5px}.field select{width:100%;padding:10px 11px;border:1px solid #cbd7da;background:#fff;color:var(--ink)}.field select:focus,.action:focus,.path button:focus{outline:3px solid #45bdd044;outline-offset:2px}.actions{display:flex;align-items:center;gap:10px;margin-top:22px}.action{border:1px solid var(--ink);background:var(--ink);color:#fff;padding:10px 16px;cursor:pointer;font-weight:700}.action.secondary{background:#fff;color:var(--ink)}.warning{margin-top:17px;border-left:3px solid #e6b74d;background:var(--warn);padding:10px 12px;font-size:12px;color:#6b5520}.results{margin-top:35px}.results-head{display:flex;justify-content:space-between;align-items:end;border-bottom:1px solid var(--line);padding-bottom:10px}.results-head h3{margin:0;font-size:18px}.results-head span{font-size:11px;color:var(--muted)}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:18px}.card{border:1px solid var(--line);border-top:6px solid var(--stage);background:#fff}.card-main{padding:17px 18px}.card button{border:0;background:none;padding:0;text-align:left;cursor:pointer;color:var(--ink)}.card h4{font-size:17px;line-height:1.35;margin:0 0 8px}.chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.chip{font-size:10px;padding:3px 7px;background:#eef4f5;color:#456067}.match{display:flex;align-items:center;gap:9px;color:var(--muted);font-size:11px;margin-top:10px}.bar{height:5px;flex:1;background:#e7edef}.bar i{display:block;height:100%;background:var(--stage)}details{border-top:1px solid var(--line);padding:11px 18px;font-size:11px}summary{cursor:pointer;font-weight:700}.evidence{color:#455a61;margin-top:9px;max-height:160px;overflow:auto}.empty{border:1px dashed #aebfc3;padding:24px;color:var(--muted)}.next{margin-top:14px;color:#267560;font-size:12px}.footer-note{padding:20px 58px;border-top:1px solid var(--line);font-size:11px;color:var(--muted)}
.page-view{min-height:calc(100vh - 72px);background:#fff}.page-hero{padding:42px max(32px,calc((100vw - 1280px)/2));border-bottom:1px solid var(--line);background:linear-gradient(90deg,#f8fdfd 0,#fff 68%);position:relative;overflow:hidden}.page-hero:after{content:"";position:absolute;right:-50px;bottom:-150px;width:500px;height:280px;opacity:.16;background:repeating-radial-gradient(ellipse at 25% 45%,transparent 0 11px,#45bdd0 12px 13px,transparent 14px 22px)}.page-hero h1{font-size:34px;letter-spacing:-.04em;margin:0 0 8px}.page-hero p{max-width:760px;margin:0;color:var(--muted);font-size:14px}.page-body{max-width:1280px;margin:auto;padding:32px 32px 70px}.full-stats{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);margin-bottom:26px}.full-stats div{padding:17px 20px;border-right:1px solid var(--line)}.full-stats div:last-child{border-right:0}.full-stats b{display:block;font-size:27px}.full-stats span{font-size:12px;color:var(--muted)}.corpus-controls{display:grid;grid-template-columns:2fr repeat(4,1fr);gap:10px;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.corpus-controls input,.corpus-controls select{width:100%;min-width:0;border:1px solid #cbd7da;background:#fff;padding:9px 10px;color:var(--ink)}.section-heading{display:flex;justify-content:space-between;align-items:end;margin:28px 0 12px}.section-heading h2{font-size:20px;margin:0}.section-heading p{font-size:12px;color:var(--muted);margin:0}.dist-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}.dist-panel{border-top:5px solid var(--accent);padding-top:12px}.dist-panel h3{font-size:14px;margin:0 0 12px}.dist-row{display:grid;grid-template-columns:minmax(105px,1fr) 2fr 34px;gap:8px;align-items:center;margin:8px 0;font-size:11px}.dist-row span:first-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.dist-track{height:6px;background:#e8eff0}.dist-track i{display:block;height:100%;background:var(--accent)}.table-wrap{overflow:auto;border:1px solid var(--line)}.evidence-table{width:100%;border-collapse:collapse;min-width:1050px}.evidence-table th{position:sticky;top:0;background:#eef8f8;text-align:left;font-size:11px;padding:10px 12px;border-bottom:1px solid var(--line)}.evidence-table td{vertical-align:top;padding:12px;border-bottom:1px solid var(--line);font-size:11px}.evidence-table tr:last-child td{border-bottom:0}.study-title{font-size:12px;font-weight:700;line-height:1.35;margin-bottom:4px}.meta{color:var(--muted)}.table-code{display:block;margin-bottom:4px}.status{display:inline-block;padding:3px 7px;background:#edf3f4;color:#456067}.status.strict{background:#dff3ed;color:#267560}.status.expanded{background:#e9edf8;color:#50689a}.method-chain{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);margin-bottom:30px}.chain-step{position:relative;padding:20px;border-right:1px solid var(--line);min-height:122px}.chain-step:last-child{border-right:0}.chain-step:not(:last-child):after{content:"";position:absolute;right:-5px;top:30px;width:9px;height:9px;background:#fff;border-top:2px solid var(--cyan);border-right:2px solid var(--cyan);transform:rotate(45deg);z-index:1}.chain-step b{display:block;font-size:15px;margin-bottom:7px}.chain-step span{font-size:12px;color:var(--muted)}.method-grid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(300px,.75fr);gap:36px}.method-section{border-top:1px solid var(--ink);padding-top:13px;margin-bottom:30px}.method-section h2{font-size:19px;margin:0 0 8px}.method-section p,.method-section li{font-size:13px;color:#4e6268}.relationship-table{width:100%;border-collapse:collapse;margin-top:14px}.relationship-table th,.relationship-table td{text-align:left;padding:10px;border-bottom:1px solid var(--line);font-size:11px;vertical-align:top}.relationship-table th{background:#f0f8f8}.factor-list{display:flex;flex-wrap:wrap;gap:5px}.factor-list span{padding:3px 7px;background:#e6f4f2;color:#267560}.formula{border-left:5px solid var(--cyan);background:#f2fafa;padding:18px 20px;font-size:15px;line-height:1.55}.robust-pair{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line)}.robust-pair div{padding:16px}.robust-pair div+div{border-left:1px solid var(--line)}.robust-pair b{display:block;margin-bottom:5px}.method-note-box{background:var(--warn);border-left:3px solid #e6b74d;padding:14px;font-size:12px;color:#6b5520}.plain-list{padding-left:18px;margin:8px 0}.plain-list li{margin:7px 0}
.table-wrap{max-height:760px}.evidence-table th{z-index:1}
@media(max-width:1000px){.corpus-controls{grid-template-columns:repeat(2,1fr)}.corpus-controls input{grid-column:1/-1}.method-grid{grid-template-columns:1fr}}
@media(max-width:900px){.topbar{height:auto;min-height:72px;flex-wrap:wrap}.nav{order:3;width:100%;height:44px;margin-left:0;gap:28px}.shell{grid-template-columns:1fr}.sidebar{position:relative;top:0;height:auto;border-right:0;border-bottom:1px solid var(--line)}.path{display:grid;grid-template-columns:repeat(3,1fr)}.intro,.workspace,.footer-note{padding-left:24px;padding-right:24px}.cards{grid-template-columns:1fr}.page-view{min-height:calc(100vh - 116px)}.dist-grid{grid-template-columns:1fr}.method-chain{grid-template-columns:repeat(2,1fr)}.chain-step:nth-child(2){border-right:0}.chain-step:nth-child(-n+2){border-bottom:1px solid var(--line)}}
@media(max-width:600px){.topbar{padding:0 18px}.brand{font-size:15px;line-height:1.2;max-width:315px}.lang{display:none}.input-grid,.path{grid-template-columns:1fr}.corpus{grid-template-columns:repeat(4,1fr)}.workspace{padding-top:22px}.intro h1,.page-hero h1{font-size:25px}.actions{align-items:stretch;flex-direction:column}.action{width:100%}.page-hero,.page-body{padding-left:24px;padding-right:24px}.full-stats{grid-template-columns:repeat(2,1fr)}.full-stats div:nth-child(2){border-right:0}.full-stats div:nth-child(-n+2){border-bottom:1px solid var(--line)}.corpus-controls{grid-template-columns:1fr}.method-chain{grid-template-columns:1fr}.chain-step{border-right:0;border-bottom:1px solid var(--line)}.chain-step:last-child{border-bottom:0}.chain-step:after{display:none}.robust-pair{grid-template-columns:1fr}.robust-pair div+div{border-left:0;border-top:1px solid var(--line)}}
</style></head><body>
<header class="topbar"><div class="brand">Evidence-Based Evaluation Operationalization Recommender</div><nav class="nav"><a data-view="recommender" href="#recommender">Recommender</a><a data-view="corpus" href="#corpus">Corpus</a><a data-view="method" href="#method">Method</a></nav><div class="lang">EN</div></header>
<div class="shell app-view" id="page-recommender"><aside class="sidebar"><h2 class="side-title">Evaluation pathway</h2><div id="path"></div><hr class="side-rule"><section><h2 class="side-title">Review corpus</h2><div class="corpus" id="corpusStats"></div></section><hr class="side-rule"><section class="scope"><label for="tier">Evidence scope</label><select id="tier"><option value="auto">Auto: strict before expanded</option><option value="main">Strict analytical subset</option><option value="expanded">Expanded analytical subset</option></select></section><section><p class="method-note">Only factors supported by both group-deletion retraining and test-set permutation enter the recommender. Weights guide matching; they are not causal effects.</p></section></aside>
<main class="main"><section class="intro"><h1>Plan a context-sensitive subjective evaluation</h1><p>Move from evaluation dimensions to subjective indicators and tools. Confirm each layer before the next set of contextual inputs is disclosed.</p></section><section class="workspace" id="workspace"></section><footer class="footer-note">Built from 125 papers, 159 evaluation cases, 514 candidate evidence records, and 624 tool instances. Recommendations expose supporting records and should be interpreted with construct validity and study context.</footer></main></div>

<section class="page-view app-view" id="page-corpus"><header class="page-hero"><h1>Corpus and evidence map</h1><p>Inspect the studies and operationalization records behind the recommendations. Filter the corpus by study context or follow a record from evaluation dimension to subjective indicator and tool class.</p></header><div class="page-body"><div class="full-stats" id="corpusStatsFull"></div><div class="corpus-controls"><input id="corpusSearch" type="search" placeholder="Search study title, paper ID, dimension, or indicator"><select id="filterDomain" aria-label="Filter by design domain"></select><select id="filterStage" aria-label="Filter by design stage"></select><select id="filterDimension" aria-label="Filter by evaluation dimension"></select><select id="filterTool" aria-label="Filter by tool class"></select></div><div class="section-heading"><h2>Corpus profile</h2><p>Counts refer to evaluation-evidence records, not independent studies.</p></div><div class="dist-grid" id="corpusDistributions"></div><div class="section-heading"><h2>Evidence records</h2><p id="corpusCount"></p></div><div class="table-wrap"><table class="evidence-table"><thead><tr><th>Study</th><th>Context</th><th>Evaluation dimension</th><th>Subjective indicator</th><th>Tool classes</th><th>Evidence status</th></tr></thead><tbody id="corpusRows"></tbody></table></div></div></section>

<section class="page-view app-view" id="page-method"><header class="page-hero"><h1>How recommendations are produced</h1><p>The recommender translates the review corpus into a progressive operationalization pathway. It exposes only contextual relationships that remained positive in two complementary robustness tests.</p></header><div class="page-body"><div class="method-chain"><div class="chain-step"><b>Evaluation question</b><span>Defines what the evaluation seeks to establish in a specific design context.</span></div><div class="chain-step"><b>Evaluation dimension</b><span>Organizes the relevant perceived effects into a conceptual domain.</span></div><div class="chain-step"><b>Subjective indicator</b><span>Specifies the attribute through which the dimension is assessed.</span></div><div class="chain-step"><b>Tool</b><span>Elicits and records judgments about the selected indicator.</span></div></div><div class="method-grid"><div><section class="method-section"><h2>Progressive contextual routing</h2><p>Each operationalization layer uses a different subset of contextual factors. Later inputs are disclosed only after the preceding component has been selected.</p><table class="relationship-table"><thead><tr><th>Recommended component</th><th>Selected model</th><th>Dual-method robust contextual factors</th></tr></thead><tbody id="methodRelationships"></tbody></table></section><section class="method-section"><h2>Model selection</h2><p>Four classifiers were compared using paper-grouped repeated cross-validation. The model with the highest mean Macro-F1 was retained for each prediction target.</p><table class="relationship-table"><thead><tr><th>Prediction target</th><th>Retained model</th><th>Mean Macro-F1</th></tr></thead><tbody><tr><td>Evaluation dimensions</td><td>Random forest</td><td>0.500</td></tr><tr><td>Subjective indicators</td><td>Random forest</td><td>0.372</td></tr><tr><td>Tool classes</td><td>L2 multinomial logistic regression</td><td>0.265</td></tr></tbody></table></section><section class="method-section"><h2>Robustness gate</h2><div class="robust-pair"><div><b>Group-deletion retraining</b><span>Removes one complete contextual factor and retrains the model to test whether the remaining factors can compensate for its information.</span></div><div><b>Test-set permutation</b><span>Keeps the fitted model fixed and shuffles one factor in the test set to test dependence on its observed values.</span></div></div><p>A contextual factor enters the recommender only when the 95% bootstrap confidence intervals for both contribution estimates are above zero.</p></section></div><aside><section class="method-section"><h2>Matching and ranking</h2><div class="formula">Recommendation score = the weighted match between the specified context and supporting evidence records.</div><ul class="plain-list"><li>Weights are normalized conditional predictive contributions.</li><li>Evidence support is summarized by records, papers, and tool instances.</li><li>The strict subset is used first; the expanded subset is disclosed when strict support is sparse.</li><li>Users can inspect the studies supporting each candidate.</li></ul></section><section class="method-section"><h2>Evidence subsets</h2><p><b>Strict analytical subset</b><br>Records meeting the primary rigor and model-eligibility requirements.</p><p><b>Expanded analytical subset</b><br>Additional records retained for sensitivity analysis and sparse configurations.</p></section><section class="method-section"><h2>Interpretation boundary</h2><div class="method-note-box">The recommender identifies patterns in the reviewed literature. Its weights are not causal effects, and a frequently supported choice is not automatically the most valid choice for every study. Construct definition, participant characteristics, and measurement quality still require expert judgment.</div></section></aside></div></div></section>
<script src="data.js"></script><script>
const D=window.REVIEW_DATA,L=D.labels,T=D.toolLabels;
const split=s=>String(s||'').split(';').filter(x=>x&&!['NR','NA','UNMAPPED'].includes(x));
const esc=s=>String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const short=(s,n=310)=>{s=String(s||'').replace(/\s+/g,' ').trim();return s.length>n?s.slice(0,n-1)+'…':s};
const groupLabels={G1:'Evaluation purpose',G2:'Design domain',G3:'Design stage',G4:'Evaluation object',G5:'Evaluators',G6:'Target users',G7:'AI function'};
const groupFields={G1:[['purposes','purpose']],G2:[['domains','domain']],G3:[['stages','stage']],G4:[['objects_g4','object']],G5:[['evaluators_g5','evaluator']],G6:[['target_users_g6','target_user']],G7:[['ai_functions','ai_function']]};
const targetName={dimension:'Evaluation dimensions',indicator:'Subjective indicators',tool:'Tools'};
const targetKey={dimension:'评价维度',indicator:'主观指标',tool:'测量工具类别'};
const stageTarget={1:'dimension',2:'indicator',3:'tool'};
const stageColor={dimension:'#63c3a6',indicator:'#849bd0',tool:'#df83b6'};
const state={stage:1,maxStage:1,answers:{},dimension:'',indicator:'',showResults:false,tier:'auto'};
function weightRows(target){return D.weights.filter(x=>x.analysis_tier==='扩展规范集'&&x.target===targetKey[target])}
function weightMap(target){const out={};weightRows(target).forEach(x=>out[x.feature_group.split('_')[0]]=+x.normalized_weight||0);return out}
function robustMap(target){const out={};weightRows(target).forEach(x=>out[x.feature_group.split('_')[0]]=+x.robust_positive===1);return out}
function orderedGroups(target){const w=weightMap(target),r=robustMap(target);return Object.keys(groupFields).filter(g=>r[g]).sort((a,b)=>w[b]-w[a])}
function fieldMatch(c,col,val){return split(c[col]).includes(val)}
function rowScore(c,target){const w=weightMap(target);let numerator=0,denominator=0;for(const g of orderedGroups(target)){const answered=groupFields[g].filter(([col])=>state.answers[col]);if(!answered.length)continue;const matched=answered.filter(([col])=>fieldMatch(c,col,state.answers[col])).length;denominator+=w[g];numerator+=w[g]*(matched/answered.length)}return denominator?numerator/denominator:1}
function sourceRows(mode){return D.chains.filter(c=>+(mode==='main'?c.model_eligible_main:c.model_eligible_sensitivity)===1)}
function summarize(rows,target,filterFn=()=>true){const map={};for(const c of rows.filter(filterFn)){const code=target==='dimension'?c.dimension_code:c.indicator_code;const labels=target==='dimension'?L.dimension:L.indicator;if(!labels[code])continue;const s=rowScore(c,target);if(s<=0)continue;const x=map[code]??={code,label:labels[code],score:0,chains:new Set(),papers:new Set(),rows:[]};x.score+=s;x.chains.add(c.chain_id);x.papers.add(c.paper_id);x.rows.push({...c,_score:s})}return Object.values(map).map(x=>({...x,n:x.chains.size,p:x.papers.size})).sort((a,b)=>b.score-a.score||b.p-a.p||b.n-a.n)}
function chooseTier(target,filterFn=()=>true){if(state.tier!=='auto')return{tier:state.tier,rows:sourceRows(state.tier),fallback:false};const main=summarize(sourceRows('main'),target,filterFn);const enough=main.some(x=>x.p>=2&&x.n>=3);return enough?{tier:'main',rows:sourceRows('main'),fallback:false}:{tier:'expanded',rows:sourceRows('expanded'),fallback:true}}
function toolSummary(rows){const valid=new Set(rows.map(c=>c.chain_id)),byChain=new Map(rows.map(c=>[c.chain_id,c])),map={};for(const i of D.instances.filter(x=>valid.has(x.chain_id)&&T[x.tool_code])){const c=byChain.get(i.chain_id);if(!c)continue;const s=rowScore(c,'tool');if(s<=0)continue;const x=map[i.tool_code]??={code:i.tool_code,label:T[i.tool_code],score:0,instances:0,chains:new Set(),papers:new Set(),names:{},rows:[]};x.score+=s;x.instances++;x.chains.add(i.chain_id);x.papers.add(i.paper_id);if(i.instrument_name)x.names[i.instrument_name]=(x.names[i.instrument_name]||0)+1;x.rows.push({...c,_score:s})}return Object.values(map).map(x=>({...x,n:x.chains.size,p:x.papers.size,topNames:Object.entries(x.names).sort((a,b)=>b[1]-a[1]).slice(0,4)})).sort((a,b)=>b.score-a.score||b.p-a.p||b.instances-a.instances)}
function renderPath(){const desc={1:'Purpose + evaluation object',2:'Domain + object + target users',3:'Purpose + stage + object + AI function'};document.querySelector('#path').innerHTML=`<ol class="path">${[1,2,3].map(n=>{const target=stageTarget[n],locked=n>state.maxStage;return `<li><button data-stage="${n}" style="--stage:${stageColor[target]}" class="${n===state.stage?'active ':''}${locked?'locked':''}" ${locked?'disabled':''}>${targetName[target]}<small>${desc[n]}</small></button></li>`}).join('')}</ol>`;document.querySelectorAll('[data-stage]').forEach(b=>b.onclick=()=>{state.stage=+b.dataset.stage;state.showResults=false;render()})}
function chosen(){const bits=[];if(state.dimension)bits.push(`<span>Dimension: <b>${state.dimension} ${esc(L.dimension[state.dimension])}</b></span>`);if(state.indicator)bits.push(`<span>Indicator: <b>${state.indicator} ${esc(L.indicator[state.indicator])}</b></span>`);return bits.length?`<div class="chosen">${bits.join('')}</div>`:''}
function options(key,current){return `<option value="">Not specified / no restriction</option>${Object.entries(L[key]||{}).map(([k,v])=>`<option value="${k}" ${current===k?'selected':''}>${k}  ${esc(v)}</option>`).join('')}`}
function firstLabel(c,col,key){const code=split(c[col])[0];return code&&L[key]?.[code]?`${code} ${L[key][code]}`:'Not reported'}
function evidenceContext(c){return `Purpose: ${esc(firstLabel(c,'purposes','purpose'))}<br>Domain: ${esc(firstLabel(c,'domains','domain'))}<br>Stage: ${esc(firstLabel(c,'stages','stage'))}<br>Evaluation object: ${esc(firstLabel(c,'objects_g4','object'))}<br>AI function: ${esc(firstLabel(c,'ai_functions_g7','ai_function'))}`}
function modelName(model){if(model==='随机森林')return 'Random forest';if(model==='L2多项逻辑回归')return 'L2 multinomial logistic regression';return model||'Not available'}
function renderInputs(target){const w=weightMap(target);return `<div class="input-grid">${orderedGroups(target).map(g=>`<section class="input-row"><div class="input-head"><h3>${groupLabels[g]} <span class="robust">Dual-method robust</span></h3><span class="weight">Ranking weight ${(w[g]*100).toFixed(1)}% <i style="--w:${Math.max(2,Math.round(w[g]*100))}%"></i></span></div>${groupFields[g].map(([col,key])=>`<div class="field"><label>${state.answers[col]?'Inherited from an earlier layer':'Select '+groupLabels[g].toLowerCase()}</label><select data-answer="${col}">${options(key,state.answers[col]||'')}</select></div>`).join('')}</section>`).join('')}</div>`}
function evidenceCard(x,target,tier,maxScore){const samples=x.rows.sort((a,b)=>b._score-a._score).slice(0,3).map(c=>`<b>${esc(c.title||'Untitled study')} (${esc(c.year)})</b><br>${evidenceContext(c)}`).join('<br><br>');return `<article class="card" style="--stage:${stageColor[target]}"><div class="card-main"><button data-pick="${target}" data-code="${x.code}"><h4>${x.code}  ${esc(x.label)}</h4></button><div class="chips"><span class="chip">${tier==='main'?'Strict':'Expanded'} subset</span><span class="chip">${x.p} papers</span><span class="chip">${x.n} records</span>${x.instances?`<span class="chip">${x.instances} instances</span>`:''}</div><div class="match"><span>Matched support ${x.score.toFixed(1)}</span><span class="bar"><i style="width:${Math.max(4,Math.round(100*x.score/Math.max(.001,maxScore)))}%"></i></span></div></div><details><summary>Inspect supporting evidence</summary><div class="evidence">${samples||'No supporting record is available.'}</div></details></article>`}
function renderResults(target){let pick,items,filterFn=()=>true;if(target==='dimension'){pick=chooseTier(target);items=summarize(pick.rows,target).slice(0,5)}else if(target==='indicator'){filterFn=c=>c.dimension_code===state.dimension;pick=chooseTier(target,filterFn);items=summarize(pick.rows,target,filterFn).slice(0,8)}else{filterFn=c=>c.dimension_code===state.dimension&&c.indicator_code===state.indicator;pick=chooseTier('indicator',filterFn);const toolTier=state.tier==='auto'?(pick.fallback?'expanded':'main'):state.tier;pick={tier:toolTier,rows:sourceRows(toolTier),fallback:state.tier==='auto'&&toolTier==='expanded'};items=toolSummary(pick.rows.filter(filterFn)).slice(0,5)}const fallback=pick.fallback?'Strict-subset support was sparse, so this layer uses the expanded subset.':'';const title=target==='dimension'?'Choose a dimension to continue':target==='indicator'?'Choose an indicator to continue':'Recommended tool classes and evidence';return `<section class="results"><div class="results-head"><h3>${title}</h3><span>${fallback}</span></div>${items.length?`<div class="cards">${items.map(x=>evidenceCard(x,target,pick.tier,items[0]?.score||1)).join('')}</div>${target!=='tool'?'<p class="next">Selecting a candidate reveals the next layer.</p>':''}`:'<div class="empty">No sufficiently supported evidence matches the current conditions. Remove one restriction or record this configuration as an evidence gap.</div>'}</section>`}
function renderMain(){const target=stageTarget[state.stage],rows=weightRows(target),model=modelName(rows[0]?.selected_model);const descriptions={dimension:'Use evaluation purpose and evaluation object to route candidate dimensions.',indicator:'Use evaluation object, design domain, and target users within the confirmed dimension.',tool:'Use evaluation purpose, design stage, evaluation object, and AI function within the confirmed dimension and indicator.'};document.querySelector('#workspace').style.setProperty('--stage',stageColor[target]);document.querySelector('#workspace').innerHTML=`<header class="stage-head"><span class="stage-dot"></span><div><h2>${state.stage}. ${targetName[target]}</h2><p>${descriptions[target]} Selected model: ${esc(model)}. Only factors whose 95% bootstrap intervals were above zero in both robustness tests are shown.</p>${chosen()}</div></header>${renderInputs(target)}<div class="actions"><button class="action" id="recommend">Generate ${targetName[target].toLowerCase()}</button><button class="action secondary" id="clear">Clear this layer</button></div><div class="warning">The matching score uses only the dual-method robust factors shown above. Ranking weights are conditional predictive contributions, not causal importance.</div>${state.showResults?renderResults(target):''}`;document.querySelectorAll('[data-answer]').forEach(e=>e.onchange=()=>{if(e.value)state.answers[e.dataset.answer]=e.value;else delete state.answers[e.dataset.answer];state.showResults=false;render()});document.querySelector('#recommend').onclick=()=>{state.showResults=true;render()};document.querySelector('#clear').onclick=()=>{for(const g of orderedGroups(target))for(const [col] of groupFields[g])delete state.answers[col];state.showResults=false;render()};document.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>{if(b.dataset.pick==='dimension'){state.dimension=b.dataset.code;state.indicator='';state.stage=2;state.maxStage=Math.max(state.maxStage,2)}else if(b.dataset.pick==='indicator'){state.indicator=b.dataset.code;state.stage=3;state.maxStage=3}state.showResults=false;render();document.querySelector('#page-recommender').scrollIntoView({behavior:'smooth'})})}
function render(){renderPath();renderMain();document.querySelector('#tier').value=state.tier}
const statRows=[['Papers',D.summary.papers],['Evaluation cases',D.summary.evaluation_cases],['Evidence records',D.summary.evidence_chains],['Tool instances',D.summary.measure_instances]];
document.querySelector('#corpusStats').innerHTML=statRows.map(([label,value])=>`<div><b>${value}</b><span>${label.replace('Evaluation ','').replace('Evidence ','').replace(' instances','s')}</span></div>`).join('');
document.querySelector('#corpusStatsFull').innerHTML=statRows.map(([label,value])=>`<div><b>${value}</b><span>${label}</span></div>`).join('');
document.querySelector('#tier').onchange=e=>{state.tier=e.target.value;state.showResults=false;render()};

const toolsByChain={};for(const i of D.instances){if(!toolsByChain[i.chain_id])toolsByChain[i.chain_id]=new Set();if(T[i.tool_code])toolsByChain[i.chain_id].add(i.tool_code)}
const selectMarkup=(label,labels)=>`<option value="">${label}</option>${Object.entries(labels).map(([code,name])=>`<option value="${code}">${code}  ${esc(name)}</option>`).join('')}`;
document.querySelector('#filterDomain').innerHTML=selectMarkup('All design domains',L.domain);
document.querySelector('#filterStage').innerHTML=selectMarkup('All design stages',L.stage);
document.querySelector('#filterDimension').innerHTML=selectMarkup('All evaluation dimensions',L.dimension);
document.querySelector('#filterTool').innerHTML=selectMarkup('All tool classes',T);
const corpusEls=['corpusSearch','filterDomain','filterStage','filterDimension','filterTool'].map(id=>document.querySelector('#'+id));
function displayCode(code,labels){return labels[code]?`${code} ${labels[code]}`:'Not mapped'}
function recordStatus(c){if(+c.model_eligible_main===1)return['Strict','strict'];if(+c.model_eligible_sensitivity===1)return['Expanded','expanded'];return['Candidate','']}
function distribution(rows,col,labels){const counts={};for(const c of rows)for(const code of split(c[col]))if(labels[code])counts[code]=(counts[code]||0)+1;return Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([code,n])=>({label:`${code} ${labels[code]}`,n}))}
function renderDistribution(title,items,color){const max=Math.max(1,...items.map(x=>x.n));return `<section class="dist-panel" style="--accent:${color}"><h3>${title}</h3>${items.map(x=>`<div class="dist-row"><span title="${esc(x.label)}">${esc(x.label)}</span><span class="dist-track"><i style="width:${Math.round(100*x.n/max)}%"></i></span><b>${x.n}</b></div>`).join('')}</section>`}
function renderCorpus(){const q=document.querySelector('#corpusSearch').value.trim().toLowerCase(),domain=document.querySelector('#filterDomain').value,stage=document.querySelector('#filterStage').value,dimension=document.querySelector('#filterDimension').value,tool=document.querySelector('#filterTool').value;const rows=D.chains.filter(c=>{const toolCodes=[...(toolsByChain[c.chain_id]||[])];const searchable=[c.title,c.paper_id,c.dimension_code,c.indicator_code,L.dimension[c.dimension_code],L.indicator[c.indicator_code]].join(' ').toLowerCase();return(!q||searchable.includes(q))&&(!domain||split(c.domains).includes(domain))&&(!stage||split(c.stages).includes(stage))&&(!dimension||c.dimension_code===dimension)&&(!tool||toolCodes.includes(tool))});document.querySelector('#corpusCount').textContent=`Showing ${Math.min(rows.length,100)} of ${rows.length} matching records`;document.querySelector('#corpusDistributions').innerHTML=renderDistribution('Design domains',distribution(rows,'domains',L.domain),'#45bdd0')+renderDistribution('Evaluation dimensions',distribution(rows,'dimension_code',L.dimension),'#63c3a6')+renderDistribution('Design stages',distribution(rows,'stages',L.stage),'#849bd0');document.querySelector('#corpusRows').innerHTML=rows.slice(0,100).map(c=>{const toolCodes=[...(toolsByChain[c.chain_id]||[])],status=recordStatus(c),domains=split(c.domains).map(x=>L.domain[x]).filter(Boolean),stages=split(c.stages).map(x=>L.stage[x]).filter(Boolean);return `<tr><td><div class="study-title">${esc(c.title||'Untitled study')}</div><div class="meta">Paper ${esc(c.paper_id)} · ${esc(c.year)} · ${esc(c.chain_id)}</div></td><td>${esc(domains.join('; ')||'Domain not mapped')}<br><span class="meta">${esc(stages.join('; ')||'Stage not mapped')}</span></td><td><span class="table-code">${esc(displayCode(c.dimension_code,L.dimension))}</span></td><td>${esc(displayCode(c.indicator_code,L.indicator))}</td><td>${toolCodes.length?toolCodes.map(code=>`<span class="table-code">${code} ${esc(T[code])}</span>`).join(''):'Not mapped'}</td><td><span class="status ${status[1]}">${status[0]}</span><br><span class="meta">Quality ${esc(c.revised_quality_tier||'not classified')}</span></td></tr>`}).join('')||'<tr><td colspan="6">No evidence records match these filters.</td></tr>'}
for(const el of corpusEls)el.addEventListener(el.type==='search'?'input':'change',renderCorpus);

function renderMethod(){document.querySelector('#methodRelationships').innerHTML=['dimension','indicator','tool'].map(target=>{const rows=weightRows(target),factors=orderedGroups(target),weights=weightMap(target);return `<tr><td>${targetName[target]}</td><td>${esc(modelName(rows[0]?.selected_model))}</td><td><div class="factor-list">${factors.map(g=>`<span>${g} ${groupLabels[g]} ${(weights[g]*100).toFixed(1)}%</span>`).join('')}</div></td></tr>`}).join('')}
function setView(){const requested=location.hash.replace('#',''),view=['recommender','corpus','method'].includes(requested)?requested:'recommender';document.querySelectorAll('.app-view').forEach(el=>el.classList.toggle('active',el.id===`page-${view}`));document.querySelectorAll('[data-view]').forEach(el=>el.classList.toggle('active',el.dataset.view===view));if(view==='corpus')renderCorpus();if(view==='method')renderMethod();window.scrollTo(0,0)}
window.addEventListener('hashchange',setView);render();setView();
</script></body></html>'''
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(OUT / "index.html")


if __name__ == "__main__":
    main()

