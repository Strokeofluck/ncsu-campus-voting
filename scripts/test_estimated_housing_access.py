"""Audit separate estimates against frozen GIS; preserve original denominators."""
import argparse,hashlib,json,math,sys,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--library-dir');args=p.parse_args()
if args.library_dir:sys.path.append(args.library_dir)
from pyproj import Transformer
from shapely.geometry import LineString,Point,Polygon
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk';t=Transformer.from_crs(4326,32119,always_xy=True)
with zipfile.ZipFile(OUT/'official-gis-snapshot.zip') as z:
 buildings=json.loads(z.read('buildings.json'))['features'];source_lines=[]
 for key in ['walks','accessible_paths']:
  for f in json.loads(z.read(key+'.json'))['features']:
   if f['attributes'].get('Enabled')==1:source_lines.extend(LineString([t.transform(*p[:2]) for p in path]) for path in f.get('geometry',{}).get('paths',[]) if len(path)>1)
polys=[Polygon([t.transform(*p[:2]) for p in f['geometry']['rings'][0]]) for f in buildings if f.get('geometry')];bycode={f['attributes']['BLDG_NUM']:Polygon([t.transform(*p[:2]) for p in f['geometry']['rings'][0]]) for f in buildings if f.get('geometry')};network=unary_union(source_lines).buffer(.06)
est=json.loads((OUT/'estimated-access-routes.json').read_text(encoding='utf-8'));original=json.loads((OUT/'routes.json').read_text(encoding='utf-8'));s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'))
assert {r['id'] for r in est['rows']}=={r['id'] for r in original['rows'] if not r['available']}=={'271A','012','079','013'}
for r in est['rows']:
 assert r['estimated_access'] and not r['available'];assert bycode[r['id']].boundary.distance(Point(t.transform(*r['access_coordinates'])))<.001
 for field in ['talley','western']:
  a=r[field+'_route'];line=LineString([t.transform(*p) for p in a['geometry']['coordinates']]);start=LineString([t.transform(*p) for p in a['origin_connector']['coordinates']]);end=LineString([t.transform(*p) for p in a['destination_connector']['coordinates']]);assert line.difference(network).length<.1
  assert max(start.length,end.length)<=30;assert all(start.intersection(poly).length<=2.5001 for poly in polys)
  assert abs(start.length-r['estimated_connector_m'])<.001;assert abs(line.length+start.length+end.length-r[field+'_m'])<.002
  assert math.dist(start.coords[-1],line.coords[0])<.001;assert math.dist(line.coords[-1],end.coords[0])<.001
 assert abs(r['difference_m']-r['western_m']+r['talley_m'])<1e-8
assert s['queries']['campus_estimated_access']['rows']==est['rows'];assert s['queries']['campus_walking_routes']['rows']==original['rows'];assert sum(r['available'] for r in original['rows'])==36;assert len(s['queries']['campus_passby']['rows'])==792
catalog=json.loads((ROOT/'data/sources/ncsu-gis/2026-11-01/catalog.json').read_text(encoding='utf-8'))
for f in catalog['files']:assert hashlib.sha256((ROOT/'data/sources/ncsu-gis/2026-11-01'/f['name']).read_bytes()).hexdigest()==f['sha256']
print('PASS: all 8 supplemental routes follow source paths; estimated boundary connectors are <=30 m and avoid building interiors; lengths reconcile; original averages/routine denominators unchanged; archived source hashes verified.')
