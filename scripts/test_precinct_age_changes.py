"""Independently check age counts, exact precinct denominators and missing cases."""
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
rows=s['queries']['precinct_age_changes']['rows']
lookup={(r['area'],r['year'],r['cohort']):r for r in s['queries']['geography']['rows'] if r['dimension']=='Precinct'}
areas={r['area'] for r in s['queries']['precinct_shapes']['rows']}
assert len({(r['area'],r['cohort']) for r in rows})==len(rows)
for r in rows:
    assert r['mapped']==(r['area'] in areas)
    vals=[];shares=[]
    for y in [2022,2026]:
        a=lookup.get((r['area'],y,r['cohort']));all_row=lookup.get((r['area'],y,'All ages'))
        v=a['wake_ballots'] if a and a['area_present'] else None
        total=all_row['wake_ballots'] if all_row and all_row['area_present'] else None
        assert r[f'ballots_{y}']==v and r[f'all_age_ballots_{y}']==total
        share=v/total*100 if v is not None and total else None
        assert r[f'age_share_{y}_pct']==share
        vals.append(v);shares.append(share)
    a,b=vals;before,after=shares
    assert r['ballot_change']==(b-a if a is not None and b is not None else None)
    assert r['growth_pct']==((b-a)/a*100 if a is not None and a>0 and b is not None else None)
    assert r['share_change_pp']==(after-before if before is not None and after is not None else None)
    assert r['new_from_zero']==(a==0 and b is not None and b>0)
assert set(r['cohort'] for r in rows)=={'18–24','25–34','35–44','45–64','65+'}
for cohort in ['18–24','25–34','35–44','45–64','65+']:
    for y in [2022,2026]:
        expected=sum(r['votes'] for r in s['queries']['demographics']['rows'] if r['scope']=='Wake County' and r['year']==y and r['dimension']=='age_group' and r['value']==cohort)
        assert sum(r[f'ballots_{y}'] or 0 for r in rows if r['cohort']==cohort)==expected
with (ROOT/'data/processed/comparison/precinct_age_changes.csv').open(encoding='utf-8',newline='') as f:
    csv_rows=list(csv.DictReader(f))
assert len(csv_rows)==len(rows)
for a,b in zip(rows,csv_rows):assert {k:'' if v is None else str(v) for k,v in a.items()}==b
focus={(r['area'],r['cohort']):r for r in rows}
assert (focus['PRECINCT 01-23','18–24']['ballots_2022'],focus['PRECINCT 01-23','18–24']['ballots_2026'])==(599,1066)
assert (focus['PRECINCT 01-31','65+']['ballots_2022'],focus['PRECINCT 01-31','65+']['ballots_2026'])==(76,114)
assert math.isclose(focus['PRECINCT 01-31','18–24']['share_change_pp'],(320/1083-145/599)*100,abs_tol=1e-10)
print(f'Passed {len(rows)} exact age/precinct comparisons, both county reconciliations, same-precinct denominators, zero/missing cases and CSV agreement.')
