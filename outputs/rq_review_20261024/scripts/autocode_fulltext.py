"""Reproducible full-corpus candidate coding from PDF text only.

The supplied legacy coding workbook is deliberately not read. Fixed code labels come
from config.py. Every inferred code retains a page and sentence for audit. The 12 manually
reviewed papers remain a validation/override set in later consolidation.
"""
from __future__ import annotations
import json,re,collections,math
from pathlib import Path
from pypdf import PdfReader
from config import ROOT,LABELS,STANDARDS,quality_gate

SRC=ROOT/'extracted';PDF=ROOT.parents[1]/'最终'/'全文-重新排序 - 副本';OUT=ROOT/'autocode';OUT.mkdir(exist_ok=True)

def norm(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def sent_split(text):
    text=norm(text)
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9“\[])|\s*\n\s*',text) if len(x.strip())>24]
def evid(pages,rx,limit=4):
    q=re.compile(rx,re.I);out=[]
    for p in pages:
        for s in sent_split(p['text']):
            if q.search(s):out.append({'page':p['page'],'quote':s[:700]})
    return out[:limit]
def has(t,rx):return bool(re.search(rx,t,re.I))
def codes_with_evidence(pages,mapping,scope=None,min_hits=1):
    use=[p for p in pages if scope is None or p['page'] in scope];ans=[]
    for code,rx in mapping.items():
        ev=evid(use,rx,8)
        if len(ev)>=min_hits:ans.append({'code':code,'evidence':ev[:3]})
    return ans

