from pathlib import Path
import csv,json,hashlib,zipfile
from collections import Counter
from datetime import datetime
root=Path(__file__).resolve().parents[1]
raw=root/'data/raw/early_voting'
data=json.loads((root/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
proof=[]
for expected in [r for r in data['summary'] if r['scope']=='Campus site']:
    year=expected['year'];date={2022:'20221108',2024:'20241105',2026:'20261103'}[year]
    site=data['site_mapping'][str(year)];start=expected['start_date'];end=expected['end_date']
    daily=Counter();ages=Counter();statuses=Counter();sdr=0;daily_youth=Counter();daily_narrow=Counter();daily_sdr=Counter();demographics=Counter()
    with (raw/f'wake_{date}.csv').open(encoding='latin-1',newline='') as f:
        for row in csv.DictReader(f):
            if row['county_desc'].strip()!='WAKE' or row['site_name'].strip()!=site:continue
            if row['ballot_req_type'].strip().upper() not in ['ONE-STOP','ONE STOP','EARLY VOTING']:continue
            try:day=datetime.strptime(row['ballot_rtn_dt'].strip(),'%m/%d/%Y').date().isoformat()
            except ValueError:continue
            if not start<=day<=end:continue
            statuses[row['ballot_rtn_status'].strip()]+=1
            if row['ballot_rtn_status'].strip()!='ACCEPTED':continue
            daily[day]+=1;ages[row['age'].strip()]+=1
            for dimension,field in [('party','voter_party_code'),('race','race'),('ethnicity','ethnicity'),('gender','gender')]:
                demographics[(dimension,row[field].strip() or 'Unknown')]+=1
            try:parsed_age=int(row['age'].strip())
            except ValueError:parsed_age=None
            demographics[('age',str(parsed_age) if parsed_age is not None else 'Unknown')]+=1
            group=next((label for lo,hi,label in [(18,24,'18–24'),(25,34,'25–34'),(35,44,'35–44'),(45,64,'45–64'),(65,120,'65+')] if parsed_age is not None and lo<=parsed_age<=hi),'Unknown / outside range')
            demographics[('age_group',group)]+=1
            is_sdr=row['sdr'].strip().upper() in ['Y','YES'];sdr+=is_sdr;daily_sdr[day]+=is_sdr
            if row['age'].strip().isdigit():
                age=int(row['age'].strip());daily_youth[day]+=18<=age<=24;daily_narrow[day]+=18<=age<=22
    count=sum(daily.values());young=sum(ages[str(a)] for a in range(18,25));narrow=sum(ages[str(a)] for a in range(18,23))
    expected=next(r for r in data['summary'] if r['year']==year and r['scope']=='Campus site')
    actual={'all_ages':count,'age_18_24':young,'age_18_22':narrow,'same_day_registration':sdr,'age_18_24_share':100*young/count}
    assert all(actual[k]==expected[k] for k in actual)
    expected_demographics={(r['dimension'],r['value']):r['votes'] for r in data['demographics'] if r['year']==year and r['scope']=='Campus site'}
    assert dict(demographics)==expected_demographics, f'Demographic recount differs in {year}'
    source=next(s for s in data['sources'] if date in s['url'])
    with (raw/f'absentee_county_{date}.zip').open('rb') as file:
        assert hashlib.file_digest(file,'sha256').hexdigest()==source['sha256']
    with zipfile.ZipFile(raw/f'absentee_county_{date}.zip') as archive,archive.open(source['member']) as member,(raw/f'wake_{date}.csv').open('rb') as csvfile:
        member_sha=hashlib.file_digest(member,'sha256').hexdigest()
        assert member_sha==hashlib.file_digest(csvfile,'sha256').hexdigest()
    source={**source,'wake_csv_sha256':member_sha}
    proof.append({'year':year,'site_name':site,'start_date':start,'end_date':end,'actual':actual,'daily':dict(sorted(daily.items())),'daily_metrics':[{'date':day,'all_ages':daily[day],'age_18_24':daily_youth[day],'age_18_22':daily_narrow[day],'same_day_registration':daily_sdr[day]} for day in sorted(daily)],'ages_18_24':{str(a):ages[str(a)] for a in range(18,25)},'demographics':[{'dimension':dim,'value':value,'votes':votes} for (dim,value),votes in sorted(demographics.items())],'status_counts_before_accepted_filter':dict(statuses),'source':source,'verification':'Exact match to published aggregate table and every campus demographic breakdown; original archive and member hashes verified'})
target=root/'data/processed/comparison/reference_audit.json'
target.write_text(json.dumps({'classification':'Project calculations from official records; not values printed on the NCSBE catalog page','checks':proof},indent=2),encoding='utf-8')
print(json.dumps(proof,indent=2))
