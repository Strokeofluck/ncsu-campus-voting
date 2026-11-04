import codecs,csv,hashlib,io,json,math,re,zipfile
from datetime import date
from pathlib import Path
from lxml import etree
import argparse
parser=argparse.ArgumentParser();parser.add_argument('package',type=Path);parser.add_argument('--summary-only',action='store_true');args=parser.parse_args()
repo=Path(__file__).resolve().parents[1]
outer=zipfile.ZipFile(args.package)
manifest=json.loads(outer.read('03 Source checks/source-manifest.json'))
book=zipfile.ZipFile(io.BytesIO(outer.read('02 Working copy/talley-western-growth-step-by-step.xlsx')))
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def text(value):
 return re.sub(r'_x([0-9a-fA-F]{4})_',lambda m:chr(int(m[1],16)),value or '')
def rows(n):
 with book.open(f'xl/worksheets/sheet{n}.xml') as f:
  for _,r in etree.iterparse(f,events=('end',),tag='{*}row'):
   cells={}
   for c in r:
    col=re.match('[A-Z]+',c.get('r')).group();v=c.find('s:v',ns);formula=c.find('s:f',ns)
    if c.get('t')=='inlineStr':value=text(''.join(c.itertext()))
    elif c.get('t')=='str':value=text(v.text if v is not None else '')
    else:value=float(v.text) if v is not None and v.text else None
    cells[col]=(value,formula.text if formula is not None else None)
   yield int(r.get('r')),cells
   r.clear()
   while r.getprevious() is not None:del r.getparent()[0]
def col(i):
 out='';i+=1
 while i:out=chr(65+(i-1)%26)+out;i=(i-1)//26
 return out
def skip(it,first):
 for r,c in it:
  if r>=first:yield r,c
codecs.register_error('browser1252',lambda e:(''.join(chr(b) for b in e.object[e.start:e.end]),e.end))
expected=json.loads((repo/'report-source/snapshot.json').read_text(encoding='utf-8'))['queries']['age_growth_benchmarks']['rows']
fields=['county_desc','ballot_req_type','ballot_rtn_status','ballot_rtn_dt','site_name','age']
bands=[(18,24),(25,34),(35,44),(45,64),(65,120)]
if manifest.get('mode')=='updated':
 expected=manifest['results']
 if args.summary_only:
  for source in manifest['sources']:
   year=source['year'];path=f'01 Original files/{year}/{source["member"]}';totals=[[0,0] for _ in bands]
   with outer.open(path) as raw:assert hashlib.file_digest(raw,'sha256').hexdigest()==source['wake_csv_sha256']
   with outer.open(path) as raw:
    for row in csv.DictReader(io.TextIOWrapper(raw,encoding='cp1252',errors='browser1252',newline='')):
     if row['county_desc'].strip()!='WAKE' or row['ballot_req_type'].strip().upper() not in ['ONE-STOP','ONE STOP','EARLY VOTING'] or row['ballot_rtn_status'].strip()!='ACCEPTED':continue
     parts=row['ballot_rtn_dt'].strip().split('/');day=f'{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}' if len(parts)==3 else '';age=row['age'].strip()
     start,end=('2022-10-20','2022-11-04') if year==2022 else ('2026-10-15','2026-10-30')
     if not start<=day<=end or not age.isdigit():continue
     site='TA - NCSU TALLEY STUDENT CENTER' if year==2022 else 'NCSU WESTERN BLVD BUSINESS SERVICES'
     for b,(lo,hi) in enumerate(bands):
      if lo<=int(age)<=hi:totals[b][0]+=int(row['site_name'].strip()==site);totals[b][1]+=1
   for b,row in enumerate(expected):assert totals[b]==[row[f'site_ballots_{year}'],row[f'county_ballots_{year}']]
  print('Updated input hashes and all 20 counts independently verified from included original CSVs.',flush=True)
