from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import revised_pipeline as rp  # noqa: E402
from config import LABELS  # noqa: E402


ROOT = SCRIPT_DIR.parent
SRC = ROOT / "revised_results"
OUT = ROOT / "rq3_g1_g7_rebuilt"
OUT.mkdir(parents=True, exist_ok=True)


FINAL_LABELS = {
    "purpose": LABELS["purpose"],
    "domain": LABELS["domain"],
    "stage": LABELS["stage"],
    "object": {
        "O1": "设计成果或解决方案",
        "O2": "设计任务或工作流程",
        "O3": "AI辅助设计系统或界面",
        "O4": "人的状态或能力",
        "O5": "人机协作关系",
    },
    "evaluator": {
        "V1": "设计任务执行者",
        "V2": "设计成果使用者",
        "V3": "外部领域专家",
        "V4": "一般公众／非目标人群",
        "V5": "内部研究者／系统开发者",
    },
    "target_user": {
        "U1": "专业设计从业者",
        "U2": "设计学习者／新手设计者",
        "U3": "非专业创作者",
    },
    "ai_function": LABELS["ai_function"],
    "dimension": LABELS["dimension"],
    "indicator": LABELS["indicator"],
    "tool": rp.TOOL_LABELS,
}


FEATURE_GROUPS = {
    "G1_评价目的": ["purposes"],
    "G2_设计领域": ["domains"],
    "G3_设计阶段": ["stages"],
    "G4_评价对象": ["objects_g4"],
    "G5_评价主体": ["evaluators_g5"],
    "G6_目标用户": ["target_users_g6"],
    "G7_AI功能": ["ai_functions"],
}


def codes(value) -> list[str]:
    return [x for x in str(value or "").split(";") if x and x not in {"nan", "NR", "NA", "UNMAPPED"}]


def join_codes(values) -> str:
    return ";".join(dict.fromkeys(values))


def text_of(row, cols) -> str:
    return " | ".join(str(row.get(c, "") or "") for c in cols).lower()


def recode_object(row) -> tuple[str, str]:
    """Code the direct evaluand of a chain; do not retain old O6/O7 as objects."""
    dim = str(row.get("dimension_code", ""))
    ind = str(row.get("indicator_code", ""))
    text = text_of(
        row,
        ["claim_quote", "claim_summary", "construct_raw", "indicator_raw", "item_quote", "instrument_raw"],
    )

    # Strong chain-level referents. These rules are also retained in the output
    # so every recode can be audited.
    if ind in {"D6", "D7", "D8"} or re.search(
        r"human.?ai collabor|co-?creat|共同创作|人机协作|主体性|agency|ownership|role division|贡献公平|共同理解|coordination|协同|沟通|冲突",
        text,
    ):
        return "O5", "人机关系／协作构念直接指向"
    if ind in {"D1", "D2", "D3", "D4", "D5"} or re.search(
        r"usability|easy to use|ease of use|system interface|interface usability|transparen|explainab|controllab|trust in (?:the )?(?:ai|system|tool)|系统易用|界面|可解释|透明度|可控性|系统信任",
        text,
    ):
        return "O3", "AI系统／界面构念直接指向"
    if dim == "B" or re.search(
        r"workflow|design process|task process|time efficiency|workload|iteration|decision support|handoff|过程连续|工作流程|设计过程|任务效率|工作负荷|迭代效率|决策支持|交接效率",
        text,
    ):
        return "O2", "设计任务／流程构念直接指向"
    if dim == "C" or re.search(
        r"inspiration|knowledge gain|self.?efficacy|engagement|immersion|enjoyment|reflection|fixation|capabilit|cognitive|mental state|灵感|知识获得|自我效能|沉浸|愉悦|反思|固着|能力扩展|认知状态",
        text,
    ):
        return "O4", "人的状态／能力构念直接指向"
    if dim == "A":
        return "O1", "设计成果质量构念直接指向"

    # Social/contextual effects still evaluate the solution unless the text
    # explicitly attributes fit or consequences to the workflow/system.
    if dim == "E":
        if re.search(r"system|tool|interface|平台|系统|工具", text):
            return "O3", "社会情境效应明确归属于AI系统"
        if re.search(r"workflow|process|组织流程|工作流程|设计过程", text):
            return "O2", "社会情境效应明确归属于工作流程"
        return "O1", "设计成果在使用／社会情境中的效应"

    # Unmapped chains: use the most explicit referent in the raw text, then the
    # old object tags only as a last-resort audit aid.
    patterns = [
        ("O5", r"human.?ai|co-?creat|collabor|人机|协作|共同创作"),
        ("O3", r"system|tool|interface|platform|系统|工具|界面|平台"),
        ("O2", r"workflow|process|task|工作流|过程|任务"),
        ("O4", r"designer(?:'s)? (?:state|ability|cognition)|participant(?:'s)? (?:feeling|experience)|设计者.*(?:状态|能力|认知|情感)"),
        ("O1", r"design solution|design outcome|artifact|product|prototype|方案|设计成果|产品|原型"),
    ]
    for code, pat in patterns:
        if re.search(pat, text):
            return code, "未映射构念按原文直接指向判定"
    old = set(codes(row.get("objects")))
    for old_code, new_code in [("O1", "O1"), ("O2", "O2"), ("O3", "O3"), ("O5", "O4"), ("O4", "O5")]:
        if old_code in old:
            return new_code, "原文不足，按旧对象标签保守回退"
    return "", "无法判定"


