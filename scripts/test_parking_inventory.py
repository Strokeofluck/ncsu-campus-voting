"""Audit source-field parking totals and preserve route evidence and date limitations."""
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk';SRC=ROOT/'data/sources/ncsu-gis/2026-11-01'
talley=json.loads((OUT/'talley-parking-gis-raw.json').read_text(encoding='utf-8'));western=json.loads((OUT/'parking-gis-raw.json').read_text(encoding='utf-8'))
raw={f['attributes']['OBJECTID']:f for d in [talley,western] for f in d['data']['features']};park=json.loads((OUT/'nearby-parking.geojson').read_text(encoding='utf-8'));rows=[f['properties'] for f in park['features']]
assert len(rows)==len({r['objectid'] for r in rows})==10
for r in rows:
 a=raw[r['objectid']]['attributes'];assert all(r[k]==a[f] for k,f in [('name','NAME'),('spaces','SPACES'),('type','Type'),('zone','ZONE_')]);assert r['spaces']>=0
deck=[raw[i]['attributes'] for i in [26,92,166]];assert {a['Type'] for a in deck}=={'Deck'};assert {a['ZONE_'] for a in deck}=={'PY','CD','RE'}
assert sum(a['SPACES'] for a in deck)==2192
assert sum(raw[i]['attributes']['SPACES'] for i in [34,38,55,56])==660
assert all(raw[i]['attributes']['Type']=='Surface' for i in [34,38,55,56,143,144,82])
assert raw[143]['attributes']['SPACES']==226 and raw[144]['attributes']['SPACES']==66 and raw[82]['attributes']['SPACES']==15
assert round(660/2192*100,1)==30.1 and 2192-660==1532 and round(1532/2192*100,1)==69.9
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));assert s['campusParking']==park;assert s['queries']['campus_parking']['rows']==rows
original=json.loads((OUT/'routes.json').read_text(encoding='utf-8'));assert s['queries']['campus_walking_routes']['rows']==original['rows'];assert len(s['queries']['campus_passby']['rows'])==792
catalog=json.loads((SRC/'catalog.json').read_text(encoding='utf-8'))
for f in catalog['files']:assert hashlib.sha256((SRC/f['name']).read_bytes()).hexdigest()==f['sha256']
evidence=json.loads((SRC/'parking-evidence.json').read_text(encoding='utf-8'));assert '2022' in evidence['unverified']
html=(ROOT/'references.html').read_text(encoding='utf-8');assert all(x in html for x in ['id="talley-parking"','id="parking-capacity"','30.1%','1,532','69.9%','fall 2022','Not confirmed from the public sources reviewed'])
assert html.count('Checking Show all routes pauses autoplay and restores the full route network.')==1
print('PASS: ten exact source-feature counts; deck-only 2,192 and four-area McKimmon 660; separate surface areas excluded; hypothetical percentages/remainder; frozen hashes; original routes/denominators and date limits preserved.')
