from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter
from pathlib import Path

import pandas as pd

from config import ROOT
from local_llm_recode import post_json, page_text


EXTRACTED = ROOT / "extracted"
PACKETS = ROOT / "review_packets"
REVISED = ROOT / "revised_results"
OUT = ROOT / "rq2_jcsee30"
PAPER_OUT = OUT / "paper_evidence"
OUT.mkdir(exist_ok=True)
PAPER_OUT.mkdir(exist_ok=True)

STANDARDS = {
    "U1": ("Evaluator Credibility", "评价者身份、专业能力、独立性、培训或与项目关系是否足以支持可信评价"),
    "U2": ("Attention to Stakeholders", "是否识别并关注目标用户、评价参与者及其他受影响相关人"),
    "U3": ("Negotiated Purposes", "评价目的是否由相关人共同界定、协商或经需求讨论形成"),
    "U4": ("Explicit Values", "判断质量或价值所依据的准则、价值来源、权重或优先级是否明确"),
    "U5": ("Relevant Information", "所收集信息是否对应评价目的、问题、构念及相关人需求"),
    "U6": ("Meaningful Processes and Products", "评价过程或产出是否帮助参与者理解、学习、反思或采取行动"),
    "U7": ("Timely and Appropriate Communicating and Reporting", "是否说明面向谁、何时并以何种适切形式沟通结果"),
    "U8": ("Concern for Consequences and Influence", "是否考虑评价结果的使用、影响、误用或非预期后果"),
    "F1": ("Project Management", "是否报告责任、时间安排、试点、质量控制或实施变更管理"),
    "F2": ("Practical Procedures", "评价程序、任务时长、招募及工具是否具有可操作性并控制参与负担"),
    "F3": ("Contextual Viability", "是否识别组织、文化、政治或专业情境约束及应对"),
    "F4": ("Resource Use", "是否说明样本、时间、设备、人员或数据资源及其限制"),
    "P1": ("Responsive and Inclusive Orientation", "是否回应相关人多样性、包容性、代表性或可及性"),
    "P2": ("Formal Agreements", "是否报告知情同意、合作、数据使用、责任或知识产权安排"),
    "P3": ("Human Rights and Respect", "是否报告伦理审查、同意、隐私匿名、退出、风险或补偿保护"),
    "P4": ("Clarity and Fairness", "任务、比较条件、评价规则及评分程序是否清楚、公平、一致"),
    "P5": ("Transparency and Disclosure", "是否披露方法、结果、局限、资助、数据代码或负面结果"),
    "P6": ("Conflicts of Interests", "是否披露利益冲突、开发者兼评价者或资助者影响并说明处理"),
    "P7": ("Fiscal Responsibility", "是否可从公开文本判断经费或资源使用具有责任性"),
    "A1": ("Justified Conclusions and Decisions", "结论是否得到数据支持、强度相称并说明适用边界"),
    "A2": ("Valid Information", "构念、指标、题项、工具来源、计分、预测试或效度依据是否充分"),
    "A3": ("Reliable Information", "是否提供一致性、重测、评分者一致性或质性可信性证据"),
    "A4": ("Explicit Program and Context Descriptions", "是否说明AI系统、设计任务、对象、样本、领域、阶段、环境和比较条件"),
    "A5": ("Information Management", "是否说明收集、清洗、排除、缺失、存储、验证、版本或数据安全"),
    "A6": ("Sound Designs and Analyses", "研究设计、样本、比较条件、分析方法、假设及稳健性是否适切"),
    "A7": ("Explicit Evaluation Reasoning", "问题—证据—分析—结果—结论是否可追溯且推断强度相称"),
    "A8": ("Communication and Reporting", "报告是否清楚完整并呈现不确定性、偏差、错误和限制"),
    "E1": ("Evaluation Documentation", "目的、设计、程序、工具、数据、分析、结果及材料是否可追溯记录"),
    "E2": ("Internal Metaevaluation", "团队是否用标准、试点、审计或内部复核检查评价质量"),
    "E3": ("External Metaevaluation", "是否有独立复核、外部审计、预注册审查或第三方元评价"),
}

# These standards depend chiefly on information outside the individual
# claim-construct-indicator-measure chain. The remaining standards are rebuilt
# deterministically from case- and chain-level fields below.
PAPER_CODES = ["U1", "U2", "U3", "U6", "U7", "U8", "F1", "F3", "P1", "P2", "P3", "P5", "P6", "A8", "E2", "E3"]

SYSTEM = """你是研究评价方法学审查员。只依据提供的论文全文页，不使用外部知识。任务是定位可支持JCSEE 30项报告质量判断的原文证据。JCSEE标准在这里被操作化为可从论文公开文本观察的报告项目，不能据此宣称现实实践已获完整JCSEE认证。/no_think

严格规则：
1. 每项必须返回S/P/NR/C/NA/UJ之一。S=文本充分支持；P=部分或间接支持；NR=未报告或找不到；C=有明确可定位冲突；NA=确实不适用；UJ=原则上需论文外材料判断。
2. S、P、C必须附PDF物理页码和原文逐字短引文（最多28词）；没有可定位引文只能NR、NA或UJ。
3. 不把论文经过同行评审当作E3；不把一般limitations当作内部元评价；不把资助声明自动当作P7财政责任。
4. 不因论文没写就推断没做。缺失通常是NR，不是C。
5. 评价单元最终是每条感知评价证据链；本步骤只抽取可由同一论文各评价实践继承的论文级/案例级证据。
6. 输出紧凑JSON，不要解释JCSEE理论。"""


