from __future__ import annotations

import json
import re
from pathlib import Path

from config import ROOT, STANDARDS


LLM = ROOT / "llm_review"
AUTO = ROOT / "autocode"
EXT = ROOT / "extracted"
OUT = ROOT / "hybrid_review"
OUT.mkdir(exist_ok=True)
MANUAL = {1, 2, 3, 4, 43, 44, 45, 46, 47, 85, 86, 87}


def lst(x):
    return x if isinstance(x, list) else ([] if x is None else [x])


def cap(values, n):
    return list(dict.fromkeys(lst(values)))[:n]


def nums(values):
    out = []
    for x in lst(values):
        try:
            out.append(int(x))
        except Exception:
            for y in re.findall(r"\d+", str(x)):
                out.append(int(y))
    return sorted(set(out))


def sentence(text, rx):
    for part in re.split(r"(?<=[.!?])\s+|\n+", text):
        if re.search(rx, part, re.I):
            return re.sub(r"\s+", " ", part).strip()[:450]
    return ""


def find_page(pages, quote):
    q = re.sub(r"\W+", "", str(quote)).lower()
    if len(q) < 18:
        return None
    needle = q[:80]
    for p in pages:
        hay = re.sub(r"\W+", "", p.get("text", "")).lower()
        if needle in hay:
            return int(p["page"])
    return None


def audit_item(standard, status, facts, reason, pages, quote):
    return {"standard": standard, "status": status, "facts": facts, "reason": reason, "pages": nums(pages), "quote": quote[:350]}


def derive_study_codes(text):
    def hits(mapping, limit):
        return [code for code, rx in mapping if re.search(rx, text, re.I)][:limit]
    purpose = hits([
        ("P2", r"training labels?|ground truth|annotation|reward model|supervised|model validation"),
        ("P1", r"elicit|requirements?|preferences?|kansei words?|design criteria|weights?"),
        ("P3", r"formative|during (?:the )?design|iterative feedback|feedback (?:to|for) (?:revise|improve)|iteration"),
        ("P4", r"to evaluate|to assess|compare|comparison|experiment|hypothesi[sz]|effectiveness"),
    ], 2)
    if not purpose and re.search(r"study|evaluation", text, re.I): purpose = ["P4"]
    obj = hits([
        ("O1", r"design (?:solution|concept|output|artifact)|product design|image|prototype|render"),
        ("O2", r"design process|workflow|ideation process|iteration process"),
        ("O3", r"AI system|system interface|tool|usability|user interface|platform"),
        ("O4", r"human.?AI|co.?creat|collaboration|agency|division of labor"),
        ("O5", r"designer experience|workload|self.?efficacy|designer.?s? (?:emotion|ability|learning|reflection)"),
        ("O6", r"end.?user|consumer|acceptance|social|cultural|sustainab|market"),
        ("O7", r"requirements?|preferences?|value standards?|criteria"),
    ], 3)
    evaluator = hits([
        ("V1", r"professional designers?|domain experts?|design experts?|expert raters?|expert evaluation"),
        ("V2", r"design students?|novice designers?|students?"),
        ("V3", r"end.?users?|consumers?|target users?"),
        ("V4", r"crowd|general public|lay participants?|online participants?"),
        ("V5", r"clients?|organizational stakeholders?|managers?"),
        ("V6", r"researchers? (?:rated|coded|evaluated)|author evaluation"),
    ], 3)
    source = hits([
        ("H1", r"questionnaire|survey|self.?report|likert|semantic differential"),
        ("H2", r"expert evaluation|raters?|judges?|independent evaluators?|inter.?rater"),
        ("H3", r"interview|focus group|open.?ended|think.?aloud|thematic"),
        ("H4", r"existing reviews?|social media|online comments?|archival text"),
        ("H5", r"interaction logs?|task logs?|clickstream|behavioral logs?"),
        ("H6", r"automatic metric|computed|precision|recall|embedding|classifier"),
    ], 4)
    if re.search(r"within.?subject", text, re.I): design = "G2"
    elif re.search(r"between.?subject", text, re.I): design = "G3"
    elif re.search(r"mixed design|mixed.?methods", text, re.I): design = "G4"
    elif re.search(r"qualitative|interview study|thematic analysis", text, re.I): design = "G5"
    elif re.search(r"archive|existing reviews?|secondary data", text, re.I): design = "G6"
    elif re.search(r"pairwise preference|rank(?:ing)?|weight elicitation", text, re.I): design = "G7"
    elif re.search(r"annotation|training labels?|ground truth", text, re.I): design = "G8"
    else: design = "G1"
    if re.search(r"controlled|laboratory|lab study|experiment", text, re.I): setting = "L1"
    elif re.search(r"online|remote|crowd", text, re.I): setting = "L2"
    elif re.search(r"in the wild|field study|real.?world|workplace", text, re.I): setting = "L3"
    elif re.search(r"mixed setting|both online and", text, re.I): setting = "L4"
    elif re.search(r"archive|secondary data", text, re.I): setting = "L5"
    else: setting = "NR"
    tasks = hits([
        ("K1", r"requirements?|research analys|user research"), ("K2", r"ideation|concept generat|brainstorm"),
        ("K3", r"content creat|visuali[sz]|sketch|render|image generat"), ("K4", r"compare|select|choice|ranking"),
        ("K5", r"revise|refine|modify|iteration|optim"), ("K6", r"prototype|implementation|testing"),
        ("K7", r"collaborat|communicat|feedback"),
    ], 4)
    constraints = hits([
        ("Q1", r"limited access to (?:experts?|participants?)|recruitment limitation"),
        ("Q2", r"time limit|time constraint|burden|fatigue"), ("Q3", r"language|translation|cross.?cultural|culture"),
        ("Q4", r"prototype unavailable|lack of real.?world|limited ecological validity"),
        ("Q5", r"available data|existing data|data availability"), ("Q6", r"privacy|confidential|organizational access"),
    ], 3)
    return purpose, obj, evaluator, source, setting, design, tasks, constraints