DOMAIN={
'D1':r'graphic design|visual communication|poster|logo|typograph|icon design|illustration|advertis(?:ing|ement)|visual identity|packaging graphic',
'D2':r'industrial design|product design|engineering design|furniture|chair|vehicle|automotive|car design|train (?:appearance|design)|consumer product|product form|product styl',
'D3':r'fashion|garment|apparel|clothing|textile|outfit',
'D4':r'interior design|interior space|room layout|indoor environment|architectural interior',
'D5':r'service design|service system|customer journey|service blueprint|service experience',
'D6':r'ui/ux|user interface|user experience design|interface design|web design|mobile app|dashboard design|interaction design',}
STAGE={'S1':r'user need|requirement analys|design research|preference elic|kansei word|persona|empath|market research|problem framing',
'S2':r'ideation|concept(?:ual)? design|brainstorm|idea generation|sketch|design concept|early.stage design|divergent thinking',
'S3':r'prototype|mock.?up|usability test|user test|design evaluation|concept evaluation|rendered design|3d model',
'S4':r'implementation|deployment|production|manufactur|commerciali[sz]|real.world adoption|field deployment'}
AIF={'F1':r'identif(?:y|ying) (?:user )?needs?|need extraction|requirement analys|preference (?:understand|elic)|kansei extraction|persona generation',
'F2':r'knowledge retriev|information retriev|knowledge graph|literature search|precedent|analogy retriev|case.based|reference image',
'F3':r'generat(?:e|ing|ion) (?:design|image|idea|concept|solution|content|form)|text.to.image|diffusion model|generative adversarial|design synthesis',
'F4':r'prototyp|code generation|3d reconstruction|cad model|fabricat|rendering|implementation support',
'F5':r'evaluat(?:e|ion)|design assessment|feedback|scor(?:e|ing)|predict(?:ion|ing) (?:preference|emotion|rating)|quality assessment',
'F6':r'iterat(?:e|ion|ive)|refin(?:e|ement)|optimis|optimiz|revision|modify|improv(?:e|ement) (?:the )?design'}
AIROLE={'R1':r'user prompt|prompted|generate on request|text.to.image|designer input',
'R2':r'advice|recommend|suggest|feedback|assistant|decision support|evaluate|critic|coach',
'R3':r'co.?creat|collaborat|mixed.initiative|take initiative|proactive|agentic|multi.agent'}
PURPOSE={'P1':r'elic(?:it|itation)|identify (?:user )?(?:needs|preferences|values)|derive (?:criteria|weights)|kansei engineering|requirement gathering',
'P2':r'training label|ground truth|supervised|reward model|loss function|model calibration|validation label|annotation dataset',
'P3':r'formative|during (?:the )?design|real.time feedback|iterative feedback|refine the design|revision support|guide iteration',
'P4':r'evaluat(?:e|ion)|compare|comparative|controlled experiment|user study|usability test|validate the (?:system|method|tool)|benchmark'}
OBJECT={'O1':r'design outcome|design solution|generated (?:image|design|concept)|artifact|prototype|product form|final design',
'O2':r'design process|workflow|ideation process|design activity|creative process',
'O3':r'ai system|ai tool|interface|prototype system|platform|application|method usability',
'O4':r'human.ai|co.?creat|collaboration|division of labor|agency|partnership',
'O5':r'designer(?:s)? (?:experience|ability|cognition)|participant experience|workload|self.efficacy|learning|inspiration',
'O6':r'end.user experience|user acceptance|social impact|adoption|purchase intention|sustainab|ethical',
'O7':r'user need|preference|value criteria|kansei|requirement|weight(?:ing)?'}
EVALUATOR={'V1':r'expert(?:s)?|professional designer|domain expert|design practitioner',
'V2':r'design student|novice designer|undergraduate design|graduate design',
'V3':r'target users?|end users?|consumer(?:s)?|customer(?:s)?',
'V4':r'general public|crowd(?:source|worker)|mturk|prolific|online participants?',
'V5':r'client(?:s)?|stakeholder(?:s)?|manager(?:s)?|organisation|organization',
'V6':r'researcher(?:s)? (?:rated|evaluated|coded)|author(?:s)? (?:rated|evaluated|coded)'}
SOURCE={'H1':r'questionnaire|survey|self.report|likert|semantic differential|rating scale',
'H2':r'expert rating|expert evaluation|judge(?:s)?|rater(?:s)?|third.party rating',
'H3':r'interview|focus group|think.aloud|open.ended|thematic analys',
'H4':r'online review|social media|comment dataset|existing reviews?|archival text',
'H5':r'interaction log|behavioral log|click|task completion|design history|screen recording',
'H6':r'automatic metric|computational metric|embedding|clip score|fid\b|precision|recall|classifier'}
SETTING={'L1':r'laboratory|lab study|controlled experiment|in.person', 'L2':r'online survey|remote study|web.based|prolific|mturk',
'L3':r'field study|workplace|real.world|in the wild|professional practice', 'L4':r'mixed setting|both online and in.person', 'L5':r'archival|secondary data|existing (?:reviews|comments)'}
DESIGN={'G2':r'within.subject|repeated.measure|counterbalanc', 'G3':r'between.subject|independent groups?|random(?:ly)? assigned',
'G4':r'mixed design', 'G5':r'qualitative study|thematic analys|interview study', 'G6':r'archival|secondary data',
'G7':r'pairwise comparison|analytic hierarchy|ahp\b|best.worst|weight elicitation', 'G8':r'annotation|training label|ground truth|supervised dataset'}
TOOLS={'M2':r'nasa.?tlx|system usability scale|\bSUS\b|creativity support index|\bCSI\b|ueq\b|attrakdiff|technology acceptance model|\bTAM\b|panas|self.efficacy scale|trust scale',
'M1':r'likert|semantic differential|rating scale|questionnaire|survey', 'M3':r'pairwise comparison|rank(?:ing|ed)|preference choice|forced.choice',
'M4':r'semi.structured interview|focus group|interview', 'M5':r'open.ended|think.aloud|observation|thematic analys',
'M6':r'analytic hierarchy|\bAHP\b|fuzzy evaluation|kansei engineering|multi.criteria', 'M7':r'online review|social media|sentiment analys|comment dataset'}
ORIGIN={'T1':r'(?:used|administered) (?:the )?(?:NASA.?TLX|SUS|CSI|UEQ|AttrakDiff|PANAS)',
'T2':r'adapted|modified|translated|short version|items? from', 'T4':r'interview protocol|thematic analys|focus group', 'T5':r'existing reviews?|archival|secondary data'}
CLAIM={'C3':r'caused|led to|resulted in|impact of|effect of|improved|enhanced|reduced|increased', 'C2':r'compared|higher than|lower than|difference|outperformed|versus|vs\.', 'C4':r'explore|understand|elicit|identify', 'C1':r'descriptive|reported|rated|perceived'}
TASK={'K1':r'requirement|need|research|analysis|preference', 'K2':r'ideation|brainstorm|concept|sketch|creative', 'K3':r'visuali[sz]|render|content creation|image generation|presentation',
'K4':r'compare|select|choice|ranking|evaluation', 'K5':r'refine|revise|modify|iterate|optim', 'K6':r'prototype|implement|test|fabricat', 'K7':r'collaborat|communicat|feedback|team'}
CONSTRAINT={'Q1':r'difficult to recruit|recruitment limitation|limited access to (?:experts|participants)', 'Q2':r'time constraint|participant burden|fatigue|time limit',
'Q3':r'translat|language limitation|cross.cultural|cultural adaptation', 'Q4':r'prototype limitation|not deployed|laboratory setting|lack of real.world',
'Q5':r'data availability|limited dataset|data scarcity|lack of data', 'Q6':r'privacy|confidential|organisational access|organizational access'}

