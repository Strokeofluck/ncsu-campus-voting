#!/usr/bin/env python3
"""Preview verified original ZIP/CSV metadata and grouped non-identifying columns."""
import csv,json,hashlib,zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from build_figure_sources import preview_key

ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/processed/comparison/comparison.json').read_text(encoding='utf-8'))
proofs=json.loads((ROOT/'data/processed/comparison/figure_sources.json').read_text(encoding='utf-8'))
audits={r['year']:r for r in json.loads((ROOT/'data/processed/comparison/reference_audit.json').read_text(encoding='utf-8'))['checks']}
requests={preview_key(s):s for r in proofs['records'].values() for s in r['selections']}
groups={key:Counter() for key in requests}
columns=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name']
metadata={}
for year,stamp in [(2022,'20221108'),(2024,'20241105'),(2026,'20261103')]:
    audit=audits[year];source=audit['source'];archive=ROOT/f'data/raw/early_voting/absentee_county_{stamp}.zip';csvpath=ROOT/f'data/raw/early_voting/wake_{stamp}.csv'
    for path,expected in [(archive,source['sha256']),(csvpath,source['wake_csv_sha256'])]:
        with path.open('rb') as file:assert hashlib.file_digest(file,'sha256').hexdigest()==expected,f'Source hash differs: {path.name}'
    with zipfile.ZipFile(archive) as z:
        member=z.getinfo(source['member'])
        entries=[{'filename':i.filename,'bytes':i.file_size} for i in z.infolist() if not i.is_dir()]
        with z.open(member) as file:assert hashlib.file_digest(file,'sha256').hexdigest()==source['wake_csv_sha256']
    source_rows=0
    with csvpath.open(encoding='latin-1',newline='') as f:
        header_line=f.readline().rstrip('\r\n');f.seek(0)
        reader=csv.DictReader(f);headers=reader.fieldnames
        assert set(columns)<=set(headers)
        for row in reader:
            source_rows+=1
            if row['county_desc'].strip()!='WAKE' or row['ballot_req_type'].strip().upper() not in ['ONE-STOP','ONE STOP','EARLY VOTING'] or row['ballot_rtn_status'].strip()!='ACCEPTED':continue
            day=datetime.strptime(row['ballot_rtn_dt'].strip(),'%m/%d/%Y').date().isoformat()
            if not audit['start_date']<=day<=audit['end_date']:continue
            campus=row['site_name'].strip()==audit['site_name']
            scopes=['Wake County','Campus site' if campus else 'Other Wake sites']
            try:age=int(row['age'].strip())
            except ValueError:age=None
            group=next((v for lo,hi,v in [(18,24,'18–24'),(25,34,'25–34'),(35,44,'35–44'),(45,64,'45–64'),(65,120,'65+')] if age is not None and lo<=age<=hi),'Unknown / outside range')
            fields=['all_ages']+(['age_18_24'] if age is not None and 18<=age<=24 else [])+(['age_18_22'] if age is not None and 18<=age<=22 else [])+(['same_day_registration'] if row['sdr'].strip().upper() in ['Y','YES'] else [])
            keys=[preview_key({'year':year,'scope':scope,'field':field}) for scope in scopes for field in fields]
            if campus:
                party=row['voter_party_code'].strip();party=party if party in ['DEM','REP','UNA'] else 'OTHER_PARTIES'
                dims=[('all','all'),('age_group',group),('party',party)]+[(dim,row[dim].strip() or 'Unknown') for dim in ['race','gender','ethnicity']]
                keys.extend(preview_key({'year':year,'scope':'Campus site','dimension':dim,'value':value}) for dim,value in dims)
            original_values=tuple(row[column] for column in columns)
            for key in keys:
                if key in groups:groups[key][original_values]+=1
    metadata[str(year)]={'year':year,'url':source['url'],'filename':archive.name,'archive_bytes':archive.stat().st_size,'sha256':source['sha256'],'member':source['member'],'member_bytes':member.file_size,'wake_csv_sha256':source['wake_csv_sha256'],'source_rows':source_rows,'headers':headers,'header_line':header_line,'zip_entries':entries,'verified_archive_and_csv_hashes':True,'last_modified':source['last_modified'],'downloaded_at':source['downloaded_at']}

def expected(selection):
    year=selection['year'];scope=selection['scope']
    row=next(r for r in d['summary'] if r['year']==year and r['scope']==scope)
    if 'field' in selection:return row[selection['field']]
    dim=selection['dimension'];value=selection['value']
    if dim=='all':return row['all_ages']
    return sum(r['votes'] for r in d['demographics'] if r['year']==year and r['scope']==scope and r['dimension']==dim and (r['value']==value if value!='OTHER_PARTIES' else r['value'] not in ['DEM','REP','UNA']))

previews={}
for key,selection in requests.items():
    bucket=groups[key];count=sum(bucket.values());assert count==expected(selection),(key,count,expected(selection))
    ordered=sorted(bucket.items(),key=lambda item:(datetime.strptime(item[0][3].strip(),'%m/%d/%Y'),item[0][4],item[0]))
    previews[key]={'selection':selection,'total_records':count,'total_groups':len(bucket),'shown_groups':min(8,len(bucket)),'rows':[{'values':dict(zip(columns,values)),'records':votes} for values,votes in ordered[:8]]}
payload={'classification':'Verified original file metadata and filtered, grouped extracts; not a full CSV or individual voter rows','as_of':d['as_of'],'preview_columns':columns,'sources':metadata,'previews':previews}
path=ROOT/'data/processed/comparison/source_previews.json';path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Built {len(previews)} source extracts; every full selected count independently matches the report. No names, addresses, voter IDs or individual rows exported.')
