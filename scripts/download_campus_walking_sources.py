"""Download public campus GIS with pagination and record source hashes."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime,timezone
import json,hashlib,concurrent.futures
root=Path(__file__).resolve().parents[1];out=root/'data/raw/campus-walk';out.mkdir(parents=True,exist_ok=True)
base='https://gismaps.oit.ncsu.edu/arcgis/rest/services/'
jobs={'walks':'CampusBaseMap/CampusWalks/MapServer/0','entrances':'Accessibility/Accessibility/MapServer/0','buildings':'Buildings/Buildings_OnlineCampusMap/MapServer/1','accessible_paths':'Accessibility/Accessibility/MapServer/1'}
def run(item):
 key,path=item
 url=base+path+'/query?'+urlencode({'where':'1=1','outFields':'*','outSR':4326,'returnGeometry':'true','f':'json','resultRecordCount':1000,'orderByFields':'OBJECTID'})
 all_features=[];offset=0
 while True:
  page_url=url+'&resultOffset='+str(offset);raw=urlopen(page_url,timeout=50).read();d=json.loads(raw);assert not d.get('error'),d.get('error');all_features+=d['features']
  if not d.get('exceededTransferLimit'):break
  assert d['features'];offset+=len(d['features'])
 expected=json.load(urlopen(base+path+'/query?where=1%3D1&returnCountOnly=true&f=json',timeout=30))['count'];assert len(all_features)==expected
 payload={'features':all_features,'geometryType':d.get('geometryType'),'spatialReference':d.get('spatialReference')};raw=(json.dumps(payload,separators=(',',':'))+'\n').encode();(out/(key+'.json')).write_bytes(raw)
 return key,{'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'features':len(all_features),'pagination':'OBJECTID order, batches of 1000; count reconciled to returnCountOnly'}

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: sources=dict(pool.map(run,jobs.items()))
(out/'manifest.json').write_text(json.dumps({'retrieved_at':datetime.now(timezone.utc).isoformat(),'sources':sources},indent=2)+'\n')
print(sources)
for key in ['walks','buildings','entrances']:
 d=json.loads((out/(key+'.json')).read_text());print(key,len(d['features']))
 if key=='walks':
  from collections import Counter
  print('types',Counter(f['attributes']['Type'] for f in d['features']));print('enabled',Counter(f['attributes']['Enabled'] for f in d['features']))
 if key=='buildings':
  for f in d['features']:
   if f['attributes'].get('BLDG_NUM') in ['102','131']:print('SITE',f['attributes']['BLDG_NAME'])
