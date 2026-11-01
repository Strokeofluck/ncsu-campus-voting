"""Verify every displayed classification against untouched original GIS records."""
import collections,hashlib,json,zipfile
from pathlib import Path
from urllib.parse import urlparse,parse_qs
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk';audit=json.loads((OUT/'destination-sources.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(OUT/'official-gis-snapshot.zip') as z:
 raw=z.read('buildings.json');assert hashlib.sha256(raw).hexdigest()==audit['source_snapshot_sha256'];original={r['attributes']['BLDG_NUM']:r for r in json.loads(raw)['features']}
assert collections.Counter(r['gis_use_name'] for r in audit['rows'])=={'Classroom':16,'Dining':3,'Student Center':1,'Library':2}
assert collections.Counter(r['model_category'] for r in audit['rows'])=={'Teaching':16,'Dining':4,'Library':2}
for r in audit['rows']:
 a=original[r['building_number']]['attributes'];assert r['gis_use_name']==a['USE_NAME'] and r['gis_building_name']==a['BLDG_NAME'] and r['gis_use_code']==a['USECODE']
 u=urlparse(r['official_gis_record_url']);q=parse_qs(u.query);assert u.netloc=='gismaps.oit.ncsu.edu' and q['where']==["BLDG_NUM = '"+r['building_number']+"'"] and 'USE_NAME' in q['outFields'][0]
 if r['building_number']=='102':assert r['gis_use_name']=='Student Center' and r['additional_official_source_url']=='https://studentcenters.ncsu.edu/location/talley/'
extract=json.loads((OUT/'destination-gis-records.json').read_text(encoding='utf-8'))
assert len(extract['features'])==22
for r in extract['features']:assert r==original[r['attributes']['BLDG_NUM']]
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));assert s['queries']['campus_destination_sources']['rows']==audit['rows']
assert {r['building_number'] for r in audit['rows']}=={r['destination_id'] for r in s['queries']['campus_passby']['rows']}
print('PASS: 22 classifications match original GIS records exactly; manual Talley addition, record URLs, frozen extracts and model membership verified.')
