"""Recount original NCSBE CSVs independently of the displayed aggregate inputs."""
import csv,json,math
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
benchmarks={r['cohort']:r for r in s['queries']['age_growth_benchmarks']['rows']}
counts=Counter()
focal=Counter()
for year,suffix in [(2022,'20221108'),(2026,'20261103')]:
    window=next(r for r in s['queries']['summary']['rows'] if r['year']==year and r['scope']=='Wake County')
    site=s['comparison']['site_mapping'][str(year)]
    with (ROOT/f'data/raw/early_voting/wake_{suffix}.csv').open(encoding='latin-1',newline='') as f:
        for r in csv.DictReader(f):
            if r['county_desc'].strip().upper()!='WAKE' or r['ballot_req_type'].strip().upper() not in {'ONE-STOP','ONE STOP','EARLY VOTING'} or r['ballot_rtn_status'].strip().upper()!='ACCEPTED':continue
            date=datetime.strptime(r['ballot_rtn_dt'].strip(),'%m/%d/%Y').date().isoformat()
            if not window['start_date']<=date<=window['end_date']:continue
            try:age=int(r['age'])
            except ValueError:continue
            cohort=next((label for lo,hi,label in [(18,24,'18–24'),(25,34,'25–34'),(35,44,'35–44'),(45,64,'45–64'),(65,120,'65+')] if lo<=age<=hi),None)
            if cohort is None:continue
            counts[year,'county',cohort]+=1
            if r['site_name'].strip()==site:counts[year,'site',cohort]+=1
            if r['precinct_desc'].strip() in {'PRECINCT 01-23','PRECINCT 01-31'}:focal[year,r['precinct_desc'].strip(),cohort]+=1
for cohort,b in benchmarks.items():
    for y in [2022,2026]:
        assert b[f'county_ballots_{y}']==counts[y,'county',cohort]
        assert b[f'site_ballots_{y}']==counts[y,'site',cohort]
    county=(counts[2026,'county',cohort]-counts[2022,'county',cohort])/counts[2022,'county',cohort]*100
    site=(counts[2026,'site',cohort]-counts[2022,'site',cohort])/counts[2022,'site',cohort]*100
    assert math.isclose(b['county_growth_pct'],county,abs_tol=1e-10)
    assert math.isclose(b['site_growth_pct'],site,abs_tol=1e-10)
    assert math.isclose(b['site_growth_gap_pp'],site-county,abs_tol=1e-10)
    rows=[r for r in s['queries']['precinct_age_changes']['rows'] if r['cohort']==cohort]
    for y in [2022,2026]:assert sum(r[f'ballots_{y}'] or 0 for r in rows)==counts[y,'county',cohort]
    for r in rows:
        if r['area'] in {'PRECINCT 01-23','PRECINCT 01-31'}:
            for y in [2022,2026]:assert r[f'ballots_{y}']==focal[y,r['area'],cohort]
        assert r['county_growth_pct']==b['county_growth_pct']
        if r['growth_pct'] is None:assert r['growth_gap_pp'] is None
        else:assert math.isclose(r['growth_gap_pp'],r['growth_pct']-county,abs_tol=1e-10)
    print(cohort,': county',round(county,4),'site',round(site,4),'gap',round(site-county,4))
print('Passed original-record recount of county/site age benchmarks, focal precinct counts, all-precinct reconciliation, and missing-baseline semantics.')
