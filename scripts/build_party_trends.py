#!/usr/bin/env python3
"""Recount daily party-registration ballots from the unchanged reviewed Wake CSVs."""
import copy,csv,hashlib,json
from collections import Counter
from datetime import date,datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/comparison'
PARTIES=['Democratic','Republican','Unaffiliated','Other registered parties']
AGE_BANDS=['18–24','25–34','35–44','45–64','65+','Unknown / outside range']
COMPONENTS=['voting-party-trend-2022','voting-party-trend-2024','voting-party-trend','voting-party-totals']
def age_band(age):
    return next((label for lo,hi,label in [(18,24,'18–24'),(25,34,'25–34'),(35,44,'35–44'),(45,64,'45–64'),(65,120,'65+')] if age is not None and lo<=age<=hi),'Unknown / outside range')
def party_label(code):
    return {'DEM':'Democratic','REP':'Republican','UNA':'Unaffiliated'}.get(code,'Other registered parties' if code else 'Not specified')

def add_party_trends(snapshot,data):
    audit=json.loads((DATA/'reference_audit.json').read_text(encoding='utf-8'))['checks']
    counts=Counter();codes=Counter();years=[2022,2024,2026];scopes=['Campus site','Wake County','Other Wake sites'];cohorts=['All ages',*AGE_BANDS,'18–22']
    for year in years:
        source=next(r['source'] for r in audit if r['year']==year)
        election={2022:'20221108',2024:'20241105',2026:'20261103'}[year]
        path=ROOT/'data/raw/early_voting'/f'wake_{election}.csv'
        with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source['wake_csv_sha256'],'Changed source snapshot'
        window=next(r for r in data['summary'] if r['year']==year and r['scope']=='Campus site')
        start=date.fromisoformat(window['start_date']);end=date.fromisoformat(window['end_date']);seen=set()
        with path.open(encoding='cp1252',errors='replace',newline='') as f:
            for r in csv.DictReader(f):
                if r['county_desc'].strip()!='WAKE' or r['ballot_req_type'].strip().upper() not in {'ONE-STOP','ONE STOP','EARLY VOTING'} or r['ballot_rtn_status'].strip().upper()!='ACCEPTED':continue
                when=datetime.strptime(r['ballot_rtn_dt'].strip(),'%m/%d/%Y').date()
                if not start<=when<=end:continue
                identifier=r['ncid'].strip();assert identifier and identifier not in seen;seen.add(identifier)
                day=(when-start).days+1;code=r['voter_party_code'].strip().upper();party=party_label(code);codes[year,code]+=1
                try:age=int(r['age'].strip())
                except ValueError:age=None
                selected=['All ages',age_band(age)]+(['18–22'] if age is not None and 18<=age<=22 else [])
                locations=['Wake County','Campus site' if r['site_name'].strip()==data['site_mapping'][str(year)] else 'Other Wake sites']
                for scope in locations:
                    for cohort in selected:counts[year,scope,cohort,day,party]+=1
    parties=PARTIES+(['Not specified'] if any(key[-1]=='Not specified' for key in counts) else [])
    rows=[];daily={(r['year'],r['scope'],r['cohort'],r['day']):r for r in data['daily']}
    for year in years:
        for scope in scopes:
            for cohort in cohorts:
                running={party:0 for party in parties}
                for day in range(1,data['matched_days']+1):
                    expected=daily.get((year,scope,cohort,day))
                    all_day=daily[year,scope,'All ages',day]
                    if expected:assert sum(counts[year,scope,cohort,day,p] for p in parties)==expected['votes']
                    for party in parties:
                        votes=counts[year,scope,cohort,day,party];running[party]+=votes
                        rows.append({'year':year,'scope':scope,'cohort':cohort,'day':day,'date':all_day['date'],'party_registration':party,'votes':votes,'cumulative':running[party]})
                    if expected:assert sum(running.values())==expected['cumulative']
                if cohort in AGE_BANDS:
                    expected_band=sum(r['votes'] for r in data['demographics'] if r['year']==year and r['scope']==scope and r['dimension']=='age_group' and r['value']==cohort)
                    assert sum(running.values())==expected_band
            for day in range(1,data['matched_days']+1):
                for party in parties:assert sum(counts[year,scope,band,day,party] for band in AGE_BANDS)==counts[year,scope,'All ages',day,party]
    for year in years:
        for scope in scopes:
            grouped=Counter()
            for r in data['demographics']:
                if r['year']==year and r['scope']==scope and r['dimension']=='party':grouped[party_label(r['value'].upper() if r['value']!='Unknown' else '')]+=r['votes']
            for party in parties:assert sum(counts[year,scope,'All ages',day,party] for day in range(1,data['matched_days']+1))==grouped[party]
    source=copy.deepcopy(snapshot['queries']['daily']['source'])
    source.update(label='NCSBE daily early ballots by voter party registration',executedAt=datetime.now(timezone.utc).isoformat())
    source['metricDefinitions']=[
        {'label':'Daily accepted ballots','definition':'Each matching original record contributes one ballot to its return date, party-registration group, selected scope and age cohort.','componentIds':['voting-party-trend','voting-party-totals']},
        {'label':'Cumulative ballots','definition':'For one year, scope, age cohort and party group, cumulative ballots equal the sum of daily ballots from day 1 through the displayed date. This is a running total, not a turnout rate.','formula':'cumulative(day) = cumulative(day - 1) + votes(day)','componentIds':['voting-party-trend','voting-party-totals']},
        {'label':'Party registration','definition':'DEM = Democratic; REP = Republican; UNA = Unaffiliated. All remaining nonblank registration codes form Other registered parties. Blank codes remain Not specified if observed. Registration does not reveal candidate choice.','componentIds':['voting-party-trend','voting-party-totals']},
        {'label':'Source party codes','definition':json.dumps({str(y):{code:n for (year,code),n in codes.items() if year==y} for y in years})},
        {'label':'Separate age bands','definition':'18–24, 25–34, 35–44, 45–64 and 65–120 do not overlap. Unknown or outside-range ages remain in the all-age total. The legacy 18–22 sensitivity rows are retained in the CSV but are not a separate age-menu band.','componentIds':COMPONENTS},
        {'label':'Shared scale ceiling','definition':'The guide is the highest final cumulative party count among 2022, 2024 and 2026 for the selected scope and age band. The same reviewed maximum sets all three vertical scales; it is not an extra ballot series.','componentIds':COMPONENTS}]
    for definition in source['metricDefinitions']:
        if 'componentIds' in definition:definition['componentIds']=COMPONENTS
    source['metricDefinitions'].append({'label':'Final counts, shares and changes','definition':'Final category counts use the last matched day. Share = category count / all selected ballots * 100; count change = 2026 - baseline; growth = change / baseline * 100; share change subtracts unrounded shares, in percentage points. Both 2022 and 2024 comparisons remain visible. Zero denominators display N/A.','componentIds':['voting-party-totals']})
    source['evidenceFlow']=[{'title':'Exact reviewed originals','detail':json.dumps([r['source'] for r in audit])},{'title':'Count and accumulate','detail':'scripts/build_party_trends.py verifies original CSV SHA-256 hashes, counts accepted early-voting records by return date and party registration, then computes running totals. Every day reconciles to matched_daily.csv; all-age party totals reconcile to matched_demographics.csv. Only aggregates are exported.'}]
    snapshot['queries']['party_daily']={'rows':rows,'source':source,'methods':[{'language':'python','code':'python scripts/build_party_trends.py\n# Per party: cumulative[d] = sum(votes[1:d+1]); count each matching source record once.\n# Inspect matched_party_daily.csv for all dates and exact running totals.'}]}
    with (DATA/'matched_party_daily.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (DATA/'party_trends.json').write_text(json.dumps({'as_of':data['as_of'],'matched_days':data['matched_days'],'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Validated {len(rows)} daily/party rows against every matched daily total and all-age party totals.')

if __name__=='__main__':
    path=ROOT/'report-source/snapshot.json';snapshot=json.loads(path.read_text(encoding='utf-8'));data=json.loads((DATA/'comparison.json').read_text(encoding='utf-8'))
    add_party_trends(snapshot,data);snapshot['buildStatus']='updating';snapshot['generatedAt']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