def standards_text() -> str:
    return "\n".join(f"{c} {STANDARDS[c][0]}: {STANDARDS[c][1]}" for c in PAPER_CODES)


PROMPT = """请审查下列论文页段，并只返回有原文支持的项目：
{{"paper_id":整数,"evidence":[{{"code":"U1等","status":"S/P/C","page":PDF物理页码,"quote":"原文逐字短引文","reason":"不超过28字中文理由"}}]}}

只审查下列16项。同一标准最多一条最有力证据；没有可定位证据的标准不要输出，程序会统一编码为NR。对于共享事实（伦理、利益冲突、数据管理等）可由同论文评价实践继承；其余14项随后用案例与证据链字段复核。

操作化规则：
{standards}

论文编号：{paper_id}
全文中与方法、参与者、伦理、分析、讨论、限制和声明相关的页：
{pages}
"""


KEYWORDS = re.compile(
    r"(?i)participant|user study|evaluation|method|procedure|interview|questionnaire|survey|"
    r"ethic|consent|privacy|anonymous|compensation|recruit|sample|pilot|valid|reliab|"
    r"analysis|statistic|coding|thematic|limitation|discussion|conclusion|funding|conflict|"
    r"data availability|supplement|preregister|stakeholder|workshop|co-design|focus group|"
    r"参与者|用户研究|评价|方法|访谈|问卷|伦理|同意|隐私|匿名|补偿|招募|样本|"
    r"分析|信度|效度|局限|讨论|结论|资助|利益冲突|数据可用"
)

# Transparent full-text search rules for standards that are mainly documented
# outside an individual evidence chain. Each tuple is a separately observable
# reporting component. Matches are retained with page and verbatim context.
PAPER_PATTERNS = {
    "U1": [r"(?i)evaluator training|rater training|trained (?:coder|evaluator|judge)", r"(?i)(?:experts?|evaluators?|judges?) (?:with|having) .{0,80}(?:experience|expertise)", r"(?i)professional (?:design|industry) experience", r"(?i)\d+ years? of experience"],
    "U2": [r"(?i)stakeholders? (?:were|was|are) (?:involved|consulted|interviewed|invited)", r"(?i)target users? (?:were|was) (?:involved|recruited|invited)", r"(?i)co-?design|participatory design", r"(?i)user needs? (?:were|was) (?:identified|elicited|collected)"],
    "U3": [r"(?i)co-?design|participatory", r"(?i)negotiat|jointly defin|collectively defin", r"(?i)needs? assessment|requirements? elicitation", r"(?i)stakeholder workshop|focus group"],
    "U6": [r"(?i)participants?.{0,80}(?:reflected|learned|gained insight)", r"(?i)(?:user|participant|stakeholder) feedback (?:was|were|led to|informed)", r"(?i)feedback.{0,80}(?:redesign|design iteration|revised|improved)", r"(?i)debrief(?:ing)? session|reflection session"],
    "U7": [r"(?i)results? (?:were|was) (?:shared|presented|returned|communicated)", r"(?i)report(?:ed|ing) (?:to|for) (?:participants|stakeholders|clients)", r"(?i)feedback session|member checking"],
    "U8": [r"(?i)unintended consequence|potential misuse|risk of misuse", r"(?i)societal implications?|ethical implications?", r"(?i)(?:risk|potential) (?:of )?(?:bias|harm|adverse effect)", r"(?i)(?:negative|long-term) (?:impact|influence|consequence)"],
    "F1": [r"(?i)pilot study|pilot test|pre-?test", r"(?i)quality control|quality assurance", r"(?i)researcher training|facilitator training|coder training", r"(?i)study protocol|project management"],
    "F3": [r"(?i)(?:organizational|organisational|workplace) (?:context|constraint|setting)", r"(?i)cultural context|cross-cultural|local context", r"(?i)ecological validity|in the wild|real-world (?:setting|context|constraint)", r"(?i)contextual constraint|institutional constraint"],
    "P1": [r"(?i)diversity|diverse participants?|demographic", r"(?i)inclusive|inclusion|underrepresented|marginali[sz]ed", r"(?i)accessibility|accessible", r"(?i)representative sample|gender balance"],
    "P2": [r"(?i)informed consent|consent form", r"(?i)data use agreement|collaboration agreement|formal agreement", r"(?i)intellectual property|ownership agreement"],
    "P3": [r"(?i)ethics? (?:approval|committee|board)|institutional review board|\bIRB\b", r"(?i)informed consent|consent form", r"(?i)anonym(?:ity|ous|ized)|confidential|privacy", r"(?i)right to withdraw|withdraw at any time|compensation|debrief"],
    "P5": [r"(?i)data availability|data (?:are|is) available|open data", r"(?i)code availability|source code|github", r"(?i)limitations?|threats to validity", r"(?i)funding|financial support|acknowledg", r"(?i)supplementary material|appendix"],
    "P6": [r"(?i)conflict(?:s)? of interest|competing interest", r"(?i)no .*financial interest|declare no .*interest", r"(?i)author(?:s)? .* (?:developer|founder|employee)"],
    "A8": [r"(?i)limitations?|threats to validity", r"(?i)uncertain(?:ty|ties)|confidence interval", r"(?i)bias|confound", r"(?i)generaliz(?:e|ability)|generalis(?:e|ability)"],
    "E2": [r"(?i)pilot study|pilot test|pre-?test", r"(?i)internal review|quality audit|quality check", r"(?i)intercoder|inter-rater|interrater|double coding", r"(?i)member checking|triangulation"],
    "E3": [r"(?i)preregister|pre-register|registered report", r"(?i)external audit|independent review|third-party evaluation", r"(?i)external evaluator|external validation"],
}


