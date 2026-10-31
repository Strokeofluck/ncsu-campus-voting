#!/usr/bin/env python3
"""Build the portfolio-style reference page from the reviewed comparison snapshot."""
import json,re
from datetime import date
from html import escape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/comparison'
comparison=json.loads((DATA/'comparison.json').read_text(encoding='utf-8'))
records=json.loads((DATA/'figure_sources.json').read_text(encoding='utf-8'))['records']
library=ROOT/'report-source/reference-library.html'
if not library.exists():
    old=(ROOT/'references.html').read_text(encoding='utf-8')
    keep=[]
    for card in re.findall(r'<div class="card">[\s\S]*?</div>',old):
        if any(name in card for name in ['NC State — 2026 early-voting location','Wake County — Early Voting Sites by Election','NCSBE — 2022 Early Voting Sites']):keep.append(card)
    marker='<h2 class="section">Election Day</h2>'
    assert marker in old,'Preserve the original source library before rebuilding'
    keep.append(old[old.index(marker):old.index('</body>')])
    library.write_text('\n'.join(keep)+'\n',encoding='utf-8')

def nice(day):
    d=date.fromisoformat(day)
    return f'{d:%B} {d.day}, {d.year}'

def proof_id(base,kind):
    return {'all':'growth-'+str(base)+'-campus-site-all-ages','college':'growth-'+str(base)+'-campus-site-age-18-24',
        'share':'change-'+str(base)+'-age-group-18-24','older':'change-'+str(base)+'-age-group-65',
        'county':'growth-'+str(base)+'-wake-county-age-18-24'}[kind]

def summary(year,scope):return next(r for r in comparison['summary'] if r['year']==year and r['scope']==scope)
def age_share(year,group):return records[f'demographic-{year}-age-group-{group}']['value']
def value(number,unit):return f'{number:.1f}%' if unit=='%' else f'{number:,}'
def change(number,unit):return f'{number:+.1f}'+('%' if unit=='%' else ' pp')
def link(figure,text,label):
    assert figure in records,figure
    return f'<a class="figure-link" data-figure="{figure}" href="csv-proof.html?figure={figure}&amp;tab=calculation" aria-label="{escape(label,quote=True)}">{escape(text)}</a>'

rows=[]
for kind,label,field,scope,unit,share_group in [
 ('all','Talley → Western Boulevard · all ages','all_ages','Campus site','ballots',None),
 ('college','Talley → Western Boulevard · ages 18–24','age_18_24','Campus site','ballots',None),
 ('share','College-age share of site ballots',None,'Campus site','%','18-24'),
 ('older','65+ share of site ballots',None,'Campus site','%','65'),
 ('county','Wake County · ages 18–24','age_18_24','Wake County','ballots',None)]:
    numbers=[]
    for year in [2022,2026]:
        numbers.append(age_share(year,share_group) if share_group else summary(year,scope)[field])
    root=records[proof_id(2022,kind)]
    expected=numbers[1]-numbers[0] if unit=='%' else (numbers[1]-numbers[0])/numbers[0]*100
    assert abs(root['value']-expected)<1e-8
    rows.append(f'<tr data-kind="{kind}"'+(' class="is-selected"' if kind=='share' else '')+f'><th scope="row">{label}</th><td>{value(numbers[0],unit)}</td><td>{value(numbers[1],unit)}</td><td>{change(root["value"],root["unit"])}</td><td>{link(root["id"],"Check math","Check math: "+label)}</td></tr>')

sources=[];source_records=[]
for year in [2022,2024,2026]:
    s=records[f'summary-{year}-campus-site-all-ages']['sources'][0];w=summary(year,'Campus site');source_records.append(s)
    sources.append(f'''<article class="source-card"><p class="source-year">{year}</p><h3>{'Western Boulevard Business Services' if year==2026 else 'Talley Student Union'}</h3><p>{nice(w['start_date'])}–{nice(w['end_date'])}<br>First {comparison['matched_days']} early-voting days.</p><code>{escape(s['member'])}</code><p class="source-links"><a href="{escape(s['url'],quote=True)}">Original government ZIP ↗</a><a href="{escape(s['listing_url'],quote=True)}" target="_blank" rel="noopener">Official file listing ↗</a><a href="{escape(s['catalog'],quote=True)}" target="_blank" rel="noopener">NCSBE catalog ↗</a></p><details><summary>Exact site label and source snapshot</summary><dl>{''.join('<dt>'+label+'</dt><dd><code>'+escape(text)+'</code></dd>' for label,text in [('Site label',comparison['site_mapping'][str(year)]),('Source last modified (UTC)',s['last_modified']),('Downloaded (UTC)',s['downloaded_at']),('Archive SHA-256',s['sha256']),('Wake CSV SHA-256',s['wake_csv_sha256'])])}</dl></details></article>''')

required={proof_id(base,kind) for base in [2022,2024] for kind in ['all','college','share','older','county']}
required|={f'demographic-{year}-age-group-{group}' for year in [2022,2024,2026] for group in ['18-24','65']}
assert all(key in records for key in required)
payload={'summary':comparison['summary'],'records':{key:{k:records[key][k] for k in ['id','label','value','unit']} for key in sorted(required)},'matched_days':comparison['matched_days'],'as_of':comparison['as_of']}
period='Talley: '+nice(summary(2022,'Campus site')['start_date'])+'–'+nice(summary(2022,'Campus site')['end_date'])+'. Western Boulevard: '+nice(summary(2026,'Campus site')['start_date'])+'–'+nice(summary(2026,'Campus site')['end_date'])+'. Both elections are midterms.'
template=(ROOT/'report-source/references.html').read_text(encoding='utf-8')
proof=(ROOT/'csv-proof.html').read_text(encoding='utf-8')
workspace=re.search(r'<main\b[^>]*>([\s\S]*?)</main>',proof).group(1)
workspace=re.sub(r'<nav>[\s\S]*?</nav>','',workspace)
workspace=re.sub(r'<h1 id="title">[\s\S]*?</h1>','<span id="title" hidden></span>',workspace)
workspace=re.sub(r'<p>Follow the number[\s\S]*?</p>','',workspace)
workspace=re.sub(r'<p class="muted">The Excel workbook uses[\s\S]*?</p>','',workspace)
workspace=re.sub(r'id="([^"]+)"',lambda m:'id="proof-'+m[1]+'"',workspace)
workspace=re.sub(r'(aria-controls|aria-labelledby)="([^"]+)"',lambda m:m[1]+'="'+' '.join('proof-'+value for value in m[2].split())+'"',workspace)
workspace='<div id="csv-workspace" class="csv-workspace" data-csv-proof data-proof-prefix="proof-">'+workspace+'</div>'
replacements={'__MATCHED_DAYS__':str(comparison['matched_days']),'__CUTOFF__':nice(comparison['as_of']),'__PERIOD_NOTE__':period,'__INITIAL_ROWS__':'\n'.join(rows),'__SOURCE_CARDS__':'\n'.join(sources),'__REFERENCE_LIBRARY__':library.read_text(encoding='utf-8'),'__REFERENCE_DATA__':json.dumps(payload,ensure_ascii=False).replace('<','\\u003c'),'__CSV_WORKSPACE__':workspace}
for key,text in replacements.items():
    assert key in template,key
    template=template.replace(key,text)
assert not re.search(r'__[A-Z_]+__',template)
(ROOT/'references.html').write_text(template,encoding='utf-8')
print('Built portfolio-style reporting references: five comparison measures, both baselines, three source snapshots and preserved earlier references.')
