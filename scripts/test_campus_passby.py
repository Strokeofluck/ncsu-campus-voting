"""Audit route-pair denominators, threshold counts and independent geometric proximity."""
import argparse,csv,json,math,sys,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--library-dir');args=p.parse_args()
if args.library_dir:sys.path.append(args.library_dir)
from pyproj import Transformer
from shapely.geometry import Polygon,LineString,Point
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/processed/campus-walk';d=json.loads((OUT/'passby.json').read_text(encoding='utf-8'));rows=d['rows']
t=Transformer.from_crs(4326,32119,always_xy=True)
with zipfile.ZipFile(OUT/'official-gis-snapshot.zip') as z:buildings=json.loads(z.read('buildings.json'))['features']
points={s['id']:Point(t.transform(*s['coordinates'])) for s in d['site_points']}
polys={f['attributes']['BLDG_NUM']:Polygon([t.transform(*p[:2]) for p in f['geometry']['rings'][0]]) for f in buildings if f['attributes']['BLDG_NUM'] in ['102','131']}
assert len(d['origins'])==36 and len(d['destinations'])==22 and len(rows)==36*22
assert len({(r['origin_id'],r['destination_id']) for r in rows})==len(rows)
assert '024' not in [r['id'] for r in d['destinations']]
assert [r['id'] for r in d['destinations']].count('047')==1 and not any(r['id'] in ['047A','047B','047C'] for r in d['destinations'])
for r in rows:
 line=LineString([t.transform(*p) for p in r['geometry']['coordinates']])
 assert r['route_m']+1>=line.length
 for name,code in [('talley','102'),('western','131')]:
  # Public display geometry is simplified within 1 m; calculated distances use full geometry.
  assert abs(line.distance(polys[code])-r[name+'_nearest_m'])<=1.01,(r['origin_id'],r['destination_id'],name)
  assert abs(line.distance(points[code])-r[name+'_entrance_nearest_m'])<=1.01,(r['origin_id'],r['destination_id'],name,'entrance')
for basis in ['footprint','entrance']:
 for include in [False,True]:
  eligible=[r for r in rows if include or not r['ends_at_talley']]
  assert len(eligible)==(792 if include else 756)
  for site in ['talley','western']:
   previous=-1
   for radius in [25,50,100]:
    s=next(s for s in d['summary'] if s['distance_basis']==basis and s['radius_m']==radius and s['site']==site and s['include_talley_destinations']==include)
    key=site+('_entrance_nearest_m' if basis=='entrance' else '_nearest_m')
    count=sum(r[key]<=radius for r in eligible)
    assert s['near_routes']==count and s['total_routes']==len(eligible) and count>=previous
    assert math.isclose(s['share_pct'],count/len(eligible)*100,abs_tol=1e-10);previous=count
assert next(s for s in d['summary'] if s['distance_basis']=='footprint' and s['site']=='talley' and s['radius_m']==50 and not s['include_talley_destinations'])['near_routes']==334
assert next(s for s in d['summary'] if s['distance_basis']=='entrance' and s['site']=='talley' and s['radius_m']==50 and not s['include_talley_destinations'])['near_routes']==25
with (OUT/'passby-routes.csv').open(encoding='utf-8',newline='') as f:
 csvrows=list(csv.DictReader(f));assert len(csvrows)==len(rows)
 for a,b in zip(csvrows,rows):assert a['origin_id']==b['origin_id'] and a['destination_id']==b['destination_id'] and float(a['talley_nearest_m'])==b['talley_nearest_m']
s=json.loads((ROOT/'report-source/snapshot.json').read_text(encoding='utf-8'));assert s['queries']['campus_passby']['rows']==rows and s['report']['asOf']=='2026-10-30'
print('PASS: all 792 unique modeled pairs, complete paired denominators, threshold sensitivity, full-resolution proximity within display tolerance, destination exclusions and CSV/source rows verified.')
