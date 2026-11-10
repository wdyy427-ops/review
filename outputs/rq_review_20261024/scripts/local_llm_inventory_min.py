from __future__ import annotations

import argparse
import json
import time

from config import LABELS
from local_llm_recode import EXTRACTED, PACKETS, OUT, post_json, page_text, derive_first_page_metadata, normalize
from local_llm_recode_fast import select_compact


MANUAL = {1, 2, 3, 4, 43, 44, 45, 46, 47, 85, 86, 87}
SYSTEM = """你是系统综述全文证据筛查员。只依据提供的论文原文页，不使用旧表或外部知识。判断论文是否实际收集了人的主观感知、判断、态度、体验或价值证据。纯自动指标、客观性能、日志、模拟persona、作者讨论、引用既有研究、未来研究计划均不算。短引文必须逐字来自原文。/no_think"""
PROMPT = """返回紧凑JSON：
{{paper_id,title,doi,year,target_user_codes,context_summary,human_evaluations,exclusion_facts}}

human_evaluations中每个独立人类样本/研究只含study_label,sample_n,pages,quote。pages为PDF物理页码数组；quote是不超过35词的原文短引文，必须能证明实际招募人并收集主观评价。同一参与者研究不要因多个指标拆成多个研究，最多6个。没有合格研究则human_evaluations=[]。

target_user_codes只指AI辅助工作流的预期使用者，最多3个：{targets}
所有说明文本各不超过35词，整个JSON不超过900 tokens。

论文编号：{pid}
全文逐页筛查后选出的高相关原文页：
{pages}
"""


def process(pid, force=False):
    path = OUT / f"paper_{pid:03d}.json"
    if path.exists() and not force:
        return "skip"
    doc = json.loads((EXTRACTED / f"{pid:03d}.json").read_text(encoding="utf-8"))
    packet = json.loads((PACKETS / f"{pid:03d}.json").read_text(encoding="utf-8"))
    selected = select_compact(doc, packet, max_pages=15)
    raw = page_text(doc["pages"], selected)
    targets = "; ".join(f"{k}={v}" for k,v in LABELS["target_user"].items())
    prompt = PROMPT.format(targets=targets, pid=pid, pages=raw)
    inv, usage = post_json([{"role":"system","content":SYSTEM},{"role":"user","content":prompt}], max_tokens=1200, retries=2)
    result = {
        "paper_id": pid, "title": inv.get("title", ""), "doi": inv.get("doi", ""), "year": inv.get("year"),
        "reviewed_pages": selected, "scope_note": "全文逐页规则筛查后，对高相关证据页进行人类主观评价清点。",
        "domain_codes": [], "stage_codes": [], "ai_function_codes": [], "ai_role_codes": [],
        "target_user_codes": inv.get("target_user_codes", []), "context_summary": inv.get("context_summary", ""),
        "context_evidence": [], "category_gaps": [], "exclusion_facts": inv.get("exclusion_facts", []),
        "inventory_human_evaluations": inv.get("human_evaluations", []), "evaluations": [],
        "pdf_path": doc.get("pdf_path", ""), "derived_metadata_hint": derive_first_page_metadata(doc),
        "llm_usage": [usage], "coding_source": "local_llm_minimal_human_evaluation_inventory",
    }
    result = normalize(result, pid, selected)
    result["inventory_human_evaluations"] = inv.get("human_evaluations", [])
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"ok studies={len(result['inventory_human_evaluations'])} pages={len(selected)}"


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--start",type=int,default=1);ap.add_argument("--end",type=int,default=125);ap.add_argument("--force",action="store_true");args=ap.parse_args()
    log=OUT/"min_inventory.log"
    for pid in range(args.start,args.end+1):
        if pid in MANUAL: line=f"{pid:03d}\tmanual_fulltext_override\t0.0s"
        else:
            t=time.time()
            try: line=f"{pid:03d}\t{process(pid,args.force)}\t{time.time()-t:.1f}s"
            except Exception as exc: line=f"{pid:03d}\tERROR {type(exc).__name__}: {exc}\t{time.time()-t:.1f}s"
        with log.open("a",encoding="utf-8") as f:f.write(line+"\n")
        print(line,flush=True)


if __name__=="__main__":main()