IND={
'A1':r'novel(?:ty)?|originality|creativ(?:e|ity)|unique(?:ness)?', 'A2':r'aestheti|visual appeal|beaut(?:y|iful)|attractiveness|elegan',
'A3':r'useful(?:ness)?|appropriat|relevance|functional(?:ity)?|fit for purpose|practicality', 'A4':r'feasib|manufacturab|implementab|realizab',
'A5':r'fidelity|realism|representativeness|match (?:the )?(?:reference|target image)|visual consistency', 'A6':r'completeness|comprehensiveness|overall quality|holistic',
'B1':r'time efficien|time saving|faster|reduced time|task time|speed', 'B2':r'workload|mental demand|effort|cognitive load|nasa.?tlx',
'B3':r'iteration efficiency|number of iterations|revision efficiency|rapid iteration', 'B4':r'decision support|think through|task structuring|design reasoning|direction selection',
'B5':r'workflow continuity|process continuity|flow|seamless workflow', 'B6':r'handoff|transition between|cross.stage transfer',
'C1':r'inspir|stimulat|idea fluency|ideational support', 'C2':r'learn|knowledge gain|knowledge acquisition|understanding', 'C3':r'self.efficacy|confidence',
'C4':r'engagement|immersion|involvement|flow experience', 'C5':r'enjoy|pleasure|delight|fun', 'C6':r'reflect|critical thinking|metacogn',
'C7':r'fixation|dependenc|over.reliance|automation bias', 'C8':r'capability|empower|skill extension|augment(?:ed|ation)|performance support',
'D1':r'usability|ease of use|easy to use|learnability|interaction quality', 'D2':r'intention to use|willingness to use|continued use|adoption intention',
'D3':r'control(?:lability)?|agency|steerability', 'D4':r'transparen|explainab|understand system|interpretability', 'D5':r'trust|reliance|credibility',
'D6':r'ownership|authorship|pride|sense of agency|autonomy', 'D7':r'role|division of labor|contribution|fairness', 'D8':r'collaborat|communication|coordination|conflict|shared understanding|co.creation',
'E1':r'user experience|acceptance|satisfaction|purchase intention|preference|emotional response', 'E2':r'need fit|goal match|context fit|personalization|user requirement|kansei match|target emotion',
'E3':r'professional practice|workflow fit|organisation|organization|work practice', 'E4':r'cultur|social value|public value|identity|heritage',
'E5':r'ethic|fairness|bias|inclusion|inclusive|accessibility', 'E6':r'sustainab|environmental', 'E7':r'business|brand|market|commercial', 'E8':r'long.term|governance|responsib|accountability|maintenance'}

MEASURE_GATE=re.compile(r'likert|questionnaire|survey|(?:rating|rated|scored)\b|(?:measurement|measure|measured)\b|items?\b|criteri(?:on|a)\b|dimensions?\b|asked (?:to|whether)|semantic differential|pairwise comparison|ranking',re.I)
RESULT_GATE=re.compile(r'p\s*[<=>]|significant|mean(?: score)?\b|standard deviation|participants? (?:reported|preferred|felt|rated|indicated)|respondents? (?:reported|preferred|felt|rated|indicated)|higher (?:score|rating)|lower (?:score|rating)|themes? (?:included|emerged)',re.I)
HUMAN_GATE=re.compile(r'participant|respondent|designer|student|expert|user|consumer|customer|rater|judge|interviewee|crowd',re.I)
SAMPLE_GATE=re.compile(r'\b(?:n\s*=\s*\d+|\d+\s+(?:participants?|respondents?|designers?|students?|experts?|raters?|judges?|users?|consumers?)|participants? (?:were )?recruited|we recruited)\b',re.I)

