from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd

from config import ROOT, LABELS
from local_llm_recode import post_json, page_text

REVISED = ROOT / "revised_results"
EXTRACTED = ROOT / "extracted"
PACKETS = ROOT / "review_packets"
OUT = ROOT / "rq2_jcsee30" / "incomplete_review"
OUT.mkdir(parents=True, exist_ok=True)

SYSTEM = """你是系统综述全文证据链复核员。只依据提供的论文原文和候选评价案例背景，不使用外部知识。/no_think

纳入：研究实际让人对AI辅助设计的成果、过程、系统、协作、设计者状态或社会后果作主观感知、判断、态度、体验或价值评价。
排除：自动指标、客观性能、眼动/日志本身、模拟persona、作者讨论、引用既有研究、未来计划、只由研究者观察但没有人的主观评价。
每条纳入链必须至少有实际人类样本证据、被评价的构念/属性和实际测量方式；找不到则排除该候选。短引文必须逐字来自原文并带PDF物理页码。不要用UNMAPPED；确实无法落入固定36类时用EXCLUDE_CATEGORY_GAP并说明。"""

PROMPT = """复核论文中的一个待定评价案例。返回include或exclude；include时抽取原文中的人类主观评价链。

JSON格式：
{{"paper_id":整数,"eval_id":"原ID","decision":"include/exclude","reason":"中文短理由","chains":[{{"claim_quote":"原文效果主张或研究问题短引文；没有则NR","claim_summary":"中文归纳","construct_raw":"原文构念","indicator_raw":"原文指标或题项","instrument_raw":"实际测量工具","response_scoring":"量尺或评分","result_quote":"原文结果短引文或NR","pages":[页码]}}]}}

规则：
1. 同一构念的同义题项合并；不同主观属性分链；最多8条。
2. 不因为缺少显著性检验而排除；但只有样本/方法线索、没有具体感知构念或属性则排除。
3. construct、indicator、instrument必须使用论文原文术语，不能写UNMAPPED。
4. 自动指标和眼动数据不算；只有它们时排除。

候选案例背景：
{case}

相关全文页：
{pages}
"""


def select_pages(doc, packet, group: pd.DataFrame, max_pages=10):
    total = len(doc["pages"])
    priority = []
    for val in group.pages:
        for x in re.findall(r"\d+", str(val)):
            n=int(x)
            priority.extend(range(max(1,n-2), min(total,n+2)+1))
    for row in packet.get("page_scores", [])[:10]:
        priority.append(int(row["page"]))
    priority.extend([1,2,3])
    chosen=[]
    for n in priority:
        if 1 <= n <= total and n not in chosen:
            chosen.append(n)
        if len(chosen)>=max_pages:break
    return sorted(chosen)


def review_eval(pid: int, eid: str, group: pd.DataFrame, case: dict, force=False):
    safe=eid.replace('/','_')
    out=OUT/f"{safe}.json"
    if out.exists() and not force:return "skip"
    doc=json.loads((EXTRACTED/f"{pid:03d}.json").read_text(encoding="utf-8"))
    packet=json.loads((PACKETS/f"{pid:03d}.json").read_text(encoding="utf-8"))
    selected=select_pages(doc,packet,group)
    ctx={"eval_id":eid,"sample":case.get("sample_description",""),"task":case.get("task",""),"procedure":case.get("procedure",""),"analysis":case.get("analysis",""),"results":case.get("actual_results","")}
    prompt=PROMPT.format(case=json.dumps(ctx,ensure_ascii=False),pages=page_text(doc["pages"],selected))
    raw,usage=post_json([{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],max_tokens=1800,retries=3)
    raw["reviewed_pages"]=selected
    raw["usage"]=usage
    out.write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding="utf-8")
    return f"ok pages={len(selected)} decision={raw.get('decision','?')} chains={len(raw.get('chains',[]))}"


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--start",type=int,default=1);ap.add_argument("--end",type=int,default=125);ap.add_argument("--force",action="store_true");args=ap.parse_args()
    chains=pd.read_csv(REVISED/"evidence_chains_revised.csv",dtype=str).fillna("")
    inc=chains[(chains.dimension_code=="UNMAPPED")|(chains.indicator_code=="UNMAPPED")]
    cases=pd.read_csv(REVISED/"evaluation_cases.csv",dtype=str).fillna("")
    case_idx=cases.set_index("eval_id").to_dict("index")
    for (pid_s,eid),g in inc.groupby(["paper_id","eval_id"]):
        pid=int(pid_s)
        if not args.start<=pid<=args.end:continue
        t=time.time()
        try:msg=review_eval(pid,eid,g,case_idx.get(eid,{}),args.force)
        except Exception as e:msg=f"ERROR {type(e).__name__}: {e}"
        print(f"{pid:03d}\t{eid}\t{msg}\t{time.time()-t:.1f}s",flush=True)

if __name__=="__main__":main()