def derive_target_users(pages, title=""):
    """Conservatively code intended workflow users from explicit PDF wording.

    The local semantic inventory tended to emit the first three user classes as a
    default.  For the final analysis, only explicit role phrases in the title,
    abstract/introduction, and conclusion are accepted.  Generic occurrences of
    ``user`` or ``participant`` are deliberately insufficient.
    """
    head = "\n".join(str(p.get("text", "")) for p in pages[:4])
    tail = "\n".join(str(p.get("text", "")) for p in pages[-2:])
    text = f"{title}\n{head}\n{tail}"
    rules = [
        ("U2", r"\bdesign students?\b|\bstudent designers?\b|\bnovice designers?\b|\bdesign novices?\b"),
        ("U3", r"\bnon[- ]?designers?\b|\bnon[- ]?professional creators?\b|\blay creators?\b|\bamateur creators?\b"),
        ("U4", r"\bdesign teams?\b|\bcreative teams?\b|\bdesign organizations?\b|\bdesign firms?\b|\bcross[- ]functional teams?\b"),
        ("U5", r"\bengineers?\b|\barchitects?\b|\bclinicians?\b|\bteachers?\b|\bfashion professionals?\b|\bservice professionals?\b"),
        ("U6", r"\bend users?\b|\bconsumers?\b|\bcustomers?\b|\bpatients?\b|\bcitizens?\b"),
        ("U1", r"\bprofessional designers?\b|\bindustrial designers?\b|\bproduct designers?\b|\bgraphic designers?\b|\bvisual designers?\b|\bUX designers?\b|\bUI designers?\b|\bservice designers?\b|\bfashion designers?\b|\binterior designers?\b"),
    ]
    out = [code for code, rx in rules if re.search(rx, text, re.I)]
    # A paper may say simply "designers" without an explicit seniority label.
    if "U1" not in out and re.search(r"\bdesigners?\b", f"{title}\n{head}", re.I):
        out.append("U1")
    return out[:3]


def cluster_studies(studies):
    def quote_score(q):
        q = str(q or "")
        return (2 if re.search(r"participant|respondent|designer|student|expert|user|consumer|rater|judge|interviewee|crowd", q, re.I) else 0) + (2 if re.search(r"likert|questionnaire|survey|interview|subjective|perceiv|rating|preference|satisfaction|trust|usability|workload|experience", q, re.I) else 0) + (1 if re.search(r"recruit|sample|\bn\s*=", q, re.I) else 0)
    clusters = []
    for raw in studies:
        s = dict(raw); sp = set(nums(s.get("pages")))
        try: sn = int(s.get("sample_n"))
        except Exception: sn = None
        placed = False
        for c in clusters:
            cp = set(nums(c.get("pages")))
            try: cn = int(c.get("sample_n"))
            except Exception: cn = None
            distance = min((abs(a-b) for a in sp for b in cp), default=999)
            similar_n = sn is None or cn is None or (min(sn,cn)/max(sn,cn) >= .7)
            same_span = bool(sp and cp and sp == cp)
            if same_span or (similar_n and (sp.intersection(cp) or distance <= 1)):
                c["pages"] = sorted(sp.union(cp))
                if not c.get("sample_n") and s.get("sample_n"): c["sample_n"] = s.get("sample_n")
                if quote_score(s.get("quote")) > quote_score(c.get("quote")) or (quote_score(s.get("quote")) == quote_score(c.get("quote")) and len(str(s.get("quote", ""))) > len(str(c.get("quote", "")))):
                    c["quote"] = s.get("quote", "")
                placed = True; break
        if not placed:
            clusters.append(s)
    return clusters[:6]


