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
assert d['periods']['2022']=={'start_date':'2022-10-20','end_date':'2022-11-04'}
assert d['periods']['2026']=={'start_date':'2026-10-15','end_date':'2026-10-30'}
assert d['as_of']=='2026-10-30' and d['matched_days']==16
assert html.count('class="source-card"')==2
assert 'id="baseline"' not in html and 'CsvProofView' not in html and 'csv-workspace' not in html
assert '32.1%' not in html and '31.8%' not in html and 'share of site ballots' not in html
assert '+40.5%' in html and '+103.6%' in html and '63.1 percentage points behind' in html
youngest=d['rows'][0]
benchmark=Fraction(youngest['site_ballots_2022'],youngest['county_ballots_2022'])*youngest['county_ballots_2026']
assert round(benchmark)==6106 and round(benchmark-youngest['site_ballots_2026'])==1892
assert 'id="youngest-benchmark"' in html and 'about 6,106 ballots at the benchmark versus 4,214 actual' in html and 'about 1,892 fewer' in html
assert 'always for the youngest age group' in html and 'not a prediction or a count of people who did not vote' in html
for href in p.links:
 u=urlsplit(href)
 if u.scheme or u.netloc:continue
 if u.path:
  path=ROOT/unquote(u.path)
  assert path.is_file() or (path/'index.html').is_file(),href
 elif u.fragment:assert unquote(u.fragment) in p.ids,href
article=json.loads((ROOT/'report-source/article-snapshot.json').read_text(encoding='utf-8'))
prototype=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
assert article['id']!=prototype['id']
for key in article['queries']:
 if key not in {'statewide_early_voting_context','article_opening_context'}:assert article['queries'][key]['rows']==prototype['queries'][key]['rows'],key
opening=article['queries']['article_opening_context']
assert len(opening['rows'])==3 and all(r['source_url'] in opening['source']['files'] for r in opening['rows'])
assert opening['rows'][0]['reported_at']=='2026-10-31' and 'midterm early' in opening['rows'][0]['claim']
assert 'portion' in opening['rows'][2]['claim']
assert sum(r['spaces'] for r in article['queries']['campus_parking']['rows'] if r['objectid'] in [26,92,166])==2192
assert sum(r['spaces'] for r in article['queries']['campus_parking']['rows'] if r['objectid'] in [34,38,55,56])==660
if 'statewide_early_voting_context' in article['queries']:
 context=article['queries']['statewide_early_voting_context']['rows'][0]
 assert context['accepted_early_ballots']==2612240 and context['growth_vs_2022_same_day_pct_displayed']==32
 assert context['in_person_ballots']+context['mail_ballots']==context['accepted_early_ballots']
 assert context['ballots_through']=='2026-10-30' and context['election_day']=='2026-11-03'
assert article['report']['asOf']==prototype['report']['asOf']
print('PASS: original aggregate inputs, all five exact growth/gap calculations, matched windows, focused reference scope, local links, and distinct article identity with unchanged evidence.')
