#!/usr/bin/env python3
"""Compare all five age groups’ early-ballot counts and within-precinct age mix."""
import copy,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COHORTS=['18–24','25–34','35–44','45–64','65+']
COMPONENTS=['voting-age-region-intro','voting-age-region-young','voting-age-region-old','voting-age-region-focus','voting-age-region-ranks','voting-campus-age-intro',*[f'voting-campus-age-{i}' for i in range(5)]]
def add_precinct_age_changes(snapshot):
    geo=[r for r in snapshot['queries']['geography']['rows'] if r['dimension']=='Precinct']
    lookup={(r['area'],r['year'],r['cohort']):r for r in geo}
    assert len(lookup)==len(geo)
    shapes={r['area'] for r in snapshot['queries']['precinct_shapes']['rows']}
    demographics=snapshot['queries']['demographics']['rows']
    age_counts={(r['scope'],r['year'],r['value']):r['votes'] for r in demographics if r['dimension']=='age_group' and r['year'] in [2022,2026]}
    benchmarks=[]
    for cohort in COHORTS:
        a,b=[age_counts['Wake County',year,cohort] for year in [2022,2026]]
        c,d=[age_counts['Campus site',year,cohort] for year in [2022,2026]]
        county_growth=(b-a)/a*100 if a else None
        site_growth=(d-c)/c*100 if c else None
        benchmarks.append({'cohort':cohort,'county_ballots_2022':a,'county_ballots_2026':b,'county_growth_pct':county_growth,
            'site_ballots_2022':c,'site_ballots_2026':d,'site_growth_pct':site_growth,
            'site_growth_gap_pp':site_growth-county_growth if site_growth is not None and county_growth is not None else None})
    county_growth_by_age={r['cohort']:r['county_growth_pct'] for r in benchmarks}
    rows=[]
    for area in sorted({r['area'] for r in geo}):
        for cohort in COHORTS:
            old=lookup.get((area,2022,cohort));new=lookup.get((area,2026,cohort))
            a=old['wake_ballots'] if old and old['area_present'] else None
            b=new['wake_ballots'] if new and new['area_present'] else None
            totals=[lookup.get((area,y,'All ages')) for y in [2022,2026]]
            denominators=[r['wake_ballots'] if r and r['area_present'] else None for r in totals]
            before=a/denominators[0]*100 if a is not None and denominators[0] else None
            after=b/denominators[1]*100 if b is not None and denominators[1] else None
            available=a is not None and b is not None
            rows.append({'area':area,'cohort':cohort,'mapped':area in shapes,'ballots_2022':a,'ballots_2026':b,
                'all_age_ballots_2022':denominators[0],'all_age_ballots_2026':denominators[1],
                'ballot_change':b-a if available else None,'growth_pct':(b-a)/a*100 if available and a>0 else None,
                'age_share_2022_pct':before,'age_share_2026_pct':after,
                'share_change_pp':after-before if before is not None and after is not None else None,
                'new_from_zero':available and a==0 and b>0,'small_baseline':a is not None and a<20})
            growth=rows[-1]['growth_pct'];county_growth=county_growth_by_age[cohort]
            rows[-1].update(county_growth_pct=county_growth,growth_gap_pp=growth-county_growth if growth is not None and county_growth is not None else None)
    source=copy.deepcopy(snapshot['queries']['geography']['source'])
    source['label']='NCSBE residential precinct age changes, matched first 16 early-voting days in 2022 and 2026'
    source['files']=[f for f in source.get('files',[]) if '/2024_' not in str(f)]
    windows=[r for r in snapshot['queries']['summary']['rows'] if r['scope']=='Campus site' and r['year'] in [2022,2026]]
    source['period']='Matched first 16 early-voting days: '+'; '.join(f"{r['year']}: {r['start_date']} through {r['end_date']}" for r in windows)
    source['filters']=[*source.get('filters',[]),'Residential precinct; non-overlapping ages 18–24, 25–34, 35–44, 45–64 and 65+; accepted early ballots at ANY Wake location; 2022 and 2026 only']
    source['caveats']=[
        'Both elections are midterms. Matching the first 16 days does not equalize populations, boundaries, site availability or reporting lags.',
        'Ages 18–24 are an age proxy, not verified NC State students. No eligible-resident or registered-voter turnout denominator is supplied.',
        f"2022 finalized records versus preliminary 2026 records through {snapshot['comparison']['as_of']}.",
        'Current precinct outlines are not harmonized historical boundaries. Counts describe residents recorded under each precinct code, wherever they voted early in Wake.',
        'Ballot counts and age composition do not establish the causal effect of relocating a voting site.'
    ]
    source['metricDefinitions']=[
        {'label':'Growth versus Wake County','formula':'county_growth_pct = (sum(county age-group ballots in 2026) / sum(county age-group ballots in 2022) - 1) * 100; growth_gap_pp = precinct growth_pct - county_growth_pct',
         'definition':'A separate count-weighted county benchmark is calculated for each age group from the full Wake County totals, including unmapped precincts. It is not an average of precinct percentages. Both periods use the same first 16 early-voting days. Negative means slower growth than Wake even when counts rose; positive means faster growth. Undefined precinct growth stays missing, including zero baselines. Units are percentage points. The campus voting-site comparison uses accepted ballots cast at Talley in 2022 and Western Boulevard in 2026, regardless of home precinct; these are separate populations from the residential polygons.','componentIds':COMPONENTS},
        {'label':'Extra ballots','formula':'ballot_change = ballots_2026 - ballots_2022','definition':'Age-group ballots from residents recorded in a precinct, wherever they voted early in Wake. Not restricted to Talley or Western Boulevard. Both years must be observed; missing is not zero.','componentIds':COMPONENTS},
        {'label':'Percentage growth','formula':'growth_pct = ballot_change / ballots_2022 * 100','definition':'Undefined for a missing or zero baseline. Positive 2026 count from a known zero baseline is separately flagged. Dashed map borders identify baselines below 20 ballots; the rank filter defaults to at least 20 for this measure and can be changed. Exact counts remain available.','componentIds':COMPONENTS},
        {'label':'Change in age mix','formula':'age_share_year = age-group ballots / ALL-age ballots from the SAME precinct and year * 100; share_change_pp = unrounded 2026 share - unrounded 2022 share','definition':'Percentage points compare composition among observed early ballots, not demographic changes in all residents. Every denominator includes all accepted early ballots from that precinct at any Wake location. A zero all-age denominator has no defined share.','componentIds':COMPONENTS},
        {'label':'County maps and rankings','definition':'Both maps use the same fixed color classes and geographic viewport in the selected units. Gold outlines identify 01-23 (current Talley area) and 01-31 (current Western Boulevard area). Rankings include only mapped precinct codes with defined comparisons; largest-change mode sorts by absolute magnitude. Unmapped and missing comparisons remain in the CSV/source rows. Current precinct polygons are not harmonized historical boundaries; changes may reflect boundary, population and voting-pattern changes. Age is not verified student status. These are first-16-day counts, not resident turnout rates or estimates of the move’s effect.','componentIds':COMPONENTS}]
    source['evidenceFlow']=[*source.get('evidenceFlow',[]),{'title':'Five-age precinct comparison','detail':'scripts/build_precinct_age_changes.py joins the same recorded precinct code and each of five non-overlapping age groups in 2022 and 2026, retaining exact all-age denominators and missing/zero semantics. It does not alter original government files or earlier reviewed aggregate queries. The additional small-multiple maps start focused on 01-23 and 01-31 and share the same classes and linked viewport across all five groups.'}]
    source['evidenceFlow'].append({'title':'The two NC State-area precincts','detail':json.dumps({'source':snapshot['queries']['voting_site_points']['source']['url'],'points':[{'name':r['name'],'current_precinct':r['current_precinct_area']} for r in snapshot['queries']['voting_site_points']['rows']]})})
    snapshot['queries']['precinct_age_changes']={'rows':rows,'source':source,'methods':[{'language':'python','code':'python scripts/build_precinct_age_changes.py\npython scripts/test_precinct_age_changes.py'}]}
    benchmark_source=copy.deepcopy(snapshot['queries']['demographics']['source'])
    benchmark_source.update(label='Age-specific Wake County and campus-site growth benchmarks, matched 2022 and 2026',period=source['period'])
    benchmark_source['metricDefinitions']=[source['metricDefinitions'][0]]
    benchmark_source['caveats']=source['caveats']
    snapshot['queries']['age_growth_benchmarks']={'rows':benchmarks,'source':benchmark_source,'methods':[{'language':'python','code':'python scripts/build_precinct_age_changes.py\n# Full Wake totals by age, never the average precinct percentage; site totals use the Talley-to-Western location mapping.'}]}
    with (ROOT/'data/processed/comparison/age_growth_benchmarks.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(benchmarks[0]));w.writeheader();w.writerows(benchmarks)
    p=ROOT/'data/processed/comparison/precinct_age_changes.csv'
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'Prepared {len(rows)} age/precinct comparisons with exact counts, growth and same-precinct age shares.')
if __name__=='__main__':
    p=ROOT/'report-source/snapshot.json';s=json.loads(p.read_text(encoding='utf-8'));add_precinct_age_changes(s);s['buildStatus']='updating';p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
