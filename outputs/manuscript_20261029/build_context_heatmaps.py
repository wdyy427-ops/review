import json
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
RELATIVE_SOURCE = Path('04_RQ1/rq1_domain_stage_by_dimension_indicator_tool.csv')
DATA_ROOT = ROOT / 'source_data'
if not DATA_ROOT.is_dir():
    DATA_ROOT = ROOT.parent / 'rq_review_20261024' / 'supplement_enhanced_v2'
SOURCE = DATA_ROOT / RELATIVE_SOURCE
with SOURCE.open(encoding='utf-8-sig', newline='') as stream:
    records = {
        (row['context_field'], row['context_code'], row['target_level'], row['target_code']): row
        for row in csv.DictReader(stream)
    }

CONTEXTS = {
    'domain': (['D1', 'D2', 'D3', 'D4', 'D5', 'D6'],
               ['Visual\ncommunication', 'Industrial /\nproduct', 'Fashion', 'Interior', 'Service', 'UI/UX']),
    'stage': (['S1', 'S2', 'S3', 'S4'],
              ['Research', 'Ideation', 'Prototyping\nand testing', 'Implementation']),
}
dimension_names = [
    'A  Design outcome quality',
    'B  Design process quality',
    'C  Designers’ cognition, affect,\n     and abilities',
    'D  Human–AI interaction experience',
    'E  Social and contextual value',
]
indicator_names = {
    'A1': 'Novelty', 'A2': 'Aesthetic appeal', 'A3': 'Suitability',
    'A4': 'Feasibility', 'A5': 'Fidelity', 'A6': 'Comprehensiveness',
    'C1': 'Inspiration', 'C2': 'Knowledge acquisition', 'C3': 'Self-efficacy',
    'C4': 'Engagement and immersion', 'C5': 'Enjoyment', 'C6': 'Reflection',
    'C7': 'Fixation and dependence', 'C8': 'Capability expansion',
    'D1': 'Ease of use', 'D2': 'Intention to use', 'D3': 'Sense of control',
    'D4': 'Explainability', 'D5': 'Trust', 'D6': 'Agency',
    'D7': 'Roles, division of labor,\n     and contribution fairness',
    'D8': 'Communication, coordination,\n     conflict, and shared understanding',
}

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'pdf.fonttype': 42, 'ps.fonttype': 42})

def aggregate(context, field, codes, groups):
    rows = [[records[(context + 's', group, field, code)] for group in groups]
            for code in codes]
    counts = np.array([[int(row['n']) for row in line] for line in rows])
    denom = np.array([int(row['denominator']) for row in rows[0]])
    if field == 'dimension_code':
        assert np.array_equal(counts.sum(axis=0), denom)
    assert all(int(row['denominator']) == n for line in rows for row, n in zip(line, denom))
    return counts, denom

def draw(context, field, codes, labels, title, subtitle, filename, height, vmax, ticks):
    groups, group_names = CONTEXTS[context]
    counts, denom = aggregate(context, field, codes, groups)
    shares = counts / denom * 100
    fig = plt.figure(figsize=(12.8, height), facecolor='white')
    ax = fig.add_axes([0.355, 0.17 if height < 8 else 0.115,
                       0.545, 0.61 if height < 8 else 0.755])
    norm = Normalize(0, vmax)
    im = ax.imshow(shares, cmap='Blues', norm=norm, aspect='auto', interpolation='nearest')
    ax.set_xticks(range(len(groups)), [f'{label}\nn = {n}' for label, n in zip(group_names, denom)], fontsize=10)
    ax.xaxis.tick_top()
    ax.tick_params(axis='both', which='both', length=0, pad=9)
    ax.set_yticks(range(len(codes)), labels, fontsize=10.5)
    ax.set_xticks(np.arange(-.5, len(groups), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(codes), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.3)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(len(codes)):
        for j in range(len(groups)):
            color = 'white' if norm(shares[i, j]) > .60 else '#18334b'
            ax.text(j, i, str(counts[i, j]), ha='center', va='center', color=color, fontsize=11)
    if field == 'indicator_code':
        for boundary in [5.5, 13.5]:
            ax.axhline(boundary, color='#526676', lw=1.6)
    cax = fig.add_axes([.925, ax.get_position().y0, .015, ax.get_position().height])
    cb = fig.colorbar(im, cax=cax, ticks=ticks)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=10)
    cb.set_label(f'Share within design {context} (%)', labelpad=11)
    fig.text(.04, .965, title, ha='left', va='top', size=17, weight='bold', color='#182b3a')
    fig.text(.04, .918 if height < 8 else .935, subtitle, ha='left', va='top', size=10.5, color='#53616a')
    note = ('Cell labels: record counts. Color: percentage of mapped records within each domain.\n'
            'Domain labels can overlap; column totals do not sum to the number of unique records.')
    if field == 'indicator_code':
        note = ('Cell labels: record counts. Color: percentage of all indicator-mapped records within each domain.\n'
                'Rows show all indicators in A, C, and D; displayed percentages need not sum to 100%.\n'
                'Domain labels can overlap. Zero indicates no mapped record in the coded dataset.')
    note = note.replace('domain', context).replace('Domain', context.capitalize())
    fig.text(.04, .065 if height < 8 else .058, note, ha='left', va='bottom', size=9.5,
             color='#53616a', linespacing=1.55)
    fig.savefig(OUT / f'{filename}.png', dpi=300, facecolor='white')
    fig.savefig(OUT / f'{filename}.pdf', facecolor='white')
    plt.close(fig)
    return counts, denom


def main():
    OUT.mkdir(exist_ok=True)
    manifest = []
    for context in CONTEXTS:
        for field, codes, labels, title, subtitle, prefix, height, limit, step, denominator in [
            ('dimension_code', list('ABCDE'), dimension_names, 'Evaluation dimensions',
             'All five evaluation dimensions · 460 unique dimension-mapped records',
             'evaluation_dimensions', 6.8, 35, 5, 'all dimension-mapped records'),
            ('indicator_code', list(indicator_names),
             [f'{code}  {label}' for code, label in indicator_names.items()], 'Subjective indicators',
             'A  Design outcome quality     C  Cognition, affect, and abilities     D  Human–AI interaction experience',
             'subjective_indicators_ACD', 13.8, 14, 2, 'all indicator-mapped records'),
        ]:
            title = f'{title} across design {context}s'
            filename = f'{prefix}_by_design_{context}'
            draw(context, field, codes, labels, title, subtitle, filename, height, limit,
                 list(range(0, limit + 1, step)))
            scope = ' The rows show all indicators in dimensions A, C, and D.' if field == 'indicator_code' else ''
            manifest.append({
                'id': filename,
                'appendix_label': f'D{len(manifest) + 1}',
                'caption': f'{title}. Cell labels show record counts. Color shows the share of '
                           f'{denominator} within each {context}.{scope}',
                'files': {ext: f'figures/{filename}.{ext}' for ext in ('png', 'pdf')},
                'source_files': [RELATIVE_SOURCE.as_posix()],
                'aspect_ratio': 12.8 / height,
            })
    (ROOT / 'context_heatmap_manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
