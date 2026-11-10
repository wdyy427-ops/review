from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency
from sklearn.model_selection import StratifiedKFold

from config import ROOT, LABELS, INDICATORS
from revised_pipeline import (
    TOOL_LABELS,
    candidate_models,
    encode_features,
    evaluate_model,
    make_splits,
    positive_evidence,
    present,
    split_codes,
)

plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


DATA = ROOT / "revised_results"
OUT = ROOT / "extended_results"
FIG = ROOT / "extended_figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)


def read(name):
    return pd.read_csv(DATA / name, keep_default_na=False)


def hierarchy_counts(papers, evals, chains, instances):
    paper_case = evals.groupby("paper_id").eval_id.nunique()
    case_chain = chains.groupby("eval_id").chain_id.nunique()
    chain_inst = instances.groupby("chain_id").measure_instance_id.nunique()
    rows = [
        {"transition":"论文→评价案例", "parent_total":len(papers), "parents_with_children":paper_case.size, "parents_without_children":len(papers)-paper_case.size, "children_total":len(evals), "distribution":json.dumps(paper_case.value_counts().sort_index().to_dict(), ensure_ascii=False)},
        {"transition":"评价案例→评价证据链", "parent_total":len(evals), "parents_with_children":case_chain.size, "parents_without_children":len(evals)-case_chain.size, "children_total":len(chains), "distribution":json.dumps(case_chain.value_counts().sort_index().to_dict(), ensure_ascii=False)},
        {"transition":"评价证据链→测量工具实例", "parent_total":len(chains), "parents_with_children":chain_inst.size, "parents_without_children":len(chains)-chain_inst.size, "children_total":len(instances), "distribution":json.dumps(chain_inst.value_counts().sort_index().to_dict(), ensure_ascii=False)},
    ]
    return pd.DataFrame(rows)


def expand_context(df, context_col, code_col, labels, unit_id):
    rows=[]
    for _,r in df.iterrows():
        outcome=r.get(code_col,"")
        if outcome not in labels:
            continue
        for ctx in split_codes(r.get(context_col,"")):
            if ctx in LABELS["domain" if context_col=="domains" else "stage"]:
                rows.append({"unit_id":r[unit_id],"context_code":ctx,"outcome_code":outcome})
    long=pd.DataFrame(rows)
    ctx_labels=LABELS["domain" if context_col=="domains" else "stage"]
    table=pd.crosstab(long.context_code,long.outcome_code).reindex(index=list(ctx_labels),columns=list(labels),fill_value=0)
    denom=table.sum(axis=1).replace(0,np.nan)
    detail=[]
    for ctx in table.index:
        for code in table.columns:
            detail.append({"context_field":context_col,"context_code":ctx,"context_label":ctx_labels[ctx],"outcome_code":code,"outcome_label":labels[code],"n":int(table.loc[ctx,code]),"context_denominator":int(table.loc[ctx].sum()),"context_percent":float(table.loc[ctx,code]/denom.loc[ctx]) if pd.notna(denom.loc[ctx]) else np.nan})
    stats={"context_field":context_col,"outcome":code_col,"n_assignments":int(table.values.sum()),"rows":table.shape[0],"columns":table.shape[1]}
    nonzero_rows=table.sum(axis=1)>0; nonzero_cols=table.sum(axis=0)>0
    sub=table.loc[nonzero_rows,nonzero_cols]
    if sub.shape[0]>1 and sub.shape[1]>1:
        chi,p,dfree,expected=chi2_contingency(sub.values)
        stats.update({"chi_square":float(chi),"df":int(dfree),"p_value":float(p),"cramers_v":float(math.sqrt(chi/(sub.values.sum()*min(sub.shape[0]-1,sub.shape[1]-1)))),"expected_below_5_percent":float((expected<5).mean()),"minimum_expected":float(expected.min())})
    return long,table,pd.DataFrame(detail),stats


def bool_status(value, applicable=True, problem=False):
    if not applicable:
        return "NA"
    if problem:
        return "C"
    return "S" if bool(value) else "NR"