def first_metadata(pdf,pages):
    m=PdfReader(str(pdf)).metadata
    first=norm(pages[0]['text'])
    doi=(re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',first,re.I) or re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',norm(' '.join(p['text'] for p in pages[:2])),re.I))
    years=[int(x) for x in re.findall(r'\b(20[12]\d)\b',first)]
    title=norm(getattr(m,'title',None))
    if not title or re.match(r'^(DSJ_|Microsoft Word|untitled|Adobe)',title,re.I):
        pre=re.split(r'\bAbstract\b',first,flags=re.I)[0]
        mm=re.search(r'(?:Journal homepage:[^|]+\||https?://doi\.org/[^ ]+\s+)(.{20,220}?)(?:\s+[A-Z][A-Za-z .,&-]{3,80}\s+(?:Department|School|College|To cite))',pre,re.I)
        title=norm(mm.group(1)) if mm else norm(pre[:180])
    return title[:300],doi.group(0).rstrip('.,') if doi else '',max(years) if years else None

def select_eval_pages(pages):
    score={}
    for p in pages:
        t=p['text'];s=0
        s+=7*len(re.findall(r'user stud(?:y|ies)|participants? (?:were )?recruited|we recruited|\bn\s*=\s*\d+|\d+\s+(?:participants?|respondents?|designers?|students?|experts?|raters?|judges?|users?|consumers?)',t,re.I))
        s+=4*len(re.findall(r'questionnaire|survey|semi.structured interview|focus group|likert|semantic differential',t,re.I))
        s+=3*len(re.findall(r'likert|scale|rating|measure|evaluation method|results|findings',t,re.I))
        s+=2*len(re.findall(r'cronbach|reliab|validit|p\s*[<=>]|significant|mean|standard deviation',t,re.I))
        score[p['page']]=s
    seeds={pg for pg,s in score.items() if s>=12 and SAMPLE_GATE.search(next(p['text'] for p in pages if p['page']==pg))}
    if not seeds:
        seeds={pg for pg,s in score.items() if s>=16 and re.search(r'user stud(?:y|ies)|participants? (?:were )?recruited|questionnaire|likert',next(p['text'] for p in pages if p['page']==pg),re.I)}
    if not seeds:seeds={pg for pg,s in sorted(score.items(),key=lambda x:x[1],reverse=True)[:3] if s>0}
    keep=sorted({q for pg in seeds for q in range(max(1,pg-1),min(len(pages),pg+1)+1)})
    return keep,score

