"""Derive stationary display-marker centers; never alter route entrances or calculations."""
import json,zipfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk';p=ROOT/'report-source/snapshot.json';s=json.loads(p.read_text(encoding='utf-8'))
with zipfile.ZipFile(OUT/'official-gis-snapshot.zip') as z:
 raw=z.read('buildings.json');m=json.loads(z.read('manifest.json'));assert hashlib.sha256(raw).hexdigest()==m['sources']['buildings']['sha256'];features=json.loads(raw)['features']
bycode={f['attributes']['BLDG_NUM']:f for f in features if f.get('geometry')}
ids=set(r['id'] for r in s['queries']['campus_walking_routes']['rows'])|set(r['id'] for r in s['campusPassby']['destinations'])|{'102','131'};centers={}
for code in sorted(ids):
 parts=[bycode[c] for c in ['047','047A','047B','047C'] if c in bycode] if code=='047' else [bycode[code]]
 xy=[xy for f in parts for ring in f['geometry']['rings'] for xy in ring];centers[code]=[(min(p[0] for p in xy)+max(p[0] for p in xy))/2,(min(p[1] for p in xy)+max(p[1] for p in xy))/2]
payload={'basis':'Geographic bounding-box center of original frozen GIS building outline; Hill wings merged. Stationary display markers only. Route entrances, measured lengths, proximity and averages are unchanged.','source_sha256':m['sources']['buildings']['sha256'],'centers':centers,'labels':{code:{'name':bycode[code]['attributes']['BLDG_NAME'],'use_name':bycode[code]['attributes']['USE_NAME']} for code in sorted(ids)}}
(OUT/'display-centers.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');s['campusBuildingCenters']=centers;s['campusBuildingLabels']=payload['labels'];p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Prepared',len(centers),'display centers without editing route rows.')