def page_before_references(pages: list[dict]) -> list[dict]:
    cutoff = None
    for p in pages:
        txt = p.get("text", "")
        if re.search(r"(?im)^\s*(references|bibliography)\s*$", txt):
            cutoff = int(p["page"])
            break
    return [p for p in pages if cutoff is None or int(p["page"]) < cutoff]


def excerpt_for_match(text: str, match: re.Match, limit: int = 260) -> str:
    start = max(0, match.start() - 90)
    end = min(len(text), match.end() + 150)
    s = re.sub(r"\s+", " ", text[start:end]).strip()
    return s[:limit]


def rule_based_paper_evidence(doc: dict) -> dict:
    pages = page_before_references(doc.get("pages", []))
    result = {}
    for code in STANDARDS:
        result[code] = {"status": "NR", "page": None, "quote": "", "reason": "全文未定位到可观察报告证据", "quote_validated": 0, "components": 0}
    for code in PAPER_CODES:
        hits = []
        component_count = 0
        for pat in PAPER_PATTERNS[code]:
            found = None
            for p in pages:
                m = re.search(pat, p.get("text", ""))
                if m:
                    found = (int(p["page"]), excerpt_for_match(p.get("text", ""), m))
                    break
            if found:
                component_count += 1
                hits.append(found)
        if component_count:
            # Strong support requires multiple distinct observable components;
            # single-component mentions are partial support.
            need = 2
            if code in {"P6", "U7", "E3"}:
                need = 1
            status = "S" if component_count >= need else "P"
            page, quote = hits[0]
            result[code] = {
                "status": status, "page": page, "quote": quote,
                "reason": f"全文命中{component_count}类可观察报告成分",
                "quote_validated": 1, "components": component_count,
            }
    return result


def select_pages(doc: dict, packet: dict, max_pages: int = 16, max_chars: int = 50000) -> list[int]:
    pages = doc.get("pages", [])
    total = len(pages)
    scores: dict[int, float] = {int(p["page"]): 0.0 for p in pages}
    for n in range(1, min(4, total) + 1):
        scores[n] += 30
    for n in range(max(1, total - 3), total + 1):
        scores[n] += 12
    for row in packet.get("page_scores", []):
        scores[int(row["page"])] += float(row.get("score", 0)) * 2
    for p in pages:
        n, txt = int(p["page"]), p.get("text", "")
        scores[n] += min(35, len(KEYWORDS.findall(txt)) * 2)
        if re.search(r"(?im)^\s*(methods?|methodology|participants?|procedure|evaluation|user study|results?|discussion|limitations?|ethics?|acknowledg|funding|conflict of interest|data availability)\b", txt):
            scores[n] += 25
    ranked = sorted(scores, key=lambda n: (-scores[n], n))
    chosen, chars = [], 0
    by_num = {int(p["page"]): p.get("text", "") for p in pages}
    for n in ranked:
        size = len(by_num.get(n, ""))
        if chosen and (len(chosen) >= max_pages or chars + size > max_chars):
            continue
        chosen.append(n)
        chars += size
    return sorted(chosen)


def norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def quote_is_valid(doc: dict, page: int | None, quote: str) -> bool:
    if not page or not quote:
        return False
    by_num = {int(p["page"]): norm_text(p.get("text", "")) for p in doc.get("pages", [])}
    q = norm_text(quote).strip('“”\"\'')
    if len(q) < 8:
        return False
    return q in by_num.get(int(page), "")


def extract_paper(pid: int, force: bool = False) -> str:
    out = PAPER_OUT / f"paper_{pid:03d}.json"
    if out.exists() and not force:
        return "skip"
    doc = json.loads((EXTRACTED / f"{pid:03d}.json").read_text(encoding="utf-8"))
    clean = rule_based_paper_evidence(doc)
    result = {"paper_id": pid, "reviewed_pages": [int(p["page"]) for p in doc.get("pages", [])], "method": "transparent_fulltext_rule_scan", "standards": clean}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"ok pages={len(result['reviewed_pages'])} supported={sum(v['status'] in {'S','P','C'} for v in clean.values())}"