def subrule_audit(chains, evals, instances):
    evmap=evals.set_index("eval_id").to_dict("index")
    imap=instances.groupby("chain_id").apply(lambda x:x.to_dict("records"),include_groups=False).to_dict()
    defs=[]
    def rule(std,code,name,observable,basis):
        defs.append({"standard":std,"subrule":code,"subrule_name":name,"observable_rule":observable,"basis":basis})
    rule("U5","U5.1","评价目的可识别","purposes至少有一个有效代码","U5要求信息服务于已识别需求；目的必须先可识别")
    rule("U5","U5.2","相关人可识别","评价主体或目标用户至少一项可识别","用可报告的相关人代理stakeholder information needs")
    rule("U5","U5.3","评价问题／效果主张明确","有原文主张或可追溯主张摘要","评价证据必须回答明确问题")
    rule("U5","U5.4","构念与指标可操作化","构念存在且指标映射到既定代码","相关信息需转化为可测构念与指标")
    rule("U5","U5.5","指标与测量相连","证据链至少有一个可判定M1–M5工具实例","信息必须有取得证据的程序")
    rule("A2","A2.1","感知构念有定义或名称","construct_raw可定位","有效解释需要明确被解释的构念")
    rule("A2","A2.2","主观指标可识别","indicator_raw存在且indicator_code有效","测量解释需明确指标")
    rule("A2","A2.3","工具可识别","instrument_raw存在且工具类别可判定","有效信息需说明取得方式")
    rule("A2","A2.4","题项／提示可复核","item_quote存在","题项或提示支持内容效度判断")
    rule("A2","A2.5","计分／反应格式可复核","response_scoring存在","解释分数需要计分和反应格式")
    rule("A2","A2.6","效度依据被报告","validity_evidence含效度、预测试、专家审查或验证信息","A2直接要求信息支持有效解释")
    rule("A3","A3.1","量化测量可靠性依据","量化工具报告alpha、ICC、重测或其他可靠性证据","A3要求程序产生足够一致的信息")
    rule("A3","A3.2","评分／编码一致性依据","第三方评分或质性编码报告评分者／编码者一致性","多人判断时需检验一致性")
    rule("A3","A3.3","质性可信性依据","定性工具报告饱和、三角互证、成员核查或双人编码","质性资料以可信性程序对应A3")
    rule("A3","A3.4","重复实施所需细节","有题项／提示且有计分说明，或使用可识别具名量表","程序细节是稳定复现的最低报告条件")
    rule("A4","A4.1","评价对象可识别","objects至少有一个有效代码","A4要求明确描述被评价对象")
    rule("A4","A4.2","样本量可识别","sample_n有有效值","判断证据适用范围需要样本规模")
    rule("A4","A4.3","样本特征可识别","sample_description有有效值","A4要求对象与情境适当细节")
    rule("A4","A4.4","招募方式可识别","recruitment有有效值","招募影响样本边界与偏差判断")
    rule("A4","A4.5","任务／程序可识别","task或procedure至少一项存在","评价情境需说明参与者做了什么")
    rule("A4","A4.6","评价环境可识别","setting有有效代码","实验室、线上、现场等影响解释")
    rule("A4","A4.7","比较条件可识别","比较／因果主张时comparator存在；其他主张NA","条件比较必须描述比较基础")
    rule("A4","A4.8","设计与AI情境可识别","设计领域、阶段及AI功能／角色均可识别","本研究问题要求明确AI辅助设计情境")
    rule("A6","A6.1","研究设计可识别","design至少有一个有效代码","适切性判断先要识别设计")
    rule("A6","A6.2","分析方法可识别","analysis字段报告分析程序","A6要求技术上适切的分析")
    rule("A6","A6.3","比较设计与主张匹配","C2/C3主张有比较条件；其他主张NA","比较或因果推断需比较基础")
    rule("A6","A6.4","分析证据可定位","报告统计检验、回归、混合模型、质性分析或置信区间等","不能仅凭结论判断分析充分")
    rule("A6","A6.5","结果可定位","result_quote存在","设计和分析应产生可复核结果")
    rule("A6","A6.6","没有明显因果越界","明确因果主张同时具有比较条件和分析证据；非因果主张通过","防止设计能力低于结论强度")
    rule("A7","A7.1","主张可追溯","claim_quote或claim_summary存在","推理起点可见")
    rule("A7","A7.2","结果可追溯","result_quote存在","推理所依据的信息可见")
    rule("A7","A7.3","位置可追溯","pages存在","允许回到全文复核")
    rule("A7","A7.4","完整证据链可追溯","主张、构念、指标、工具、结果均存在","从问题到结论的中间环节完整")
    rule("A7","A7.5","推理强度与设计相称","C2/C3具有比较／分析支持，其他类型通过","A7要求显式记录从分析到判断的推理")
    rule("E1","E1.1","目的有记录","purposes存在","E1要求记录协商目的")
    rule("E1","E1.2","设计与程序有记录","design与procedure存在","E1要求记录实施设计和程序")
    rule("E1","E1.3","工具有记录","instrument_raw存在且工具类别可判定","E1要求记录数据取得程序")
    rule("E1","E1.4","题项／提示有记录","item_quote存在","支持复核具体测量内容")
    rule("E1","E1.5","计分有记录","response_scoring存在","支持复核数据如何形成")
    rule("E1","E1.6","结果有记录","result_quote存在","E1要求记录结果")
    rule("E1","E1.7","页码有记录","pages存在","支持文献内回溯")

    analysis_patterns=[r"anova",r"t[- ]?test",r"regression",r"mixed[- ]?effects?",r"wilcoxon",r"mann[- ]?whitney",r"chi[- ]?square",r"thematic analysis",r"content analysis",r"confidence interval",r"\bp\s*[<=>]"]
    rel_patterns=[r"cronbach",r"\bICC\b",r"kappa",r"kendall",r"inter[- ]?rater",r"test[- ]?retest",r"reliab",r"信度",r"一致性"]
    coder_patterns=[r"kappa",r"kendall",r"inter[- ]?rater",r"double cod",r"two coders",r"编码一致",r"评分者一致"]
    qual_patterns=[r"saturation",r"triangulat",r"member check",r"double cod",r"two coders",r"饱和",r"三角",r"成员核查",r"双人编码"]
    valid_patterns=[r"content validity",r"construct validity",r"factor analysis",r"validated",r"pilot",r"pretest",r"expert review",r"理论依据",r"效度",r"预测试"]
    records=[]
    for _,r in chains.iterrows():
        ev=evmap.get(r.eval_id,{})
        ins=imap.get(r.chain_id,[])
        tools={x["tool_code"] for x in ins if x["tool_code"] in TOOL_LABELS}
        named=any(x["tool_code"]=="M1" and "待人工核验" not in x["instrument_name"] for x in ins)
        claim=present(r.claim_quote) or present(r.claim_summary)
        construct=present(r.construct_raw)
        indicator=present(r.indicator_raw) and r.indicator_code in LABELS["indicator"]
        instrument=present(r.instrument_raw) and bool(tools)
        item=present(r.item_quote); scoring=present(r.response_scoring); result=present(r.result_quote); pages=present(r.pages)
        purpose=bool(split_codes(r.purposes)); people=bool(split_codes(r.evaluators) or split_codes(r.target_users)); obj=bool(split_codes(r.objects)); setting=bool(split_codes(r.setting)); design=bool(split_codes(r.design))
        sample_n=present(ev.get("sample_n")); sample_desc=present(ev.get("sample_description")); recruit=present(ev.get("recruitment")); procedure=present(ev.get("procedure")); task=present(ev.get("task")) or bool(split_codes(r.tasks)); comparator=present(ev.get("comparator")) and str(ev.get("comparator")).lower() not in {"nr","na","none","无"}; analysis_field=present(ev.get("analysis"));
        analysis_text=" | ".join(str(ev.get(c,"") or "") for c in ["analysis","procedure","comparator","actual_results"])
        analysis_evidence=positive_evidence(analysis_text,analysis_patterns)
        validity=positive_evidence(r.validity_evidence,valid_patterns)
        reliability=positive_evidence(r.reliability_evidence,rel_patterns)
        coder=positive_evidence(r.reliability_evidence,coder_patterns)
        qualcred=positive_evidence(r.reliability_evidence,qual_patterns)
        comparative=r.claim_type in {"C2","C3"}; causal=r.claim_type=="C3"
        ai_ctx=bool(split_codes(r.domains)) and bool(split_codes(r.stages)) and bool(split_codes(r.ai_functions) or split_codes(r.ai_roles))
        quantitative=bool(tools.intersection({"M1","M2"})); rater=bool("H2" in split_codes(r.sources) or "V1" in split_codes(r.evaluators)); qualitative="M3" in tools
        values={
            "U5.1":bool_status(purpose),"U5.2":bool_status(people),"U5.3":bool_status(claim),"U5.4":bool_status(construct and indicator),"U5.5":bool_status(indicator and instrument),
            "A2.1":bool_status(construct),"A2.2":bool_status(indicator),"A2.3":bool_status(instrument),"A2.4":bool_status(item),"A2.5":bool_status(scoring),"A2.6":bool_status(validity),
            "A3.1":bool_status(reliability,quantitative),"A3.2":bool_status(coder,rater or qualitative),"A3.3":bool_status(qualcred,qualitative),"A3.4":bool_status((item and scoring) or named),
            "A4.1":bool_status(obj),"A4.2":bool_status(sample_n),"A4.3":bool_status(sample_desc),"A4.4":bool_status(recruit),"A4.5":bool_status(task or procedure),"A4.6":bool_status(setting),"A4.7":bool_status(comparator,comparative),"A4.8":bool_status(ai_ctx),
            "A6.1":bool_status(design),"A6.2":bool_status(analysis_field),"A6.3":bool_status(comparator,comparative),"A6.4":bool_status(analysis_evidence),"A6.5":bool_status(result),"A6.6":bool_status((not causal) or (comparator and analysis_evidence),problem=causal and not(comparator and analysis_evidence)),
            "A7.1":bool_status(claim),"A7.2":bool_status(result),"A7.3":bool_status(pages),"A7.4":bool_status(claim and construct and indicator and instrument and result),"A7.5":bool_status((not comparative) or (comparator and analysis_evidence),problem=comparative and not(comparator and analysis_evidence)),
            "E1.1":bool_status(purpose),"E1.2":bool_status(design and procedure),"E1.3":bool_status(instrument),"E1.4":bool_status(item),"E1.5":bool_status(scoring),"E1.6":bool_status(result),"E1.7":bool_status(pages),
        }
        for d in defs:
            records.append({"paper_id":r.paper_id,"eval_id":r.eval_id,"chain_id":r.chain_id,**d,"status":values[d["subrule"]]})
    detail=pd.DataFrame(records)
    summary=detail.groupby(["standard","subrule","subrule_name","observable_rule","basis","status"]).size().rename("n").reset_index()
    den=detail.groupby("subrule").size().rename("all_chains")
    app=detail[detail.status!="NA"].groupby("subrule").size().rename("applicable_chains")
    summary=summary.merge(den,on="subrule").merge(app,on="subrule",how="left")
    summary["percent_all"]=summary.n/summary.all_chains
    summary["percent_applicable"]=np.where(summary.status=="NA",np.nan,summary.n/summary.applicable_chains)
    return pd.DataFrame(defs),detail,summary


