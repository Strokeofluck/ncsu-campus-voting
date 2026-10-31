#!/usr/bin/env python3
"""Check the exported registration series and all containing-scope denominators."""
import csv,json
from pathlib import Path
from collections import defaultdict
from build_party_trends import AGE_BANDS
root=Path(__file__).resolve().parents[1]
s=json.loads((root/'report-source/snapshot.json').read_text(encoding='utf-8'))
rows=s['queries']['sdr_daily']['rows']
assert rows==json.loads((root/'data/processed/comparison/sdr_trends.json').read_text(encoding='utf-8'))['rows']
with (root/'data/processed/comparison/matched_sdr_daily.csv').open(encoding='utf-8',newline='') as f:export=list(csv.DictReader(f))
assert len(rows)==len(export)==1152
for a,b in zip(rows,export):assert {k:str(v) for k,v in a.items()}==b
lookup={};series=defaultdict(list);ballots=defaultdict(int)
for r in s['queries']['party_daily']['rows']:ballots[r['year'],r['scope'],r['cohort'],r['day']]+=r['votes']
for r in rows:
    assert set(r)=={'year','scope','cohort','day','date','votes','cumulative','ballots','cumulative_ballots'}
    key=r['year'],r['scope'],r['cohort'],r['day'];assert key not in lookup;lookup[key]=r
    assert 0<=r['votes']<=r['ballots']==ballots[key]
    series[key[:3]].append(r)
for (year,scope,cohort),values in series.items():
    assert [r['day'] for r in values]==list(range(1,17));running=total=0
    for r in values:
        running+=r['votes'];total+=r['ballots'];assert running==r['cumulative'] and total==r['cumulative_ballots']
        if scope=='Wake County':
            for field in ['votes','cumulative','ballots','cumulative_ballots']:assert r[field]==sum(lookup[year,v,cohort,r['day']][field] for v in ['Campus site','Other Wake sites'])
        if cohort=='All ages':
            for field in ['votes','cumulative','ballots','cumulative_ballots']:assert r[field]==sum(lookup[year,scope,v,r['day']][field] for v in AGE_BANDS)
    if cohort=='All ages':assert running==next(r['same_day_registration'] for r in s['queries']['summary']['rows'] if r['year']==year and r['scope']==scope)
assert [lookup[y,'Campus site','18–24',16]['cumulative'] for y in [2022,2024,2026]]==[528,1859,720]
assert s['id']=='report:280801c5-2e0b-43cf-b10c-322b5c90a10e'
print('Passed 1152 registration rows, daily subsets, running sums, all age/scope partitions, existing totals and CSV/JSON/snapshot agreement.')