def recode_evaluators(row, ev) -> tuple[str, str]:
    old = set(codes(row.get("evaluators")))
    sources = set(codes(row.get("sources")))
    text = text_of(
        {**row.to_dict(), **(ev or {})},
        ["sample_description", "recruitment", "task", "procedure", "instrument_raw", "claim_summary"],
    )
    out: list[str] = []
    why: list[str] = []

    # Direct mappings where the old code already described the evaluation role.
    if "V2" in old:
        out.append("V1"); why.append("旧V2学生／新手实际执行设计任务")
    if "V3" in old:
        out.append("V2"); why.append("旧V3为设计成果使用者／目标终端用户")
    if "V4" in old:
        out.append("V4"); why.append("旧V4为一般公众／众包非目标样本")
    if "V6" in old:
        out.append("V5"); why.append("旧V6为研究团队自评")

    performs = bool(re.search(
        r"participants? (?:used|created|designed|generated|completed|performed|worked with|interacted with)|使用.*(?:系统|工具)|完成.*(?:设计|任务)|进行.*设计|参与.*共同设计|co-?design task",
        text,
    ))
    judges = bool(re.search(
        r"experts? (?:rated|evaluated|assessed|judged|scored|reviewed)|expert evaluation|expert rating|专家.*(?:评价|评分|评审)|评委|domain experts?",
        text,
    ))
    outcome_user = bool(re.search(
        r"consumer|customer|end user|resident|patient|passenger|driver|pedestrian|service recipient|消费者|顾客|终端用户|居民|患者|乘客|驾驶员|行人",
        text,
    ))

    if "V1" in old:
        if performs:
            out.append("V1"); why.append("专业人员直接执行设计／操作系统")
        if judges or ("H2" in sources and not performs):
            out.append("V3"); why.append("专业人员作为外部领域评审者")
        if not performs and not judges:
            # H1 with process/system experience is more consistent with a task
            # executor; otherwise retain the conservative expert interpretation.
            if "H1" in sources and str(row.get("dimension_code", "")) in {"B", "C", "D"}:
                out.append("V1"); why.append("专业人员报告任务／系统使用体验")
            else:
                out.append("V3"); why.append("专业身份但任务角色未明，保守记外部专家")

    if "V5" in old:
        if performs:
            out.append("V1"); why.append("组织相关人员直接执行设计任务")
        elif outcome_user:
            out.append("V2"); why.append("客户／相关人以成果使用者身份评价")
        else:
            out.append("V3"); why.append("客户／组织相关人以领域判断者身份评价")

    return join_codes(out), "；".join(dict.fromkeys(why)) if why else "未报告／无法判断"


def recode_target_users(value) -> str:
    old = set(codes(value))
    # Only direct users of the AI-assisted design workflow are retained.
    return join_codes([c for c in ["U1", "U2", "U3"] if c in old])


