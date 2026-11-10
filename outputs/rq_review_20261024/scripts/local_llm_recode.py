from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from config import ROOT, LABELS, INDICATORS, STANDARDS


ENDPOINT = "http://127.0.0.1:8787/v1/chat/completions"
EXTRACTED = ROOT / "extracted"
PACKETS = ROOT / "review_packets"
OUT = ROOT / "llm_review"
OUT.mkdir(exist_ok=True)


def compact_codebook() -> str:
    parts = []
    for field in [
        "domain", "stage", "ai_function", "ai_role", "purpose", "object",
        "evaluator", "target_user", "source", "setting", "design", "task",
        "constraint", "dimension", "indicator", "tool_family", "tool_origin",
        "claim_type",
    ]:
        vals = LABELS[field]
        parts.append(field + ": " + "; ".join(f"{k}={v}" for k, v in vals.items()))
    parts.append("audit: " + "; ".join(f"{k}={v}" for k, v in STANDARDS.items()))
    return "\n".join(parts)


CODEBOOK = compact_codebook()


SYSTEM = """你是系统综述全文编码员。任务是从所给论文原文中抽取 AI-assisted design workflow 的人类主观 perceived-effect 评价实践。只依据本次提供的原文，不使用外部知识或旧表。/no_think

严格规则：
1. 只纳入人对设计成果、过程、AI系统、人机协作、设计者状态或社会后果的主观感知、判断、态度、体验或价值。纯自动指标、客观性能、日志、作者没有数据支撑的讨论不构成评价证据链。
2. 每个事实必须带 PDF 物理页码和不超过240字的短引文。找不到原文就标 NR 或留空，绝不补写。
3. 固定分类只能用下列代码；确实无法映射时用 UNMAPPED，并在 category_gaps 解释。多标签可并列。
4. 效果主张是作者用主观数据回答的问题或得出的结论；构念是被测的潜在概念；指标是构念可观察的主观属性/题项；Measure 是实际量表、问卷、访谈、评分、排序等工具。
5. 一次参与者研究可有多条 chain，但只建一个 evaluation。多个独立研究或不同样本分别建 evaluation。
6. JCSEE 对照审查状态：S=充分支持，P=部分支持，C=明确问题，NR=未报告/无法判断，NA=不适用。审查 U5 相关性、A2 效度依据、A3 可靠性依据、A4 对象情境描述、A6 设计分析适切性、A7 推理可追溯性、E1 记录充分性。状态必须由原文事实决定。
7. 不要把 AI 自动评价者当成人类评价主体。H6 单独出现时不是本综述的人类主观评价。
8. 领域边界：实体产品、机械、家具、工程方案归 D2；平面、品牌、字体、图像和传播材料归 D1；空间/建筑室内归 D4；服务流程归 D5；软件界面、交互系统和数字产品体验归 D6。论文用了网页或LLM界面不代表 D6，应按被设计对象归类。
9. 阶段与功能按论文实际工作流编码。F6 仅在 AI 根据评价/反馈修改已有方案时使用；单纯一次生成、并行生成或更换提示词不自动构成 F6。目标用户是 AI 辅助的设计工作流使用者，不等于被招募的评价者。

固定代码本：
""" + CODEBOOK


NOTE_PROMPT = """阅读以下论文页段，制作可供第二遍汇总的证据笔记。请返回一个 JSON 对象，字段：
paper_id, pages_read, context_facts（领域/阶段/AI功能/角色/目标用户，每项含 code,page,quote）, human_subjective_evaluations（数组；每项含 study_label,purpose/object/evaluator/source/setting/design/task/constraint 的代码及证据、sample、procedure、analysis、results、ethics、limitations、chains、audit_facts；chains 含 claim_quote/claim_summary/claim_type/construct_raw/indicator_raw/item_quote/dimension_code/indicator_code/instrument_raw/tool_family_codes/tool_origin_code/adaptation,response_scoring,validity_evidence,reliability_evidence,result_quote,effect_direction,pages），exclusion_facts，category_gaps。
若本页段没有人类主观评价，human_subjective_evaluations=[]。保留可能跨页衔接的信息，不要下最终结论。务必紧凑：同一构念的重复题项合并，最多保留12条代表性证据链，整份笔记不超过2500 tokens。

论文编号：{paper_id}
页段：
{text}
"""


