"""Read-only audit of review source data; outputs confined to manuscript directory."""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import json
import urllib.request
import urllib.parse
import openpyxl
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'outputs/rq_review_20261024/supplement_enhanced_v2'

def read(name):
    return list(csv.DictReader((DATA / name).open(encoding='utf-8-sig')))

def book(path, sheet=0):
    return list(openpyxl.load_workbook(ROOT / path, read_only=True, data_only=True).worksheets[sheet].values)

def write(name, rows):
    pd.DataFrame(rows).to_csv(OUT / name, index=False, encoding='utf-8-sig')

def normdoi(s):
    return str(s or '').lower().strip().removeprefix('https://doi.org/')

def metadata(doi):
    try:
        url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='')
        req = urllib.request.Request(url, headers={'User-Agent': 'ResearchCorpusMetadataAudit/1.0'})
        msg = json.load(urllib.request.urlopen(req, timeout=25))['message']
        fields = ['DOI', 'title', 'container-title', 'published', 'published-online', 'published-print', 'issued', 'URL', 'type', 'author']
        return {k: msg.get(k) for k in fields}
    except Exception as exc:
        return {'error': str(exc)}

def run():
    papers = read('03_revised_results/papers_supplement_enhanced.csv')
    chains = read('03_revised_results/evidence_chains_supplement_enhanced.csv')
    tools = read('03_revised_results/measure_instances_supplement_enhanced.csv')
    audits = read('03_revised_results/jcsee_chain_audit_supplement_enhanced.csv')
    numbered = book('最终/Final included_descending_numbered.xlsx')[1:]
    assert len(papers) == 125 and len(numbered) == 140
    byid = {int(r[0]): r for r in numbered}
    catalogue = []
    for p in papers:
        rid = int(p['paper_id'])
        r = byid[rid]
        # Original numbered records establish manuscript record identity.
        title = str(r[2])
        catalogue.append({'paper_id': rid, 'title': title, 'doi': normdoi(r[10]), 'screening_year': int(r[3]),
                          'coded_year': int(p['year']), 'coded_title': p['title'], 'coded_doi': p['doi'],
                          'doi_correction': normdoi(r[10]) != normdoi(p['doi']), 'screening_date': r[4],
                          'venue': r[6], 'domains': p['domains'], 'stages': p['stages'],
                          'source': '最终/Final included_descending_numbered.xlsx row ' + str(rid + 1)})
    assert all(r['screening_year'] >= 2022 for r in catalogue)
    assert all(int(r[3]) < 2022 for r in numbered[125:])
    write('reviewed_corpus_catalogue.csv', catalogue)

    consensus, pairrows = [], []
    model_a = book('1_consensus test/model consensus/5.6 sol consensus test screened.xlsx')[1:]
    model_b = book('1_consensus test/model consensus/6.1 sol consensus test screened.xlsx')[1:]
    human_a = book('1_consensus test/model-human consensus/6.1 sol test.xlsx')[1:]
    human_b = book('1_consensus test/model-human consensus/artificial test.xlsx')
    full_a = book('2_consensus test/6.1 sol consensus test2 screened.xlsx')
    full_b = book('2_consensus test/artificial experiment.xlsx')
    norm = lambda s: str(s).strip().lower().replace('included', 'include')
    def compare(name, pairs):
        a = [p['model_a_label'] for p in pairs]
        b = [p['model_b_or_human_label'] for p in pairs]
        consensus.append({'comparison': name, 'n': len(pairs), 'agreements': sum(x == y for x, y in zip(a, b)),
                          'agreement_proportion': sum(x == y for x, y in zip(a, b)) / len(pairs),
                          'cohen_kappa': cohen_kappa_score(a, b),
                          'confusion_labels': 'exclude;include;unclear',
                          'confusion_matrix_rows_a_cols_b': json.dumps(confusion_matrix(a, b, labels=['exclude', 'include', 'unclear']).tolist())})
    for name, aa, bb, aid, bid, ac, bc, skip in [
        ('title_abstract_model_model', model_a, model_b, 0, 0, 12, 12, False),
        ('title_abstract_model_human', human_a, human_b, 1, 0, 17, 13, False),
        ('later_screening_model_human_all_rows', full_a, full_b, 0, 0, 20, 20, True)]:
        pairs = []
        assert len(aa) == len(bb)
        for i, (a, b) in enumerate(zip(aa, bb)):
            if skip and (len(a) <= ac or not a[ac] or not b[bc]):
                continue
            assert str(a[aid]) == str(b[bid]), (name, i)
            row = {'comparison': name, 'model_source_row_index_1based': i + (1 if skip else 2),
                   'comparison_source_row_index_1based': i + (1 if skip or name == 'title_abstract_model_human' else 2),
                   'record_id': a[aid], 'title': a[2] if name == 'title_abstract_model_human' else a[1],
                   'model_a_label': norm(a[ac]), 'model_b_or_human_label': norm(b[bc]),
                   'agreement': norm(a[ac]) == norm(b[bc]), 'basis': str(a[19]) if skip else 'title and abstract'}
            pairs.append(row)
        compare(name, pairs)
        pairrows.extend(pairs)
        if skip:
            unique = {}
            for p in pairs:
                key = str(p['record_id'])
                if key in unique:
                    assert (p['model_a_label'], p['model_b_or_human_label']) == (unique[key]['model_a_label'], unique[key]['model_b_or_human_label'])
                unique.setdefault(key, p)
            compare('later_screening_model_human_unique_records', list(unique.values()))
            compare('later_screening_fulltext_basis_only', [p for p in pairs if p['basis'] == '全文'])
    write('consensus_recalculated.csv', consensus)
    write('consensus_paired_decisions.csv', pairrows)
    write('consensus_disagreements.csv', [r for r in pairrows if not r['agreement']])

    search = [
        {'stage': 'Raw retrieval results', 'n': 5299, 'source': 'text.docx narrative', 'verification': 'Narrative only; raw per-query logs not located in check workbooks'},
        {'stage': 'Repeated identical record IDs across retrieval runs', 'n': 164, 'source': 'text.docx narrative', 'verification': 'Narrative only'},
        {'stage': 'Unique retrieved IDs before screening', 'n': 5135, 'source': 'text.docx narrative and check/round1_corrected.xlsx', 'verification': '4993 candidates +142 exclusions =5135'},
        {'stage': 'Duplicate titles removed', 'n': 54, 'source': 'check/round1_corrected.xlsx:Excluded', 'verification': 'Counted exact exclusion label'},
        {'stage': 'Duplicate DOI removed', 'n': 1, 'source': 'check/round1_corrected.xlsx:Excluded', 'verification': 'Counted exact exclusion label'},
        {'stage': 'Metadata-identifiable not peer reviewed full paper', 'n': 87, 'source': 'check/round1_corrected.xlsx:Excluded', 'verification': 'Counted exact exclusion label'},
        {'stage': 'Title abstract screened', 'n': 4993, 'source': 'check/round1_corrected.xlsx:Candidates', 'verification': 'Nonheader rows'},
        {'stage': 'Provisional include', 'n': 82, 'source': 'check/round2_corrected.xlsx:included', 'verification': 'Nonheader rows'},
        {'stage': 'Unclear advanced', 'n': 503, 'source': 'check/round2_corrected.xlsx:unclear', 'verification': 'Nonheader rows'},
        {'stage': 'Title abstract excluded', 'n': 4408, 'source': 'check/round2_corrected.xlsx:excluded', 'verification': 'Nonheader rows'},
        {'stage': 'Advanced assessment', 'n': 585, 'source': 'check/round3.xlsx', 'verification': '82+503; do not imply585 retrieved full texts'},
        {'stage': 'Unclear to include', 'n': 80, 'source': 'check/round3.xlsx:unclear include', 'verification': 'Nonheader rows'},
        {'stage': 'Unclear to exclude', 'n': 423, 'source': 'check/round3.xlsx:unclear exclude', 'verification': 'Nonheader rows'},
        {'stage': 'Provisional include retained', 'n': 60, 'source': 'check/round3.xlsx:include include', 'verification': 'Nonheader rows'},
        {'stage': 'Provisional include rejected', 'n': 22, 'source': 'check/round3.xlsx:include exclude', 'verification': 'Nonheader rows'},
        {'stage': 'Retained before date narrowing', 'n': 140, 'source': 'check/Final included_corrected.xlsx', 'verification': '80+60'},
        {'stage': 'Pre2022 excluded by subsequent scope refinement', 'n': 15, 'source': '最终/Final included_descending_numbered.xlsx', 'verification': 'Numbered records126–140; screening_year<2022'},
        {'stage': 'Final corpus', 'n': 125, 'source': '03_revised_results/papers_supplement_enhanced.csv', 'verification': 'Records1–125 in final numbered workbook'}]
    write('search_screening_audit.csv', search)

    facts = {'papers': len(papers), 'evaluation_cases': len(read('03_revised_results/evaluation_cases_supplement_enhanced.csv')),
             'candidate_chains': len(chains), 'dimension_mapped': sum(r['dimension_code'] in 'ABCDE' and len(r['dimension_code']) == 1 for r in chains),
             'indicator_mapped': sum(r['indicator_code'] not in ['', 'UNMAPPED', 'NA', 'NR'] for r in chains),
             'tool_instances': len(tools), 'tool_instances_classified': sum(r['tool_code'] in ['M1', 'M2', 'M3', 'M4', 'M5'] for r in tools),
             'dimension_counts': dict(Counter(r['dimension_code'] for r in chains)), 'tool_counts': dict(Counter(r['tool_code'] for r in tools)),
             'quality_tiers': dict(Counter(r['revised_quality_tier'] for r in chains)),
             'audit_statuses': {s: dict(Counter(r['status'] for r in audits if r['standard'] == s)) for s in ['U5', 'A2', 'A3', 'A4', 'A6', 'A7', 'E1']},
             'coding_year_counts': dict(Counter(int(p['year']) for p in papers)),
             'screening_year_counts': dict(Counter(r['screening_year'] for r in catalogue)),
             'year_mismatches': sum(r['coded_year'] != r['screening_year'] for r in catalogue),
             'doi_mismatches': sum(r['doi_correction'] for r in catalogue)}
    candidate_papers = set(r['paper_id'] for r in chains)
    mapped_papers = set(r['paper_id'] for r in chains if r['dimension_code'] != 'UNMAPPED')
    facts.update(candidate_record_papers=len(candidate_papers), dimension_mapped_papers=len(mapped_papers),
                 only_unmapped_papers=len(candidate_papers - mapped_papers),
                 no_candidate_record_papers=len(papers) - len(candidate_papers),
                 papers_with_some_unmapped_records=len(set(r['paper_id'] for r in chains if r['dimension_code'] == 'UNMAPPED')))
    for name, field in [('main', 'model_eligible_main'), ('expanded', 'model_eligible_sensitivity')]:
        selected = [r for r in chains if r[field] == '1']
        instances = [r for r in tools if r[field] == '1' and r['tool_code'] != 'UNMAPPED']
        facts[name] = {'chains': len(selected), 'papers': len(set(r['paper_id'] for r in selected)), 'tool_instances': len(instances), 'tool_papers': len(set(r['paper_id'] for r in instances))}
    (OUT / 'audit_facts.json').write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding='utf-8')

    # Fetch official metadata into a new cache; never overwrite review source data.
    cachefile = OUT / 'crossref_corpus_metadata.json'
    cache = json.loads(cachefile.read_text(encoding='utf-8')) if cachefile.exists() else {}
    missing = [r['doi'] for r in catalogue if r['doi'] not in cache or 'error' in cache[r['doi']]]
    with ThreadPoolExecutor(max_workers=2) as executor:
        jobs = {executor.submit(metadata, d): d for d in missing}
        for future in as_completed(jobs):
            cache[jobs[future]] = future.result()
    cachefile.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    for r in catalogue:
        meta = cache[r['doi']]
        r['crossref_status'] = 'error' if 'error' in meta else 'ok'
        r['crossref_title'] = (meta.get('title') or [''])[0]
        for field in ['published-online', 'published-print', 'published', 'issued']:
            date = ((meta.get(field) or {}).get('date-parts') or [[]])[0]
            r['crossref_' + field.replace('-', '_')] = '-'.join(str(v) for v in date)
    write('reviewed_corpus_catalogue.csv', catalogue)
    sy = {str(r['paper_id']): r['screening_year'] for r in catalogue}
    cy = {str(r['paper_id']): int(r['crossref_published'].split('-')[0]) for r in catalogue if r['crossref_published']}
    year_rows = []
    for unit, rows, outcome in [('papers', papers, None), ('chains', chains, 'dimension_code'), ('tools', tools, 'tool_code')]:
        for convention in ['coded', 'screening', 'crossref_published']:
            vals = Counter((int(r['year']) if convention == 'coded' else (sy if convention == 'screening' else cy).get(str(int(r['paper_id'])), 'unavailable'), r[outcome] if outcome else 'all') for r in rows)
            year_rows.extend({'unit': unit, 'year_convention': convention, 'year': y, 'category': cat, 'n': n} for (y, cat), n in sorted(vals.items()))
    write('publication_year_sensitivity.csv', year_rows)
    print(json.dumps(facts, ensure_ascii=False, indent=2))
    print('Crossref ok', sum(r['crossref_status'] == 'ok' for r in catalogue), 'of', len(catalogue))

if __name__ == '__main__':
    run()