def leakage_comparison(chains,instances,model_comp):
    merged_inst=instances.merge(chains.drop(columns=["revised_quality_tier","revised_quality_index","model_eligible_main","model_eligible_sensitivity"],errors="ignore"),on=["paper_id","eval_id","chain_id","year","dimension_code","indicator_code"],how="left",suffixes=("","_chain"))
    sets=[
        (chains[(chains.model_eligible_sensitivity==1)&chains.dimension_code.isin(LABELS["dimension"])],"dimension_code","评价维度",[]),
        (chains[(chains.model_eligible_sensitivity==1)&chains.indicator_code.isin(LABELS["indicator"])],"indicator_code","主观指标",["dimension_code"]),
        (merged_inst[(merged_inst.model_eligible_sensitivity==1)&merged_inst.tool_code.isin(TOOL_LABELS)],"tool_code","测量工具类别",["dimension_code","indicator_code"]),
    ]
    rows=[]
    for df,target_col,target_name,fixed in sets:
        counts=df[target_col].value_counts(); pc=df[[target_col,"paper_id"]].drop_duplicates()[target_col].value_counts(); keep=[c for c in counts.index if counts[c]>=5 and pc.get(c,0)>=3]
        d=df[df[target_col].isin(keep)].reset_index(drop=True); y=d[target_col].astype(str); x,_=encode_features(d,fixed)
        grouped=make_splits(y,d.paper_id); nfold=len(grouped)
        random=list(StratifiedKFold(n_splits=nfold,shuffle=True,random_state=20261025).split(x,y))
        best=model_comp[(model_comp.analysis_tier=="扩展规范集")&(model_comp.target==target_name)&(model_comp.model!="频率基线")].sort_values("macro_f1_mean",ascending=False).iloc[0].model
        model=candidate_models()[best]
        for scheme,splits in [("按论文分组",grouped),("随机按证据链／实例",random)]:
            met=evaluate_model(model,x,y,splits)
            rows.append({"target":target_name,"model":best,"validation":scheme,"n":len(d),"papers":d.paper_id.nunique(),"classes":y.nunique(),"folds":len(splits),"macro_f1":met.macro_f1.mean(),"accuracy":met.accuracy.mean(),"top2_accuracy":met.top2_accuracy.mean(),"macro_f1_sd":met.macro_f1.std(ddof=1)})
    out=pd.DataFrame(rows)
    grouped=out[out.validation=="按论文分组"].set_index("target")
    random=out[out.validation=="随机按证据链／实例"].set_index("target")
    out["inflation_vs_grouped"]=[row.macro_f1/grouped.loc[row.target,"macro_f1"]-1 if row.validation!="按论文分组" else 0 for row in out.itertuples()]
    return out


