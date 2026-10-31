#!/usr/bin/env python3
"""Verify geography partitions, missing-area semantics and exported evidence."""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
from build_party_trends import AGE_BANDS
root=Path(__file__).resolve().parents[1];s=json.loads((root/'report-source/snapshot.json').read_text(encoding='utf-8'));rows=s['queries']['geography']['rows']
assert rows==json.loads((root/'data/processed/comparison/geography.json').read_text(encoding='utf-8'))['rows']
with (root/'data/processed/comparison/matched_geography.csv').open(encoding='utf-8',newline='') as f:export=list(csv.DictReader(f))
assert len(rows)==len(export)==5670
for a,b in zip(rows,export):assert {k:('' if v is None else str(v)) for k,v in a.items()}==b
expected=Counter();groups=defaultdict(list);lookup={}
for r in s['queries']['party_daily']['rows']:
 if r['day']==16:expected[r['year'],r['scope'],r['cohort']]+=r['cumulative']
for r in rows:
 assert set(r)=={'year','dimension','area','cohort','area_present','site_ballots','other_wake_ballots','wake_ballots','site_share_pct'}
 key=r['year'],r['dimension'],r['area'],r['cohort'];assert key not in lookup;lookup[key]=r
 groups[r['year'],r['dimension'],r['cohort']].append(r)
 if r['area_present']:
  assert r['site_ballots']+r['other_wake_ballots']==r['wake_ballots']
  assert r['site_share_pct']==(r['site_ballots']/r['wake_ballots']*100 if r['wake_ballots'] else None)
 else:assert all(r[k] is None for k in ['site_ballots','other_wake_ballots','wake_ballots','site_share_pct'])
for (year,dimension,cohort),values in groups.items():
 for field,scope in [('site_ballots','Campus site'),('other_wake_ballots','Other Wake sites'),('wake_ballots','Wake County')]:assert sum(r[field] or 0 for r in values)==expected[year,scope,cohort]
 if cohort=='All ages':
  for r in values:
   for field in ['site_ballots','other_wake_ballots','wake_ballots']:assert (r[field] or 0)==sum(lookup[year,dimension,r['area'],band][field] or 0 for band in AGE_BANDS)
assert len({r['area'] for r in rows if r['dimension']=='Precinct'})==230
assert len({r['area'] for r in rows if r['dimension']=='ZIP code'})==40
assert any(not r['area_present'] for r in rows)
print('Passed 5670 aggregate geography rows, all yearly scope/age partitions, exact share denominators, missing-area semantics and CSV/JSON/snapshot agreement.')