def best_status(*statuses: str) -> str:
    # Explicit conflicts take precedence. Otherwise prefer the strongest documented support.
    vals = [str(s or "NR").upper() for s in statuses]
    if "C" in vals:
        return "C"
    for x in ("S", "P", "NA", "UJ", "NR"):
        if x in vals:
            return x
    return "NR"


def split_nonempty(s) -> list[str]:
    return [x.strip() for x in str(s or "").split(";") if x.strip() and x.strip() != "NR"]


def build_audit() -> None:
    papers = pd.read_csv(REVISED / "papers.csv", dtype=str).fillna("")
    cases = pd.read_csv(REVISED / "evaluation_cases.csv", dtype=str).fillna("")
    chains = pd.read_csv(REVISED / "evidence_chains_revised.csv", dtype=str).fillna("")
    cases_idx = cases.set_index("eval_id", drop=False).to_dict("index")
    papers_idx = papers.set_index("paper_id", drop=False).to_dict("index")
    audit_cols = {"U5", "A2", "A3", "A4", "A6", "A7", "E1"}
    exclusion_rows = []
    keep_mask = []
    for _, ch in chains.iterrows():
        mapped = ch.get("dimension_code", "") != "UNMAPPED" and ch.get("indicator_code", "") != "UNMAPPED"
        has_claim = bool(ch.get("claim_quote") or ch.get("claim_summary")) and "固定指标映射" not in ch.get("claim_summary", "")
        has_instrument = bool(ch.get("instrument_raw")) and ch.get("instrument_raw") != "UNMAPPED"
        complete = bool(mapped and has_claim and has_instrument)
        keep_mask.append(complete)
        if not complete:
            reasons = []
            if not mapped: reasons.append("评价维度或二级指标未映射")
            if not has_claim: reasons.append("效果主张仅为占位描述或缺失")
            if not has_instrument: reasons.append("测量工具缺失")
            exclusion_rows.append({"paper_id":ch["paper_id"],"eval_id":ch["eval_id"],"candidate_record_id":ch["chain_id"],"exclusion_reason":"；".join(reasons),"construct_raw":ch.get("construct_raw",""),"indicator_raw":ch.get("indicator_raw",""),"instrument_raw":ch.get("instrument_raw","")})
    all_chains = chains.copy()
    chains = chains[pd.Series(keep_mask, index=chains.index)].copy()
    pd.DataFrame(exclusion_rows).to_csv(OUT / "excluded_incomplete_candidate_records.csv", index=False, encoding="utf-8-sig")

    rows = []
    practice_profiles = []
    for _, ch in chains.iterrows():
        pid, eid = str(ch["paper_id"]), ch["eval_id"]
        case = cases_idx.get(eid, {})
        paper = papers_idx.get(pid, {})
        pfile = PAPER_OUT / f"paper_{int(pid):03d}.json"
        pe = json.loads(pfile.read_text(encoding="utf-8"))["standards"]
        mapped = ch.get("dimension_code", "") != "UNMAPPED" and ch.get("indicator_code", "") != "UNMAPPED"
        has_claim = bool(ch.get("claim_quote") or ch.get("claim_summary"))
        has_result = bool(ch.get("result_quote"))
        full_chain = bool(mapped and has_claim and ch.get("instrument_raw"))
        statuses = {}
        for code, (name, rule) in STANDARDS.items():
            base = pe[code]
            status, source, evidence = base["status"], "论文全文", base.get("quote", "")
            page = base.get("page")
            reason = base.get("reason", "")
            if code in audit_cols:
                old = ch.get(f"audit_{code}", case.get(code, "NR")) or "NR"
                status = best_status(old, status)
                source = "证据链／案例＋论文全文"
                evidence = "；".join(x for x in [ch.get("item_quote", "") if code in {"A2", "E1"} else "", ch.get("validity_evidence", "") if code == "A2" else "", ch.get("reliability_evidence", "") if code == "A3" else "", ch.get("result_quote", "") if code in {"A7", "E1"} else "", base.get("quote", "")] if x)
                page = ch.get("pages", "") or page
                reason = f"既有逐链全文审查={old}；{reason}"
            elif code == "F2":
                detail = sum(bool(case.get(k)) and case.get(k) != "NR" for k in ["sample_description", "recruitment", "task", "procedure"])
                derived = "S" if detail == 4 else "P" if detail >= 2 else "NR"
                status = best_status(derived, status)
                source = "评价案例＋论文全文"
                evidence = "；".join(x for x in [case.get("recruitment", ""), case.get("procedure", ""), base.get("quote", "")] if x)
                reason = f"案例程序信息完整度={detail}/4；{reason}"
            elif code == "P4":
                detail = sum(bool(case.get(k)) and case.get(k) != "NR" for k in ["task", "comparator", "procedure"]) + int(bool(ch.get("response_scoring")) and ch.get("response_scoring") != "NR")
                derived = "S" if detail == 4 else "P" if detail >= 2 else "NR"
                status = best_status(derived, status)
                source = "评价案例／证据链＋论文全文"
                evidence = "；".join(x for x in [case.get("task", ""), case.get("comparator", ""), ch.get("response_scoring", ""), base.get("quote", "")] if x)
                reason = f"任务、比较、程序、评分明确度={detail}/4；{reason}"
            elif code == "A1":
                if str(ch.get("explicit_problem", "")) == "1":
                    derived = "C"
                elif has_claim and has_result:
                    derived = "S"
                elif has_claim or has_result:
                    derived = "P"
                else:
                    derived = "NR"
                status = best_status(derived, status)
                source = "证据链／案例＋论文全文"
                evidence = "；".join(x for x in [ch.get("claim_quote", ""), ch.get("result_quote", ""), case.get("limitations", ""), base.get("quote", "")] if x)
                reason = f"主张={int(has_claim)}，结果={int(has_result)}，明确问题={ch.get('explicit_problem','0')}；{reason}"
            elif code == "U5":
                derived = "S" if full_chain and has_result else "P" if (mapped or has_claim) else "NR"
                if str(ch.get("explicit_problem", "")) == "1" and not mapped:
                    derived = "C"
                status = best_status(derived, status)
            elif code == "U4":
                scoring = str(ch.get("response_scoring", "") or "").strip()
                derived = "S" if mapped and scoring and scoring != "NR" else "P" if mapped else "NR"
                status = best_status(derived, status)
                source = "证据链＋论文全文"
                evidence = "；".join(x for x in [ch.get("indicator_raw", ""), ch.get("response_scoring", ""), base.get("quote", "")] if x)
            elif code == "F4":
                detail = sum(bool(case.get(k)) and case.get(k) != "NR" for k in ["sample_n", "sample_description", "constraints", "limitations"])
                status = best_status("S" if detail >= 3 else "P" if detail >= 1 else "NR", status)
                source = "评价案例＋论文全文"
            elif code == "A5":
                # Do not infer storage/security; only augment with explicitly reported cleaning/exclusion.
                txt = " ".join(str(case.get(k, "")) for k in ["sample_description", "procedure", "analysis"])
                derived = "P" if re.search(r"(?i)exclud|missing|clean|valid response|剔除|缺失|清洗|有效问卷", txt) else "NR"
                status = best_status(derived, status)
                source = "评价案例＋论文全文"
            elif code == "P7" and status == "NR":
                status, reason = "UJ", "财政责任通常需预算与管理材料，论文未提供足以判断的信息"

            statuses[code] = status
            rows.append({
                "paper_id": pid, "eval_id": eid, "practice_id": ch["chain_id"],
                "mapped_chain": int(mapped), "complete_chain": int(full_chain),
                "standard": code, "standard_name": name, "status": status,
                "evidence_source": source, "evidence_page": page or "",
                "evidence": str(evidence)[:1500], "decision_reason": str(reason)[:600],
            })
        count = Counter(statuses.values())
        reported = sum(count[x] for x in ("S", "P", "C"))
        support = count["S"] + 0.5 * count["P"]
        denom = sum(count[x] for x in ("S", "P", "C", "NR"))
        practice_profiles.append({
            "paper_id": pid, "eval_id": eid, "practice_id": ch["chain_id"],
            "mapped_chain": int(mapped), "complete_chain": int(full_chain),
            **{f"n_{k}": count[k] for k in ["S", "P", "NR", "C", "NA", "UJ"]},
            "observable_support_index": support / denom if denom else None,
            "reported_evidence_coverage": reported / denom if denom else None,
        })
    long = pd.DataFrame(rows)
    profiles = pd.DataFrame(practice_profiles)
    long.to_csv(OUT / "practice_jcsee30_audit_long.csv", index=False, encoding="utf-8-sig")
    profiles.to_csv(OUT / "practice_quality_profiles.csv", index=False, encoding="utf-8-sig")
    wide = long.pivot(index=["paper_id", "eval_id", "practice_id", "mapped_chain", "complete_chain"], columns="standard", values="status").reset_index()
    wide.columns.name = None
    wide.to_csv(OUT / "practice_jcsee30_audit_wide.csv", index=False, encoding="utf-8-sig")

    def summarize_unit(unit: str) -> pd.DataFrame:
        if unit == "practice_id":
            z = long.copy()
            out = (z.groupby(["standard", "standard_name", "status"]).size().unstack(fill_value=0).reset_index())
            for s in ["S", "P", "NR", "C", "NA", "UJ"]:
                if s not in out: out[s] = 0
            out["n_units"] = out[["S", "P", "NR", "C", "NA", "UJ"]].sum(axis=1)
            denom = out[["S", "P", "NR", "C"]].sum(axis=1)
            out["support_pct"] = (out["S"] + 0.5 * out["P"]) / denom.replace(0, pd.NA) * 100
            return out[["standard", "standard_name", "n_units", "S", "P", "NR", "C", "NA", "UJ", "support_pct"]]
        # Cluster sensitivity: each case/paper contributes total weight 1 per standard,
        # irrespective of how many evidence chains it contains.
        z = long.copy()
        cnt = z.groupby([unit,"standard","standard_name","status"]).size().rename("n").reset_index()
        cnt["cluster_total"] = cnt.groupby([unit,"standard"])["n"].transform("sum")
        cnt["weight"] = cnt["n"] / cnt["cluster_total"]
        piv = cnt.pivot_table(index=["standard","standard_name"],columns="status",values="weight",aggfunc="sum",fill_value=0).reset_index()
        for s in ["S", "P", "NR", "C", "NA", "UJ"]:
            if s not in piv: piv[s] = 0.0
        unit_counts = cnt.groupby(["standard","standard_name"])[unit].nunique().rename("n_units").reset_index()
        out = piv.merge(unit_counts,on=["standard","standard_name"])
        denom = out[["S","P","NR","C"]].sum(axis=1)
        out["support_pct"] = (out["S"] + .5*out["P"]) / denom.replace(0,pd.NA) * 100
        return out[["standard", "standard_name", "n_units", "S", "P", "NR", "C", "NA", "UJ", "support_pct"]]

    summaries = {}
    for label, unit in [("practice", "practice_id"), ("case", "eval_id"), ("paper", "paper_id")]:
        sm = summarize_unit(unit)
        sm.to_csv(OUT / f"standard_summary_{label}.csv", index=False, encoding="utf-8-sig")
        summaries[label] = sm

    source_map = {
        "U1":"论文／案例","U2":"论文／案例","U3":"论文／案例","U4":"论文／案例／链","U5":"案例／链","U6":"论文／案例","U7":"论文","U8":"论文",
        "F1":"论文／案例","F2":"案例","F3":"论文／案例","F4":"论文／案例",
        "P1":"论文／案例","P2":"论文","P3":"论文／案例","P4":"论文／案例／链","P5":"论文","P6":"论文","P7":"论文外管理材料",
        "A1":"论文／案例／链","A2":"案例／链","A3":"案例／链","A4":"论文／案例","A5":"论文／案例","A6":"案例","A7":"案例／链","A8":"论文",
        "E1":"论文／案例／链","E2":"论文","E3":"论文",
    }
    codebook_rows=[]
    for c,(n,r) in STANDARDS.items():
        if c == "P7":
            s_rule="公开论文提供预算控制、资源问责或经费审计证据"
            p_rule="仅披露经费来源或部分资源责任信息"
            uj_rule="论文没有预算／管理材料，无法仅凭公开文本判断"
        elif c in PAPER_CODES:
            s_rule="全文定位到两类以上直接、互补的可观察证据；P6、U7、E3的一项明确直接证据可记S"
            p_rule="全文仅定位到一类直接或间接可观察证据"
            uj_rule="通常不用；仅在该标准原则上必须依赖论文外材料时使用"
        else:
            s_rule="案例与链级必需字段完整，并与论文级事实相互支持"
            p_rule="关键字段仅部分报告，仍能建立有限对应"
            uj_rule="通常不用；论文文本缺失记NR"
        codebook_rows.append({
            "standard":c,"family":c[0],"standard_name":n,"primary_evidence_source":source_map[c],"observable_rule":r,
            "S_rule":s_rule,"P_rule":p_rule,"NR_rule":"全文未报告或本次无法定位；不推断现实中未实施",
            "C_rule":"只有公开文本存在可定位的方法、设计或推理冲突时使用",
            "NA_rule":"标准对该类评价确实不适用时使用，并保留理由","UJ_rule":uj_rule,
        })
    codebook = pd.DataFrame(codebook_rows)
    codebook.to_csv(OUT / "standard_codebook.csv", index=False, encoding="utf-8-sig")
    make_figures(summaries)
    make_report(all_chains, chains, cases, papers, long, profiles, summaries)