def code_paper(i):
    d=json.loads((SRC/f'{i:03d}.json').read_text(encoding='utf8'));pages=d['pages'];pdf=Path(d['pdf_path'])
    title,doi,year=first_metadata(pdf,pages);eval_pages,scores=select_eval_pages(pages)
    first_pages=pages[:min(4,len(pages))];context_pages=first_pages+[p for p in pages if p['page'] in eval_pages]
    ctx=norm(' '.join(p['text'] for p in first_pages));etext=norm(' '.join(p['text'] for p in pages if p['page'] in eval_pages))
    context={f:codes_with_evidence(first_pages,mp) for f,mp in [('domain',DOMAIN),('stage',STAGE),('ai_function',AIF),('ai_role',AIROLE)]}
    human=bool(SAMPLE_GATE.search(etext) and HUMAN_GATE.search(etext) and MEASURE_GATE.search(etext))
    subjective=bool(re.search(r'likert|questionnaire|survey|rating|interview|focus group|semantic differential|preference|satisfaction|perceived',etext,re.I))
    ev=[];chains=[]
    if human and subjective:
        maps=[('purpose',PURPOSE),('object',OBJECT),('evaluator',EVALUATOR),('source',SOURCE),('setting',SETTING),('design',DESIGN),('task',TASK),('constraint',CONSTRAINT)]
        ec={f:codes_with_evidence([p for p in pages if p['page'] in eval_pages],mp) for f,mp in maps}
        if not ec['design']:
            ec['design']=[{'code':'G1','evidence':evid([p for p in pages if p['page'] in eval_pages],r'evaluat|rating|survey',1)}]
        # One reproducible article-level case; chain pages preserve within-paper evidence.
        case={'paper_id':i,'eval_id':f'{i:03d}-A1','candidate_pages':eval_pages,
              **{f+'_codes':[x['code'] for x in ec[f]] for f,_ in maps},
              'evidence_by_field':ec,'sample_evidence':evid([p for p in pages if p['page'] in eval_pages],r'\b(?:n\s*=\s*\d+|\d+ participants?|\d+ respondents?|recruited)\b',5),
              'analysis_evidence':evid([p for p in pages if p['page'] in eval_pages],r'paired t.test|independent t.test|anova|wilcoxon|mann.whitney|regression|thematic analys|descriptive statistics|cronbach|kappa|kendall',6)}
        relevant=[p for p in pages if p['page'] in eval_pages]
        all_sents=[(p['page'],s) for p in relevant for s in sent_split(p['text'])]
        tool_ev=codes_with_evidence(relevant,TOOLS);origin_ev=codes_with_evidence(relevant,ORIGIN)
        for ind,rx in IND.items():
            candidates=[(pg,s) for pg,s in all_sents if re.search(rx,s,re.I) and MEASURE_GATE.search(s)]
            if not candidates:
                # Allow result sentences when a measurement sentence elsewhere establishes a subjective study.
                candidates=[(pg,s) for pg,s in all_sents if re.search(rx,s,re.I) and RESULT_GATE.search(s)]
            if not candidates:continue
            pg,s=candidates[0]
            result=next(((p2,s2) for p2,s2 in all_sents if abs(p2-pg)<=2 and re.search(rx,s2,re.I) and RESULT_GATE.search(s2)),(pg,''))
            direction='NR';low=result[1].lower()
            if re.search(r'non.significant|not significant|no significant|p\s*[=>]\s*0\.0?5',low):direction='无显著差异'
            elif re.search(r'higher|improv|increase|positive|outperform|preferred|enhanc',low):direction='正向'
            elif re.search(r'lower|reduc|decrease|negative|worse',low):direction='负向'
            claim=next((x for p2,x in all_sents if abs(p2-pg)<=2 and re.search(rx,x,re.I) and re.search(r'effect|impact|improv|enhanc|reduc|increase|compare|evaluate|investigat',x,re.I)),s)
            ctype=next((code for code,crx in CLAIM.items() if re.search(crx,claim,re.I)),'C1')
            chains.append({'paper_id':i,'eval_id':case['eval_id'],'chain_id':f'{case["eval_id"]}-C{len(chains)+1:02d}',
               'claim_quote':claim[:700],'claim_summary':claim[:300],'claim_type':ctype,'construct_raw':re.search(rx,s,re.I).group(0),
               'indicator_raw':re.search(rx,s,re.I).group(0),'item_quote':s[:700],'dimension_code':ind[0],'indicator_code':ind,
               'instrument_raw':'；'.join(x['evidence'][0]['quote'][:160] for x in tool_ev[:3]) or 'NR',
               'tool_family_codes':[x['code'] for x in tool_ev] or ['NR'],'tool_origin_code':(origin_ev[0]['code'] if origin_ev else ('T3' if tool_ev else 'NR')),
               'response_scoring':next((x['quote'] for x in evid(relevant,r'\b[1-9][-. ]point (?:likert|scale)|strongly disagree|strongly agree|semantic differential',3)),'NR'),
               'validity_evidence':next((x['quote'] for x in evid(relevant,r'validit|validated scale|factor analys|content valid',3)),'NR'),
               'reliability_evidence':next((x['quote'] for x in evid(relevant,r'cronbach|reliab|inter.rater|kappa|kendall|icc\b|test.retest|two (?:researchers|coders)',3)),'NR'),
               'result_quote':result[1][:700] if result[1] else 'NR','effect_direction':direction,'pages':sorted(set([pg,result[0]]))})
        # Unmapped subjective construct is retained when the paper clearly has a subjective study but no fixed indicator was detected.
        if not chains:
            q=evid(relevant,r'questionnaire|likert|rating|interview|survey',1)
            chains.append({'paper_id':i,'eval_id':case['eval_id'],'chain_id':f'{case["eval_id"]}-C01','claim_quote':'NR','claim_summary':'主观感知评价存在，但固定指标映射需人工复核','claim_type':'C1','construct_raw':'UNMAPPED','indicator_raw':'UNMAPPED','item_quote':q[0]['quote'] if q else 'NR','dimension_code':'UNMAPPED','indicator_code':'UNMAPPED','instrument_raw':q[0]['quote'] if q else 'NR','tool_family_codes':[x['code'] for x in tool_ev] or ['NR'],'tool_origin_code':(origin_ev[0]['code'] if origin_ev else 'NR'),'response_scoring':'NR','validity_evidence':'NR','reliability_evidence':'NR','result_quote':'NR','effect_direction':'NR','pages':[q[0]['page']] if q else eval_pages[:1]})
        # Reporting audit, explicitly conservative.
        sample=bool(case['sample_evidence']);task=bool(evid(relevant,r'task|procedure|participants? (?:were|completed|performed)',2));setting=bool(ec['setting'])
        stats=bool(case['analysis_evidence']);result=any(c['result_quote']!='NR' for c in chains)
        named=any('M2'==x['code'] for x in tool_ev);valid=any(c['validity_evidence']!='NR' for c in chains);reliable=any(c['reliability_evidence']!='NR' for c in chains)
        complete_items=any(c['item_quote']!='NR' and c['response_scoring']!='NR' for c in chains)
        non_sig_over=False
        for c in chains:
            if c['effect_direction']=='无显著差异' and re.search(r'improv|outperform|enhanc|higher',c['claim_quote'],re.I):non_sig_over=True
        audit={
          'U5':'S' if chains and any(ec['purpose']) else 'P',
          'A2':'S' if valid else ('P' if named or complete_items or len(chains)>0 else 'NR'),
          'A3':'S' if reliable and bool(re.search(r'cronbach|kappa|kendall|icc\b|test.retest',etext,re.I)) else ('P' if reliable else 'NR'),
          'A4':'S' if sample and task and setting else ('P' if sum([sample,task,setting])>=2 else 'NR'),
          'A6':'S' if stats and result else ('P' if result else 'NR'),
          'A7':'C' if non_sig_over else ('S' if result and stats else ('P' if result else 'NR')),
          'E1':'S' if complete_items and result else ('P' if chains and result else 'NR')}
        case['audit_statuses']=audit;case['audit_note']='全文规则辅助判定；须结合逐页人工复核后方可作为最终规范性结论。'
        strict,sens=quality_gate(audit)
        for c in chains:c['audit_statuses']=audit;c['strict_eligible']=strict;c['sensitivity_eligible']=sens;c['coding_status']='全文规则候选，待人工语义复核'
        case['chain_ids']=[c['chain_id'] for c in chains];case['dimension_codes']=sorted({c['dimension_code'] for c in chains});case['indicator_codes']=sorted({c['indicator_code'] for c in chains});case['tool_family_codes']=sorted({x for c in chains for x in c['tool_family_codes']})
        ev=[case]
    return {'paper_id':i,'title':title,'doi':doi,'year':year,'pdf_path':str(pdf),'pdf_pages':len(pages),'candidate_pages':eval_pages,
       **{f+'_codes':[x['code'] for x in context[f]] for f in context},'context_evidence':context,
       'has_human_subjective_evaluation':bool(ev),'evaluation_count':len(ev),'chain_count':len(chains),'evaluations':ev,'chains':chains,
       'coding_status':'全文规则候选；未使用旧表内容；待人工语义复核'}

papers=[]
for i in range(1,126):
    x=code_paper(i);papers.append(x);(OUT/f'paper_{i:03d}.json').write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
    print(i,x['evaluation_count'],x['chain_count'],flush=True)
(OUT/'all_papers.json').write_text(json.dumps(papers,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'papers':125,'human_subjective_papers':sum(x['has_human_subjective_evaluation'] for x in papers),'evaluations':sum(x['evaluation_count'] for x in papers),'chains':sum(x['chain_count'] for x in papers)},ensure_ascii=False))