def recode_context(chains: pd.DataFrame, evals: pd.DataFrame) -> pd.DataFrame:
    ev_lookup = evals.set_index("eval_id").to_dict("index")
    rows = []
    for _, row in chains.iterrows():
        obj, obj_rule = recode_object(row)
        evaluators, eval_rule = recode_evaluators(row, ev_lookup.get(row.eval_id, {}))
        out = row.to_dict()
        out.update(
            {
                "objects_g4": obj,
                "object_recode_rule": obj_rule,
                "evaluators_g5": evaluators,
                "evaluator_recode_rule": eval_rule,
                "target_users_g6": recode_target_users(row.get("target_users")),
            }
        )
        rows.append(out)
    return pd.DataFrame(rows)


def bh_adjust(values):
    p = np.asarray(values, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.minimum.accumulate((ranked * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    out = np.empty_like(adjusted)
    out[order] = np.minimum(1, adjusted)
    return out


def association_table(chains, instances, eligible_col, tier_name):
    base = chains[chains[eligible_col] == 1].copy()
    inst = instances[instances[eligible_col] == 1].copy()
    context_fields = {
        "G1_评价目的": ("purposes", FINAL_LABELS["purpose"]),
        "G2_设计领域": ("domains", FINAL_LABELS["domain"]),
        "G3_设计阶段": ("stages", FINAL_LABELS["stage"]),
        "G4_评价对象": ("objects_g4", FINAL_LABELS["object"]),
        "G5_评价主体": ("evaluators_g5", FINAL_LABELS["evaluator"]),
        "G6_目标用户": ("target_users_g6", FINAL_LABELS["target_user"]),
        "G7_AI功能": ("ai_functions", FINAL_LABELS["ai_function"]),
    }
    outcomes = {
        "评价维度": (base, "dimension_code", FINAL_LABELS["dimension"], "chain_id"),
        "主观指标": (base, "indicator_code", FINAL_LABELS["indicator"], "chain_id"),
        "测量工具": (inst.merge(base[["chain_id"] + list(FEATURE_GROUPS.values())[0]], on="chain_id", how="inner") if False else inst, "tool_code", FINAL_LABELS["tool"], "measure_instance_id"),
    }
    rows = []
    # Dimension and indicator operate on chains.
    for gname, (col, labels) in context_fields.items():
        for ccode, clabel in labels.items():
            x = base[col].fillna("").map(lambda z: ccode in codes(z))
            if x.sum() < 3 or (~x).sum() < 3:
                continue
            for target_name, tcol, tlabels in [
                ("评价维度", "dimension_code", FINAL_LABELS["dimension"]),
                ("主观指标", "indicator_code", FINAL_LABELS["indicator"]),
            ]:
                for ocode, olabel in tlabels.items():
                    y = base[tcol].astype(str) == ocode
                    if y.sum() < 3 or (~y).sum() < 3:
                        continue
                    a = int((x & y).sum()); b = int((x & ~y).sum()); c = int((~x & y).sum()); d = int((~x & ~y).sum())
                    odds, p = fisher_exact([[a, b], [c, d]])
                    n = a + b + c + d
                    phi = (a*d-b*c)/math.sqrt((a+b)*(c+d)*(a+c)*(b+d)) if min(a+b,c+d,a+c,b+d)>0 else 0
                    cond = a/(a+b); baseline=(a+c)/n
                    rows.append({"analysis_tier":tier_name,"feature_group":gname,"context_code":ccode,"context_label":clabel,"target":target_name,"target_code":ocode,"target_label":olabel,"a_both":a,"context_n":a+b,"target_n":a+c,"n":n,"conditional_probability":cond,"baseline_probability":baseline,"lift":cond/baseline if baseline else np.nan,"odds_ratio":odds,"cramers_v_signed":phi,"p_value":p})

    # Tool outcomes operate on measure instances but inherit context from chain.
    if len(inst):
        join_cols = ["chain_id"] + sorted({c for cols in FEATURE_GROUPS.values() for c in cols})
        tool_data = inst.drop(columns=[c for c in join_cols if c != "chain_id" and c in inst.columns], errors="ignore").merge(base[join_cols], on="chain_id", how="inner")
        for gname, (col, labels) in context_fields.items():
            for ccode, clabel in labels.items():
                x = tool_data[col].fillna("").map(lambda z: ccode in codes(z))
                if x.sum() < 3 or (~x).sum() < 3:
                    continue
                for ocode, olabel in FINAL_LABELS["tool"].items():
                    y = tool_data.tool_code.astype(str) == ocode
                    if y.sum() < 3 or (~y).sum() < 3:
                        continue
                    a = int((x & y).sum()); b = int((x & ~y).sum()); c = int((~x & y).sum()); d = int((~x & ~y).sum())
                    odds, p = fisher_exact([[a,b],[c,d]])
                    n=a+b+c+d
                    phi=(a*d-b*c)/math.sqrt((a+b)*(c+d)*(a+c)*(b+d)) if min(a+b,c+d,a+c,b+d)>0 else 0
                    cond=a/(a+b); baseline=(a+c)/n
                    rows.append({"analysis_tier":tier_name,"feature_group":gname,"context_code":ccode,"context_label":clabel,"target":"测量工具类别","target_code":ocode,"target_label":olabel,"a_both":a,"context_n":a+b,"target_n":a+c,"n":n,"conditional_probability":cond,"baseline_probability":baseline,"lift":cond/baseline if baseline else np.nan,"odds_ratio":odds,"cramers_v_signed":phi,"p_value":p})
    out = pd.DataFrame(rows)
    if len(out):
        out["q_value_bh"] = bh_adjust(out.p_value.values)
        out["evidence_grade"] = np.select([(out.q_value_bh<=.05)&(out.a_both>=5),(out.q_value_bh<=.10)&(out.a_both>=3)],["较强","探索性"],default="有限")
        out=out.sort_values(["q_value_bh","cramers_v_signed"],ascending=[True,False])
    return out


def main():
    chains = pd.read_csv(SRC / "evidence_chains_revised.csv", encoding="utf-8-sig")
    evals = pd.read_csv(SRC / "evaluation_cases.csv", encoding="utf-8-sig")
    instances = pd.read_csv(SRC / "measure_instances.csv", encoding="utf-8-sig")
    recoded = recode_context(chains, evals)
    recoded.to_csv(OUT / "evidence_chains_context_g1_g7.csv", index=False, encoding="utf-8-sig")

    # Make the requested seven groups the only contextual feature groups.
    rp.FEATURE_GROUPS = FEATURE_GROUPS

    main_chains = recoded[(recoded.model_eligible_main == 1) & recoded.dimension_code.isin(LABELS["dimension"])].copy()
    expanded_chains = recoded[(recoded.model_eligible_sensitivity == 1) & recoded.dimension_code.isin(LABELS["dimension"])].copy()

    chain_context_cols = ["chain_id"] + sorted({c for cols in FEATURE_GROUPS.values() for c in cols})
    main_instances = instances[(instances.model_eligible_main == 1) & instances.tool_code.isin(rp.TOOL_LABELS)].copy()
    expanded_instances = instances[(instances.model_eligible_sensitivity == 1) & instances.tool_code.isin(rp.TOOL_LABELS)].copy()
    for name, frame in [("main", main_instances), ("expanded", expanded_instances)]:
        base = main_chains if name == "main" else expanded_chains
        missing = [c for c in chain_context_cols if c != "chain_id" and c in frame.columns]
        frame.drop(columns=missing, inplace=True, errors="ignore")
        merged = frame.merge(base[chain_context_cols], on="chain_id", how="inner")
        if name == "main":
            main_instances = merged
        else:
            expanded_instances = merged

    main_chains.to_csv(OUT / "main_normative_chains_g1_g7.csv", index=False, encoding="utf-8-sig")
    expanded_chains.to_csv(OUT / "expanded_normative_chains_g1_g7.csv", index=False, encoding="utf-8-sig")
    main_instances.to_csv(OUT / "main_normative_measure_instances_g1_g7.csv", index=False, encoding="utf-8-sig")
    expanded_instances.to_csv(OUT / "expanded_normative_measure_instances_g1_g7.csv", index=False, encoding="utf-8-sig")

    comparisons=[]; weights=[]; metas=[]
    for tier_name, tier_chains, tier_instances in [
        ("主要规范集",main_chains,main_instances),
        ("扩展规范集",expanded_chains,expanded_instances),
    ]:
        jobs=[
            (tier_chains,"dimension_code","评价维度",[]),
            (tier_chains[tier_chains.indicator_code.isin(LABELS["indicator"])],"indicator_code","主观指标",["dimension_code"]),
            (tier_instances,"tool_code","测量工具类别",["dimension_code","indicator_code"]),
        ]
        for df,target_col,target_name,fixed in jobs:
            comp,imp,meta=rp.model_and_weights(df,target_col,target_name,fixed)
            if len(comp):
                comp.insert(0,"analysis_tier",tier_name); comparisons.append(comp)
            if len(imp):
                imp.insert(0,"analysis_tier",tier_name); weights.append(imp)
            meta["analysis_tier"]=tier_name; metas.append(meta)

    model_comp=pd.concat(comparisons,ignore_index=True) if comparisons else pd.DataFrame()
    weight_df=pd.concat(weights,ignore_index=True) if weights else pd.DataFrame()
    model_comp.to_csv(OUT / "rq3_model_comparison_g1_g7.csv",index=False,encoding="utf-8-sig")
    weight_df.to_csv(OUT / "rq3_label_group_weights_g1_g7.csv",index=False,encoding="utf-8-sig")

    assoc=pd.concat([
        association_table(recoded,instances,"model_eligible_main","主要规范集"),
        association_table(recoded,instances,"model_eligible_sensitivity","扩展规范集"),
    ],ignore_index=True)
    assoc.to_csv(OUT / "rq3_context_associations_g1_g7.csv",index=False,encoding="utf-8-sig")

    # The five object classes are semantically close to the five outcome
    # dimensions. Quantify how much dimension prediction changes when G4 is
    # omitted so the paper can distinguish useful routing information from
    # possible construct overlap.
    rp.FEATURE_GROUPS = {k: v for k, v in FEATURE_GROUPS.items() if k != "G4_评价对象"}
    no_object_parts = []
    for tier_name, tier_chains in [("主要规范集", main_chains), ("扩展规范集", expanded_chains)]:
        comp, _, meta = rp.model_and_weights(tier_chains, "dimension_code", "评价维度（不含G4）", [])
        if len(comp):
            comp.insert(0, "analysis_tier", tier_name)
            no_object_parts.append(comp)
    no_object = pd.concat(no_object_parts, ignore_index=True) if no_object_parts else pd.DataFrame()
    no_object.to_csv(OUT / "rq3_dimension_without_g4_sensitivity.csv", index=False, encoding="utf-8-sig")
    rp.FEATURE_GROUPS = FEATURE_GROUPS

    # QC summaries make the recoding and missingness auditable.
    qc=[]
    for tier_name,frame in [("全部证据链",recoded),("主要规范集",main_chains),("扩展规范集",expanded_chains)]:
        for group,cols in FEATURE_GROUPS.items():
            col=cols[0]
            qc.append({"analysis_tier":tier_name,"feature_group":group,"field":col,"n_rows":len(frame),"n_present":int(frame[col].fillna("").astype(str).str.strip().ne("").sum()),"percent_present":float(frame[col].fillna("").astype(str).str.strip().ne("").mean())})
    pd.DataFrame(qc).to_csv(OUT / "rq3_context_completeness_g1_g7.csv",index=False,encoding="utf-8-sig")

    summary={
        "feature_groups":FEATURE_GROUPS,
        "labels":FINAL_LABELS,
        "all_chains":int(len(recoded)),
        "main_chains":int(len(main_chains)),
        "expanded_chains":int(len(expanded_chains)),
        "main_measure_instances":int(len(main_instances)),
        "expanded_measure_instances":int(len(expanded_instances)),
        "model_metadata":metas,
        "object_rules":recoded.object_recode_rule.value_counts().to_dict(),
        "evaluator_rules":recoded.evaluator_recode_rule.value_counts().head(30).to_dict(),
    }
    (OUT / "summary_g1_g7.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
