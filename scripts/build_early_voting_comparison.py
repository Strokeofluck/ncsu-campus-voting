#!/usr/bin/env python3
"""Rebuild aggregate-only, matched-day 2022/2024/2026 early-voting comparisons.

Run after scripts/download_early_voting_sources.py, or supply --raw-dir.
No names, addresses, registration numbers, or voter identifiers are exported.
"""
from __future__ import annotations
import argparse,csv,json,hashlib
from collections import Counter,defaultdict
from datetime import date,datetime,timedelta,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
YEARS=[2022,2024,2026]
START={2022:date(2022,10,20),2024:date(2024,10,17),2026:date(2026,10,15)}
ELECTION={2022:'20221108',2024:'20241105',2026:'20261103'}
SITE={2022:'TA - NCSU TALLEY STUDENT CENTER',2024:'TA - NCSU TALLEY STUDENT CENTER',2026:'NCSU WESTERN BLVD BUSINESS SERVICES'}
AGE_GROUPS=['18–24','25–34','35–44','45–64','65+','Unknown / outside range']

def age_group(age):
    for lo,hi,label in [(18,24,AGE_GROUPS[0]),(25,34,AGE_GROUPS[1]),(35,44,AGE_GROUPS[2]),(45,64,AGE_GROUPS[3]),(65,120,AGE_GROUPS[4])]:
        if age is not None and lo<=age<=hi:return label
    return AGE_GROUPS[-1]

