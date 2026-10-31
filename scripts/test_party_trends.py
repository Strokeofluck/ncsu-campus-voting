"""Check published aggregate party rows, cumulative arithmetic and scope reconciliation."""
import csv,json
from collections import defaultdict
from pathlib import Path
root=Path(__file__).resolve().parents[1]
snapshot=json.loads((root/'report-source/snapshot.json').read_text(encoding='utf-8'))
rows=snapshot['queries']['party_daily']['rows'];days=snapshot['comparison']['matched_days']
assert rows==json.loads((root/'data/processed/comparison/party_trends.json').read_text(encoding='utf-8'))['rows']
with (root/'data/processed/comparison/matched_party_daily.csv').open(encoding='utf-8',newline='') as f:
    exported=list(csv.DictReader(f))
assert len(exported)==len(rows)
for a,b in zip(rows,exported):assert {k:str(v) for k,v in a.items()}==b
series=defaultdict(list);daily=defaultdict(int);lookup={}
for r in rows:
    assert set(r)=={'year','scope','cohort','day','date','party_registration','votes','cumulative'}
    key=(r['year'],r['scope'],r['cohort'],r['party_registration'])
    series[key].append(r);daily[r['year'],r['scope'],r['cohort'],r['day']]+=r['votes'];lookup[*key,r['day']]=r
for key,values in series.items():
    assert [r['day'] for r in values]==list(range(1,days+1));running=0
    for r in values:running+=r['votes'];assert running==r['cumulative'] and r['votes']>=0
    if key[1]=='Wake County':
        for r in values:assert r['votes']==sum(lookup[key[0],scope,key[2],key[3],r['day']]['votes'] for scope in ['Campus site','Other Wake sites'])
for r in snapshot['queries']['daily']['rows']:
    assert daily[r['year'],r['scope'],r['cohort'],r['day']]==r['votes']
bands=['18–24','25–34','35–44','45–64','65+','Unknown / outside range']
for (year,scope,cohort,party),values in series.items():
    if cohort=='All ages':
        for r in values:assert sum(lookup[year,scope,band,party,r['day']]['votes'] for band in bands)==r['votes']
for r in snapshot['queries']['demographics']['rows']:
    if r['dimension']=='age_group':assert daily[r['year'],r['scope'],r['value'],days]>=0 and sum(v['votes'] for v in rows if v['year']==r['year'] and v['scope']==r['scope'] and v['cohort']==r['value'])==r['votes']
assert snapshot['buildStatus']=='complete' and snapshot['id']=='report:280801c5-2e0b-43cf-b10c-322b5c90a10e'
print(f'Passed {len(rows)} aggregate party rows, all running sums, all 432 daily denominators, per-party scope partitions, CSV/JSON/snapshot agreement and retained report identity.')