def save_heatmap(detail, outcome_labels, title, filename, figsize):
    mat=detail.pivot(index="outcome_code",columns="context_code",values="context_percent").reindex(index=list(outcome_labels))*100
    counts=detail.pivot(index="outcome_code",columns="context_code",values="n").reindex(index=list(outcome_labels),columns=mat.columns)
    ann=counts.fillna(0).astype(int).astype(str)
    ann=ann.where(counts>0,"")
    fig,ax=plt.subplots(figsize=figsize)
    sns.heatmap(mat,annot=ann,fmt="",cmap="YlGnBu",vmin=0,cbar_kws={"label":"该情境内占比（%）"},linewidths=.35,linecolor="white",ax=ax)
    ax.set_yticklabels([f"{c} {outcome_labels[c]}" for c in mat.index],rotation=0,fontsize=8)
    ctxfield=detail.context_field.iloc[0]; ctxlabels=LABELS["domain" if ctxfield=="domains" else "stage"]
    ax.set_xticklabels([f"{c}\n{ctxlabels[c]}" for c in mat.columns],rotation=0)
    ax.set_xlabel(""); ax.set_ylabel(""); ax.set_title(title,loc="left",fontweight="bold")
    if all(str(x)[0] in "ABCDE" for x in mat.index):
        positions=[]; last=None
        for i,c in enumerate(mat.index):
            if last and c[0]!=last: positions.append(i)
            last=c[0]
        for p in positions: ax.axhline(p,color="#213547",lw=1.2)
    fig.tight_layout(); fig.savefig(FIG/f"{filename}.png",dpi=320,bbox_inches="tight",facecolor="white"); fig.savefig(FIG/f"{filename}.pdf",bbox_inches="tight",facecolor="white"); plt.close(fig)


