#!/usr/bin/env python3
"""Compare aggregate residential precinct/ZIP origins and location use."""
import copy,csv,hashlib,json
from collections import Counter
from datetime import date,datetime,timezone
from pathlib import Path
from build_party_trends import AGE_BANDS,age_band

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed/comparison'
def add_geography(snapshot,data):
    audit=json.loads((DATA/'reference_audit.json').read_text(encoding='utf-8'))['checks']
    counts=Counter();present=set();areas={'Precinct':set(),'ZIP code':set()};years=[2022,2024,2026];cohorts=['All ages',*AGE_BANDS]
    for year in years:
        source=next(r['source'] for r in audit if r['year']==year);election={2022:'20221108',2024:'20241105',2026:'20261103'}[year]
        path=ROOT/'data/raw/early_voting'/f'wake_{election}.csv'
        with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source['wake_csv_sha256'],'Changed source snapshot'
        window=next(r for r in data['summary'] if r['year']==year and r['scope']=='Campus site');start=date.fromisoformat(window['start_date']);end=date.fromisoformat(window['end_date']);seen=set()
        with path.open(encoding='cp1252',errors='replace',newline='') as f:
            for r in csv.DictReader(f):
                if r['county_desc'].strip()!='WAKE' or r['ballot_req_type'].strip().upper() not in {'ONE-STOP','ONE STOP','EARLY VOTING'} or r['ballot_rtn_status'].strip().upper()!='ACCEPTED':continue
                when=datetime.strptime(r['ballot_rtn_dt'].strip(),'%m/%d/%Y').date()
                if not start<=when<=end:continue
                identifier=r['ncid'].strip();assert identifier and identifier not in seen;seen.add(identifier)
                try:age=int(r['age'].strip())
                except ValueError:age=None
                selected=['All ages',age_band(age)];at_site=r['site_name'].strip()==data['site_mapping'][str(year)]
                for dimension,field in [('Precinct','precinct_desc'),('ZIP code','voter_zip')]:
                    area=r[field].strip() or 'Unknown / blank';areas[dimension].add(area);present.add((year,dimension,area))
                    for cohort in selected:
                        counts[year,dimension,area,cohort,'wake']+=1
                        counts[year,dimension,area,cohort,'site' if at_site else 'other']+=1
    rows=[];final=Counter()
    for r in snapshot['queries']['party_daily']['rows']:
        if r['day']==data['matched_days']:final[r['year'],r['scope'],r['cohort']]+=r['cumulative']
    for dimension in areas:
        for area in sorted(areas[dimension]):
            for year in years:
                available=(year,dimension,area) in present
                for cohort in cohorts:
                    key=year,dimension,area,cohort;site=counts[*key,'site'];other=counts[*key,'other'];wake=counts[*key,'wake'];assert site+other==wake
                    rows.append({'year':year,'dimension':dimension,'area':area,'cohort':cohort,'area_present':available,'site_ballots':site if available else None,'other_wake_ballots':other if available else None,'wake_ballots':wake if available else None,'site_share_pct':site/wake*100 if available and wake else None})
        for year in years:
            for cohort in cohorts:
                selected=[r for r in rows if r['dimension']==dimension and r['year']==year and r['cohort']==cohort]
                for field,scope in [('site_ballots','Campus site'),('other_wake_ballots','Other Wake sites'),('wake_ballots','Wake County')]:assert sum(r[field] or 0 for r in selected)==final[year,scope,cohort]
            for area in areas[dimension]:
                for field in ['site','other','wake']:assert counts[year,dimension,area,'All ages',field]==sum(counts[year,dimension,area,cohort,field] for cohort in AGE_BANDS)
    source=copy.deepcopy(snapshot['queries']['summary']['source']);source.update(label='NCSBE residential precinct/ZIP and early-voting location aggregates',executedAt=datetime.now(timezone.utc).isoformat())
    source['metricDefinitions']=[
        {'label':'Residential area','definition':'Precinct uses precinct_desc; ZIP code uses voter_zip, not a mailing-address field. Original trimmed field text is retained; blank is Unknown / blank. These are recorded residence groups, not the voting site precinct or verified NC State student residence.','componentIds':['voting-geography-intro','voting-geography-chart','voting-geography-table']},
        {'label':'Same-area location use','formula':'site_share_pct = site_ballots / wake_ballots * 100; wake_ballots = site_ballots + other_wake_ballots','definition':'For one residential area, year and age band, denominator is its accepted early ballots at ANY Wake location in the matched window. Site is Talley in 2022/2024 and Western Boulevard in 2026. This is site choice among observed early ballots, not resident turnout. Share differences subtract unrounded shares.'},
        {'label':'Absent versus zero','definition':'If an area label has no accepted early ballots of any age in a year, area_present is false and all counts are null. Zero is used only for a cohort within an otherwise observed area. Null shares occur when cohort ballots are zero. Absence does not establish when a precinct was created.'},
        {'label':'Comparability','definition':'Precinct boundaries/labels, populations, ZIP composition and election cycles may change. These independent yearly cohorts do not prove the same individuals switched locations. 2024 is presidential; 2022/2026 are midterms. Mail and Election Day ballots and registered-population denominators are absent.'},
        {'label':'Chart selection','definition':'Rank residential areas by their combined named-site ballots across all three selected years, and show up to ten matching the search. The full table is searchable and paginated. Count and share chart modes use the same areas.'}]
    source['metricDefinitions'].append({'label':'Full age breakdown for a selected precinct','definition':'All disjoint age bands are shown together, independent of the map age filter. Count stacks split each age band into named-site and other-Wake ballots. Percentage stacks divide each part by that same age band’s Wake total, not the all-age total. The table retains 2022, 2024 and 2026; its All ages footer equals the sum of the age bands before rounding. Unavailable areas or zero denominators retain N/A.','componentIds':['voting-precinct-age-chart','voting-precinct-age-table']})
    source['metricDefinitions'].append({'label': 'Simultaneous precinct age cards and companion area', 'definition': 'All disjoint age bands and a separately labeled All ages combined card remain visible beside the map. Each card retains 2022, 2024 and 2026 site, other-Wake and total counts; its heading selects the age used for map shading without hiding the other cards. All source rows for the selected precinct remain inspectable alongside the shaded-map cohort. A separate table below retains current Western Boulevard precinct 01-31 when another precinct is selected; when 01-31 is selected, it shows current Talley precinct 01-23 instead. No ballot aggregates or age denominators change.', 'componentIds': ['voting-precinct-map', 'voting-site-precinct-companion']})
    source['evidenceFlow']=[{'title':'Reviewed originals','detail':json.dumps([r['source'] for r in audit])},{'title':'Recount and reconcile','detail':'scripts/build_geography.py verifies source hashes and unique accepted records locally, groups only precinct or residential ZIP with age and year, checks site + other = Wake, disjoint age bands, and every year/dimension/cohort against reviewed party-derived denominators. No names, addresses or identifiers are exported.'}]
    snapshot['queries']['geography']={'rows':rows,'source':source,'methods':[{'language':'python','code':'python scripts/build_geography.py\n# Each geography separately partitions the complete reviewed Wake cohort. Do not add precinct totals to ZIP totals.'}]}
    with (DATA/'matched_geography.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (DATA/'geography.json').write_text(json.dumps({'as_of':data['as_of'],'matched_days':data['matched_days'],'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Validated {len(rows)} geography aggregates: '+', '.join(f'{k}: {len(v)} areas' for k,v in areas.items())+'. All age, year, location and county totals reconcile.')

if __name__=='__main__':
    path=ROOT/'report-source/snapshot.json';snapshot=json.loads(path.read_text(encoding='utf-8'));data=json.loads((DATA/'comparison.json').read_text(encoding='utf-8'))
    add_geography(snapshot,data);snapshot['buildStatus']='updating';path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