FINAL_PROMPT = """把下面各页段的证据笔记合并成该论文的最终全文编码。去重并修正冲突；只有被短引文与页码支持的代码可以保留。不要因为摘要声称“用户评价”就推定正文实际实施了评价。

返回 JSON 对象，字段必须为：
paper_id,title,doi,year,reviewed_pages,scope_note,domain_codes,stage_codes,ai_function_codes,ai_role_codes,target_user_codes,context_summary,context_evidence,category_gaps,evaluations。
evaluations 每项字段必须为：eval_id,purpose_codes,object_codes,evaluator_codes,source_codes,setting_code,design_code,evaluation_stage_codes,task_codes,constraint_codes,sample_n,sample_description,recruitment,task,comparator,procedure,analysis,actual_results,limitations,ethics,evidence,audit,chains。
audit 必须正好有 U5,A2,A3,A4,A6,A7,E1 七项，每项含 standard,status,facts,reason,pages,quote。
chains 每项字段必须为：claim_quote,claim_summary,claim_type,construct_raw,indicator_raw,item_quote,dimension_code,indicator_code,instrument_raw,tool_family_codes,tool_origin_code,adaptation,response_scoring,validity_evidence,reliability_evidence,result_quote,effect_direction,pages。
如果全文没有符合标准的人类主观评价，evaluations=[]，但仍编码论文的设计领域、阶段和AI功能。所有未知文本字段用空字符串，未知代码字段用 [] 或 NR；不允许虚构。

论文首页信息（仅来自PDF）：
{first_pages}

证据笔记：
{notes}
"""


def post_json(messages, max_tokens=6500, retries=4):
    body = {
        "model": "qwen3-8b",
        "messages": messages,
        "temperature": 0.1,
        "top_p": 0.8,
        "seed": 20261025,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(ENDPOINT, data=raw, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=900) as resp:
                obj = json.loads(resp.read().decode("utf-8"))
            content = obj["choices"][0]["message"]["content"].strip()
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I | re.S)
            return json.loads(content), obj.get("usage", {})
        except Exception as exc:
            if attempt == retries - 1:
                raise
            time.sleep(3 * (attempt + 1))


def page_text(pages, page_numbers):
    by_num = {int(p["page"]): p.get("text", "") for p in pages}
    return "\n\n".join(f"===== PDF物理页 {n} =====\n{by_num.get(n, '')}" for n in page_numbers)


def select_pages(doc, packet):
    total = len(doc["pages"])
    chosen = set(range(1, min(4, total) + 1))
    candidates = {int(x) for x in packet.get("candidate_pages", [])}
    for n in candidates:
        chosen.add(n)
        if n > 1:
            chosen.add(n - 1)
        if n < total:
            chosen.add(n + 1)
    # Include the last substantive pages before references when candidate selection missed discussion.
    for p in doc["pages"]:
        text = p.get("text", "")
        if re.search(r"(?im)^\s*(discussion|conclusion|conclusions|limitations?)\s*$", text):
            n = int(p["page"])
            chosen.update(range(n, min(total, n + 3) + 1))
    return sorted(n for n in chosen if 1 <= n <= total)


def chunks_by_chars(doc, selected, limit=54000):
    chunks, current, size = [], [], 0
    by_num = {int(p["page"]): p.get("text", "") for p in doc["pages"]}
    for n in selected:
        text = by_num.get(n, "")
        if current and size + len(text) > limit:
            chunks.append(current)
            current, size = [], 0
        current.append(n)
        size += len(text)
    if current:
        chunks.append(current)
    return chunks


