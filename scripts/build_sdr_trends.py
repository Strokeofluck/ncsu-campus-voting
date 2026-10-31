#!/usr/bin/env python3
"""Recount aggregate daily same-day-registration ballots from reviewed originals."""
import copy,csv,hashlib,json
from collections import Counter
from datetime import date,datetime,timezone
from pathlib import Path
from build_party_trends import AGE_BANDS,age_band

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/comparison'
COMPONENTS=['voting-sdr-trend','voting-sdr-totals','voting-sdr-intro']

def add_sdr_trends(snapshot,data):
    audit=json.loads((DATA/'reference_audit.json').read_text(encoding='utf-8'))['checks']
    counts=Counter();years=[2022,2024,2026];scopes=['Campus site','Wake County','Other Wake sites'];cohorts=['All ages',*AGE_BANDS,'18–22']
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
                if r['sdr'].strip().upper() not in {'Y','YES'}:continue
                try:age=int(r['age'].strip())
                except ValueError:age=None
                selected=['All ages',age_band(age)]+(['18–22'] if age is not None and 18<=age<=22 else [])
                locations=['Wake County','Campus site' if r['site_name'].strip()==data['site_mapping'][str(year)] else 'Other Wake sites']
                for scope in locations:
                    for cohort in selected:counts[year,scope,cohort,(when-start).days+1]+=1
    denominators=Counter()
    for r in snapshot['queries']['party_daily']['rows']:denominators[r['year'],r['scope'],r['cohort'],r['day']]+=r['votes']
    daily={(r['year'],r['scope'],r['day']):r['date'] for r in data['daily'] if r['cohort']=='All ages'}
    rows=[]
    for year in years:
        for scope in scopes:
            for cohort in cohorts:
                running=all_running=0
                for day in range(1,data['matched_days']+1):
                    key=year,scope,cohort,day;votes=counts[key];ballots=denominators[key]
                    assert 0<=votes<=ballots
                    assert counts[year,'Wake County',cohort,day]==counts[year,'Campus site',cohort,day]+counts[year,'Other Wake sites',cohort,day]
                    if cohort=='All ages':assert votes==sum(counts[year,scope,band,day] for band in AGE_BANDS)
                    running+=votes;all_running+=ballots
                    rows.append({'year':year,'scope':scope,'cohort':cohort,'day':day,'date':daily[year,scope,day],'votes':votes,'cumulative':running,'ballots':ballots,'cumulative_ballots':all_running})
                if cohort=='All ages':assert running==next(r['same_day_registration'] for r in data['summary'] if r['year']==year and r['scope']==scope)
    source=copy.deepcopy(snapshot['queries']['daily']['source'])
    source.update(label='NCSBE same-day-registration early ballots by day and age',executedAt=datetime.now(timezone.utc).isoformat())
    source['metricDefinitions']=[
        {'label':'Same-day-registration ballots','definition':'Accepted early-voting records with sdr equal to Y or YES, by original return date, matched first 16 days, selected location and age band. These ballots are already included in total ballots; this is not a count of every new registration.','componentIds':COMPONENTS},
        {'label':'Running registration count','formula':'cumulative(day) = sum(votes from day 1 through day)','definition':'Each matching original ballot contributes one. Ages 18–24 are a proxy, not verified student status.','componentIds':COMPONENTS},
        {'label':'Registration share and comparisons','formula':'share = cumulative / cumulative_ballots × 100; count change = 2026 − baseline; growth = count change / baseline × 100; share change = unrounded 2026 share − baseline share','definition':'Shares use all accepted ballots in the SAME location, age band and period. A zero denominator has no defined share or growth. Share differences are percentage points.','componentIds':COMPONENTS}]
    source['evidenceFlow']=[{'title':'Reviewed originals','detail':json.dumps([r['source'] for r in audit])},{'title':'Recount and reconcile','detail':'scripts/build_sdr_trends.py verifies every original CSV hash, independently counts sdr Y/YES by day and age, checks each subset against party-derived ballot denominators, all-age totals against the existing summary, age partitions and scope partitions. Only aggregates are exported.'}]
    snapshot['queries']['sdr_daily']={'rows':rows,'source':source,'methods':[{'language':'python','code':'python scripts/build_sdr_trends.py\n# Inspect matched_sdr_daily.csv for daily counts, running sums and same-cohort ballot denominators.'}]}
    with (DATA/'matched_sdr_daily.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (DATA/'sdr_trends.json').write_text(json.dumps({'as_of':data['as_of'],'matched_days':data['matched_days'],'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Validated {len(rows)} same-day-registration rows, subset denominators, original summary totals, age bands and scopes.')

if __name__=='__main__':
    path=ROOT/'report-source/snapshot.json';snapshot=json.loads(path.read_text(encoding='utf-8'));data=json.loads((DATA/'comparison.json').read_text(encoding='utf-8'))
    add_sdr_trends(snapshot,data);snapshot['buildStatus']='updating';path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
