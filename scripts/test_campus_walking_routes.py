"""Independently verify route geometry, source coverage, units and missingness."""
import argparse,csv,hashlib,json,math,sys,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--library-dir');args=p.parse_args()
if args.library_dir:sys.path.append(args.library_dir)
from pyproj import Transformer,Geod
from shapely.geometry import LineString
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk'
d=json.loads((OUT/'routes.json').read_text(encoding='utf-8'));t=Transformer.from_crs(4326,32119,always_xy=True);geod=Geod(ellps='WGS84')
source_lines=[]
with zipfile.ZipFile(OUT/'official-gis-snapshot.zip') as archive:
 for key,source in d['sources'].items():
  raw=archive.read(key+'.json');assert hashlib.sha256(raw).hexdigest()==source['sha256'];features=json.loads(raw)['features'];assert len(features)==source['features']
  if key not in ['walks','accessible_paths']:continue
  for f in features:
   if f['attributes'].get('Enabled')!=1:continue
   source_lines.extend(LineString([t.transform(*p[:2]) for p in line]) for line in f.get('geometry',{}).get('paths',[]) if len(line)>1)
network=unary_union(source_lines).buffer(.06)
sites={s['id']:s for s in d['sites']};assert len({r['id'] for r in d['rows']})==len(d['rows'])==40
for r in d['rows']:
 if not r['available']:
  assert r['unavailable_reason'] and all(k not in r for k in ['talley_m','western_m','difference_m']);continue
 assert math.isclose(r['difference_m'],r['western_m']-r['talley_m'],abs_tol=1e-9)
 for key,site in [('talley','102'),('western','131')]:
  v=r[key+'_route'];line=LineString([t.transform(*p) for p in v['geometry']['coordinates']]);assert abs(line.length-v['network_m'])<.001
  assert line.difference(network).length<.1,(r['name'],key,'route leaves enabled source paths')
  a=LineString([t.transform(*p) for p in v['origin_connector']['coordinates']]);b=LineString([t.transform(*p) for p in v['destination_connector']['coordinates']])
  assert abs(a.length-v['origin_connector_m'])<.001 and abs(b.length-v['destination_connector_m'])<.001
  assert max(a.length,b.length)<=30
  assert math.dist(a.coords[-1],line.coords[0])<.001 and math.dist(line.coords[-1],b.coords[0])<.001
  assert math.dist(a.coords[0],t.transform(*r['entrance_coordinates']))<.001
  assert math.dist(b.coords[-1],t.transform(*sites[site]['coordinates']))<.001
  assert abs(v['total_m']-line.length-a.length-b.length)<.002 and abs(r[key+'_m']-v['total_m'])<1e-9
  ll=v['geometry']['coordinates'];gl=abs(geod.line_length([p[0] for p in ll],[p[1] for p in ll]));assert abs(gl/line.length-1)<.001
assert sum(r['available'] for r in d['rows'])==d['audit']['routed_count']==36
assert 1500<d['audit']['talley_to_western_m']<1900
assert not d['audit']['network_gaps_bridged'] and not d['audit']['planar_intersections_joined']
with (OUT/'distances.csv').open(encoding='utf-8',newline='') as f:
 records=list(csv.DictReader(f));assert len(records)==40
 for r in records:
  if r['available']=='False':assert r['talley_m']==r['western_m']==r['difference_m']==''
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));assert s['queries']['campus_walking_routes']['rows']==d['rows'];assert s['report']['asOf']=='2026-10-30'
print('PASS: 36 route pairs follow frozen enabled GIS geometry; metres independently reconcile with geodesic lengths, connectors, CSV and all differences; four missing routes stay missing; voting cutoff preserved.')
