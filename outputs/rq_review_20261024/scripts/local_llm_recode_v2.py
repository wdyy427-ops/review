from __future__ import annotations

import argparse
import json
import re
import time

from config import LABELS, STANDARDS
from local_llm_recode import EXTRACTED, PACKETS, OUT, post_json, page_text, derive_first_page_metadata, normalize
from local_llm_recode_fast import select_compact


MANUAL = {1, 2, 3, 4, 43, 44, 45, 46, 47, 85, 86, 87}


def codes(fields):
    return "\n".join(f"{f}: " + "; ".join(f"{k}={v}" for k, v in LABELS[f].items()) for f in fields)


SYSTEM = """你是系统综述的全文证据编码员。只依据用户提供的论文原文，不使用旧表或外部知识。仅纳入实际由人类提供的主观感知、判断、态度、体验或价值证据。纯自动指标、客观性能、日志和作者无数据的讨论均排除。每个判断必须有PDF物理页码和短引文；没有证据就留空或NR。/no_think"""


INVENTORY_PROMPT = """先做稀疏的论文与研究清点，不抽取详细题项。返回JSON：
{{paper_id,title,doi,year,domain_codes,stage_codes,ai_function_codes,ai_role_codes,target_user_codes,context_summary,context_evidence,human_evaluations,exclusion_facts,category_gaps}}

human_evaluations中每个独立样本/研究只写：study_label,sample_n,purpose_codes,object_codes,evaluator_codes,source_codes,setting_code,design_code,evaluation_stage_codes,pages,quote。

硬性稀疏规则：domain最多2个；stage和ai_function各最多4个；ai_role最多2个；target_user最多3个；每个研究purpose最多2个、object最多3个、evaluator最多3个、source最多4个。绝不能为了“覆盖全面”列出全部代码。只有原文直接支持的代码才保留。评价者和AI辅助目标用户是不同概念。实体产品归D2，平面/图像/品牌归D1，空间归D4，服务归D5，数字界面与交互产品归D6。

如果全文没有实际收集人类主观评价，human_evaluations=[]，并在exclusion_facts说明自动指标或未来工作。短引文必须逐字来自下列页面。所有summary/quote文本各不超过45词，整个JSON尽量短。

代码本：
{codebook}

论文编号：{pid}
原文证据页：
{pages}
"""


DETAIL_PROMPT = """根据原文证据页和已经确认的单个研究清点，为这一个human_evaluation形成详细评价案例。只返回JSON：{{evaluations:[一个案例]}}。

每个evaluation字段：study_label,purpose_codes,object_codes,evaluator_codes,source_codes,setting_code,design_code,evaluation_stage_codes,task_codes,constraint_codes,sample_n,sample_description,recruitment,task,comparator,procedure,analysis,actual_results,limitations,ethics,evidence,audit,chains。

audit必须正好含U5,A2,A3,A4,A6,A7,E1，每项含standard,status,facts,reason,pages,quote。facts和reason各不超过25词，quote不超过35词。状态只能S/P/C/NR/NA：S充分支持，P部分支持，C明确问题，NR未报告/无法判断，NA不适用。

chains记录“效果主张→构念→指标→测量工具”，每条字段：claim_quote,claim_summary,claim_type,construct_raw,indicator_raw,item_quote,dimension_code,indicator_code,instrument_raw,tool_family_codes,tool_origin_code,adaptation,response_scoring,validity_evidence,reliability_evidence,result_quote,effect_direction,pages。合并同一构念下重复题项，最多6条代表性链。每个文本字段不超过35词。只有人的主观证据可建链。无法映射固定指标时用UNMAPPED，不得自建二级类别。

每个研究purpose最多2个、object最多3个、evaluator最多3个、source最多4个；task和constraint只编码原文明示内容。不要列出整套代码。

代码本：
{codebook}

研究清点：
{inventory}

原文证据页：
{pages}
"""


CONTEXT_FIELDS = ["domain", "stage", "ai_function", "ai_role", "target_user", "purpose", "object", "evaluator", "source", "setting", "design"]
DETAIL_FIELDS = ["purpose", "object", "evaluator", "source", "setting", "design", "stage", "task", "constraint", "dimension", "indicator", "tool_family", "tool_origin", "claim_type"]


def process(pid, force=False, inventory_only=False):
    final_path = OUT / f"paper_{pid:03d}.json"
    if final_path.exists() and not force:
        return "skip"
    doc = json.loads((EXTRACTED / f"{pid:03d}.json").read_text(encoding="utf-8"))
    packet = json.loads((PACKETS / f"{pid:03d}.json").read_text(encoding="utf-8"))
    selected = select_compact(doc, packet, max_pages=15)
    raw_pages = page_text(doc["pages"], selected)
    inv_prompt = INVENTORY_PROMPT.format(codebook=codes(CONTEXT_FIELDS), pid=pid, pages=raw_pages)
    inventory, usage1 = post_json([{"role": "system", "content": SYSTEM}, {"role": "user", "content": inv_prompt}], max_tokens=2200)
    evaluations = []
    usage = [usage1]
    if inventory.get("human_evaluations") and not inventory_only:
        for study in inventory.get("human_evaluations", []):
            detail_prompt = DETAIL_PROMPT.format(codebook=codes(DETAIL_FIELDS), inventory=json.dumps(study, ensure_ascii=False), pages=raw_pages)
            detail, usage2 = post_json([{"role": "system", "content": SYSTEM}, {"role": "user", "content": detail_prompt}], max_tokens=3000)
            if isinstance(detail, dict):
                evaluations.extend(detail.get("evaluations", [])[:1])
            usage.append(usage2)
    result = {
        "paper_id": pid,
        "title": inventory.get("title", ""), "doi": inventory.get("doi", ""), "year": inventory.get("year"),
        "scope_note": "全文逐页关键词筛查后，对高相关证据页进行两阶段语义编码；无证据字段保留NR。",
        "domain_codes": inventory.get("domain_codes", []), "stage_codes": inventory.get("stage_codes", []),
        "ai_function_codes": inventory.get("ai_function_codes", []), "ai_role_codes": inventory.get("ai_role_codes", []),
        "target_user_codes": inventory.get("target_user_codes", []), "context_summary": inventory.get("context_summary", ""),
        "context_evidence": inventory.get("context_evidence", []), "category_gaps": inventory.get("category_gaps", []),
        "exclusion_facts": inventory.get("exclusion_facts", []), "inventory_human_evaluations": inventory.get("human_evaluations", []), "evaluations": evaluations,
    }
    result = normalize(result, pid, selected)
    result["pdf_path"] = doc.get("pdf_path", "")
    result["derived_metadata_hint"] = derive_first_page_metadata(doc)
    result["llm_usage"] = usage
    result["coding_source"] = "local_llm_two_stage_evidence_review"
    final_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"ok pages={len(selected)} evals={len(result['evaluations'])}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=125)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--inventory-only", action="store_true")
    args = ap.parse_args()
    log = OUT / "v2_run.log"
    for pid in range(args.start, args.end + 1):
        if pid in MANUAL:
            line = f"{pid:03d}\tmanual_fulltext_override\t0.0s"
        else:
            t0 = time.time()
            try:
                line = f"{pid:03d}\t{process(pid, args.force, args.inventory_only)}\t{time.time()-t0:.1f}s"
            except Exception as exc:
                line = f"{pid:03d}\tERROR {type(exc).__name__}: {exc}\t{time.time()-t0:.1f}s"
        with log.open("a", encoding="utf-8") as f:
            f.write(line+"\n")
        print(line, flush=True)


if __name__ == "__main__":
    main()