def pct(n,d):return 100*n/d if d else None
def write_csv(path,rows):
    if not rows:return
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def campus_age_changes(demo_rows):
    """Match the report table: 2026 minus each Talley baseline, before rounding."""
    ages={(r['year'],r['value']):r for r in demo_rows if r['scope']=='Campus site' and r['dimension']=='age_group'}
    changes=[]
    for baseline in (2024,2022):
        rows=[]
        for (year,age),current in ages.items():
            previous=ages.get((baseline,age))
            if year!=2026 or previous is None:continue
            delta=current['votes']-previous['votes']
            rows.append({'age':age,'baseline_year':baseline,'comparison_year':2026,'baseline_ballots':previous['votes'],'ballots_2026':current['votes'],'ballot_change':delta,'ballot_change_pct':pct(delta,previous['votes']),'baseline_share_pct':previous['share'],'share_2026_pct':current['share'],'share_change_pp':current['share']-previous['share']})
        changes.extend(sorted(rows,key=lambda r:r['share_change_pp'],reverse=True))
    return changes

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir',type=Path,default=ROOT/'data/raw/early_voting')
    p.add_argument('--output-dir',type=Path,default=ROOT/'data/processed/comparison')
    p.add_argument('--cutoff-date',required=True,type=date.fromisoformat,help='Last complete 2026 voting date, YYYY-MM-DD')
    args=p.parse_args(); n=(args.cutoff_date-START[2026]).days+1
    if not 1<=n<=17:raise ValueError('Cutoff must fall within the 17-day 2026 early-voting period')
    output=args.output_dir;output.mkdir(parents=True,exist_ok=True)
    daily=Counter(); demos=Counter(); sdr=Counter();sites=Counter();qa={};full={};source_meta=json.loads((args.raw_dir/'source_manifest.json').read_text())
    for year in YEARS:
        seen=set();total=0;campus=0;types=Counter();statuses=Counter();days=Counter();bad_age=0;full_youth=Counter()
        path=args.raw_dir/f'wake_{ELECTION[year]}.csv'
        with path.open(encoding='latin-1',newline='') as f:
            reader=csv.DictReader(f)
            required={'county_desc','ncid','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age','sdr','voter_party_code','race','ethnicity','gender','precinct_desc'}
            if not required.issubset(reader.fieldnames):raise ValueError(f'Missing columns: {required-set(reader.fieldnames)}')
            for r in reader:
                if r['county_desc'].strip().upper()!='WAKE':continue
                typ=r['ballot_req_type'].strip().upper();types[typ]+=1
                if typ not in {'ONE-STOP','ONE STOP','EARLY VOTING'}:continue
                status=r['ballot_rtn_status'].strip().upper();statuses[status]+=1
                if status!='ACCEPTED':continue
                identifier=r['ncid'].strip()
                if not identifier or identifier in seen:raise ValueError(f'Missing or duplicate accepted early voter identifier in {year}')
                seen.add(identifier)
                dt=datetime.strptime(r['ballot_rtn_dt'].strip(),'%m/%d/%Y').date();day=(dt-START[year]).days+1
                if not 1<=day<=17:raise ValueError(f'Out-of-window early-voting date in {year}')
                days[dt.isoformat()]+=1
                name=r['site_name'].strip();is_campus=name==SITE[year];total+=1;campus+=is_campus
                try:age=int(r['age'].strip())
                except ValueError:age=None
                ag=age_group(age);bad_age+=ag==AGE_GROUPS[-1]
                if is_campus and age is not None:
                    if 18<=age<=24:full_youth['18_24']+=1
                    if 18<=age<=22:full_youth['18_22']+=1
                if day>n:continue
                cohorts=['All ages']+(['18–24'] if age is not None and 18<=age<=24 else [])+(['18–22'] if age is not None and 18<=age<=22 else [])
                scopes=['Wake County', 'Campus site' if is_campus else 'Other Wake sites']
                for scope in scopes:
                    for cohort in cohorts:daily[(year,day,scope,cohort)]+=1
                    for dim,value in [('age_group',ag),('age',str(age) if age is not None else 'Unknown'),('party',r['voter_party_code'].strip()),('race',r['race'].strip()),('ethnicity',r['ethnicity'].strip()),('gender',r['gender'].strip())]:demos[(year,scope,dim,value or 'Unknown')]+=1
                    if r['sdr'].strip().upper() in {'Y','YES'}:sdr[(year,scope)]+=1
                for cohort in cohorts:sites[(year,name,cohort)]+=1
        if year==2022 and (campus!=10390 or total!=219169):raise ValueError('2022 does not match locked project baseline')
        if SITE[year] not in [k[1] for k in sites if k[0]==year]:raise ValueError('Campus site missing; review mapping')
        qa[str(year)]={'accepted_early_unique_ncid':len(seen),'accepted_early_rows':total,'duplicate_accepted_ncid':0,'accepted_early_by_date':dict(sorted(days.items())),'early_statuses_before_filter':dict(statuses),'unknown_or_outside_range_age':bad_age}
        full[str(year)]={'wake_accepted_early':total,'campus_accepted_early':campus,'campus_age_18_24':full_youth['18_24'],'campus_age_18_22':full_youth['18_22']}
    latest=max(qa['2026']['accepted_early_by_date'])
    if args.cutoff_date.isoformat()>latest:raise ValueError('Requested cutoff exceeds latest observed 2026 voting date')
    def count(year,scope,cohort):return sum(daily[(year,d,scope,cohort)] for d in range(1,n+1))
    summary=[]
    for year in YEARS:
        for scope in ['Campus site','Wake County','Other Wake sites']:
            total=count(year,scope,'All ages')
            summary.append({'year':year,'scope':scope,'start_date':START[year].isoformat(),'end_date':(START[year]+timedelta(days=n-1)).isoformat(),'matched_days':n,'all_ages':total,'age_18_24':count(year,scope,'18–24'),'age_18_22':count(year,scope,'18–22'),'age_18_24_share':pct(count(year,scope,'18–24'),total),'same_day_registration':sdr[(year,scope)]})
    daily_rows=[]
    for year in YEARS:
        for scope in ['Campus site','Wake County','Other Wake sites']:
            for cohort in ['All ages','18–24','18–22']:
                cumulative=0
                for day in range(1,n+1):
                    votes=daily[(year,day,scope,cohort)];cumulative+=votes
                    daily_rows.append({'year':year,'day':day,'date':(START[year]+timedelta(days=day-1)).isoformat(),'scope':scope,'cohort':cohort,'votes':votes,'cumulative':cumulative})
    demo_rows=[{'year':y,'scope':sc,'dimension':dim,'value':v,'votes':c,'share':pct(c,count(y,sc,'All ages'))} for (y,sc,dim,v),c in sorted(demos.items())]
    site_rows=[{'year':y,'site_name':site,'cohort':cohort,'votes':c} for (y,site,cohort),c in sorted(sites.items())]
    def row(y,scope):return next(x for x in summary if x['year']==y and x['scope']==scope)
    c22=row(2022,'Campus site');c26=row(2026,'Campus site');w22=row(2022,'Wake County');w26=row(2026,'Wake County')
    metrics={'campus_total_change_pct':pct(c26['all_ages']-c22['all_ages'],c22['all_ages']),'campus_youth_change_pct':pct(c26['age_18_24']-c22['age_18_24'],c22['age_18_24']),'wake_youth_change_pct':pct(w26['age_18_24']-w22['age_18_24'],w22['age_18_24']),'campus_youth_share_change_pp':c26['age_18_24_share']-c22['age_18_24_share'],'campus_share_wake_youth_2022':pct(c22['age_18_24'],w22['age_18_24']),'campus_share_wake_youth_2026':pct(c26['age_18_24'],w26['age_18_24'])}
    c24=row(2024,'Campus site');w24=row(2024,'Wake County')
    metrics['versus_2024']={'campus_youth_change_pct':pct(c26['age_18_24']-c24['age_18_24'],c24['age_18_24']),'campus_total_change_pct':pct(c26['all_ages']-c24['all_ages'],c24['all_ages']),'wake_youth_change_pct':pct(w26['age_18_24']-w24['age_18_24'],w24['age_18_24']),'campus_youth_share_change_pp':c26['age_18_24_share']-c24['age_18_24_share'],'campus_share_wake_youth_2024':pct(c24['age_18_24'],w24['age_18_24'])}
    result={'as_of':args.cutoff_date.isoformat(),'retrieved_at':source_meta[-1]['downloaded_at'],'source_last_modified':source_meta[-1]['last_modified'],'matched_days':n,'site_mapping':SITE,'sources':source_meta,'summary':summary,'metrics':metrics,'full_file_context':full,'qa':qa,'daily':daily_rows,'demographics':demo_rows,'sites':site_rows}
    (output/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for file,rows in [('matched_summary.csv',summary),('matched_daily.csv',daily_rows),('matched_demographics.csv',demo_rows),('matched_sites.csv',site_rows)]:write_csv(output/file,rows)
    campus_rows=[{'year':r['year'],'site_name':SITE[r['year']],**{k:v for k,v in r.items() if k not in {'year','scope'}}} for r in summary if r['scope']=='Campus site']
    write_csv(output/'campus_site_matched_counts.csv',campus_rows)
    write_csv(output/'age_group_changes.csv',campus_age_changes(demo_rows))
    print(json.dumps({'as_of':result['as_of'],'summary':summary,'metrics':metrics},ensure_ascii=True,indent=2))

if __name__=='__main__':main()
