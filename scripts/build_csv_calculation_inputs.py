#!/usr/bin/env python3
"""Export local grouped campus CSV inputs after a fresh raw recount."""
import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/comparison'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,required=True,help='Local output directory; this extract is not published with the site')
output=parser.parse_args().output_dir.resolve()
output.mkdir(parents=True,exist_ok=True)
d=json.loads((OUT/'comparison.json').read_text(encoding='utf-8'))
figures=json.loads((OUT/'figure_sources.json').read_text(encoding='utf-8'))['records']
columns=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age','sdr']
groups=[]
for year in (2022,2024,2026):
    source=figures[f'summary-{year}-campus-site-all-ages']['sources'][0]
    path=ROOT/'data/raw/early_voting'/f'wake_{str(year)}{ {2022:"1108",2024:"1105",2026:"1103"}[year]}.csv'
    with path.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest()==source['wake_csv_sha256'],year
    window=next(r for r in d['summary'] if r['year']==year and r['scope']=='Campus site')
    counter=Counter()
    # Latin-1 maps every byte; the selected source fields use ASCII values.
    with path.open(encoding='latin-1',newline='') as stream:
        for row in csv.DictReader(stream):
            r={k:v.strip() for k,v in row.items()}
            parts=r['ballot_rtn_dt'].split('/')
            day=f'{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}' if len(parts)==3 else ''
            if r['county_desc']!='WAKE' or r['site_name']!=d['site_mapping'][str(year)] or r['ballot_req_type'].upper() not in ('ONE-STOP','ONE STOP','EARLY VOTING') or r['ballot_rtn_status']!='ACCEPTED' or not window['start_date']<=day<=window['end_date']:continue
            counter[tuple(row[k] for k in columns)]+=1
    assert sum(counter.values())==window['all_ages']
    def number(value):return int(value.strip()) if value.strip().isdigit() else -1
    assert sum(n for values,n in counter.items() if 18<=number(values[5])<=24)==window['age_18_24']
    assert sum(n for values,n in counter.items() if 18<=number(values[5])<=22)==window['age_18_22']
    assert sum(n for values,n in counter.items() if values[6].strip().upper() in ('Y','YES'))==window['same_day_registration']
    for lo,hi,label in ((18,24,'18–24'),(25,34,'25–34'),(35,44,'35–44'),(45,64,'45–64'),(65,120,'65+')):
        expected=sum(r['votes'] for r in d['demographics'] if r['year']==year and r['scope']=='Campus site' and r['dimension']=='age_group' and r['value']==label)
        assert sum(n for values,n in counter.items() if lo<=number(values[5])<=hi)==expected,(year,label)
    groups.extend((year,*values,n) for values,n in sorted(counter.items()))
    print(f'{year}: {sum(counter.values()):,} ballots in {len(counter):,} original-field groups; age and registration totals match.')
with (output/'campus_age_source_groups.csv').open('w',encoding='utf-8',newline='') as stream:
    writer=csv.writer(stream);writer.writerow(['source_year',*columns,'matching_records']);writer.writerows(groups)
print(f'Wrote {len(groups):,} grouped rows. Names, addresses and voter identifiers are excluded.')