def subrule_figure(summary):
    p=summary[summary.status.isin(["S","NR","C"])].copy()
    piv=p.pivot_table(index=["standard","subrule","subrule_name"],columns="status",values="percent_applicable",fill_value=0).reset_index()
    for c in ["S","NR","C"]:
        if c not in piv:piv[c]=0
    piv=piv.sort_values(["standard","S"],ascending=[True,True])
    fig,ax=plt.subplots(figsize=(12,14))
    y=np.arange(len(piv)); left=np.zeros(len(piv))
    colors={"S":"#2F7D6D","NR":"#A9AFB8","C":"#C95D63"}
    for st in ["S","NR","C"]:
        v=piv[st].to_numpy()*100; ax.barh(y,v,left=left,color=colors[st],label={"S":"可观察支持","NR":"未报告／无法判断","C":"明确问题"}[st]); left+=v
    ax.set_yticks(y,[f"{r.subrule} {r.subrule_name}" for r in piv.itertuples()],fontsize=8)
    ax.set_xlim(0,100); ax.set_xlabel("适用证据链中的比例（%）"); ax.set_title("JCSEE启发的可观察子规则分布",loc="left",fontweight="bold")
    ax.legend(ncol=3,loc="lower center",bbox_to_anchor=(.5,-.06),frameon=False); ax.grid(axis="y",visible=False); ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG/"图10_JCSEE子规则分布.png",dpi=320,bbox_inches="tight",facecolor="white"); fig.savefig(FIG/"图10_JCSEE子规则分布.pdf",bbox_inches="tight",facecolor="white"); plt.close(fig)