if not args.summary_only:
 for j,source in enumerate(manifest['sources']):
  year=source['year'];path=f'01 Original files/{year}/{source["member"]}'
  with outer.open(path) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source['wake_csv_sha256']
  copy=iter(rows(3+j));field=iter(skip(rows(5+j),6));rules=iter(skip(rows(7+j),6));count=0;running=[0,0];totals=[[0,0] for _ in bands]
  with outer.open(path) as raw:
   reader=csv.reader(io.TextIOWrapper(raw,encoding='cp1252',errors='browser1252',newline=''));headers=next(reader)
   r,c=next(copy);assert r==1 and [c[col(i)][0] for i in range(len(headers))]==headers
   indexes=[headers.index(f) for f in fields]
   site='TA - NCSU TALLEY STUDENT CENTER' if year==2022 else 'NCSU WESTERN BLVD BUSINESS SERVICES'
   start,end=('2022-10-20','2022-11-04') if year==2022 else ('2026-10-15','2026-10-30')
   for count,original in enumerate(reader,1):
    cr,cc=next(copy);assert cr==count+1
    assert [cc[col(i)][0] for i in range(len(headers))]==original,('Copy differs',year,count)
    fr,fc=next(field);rr,rc=next(rules);assert fr==rr==count+5
    selected=[original[i] for i in indexes];assert fc['A'][0]==count+1
    for k,value in enumerate(selected):
     cell=fc[col(k+1)];assert cell[0]==value and cell[1]==f'IF(\'Copy {year}\'!{col(indexes[k])}{count+1}="","",\'Copy {year}\'!{col(indexes[k])}{count+1})'
    county,method,status,rawdate,location,rawage=[v.strip() for v in selected]
    day=rawdate[6:]+'-'+rawdate[:2]+'-'+rawdate[3:5] if re.fullmatch(r'\d{2}/\d{2}/\d{4}',rawdate) else ''
    age=int(rawage) if rawage.isdigit() else None
    wake=int(county=='WAKE');early=int(method.upper() in ['ONE-STOP','ONE STOP','EARLY VOTING']);accepted=int(status=='ACCEPTED');matched=int(bool(day) and start<=day<=end);at=int(location==site)
    included=wake*early*accepted*matched;named=included*at;running[0]+=included;running[1]+=named
    serial=(date.fromisoformat(day)-date(1899,12,30)).days if day else ''
    calculated=[count+1,wake,early,accepted,serial,matched,age if age is not None else '',at,included,named,*running]
    assert [rc[col(i)][0] for i in range(12)]==calculated,('Rule cached result differs',year,count)
    assert all(rc[col(i)][1] for i in range(12))
    for b,(lo,hi) in enumerate(bands):
     if age is not None and lo<=age<=hi:totals[b][0]+=named;totals[b][1]+=included
    if count%100000==0:print('Verified every original cell, linked field, flag and running sum:',year,count,flush=True)
  assert count==source['original_records'];assert next(copy,None) is None and next(field,None) is None and next(rules,None) is None
  for b,r in enumerate(expected):assert totals[b]==[r[f'site_ballots_{year}'],r[f'county_ballots_{year}']]
  print('Complete year verified:',year,count,'records',flush=True)
for n in [1,9,10]:
 data={r:c for r,c in rows(n) if 6<=r<=10}
 for b,e in enumerate(expected):
  r=b+6;c=data[r]
  if n==1:values=[c[x][0] for x in ['B','C','D']];want=[e['site_growth_pct'],e['county_growth_pct'],e['site_growth_gap_pp']]
  elif n==9:values=[c[x][0] for x in ['B','C','D','E']];want=[e[f'{s}_ballots_{y}'] for s,y in [('site',2022),('site',2026),('county',2022),('county',2026)]]
  else:values=[c[x][0] for x in ['F','K','L']];want=[e['site_growth_pct'],e['county_growth_pct'],e['site_growth_gap_pp']]
  assert all(math.isclose(a,b,abs_tol=1e-9) for a,b in zip(values,want))
  assert all(c[x][1] for x in (['B','C','D'] if n==1 else ['B','C','D','E'] if n==9 else list('BCDEFGHIJKL')))
for j,source in ([] if args.summary_only else enumerate(manifest['sources'])):
 with book.open(f'xl/worksheets/sheet{7+j}.xml') as f:
  f.seek(-12000,2);tail=f.read().decode('utf-8')
 ranges=re.findall(r'sqref="([^"]+)"',tail)
 assert f'I6:I{source["original_records"]+5}' in ranges and f'J6:J{source["original_records"]+5}' in ranges
 assert f'autoFilter ref="A5:L{source["original_records"]+5}"' in tail
share={r:c for r,c in rows(10) if 15<=r<=17}
a=expected[0];before=a['site_ballots_2022']/a['county_ballots_2022'];after=a['site_ballots_2026']/a['county_ballots_2026']
for r,want,formula in [(15,before,'B15/C15'),(16,after,'B16/C16'),(17,(after-before)*100,'(D16-D15)*100')]:
 assert math.isclose(share[r]['D'][0],want,abs_tol=1e-10) and share[r]['D'][1]==formula
workbook=etree.fromstring(book.read('xl/workbook.xml'));calc=workbook.find('s:calcPr',ns);assert calc is not None and calc.get('fullCalcOnLoad')=='1' and calc.get('calcMode')=='auto'
print('PASS: '+('all original copies, linked fields and rule rows; ' if not args.summary_only else '')+'all five age-group counts/growth/gaps; worked countywide share formulas and automatic recalculation.',flush=True)
