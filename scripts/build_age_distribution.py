#!/usr/bin/env python3
"""Derive full single-year-of-age distributions from reviewed aggregate counts."""
import copy,csv,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
YEARS=(2022,2024,2026)
COMPONENTS=['voting-age-distribution-intro','voting-age-distribution-table',*[f'voting-age-distribution-{y}' for y in YEARS]]

def add_age_distribution(snapshot,data):
    originals=[r for r in snapshot['queries']['demographics']['rows'] if r['scope']=='Campus site' and r['dimension']=='age']
    totals={r['year']:r['all_ages'] for r in snapshot['queries']['summary']['rows'] if r['scope']=='Campus site'}
    counts={}
    for r in originals:
        age=int(r['value'])
        assert str(age)==str(r['value']) and 18<=age<=120, 'Review missing or outside-range ages before publishing'
        key=(r['year'],age)
        assert key not in counts and isinstance(r['votes'],int) and r['votes']>=0
        counts[key]=r['votes']
        assert math.isclose(r['share'],r['votes']/totals[r['year']]*100,abs_tol=1e-10)
    for year in YEARS:
        assert sum(r['votes'] for r in originals if r['year']==year)==totals[year], 'Full age breakdown must reconcile before absent ages become zero'
    low=min(age for year,age in counts);high=max(age for year,age in counts)
    count_ceiling=math.ceil(max(counts.values())/500)*500
    share_ceiling=math.ceil(max(v/totals[y]*100 for (y,a),v in counts.items())/5)*5
    rows=[]
    for year in YEARS:
        site='Western Boulevard Business Services' if year==2026 else 'Talley Student Union'
        for age in range(low,high+1):
            votes=counts.get((year,age),0)
            rows.append({'year':year,'site':site,'age':age,'votes':votes,'site_ballots':totals[year],
                         'Age share (%)':votes/totals[year]*100,'count_ceiling':count_ceiling,
                         'Share ceiling (%)':share_ceiling,'source_age_present':(year,age) in counts})
    source=copy.deepcopy(snapshot['queries']['demographics']['source'])
    source['label']='NCSBE individual ages at Talley and Western Boulevard; complete matched-period age distributions'
    source['filters']=[*source.get('filters',[]),'Exact campus-site mapping in each year; all recorded ages, without an age-cohort filter']
    source['metricDefinitions']=[
        {'label':'Single-year age counts and shares','formula':'Age share (%) = votes at exact age / all accepted ballots at the same site and year * 100',
         'definition':'One observation per recorded integer age. Every accepted matched-period site ballot is represented exactly once. The complete original age breakdown reconciles to the all-age summary in each year; only then are absent ages within the shared minimum/maximum range represented as zero. No fitted normal curve, age grouping or age-based exclusions. Lines connect the single-age observations; the exact counts remain in tooltips and the table. Source ages are used as recorded, without recalculating birth dates.',
         'componentIds':COMPONENTS},
        {'label':'Shared chart scales','formula':'count_ceiling = ceil(max age count across all three years / 500) * 500; Share ceiling (%) = ceil(max unrounded age share / 5) * 5',
         'definition':'Each chart uses the same age range and a common reviewed upper guide in the selected units, starting at zero. The guide is a display aid and is never added to ballot counts. Percentages use each year’s own total, so unequal election totals do not determine the comparison of age mix.',
         'componentIds':COMPONENTS}]
    source['evidenceFlow']=[*source.get('evidenceFlow',[]),{'title':'Reconciled individual ages','detail':'scripts/build_age_distribution.py checks unique exact-age aggregate counts, all-age reconciliation and unrounded percentages; creates a shared consecutive age range and aggregate CSV without altering original government CSVs or existing reviewed queries.'}]
    snapshot['queries']['age_distribution']={'rows':rows,'source':source,'methods':[{'language':'python','code':'python scripts/build_age_distribution.py\npython scripts/test_age_distribution.py'}]}
    out=ROOT/'data/processed/comparison/age_distribution.csv'
    with out.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(f'Reconciled {len(rows)} age/year rows, ages {low}–{high}, against all three site totals.')

if __name__=='__main__':
    path=ROOT/'report-source/snapshot.json';snapshot=json.loads(path.read_text(encoding='utf-8'))
    add_age_distribution(snapshot,snapshot['comparison']);snapshot['buildStatus']='updating'
    path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