def main():
    papers=read("papers.csv"); evals=read("evaluation_cases.csv"); chains=read("evidence_chains_revised.csv"); instances=read("measure_instances.csv")
    hierarchy_counts(papers,evals,chains,instances).to_csv(OUT/"hierarchy_counts.csv",index=False,encoding="utf-8-sig")
    stats=[]
    for ctx,stem in [("domains","domain"),("stages","stage")]:
        _,_,detail,s=expand_context(chains,ctx,"indicator_code",LABELS["indicator"],"chain_id"); detail.to_csv(OUT/f"rq1_indicator_by_{stem}.csv",index=False,encoding="utf-8-sig"); stats.append(s)
        merged=instances.merge(chains[["chain_id",ctx]],on="chain_id",how="left")
        _,_,tdetail,ts=expand_context(merged,ctx,"tool_code",TOOL_LABELS,"measure_instance_id"); tdetail.to_csv(OUT/f"rq1_tool_by_{stem}.csv",index=False,encoding="utf-8-sig"); stats.append(ts)
        save_heatmap(detail,LABELS["indicator"],f"主观指标在{'设计领域' if stem=='domain' else '设计阶段'}中的分布",f"图08{'A' if stem=='domain' else 'B'}_指标与{('设计领域' if stem=='domain' else '设计阶段')}",(11,14))
        save_heatmap(tdetail,TOOL_LABELS,f"测量工具在{'设计领域' if stem=='domain' else '设计阶段'}中的分布",f"图09{'A' if stem=='domain' else 'B'}_工具与{('设计领域' if stem=='domain' else '设计阶段')}",(11,5.4))
    pd.DataFrame(stats).to_csv(OUT/"rq1_extended_context_tests.csv",index=False,encoding="utf-8-sig")
    defs,subdetail,subsummary=subrule_audit(chains,evals,instances); defs.to_csv(OUT/"jcsee_subrule_codebook.csv",index=False,encoding="utf-8-sig"); subdetail.to_csv(OUT/"jcsee_subrule_audit.csv",index=False,encoding="utf-8-sig"); subsummary.to_csv(OUT/"jcsee_subrule_summary.csv",index=False,encoding="utf-8-sig"); subrule_figure(subsummary)
    leak=leakage_comparison(chains,instances,read("rq3_model_comparison.csv")); leak.to_csv(OUT/"grouped_vs_random_cv.csv",index=False,encoding="utf-8-sig")
    print(json.dumps({"hierarchy":pd.read_csv(OUT/"hierarchy_counts.csv").to_dict("records"),"context_stats":stats,"subrules":len(defs),"leakage":leak.to_dict("records")},ensure_ascii=False,indent=2))


if __name__=="__main__":main()