def derive_first_page_metadata(doc):
    first = "\n".join(p.get("text", "") for p in doc["pages"][:3])
    title = next((ln.strip() for ln in first.splitlines() if 18 <= len(ln.strip()) <= 240), "")
    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", first, re.I)
    years = [int(y) for y in re.findall(r"\b(20[0-2]\d)\b", first)]
    return {"title_hint": title, "doi_hint": doi_match.group(0).rstrip(".,;") if doi_match else "", "year_hint": min(years) if years else None}


def normalize(result, paper_id, selected):
    result["paper_id"] = paper_id
    result["reviewed_pages"] = selected
    for field in ["domain_codes", "stage_codes", "ai_function_codes", "ai_role_codes", "target_user_codes", "category_gaps", "evaluations"]:
        if not isinstance(result.get(field), list):
            result[field] = []
    if not isinstance(result.get("context_evidence"), list):
        value = result.get("context_evidence", "")
        result["context_evidence"] = [{"page": None, "quote": value}] if value else []
    result["category_gaps"] = [json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else str(x) for x in result["category_gaps"]]
    try:
        result["year"] = int(result.get("year")) if result.get("year") else None
    except (TypeError, ValueError):
        result["year"] = None
    for i, ev in enumerate(result["evaluations"], 1):
        ev["eval_id"] = f"{paper_id:03d}-E{i}"
        audit_by = {a.get("standard"): a for a in ev.get("audit", []) if isinstance(a, dict)}
        ev["audit"] = [audit_by.get(s, {"standard": s, "status": "NR", "facts": "", "reason": "", "pages": [], "quote": ""}) for s in STANDARDS]
    result["coding_source"] = "local_llm_fulltext_evidence_review"
    return result


def process_one(paper_id, force=False):
    final_path = OUT / f"paper_{paper_id:03d}.json"
    if final_path.exists() and not force:
        return "skip"
    doc = json.loads((EXTRACTED / f"{paper_id:03d}.json").read_text(encoding="utf-8"))
    packet = json.loads((PACKETS / f"{paper_id:03d}.json").read_text(encoding="utf-8"))
    selected = select_pages(doc, packet)
    chunks = chunks_by_chars(doc, selected)
    notes, usages = [], []
    for j, nums in enumerate(chunks, 1):
        note_path = OUT / f"paper_{paper_id:03d}_chunk_{j:02d}.json"
        if note_path.exists() and not force:
            note = json.loads(note_path.read_text(encoding="utf-8"))
        else:
            prompt = NOTE_PROMPT.format(paper_id=paper_id, text=page_text(doc["pages"], nums))
            note, usage = post_json([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=3200)
            note_path.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
            usages.append(usage)
        notes.append(note)
    meta = derive_first_page_metadata(doc)
    first_pages = page_text(doc["pages"], list(range(1, min(3, len(doc["pages"])) + 1)))
    final_prompt = FINAL_PROMPT.format(first_pages=first_pages[:18000], notes=json.dumps(notes, ensure_ascii=False))
    final, usage = post_json([{"role": "system", "content": SYSTEM}, {"role": "user", "content": final_prompt}], max_tokens=5200)
    usages.append(usage)
    final = normalize(final, paper_id, selected)
    final["pdf_path"] = doc.get("pdf_path", "")
    final["derived_metadata_hint"] = meta
    final["llm_usage"] = usages
    final_path.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"ok chunks={len(chunks)} evals={len(final['evaluations'])}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=125)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    log_path = OUT / "run.log"
    for paper_id in range(args.start, args.end + 1):
        if paper_id in {1, 2, 3, 4, 43, 44, 45, 46, 47, 85, 86, 87}:
            line = f"{paper_id:03d}\tmanual_fulltext_override\t0.0s"
            with log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            print(line, flush=True)
            continue
        t0 = time.time()
        try:
            status = process_one(paper_id, force=args.force)
            line = f"{paper_id:03d}\t{status}\t{time.time()-t0:.1f}s"
        except Exception as exc:
            line = f"{paper_id:03d}\tERROR {type(exc).__name__}: {exc}\t{time.time()-t0:.1f}s"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, flush=True)


if __name__ == "__main__":
    main()
