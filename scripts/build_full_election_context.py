"""Aggregate the Nov. 4 post-election pull; never export individual voter records.

Inputs are ignored official downloads in data/raw/postelection_20261104 and
the already hashed county absentee CSVs. Results votes are NOT voter counts.
"""
import csv,hashlib,io,json,zipfile
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/postelection_20261104'
OUT=ROOT/'data/processed/postelection_20261104'
OUT.mkdir(parents=True,exist_ok=True)
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def table(name,rows):
 with (OUT/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

manifest=load(RAW/'source_manifest.json')
for source in manifest:
 assert hashlib.file_digest((RAW/source['file']).open('rb'),'sha256').hexdigest()==source['sha256']
save('source_manifest.json',manifest)
availability=load(RAW/'availability.json')
assert availability[0]['http_status']==404
assert 'history_stats_20261103' not in (RAW/'listing.txt').read_text()
availability.append({'finding':'2026 general-election demographic voter-history statistics absent from official directory; current statewide voter history predates Election Day. Missing is not zero.','source':'https://www.ncsbe.gov/results-data/voter-history-data'})
save('availability.json',availability)

counties=[]
for year in [2022,2026]:
 for r in load(RAW/f'county_{year}.json'):
  counties.append({'year':year,'county':r['cnm'],'ballots_cast':int(r['bct']),
   'registered_voters':int(r['rtl']),'reported_turnout_pct':float(r['bpt'].rstrip('%')),
   'precincts_reported':int(r['prt']),'precincts_total':int(r['ptl']),
   'status':'Unofficial' if 'UNOFFICIAL' in r['tle'] else 'Official',
   'county_last_upload':r['imp'],'county_last_submit':r['sub'],
   'source_url':f'https://er.ncsbe.gov/enr/{year}1108/data/county.txt' if year==2022 else 'https://er.ncsbe.gov/enr/20261103/data/county.txt'})
table('county_ballots_and_turnout.csv',counties)
comparisons=[]
for name in ['WAKE','STATE']:
 a,b=[next(r for r in counties if r['year']==y and r['county']==name) for y in [2022,2026]]
 comparisons.append({'scope':'Wake County' if name=='WAKE' else 'North Carolina',
  'ballots_2022':a['ballots_cast'],'ballots_2026':b['ballots_cast'],
  'ballot_change':b['ballots_cast']-a['ballots_cast'],
  'growth_pct':(b['ballots_cast']/a['ballots_cast']-1)*100,
  'reported_turnout_pct_2022':a['reported_turnout_pct'],'reported_turnout_pct_2026':b['reported_turnout_pct'],
  'turnout_change_pp':b['reported_turnout_pct']-a['reported_turnout_pct'],
  'registered_2022':a['registered_voters'],'registered_2026':b['registered_voters'],
  'precincts_reported_2026':b['precincts_reported'],'precincts_total_2026':b['precincts_total'],
  'status_2022':a['status'],'status_2026':b['status'],
  'source_2022':a['source_url'],'source_2026':b['source_url']})
table('state_and_wake_comparison.csv',comparisons)

methods=[];mail_groups=[];statuses=[]
for year in [2022,2026]:
 tally=Counter();demographics=Counter();status=Counter()
 path=ROOT/f'data/raw/early_voting/wake_{year}{"1108" if year==2022 else "1103"}.csv'
 with path.open(encoding='latin-1',newline='') as f:
  for r in csv.DictReader(f):
   assert r['county_desc'].strip()=='WAKE'
   kind=r['ballot_req_type'].strip().upper();accepted=r['ballot_rtn_status'].strip()
   if kind=='MAIL':
    status[accepted]+=1
    if not accepted.startswith('ACCEPTED'):continue
    tally['Accepted mail ballots']+=1
    age=int(r['age']) if r['age'].strip().isdigit() else None
    band=next((label for lo,hi,label in [(0,17,'Under 18'),(18,24,'18–24'),(25,34,'25–34'),(35,44,'35–44'),(45,64,'45–64'),(65,200,'65+')] if age is not None and lo<=age<=hi),'Unknown')
    demographics['age_group',band]+=1
    for key in ['voter_party_code','race','ethnicity','gender']:demographics[key,r[key].strip()]+=1
   elif kind in ['EARLY VOTING','ONE-STOP','ONE STOP'] and accepted=='ACCEPTED':tally['Accepted in-person early ballots']+=1
 for method,n in tally.items():methods.append({'year':year,'scope':'Wake County','method':method,'ballots':n,'status':'Preliminary' if year==2026 else 'Historical accepted-ballot extract','source_url':f'https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/{year}_{"11_08" if year==2022 else "11_03"}/absentee_county_{year}{"1108" if year==2022 else "1103"}.zip'})
 for (dimension,value),n in sorted(demographics.items()):mail_groups.append({'year':year,'scope':'Wake County','dimension':dimension,'value':value,'accepted_mail_ballots':n})
 for status,n in sorted(status.items()):statuses.append({'year':year,'scope':'Wake County','mail_status':status,'records':n,'included_in_accepted_mail':status.startswith('ACCEPTED')})
 assert sum(n for (d,v),n in demographics.items() if d=='age_group')==tally['Accepted mail ballots']
table('accepted_early_and_mail.csv',methods);table('accepted_mail_demographics.csv',mail_groups);table('mail_status_counts.csv',statuses)

# Independent 2026 published aggregate check; demographic cross-products are disjoint.
for suffix,scope in [('county','Wake County'),('state','North Carolina')]:
 totals=Counter()
 with (RAW/f'absentee_counts_{suffix}_2026.csv').open(encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f):
   if suffix=='county' and r['county_name']!='WAKE':continue
   totals[r['abs_request_type']]+=int(r['0'])
 early=totals['EARLY VOTING']+totals['EARLYVOTING']+totals['ONE-STOP']
 mail=sum(totals[k] for k in ['CIVILIAN','MILITARY','OVERSEAS'])
 if scope=='Wake County':
  assert early==next(r['ballots'] for r in methods if r['year']==2026 and r['method']=='Accepted in-person early ballots')
  assert mail==next(r['ballots'] for r in methods if r['year']==2026 and r['method']=='Accepted mail ballots')
 else:
  for label,n in [('Accepted in-person early ballots',early),('Accepted mail ballots',mail)]:methods.append({'year':2026,'scope':scope,'method':label,'ballots':n,'status':'Preliminary','source_url':next(s['url'] for s in manifest if s['file']=='absentee_counts_state_2026.csv')})
table('accepted_early_and_mail.csv',methods)

pv=Counter()
with (RAW/'provisional_2026.txt').open(encoding='utf-16',newline='') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  if r['county_name'].strip()=='WAKE':pv[r['pv_status'].strip()]+=1
table('wake_provisional_status.csv',[{'year':2026,'county':'WAKE','status':s,'records':n,'interpretation':'Pending is not an additional counted ballot'} for s,n in sorted(pv.items())])

# A contest's choice votes are useful Election Day evidence, but never turnout.
contest=defaultdict(Counter);precinct=[]
with zipfile.ZipFile(RAW/'results_2026.zip') as z:
 with io.TextIOWrapper(z.open(z.namelist()[0]),encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f,delimiter='\t'):
   if r['County']!='WAKE':continue
   keys=['Election Day','Early Voting','Absentee by Mail','Provisional','Total Votes']
   nums={k:int(r[k]) for k in keys};assert sum(nums[k] for k in keys[:-1])==nums['Total Votes']
   contest[r['Contest Name']].update(nums)
   if r['Contest Name']=='US SENATE':precinct.append({k:r[k] for k in ['Precinct','Choice','Choice Party','Vote For','Real Precinct']}|nums)
table('wake_contest_votes_by_method.csv',[{'contest':c,'unit':'Choice votes, not unique voters',**n} for c,n in sorted(contest.items())])
if precinct:table('wake_us_senate_precinct_votes.csv',precinct)
summary={'as_of':'2026-11-04','retrieved_utc':manifest[0]['retrieved_utc'],'certification_status_2026':'Unofficial',
 'comparisons':comparisons,'accepted_method_counts':methods,'wake_provisional_status':dict(pv),
 'election_day_demographics':'Unavailable: 2026 Nov. 3 history_stats not published; current voter history last modified Nov. 2 UTC.',
 'reconciliation':'Dashboard ballots, accepted absentee extracts and pending provisionals have separate source cutoffs. Do not subtract them to manufacture an Election Day voter count. Contest totals count choices, not unique voters.'}
save('summary.json',summary)
article_path=ROOT/'report-source/article-snapshot.json'
article=load(article_path)
display_rows=[]
for comparison in comparisons:
 row=dict(comparison)
 if row['scope']=='Wake County':
  for year in [2022,2026]:
   for label,key in [('Accepted in-person early ballots','early'),('Accepted mail ballots','mail')]:
    row[f'{key}_{year}']=next(r['ballots'] for r in methods if r['scope']=='Wake County' and r['year']==year and r['method']==label)
  row['pending_provisionals']=pv['PENDING']
 display_rows.append(row)
article['queries']['full_election_context']={'rows':display_rows,'source':{
 'label':'NCSBE all-method ballot totals and accepted early/mail extracts, November 4 pull',
 'provider':'North Carolina State Board of Elections','executedAt':summary['retrieved_utc'],
 'period':'2022 and 2026 general elections; all-method results through November 4, 2026',
 'files':[r['source_2022'] for r in comparisons[:1]]+[r['source_2026'] for r in comparisons[:1]]+[r['source_url'] for r in methods if r['scope']=='Wake County']+['https://www.ncsbe.gov/results-data/voter-history-data'],
 'filters':['Dashboard bct = ballots cast; rtl = registered voters; bpt = reported turnout', 'Absentee county = WAKE; early status = ACCEPTED; mail status starts with ACCEPTED'],
 'caveats':['2022 official; 2026 unofficial. Precincts reported is not certification.',summary['election_day_demographics'],summary['reconciliation']],
 'evidenceFlow':[{'title':'Source hashes and dates','detail':'data/processed/postelection_20261104/source_manifest.json'},{'title':'Reproduce aggregate tables','detail':'scripts/build_full_election_context.py; 2026 Wake accepted early/mail totals independently reconcile to published absentee aggregates.'}]},
 'methods':{'description':summary['reconciliation']}}
article.setdefault('authoredRevision',8)
article['report']['asOf']='2026-11-04'
article['buildStatus']='complete'
article_path.write_text(json.dumps(article,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prototype_path=ROOT/'report-source/snapshot.json'
prototype=load(prototype_path)
prototype['queries']['full_election_context']=article['queries']['full_election_context']
prototype['report']['asOf']='2026-11-04'
prototype['buildStatus']='complete'
prototype_path.write_text(json.dumps(prototype,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notes='''# Post-election data, November 4, 2026

2026 results are unofficial. These aggregates include current reported all-method ballot totals, accepted early/mail extracts, provisional status, and Election Day choice votes by contest. They do not yet provide Election Day or all-method age-18–24 participation. NCSBE updates current voter history weekly, and county finalization can take multiple weeks.

`county_ballots_and_turnout.csv` preserves the dashboard ballot/registration/turnout fields for all 100 counties plus the statewide aggregate in each year. STATE is an aggregate: do not add it to counties. `state_and_wake_comparison.csv` compares 2022 official with 2026 unofficial results. Rates shown are the dashboard's rounded rates, not an age-specific denominator.

`accepted_early_and_mail.csv` and `accepted_mail_demographics.csv` use the official county absentee files. Accepted mail includes ACCEPTED, ACCEPTED - CURED and ACCEPTED - EXCEPTION where present. Status counts remain separate. The 2026 Wake totals independently match NCSBE's demographic aggregate file. Early and mail extracts are separate from the later results-dashboard snapshot, and must not be subtracted from it to assert an Election Day voter count.

`wake_contest_votes_by_method.csv` contains votes for choices within each contest. Never sum different contests as voters. Multi-seat races permit multiple choices; undervotes also prevent treating a single contest as unique ballot counts. The Election Day column is evidence of votes cast in that method, not demographic turnout. `wake_provisional_status.csv` counts pending records; pending is not accepted.

`availability.json` records the missing 2026 demographic history release and the pre-election timestamp of current statewide voter history. The available Nov. 3 registration statistics group ages 18–25, which do not match the article's 18–24 group. They are not substituted for the missing election participation data.

Sources: [NCSBE results dashboard](https://er.ncsbe.gov/), [historical election result layouts](https://www.ncsbe.gov/results-data/election-results/historical-election-results-data), [voter history availability and release schedule](https://www.ncsbe.gov/results-data/voter-history-data). Download timestamps, source URLs and SHA-256 values are in source_manifest.json. Raw voter files stay outside published artifacts.
'''
(OUT/'README.md').write_text(notes,encoding='utf-8')
archive=ROOT/'downloads/nc-voting-postelection-20261104.zip'
archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(OUT.iterdir()):
  if path.is_file():z.write(path,path.name)
print(json.dumps({'comparisons':comparisons,'methods':methods,'pending':dict(pv),'wake_contests':len(contest),'mail_age_18_24':[r for r in mail_groups if r['dimension']=='age_group' and r['value']=='18–24']},ensure_ascii=False))