def build_audit(study, chains, text, selected_pages):
    has_purpose = bool(study.get("purpose_codes"))
    has_measure = bool(chains)
    sample = bool(study.get("sample_n")) or bool(re.search(r"\b(?:n\s*=\s*\d+|\d+\s+(?:participants?|respondents?|designers?|students?|experts?|raters?|users?))", text, re.I))
    task = bool(re.search(r"task|procedure|participants? (?:completed|performed|were asked)|study design", text, re.I))
    setting = study.get("setting_code") not in {None, "", "NR"}
    valid = bool(re.search(r"validat(?:ed|ion)|factor analys|content validity|construct validity", text, re.I))
    named = any("M2" in lst(c.get("tool_family_codes")) for c in chains)
    items = any(c.get("item_quote") not in {None, "", "NR"} for c in chains)
    reliable = bool(re.search(r"cronbach|inter.?rater|intra.?class|\bICC\b|cohen.?s kappa|kendall|test.?retest|reliab", text, re.I))
    analysis = bool(re.search(r"t.?test|anova|manova|regression|mixed.?effects?|wilcoxon|mann.?whitney|chi.?square|thematic analysis|content analysis|confidence interval|p\s*[<=>]", text, re.I))
    result = any(c.get("result_quote") not in {None, "", "NR"} for c in chains)
    comparator = bool(re.search(r"baseline|control group|between.subject|within.subject|compared with|comparison", text, re.I))
    causal = any(re.search(r"improv|enhanc|outperform|lead to|increase|decrease|effect", str(c.get("claim_quote", "")), re.I) for c in chains)
    scoring = any(c.get("response_scoring") not in {None, "", "NR"} for c in chains)
    quotes = {
        "purpose": sentence(text, r"to evaluate|aim(?:ed|s)? to|we investigate|research question"),
        "measure": sentence(text, r"likert|questionnaire|survey|interview|rating|scale|measure"),
        "reliable": sentence(text, r"cronbach|inter.?rater|\bICC\b|kappa|kendall|reliab"),
        "sample": sentence(text, r"\bparticipants?|respondents?|sample|recruited"),
        "analysis": sentence(text, r"t.?test|anova|regression|wilcoxon|thematic analysis|p\s*[<=>]"),
        "result": next((str(c.get("result_quote", "")) for c in chains if c.get("result_quote") not in {None, "", "NR"}), ""),
    }
    u5 = "S" if has_purpose and has_measure else ("P" if has_measure else "NR")
    a2 = "S" if valid else ("P" if named or items else "NR")
    a3 = "S" if reliable else "NR"
    a4 = "S" if sample and task and setting else ("P" if sum([sample, task, setting]) >= 2 else "NR")
    a6 = "C" if causal and not comparator and not analysis else ("S" if analysis and result else ("P" if result else "NR"))
    a7 = "C" if causal and not comparator and not analysis else ("S" if result and analysis else ("P" if result else "NR"))
    e1 = "S" if sample and scoring and result else ("P" if has_measure and result else "NR")
    return [
        audit_item("U5", u5, "评价问题／目的与实际主观证据的对应", "目的与证据均明确为充分；仅证据明确为部分。", selected_pages, quotes["purpose"]),
        audit_item("A2", a2, "构念、题项、工具来源或效度依据", "报告效度依据为充分；仅报告工具／题项为部分。", selected_pages, quotes["measure"]),
        audit_item("A3", a3, "可靠性或评分一致性依据", "找到可靠性／一致性依据为充分；未找到记NR。", selected_pages, quotes["reliable"]),
        audit_item("A4", a4, "样本、任务与实施情境描述", "三项均明确为充分，两项明确为部分。", selected_pages, quotes["sample"]),
        audit_item("A6", a6, "研究设计、比较条件与分析", "分析与结果均明确为充分；无比较／分析却作效果主张为明确问题。", selected_pages, quotes["analysis"]),
        audit_item("A7", a7, "结果到效果主张的可追溯性", "结果和分析均可定位为充分；只有结果为部分；推断越界为明确问题。", selected_pages, quotes["result"]),
        audit_item("E1", e1, "样本、计分、结果与工具记录", "样本、计分和结果均可定位为充分；部分可定位为部分。", selected_pages, quotes["measure"]),
    ]


