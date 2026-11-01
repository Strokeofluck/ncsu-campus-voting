"""Independently reconcile each displayed age, bin, denominator and exported row."""
import copy,csv,json,math
from pathlib import Path
from build_age_distribution import add_age_distribution
root=Path(__file__).resolve().parents[1]
snapshot=json.loads((root/'report-source/snapshot.json').read_text(encoding='utf-8'))
rows=snapshot['queries']['age_distribution']['rows']
source={(r['year'],int(r['value'])):r for r in snapshot['queries']['demographics']['rows'] if r['scope']=='Campus site' and r['dimension']=='age'}
summaries={r['year']:r for r in snapshot['queries']['summary']['rows'] if r['scope']=='Campus site'}
ages=range(min(age for year,age in source),max(age for year,age in source)+1)
assert len(rows)==len(ages)*3 and len({(r['year'],r['age']) for r in rows})==len(rows)
for r in rows:
    original=source.get((r['year'],r['age']))
    assert r['source_age_present']==(original is not None)
    assert r['votes']==(original['votes'] if original else 0)
    assert r['site_ballots']==summaries[r['year']]['all_ages']
    assert math.isclose(r['Age share (%)'],r['votes']/r['site_ballots']*100,abs_tol=1e-12)
    assert r['votes']<=r['count_ceiling'] and r['Age share (%)']<=r['Share ceiling (%)']
assert len({r['count_ceiling'] for r in rows})==len({r['Share ceiling (%)'] for r in rows})==1
for year in [2022,2024,2026]:
    selected=[r for r in rows if r['year']==year]
    assert [r['age'] for r in selected]==list(ages)
    assert sum(r['votes'] for r in selected)==summaries[year]['all_ages']
    assert math.isclose(sum(r['Age share (%)'] for r in selected),100,abs_tol=1e-10)
    assert sum(r['votes'] for r in selected if 18<=r['age']<=24)==summaries[year]['age_18_24']
with (root/'data/processed/comparison/age_distribution.csv').open(encoding='utf-8',newline='') as f:
    exported=list(csv.DictReader(f))
assert len(exported)==len(rows)
for a,b in zip(rows,exported):assert {k:str(v) for k,v in a.items()}==b
# An incomplete age breakdown must never be silently zero-filled.
broken=copy.deepcopy(snapshot)
broken['queries']['demographics']['rows'].remove(next(r for r in broken['queries']['demographics']['rows'] if r['scope']=='Campus site' and r['dimension']=='age' and r['votes']>0))
try:add_age_distribution(broken,broken['comparison'])
except AssertionError:pass
else:raise AssertionError('Incomplete age distribution accepted')
print(f'Passed all {len(rows)} age counts, percentages, zero bins, shared bounds, all-age and college-age totals, CSV agreement and incomplete-source rejection.')
