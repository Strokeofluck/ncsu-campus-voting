"""Check article evidence, exact math, source windows, and usable reference links."""
import csv,json,math,re
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.inside=False;self.data=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if tag in ['a','script','link'] and (a.get('href') or a.get('src')):self.links.append(a.get('href',a.get('src')))
  if tag=='script' and a.get('id')=='reference-data':self.inside=True
 def handle_endtag(self,tag):
  if tag=='script':self.inside=False
 def handle_data(self,text):
  if self.inside:self.data+=text

html=(ROOT/'references.html').read_text(encoding='utf-8');p=Page();p.feed(html)
assert len(p.ids)==len(set(p.ids)) and not re.search(r'__[A-Z_]+__',html)
d=json.loads(p.data)
with (ROOT/'data/processed/comparison/matched_demographics.csv').open(encoding='utf-8',newline='') as f:raw=list(csv.DictReader(f))
assert [r['cohort'] for r in d['rows']]==['18–24','25–34','35–44','45–64','65+']
assert min(d['rows'],key=lambda r:r['site_growth_gap_pp'])['cohort']=='18–24'
for r in d['rows']:
 for scope,prefix in [('Campus site','site'),('Wake County','county')]:
  for year in [2022,2026]:
   expected=sum(int(v['votes']) for v in raw if int(v['year'])==year and v['scope']==scope and v['dimension']=='age_group' and v['value']==r['cohort'])
   assert r[f'{prefix}_ballots_{year}']==expected
  a,b=[r[f'{prefix}_ballots_{y}'] for y in [2022,2026]]
  exact=float(Fraction(b-a,a)*100)
  assert math.isclose(r[prefix+'_growth_pct'],exact,abs_tol=1e-10)
 assert math.isclose(r['site_growth_gap_pp'],r['site_growth_pct']-r['county_growth_pct'],abs_tol=1e-10)
assert d['periods']['2022']=={'start_date':'2022-10-20','end_date':'2022-11-05'}
assert d['periods']['2026']=={'start_date':'2026-10-15','end_date':'2026-10-31'}
assert d['as_of']=='2026-10-31' and d['matched_days']==17
assert html.count('class="source-card"')==2
assert 'id="baseline"' not in html and 'CsvProofView' not in html and 'csv-workspace' not in html
assert '32.1%' not in html and '31.8%' not in html and 'share of site ballots' not in html
assert '+36.4%' in html and '+90.8%' in html and '54.5 percentage points behind' in html
youngest=d['rows'][0]
benchmark=Fraction(youngest['site_ballots_2022'],youngest['county_ballots_2022'])*youngest['county_ballots_2026']
assert round(benchmark)==6493 and round(benchmark-youngest['site_ballots_2026'])==1854
assert 'id="youngest-benchmark"' in html and '6,493 benchmark − 4,639 actual ≈ 1,854 below benchmark' in html
assert 'not a count of nonvoters or proof of the move' in html
assert '50 ÷ 80 × 60 = 37.5 seconds ≈ 38 seconds' in html and '0.625 minutes' not in html
assert all(f'id="{id}"' in html for id in ['ref-growth','ref-walking','ref-routine','ref-parking','ref-reporting','google-route-verification'])
assert html.count('class="google-verification-group"')==4
for href in p.links:
 u=urlsplit(href)
 if u.scheme or u.netloc:continue
 if u.path:
  path=ROOT/unquote(u.path)
  assert path.is_file() or (path/'index.html').is_file(),href
 elif u.fragment:assert unquote(u.fragment) in p.ids,href
article=json.loads((ROOT/'report-source/article-snapshot.json').read_text(encoding='utf-8'))
prototype=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
expected_google={r[key+'_url'] for r in prototype['queries']['campus_google_walks']['rows'] for key in ['talley','western']}
actual_google={href for href in p.links if href.startswith('https://www.google.com/maps/dir/')}
assert len(expected_google)==80 and actual_google==expected_google
assert 50/80*60==37.5
assert 'Wolf Village apartments · 8 / 8 buildings · 0.63 mi closer' in html
assert article['id']!=prototype['id']
for key in article['queries']:
 if key not in {'statewide_early_voting_context','article_opening_context','full_election_context'}:assert article['queries'][key]['rows']==prototype['queries'][key]['rows'],key
opening=article['queries']['article_opening_context']
assert len(opening['rows'])==3 and all(r['source_url'] in opening['source']['files'] for r in opening['rows'])
assert opening['rows'][0]['reported_at']=='2026-11-02' and 'midterm early' in opening['rows'][0]['claim']
assert 'id="full-period-data"' in html and '334,088' in html and '14,496' in html
assert 'portion' in opening['rows'][2]['claim']
assert sum(r['spaces'] for r in article['queries']['campus_parking']['rows'] if r['objectid'] in [26,92,166])==2192
assert sum(r['spaces'] for r in article['queries']['campus_parking']['rows'] if r['objectid'] in [34,38,55,56])==660
routine=[r for r in article['queries']['campus_passby']['rows'] if not r['ends_at_talley']]
assert len(routine)==756 and len({r['origin_id'] for r in routine})==36 and len({r['destination_id'] for r in routine})==21
assert sum(r['talley_nearest_m']<=50 for r in routine)==334
assert sum(r['western_nearest_m']<=50 for r in routine)==0
if 'statewide_early_voting_context' in article['queries']:
 context=article['queries']['statewide_early_voting_context']['rows'][0]
 assert context['accepted_early_ballots']==2612240 and context['growth_vs_2022_same_day_pct_displayed']==32
 assert context['in_person_ballots']+context['mail_ballots']==context['accepted_early_ballots']
 assert context['ballots_through']=='2026-10-30' and context['election_day']=='2026-11-03'
assert article['report']['asOf']=='2026-11-04' and prototype['report']['asOf']=='2026-10-31'
print('PASS: original aggregate inputs, all five exact growth/gap calculations, matched windows, focused reference scope, local links, and distinct article identity with unchanged evidence.')

full=json.loads((ROOT/'data/processed/postelection_20261104/summary.json').read_text(encoding='utf-8'))
assert 'id="full-election-data"' in html and '525,061' in html and '4,223,102' in html
assert 'Election Day age counts are not available yet.' in html
for actual,want in zip(article['queries']['full_election_context']['rows'],full['comparisons']):
 for key,value in want.items():assert actual[key]==value
wake=article['queries']['full_election_context']['rows'][0]
assert wake['ballots_2022']==454488 and wake['ballots_2026']==525061
assert wake['early_2026']==334088 and wake['mail_2026']==19334 and wake['mail_2022']==36240
assert wake['pending_provisionals']==547 and wake['status_2026']=='Unofficial'
print('PASS: all-method context, accepted mail variants, provisional status and unavailable Election Day ages agree with source aggregates.')
