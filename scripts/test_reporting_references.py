import json,re
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[];self.in_data=False;self.data='';self.iframes=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag in ['a','link','script']:
            href=a.get('href',a.get('src'))
            if href:self.links.append(href)
        if tag=='iframe':self.iframes.append(a)
        if tag=='script' and a.get('id')=='reference-data':self.in_data=True
    def handle_endtag(self,tag):
        if tag=='script':self.in_data=False
    def handle_data(self,text):
        if self.in_data:self.data+=text

html=(ROOT/'references.html').read_text(encoding='utf-8');page=Page();page.feed(html)
assert len(page.ids)==len(set(page.ids))
assert not re.search(r'__[A-Z_]+__',html)
assert '41.5%' not in html and '7,194' not in html and '17,339' not in html
d=json.loads(page.data)
figures=json.loads((ROOT/'data/processed/comparison/figure_sources.json').read_text(encoding='utf-8'))['records']
summary=lambda y,s:next(r for r in d['summary'] if r['year']==y and r['scope']==s)
for baseline in [2022,2024]:
    for scope,field in [('Campus site','all_ages'),('Campus site','age_18_24'),('Wake County','age_18_24')]:
        old=summary(baseline,scope)[field];new=summary(2026,scope)[field]
        key=f'growth-{baseline}-'+scope.lower().replace(' ','-')+'-'+field.replace('_','-')
        assert abs(d['records'][key]['value']-float(Fraction(new-old,old)*100))<1e-10
    for group in ['18-24','65']:
        old=figures[f'demographic-{baseline}-age-group-{group}']['inputs'][0]['value'];new=figures[f'demographic-2026-age-group-{group}']['inputs'][0]['value']
        expected=(Fraction(new,summary(2026,'Campus site')['all_ages'])-Fraction(old,summary(baseline,'Campus site')['all_ages']))*100
        assert abs(d['records'][f'change-{baseline}-age-group-{group}']['value']-float(expected))<1e-10
for key,record in d['records'].items():assert record['value']==figures[key]['value'] and record['unit']==figures[key]['unit']
for href in page.links:
    url=urlsplit(href)
    if url.scheme or url.netloc:continue
    if url.path:assert (ROOT/unquote(url.path)).is_file(),href
    elif url.fragment:assert unquote(url.fragment) in page.ids,href
for year in [2022,2024,2026]:
    source=figures[f'summary-{year}-campus-site-all-ages']['sources'][0]
    archive=unquote(urlsplit(source['url']).path.rsplit('/',1)[-1])
    assert archive in html and source['member'] in html
assert html.count('class="official-download-steps"')==3
assert not page.iframes
assert 'csv-workspace' in page.ids and 'proof-math' in page.ids
assert 'proof-tab-calculation' in page.ids and 'proof-download-workbook' in page.ids
assert 'growth-proof-cards' in page.ids and html.count('class="growth-proof-card"')==2
assert '+40.5%' in html and '+103.6%' in html
for required in ['5 County source','6 County flags','7 County counts','8 Growth proof','twelve']:
    assert required in html,required
assert 'browser-preview' not in html and 'Open calculation in a full tab' not in html
library=(ROOT/'report-source/reference-library.html').read_text(encoding='utf-8')
for expected in ['EarlyVotingSitesWithTurnout.pdf','history_stats_20221108.zip','polling_place_20221108.csv','157482/news/heres-who-voted-early-in-talley-student-union','docs/election-day-methodology.md']:
    assert expected in library and expected in html,expected
print('Passed reporting-reference checks: both baselines, exact growth and percentage-point calculations, current snapshot values, local assets, unique anchors, calculation-first CSV preview and preserved earlier source links.')
