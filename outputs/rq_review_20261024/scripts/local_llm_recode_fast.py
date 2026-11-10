from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from local_llm_recode import (
    EXTRACTED, PACKETS, OUT, SYSTEM, FINAL_PROMPT, post_json, page_text,
    derive_first_page_metadata, normalize,
)


MANUAL = {1, 2, 3, 4, 43, 44, 45, 46, 47, 85, 86, 87}


def select_compact(doc, packet, max_pages=16):
    total = len(doc["pages"])
    chosen = set(range(1, min(3, total) + 1))
    ranked = [int(x["page"]) for x in packet.get("page_scores", [])]
    for n in ranked[:max_pages]:
        chosen.add(n)
    # Methods often start just before a high-scoring measures page.
    for n in ranked[:6]:
        if n > 1:
            chosen.add(n - 1)
    for p in doc["pages"]:
        txt = p.get("text", "")
        if re.search(r"(?im)^\s*(discussion|conclusion|conclusions|limitations?)\s*$", txt):
            n = int(p["page"])
            chosen.add(n)
            if n < total:
                chosen.add(n + 1)
    # Keep the prompt bounded while retaining the highest-ranked evidence pages.
    priority = list(range(1, min(3, total) + 1)) + ranked[:max_pages]
    tail = sorted(chosen - set(priority))
    ordered = list(dict.fromkeys(priority + tail))
    by_num = {int(p["page"]): p.get("text", "") for p in doc["pages"]}
    kept, chars = [], 0
    for n in ordered:
        size = len(by_num.get(n, ""))
        if kept and chars + size > 70000:
            continue
        kept.append(n)
        chars += size
        if len(kept) >= 22:
            break
    return sorted(kept)


DIRECT = """下面不是旧表，而是程序从全文逐页扫描后选出的高相关证据页，并附有首页。直接完成最终全文编码。必须以页码和短引文为依据；如果所给页不足以判断，标NR或留空。不要输出页段笔记。

{pages}
"""


def process(pid, force=False):
    final_path = OUT / f"paper_{pid:03d}.json"
    if final_path.exists() and not force:
        return "skip"
    doc = json.loads((EXTRACTED / f"{pid:03d}.json").read_text(encoding="utf-8"))
    packet = json.loads((PACKETS / f"{pid:03d}.json").read_text(encoding="utf-8"))
    selected = select_compact(doc, packet)
    first = page_text(doc["pages"], list(range(1, min(3, len(doc["pages"])) + 1)))
    evidence = page_text(doc["pages"], selected)
    prompt = FINAL_PROMPT.format(first_pages=first[:16000], notes=DIRECT.format(pages=evidence))
    result, usage = post_json([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=4200)
    result = normalize(result, pid, selected)
    result["pdf_path"] = doc.get("pdf_path", "")
    result["derived_metadata_hint"] = derive_first_page_metadata(doc)
    result["llm_usage"] = [usage]
    result["coding_source"] = "local_llm_fulltext_page_screen_and_evidence_review"
    final_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"ok pages={len(selected)} evals={len(result['evaluations'])}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=125)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    log = OUT / "fast_run.log"
    for pid in range(args.start, args.end + 1):
        if pid in MANUAL:
            line = f"{pid:03d}\tmanual_fulltext_override\t0.0s"
        else:
            t0 = time.time()
            try:
                line = f"{pid:03d}\t{process(pid, args.force)}\t{time.time()-t0:.1f}s"
            except Exception as exc:
                line = f"{pid:03d}\tERROR {type(exc).__name__}: {exc}\t{time.time()-t0:.1f}s"
        with log.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, flush=True)


if __name__ == "__main__":
    main()
