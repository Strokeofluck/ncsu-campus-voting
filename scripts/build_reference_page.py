#!/usr/bin/env python3
"""Refresh the existing figure-verification page from independent audit inputs."""
import json,re
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
checks=json.loads((ROOT/'data/processed/comparison/reference_audit.json').read_text(encoding='utf-8'))['checks']
path=ROOT/'verify-figures.html';old=path.read_text(encoding='utf-8')
head=old[:old.index('<body>')]
num=lambda n:f'{n:,}'
labels={'all_ages':'All ages','age_18_24':'Ages 18–24','age_18_22':'Ages 18–22','age_18_24_share':'18–24 share','same_day_registration':'Same-day registration'}
def metric(value,key):return f'{value:.1f}%' if key=='age_18_24_share' else num(value)
def summaryrow(c):
    y=c['year'];a=c['actual'];site='Western Boulevard' if y==2026 else 'Talley Student Union'
    return f'<tr><th>{site} · {y}</th>'+''.join(f'<td><a href="#proof-{y}-{key}">{metric(a[key],key)}</a></td>' for key in labels)+'</tr>'
sections=[]
for c in checks:
    y=c['year'];a=c['actual'];src=c['source'];url=escape(src['url']);site='Western Boulevard Business Services' if y==2026 else 'Talley Student Union'
    cards=[]
    for key,label in labels.items():
        if key=='all_ages':values=c['daily'].values();desc='One accepted early-voting record at this site within the date window.'
        elif key=='same_day_registration':values=[r['same_day_registration'] for r in c['daily_metrics']];desc='Accepted site records with sdr equal to Y or YES, across all ages.'
        elif key=='age_18_24_share':values=[];desc='College-age ballots divided by all accepted ballots at this site, multiplied by 100.'
        else:values=[c['ages_18_24'][str(age)] for age in range(18,25 if key=='age_18_24' else 23)];desc='Accepted site records within the inclusive source-age bounds.'
        arithmetic=f'{num(a["age_18_24"])} ÷ {num(a["all_ages"])} × 100 = {a[key]:.6f}% → ' if key=='age_18_24_share' else ' + '.join(num(v) for v in values)+' = '
        cards.append(f'<article class="proof" id="proof-{y}-{key}" tabindex="-1"><p class="label">{label} · {y}</p><h3>{metric(a[key],key)}</h3><p>{desc}</p><p class="arithmetic">{arithmetic}<mark>{metric(a[key],key)}</mark></p><p class="mini">Inputs: the daily and age breakdowns below. <a href="{url}">Original official ZIP</a></p></article>')
    daily=''.join('<tr><th scope="row">'+r['date']+'</th>'+''.join('<td>'+num(r[k])+'</td>' for k in ['all_ages','age_18_24','age_18_22','same_day_registration'])+'</tr>' for r in c['daily_metrics'])
    ages=''.join(f'<tr><th scope="row">{age}</th><td>{num(value)}</td></tr>' for age,value in c['ages_18_24'].items())
    exclusions=', '.join(f'{num(v)} {escape(k)}' for k,v in c['status_counts_before_accepted_filter'].items() if k!='ACCEPTED') or 'None'
    details=[('CSV inside official ZIP',src['member']),('Source site label',c['site_name']),('Filters','county_desc = WAKE; ballot_req_type = ONE-STOP, ONE STOP or EARLY VOTING; ballot_rtn_status = ACCEPTED; ballot_rtn_dt within the dates above.'),('Source last modified',src['last_modified']),('Downloaded',src['downloaded_at']),('Original archive SHA-256',src['sha256']),('Wake CSV SHA-256',src['wake_csv_sha256']),('Excluded records in this site/date window',exclusions)]
    sections.append(f'''<section class="year" id="year-{y}"><header><p class="eyebrow">OFFICIAL RECORDS → PROJECT CALCULATION</p><h2>{y}: {site}</h2><p>{c['start_date']} through {c['end_date']} · first {data['matched_days']} early-voting days</p></header>
<div class="links"><a class="button" href="https://www.ncsbe.gov/results-data/absentee-and-provisional-data#:~:text={y}%20Nov" target="_blank" rel="noopener">Official NCSBE page: highlight this download ↗</a><a class="button secondary" href="{url}">Download original ZIP</a></div>
<p class="mini">The official catalog lists the source archive; the campus totals below are project calculations from its records.</p>
<details><summary>Exact source, filters and snapshot</summary><dl>{''.join(f'<dt>{k}</dt><dd><code class="hash">{escape(v)}</code></dd>' for k,v in details)}</dl><p>Hashes identify the downloaded snapshot, not an NCSBE digital signature. Later downloads of the live URL can yield different counts.</p></details>
<div class="proof-grid">{''.join(cards)}</div><details class="breakdowns" open><summary>Daily and individual-age counts used in the arithmetic</summary><div class="breakdown-grid"><div class="scroll"><table><caption>Accepted site records by voting date</caption><thead><tr><th>Date</th><th>All ages</th><th>18–24</th><th>18–22</th><th>Same-day registration</th></tr></thead><tbody>{daily}</tbody><tfoot><tr><th>Sum</th>{''.join(f'<td>{num(a[k])}</td>' for k in ['all_ages','age_18_24','age_18_22','same_day_registration'])}</tr></tfoot></table></div><div><table><caption>Accepted site records by age</caption><thead><tr><th>Age</th><th>Ballots</th></tr></thead><tbody>{ages}</tbody><tfoot><tr><th>18–24 total</th><td>{num(a['age_18_24'])}</td></tr><tr><th>18–22 subtotal</th><td>{num(a['age_18_22'])}</td></tr></tfoot></table></div></div></details></section>''')
body=f'''<body><main><nav><a href="index.html">← Interactive report</a> · <a href="references.html">All references</a></nav><p class="eyebrow">NC STATE CAMPUS VOTING</p><h1>Verify the campus-site figures</h1><p class="lede">Click a figure to inspect its arithmetic, daily and age inputs, and original NCSBE archive. All three years cover the first {data['matched_days']} early-voting days. 2026 is preliminary through {data['as_of']}.</p><p class="note">These are project calculations from official ballot records. Ages 18–24 are a college-age proxy, not verified students. 2024 was presidential; 2022 and 2026 are midterms. These comparisons do not establish the move's causal effect.</p><div class="scroll"><table><thead><tr><th>Site / year</th>{''.join(f'<th>{v}</th>' for v in labels.values())}</tr></thead><tbody>{''.join(summaryrow(c) for c in checks)}</tbody></table></div>
{''.join(sections)}<footer><h2>Reproduce the check yourself</h2><p>Download the official by-county archives, keep the Wake CSVs in ignored raw storage, and run:</p><pre><code>python scripts/audit_campus_figures.py
python scripts/build_reference_page.py</code></pre><p><a href="data/processed/comparison/reference_audit.json">Aggregate audit inputs and source hashes</a> · <a href="data/processed/comparison/campus_site_matched_counts.csv">Campus-site table</a></p><p class="mini">Raw voter-level files are not published. The audit independently recounts campus records and verifies archive and CSV hashes. No separate Wake County publication reconciliation is claimed for 2024 or 2026.</p></footer></main></body></html>'''
path.write_text(head+body,encoding='utf-8')
print('Updated figure-verification page from audited aggregates.')