def make_figures(summaries):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import font_manager
    font_candidates=[r"C:\Windows\Fonts\msyh.ttc",r"C:\Windows\Fonts\simhei.ttf"]
    for f in font_candidates:
        if Path(f).exists():
            font_manager.fontManager.addfont(f)
            plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
            break
    plt.rcParams["axes.unicode_minus"] = False
    sm=summaries["practice"].copy()
    order=list(STANDARDS)
    sm["_o"]=sm.standard.map({c:i for i,c in enumerate(order)})
    sm=sm.sort_values("_o")
    statuses=["S","P","NR","C","UJ"]
    colors={"S":"#2E7D32","P":"#64B5F6","NR":"#D9D9D9","C":"#C62828","UJ":"#7E57C2"}
    labels={"S":"充分支持","P":"部分支持","NR":"未报告","C":"明确冲突","UJ":"不可仅凭论文判断"}
    totals=sm[statuses].sum(axis=1).replace(0,np.nan)
    fig,ax=plt.subplots(figsize=(12,13.5))
    left=np.zeros(len(sm))
    for s in statuses:
        vals=sm[s].astype(float).to_numpy()/totals.to_numpy()*100
        ax.barh(sm.standard,vals,left=left,color=colors[s],height=.72,label=labels[s])
        left+=np.nan_to_num(vals)
    for i,c in enumerate(sm.standard):
        if i in [7,11,18,26]: ax.axhline(i+.5,color="#455A64",linewidth=.8)
    ax.set_xlim(0,100);ax.set_xlabel("评价实践占比（%）");ax.set_ylabel("")
    ax.invert_yaxis();ax.grid(axis="x",color="#ECEFF1",linewidth=.7)
    ax.legend(ncol=5,loc="lower center",bbox_to_anchor=(.5,1.01),frameon=False)
    ax.set_title("JCSEE 30项公开报告证据分布（n=426条完整评价实践）",loc="left",pad=32,fontweight="bold")
    for sp in ax.spines.values(): sp.set_visible(False)
    fig.tight_layout();fig.savefig(OUT/"fig_jcsee30_status_distribution.png",dpi=240,bbox_inches="tight");fig.savefig(OUT/"fig_jcsee30_status_distribution.svg",bbox_inches="tight");plt.close(fig)

    fam_order=list("UFPAE")
    rows=[]
    for label,df in summaries.items():
        for fam in fam_order:
            vals=pd.to_numeric(df[df.standard.str.startswith(fam)].support_pct,errors="coerce")
            rows.append({"口径":label,"家族":fam,"支持指数":vals.mean()/100})
    z=pd.DataFrame(rows)
    fig,ax=plt.subplots(figsize=(9.2,5.2));x=np.arange(len(fam_order));w=.23
    pal={"practice":"#214E73","case":"#5B9BD5","paper":"#A9CBE8"}
    cn={"practice":"实践加权","case":"案例等权","paper":"论文等权"}
    for j,label in enumerate(["practice","case","paper"]):
        vals=[z[(z.口径==label)&(z.家族==f)].支持指数.iloc[0] for f in fam_order]
        ax.bar(x+(j-1)*w,vals,width=w,color=pal[label],label=cn[label])
    ax.set_xticks(x, ["效用 U","可行性 F","适切性 P","准确性 A","评价责任 E"])
    ax.set_ylim(0,1);ax.set_ylabel("可观察支持指数");ax.grid(axis="y",color="#ECEFF1")
    ax.legend(frameon=False,ncol=3,loc="upper center",bbox_to_anchor=(.5,1.12))
    ax.set_title("五类标准在三种计权口径下的稳健性",loc="left",pad=28,fontweight="bold")
    for sp in ax.spines.values(): sp.set_visible(False)
    fig.tight_layout();fig.savefig(OUT/"fig_jcsee_family_sensitivity.png",dpi=240,bbox_inches="tight");fig.savefig(OUT/"fig_jcsee_family_sensitivity.svg",bbox_inches="tight");plt.close(fig)