def normalize_chain(c, pages):
    c = dict(c)
    # Autocode chains are derived from exact PDF sentences. Verify again and repair missing page locations.
    located = []
    for key in ["claim_quote", "item_quote", "result_quote"]:
        pg = find_page(pages, c.get(key, ""))
        if pg:
            located.append(pg)
    existing = nums(c.get("pages"))
    c["pages"] = sorted(set(existing + located))
    c.pop("paper_id", None); c.pop("eval_id", None); c.pop("chain_id", None)
    c.pop("audit_statuses", None); c.pop("strict_eligible", None); c.pop("sensitivity_eligible", None); c.pop("coding_status", None)
    c.setdefault("adaptation", "NR")
    return c


def main():
    for pid in range(1, 126):
        if pid in MANUAL:
            continue
        inv = json.loads((LLM / f"paper_{pid:03d}.json").read_text(encoding="utf-8"))
        auto = json.loads((AUTO / f"paper_{pid:03d}.json").read_text(encoding="utf-8"))
        doc = json.loads((EXT / f"{pid:03d}.json").read_text(encoding="utf-8"))
        pages = doc["pages"]
        studies = cluster_studies(lst(inv.get("inventory_human_evaluations")))
        out = {
            "paper_id": pid, "title": inv.get("title") or auto.get("title", ""), "doi": inv.get("doi") or auto.get("doi", ""),
            "year": inv.get("year") or auto.get("year"), "reviewed_pages": inv.get("reviewed_pages", []),
            "scope_note": "全文逐页规则筛查＋高相关证据页语义清点；证据链仅保留PDF原句定位，未使用旧表内容。",
            "domain_codes": cap(auto.get("domain_codes"), 2), "stage_codes": cap(auto.get("stage_codes"), 4),
            "ai_function_codes": cap(auto.get("ai_function_codes"), 4), "ai_role_codes": cap(auto.get("ai_role_codes"), 2),
            "target_user_codes": derive_target_users(pages, inv.get("title") or auto.get("title", "")), "context_summary": inv.get("context_summary", ""),
            "context_evidence": inv.get("context_evidence", []), "category_gaps": inv.get("category_gaps", []),
            "exclusion_facts": inv.get("exclusion_facts", []), "evaluations": [], "coding_source": "hybrid_fulltext_rules_plus_semantic_inventory",
            "pdf_path": doc.get("pdf_path", ""),
        }
        auto_chains = [normalize_chain(c, pages) for c in lst(auto.get("chains"))]
        seen_studies = set()
        for ei, study0 in enumerate(studies, 1):
            study = dict(study0)
            study_pages = nums(study.get("pages"))
            quote_page = find_page(pages, study.get("quote", ""))
            if quote_page:
                study_pages = sorted(set(study_pages + [quote_page]))
            fp = (str(study.get("sample_n", "")), tuple(study_pages), re.sub(r"\W+", "", str(study.get("quote", ""))).lower()[:100])
            if fp in seen_studies:
                continue
            seen_studies.add(fp)
            expanded = {x for n in study_pages for x in range(max(1, n-2), min(len(pages), n+2)+1)}
            chains = [c for c in auto_chains if expanded.intersection(nums(c.get("pages")))] if expanded else auto_chains
            # Exact evidence only, deduplicated by fixed indicator + tool + result.
            dedup, seen = [], set()
            for c in chains:
                if not c.get("pages"):
                    continue
                key = (c.get("indicator_code"), tuple(lst(c.get("tool_family_codes"))), re.sub(r"\W+", "", str(c.get("result_quote", ""))).lower()[:80])
                if key in seen:
                    continue
                seen.add(key); dedup.append(c)
            chains = dedup[:12]
            selected = sorted(expanded) if expanded else sorted({n for c in chains for n in nums(c.get("pages"))})
            text = "\n".join(p.get("text", "") for p in pages if int(p["page"]) in set(selected))
            human_ok = bool(re.search(r"participant|respondent|designer|student|expert|user|consumer|customer|rater|judge|interviewee|crowd", text, re.I))
            subjective_ok = bool(re.search(r"likert|questionnaire|survey|interview|subjective|perceiv|rating|rated|preference|satisfaction|trust|usability|workload|experience", text, re.I))
            quote_human = bool(re.search(r"participant|respondent|designer|student|expert|user|consumer|customer|rater|judge|interviewee|crowd", str(study.get("quote", "")), re.I)) or bool(re.fullmatch(r"P\d+", str(study.get("study_label", "")), re.I))
            quote_subjective = bool(re.search(r"likert|questionnaire|survey|interview|subjective|perceiv|rating|rated|preference|satisfaction|trust|usability|workload|experience", str(study.get("quote", "")), re.I))
            explicit_human_sample = bool(re.search(r"\b(?:n\s*=\s*\d+|\d+\s+(?:participants?|respondents?|designers?|students?|experts?|raters?|judges?|users?|consumers?))", text, re.I))
            if not (human_ok and subjective_ok and (quote_human or (quote_subjective and explicit_human_sample))):
                continue
            purpose, objects, evaluators, sources, setting, design, tasks, constraints = derive_study_codes(text)
            sample_hits = re.findall(r"\b(?:n\s*=\s*(\d+)|(\d+)\s+(?:participants?|respondents?|designers?|students?|experts?|raters?|users?))", text, re.I)
            sample_n = next((int(a or b) for a, b in sample_hits if int(a or b) > 0), study.get("sample_n"))
            evidence_quote = study.get("quote", "") if quote_page else sentence(text, r"participants?|respondents?|questionnaire|survey|interview|subjective|rating")
            if not chains:
                quote = study.get("quote", "")
                tool = ["M4"] if "H3" in sources else (["M1"] if any(x in sources for x in ["H1", "H2"]) else ["UNMAPPED"])
                chains = [{
                    "claim_quote": quote, "claim_summary": "全文确认存在人类主观评价，但固定指标映射证据不足", "claim_type": "C1",
                    "construct_raw": "UNMAPPED", "indicator_raw": "UNMAPPED", "item_quote": quote,
                    "dimension_code": "UNMAPPED", "indicator_code": "UNMAPPED", "instrument_raw": sentence(text, r"questionnaire|survey|interview|rating|scale") or "NR",
                    "tool_family_codes": tool, "tool_origin_code": "NR", "adaptation": "NR", "response_scoring": sentence(text, r"likert|point scale|strongly disagree") or "NR",
                    "validity_evidence": "NR", "reliability_evidence": "NR", "result_quote": "NR", "effect_direction": "NR", "pages": study_pages[:1],
                }]
            ev = {
                "eval_id": f"{pid:03d}-E{ei}", "purpose_codes": purpose,
                "object_codes": objects, "evaluator_codes": evaluators,
                "source_codes": sources, "setting_code": setting,
                "design_code": design,
                "evaluation_stage_codes": cap(study.get("evaluation_stage_codes"), 4), "task_codes": tasks, "constraint_codes": constraints,
                "sample_n": sample_n, "sample_description": evidence_quote, "recruitment": sentence(text, r"recruit|sampling"),
                "task": sentence(text, r"task|were asked|required to"), "comparator": sentence(text, r"baseline|control group|compared with|between.subject|within.subject"),
                "procedure": sentence(text, r"procedure|participants? (?:completed|performed|were asked)"),
                "analysis": sentence(text, r"t.?test|anova|regression|wilcoxon|thematic analysis|content analysis|p\s*[<=>]"),
                "actual_results": next((str(c.get("result_quote", "")) for c in chains if c.get("result_quote") not in {None, "", "NR"}), ""),
                "limitations": sentence(text, r"limitation|future work"), "ethics": sentence(text, r"ethic|informed consent|institutional review|IRB"),
                "evidence": [{"field": "study_inventory", "page": (quote_page or (study_pages[0] if study_pages else None)), "quote": evidence_quote}],
                "chains": chains,
            }
            ev["audit"] = build_audit(study, chains, text, selected)
            out["evaluations"].append(ev)
        (OUT / f"paper_{pid:03d}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("hybrid finalized")


if __name__ == "__main__":
    main()
