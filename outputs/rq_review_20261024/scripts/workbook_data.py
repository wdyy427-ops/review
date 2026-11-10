import json,collections
from config import ROOT,LABELS,STANDARDS
res=ROOT/'results'
def load(n):return json.loads((res/f'{n}.json').read_text(encoding='utf8'))
def v(x):
    if isinstance(x,(list,dict)):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
    return '' if x is None else x
def table(rows,fields,heads):return [heads]+[[v(r.get(k)) for k in fields] for r in rows]
lp=load('legacy_papers');lc=load('legacy_cases');lr=load('legacy_rows');rp=load('papers');ev=load('evaluations');ch=load('chains');aud=load('audits');changes=load('changes');md=load('legacy_exploratory_model_comparison');assoc=load('legacy_exploratory_associations')
q=load('rq2_distributions');dist=load('rq1_distributions')
overview=[['项目','结果','解释'],['论文PDF','125','全部提取文本并建立索引；不等于全部全文复核'],['PDF全文复核',len(rp),'具逐页提取与JCSEE审查'],['尚待全文复核',125-len(rp),'旧表数据仅供探索，不能进入正式规范性或推荐模型'],['旧表评价案例',len(lc),'首轮来源；案例界定可能改变'],['旧表感知行',len(lr),'首轮来源；存在误归类及重复'],['复核后评价案例',len(ev),'仅覆盖已复核论文'],['复核后证据链',len(ch),'已排除纯计算/客观代理与无主观数据行'],['严格规范性证据链',sum(x['strict_eligible'] for x in ch),'筛选规则在协议中预先锁定；当前无法训练正式模型'],['敏感性证据链',sum(x['sensitivity_eligible'] for x in ch),'只表示报告支持较充分，不能称规范认证'],['RQ3模型','仅旧表探索','5折论文分组交叉验证；不用于网站最佳工具推荐']]

paper_rows=[];rev={r['paper_id']:r for r in rp}
for p in lp:
    r=rev.get(p['paper_id'],{})
    paper_rows.append({**p,'reviewed_domain_codes':r.get('domain_codes',[]),'reviewed_stage_codes':r.get('stage_codes',[]),'reviewed_ai_function_codes':r.get('ai_function_codes',[]),'reviewed_context_summary':r.get('context_summary',''),'reviewed_evaluations':r.get('evaluation_count',''),'reviewed_chains':r.get('chain_count','')})
stdrows=[{'standard':s,'meaning':name,'rule':'S充分；P部分；C明确问题；NR未报告；NA不适用','reviewed_cases':len(ev),**{z:sum(e['audit_statuses'].get(s)==z for e in ev) for z in ['S','P','C','NR','NA']}} for s,name in STANDARDS.items()]
book={
 '概览':overview,
 '论文125':table(paper_rows,['paper_id','year','title','doi','domain_codes','stage_codes','ai_function_codes','review_status','pdf_pages','reviewed_domain_codes','reviewed_stage_codes','reviewed_ai_function_codes','reviewed_context_summary','reviewed_evaluations','reviewed_chains'],['编号','年份','题名','DOI','旧领域','旧阶段','旧AI功能','复核状态','PDF页数','复核领域','复核阶段','复核AI功能','复核情境概要','复核评价数','复核证据链数']),
 '旧表案例198':table(lc,['paper_id','legacy_eval_id','year','domain_codes','stage_codes','ai_function_codes','purpose_codes','dimension_codes','indicator_codes','row_count','review_status'],['论文','旧评价ID','年份','设计领域','设计阶段','AI功能','评价目的','感知维度','指标类别','原始行数','复核状态']),
 '旧表行567':table(lr,['paper_id','legacy_row','legacy_eval_id','year','claim_summary_previous','dimension_code_previous','indicator_code_previous','indicator_raw_previous','instrument_previous','result_direction_previous','source_locator_previous','review_status','notice'],['论文','旧表行','旧评价ID','年份','旧效果主张','旧维度','旧指标代码','旧原文指标译述','旧工具','旧效果方向','旧PDF定位','复核状态','使用边界']),
 '复核评价31':table(ev,['paper_id','eval_id','legacy_eval_ids','domain_codes','stage_codes','ai_function_codes','purpose_codes','object_codes','evaluator_codes','source_codes','task_codes','constraint_codes','setting_code','design_code','sample_n','sample_description','task','procedure','analysis','actual_results','limitations','audit_statuses','chain_ids'],['论文','复核评价ID','旧评价ID','领域','阶段','AI功能','目的','评价对象','评价主体','数据源','任务','可行条件','环境','设计','样本n','样本说明','具体任务','程序','分析','报告结果','局限','JCSEE状态','证据链ID']),
 '复核证据链95':table(ch,['paper_id','eval_id','chain_id','legacy_rows','claim_summary','claim_quote','claim_type','construct_raw','dimension_code','indicator_code','indicator_raw','item_quote','instrument_raw','tool_family_codes','tool_origin_code','response_scoring','validity_evidence','reliability_evidence','result_quote','effect_direction','pages','audit_statuses','strict_eligible','sensitivity_eligible'],['论文','评价ID','证据链ID','旧表行','效果主张概述','主张原文','主张类型','构念原文','维度','指标代码','指标原文','题项原文','工具原文','工具族','工具来源','量尺评分','效度依据','信度依据','结果原文','结果方向','PDF页码','JCSEE状态','严格纳入','敏感性纳入']),
 'JCSEE审查':table(aud,['paper_id','eval_id','chain_id','standard','status','facts','reason','pages','quote'],['论文','评价ID','证据链ID','条款','状态','事实','判定理由','PDF页码','原文引证']),
 '审查汇总':table(stdrows,['standard','meaning','rule','reviewed_cases','S','P','C','NR','NA'],['条款','本综述的操作化含义','判定等级','复核案例','S','P','C','NR','NA']),
 '复核分布':table(dist,['unit','field','code','label','n','denominator','proportion'],['单位','维度','代码','标签','计数','分母','比例']),
 '模型试算':table(md,['model','cases_n','papers_n','micro_ap','macro_ap','micro_f1_at_0_5','macro_f1_at_0_5','brier','per_dimension_ap','use_limit'],['模型','旧表案例','论文','微AP','宏AP','微F1','宏F1','Brier','各维度AP','使用边界']),
 '关联试算':table(assoc,['feature','context_code','context','dimension_code','dimension','both_papers','context_only','dimension_only','neither','risk_difference','odds_ratio','p_fisher','q_BH_all_100_tests'],['情境变量','情境代码','情境','维度代码','感知维度','两者共现论文','仅情境','仅维度','两者皆无','风险差','比值比','Fisher p','100检验BH q']),
 '编码变更':table(changes,['paper_id','legacy_row','eval_id','chain_id','action','reason','pages'],['论文','旧表行','复核评价','证据链','动作','理由','PDF页码']),
 '代码本':[['变量','代码','定义','来源／说明']]+[[f,c,name,('保留上一版既定分类' if f in ['domain','stage','ai_function','ai_role','dimension','indicator','purpose'] else '本综述预设分类；允许NR/UNMAPPED')] for f,vs in LABELS.items() for c,name in vs.items()],
}
(ROOT/'workbook_data.json').write_text(json.dumps(book,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({k:[len(v)-1,len(v[0])] for k,v in book.items()},ensure_ascii=False))