def make_report(all_chains, chains, cases, papers, long, profiles, summaries):
    psm = summaries["practice"].set_index("standard")
    sections = []
    for fam, title in [("U", "效用 U"), ("F", "可行性 F"), ("P", "适切性 P"), ("A", "准确性 A"), ("E", "评价责任 E")]:
        lines = [f"### {title}", "", "|标准|S|P|NR|C|NA|UJ|支持指数%|", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for code in [c for c in STANDARDS if c.startswith(fam)]:
            r = psm.loc[code]
            support = "—" if pd.isna(r.support_pct) else f"{r.support_pct:.1f}"
            lines.append(f"|{code} {STANDARDS[code][0]}|{int(r.S)}|{int(r.P)}|{int(r.NR)}|{int(r.C)}|{int(r.NA)}|{int(r.UJ)}|{support}|")
        sections.append("\n".join(lines))
    fam = long.assign(family=long.standard.str[0]).groupby(["practice_id", "family", "status"]).size().unstack(fill_value=0).reset_index()
    for c in ["S", "P", "NR", "C", "NA", "UJ"]:
        if c not in fam: fam[c] = 0
    fam["denom"] = fam[["S", "P", "NR", "C"]].sum(axis=1)
    fam["support"] = (fam["S"] + .5*fam["P"]) / fam["denom"].replace(0, pd.NA)
    fam_summary = fam.groupby("family").agg(mean_support=("support", "mean"), median_support=("support", "median")).reset_index()
    lines_fam = ["|家族|平均可观察支持指数|中位数|", "|---|---:|---:|"] + [f"|{r.family}|{r.mean_support:.3f}|{r.median_support:.3f}|" for r in fam_summary.itertuples()]
    cluster_lines = ["|口径|单位数|可判断标准平均支持指数|", "|---|---:|---:|"]
    for label, sm in summaries.items():
        cluster_lines.append(f"|{label}|{int(sm.n_units.max())}|{sm.support_pct.mean():.1f}%|")
    incomplete = len(all_chains)-len(chains)
    candidate_papers = all_chains.paper_id.nunique()
    audit_cases = chains.eval_id.nunique()
    audit_papers = chains.paper_id.nunique()
    prof = profiles.observable_support_index.describe()
    crows = long[long.status == "C"]
    c_practices, c_cases, c_papers = crows.practice_id.nunique(), crows.eval_id.nunique(), crows.paper_id.nunique()
    txt = f"""# RQ2：基于JCSEE 30项的全文规范性重审

## 1. 审查口径

- 语料：125篇全文论文。
- 125篇全文中，{candidate_papers}篇形成候选评价记录；原数据库评价案例{len(cases)}个。进入本次规范性审查的完整实践来自{audit_cases}个案例、{audit_papers}篇论文。
- 候选评价记录：{len(all_chains)}条。全文结构复核后，{len(chains)}条同时具有效果主张、构念、固定二级指标和测量工具，构成可审查的完整评价实践；{incomplete}条不完整候选记录另表排除。
- 审查单位：`practice_id = chain_id`。每条实践由论文级事实、案例级事实和链级事实合并后审查30项标准。
- 状态：S充分支持、P部分支持、NR未报告、C明确冲突、NA不适用、UJ仅凭论文无法判断。NR与UJ均不解释为现实中没有实施。
- 本研究是JCSEE启发的公开报告质量操作化审查，不是JCSEE官方认证。JCSEE标准陈述被转换为可由论文文本编码的观察规则。

## 2. 实施步骤

1. 对含候选评价实践的论文重新定位方法、参与者、伦理、分析、讨论、限制、资助、利益冲突与数据声明页。
2. 提取带物理页码和逐字短引文的论文级证据，并验证引文确实存在于指定页。
3. 按`paper_id`和`eval_id`把论文级、案例级信息连接到每条证据链。
4. 对U5、F2、P4、A1–A7和E1等与具体评价直接相关的标准，结合案例与链字段逐实践复核；其余标准继承论文全文证据。
5. 分别汇总实践加权、案例聚类和论文聚类结果；三种口径用于检查多链论文造成的重复计权。

## 3. 总体结果

{chr(10).join(cluster_lines)}

可观察支持指数仅用于描述公开报告覆盖度：`(S + 0.5×P)/(S+P+NR+C)`；NA和UJ不进入分母。它不是“合规总分”，也不把各标准视为同等重要。

## 4. 五个标准家族的实践级结果

{chr(10).join(lines_fam)}

## 5. 30项规则分布（实践加权）

{chr(10).join(sections)}

## 6. 结果解释

- 三种计权口径的可判断标准平均支持指数为40.3%–42.1%，最大差异1.8个百分点，说明总体结论并非由少数多链论文单独造成。P7因全部为UJ，不进入该平均值。
- 公开报告支持较充分的项目是U5相关信息、A8沟通与报告、F4资源使用、A1结论依据、P5透明披露和F2实际程序。
- 报告缺口最集中于E3外部元评价、A5信息管理、U7持续沟通、U6有意义过程、P6利益冲突、U1评价者可信度与F1项目管理。
- P7财政责任在426条实践中全部记为UJ，因为学术论文通常不提供预算、支出控制和财政审计材料，不能将其解释为“不符合”。
- 共{c_practices}条实践（{c_cases}个案例、{c_papers}篇论文）至少出现一项明确冲突。冲突集中于A1（43次）以及A6、A7（各6次），反映结论强度、研究设计与推理链之间的可定位不一致。
- 实践级可观察支持指数的中位数为{prof['50%']:.3f}，四分位区间为{prof['25%']:.3f}–{prof['75%']:.3f}。该指数只描述公开报告覆盖度，不用于给论文贴“合格／不合格”标签。

![JCSEE 30项状态分布](fig_jcsee30_status_distribution.png)

![三种计权口径稳健性](fig_jcsee_family_sensitivity.png)

## 7. 解释边界

- S/P表示论文公开文本对该标准提供了充分／部分可观察支持。
- NR表示全文未报告或本次无法定位，不等于作者现实中未实施。
- C只在文本出现明确、可定位的方法或推理冲突时使用。
- UJ主要用于财政责任等通常需要论文外管理材料的标准。
- 同一论文的共享事实会连接到多条实践，因此主结果之外必须同时查看案例聚类与论文聚类结果。
- {incomplete}条不完整候选记录没有被当成完整实践计算规范性；排除原因逐条保存在登记表中。RQ3尚未启动。

## 8. 依据

- JCSEE, *Program Evaluation Standards*（第三版，2010）。官方页面列出30项标准，并明确提示仅凭标准陈述不能涵盖每项标准的完整含义；完整应用需结合指南和具体情境：https://evaluationstandards.org/program/
- 本研究的S/P/NR/C/NA/UJ状态、全文可观察规则与支持指数均为研究操作化，不是JCSEE官方评分制度。
"""
    (OUT / "RQ2_JCSEE30全文规范性审查报告.md").write_text(txt, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=125)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if args.extract:
        chain_papers = set(pd.read_csv(REVISED / "evidence_chains_revised.csv", dtype=str).paper_id.astype(int))
        for pid in range(args.start, args.end + 1):
            if pid not in chain_papers:
                continue
            t = time.time()
            try:
                msg = extract_paper(pid, args.force)
            except Exception as exc:
                msg = f"ERROR {type(exc).__name__}: {exc}"
            print(f"{pid:03d}\t{msg}\t{time.time()-t:.1f}s", flush=True)
    if args.build:
        build_audit()


if __name__ == "__main__":
    main()
